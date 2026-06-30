# 运算符

运算符是对操作数执行操作的函数。它们为常见操作（如算术运算、比较运算、逻辑运算和赋值）提供简洁的语法。

## 运算符形式

Verse 运算符根据其相对于操作数的位置分为三种形式：

**前缀运算符（Prefix Operators）**

前缀运算符出现在其单个操作数之前：

- `not Expression` — 逻辑取反
- `-Value` — 数值取反
- `+Value` — 数值正号（用于对齐）

**中缀运算符（Infix Operators）**

中缀运算符出现在其两个操作数之间：

- `A + B` — 加法
- `A * B` — 乘法
- `A = B` — 相等比较
- `A and B` — 逻辑 AND

**后缀运算符（Postfix Operators）**

后缀运算符绑定到其左侧的表达式。虽然有些运算符（如 `.`）出现在两个元素之间，但它们被归类为后缀，因为它们作用于左侧表达式：

- `Value?` — 对逻辑值的查询运算符
- `Object.Member` — 成员访问（`.` 作用于其左侧的对象）
- `Array[Index]` — 数组索引（`[]` 作用于其左侧的数组）
- `Function()` — 函数调用（`()` 作用于其左侧的函数）
- `Constructor{}` — 对象构造（`{}` 作用于其左侧的类型）

虽然 `.` 出现在 `Player.Respawn()` 中的 `Player` 和 `Respawn` *之间*，但它被视为后缀，因为它绑定到 `Player` 并从中选择成员。右侧（`Respawn`）不是一个独立操作数，而是一个成员选择器。

## 优先级

当同一表达式中有多个运算符时，它们将根据其优先级级别进行求值。优先级较高的运算符先求值。相同优先级的运算符从左到右求值（赋值和一元运算符除外，它们是右结合的）。

优先级从高到低如下：

| 优先级 | 运算符 | 类别 | 形式 | 结合性 | 示例 |
|------------|-----------|----------|--------|---------------|--|
| 11 | `.`, `[]`, `()`, `{}`, `?`（后缀） | 成员访问、索引、调用、构造、查询 | 后缀 | 左 | `BossDefeated?`, `Player.Respawn()` |
| 10 | `+`, `-`（一元）, `not` | 一元运算 | 前缀 | 右 | `+Score`, `-Distance`, `not HasCooldown?` |
| 9 | `*`, `/` | 乘法、除法 | 中缀 | 左 | `Score * Multiplier` |
| 8 | `+`, `-`（二元） | 加法、减法 | 中缀 | 左 | `X + Y`, `Health - Damage` |
| 7 | `=`（关系）, `<>`, `<`, `<=`, `>`, `>=` | 关系比较 | 中缀 | 右 | `Player <> Target`, `Score > 100` |
| 5 | `and` | 逻辑 AND | 中缀 | 左 | `HasPotion? and TryUsePotion[]` |
| 4 | `or` | 逻辑 OR | 中缀 | 左 | `IsAlive? or Respawn()` |
| 3 | `..` | 范围 | 中缀 | 左 | `0..100`, `-15..50` |
| 2 | ~~Lambda 表达式~~ | ~~函数字面量~~（尚不支持） | 特殊 | N/A | N/A |
| 1 | `:=`, `set =` | 赋值 | 中缀 | 右 | `X := 15`, `set Y = 25` |

`=` 符号在 Verse 中有两个不同的用途：
- **关系比较**（优先级 7）：当用作表达式中的运算符时，`A = B` 测试相等性并返回一个 `logic` 值
- **赋值**（优先级 1）：当与 `set` 关键字一起使用时，`set X = Value` 为已有变量赋新值

这与 `:=` 不同，`:=` 始终表示对新变量"定义并初始化"。`=` 的含义由上下文决定。

## 算术运算符

算术运算符对数值执行数学运算。它们适用于 `int` 和 `float` 类型，并在类型转换和整数除法方面有一些特殊行为。

### 基本算术

| 运算符 | 运算 | 类型 | 说明 |
|----------|-----------|-------|-------|
| `+` | 加法 | `int`, `float` | 也可连接字符串和数组 |
| `-` | 减法 | `int`, `float` | 可用作一元取反 |
| `*` | 乘法 | `int`, `float` | 混合使用时将 `int` 转换为 `float` |
| `/` | 除法 | `int`（可失败）, `float` | 整数除法返回 `rational` |

<!--versetest-->
<!-- 01-->
```verse
# Basic arithmetic
Sum := 10 + 20      # 30
Diff := 50 - 15     # 35
Prod := 6 * 7       # 42
Quot := 20.0 / 4.0  # 5.0

# Unary operators
Negative := -42     # -42
Positive := +42     # 42 (for alignment)

# Integer division (failable, returns rational)
if (Result := 10 / 3):
    IntResult := Floor(Result)  # 3

# Type conversion through multiplication
IntValue:int = 42
FloatValue:float = IntValue * 1.0  # Converts to 42.0
```

### 复合赋值

复合赋值运算符将算术运算与赋值结合：

| 运算符 | 等价于 | 类型 |
|----------|---------------|-------|
| `set +=` | `set X = X + Y` | `int`, `float`, `string`, `array` |
| `set -=` | `set X = X - Y` | `int`, `float` |
| `set *=` | `set X = X * Y` | `int`, `float` |
| `set /=` | `set X = X / Y` | `float` only |

<!--versetest-->
<!-- 02-->
```verse
var Score:int = 100
set Score += 50    # Score is now 150
set Score -= 25    # Score is now 125
set Score *= 2     # Score is now 250

var Health:float = 100.0
set Health /= 2.0  # Health is now 50.0

# Arrays can use += with both arrays and tuples
var Items:[]int = array{1, 2, 3}
set Items += array{4, 5}  # Items is now array{1, 2, 3, 4, 5}
set Items += (6, 7)       # Items is now array{1, 2, 3, 4, 5, 6, 7}

# Note: set /= doesn't work with integers due to failable division
# var IntValue:int = 10
# set IntValue /= 2  # Compile error!
```

## 比较运算符

比较运算符测试值之间的关系，是可失败表达式，根据比较结果成功或失败。

### 关系运算符

| 运算符 | 含义 | 支持的类型 | 示例 |
|----------|---------|-----------------|---------|
| `<` | 小于 | `int`, `float` | `Score < 100` |
| `<=` | 小于或等于 | `int`, `float` | `Health <= 0.0` |
| `>` | 大于 | `int`, `float` | `Level > 5` |
| `>=` | 大于或等于 | `int`, `float` | `Time >= MaxTime` |

### 相等运算符

| 运算符 | 含义 | 支持的类型 | 示例 |
|----------|---------|-----------------|---------|
| `=` | 等于 | 所有可比较类型 | `Name = "Player1"` |
| `<>` | 不等于 | 所有可比较类型 | `State <> idle` |

<!--versetest
HandlePlayerDeath():void={}
EnableAdminMode():void={}
ShowMenu():void={}
UnlockAchievement():void={}
game_state := enum{Playing, Paused}
Score:int = 1500
HighScore:int = 1000
Health:float = 0.0
PlayerName:string = "Admin"
CurrentState:game_state = game_state.Paused
Level:int = 15
-->
<!-- 03-->
```verse
# Numeric comparisons
if (Score > HighScore):
    Print("New high score!")

if (Health <= 0.0):
    HandlePlayerDeath()

# Example with other comparable types
if (PlayerName = "Admin"):
    EnableAdminMode()

if (CurrentState <> game_state.Playing):
    ShowMenu()

# Comparison in complex expressions
if (Level >= 10 and Score > 1000):
    UnlockAchievement()
```

以下类型支持相等比较运算（`=` 和 `<>`）：

- 数值类型：`int`, `float`, `rational`
- 布尔类型：`logic`
- 文本类型：`string`, `char`, `char32`
- 枚举类型：所有 `enum` 类型
- 集合类型：`array`, `map`, `tuple`, `option`（如果元素可比较）
- 结构体：如果所有字段都可比较
- 唯一类：标记为 `<unique>` 的类（仅标识相等性）

不同类型之间的比较通常会失败：

<!--versetest
assert:
    not (0 = 0.0)
    not ("5" = 5)
<#
-->
<!-- 04-->
```verse
0 = 0.0  # Fails: int vs float
"5" = 5  # Fails: string vs int
```
<!-- #>-->

## 逻辑运算符

逻辑运算符与可失败表达式一起使用，控制成功和失败的流程。

### 查询运算符（`?`）

查询运算符检查 `logic` 值是否为 `true`（关于 `?` 如何与其他类型配合使用，请参阅 [失败](08_failure.md#failable-expressions)）：

<!--versetest
StartGame():void={}
-->
<!-- 05-->
```verse
var IsReady:logic = true

if (IsReady?):
    StartGame()

# Equivalent to:
if (IsReady = true):
    StartGame()
```

### Not 运算符

`not` 运算符对表达式的成功或失败取反：

<!--versetest
ContinuePlaying()<computes>:void={}
IsGameOver:?int = option{1}
-->
<!-- 06-->
```verse
if (not IsGameOver?):
    ContinuePlaying()

# Effects are not committed with not
var X:int = 0
if (not (set X = 5, IsGameOver?)):
    # X is still 0 here, even though the assignment "tried" to happen
    Print("X is {X}")  # Prints "X is 0"
```

### And 运算符

`and` 运算符仅在两个操作数都成功时才成功：

<!--versetest
EnterRoom()<computes>:void={}
AllowQuestAccess()<computes>:void={}
ProcessResult()<computes>:void={}
HasKey:?int = option{1}
DoorUnlocked:?int = option{1}
player := struct{Level:int, HasItem:?int}
QuickCheck()<computes><decides>:void = {}
ExpensiveCheck()<computes><decides>:void = {}
-->
<!-- 07-->
```verse
Player:player = player{Level:=10, HasItem:=option{1}}
if (HasKey? and DoorUnlocked?):
    EnterRoom()

# Short-circuit evaluation - second operand not evaluated if first fails
if (QuickCheck[] and ExpensiveCheck[]):
    ProcessResult()
```

### Or 运算符

`or` 运算符在至少一个操作数成功时成功：

<!--versetest
OpenDoor()<computes>:void={}
ProcessResult()<computes>:void={}
HasKeyCard:?int = false
HasMasterKey:?int = option{1}
QuickCheck()<computes><decides>:void = {}
ExpensiveCheck()<computes><decides>:void = {}
-->
<!-- 08-->
```verse
if (HasKeyCard? or HasMasterKey?):
    OpenDoor()

# Short-circuit evaluation - second operand not evaluated if first succeeds
if (QuickCheck[] or ExpensiveCheck[]):
    ProcessResult()
```

### 真值表

考虑两个表达式 `P` 和 `Q`，它们要么成功要么失败，下表显示了对其应用逻辑运算符的结果：

| 表达式 P | 表达式 Q | P and Q | P or Q | not P |
|--------------|--------------|---------|---------|-------|
| 成功 | 成功 | 成功（Q 的值） | 成功（P 的值） | 失败 |
| 成功 | 失败 | 失败 | 成功（P 的值） | 失败 |
| 失败 | 成功 | 失败 | 成功（Q 的值） | 成功 |
| 失败 | 失败 | 失败 | 失败 | 成功 |

## 赋值与初始化

在初始化常量和变量时，如果提供了显式类型，则 `=` 和 `:=` 都可以使用。对于类型推断（无类型注解），必须使用 `:=`。

<!--versetest-->
<!-- 09-->
```verse
# Constant initialization with explicit types - both = and := work
MaxHealth:int = 100
PlayerName:string := "Hero"

# Variable initialization with explicit types - both = and := work
var CurrentHealth:int = 100
var Score:int := 0

# Type inference requires := (no type annotation)
AutoTyped := 42  # Inferred as int

# Note: var requires explicit type - var X := value is not allowed
```

`set =` 运算符用于更新变量值：

<!--versetest
vector3:=struct{X:float, Y:float, Z:float}
-->
<!-- 10-->
```verse
var Points:int = 0
set Points = 100

var Position:vector3 = vector3{X := 0.0, Y := 0.0, Z := 0.0}
set Position = vector3{X := 10.0, Y := 20.0, Z := 0.0}
```

## 特殊运算符

### 索引

方括号运算符在 Verse 中有多种用途：

1. **数组/映射索引** — 访问集合中的元素
2. **函数调用** — 调用可能失败的函数

<!--versetest
MyFunction1(X:int, Y:int)<decides>:void={}
MyFunction2(?X:int=0, ?Y:int=0)<decides>:void={}
Arg1:int = 0
Arg2:int = 0
<#
-->
<!-- 11-->
```verse
# Array indexing (failable)
MyArray := array{10, 20, 30}
if (Element := MyArray[1]):
    Print("Element at index 1: {Element}")  # Prints 20

# Map lookup (failable)
Scores:[string]int = map{"Alice" => 100, "Bob" => 85}
if (AliceScore := Scores["Alice"]):
    Print("Alice's score: {AliceScore}")

# String indexing (failable)
Name:string = "Verse"
if (FirstChar := Name[0]):
    Print("First character: {FirstChar}")  # Prints 'V'

# Function call that can fail
Result1 := MyFunction1[Arg1, Arg2]          # Can fail
Result2 := MyFunction2[?X:=Arg1, ?Y:=Arg2]  # Named arguments
EmptyCall := MyFunction2[]                  # and optional values
```
<!-- #>-->

### 成员访问

点运算符用于访问对象的字段和方法：

<!--versetest
player := class<computes>{Health:float = 100.0, GetName()<computes>:string = "Hero"}
vector3 := struct<computes>{X:float, Y:float, Z:float}
config_settings := struct<computes>{MaxPlayers:int = 10}
config := struct<computes>{Settings:config_settings = config_settings{}}
Player:player = player{}
MyVector:vector3 = vector3{X:=1.0, Y:=2.0, Z:=3.0}
Config:config = config{}
-->
<!-- 12-->
```verse
Player.Health
Player.GetName()
MyVector.X
Config.Settings.MaxPlayers
```

### 范围

范围运算符用于创建迭代范围：

<!--versetest-->
<!-- 13-->
```verse
# Inclusive range
for (I := 0..4):
    Print("{I}")  # Prints 0, 1, 2, 3, 4
```

### 对象构造

Verse 提供了多种构造对象的语法。以下所有方式都是等价的：

<!--versetest
point:=struct{X:int = 0, Y:int = 0}
player_data:=struct{Name:string,Level:int,Health:float}
game_config:=struct{MaxPlayers:int,EnablePvP:logic}
-->
<!-- 14-->
```verse
# Curly braces with commas
Point1 := point{X:= 10, Y:= 20}

# Curly braces with semicolons
Point2 := point{X:= 10; Y:= 20}

# Colon syntax with newlines (no braces)
Point3 := point:
    X:= 10
    Y:= 20

# Colon syntax with commas and newlines
Point4 := point:
    X:= 10,
    Y:= 20

# Fields can be separated by newlines inside braces
Player := player_data {
    Name := "Hero"
    Level := 5
    Health := 100.0
}

# Trailing commas are not allowed
Config := game_config{
    MaxPlayers := 100,
    EnablePvP := true # ,  -- comma not allowed here
}

# Dot syntax for single field (requires defaults for other fields)
Point5 := point . X:=10  # Y gets default value 0
Point6 := point . Y:=20  # X gets default value 0
```

### 元组访问

圆括号在元组表达式之后与单个参数一起使用时，用于访问元组元素：

<!--versetest-->
<!-- 15-->
```verse
MyTuple := (10, 20, 30)
FirstElement := MyTuple(0)  # Access first element
SecondElement := MyTuple(1)  # Access second element
```

## 类型转换

Verse 的隐式类型转换有限。大多数转换必须是显式的：

<!--versetest-->
<!-- 16-->
```verse
# No implicit int to float conversion
MyInt:int = 42
# MyFloat:float = MyInt  # Error!
MyFloat:float = MyInt * 1.0  # OK: explicit conversion

# No implicit numeric to string conversion
Score:int = 100
# Message:string = "Score: " + Score  # Error!
Message:string = "Score: {Score}"  # OK: string interpolation
```

当运算符处理混合类型时，适用特定规则：

<!--versetest-->
<!-- 17-->
```verse
# int * float -> float
Result := 5 * 2.0  # Result is 10.0 (float)

# Comparisons must be same type
if (5 = 5):     # OK
if (5.0 = 5.0): # OK
# if (5 = 5.0):   # Fails
```
