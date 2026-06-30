# 结构体和枚举

结构和枚举代表 Verse 的面向值的类型系统，为简单的数据聚合和固定的命名值集提供了类的轻量级替代方案。与具有面向对象特性的类不同，结构和枚举注重简单性、不变性和值语义。

结构捆绑相关数据，无需方法或继承，非常适合数学类型、配置数据和简单记录。枚举定义固定的命名常量集，用有意义的名称替换幻数，并通过详尽的模式匹配提供编译时安全性。

结构和枚举通过提供针对特定用例优化的更简单、更受约束的类型构造函数来补充类和接口。

<a id="structs"></a>
## 结构体

结构提供轻量级数据容器，但没有类的面向对象功能。它们是针对简单数据聚合而优化的值类型，非常适合数学类型、数据传输对象以及任何需要简单的相关值捆绑而无需行为的场景。

以最小的开销构造组相关数据：

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
    A : int = 255  # Alpha 通道

damage_info := struct:
    Amount : int = 0
    Type : damage_type = damage_type.Physical
    Source : ?character = false
    IsCritical : logic = false
```
默认情况下，所有结构字段都是公共且不可变的。结构不能有方法、构造函数，也不能参与继承层次结构。这种简单性使它们高效且可预测。

### 建设

创建结构实例使用与类相同的原型语法：

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
Origin := vector2{}  # 使用默认值：(0.0, 0.0)
PlayerPos := vector2{X := 100.0, Y := 250.0}
RedColor := color{R := 255}  # 其他通道默认为0/255

# 结构就是值 - 赋值创建一个副本
NewPos := PlayerPos
# NewPos 是具有相同值的单独实例
```
由于结构体是值类型，因此将结构体分配给变量会创建其所有数据的副本。这与使用引用语义的类不同。

### 比较

具有所有可比较字段的结构都支持相等比较：

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

if (Origin = vector3i{}):  # 成功 - 所有字段都匹配
    Print("At origin")

if (Origin = UnitX):  # 失败 - X 字段不同
    Print("Same position")
```
<!-- #> -->

比较逐个字段进行，只有当所有相应字段都相等时才会成功。

<a id="persistable-structs"></a>
### 可持久化结构

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

# 可用于持久存储
PlayerData : weak_map(player, player_stats) = map{}
```
<!-- #> -->

一旦发布，可持久化结构就无法修改，从而确保游戏更新之间的数据兼容性。

<a id="enums"></a>
## 枚举

枚举使用一组固定的命名值定义类型，非常适合表示状态、类型或具有已知的有限替代集的任何概念。它们通过用有意义的名称替换幻数来使代码更具可读性，并通过将值限制为定义的集合来提供编译时安全性。

枚举列出了类型的所有可能值：

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
枚举中的每个值都成为该枚举类型的命名常量。编译器确保枚举类型的变量只能保存这些定义值之一。枚举甚至可以为空：

<!--versetest
placeholder := enum{}
<#
-->
<!-- 06 -->
```verse
placeholder := enum{}  # 有效但很少有用
```
<!-- #> -->

枚举引入了一种类型和一组值，区分它们至关重要：

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

# 状态是类型
# status.Active 和 status.Inactive 是 VALUES

CurrentStatus:status = status.Active  # OK - 类型状态的值
```
<!-- #> -->

您不能在需要值的地方使用枚举类型：

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
# 错误：无法使用类型作为值
BadAssignment:status = status  # 编译错误
set CurrentStatus = status     # 编译错误

# 正确：使用枚举值
GoodAssignment:status = status.Active  # 好的
set CurrentStatus = status.Inactive    # 好的
```
<!-- #> -->

这种区别可以防止混淆并确保类型安全。枚举类型定义了可能的值，而枚举值是您在代码中使用的实际常量。

### 限制

枚举有特定的语法要求，以保持其用法清晰明确：

**枚举必须位于定义的直接右侧：**

<!--versetest
priority := enum:
    Low
    Medium
    High
<#
-->
<!-- 09 -->
```verse
# 有效
priority := enum:
    Low
    Medium
    High

# 无效 - 不能在表达式中使用枚举
Result := -enum{A, B}      # 编译错误
value := enum{X, Y} + 1    # 编译错误
```
<!-- #> -->

**枚举必须是模块或类级定义：**

<!--versetest
my_enum := enum:
    Value1
    Value2

ProcessData():void = {}
<#
-->
<!-- 10 -->
```verse
# 有效
my_enum := enum:
    Value1
    Value2

# 无效 - 无法定义本地枚举
ProcessData():void =
    LocalEnum := enum{A, B}  # 编译错误 - 没有本地枚举
```
<!-- #> -->

这些限制确保枚举在整个代码库中保持稳定、可引用的定义，而不是短暂的本地值。

<a id="using-enums"></a>
### 使用枚举

枚举为容易出错的字符串或整数常量提供了类型安全的替代方案：

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
带有枚举的 `case` 表达式提供强大的模式匹配和详尽检查，确保您正确处理所有可能的值。

<a id="open-vs-closed-enums"></a>
### 开放枚举与封闭枚举

枚举可以标记为开放或封闭，从根本上影响它们如何演变以及它们如何与模式匹配交互：

<!--NoCompile-->
<!-- 12 -->
```verse
# 封闭枚举 - 发布后无法添加值
day_of_week := enum<closed>:  # <关闭> 是默认值
    Monday
    Tuesday
    Wednesday
    Thursday
    Friday
    Saturday
    Sunday

# 开放枚举 - 可以在发布后添加新值
weapon_type := enum<open>:
    Sword
    Bow
    Staff
    # 可以在更新中添加魔杖、匕首等
```
**封闭枚举**（默认）永远承诺一组固定的值。这允许编译器验证 case 表达式是否详尽地处理了所有可能性。使用封闭枚举来实现真正固定的集合：一周中的几天、基本方向、基本游戏状态。

**开放枚举**允许在未来版本中添加新值。这种灵活性是有代价的：case 表达式不能详尽无遗，因为未来的值可能存在。对可扩展集使用开放枚举：项目类型、敌人类型、伤害类型或任何可能增长的内容。

### 详尽性

枚举类型和 case 表达式之间的交互遵循复杂的规则，可以防止错误，同时实现安全性和灵活性。理解这些规则对于有效地使用枚举至关重要。

**完全覆盖的封闭枚举：**

当您的 case 表达式处理封闭枚举中的每个值时，不需要通配符：

<!--NoCompile-->
<!-- 13 -->
```verse
day := enum:
    Monday
    Tuesday
    Wednesday

# 详尽 - 涵盖所有价值
GetDayType(D:day):string =
    case (D):
        day.Monday => "Weekday"
        day.Tuesday => "Weekday"
        day.Wednesday => "Weekday"
    # 不需要通配符 - 处理所有值
```
当覆盖所有情况时添加通配符会触发无法访问的代码警告：

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
# 警告：无法访问通配符
GetDayType(D:day):string =
    case (D):
        day.Monday => "Weekday"
        day.Tuesday => "Weekday"
        day.Wednesday => "Weekday"
        _ => "Unknown"  # 警告：无法访问 - 所有值均已匹配
```
<!-- #> -->

**部分覆盖的封闭枚举：**

如果您不匹配所有值，则必须提供通配符或位于 `<decides>` 上下文中：

<!--NoCompile-->
<!-- 15 -->
```verse
day := enum:
    Monday
    Tuesday
    Wednesday
    Thursday

# 使用通配符 - 确定
GetWeekStartWildCard(D:day):string =
    case (D):
        day.Monday => "Week start"
        _ => "Mid-week"

# 没有通配符但在 <decides> 上下文中 - 好的
GetWeekStartDecides(D:day)<decides>:string =
    case (D):
        day.Monday => "Week start"
        # 错过其他日子会导致失败

# 没有任何一个 - 编译错误
# GetWeekStartBad(D:day):string =
#    case (D):
#        day.Monday => "Week start"
#        # 错误：缺少大小写且没有通配符
```
**开放枚举始终需要通配符或 `<decides>`：**

开放枚举可以在发布后添加新值，因此它们永远不会详尽无遗。\
这是为了确保使用它们的函数的向后兼容性（另请参见[发布函数](06_functions.md/#publishing-functions)）：

<!--NoCompile-->
<!-- 16 -->
```verse
weapon := enum<open>:
    Sword
    Bow
    Staff

# 必须有通配符 - 好的
GetWeaponClassWildCard(W:weapon):string =
    case (W):
        weapon.Sword => "Melee"
        weapon.Bow => "Ranged"
        weapon.Staff => "Magic"
        _ => "Unknown"  # 必需 - 未来值可能存在

# 在没有通配符的 <decides> 上下文中 - 确定
GetWeaponClassDecides(W:weapon)<decides>:string =
    case (W):
        weapon.Sword => "Melee"
        weapon.Bow => "Ranged"
        weapon.Staff => "Magic"
        # 可能因未知（未来）值而失败

# 没有任何一个 - 编译错误
# GetWeaponClassBad(W:weapon):string =
#    case (W):
#        weapon.Sword => "Melee"
#        weapon.Bow => "Ranged"
#        weapon.Staff => "Magic"
#        # 错误：开放枚举需要通配符或 <decides>
```
即使您匹配开放枚举中所有当前定义的值，您仍然需要通配符或 `<decides>` 上下文，因为未来版本中可能会添加新值。

**详尽性规则摘要：**

|枚举类型 |案例报道 |通配符 |背景 |结果 |
|------------|--------------|----------|---------|--------|
|关闭 |完整|没有 |任何 | ✓ 有效 - 详尽 |
|关闭 |完整|是的 |任何 | ⚠ 警告 - 无法访问的通配符 |
|关闭 |部分|是的 |任何 | ✓ 有效 |
|关闭 |部分|没有 | `<decides>` | ✓ 有效 - 不匹配的值失败 |
|关闭 |部分|没有 |非`<decides>` | ✗ 错误 - 丢失案例 |
|打开|任何 |是的 |任何 | ✓ 有效 |
|打开|任何 |没有 | `<decides>` | ✓ 有效 - 不匹配的值失败 |
|打开|任何 |没有 |非`<decides>` | ✗ 错误 - 打开枚举需要通配符 |

这些规则确保封闭枚举通过详尽性提供安全性，而开放枚举则需要显式处理未知值。

### 无法到达的案例检测

编译器主动检测 case 表达式中无法访问的 case，帮助您识别死代码和逻辑错误：

**重复的案例**被标记为无法访问：

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

# 错误：无法访问重复的案例
GetStatusCode(S:status):int =
    case (S):
        status.Active => 1
        status.Inactive => 2
        status.Pending => 3
        status.Pending => 4  # 错误：无法访问 - 上面已匹配
```
<!-- #> -->

**通配符之后的情况**始终无法访问：

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
# 错误：通配符后出现大小写
GetStatusCode(S:status):int =
    case (S):
        status.Active => 1
        _ => 0  # 通配符匹配所有内容
        status.Inactive => 2  # 错误：无法访问 - 通配符已匹配
```
<!-- #> -->

这些错误可以防止您认为正在处理特定情况但代码永远不会执行的逻辑错误。

### `@ignore_unreachable` 属性

有时，您故意想要无法访问的案例 - 用于测试、迁移或防御性编程。 `@ignore_unreachable` 属性抑制特定情况下无法访问的警告和错误：

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
        @ignore_unreachable status.Inactive => 3  # 没有错误
        @ignore_unreachable _ => 0  # 没有无法到达的警告
```
此属性仅影响其应用的情况。其他没有该属性的无法访问的情况仍然会产生错误：

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
        @ignore_unreachable status.Inactive => 3  # 压抑
        status.Active => 4  # 错误：没有属性仍然无法访问
```
<!-- #> -->

谨慎使用 `@ignore_unreachable`，主要是在重构期间或出于测试目的维护多个代码路径时。

### 明确的资格

枚举数可能会与父作用域中的标识符发生冲突。发生这种情况时，您可以使用显式限定来消除歧义：

<!--NoCompile-->
<!-- 21 -->
```verse
# 顶级“开始”
Start:int = 0

# Enum 希望使用“Start”作为枚举器
game_state := enum:
    (game_state:)Start  # 明确的资格避免冲突
    Playing
    Paused

# 现在两者都可以访问
OuterStart:int = Start             # 引用 int
StateStart:game_state = game_state.Start  # 引用枚举值
```
语法 `(enum_name:)enumerator` 显式限定枚举器，防止与外部范围符号发生冲突。

**使用保留字作为枚举值：**

资格还允许您使用保留字和关键字作为枚举值，否则会导致错误：

<!--NoCompile-->
<!-- 22 -->
```verse
# 使用保留字作为枚举值
keyword_enum := enum:
    (keyword_enum:)public    # OK：保留字正确
    (keyword_enum:)for       # OK：关键字合格
    (keyword_enum:)class     # OK：保留字正确
    Regular                  # 正常枚举值

# 没有资格 - 错误
# bad_enum := enum:
#    public # 错误：保留字
#    for       # Error: reserved keyword
```
这在对语言结构、访问级别或保留字生成自然值名称的任何域进行建模时特别有用。

**自引用枚举值：**

您甚至可以在限定时使用枚举自己的名称作为值：

<!--NoCompile-->
<!-- 23 -->
```verse
recursive_enum := enum:
    (recursive_enum:)recursive_enum  # OK：用枚举名称限定
    OtherValue

# 没有资格-错误
# bad_recursive := enum:
  #  bad_recursive # 错误：隐藏类型名称
```
### 比较

枚举值完全可比较，这意味着它们支持相等 (`=`) 和不等 (`<>`) 运算符。这使得它们非常适合状态跟踪和条件逻辑：

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
相同枚举类型的枚举值可以进行比较，而不同枚举类型的值总是不相等：

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
    letters.A = letters.A    # 成功 - 相同的价值
    letters.A <> letters.B   # 成功——不同的价值观
    letters.A <> numbers.One # 成功 - 不同的枚举类型
```
<!-- #> -->

因为枚举是可比较的，所以它们可以用作映射键，存储在集合中，并与需要可比较类型的泛型函数一起使用：

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
# 枚举作为映射键
StateIDs:[game_state]int = map{
    game_state.Menu => 0,
    game_state.Playing => 1,
    game_state.Paused => 2
}

# 在泛型函数中
FindStateID(States:[]game_state, Target:game_state):int =
    for (
        State : States, State = Target,
        ID := StateIDs[State]
    ):
        return ID
    -1 # 如果未找到状态则返回-1
```
