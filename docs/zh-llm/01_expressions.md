# 表达式

一切都是表达式。这一设计原则将 Verse 与许多其他将语句和表达式视为不同概念的语言区分开来。你编写的每一段代码都会产生一个值，即使是你可能认为纯粹是副作用的构造也是如此。这创造了一种编程模型，使代码能够以自然且可预测的方式进行组合和结合。

## 基本表达式

一切从基本表达式开始——它们是构建更复杂表达式的基本单元。这些包括字面量、标识符、带括号的表达式，以及提供轻量数据聚合的元组构造。

### 基本值

字面量是常量值的源代码表示形式。Verse 为其所有基本类型提供了字面量：整数、浮点数、字符、字符串、布尔值和函数。每种字面量类型都有特定的语法规则，决定了可以表达哪些值以及如何解释它们。

<!--versetest
point := struct{X:float, Y:float}
Condition:logic = true
-->
<!-- 01 -->
```verse
Result := if (Condition?) then 42 else 3.14  # Integer and float literals
array{1, 2, 3}                               # Integer literals in array construction
point{X:=0.0, Y:=1.0}                        # Float literals in object construction
```

#### 整数字面量

整数字面量表示整数，可以用两种格式书写：

*十进制表示法*使用标准数字：

<!--versetest-->
<!-- 02 -->
```verse
Count := 42
Negative := -17
Zero := 0
Large := 9223372036854775807                # Maximum 64-bit signed integer literals
```

*十六进制表示法*使用 `0x` 前缀后跟十六进制数字（0-9, a-f, A-F）：

<!--versetest-->
<!-- 03 -->
```verse
Byte := 0xFF
Address := 0x1F4A
LowercaseHex := 0xabcdef
UppercaseHex := 0xABCDEF
```

整数字面量必须适合 64 位有符号整数范围（`-9223372036854775808` 到 `9223372036854775807`）。在运行时，整数值具有任意精度，可以增长到超过可以作为字面量书写的值。然而，超过 64 位的整数支持有限（例如，不能在字符串插值中使用或持久化）。

#### 浮点数字面量

浮点数字面量表示十进制数，它们必须包含小数点，在某些情况下还需要 `f64` 后缀。

<!--versetest-->
<!-- 04 -->
```verse
Pi := 3.14159
Half := 0.5
Explicit := 12.34f64    # Explicit bit-depth suffix
```

科学计数法用于表示非常大或非常小的数字，使用指数形式：

<!--versetest-->
<!-- 05 -->
```verse
Large := 1.0e10         # 10,000,000,000 (sign optional)
Small := 1.0e-5         # 0.00001
WithSign := 2.5e+3      # 2,500 (explicit + sign)
Compact := 1.5e2        # 150 (no sign defaults to +)
```

一些规则：

- 必须包含小数点：`1.0` 是有效的，`1` 是整数
- 末尾小数点后无数字是无效的：`1.` 是语法错误
- 所有浮点数都是 64 位（IEEE 754 双精度）；`f64` 后缀是可选的
- 一元运算符的工作方式与整数相同：`-1.0`，`+1.0`

**溢出与下溢行为：**

超出 IEEE 754 双精度范围的浮点数字面量会产生**编译时错误**：

<!--versetest-->
<!-- 06 -->
```verse
#TooBig := 1.7976931348623159e+308    # Compile error: literal overflow
Maximum := 1.7976931348623158e+308    # OK: Maximum finite float
```

然而，**运行时**浮点数算术遵循标准 IEEE 754 语义：

<!--versetest-->
<!-- 666 -->
```verse
# Runtime overflow produces infinity
Large := 1.0e308
Overflow := Large * 10.0    # Overflow produces infinity

# Division by zero produces infinity
PosInf := 1.0 / 0.0
NegInf := -1.0 / 0.0

# Underflow produces denormalized numbers or zero
Small := 1.0e-320
Smaller := Small / 1.0e10   # Underflows gracefully
```

会产生 NaN（如 `0.0 / 0.0` 或 `Inf - Inf`）的运算会导致运行时错误，而不是产生 NaN 值。

#### 字符字面量

字符字面量表示单个文本单元。Verse 有两种字符类型，具有不同的字面量语法：

`char` 字面量表示 UTF-8 编码单元（单字节，0-255）：

<!--versetest-->
<!-- 07 -->
```verse
LetterA := 'a'          # Printable ASCII character
Space := ' '
Tab := '\t'             # Escape sequence
Hex := 0o61             # Hex notation: 0oXX (97 decimal = 'a')
```

`char32` 字面量表示 Unicode 码点：

<!--versetest-->
<!-- 08 -->
```verse
Emoji := '😀'           # Non-ASCII automatically char32
Accented := 'é'
ChineseChar := '好'
HexUnicode := 0u1f600   # Hex notation: 0uXXXXX (😀)
```

根据字面量的类型推断：

- ASCII 字符（`U+0000` 到 `U+007F`）：`'a'` 的类型为 `char`
- 非 ASCII 字符：`'😀'` 的类型为 `char32`
- `char` 和 `char32` 之间没有隐式转换

转义序列在 `char` 和字符串中均可使用：

| 转义序列 | 含义 | 码点 |
|--------|---------|-----------|
| `\t`   | 制表符 | U+0009 |
| `\n`   | 换行符 | U+000A |
| `\r`   | 回车符 | U+000D |
| `\"`   | 双引号 | U+0022 |
| `\'`   | 单引号 | U+0027 |
| `\\`   | 反斜杠 | U+005C |
| `\{`   | 左大括号（字符串插值） | U+007B |
| `\}`   | 右大括号（字符串插值） | U+007D |
| `\<`   | 小于号 | U+003C |
| `\>`   | 大于号 | U+003E |
| `\&`   | & 符号 | U+0026 |
| `\#`   | 井号 | U+0023 |
| `\~`   | 波浪号 | U+007E |

十六进制表示法的用法如下：

- `0oXX` 用于 `char`（两位十六进制数字，`0o00` 到 `0off`）
- `0uXXXXX` 用于 `char32`（最多六位十六进制数字，`0u00000` 到 `0u10ffff`）

字符字面量不能为空或包含多个字符。

#### 字符串字面量

字符串字面量表示文本序列，并支持用于嵌入表达式的插值。基本字符串使用双引号：

<!--versetest-->
<!-- 09 -->
```verse
Greeting := "Hello, World!"
Empty := ""
WithEscapes := "Line 1\nLine 2\tTabbed"
```

字符串插值使用花括号嵌入表达式：

<!--versetest
Format(D:float, ?Decimals:int):string=""
-->
<!-- 10 -->
```verse
Name := "Alice"
Age := 30

# Simple interpolation
Message := "Hello, {Name}!"                      # "Hello, Alice!"

# Expression interpolation
Info := "Age next year: {Age + 1}"               # "Age next year: 31"

# Function calls
Score := 100
Text := "Score: {ToString(Score)}"               # "Score: 100"

# Function calls with named arguments
Distance := 5.5
Formatted := "Distance: {Format(Distance, ?Decimals:=2)}"
```

多行字符串可以使用插值大括号实现跨行连续：

<!--versetest-->
<!-- 11 -->
```verse
LongMessage := "This is a multi-line {
}string that continues across {
}multiple lines."
# Result: "This is a multi-line string that continues across multiple lines."

OtherMessage := "Another message{
}    with some empty{
}    spaces."
# Result := "Another message    with some empty    spaces."
```

空的插值内容将被忽略：

<!--versetest-->
<!-- 12 -->
```verse
Text1 := "ab{}cd"        # Same as "abcd"
Text2 := "ab{
}cd"                    # Same as "abcd" (newline ignored)
```

特殊规则：

- 花括号必须转义：`"\{ \}"` 表示字面花括号
- `string` 是 `[]char`（UTF-8 编码单元数组）的别名
- 字符串是 UTF-8 字节序列，而非 Unicode 字符
- `"José".Length = 5`（5 个字节，而非 4 个字符——é 占 2 个字节）

字符串与数组的等价性：

<!--versetest-->
<!-- 13 -->
```verse
Test1 := logic{"abc" = array{'a', 'b', 'c'}}    # True
Test2 := logic{"" = array{}}                    # True
```

字符串中的注释会被移除：

<!--versetest-->
<!-- 14 -->
```verse
Text1 := "abc<#comment#>def"     # Same as "abcdef"
```

#### 布尔字面量

`logic` 类型有两个字面量值：

<!--versetest-->
<!-- 15 -->
```verse
IsReady := true
IsComplete := false
```

布尔值与查询运算符 `?` 或比较运算一起使用：

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


`logic{}` 表达式从可失败表达式创建布尔值（关于可失败表达式的详细信息，请参见[失败](08_failure.md)）：

<!--versetest
Operation()<computes><decides>:void = {}
Optional:?int = option{1}
X:int = 1
Y:int = 1
-->
<!-- 17 -->
```verse
# Converts <decides> expression to logic value
Success := logic{Operation[]}        # true if succeeds, false if fails
HasValue := logic{Optional?}         # true if optional has value
IsEqual := logic{X = Y}              # true if equal, false otherwise
```

`logic{}` 表达式至少需要存在表面上的失败可能性。没有 `<decides>` 效果的纯表达式会导致错误：

<!--versetest-->
<!-- 18 -->
```verse
# ERROR: logic{0} has no decides effect
# ERROR: logic{} is empty
Valid := logic{false?}               # OK: false? can fail
```

`logic{}` 内的多个表达式可以用分号或逗号分隔（详见[分号与逗号](#semicolons-vs-commas)）：

<!--versetest-->
<!-- 19 -->
```verse
Result1 := logic{true?; true?}       # Semicolon separator
Result2 := logic{true?, true?}       # Comma separator
```

#### 路径字面量

路径字面量使用分层命名方案标识模块和包：

<!--NoCompile-->
<!-- 21 -->
```verse
/Verse.org/Verse                    # Standard library path
/YourGame/Player/Inventory          # Custom module path
/user@example.com/MyModule          # Personal namespace
```

路径语法遵循特定规则：

- 以 `/` 开头
- 包含标签（字母数字、`.`、`-`）
- 标识符必须以字母或 `_` 开头

路径字面量在模块章节中有详细说明。

### 标识符与引用

标识符用作值的引用，无论是常量、变量、函数还是类型。标识符由以下部分组成：

- **首字符：** 字母（A-Z, a-z）或下划线（`_`）
- **后续字符：** 字母、数字（0-9）或下划线
- **保留：** 单个下划线 `_` 不能用作标识符

标识符区分大小写，且仅使用 ASCII 字符——标识符不支持 Unicode 字符。

<!--NoCompile-->
<!-- 22 -->
```verse
int               # Reference to the int type
GetValue          # Reference to a function
Counter           # Reference to a variable
my_class          # Reference to a class
_private          # Leading underscore allowed
variable123       # Digits allowed after first character

# Invalid identifiers:
# 123invalid      # Cannot start with digit
# my-variable     # Hyphen not allowed
# café            # Unicode not supported
# _               # Single underscore is reserved
```

语言在语法上不区分不同种类的标识符（类型、函数、变量）——上下文决定了每个标识符的用法。

### 括号与分组

括号有双重用途：它们对表达式进行分组以控制求值顺序，以及创建元组表达式。带括号的表达式简单地求值为其内容的值，允许你覆盖默认的运算符优先级或提高可读性：

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
(A + B) * C       # Group addition before multiplication
if (X > 0 and Y > 0) then Positive else Negative
```

### 元组

元组提供了一种将两个或多个值分组在一起的简便方式。语法通过逗号的存在来区分用于分组的括号和用于元组构造的括号：

<!--versetest
X:int = 5
Y:int = 10
-->
<!-- 24 -->
```verse
(X, Y)            # Two-element tuple
(1, "hello", true) # Mixed-type tuple
```

元组可以使用带单个整数参数的函数调用语法进行访问：

<!--versetest-->
<!-- 25 -->
```verse
point := (10, 20)
x := point(0)     # Access first element
y := point(1)     # Access second element
```

元组类型的书写方式：

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

虽然编译器可以接受单元素的类型 `tuple(int)`，但目前没有书写一个元素的元组的语法。

## 后缀运算

后缀运算是跟在操作数之后并且可以链式组合的运算。这创建了一种从左到右的阅读顺序，感觉很自然，并允许直观的组合。

### 成员访问

点运算符提供对对象、模块和其他结构化值的成员的访问。成员访问表达式求值为指定成员的值：

<!--NoCompile-->
<!-- 27 -->
```verse
Player.Health           # Access field
Config.MaxPlayers       # Access nested value
math.Sqrt(16.0)         # Access module function
Point.X                 # Access struct field
```
<!-- math.Sqrt may not compile ... I don't really care to fix it. -->

成员访问可以链式组合，形成通过嵌套结构的路径：

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

方括号提供对元素的计算访问，无论是数组、映射还是其他可索引结构。括号内的表达式被求值以确定要访问哪个元素：

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
Array[0]                # Array indexing
Map["key"]              # Map lookup
Matrix[Row][Col]        # Nested indexing
Data[ComputeIndex()]    # Dynamic index computation
```
<!-- #> -->

方括号语法 `Func[]` **必须**用于调用可能失败的函数（带有 `<decides>` 效果的函数）。常规圆括号 `Func()` 用于总是成功的函数。数组索引也使用 `[]`，因为当索引越界时它可能失败。

```verse
GetValue()<decides>:int = ...
GetData():int = ...

# Must use [] for functions that may fail
if (X := GetValue[]):
    Print("Got: {X}")

# Must use () for functions that always succeed
Y := GetData()

# ERROR: Cannot use () for failable functions
# Z := GetValue()  # Compile error!
```

### 函数调用

函数调用使用圆括号和逗号分隔的参数。语言将函数调用视为求值为函数返回值的表达式：

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
Sqrt(16)                        # Single argument
MaxOf(A, B)                     # Multiple arguments
Initialize()                    # No arguments
Process[GetData(), Transform()] # Nested calls, outer call may fail
```
<!-- #> -->

## 对象构造

对象构造使用独特的花括号语法来表示创建新实例。该语法需要使用 `:=` 运算符进行显式字段初始化：

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

使用 `:=` 进行字段初始化强化了这些是绑定操作这一概念——你正在构造时将值绑定到字段。对象构造函数可以嵌套，创建复杂的初始化表达式：

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

## 作为表达式的控制流

Verse 的一个显著特点是控制流构造是表达式而不是语句。这意味着 if 表达式、循环和 case 表达式都会产生值，可以在更大的表达式中使用。

### 条件

if-then-else 构造是一个表达式，根据条件求值为两个值之一：

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

else 子句可以省略，但这会影响表达式的类型。Verse 支持 if 表达式的多种语法形式，包括带括号的条件和缩进体：

<!--versetest
Condition:logic = true
Value1:int = 42
Value2:int = 100
-->
<!-- 34 -->
```verse
# Standard form
if (Condition?) then Value1 else Value2

# Indented form
if:
    Condition?
then:
    Value1
else:
    Value2
```

### For

For 表达式遍历集合并产生值。基本形式遍历元素：

<!--versetest
Process(Item:int):void={}
Collection:[]int = array{1, 2, 3}
-->
<!-- 35 -->
```verse
for (Item : Collection) { Process(Item) }
```

扩展形式提供对索引和元素的访问——对于 `Map`，索引不限于整数：

<!--versetest
Collection:[]int = array{1, 2, 3}
-->
<!-- 36 -->
```verse
for (Index -> Item : Collection) {
    Print("Item at {Index} is {Item}")
}
```

由于 for 表达式本身就是表达式，它们会产生数组值并与其他表达式组合。for 表达式的体部在每次成功迭代时求值，整个表达式的值由这些求值结果决定。

### 循环

Loop 表达式提供不定迭代，持续执行直到通过失败或其他控制流显式终止：

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

循环构造可以使用缩进语法以提高清晰度。

循环表达式产生的值类型为 `true`（Verse 类型系统中的顶类型），无论其体部中出现什么表达式。这个值目前在实际应用中并无用处——你通常使用循环是为了其副作用而非返回值。

```verse
Result := loop:
    ProcessData()
    if (ShouldStop[]):
        break
# Result has type 'true' (and returns `true`)
```

### Case

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

`_` 模式作为通配符，确保 case 表达式是穷尽的。Case 表达式求值为匹配分支的值，使其既适用于值计算也适用于控制流。

## 二元运算

二元表达式遵循精心设计的优先级层级，在数学惯例与编程实用性之间取得平衡。

### 赋值与绑定

在最低优先级级别，赋值运算符将值绑定到标识符。`:=` 运算符创建不可变绑定，而 `set =` 执行可变赋值：

<!--versetest-->
<!-- 39 -->
```verse
X := 42           # Immutable binding
Y := X * 2        # Binding to computed value
Z := W := 10      # Right-associative chaining
```

赋值运算符是右结合的，这意味着 `a := b := c` 的分组方式为 `a := (b := c)`。这允许在保持求值顺序清晰的同时自然地进行赋值链式组合。

复合赋值提供了常见更新模式的简写形式：

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
set Counter += 1      # Equivalent to: set Counter = Counter + 1
set Total *= Factor   # Equivalent to: set Total = Total * Factor
```
<!-- #> -->

复合赋值运算符对左侧表达式**仅求值一次**，当表达式具有副作用时这一点是可观察的：

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

# Compound assignment calls Inc() one
set Array[Inc()] += 1
# Result: Array[1] = Array[1] + 1

# Expanded form would call Inc() twice
# set Array[Inc()] = Array[Inc()] + 1
# Result: Array[1] = Array[2] + 1  (different!)
```

在复合赋值 `set Array[Inc()] += 1` 中，函数 `Inc()` 被调用一次以确定索引，然后读取该位置、递增并存储回去。

### 范围表达式

范围运算符（`..`）创建整数范围，用于 `for` 循环中的迭代。范围**两端都包含**，并且只能直接出现在 for 循环迭代子句中：

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
1..10             # Range from 1 to 10 (inclusive)
Start..End        # Variable-defined range
for (I := 0..Count):  # Must use := syntax, not :
    Process(I)
```
<!-- #> -->

范围不是一等值。它们不能存储在变量中或在 `for` 循环迭代子句之外使用。详见[范围运算符限制](07_control.md#for-expressions)章节。

### 逻辑运算

逻辑运算符使用短路求值组合布尔值。它们的结果是成功或失败。Verse 使用关键字运算符（`and`、`or`、`not`）而非符号，提高了可读性：

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

优先级确保 `and` 的绑定比 `or` 更紧密，符合数学逻辑惯例，`logic{}` 表达式将成功或失败转换为一个值：

<!--NoCompile-->
<!-- 43 -->
```verse
# Evaluates as: (ExpA and ExpB) or (ExpC and ExpD)
Condition := logic{ExpA and ExpB or ExpC and ExpD}
```

**重要：** 变量绑定不会从逻辑运算中逃逸。当你在 `and`、`or` 或 `not` 表达式中使用 `:=` 时，这些绑定仅在短路控制流中被求值，之后**不可访问**：

<!--NoCompile-->
<!-- 998 -->
```verse
Arr:[]int = array{10, 20}

# ERROR: Bindings in logical operations are NOT accessible
if ((X := Arr[0]) and (Y := Arr[1])):
    # X and Y are not bound here - this will cause a compilation error!
    Z := X + Y

# Simple if binding DOES work
if (X := Arr[0]):
    # OK: X is accessible here
    Y := X + 1
```

### 比较运算

比较运算符也会成功或失败，并且可以链式组合以进行范围检查：

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

所有比较运算符都具有相同的优先级，并且按**从左到右**求值。关键在于，*比较运算符在比较成功时返回其左操作数*，而*比较链具有特殊语法*，检查所有相邻对。

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
# X equals 0 (the left operand)

0 <= Value <= 100
# Special chain syntax that checks BOTH:
#   - 0 <= Value (lower bound)
#   - Value <= 100 (upper bound)
# Returns 0 (leftmost operand) if both succeed
```
<!-- #> -->

比较链 `A <= B <= C` **不是**按 `(A <= B) <= C` 求值的。相反，它是一种特殊语法，同时检查 `A <= B` **和** `B <= C`，并在成功时返回最左边的操作数（`A`）。这使得范围的数学符号表达变得自然，无需使用 `and` 运算符。

### 算术运算

算术运算遵循标准数学优先级，乘法和除法的绑定比加法和减法更紧密：

<!--versetest
A:int = 1
B:int = 2
C:int = 3
-->
<!-- 45 -->
```verse
Result := A + B * C      # Multiplication first
Average := (A + B) / 2   # Parentheses override precedence
```

整数除以零会失败并具有 `<decides>` 效果。在整数除法中，如果 `Y` 为 `0`，`X / Y` 可能失败，允许你安全地处理这种情况：

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

浮点数除以零不会失败；根据 IEEE 754 浮点语义，它返回无穷大。

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
Result := -X * Y    # Unary minus applies to x only
```

## 赋值表达式

虽然 Verse 强调不可变性，但实际编程有时需要可变性。赋值表达式提供对变量和字段的可变赋值：

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
set X = 10                    # Variable assignment
set Obj.Field = Value         # Field assignment
set Arr[Index] = Element      # Array element assignment
set Map[Key] = MappedValue    # Map entry assignment
```
<!-- #> -->

赋值表达式本身就是表达式，**返回被赋值的值**（右侧值）。例如，`set Obj.Field = Value` 返回 `Value`，而不是 `Obj`。这允许链式赋值：

```verse
set Y = set X = 5  # Both X and Y become 5
```

虽然赋值表达式有值，但它们通常用于其副作用。左侧必须是一个有效的 LValue——即可被赋值的内容。

支持复杂的 LValue，允许在深层嵌套的数据结构中进行更新：

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

## 分号与逗号

Verse 在各种上下文中使用分号和逗号作为分隔符，但它们在大多数情况下具有根本不同的语义。理解何时使用每种分隔符对于编写正确的 Verse 代码至关重要。

**分号**（在括号内）创建*序列*——它们按顺序求值表达式并返回最后一个表达式的值：

<!--versetest
assert:
    Result := (1; 2; 3)
    Result = 3
-->
<!-- 49 -->
```verse
Result := (1; 2; 3)     # Evaluates 1, then 2, then 3; returns 3
# Note: Parentheses are required
# Result := 1; 2         # ERROR: Not valid without parentheses
```

**逗号**（在括号内）创建*元组*——它们将多个值分组为一个复合值：

<!--versetest-->
<!-- 50 -->
```verse
Result := (1, 2, 3)     # Creates a tuple of three elements
# Result = (1, 2, 3) (type: tuple(int, int, int))
# Note: Parentheses are required
# Result := 1, 2         # ERROR: Not valid without parentheses
```

### 上下文特定行为

在表达式上下文中（如赋值），分号和逗号需要括号来创建序列和元组。比较带括号的表达式时，区别很明显：

<!--versetest-->
<!-- 51 -->
```verse
# Semicolon: sequence (returns last value)
X := (0; 1)              # X = 1, type is int

# Comma: tuple (groups values)
Y := (0, 1)              # Y = (0, 1), type is tuple(int, int)
```

这同样适用于函数返回值：

<!--versetest-->
<!-- 52 -->
```verse
GetInt():int = (1.0; 2)                    # Returns 2 (int)
GetTuple():tuple(float, int) = (1.0, 2)    # Returns (1.0, 2)
```

在参数位置的分号创建了一个*在调用之前执行的序列*，只有最后一个值作为参数传递：

<!--versetest
Process(X:int):void={}
LogEvent(S:string):int=1
-->
<!-- 53 -->
```verse
# Semicolon executes side effects, then passes last value
Process(LogEvent("called"); 42)   # Logs "called", then calls Process(42)

# Equivalent to:
LogEvent("called")
Process(42)
```

这种模式使得在参数位置产生副作用成为可能：

<!--versetest
MultiplyByTen(X:int):int = X * 10
-->
<!-- 54 -->
```verse
Result := MultiplyByTen(2; 3)     # Evaluates 2 (discards it), calls Multiply(3)
Result = 30
```

逗号以标准方式分隔不同的参数：

<!--versetest
Add(A:int, B:int):int = A + B
-->
<!-- 55 -->
```verse
Sum := Add(10, 20)                # Two separate arguments
Sum = 30
```

分号在参数列表中**不允许**——必须使用逗号：

<!--versetest
assert_semantic_error(3540):
    InvalidFunc(A:int; B:int):void = {}
-->
<!-- 56 -->
```verse
# VALID: Comma-separated parameters
ValidFunc(A:int, B:int):void = {}

# INVALID: Semicolon in parameters
# InvalidFunc(A:int; B:int):void = {}
```

### 特定作用域中的规则

在块表达式（花括号）内，分号和逗号作为定义之间的分隔符可以互换使用：

<!--versetest-->
<!-- 57 -->
```verse
# In block scope, all three separators work:
block:
    X:int = 0; Y:int = 0      # Semicolon separator

block:
    X:int = 0, Y:int = 0      # Comma separator

block:
    X:int = 0                 # Newline separator (most common)
    Y:int = 0
```

在 `logic{}` 构造函数中——分号和逗号都可以使用，但根据构造的行为具有不同的语义：

<!--versetest-->
<!-- 58 -->
```verse
# Both evaluate all expressions and return logic value
Result1 := logic{true?; true?}    # Sequence of queries
Result2 := logic{true?, true?}    # Also valid
```

在 `option{}` 构造函数中——遵循标准的序列与元组规则：

<!--versetest-->
<!-- 59 -->
```verse
# Semicolon: sequence, wraps last value
Option1 := option{1; 2}?          # 2

# Comma: tuple, wraps the tuple
Option2 := option{1, 2}?          # (1, 2)
```

在 `for` 表达式中——分号通常分隔迭代子句与过滤条件，而逗号分隔多个条件：

<!--versetest-->
<!-- 60 -->
```verse
# Semicolon separates iteration from filter
for (X := 1..3; X <> 2) { X }

# Comma separates multiple filter conditions
for (X := 1..3, X <> 2) { X }      # Same meaning in this context
```

在 `array{}` 构造函数中，元素可以用逗号**或**分号分隔（但不能混用）：

<!--versetest-->
<!-- 61 -->
```verse
CommaArray := array{1, 2, 3}       # Commas work
SemiArray := array{1; 2; 3}        # Semicolons also work
# MixedArray := array{1, 2; 3}     # ERROR: Cannot mix separators
```

### 换行符作为分隔符

除了分号和逗号，**换行符**也可以在复合表达式和块中作为分隔符使用。换行符的行为类似于分号——它们创建序列：

<!--versetest-->
<!-- 62 -->
```verse
# These are equivalent:
Result1 := (1; 2; 3)

Result2 := (
    1
    2
    3
)
# Both return 3
```

## 复合表达式与块表达式

复合表达式由花括号分隔，将多个表达式分组为单个表达式。复合表达式的值是其最后一个子表达式的值：

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

复合表达式为变量创建新作用域，允许局部绑定而不影响外围作用域：

<!--versetest-->
<!-- 64 -->
```verse
block:
    X := 10    # Local to this block
    Y := 20
    X + Y
               # X and Y no longer accessible
```

复合中的表达式可以用分号、逗号或换行符分隔。分号和换行符创建序列（返回最后一个值），而逗号创建元组。完整规则请参见[分号与逗号](#semicolons-vs-commas)：

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
{ A; B; C }           # Semicolon separation (returns C)
{ A, B, C }           # Comma separation (returns tuple (A, B, C))
{                     # Newline separation (returns C)
    A
    B
    C
}
```
<!-- #> -->

## 数组表达式

数组表达式使用 `array` 关键字后跟花括号中的元素来创建数组值：

<!--versetest-->
<!-- 66 -->
```verse
NumArray := array{1, 2, 3, 4, 5}
Empty := array{}
Mixed := array{1, "two", 3.0}  # Mixed types if allowed
```

对于较长的列表，数组也可以使用缩进语法以提高清晰度：

<!--versetest-->
<!-- 67 -->
```verse
Colors := array:
    "red"
    "green"
    "blue"
    "yellow"
```
