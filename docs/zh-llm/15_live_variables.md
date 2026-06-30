# 实时变量

!!! note "未发布的功能"
     实时变量尚未发布。本章记录的是计划中的功能，目前尚不可用。

实时变量代表了 Verse 中的响应式编程范式，使得变量能够在依赖项发生变化时自动重新计算其值。实时变量不需要显式的回调或事件处理函数，而是在数据之间建立动态关系，创建了一个声明式系统，让变化自然地通过代码传播。

传统编程需要手动跟踪依赖关系，并在值发生变化时显式更新。如果变量 `A` 依赖于变量 `B`，你必须在 `B` 变化时记得更新 `A`，通常通过回调函数或观察者模式来实现。实时变量通过自动跟踪求值过程中读取了哪些变量、并在这些依赖项变化时重新求值，消除了这种簿记工作。这使得代码更易维护——意图（即 `A` 应始终反映 `B` 的某个函数）直接表达在代码中。

实时变量为响应式编程结构（包括 `await`、`upon` 和 `when`）奠定了基础。理解实时变量对于使用 Verse 的事件驱动编程模型至关重要，尤其是在游戏开发场景中，许多值需要保持同步。

## 实时表达式

*实时表达式*在一个变量与一个守卫之间建立动态关系。一旦建立，只要守卫的任何依赖项发生变化，目标变量就会自动重新求值，从而保持变量同步。

<!--versetest-->
<!-- 01-->
```verse
var X:int = 0
var Y:int = 0
set live X = Y+1  # X now tracks Y
set Y = 5         # X automatically becomes 6
```
<!--
X = 6
-->

在上例中，`set live X = Y+1` 是一个实时表达式，目标变量是之前声明的变量 `X`，守卫是表达式 `Y+1`，它依赖于变量 `Y`。

实时变量拓展了可变变量（参见[可变性](05_mutability.md)），增加了自动依赖跟踪功能：守卫表达式求值过程中读取的任何变量都会被跟踪。当这些变量中的任何一个发生变化时，守卫会被重新求值，目标变量自动更新。

### 声明形式

实时变量可以通过多种方式声明，每种方式适用于不同的使用场景：

<!--NoCompile-->
<!-- 02-->
```verse
# Live variable declaration
var live X:int = Exp

# Live assignment to existing variable
var X:int = 0
# ... later ...
set live X = Exp

# Immutable live variable
live Y:int = Exp

# Variable with a function type (with <reads> effect)
var X: F = Exp            # Initial value computed normally
var live X: F = Exp       # Initial value tracked for dependencies

# Immutable variable with a function type (with <reads> effect)
X: F = Exp                # Initial value computed normally
live X: F = Exp           # Initial value tracked for dependencies

# Input-output variable pairs
var In->Out: F = Exp      # Initial value computed normally
var live In->Out: F = Exp # Initial value tracked for dependencies

In->Out: F = Exp          # Initial value computed normally
live In->Out: F = Exp     # Initial value tracked for dependencies
```

最常见的形式 `var live X = Exp` 创建了一个可变变量，其初始值来自守卫的求值，随后在依赖项发生变化时更新。守卫表达式可以读取其他变量，这些读取操作会被跟踪，从而建立依赖关系。

赋值形式 `set live X = Exp` 通过附加一个守卫，将已有变量转换为实时变量。这在需要在初始化之后、或根据程序状态有条件地使变量变为响应式时非常有用。

不可变实时变量通过 `live Y = Exp` 声明，不能直接写入，但仍会在其守卫的依赖项变化时自动更新。这提供了一个只读的响应式值，适用于那些绝不应手动覆盖的派生计算。

当变量的类型是带有 `<reads>` 效果的函数时，该变量通过其类型变为实时的（赋值会通过该函数进行过滤，对函数依赖项的更改会触发重新计算）。声明中的 `live` 关键字决定初始表达式 `Exp` 是否也被跟踪依赖项。如果没有 `live`，`Exp` 只求值一次；有 `live` 时，`Exp` 中的依赖项会被跟踪，并可能在第一次赋值之前触发更新。

输入-输出对会创建两个变量，一个捕获原始值，另一个保存转换后的值。同样，`live` 关键字控制初始表达式 `Exp` 的依赖项是否被跟踪。

以下各节将详细说明这些更复杂的形式。

### 函数作为类型

Verse 允许将函数用作变量的类型。当带有 `<reads>` 效果的函数用作类型时，变量会自动变为实时，在该函数的依赖项发生变化时更新。

<!--versetest-->
<!-- 03 FAILURE
  Line 8: Script Error 3547: Expected a type, got function identifier instead.
  Line 8: Script Error 3601: Data definitions at this scope must be initialized with a value.
-->
```verse
var Mult:int = 2

Multiply(Arg: int)<reads>:int = Arg * Mult

var X : Multiply

set X = 10        # X gets 20
set Mult = 1      # X gets 10
```
<!--
X = 10
-->

在这个示例中，`Multiply` 扮演了双重角色：它既是一个函数，也是变量 `X` 的一个类型。

**作为类型：** 当你声明 `var X : Multiply` 时，会发生以下几件事：

- `X` 的存储类型变为 `int`（函数的返回类型）
- 赋给 `X` 的值必须是 `int`（函数的参数类型）
- 每次赋值都通过该函数：`set X = 10` 调用 `Multiply(10)` 并存储结果

**作为实时表达式：** 由于 `Multiply` 具有 `<reads>` 效果（它读取了可变变量 `Mult`），该变量声明成为一个实时表达式，以 `Multiply` 作为其守卫。这产生了两种值变化的方式：

1. **直接赋值：** `set X = 10` 将值通过 `Multiply` 过滤，存储 20
2. **依赖项更新：** `set Mult = 1` 触发重新计算，将 `X` 更新为 10

这种模式优雅地结合了转换（每次写入都被过滤）和响应式（对依赖项的更改会触发更新）。

### 输入-输出变量

输入-输出变量对同时捕获原始输入值和转换后的输出值。语法 `var In->Out:F=Exp` 创建了两个相关的变量，其中 `Out` 是可写变量，`In` 自动存储未经过函数 `F` 转换的原始值。

这种模式优雅地处理了常见的游戏场景，即值必须保持在动态约束范围内。考虑必须保持在边界内的生命值：

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

# Health = 50 (clamped to [0, 100])
set Health = 75      # BaseHealth = 75, Health = 75
set Health = 120     # BaseHealth = 120, Health = 100 (clamped)
set Clamp.Upper = 60 # BaseHealth = 120, Health = 60 (reclamped)
```

当你写入 `Health` 时，会发生两件事：

 1. 原始值存储在 `BaseHealth` 中
 2. 该值通过 `Clamp.Evaluate` 传递，结果存储在 `Health` 中

由于 `Clamp.Evaluate` 具有 `<reads>` 效果（它读取了可变变量 `Lower` 和 `Upper`），这成为一个实时表达式。当约束发生变化时，`Health` 会根据 `BaseHealth` 自动重新计算。

**工作原理**

声明 `var BaseHealth->Health: Clamp.Evaluate = 50` 创建了一个实时表达式，其中：

- `BaseHealth` 存储原始输入值（从外部视角看是只读的）
- `Health` 存储限制后的值（可读写）
- `Clamp.Evaluate` 是带有 `<reads>` 效果的转换函数

对象 `Clamp` 是类 `clamp` 的一个实例，具有可变的边界 `Lower` 和 `Upper`。由于 `Evaluate` 读取了这些可变变量，对它们的更改会触发重新计算：

- `set Health=75` — 值未经过改变直接通过，因此 `BaseHealth` 和 `Health` 都变为 75
- `set Health=120` — 超过 `Upper`，因此 `BaseHealth` 变为 120，但 `Health` 变为 100
- `set Clamp.Upper=60` — 约束发生变化，触发重新计算：`Health` 更新为 60，而 `BaseHealth` 保持为 120

使用实例方法（如 `Clamp.Evaluate`）允许在同一上下文中存在多个独立的限制器，每个都有自己动态的边界。

**访问控制**

输入和输出变量的作用域可以通过添加访问说明符来独立控制：例如 `var In<private>->Out<public>:t` 使基值私有，同时公开暴露受约束的值。

### 限制效果与稳定性

实时变量的守卫不能具有 `<writes>` 效果。这一基本限制防止了守卫求值过程中的副作用——Verse 需要能够在依赖项变化时自由地进行守卫求值。

<!--NoCompile-->
<!-- 05-->
```verse
# ERROR: guard cannot write
var X:int = 0
var GlobalCounter:int = 0
set live X = block:
    set GlobalCounter += 1  # Not allowed!
    GlobalCounter
```

相互依赖的实时变量可能形成循环。当目标表达式使用幂等操作且值是可比较的时，这些循环可以自然地收敛到不动点。

<!--versetest-->
<!-- 06-->
```verse
var X:int = 2
var Y:int = 2

set live X = if (Y < 0) then 0 else Y - 1
set live Y = if (X < 0) then 0 else X - 1

# Evaluates as: X=1, Y=0, X=-1, Y=0 (stable)
```
<!--
X=-1
Y=0
-->

如果变量的类型是可比较的，守卫会被重新求值，直到值稳定下来。在这个示例中，`X` 递减到 -1，`Y` 限制到 0，然后 `X` 会重新计算但结果仍然是 -1，因此系统稳定下来。

然而，没有适当终止条件的循环可能会发散。Verse 无法阻止所有发散——在设计相互依赖的实时变量时必须小心。

这有一个微妙的含义：由于任何变量在创建后都可能变为实时，读取任何变量都必须假定可能触发守卫求值，在最坏情况下可能触发循环。效果系统考虑到了这一点：`<writes>` 效果隐含了 `<diverges>`，因为任何写入都可能触发循环的实时变量求值。以下示例说明了当 `X` 大于 0 时的循环定义：

<!--NoCompile-->
<!-- 07-->
```verse
var X:int = 0
var live Y:int = if (X>0) then X+1 else 0

set live X = Y
set X = 1  # Error! Cyclic evaluation
```

### 跟踪依赖项

实时变量在运行时动态跟踪依赖项，而不是从源代码静态推断。一个变量只有当它在求值过程中实际被读取时，才成为依赖项，而不仅仅是因为它出现在守卫表达式中：

1. *运行时跟踪：* 依赖项由每次求值过程中实际访问的变量决定
2. *传递跟踪：* 依赖项包括在被调用函数中读取的变量
3. *动态变化：* 依赖项集合可以在不同次求值之间发生改变

考虑以下示例：

<!--NoCompile-->
<!-- 08-->
```verse
var X:int = 1
var Y:int = 2
var Z:int = 3

SomeFun(Value:int):int =
   if(Value > 0) then X else Y

var live W:int = SomeFun(Z)   # W is 1, Dependencies: {Z, X}
set Z = 0                     # W is 2, Dependencies: {Z, Y}
```

最初，`SomeFun(Z)` 读取了 `Z`（值为 3）并求值 `then` 分支，读取了 `X`，得到 `W=1`，依赖项为 `{Z, X}`。

在 `set Z=0` 之后，`Z` 的变化触发了重新求值。现在 `SomeFun(Z)` 读取了 `Z`（值为 0）并求值 `else` 分支，读取了 `Y`。结果是 `W=2`，新的依赖项为 `{Z, Y}`。

注意 `Y` 只有在执行路径改变时才成为依赖项。如果之后修改了 `X`，`W` 将*不会*更新，因为 `X` 已不在依赖项集合中。这种动态跟踪确保实时变量只对实际影响其当前值的变化作出反应。

### 关闭实时性

通过守卫（而非通过其类型）建立的实时变量，可以通过后续的普通赋值来关闭实时性。

<!--versetest-->
<!-- 09-->
```verse
var X:int = 0
var Y:int = 5
set live X = Y  # X is now live, tracking Y

set Y = 10      # X becomes 10
set X = 20      # X is now a regular variable again
set Y = 15      # X remains 20 (no longer tracking Y)
```
<!--
X=20
-->

这允许临时的响应式行为，在不再需要时可以禁用它。然而，通过其类型表达式变为实时的变量将永久保持实时——它们的响应式行为是其类型固有的。

## 响应式构造

实时变量构成了三种响应式构造的基础，它们无需显式回调即可处理异步事件：`await`、`upon` 和 `when`。

### await 表达式

`await` 表达式会挂起执行，直到目标表达式成功，为异步编程提供了同步原语。

<!--versetest
-->
<!-- 10-->
```verse
F()<suspends>:void =
    var X:int = 0

    OldX := X # copy the old value

    # Suspend until X changes from OldX (0)
    await{X <> OldX}
    Print("X changed to: {X}")
```

目标表达式会立即求值。如果失败，任务挂起。Verse 会跟踪求值过程中读取了哪些变量。每当这些变量发生变化时，守卫会被重新求值。如果成功，执行立即恢复。

实际意义在于，你可以编写自然地表达"等待此条件"的代码，而无需手动管理事件处理函数或回调注册。代码在 await 处挂起，并在条件变为真时精确地恢复执行。

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
# Wait for a specific condition
await{X.Contents > 10}
set Y.Contents = X.Contents * 2
```
<!-- #>-->

守卫表达式必须具有效果 `<reads><computes><decides>`（参见[效果](13_effects.md)）——它可以读取和计算，但不能写入。这确保重新求值是无副作用的。
`await` 的主体也不能包含 `branch` 表达式，因为 `branch` 需要 `<suspends>` 上下文，而守卫必须保持无副作用。

### upon 表达式

`upon` 表达式提供了一次性的响应式行为：当一个条件变为真时，执行一次某些代码。与 `await` 不同（它恢复当前任务），`upon` 创建一个新的并发任务，在触发时运行。

<!--versetest-->
<!-- 12-->
```verse
var Health:int = 100
var IsDead:logic = false

upon(Health <= 0):
    set IsDead = true
    Print("Player died!")

set Health = 50  # Nothing happens
set Health = 0   # Triggers: prints "Player died!"
set Health = -10 # Nothing happens (already triggered once)
```

`upon` 表达式会立即求值其守卫并记录读取的变量。然后它产生一个 `task(t)`，其中 `t` 是主体的结果类型，表示待处理的响应式行为。当依赖项发生变化时，守卫被重新求值。如果成功，主体在一个新的并发任务中执行一次，并且 upon 完成。

这种一次性行为使得 `upon` 非常适合状态转换和事件通知。当超过阈值时，当资源变得可用时，当定时器到期时——这些场景自然地映射到 `upon` 的"条件变为真时触发一次"的语义。

主体必须具有 `<transacts>` 效果（参见[效果](13_effects.md)），允许它读取和写入变量（包括其他实时变量），并且执行保证相对于通知是原子的。

### when 表达式

`when` 表达式提供了持续的响应式行为：每次条件为真时，执行某些代码。这创建了一个持久的观察者，每当其守卫成功时运行。

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

set Score = 100  # Triggers: prints "Score updated to: 100"
set Score = 100  # No trigger (value unchanged)
set Score = 200  # Triggers: prints "Score updated to: 200"
```

`when` 表达式会立即求值其守卫。如果守卫成功，主体执行。然后它记录守卫读取的变量并产生一个 `task(void)`。每当依赖项发生变化且守卫成功时，主体再次执行，形成一个持续的观察循环。

这使得 `when` 成为维护派生状态和响应持续变化的理想选择。将 UI 与游戏状态同步、根据玩家行为更新 AI 行为、或维护相关变量之间的一致性，都受益于 `when` 的持久响应式特性。

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

# These when expressions will stabilize at X = -1, Y = 0
```

主体以 `<transacts>` 效果执行，并且 when 在每次执行后立即重新注册，形成持续的观察模式。

### 取消

所有三种响应式构造——`await`、`upon` 和 `when`——都返回一个可以取消的 `task`，从而允许对响应式行为进行动态控制。

<!--versetest-->
<!-- 15 FAILURE
  Line 10: Script Error 3512: This invocation calls a function that has the 'suspends' effect, which is not allowed by its context.
-->
```verse
var X:int = 0
var Y:int = 0

Task := upon(X > 5):
    set Y = X

Task.Cancel()  # Cancels the reactive behavior
set X = 10     # Y remains 0
```

取消一个任务会立即移除所有依赖跟踪，并阻止相关代码运行。这提供了对响应式行为生命周期的细粒度控制，允许你根据游戏状态或用户操作启用和禁用观察。

## batch 表达式

`batch` 表达式将多个变量更新分组在一起，延迟通知直到整个组完成。这防止了中间状态触发响应式行为，并确保观察者看到相关变更的一致快照。

<!--versetest-->
<!-- 16-->
```verse
var X:int = 0
var Y:int = 0

when(X > 1 and Y < 10):
    Print("Fired!") # Never prints

when(X):
    Print("X Changed to {X}!") # Prints once

batch:
    set X = 2   
    set Y = 10
    set X += 5
    Print("Inside batch")

Print("After batch")

# Output order:
# -"Inside batch"
# -"X Changed to 7!"
# -"After batch"
```

在 `batch` 块内部，变量更新会立即发生，但向等待的任务和响应式构造的通知会被推迟。当 batch 完成时，所有待处理的通知按照其触发顺序发出，但观察者看到的是最终一致的状态，而不是中间值。

如果同一个通知发生两次，只有第一个会被投递。

Batch 表达式可以嵌套：通知会被延迟，直到所有封闭的 batch 完成。这种可组合性确保无论代码嵌套得多深，你都可以保证相关变量的原子更新。

Batch 的主体不能具有 `<suspends>` 效果——所有操作必须立即完成。这确保了 batch 块具有明确定义的边界，并且不会因为在更新中途挂起而导致系统处于不一致状态。

## 问题与模式

### API 设计

任何出现在类或模块公共接口中的变量，都可能被外部代码设为实时，从而可能违反类的不变性。为了避免这种情况，可以限制可变变量的暴露范围，或至少使用访问修饰符来控制：

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

这里 `X` 对于读取是公开可见的，但只能由类本身更新。这防止了外部代码附加可能破坏类不变性的任意守卫。

### 失败与实时性

实时变量的更新和响应式构造的触发已集成到 Verse 的失败语义中。当发生失败时，实时变量的更新会被回滚，其通知也会被抑制。

<!--versetest-->
<!-- 18-->
```verse
var X:int = 0
var Y:int = 0

if:
    set live X = Y + 5  # Establishes live relationship
    false?          # Transaction fails

upon(X):
    Print("{X}") # Does not print when Y changes

# Live relationship was not established
set Y = 10  # X remains 0
```

这确保了响应式行为只观察到已提交的变更，即使在推测执行和失败的情况下也能保持一致性。

### 派生同步

一个常见的模式是多个 UI 元素反映相同的游戏状态，`when` 提供了自动同步：

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

每次 `PlayerScore` 变化都会自动更新数值显示值和格式化文本，使 UI 保持一致，无需手动协调。

### 条件响应式

实时变量可以根据条件跟踪不同的源：

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

# CurrentValue = 10
set UseAlternate = true
# CurrentValue = 20
set AlternateValue = 30
# CurrentValue = 30
set PrimaryValue = 15
# CurrentValue = 30 (still tracking AlternateValue)
```

依赖跟踪是动态的：当条件变化时，被跟踪的变量集合也随之变化，从而实现灵活的响应式路由。

### 资源加载

使用 `upon` 进行一次性初始化，当资源变为可用时：

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

这种模式消除了手动跟踪加载状态的需要。当两个资源都完成加载时，游戏自动启动。

### 修饰器栈（考虑中）

**修饰器栈的设计尚未最终确定；此处展示的内容很可能会发生变化。**

游戏开发通常需要对单个值应用多个修饰器。例如，玩家生命值可能需要被限制在有效范围内，被生命药水暂时提升，并在依赖项变化时自动重新计算。

`modifier_stack` 模式提供了一种使用实时变量和函数作为类型的可组合解决方案，允许有序的转换，在任何修饰器的依赖项变化时自动更新。

修饰器栈由三个组件组成：

1. **`modifier_iterface(t)`** — 一个接口，用于转换类型为 `t` 的值的修饰器
2. **`modifier_stack(t)`** — 一个容器，用于排序和组合修饰器
3. **实时变量** — 使用 `modifier_stack.Evaluate` 作为其类型以实现自动响应式

当你向具有修饰器栈类型的实时变量赋值时，该值按位置顺序流经每个修饰器，最终结果被存储。由于 `modifier_stack.Evaluate` 具有 `<reads>` 效果，任何修饰器依赖项的变化（或添加/移除修饰器）都会触发自动重新计算。

公开 API 如下：

<!--NoCompile-->
<!-- 22-->
```verse
modifier_iterface(t : type) := interface:
   Evaluate(Value:t)<reads> : t

modifier_stack(t:type) := class:
   # Insert a Modifier at Position; return a cancelable used to remove the Modifier.
   AddModifier<final>(Modifier:modifier_iterface(t), Position:rational)<transacts>: cancelable

   # Returns the input Value evaluated against each modifier in the stack in position order.
   Evaluate<final>(Value:t)<reads> : t
```

`AddModifier` 方法返回一个 `cancelable`，可用于移除已插入的修饰器。移除修饰器会触发与此栈关联的任何实时变量的重新计算。

例如，以下代码创建了一个通过修饰器栈过滤的实时变量 `Health`，该栈包含一个使输入值加倍的魔法药水修饰器：

<!--NoCompile-->
<!-- 23-->
```verse
HealthStack := modifier_stack(float){}
HealthStack.AddModifier(magic_potion{Value:=2.0})
var RawHealth -> Health : HealthStack.Evaluate = 10.0
# RawHealth = 10.0, Health = 20.0
```

当乘数改变或修饰器被添加到栈中时，变量会自动重新计算。

更详细地说，以下示例展示了两个修饰器协同工作：一个 `magic_potion`（魔法药水）倍增生命值，以及一个 `clamp`（限制器）将值限制在范围内。

<!--NoCompile-->
<!-- 24-->
```verse
# Define modifier implementations
magic_potion := class(modifier_iterface(float)):
   var Value:float
   Evaluate<override>(Arg:float)<reads>:float = Arg * Value

clamp := class(modifier_iterface(float)):
   var Low:float
   var High:float
   Evaluate<override>(Arg:float)<reads>:float =
       if (Arg<Low) then Low else { if (Arg>High) then High else Arg }

# Create instances
Potion := magic_potion{ Value:= 2.0 }
Clamp := clamp{Low:=1.0, High:= 12.0 }

# Build the modifier stack
HealthStack := modifier_stack(float){}
RevokePotion := HealthStack.AddModifier(Potion, 0.0)  # Apply first (position 0.0)
HealthStack.AddModifier(Clamp, 1.0)                   # Apply second (position 1.0)

# Create live variable with modifier stack
var Health : HealthStack.Evaluate = 5.0  # 5.0 * 2.0 = 10.0 (then clamped to [1.0, 12.0])
set Potion.Value = 3.0                   # 5.0 * 3.0 = 15.0 (clamped to 12.0)
RevokePotion.Cancel()                    # 5.0 (no potion, just clamp to [1.0, 12.0])
```

值按位置顺序流经修饰器：

1. **初始：** 5.0 → 药水（×2.0）→ 10.0 → 限制器 → 10.0
2. **更改 `Potion.Value` 后：** 5.0 → 药水（×3.0）→ 15.0 → 限制器 → 12.0
3. **移除药水后：** 5.0 → 限制器 → 5.0

计划通过编译器强制以下规则：每个修饰器实例只能添加到一个栈中，每个栈实例只能与一个变量关联。这将为未来修饰器栈维护与其关联实时变量相关的状态的功能提供支持。

### 常见错误

**不必要的实时声明**

定义一个没有可变依赖项的实时变量是不必要且具有误导性的：

<!--NoCompile-->
<!-- 25-->
```verse
var live X:int = 10    # X is 10 and will never change
set live X = 20        # X is 20 and will never change
```

在这两种情况下，`X` 都不会自动更新，因此程序行为与不使用 `live` 关键字时完全相同。`live` 注解错误地暗示了实际上不存在的响应式行为。

**缺少可变依赖项**

类似地，一个仅依赖于不可变值的实时变量永远不会更新：

<!--NoCompile-->
<!-- 26-->
```verse
X:int = 10
var live Y = X+1    # Y is 11 and will never change
```

由于 `X` 是不可变的，`Y` 没有可变依赖项，将永远保持为 11。`live` 声明毫无意义。

**函数作为类型的混淆**

一个微妙的错误发生在试图通过函数类型使变量变为实时时：

<!--NoCompile-->
<!-- 27-->
```verse
var Mult:int = 10

Multiply(Value:int):type{_(:int):int} =
    Fun(Arg:int):int = Value * Arg
    Fun

var X:Multiply(Mult) = 10    # X = 100

set Mult = 20                 # X is still 100 (not live!)
```

这段代码是错误的。程序员可能认为 `Multiply(Mult)` 会使 `X` 变为实时，因为该表达式具有 `<reads>` 效果（它读取了 `Mult`）并返回一个函数类型 `int->int`。

**错误：** 要使变量通过其类型变为实时，*返回的函数本身*必须具有 `<reads>` 效果，而不是产生该函数的表达式。

要理解原因，请考虑以下等价转换：

<!--NoCompile-->
<!-- 28-->
```verse
MFun = Multiply(Mult)
var X:MFun = 10
```

现在很明显 `X` 不是实时的——`MFun` 只是一个类型为 `int->int` 的函数值，且该函数没有 `<reads>` 效果。

**正确做法：** 使用函数直接具有 `<reads>` 效果的模式：

<!--NoCompile-->
<!-- 29-->
```verse
var Mult:int = 10

Multiply(Arg:int)<reads>:int = Arg * Mult

var X:Multiply = 10    # X = 100
set Mult = 20          # X = 200 (now live!)
```

这里 `Multiply` 本身具有 `<reads>` 效果，因此将其用作类型会使 `X` 变为实时。

如果同一个函数需要在不同的变量上重用作为依赖，可以像之前展示的那样将其封装在对象中。

## 演化

在发布系统的新版本时，允许从变量定义中移除 `live`。这一向前兼容性保证意味着响应式行为是一个实现细节，可以在不破坏客户端代码的情况下被优化掉。

在新版本中将普通变量转换为实时变量通常是安全的，前提是计算出的值与之前版本手动维护的值一致。然而，如果外部代码依赖于能够设置任意值，这可能会破坏预期。

取消响应式构造的能力提供了一条重要的升级路径：创建了 `when` 或 `upon` 观察者的代码，以后可以修改为在不同条件下取消它们，而不会破坏现有行为。