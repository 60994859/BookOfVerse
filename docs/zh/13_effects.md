# 效果

每个函数都讲述两个故事。第一个故事，通过类型讲述，
描述哪些数据流入以及哪些数据流出。第二个
通过效果讲述的故事描述了该功能的作用
方式——是否从内存读取、写入存储、是否可能失败，
或可以暂停执行。虽然大多数语言将这个第二个故事隐式处理，Verse 使其显式化，将隐藏的副作用转变为有文档记录的契约。

考虑一个更新玩家得分的简单游戏功能。在
在大多数语言中，您会看到类似“UpdateScore(player,
点）`并且必须猜测里面发生了什么。是否修改了
玩家对象？写入数据库？打印到日志？触发
动画？如果不阅读实现，你就无法知道。在
Verse、效果是签名本身的一部分，预先声明
该函数到底可以执行什么类型的操作。

这种明确性乍一看似乎是额外的工作，但它
从根本上改变了你推理代码的方式。当你看到
`<reads>` 在一个函数上，你知道它观察可变状态。当你
参见 `<writes>`，您知道它会修改该状态。当你看到
`<decides>`，你知道它可能会失败。这些不是评论或
可能是错误的文档——它们是编译器强制执行的
合同必须准确。

## 了解效果

效果表示您的代码和对象之间可观察到的交互
它周围的世界。读取玩家的健康状况、更新分数、生成
粒子效果，等待动画完成——所有这些
运算的影响超出了简单计算的范围。Verse的
效果系统捕获这些交互，使它们可见并
可验证的。

考虑这个向玩家打招呼的简单函数：

<!--versetest
c:=class:
    var CurrentGreeting:string=""
    GreetPlayer()<transacts>:void =
        set CurrentGreeting = "Hello, adventurer!"
assert:
    C:=c{}
    C.GreetPlayer()
<#
-->
<!-- 01 -->
```verse
GreetPlayer()<transacts>:void =
    set CurrentGreeting = "Hello, adventurer!"
    Print(CurrentGreeting)
```
<!--
#>
-->

`<transacts>`效果立即告诉你这个功能
修改可变状态。您不需要阅读实现
知道调用 `GreetPlayer()` 会改变您的某些内容
程序的内存。效果是对行为的承诺，经过检查和验证
由编译器强制执行。

效果通过函数调用自然地组合。如果函数A调用
函数B，并且B有一定的作用，那么A至少必须声明
这些相同的效果（除了我们将探讨的一些例外）。这个
传播确保效果不会被隐藏或洗白
中间函数——操作的真实本质始终是
在调用堆栈的每个级别都可见。

**为什么效果很重要**

使效果显式服务于人类理解和编译器
优化。对于开发人员来说，效果充当文档，但不能
撒谎。当您调试值意外更改的原因时，您可以
跟踪调用链，仅查看具有以下内容的函数
`<writes>`。当你试图理解为什么一个函数可能会
失败，你寻找`<decides>`。这不是猜测——这是有保证的
通过类型系统。

对于编译器来说，显式效果可以实现强大的优化和
安全保证。标记为`<computes>`的纯函数可以被记忆，
他们的结果被缓存，因为他们总是返回相同的输出
相同的输入。没有 `<writes>` 的功能可以安全地执行
并行无锁。没有`<decides>`的函数可以调用
无需失败处理。

效果系统还强制执行架构决策。想要
确保你的数学库保持纯净？标记其功能
`<computes>`。构建必须运行的预测客户端系统
玩家的机器？使用`<predicts>`确保没有仅服务器
操作潜入。这些不仅仅是惯例——它们是
编译器强制的保证。

## 效果系列和说明符

Verse 将效果组织成系列，每个系列跟踪一个特定方面
的计算。每个家族都包含基本效果和效果
说明符声明函数可以执行哪些效果。

这六个效果系列是：

* **基数**：函数是否以及如何返回
* **堆**：访问可变内存
* **暂停**：函数是否可以暂停执行
* **发散**：函数是否可以永远运行
* **预测**：函数运行的位置
* **内部**：保留供内部使用

有些效果没有说明符，而有些说明符则暗示多个
影响。例如，`<transacts>` 意味着 `reads`、`writes` 和
`allocates`，属于Heap家族。

效果说明符可以进一步分为*独占*说明符
（`<converges>`、`<computes>`、`<transacts>`）和*附加*说明符
（`<suspends>`、`<decides>`、`<reads>`、`<writes>`、`<allocates>`）。一个
函数最多可以有一个独占说明符，但可以组合
多个附加的。例如，`<computes><decides>` 有效
（纯计算可能会失败），但 `<computes><transacts>` 是一个
错误（不能有两个互斥的效果）。|基本效果|效果说明符|效果系列|说明符隐含的效果|笔记|
| -----| ----------- | -------- | -----| ---- |
| **成功** |                |基数 |                  | *无说明符；必须成功* |
| **失败** |                |基数 |                  | *无说明符；可能会失败* |
|              | `<decides>` |基数 | `{succeeds, fails}` | *不能与 `<suspends>` 结合使用* |
| **阅读** | `<reads>` |堆| `{reads}` | *允许读取可变状态* |
| **写** | `<writes>` |堆| `{writes}` | *允许写入可变状态* |
| **分配**| `<allocates>` |堆| `{allocates}` | *允许分配可变内存* |
|              | `<transacts>` |堆| `{reads, writes, allocates}` | *独家的;默认* |
|              | `<computes>` |堆| `{}` | *独家的;纯计算* |
| **暂停** | `<suspends>` |暂停| `{suspends}` | *不能与 `<decides>` 结合使用* |
| **分歧** |                |分歧| `{diverges}` | *无说明符；可能会永远运行* |
|              | `<converges>` |分歧| `{}` | *独家的;本机函数、抽象方法、类型签名* |
| **规定** |                |预测| `{dictates}` | *无说明符；服务器权限* |
|              | `<predicts>` |预测| `{}` | *允许客户预测* |
| **无回滚** |             |内部| `{no_rollback}` | *将被弃用；禁止交易* |

以下限制有效：

- `<suspends>` 和 `<decides>` 不能组合使用同一功能，
- `<converges>` 仅允许用于 `<native>` 函数、抽象方法和类型签名，
- 重复的说明符（例如，`<computes><computes>`）是错误的。

## 效果如何组成

将效果说明符视为位向量中的设置位：一位
每个基本效果。没有任何注释，函数如
`GameUpdate`具有以下效果：

<!--NoCompile-->
<!-- 02 -->
```verse
GameUpdate():void = ...  # 没有指定明确的效果
```
|规定|暂停|读 |写道|分配 |成功|失败|
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| ✔️ | ❌ | ✔️ | ✔️ | ✔️ | ✔️ | ❌ |

这意味着它具有效果 `dictates`、`reads`、`writes`、`allocates`
和 `succeeds`。这几乎就像写 `<dictates><transacts>`
除非我们缺乏一种方法来表明该函数不会失败。

顺便说一句：缺少 `fails` 和 `succeeds` 的说明符可以
可以通过这样的事实来解释：像 `<fails>` 这样的说明符意味着
函数总是失败，从不返回值，并且不能有
可观察到的副作用（它们会因失败而消失）。  的
`succeeds` 效果是隐含的。

注释函数仅影响该说明符中的位
家庭。例如，函数 `CheckPlayerStatus` 与 `<reads>`
和 `<predicts>` 说明符：

<!--NoCompile-->
<!-- 03 -->
```verse
CheckPlayerStatus()<reads><predicts>:string = ...
```
有以下效果：

|规定|暂停|读 |写道|分配 |成功|失败|
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| ❌ | ❌ | ✔️ | ❌ | ❌ | ✔️ | ❌ |

指定 `<reads>` 将清除 `writes` 和 `allocates` 位，并且
`<predicts>` 清零 `dictates` 位，其他一切不变。

## 效果系列详细信息

### 基数效果

基数族处理函数是否返回值
成功。每个函数要么成功（返回其声明的
类型）或失败（不产生任何值）。大多数功能总是成功的——
它们是总是产生输出的确定性转换。但是
标有 `<decides>` 的功能可能会失败，将失败变成
控制流机制。

<!--versetest
ValidateHealth(Health:float)<transacts><decides>:void =
    Health > 0.0
    Health <= 100.0

StartCombat():void={}
player:=struct{Health:float}

assert:
    Player:=player{Health:=50.0}
    if (ValidateHealth[Player.Health]):
        StartCombat()
<#
-->
<!-- 04 -->
```verse
ValidateHealth(Health:float)<transacts><decides>:void =
    Health > 0.0      # 如果健康状况为零或负数则失败
    Health <= 100.0   # 如果生命值超过最大值则失败

# 用途
if (ValidateHealth[Player.Health]):
    # 健康有效，继续处理
    StartCombat()
```
<!--
#>
-->

决定效果的美妙之处在于它将验证与
控制流统一。你不会先检查条件再采取行动——
检查本身决定了程序的执行路径。

### 堆效果

堆家族控制对可变内存的访问。这或许就是
理解程序行为最重要的家族，因为它
确定函数是否可以观察或修改状态。

`<computes>` 说明符标记纯函数 - 那些既不
读取或写入可变状态。这些函数是确定性的：给定
相同的输入，它们总是产生相同的输出。他们是
计算的数学理想，无边变换数据
影响。

<!--versetest-->
<!-- 05 -->
```verse
CalculateDamage(BaseDamage:float, Multiplier:float)<computes>:float =
    BaseDamage * Multiplier
```
`<reads>` 效果允许函数观察可变状态。他们
可以查看变量和可变字段的当前值，但不能
修改它们。这对于基于以下内容的查询和计算很有用
当前游戏状态。

<!--versetest
player := class:
    Name:string
    var Health:float = 100.0
    var Score:int = 0

GetPlayerStatus(P:player)<reads>:string =
    if (P.Health > 50.0):
        "Healthy"
    else if (P.Health > 0.0):
        "Injured"
    else:
        "Defeated"

assert:
    P:=player{Name:="Test"}
    Status:=GetPlayerStatus(P)
<#
-->
<!-- 06 -->
```verse
player := class:
    Name:string
    var Health:float = 100.0
    var Score:int = 0

GetPlayerStatus(P:player)<reads>:string =
    if (P.Health > 50.0):
        "Healthy"
    else if (P.Health > 0.0):
        "Injured"
    else:
        "Defeated"
```
<!--
#>
-->

`<writes>` 效果允许修改可变状态。功能
有了这个效果可以使用`set`来更新变量和可变
字段。 `<writes>` 通常也需要 `<reads>`，例如当
修改涉及读取当前值。

事实上，`set` 指令默认为 `<transacts>`，因为
在语言中添加*实时变量*。实时变量是
其值取决于其他变量的变量；当其中之一
变量由 `set` 更新，实时变量将被评估
可能有一些 `reads` 和 `allocates`。

<!--versetest
player := class:
    Name:string
    var Health:float = 100.0

HealPlayer(P:player, Amount:float)<transacts>:void =
    NewHealth := P.Health + Amount
    set P.Health = Min(NewHealth, 100.0)

assert:
    P:=player{Name:="Test", Health:=50.0}
    HealPlayer(P, 30.0)
<#
-->
<!-- 07 -->
```verse
HealPlayer(P:player, Amount:float)<transacts>:void =
    NewHealth := P.Health + Amount
    set P.Health = Min(NewHealth, 100.0)
```
<!--
#>
-->

`<allocates>` 效果表示可观察地创建的函数
唯一值 — 标记为 `<unique>` 的对象或包含以下内容的值
可变字段。每次调用此类函数都会返回一个不同的值，
即使输入相同。

<!--NoCompile-->
<!-- 08 -->
```verse
game_entity := class<allocates>:
    ID:id
    var Position:vector3

CreateEntity(Pos:vector3)<allocates>:game_entity =
    game_entity{ID := GenerateID(), Position := Pos}
```
`<transacts>` 是默认的功能。 

### 暂停效果

悬架系列包含单一效果：
`<suspends>`。具有此效果的函数可以暂停其执行并
稍后恢复，可能跨多个游戏帧。这是
对于需要时间的操作至关重要：动画、冷却时间、
等待玩家输入或任何多帧行为。

<!--NoCompile-->
<!-- 09 -->
```verse
PlayVictorySequence()<suspends>:void =
    PlayAnimation(VictoryDance)
    Sleep(2.0)  # 等待 2 秒
    PlaySound(VictoryFanfare)
    Sleep(1.0)
    ShowRewardsScreen()
```
`suspends` 效果是病毒式的——任何调用暂停的函数
函数本身必须标记为 `<suspends>`。这确保您始终
了解哪些功能可能需要时间才能完成。

而 `<suspends>` 和 `<decides>` 不能组合在同一
函数，它们对于如何交互有特定的规则
函数调用。 `<suspends>` 函数可以调用 `<decides>`
函数，但*仅在失败上下文中*使用方括号
`[]` 语法——这确保失败在本地处理并且
不会作为失败效果传播：

<!--versetest
DoAsyncWork():void={}
-->
<!-- 10 -->
```verse
ValidateInput(Value:int)<decides><computes>:void =
    Value > 0
    Value < 100

ProcessAsync(Value:int)<suspends>:void =
    # 有效：在失败上下文中调用决定函数
    if (ValidateInput[Value]):
        # 处理有效输入
        DoAsyncWork()

# 无效：调用决定失败上下文之外的函数
# ProcessAsync(Value:int)<suspends>:void =
#     ValidateInput(Value)  # ERROR: must use [] syntax
```
`<suspends>` 函数可以调用另一个 `<suspends>` 函数，但*不得使用失败处理语法*，如 `?`：

<!--versetest-->
<!-- 11 -->
```verse
AsyncOp()<suspends>:?int = false

CallAsync()<suspends>:void =
    # 有效：正常调用挂起函数
    X := AsyncOp()

    # 无效：不能使用？在暂停上下文中暂停
    # if (Value := AsyncOp()?):
```
存在不对称性是因为 `<suspends>` 和 `<decides>` 代表
根本不同的控制流机制——暂停是关于
时间，而失败则关乎成功/失败。混合他们的语法
表单对正在处理的内容造成了模糊性。

### 内部效果

**[预发布]**：`<no_rollback>` 效果已弃用。

#### 预测效果

!!!注意“未发布的功能”
    `<predicts>`效果尚未发布。

预测系列确定代码在客户端-服务器中运行的位置
架构。默认情况下，函数具有 `dictates` 效果，
这意味着它们在服务器上权威运行。 `<predicts>`
说明符允许函数在客户端上预测性地运行
响应能力，服务器稍后验证并可能
修正结果。

<!--NoCompile-->
<!-- 12 -->
```verse
HandleJumpInput()<predicts>:void =
    # 立即在客户端上运行以获得响应能力
    StartJumpAnimation()
    PlayJumpSound()

    # 如果需要，服务器将验证并更正
    PerformJump()
```
即使有网络延迟，这也能实现响应式游戏，因为玩家
在服务器维护时查看其操作的即时反馈
权威国家。

#### 发散效果

目前正在规划中，分歧家族将追踪是否
函数保证终止。 `<converges>` 说明符
标记可证明在有限时间内完成的函数，而
没有它的函数可能会永远运行。这一点尤为重要
用于构造函数和初始化代码。

`<converges>` 说明符可用于：

- `<native>` 保证终止的函数
- 类和接口中的抽象方法签名
- 类型表达式中的函数签名

常规函数实现不能使用 `<converges>` — 只能使用它们在抽象上下文中的声明或作为本机函数。


<!-- TODO: write more -->

## 效果合成

效果通常沿着调用链向上传播——函数必须
声明它调用的函数的所有效果。然而，某些
语言结构可以隐藏特定的效果，防止它们
进一步传播。
`if` 表达式在其失败上下文中隐藏 `fails` 影响，因此

某种情况下的失败不会传播到周围的失败
功能：

<!--versetest-->
<!-- 13 -->
```verse
SafeMod(A:int, B:int)<computes>:int =
    if (V:= Mod[A,B])  then V else 0
```
`spawn` 表达式隐藏了 `suspends` 效果，允许立即
启动继续的异步操作的函数
独立地：

<!--versetest
GetNextTrack():int=0
PlayTrack(:int)<suspends>:void={}
-->
<!-- 14 -->
```verse
Play()<suspends>:void =
        loop:
            PlayTrack(GetNextTrack())
            Sleep(180.0)  

StartBackgroundMusic():void =  # 明确 <suspends>
    spawn:
        Play() # 暂停重生隐藏的效果
```
如上所述，`<suspends>` 代码中不允许出现失败
包括`spawn`。解决此限制的一种方法是使用
`option` 表达式将失败转换为可选值，
将 `fails` 效果转换为常规值，可以
在没有 `<decides>` 的情况下处理：

<!--versetest
item:=struct{}
-->
<!-- 16 -->
```verse
TryGetItem(Items:[]item, Index:int):?item =
    option{Items[Index]}  # 数组访问可能失败，选项捕获它
```
`defer` 表达式提供了退出时运行的清理代码。
范围，但有严格的效果限制：

- 不能包含 `<suspends>` 操作——延迟代码必须同步执行
- 不能包含 `<decides>` 操作 - 延迟代码必须始终成功

<!--versetest
resource:=class{}
DoAsyncWork():void={}
GetResource()<transacts>:resource=resource{}
-->
<!-- 17 -->
```verse
AcquireResource()<transacts>:resource = GetResource()
ReleaseResource(R:resource)<transacts>:void = {}

ProcessResource()<suspends>:void =
    R := AcquireResource()
    defer:
        ReleaseResource(R)  # 有效：允许延迟交易

    # 使用异步操作处理资源
    DoAsyncWork()
```
这些约束确保清理代码可预测地执行，并且
完全，没有暂停或失败的可能性
可能会使资源处于不一致的状态。

## 子类型和类型兼容性

效果注释创建函数之间的子类型关系
类型。了解效果如何与类型兼容性相互作用是
将函数存储在变量中时至关重要，将它们传递为
参数，或在不同的实现之间进行选择。

可以使用具有**较少影响**的函数
**预计会有更多影响**。这就是效果子类型化——一个函数
做得更少与允许更多的上下文兼容：

<!--versetest-->
<!-- 18 -->
```verse
# 仅进行计算的纯函数
PureAdd(X:int)<computes>:int = X + 1

# 期望计算并决定的变量
F:type{_(:int)<computes><decides>:int} = PureAdd

# 通过变量调用
Result := F[5]  # 必须使用 [] 语法，因为类型具有 <decides>
# 返回option{6}，因为PureAdd永远不会失败
```
在这个例子中，`PureAdd`只有`<computes>`，但它可以是
分配给期望 `<computes><decides>` 的变量。纯粹的
函数是可失败接口的有效实现——它只是
从不锻炼失败能力。

这个原则适用于所有效果：

<!--versetest-->
<!-- 19 -->
```verse
# 带有 <computes> 的函数
Compute(X:int)<computes>:int = X * 2

# 可以分配给期望更多效果的类型
F1:type{_(:int)<computes><decides>:int} = Compute
F2:type{_(:int)<transacts>:int} = Compute
F3:type{_(:int)<reads>:int} = Compute

# 全部有效 - 计算执行的操作少于允许的范围
```
在决定子类型时，效果具有以下影响：

- `<computes>` 是 `<reads>`、`<transacts>` 以及与 `<decides>` 的任意组合的子类型
- `<reads>` 是 `<transacts>` 的子类型
- 不带 `<decides>` 的函数是带 `<decides>` 的函数的子类型
- 不带 `<suspends>` 的功能是带 `<suspends>` 的功能的子类型（兼容时）

虽然您可以通过子类型添加效果，但**无法删除**
函数实际具有的效果：

<!--versetest-->
<!-- 20 -->
```verse
Validate(X:int)<computes><decides>:int =
    X > 0
    X

# 错误：无法在没有<decides>的情况下分配给类型
# F:type{_(:int)<computes>:int} = Validate
# 函数可能会失败，但类型不允许
```
同样，具有堆效果的函数不能分配给纯类型：

<!--NoCompile-->
<!-- 21 -->
```verse
counter := class:
    var Count:int = 0

Increment(C:counter)<transacts>:int =
    set C.Count = C.Count + 1
    C.Count

# 错误：无法将事务函数分配给计算类型
# F:type{_(:counter)<computes>:int} = Increment
# 函数写入状态，类型不允许
```
此限制确保类型安全——类型签名是一种承诺
关于该功能可能执行的效果以及实际功能
必须兑现这一承诺。

当您有条件地在具有不同功能的功能之间进行选择时
效果，结果表达式具有所有可能的并集
影响。这是*效果连接*——编译器保守地假设
结果可能会执行任何分支可以执行的任何效果：

<!--versetest-->
<!-- 22 -->
```verse
# 功能不同效果不同
PureFunction(X:int)<computes>:int = X + 1
FailableFunction(X:int)<computes><decides>:int =
    X > 0
    X + 1

# 条件选择连接效果
SelectFunction(UseFailable:logic):type{_(:int)<computes><decides>:int} =
    if (UseFailable?):
        FailableFunction  # 有<computes><decides>
    else:
        PureFunction      # 有<computes>
    # 结果类型必须同时考虑：<computes><decides>

# 返回的函数可能会失败（来自 FailableFunction）
# 或可能不（来自 PureFunction），因此类型必须包含 <decides>
F := SelectFunction(true)
Result := F[5]  # 必须使用 [] 因为结果类型具有 <decides>
```
效果连接适用于在函数之间进行选择的所有控制流：

<!--versetest-->
<!-- 23 -->
```verse
Identity(X:int)<computes>:int = X

DecidesIdentity(X:int)<computes><decides>:int =
    X > 0
    X

TransactsIdentity(X:int)<transacts>:int = X

# 连接 <computes> 和 <computes><decides>
F1:type{_(:int)<computes><decides>:int} =
    if (true?):
        Identity
    else:
        DecidesIdentity
# 结果：<computes><decides>（效果并集）

# 连接 <computes><decides> 和 <transacts>
F2:type{_(:int)<decides><transacts>:int} =
    if (true?):
        DecidesIdentity  # <computes><decides>
    else:
        TransactsIdentity  # <transacts>
# 结果：<decides><transacts>（效果并集）
```
效果子类型支持灵活的函数参数：

<!--versetest
PureAdd(:int)<computes>:int=1
Validate(:int)<computes><decides>:int=1
Increment(:int)<transacts>:int=1
-->
<!-- 25 -->
```verse
# 接受任何不超过 <transacts><decides> 的函数
ProcessValues(
    Data:[]int,
    Transform(:int)<transacts><decides>:int
):[]int =
    for (Value:Data, Result := Transform[Value]):
        Result

# 可以传递纯函数
ProcessValues(array{1, 2, 3}, PureAdd)

# 可以传递失败的函数
ProcessValues(array{1, 2, 3}, Validate)

# 可以传递事务函数
ProcessValues(array{1, 2, 3}, Increment)
```
效果子类型使函数组合自然地发挥作用：

<!--versetest
PureFunction(:int)<computes>:int=1
FailableFunction(:int)<computes><decides>:int=1
-->
<!-- 26 -->
```verse
Compose(
    F(:int)<computes>:int,
    G(:int)<computes>:int
):type{_(:int)<computes>:int} =
    Local(X:int)<computes>:int = G(F(X))
    Local

# 如果我们想允许更多效果：
ComposeFlexible(
    F(:int)<transacts><decides>:int,
    G(:int)<transacts><decides>:int
):type{_(:int)<transacts><decides>:int} =
    Local(X:int)<transacts><decides>:int =
        if (IntermediateResult := F[X]):
            G[IntermediateResult]
        else:
            1=2; 0
    Local

# 可以传递效果较少的函数
ComposeFlexible(PureFunction, PureFunction)
ComposeFlexible(PureFunction, FailableFunction)
```
下表总结了效果和类型的相互作用：

|场景|有效的？ |说明|
|----------|--------|-------------|
|将 `<computes>` 分配给 `<computes><decides>` 类型 | ✓ |通过子类型添加效果 |
|将 `<computes>` 分配给 `<transacts>` 类型 | ✓ |纯粹是交易的子类型 |
|将 `<reads>` 分配给 `<transacts>` 类型 | ✓ |读取是事务性的子类型 |
|将 `<computes><decides>` 分配给 `<computes>` 类型 | ✗ |无法删除 `<decides>` |
|将 `<transacts>` 分配给 `<computes>` 类型 | ✗ |无法消除堆效果 |
|在 `<computes>` 和 `<decides>` 之间选择 |结果：`<computes><decides>` |效果加盟|
|在 `<reads>` 和 `<transacts>` 之间选择 |结果：`<transacts>` |效果加盟|

这些规则确保效果注释保持可信
契约——函数可以做的事情少于声明的（子类型化），但永远不会
更多，条件选择保守地考虑了所有
可能性（加入）。

## 对数据类型的影响

类、结构体和接口都可以进行注释，效果如下
说明符，适用于它们的构造函数。这一点特别
对于确保创建某些对象保持纯粹或具有
效果有限：

<!--versetest-->
<!-- 28 -->
```verse
# 纯数据结构 - 构造函数没有效果
vector3 := struct<computes>:
    X:float = 0.0
    Y:float = 0.0
    Z:float = 0.0

# 由于唯一身份而需要分配的实体
monster := class<unique><allocates>:
    Name:string
    var Health:float = 100.0
```
类、接口和结构**不能**用 `<suspends>` 或 `<decides>` 标记：

<!--versetest-->
<!-- 29 -->
```verse
# 类/接口/结构的有效效果说明符：
valid_class := class<computes>{}
valid_interface := interface<computes>{}
valid_struct := struct<transacts>{}

# 无效：不允许异步和失败效果
# invalid_class := class<suspends>{}      # ERROR
# invalid_interface := interface<decides>{}  # ERROR
# invalid_struct := struct<decides>{}     # ERROR
```
此限制适用于类/结构**声明**本身 -
原型构造函数 `my_class{...}` 不能失败或
暂停。但是，**构造函数**可以使用 `<decides>`：

<!--NoCompile-->
<!-- 29a -->
```verse
# 类别声明不能是<decides>
my_class := class:
    Value:int

# 但是构造函数可以是<decides>
MakeMyClass<constructor>(V:int)<transacts><decides> := my_class:
    Value := block:
        V > 0      # 如果 V <= 0，则失败
        V < 100    # 如果 V >= 100，则失败
        V
```
这在需要时提供了可失败构造——对象要么
存在完整形式或构造函数失败并且没有对象
被创建。

类中的字段默认值和块子句有严格的效果要求：

<!--versetest-->
<!-- 30 -->
```verse
# 字段初始值设定项必须使用纯函数
HelperFunction()<transacts>:int = 42

# 无效：字段初始值设定项无法调用事务函数
# bad_class := class:
#     值：int = HelperFunction() # 错误

# 块条款必须尊重阶级效果
valid_class := class<transacts>:
    var Counter:int = 0
    block:
        set Counter = 1  # 有效：班级有交易

# 无效：块效果超过类效果
# bad_class := class<computes>:
#     变量计数：int = 0
#     块：
#         set Counter = 1  # ERROR: computes class cannot write
```
类成员初始值设定项和块子句受到隐式限制
不具有比类声明的更多的效果。这确保了
构造类的实例尊重类的效果
合同。

限制构造函数的影响有助于维护架构
边界。使用`<computes>`可以保持数据传输对象的纯净，
确保它们只是数据载体。游戏实体可能需要
`<allocates>` 用于唯一标识，而服务对象可能需要
完整的`<transacts>`来初始化它们的状态。

### 接口构建效果约束

当类或接口继承具有构造效果的接口时，它们必须至少声明相同的构造效果：

<!--versetest-->
<!-- 31 -->
```verse
# 具有事务效果的接口
transacting_interface := interface<transacts>{}

# 有效：班级至少有交易
valid_class := class<transacts>(transacting_interface){}

# 无效：类的效果小于接口所需的效果
# invalid_class := class<computes>(transacting_interface){}  # ERROR
```
接口字段初始值设定项还必须尊重接口声明的构造效果：

<!--versetest-->
<!-- 32 -->
```verse
transacting_class := class<transacts>{}

# 有效：接口有事务，字段初始值设定项有事务
valid_interface := interface<transacts>:
    Instance:transacting_class = transacting_class{}

# 无效：接口有计算，但字段初始值设定项有交易
# invalid_interface := interface<computes>:
#     实例：transacting_class = transacting_class{} # 错误
```
这些约束确保构造效果在继承层次结构中正确流动。继承接口的类必须能够构造所有接口字段，这要求至少具有相同的构造效果。

## 使用效果

设计功能时，从所需的最小效果开始，
仅在必要时扩展。具有 `<computes>` 的纯函数是
最容易测试、推理和编写。添加 `<reads>` 当您
需要修改时需要观察状态，`<writes>`，以及
`<decides>` 当您需要基于失败的控制流时。

效果是 API 合同的一部分。一旦发布，删除
Effects 是向后兼容的更改（您的函数执行的操作少于
之前），但添加效果正在破坏（你的函数现在做了更多
超出呼叫者的预期）。设计您的效果签名
深思熟虑，因为它们成为对用户的承诺。

请记住，过度指定效果是允许的，有时
有益的。标记为 `<reads>` 的函数可以实现为纯函数
`<computes>` 内部。这为未来的变化提供了灵活性
而不破坏现有的调用者。

<!--versetest
weapon:=struct<computes>{Type:weapon_type,Dammage:int}
weapon_type:=enum:
    Sword
-->
<!-- 32 -->
```verse
# API承诺它可以读取状态
GetDefaultWeapon<public>()<reads>:weapon =
    # 但目前的实现是纯粹的
    weapon{Type := weapon_type.Sword, Dammage := 10}
```
效果超规格可以使 API 面向未来并避免破坏
稍后更改。例如，将当前的纯函数标记为
`<reads>` 允许您将来添加状态观察，而无需
破坏兼容性。

## 向后兼容性

函数的效果是向后检查的一部分
兼容性。更新属于已发布的函数的一部分时
API，新版本可以有“更少的位”，但不能有更多。所以，一个
以前版本中标记为 `<reads>` 的函数不能
更改为`<transacts>`，但可以细化为`<computes>`。

效果将副作用从隐藏的问题转变为可见的，
可验证的合同。通过将隐含的内容变得明确，Verse 可以帮助您
编写更可预测、可维护且正确的代码。效果
系统不是负担——它是帮助你表达意图的工具
清楚地让编译器验证您的实现是否匹配
那个意图。