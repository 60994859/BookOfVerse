# 并发

并发是 Verse 的一个基本方面，它允许你像控制程序流程一样自然地控制时间流。与将并发作为事后追加的传统编程语言不同，Verse 通过专用表达式和效果，将时间流控制直接集成到语言中。

游戏开发本质上需要管理多个同时进行的活动。想想一个典型的游戏场景：NPC 巡逻其路线，同时粒子效果播放，UI 元素在冷却计时器倒计时时动画化，背景音乐在曲目间淡入淡出。所有这些活动都是并发发生的，在时间上重叠。Verse 认识到这一现实，并提供了语言级结构来表达这些并行行为。

该语言通过结构化和非结构化并发原语的组合来实现这一点，所有原语都建立在异步表达式的概念之上，这些表达式可以在多个模拟更新之间挂起和恢复。这种方法使并发编程感觉像编写顺序代码一样自然，同时避免了基于线程的并发（如数据竞争和死锁）的传统陷阱。

## 核心概念

### 立即表达式与异步表达式

每个表达式都属于两类之一：立即或异步。理解这一区别对于使用 Verse 的并发模型至关重要。

立即表达式计算时没有延迟，完全在当前模拟更新或帧内完成。这些包括你期望立即发生的大多数基本操作：算术计算、变量访问、简单函数调用和数据结构操作。当你编写 `X := 5 + 3` 时，加法立即发生，赋值立即完成，执行移动到下一条语句而不可能被中断。

另一方面，异步表达式有可能需要时间来计算，可能跨越多个模拟更新。它们代表在游戏世界中固有地需要时间的操作：播放动画、计时器倒计时、网络请求完成，或者只是等待下一帧。一个异步表达式可能在其条件已经满足时立即完成，也可能挂起执行，允许其他代码在它等待合适时机恢复时运行。

### 模拟更新

模拟更新（或 tick）代表游戏模拟的一步。模拟和渲染是**独立的**——它们以不同的速率运行，在现代引擎中彼此解耦。

每个 tick 处理输入、更新游戏逻辑、运行物理模拟，并推进游戏状态。Verse 的并发模型让你能够以逻辑时间流的方式思考——异步表达式在 tick 边界挂起，并在未来的 tick 中当条件满足时恢复。

异步表达式自然地与该更新周期对齐。当异步表达式挂起时，它将控制交还给游戏引擎，游戏引擎继续处理其他任务和渲染帧。挂起的表达式在未来的更新中当条件满足时恢复，无缝地从中断处继续。这种协作模型确保长时间运行的操作不会阻塞游戏的响应性。

### suspends 效果

并发操作需要 `<suspends>` 效果说明符（参见[效果](13_effects.md)）。标记为 `<suspends>` 的函数可以使用并发表达式，调用其他挂起函数，并协作地让出执行权：

<!--versetest-->
<!-- 01 -->
```verse
# Function marked with suspends can use async expressions
MyAsyncFunction()<suspends>:void =
    Sleep(1.0)  # Pause execution
    Print("One second later!")

# Regular functions cannot use async expressions
MyImmediateFunction():void =
    # Sleep(1.0)  # ERROR: Cannot use Sleep without suspends
    Print("This happens immediately")
```

`<suspends>` 效果通过调用链传播——任何调用挂起函数的函数本身必须标记为 `<suspends>`。

## 结构化并发

结构化并发代表了 Verse 最优雅的设计决策之一。结构化并发表达式不是产生独立存在并需要手动生命周期管理的线程或任务，其生命周期自然地绑定到其所属作用域。当你进入一个结构化并发块时，你知道其中的所有并发操作在块退出时都会被妥善管理和清理，防止资源泄漏并使代码更易于推理。

这种方法反映了我们思考顺序代码的方式。就像顺序语句块有明确的开始和结束一样，结构化并发操作具有确定的生命周期。你可以嵌套它们、组合它们，并使用与常规代码块相同的思维模型来推理它们。

### 效果要求

所有结构化并发表达式（`sync`、`race`、`rush` 和 `branch`）都需要 `<suspends>` 效果。你不能在立即（非挂起）函数中使用这些结构：

<!--versetest
Operation1<public>()<suspends>:void = {}
Operation2<public>()<suspends>:void = {}
-->
<!-- 02 -->
```verse
# Valid: structured concurrency in suspends function
ProcessConcurrently()<suspends>:void =
    sync:
        Operation1()
        Operation2()

# Invalid: cannot use sync without suspends
# ProcessImmediate():void =
#     sync:  # ERROR: sync requires suspends
#         Operation1()
```

### sync 表达式

`sync` 表达式体现了最简单的并发模式：同时做多件事并等待它们全部完成。当你拥有可以从并行执行中受益的独立操作时，`sync` 提供了一种清晰的方式来表达这种并行性，同时保持确定性行为。

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
# All expressions start simultaneously and must all complete
Results := sync:
    AsyncOperation1()  # Returns value1
    AsyncOperation2()  # Returns value2
    AsyncOperation3()  # Returns value3

Print("All operations complete with results: {Results(0)} {Results(1)} {Results(2)}")
```
<!-- #> -->

在 `sync` 块内部，所有子表达式基本上在同一时刻开始执行。然后 sync 表达式耐心等待每一个子表达式完成，无论每个子表达式各自需要多长时间。如果一个操作在毫秒内完成，而另一个需要几秒钟，sync 会一直等待直到最后一个操作完成。只有到那时，执行才会继续到 sync 块之后。

sync 的美妙之处在于它的可预测性。你总是能从所有子表达式得到结果，总是按照你编写它们的顺序，整齐地打包在一个元组中。这使得 sync 非常适合需要多个数据片段或需要确保多个系统准备就绪才能继续的场景。并行加载游戏资源、同时初始化多个子系统或从多个来源收集数据，都能从 sync 的全有或全无方法中受益。

考虑一个更复杂的例子，展示 sync 的可组合性：

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
# Nested blocks for complex operations
sync:
    block:  # Task 1 - sequential operations
        LoadTexture()
        ApplyTexture()
    block:  # Task 2 - parallel to task 1
        LoadSound()
        PlaySound()
    LoadModel()  # Task 3 - parallel to tasks 1 and 2

# Using sync results directly as function arguments
ProcessData(sync:
    FetchDataA()
    FetchDataB()
    FetchDataC()
)
```
<!--versetest
#>
-->

### race 表达式

`sync` 体现的是合作，而 `race` 代表的是竞争。race 表达式同时启动多个异步操作，但只关心第一个到达终点的操作。一旦有一个子表达式完成，race 立即取消所有其他子表达式，并继续执行获胜者的结果。这种胜者全得的语义使 race 非常适合超时模式、回退机制以及任何需要最快响应的场景。

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
# First to complete wins, others are canceled
Winner := race:
    SlowOperation()     # Takes 5 seconds
    FastOperation()     # Takes 1 second - wins!
    MediumOperation()   # Takes 3 seconds

Print("Winner result: {Winner}")  # Prints FastOperation's result
```
<!-- #> -->

race 的强大之处在考虑真实游戏场景时变得明显。想象一下查询多个服务器获取数据，你想要使用最先响应的那个。或者实现一个带超时的玩家动作，要么玩家完成动作，要么时间耗尽。Race 优雅地表达了这些模式，无需复杂的状态管理或手动取消逻辑。

race 中的取消是立即且彻底的。一旦胜者出现，所有失败的子表达式都会收到取消信号并开始清理。这不仅仅是一种优化；对于资源管理和防止不再需要的操作产生不必要的副作用至关重要。

**race 中的类型处理：**

类型系统优雅地处理了 race。由于只有一个子表达式的结果会被返回，race 的结果类型是所有子表达式的最具体公共超类型。这确保了类型安全，同时保持了在可以互相竞争的操作类型上的灵活性：

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

# Result type is base_class (common supertype)
Result:base_class = race:
    GetA()  # Returns derived_a
    GetB()  # Returns derived_b
# Result is base_class, can hold either derived type

# If all expressions return the same type, that's the result type
SameTypeResult:int = race:
    block:
        Sleep(1.0)
        42
    block:
        Sleep(2.0)
        100
# Result type is int
```
<!-- #> -->

一种常见模式是添加标识符来确定哪个子表达式获胜：

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
# Adding identifiers to determine which expression won
WinnerID := race:
    block:
        SlowOperation()
        1  # Return 1 if this wins
    block:
        FastOperation()
        2  # Return 2 if this wins
    block:
        loop:
            InfiniteOperation()
        3  # Never returns

case(WinnerID):
    1 => Print("Slow operation won somehow!")
    2 => Print("Fast operation won as expected")
    _ => Print("Impossible!")
```
<!-- #> -->

### rush 表达式

`rush` 表达式在 `sync` 和 `race` 之间占据了一个独特的中间地带。和 race 一样，它在第一个子表达式完成时立即结束。与 race 不同的是，它不会取消其他子表达式。这产生了一种有趣的模式：你可以启动多个操作，一旦有一个提供结果就继续执行，同时允许其他操作在后台继续工作。

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
# First to complete allows continuation, others keep running
FirstResult := rush:
    LongBackgroundTask()   # Continues after rush completes
    QuickCheck()          # Finishes first
    MediumTask()          # Also continues after rush

Print("First result: {FirstResult}")
# LongBackgroundTask and MediumTask are still running!
```
<!-- #> -->

Rush 在希望保持响应性同时最终完成所有操作的场景中表现出色。考虑预加载游戏资源：你可以同时开始加载多个关卡，一旦当前关卡加载完成就开始游戏，同时继续在后台缓存其他关卡。或者考虑成就检查，你希望在解锁一个成就时立即通知玩家，同时继续检查其他成就。

rush 的非取消特性需要仔细考虑。那些后台任务在 rush 完成后仍然继续消耗资源并执行操作。它们会一直运行直到自然完成，或者直到它们所属的异步上下文结束。这使得 rush 功能强大，但如果误用于可能永远不会完成或消耗大量资源的操作，也可能很危险。

有一个重要的技术限制需要注意：rush 不能直接在 `loop` 或 `for` 等迭代表达式的体中使用。rush 的后台任务与迭代之间的交互可能导致资源累积。如果你需要在循环中使用类似 rush 的行为，将其封装在一个异步函数中，然后从迭代中调用该函数。

### 从并发臂中返回

`sync`、`race` 或 `rush` 臂内部的 `return` 语句会导致封闭的*函数*返回，而不仅仅是该臂。结构化并发表达式被放弃，已经启动的臂中的 defer 会执行，而尚未启动的臂则被简单跳过。

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
        return V         # Returns from MaybeReturn
    Log("done")
    "no-return"

Wrapper(Value:?string)<suspends>:string =
    defer { Log("z") }
    R := sync:
        block:
            MaybeReturn(0, Value)   # Arm 1
        block:
            defer { Log("b") }
            CoroUtils.WaitTicks(1)
            Log("2")
            2
    "{R(0)}"
```

当设置了 `Value` 时，臂 1 在 `MaybeReturn` 内部执行 `return V`。这会完全退出 `Wrapper`——`sync` 被放弃，臂 2 永远无法完成，并且 defer 在展开期间执行。当没有设置 `Value` 时，臂 1 正常完成，`sync` 等待两个臂都结束。

### branch 表达式

`branch` 表达式代表了结构化上下文中的即发即弃并发。当你遇到一个分支时，它立即开始将其体作为后台任务执行，然后毫不犹豫地继续执行下一个表达式。没有等待，没有结果收集，只有一个任务在主线流程不受阻碍地进行时分离出去做它的工作。

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
    # This block runs independently
    AsyncOperation1()
    ImmediateOperation()
    AsyncOperation2()

# Execution continues immediately here
Print("Branch started, continuing main flow")
# Branch block is still running in background
```
<!-- #> -->


Branch 擅长处理不应中断主游戏流程但可以接受在封闭作用域结束时丢失的副作用。想想触发随时间播放的粒子效果、开始逐渐淡入的背景音乐，或预加载可能很快需要的资源。这些操作需要发生，但没有理由让玩家等待它们完成。Branch 让你直接表达这种"启动它然后继续"的模式。

branch 的关键语义是其**取消行为**：当执行离开封闭的函数作用域时，分支任务会被自动取消，无论这是通过正常完成、失败还是来自上层的取消发生的。这就是结构化并发的保证在起作用——分支不能超过其父上下文的存在时间，这防止了孤立任务的累积。但这也意味着 branch 不适合那些*必须*完成的工作，比如记录分析事件或保存玩家进度。对于这些任务，应使用 `spawn`，它独立于其创建作用域运行。

与 rush 一样，branch 也面临迭代表达式的限制。你不能直接在循环或 for 体中使用 branch，因为这可能导致无限制的后台任务。解决方法仍然是相同的：将 branch 封装在一个异步函数中，然后从迭代中调用该函数。

## 非结构化并发

### spawn 表达式

虽然结构化并发优雅地处理了大多数并发编程需求，但有时你需要打破层次化的任务结构。`spawn` 表达式是 Verse 对非结构化并发的唯一让步，允许你启动一个独立于其创建作用域生存的异步操作。将 spawn 视为应急出口——在需要时功能强大，但不是在典型并发模式中的首选。

<!--versetest
LongRunningTask()  <suspends> :int=0
-->
<!-- 11 -->
```verse
# spawn returns a task(t) object you can control
BackgroundTask:task(int) = spawn{LongRunningTask()}

# Or fire-and-forget without capturing the task
spawn{LongRunningTask()}
Print("Spawned task continues even after this scope exits")
```

使 spawn 独一无二的是它在任何地方都能工作的能力。与所有需要异步上下文的结构化并发表达式不同，spawn 可以在立即函数、类构造函数、模块初始化中工作——任何你可以编写代码的地方。这种通用性伴随着责任。你产生的任务成为一个自由代理，无论创建它的代码发生什么，它都会继续工作。没有自动清理，没有父子关系，只有一个独立的任务追求其目标。

被生成的函数必须具有 `<suspends>` 效果。你**不能**生成具有 `<decides>` 效果的函数：

<!--versetest-->
<!-- 12 -->
```verse
AsyncWork()<suspends>:void =
    Sleep(1.0)
    Print("Background work complete")

FailableWork()<decides>:void =
    false?  # Might fail

# Valid: spawning suspends function
spawn{AsyncWork()}

# Invalid: cannot spawn decides function
# spawn{FailableWork()}  # ERROR: spawn requires suspends, not decides
```

这个限制的存在是因为生成的任务独立运行，没有父级来处理它们的失败。由于 `<suspends>` 和 `<decides>` 不能在同一函数上组合，并且 spawn 需要 `<suspends>`，因此不能生成带有 `<decides>` 的函数。如果你需要生成可失败的工作，将其包装在一个在内部处理失败的挂起函数中：

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

spawn{SafeFailableWork()}  # Valid - failure handled inside
```

Spawn 在特定的架构模式中找到自己的位置。监控整个会话期间游戏状态的全局后台服务、即使触发上下文结束也必须完成的清理任务，或者立即代码需要触发异步操作的集成点——这些场景证明了使用 spawn 而非结构化替代方案的合理性。

与 branch 的对比阐明了设计理念。Branch 为你提供了结构化的即发即弃并发，但其任务在封闭作用域退出时被取消。Spawn 为你提供的任务可以超过其创建作用域的寿命——当工作*必须*完成时使用它，无论启动它的代码发生什么。当取消可以接受时选择 branch；当不能接受时选择 spawn。

**使用生成的任务：**

`spawn` 表达式返回一个 `task(t)` 对象，其中 `t` 是被生成函数的返回类型。这个任务对象提供了控制和查询生成操作的方法——你可以取消它，等待它完成，或检查其当前状态。虽然 spawn 创建了不需要管理的独立任务，但访问任务对象使你有能力在需要时进行干预。请参阅下面的 "task(t) 类型" 部分，了解任务对象及其功能的完整细节。

## task(t) 类型

`task(t)` 类型表示一个正在执行的异步操作的句柄，其中 `t` 是该操作的返回类型。虽然 Verse 在后台为所有异步表达式自动创建任务，但只有 `spawn` 让你直接访问可以控制和查询的任务对象。

<!--versetest-->
<!-- 14 -->
```verse
# spawn returns task(t) where t is the return type
BackgroundWork()<suspends>:int =
    Sleep(2.0)
    42

MyTask:task(int) = spawn{BackgroundWork()}
# MyTask is a handle to the spawned operation
```

任务对象提供了用于管理异步操作的丰富接口：你可以取消它们，等待它们完成，并查询它们的当前状态。这种控制对于实现需要协调多个独立操作的健壮并发系统至关重要。


一个任务在其生命周期中会经历几个不同的状态：

**Active（活跃）**：任务当前正在运行或已挂起，但尚未完成。它仍在工作或等待恢复。

**Completed（已完成）**：任务成功完成并返回了结果。一旦完成，任务再也不会改变状态。（终态）

**Canceled（已取消）**：任务在能够完成之前被取消。这是一个终态——已取消的任务无法恢复。

**Settled（已终结）**：如果任务已达到 Completed 或 Canceled 状态，则视为已终结。已终结的任务不再执行。（终态）

**Uninterrupted（未被中断）**：如果任务成功完成且未被取消，则视为未被中断。这等同于 Completed 状态。（别名）

**Interrupted（已中断）**：如果任务被取消，则视为已中断。这等同于 Canceled 状态。（别名）

### Task.Cancel()

!!! note "未发布功能"
    Cancel() 方法目前尚未发布。
	
`Cancel()` 方法请求取消一个任务。这是一个安全操作，可以在任何状态的任何任务上调用：

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

# Request cancellation
LongTask.Cancel()

# Safe to call multiple times
LongTask.Cancel()  # No error

# Safe to call on completed tasks (has no effect)
```
<!-- #> -->

取消是协作式的——任务不会立即停止。相反，它会收到一个取消信号，该信号在下一个挂起点被检查。然后任务优雅地展开，允许清理代码运行。有关取消何时生效的详细信息，请参阅下面的"挂起点与取消"。

对已完成任务调用 `Cancel()` 是安全的，并且没有任何效果。这意味着你可以取消任务而不用担心完成和取消之间的竞争条件。

### Task.Await()

`Await()` 方法挂起调用上下文直到任务完成，然后返回任务的结果：

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

# Wait for task to complete and get result
Result:int = ComputeTask.Await()
Print("Task returned: {Result}")
```
<!-- #> -->

**Await() 的关键行为：**

- **阻塞直到完成**：如果任务仍在运行，`Await()` 会挂起直到它完成
- **如果已完成则立即返回**：如果任务已经完成，`Await()` 会立即返回缓存的结果（粘性）
- **可以多次调用**：你可以重复等待同一个任务，总是得到相同的结果
- **传播取消**：如果被等待的任务被取消，`Await()` 会将取消传播给调用者

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

# First await - waits for completion
FirstResult := MyTask.Await()

# Second await - returns cached result immediately
SecondResult := MyTask.Await()

# FirstResult = SecondResult
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

    # Wait for all to complete
    Results := sync:
        T1.Await()
        T2.Await()
        T3.Await()

    Print("All tasks complete: {Results(0)}, {Results(1)}, {Results(2)}")
```


### 挂起点与取消

Verse 中的任务取消遵循协作式模型。Verse 不是强制终止任务（这可能导致资源处于不一致状态），而是在**挂起点**发送任务检查的取消信号。当任务收到取消信号时，它有机会在终止前清理资源。这种协作方法既防止了数据损坏，又确保了响应式的取消。

挂起点是异步任务可以暂停和恢复的特定位置。这些是唯一的地方：

- 任务可以被挂起以允许其他任务运行
- 取消信号被检查和处理的
- 运行时可以在并发任务之间切换

常见的挂起点包括：

**计时操作：**

<!--versetest
F()<suspends>:void=
    Sleep(1.0)
    NextTick() 
<#
-->
<!-- 30 -->
```verse
Sleep(1.0)  # Suspends for duration, checks cancellation when resuming
NextTick()  # Waits one simulation update, checks cancellation
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
Result := SomeAsyncFunction()  # Suspension point at the call
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
sync:  # Suspension point when entering sync
    Op1()
    Op2()
# Suspension point when sync completes
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
Result := MyTask.Await()  # Suspension point while waiting
```
<!-- #> -->

**重要：** 挂起点之间的立即代码不间断地运行。如果你编写一个没有挂起点的长计算循环，该任务无法被取消，直到它到达下一个挂起点：

<!--versetest
ComputeExpensiveOperation(:int):void={}
-->
<!-- 35  -->
```verse
# Cannot be canceled during the loop
LongComputation()<suspends>:void =
    for (I := 0..1000000):
        # No suspension points - runs to completion
        ComputeExpensiveOperation(I)
    Sleep(0.0)  # First cancellation check happens here!

# Can be canceled every iteration
ResponsiveComputation()<suspends>:void =
    for (I := 0..1000000):
        ComputeExpensiveOperation(I)
        Sleep(0.0)  # Cancellation checked every iteration
```

如果你需要使长时间运行的计算可取消，请使用 `Sleep(0.0)` 或 `NextTick()` 插入定期的挂起点，这些调用在实际没有延迟的情况下让出控制权，但允许取消检查。

取消通过任务层级级联。当父任务被取消时，其所有子任务也会收到取消信号。这种级联行为维护了子任务在结构化并发中不会超过父任务生命周期的约束，防止资源泄漏并确保可预测的清理。例如，在 race 表达式中，当胜者完成时，race 任务会向所有失败的子任务发送取消信号，这些信号然后级联到这些失败任务可能创建的任何任务。

## 清理与资源管理

### defer: 块

`defer:` 块提供了有保证的清理代码，这些代码在其封闭作用域退出时执行——无论是通过正常完成、失败还是取消。关于 `defer` 语义的完整描述，包括执行顺序、作用域规则和限制，请参见[Defer 语句](07_control.md#defer-statements)。

本节重点关注 `defer` 如何与并发交互。

**defer: 与取消：**

当并发任务被取消时（例如，失败的 `race` 臂或被取消的 `spawn`），defer 块在栈从取消点展开时执行。这使得 `defer` 对于并发代码中的资源清理至关重要：

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
                ReleaseResource(Resource)  # Runs when this arm is cancelled
            LongRunningTask(Resource)
        block:
            Sleep(10.0)  # Timeout
    # If timeout wins, first block is cancelled and defer runs
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

    # If this task is canceled, defer runs during unwinding
    LongOperation()
```

**defer 中不能有挂起操作：**

defer 块**不能**包含挂起操作。这确保清理立即发生，没有延迟：

<!--versetest
ValidDefer()<suspends>:void =
    defer:
        Print("Cleanup happens immediately")
    Sleep(1.0)
<#
-->
<!-- 44 -->
```verse
# ERROR: Cannot use suspending operations in defer
BadDefer()<suspends>:void =
    defer:
        Sleep(1.0)  # ERROR: defer blocks cannot suspend
        NextTick()  # ERROR: defer blocks cannot suspend
```
<!-- #> -->

这个限制至关重要——如果 defer 块可以挂起，清理可能会无限期延迟，违背了其作为有保证的终结处理的目的。但是，defer 块*可以*使用 `spawn` 来进行即发即弃的异步操作。

## 计时函数

用于在指定持续时间内挂起执行的基本计时函数：

<!--versetest
M()<suspends>:void =
    Sleep(1.0)

    Sleep(0.0)
<#
-->
<!-- 46 -->
```verse
# Suspend for 1 second
Sleep(1.0)

# Suspend for one frame (smallest possible delay)
Sleep(0.0)
```
<!-- #> -->

`Sleep(0.0)` 模式值得特别关注。虽然它不增加实际延迟，但它有两个关键目的：

1. **创建一个用于取消检查的挂起点**
2. **让出控制权**给其他并发任务，防止一个任务独占执行

这使得 `Sleep(0.0)` 对于响应式并发代码至关重要：

<!--versetest
ProcessFrame():void={}
ExpensiveOperation(:int):void={}
-->
<!-- 47 -->
```verse
# Without Sleep(0.0) - cannot be cancelled during loop
UnresponsiveLoop()<suspends>:void =
    for (I := 0..10000):
        ExpensiveOperation(I)
    # Cancellation only checked after all iterations

# With Sleep(0.0) - responsive to cancellation
ResponsiveLoop()<suspends>:void =
    for (I := 0..10000):
        ExpensiveOperation(I)
        Sleep(0.0)  # Yields and checks cancellation each iteration
```

**最佳实践：** 在长时间运行的循环中插入 `Sleep(0.0)`，以确保任务对取消保持响应，并与其他并发操作公平地共享执行时间。

### NextTick()

!!! note "未发布功能"
    NextTick() 目前尚未发布。

`NextTick()` 函数挂起执行直到下一次模拟更新（tick）。与 `Sleep(0.0)`（让出控制权，如果没有其他工作待处理则可能在同一 tick 中恢复）不同，`NextTick()` 保证在恢复之前至少发生一次模拟更新：

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
# Wait for exactly one simulation tick
NextTick()

# Multiple ticks
NextTick()  # Wait 1 tick
NextTick()  # Wait another tick
NextTick()  # Wait a third tick
```
<!-- #> -->

`NextTick()` 对于需要与模拟更新同步的游戏逻辑至关重要：

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
# Process game logic every tick
GameLoop()<suspends>:void =
    loop:
        ProcessGameLogic()
        UpdatePhysics()
        CheckCollisions()
        NextTick()  # Wait for next simulation update

# Delay action by specific number of ticks
DelayByTicks(TickCount:int)<suspends>:void =
    for (I := 1..TickCount):
        NextTick()

# Wait 5 ticks before executing action
DelayByTicks(5)
PerformAction()
```
<!-- #> -->

**Sleep(0.0) 与 NextTick() 对比：**

| 特性     | Sleep(0.0)                | NextTick() |
|---------  |------------               |------------|
| 时机      | 可能在同一 tick 中恢复     | 始终等待下一个 tick |
| 用途      | 让出控制权以进行取消检查   | 与模拟更新同步 |
| 保证      | 创建挂起点                | 保证 tick 边界 |

两者都创建用于取消的挂起点，但当你需要与模拟时钟对齐时，`NextTick()` 提供了更强的时间保证。

<!--versetest
ProcessFrame()<computes>:logic=false
-->
<!-- 50 -->
```verse
# Common patterns
LoopWithDelay()<suspends>:void =
    loop:
        ProcessFrame()
        Sleep(0.033)  # ~30 FPS

TickBasedLoop()<suspends>:void =
    loop:
        if (ProcessFrame()=false): 
             break
        NextTick()  # Once per simulation tick	
```

计时模式：

<!--versetest
DoAction():void={}
UpdateLogic()<computes>:void={}
Float(:int)<computes>:float=0.0
SetPosition(:float):void={}
-->
<!-- 51 -->
```verse
# Delayed action
PerformDelayedAction()<suspends>:void =
    Sleep(2.0)  # Wait 2 seconds
    DoAction()

# Periodic execution
PeriodicUpdate()<suspends>:void =
    loop:
        UpdateLogic()
        Sleep(1.0)  # Update every second

# Animation timing
AnimateMovement(Start:float,End:float)<suspends>:void =
    for (T := 0..10):
        SetPosition(Lerp(Start, End, Float(T)/10.0))
        Sleep(0.0)  # One frame
```

### 获取当前时间：GetSecondsSinceEpoch

`GetSecondsSinceEpoch()` 函数返回当前的 Unix 时间戳——自 1970 年 1 月 1 日 00:00:00 UTC 以来经过的秒数。此函数对于给事件打时间戳、测量持续时间以及与使用 Unix 时间的外部系统同步至关重要。

<!--versetest
LogEvent(Message:string):void =
    Timestamp := GetSecondsSinceEpoch()
    Print("[{Timestamp}] {Message}")
<#
-->
<!-- 52 -->
```verse
# Get current timestamp
CurrentTime := GetSecondsSinceEpoch()
# Returns something like 1716411409.0 (May 22, 2024)

# Log an event with timestamp
LogEvent(Message:string):void =
    Timestamp := GetSecondsSinceEpoch()
    Print("[{Timestamp}] {Message}")
```
<!-- #> -->

**关键的事务性行为：**

在单个事务内，`GetSecondsSinceEpoch()` 每次调用返回**相同的值**。这确保了确定性行为并防止了与时间相关的竞争条件：

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

    # Perform complex operations
    DoExpensiveWork()
    PerformDatabaseUpdates()

    EndTime := GetSecondsSinceEpoch()

    # StartTime = EndTime!
    # Time is "frozen" within the transaction
    Duration := EndTime - StartTime  # Always 0.0
```
<!-- #> -->

这种事务一致性是故意的——它防止了不确定性行为，即事务重试可能因时间推进而产生不同结果。如果事务失败并重试，重试尝试中所有对 `GetSecondsSinceEpoch()` 的调用将返回一个新的、一致的时间戳。

**使用场景：**

**事件日志记录与调试：**

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
    Cooldown:float = 5.0  # 5 second cooldown

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

**用于外部系统的绝对时间戳：**

当与使用 Unix 时间戳的外部系统、数据库或 API 交互时：

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
# Timestamp for external analytics
AnalyticsEvent := map{
    "event_type" => "player_action",
    "timestamp" => GetSecondsSinceEpoch(),
    "player_id" => MyPlayerID
}
SendToAnalytics(AnalyticsEvent)

# Comparing with server timestamps
ServerTime := FetchServerTime()
LocalTime := GetSecondsSinceEpoch()
ClockSkew := LocalTime - ServerTime
```
<!-- #> -->

**重要说明：**

- 返回 `float` 类型的秒数（可能有小数部分以提供毫秒精度）
- 位于 `/Verse.org/Verse` 模块中——使用 `using { /Verse.org/Verse }` 访问
- 不受 `Sleep()` 或其他挂起影响——测量的是真实世界的时间
- 在事务内保持一致以确保确定性
- 每个新事务获得一个全新的时间戳

**与 Sleep 结合用于基于时间的逻辑：**

<!--versetest
PerformAction<public>()<suspends>:void = {}
-->
<!-- 59 -->
```verse
# Wait until a specific time
WaitUntil(TargetTime:float)<suspends>:void =
    loop:
        if (GetSecondsSinceEpoch() >= TargetTime) then:
            break
        Sleep(0.1)  # Check every 100ms

# Schedule an action for the future
ScheduleDelayedAction(DelaySeconds:float)<suspends>:void =
    TargetTime := GetSecondsSinceEpoch() + DelaySeconds
    WaitUntil(TargetTime)
    PerformAction()
```

请注意，事务一致性意味着你不能在单个事务内使用 `GetSecondsSinceEpoch()` 来测量时间。对于测量不跨事务的操作执行时间，请使用性能分析工具或外部计时机制。

## 事件与同步

事件提供了并发任务之间协调的同步原语。它们实现了生产者-消费者和观察者模式，允许任务之间相互通知并等待特定条件。事件弥补了独立并发操作之间的差距，无需共享可变状态即可实现通信。

### 基本事件

`event(t)` 类型创建了一个通信渠道，生产者在其中发送值，消费者等待这些值。每个信号将一个值传递给每个等待的任务：

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
# Create an event channel for integers
GameEvent := event(int){}

# Producer: signals values to the event
ProducerTask()<suspends>:void =
    Sleep(1.0)
    GameEvent.Signal(42)

# Consumer: awaits values from the event
ConsumerTask()<suspends>:void =
    Value := GameEvent.Await()
    ProcessValue(Value)

sync:
    ProducerTask()
    ConsumerTask()
```
<!-- #> -->

当在事件上调用 `Await()` 时，调用任务会挂起，直到另一个任务调用 `Signal()` 并传入一个值。被发送的值被传递给一个等待的任务，执行恢复。如果多个任务等待同一个事件，每个 `Signal()` 恰好唤醒一个等待者——信号和等待一一配对。

这种一对一匹配使得事件非常适合任务协调。想想一个玩家动作系统：输入处理器发送按钮按下信号，而游戏系统则等待它们。或者考虑一个 AI 寻路请求：游戏逻辑发送目标请求，而寻路系统等待并处理它们。

事件可以与结构化并发自然地配合使用。你可以在 `sync` 块中使用它们来协调并行操作，或者与 `race` 结合实现事件等待的超时：

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
# Wait for event with timeout
Result := race:
    block:
        Value := GameEvent.Await()
        option{Value}
    block:
        Sleep(5.0)
        false  # Timeout - no value received
```
<!-- #> -->

### 粘性事件

!!! note "未发布功能"
    粘性事件（Sticky Events）目前尚未发布，暂时不可用。

基本事件将每个信号恰好传递给一个等待者，而 `sticky_event(t)` 会记住最后一个发送的值，并将其传递给所有后续的等待，直到有新值被发送：

<!--NoCompile-->
<!-- 62 -->
```verse
StateEvent := sticky_event(int){}

# Signal once
StateEvent.Signal(100)

# Multiple awaits all receive the same value
Value1 := StateEvent.Await()  # Gets 100
Value2 := StateEvent.Await()  # Gets 100 again
Value3 := StateEvent.Await()  # Still gets 100

# New signal updates the sticky value
StateEvent.Signal(200)
Value4 := StateEvent.Await()  # Gets 200
Value5 := StateEvent.Await()  # Also gets 200
```

粘性事件在表示多个消费者需要观察的状态变化时表现出色。与每个信号在一次等待后消失的基本事件不同，粘性事件维护当前状态。考虑一个游戏阶段系统：当阶段从"大厅"变为"游戏中"时，每个检查阶段的系统都应该看到"游戏中"，而不是一个系统消耗了信号而其他系统错过它。

粘性行为创建了一种最终一致的状态。如果一个任务等待一个粘性事件，它保证能看到最近的信号，即使该信号发生在等待之前。这使得粘性事件非常适合配置更新、模式切换，或任何"当前状态是什么？"比"刚刚发生了什么变化？"更重要的场景。

### 可订阅事件

!!! note "未发布功能"
    可订阅事件（Subscribable Events）目前尚未发布，暂时不可用。

`subscribable_event` 类型实现了观察者模式，允许多个处理程序对每个信号做出反应。与等待任务显式等待的事件不同，可订阅事件允许你注册回调函数，这些函数在发送值时自动执行：

<!--NoCompile-->
<!-- 63 -->
```verse
LogScore(:int):void={}
UpdateUI(:int):void={}
CheckAchievements(:int):void={}

ScoreEvent := subscribable_event(int){}

# Subscribe multiple handlers
Logger := ScoreEvent.Subscribe(LogScore)
UIUpdater := ScoreEvent.Subscribe(UpdateUI)
AchievementChecker := ScoreEvent.Subscribe(CheckAchievements)

# Signal invokes all subscribed handlers
ScoreEvent.Signal(1000)  # Calls LogScore(1000), UpdateUI(1000), CheckAchievements(1000)

# Unsubscribe to stop receiving signals
Logger.Cancel()
ScoreEvent.Signal(2000)  # Only calls UpdateUI and CheckAchievements
```

每个订阅返回一个 `cancelable` 对象，你可以通过调用 `Cancel()` 来取消订阅。一旦取消，该处理程序停止接收信号。这提供了对处理程序生命周期的细粒度控制，对于在游戏过程中来去自如的系统至关重要。

可订阅事件在广播场景中表现出色，其中多个独立的系统需要对同一事件做出反应。当玩家得分时，UI 需要更新，音频系统需要播放声音，成就系统需要检查解锁，分析系统需要记录事件。使用可订阅事件，每个系统独立注册其处理程序，每个信号到达所有感兴趣的一方。

### awaitable 和 signalable 接口

事件建立于两个基础接口之上，你可以使用它们创建自定义同步类型：

<!--NoCompile-->
<!-- 64 -->
```verse
awaitable(t:type) := interface:
    Await()<suspends>:t

signalable(t:type) := interface:
    Signal(Value:t):void
```

`awaitable` 接口表示可以被等待的任何东西，而 `signalable` 表示可以发送信号的任何东西。通过分离这些能力，Verse 实现了对谁能产生值以及谁能消费值的精确控制。

你可以将 `awaitable` 参数传递给只应从事件读取的函数，防止意外发送：

<!--versetest
ProcessValue(:int):void={}
-->
<!-- 65 -->
```verse
# This function can only await, not signal
ConsumerFunction(Source:awaitable(int))<suspends>:void =
    Value := Source.Await()
    ProcessValue(Value)
    # Source.Signal(123)  # ERROR: awaitable doesn't have Signal

# This function can only signal, not await
ProducerFunction(Target:signalable(int)):void =
    Target.Signal(42)
    # Value := Target.Await()  # ERROR: signalable doesn't have Await
```

这种分离为生产者-消费者关系创建了清晰的接口。一个队列实现可能向消费者暴露一个 `awaitable` 接口用于读取，向生产者暴露一个 `signalable` 接口用于写入，确保任何一方都不能意外使用错误的操作。

### 事务性行为

事件订阅参与 Verse 的事务系统。如果包含 `Subscribe()` 调用的事务失败并回滚，订阅永远不会生效：

<!--NoCompile-->
<!-- 66 -->
```verse
Handler(:int):void={}

MyEvent := subscribable_event(int){}

# Subscription in a failing transaction
if:
    Sub := MyEvent.Subscribe(Handler)
    false?  # Transaction fails and rolls back

# Subscription was rolled back - handler not called
MyEvent.Signal(100)
```

同样，`Cancel()` 操作也是事务性的。如果你在稍后失败的事务中取消订阅，订阅仍然有效：

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

# Cancel in a failing transaction
if:
    Sub.Cancel()
    false?  # Transaction fails

# Cancel was rolled back - subscription still active
MyEvent.Signal(100)  # Handler still gets called
```

这种事务集成确保事件订阅与其他事务操作保持一致性。如果你正在建立一个复杂的系统，其中订阅事件是可能失败的更大初始化的一部分，事务系统保证要么所有初始化都成功，要么都不成功，防止可能导致微妙错误的部分设置。

### 事件模式与使用场景

**请求-响应：** 使用基本事件在系统之间实现请求-响应模式：

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
PathRequest := event(tuple(int, int)){}  # (start, goal)
PathResponse := event(int){}             # path result

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

# Systems await current phase without missing updates
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

**多系统通知：** 当许多系统需要对相同事件做出反应时，使用可订阅事件：

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

# Each system subscribes independently
InitializeSystems():void =
    ItemPickedUp.Subscribe(UpdateInventoryUI)
    ItemPickedUp.Subscribe(PlayPickupSound)
    ItemPickedUp.Subscribe(CheckCollectionAchievement)
    ItemPickedUp.Subscribe(LogItemPickup)

# Single signal reaches all systems
OnPlayerPickupItem(ItemID:int):void =
    ItemPickedUp.Signal(ItemID)
```

事件补充了结构化并发，提供了比单个并发操作更长寿命的通信渠道。`sync`、`race`、`rush` 和 `branch` 组织了任务之间的相对执行方式，而事件则组织了任务之间如何共享信息和协调行动。

## 常见模式与最佳实践

使用 `race` 实现带超时的操作：

<!--versetest
ActualOperation()<suspends>:void={}
-->
<!-- 71 -->
```verse
PerformWithTimeout()<suspends>:logic =
    race:
        block:
            ActualOperation()
            true  # Success
        block:
            Sleep(5.0)  # 5 second timeout
            false  # Timeout
```

并发初始化多个系统：

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

启动不阻塞游戏玩法的后台任务：

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
    # Main game continues while background tasks run
```

带延迟生成实体：

<!--versetest
enemy_class := class {     Spawn()<suspends>:void={} }
-->
<!-- 74 -->
```verse
SpawnWave(Enemies:[]enemy_class)<suspends>:void =
    for (Enemy : Enemies):
        spawn{Enemy.Spawn()}
        Sleep(0.5)  # Half second between spawns
```

## 限制与注意事项

### 迭代限制

迭代与某些并发表达式之间的交互需要仔细考虑。Rush 和 branch 不能直接在 loop 或 for 体中使用，这个限制防止了无限制的任务累积。当你编写一个可能执行成百上千次的循环时，允许直接使用 rush 或 branch 会创建那么多后台任务，可能压垮系统。

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
# Not allowed
for (I := 0..10):
    rush:  # ERROR: Cannot use rush in loop
        Operation1()
        Operation2()

# Workaround - wrap in function
ProcessWithRush(I:int)<suspends>:void =
    rush:
        Operation1()
        Operation2()

for (I := 0..10):
    ProcessWithRush(I)  # OK
```
<!-- #> -->

这个限制强制你在迭代中创建后台任务时要有意图性。通过将并发操作封装在函数中，你承认了任务的创建并在代码结构中使其显式化。这种小小的摩擦防止了意外的资源耗尽，同时在真正需要时保持使用这些模式的灵活性。

### 抽象而非实现

Verse 有意地抽象掉了底层的线程和调度机制。你不会找到线程创建 API、线程局部存储或显式的同步原语如互斥锁或信号量。这不是一个限制，而是一种设计理念。通过使用更高级别的任务抽象，Verse 消除了整类错误——没有数据竞争，没有因错误锁顺序导致的死锁，没有忘记的解锁调用。

并发模型是协作式而非抢占式的。任务在挂起点自愿让出控制权，而不是被调度器强制中断。这种协作性质使得推理并发代码更容易，因为你确切知道任务切换可能发生的位置。它还与游戏引擎的基于帧的执行模型自然集成，其中可预测的时序至关重要。

### 效果交互

使 Verse 并发安全的效果系统也引入了一些限制。`decides` 效果（标记可能失败的函数）不能与 `suspends` 效果组合。这种分离保持了失败模型和并发模型的正交性，防止了难以推理的复杂交互。事务性操作和某些特定于设备的操作在并发上下文中使用时也可能有限制，确保必须原子的操作保持原子性。

