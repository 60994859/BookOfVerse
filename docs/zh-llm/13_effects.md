# 效果

每个函数都会讲述两个故事。第一个故事通过类型来讲述，描述了什么数据流入、什么数据流出。第二个故事通过效果来讲述，描述了函数在执行过程中做了什么——是否读取内存、写入存储、可能失败或挂起执行。虽然大多数语言让这第二个故事隐含不彰，但 Verse 将其显式化，把副作用从隐藏的意外转变为文档化的契约。

考虑一个简单的游戏函数，它会更新玩家的分数。在大多数语言中，你会看到一个签名如 `UpdateScore(player, points)`，然后不得不猜测内部发生了什么。它是否修改了玩家对象？写入数据库？打印日志？触发动画？不阅读实现，你无法知道。在 Verse 中，效果是签名本身的一部分，它预先声明了函数可能执行的操作类型。

这种显式化的做法起初可能看起来像是额外的工作，但它从根本上改变了你推理代码的方式。当你在函数上看到 `<reads>` 时，你知道它会观察可变状态。当你看到 `<writes>` 时，你知道它会修改该状态。当你看到 `<decides>` 时，你知道它可能失败。这些不是可能出错的注释或文档——它们是编译器强制执行的契约，必须精确无误。

## 理解效果

效果表示代码与其周围世界之间的可观察交互。读取玩家的生命值、更新分数、生成粒子效果、等待动画完成——所有这些操作都会产生超越简单计算的效果。Verse 的效果系统捕获了这些交互，使其可见且可验证。

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

`<transacts>` 效果立即告诉你这个函数会修改可变状态。你不需要阅读实现就能知道调用 `GreetPlayer()` 会改变程序内存中的某些内容。效果是关于行为的承诺，由编译器检查并强制实施。

效果通过函数调用自然组合。如果函数 A 调用函数 B，而 B 有某些效果，那么 A 必须至少声明这些相同的效果（有一些例外情况我们稍后会讨论）。这种传播确保效果不能通过中间函数隐藏或洗白——操作的真实本质在调用栈的每一层都是可见的。

**为什么效果很重要**

将效果显式化既有助于人类理解，也有利于编译器优化。对于开发者来说，效果充当了不会说谎的文档。当你调试某个值为何意外变化时，可以沿着调用链只查看带有 `<writes>` 的函数。当你试图理解某个函数为何可能失败时，可以查找 `<decides>`。这不是猜测——这是类型系统的保证。

对于编译器来说，显式化的效果可以带来强大的优化和安全保证。标记为 `<computes>` 的纯函数可以被记忆化，其结果可以缓存，因为它们对相同的输入总是返回相同的输出。没有 `<writes>` 的函数可以安全地并行执行，无需锁。没有 `<decides>` 的函数可以在不处理失败的情况下调用。

效果系统还强制实施了架构决策。想确保你的数学库保持纯粹？将其函数标记为 `<computes>`。正在构建一个必须在玩家机器上运行的预测性客户端系统？使用 `<predicts>` 来确保不会有仅限服务器的操作混入。这些不仅仅是约定——它们是编译器强制执行的保证。

## 效果家族与效果说明符

Verse 将效果组织为家族，每个家族追踪计算的某个特定方面。每个家族包含若干基础效果，而效果说明符则声明函数可以执行哪些效果。

六个效果家族分别是：

*   **基数性（Cardinality）**：函数是否返回以及如何返回
*   **堆（Heap）**：对可变内存的访问
*   **挂起（Suspension）**：函数是否可以挂起执行
*   **发散（Divergence）**：函数是否可能永远运行
*   **预测（Prediction）**：函数在哪里运行
*   **内部（Internal）**：保留供内部使用

有些效果没有说明符，而有些说明符隐含了多个效果。例如，`<transacts>` 隐含了 `reads`、`writes` 和 `allocates`，属于堆家族。

效果说明符可以进一步分为*排他性*说明符（`<converges>`、`<computes>`、`<transacts>`）和*叠加性*说明符（`<suspends>`、`<decides>`、`<reads>`、`<writes>`、`<allocates>`）。一个函数最多可以有一个排他性说明符，但可以组合多个叠加性说明符。例如，`<computes><decides>` 是有效的（可能失败的纯计算），但 `<computes><transacts>` 是错误的（不能同时具有两个排他性效果）。

|基础效果|效果说明符|效果家族|说明符隐含的效果|备注|
| ----- | ----------- | ------- | ----- | ---- |
| **succeeds** | | 基数性 | | *无说明符；必须成功* |
| **fails** | | 基数性 | | *无说明符；可以失败* |
| | `<decides>` | 基数性 | `{succeeds, fails}` | *不能与 `<suspends>` 组合* |
| **reads** | `<reads>` | 堆 | `{reads}` | *允许读取可变状态* |
| **writes** | `<writes>` | 堆 | `{writes}` | *允许写入可变状态* |
| **allocates** | `<allocates>` | 堆 | `{allocates}` | *允许分配可变内存* |
| | `<transacts>` | 堆 | `{reads, writes, allocates}` | *排他性；默认值* |
| | `<computes>` | 堆 | `{}` | *排他性；纯计算* |
| **suspends** | `<suspends>` | 挂起 | `{suspends}` | *不能与 `<decides>` 组合* |
| **diverges** | | 发散 | `{diverges}` | *无说明符；可能永远运行* |
| | `<converges>` | 发散 | `{}` | *排他性；内在函数、抽象方法、类型签名* |
| **dictates** | | 预测 | `{dictates}` | *无说明符；服务器权威* |
| | `<predicts>` | 预测 | `{}` | *允许客户端预测* |
| **no_rollback** | | 内部 | `{no_rollback}` | *即将废弃；不允许事务* |

以下是现有的限制：

- `<suspends>` 和 `<decides>` 不能在同一函数上组合，
- `<converges>` 仅允许在 `<native>` 函数、抽象方法和类型签名上使用，
- 重复的说明符（例如 `<computes><computes>`）是错误的。

## 效果如何组合

可以把效果说明符想象成在位向量中设置位：每个基础效果对应一个位。没有任何标注的情况下，像 `GameUpdate` 这样的函数具有以下效果：

<!--NoCompile-->
<!-- 02 -->
```verse
GameUpdate():void = ...  # No explicit effects specified
```

| dictates | suspends | reads | writes | allocates | succeeds | fails |
| :---:    | :---:    | :---: | :---:  | :---:     | :---:    | :---: |
| ✔️       | ❌      | ✔️    | ✔️    | ✔️        | ✔️      | ❌    |

这意味着它具有效果 `dictates`、`reads`、`writes`、`allocates` 和 `succeeds`。这几乎等同于写 `<dictates><transacts>`，只是我们缺少表达该函数不会失败的方式。

顺便提一句：`fails` 和 `succeeds` 没有说明符，其原因在于，像 `<fails>` 这样的说明符意味着函数总是失败，永远不会返回值，且不能有可观察的副作用（它们会被失败撤销）。`succeeds` 效果是隐式的。

为函数添加标注只会影响该说明符所属家族中的位。例如，带有 `<reads>` 和 `<predicts>` 说明符的函数 `CheckPlayerStatus`：

<!--NoCompile-->
<!-- 03 -->
```verse
CheckPlayerStatus()<reads><predicts>:string = ...
```

具有以下效果：

| dictates | suspends | reads | writes | allocates | succeeds | fails |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| ❌ | ❌ | ✔️ | ❌ | ❌ | ✔️ | ❌ |

指定 `<reads>` 清除了 `writes` 和 `allocates` 位，`<predicts>` 清除了 `dictates` 位，其他位保持不变。

## 效果家族详解

### 基数性效果

基数性家族处理函数是否成功返回值。每个函数要么成功（返回其声明的类型），要么失败（不产生任何值）。大多数函数总是成功——它们是确定性的转换，总是产生输出。但标记了 `<decides>` 的函数可以失败，将失败转化为一种控制流机制。

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
    Health > 0.0      # Fails if health is zero or negative
    Health <= 100.0   # Fails if health exceeds maximum

# Usage
if (ValidateHealth[Player.Health]):
    # Health is valid, continue processing
    StartCombat()
```
<!--
#>
-->

`decides` 效果的优美之处在于它将验证与控制流统一了起来。你不需要先检查条件再根据它们行动——检查本身驱动了程序的路径。

### 堆效果

堆家族管理对可变内存的访问。这可能是理解程序行为最重要的家族，因为它决定了函数是否可以观察或修改状态。

`<computes>` 说明符标记纯函数——那些既不读取也不写入可变状态的函数。这些函数是确定性的：给定相同的输入，它们总是产生相同的输出。它们是计算的数学理想形态，转换数据而没有副作用。

<!--versetest-->
<!-- 05 -->
```verse
CalculateDamage(BaseDamage:float, Multiplier:float)<computes>:float =
    BaseDamage * Multiplier
```

`<reads>` 效果允许函数观察可变状态。它们可以看到变量和可变字段的当前值，但不能修改它们。这对于基于当前游戏状态的查询和计算非常有用。

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

`<writes>` 效果允许修改可变状态。具有此效果的函数可以使用 `set` 来更新变量和可变字段。`<writes>` 通常也需要 `<reads>`，例如当修改涉及读取当前值时。

实际上，`set` 指令默认是 `<transacts>`，因为语言中加入了*实时变量*。实时变量是其值依赖于其他变量的变量；当其中一个变量被 `set` 更新时，实时变量会被重新求值，可能涉及一些 `reads` 和 `allocates`。

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

`<allocates>` 效果表示创建可观察唯一值的函数——要么是标记为 `<unique>` 的对象，要么是包含可变字段的值。每次调用这样的函数都会返回一个不同的值，即使输入相同。

<!--NoCompile-->
<!-- 08 -->
```verse
game_entity := class<allocates>:
    ID:id
    var Position:vector3

CreateEntity(Pos:vector3)<allocates>:game_entity =
    game_entity{ID := GenerateID(), Position := Pos}
```

`<transacts>` 是函数的默认值。

### 挂起效果

挂起家族包含一个效果：`<suspends>`。具有此效果的函数可以暂停执行并在之后恢复，可能跨越多个游戏帧。这对于需要时间的操作至关重要：动画、冷却、等待玩家输入，或任何多帧行为。

<!--NoCompile-->
<!-- 09 -->
```verse
PlayVictorySequence()<suspends>:void =
    PlayAnimation(VictoryDance)
    Sleep(2.0)  # Wait 2 seconds
    PlaySound(VictoryFanfare)
    Sleep(1.0)
    ShowRewardsScreen()
```

`suspends` 效果具有传染性——任何调用挂起函数的函数本身必须标记为 `<suspends>`。这确保了你总是知道哪些函数可能需要时间才能完成。

虽然 `<suspends>` 和 `<decides>` 不能在同一函数上组合，但它们有特定的规则来说明如何在函数调用间交互。一个 `<suspends>` 函数可以调用一个 `<decides>` 函数，但*只能在失败上下文中*使用方括号 `[]` 语法——这确保了失败在本地处理，不会作为失败效果传播：

<!--versetest
DoAsyncWork():void={}
-->
<!-- 10 -->
```verse
ValidateInput(Value:int)<decides><computes>:void =
    Value > 0
    Value < 100

ProcessAsync(Value:int)<suspends>:void =
    # Valid: calling decides function in failure context
    if (ValidateInput[Value]):
        # Process valid input
        DoAsyncWork()

# Invalid: calling decides function outside failure context
# ProcessAsync(Value:int)<suspends>:void =
#     ValidateInput(Value)  # ERROR: must use [] syntax
```

一个 `<suspends>` 函数可以调用另一个 `<suspends>` 函数，但*不能使用失败处理语法*如 `?`：

<!--versetest-->
<!-- 11 -->
```verse
AsyncOp()<suspends>:?int = false

CallAsync()<suspends>:void =
    # Valid: calling suspends function normally
    X := AsyncOp()

    # Invalid: cannot use ? with suspends in suspends context
    # if (Value := AsyncOp()?):
```

这种非对称性存在是因为 `<suspends>` 和 `<decides>` 代表了根本不同的控制流机制——挂起关乎时间，而失败关乎成功/失败。混合它们的语法形式会造成关于正在处理的对象的不明确性。

### 内部效果

**[预发布]**：`<no_rollback>` 效果已废弃。

#### 预测效果

!!! note "未发布的功能"
    `<predicts>` 效果尚未发布。

预测家族决定了代码在客户端-服务器架构中的运行位置。默认情况下，函数具有 `dictates` 效果，意味着它们在服务器上以权威方式运行。`<predicts>` 说明符允许函数在客户端上预测性地运行以获得响应速度，然后由服务器进行验证并可能修正结果。

<!--NoCompile-->
<!-- 12 -->
```verse
HandleJumpInput()<predicts>:void =
    # Runs immediately on the client for responsiveness
    StartJumpAnimation()
    PlayJumpSound()

    # Server will validate and correct if needed
    PerformJump()
```

即使在网络延迟的情况下，这也实现了响应式游戏体验，因为玩家能立即看到自己动作的反馈，同时服务器维护着权威状态。

#### 发散效果

目前处于规划阶段，发散家族将跟踪函数是否保证终止。`<converges>` 说明符标记了可证明在有限时间内完成的函数，而没有它的函数可能永远运行。这对于构造函数和初始化代码尤其重要。

`<converges>` 说明符可用于：

- 保证终止的 `<native>` 函数
- 类和接口中的抽象方法签名
- 类型表达式中的函数签名

常规函数实现不能使用 `<converges>`——只有抽象上下文中的声明或作为内在函数才能使用。

## 效果组合

效果通常沿调用链向上传播——一个函数必须声明它所调用的函数的所有效果。然而，某些语言构造可以隐藏特定效果，阻止它们继续传播。

`if` 表达式会在其失败上下文中隐藏 `fails` 效果，因此条件中的失败不会传播到外层函数：

<!--versetest-->
<!-- 13 -->
```verse
SafeMod(A:int, B:int)<computes>:int =
    if (V:= Mod[A,B])  then V else 0
```

`spawn` 表达式隐藏了 `suspends` 效果，允许即时函数启动异步操作，这些操作独立继续执行：

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

StartBackgroundMusic():void =  # No <suspends>
    spawn:
        Play() # Suspends effect hidden by spawn
```

如前所述，在 `<suspends>` 代码（包括 `spawn`）中不允许出现失败。绕过这一限制的一种方法是使用 `option` 表达式将失败转换为可选值，将 `fails` 效果转化为一个常规值，无需 `<decides>` 即可处理：

<!--versetest
item:=struct{}
-->
<!-- 16 -->
```verse
TryGetItem(Items:[]item, Index:int):?item =
    option{Items[Index]}  # Array access might fail, option catches it
```

`defer` 表达式提供了在退出作用域时运行的清理代码，但有严格的效果限制：

- 不能包含 `<suspends>` 操作——延迟执行的代码必须同步执行
- 不能包含 `<decides>` 操作——延迟执行的代码必须始终成功

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
        ReleaseResource(R)  # Valid: transacts allowed in defer

    # Process resource with async operations
    DoAsyncWork()
```

这些约束确保了清理代码可预测且完整地执行，不会出现可能导致资源处于不一致状态的挂起或失败。

## 子类型与类型兼容性

效果标注在函数类型之间建立了子类型关系。理解效果如何与类型兼容性交互，对于将函数存储在变量中、作为参数传递或在不同实现之间选择至关重要。

具有**较少效果**的函数可以用在期望具有**较多效果**的函数的位置。这就是效果子类型——一个做得更少的函数，与允许更多效果的上文兼容：

<!--versetest-->
<!-- 18 -->
```verse
# Pure function with only computes
PureAdd(X:int)<computes>:int = X + 1

# Variable that expects computes and decides
F:type{_(:int)<computes><decides>:int} = PureAdd

# Calling through the variable
Result := F[5]  # Must use [] syntax since type has <decides>
# Returns option{6} since PureAdd never fails
```

在这个例子中，`PureAdd` 只有 `<computes>`，但它可以赋值给一个期望 `<computes><decides>` 的变量。这个纯函数是可失败接口的有效实现——它只是从来不使用这个失败能力。

这一原则适用于所有效果：

<!--versetest-->
<!-- 19 -->
```verse
# Function with <computes>
Compute(X:int)<computes>:int = X * 2

# Can assign to types expecting more effects
F1:type{_(:int)<computes><decides>:int} = Compute
F2:type{_(:int)<transacts>:int} = Compute
F3:type{_(:int)<reads>:int} = Compute

# All valid - Compute does less than what's allowed
```

在决定子类型时，效果有以下影响：

- `<computes>` 是 `<reads>`、`<transacts>` 以及与 `<decides>` 任意组合的子类型
- `<reads>` 是 `<transacts>` 的子类型
- 不带 `<decides>` 的函数是带 `<decides>` 的函数的子类型
- 不带 `<suspends>` 的函数是带 `<suspends>` 的函数的子类型（在兼容的情况下）

虽然你可以通过子类型添加效果，但**不能移除**函数实际具有的效果：

<!--versetest-->
<!-- 20 -->
```verse
Validate(X:int)<computes><decides>:int =
    X > 0
    X

# ERROR: Cannot assign to type without <decides>
# F:type{_(:int)<computes>:int} = Validate
# The function CAN fail, but the type doesn't allow it
```

类似地，具有堆效果的函数不能赋值给纯类型：

<!--NoCompile-->
<!-- 21 -->
```verse
counter := class:
    var Count:int = 0

Increment(C:counter)<transacts>:int =
    set C.Count = C.Count + 1
    C.Count

# ERROR: Cannot assign transacts function to computes type
# F:type{_(:counter)<computes>:int} = Increment
# The function writes state, type doesn't permit it
```

这一限制保证了类型安全——类型签名是关于函数可能执行什么效果的承诺，而实际函数必须兑现该承诺。

当你有条件地在具有不同效果的函数之间选择时，结果表达式具有所有可能效果的并集。这就是*效果合并*——编译器保守地假设结果可能执行任何分支可能执行的任何效果：

<!--versetest-->
<!-- 22 -->
```verse
# Functions with different effects
PureFunction(X:int)<computes>:int = X + 1
FailableFunction(X:int)<computes><decides>:int =
    X > 0
    X + 1

# Conditional selection joins effects
SelectFunction(UseFailable:logic):type{_(:int)<computes><decides>:int} =
    if (UseFailable?):
        FailableFunction  # Has <computes><decides>
    else:
        PureFunction      # Has <computes>
    # Result type must account for both: <computes><decides>

# The returned function might fail (from FailableFunction)
# or might not (from PureFunction), so type must include <decides>
F := SelectFunction(true)
Result := F[5]  # Must use [] because result type has <decides>
```

效果合并适用于所有在函数间进行选择的控制流：

<!--versetest-->
<!-- 23 -->
```verse
Identity(X:int)<computes>:int = X

DecidesIdentity(X:int)<computes><decides>:int =
    X > 0
    X

TransactsIdentity(X:int)<transacts>:int = X

# Joining <computes> and <computes><decides>
F1:type{_(:int)<computes><decides>:int} =
    if (true?):
        Identity
    else:
        DecidesIdentity
# Result: <computes><decides> (union of effects)

# Joining <computes><decides> and <transacts>
F2:type{_(:int)<decides><transacts>:int} =
    if (true?):
        DecidesIdentity  # <computes><decides>
    else:
        TransactsIdentity  # <transacts>
# Result: <decides><transacts> (union of effects)
```

效果子类型实现了灵活的函数参数：

<!--versetest
PureAdd(:int)<computes>:int=1
Validate(:int)<computes><decides>:int=1
Increment(:int)<transacts>:int=1
-->
<!-- 25 -->
```verse
# Accepts any function that doesn't exceed <transacts><decides>
ProcessValues(
    Data:[]int,
    Transform(:int)<transacts><decides>:int
):[]int =
    for (Value:Data, Result := Transform[Value]):
        Result

# Can pass pure functions
ProcessValues(array{1, 2, 3}, PureAdd)

# Can pass failable functions
ProcessValues(array{1, 2, 3}, Validate)

# Can pass transactional functions
ProcessValues(array{1, 2, 3}, Increment)
```

效果子类型使函数组合自然地工作：

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

# If we want to allow more effects:
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

# Can pass functions with fewer effects
ComposeFlexible(PureFunction, PureFunction)
ComposeFlexible(PureFunction, FailableFunction)
```

下表总结了效果与类型的交互：

| 场景 | 有效？ | 说明 |
|----------|--------|-------------|
| 将 `<computes>` 赋值给 `<computes><decides>` 类型 | ✓ | 通过子类型添加效果 |
| 将 `<computes>` 赋值给 `<transacts>` 类型 | ✓ | 纯类型是事务类型的子类型 |
| 将 `<reads>` 赋值给 `<transacts>` 类型 | ✓ | Reads 是事务类型的子类型 |
| 将 `<computes><decides>` 赋值给 `<computes>` 类型 | ✗ | 不能移除 `<decides>` |
| 将 `<transacts>` 赋值给 `<computes>` 类型 | ✗ | 不能移除堆效果 |
| 在 `<computes>` 和 `<decides>` 之间选择 | 结果：`<computes><decides>` | 效果合并 |
| 在 `<reads>` 和 `<transacts>` 之间选择 | 结果：`<transacts>` | 效果合并 |

这些规则确保效果标注始终是值得信赖的契约——函数可以做得比声明更少（子类型），但绝不能更多，而有条件的选择会保守地考虑所有可能性（合并）。

## 数据类型上的效果

类、结构体和接口可以用效果说明符进行标注，这些说明符适用于它们的构造函数。这对于确保创建某些对象保持纯粹或具有有限效果特别有用：

<!--versetest-->
<!-- 28 -->
```verse
# Pure data structure - constructor has no effects
vector3 := struct<computes>:
    X:float = 0.0
    Y:float = 0.0
    Z:float = 0.0

# Entity that requires allocation due to unique identity
monster := class<unique><allocates>:
    Name:string
    var Health:float = 100.0
```

类、接口和结构体**不能**标记为 `<suspends>` 或 `<decides>`：

<!--versetest-->
<!-- 29 -->
```verse
# Valid effect specifiers for classes/interfaces/structs:
valid_class := class<computes>{}
valid_interface := interface<computes>{}
valid_struct := struct<transacts>{}

# Invalid: async and failable effects not allowed
# invalid_class := class<suspends>{}      # ERROR
# invalid_interface := interface<decides>{}  # ERROR
# invalid_struct := struct<decides>{}     # ERROR
```

这一限制适用于类/结构体的**声明**本身——原型构造函数 `my_class{...}` 不能是可失败或可挂起的。然而，**构造函数函数**可以使用 `<decides>`：

<!--NoCompile-->
<!-- 29a -->
```verse
# The class declaration cannot be <decides>
my_class := class:
    Value:int

# But a constructor function CAN be <decides>
MakeMyClass<constructor>(V:int)<transacts><decides> := my_class:
    Value := block:
        V > 0      # Fails if V <= 0
        V < 100    # Fails if V >= 100
        V
```

这提供了在需要时可失败的构造——对象要么完整创建，要么构造函数函数失败且不创建任何对象。

字段默认值和类中的块子句有严格的效果要求：

<!--versetest-->
<!-- 30 -->
```verse
# Field initializers must use pure functions
HelperFunction()<transacts>:int = 42

# Invalid: field initializers cannot call transacts functions
# bad_class := class:
#     Value:int = HelperFunction()  # ERROR

# Block clauses must respect class effects
valid_class := class<transacts>:
    var Counter:int = 0
    block:
        set Counter = 1  # Valid: class has transacts

# Invalid: block effect exceeds class effect
# bad_class := class<computes>:
#     var Counter:int = 0
#     block:
#         set Counter = 1  # ERROR: computes class cannot write
```

类成员初始化器和块子句被隐式限制为不能超过类声明的效果。这确保了构造类的实例时遵守类的效果契约。

限制构造函数的效果有助于维护架构边界。数据传输对象可以用 `<computes>` 保持纯粹，确保它们只是数据载体。游戏实体可能需要 `<allocates>` 来保证唯一标识，而服务对象可能需要完整的 `<transacts>` 来初始化其状态。

### 接口构造效果约束

当类或接口继承自具有构造效果的接口时，它们必须声明至少相同的构造效果：

<!--versetest-->
<!-- 31 -->
```verse
# Interface with transacts effect
transacting_interface := interface<transacts>{}

# Valid: class has at least transacts
valid_class := class<transacts>(transacting_interface){}

# Invalid: class has less effects than interface requires
# invalid_class := class<computes>(transacting_interface){}  # ERROR
```

接口字段初始化器也必须尊重接口声明的构造效果：

<!--versetest-->
<!-- 32 -->
```verse
transacting_class := class<transacts>{}

# Valid: interface has transacts, field initializer has transacts
valid_interface := interface<transacts>:
    Instance:transacting_class = transacting_class{}

# Invalid: interface has computes, but field initializer has transacts
# invalid_interface := interface<computes>:
#     Instance:transacting_class = transacting_class{}  # ERROR
```

这些约束确保了构造效果在继承层次结构中正确流动。继承某个接口的类必须能够构造该接口的所有字段，这要求它至少具有相同的构造效果。

## 使用效果

在设计函数时，从最小所需效果开始，只在必要时扩展。带有 `<computes>` 的纯函数最容易测试、推理和组合。添加 `<reads>` 用于需要观察状态时，添加 `<writes>` 用于需要修改状态时，添加 `<decides>` 用于需要基于失败的控制流时。

效果是你 API 契约的一部分。一旦发布，减少效果是向后兼容的变更（你的函数比以前做得更少），但增加效果是破坏性变更（你的函数现在比调用者可能预期的做得更多）。请深思熟虑地设计你的效果签名，因为它们将成为对用户的承诺。

请记住，过度指定效果是允许的，有时甚至是有益的。一个标记为 `<reads>` 的函数可以在内部实现为纯 `<computes>`。这为未来的变更提供了灵活性，而不会破坏现有的调用者。

<!--versetest
weapon:=struct<computes>{Type:weapon_type,Dammage:int}
weapon_type:=enum:
    Sword
-->
<!-- 32 -->
```verse
# API promises it might read state
GetDefaultWeapon<public>()<reads>:weapon =
    # But current implementation is pure
    weapon{Type := weapon_type.Sword, Dammage := 10}
```

过度指定效果可以为 API 的未来变更做好准备，避免后来产生破坏性变更。例如，将当前纯函数标记为 `<reads>` 允许你在未来添加状态观察功能而不会破坏兼容性。

## 向后兼容性

函数的效果是向后兼容性检查的一部分。当更新作为已发布 API 一部分的函数时，新版本可以具有"更少的位"，但不能更多。因此，之前版本中标记为 `<reads>` 的函数不能改为 `<transacts>`，但可以细化为 `<computes>`。

效果将副作用从隐藏的陷阱转变为可见、可验证的契约。通过将隐式变为显式，Verse 帮助你编写更可预测、更可维护和更正确的代码。效果系统不是负担——它是一种工具，帮助你清晰地表达意图，并让编译器验证你的实现是否符合该意图。