# 并发

并发是 Verse 的一个基本方面，允许您控制
时间的流动就像你控制程序的流动一样自然。与传统不同
事后才考虑并发性的编程语言，
Verse 通过以下方式将时间流控制直接集成到语言中：
专用的表情和效果。

游戏开发本质上需要同时管理多个
活动。想想一个典型的游戏场景：NPC 巡逻他们的路线
当粒子效果发挥时，UI 元素会随着冷却计时器而动画化
倒计时，背景音乐在曲目之间逐渐消失。所有这些
活动同时发生，时间上重叠。Verse认识到
这个现实并提供一流的语言结构来表达
这些平行的行为自然而然。

该语言通过结构化和
非结构化并发原语，全部基于异步概念构建
可以在多个模拟中暂停和恢复的表达式
更新。这种方法使并发编程感觉像
编写顺序代码，同时避免传统的陷阱
基于线程的并发，例如数据争用和死锁。

## 核心概念

### 立即表达式与异步表达式

每个表达式都属于以下两类之一：立即或
异步。理解这种区别对于与他人合作至关重要
Verse 的并发模型。

立即表达式立即计算，完全完成
在当前模拟更新或框架内。这些包括大多数
您希望立即发生的基本运算：算术
计算、变量访问、简单函数调用和数据
结构操纵。当您写入 `X := 5 + 3` 时，添加
立即发生，分配立即完成，并执行
移动到下一个语句，没有任何中断的可能性。

另一方面，异步表达式有可能采用
评估时间，可能跨越多个模拟
更新。它们代表了本质上需要时间的操作
游戏世界：动画播放、计时器倒计时、网络
请求完成，或者只是等待下一帧。一个异步
如果条件已经满足，表达式可能会立即完成
满足，或者它可能会暂停执行，允许其他代码运行
它等待合适的时机恢复。

### 模拟更新

模拟更新（或勾选）代表游戏的一个步骤
模拟。模拟和渲染是**独立的**——它们运行
以不同的速率，并且在现代发动机中彼此解耦。

每个刻度都会处理输入、更新游戏逻辑、运行物理，以及
推进游戏状态。 Verse 的并发模型让你思考
就逻辑时间流而言 - 异步表达式在滴答处暂停
边界并在满足条件时在未来的蜱虫中恢复。

异步表达式自然地与此更新周期保持一致。当
异步表达式挂起，它将控制权交还给游戏引擎，
它继续处理其他任务和渲染帧。的
当其条件满足时，暂停的表达将在未来的更新中恢复
满足，从中断的地方无缝地继续。这个
协作模型确保长时间运行的操作不会阻塞
游戏的响应能力。

### `suspends` 效果

并发操作需要 `<suspends>` 效果说明符（请参阅
[效果](13_effects.md))。标有`<suspends>`的功能可以使用
并发表达式，调用其他挂起函数，以及
合作产生执行：

<!--versetest-->
<!-- 01 -->
```verse
# 标有 suspends 的函数可以使用简单表达式
MyAsyncFunction()<suspends>:void =
    Sleep(1.0)  # 暂停执行
    Print("One second later!")

# 常规函数不能使用异步表达式
MyImmediateFunction():void =
    # Sleep(1.0)  # ERROR: Cannot use Sleep without suspends
    Print("This happens immediately")
```
`<suspends>` 效果通过调用链（任何函数）传播
调用挂起函数本身必须标记为 `<suspends>`。

## 结构化并发

结构化并发代表了 Verse 最优雅的设计之一
决定。而不是产生存活的线程或任务
独立且需要手动生命周期管理、结构化
并发表达式的生命周期自然与其相关
封闭范围。当您进入结构化并发块时，您
知道其中的所有并发操作都将得到妥善管理
并在块退出时进行清理，防止资源泄漏
使代码更容易推理。

这种方法反映了我们对顺序代码的看法。就像一个
顺序语句块有明确的开始和结束，
结构化并发操作具有定义的生命周期。你可以筑巢
使用相同的心智模型来构建它们、组合它们并推理它们
用于常规代码块。

### 效果要求

所有结构化并发表达式（`sync`、`race`、`rush` 和
`branch`) 需要 `<suspends>` 效果。你不能使用这些
在立即（非挂起）函数中构造：

<!--versetest
Operation1<public>()<suspends>:void = {}
Operation2<public>()<suspends>:void = {}
-->
<!-- 02 -->
```verse
# 有效：挂起函数中的结构化并发
ProcessConcurrently()<suspends>:void =
    sync:
        Operation1()
        Operation2()

# 无效：无法在没有挂起的情况下使用同步
# ProcessImmediate():void =
#     sync:  # ERROR: sync requires suspends
#         Operation1()
```
### 同步表达式

`sync` 表达式体现了最简单的并发模式：
同时处理多项事情并等待所有事情完成。当
您拥有可以从并行中受益的独立操作
执行时，`sync` 提供了一种干净的方式来表达这种并行性
同时保持确定性行为。

<!--versetest
AsyncOperation1()<suspends>:int=1
AsyncOperation2()<suspends>:int=1
AsyncOperation3()<suspends>:int=1
F()<suspends>:void={
Results := sync:
    AsyncOperation1()
    AsyncOperation2()
    AsyncOperation3()
Print("All operations complete with results: {Results(0)} {Results(1)} {Results(2)}")
}
<#
-->
<!-- 04 -->
```verse
# 所有表达式同时开始并且必须全部完成
Results := sync:
    AsyncOperation1()  # 返回值1
    AsyncOperation2()  # 返回值2
    AsyncOperation3()  # 返回值3

Print("All operations complete with results: {Results(0)} {Results(1)} {Results(2)}")
```
<!-- #> -->

在 `sync` 块内，所有子表达式开始执行
本质上是同一时刻。然后同步表达式耐心等待
对于每个要完成的子表达式，无论多长时间
每个都单独进行。如果一项操作在几毫秒内完成
当另一个需要几秒钟时，同步会继续等待，直到那个
最后一个操作完成。只有这样，执行才会继续过去
同步块。

同步的美妙之处在于它的可预测性。你总能得到结果
来自所有子表达式，始终按照您编写它们的顺序，
整齐地包装在一个元组中。这使得同步非常适合场景
当您需要多条数据或需要确保多个
系统已准备就绪，然后再继续。并行加载游戏资源，
同时初始化多个子系统，或收集数据
来自多个来源的所有内容都受益于同步的全有或全无方法。

考虑一个更复杂的示例来演示同步的可组合性：

<!--versetest
LoadTexture()<suspends>:void={}
ApplyTexture()<suspends>:void={}
LoadSound()<suspends>:void={}
PlaySound()<suspends>:void={}
LoadModel():void={}
ProcessData(:int,:int,:int):void={}
FetchDataA()<suspends>:int=1
FetchDataB()<suspends>:int=1
FetchDataC():int=1
F()<suspends>:void={
sync:
    block:  # Task 1 - sequential operations
        LoadTexture()
        ApplyTexture()
    block:  # Task 2 - parallel to task 1
        LoadSound()
        PlaySound()
    LoadModel()  # Task 3 - parallel to tasks 1 and 2
ProcessData(sync:
    FetchDataA()
    FetchDataB()
    FetchDataC()
)
}
<#
-->
<!-- 05 -->
```verse
# 用于复杂操作的嵌套块
sync:
    block:  # 任务 1 - 顺序操作
        LoadTexture()
        ApplyTexture()
    block:  # 任务 2 - 与任务 1 并行
        LoadSound()
        PlaySound()
    LoadModel()  # 任务 3 - 与任务 1 和 2 并行

# 直接使用同步结果作为函数参数
ProcessData(sync:
    FetchDataA()
    FetchDataB()
    FetchDataC()
)
```
<!--versetest
#>
-->

### `race` 表达式

`sync` 表示协作，`race` 表示竞争。`race` 表达式会同时启动
多个异步操作，但只关心最先完成的操作。一旦某个子表达式完成，
`race` 会立即取消其余所有子表达式，并继续使用获胜者的结果。
这种赢家通吃的语义非常适合超时模式、后备机制，以及任何需要
最快响应的场景。

<!--versetest
SlowOperation()<suspends>:int=0
FastOperation()<suspends>   :int=0
MediumOperation()<suspends>   :int=0

TestRace()<suspends>:void =
    # First to complete wins, others are canceled
    Winner := race:
        SlowOperation()     # Takes 5 seconds
        FastOperation()     # Takes 1 second - wins!
        MediumOperation()   # Takes 3 seconds

    Print("Winner result: {Winner}")  # Prints FastOperation's result 
<#
-->
<!-- 06 -->
```verse
# 最先完成者获胜，其他者取消
Winner := race:
    SlowOperation()     # 需要 5 秒
    FastOperation()     # 需要 1 秒 - 获胜！
    MediumOperation()   # 需要3秒

Print("Winner result: {Winner}")  # 打印 FastOperation 的结果
```
<!-- #> -->

在真实游戏场景中，`race` 的作用会更加明显。设想你同时查询
多个服务器并采用最先响应的数据，或者等待玩家完成动作或超时。
`race` 能优雅地表达这些模式，而无需复杂的状态管理或手动取消逻辑。

`race` 的取消是即时且彻底的。获胜者一出现，其余子表达式就会
收到取消信号并开始清理。这不仅是一种优化；对于资源管理以及
避免不再需要的操作产生副作用也至关重要。

**比赛中的类型处理：**

类型系统会优雅地处理 `race`。由于只有一个子表达式返回结果，
`race` 的结果类型至多是所有子表达式最具体的公共超类型。这既
保证了类型安全，又保留了让不同操作相互竞争的灵活性：

<!--versetest
base_class := class:
    Value:int

derived_a := class(base_class):
    Name:string = "A"

derived_b := class(base_class):
    Name:string = "B"

GetA()<suspends>:derived_a = derived_a{Value := 1}
GetB()<suspends>:derived_b = derived_b{Value := 2}

F()<suspends>:void={
Result:base_class = race:
    GetA()
    GetB()
SameTypeResult:int = race:
    block:
        Sleep(1.0)
        42
    block:
        Sleep(2.0)
        100
}
<#
-->
<!-- 07 -->
```verse
base_class := class:
    Value:int

derived_a := class(base_class):
    Name:string = "A"

derived_b := class(base_class):
    Name:string = "B"

GetA()<suspends>:derived_a = derived_a{Value := 1}
GetB()<suspends>:derived_b = derived_b{Value := 2}

# 结果类型是base_class（公共超类型）
Result:base_class = race:
    GetA()  # 返回衍生_a
    GetB()  # 返回衍生_b
# 结果是base_class，可以保存任意派生类型

# 如果所有表达式返回相同的类型，则这就是结果类型
SameTypeResult:int = race:
    block:
        Sleep(1.0)
        42
    block:
        Sleep(2.0)
        100
# 结果类型为int
```
<!-- #> -->

模式涉及添加标识符来确定哪个子表达式获胜：

<!--versetest
SlowOperation()<suspends>:int=0
FastOperation()  <suspends> :int=0
InfiniteOperation()  <suspends> :int=0
F()<suspends>:void={
WinnerID := race:
    block:
        SlowOperation()
        1
    block:
        FastOperation()
        2
    block:
        loop:
            InfiniteOperation()
        3

case(WinnerID):
    1 => Print("Slow operation won somehow!")
    2 => Print("Fast operation won as expected")
    _ => Print("Impossible!")
}
<#
-->
<!-- 08 -->
```verse
# 添加标识符以确定哪个表达式获胜
WinnerID := race:
    block:
        SlowOperation()
        1  # 如果获胜则返回 1
    block:
        FastOperation()
        2  # 如果获胜则返回 2
    block:
        loop:
            InfiniteOperation()
        3  # 永不返回

case(WinnerID):
    1 => Print("Slow operation won somehow!")
    2 => Print("Fast operation won as expected")
    _ => Print("Impossible!")
```
<!-- #> -->

### `rush` 表达式

`rush` 表达式位于 `sync` 和 `race` 之间。和 `race` 一样，
它会在第一个子表达式完成后结束；不同之处在于，它不会取消其余
分支。这样便可在一个操作给出结果后继续执行，同时允许其他操作
在后台继续工作。

<!--versetest
LongBackgroundTask()<suspends>:int=0
QuickCheck() <suspends>  :int=0
MediumTask() <suspends>  :int=0
F()<suspends>:void={
FirstResult := rush:
    LongBackgroundTask()
    QuickCheck()
    MediumTask()

Print("First result: {FirstResult}")
}
<#
-->
<!-- 09 -->
```verse
# 最先完成者获胜，其他任务继续运行
FirstResult := rush:
    LongBackgroundTask()   # `rush` 完成后继续
    QuickCheck()          # 首先完成
    MediumTask()          # `rush` 完成后也继续

Print("First result: {FirstResult}")
# LongBackgroundTask 和 MediumTask 目前正在运行！
```
<!-- #> -->

`rush` 适用于希望先获得响应、但仍让所有操作最终完成的场景。
考虑预加载游戏资源：
您可能会开始同时加载多个关卡，开始游戏
当前关卡加载后，同时继续缓存
背景中的其他级别。或者考虑一下成绩检查，
您想要在一项成就解锁后立即通知玩家的位置
同时继续检查其他人。

`rush` 的不可取消特性需要仔细考量。后台任务即使在 `rush` 完成后
仍会继续消耗资源并执行操作，直到自然完成或其所在的异步上下文
结束。因此它很强大，但若用于可能永不完成或消耗大量资源的操作，
也可能带来风险。

有一项重要的技术限制：`rush` 不能直接用在 `loop` 或 `for` 等
迭代表达式的主体中。`rush` 的后台任务与迭代之间的交互可能导致
资源累积。若在循环中需要类似 `rush` 的行为，请将其封装在异步
函数中，再从迭代中调用该函数。

### 从并发分支返回

`sync`、`race` 或 `rush` 分支中的 `return` 语句会导致
封闭的*函数*返回，而不只是退出该分支。结构化
并发表达式被放弃，推迟到已经有
开始执行，尚未开始的分支则会被直接
跳过了。

<!--versetest
CoroUtils := module:
    LogEvent(Msg:string):void = {}
    GetEventLogString()<computes>:string = ""
    WaitTicks(N:int)<suspends>:void = {}
    Tick(N:int):void = {}
-->
<!-- 09b -->
```verse
Log(Msg:string):void = CoroUtils.LogEvent(Msg)

MaybeReturn(Delay:int, Value:?string)<suspends>:string =
    defer { Log("a") }
    CoroUtils.WaitTicks(Delay)
    if (V := Value?):
        return V         # 来自 MaybeReturn 返回
    Log("done")
    "no-return"

Wrapper(Value:?string)<suspends>:string =
    defer { Log("z") }
    R := sync:
        block:
            MaybeReturn(0, Value)   # 第 1 臂
        block:
            defer { Log("b") }
            CoroUtils.WaitTicks(1)
            Log("2")
            2
    "{R(0)}"
```
当`Value`置位时，机械臂1内部执行`return V`
`MaybeReturn`。这完全退出 `Wrapper` — `sync` 是
被放弃，臂 2 永远不会完成，并在展开期间推迟运行。
当`Value`未设置时，臂1正常完成，`sync`等待
让双臂完成。

### 分支表达式

`branch` 表达式表示“即发即弃”并发性
结构化的上下文。当你遇到一个分支时，它会立即
开始将其主体作为后台任务执行，然后，没有任何
停顿或犹豫，继续下一个表达。没有
等待，没有结果收集，只是一个任务分拆来完成其工作
而主流则畅通无阻。

<!--versetest
AsyncOperation1()<computes><suspends>:int=0
ImmediateOperation()<computes> :int=0
AsyncOperation2() <suspends><computes>  :int=0
F()<suspends>:void={
branch:
    AsyncOperation1()
    ImmediateOperation()
    AsyncOperation2()
}
<#
-->
<!-- 10 -->
```verse
branch:
    # 该块独立运行
    AsyncOperation1()
    ImmediateOperation()
    AsyncOperation2()

# 此处立即继续执行
Print("Branch started, continuing main flow")
# 分支块仍在后台运行
```
<!-- #> -->


Branch 擅长处理不应中断的副作用
主要游戏流程，但如果封闭范围内，失败是可以接受的
结束。考虑触发随时间推移而发挥的粒子效果，
开始逐渐淡入或预加载的背景音乐
可能很快需要的资产。这些操作需要进行，但是
没有理由让玩家等待他们完成。分公司
让您直接表达这种“开始并继续”模式。

分支的关键语义是它的**取消行为**：
当执行离开时，分支任务会自动取消
封闭函数作用域，无论这是否通过正常情况发生
完成、失败或来自上方的取消。这是
工作中的结构化并发保证——分支不能比它们的生命周期长
父上下文，防止孤立任务累积。但是
这也意味着分支对于*必须*的工作来说是错误的选择
完整，例如记录分析事件或保存玩家进度。对于
这些任务，请使用 `spawn` 代替，它独立于其运行
创造范围。

与rush一样，branch也面临着迭代表达式的限制。你
不能直接在循环内或 for 主体中使用分支，因为这可能
导致无限数量的后台任务。解决方法
保持不变：将分支封装在异步函数中并调用
迭代中的该函数。

## 非结构化并发

### 生成表达式

虽然结构化并发可以处理大多数并发编程需求
优雅地，有时你需要摆脱层级任务
结构。 `spawn` 表达式是 Verse 对
非结构化并发，允许您启动异步操作
它独立于其创造范围而存在。将 Spawn 视为
应急手段——需要时很有用，但不应作为典型并发模式的首选
对于典型的并发模式。

<!--versetest
LongRunningTask()  <suspends> :int=0
-->
<!-- 11 -->
```verse
# spawn 返回一个可控制的 task(t) 对象
BackgroundTask:task(int) = spawn{LongRunningTask()}

# 或者“即发即弃”而不捕获任务
spawn{LongRunningTask()}
Print("Spawned task continues even after this scope exits")
```
Spawn 的独特之处在于它能够在任何地方工作。与所有不同
需要异步上下文的结构化并发表达式，
spawn 在立即函数、类构造函数、模块中工作
初始化——任何可以编写代码的地方。这种普遍性来了
带着责任。您生成的任务成为自由代理，
无论代码发生什么情况都会继续工作
创建了它。没有自动清理，没有父子关系
关系，只是追求其目标的独立任务。

生成的函数必须具有 `<suspends>` 效果。你**不能**
具有 `<decides>` 效果的 spawn 函数：

<!--versetest-->
<!-- 12 -->
```verse
AsyncWork()<suspends>:void =
    Sleep(1.0)
    Print("Background work complete")

FailableWork()<decides>:void =
    false?  # 可能会失败

# 有效：产卵暂停功能
spawn{AsyncWork()}

# 无效：无法生成决定功能
# spawn{FailableWork()}  # ERROR: spawn requires suspends, not decides
```
存在此限制是因为生成的任务独立运行
没有父母来处理他们的失败。由于 `<suspends>` 和
`<decides>` 不能组合在同一功能上，并且需要spawn
`<suspends>`，无法生成具有 `<decides>` 的函数。如果你
需要产生失败的工作，将其包装在一个挂起函数中
内部处理失败：

<!--versetest
FailableWork<public>()<computes><decides>:void = {}
-->
<!-- 13 -->
```verse
SafeFailableWork()<suspends>:void =
    if (FailableWork[]):
        Print("Work succeeded")
    else:
        Print("Work failed, but handled gracefully")

spawn{SafeFailableWork()}  # 有效 - 内部处理失败
```
Spawn 在特定的架构模式中找到了自己的位置。全球
全程监控游戏状态的后台服务
会话，即使触发也必须完成的清理任务
上下文结束，或立即代码需要的集成点
触发异步操作——这些场景证明了到达spawn的合理性
优于结构化替代方案。

与树枝的对比阐明了设计理念。分公司
为您提供结构化的即发即忘并发性，但它的任务是
当封闭范围退出时取消。 Spawn 为您提供的任务
比他们的创造范围更长久——当工作*必须*完成时使用它
无论启动它的代码发生了什么。选择分行
何时可以接受取消；当不是时选择spawn。

**使用衍生任务：**

`spawn` 表达式返回 `task(t)` 对象，其中 `t` 是
生成函数的返回类型。该任务对象提供方法
控制和查询生成的操作 - 您可以取消它，等待
它完成，或检查其当前状态。当spawn创建时
不需要管理的独立任务，可以访问
任务对象使您能够在需要时进行干预。参见“
任务（t）类型”部分，了解有关任务对象的完整详细信息和
他们的能力。

## 任务(t) 类型

`task(t)` 类型表示执行异步的句柄
操作，其中 `t` 是操作的返回类型。而Verse
在幕后自动为所有异步创建任务
表达式，只有 `spawn` 可以让您直接访问任务对象
您可以控制和查询。

<!--versetest-->
<!-- 14 -->
```verse
# spawn 返回 task(t)，其中 t 为返回类型
BackgroundWork()<suspends>:int =
    Sleep(2.0)
    42

MyTask:task(int) = spawn{BackgroundWork()}
# MyTask 是生成操作的句柄
```
任务对象提供了丰富的接口来管理异步操作：
您可以取消它们，等待它们完成，并查询它们
当前状态。这种控制对于实现鲁棒性至关重要
需要协调多个独立的并发系统
操作。


任务在其生命周期内会经历几个不同的状态：

**活动**：任务当前正在运行或挂起，但尚未执行
尚未完成。它仍在工作或等待恢复。

**完成**：任务成功完成并返回
结果。一旦完成，任务就不会再改变状态。 （终端状态）

**已取消**：任务在完成之前已被取消。这是
最终状态——取消的任务无法恢复。

**已解决**：如果任务已达到已完成状态，则任务已解决
或取消状态。已解决的任务不再执行。 （终端状态）

**不间断**：任务如果完成则不间断
成功，没有被取消。这相当于
完成状态。 （别名）

**中断**：如果任务被取消，则任务被中断。这是
相当于取消状态。 （别名）

### 任务.取消()

!!!注意“未发布的功能”
    此时Cancel()方法还没有被释放。
	
`Cancel()` 方法请求取消任务。这是一个安全
可以在任何状态下的任何任务上调用的操作：

<!--versetest
BackgroundWork()<transacts><suspends>:void={Sleep(1.0)}
F()<suspends>:void= {
LongTask:task(void) = spawn{BackgroundWork()}
LongTask.Cancel()
LongTask.Cancel()
}
<#
-->
<!-- 16 -->
```verse
LongTask:task(void) = spawn{BackgroundWork()}

# 请求取消
LongTask.Cancel()

# 多次通话安全
LongTask.Cancel()  # 没有错误

# 可以安全地调用已完成的任务（没有效果）
```
<!-- #> -->

取消是合作性的——任务不会停止
立即。相反，它收到一个取消信号，即
在下一个暂停点进行检查。然后任务就展开了
优雅地允许清理代码运行。请参阅“悬挂点和
有关取消何时生效的详细信息，请参见下文的“取消”。

在已完成的任务上调用 `Cancel()` 是安全的，不会产生任何影响。
效果。这意味着您可以取消任务而不必担心竞争
完成和取消之间的条件。

### 任务.Await()

`Await()` 方法挂起调用上下文，直到任务
完成，然后返回任务结果：

<!--versetest
BackgroundWork()<computes><suspends>:int=42
F()<suspends>:void={
ComputeTask:task(int) = spawn{BackgroundWork()}
Result:int = ComputeTask.Await()
Print("Task returned: {Result}")
}
<#
-->
<!-- 17 -->
```verse
ComputeTask:task(int) = spawn{BackgroundWork()}

# 等待任务完成并获取结果
Result:int = ComputeTask.Await()
Print("Task returned: {Result}")
```
<!-- #> -->

**Await() 的关键行为：**

- **阻塞直到完成**：如果任务仍在运行，`Await()`
  暂停直到完成
- **如果完成则立即返回**：如果任务已经完成，
  `Await()` 立即返回缓存结果（Sticky）
- **可以多次调用**：您可以等待相同的任务
  反复，总是得到相同的结果
- **传播取消**：如果等待的任务被取消，
  `Await()` 将取消传播给调用者

<!--versetest
ComputeValue<public>()<suspends>:int = 42
F()<suspends>:void={
MyTask:task(int) = spawn{ComputeValue()}
FirstResult := MyTask.Await()
SecondResult := MyTask.Await()
}
<#
-->
<!-- 18 -->
```verse
MyTask:task(int) = spawn{ComputeValue()}

# 首先等待-等待完成
FirstResult := MyTask.Await()

# 第二个等待 - 立即返回缓存结果
SecondResult := MyTask.Await()

# 第一个结果 = 第二个结果
```
<!-- #> -->


### 常见任务模式

**超时后取消任务：**

<!--versetest
ProcessData()<suspends>:void={}
-->
<!-- 27 -->
```verse
StartTask()<suspends>:void =
    DataTask:task(void) = spawn{ProcessData()}

    race:
        block:
            DataTask.Await()
            Print("Task completed")
        block:
            Sleep(5.0)
            DataTask.Cancel()
            Print("Task timed out and was canceled")
```
**等待多个生成的任务：**

<!--versetest
Task1()<suspends>:int=1
Task2()<suspends>:int=2
Task3()<suspends>:int=3
-->
<!-- 28 -->
```verse
RunMultipleTasks()<suspends>:void =
    T1 := spawn{Task1()}
    T2 := spawn{Task2()}
    T3 := spawn{Task3()}

    # 等待全部完成
    Results := sync:
        T1.Await()
        T2.Await()
        T3.Await()

    Print("All tasks complete: {Results(0)}, {Results(1)}, {Results(2)}")
```
### 暂停点和取消

Verse 中的任务取消遵循合作模型。而不是
强制终止任务，这可能会导致资源浪费
状态不一致，Verse 发送任务检查的取消信号
在**暂停点**。当任务收到取消信号时，
它有机会在终止之前清理资源。这个
合作方法可以防止数据损坏，同时确保
响应式取消。

挂起点是异步任务可以执行的特定位置
暂停和恢复。这些是唯一的地方：

- 可以暂停一个任务以允许其他任务运行
- 检查并处理取消信号
- 运行时可以在并发任务之间切换

常见的悬挂点包括：

**计时操作：**

<!--versetest
F()<suspends>:void=
    Sleep(1.0)
    NextTick() 
<#
-->
<!-- 30 -->
```verse
Sleep(1.0)  # 暂停一段时间，恢复时检查取消
NextTick()  # 等待一次模拟更新，检查取消
```
<!-- #> -->

**调用挂起函数：**

<!--versetest
SomeAsyncFunction<public>()<suspends>:void = {}
F()<suspends>:void={
Result := SomeAsyncFunction()
}
<#
-->
<!-- 32 -->
```verse
Result := SomeAsyncFunction()  # 通话时的暂停点
```
<!-- #> -->

**结构化并发表达式：**

<!--versetest
Op1()<suspends>:void = {}
Op2()<suspends>:void = {}
M()<suspends>:void =
    sync:
        Op1()
        Op2()
<#
-->
<!-- 33 -->
```verse
sync:  # 进入同步时的暂停点
    Op1()
    Op2()
# 同步完成时的暂停点
```
<!-- #> -->

**任务操作：**

<!--versetest
ComputeValue<public>()<suspends>:int = 42
F()<suspends>:void={
MyTask:task(int) = spawn{ComputeValue()}
Result := MyTask.Await()
}
<#
-->
<!-- 34 -->
```verse
Result := MyTask.Await()  # 等待时的暂停点
```
<!-- #> -->

**重要：** 暂停点之间的立即代码运行无需
中断。如果您编写一个长计算循环而没有任何
暂停点，该任务在到达暂停点之前无法取消
下一个暂停点：

<!--versetest
ComputeExpensiveOperation(:int):void={}
-->
<!-- 35  -->
```verse
# 循环期间无法取消
LongComputation()<suspends>:void =
    for (I := 0..1000000):
        # 无暂停点 - 运行至完成
        ComputeExpensiveOperation(I)
    Sleep(0.0)  # 第一次取消检查在这里进行！

# 每次迭代都可以取消
ResponsiveComputation()<suspends>:void =
    for (I := 0..1000000):
        ComputeExpensiveOperation(I)
        Sleep(0.0)  # 每次迭代都会检查取消
```
如果您需要取消长时间运行的计算，请插入
使用 `Sleep(0.0)` 或 `NextTick()` 定期暂停点，其中
产量控制没有实际延迟，但允许取消检查。

取消在任务层次结构中级联进行。当父任务
被取消，其所有子任务都会收到取消信号
也是。这种级联行为保持了子任务的不变性
在结构化并发中不要比他们的父母活得更久，防止
资源泄漏并确保可预测的清理。在种族表达中，
例如，当获胜者完成时，竞赛任务会发送
向所有丢失的子任务发出取消信号，然后级联到任何
这些失败者可能创建的任务。

<a id="cleanup-and-resource-management"></a>
## 清理和资源管理

### 延迟：块

`defer:` 块提供有保证的清理代码，该代码在以下情况下执行：
它的封闭范围存在——无论是通过正常完成、失败，
或取消。对于`defer`语义的完整描述，
包括执行顺序、范围规则和限制，请参见
[延迟语句](07_control.md#defer-statements)。

本节重点介绍 `defer` 如何与并发交互。

**推迟：取消：**

当并发任务被取消时（例如，丢失的 `race` 臂或
取消了 `spawn`)，延迟块在堆栈从
取消点。这使得 `defer` 对于资源清理至关重要
在并发代码中：

<!--versetest
AcquireResource():int=42
ReleaseResource(:int):void={}
LongRunningTask(:int)<suspends>:void={loop{NextTick()}}
-->
<!-- 36 -->
```verse
ProcessWithTimeout()<suspends>:void =
    race:
        block:
            Resource := AcquireResource()
            defer:
                ReleaseResource(Resource)  # 当该臂被取消时运行
            LongRunningTask(Resource)
        block:
            Sleep(10.0)  # 超时
    # 如果超时获胜，第一个块将被取消并推迟运行
```
<!--versetest
Setup():void={}
Teardown():void={}
LongOperation()<suspends>:void={loop{NextTick()}}
-->
<!-- 42 -->
```verse
CancellableWork()<suspends>:void =
    Setup()

    defer:
        Teardown()
        Print("Cleanup after cancellation")

    # 如果取消此任务，则在展开期间推迟运行
    LongOperation()
```
**延迟中不暂停：**

defer 块**不能**包含挂起操作。这确保了
清理立即发生，不会延迟：

<!--versetest
ValidDefer()<suspends>:void =
    defer:
        Print("Cleanup happens immediately")
    Sleep(1.0)
<#
-->
<!-- 44 -->
```verse
# 错误：无法在延迟中使用挂起操作
BadDefer()<suspends>:void =
    defer:
        Sleep(1.0)  # 错误：延迟块无法暂停
        NextTick()  # 错误：延迟块无法暂停
```
<!-- #> -->

这个限制是必要的——如果延迟块可以暂停，清理
可能会无限期地推迟，从而违背了他们所保证的目的
最终确定。但是，延迟块*可以*使用 `spawn`
即发即忘的异步操作。

## 计时函数

将执行暂停指定持续时间的基本计时函数：

<!--versetest
M()<suspends>:void =
    Sleep(1.0)

    Sleep(0.0)
<#
-->
<!-- 46 -->
```verse
# 暂停1秒
Sleep(1.0)

# 暂停一帧（尽可能小的延迟）
Sleep(0.0)
```
<!-- #> -->

`Sleep(0.0)` 模式值得特别关注。虽然没有
添加实际延迟，它有两个关键目的：

1. **创建暂停点**用于取消检查
2. **将控制权**交给其他并发任务，防止一个任务独占执行

这使得 `Sleep(0.0)` 对于响应式并发代码至关重要：

<!--versetest
ProcessFrame():void={}
ExpensiveOperation(:int):void={}
-->
<!-- 47 -->
```verse
# 没有 Sleep(0.0) - 循环期间无法取消
UnresponsiveLoop()<suspends>:void =
    for (I := 0..10000):
        ExpensiveOperation(I)
    # 仅在所有迭代后检查取消

# With Sleep(0.0) - 响应取消
ResponsiveLoop()<suspends>:void =
    for (I := 0..10000):
        ExpensiveOperation(I)
        Sleep(0.0)  # 每次迭代的产量和检查取消
```
**最佳实践：** 在长时间运行的循环中插入 `Sleep(0.0)` 以确保
任务保持对取消的响应并共享执行时间
与其他并发操作相当。

### NextTick()

!!!注意“未发布的功能”
    NextTick() 尚未发布。 

`NextTick()`函数暂停执行，直到下一次仿真
更新（勾选）。与 `Sleep(0.0)` 不同，`Sleep(0.0)` 会产生控制并可能恢复
在同一时间点内，如果没有其他工作待处理，`NextTick()` 保证
在恢复之前至少会发生一次模拟更新：

<!--versetest
M()<suspends>:void =
    NextTick()

    NextTick()
    NextTick()
    NextTick()
<#
-->
<!-- 48 -->
```verse
# 等待恰好一个模拟滴答声
NextTick()

# 多个刻度
NextTick()  # 等待 1 个刻度
NextTick()  # 等待另一个滴答声
NextTick()  # 等待第三个滴答声
```
<!-- #> -->

`NextTick()`对于需要与模拟更新同步的游戏逻辑至关重要：

<!--versetest
ProcessGameLogic():void={}
UpdatePhysics():void={}
CheckCollisions():void={}
PerformAction():void={}

GameLoop()<suspends>:void =
    loop:
        ProcessGameLogic()
        UpdatePhysics()
        CheckCollisions()
        NextTick()

DelayByTicks(TickCount:int)<suspends>:void =
    for (I := 1..TickCount):
        NextTick()

# Test the delay function
TestDelay()<suspends>:void =
    DelayByTicks(5)
    PerformAction()
<#
-->
<!-- 49 -->
```verse
# 每个刻度处理游戏逻辑
GameLoop()<suspends>:void =
    loop:
        ProcessGameLogic()
        UpdatePhysics()
        CheckCollisions()
        NextTick()  # 等待下一次模拟更新

# 按特定数量的刻度延迟操作
DelayByTicks(TickCount:int)<suspends>:void =
    for (I := 1..TickCount):
        NextTick()

# 执行操作前等待 5 个周期
DelayByTicks(5)
PerformAction()
```
<!-- #> -->

**睡眠（0.0）与NextTick（）：**

|特色 |睡眠(0.0) |下一个刻度（）|
|--------- |------------ |------------|
|时间 |可能会在同一时间点恢复|总是等待下一个报价 |
|使用案例 |取消支票收益 |与模拟更新同步|
|保证|创建悬挂点 |保证刻度边界|

两者都创建取消的暂停点，但 `NextTick()`
当您需要与
模拟时钟。

<!--versetest
ProcessFrame()<computes>:logic=false
-->
<!-- 50 -->
```verse
# 常见模式
LoopWithDelay()<suspends>:void =
    loop:
        ProcessFrame()
        Sleep(0.033)  # 〜30 FPS

TickBasedLoop()<suspends>:void =
    loop:
        if (ProcessFrame()=false): 
             break
        NextTick()  # 每个模拟刻度一次
```
时序模式为：

<!--versetest
DoAction():void={}
UpdateLogic()<computes>:void={}
Float(:int)<computes>:float=0.0
SetPosition(:float):void={}
-->
<!-- 51 -->
```verse
# 行动迟缓
PerformDelayedAction()<suspends>:void =
    Sleep(2.0)  # 等待 2 秒
    DoAction()

# 定期执行
PeriodicUpdate()<suspends>:void =
    loop:
        UpdateLogic()
        Sleep(1.0)  # 每秒更新一次

# 动画时序
AnimateMovement(Start:float,End:float)<suspends>:void =
    for (T := 0..10):
        SetPosition(Lerp(Start, End, Float(T)/10.0))
        Sleep(0.0)  # 一帧
```
### 获取当前时间：GetSecondsSinceEpoch

`GetSecondsSinceEpoch()`函数返回当前的Unix
时间戳——自 1970 年 1 月 1 日以来经过的秒数，
世界标准时间 00:00:00。此功能对于时间戳事件至关重要，
测量持续时间，并与使用的外部系统同步
Unix 时间。

<!--versetest
LogEvent(Message:string):void =
    Timestamp := GetSecondsSinceEpoch()
    Print("[{Timestamp}] {Message}")
<#
-->
<!-- 52 -->
```verse
# 获取当前时间戳
CurrentTime := GetSecondsSinceEpoch()
# 返回类似 1716411409.0（2024 年 5 月 22 日）的内容

# 记录带有时间戳的事件
LogEvent(Message:string):void =
    Timestamp := GetSecondsSinceEpoch()
    Print("[{Timestamp}] {Message}")
```
<!-- #> -->

**关键交易行为：**

在单个事务中，`GetSecondsSinceEpoch()` 返回
每次调用时**相同的值**。这确保了确定性
行为并防止与时间相关的竞争条件：

<!--versetest
DoExpensiveWork()<transacts>:void = {}
PerformDatabaseUpdates()<transacts>:void = {}

MeasureTransactionTime()<transacts>:void =
    StartTime := GetSecondsSinceEpoch()

    DoExpensiveWork()
    PerformDatabaseUpdates()

    EndTime := GetSecondsSinceEpoch()

    Duration := EndTime - StartTime
<#
-->
<!-- 53 -->
```verse
MeasureTransactionTime()<transacts>:void =
    StartTime := GetSecondsSinceEpoch()

    # 执行复杂的操作
    DoExpensiveWork()
    PerformDatabaseUpdates()

    EndTime := GetSecondsSinceEpoch()

    # 开始时间=结束时间！
    # 时间在交易中被“冻结”
    Duration := EndTime - StartTime  # 始终为 0.0
```
<!-- #> -->

这种事务一致性是有意为之的——它阻止了
事务重试可能产生的非确定性行为
由于时间的进展而产生不同的结果。如果交易失败
并重试，重试中对 `GetSecondsSinceEpoch()` 的所有调用
尝试将返回一个新的一致时间戳。

**使用案例：**

**事件记录和调试：**

<!--versetest
logger := class:
    var EventLog:[]tuple(float, string) = array{}

    Log(Message:string)<transacts>:void =
        Timestamp := GetSecondsSinceEpoch()
        set EventLog = EventLog + array{(Timestamp, Message)}

    GetRecentEvents(LastSeconds:float)<transacts>:[]string =
        Now := GetSecondsSinceEpoch()
        Cutoff := Now - LastSeconds
        for (Entry : EventLog, Entry(0) >= Cutoff):
            Entry(1)
<#
-->
<!-- 55 -->
```verse
logger := class:
    var EventLog:[]tuple(float, string) = array{}

    Log(Message:string)<transacts>:void =
        Timestamp := GetSecondsSinceEpoch()
        set EventLog = EventLog + array{(Timestamp, Message)}

    GetRecentEvents(LastSeconds:float)<transacts>:[]string =
        Now := GetSecondsSinceEpoch()
        Cutoff := Now - LastSeconds
        for ((Time, Message) : EventLog, Time >= Cutoff):
            Message
```
<!-- #> -->

**会话跟踪：**
<!--versetest-->
<!-- 56 -->
```verse
player_session := class:
    LoginTime:float

MakeSession()<transacts>:player_session =
    player_session{LoginTime := GetSecondsSinceEpoch()}

GetSessionDuration(S:player_session)<transacts>:float =
    GetSecondsSinceEpoch() - S.LoginTime
```
**速率限制：**

<!--versetest
PerformAction():void={}
ShowCooldownMessage():void={}
rate_limiter := class:
    var LastAction:float = 0.0
    Cooldown:float = 5.0

    CanAct()<transacts><decides>:void =
        Now := GetSecondsSinceEpoch()
        TimeSinceLastAction := Now - LastAction
        TimeSinceLastAction >= Cooldown
        set LastAction = Now

assert:
   Limiter := rate_limiter{}
   if (Limiter.CanAct[]):
       PerformAction()
   else:
       ShowCooldownMessage()
<#
-->
<!-- 57 -->
```verse
rate_limiter := class:
    var LastAction:float = 0.0
    Cooldown:float = 5.0  # 5秒冷却时间

    CanAct()<transacts><decides>:void =
        Now := GetSecondsSinceEpoch()
        TimeSinceLastAction := Now - LastAction
        TimeSinceLastAction >= Cooldown
        set LastAction = Now

Limiter := rate_limiter{}

if (Limiter.CanAct[]):
    PerformAction()
else:
    ShowCooldownMessage()
```
<!-- #> -->

**外部系统的绝对时间戳：**

与使用 Unix 时间戳的外部系统、数据库或 API 交互时：

<!--versetest
MyPlayerID:string = "player123"
SendToAnalytics<public>(EventType:string, Timestamp:float, PlayerID:string):void = {}
FetchServerTime():float = 1716411409.0

M():void =
    SendToAnalytics("player_action", GetSecondsSinceEpoch(), MyPlayerID)

    ServerTime := FetchServerTime()
    LocalTime := GetSecondsSinceEpoch()
    ClockSkew := LocalTime - ServerTime
<#
-->
<!-- 58 -->
```verse
# 用于外部分析的时间戳
AnalyticsEvent := map{
    "event_type" => "player_action",
    "timestamp" => GetSecondsSinceEpoch(),
    "player_id" => MyPlayerID
}
SendToAnalytics(AnalyticsEvent)

# 与服务器时间戳比较
ServerTime := FetchServerTime()
LocalTime := GetSecondsSinceEpoch()
ClockSkew := LocalTime - ServerTime
```
<!-- #> -->

**重要说明：**

- 返回代表秒的 `float`（可能有毫秒精度的小数部分）
- 位于`/Verse.org/Verse`模块中—使用`using { /Verse.org/Verse }`访问
- 不受 `Sleep()` 或其他暂停的影响 — 测量真实世界时间
- 交易内一致的决定论
- 每笔新交易都会有一个新的时间戳

**与基于时间的逻辑的睡眠相结合：**

<!--versetest
PerformAction<public>()<suspends>:void = {}
-->
<!-- 59 -->
```verse
# 等到特定时间
WaitUntil(TargetTime:float)<suspends>:void =
    loop:
        if (GetSecondsSinceEpoch() >= TargetTime) then:
            break
        Sleep(0.1)  # 每 100 毫秒检查一次

# 为未来安排一个行动
ScheduleDelayedAction(DelaySeconds:float)<suspends>:void =
    TargetTime := GetSecondsSinceEpoch() + DelaySeconds
    WaitUntil(TargetTime)
    PerformAction()
```
请注意，事务一致性意味着您不能使用
`GetSecondsSinceEpoch()` 测量单次内的时间
交易。用于测量不执行的操作的执行时间
跨越事务，使用分析工具或外部计时机制。

## 事件和同步

事件提供同步原语来协调
并发任务。他们实现了生产者-消费者和观察者
模式，允许任务相互发出信号并等待特定的
条件。事件弥合了独立并发之间的差距
操作，无需共享可变状态即可进行通信。

### 基本事件

`event(t)` 类型创建了一个通信通道，生产者可以通过该通道
信号价值和消费者等待着它们。每个信号传递一个值
对于每个等待任务：

<!--versetest
ProcessValue(:int):void={}
F()<suspends>:void={
GameEvent := event(int){}

ProducerTask()<suspends>:void =
    Sleep(1.0)
    GameEvent.Signal(42)

ConsumerTask()<suspends>:void =
    Value := GameEvent.Await()
    ProcessValue(Value)

sync:
    ProducerTask()
    ConsumerTask()
}
<#
-->
<!-- 60 -->
```verse
# 为整数创建事件通道
GameEvent := event(int){}

# 生产者：向事件发出信号值
ProducerTask()<suspends>:void =
    Sleep(1.0)
    GameEvent.Signal(42)

# 消费者：等待事件的值
ConsumerTask()<suspends>:void =
    Value := GameEvent.Await()
    ProcessValue(Value)

sync:
    ProducerTask()
    ConsumerTask()
```
<!-- #> -->

当针对事件调用 `Await()` 时，调用任务将挂起，直到
另一个任务使用值调用 `Signal()`。信号值是
交付给一项正在等待的任务，然后继续执行。如果有多个
任务等待相同的事件，每个 `Signal()` 恰好唤醒一个
waiter——信号和等待一对一地配对。

这种一对一的匹配使活动非常适合任务
协调。考虑一个玩家动作系统：输入处理程序
当游戏系统等待按钮按下时发出信号。或者
考虑人工智能寻路请求：游戏逻辑发出目的地信号
寻路系统等待并处理请求时。

事件可以自然地与结构化并发一起工作。你可以使用它们
在 `sync` 块内协调并行操作，或组合
他们使用 `race` 来实现事件等待超时：

<!--versetest
F()<suspends>:void={
GameEvent:event(int)=event(int){}
Result := race:
    block:
        Value := GameEvent.Await()
        option{Value}
    block:
        Sleep(5.0)
        false
}
<#
-->
<!-- 61 -->
```verse
# 等待超时事件
Result := race:
    block:
        Value := GameEvent.Await()
        option{Value}
    block:
        Sleep(5.0)
        false  # 超时 - 未收到任何值
```
<!-- #> -->

### 粘性事件

!!!注意“未发布的功能”
    粘性事件尚未发布，目前不可用。

虽然基本事件将每个信号传递给恰好一个等待者，
`sticky_event(t)` 记住最后一个信号值并将其传递给
所有后续等待，直到发出新值信号为止：

<!--NoCompile-->
<!-- 62 -->
```verse
StateEvent := sticky_event(int){}

# 信号一次
StateEvent.Signal(100)

# 多个等待都收到相同的值
Value1 := StateEvent.Await()  # 获得 100
Value2 := StateEvent.Await()  # 再次获得100
Value3 := StateEvent.Await()  # 还是能拿到100

# 新信号更新粘性值
StateEvent.Signal(200)
Value4 := StateEvent.Await()  # 获得 200
Value5 := StateEvent.Await()  # 还获得200
```
粘性事件擅长表示多个状态变化
消费者需要观察。与每个信号不同的基本事件
一次等待后消失，粘性事件保持当前
状态。考虑一个游戏阶段系统：当阶段从
从“大厅”到“播放”，每个检查阶段的系统都应该看到
“播放”，不让一个系统消耗信号而其他系统错过信号
它。

粘性行为创建了一种最终一致状态的形式。如果
任务等待粘性事件，保证看到最新的
信号，即使该信号发生在等待之前。这使得
粘性事件非常适合配置更新、模式切换或任何
“当前状态是什么？”的场景比“什么”更重要
刚刚改变？”。

### 可订阅的活动

!!!注意“未发布的功能”
    可订阅活动尚未发布，目前不可用。

`subscribable_event`类型实现了观察者模式，
允许多个处理程序对每个信号做出反应。与活动不同
在等待任务显式等待的情况下，可订阅事件让您
注册回调函数，当值是时自动执行
发出信号：

<!--NoCompile-->
<!-- 63 -->
```verse
LogScore(:int):void={}
UpdateUI(:int):void={}
CheckAchievements(:int):void={}

ScoreEvent := subscribable_event(int){}

# 订阅多个处理程序
Logger := ScoreEvent.Subscribe(LogScore)
UIUpdater := ScoreEvent.Subscribe(UpdateUI)
AchievementChecker := ScoreEvent.Subscribe(CheckAchievements)

# 信号调用所有订阅的处理程序
ScoreEvent.Signal(1000)  # 调用LogScore(1000)、UpdateUI(1000)、CheckAchievements(1000)

# 取消订阅以停止接收信号
Logger.Cancel()
ScoreEvent.Signal(2000)  # 仅调用 UpdateUI 和 CheckAchievements
```
每个订阅都会返回一个 `cancelable` 对象，该对象允许您
通过拨打 `Cancel()` 取消订阅。一旦取消，该处理程序就会停止
接收信号。这提供了对处理程序的细粒度控制
生命周期，对于游戏过程中来来去去的系统至关重要。

订阅事件在多个广播场景中大放异彩
独立的系统需要对同一事件做出反应。当一个
玩家得分、UI 需要更新、音频系统需要
要播放声音，成就系统需要检查解锁，
分析系统需要记录该事件。可订阅
事件，每个系统独立注册其处理程序，并且每个
信号到达所有相关方。

### 可等待和可发出信号的接口

事件基于两个基本接口构建，您可以使用它们来创建自定义同步类型：

<!--NoCompile-->
<!-- 64 -->
```verse
awaitable(t:type) := interface:
    Await()<suspends>:t

signalable(t:type) := interface:
    Signal(Value:t):void
```
`awaitable` 接口代表任何可以等待的东西，
而`signalable`代表任何可以发送信号的东西。由
将这些功能分开，Verse 可以精确控制谁
可以产生价值与谁可以消费价值。

您可以将 `awaitable` 参数传递给只应读取的函数
防止意外信号：

<!--versetest
ProcessValue(:int):void={}
-->
<!-- 65 -->
```verse
# 该函数只能await，不能signal
ConsumerFunction(Source:awaitable(int))<suspends>:void =
    Value := Source.Await()
    ProcessValue(Value)
    # Source.Signal(123)  # ERROR: awaitable doesn't have Signal

# 该函数只能发出信号，不能等待
ProducerFunction(Target:signalable(int)):void =
    Target.Signal(42)
    # Value := Target.Await()  # ERROR: signalable doesn't have Await
```
这种分离为生产者-消费者创建了清晰的界面
关系。队列实现可能会暴露 `awaitable`
消费者读取接口和 `signalable` 接口
生产者进行书写，确保双方都不会意外使用
错误操作。

### 交易行为

事件订阅参与 Verse 的交易系统。如果一个
包含 `Subscribe()` 调用的事务失败并回滚，
订阅永远不会生效：

<!--NoCompile-->
<!-- 66 -->
```verse
Handler(:int):void={}

MyEvent := subscribable_event(int){}

# 失败交易中的订阅
if:
    Sub := MyEvent.Subscribe(Handler)
    false?  # 事务失败并回滚

# 订阅已回滚 - 未调用处理程序
MyEvent.Signal(100)
```
同样，`Cancel()` 操作是事务性的。如果您在后来失败的事务中取消订阅，则订阅仍保持活动状态：

<!--versetest
subscription := class:
    Cancel()<transacts>:void = {}

subscribable_event(t:type) := class:
    Subscribe(Handler:t->void)<transacts>:subscription = subscription{}
    Signal(Value:t)<transacts>:void = {}
-->
<!-- 67 -->
```verse
Handler(:int):void={}

MyEvent := subscribable_event(int){}
Sub := MyEvent.Subscribe(Handler)

# 交易失败时取消
if:
    Sub.Cancel()
    false?  # 交易失败

# 取消已回滚 - 订阅仍然有效
MyEvent.Signal(100)  # 处理程序仍然被调用
```
这种事务集成确保事件订阅
保持与其他事务操作的一致性。如果你是
建立一个复杂的系统，其中订阅事件是系统的一部分
较大的初始化可能会失败，事务系统
保证所有初始化要么成功，要么全部都不成功，
防止部分设置可能导致细微的错误。

### 事件模式和用例

**请求-响应：** 使用基本事件来实现系统之间的请求-响应模式：

<!--versetest
FindPath(Start:int, Goal:int):void = {}

pathfinding_system := class:
    PathRequest:event(tuple(int, int)) = event(tuple(int, int)){}
    PathResponse:event(int) = event(int){}

    PathfindingService()<suspends>:void =
        loop:
            Request := PathRequest.Await()
            Start := Request(0)
            Goal := Request(1)
            FindPath(Start, Goal)
            PathResponse.Signal(42)

    RequestPath(Start:int, Goal:int)<suspends>:int =
        PathRequest.Signal((Start, Goal))
        PathResponse.Await()
<#
-->
<!-- 68 -->
```verse
PathRequest := event(tuple(int, int)){}  # （开始，目标）
PathResponse := event(int){}             # 路径结果

PathfindingService()<suspends>:void =
    loop:
        (Start, Goal) := PathRequest.Await()
        FindPath(Start, Goal)
        PathResponse.Signal(42)

RequestPath(Start:int, Goal:int)<suspends>:int =
    PathRequest.Signal((Start, Goal))
    PathResponse.Await()
```
<!-- #> -->

**状态广播：** 使用粘性事件来表示多个系统需要观察的状态：

<!--versetest
game_phase := enum{Menu, Playing, Paused, GameOver}
UIUpdate(P:game_phase)<transacts>:void={}
AIUpdate(P:game_phase)<transacts>:void={}
AudioUpdate(P:game_phase)<transacts>:void={}

sticky_event(t:type) := class:
    var CurrentValue:?t = false
    Signal(Value:t)<transacts>:void = set CurrentValue = option{Value}
    Await()<suspends><transacts>:t =
        loop:
            if (V := CurrentValue?):
                return V
-->
<!-- 69 -->
```verse
PhaseChange := sticky_event(game_phase){}

# 系统等待当前阶段而不会丢失更新
UISystem()<suspends>:void =
    loop:
        Phase := PhaseChange.Await()
        UIUpdate(Phase)

AISystem()<suspends>:void =
    loop:
        Phase := PhaseChange.Await()
        AIUpdate(Phase)

AudioSystem()<suspends>:void =
    loop:
        Phase := PhaseChange.Await()
        AudioUpdate(Phase)
```
**多系统通知：** 当有多个系统时，使用可订阅事件
系统需要对相同的事件做出反应：

<!--versetest
subscription := class:
    Cancel()<transacts>:void = {}

subscribable_event(t:type) := class:
    Subscribe(Handler:t->void)<transacts>:subscription = subscription{}
    Signal(Value:t)<transacts>:void = {}
-->
<!-- 70 -->
```verse
UpdateInventoryUI(:int):void={}
PlayPickupSound(:int):void={}
CheckCollectionAchievement(:int):void={}
LogItemPickup(:int):void={}

ItemPickedUp := subscribable_event(int){}

# 各系统独立订阅
InitializeSystems():void =
    ItemPickedUp.Subscribe(UpdateInventoryUI)
    ItemPickedUp.Subscribe(PlayPickupSound)
    ItemPickedUp.Subscribe(CheckCollectionAchievement)
    ItemPickedUp.Subscribe(LogItemPickup)

# 单一信号到达所有系统
OnPlayerPickupItem(ItemID:int):void =
    ItemPickedUp.Signal(ItemID)
```
事件通过提供通信来补充结构化并发
比单个并发操作更长寿的通道。而`sync`，
`race`、`rush` 和 `branch` 组织任务相对于
事件彼此组织任务如何共享信息和协调
他们的行动。

## 常见模式和最佳实践

使用 `race` 实现超时操作：

<!--versetest
ActualOperation()<suspends>:void={}
-->
<!-- 71 -->
```verse
PerformWithTimeout()<suspends>:logic =
    race:
        block:
            ActualOperation()
            true  # 成功
        block:
            Sleep(5.0)  # 5秒超时
            false  # 超时
```
同时初始化多个系统：

<!--versetest
LoadAssets()<suspends>:void={}
ConnectToServer()<suspends>:void={}
InitializeUI()<suspends>:void={}
PrepareAudio()<suspends>:void={}

InitializeGame()<suspends>:void =
    sync:
        LoadAssets()
        ConnectToServer()
        InitializeUI()
        PrepareAudio()
    Print("Game ready!")
<#
-->
<!-- 72 -->
```verse
InitializeGame()<suspends>:void =
    sync:
        LoadAssets()
        ConnectToServer()
        InitializeUI()
        PrepareAudio()
    Print("Game ready!")
```
<!-- #>-->

启动不妨碍游戏玩法的后台任务：

<!--versetest
MonitorPlayerStats()<suspends>:void={}
UpdateLeaderboards()<suspends>:void={}
ProcessAchievements()<suspends>:void={}
-->
<!-- 73 -->
```verse
StartBackgroundSystems()<suspends>:void =
    branch:
        MonitorPlayerStats()
    branch:
        UpdateLeaderboards()
    branch:
        ProcessAchievements()
    # 主游戏继续，后台任务运行
```
产生延迟的实体：

<!--versetest
enemy_class := class {     Spawn()<suspends>:void={} }
-->
<!-- 74 -->
```verse
SpawnWave(Enemies:[]enemy_class)<suspends>:void =
    for (Enemy : Enemies):
        spawn{Enemy.Spawn()}
        Sleep(0.5)  # 生成之间半秒
```
## 限制和注意事项

### 迭代限制

迭代与某些并发表达式之间的交互
需要仔细考虑。冲和分支不能使用
直接在循环内部或对于主体，这一限制阻止
无限的任务积累。当你编写一个可能执行的循环时
数百或数千次，直接允许rush或分支将
创建那么多后台任务，可能会压垮
系统。

<!--versetest
Operation1()<suspends>:void = {}
Operation2()<suspends>:void = {}

ProcessWithRush(I:int)<suspends>:void =
    rush:
        Operation1()
        Operation2()

M()<suspends>:void =
    for (I := 0..10):
        ProcessWithRush(I)
<#
-->
<!-- 76 -->
```verse
# 不允许
for (I := 0..10):
    rush:  # 错误：无法在循环中使用rush
        Operation1()
        Operation2()

# 解决方法 - 包装在函数中
ProcessWithRush(I:int)<suspends>:void =
    rush:
        Operation1()
        Operation2()

for (I := 0..10):
    ProcessWithRush(I)  # 好的
```
<!-- #> -->

此限制迫使您有意识地创建
迭代中的后台任务。通过包装并发操作
在函数中，您确认任务创建并使其明确
在你的代码结构中。这种小摩擦可以防止意外
资源耗尽，同时保持使用这些资源的灵活性
真正需要时的模式。

### 抽象优于实现

Verse 故意抽象掉底层的线程并
调度机制。你找不到线程创建 API，
线程本地存储，或显式同步原语，例如
互斥体或信号量。这不是限制而是设计
哲学。通过使用更高级别的任务抽象，Verse
消除了整个类别的错误——没有数据竞争，没有死锁
不正确的锁定顺序，没有忘记解锁调用。

并发模型是合作的而不是抢占的。任务
自愿在暂停点进行产量控制，而不是被
被调度程序强制中断。这种合作性质使得
由于您确切知道在哪里，因此可以更轻松地推理并发代码
可能会发生任务切换。也与游戏自然融合
引擎基于帧的执行模型，其中可预测的时间是
至关重要。

### 效果交互

让Verse的并发安全的效果系统也介绍了
一些限制。 `decides` 效果，标记函数
可能会失败，不能与 `suspends` 效果结合使用。这个
分离保留了失败模型和并发模型
正交，防止难以实现的复杂相互作用
原因.事务操作和某些特定于设备的操作
并发使用时操作也可能有限制
上下文，确保必须是原子的操作保持如此。
