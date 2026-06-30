# 控制流

每个程序都有其自然的执行节奏，即指令被处理和决策做出的顺序。在 Verse 中，这种流不仅仅是代码行的机械推进——它是一种精心编排的、不同类型表达式之间的协作，每种表达式都为程序的整体行为做出贡献。

## 代码块

代码块是基本组织单元，它将相关表达式组合在一起，并为变量和常量创建新的作用域。与许多语言中代码块仅仅是语法便利不同，在 Verse 中，代码块本身就是表达式，这意味着它们像其他任何表达式一样产生值。

作用域的概念对于理解代码块至关重要。当你在代码块中创建变量或常量时，它仅存在于该代码块的上下文内。这种封闭性确保你的代码保持有序，并且名称不会在程序的不同部分意外冲突。考虑以下函数，其主体是一个包含单个 if-then-else 表达式的代码块，而该表达式本身又由三个不同的代码块组成：

<!--versetest-->
<!-- 01 -->
```verse
CalculateReward(PlayerLevel:int)<reads>:int =
    if:
        PlayerLevel > 10
        Multiplier := 2.0  # Only exists within this if block
        Base := 100
        Result := Floor[(Base+PlayerLevel) * Multiplier] # Fails on infinity
    then:
        Result  # This block extends the scope of the if
    else:
        50      # Different branch, different scope
                # Multiplier and Result don't exist here
```
<!-- CalculateReward(11) = 222 -->

Verse 具有灵活的语法，提供了三种等效的代码块书写格式。空格格式最为常见，使用冒号引入代码块并通过缩进展示结构：

<!--versetest
IsPlayerReady()<decides><transacts>:void = {}
StartMatch()<transacts>:void = {}
BeginCountdown()<transacts>:void = {}
-->
<!-- 02 -->
```verse
if (IsPlayerReady[]):
    StartMatch()
    BeginCountdown()
```

多行大括号格式为来自 C 风格语言的程序员提供了熟悉的体验：

<!--versetest
IsPlayerReady()<decides><transacts>:void = {}
StartMatch()<transacts>:void = {}
BeginCountdown()<transacts>:void = {}
-->
<!-- 03 -->
```verse
if (IsPlayerReady[]) {
    StartMatch()
    BeginCountdown()
}
```

对于简单操作，单行点号格式使代码保持简洁：

<!--versetest-->
<!-- 04 -->
```verse
HasPowerup()<computes><decides>:void={}
ApplyBoost():void={}
F():void=
    if (HasPowerup[]). ApplyBoost()
```

由于一切都是表达式，代码块本身也具有值。代码块的值由其中执行的最后一个表达式给出。这实现了优雅的模式，复杂计算可以封装在代码块中，并与周围代码无缝集成：

<!--versetest
CalculateScore()<computes>:int = 100
CalculateBonus(Time:float)<computes>:int = 50
CompletionTime:float = 10.0
AccuracyValue:float = 0.95
-->
<!-- 05 -->
```verse
FinalScore := block:              # The variable has the block's value
    Base := CalculateScore()
    Bonus := CalculateBonus(CompletionTime)
    Accuracy := Floor[AccuracyValue * 100.0]
    Base + Bonus + Accuracy       # This becomes the block's value
```


## If 表达式

`if` 表达式利用成功和失败来驱动决策（详见[失败](08_failure.md)）。当条件中的表达式成功时，相应的分支执行：

<!--versetest
player := class:
   CanJump()<computes><decides>:void={}
   Jump()<computes>:void={}
   GetEquippedWeapon()<computes><decides>:weapon=weapon{}
   Idle()<computes>:void={}

weapon:=class<computes>{
   Fire():void={}
}
ConsumeAmmo():void={}
PlayJumpSound():void={}
-->
<!-- 07 -->
```verse
HandlePlayerAction(Player:player, Action:string):void =
    if (Action = "jump", Player.CanJump[]):
        Player.Jump()
        PlayJumpSound()
    else if (Action = "attack", Weapon := Player.GetEquippedWeapon[]):
        Weapon.Fire()
        ConsumeAmmo()
    else:
        # Default action
        Player.Idle()
```

这种方法允许你链接可能失败的条件，而无需在每一步进行显式错误处理。

另一种语法使用 `then:` 和 `else:` 关键字来显式标记分支：

<!--versetest-->
<!-- 08 -->
```verse
ProcessValue(Value:int):string =
    if:
        Value > 0
        Value < 100
    then:
        "Valid"
    else:
        "Out of range"

ProcessValue(50) = "Valid"
```

当你有多重条件或希望强调条件与动作的分离时，这种语法可以提高可读性。

`if` 中的条件必须至少包含一个可以失败的表达式。这一要求确保 `if` 被用于其预期目的——处理不确定的结果：

<!--NoCompile-->
<!-- 10 -->
```verse
# Error: condition cannot fail
if (1 + 1):  # Compile error - no fallible expression
    DoSomething()

# Valid: array access can fail
if (FirstItem := Items[0]):
    Process(FirstItem)
```

空条件也是不允许的——每个 `if` 都必须测试某些内容。

如果条件中的任何表达式失败，控制流将进入 `else` 分支（如果存在）。评估条件时产生的任何效果都会自动回滚（详见[失败](08_failure.md#speculative-execution)）：

<!--versetest
GetPlayerScore()<decides><computes>:int=1
-->
<!-- 11 -->
```verse
var Counter:int = 0

if:
    set Counter = Counter + 1  # Provisional change
    Score := GetPlayerScore[]  # Might fail
    Score > 100
then:
    # Counter was incremented
else:
    # Counter rolled back to original value - increment undone!
```

这种推测执行使条件逻辑更安全——你可以乐观地执行操作，知道如果后续条件失败，这些操作将被撤销。

在条件中定义的变量在 `then` 分支中可用，但在 `else` 分支中不可用：

<!--NoCompile-->
<!-- 12 -->
```verse
if:
    Player := FindPlayer[Name]  # Define Player
then:
    AwardBonus(Player)  # OK - Player available
else:
    Penalize(Player)  # Compile error
```

这种作用域规则反映了逻辑流程：在 `else` 分支中，条件失败了，因此在条件期间绑定的任何变量可能不具有有意义的值。

由于 `if` 是表达式，它会产生一个值。当所有分支返回兼容的类型时，`if` 可以在任何需要值的地方使用：

<!--versetest
IsCritical:logic= false
BaseDamage:int=0
Health:int=0
-->
<!-- 13 -->
```verse
Damage := if (IsCritical?):
    BaseDamage * 2
else:
    BaseDamage

# Ternary-style
Status := if (Health > 50). "Healthy" else. "Wounded"
```

当分支具有不兼容的类型时，结果会被拓宽为 `any`：

<!--versetest
UseNumber:logic=false
-->
<!-- 14 -->
```verse
# Different types in branches yields any
Result:any = if (UseNumber?) then 42 else "text"
```

所有分支都必须产生一个值，`if` 才能作为表达式使用。

## Case 表达式

当你需要基于多个可能的值做决策时，`case` 表达式提供了清晰、可读的分支：

<!--versetest-->
<!-- 15 -->
```verse
GetWeaponDamage(WeaponType:string):float =
    case(WeaponType):
        "sword"  => 50.0
        "bow"    => 35.0
        "staff"  => 40.0
        "dagger" => 25.0
        _        => 10.0  # Default damage for unknown weapons

GetWeaponDamage("sword") = 50.0
```

当你需要匹配离散值时使用 `case` 表达式，它比一系列 `if-else` 条件更能清晰地表达意图。

Case 表达式适用于支持直接值比较的特定类型：

- **基本类型**：`int`、`logic`、`char`
- **字符串**：`string`
- **枚举**：开放枚举和封闭枚举
- **精化类型**：具有约束的自定义类型

由于实现限制，它们不适用于 `float`、对象和元组。

**枚举的穷尽性检查。** 对 `enum` 的 `case` 会进行穷尽性检查。对于所有值都已知的封闭枚举，编译器会验证你是否已处理所有情况：

<!--versetest
direction := enum:
    North
    South
    East
    West
-->
<!-- 17 -->
```verse
# Exhaustive - no wildcard needed
GetVector(Dir:direction):tuple(int, int) =
    case (Dir):
        direction.North => (0, 1)
        direction.South => (0, -1)
        direction.East => (1, 0)
        direction.West => (-1, 0)

GetVector(direction.North) = (0, 1)
```

如果你在所有情况都已覆盖时添加通配符，你会收到通配符不可达的警告：

<!--versetest
direction := enum:
    North
    South
    East
    West

GetVectorWithUnreachable(Dir:direction):tuple(int, int) =
    case (Dir):
        direction.North => (0, 1)
        direction.South => (0, -1)
        direction.East => (1, 0)
        direction.West => (-1, 0)
        _ => (0, 0)

assert:
    # Test that the function works despite unreachable wildcard
    GetVectorWithUnreachable(direction.North) = (0, 1)
<#
-->
<!-- 18 -->
```verse
    case (Dir):
        direction.North => (0, 1)
        direction.South => (0, -1)
        direction.East => (1, 0)
        direction.West => (-1, 0)
        _ => (0, 0)  # Warning: all cases already covered
```
<!-- #> -->

不完整的 case 覆盖在 `<decides>` 上下文中是允许的：

<!--versetest
direction := enum{  North, South, East, West}
-->
<!-- 19 -->
```verse
# Without wildcard in <decides> context - OK
GetPrimaryDirection2(Dir:direction)<decides>:string =
    case (Dir):
        direction.North => "Primary"
        # Other directions cause function to fail
```

开放枚举在发布后可以添加新值，因此它们永远无法被穷尽。它们总是需要通配符或 `<decides>` 上下文。

## Loop 表达式

`loop` 表达式创建一个无限循环，持续执行直到显式中断：

<!--versetest
UpdatePlayerPositions()<transacts>:void={}
CheckCollisions()<transacts>:void={}
RenderFrame()<transacts>:void={}
GameOver()<decides><transacts>:void={}
-->
<!-- 22 -->
```verse
GameLoop():void =
    loop:
        UpdatePlayerPositions()
        CheckCollisions()
        RenderFrame()
        if (GameOver[]). break
```

`break` 表达式完全退出循环，终止迭代。`break` 具有"底"类型——一种表示从不正常返回的计算的类型。由于底类型是所有其他类型的子类型，`break` 可以在任何类型上下文中使用：

<!--versetest-->
<!-- 55 -->
```verse
NumberOfBits(X:int):int =
    var B:int = 1
    var C:int = 0
    loop:
        set B = if (B > X) { break } else { 2*B }
        set C = C+1
    C
```

这展示了底类型：`break` 在 if 表达式中与 `int`（来自 `2*B`）统一。赋值 `set B = ...` 使用了 if 表达式的值，表明 `break` 在任何类型上下文中都是兼容的。

**循环返回值：** loop 表达式本身产生类型为 `true`（顶类型）的值，无论其主体中出现什么表达式。这个返回值在实践中很少有用——循环通常用于其副作用。

当 `break` 出现在嵌套循环中时，它只退出最内层的循环：

<!--versetest-->
<!-- 57 -->
```verse
var Outer:int = 0
loop:
    set Outer += 1
    var Inner:int = 0
    loop:
        set Inner += 1
        if (Inner = 5):
            break        # Exits inner loop
    if (Outer = 10):
        break            # Exits outer loop
```

以下限制适用。`break` 语句必须出现在代码块中，而不能作为复杂表达式的一部分。循环必须包含至少一个非 break 的语句。最后，在 `loop` 外部使用 `break` 会产生错误：

<!--versetest
ShouldStop()<decides>:void={}

assert_semantic_error(3506, 3581):
    ProcessData():void =
       if (ShouldStop[]):
               break      # Error
<#
-->
<!-- 58 -->
```verse
ProcessData():void =
   if (ShouldStop[]):
           break      # Error
```
<!-- #> -->
## For 表达式

`for` 表达式遍历集合、范围和其他可迭代类型，提供一种更结构化的重复方式：

<!--versetest
player:=class{}
GetScore(P:player):int=100
<#
-->
<!-- 23 -->
```verse
CalculateTotalScore(Players:[]player)<transacts>:int =
    var Total:int = 0
    for (Player : Players):
        PlayerScore := GetScore(Player)
        set Total += PlayerScore
    Total
```
<!-- #> -->

虽然它可能看起来与较早的命令式语言中的形式相似，但最好将 `for` 视为一种函数式构造，它结合了迭代、使用推测执行的过滤，以及结果集合的构建。

<!--versetest-->
<!-- 223 -->
```verse
Values:[]float= array{1.0, 10.1, 100.2}
Result := 
   for:
      V : Values
      V >= 10.0
      R := Floor[V]
   do:
      R*2.0

Result = array{20.0, 200.0}
```

上面的代码使用了替代的多子句语法，使用 `do:` 关键字将迭代规范与主体分离。`for` 遍历 `Values` 数组，丢弃小于 10 的值并对数字向下取整。它返回一个浮点数数组。`Floor` 函数被定义为 `decides`——如果它失败，该次迭代将被丢弃。

还有另一种替代语法：用于简单操作的单行点号语法：

<!--versetest
Values:[]int = array{1, 2, 3}
DoSomething(V:int):void = {}
-->
<!-- 26 -->
```verse
# Single-line dot style
for (V : Values). DoSomething(V)
```

**索引和值对：**

在遍历数组或映射时，你可以使用 `Index -> Value` 或 `Key -> Value` 的对语法同时访问索引/键和值：

<!--versetest
player:=struct{ Name:string }
-->
<!-- 28 -->
```verse
PrintRoster(Players:[]player):void =
    for (Index -> Player : Players):
        Print("Player {Index}: {Player.Name}")
```

索引从零开始，符合 Verse 的数组索引约定。

**在 For 子句中定义变量：**

for 循环允许你定义中间变量，这些变量可以在后续的过滤器或循环主体中使用：

<!--versetest-->
<!-- 29 -->
```verse
# Define Y based on X
Doubled := for (X := 1..5, Y := X * 2):
    Y  # Returns array{2, 4, 6, 8, 10}

# Combine with filtering
SafeDivision := for (X := -3..3, X <> 0, Y := Floor[10.0 / (X*1.0)]):
    Y  # Skips X=0, returns array{-3, -5, -10, 10, 5, 3}
```

这些中间变量的作用域限于该次迭代，并且可以引用同一子句中较早声明的变量。

**多重过滤器：**

你可以使用逗号或分号分隔的表达式链式组合多个过滤条件。每个过滤条件必须是可失败的，若任何一个失败，该次迭代将被跳过：

<!--versetest-->
<!-- 30 -->
```verse
# Multiple independent filters
Filtered := for (X := 1..10, X <> 3, X <> 7):
    X  # Returns array{1, 2, 4, 5, 6, 8, 9, 10}

# Filters with intermediate variables
Complex := for (X := 1..5, X <> 2, Y := X * 2, Y < 10):
    Y  # Only includes values where X≠2 and Y<10
```

每个过滤条件按顺序评估，只有当所有条件都成功时，迭代才会继续。

**遍历映射：**

映射可以通过两种方式遍历：仅遍历值，或使用对语法遍历键值对：

<!--versetest-->
<!-- 31 -->
```verse
# Iterate over values only
Scores:[int]int = map{1 => 100, 2 => 200, 3 => 150}
TopScores := for (Score : Scores):
    Score  # Returns array{100, 200, 150}

# Iterate over key-value pairs
PlayerScores:[string]int = map{"Alice" => 100, "Bob" => 200}
for (PlayerName -> Score : PlayerScores):
    Print("{PlayerName} scored {Score}")
```

映射保持插入顺序，因此迭代顺序与键被添加到映射的顺序一致。

**字符串迭代：**

字符串可以逐字符迭代：

<!--versetest-->
<!-- 32 -->
```verse
CountVowels(Text:string):int =
    var Count:int = 0
    for (Char : Text, Char = 'a' or Char = 'e' or Char = 'i' or Char = 'o' or Char = 'u'):
        set Count += 1
    Count
```

**嵌套迭代（笛卡尔积）：**

多个迭代源会创建嵌套循环，产生笛卡尔积：

<!--NoCompile-->
<!-- 33 -->
```verse
PrintGrid():void =
    for (X := 1..3, Y := 1..3):
        Print("({X}, {Y})")
    # Produces: (1,1), (1,2), (1,3), (2,1), (2,2), (2,3), (3,1), (3,2), (3,3)
```

**使用失败进行过滤：**

Verse 的 `for` 表达式在利用失败上下文时尤为强大，因为它们可以自然地过滤：

<!--versetest
player:=struct{ Name:string }
GetScore(P:player)<computes>:int=0
-->
<!-- 34 -->
```verse
GetHighScorers(Players:[]player):[]player =
    for (Player : Players, Score := GetScore(Player), Score > 1000):
        Player  # Only players with score > 1000 are included
```

当迭代头中的任何表达式失败时，该次迭代被跳过。这允许优雅地过滤，而无需显式的 `if` 语句：

<!--versetest
item:=struct{Price:float}
-->
<!-- 35 -->
```verse
# Filter items under budget and apply transformation
AffordableItems(Items:[]item, Budget:float):[]float =
    for (Item : Items, Item.Price <= Budget):
        Item.Price * 1.1  # Apply 10% markup
```

**For 作为表达式：**

与其他控制流构造一样，`for` 是表达式。当主体产生值时，`for` 将它们收集到数组中：

<!--versetest
player:=struct{Name:string}
-->
<!-- 36 -->
```verse
# Collect player names
GetNames(Players:[]player):[]string =
    for (Player : Players):
        Player.Name  # Each iteration produces a string
```

这使得 `for` 成为转换集合的强大工具，无需显式的累加变量。

**从 For 循环中中断：**

`break` 语句不能提前退出 `for` 循环。如果你只需要从迭代中获取第一个匹配的结果，请使用 `first` 而不是 `for`（见下面的[First 表达式](#first-expressions)）。

**关于 Continue 的说明：**

与许多语言不同，Verse 目前不支持跳过到下一次迭代的 `continue` 语句。相反，使用条件逻辑或基于失败的过滤来实现类似的结果：

<!--versetest
item:=struct{IsValid:logic}
ProcessItem(I:item):void={}
-->
<!-- 38 -->
```verse
# Instead of continue, use conditional blocks
ProcessItems(Items:[]item):void =
    for (Item : Items):
        if (Item.IsValid?):
            ProcessItem(Item)
        # No continue needed - just structure with conditions

# Or use failure-based filtering in the header
ProcessValidItems(Items:[]item):void =
    for (Item : Items, Item.IsValid?):
        ProcessItem(Item)  # Only valid items reach here
```


**范围迭代。** 范围运算符 `..` 提供了在整数序列上的数值迭代。范围两端都是包含的：

<!--versetest-->
<!-- 27 -->
```verse
# Iterates: 1, 2, 3, 4, 5 (both bounds included)
for (I := 1..5):
    Print("Count: {I}")

# Single element range
for (I := 42..42):
    Print("Answer: {I}")  # Prints once: "Answer: 42"

# Empty range (start > end produces no iterations)
for (I := 5..1):
    Print("Never executes")  # Loop body never runs
```

`..` 运算符始终是包含的。没有排他性范围的语法。

范围边界按特定顺序评估，副作用可预测地发生：

1. **先评估左边界**，然后是右边界
2. **两个边界始终被评估**，即使范围是空的
3. **副作用按顺序发生**，无论是否产生迭代

虽然你不能将范围存储为值，但你可以使用 for 表达式创建数组：

<!--versetest-->
<!-- 47 -->
```verse
# This works because for produces an array, not because ranges are storable
DoubledNumbers:[]int = for (I := 1..5){ I * 2 }

# Can then iterate over the array normally
for (N : DoubledNumbers):
    Print("{N}")
```

范围仅在 for 表达式求值期间存在；生成的数组才是被存储的内容。

**限制。** for 循环有几个重要的限制：

1. **迭代源必须是可迭代的：** 只有范围（`1..10`）、数组、映射和字符串可以被迭代。

2. **过滤器必须是可失败的：** 过滤条件必须包含至少一个可以失败的表达式。

3. **不能重新定义迭代变量：** 你不能在同一个子句中重新定义迭代变量。

4. **不能定义可变变量：** 不允许在 for 子句中使用 `var` 声明变量。

范围运算符 `..` 有严格的限制，使其区别于其他可迭代类型。范围**不是一等值**——它们是表达式，依次产生范围内的每个整数作为单独的值。范围不能在你可能期望它们工作的某些上下文中使用：

<!--NoCompile-->
<!-- 40 -->
```verse
# ERROR: Cannot store range in variable
MyRange := 1..10
for (I := MyRange):

# ERROR: Cannot pass range to function
ProcessRange(1..10)

# ERROR: Cannot use range as standalone expression
Result := 1..10

# ERROR: Cannot put range in array
Ranges := array{1..10}

# ERROR: Cannot index range
Value := (1..10)(5)

# ERROR: Cannot access members on range
Length := (1..10).Length
```

范围仅适用于 `int` 类型。其他数值类型、布尔值、类型或对象不受支持。

## First 表达式

!!! note "未发布的功能"
    `first` 表达式尚未发布。本节记录了当前不可用的计划中功能。

`first` 表达式与 `for` 类似，但它不是为域子句的每次迭代都评估主体，而是只评估域子句中**第一次**成功的迭代。它不像 `for` 那样产生数组，而是为该单一迭代产生主体的值。如果没有迭代到达主体，`first` 失败——因此它需要 `<decides>` 上下文。

<!--versetest
player:=struct{ Name:string }
GetScore(P:player)<computes><decides>:int=0
-->
<!-- 80 -->
```verse
# Find the first player with a score above the threshold
FindTopScorer(Players:[]player, Threshold:int)<decides>:player =
    first (Player : Players; GetScore[Player] > Threshold):
        Player
```

与 `for` 一样，`first` 表达式支持三种语法形式。块形式使用 `do:` 将迭代子句与主体分离：

<!--NoCompile-->
<!-- 81 -->
```verse
# Block form with do:
first:
    X : Collection
    Predicate[X]
do:
    Process(X)

# Braces form
first(X : Collection; Predicate[X]){ Process(X) }

# Dot form for single expressions
first(X : Collection; Predicate[X]). Process(X)
```

`first` 表达式使用与 `for` 相同的绑定语法。你可以迭代数组、映射、字符串和范围。你可以使用 `->` 语法使用索引-值对，链式组合多个过滤器，以及嵌套多个迭代源：

<!--versetest-->
<!-- 82 -->
```verse
# Find the index of an element using index -> value binding
IndexOf(Arr:[]int, Target:int)<decides>:int =
    first(I -> V : Arr, V = Target). I
```

注意 `first` 产生的是**主体**表达式的值，而不是迭代变量的值。这使得可以搜索一个东西而产生另一个东西——例如，通过匹配值来查找索引。

**First 与 For 的对比：**

| | `for` | `first` |
|-|-------|---------|
| 产生结果 | 所有结果的数组 | 仅第一个结果 |
| 无匹配时 | 空数组 | **失败**（需要 `<decides>`） |
| 停止时机 | 所有迭代完成后 | 第一次迭代后 |

**常见模式：**

由于 `first` 需要 `<decides>`，一种常见用法是将其包装在 `if` 或 `option` 中，以处理未找到匹配的情况：

<!--versetest-->
<!-- 83 -->
```verse
# Find with fallback using if
FindOrDefault(Arr:[]int, Target:int):int =
    if (Index := first(I -> V : Arr, V = Target). I):
        Index
    else:
        -1
```

或者：

<!--versetest-->
<!-- 84 -->
```verse
# Find with fallback using if
FindOptional(Arr:[]int, Target:int):?int =
    option:
        Index := first(I -> V : Arr, V = Target). I
            Index
```

## Return 语句

`return` 语句提供了从函数显式提前退出的方式，允许你在到达函数主体末尾之前终止执行并返回值：

<!--versetest-->
<!-- 48 -->
```verse
ValidateInput(Value:int):string =
    if (Value < 0):
        return "Error: Negative value"

    if (Value > 1000):
        return "Error: Value too large"

    "Valid"     # Implicit return
```

Return 语句只能出现在代码中的特定位置——它们必须处于"尾部位置"，这意味着它们必须是在控制退出作用域之前执行的最后一个操作。此限制确保了可预测的控制流：

<!--versetest
GetOrder(:int)<transacts><decides>:order=order{}
order := class<allocates>{ IsValid()<decides><transacts>:logic=false }
-->
<!-- 49 -->
```verse
# Valid: return is last operation
ProcessOrder(OrderId:int)<transacts>:string =
    if (Order := GetOrder[OrderId]):
        if (Order.IsValid[]):
            return "Processed"
    "Invalid order"

# Valid: return in both branches
GetStatus(Value:int):string =
    if (Value > 0):
        return "Positive"
    else:
        return "Non-positive"
```

Verse 函数隐式返回其最后一个表达式的值，因此 `return` 仅用于提前退出：

<!--versetest
CalculateBonus(Score:int):int={
    if(Score<100)then{return 0}
    Score*10
}
-->
<!-- 51 -->
```verse
# Implicit return
GetValue():int = 42  # Returns 42

# Explicit early return
GetDiscount(Price:float):float =
    if (Price < 10.0):
        return 0.0  # Early exit with no discount

    Price * 0.1  # Implicit return with 10% discount
```

在具有 `<decides>` 效果的函数中，`return` 允许你从提前退出时提供成功值，同时仍然允许其他路径失败：

<!--versetest
config:=struct{MaxRetries:int}
GetConfig()<transacts><decides>:config=config{MaxRetries:=3}
AttemptOperation(Retry:int)<computes><decides>:string="success"
-->
<!-- 52 -->
```verse
RetryableOperation()<transacts>:string =
    if (Config := GetConfig[]):
        for (Retry := 1..Config.MaxRetries):
            if (Result := AttemptOperation[Retry]):
                return Result  # Success - exit immediately
    "Failed" # All retries exhausted
```

这种模式在搜索操作中很常见，你希望在找到匹配时立即返回，但如果未找到匹配则失败。

## Defer 语句

`defer` 语句安排代码在其所在作用域退出时执行。这使得它对于清理操作（如关闭文件、释放资源或记录日志）非常宝贵。

Defer 是**基于作用域**的，而非基于函数。`defer` 块在离开直接包含它的作用域时执行，包括：

- **函数主体**——在函数返回时执行
- **`for` 循环**——`for` 主体每次迭代在其自己的作用域中运行；`for` 域也引入了一个词法作用域
- **`loop` 块的每次迭代**——在每次迭代结束时执行（包括在 `break` 时）
- **`if`/`then`/`else` 子句**——在离开所选分支时执行
- **`block` 作用域**——在离开代码块时执行
- **`not` 表达式**——`not e` 在新的词法作用域中评估 `e`
- **`or` 表达式**——`e0 or e1` 在新的词法作用域中评估 `e0`
- **`and` 表达式**——`e0 and e1` 在整个表达式的新词法作用域中评估
- **`option` 和 `logic` 表达式**——`option{e}` 和 `logic{e}` 在新的词法作用域中评估 `e`
- **`case` 表达式**——`case(e0){e1=>e2, e3=>e4}` 为整个 `case` 创建一个词法作用域，然后为每个结果表达式（`e2`、`e4`）创建作用域
- **原型实例化**——`my_class{...}` 为其主体引入词法作用域
- **`defer` 块本身**——嵌套的 defer 在外层 defer 完成时执行
- **结构化并发宏**（`race`、`rush`、`branch`）——每个分支在其自己的词法作用域中运行
- **`spawn`、`await` 和 `batch` 表达式**——`spawn{e}`、`await{e}` 和 `batch{e}` 在新的词法作用域中评估 `e`
- **`live` 绑定**——`live Name : e0 = e1` 为 `e1` 创建新的词法作用域
- **已取消的并发作用域**——在取消展开期间执行（详见[并发](14_concurrency.md#cleanup-and-resource-management)）

以下是一个基本示例：

<!--versetest
OpenFile(P:string)<computes>:?int=false
CloseFile(P:int)<computes>:void={}
ReadFile(P:int)<computes>:?string=false
ProcessContents(P:string)<computes><decides>:void={}
SaveResults()<computes><decides>:void={}
-->
<!-- 61 -->
```verse
ProcessFile(FileName:string)<transacts><decides>:void =
    File := OpenFile(FileName)?
    defer:
        CloseFile(File)  # Runs on success or early exit

    Contents := ReadFile(File)?
    ProcessContents[Contents]
    SaveResults[]
```

Deferred 代码在作用域成功退出或通过诸如 `return` 之类的显式控制流退出时执行：

<!--versetest
OpenConnection()<transacts>:int=0
CloseConnection(Id:int)<transacts>:void={}
Query(Id:int)<decides><transacts>:string="result"
ProcessResult(R:string)<transacts>:void={}

ProcessQuery()<transacts>:void =
    ConnId := OpenConnection()
    defer:
        CloseConnection(ConnId)  # Cleanup always needed

    for (Attempt := 1..5):
        if (Result := Query[ConnId]):
            ProcessResult(Result)
            return  # defer executes after return being called

    # defer executes before leaving the function scope on success

assert:
    # ProcessQuery is defined and demonstrates defer with return
<#
-->
<!-- 62 -->
```verse
ProcessQuery()<transacts>:void =
    ConnId := OpenConnection()
    defer:
        CloseConnection(ConnId)  # Cleanup always needed

    for (Attempt := 1..5):
        if (Result := Query[ConnId]):
            ProcessResult(Result)
            return  # defer executes after return being called

    # defer executes before leaving the function scope on success
```
<!-- #> -->

这是一个微妙但关键的点：如果函数由于推测执行而失败，deferred 代码**不会**执行。这是因为失败会触发回滚，撤销所有效果，包括 defer 块的调度：

<!--versetest
AcquireResource()<transacts><decides>:int=0
ReleaseResource(Id:int)<transacts>:void={}
RiskyOperation(Id:int)<transacts><decides>:void={}
-->
<!-- 63 -->
```verse
ExampleWithFailure()<transacts><decides>:void =
    ResourceId := AcquireResource[]
    defer:
        ReleaseResource(ResourceId) # Scheduled...

    RiskyOperation[ResourceId] # This fails!
    # defer does NOT run - entire scope was speculative and rolled back
```

当 `RiskyOperation` 失败时，整个函数也失败，推测执行撤销了一切——包括 defer 的注册。资源清理不会发生，因为资源获取本身也被回滚了。

这种行为确保了一致性：如果函数失败，就好像它从未执行过一样，包括任何已安排的清理代码。

**执行顺序：**

当同一作用域中存在多个 `defer` 时，它们按定义的逆序执行（后进先出），模仿嵌套资源的栈式清理：

<!--versetest
OpenDatabase()<transacts>:int=0
CloseDatabase(Id:int)<transacts>:void={}
BeginTransaction(Id:int)<decides><transacts>:int=0
CommitTransaction(Id:int)<transacts>:void={}
DoWork()<transacts><decides>:void={}
-->
<!-- 64 -->
```verse
DatabaseTransaction()<transacts><decides>:void =
    DbId := OpenDatabase()
    defer:
        CloseDatabase(DbId)  # Executes second (outer resource)

    TxnId := BeginTransaction[DbId]
    defer:
        CommitTransaction(TxnId)  # Executes first (inner resource)

    DoWork[]  # Work happens with both resources active
    # Defers execute: CommitTransaction, then CloseDatabase
```

**Defer 与异步取消：**

Deferred 代码也会在异步操作被取消时执行，例如当 `race` 完成或 `spawn` 被中断时：

<!--versetest
AcquireResource()<transacts>:int=0
ReleaseResource(Resource:int)<transacts>:void={}
LongRunningTask(Resource:int)<suspends><transacts>:void={}

ProcessWithTimeout()<suspends><transacts>:void =
    race:
        block:
            Resource := AcquireResource()
            defer:
                ReleaseResource(Resource)  # Runs if cancelled

            LongRunningTask(Resource)

        block:
            Sleep(10.0)  # Timeout
    # If timeout wins, first block is cancelled and defer runs

assert:
    # ProcessWithTimeout demonstrates defer with async cancellation
<#
-->
<!-- 65 -->
```verse
ProcessWithTimeout()<suspends><transacts>:void =
    race:
        block:
            Resource := AcquireResource()
            defer:
                ReleaseResource(Resource)  # Runs if cancelled

            LongRunningTask(Resource)

        block:
            Sleep(10.0)  # Timeout
    # If timeout wins, first block is cancelled and defer runs
```
<!-- #> -->

这确保了即使并发控制中断了你的代码，清理工作仍然会执行。

**嵌套 Defer：**

Defer 语句可以嵌套在其他 defer 块中，形成级联的清理操作：

<!--versetest
Log(S:string)<transacts>:void={}
-->
<!-- 66 -->
```verse
ProcessWithCleanup():void =
    Log("A")
    defer:
        Log("B")
        defer:
            Log("inner")  # Runs after B
        Log("C")
    Log("D")
    # Output: A D B C inner
```

执行顺序在每个嵌套层级遵循 LIFO 原则——内层 defer 在外层 defer 的代码之后执行，保持栈式清理顺序。

**控制流中的 Defer：**

Defer 在所有控制流构造中都能正确工作：

<!--versetest
Log(S:string)<transacts>:void={}
-->
<!-- 67 -->
```verse
ProcessLoop():void =
    for (I := 0..2):
        Log("Start")
        defer:
            Log("Cleanup")  # Runs after each iteration
        Log("End")
    # Output: Start End Cleanup Start End Cleanup Start End Cleanup

ProcessWithIf(Condition:logic):void =
    if (Condition?):
        defer:
            Log("Then cleanup")
        Log("Then body")
    else:
        defer:
            Log("Else cleanup")
        Log("Else body")
```

每个控制流路径独立执行其自己的 defer。

**Defer 限制。** defer 语句有重要的限制以确保可预测的行为：

1. **不能为空：** Defer 块必须包含至少一个表达式：

2. **不能用作表达式：** Defer 不能出现在期望值的位置。

3. **不能跨越边界：** Defer 块不能包含 `return`、`break` 或其他会退出 defer 作用域的控制流。

4. **不能失败：** Defer 块中的表达式不能失败。

5. **不能直接挂起：** Defer 块不能包含挂起表达式，但它们可以使用 `spawn` 进行即发即弃的异步操作。

关于 `defer` 如何与异步取消及并发构造（如 `race` 和 `spawn`）交互，请参阅[清理与资源管理](14_concurrency.md#cleanup-and-resource-management)。

## 性能分析

了解代码的性能对优化至关重要，`profile` 表达式用于测量执行时间：

<!--versetest-->
<!-- 73 -->
```verse
OptimizedCalculation():float =
    profile("Complex Math"):
        var Result:float = 0.0
        for (I := 1..1000000):
            set Result += Sin(I*1.0) * Cos(I*1.0)
        Result
```

profile 表达式包裹你想要测量的代码，将执行时间记录到输出中。你可以添加描述性标签来组织性能分析输出，从而更容易识别复杂系统中的瓶颈。

Profile 表达式透明地传递其结果，这意味着你可以将其包裹在任何表达式周围，而不会改变程序的行为：

<!--versetest
BaseDamage:float = 50.0
GetMultiplier()<computes>:float = 1.5
GetCriticalBonus()<computes>:float = 2.0
-->
<!-- 74 -->
```verse
PlayerDamage := profile("Damage Calculation"):
    BaseDamage * GetMultiplier() * GetCriticalBonus()
```
