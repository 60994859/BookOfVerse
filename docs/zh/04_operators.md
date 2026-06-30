# 运算符

运算符是对其操作数执行操作的函数。它们为算术、比较、逻辑运算和赋值等常见操作提供简洁的语法。

## 运算符格式

根据相对于操作数的位置，Verse 运算符具有三种格式：

**前缀运算符**

前缀运算符出现在其单个操作数之前：

- `not Expression` - 逻辑非
- `-Value` - 数字否定
- `+Value` - 正数字（用于对齐）

**中缀运算符**

中缀运算符出现在两个操作数之间：

- `A + B` - 添加
- `A * B` - 乘法
- `A = B` - 相等比较
- `A and B` - 逻辑与

**后缀运算符**

后缀运算符绑定到其左侧的表达式。虽然有些（如 `.`）出现在两个元素之间，但它们被归类为后缀，因为它们对左侧表达式进行操作：

- `Value?` - 逻辑值查询运算符
- `Object.Member` - 成员访问（`.` 对其左侧的对象进行操作）
- `Array[Index]` - 数组索引（`[]` 对其左侧的数组进行操作）
- `Function()` - 函数调用（`()` 对其左侧的函数进行操作）
- `Constructor{}` - 对象构造（`{}` 对其左侧的类型进行操作）

尽管 `.` 出现在 `Player.Respawn()` 中的 `Player` 和 `Respawn` 之间，但它被视为后缀，因为它绑定到 `Player` 并从中选择一个成员。右侧（`Respawn`）不是单独的操作数而是成员选择器

## 优先级

当多个运算符出现在同一表达式中时，将根据其优先级对它们进行求值。首先评估优先级较高的运算符。具有相同优先级的运算符从左到右进行计算（赋值运算符和一元运算符除外，它们是右结合的）。

优先级从最高到最低依次为：

|优先级|运营商|类别 |格式|关联性|示例|
|------------|------------|----------|--------|---------------|--|
| 11 | 11 `.`、`[]`、`()`、`{}`、`?`（后缀）|会员访问、索引、调用、构建、查询 |后缀 |左| `BossDefeated?`，`Player.Respawn()`|
| 10 | 10 `+`、`-`（一元）、`not` |一元运算 |前缀 |对| `+Score`、`-Distance`、`not HasCooldown?` |
| 9 | `*`，`/` |乘法、除法 |中缀 |左| `Score * Multiplier` |
| 8 | `+`、`-`（二进制）|加法、减法|中缀 |左| `X + Y`，`Health - Damage` |
| 7 | `=`（关系）、`<>`、`<`、`<=`、`>`、`>=` |关系比较|中缀 |对| `Player <> Target`、`Score > 100` |
| 5 | `and` |逻辑与 |中缀 |左| `HasPotion? and TryUsePotion[]` |
| 4 | `or` |逻辑或 |中缀 |左| `IsAlive? or Respawn()` |
| 3 | `..` |范围 |中缀 |左| `0..100`，`-15..50` |
| 2 | ~~Lambda 表达式~~ | ~~函数文字~~（尚不支持） |特别|不适用 |不适用 |
| 1 | `:=`，`set =` |作业 |中缀 |对| `X := 15`，`set Y = 25` |

`=` 符号在 Verse 中有两个不同的用途：
- **关系比较**（优先级 7）：当在表达式中用作运算符时，`A = B` 测试相等并返回逻辑值
- **赋值**（优先级 1）：与 `set` 关键字一起使用时，`set X = Value` 为现有变量分配新值

这与 `:=` 不同，`:=` 始终意味着新变量的“定义和初始化”。上下文决定了 `=` 适用的含义。

## 算术运算符

算术运算符对数值执行数学运算。它们适用于 `int` 和 `float` 类型，
并且在类型转换和整数除法方面具有一些特殊行为。

### 基本算术

|运算符|操作|类型|说明|
|----------|------------|--------|--------|
| `+` |加法 | `int`，`float` |还连接字符串和数组 |
| `-` |减法| `int`，`float` |可以用作一元否定 |
| `*` |乘法| `int`，`float` |混合时将 `int` 转换为 `float` |
| `/` |除法| `int`（可失败），`float` |整数除法返回 `rational` |

<!--versetest-->
<!-- 01-->
```verse
# 基础算术
Sum := 10 + 20      # 30
Diff := 50 - 15     # 35
Prod := 6 * 7       # 42
Quot := 20.0 / 4.0  # 5.0

# 一元运算符
Negative := -42     # -42
Positive := +42     # 42（用于对齐）

# 整数除法（失败，返回有理数）
if (Result := 10 / 3):
    IntResult := Floor(Result)  # 3

# 通过乘法进行类型转换
IntValue:int = 42
FloatValue:float = IntValue * 1.0  # 转换为 42.0
```
### 复合作业

复合赋值运算符将算术运算与赋值结合起来：

|操作员|相当于 |类型 |
|----------|----------------|--------|
| `set +=` | `set X = X + Y` | `int`、`float`、`string`、`array` |
| `set -=` | `set X = X - Y` | `int`，`float` |
| `set *=` | `set X = X * Y` | `int`，`float` |
| `set /=` | `set X = X / Y` |仅 `float` |

<!--versetest-->
<!-- 02-->
```verse
var Score:int = 100
set Score += 50    # 现在分数是150
set Score -= 25    # 现在分数是125
set Score *= 2     # 现在分数是250

var Health:float = 100.0
set Health /= 2.0  # 生命值现在为 50.0

# 数组可以对数组和元组使用 +=
var Items:[]int = array{1, 2, 3}
set Items += array{4, 5}  # 项目现在是备份{1, 2, 3, 4, 5}
set Items += (6, 7)       # 项目现在是数组{1, 2, 3, 4, 5, 6, 7}

# 注意：由于除法失败，set /= 独立用于整数
# var IntValue:int = 10
# set IntValue /= 2  # Compile error!
```
## 比较运算符

比较运算符测试值之间的关系，并且是根据比较结果成功或失败的可失败表达式。

### 关系运算符

|操作员|意义|支持的类型 |示例|
|----------|---------|-----------------|---------|
| `<` |小于| `int`、`float` | `Score < 100` |
| `<=` |小于或等于 | `int`，`float` | `Health <= 0.0` |
| `>` |大于| `int`，`float` | `Level > 5` |
| `>=` |大于或等于| `int`，`float` | `Time >= MaxTime` |

### 相等运算符

|操作员|意义|支持的类型 |示例|
|----------|---------|-----------------|---------|
| `=` |等于 |所有类似类型 | `Name = "Player1"` |
| `<>` |不等于|所有类似类型 | `State <> idle` |

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
# 数字比较
if (Score > HighScore):
    Print("New high score!")

if (Health <= 0.0):
    HandlePlayerDeath()

# 其他类似类型的示例
if (PlayerName = "Admin"):
    EnableAdminMode()

if (CurrentState <> game_state.Playing):
    ShowMenu()

# 复杂表达式的比较
if (Level >= 10 and Score > 1000):
    UnlockAchievement()
```
以下类型支持相等比较操作（`=` 和 `<>`）：

- 数字类型：`int`、`float`、`rational`
- 布尔值：`logic`
- 文本：`string`、`char`、`char32`
- 枚举：所有 `enum` 类型
- 集合：`array`、`map`、`tuple`、`option`（如果元素具有可比性）
- 结构：如果所有字段都可比较
- 独特的类：标有 `<unique>` 的类（仅限身份平等）

不同类型之间的比较通常会失败：

<!--versetest
assert:
    not (0 = 0.0)
    not ("5" = 5)
<#
-->
<!-- 04-->
```verse
0 = 0.0  # 失败：int 与 float
"5" = 5  # 失败：字符串与整数
```
<!-- #>-->

## 逻辑运算符

逻辑运算符使用可失败表达式并控制成功和失败的流程。

### 查询运算符 (`?`)

查询运算符检查 `logic` 值是否为 `true`（有关 `?` 如何与其他类型配合使用的信息，请参阅[失败](08_failure.md#failable-expressions)）：

<!--versetest
StartGame():void={}
-->
<!-- 05-->
```verse
var IsReady:logic = true

if (IsReady?):
    StartGame()

# 相当于：
if (IsReady = true):
    StartGame()
```
### 非运算符

`not` 运算符否定表达式的成功或失败：

<!--versetest
ContinuePlaying()<computes>:void={}
IsGameOver:?int = option{1}
-->
<!-- 06-->
```verse
if (not IsGameOver?):
    ContinuePlaying()

# 效果不提交，不
var X:int = 0
if (not (set X = 5, IsGameOver?)):
    # 即使赋值“试图”发生，这里 X 仍然是 0
    Print("X is {X}")  # 打印“X 为 0”
```
### 和运算符

仅当两个操作数都成功时，`and` 运算符才会成功：

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

# 短路评估 - 如果第一个操作数失败，则不评估第二个操作数
if (QuickCheck[] and ExpensiveCheck[]):
    ProcessResult()
```
### 或运算符

如果至少有一个操作数成功，则 `or` 运算符成功：

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

# 短路评估 - 如果第一个操作数成功，则不评估第二个操作数
if (QuickCheck[] or ExpensiveCheck[]):
    ProcessResult()
```
### 真值表

考虑两个可能成功也可能失败的表达式 `P` 和 `Q`，下表显示了应用于它们的逻辑运算符的结果：

|表达 P |表达Q | P 和 Q | P 或 Q |不是 P |
|--------------|--------------|---------|---------|--------|
|成功|成功|成功（Q 值）|成功（P 值）|失败 |
|成功|失败|失败 |成功（P 值）|失败 |
|失败 |成功|失败 |成功（Q 值）|成功|
|失败 |失败 |失败 |失败 |成功|

## 赋值和初始化

初始化常量和变量时，如果提供显式类型，则可以使用 `=` 和 `:=`。对于类型推断（无类型注释），您必须使用 `:=`。

<!--versetest-->
<!-- 09-->
```verse
# 使用显式类型初始化常量时，= 和 := 都可用
MaxHealth:int = 100
PlayerName:string := "Hero"

# 使用显式类型初始化变量时，= 和 := 都可用
var CurrentHealth:int = 100
var Score:int := 0

# 类型推断要求使用 :=（没有类型注解）
AutoTyped := 42  # 推断为 int

# 注意：var 需要显式类型；不允许使用 var X := value
```
`set =` 运算符更新变量值：

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
## 特殊操作员

### 索引

方括号运算符在 Verse 中具有多种用途：

1. **数组/映射索引** - 访问集合中的元素
2. **函数调用** - 调用可能失败的函数

<!--versetest
MyFunction1(X:int, Y:int)<decides>:void={}
MyFunction2(?X:int=0, ?Y:int=0)<decides>:void={}
Arg1:int = 0
Arg2:int = 0
<#
-->
<!-- 11-->
```verse
# 数组索引（失败）
MyArray := array{10, 20, 30}
if (Element := MyArray[1]):
    Print("Element at index 1: {Element}")  # 打印 20

# 映射查找（失败）
Scores:[string]int = map{"Alice" => 100, "Bob" => 85}
if (AliceScore := Scores["Alice"]):
    Print("Alice's score: {AliceScore}")

# 字符串索引（失败）
Name:string = "Verse"
if (FirstChar := Name[0]):
    Print("First character: {FirstChar}")  # 打印“V”

# 可能失败的函数调用
Result1 := MyFunction1[Arg1, Arg2]          # 可能会失败
Result2 := MyFunction2[?X:=Arg1, ?Y:=Arg2]  # 命名参数
EmptyCall := MyFunction2[]                  # 和可选值
```
<!-- #>-->

### 会员访问

点运算符访问对象的字段和方法：

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

范围运算符创建迭代范围：

<!--versetest-->
<!-- 13-->
```verse
# 包含范围
for (I := 0..4):
    Print("{I}")  # 打印 0、1、2、3、4
```
### 对象构造

Verse 提供了多种用于构造对象的语法。以下所有内容都是等效的：

<!--versetest
point:=struct{X:int = 0, Y:int = 0}
player_data:=struct{Name:string,Level:int,Health:float}
game_config:=struct{MaxPlayers:int,EnablePvP:logic}
-->
<!-- 14-->
```verse
# 带逗号的大括号
Point1 := point{X:= 10, Y:= 20}

# 带分号的大括号
Point2 := point{X:= 10; Y:= 20}

# 带换行符的冒号语法（无大括号）
Point3 := point:
    X:= 10
    Y:= 20

# 带有逗号和换行符的冒号语法
Point4 := point:
    X:= 10,
    Y:= 20

# 字段可以用大括号内的换行符分隔
Player := player_data {
    Name := "Hero"
    Level := 5
    Health := 100.0
}

# 不允许使用尾随逗号
Config := game_config{
    MaxPlayers := 100,
    EnablePvP := true # , -- 此处不允许使用逗号
}

# 单个字段的点语法（其他字段需要默认值）
Point5 := point . X:=10  # Y 获取默认值 0
Point6 := point . Y:=20  # X 获取默认值 0
```
### 元组访问

当圆括号与元组表达式后的单个参数一起使用时，可以访问元组元素：

<!--versetest-->
<!-- 15-->
```verse
MyTuple := (10, 20, 30)
FirstElement := MyTuple(0)  # 访问第一个元素
SecondElement := MyTuple(1)  # 访问第二个元素
```
## 类型转换

Verse 具有有限的隐式类型转换。大多数转换必须是显式的：

<!--versetest-->
<!-- 16-->
```verse
# 没有隐式 int 到 float 转换
MyInt:int = 42
# MyFloat:float = MyInt # 错误！
MyFloat:float = MyInt * 1.0  # OK：显式转换

# 没有隐式数字到字符串的转换
Score:int = 100
# Message:string = "分数: " + 分数 # 错误！
Message:string = "Score: {Score}"  # OK：字符串插值
```
当运算符使用混合类型时，适用特定规则：

<!--versetest-->
<!-- 17-->
```verse
# int * 浮点数 -> 浮点数
Result := 5 * 2.0  # 结果是 10.0（浮点数）

# 比较必须是同一类型
if (5 = 5):     # 好的
if (5.0 = 5.0): # 好的
# if (5 = 5.0):   # Fails
```
