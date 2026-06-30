# 结构体和枚举

结构体（struct）和枚举（enum）代表了 Verse 面向值的类型系统，为简单的数据聚合和固定的具名值集合提供了比类更轻量的替代方案。与具有面向对象特性的类不同，结构体和枚举专注于简单性、不可变性和值语义。

结构体将相关数据捆绑在一起，没有方法和继承，非常适合数学类型、配置数据和简单记录。枚举定义了固定的具名常量集合，用有意义的名称取代魔法数字，并通过穷举模式匹配提供编译期安全性。

结构体和枚举共同通过提供更简单、更受约束的、针对特定用例优化的类型构造器，来补充类和接口。

## 结构体

结构体提供了轻量级的数据容器，没有类的面向对象特性。它们是针对简单数据聚合优化的值类型，非常适合数学类型、数据传输对象以及任何需要简单数据捆绑而无需行为的场景。

结构体以最小的开销将相关数据分组：

<!--NoCompile-->
<!-- 01 -->
```verse
damage_type:= enum:
    Physical
character := struct{}
vector2 := struct:
    X : float = 0.0
    Y : float = 0.0

color := struct:
    R : int = 0
    G : int = 0
    B : int = 0
    A : int = 255  # Alpha channel

damage_info := struct:
    Amount : int = 0
    Type : damage_type = damage_type.Physical
    Source : ?character = false
    IsCritical : logic = false
```

所有结构体字段默认都是公开且不可变的。结构体不能有方法、构造器，也不能参与继承层次。这种简单性使得它们高效且可预测。

### 构造

创建结构体实例使用与类相同的原型语法：

<!--versetest
vector2 := struct:
    X : float = 0.0
    Y : float = 0.0

color := struct:
    R : int = 0
    G : int = 0
    B : int = 0
    A : int = 255
-->
<!-- 02 -->
```verse
Origin := vector2{}  # Uses defaults: (0.0, 0.0)
PlayerPos := vector2{X := 100.0, Y := 250.0}
RedColor := color{R := 255}  # Other channels default to 0/255

# Structs are values - assignment creates a copy
NewPos := PlayerPos
# NewPos is a separate instance with the same values
```

由于结构体是值类型，将结构体赋值给变量会创建其所有数据的副本。这与使用引用语义的类不同。

### 比较

所有字段都可比较的结构体支持相等比较：

<!--versetest
vector3i := struct:
    X : int = 0
    Y : int = 0
    Z : int = 0

PrintMsg(S:string)<transacts>:void = {}

M()<transacts>:void =
    Origin := vector3i{}
    UnitX := vector3i{X := 1}

    if (Origin = vector3i{}):
        PrintMsg("At origin")

    if (Origin = UnitX):
        PrintMsg("Same position")
<#
-->
<!-- 03 -->
```verse
vector3i := struct:
    X : int = 0
    Y : int = 0
    Z : int = 0

Origin := vector3i{}
UnitX := vector3i{X := 1}

if (Origin = vector3i{}):  # Succeeds - all fields match
    Print("At origin")

if (Origin = UnitX):  # Fails - X fields differ
    Print("Same position")
```
<!-- #> -->

比较是按字段进行的，仅当所有对应字段都相等时比较才会成功。

### 可持久化结构体

结构体可以标记为可持久化，以便与 Verse 的持久化系统一起使用：

<!--versetest
player_stats := struct<persistable>:
    HighScore : int = 0
    GamesPlayed : int = 0
    WinRate : float = 0.0

player := class<concrete><unique>{}

PlayerData : weak_map(player, player_stats) = map{}
<#
-->
<!-- 04 -->
```verse
player_stats := struct<persistable>:
    HighScore : int = 0
    GamesPlayed : int = 0
    WinRate : float = 0.0

# Can be used in persistent storage
PlayerData : weak_map(player, player_stats) = map{}
```
<!-- #> -->

一旦发布，可持久化结构体就不能再被修改，从而确保跨游戏更新的数据兼容性。

## 枚举

枚举定义了一组固定具名值的类型，非常适合表示状态、类型或任何具有已知有限备选集合的概念。它们用有意义的名称取代魔法数字，使代码更易读，并通过将值限制在定义的集合内提供编译期安全性。

枚举列出了某个类型的所有可能取值：

<!--NoCompile-->
<!-- 05 -->
```verse
game_state := enum:
    MainMenu
    Playing
    Paused
    GameOver

damage_type := enum:
    Physical
    Fire
    Ice
    Lightning
    Poison

direction := enum:
    North
    East
    South
    West
```

枚举中的每个值都成为该枚举类型的一个具名常量。编译器确保枚举类型的变量只能持有这些已定义值之一。枚举甚至可以为空：

<!--versetest
placeholder := enum{}
<#
-->
<!-- 06 -->
```verse
placeholder := enum{}  # Valid but rarely useful
```
<!-- #> -->

枚举同时引入了一个类型和一组值，区分它们至关重要：

<!--versetest
status := enum:
    Active
    Inactive


CurrentStatus:status = status.Active
<#
-->
<!-- 07 -->
```verse
status := enum:
    Active
    Inactive

# status is the TYPE
# status.Active and status.Inactive are VALUES

CurrentStatus:status = status.Active  # OK - value of type status
```
<!-- #> -->

不能在需要值的地方使用枚举类型：

<!--versetest
status := enum:
    Active
    Inactive

M()<transacts>:void =
    GoodAssignment:status = status.Active
    var CurrentStatus:status = status.Active
    set CurrentStatus = status.Inactive
<#
-->
<!-- 08 -->
```verse
# ERROR: Cannot use type as value
BadAssignment:status = status  # Compile error
set CurrentStatus = status     # Compile error

# CORRECT: Use enum values
GoodAssignment:status = status.Active  # OK
set CurrentStatus = status.Inactive    # OK
```
<!-- #> -->

这种区分防止了混淆并确保了类型安全。枚举类型定义了哪些值是可能的，而枚举值则是你在代码中实际使用的常量。

### 限制

枚举有特定的语法要求，以保持其用法清晰明确：

**枚举必须是定义的直接右侧部分：**

<!--versetest
priority := enum:
    Low
    Medium
    High
<#
-->
<!-- 09 -->
```verse
# Valid
priority := enum:
    Low
    Medium
    High

# Invalid - cannot use enum in expressions
Result := -enum{A, B}      # Compile error
value := enum{X, Y} + 1    # Compile error
```
<!-- #> -->

**枚举必须是模块级或类级定义：**

<!--versetest
my_enum := enum:
    Value1
    Value2

ProcessData():void = {}
<#
-->
<!-- 10 -->
```verse
# Valid
my_enum := enum:
    Value1
    Value2

# Invalid - cannot define local enums
ProcessData():void =
    LocalEnum := enum{A, B}  # Compile error - no local enums
```
<!-- #> -->

这些限制确保枚举在整个代码库中保持稳定、可引用的定义，而不是临时的局部值。

### 使用枚举

枚举提供了类型安全的替代方案，取代容易出错的字符串或整数常量：

<!--versetest
game_state := enum:
    MainMenu
    Playing
    Paused
    GameOver
-->
<!-- 11 -->
```verse
var CurrentState:game_state = game_state.MainMenu

ProcessInput(Input:string):void =
    case (CurrentState):
        game_state.MainMenu =>
            if (Input = "Start"):
                set CurrentState = game_state.Playing
        game_state.Playing =>
            if (Input = "Pause"):
                set CurrentState = game_state.Paused
        game_state.Paused =>
            if (Input = "Resume"):
                set CurrentState = game_state.Playing
            else if (Input = "Quit"):
                set CurrentState = game_state.MainMenu
        game_state.GameOver =>
            if (Input = "Restart"):
                set CurrentState = game_state.MainMenu
```

将 `case` 表达式与枚举一起使用，可以借助穷举检查提供强大的模式匹配，确保你正确处理所有可能的值。

### 开放枚举与封闭枚举

枚举可以标记为开放或封闭，这会从根本上影响它们如何演化以及如何与模式匹配交互：

<!--NoCompile-->
<!-- 12 -->
```verse
# Closed enum - cannot add values after publication
day_of_week := enum<closed>:  # <closed> is the default
    Monday
    Tuesday
    Wednesday
    Thursday
    Friday
    Saturday
    Sunday

# Open enum - can add new values after publication
weapon_type := enum<open>:
    Sword
    Bow
    Staff
    # Can add Wand, Dagger, etc. in updates
```

**封闭枚举**（默认）承诺永远使用固定的值集合。这使得编译器能够验证 case 表达式是否穷举了所有可能性。对于真正固定的集合使用封闭枚举：星期几、基本方向、基础游戏状态。

**开放枚举**允许在未来的版本中添加新值。这种灵活性是有代价的：case 表达式无法做到穷举，因为未来可能存在新的值。对于可扩展的集合使用开放枚举：物品类型、敌人类型、伤害类型，或任何可能增长的内容。

### 穷举性

枚举类型和 case 表达式之间的交互遵循复杂的规则，在保证安全性的同时兼顾灵活性。理解这些规则对于有效使用枚举至关重要。

**封闭枚举 + 完全覆盖：**

当你的 case 表达式处理了封闭枚举中的每个值时，不需要通配符：

<!--NoCompile-->
<!-- 13 -->
```verse
day := enum:
    Monday
    Tuesday
    Wednesday

# Exhaustive - all values covered
GetDayType(D:day):string =
    case (D):
        day.Monday => "Weekday"
        day.Tuesday => "Weekday"
        day.Wednesday => "Weekday"
    # No wildcard needed - all values handled
```

当所有 case 都已覆盖时添加通配符会触发不可达代码警告：

<!--versetest
day := enum:
    Monday
    Tuesday
    Wednesday

GetDayType(D:day):string =
    case (D):
        day.Monday => "Weekday"
        day.Tuesday => "Weekday"
        day.Wednesday => "Weekday"
<#
-->
<!-- 14 -->
```verse
# Warning: unreachable wildcard
GetDayType(D:day):string =
    case (D):
        day.Monday => "Weekday"
        day.Tuesday => "Weekday"
        day.Wednesday => "Weekday"
        _ => "Unknown"  # WARNING: unreachable - all values already matched
```
<!-- #> -->

**封闭枚举 + 部分覆盖：**

如果你没有匹配所有值，则必须提供通配符或处于 `<decides>` 上下文中：

<!--NoCompile-->
<!-- 15 -->
```verse
day := enum:
    Monday
    Tuesday
    Wednesday
    Thursday

# With wildcard - OK
GetWeekStartWildCard(D:day):string =
    case (D):
        day.Monday => "Week start"
        _ => "Mid-week"

# Without wildcard but in <decides> context - OK
GetWeekStartDecides(D:day)<decides>:string =
    case (D):
        day.Monday => "Week start"
        # Missing other days causes failure

# Without either - COMPILE ERROR
# GetWeekStartBad(D:day):string =
#    case (D):
#        day.Monday => "Week start"
#        # ERROR: Missing cases and no wildcard
```

**开放枚举始终需要通配符或 `<decides>`：**

开放枚举在发布后可以添加新的值，因此它们永远无法做到穷举。\
这是为了确保使用它们的函数的向后兼容性（另请参阅[发布函数](06_functions.md/#publishing-functions)）：

<!--NoCompile-->
<!-- 16 -->
```verse
weapon := enum<open>:
    Sword
    Bow
    Staff

# Must have wildcard - OK
GetWeaponClassWildCard(W:weapon):string =
    case (W):
        weapon.Sword => "Melee"
        weapon.Bow => "Ranged"
        weapon.Staff => "Magic"
        _ => "Unknown"  # REQUIRED - future values may exist

# In <decides> context without wildcard - OK
GetWeaponClassDecides(W:weapon)<decides>:string =
    case (W):
        weapon.Sword => "Melee"
        weapon.Bow => "Ranged"
        weapon.Staff => "Magic"
        # Can fail for unknown (future) values

# Without either - COMPILE ERROR
# GetWeaponClassBad(W:weapon):string =
#    case (W):
#        weapon.Sword => "Melee"
#        weapon.Bow => "Ranged"
#        weapon.Staff => "Magic"
#        # ERROR: Open enum requires wildcard or <decides>
```

即使你匹配了开放枚举中当前定义的所有值，你仍然需要通配符或 `<decides>` 上下文，因为未来版本可能会添加新值。

**穷举规则总结：**

| 枚举类型 | Case 覆盖 | 通配符 | 上下文 | 结果 |
|-----------|---------------|----------|---------|--------|
| 封闭 | 完全 | 无 | 任意 | ✓ 有效 - 穷举 |
| 封闭 | 完全 | 有 | 任意 | ⚠ 警告 - 通配符不可达 |
| 封闭 | 部分 | 有 | 任意 | ✓ 有效 |
| 封闭 | 部分 | 无 | `<decides>` | ✓ 有效 - 未匹配的值失败 |
| 封闭 | 部分 | 无 | 非 `<decides>` | ✗ 错误 - 缺少 case |
| 开放 | 任意 | 有 | 任意 | ✓ 有效 |
| 开放 | 任意 | 无 | `<decides>` | ✓ 有效 - 未匹配的值失败 |
| 开放 | 任意 | 无 | 非 `<decides>` | ✗ 错误 - 开放枚举需要通配符 |

这些规则确保封闭枚举通过穷举提供安全性，而开放枚举则需要显式处理未知值。

### 不可达 Case 检测

编译器会主动检测 case 表达式中的不可达 case，帮助你识别死代码和逻辑错误：

**重复的 case** 会被标记为不可达：

<!--versetest
status := enum:
    Active
    Inactive
    Pending

GetStatusCode(S:status):int =
    case (S):
        status.Active => 1
        status.Inactive => 2
        status.Pending => 3
<#
-->
<!-- 17 -->
```verse
status := enum:
    Active
    Inactive
    Pending

# ERROR: Duplicate case is unreachable
GetStatusCode(S:status):int =
    case (S):
        status.Active => 1
        status.Inactive => 2
        status.Pending => 3
        status.Pending => 4  # ERROR: unreachable - already matched above
```
<!-- #> -->

**通配符之后的 case** 始终不可达：

<!--versetest
status := enum:
    Active
    Inactive
    Pending

GetStatusCode(S:status):int =
    case (S):
        status.Active => 1
        _ => 0
<#
-->
<!-- 18 -->
```verse
# ERROR: Case after wildcard
GetStatusCode(S:status):int =
    case (S):
        status.Active => 1
        _ => 0  # Wildcard matches everything
        status.Inactive => 2  # ERROR: unreachable - wildcard already matched
```
<!-- #> -->

这些错误防止了你以为在处理特定 case 但代码永远不会执行的逻辑错误。

### `@ignore_unreachable` 属性

有时你确实想要不可达的 case——例如用于测试、迁移或防御性编程。`@ignore_unreachable` 属性可以抑制特定 case 的不可达警告和错误：

<!--NoCompile-->
<!-- 19 -->
```verse
status := enum:
    Active
    Inactive

ProcessStatus(S:status):int =
    case (S):
        status.Active => 1
        status.Inactive => 2
        @ignore_unreachable status.Inactive => 3  # No error
        @ignore_unreachable _ => 0  # No unreachable warning
```

此属性仅影响它所应用的 case。没有该属性的其他不可达 case 仍然会产生错误：

<!--versetest
status := enum:
    Active
    Inactive

ProcessStatus(S:status):int =
    case (S):
        status.Active => 1
        status.Inactive => 2
        @ignore_unreachable status.Inactive => 3
<#
-->
<!-- 20 -->
```verse
ProcessStatus(S:status):int =
    case (S):
        status.Active => 1
        status.Inactive => 2
        @ignore_unreachable status.Inactive => 3  # Suppressed
        status.Active => 4  # ERROR: still unreachable without attribute
```
<!-- #> -->

请谨慎使用 `@ignore_unreachable`，主要在重构期间或为测试目的维护多个代码路径时使用。

### 显式限定

枚举值可能与父作用域中的标识符冲突。发生这种情况时，可以使用显式限定来消除歧义：

<!--NoCompile-->
<!-- 21 -->
```verse
# Top level 'Start'
Start:int = 0

# Enum wants to use 'Start' as enumerator
game_state := enum:
    (game_state:)Start  # Explicit qualification avoids collision
    Playing
    Paused

# Now both are accessible
OuterStart:int = Start             # References the int
StateStart:game_state = game_state.Start  # References the enum value
```

语法 `(enum_name:)enumerator` 显式限定枚举值，防止与外部作用域中的符号冲突。

**使用保留字作为枚举值：**

限定还允许你将保留字和关键字用作枚举值，否则会导致错误：

<!--NoCompile-->
<!-- 22 -->
```verse
# Using reserved words as enum values
keyword_enum := enum:
    (keyword_enum:)public    # OK: reserved word qualified
    (keyword_enum:)for       # OK: keyword qualified
    (keyword_enum:)class     # OK: reserved word qualified
    Regular                  # Normal enum value

# Without qualification - errors
# bad_enum := enum:
#    public    # Error: reserved word
#    for       # Error: reserved keyword
```

这在建模语言构造、访问级别或任何保留字构成自然值名称的领域时特别有用。

**自引用枚举值：**

你甚至可以在限定的情况下将枚举自身的名称用作值：

<!--NoCompile-->
<!-- 23 -->
```verse
recursive_enum := enum:
    (recursive_enum:)recursive_enum  # OK: qualified with enum name
    OtherValue

# Without qualification - error
# bad_recursive := enum:
  #  bad_recursive  # Error: shadows the type name
```

### 比较

枚举值是完全可比较的，这意味着它们同时支持相等（`=`）和不相等（`<>`）运算符。这使得它们非常适合状态跟踪和条件逻辑：

<!--versetest
weapon_type := enum:
    Sword
    Bow
    Staff

game_state := enum:
    MainMenu
    Playing
    Paused

PlaySwordAnimation()<transacts>:void = {}
OnStateChanged(Prev:game_state, Curr:game_state)<transacts>:void = {}
-->
<!-- 25 -->
```verse
CurrentWeapon := weapon_type.Sword
if (CurrentWeapon = weapon_type.Sword):
    PlaySwordAnimation()

CurrentState := game_state.Paused
PreviousState := game_state.Playing
if (CurrentState <> PreviousState):
    OnStateChanged(PreviousState, CurrentState)
```

来自同一枚举类型的枚举值可以相互比较，而来自不同枚举类型的值始终不相等：

<!--versetest
letters := enum:
    A, B, C

numbers := enum:
    One, Two, Three

Test()<decides>:letters =
    letters.A = letters.A
    letters.A <> letters.B
    letters.A <> numbers.One
    letters.A
<#
-->
<!-- 26 -->
```verse
letters := enum:
    A, B, C

numbers := enum:
    One, Two, Three

Test()<decides>:letters =
    letters.A = letters.A    # Succeeds - same value
    letters.A <> letters.B   # Succeeds - different values
    letters.A <> numbers.One # Succeeds - different enum types
```
<!-- #> -->

由于枚举是可比较的，它们可以用作映射键、存储在集合中，并与要求可比较类型的泛型函数一起使用：

<!--versetest
game_state := enum{
    Menu
    Playing
    Paused
    GameOver
    Debug
    }
-->
<!-- 27 -->
```verse
# Enums as map keys
StateIDs:[game_state]int = map{
    game_state.Menu => 0,
    game_state.Playing => 1,
    game_state.Paused => 2
}

# In generic functions
FindStateID(States:[]game_state, Target:game_state):int =
    for (
        State : States, State = Target,
        ID := StateIDs[State]
    ):
        return ID
    -1 # Return -1 if state is not found
```
