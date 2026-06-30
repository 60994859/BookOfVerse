# 表达式

一切都是一种表达。这一设计原则使 Verse 与众不同
来自许多其他语言，其中语句和表达式是
不同的概念。你编写的每一段代码都会产生一个值，
甚至您可能认为纯粹是副作用的构造。这个
创建一个编程模型，可以在其中编写和组合代码
感觉自然且可预测的方式。

## 主要表达式

一切都从基本表达式开始——原子单元
构建了更复杂的表达式。这些包括文字、
标识符、括号表达式和元组结构
提供轻量级数据聚合。

### 基本值

文字是常量值的源代码表示。 
Verse 为其所有原始类型提供文字：整数、浮点数、字符、 
字符串、布尔值和函数。 
每种文字类型都有特定的语法规则，用于确定可以表达哪些值以及如何解释它们。

<!--versetest
point := struct{X:float, Y:float}
Condition:logic = true
-->
<!-- 01 -->
```verse
Result := if (Condition?) then 42 else 3.14  # 整数和浮点文字
array{1, 2, 3}                               # 数组构造中的整数文字
point{X:=0.0, Y:=1.0}                        # 对象构造中的浮点文字
```
#### 整数文字

整数字面量表示整数，可以用两种格式编写：

*十进制表示法*使用标准数字：

<!--versetest-->
<!-- 02 -->
```verse
Count := 42
Negative := -17
Zero := 0
Large := 9223372036854775807                # 最大 64 位有符号整数字面量
```
*十六进制表示法*使用 `0x` 前缀后跟十六进制数字
（0-9、a-f、A-F）：

<!--versetest-->
<!-- 03 -->
```verse
Byte := 0xFF
Address := 0x1F4A
LowercaseHex := 0xabcdef
UppercaseHex := 0xABCDEF
```
整数文字必须位于 64 位有符号整数范围内
（`-9223372036854775808` 至 `9223372036854775807`）。在运行时，
整数值是任意精度并且可以增长超过该值
可以写成文字。但是，超过 64 位的整数
支持有限（例如，不能用于字符串插值
或坚持）。

#### 浮点文字

浮点文字表示十进制数，它们必须包含
小数点，在某些情况下为 `f64` 后缀。

<!--versetest-->
<!-- 04 -->
```verse
Pi := 3.14159
Half := 0.5
Explicit := 12.34f64    # 显式位深度后缀
```
科学记数法用于使用指数表示非常大或非常小的数字：

<!--versetest-->
<!-- 05 -->
```verse
Large := 1.0e10         # 10,000,000,000（符号可选）
Small := 1.0e-5         # 0.00001
WithSign := 2.5e+3      # 2,500（明确+符号）
Compact := 1.5e2        # 150（无符号默认为+）
```
一些规则：

- 必须有小数点：`1.0` 有效，`1` 为整数
- 最后没有数字的小数点无效：`1.` 是语法错误
- 所有浮点数均为 64 位（IEEE 754 双精度）； `f64` 后缀是可选的
- 一元运算符与整数一样工作：`-1.0`、`+1.0`

**上溢和下溢行为：**

IEEE 754 双精度范围之外的浮点文字会产生
**编译时错误**：

<!--versetest-->
<!-- 06 -->
```verse
#TooBig := 1.7976931348623159e+308    # Compile error: literal overflow
Maximum := 1.7976931348623158e+308    # OK：最大有限浮点数
```
但是，**运行时**浮点算术遵循标准 IEEE 754 语义：

<!--versetest-->
<!-- 666 -->
```verse
# 运行时溢出产生无穷大
Large := 1.0e308
Overflow := Large * 10.0    # 溢出产生无穷大

# 除以零产生无穷大
PosInf := 1.0 / 0.0
NegInf := -1.0 / 0.0

# 下溢产生非规范化数字或零
Small := 1.0e-320
Smaller := Small / 1.0e10   # 优雅地下溢
```
会产生 NaN 的运算（例如 `0.0 / 0.0` 或 `Inf - Inf`）
导致运行时错误而不是产生 NaN 值。

#### 字符文字

字符文字代表各个文本单元。 Verse 有两种具有不同字面语法的字符类型：

`char` 文字表示 UTF-8 代码单元（单字节，0-255）：

<!--versetest-->
<!-- 07 -->
```verse
LetterA := 'a'          # 可打印 ASCII 字符
Space := ' '
Tab := '\t'             # 转义序列
Hex := 0o61             # 八睡表示法：0oXX（十睡 97 = 'a'）
```
`char32` 文字表示 Unicode 代码点：

<!--versetest-->
<!-- 08 -->
```verse
Emoji := '😀'           # 非 ASCII 自动为 char32
Accented := 'é'
ChineseChar := '好'
HexUnicode := 0u1f600   # Unicode表示法：0uXXXXX (😀)
```
从文字进行类型推断：

- ASCII 字符（`U+0000` 到 `U+007F`）：`'a'` 的类型为 `char`
- 非 ASCII 字符：`'😀'` 的类型为 `char32`
- `char` 和 `char32` 之间没有隐式转换

转义序列适用于 `char` 和字符串：

|转义符|意义|代码点 |
|--------|---------|------------|
| `\t` |制表符| U+0009 |
| `\n` |换行 | U+000A |
| `\r` |回车| U+000D |
| `\"` |双引号 | U+0022 |
| `\'` |单引号 | U+0027 |
| `\\` |反斜杠| U+005C |
| `\{` |左大括号（字符串插值）| U+007B |
| `\}` |右大括号（字符串插值）| U+007D |
| `\<` |小于| U+003C |
| `\>` |大于| U+003E |
| `\&` | & 符号 | U+0026 |
| `\#` |哈希 | U+0023 |
| `\~` |波形符| U+007E |

八进制与 Unicode 表示法的工作原理如下：

- `0oXX` 表示 `char`（两个八进制数字，`0o00` 到 `0off`）
- `0uXXXXX` 表示 `char32`（最多 6 个十六进制数字，`0u00000` 至 `0u10ffff`）

字符文字不能为空或包含多个字符。

#### 字符串文字

字符串文字表示文本序列并支持嵌入表达式的插值。基本字符串使用双引号：

<!--versetest-->
<!-- 09 -->
```verse
Greeting := "Hello, World!"
Empty := ""
WithEscapes := "Line 1\nLine 2\tTabbed"
```
字符串插值使用大括号嵌入表达式：

<!--versetest
Format(D:float, ?Decimals:int):string=""
-->
<!-- 10 -->
```verse
Name := "Alice"
Age := 30

# 简单插值
Message := "Hello, {Name}!"                      # “你好，爱丽丝！”

# 表达式插值
Info := "Age next year: {Age + 1}"               # “明年年龄：31”

# 函数调用
Score := 100
Text := "Score: {ToString(Score)}"               # “得分：100”

# 带命名参数的函数调用
Distance := 5.5
Formatted := "Distance: {Format(Distance, ?Decimals:=2)}"
```
多行字符串可以使用插值大括号来跨越多行以进行延续：

<!--versetest-->
<!-- 11 -->
```verse
LongMessage := "This is a multi-line {
}string that continues across {
}multiple lines."
# 结果：“这是一个连续多行的多行字符串。”

OtherMessage := "Another message{
}    with some empty{
}    spaces."
# Result := "Another message    with some empty    spaces."
```
空插值将被忽略：

<!--versetest-->
<!-- 12 -->
```verse
Text1 := "ab{}cd"        # 与“abcd”相同
Text2 := "ab{
}cd"                    # 与 "abcd" 相同（换行符被忽略）
```
特别规则：

- 大括号必须转义：`"\{ \}"` 用于文字大括号
- `string` 是 `[]char`（UTF-8 代码单元数组）的别名
- 字符串是 UTF-8 字节序列，而不是 Unicode 字符
- `"José".Length = 5`（5 个字节，不是 4 个字符 - é 需要 2 个字节）

字符串数组等价：

<!--versetest-->
<!-- 13 -->
```verse
Test1 := logic{"abc" = array{'a', 'b', 'c'}}    # 真实
Test2 := logic{"" = array{}}                    # 真实
```
字符串中的注释被删除：

<!--versetest-->
<!-- 14 -->
```verse
Text1 := "abc<#comment#>def"     # 与“abcdef”相同
```
#### 布尔文字

`logic` 类型有两个文字值：

<!--versetest-->
<!-- 15 -->
```verse
IsReady := true
IsComplete := false
```
布尔值与查询运算符 `?` 一起使用或用于比较：

<!--versetest
StartGame():void = {}
ShowResults():void = {}
IsReady:logic = true
IsComplete:logic = false
-->
<!-- 16 -->
```verse
if (IsReady?):
    StartGame()

if (IsComplete = true):
    ShowResults()
```
`logic{}` 表达式从可失败表达式创建布尔值（有关可失败表达式的详细信息，请参阅 [失败](08_failure.md)）：

<!--versetest
Operation()<computes><decides>:void = {}
Optional:?int = option{1}
X:int = 1
Y:int = 1
-->
<!-- 17 -->
```verse
# 将 <decides> 表达式转换为逻辑值
Success := logic{Operation[]}        # 如果成功则为true，如果失败则为false
HasValue := logic{Optional?}         # 如果真有任选价值
IsEqual := logic{X = Y}              # 如果符合则为 true，否则为 false
```
`logic{}` 表达式至少需要表面上的失败可能性。没有 `<decides>` 效果的纯表达式会导致错误：

<!--versetest-->
<!-- 18 -->
```verse
# 错误：逻辑{0}没有决定作用
# 错误：逻辑{}为空
Valid := logic{false?}               # 好吧：假的？可能会失败
```
`logic{}` 中的多个表达式可以用分号或逗号分隔（详细信息请参见[分号与逗号](#semicolons-vs-commas)）：

<!--versetest-->
<!-- 19 -->
```verse
Result1 := logic{true?; true?}       # 分号分隔符
Result2 := logic{true?, true?}       # 逗号分隔符
```
#### 路径文字

路径文字使用分层命名方案来标识模块和包：

<!--NoCompile-->
<!-- 21 -->
```verse
/Verse.org/Verse                    # 标准库路径
/YourGame/Player/Inventory          # 自定义模块路径
/user@example.com/MyModule          # 个人命名空间
```
路径语法遵循特定规则：

- 以 `/` 开头
- 包含标签（字母数字、`.`、`-`）
- 标识符必须以字母或 `_` 开头

路径文字在模块章节中有详细介绍。

### 标识符和引用

标识符用作值的引用，无论它们是常量，
变量、函数或类型。标识符由以下部分组成：

- **第一个字符：** 字母（A-Z、a-z）或下划线 (`_`)
- **后续字符：** 字母、数字 (0-9) 或下划线
- **保留：** 单下划线 `_` 不能用作标识符

标识符区分大小写并且仅使用 ASCII 字符 — Unicode
标识符中不支持字符。

<!--NoCompile-->
<!-- 22 -->
```verse
int               # 引用 int 类型
GetValue          # 对函数的引用
Counter           # 引用变量
my_class          # 引用一个类
_private          # 允许前导下划线
variable123       # 第一个字符后允许的数字

# 无效标识符：
# 123invalid # 不能以数字开头
# my-variable # 允许使用连字符
# 咖啡馆 # 不支持 Unicode
# _ # 单下划线保留
```
该语言在语法上不区分不同类型
标识符（类型、函数、变量）——上下文决定如何
使用每个标识符。

### 括号和分组

括号有双重用途：它们对表达式进行分组以进行控制
评估顺序，并且它们创建元组表达式。带括号的
表达式只是计算其内容的值，允许您
覆盖默认运算符优先级或提高可读性：

<!--versetest
A:int = 1
B:int = 2
C:int = 3
X:int = 5
Y:int = 10
Positive:string = "positive"
Negative:string = "negative"
-->
<!-- 23 -->
```verse
(A + B) * C       # 乘法前的群加法
if (X > 0 and Y > 0) then Positive else Negative
```
### 元组

元组提供了一种将两个或多个值分组的方法，只需很少的时间
仪式。语法区分用于
分组以及通过存在用于元组构造的那些
逗号：

<!--versetest
X:int = 5
Y:int = 10
-->
<!-- 24 -->
```verse
(X, Y)            # 二元元组
(1, "hello", true) # 混合类型元组
```
可以使用带有单个整数参数的函数调用语法来访问元组：

<!--versetest-->
<!-- 25 -->
```verse
point := (10, 20)
x := point(0)     # 访问第一个元素
y := point(1)     # 访问第二个元素
```
元组类型写为：

<!--versetest
GetPoint():tuple(int,int) = (10, 20)
GetData():tuple(int,string,logic) = (42, "hello", true)
<#
-->
<!-- 26 -->
```verse
tuple(int,int)
tuple(int,string,logic)
```
<!-- #> -->

虽然编译器可以接受一元元素的类型，
`tuple(int)`，目前没有语法可以编写一个元素的元组。

## 后缀操作

后缀操作是跟随其操作数的操作，可以是
链在一起。这会创建一个从左到右的阅读顺序
感觉自然并允许直观的构图。

### 成员访问

点运算符提供对对象、模块和对象的成员的访问
其他结构化价值。成员访问表达式的计算结果为
指定成员的值：

<!--NoCompile-->
<!-- 27 -->
```verse
Player.Health           # 访问字段
Config.MaxPlayers       # 访问嵌套值
math.Sqrt(16.0)         # 接入模块功能
Point.X                 # 访问结构体字段
```
<!-- math.Sqrt may not compile ... I don't really care to fix it. -->

成员访问可以链接起来，通过嵌套结构创建路径：

<!--versetest
item := class{Name:string = "Sword"}
inventory := class{Items:[]item = array{item{}}}
player_type := class{Inventory:inventory = inventory{}}
game := class{Players:[]player_type = array{player_type{}}}
M()<decides>:void =
    Game:game = game{}
    Game.Players[0].Inventory.Items[0].Name
<#
-->
<!-- 28 -->
```verse
Game.Players[0].Inventory.Items[0].Name
```
<!-- #> -->

### 计算访问

方括号提供对元素的计算访问，无论是
数组、映射或其他可索引结构。内的表达式
评估括号以确定要访问哪个元素：

<!--versetest
ComputeIndex():int = 0
M()<decides>:void =
    Array:[]int = array{1, 2, 3}
    Map:[string]int = map{"key" => 42}
    Matrix:[][]int = array{array{1, 2}, array{3, 4}}
    Row:int = 0
    Col:int = 1
    Data:[]int = array{10, 20, 30}
    Array[0]
    Map["key"]
    Matrix[Row][Col]
    Data[ComputeIndex()]
<#
-->
<!-- 29 -->
```verse
Array[0]                # 数组索引
Map["key"]              # 映射查找
Matrix[Row][Col]        # 嵌套索引
Data[ComputeIndex()]    # 动态指标计算
```
<!-- #> -->

调用时**需要**方括号语法 `Func[]`
可能会失败的功能（具有 `<decides>` 效果的功能）。常规
括号 `Func()` 用于始终成功的函数。数组
索引还使用 `[]`，因为当索引越界时它可能会失败。
```verse
GetValue()<decides>:int = ...
GetData():int = ...

# 必须使用 [] 来表示可能失败的函数
if (X := GetValue[]):
    Print("Got: {X}")

# 必须使用 () 来实现始终成功的函数
Y := GetData()

# 错误：不能使用 () 来执行可能失败的函数
# Z := GetValue()  # Compile error!
```
### 函数调用

函数调用使用括号和逗号分隔的参数。的
语言将函数调用视为计算结果为的表达式
函数的返回值：

<!--versetest
Sqrt(X:int):float = 4.0
MaxOf(A:int, B:int):int = if (A > B) then A else B
Initialize():void = {}
GetData():int = 42
Transform():int = 10
Process(X:int, Y:int)<decides>:void = {}
M()<decides>:void =
    A:int = 5
    B:int = 10
    Sqrt(16)
    MaxOf(A, B)
    Initialize()
    Process[GetData(), Transform()]
<#
-->
<!-- 30 -->
```verse
Sqrt(16)                        # 单一参数
MaxOf(A, B)                     # 多个参数
Initialize()                    # 无参数
Process[GetData(), Transform()] # 嵌套调用，外部调用可能会失败
```
<!-- #> -->

## 对象构造

对象构造使用独特的大括号语法来指示
创建一个新实例。语法需要显式字段
使用 `:=` 运算符进行初始化：

<!--versetest
point := struct{ X:int, Y:int }
player := struct{Name:string, Level:int, Health:int}
config := struct { MaxPlayers:int, Difficulty:string, EnablePvP:logic }
-->
<!-- 31 -->
```verse
point{X:=10, Y:=20}
player{Name:="Hero", Level:=1, Health:=100}
config{
    MaxPlayers := 16,
    EnablePvP := true,
    Difficulty := "normal"
}
```
使用 `:=` 进行字段初始化强化了这些是
绑定操作——您在构造时将值绑定到字段
时间。对象构造函数可以嵌套，创建复杂的
初始化表达式：

<!--versetest
point:=struct{ X:int, Y:int}
inventory:=struct{Capacity:int}
player:=struct{ Position:point, Inventory:inventory}
config:=struct{Difficulty:string}
game_state:=struct{Player:player, Settings:config}
-->
<!-- 32 -->
```verse
Game := game_state{
    Player := player{
        Position := point{X:=0, Y:=0},
        Inventory := inventory{Capacity:=20}
    },
    Settings := config{Difficulty:="hard"}
}
```
## 控制流作为表达式

Verse 的显着特征之一是控制流构造
是表达式，而不是陈述。这意味着 if 表达式，
循环和 case 表达式都会产生可用于以下用途的值
更大的表达式。

### 条件表达式

if-then-else 结构是一个计算结果为以下之一的表达式
基于条件的两个值：

<!--versetest
ComputeA():int=1
ComputeB():int=1
X:int = 5
Condition:logic = true
-->
<!-- 33 -->
```verse
Result := if (X > 0) then "positive" else "negative"
Value := if (Condition=true) then ComputeA() else ComputeB()
```
else 子句可以省略，尽管这会影响
表达。 Verse 支持多种语法形式
if 表达式，包括括号条件和缩进
机构：

<!--versetest
Condition:logic = true
Value1:int = 42
Value2:int = 100
-->
<!-- 34 -->
```verse
# 标准形式
if (Condition?) then Value1 else Value2

# 缩进形式
if:
    Condition?
then:
    Value1
else:
    Value2
```
### `for` 表达式

For 表达式迭代集合并生成值。基本的
form 迭代元素：

<!--versetest
Process(Item:int):void={}
Collection:[]int = array{1, 2, 3}
-->
<!-- 35 -->
```verse
for (Item : Collection) { Process(Item) }
```
扩展形式提供对索引和项目的访问——在这种情况下
对于 `Map`，索引不限于整数：

<!--versetest
Collection:[]int = array{1, 2, 3}
-->
<!-- 36 -->
```verse
for (Index -> Item : Collection) {
    Print("Item at {Index} is {Item}")
}
```
由于 for 表达式本身就是表达式，因此它们生成数组
值并与其他表达式组合。的身体
每次成功的迭代都会计算表达式，并且
表达式作为一个整体具有由这些评估确定的值。

### 循环

循环表达式提供无限迭代，一直持续到
由于失败或其他控制流显式终止：

<!--versetest
GetNext():int=1
Done(Value:int)<computes><decides>:void={}
Process(Value:int):void={}
M():void=
    loop {
        Value := GetNext()
        if (Done[Value]) then break
        Process(Value)
    }
<#
-->
<!-- 37 -->
```verse
loop {
    Value := GetNext()
    if (Done[Value]) then break
    Process(Value)
}
```
<!-- #> -->

为了清楚起见，循环构造可以使用缩进语法。

循环表达式生成 `true` 类型的值（
Verse 类型系统中的顶级类型），无论出现在什么表达式中
它的身体。该值目前对于实际目的没有用处 - 您
通常使用循环是因为其副作用而不是返回值。
```verse
Result := loop:
    ProcessData()
    if (ShouldStop[]):
        break
# 结果的类型为“true”（并返回“true”）
```
### `case` 表达式

Case 表达式提供基于值匹配的多路分支：

<!--versetest
color := enum:
    Red
    Yellow
    Green
    Other
Color:color = color.Red
-->
<!-- 38 -->
```verse
Description := case(Color) {
    color.Red => "Danger",
    color.Yellow => "Warning",
    color.Green => "Safe",
    _ => "Unknown"
}
```
`_` 模式充当包罗万象的角色，确保 case 表达式是
详尽无遗。 Case 表达式的计算结果为匹配的值
分支，使它们对于值计算和控制很有用
流动。

## 二元运算

二进制表达式遵循精心设计的优先级层次结构
平衡数学惯例和编程实用性。

### 赋值和绑定

在最低优先级，赋值运算符将值绑定到
标识符。 `:=` 运算符创建不可变的绑定，而 `set
=` 执行可变赋值：

<!--versetest-->
<!-- 39 -->
```verse
X := 42           # 不可变的绑定
Y := X * 2        # 绑定到计算值
Z := W := 10      # 右关联链
```
赋值运算符是右关联的，这意味着 `a := b := c`
组为 `a := (b := c)`。这允许自然链接
作业，同时保持评估顺序的清晰度。

复合分配提供了常见更新模式的简写：

<!--versetest
F()<transacts>:void=
    var Counter :int = 0
    var Total :int = 0
    Factor:=2
    set Counter += 1
    set Total *= Factor
<#
-->
<!-- 40 -->
```verse
set Counter += 1      # 相当于：设置计数器 = 计数器 + 1
set Total *= Factor   # 相当于：设置总计 = 总计 * 因子
```
<!-- #> -->

复合赋值运算符计算左侧
表达式仅一次**，当表达式有侧面时可观察到
效果：

<!--versetest
assert:
    var TestArray:[]int = array{10, 20, 30, 40, 50}
    var Index:int = 0
    Inc():int =
        set Index += 1
        Index

    # Compound assignment: Inc() called ONCE
    set TestArray[Inc()] += 1

    # Verify: Index = 1 (Inc called once)
    Index = 1
    # TestArray[1] = 20 + 1 = 21
    TestArray[1] = 21
-->
```verse
var Index:int = 0
Inc():int =
    set Index += 1
    Index

# 复合赋值调用Inc()一
set Array[Inc()] += 1
# 结果：数组[1] = 数组[1] + 1

# 扩展形式将调用 Inc() 两次
# set Array[Inc()] = Array[Inc()] + 1
# 结果：Array[1] = Array[2] + 1（不同！）
```
在复合赋值 `set Array[Inc()] += 1` 中，函数 `Inc()`
调用一次以确定索引，然后读取该位置，
递增并存储回来。

### 范围表达式

范围运算符 (`..`) 创建迭代的整数范围
`for` 循环。范围**包含两端**并且只能出现
直接在 for 循环迭代子句中：

<!--versetest
End()<computes>:int=10
Count:int=10
Start:int=1
Process(I:int):void={}
F():void=
    for (I := 1..10):
        for (J := I..(I+10)):
            for (K:= J..End()) {}
<#
-->
<!-- 41 -->
```verse
1..10             # 范围从 1 到 10（含）
Start..End        # 变量定义范围
for (I := 0..Count):  # Must use := syntax, not :
    Process(I)
```
<!-- #> -->

范围不是一流的值。它们不能存储在变量中
或在 `for` 循环迭代子句之外使用。请参阅[范围
操作员限制](07_control.md#for-expressions)
部分了解详细信息。

### 逻辑运算

逻辑运算符将布尔值与短路结合起来
评价。他们的结果要么成功，要么失败。Verse用途
关键字运算符（`and`、`or`、`not`）而不是符号，改进
可读性：

<!--versetest
ProcessQuadrant()<computes>:void = {}
Validated:logic= true
UseDefault()<computes><decides>:void = {}
IsReady()<computes><decides>:void = {}
Wait()<computes>:void = {}
M()<transacts>:void =
    X:int = 5
    Y:int = 10
    if (X > 0 and Y > 0) then ProcessQuadrant()
    Result := logic{Validated? or UseDefault[]}
    if (not IsReady[]) then Wait()
<#
-->
<!-- 42 -->
```verse
if (X > 0 and Y > 0) then ProcessQuadrant()
Result := logic{Validated? or UseDefault[]}
if (not IsReady[]) then Wait()
```
<!-- #> -->

该优先级确保 `and` 比 `or` 绑定更紧密，匹配
数理逻辑约定，`logic{}` 表达式转成功
或失败的值：

<!--NoCompile-->
<!-- 43 -->
```verse
# 计算为：（ExpA 和 ExpB）或（ExpC 和 ExpD）
Condition := logic{ExpA and ExpB or ExpC and ExpD}
```
**重要提示：** 变量绑定不会逃避逻辑运算。
当您在 `and`、`or` 或 `not` 表达式中使用 `:=` 时，这些
绑定仅针对短路控制流进行评估，并且**不**
之后可访问：

<!--NoCompile-->
<!-- 998 -->
```verse
Arr:[]int = array{10, 20}

# 错误：逻辑运算中的绑定不可访问
if ((X := Arr[0]) and (Y := Arr[1])):
    # X 和 Y 未绑定在这里 - 这将导致编译错误！
    Z := X + Y

# 如果绑定有效则很简单
if (X := Arr[0]):
    # 好的：X 可以在这里访问
    Y := X + 1
```
### 比较操作

比较运算符要么成功，要么失败，并且可以链接起来
用于范围检查：

<!--versetest
InRange():void={}
Value:int = 50
X:int = 75
Minimum:int = 0
Maximum:int = 100
A:int = 5
B:int = 10
-->
<!-- 44 -->
```verse
if (0 <= Value <= 100) then InRange()
IsValid := logic{X > Minimum and X < Maximum}
Same := logic{A = B}
Different := logic{A <> B}
```
所有比较运算符具有相同的优先级并进行评估
**从左到右**。至关重要的是，*比较运算符返回其左侧
比较成功时操作数*，并且*比较链有特殊
检查所有相邻对的语法*。

<!--versetest
assert:
    X := 0 < 10
    X = 0  # Returns left operand (0)

    Value:int = 50
    Result := 0 <= Value <= 100
    Result = 0  # Chain returns leftmost operand (0)

    # Chain checks BOTH comparisons
    Value2:int = 75
    not(10 <= Value2 <= 50)  # Fails because 75 > 50
<#
-->
<!-- 999 -->
```verse
X := 0 < 10
# X 等于 0（左操作数）

0 <= Value <= 100
# 检查两者的特殊链语法：
#   - 0 <= 值（下限）
#   - 值 <= 100（上限）
# 如果两者都成功则返回 0（最左边的操作数）
```
<!-- #> -->

比较链 `A <= B <= C` **不**评估为 `(A <= B) <= C`。
相反，它是检查 `A <= B` **和** `B <= C` 的特殊语法，而
成功时返回最左边的操作数 (`A`)。这使得自然
范围的数学符号，无需 `and` 运算符。

### 算术运算

算术运算遵循标准数学优先级，
乘法和除法的结合比加法和除法更紧密
减法：

<!--versetest
A:int = 1
B:int = 2
C:int = 3
-->
<!-- 45 -->
```verse
Result := A + B * C      # 先乘法
Average := (A + B) / 2   # 括号优先级优先
```
整数除以零失败并产生 `<decides>` 效果。
当除以整数时，如果 `Y` 是 `0`，`X / Y` 可能会失败，允许您处理
这种情况安全：

<!--versetest
X:int = 10
Y:int = 0
assert:
    not(Result := X / Y)
-->
<!-- 997 -->
```verse
if (Result := X / Y):
    Print("Division succeeded")
else:
    Print("Cannot divide by zero")
```
浮点数除以零不会失败；它返回无穷大
IEEE 754 浮点语义。

一元运算符在算术运算中具有最高优先级：

<!--versetest
Flag:logic = true
Value:int = 1
X:int = 1
Y:int = 2
-->
<!-- 46 -->
```verse
Negative := -Value
Inverted := logic{not Flag=true}
Result := -X * Y    # 一元减法仅适用于 x
```
## `set` 表达式

虽然 Verse 强调不变性，但有时实用的编程
需要突变。集合表达式提供变量的变异和
字段：

<!--versetest
c := class { var Field:int = 0 }
GetObj()<transacts>:c = c{}
GetArr()<transacts>:[]int = array{1}
GetMap()<transacts>:[string]string = map{ "hi" => "hp" }
Element:int = 5
Value:int = 100
Index:int = 0
Key:string = "key"
MappedValue:string = "value"
assert:
    var X:int = 0
    var Obj:c = GetObj()
    var Arr:[]int = GetArr()
    var Map:[string]string = GetMap()

    set X = 10
    set Obj.Field = Value
    set Arr[Index] = Element
    set Map[Key] = MappedValue
<#
-->
<!-- 47 -->
```verse
set X = 10                    # 变量赋值
set Obj.Field = Value         # 现场作业
set Arr[Index] = Element      # 数组元素赋值
set Map[Key] = MappedValue    # 映射条目分配
```
<!-- #> -->

集合表达式本身就是**返回值的表达式
分配**（右侧）。例如，`set Obj.Field = Value`
返回 `Value`，而不是 `Obj`。这允许链接分配：
```verse
set Y = set X = 5  # X和Y都变成5
```
尽管集合表达式有一个值，但它们通常用于其侧面
影响。左侧必须是有效的 LValue——可以是
分配给.

支持复杂的左值，允许在数据结构深处进行更新：

<!--versetest
item := class{Name:string = "Item"}
inventory := class{var Items:[]item = array{item{}}}
player := class{var Inventory:inventory = inventory{}}
game := class{var Players:[]player = array{player{}}}
M()<transacts><decides>:void =
    Game:game = game{}
    CurrentPlayer:int = 0
    Slot:int = 0
    NewItem:item = item{}
    set Game.Players[CurrentPlayer].Inventory.Items[Slot] = NewItem
<#
-->
<!-- 48 -->
```verse
set Game.Players[CurrentPlayer].Inventory.Items[Slot] = NewItem
```
<!-- #> -->

<a id="semicolons-vs-commas"></a>
## 分号与逗号

Verse 在各种上下文中使用分号和逗号作为分隔符，
但它们在大多数情况下具有根本不同的语义
情况。了解每种方法何时合适对于
写出正确的Verse代码。

**分号**（括号内）创建*序列* - 它们按顺序计算表达式并返回最后一个表达式的值：

<!--versetest
assert:
    Result := (1; 2; 3)
    Result = 3
-->
<!-- 49 -->
```verse
Result := (1; 2; 3)     # 评估 1，然后评估 2，然后评估 3；返回 3
# 注意：括号为必填项
# Result := 1; 2         # ERROR: Not valid without parentheses
```
**逗号**（括号内）创建*元组* - 它们将多个值分组为单个复合值：

<!--versetest-->
<!-- 50 -->
```verse
Result := (1, 2, 3)     # 创建一个包含三个元素的元组
# 结果 = (1, 2, 3) （类型：tuple(int, int, int)）
# 注意：括号为必填项
# Result := 1, 2         # ERROR: Not valid without parentheses
```
### 特定于上下文的行为

在表达式上下文中（如赋值），分号和逗号需要
括号来创建序列和元组。当
比较括号表达式：

<!--versetest-->
<!-- 51 -->
```verse
# 分号：序列（返回最后一个值）
X := (0; 1)              # X = 1，类型为int

# 逗号：元组（组值）
Y := (0, 1)              # Y = (0, 1)，类型为 tuple(int, int)
```
这也适用于函数返回值：

<!--versetest-->
<!-- 52 -->
```verse
GetInt():int = (1.0; 2)                    # 返回 2（整数）
GetTuple():tuple(float, int) = (1.0, 2)    # Returns (1.0, 2)
```
参数位置中的分号创建一个执行的 * 序列
在调用*之前，仅将最后一个值作为参数传递：

<!--versetest
Process(X:int):void={}
LogEvent(S:string):int=1
-->
<!-- 53 -->
```verse
# 分号执行副作用，然后传递最后一个值
Process(LogEvent("called"); 42)   # 记录“called”，然后调用Process(42)

# 相当于：
LogEvent("called")
Process(42)
```
此模式会在参数位置产生副作用：

<!--versetest
MultiplyByTen(X:int):int = X * 10
-->
<!-- 54 -->
```verse
Result := MultiplyByTen(2; 3)     # 计算2（丢弃它），调用Multiply(3)
Result = 30
```
逗号以标准方式分隔不同的参数：

<!--versetest
Add(A:int, B:int):int = A + B
-->
<!-- 55 -->
```verse
Sum := Add(10, 20)                # 两个不同的论点
Sum = 30
```
参数列表中*不允许*使用分号 - 您必须使用逗号：

<!--versetest
assert_semantic_error(3540):
    InvalidFunc(A:int; B:int):void = {}
-->
<!-- 56 -->
```verse
# 有效：逗号分隔的参数
ValidFunc(A:int, B:int):void = {}

# 无效：参数中的分号
# InvalidFunc(A:int; B:int):void = {}
```
### 在特定范围内

在块表达式（大括号）中，分号和逗号可以互换作为定义之间的分隔符：

<!--versetest-->
<!-- 57 -->
```verse
# 在块作用域中，所有三个分隔符都起作用：
block:
    X:int = 0; Y:int = 0      # 分号分隔符

block:
    X:int = 0, Y:int = 0      # 逗号分隔符

block:
    X:int = 0                 # 换行分隔符（最常见）
    Y:int = 0
```
在 `logic{}` 构造函数中 - 分号和逗号都可以使用，但是使用
基于构造行为的不同语义：

<!--versetest-->
<!-- 58 -->
```verse
# 两者都计算所有表达式并返回逻辑值
Result1 := logic{true?; true?}    # 查询顺序
Result2 := logic{true?, true?}    # 也有效
```
在 `option{}` 构造函数中 - 遵循标准序列与元组规则：

<!--versetest-->
<!-- 59 -->
```verse
# 分号：序列，包含最后一个值
Option1 := option{1; 2}?          # 2

# 逗号：元组，包裹元组
Option2 := option{1, 2}?          # (1, 2)
```
在 `for` 表达式中 - 分号通常将迭代子句与过滤条件分隔开，而逗号分隔多个条件：

<!--versetest-->
<!-- 60 -->
```verse
# 分号将迭代与过滤器分开
for (X := 1..3; X <> 2) { X }

# 逗号分隔多个过滤条件
for (X := 1..3, X <> 2) { X }      # 在这种情况下具有相同的含义
```
在`array{}`构造函数中，元素可以用逗号**或**分隔
分号（但不能混合）：

<!--versetest-->
<!-- 61 -->
```verse
CommaArray := array{1, 2, 3}       # 逗号工作
SemiArray := array{1; 2; 3}        # 分号也有效
# MixedArray := array{1, 2; 3}     # ERROR: Cannot mix separators
```
### 换行符作为分隔符

除了分号和逗号之外，**换行符**也可以用作
复合表达式和块中的分隔符。换行符的行为类似于
分号 - 它们创建序列：

<!--versetest-->
<!-- 62 -->
```verse
# 这些是等效的：
Result1 := (1; 2; 3)

Result2 := (
    1
    2
    3
)
# 两者都返回 3
```
## 复合表达式和块表达式

复合表达式，用大括号分隔，将多个表达式分组
到单个表达式中。复合表达式的值为
其最后一个子表达式的值：

<!--versetest
ComputeIntermediate():int=3
CalculateAdjustment(o:int):int=3
-->
<!-- 63 -->
```verse
Result := {
    Temp := ComputeIntermediate()
    Adjustment := CalculateAdjustment(Temp)
    Temp + Adjustment
}
```
复合表达式为变量创建新的作用域，允许本地绑定不影响封闭的作用域：

<!--versetest-->
<!-- 64 -->
```verse
block:
    X := 10    # 本地于该块
    Y := 20
    X + Y
               # X 和 Y 不再可访问
```
复合内的表达式可以用分号、逗号分隔，
或换行符。分号和换行符创建序列（返回
最后一个值），而逗号创建元组。请参阅[分号与
逗号](#semicolons-vs-commas) 表示完整
规则：

<!--versetest
A:int = 1
B:int = 2
C:int = 3
M():void =
    X := { A; B; C }
    Y := { A, B, C }
    Z := {
        A
        B
        C
    }
<#
-->
<!-- 65 -->
```verse
{ A; B; C }           # 分号分隔（返回 C）
{ A, B, C }           # 逗号分隔（返回元组 (A, B, C)）
{                     # 换行符分隔（返回 C）
    A
    B
    C
}
```
<!-- #> -->

## 数组表达式

数组表达式使用 `array` 关键字创建数组值
后面是大括号中的元素：

<!--versetest-->
<!-- 66 -->
```verse
NumArray := array{1, 2, 3, 4, 5}
Empty := array{}
Mixed := array{1, "two", 3.0}  # 如果允许，混合类型
```
为了清楚起见，还可以使用缩进语法构造数组
更长的列表：

<!--versetest-->
<!-- 67 -->
```verse
Colors := array:
    "red"
    "green"
    "blue"
    "yellow"
```
