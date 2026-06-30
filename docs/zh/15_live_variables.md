# 实时变量

!!!注意“未发布的功能”
    实时变量尚未发布。本章记录了当前不可用的计划功能。

实时变量代表了 Verse 中的反应式编程范例，
使变量能够在以下情况下自动重新计算其值
依赖关系发生变化。而不是需要显式回调或事件
处理程序、实时变量建立数据之间的动态关系，
创建一个声明性系统，使更改自然传播
通过你的代码。

传统编程需要手动跟踪依赖关系和
当值改变时显式更新。如果变量 `A` 取决于
变量 `B`，您必须记住每当 `B` 更改时更新 `A`，
通常通过回调函数或观察者模式。实时变量
通过自动跟踪哪些变量来消除这种簿记
在评估期间读取并重新评估这些依赖项
改变。这会创建更易于维护的代码，其目的是 `A`
应始终反映 `B` 的某些功能 - 直接表达为
代码本身。

实时变量为反应式编程结构奠定了基础，
包括 `await`、`upon` 和 `when`。了解实时变量是
对于使用 Verse 的事件驱动编程模型至关重要，
特别是对于需要许多值的游戏开发场景
保持同步。

<a id="live-expressions"></a>
## 实时表达式

*实时表达*在对象之间建立动态关系
变量和守卫。一旦确定，目标将自动
每当守卫的任何依赖项发生变化时都会重新评估，保持
变量同步。

<!--versetest-->
<!-- 01-->
```verse
var X:int = 0
var Y:int = 0
set live X = Y+1  # X 现在跟踪 Y
set Y = 5         # X自动变成6
```
<!--
X = 6
-->

上面`set live X = Y+1`是一个live表达式，目标是
先前声明的变量 `X` 和防护是表达式
`Y+1` 依赖于变量 `Y`。

活动变量扩展了可变变量（参见
[可变性](05_mutability.md)) 具有自动依赖性跟踪：
在评估保护表达式期间读取的任何变量都是
被跟踪。当这些变量中的任何一个发生变化时，警卫就会
重新评估，目标变量自动更新。

### 声明形式

实时变量可以通过多种方式声明，每种方式适合不同的用例：

<!--NoCompile-->
<!-- 02-->
```verse
# 实时变量声明
var live X:int = Exp

# 对现有变量的实时赋值
var X:int = 0
# ...后来...
set live X = Exp

# 不可变的实时变量
live Y:int = Exp

# 具有函数类型的变量（具有<reads>效果）
var X: F = Exp            # 正常计算的初始值
var live X: F = Exp       # 跟踪依赖项的初始值

# 具有函数类型的不可变变量（具有 <reads> 效果）
X: F = Exp                # 正常计算的初始值
live X: F = Exp           # 跟踪依赖项的初始值

# 输入输出变量对
var In->Out: F = Exp      # 正常计算的初始值
var live In->Out: F = Exp # 跟踪依赖项的初始值

In->Out: F = Exp          # 正常计算的初始值
live In->Out: F = Exp     # 跟踪依赖项的初始值
```
最常见的形式 `var live X = Exp` 创建一个可变变量
其初始值来自评估守卫，然后
每当依赖项发生变化时都会更新。守卫表达式可以读取
其他变量，并且跟踪这些读取以确定
依赖关系。

赋值形式 `set live X = Exp` 转换现有变量
通过附加一个守卫进入一个实时变量。当您
需要在初始化后或有条件地使变量反应
基于程序状态。

仅使用 `live Y = Exp` 声明的不可变实时变量不能
直接写入，但当他们的守卫出现时仍然会自动更新
依赖关系发生变化。这提供了一个只读的无功值，很有用
对于永远不应该手动覆盖的派生计算。

当变量的类型是具有 `<reads>` 效果的函数时，
变量通过其类型变得活跃（分配被过滤
通过函数，并更改函数的依赖项
触发重新计算）。声明中的 `live` 关键字
确定初始表达式 `Exp` 是否也被跟踪
依赖关系。没有`live`，`Exp`评估一次；与 `live`，
`Exp` 中的依赖项会被跟踪，并且可以在
第一个作业。

输入-输出对创建两个变量，其中一个变量捕获原始值
另一个持有转变后的价值观。同样，`live` 关键字
控制是否跟踪初始表达式 `Exp`
依赖关系。

以下部分详细介绍了这些更复杂的形式。

### 函数作为类型

Verse 允许将函数用作变量的类型。当一个
具有 `<reads>` 效果的函数被用作类型，变量
自动变为活动状态，并在函数运行时更新
依赖关系发生变化。

<!--versetest-->
<!-- 03 FAILURE
  Line 8: Script Error 3547: Expected a type, got function identifier instead.
  Line 8: Script Error 3601: Data definitions at this scope must be initialized with a value.
-->
```verse
var Mult:int = 2

Multiply(Arg: int)<reads>:int = Arg * Mult

var X : Multiply

set X = 10        # X 得到 20
set Mult = 1      # X 得到 10
```
<!--
X = 10
-->

在此示例中，`Multiply` 具有双重角色：它既是一个函数
以及变量 `X` 的类型。

**作为类型：** 当您声明 `var X : Multiply` 时，会发生以下情况：

- `X`的存储类型变为`int`（函数的返回类型）
- 分配给 `X` 的值必须是 `int`（函数的参数类型）
- 每个赋值都经过函数：`set X = 10` 调用 `Multiply(10)` 并存储结果

**作为现场表达：** 因为 `Multiply` 具有 `<reads>` 效果
（它读取可变变量`Mult`），变量声明变成
以 `Multiply` 作为守护者的实时表达。这创造了两种方式
值变化：

1. **直接赋值：** `set X = 10` 通过`Multiply`过滤值，存储20
2. **依赖更新：** `set Mult = 1` 触发重新计算，将 `X` 更新为 10

这种模式优雅地结合了转换（每次写入都是
过滤）具有反应性（依赖项的更改会触发更新）。

<a id="input-output-variables"></a>
### 输入输出变量

输入输出变量对捕获原始输入值及其
转换后的输出。语法 `var In->Out:F=Exp` 创建两个
相关变量，其中 `Out` 是可写变量，`In`
在传递之前自动存储未转换的值
功能 `F`。

这种模式可以优雅地处理常见的游戏场景，其中值必须
保持在动态约束内。考虑必须保留的健康
在界限内：

<!--NoCompile-->
<!-- 04-->
```verse
clamp := class:
    var Lower:int = 0
    var Upper:int = 100
    Evaluate(Value:int)<reads>:int =
        if (Value < Upper) then:
           if (Value > Lower) then Value else Lower
        else:
           Upper

Clamp := clamp{}
var BaseHealth->Health: Clamp.Evaluate = 50

# 生命值 = 50（限制为 [0, 100]）
set Health = 75      # 基础生命值 = 75，生命值 = 75
set Health = 120     # 基础生命值 = 120，生命值 = 100（固定）
set Clamp.Upper = 60 # 基础生命值 = 120，生命值 = 60（重新固定）
```
当您写入 `Health` 时，会发生两件事：

 1.原始值存储在`BaseHealth`中
 2、通过`Clamp.Evaluate`传递数值，结果存放在`Health`中

因为 `Clamp.Evaluate` 具有 `<reads>` 效果（它读取可变的
变量 `Lower` 和 `Upper`)，这成为实时表达式。当
约束发生变化，`Health` 会自动重新计算
`BaseHealth`。

**它是如何运作的**

声明 `var BaseHealth->Health: Clamp.Evaluate = 50` 创建一个实时表达式，其中：

- `BaseHealth` 存储原始输入值（从外部角度只读）
- `Health` 存储钳位值（读写）
- `Clamp.Evaluate` 是具有 `<reads>` 效果的变换函数

对象 `Clamp` 是类 `clamp` 的实例，具有可变边界 `Lower` 和 `Upper`。由于 `Evaluate` 读取这些可变变量，因此对它们的更改会触发重新计算：

- `set Health=75` — 值不变地传递，因此 `BaseHealth` 和 `Health` 都变为 75
- `set Health=120` — 超过 `Upper`，因此 `BaseHealth` 变为 120，但 `Health` 变为 100
- `set Clamp.Upper=60` — 约束发生变化，触发重新计算：`Health` 更新为 60，而 `BaseHealth` 仍为 120

使用像 `Clamp.Evaluate` 这样的实例方法允许多个
同一上下文中的独立夹具，每个夹具都有自己的动态
界限。

**访问控制**

输入输出变量的范围可以控制
通过添加访问说明符独立地：例如 `var
In<private>->Out<public>:t` 使基值私有，而
公开暴露约束值。

### 受限效果与稳定性

动态变量防护不能具有 `<writes>` 效果。这个
基本限制可防止守卫期间的副作用
评估，该 Verse 必须能够在任何时候自由执行
依赖关系发生变化。

<!--NoCompile-->
<!-- 05-->
```verse
# 错误：守卫无法写入
var X:int = 0
var GlobalCounter:int = 0
set live X = block:
    set GlobalCounter += 1  # 不允许！
    GlobalCounter
```
具有相互依赖性的实时变量可以形成循环。当目标
表达式使用幂等运算并且值是可比较的，这些
循环可以自然地收敛到固定点。

<!--versetest-->
<!-- 06-->
```verse
var X:int = 2
var Y:int = 2

set live X = if (Y < 0) then 0 else Y - 1
set live Y = if (X < 0) then 0 else X - 1

# 评估为：X=1、Y=0、X=-1、Y=0（稳定）
```
<!--
X=-1
Y=0
-->

如果变量的类型是可比较的，则重新评估防护
直至数值稳定。在此示例中，`X` 递减至 -1，`Y`
钳制为 0，`X` 将重新计算但再次产生 -1，因此
系统稳定下来。

然而，没有适当终止条件的循环可能会
发散。Verse不能阻止所有分歧——必须小心
设计相互依赖的实时变量。

这有一个微妙的含义：因为任何变量都可能变得活跃
创建后，必须假定读取任何变量可能会
触发防护评估，并在最坏的情况下触发一个周期。的
效果系统解释了这一点：`<writes>` 效果意味着
`<diverges>` 因为任何写入都可能触发循环活动变量
评价。下面说明了当 `X` 为时的循环定义
大于0：

<!--NoCompile-->
<!-- 07-->
```verse
var X:int = 0
var live Y:int = if (X>0) then X+1 else 0

set live X = Y
set X = 1  # 错误！循环评估
```
### 跟踪依赖关系

实时变量在运行时动态跟踪依赖关系，而不是从源代码静态跟踪依赖关系。 
仅当在求值期间实际读取变量时，变量才成为依赖项，而不仅仅是当它出现在保护表达式中时：

1. *运行时跟踪：*依赖关系由每次评估期间实际访问的变量决定
2. *传递跟踪：* 依赖项包括在被调用函数中读取的变量
3. *动态变化：* 依赖集可以从一个评估更改为下一个评估

考虑这个例子：

<!--NoCompile-->
<!-- 08-->
```verse
var X:int = 1
var Y:int = 2
var Z:int = 3

SomeFun(Value:int):int =
   if(Value > 0) then X else Y

var live W:int = SomeFun(Z)   # W 为 1，依赖关系：{Z, X}
set Z = 0                     # W 为 2，依赖性：{Z, Y}
```
最初，`SomeFun(Z)` 读取 `Z`（即 3）并评估 `then` 分支，读取 `X`，生成具有依赖项 `{Z, X}` 的 `W=1`。

在 `set Z=0` 之后，对 `Z` 的更改会触发重新评估。现在
`SomeFun(Z)` 读取 `Z`（为 0）并评估 `else` 分支，
正在读取 `Y`。这会导致 `W=2` 具有新的依赖项 `{Z, Y}`。

请注意，仅当执行路径为 `Y` 时，`Y` 才成为依赖项
改变了。如果 `X` 随后被修改，`W` 将“不”更新
因为 `X` 不再位于依赖项集中。这种动态跟踪
确保实时变量仅对实际影响的变化做出反应
他们的当前价值。

### 关闭实时性

通过其保护（而不是其类型）建立的实时变量可以是
被随后的常规任务关闭。

<!--versetest-->
<!-- 09-->
```verse
var X:int = 0
var Y:int = 5
set live X = Y  # X 现已上线，正在追踪 Y

set Y = 10      # X 变为 10
set X = 20      # X 现在再次成为常规变量
set Y = 15      # X 保持 20（不再跟踪 Y）
```
<!--
X=20
-->

这允许临时反应行为，当没有时可以禁用该反应行为
更需要。然而，通过其类型生存的变量
表达永远保持活力——他们的反应行为是
他们的类型固有的。

## 反应式构造

实时变量构成了三个反应式结构的基础，
处理异步事件而无需显式回调：`await`，
`upon` 和 `when`。

<a id="the-await-expression"></a>
### `await` 表达式

`await` 表达式暂停执行，直到目标表达式
成功，为异步提供同步原语
编程。

<!--versetest
-->
<!-- 10-->
```verse
F()<suspends>:void =
    var X:int = 0

    OldX := X # 复制旧值

    # 挂起直到 X 从 OldX 更改为 (0)
    await{X <> OldX}
    Print("X changed to: {X}")
```
立即计算目标表达式。如果失败，则
任务暂停。 Verse 跟踪期间读取了哪些变量
评价。每当这些变量发生变化时，防护就会重新评估。
如果成功，则立即恢复执行。

实际意义是您可以自然地编写代码
表示“等待此条件”，无需手动管理事件
处理程序或回调注册。代码在等待时暂停
点并在条件变为真时恢复。

<!--versetest
int_ref := class:
    var Contents:int = 0

TestAwait()<transacts><suspends>:void =
    X:int_ref=int_ref{}
    Y:int_ref=int_ref{}
    # Wait for a specific condition
    await{X.Contents > 10}
    set Y.Contents = X.Contents * 2
<#
-->
<!-- 11 -->
```verse
# 等待特定条件
await{X.Contents > 10}
set Y.Contents = X.Contents * 2
```
<!-- #>-->

保护表达式必须具有效果 `<reads><computes><decides>`
（参见[效果](13_effects.md)）——它可以读取和计算，但不能
写。这确保了重新评估不会产生副作用。
`await` 的主体也不能包含 `branch` 表达式，因为
`branch` 需要 `<suspends>` 上下文，并且防护必须保留
无副作用。

<a id="the-upon-expression"></a>
### `upon` 表达式

`upon` 表达式提供一次性反应行为：当
条件成立，执行一些代码一次。与 `await` 不同，
恢复当前任务，`upon` 创建一个新的并发任务
触发时运行。

<!--versetest-->
<!-- 12-->
```verse
var Health:int = 100
var IsDead:logic = false

upon(Health <= 0):
    set IsDead = true
    Print("Player died!")

set Health = 50  # 什么也没发生
set Health = 0   # 触发器：打印“玩家死了！”
set Health = -10 # 什么也没发生（已经触发过一次）
```
`upon` 表达式立即评估其防护并记录读取的变量。然后它生成一个 `task(t)`，其中 `t` 是主体的结果类型，表示待处理的反应行为。当依赖关系发生变化时，守卫会被重新评估。如果成功，主体会在新的并发任务中执行一次，然后完成。

这种一次性行为使 `upon` 非常适合状态转换和事件通知。当超过阈值时、当资源可用时、当计时器到期时，这些场景自然映射到 `upon` 的“条件变为真时触发一次”语义。

主体必须具有 `<transacts>` 效果（请参阅[效果](13_effects.md)），允许其读取和写入变量（包括其他实时变量），并保证执行相对于通知而言是原子的。

<a id="the-when-expression"></a>
### `when` 表达式

`when` 表达式提供连续的反应行为：每次条件为真时，执行一些代码。这将创建一个持久观察者，只要其守卫成功，该观察者就会运行。

<!--verstest-->
<!-- 13 FAILURE
  Line 6: Verse compiler error V3560: Expected definition but found macro invocation.
  Line 10: Verse compiler error V3560: Expected definition but found assignment.
  Line 11: Verse compiler error V3560: Expected definition but found assignment.
  Line 12: Verse compiler error V3560: Expected definition but found assignment.
  Line 3: Verse compiler error V3502: Module-scoped `var` must have `weak_map` type.
  Line 4: Verse compiler error V3502: Module-scoped `var` must have `weak_map` type.
-->
```verse
var Score:int = 0
var DisplayedScore:int = 0

when(Score):
    set DisplayedScore = Score
    Print("Score updated to: {Score}")

set Score = 100  # 触发器：打印“分数更新为：100”
set Score = 100  # 无触发（值不变）
set Score = 200  # 触发器：打印“分数更新为：200”
```
`when` 表达式立即评估其保护。如果守卫成功，身体就会执行。然后它记录警卫读取的变量并生成 `task(void)`。每当依赖关系发生变化并且防护成功时，主体就会再次执行，从而创建一个连续的观察循环。

这使得 `when` 成为维护派生状态和响应持续变化的理想选择。将 UI 与游戏状态同步、根据玩家操作更新 AI 行为或保持相关变量之间的一致性都受益于 `when` 的持久反应性。

<!--versetest-->
<!-- 14-->
```verse
var X:int = 2
var Y:int = 2

when(Y):
    Z := if (Y < 0) then 0 else Y - 1
    if (Z <> X):
        set X = Z

when(X):
    Z := if (X < 0) then 0 else X - 1
    if (Z <> Y):
        set Y = Z

# 这些表达式将稳定在 X = -1, Y = 0 时
```
主体以 `<transacts>` 效果执行，每次执行后立即重新注册，创建连续观察模式。

### 取消

所有三个反应式构造（`await`、`upon` 和 `when`）均返回可取消的 `task`，从而允许对反应行为进行动态控制。

<!--versetest-->
<!-- 15 FAILURE
  Line 10: Script Error 3512: This invocation calls a function that has the 'suspends' effect, which is not allowed by its context.
-->
```verse
var X:int = 0
var Y:int = 0

Task := upon(X > 5):
    set Y = X

Task.Cancel()  # 取消反应行为
set X = 10     # Y 保持为 0
```
取消任务会立即删除所有依赖项跟踪并阻止关联代码运行。这提供了对反应行为生命周期的细粒度控制，允许您根据游戏状态或用户操作启用和禁用观察。

<a id="the-batch-expression"></a>
## `batch` 表达式

`batch` 表达式将多个变量更新分组在一起，延迟通知，直到整个组完成。这可以防止中间状态触发反应行为，并确保观察者看到相关更改的一致快照。

<!--versetest-->
<!-- 16-->
```verse
var X:int = 0
var Y:int = 0

when(X > 1 and Y < 10):
    Print("Fired!") # 从不打印

when(X):
    Print("X Changed to {X}!") # 打印一次

batch:
    set X = 2   
    set Y = 10
    set X += 5
    Print("Inside batch")

Print("After batch")

# 输出顺序：
# -“内部批次”
# -“X改为7！”
# -“批次后”
```
在 `batch` 块内，变量更新会立即发生，但等待任务和反应式构造的通知会延迟。当批处理完成时，所有待处理的通知按照触发器发生的顺序触发，但观察者看到的是最终的一致状态而不是中间值。

如果同一通知出现两次，则仅发送第一个通知。

批处理表达式嵌套：通知会延迟，直到所有封闭的批处理完成为止。这种可组合性确保无论您的代码嵌套有多深，都可以保证相关变量的原子更新。

批处理的主体不得具有 `<suspends>` 效果 - 所有操作必须立即完成。这确保了批处理块具有明确定义的边界，并且不会因暂停更新而使系统处于不一致的状态。

## 问题和模式

### API 设计

出现在类或模块的公共接口中的任何变量
可以通过外部代码激活，可能违反类
不变量。为了避免这种情况，可以限制可变的暴露
变量或至少使用访问说明符来控制它：

<!--versetest-->
<!-- 17 FAILURE
  Line 4: Script Error 3509: This variable expects to be initialized with a value of type int, but this initializer is an incompatible value of type type{_(:float)<reads>:float}.
  Line 4: Script Error 3509: `live` requires a `comparable` right-hand side.  This right-hand side is of type type{_(:float)<reads>:float}.
  Line 4: Script Error 3641: Attributes on var only allowed inside a module or a class
  Line 4: Script Error 3594: Access level private is only allowed inside classes and interfaces.
-->
```verse
var<private> live X<public>:int = Exp
```
这里 `X` 是公开可见的，可供阅读，但只能通过以下方式更新
班级本身。这可以防止外部代码附加可能破坏类的任意防护
不变量。

### 失败与实时性

集成了实时变量更新和反应式构造触发器
在 Verse 的失败语义中。  当失败时，活着
变量更新被回滚并且它们的通知被
压制。

<!--versetest-->
<!-- 18-->
```verse
var X:int = 0
var Y:int = 0

if:
    set live X = Y + 5  # 建立实时关系
    false?          # 交易失败

upon(X):
    Print("{X}") # Y 更改时不打印

# 未建立实时关系
set Y = 10  # X 保持为 0
```
这确保了反应行为仅观察已提交的更改，
即使存在推测执行也保持一致性
和失败。

### 派生同步

一个常见的模式是多个 UI 元素反映相同的内容 
游戏状态下，`when`提供自动同步：

<!--versetest-->
<!-- 19-->
```verse
var PlayerScore:int = 0
var DisplayedScore:int = 0
var ScoreText:string = ""

when(PlayerScore):
    set DisplayedScore = PlayerScore
    set ScoreText = "Score: {PlayerScore}"
```
对 `PlayerScore` 的每次更改都会自动更新数字
显示值和格式化文本，保持 UI 一致
无需人工协调。

### 条件反应

实时变量可以根据条件跟踪不同的来源：

<!--versetest-->
<!-- 20 FAILURE
  Line 10: Script Error 3513: Expected an expression that can fail in the 'if' condition clause
-->
```verse
var UseAlternate:logic = false
var PrimaryValue:int = 10
var AlternateValue:int = 20
var CurrentValue:int = 0

set live CurrentValue =
    if (UseAlternate?) then AlternateValue else PrimaryValue

# 当前值 = 10
set UseAlternate = true
# 当前值 = 20
set AlternateValue = 30
# 当前值 = 30
set PrimaryValue = 15
# CurrentValue = 30（目前跟踪AlternateValue）
```
依赖性跟踪是动态的：当条件发生变化时，
跟踪变量集相应变化，允许灵活
反应式路由。

### 资源加载

当资源可用时，使用 `upon` 进行一次性初始化：

<!--versetest-->
<!-- 21 FAILURE
resource_manager := class:
    var TextureLoaded:logic = false
    var ModelLoaded:logic = false

    Initialize()<suspends>:void = {}
-->
<!-- 21 FAILURE
  Line 8: Verse compiler error V3502: Type definitions are not yet implemented outside of a module scope.
-->
```verse
resource_manager := class:
    var TextureLoaded:logic = false
    var ModelLoaded:logic = false

    Initialize()<suspends>:void =
        upon(TextureLoaded? and ModelLoaded?):
            Print("All resources loaded, starting game")
            StartGame()
```
这种模式消除了对加载状态的手动跟踪。当两者
资源加载完毕，游戏自动开始。

### 修改器堆栈（正在考虑中）

**modifier_stack的设计尚未最终确定；此处提供的材料可能会发生变化。**

游戏开发通常需要对单个值应用多个修饰符。例如，玩家的健康状况可能需要
限制在有效范围内，通过生命药水暂时提升，并在依赖关系发生变化时自动重新计算。

`modifier_stack` 模式提供了一个使用实时变量和函数类型的可组合解决方案，允许有序转换在任何修饰符的依赖项发生变化时自动更新。

修改器堆栈由三个组件组成：

1. **`modifier_iterface(t)`** - 用于转换 `t` 类型值的修饰符的接口
2. **`modifier_stack(t)`** - 排序和组合修饰符的容器
3. **实时变量** - 使用 `modifier_stack.Evaluate` 作为自动反应的类型

当您分配给具有修饰符堆栈类型的实时变量时，该值按位置顺序流经每个修饰符，并存储最终结果。由于 `modifier_stack.Evaluate` 具有 `<reads>` 效果，因此对任何修改器依赖项的更改（或添加/删除修改器）都会触发自动重新计算。

公共API如下：

<!--NoCompile-->
<!-- 22-->
```verse
modifier_iterface(t : type) := interface:
   Evaluate(Value:t)<reads> : t

modifier_stack(t:type) := class:
   # 在位置插入修饰符；返回一个用于删除修饰符的可取消项。
   AddModifier<final>(Modifier:modifier_iterface(t), Position:rational)<transacts>: cancelable

   # 返回根据堆栈中的每个修饰符按位置顺序计算的输入值。
   Evaluate<final>(Value:t)<reads> : t
```
`AddModifier` 方法返回 `cancelable`，可用于删除插入的修饰符。
删除修饰符会触发与此堆栈关联的任何实时变量的重新计算。

例如，考虑以下内容，它创建了一个通过过滤的实时变量 `Health`
修改器堆栈包含使输入值加倍的魔法药水修改器：

<!--NoCompile-->
<!-- 23-->
```verse
HealthStack := modifier_stack(float){}
HealthStack.AddModifier(magic_potion{Value:=2.0})
var RawHealth -> Health : HealthStack.Evaluate = 10.0
# 原始健康 = 10.0，健康 = 20.0
```
当乘数更改或将修饰符添加到堆栈时，该变量会自动重新计算。

更详细地说，此示例演示了两个协同工作的修改器：使生命值倍增的 `magic_potion` 和将值限制在一定范围内的 `clamp`。

<!--NoCompile-->
<!-- 24-->
```verse
# 定义修饰符实现
magic_potion := class(modifier_iterface(float)):
   var Value:float
   Evaluate<override>(Arg:float)<reads>:float = Arg * Value

clamp := class(modifier_iterface(float)):
   var Low:float
   var High:float
   Evaluate<override>(Arg:float)<reads>:float =
       if (Arg<Low) then Low else { if (Arg>High) then High else Arg }

# 创建实例
Potion := magic_potion{ Value:= 2.0 }
Clamp := clamp{Low:=1.0, High:= 12.0 }

# 构建修改器堆栈
HealthStack := modifier_stack(float){}
RevokePotion := HealthStack.AddModifier(Potion, 0.0)  # 先申请（位置0.0）
HealthStack.AddModifier(Clamp, 1.0)                   # 应用第二个（位置 1.0）

# 使用修改器堆栈创建实时变量
var Health : HealthStack.Evaluate = 5.0  # 5.0 * 2.0 = 10.0（然后钳位到 [1.0, 12.0]）
set Potion.Value = 3.0                   # 5.0 * 3.0 = 15.0（钳位至12.0）
RevokePotion.Cancel()                    # 5.0（没有药水，只需夹到[1.0, 12.0]）
```
值按位置顺序流经修饰符：

1. **初始：** 5.0 → 药水(×2.0) → 10.0 → 钳子 → 10.0
2. **更换`Potion.Value`后：** 5.0 → 药水(×3.0) → 15.0 → 夹子 → 12.0
3. **去除药水后：** 5.0 → 夹子 → 5.0

有计划通过编译器强制执行：每个修饰符实例只能添加到一个堆栈中，并且 
每个堆栈实例可以与一个变量相关联。  这将启用未来的功能
其中修改器堆栈维护特定于其关联的实时变量的状态。

### 常见错误

**不必要的实时声明**

定义没有可更改依赖项的实时变量是不必要的且具有误导性：

<!--NoCompile-->
<!-- 25-->
```verse
var live X:int = 10    # X是10并且永远不会改变
set live X = 20        # X是20并且永远不会改变
```
在这两种情况下，`X` 都不会自动更新，因此程序
没有 `live` 关键字时，其行为相同。 `live` 注释
错误地暗示不存在的反应行为。

**缺少可变依赖项**

同样，仅依赖于不可变值的实时变量永远不会更新：

<!--NoCompile-->
<!-- 26-->
```verse
X:int = 10
var live Y = X+1    # Y 是 11 并且永远不会改变
```
由于 `X` 是不可变的，因此 `Y` 没有可变的依赖关系，并且将
永远保持在11。 `live` 声明毫无意义。

**函数作为类型的混乱**

当尝试使变量通过
函数类型：

<!--NoCompile-->
<!-- 27-->
```verse
var Mult:int = 10

Multiply(Value:int):type{_(:int):int} =
    Fun(Arg:int):int = Value * Arg
    Fun

var X:Multiply(Mult) = 10    # X = 100

set Mult = 20                 # X 仍然是 100（未上线！）
```
这段代码是错误的。程序员可能认为
`Multiply(Mult)` 将使 `X` 生效，因为该表达式有一个
`<reads>` 效果（读取 `Mult`）并返回函数类型
`int->int`。

**错误：** 对于通过其类型生存的变量，
*返回函数本身*必须具有 `<reads>` 效果，而不是
产生该函数的表达式。

要了解原因，请考虑以下等效转换：

<!--NoCompile-->
<!-- 28-->
```verse
MFun = Multiply(Mult)
var X:MFun = 10
```
现在很明显，`X` 还没有生效——`MFun` 只是一个函数值
类型为 `int->int`，并且该函数没有 `<reads>`
效果。

**正确的方法：** 使用函数用作的模式
类型直接有`<reads>`效果：

<!--NoCompile-->
<!-- 29-->
```verse
var Mult:int = 10

Multiply(Arg:int)<reads>:int = Arg * Mult

var X:Multiply = 10    # X = 100
set Mult = 20          # X = 200（现已上线！）
```
这里`Multiply`本身有`<reads>`，所以用它作为类型使`X`活起来。

如果同一个函数必须与不同的变量重用
依赖，可以将其封装在一个对象中，如前所示。

## 演进

发布新版本系统时，允许删除
来自变量定义的 `live`。这种向前兼容性
保证意味着反应行为是一个实现细节
可以在不破坏客户端代码的情况下进行优化。

在新版本中将常规变量转换为实时变量是
如果计算值与先前版本匹配，通常是安全的
手动维护。但是，如果外部代码依赖于能够
设置任意值，这可能会超出预期。

取消反应性结构的能力提供了重要的
升级路径：创建 `when` 或 `upon` 观察者的代码稍后可以
修改为在不同条件下取消它们而不破坏
现有的行为。
