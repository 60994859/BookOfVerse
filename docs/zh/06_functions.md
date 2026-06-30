# 函数

函数是可重用的代码块，执行操作并生成
基于输入的输出。将它们视为行为的抽象，
就像在餐厅从菜单上点菜一样。当您订购时，
你告诉服务员你想要菜单上的什么，比如
`OrderFood("Ramen")`。你不需要知道厨房是如何准备的
您的菜肴，但您希望在点餐后收到食物。这个
抽象使得函数变得强大——你定义
一次说明并在整个过程中的不同上下文中重复使用它们
代码。

## 参数

函数可以接受任意数量的参数，从根本没有参数到as
根据需要很多。语法遵循简单的模式，其中
每个参数都有一个标识符和类型，以逗号分隔：

<!--versetest-->
<!-- 01-->
```verse
ProcessData(Name:string, Age:int, Score:float):string =
    "{Name} is {Age} years old with a score of {Score}"
```
对于具有许多参数或可选配置的函数，Verse
支持命名参数和默认参数。

### 命名参数

具有默认值的命名参数使函数更加灵活
符合人体工学。它们允许您：

- 按名称而不是位置指定参数
- 为可选参数提供默认值
- 仅使用您需要的参数调用函数
- 添加新的可选参数而不破坏现有代码

命名参数使用 `?` 前缀进行声明，并使用
名称和 `:=` 后跟一个值：

<!--versetest-->
<!-- 02-->
```verse
# 具有命名参数的函数
Greet(?Name:string, ?Greeting:string):string = "{Greeting} {Name}!"

# 使用命名参数的调用
Greet(?Name := "Alice", ?Greeting := "Hello") 
```
具有默认值的命名参数确实是可选的：

<!--versetest-->
<!-- 03-->
```verse
# 具有默认值的命名参数
Log(Message:string, ?Level:int=1, ?Color:string="white"):string =
    "[Level {Level}] {Message} ({Color})"

# 使用所有默认值进行调用
Log("Starting")                          # 返回“[级别 1] 开始（白色）”

# 带一些参数调用
Log("Warning", ?Level:=2)                # 返回“[2 级]警告（白色）”

# 以任意顺序调用参数
Log("Error", ?Color:="red", ?Level:= 3)  # 返回“[级别 3] 错误（红色）”
```
在第一个命名参数之后，所有后续参数也必须命名：

<!--versetest
assert_semantic_error(3629):
    Invalid(?Named:int, Positional:string):void = {}
<#
-->
<!-- 04-->
```verse
# 无效：命名后跟位置
Invalid(?Named:int, Positional:string):void = {}  # 错误
```
<!-- #>-->

当调用带有命名参数的函数时，必须使用
`?Name:=Value` 语法。所有没有默认值的参数都必须指定。
位置参数优先：

<!--versetest
Configure(Required:int, ?Option1:string = "", ?Option2:logic = false):void = {}
<#
-->
<!-- 07-->
```verse
Configure(Required:int, ?Option1:string, ?Option2:logic):void = { }

# 有效
Configure(42, ?Option1:="test", ?Option2:=true)

# 无效：在位置之前命名 arg
Configure(?Option1:="test", 42, ?Option2:=true)  # 错误
```
<!-- #>-->

默认值在函数的定义范围内计算；他们
可以参考：

  - 模块级定义
  - 类或接口成员
  - 早期参数

<!--versetest
ModuleTimeout:int = 30

Connect(?Host:string = "localhost", ?Timeout:int = ModuleTimeout):void = {}

game_config := class:
    DefaultLives:int = 3

    StartGame(?Lives:int = DefaultLives)<transacts>:void = {}

CreateRange(?Start:int = 0, ?End:int = Start + 10):[]int =
    array{Start, End}
<#
-->
<!-- 09-->
```verse
# 模块级定义
ModuleTimeout:int = 30

# 访问模块级定义
Connect(?Host:string, ?Timeout:int = ModuleTimeout):void =...

# 访问成员定义
game_config := class:
    DefaultLives:int = 3

    StartGame(?Lives:int = DefaultLives):void =...

# 访问较早的参数
CreateRange(?Start:int, ?End:int = Start + 10):[]int =...
```
<!-- #>-->

默认值适用于类层次结构中的重写成员：

<!--versetest
base_game := class:
    DefaultSpeed:float = 1.0

    Move(?Speed:float = DefaultSpeed)<transacts>:void = {}

fast_game := class(base_game):
    DefaultSpeed<override>:float = 2.0
<#
-->
<!-- 13-->
```verse
base_game := class:
    DefaultSpeed:float = 1.0

    Move(?Speed:float = DefaultSpeed):void =...
    # 使用当前实例中的DefaultSpeed

fast_game := class(base_game):
    DefaultSpeed<override>:float = 2.0

base_game{}.Move()         # 使用1.0
fast_game{}.Move()         # 使用 2.0（覆盖值）
```
<!-- #>-->

命名参数和默认参数与类型系统交互。  一个
具有默认参数的函数是同一函数的子类型
没有这些参数：

<!--versetest-->
<!-- 14-->
```verse
Process(?Required:int, ?Optional:int = 0):int = Required + Optional

# 可以分配给没有可选参数的类型
F1:type{_(?Required:int):int} = Process
F1(?Required := 5)                          # 返回 5（使用默认值）

# 可以使用可选参数分配给类型
F2:type{_(?Required:int, ?Optional:int):int} = Process
F2(?Required := 5, ?Optional := 3)          # 返回 8

# 甚至可以分配给没有参数的类型（都有默认值）
DefaultAll(?A:int = 1, ?B:int = 2):int = A + B
F3:type{_():int} = DefaultAll
F3()                                        # 返回 3
```
函数类型保留命名参数名称：

<!--versetest-->
<!-- 15-->
```verse
Calculate(?Amount:float, ?Rate:float):float = Amount * Rate

# 有效：姓名匹配
F1:type{_(?Amount:float, ?Rate:float):float} = Calculate

# 无效：名称不同
# F2:type{_(?Value:float, ?Factor:float):float} = 计算 # 错误
```
函数类型不包含默认值：

<!--versetest-->
<!-- 16-->
```verse
F1(?X:int=1):int = X

F2:type{_(?X:int=99):int} = F1    # F1和F2是同一类型
```
命名参数参与函数重载决策：

<!--versetest-->
<!-- 17-->
```verse
Process(Value:int):string = "One parameter"
Process(Value:int, ?Option:string):string = "Two parameters"
Process(Value:int, ?Option1:string, ?Option2:logic):string = "Three parameters"

Process(42)                                        # 调用第一个重载
Process(42, ?Option := "test")                     # 调用第二个重载
Process(42, ?Option1 := "test", ?Option2 := true)  # 调用第三个重载
```
编译器选择与提供的相匹配的重载
论据。命名参数使重载决策更加精确
因为名称必须完全匹配。

命名参数对于*重载独特性*有特定的规则
与位置参数不同。两个函数签名是
如果可以调用它们，则认为**不明确**（无法重载）
具有相同的论点。

**顺序对于命名参数来说并不重要：**命名参数是
按名称匹配，而不是位置匹配，因此重新排序不会创建
独特性：

<!--versetest
assert_semantic_error(3532):
    F(?Y:int, ?X:int):int = X + Y
    F(?X:int, ?Y:int):int = X - Y
<#
-->
<!-- 18-->
```verse
# 不不同 - 相同的参数，不同的顺序
F(?Y:int, ?X:int):int = X + Y
F(?X:int, ?Y:int):int = X - Y  # 错误
```
<!-- #>-->

**默认值不会产生明显性：**存在或不存在
如果参数名称默认值不会使签名不同
是相同的：

<!--versetest
assert_semantic_error(3532):
    F(?X:int=42):int = X
    F(?X:int):int = X
<#
-->
<!-- 19-->
```verse
# 带/不带默认值的相同参数名称
F(?X:int=42):int = X
F(?X:int):int = X  # 错误
```
<!-- #>-->

**全默认规则：** 如果两个重载中的所有参数都有
默认值，签名不明确，因为两者都可以
不带参数调用：

<!--versetest
assert_semantic_error(3532):
    F(?X:int=42):int = X
    F(?Y:int=42):int = Y
<#
-->
<!-- 20-->
```verse
# ERROR 两者都可以称为 F()
# F(?X:int=42):int = X
# F(?Y:int=42):int = Y         # ERROR

# 错误 两者都可以在没有参数的情况下调用
# F(?X:int=42):int = X
# F(?X:float=3.14):float = X  # ERROR
```
<!-- #>-->

**不同的参数名称是不同的：**具有不同参数的函数
命名参数名称可以重载：

<!--versetest-->
<!-- 22-->
```verse
# 有效：不同名称
F(?X:int):int = X
F(?Y:int):int = Y  # OK - 不同的参数名称
```
**命名参数与位置参数是不同的：** 命名参数是
与位置参数不同，即使具有相同的名称和
类型：

<!--versetest-->
<!-- 23-->
```verse
# 有效：命名与位置
F(?X:int):int = X
F(X:int):int = X  # 好的
```
**至少一个必需参数必须不同：** 如果一组
所需（无默认）命名参数不同，重载为
独特：

<!--versetest-->
<!-- 24-->
```verse
# 有效：第一个需要 ?Y，第二个不需要
F(?Y:int, ?X:int=42):int = X
F(?X:int):int = X  # 好的 - 所需的不同参数集
```
**位置参数创建独特性：**不同的位置
参数类型使签名不同，即使命名参数是
相同：

<!--versetest-->
<!-- 25-->
```verse
# 有效：不同的位置参数类型
F(Arg:float, ?X:int):int = X
F(Arg:int, ?X:int):int = X  # 好的
```
**调用的超集：** 如果一个签名可以处理所有调用
另一个可以，它们模糊不清：

<!--versetest
assert_semantic_error(3532):
    F(?Y:int=42, ?X:int=42):int = X
    F(?X:int):int = X
<#
-->
<!-- 26-->
```verse
# 错误 3532：第一个可以处理对第二个的所有调用
# F(?Y:int=42, ?X:int=42):int = X
# F(?X:int):int = X  # ERROR - can call first as F(?X := 10)
```
<!-- #>-->

### 元组作为参数

元组可用于提供位置参数。然而，你
不能将预构造的元组变量与附加命名变量混合
论点：

<!--versetest-->
<!-- 28-->
```verse
Calculate(A:int, B:int, ?C:int = 0):int = A + B + C

# 有效：元组提供位置参数
Args:tuple(int, int) = (1, 2)
Calculate(Args)  # 返回 3

# 有效：直接提供的所有参数
Calculate(1, 2, ?C := 5)  # 返回 8

# 无效：不能将元组变量与命名参数混合
# Calculate(Args, ?C := 5)  # ERROR
```
函数可以直接在参数中解构元组参数
列表，允许您内联提取元组元素，无需手动
索引：

<!--versetest-->
<!-- 29-->
```verse
# 就地解构元组参数
Func(A:int, (B:int, C:int), D:int):int =
    A + B + C + D

Func(1, (2, 3), 4)        # 直接元组文字 - 返回 10
X := (2, 3)
Func(1, X, 4)             # 元组变量 - 返回 10
Y := (1, (2, 3), 4)
Func(Y)                   # 整个参数列表作为元组 - 返回 10
```
参数 `(B:int, C:int)` 解构元组，直接给出
访问 `B` 和 `C`，而不需要 `Tuple(0)` 和 `Tuple(1)`
索引。

元组可以解构到任意深度：

<!--versetest-->
<!-- 30-->
```verse
# 简单嵌套
H(A:int, (B:int, (C:int, D:int)), E:int):int =
    A + B + C + D + E

H(1, (2, (3, 4)), 5)              # 返回 15
T := (2, (3, 4))
H(1, T, 5)                        # 返回 15
T2 := (1, (2, (3, 4)), 5)
H(T2)                             # 返回 15
```
您可以将解构元组参数与常规元组混合使用
未解构的参数：

<!--versetest-->
<!-- 31-->
```verse
# 解构形式 - 直接访问元素
F(A:int, (B:int, C:int), D:int):int =
    A + B + C + D

# 非解构形式 - 使用元组索引
G(A:int, T:tuple(int, int), D:int):int =
    A + T(0) + T(1) + D

# 两者工作原理相同
F(1, (2, 3), 4)  # 返回 10
G(1, (2, 3), 4)  # 返回 10
```
当您需要直接访问个人时，请选择解构形式
元素，并且当您需要将元组作为
整体到其他功能。

元组参数可以包含命名/可选参数，允许
灵活的 API，将结构分解与可选功能相结合
价值观：

<!--versetest-->
<!-- 32-->
```verse
# 嵌套元组内的命名参数
SumValues(A:int, (X:int, (Y:int, ?Z:int = 0))):int =
    A + X + Y + Z

# 可以明确提供 Z
SumValues(1, (2, (3, ?Z := 4)))  # 返回 10

# 可以省略 Z 以使用默认值
SumValues((1, (2, 3)))           # 返回 6
```
一个元组可以包含多个命名参数，它们可以是
以任意顺序指定：

<!--versetest-->
<!-- 33-->
```verse
ProcessData(Base:int, (Items:[]int, ?Scale:int = 1, ?Offset:int = 0)):int =
    if (First := Items[0]):
        First * Scale + Offset + Base
    else:
        Base

Data := array{100, 200}

ProcessData(10, Data)                              # 使用默认值：110
ProcessData(10, (Data, ?Scale := 2))               # 210
ProcessData(10, (Data, ?Offset := 5))              # 115
ProcessData(10, (Data, ?Scale := 2, ?Offset := 5)) # 215
ProcessData(10, (Data, ?Offset := 5, ?Scale := 2)) # 215（顺序无关紧要）
```
当元组参数仅包含命名参数时（无
位置参数），您必须提供一个空元组 `()`，即使
使用所有默认值：

<!--versetest-->
<!-- 34-->
```verse
# 仅具有命名参数的元组
Configure(Base:int, (?Width:int = 10, ?Height:int = 20)):int =
    Base + Width + Height

# 使用所有默认值时必须提供空元组
Configure(5, ())  # 返回 35

# 不能完全省略元组
# Configure(5)  # ERROR - tuple parameter required
```
这是当前实施中的已知限制。当
tuple 至少包含一个位置参数，这个限制
不适用。

### 展平和反展平

Verse 提供元组和多个之间的自动转换
函数调用处的参数，实现灵活的调用
无需显式打包或解包的约定。

*扁平化：*可以调用需要多个参数的函数
与单个元组。在下面，元组 `Args` 是
自动解包到 `Add` 函数的参数中：

<!--versetest-->
<!-- 36-->
```verse
Add(X:int, Y:int):int= X + Y
Args:= (3, 5)
Add(Args)       # 返回 8 - 自动展平的元组
```
*Unflattening：*需要单个元组参数的函数可以是
调用扁平化参数。  通话的各个参数
到 `F` 会自动打包到元组参数中：

<!--versetest-->
<!-- 37-->
```verse
F(P:tuple(int, int)):int = P(0) + P(1)

F(3, 5)  # 返回 8 - args 自动分配到元组中
```
空元组具有相同的展平行为：

<!--versetest-->
<!-- 39-->
```verse
F(X:tuple()):int = 42

F(())   # 显式空元组
F()     # 无参数 - 自动创建空元组
```
**过载限制：** 由于自动展平和
不平坦，您不能定义不明确的重载。如果
你定义了 `F(P:tuple(int, int))`，你不能同时定义 `F(X:int,
Y:int)` because the call `F(3, 5)` 可以匹配任一签名。
同样，`F(P:tuple(int, int))` 和 `F(Xs:[]int)` 也是不明确的
因为数组也可以用相同的语法调用。

### 评估顺序

参数按特定顺序进行评估，以保持可预测的行为：

1. *位置参数*：调用中从左到右
2. *命名参数*：从左到右在调用中遇到
3. *默认值*：省略的参数填写，从左到右
   按参数顺序

如果命名实参的出现顺序与参数不同，则
编译器使用临时变量来保留您的评估顺序
指定：

<!--versetest-->
<!-- 40-->
```verse
Process(A:int, ?B:int, ?C:int, ?D:int):string =
    "{A}, {B}, {C}, {D}"

# 使用重新排序的命名参数进行调用
Process(1, ?D := 4, ?B := 2, ?C := 3)

# 评估顺序：1、4、2、3（如书面所示）
# 但按参数顺序传递给函数：1,2,3,4
```
这确保了参数表达式中的副作用发生在
编写它们的顺序，而不是参数顺序。

## 扩展方法

扩展方法允许您向现有类型添加新方法
而不修改它们的原始定义。这个强大的功能
使您能够扩展 Verse 中的任何类型，包括内置类型，例如
`int`、`string`、数组和映射 — 具有自定义功能，同时
保持不同关注点之间的清晰分离。

扩展方法在以下情况下特别有价值：

- 您想要向内置类型添加特定于域的操作
- 您需要从您无法控制的库中扩展类型
- 您正在构建流畅的或构建器风格的 API
- 您想要将相关功能与类型定义分开组织

扩展方法在扩展类型出现的地方使用特殊语法
在方法名称之前的括号中：

<!--versetest-->
<!-- 41-->
```verse
# 使用自定义方法扩展 int
(Value:int).Double()<computes>:int = Value * 2

# 使用点符号调用扩展方法
X := 5
Y := X.Double()  # 返回 10

# 也可以调用文字
Z := 7.Double()  # 返回 14
```
括号中的类型可以是任何 Verse 类型：基元、元组、
类、接口、数组、映射或结构。

扩展原语：

<!--versetest-->
<!-- 42-->
```verse
(N:int).IsEven()<decides><computes>:void = Mod[N,2] = 0
(S:string).FirstChar()<decides><computes>:char = S[0]

42.IsEven[]           # 成功
"Hello".FirstChar[] = 'H' 
```
扩展元组：

<!--versetest-->
<!-- 43-->
```verse
# 特定元组类型的扩展（注意：Sqrt 是<reads>）
(Point:tuple(int, int)).Distance()<reads>:float =
    Sqrt( (Point(0) * Point(0) + Point(1) * Point(1)) * 1.0)

(3, 4).Distance()  # 返回 5.0
```
扩展元组时，必须指定元组类型
明确（例如，`(Point:tuple(int, int))`）。你不能使用
用于扩展的解构参数语法（例如，`(X:int, Y:int)`）
方法上下文。

空元组 `tuple()` 表示单元类型，可以有
扩展方法：

<!--versetest-->
<!-- 49-->
```verse
(Unit:tuple()).GetMagicNumber():int = 42

().GetMagicNumber()  # 返回 42
```
扩展数组：

<!--versetest-->
<!-- 44-->
```verse
(Vals:[]int).Sum()<transacts>:int =
    var Total:int = 0
    for (N:Vals):
        set Total += N
    Total

array{1, 2, 3, 4, 5}.Sum()  # 返回 15
```
扩展映射：

<!--versetest-->
<!-- 45-->
```verse
(M:[int]string).Keys()<computes>:[]int =
    for (Key->X:M):
        Key

map{1=>"a", 2=>"b", 3=>"c"}.Keys()  # 返回数组{1,2,3}
```
扩展类：

<!--NoCompile-->
<!--246-->
```verse
player := class:
    Name:string
    var Score:int
```
<!--versetest
player := class:
    Name:string
    var Score:int
-->
<!-- 46-->
```verse
# 向现有类添加方法
(P:player).AddScore(Points:int):void =
    set P.Score += Points

Player1 := player{Name := "Alice", Score := 100}
Player1.AddScore(50)  # 分数变成150
```
扩展方法支持所有参数功能，包括命名和
默认参数：


<!--versetest
<#
-->
<!-- 47-->
```verse
#（文本：字符串）.Pad（？左：int = 0，？右：int = 0）：字符串= ...

"Hello".Pad(?Left:=5)               # “你好”
"Hello".Pad(?Right:=5)              # “你好”
"Hello".Pad(?Left:= 2, ?Right:=3)   # “你好”
```
<!-- #>-->

### 重载

您可以定义多个具有相同名称的扩展方法
不同类型：

<!--versetest-->
<!-- 48-->
```verse
# 不同类型的重载扩展方法
(N:int).Format():string = "int:{N}"
(B:logic).Format():string = if (B?) {"logic:true"} else {"logic:false"}

42.Format()      # 返回“整数：42”
true.Format()    # 返回“逻辑：真”
```
编译器根据接收器类型选择适当的重载。

### 规则

**必须调用**：扩展方法不能被引用为
不调用它们的一流值：

<!--versetest-->
<!-- 50-->
```verse
(N:int).Double():int = N * 2

# 有效：调用该方法
X := 5.Double()

# 无效：引用而不调用
# F := 5.Double  # ERROR
```
**与类方法冲突：**扩展方法不能具有
与直接在类或接口中定义的方法具有相同的签名：

<!--versetest
player := class:
    Health():int = 100

<#
-->
<!-- 51-->
```verse
player := class:
    Health():int = 100

# 无效：与类方法冲突
# (P:玩家).Health():int = 50 # 错误
```
<!-- #>-->

这可以防止歧义并确保类方法始终优先。

**范围和可见性：**扩展方法的范围与常规方法一样
功能。它们仅在定义或导入的地方可见：

<!--versetest
Utils := module:
    (S:string).Reverse<public>():string = S
<#
-->
<!-- 52-->
```verse
# 在模块A中
Utils := module:
    (S:string).Reverse<public>():string =
        # 实施

# 在模块B中
using { Utils }

"Hello".Reverse()  # 导入后可用
```
<!-- #>-->

**类作用域中的扩展方法：**可以定义扩展方法
在类内部和访问类成员：

<!--versetest
game_manager := class:
    Multiplier:int = 10

    (Score:int).ScaledScore()<computes>:int =
        Score * Multiplier

    ProcessScore(Value:int)<computes>:int =
        Value.ScaledScore()

M()<transacts>:void={
GM := game_manager{}
GM.ProcessScore(5)
}
<# 
-->
<!-- 53-->
```verse
game_manager := class:
    Multiplier:int = 10

    (Score:int).ScaledScore()<computes>:int =
        Score * Multiplier  # 访问类字段

    ProcessScore(Value:int)<computes>:int =
        Value.ScaledScore()  # 使用扩展方法

GM := game_manager{}
GM.ProcessScore(5)  # 返回 50
```
<!-- #>-->

这创建了一个词法闭包，扩展方法可以在其中
引用封闭类的成员。

**元组参数转换：**当一个扩展方法有多个 
参数，您可以传递一个元组来一次提供所有参数：

<!--versetest-->
<!-- 54 -->
```verse
point := class<computes>{ X:int; Y:int }

(P:point).Translate(DX:int, DY:int)<allocates>:point =
    point{X := P.X + DX, Y := P.Y + DY}

Origin := point{X := 0, Y := 0}
Delta := (5, 10)
NewPoint := Origin.Translate(Delta)  # 元组扩展到两个参数
```
当元组类型与参数列表匹配时，此方法有效。

## Lambda

带有 `=>` 运算符的 Lambda 表达式不是
当前版本的 Verse 支持。用于创建函数
值和闭包，请改用嵌套函数。

函数是一流的值；它们可以存储在变量中，
作为参数传递，并从其他函数返回。这使得
强大的函数式编程模式，包括高阶
函数、回调和可组合操作。目前，这些
功能是通过嵌套函数而不是 lambda 提供的
表达式。

### 类型、差异和效果

函数类型遵循基于*方差*的特定子类型规则：

- *参数是逆变的*：接受更通用的函数
  类型可以替代接受特定类型的类型。

- *返回是协变的*：返回更具体类型的函数
  可以替代一种返回的通用类型。


考虑以下三个类：

<!--NoCompile-->
<!--264-->
```verse
animal := class:
    Name:string

dog := class(animal):
    Breed:string

working_dog := class(dog):
    Work:string
```
以及一些用例：

<!--versetest
animal := class:
    Name:string
dog := class(animal):
    Breed:string
working_dog := class(dog):
    Work:string

AnimalToDog(X:animal):dog = dog{Name := X.Name, Breed := "Unknown"}
DogToWorkingDog(X:dog):working_dog =
    working_dog{Name := X.Name, Breed := "Unknown", Work := "Guard"}
DogToAnimal(X:dog):animal = X
WorkingDogToDog(X:working_dog):dog = X

TestValid():void =
    var ProcessDog:type{_(:dog):dog} = AnimalToDog
    set ProcessDog = AnimalToDog  # OK: tuple(animal)->dog <: tuple(dog)->dog
    set ProcessDog = DogToWorkingDog  # OK: tuple(dog)->working_dog <: tuple(dog)->dog
<#
-->
<!-- 64 -->
```verse
# 对动物的一些功能
AnimalToDog(X:animal):dog = dog{Name := X.Name, Breed := "Unknown"}
DogToWorkingDog(X:dog):working_dog = working_dog{Name := X.Name, Breed := "Unknown", Work := "Guard"}
DogToAnimal(X:dog):animal = X
WorkingDogToDog(X:working_dog):dog = X

# 有效分配的示例
var ProcessDog:type{_(:dog):dog} = AnimalToDog

# 有效：接受更一般的（动物），返回精确的（狗）
# 通知参数：允许animal <: 狗这样做
set ProcessDog = AnimalToDog  # OK: 元组(动物)->狗 <: 元组(狗)->狗

# 有效：接受准确的（dog），返回更具体的（working_dog）
# 协变返回：working_dog <: 狗允许这样做
set ProcessDog = DogToWorkingDog  # OK: 元组(狗)->working_dog <: 元组(狗)->狗


ProcessDog1 := AnimalToDog  # 推断为 type{_(:animal):dog}
set ProcessDog1 = DogToAnimal  # 错误：分配不兼容

ProcessDog2 := AnimalToDog  # 推断为 type{_(:animal):dog}
set ProcessDog2 = WorkingDogToDog  # 错误：分配不兼容
```
<!--  #> -->

效果是函数类型的一部分。效果较少的函数
可以在需要具有更多效果的函数的地方使用 -effects
是**协变**（影响较小=亚型）：

<!--versetest
Pure()<computes>:int = 42
Transactional()<transacts>:int = 42
Suspendable()<suspends>:int = 42
UsePure(F()<computes>:int):int = F()
UseTransactional(F()<transacts>:int):int = F()
UseSuspendable(F()<suspends>:int):task(int) = spawn{ F() }
-->
<!-- 65-->
```verse
UsePure(Pure)                    # 好的
UseTransactional(Transactional)  # 好的
UseSuspendable(Suspendable)      # 好的

# 协方差：更少的效果可以替代更多的效果
UseTransactional(Pure)           # OK: ():int <: ()<transacts>:int

# 无效：更多的效果不能代替更少的效果
# UsePure(Transactional)         # ERROR: ()<transacts>:int </: ():int
```
可以在需要 `<transacts>` 的地方传递 `<computes>` 函数
因为效果越少意味着功能受到的限制越多。

当您有条件地分配不同的功能时，Verse 会找到
它们类型的最小上限（连接）：

<!--versetest
base := class:
    Value:int

derived := class(base):
    Extra:string
-->	
<!-- 66-->
```verse
# 假设如下：
# base := class{Value:int}
# derived := class(base){Extra:string}

F1():base = base{Value:=1}
F2():derived = derived{Value:=2, Extra:="test"}

# 连接： ()->base（公共超类型）
G := if(true?) {F1} else {F2}
G().Value  # 可以访问基础成员
```
### 使用 `type{}`

`type{_(...):...}` 语法声明具有完整功能的函数类型
细节。这是创建函数类型签名的机制
包括参数类型、返回类型和效果。下划线
`_` 是函数名的占位符，强调它
描述一个签名，而不是一个特定的函数：

<!--versetest-->
<!-- 72-->
```verse
# 函数类型变量
var Handler:?type{_(:string, :int)<decides>:void} = false

# 与签名匹配的嵌套函数
MakeHandler(Name:string, Count:int)<decides>:void =
    Print("{Name}: {Count}")
    Count > 0  # 决定效果

set Handler = option{MakeHandler}

# 函数接受函数参数
Process(F:type{_(:int):int}, Value:int):int =
    F(Value)

# 要传递的嵌套函数
Double(X:int):int = X * 2
Process(Double, 5)  # 返回 10
```
`type{}` 构造*声明函数类型签名*：

<!--versetest
m:= module:
    ValidType1 := type{_():int}
    ValidType2 := type{_(:string, :int):float}
    ValidType3 := type{_()<transacts><decides>:void}
<#    
-->
<!-- 73-->
```verse
# 函数签名的类型定义
ValidType1 := type{_():int}
ValidType2 := type{_(:string, :int):float}
ValidType3 := type{_()<transacts><decides>:void}
```
<!-- #>-->

在 `type{}` 中，函数声明必须具有返回类型，但
*不能有身体*。

函数类型在类中用作字段类型：

<!--versetest
calculator := class:
    Operation:type{_(:int,:int):int}
-->
<!-- 74-->
```verse
# 假设：
# calculator := class:
#    操作：类型{_(:int,:int):int}

Add(X:int, Y:int):int = X + Y
Multiply(X:int, Y:int):int = X * Y

# 创建具有不同操作的实例
Adder := calculator{Operation := Add}
Multiplier := calculator{Operation := Multiply}

Adder.Operation(5, 3)      # 返回 8
Multiplier.Operation(5, 3) # 返回 15
```
函数类型可用于局部变量，从而启用条件
功能选择：

<!--versetest-->
<!-- 75-->
```verse
ProcessA():int = 10
ProcessB():int = 20

SelectFunction(UseA:logic):int =
    # 根据条件选择功能
    Fn:type{_():int} =
        if (UseA?):
            ProcessA
        else:
            ProcessB
    Fn()

SelectFunction(true)   # 返回 10
SelectFunction(false)  # 返回 20
```
将 `type{}` 与 `?` 组合以创建可选函数类型：

<!--versetest-->
<!-- 76-->
```verse
DefaultHandler()<computes>:int = -1
CustomHandler()<computes>:int = 42

Process(Handler:?type{_()<computes>:int})<computes><decides>:int =
    # 如果提供了处理程序，则使用处理程序，否则使用默认处理程序
    Handler?() or DefaultHandler()

Process[false]                   # 返回 -1（无处理程序）
Process[option{CustomHandler}]   # 返回 42（自定义处理程序）
```
创建共享相同签名的函数数组：

<!--versetest-->
<!-- 77-->
```verse
GetZero():int = 0
GetOne():int = 1
GetTwo():int = 2

SumFunctions(Functions:[]type{_():int}):int =
    var Result:int = 0
    for (Fn : Functions):
        set Result += Fn()
    Result

SumFunctions(array{GetZero, GetOne, GetTwo})  # 返回 3
```
### 示例

**映射-过滤-减少**：

<!--versetest-->
<!-- 78-->
```verse
# 通用映射
Map(Items:[]t, F(:t)<transacts>:u where t:type, u:type)<transacts>:[]u =
    for (Item:Items):
        F(Item)

# 通用过滤器
Filter(Items:[]t, Pred(:t)<computes><decides>:void where t:type)<computes>:[]t =
    for (Item:Items, Pred[Item]):
        Item

# 通用折叠/缩小
Fold(Items:[]t, Initial:u, F(:u, :t)<transacts>:u where t:type, u:type)<transacts>:u =
    var Acc:u = Initial
    for (Item:Items):
        set Acc = F(Acc, Item)
    Acc

# 与嵌套函数一起使用
Values := array{1, 2, 3, 4, 5}

# 定义操作的嵌套函数
Square(X:int)<computes>:int = X * X
IsEven(X:int)<computes><decides>:void = X = 0 or Mod[X,2] = 0
AddTo(Acc:int, X:int)<computes>:int = Acc + X

Squared := Map(Values, Square)
Evens := Filter(Values, IsEven)
Sum := Fold(Values, 0, AddTo)
```
**功能组成**：

<!--versetest-->
<!-- 79-->
```verse
Compose(F(:b):c, G(:a):b where a:type, b:type, c:type):type{_(:a):c} =
    # 返回由 F 和 G 组成的嵌套函数
    Composed(X:a):c = F(G(X))
    Composed

Add1(X:int):int = X + 1
Double(X:int):int = X * 2

# 组合：先加倍，然后加 1
DoubleThenIncrement := Compose(Add1, Double)
DoubleThenIncrement(5)  # 返回 11 (5*2 + 1)
```
**部分应用**：

<!--versetest-->
<!-- 80-->
```verse
Partial(F(:a, :b):c, X:a where a:type, b:type, c:type):type{_(:b):c} =
    # 返回捕获了 X 的嵌套函数
    PartialFunc(Y:b):c = F(X, Y)
    PartialFunc

Add(X:int, Y:int):int = X + Y
Add5 := Partial(Add, 5)
Add5(3)  # 返回 8
```
## 嵌套函数

!!!警告“未发布的功能”
    嵌套函数尚未发布。本节记录了当前不可用的计划功能。

嵌套函数（也称为局部函数）是定义的函数
其他函数内部。它们提供封装，实现闭包
局部变量，并帮助组织复杂的逻辑
函数的范围。嵌套函数有名称，可以递归，并且
是在 Verse 中创建函数值和闭包的主要方式。

嵌套函数的声明方式与顶级函数类似，但是
在另一个函数体内：

<!--versetest-->
<!-- 81-->
```verse
Outer(X:int):int =
    # 嵌套函数定义
    Inner(Y:int):int = Y * 2

    # 调用嵌套函数
    Inner(X)

Outer(5)  # 返回 10
```
嵌套函数仅在其封闭函数内可见
范围。无法从外部访问它们。

嵌套函数从任何封闭函数捕获（封闭）变量
范围，创建强大的闭包：

<!--versetest-->
<!-- 82-->
```verse
MakeGreeter(Name:string):type{_():string} =
    # 问候语从外部范围捕获名称
    Greeting():string = "Hello, {Name}!"

    # 返回嵌套函数
    Greeting

SayHello := MakeGreeter("Alice")
SayHello()  # 返回“你好，爱丽丝！”

SayHi := MakeGreeter("Bob")
SayHi()  # 返回“你好，鲍勃！”
```
每次调用 `MakeGreeter` 都会创建一个带有自己捕获的新闭包
`Name` 值。

嵌套函数支持按参数类型重载：

<!--versetest-->
<!-- 83-->
```verse
Process(X:int):string =
    # 重载嵌套函数
    Format(Value:int):string = "int: {Value}"
    Format(Value:float):string = "float: {Value}"

    # 调用适当的重载
    IntResult := Format(42)       # 调用 int 版本
    FloatResult := Format(3.14)   # 调用浮动版本

    "{IntResult}, {FloatResult}"

Process(1)  # 返回“整数：42，浮点数：3.14”
```
重载解析的工作方式与顶级函数相同。

### 与 State 的关闭

嵌套函数可以捕获 `var` 变量并改变它们，创建有状态闭包：

<!--versetest-->
<!-- 84-->
```verse
MakeCounter(Initial:int):tuple(type{_():int}, type{_():void}) =
    var Count:int = Initial

    # Getter 统计计数
    GetCount():int = Count

    # 增量器改变捕获的计数
    Increment():void = set Count = Count + 1

    (GetCount, Increment)

Counter := MakeCounter(0)
GetValue := Counter(0)
IncrementValue := Counter(1)

GetValue()        # 返回 0
IncrementValue()  # 增量计数
GetValue()        # 返回 1
IncrementValue()  # 增量计数
GetValue()        # 返回 2
```
该模式创建了一个维护私有可变状态的闭包。

### 限制

嵌套函数有几个重要的限制来区分
它们来自顶级函数：

- 嵌套函数**不能**具有访问说明符，例如 `<public>`，
  `<internal>` 或 `<private>`：
- 嵌套函数对于其封闭函数始终是私有的。
- 您不能在函数内部定义类（嵌套或其他方式）：

<!--versetest
assert_semantic_error(3502):
    F():void =
        my_class := class {}
<#
-->
<!-- 86-->
```verse
# 错误：无法在本地范围内定义类
F():void =
    my_class := class {}  # 错误

# 正确：在模块级别定义类
my_class := class {}

F():void =
    Instance := my_class{}  # 好的 - 可以使用类
```
<!-- #>-->

- 嵌套函数不能引用变量或其他嵌套函数
  稍后在同一范围内定义的函数（这也意味着相互
  不允许递归嵌套函数）：

<!--versetest
assert_semantic_error(3506):
    F():void =
        X := G()
        G():int = 42
<#
-->
<!-- 87-->
```verse
# 错误 3506：在定义之前使用 G
F():void =
    X := G()     # 错误：G 尚未定义
    G():int = 42

# 正确：使用前定义
F():void =
    G():int = 42
    X := G()     # OK：G已定义
```
<!-- #>-->

- 用于调用父类方法的 `(super:)` 语法**不能**用于嵌套函数：

<!--versetest
assert_semantic_error(3612):
    base_class := class:
        F(X:int):int = X

    derived_class := class(base_class):
        F<override>(X:int):int =
            G():int =
                (super:)F(X)
            G()
<#
-->
<!-- 88-->
```verse
# 错误 3612：调用函数中不允许使用 super
base_class := class:
    F(X:int):int = X

derived_class := class(base_class):
    F<override>(X:int):int =
        G():int =
            (super:)F(X)  # 错误：此处不允许超级
        G()

# 正确：在重写方法中直接使用 super
derived_class := class(base_class):
    F<override>(X:int):int =
        BaseResult := (super:)F(X)  # 好的
        G():int = BaseResult * 2
        G()
```
<!-- #>-->

## 参数函数

参数函数（也称为通用函数）允许您
编写适用于多种类型的代码，同时保持完整
类型安全。您不必为每种类型编写单独的函数，
定义一个具有适应任何类型参数的函数
与它们一起使用的类型。

参数函数使用 `where` 子句声明类型参数
指定对这些类型的约束：

<!--versetest-->
<!-- 89-->
```verse
# 简单的身份函数 - 适用于任何类型
Identity(X:t where t:type):t = X
# 用法 - 自动推断类型参数
Identity(42)        # t推断为int，返回 42
Identity("hello")   # t推断为字符串，返回“hello”
```
`where t:type` 子句将 `t` 声明为带有约束 `type` 的类型参数，
意味着它可以是任何Verse类型。
函数签名 `(X:t):t` 的意思是“获取 `t` 类型的值并返回相同类型 `t` 的值”。

泛型类型参数 `t` 捕获完整的类型信息，而不仅仅是顶级类型。这意味着传递给通用函数的容器保留其内部结构：

<!--versetest-->
<!-- 901-->
```verse
# Identity 函数保留准确的容器类型
Identity(X:t where t:type):t = X

# 映射维护其键和值类型
IntToString:[int]string = map{1 => "one"}
Result1 := Identity(IntToString)  # 结果1：[int]字符串

# 数组维护元素类型
IntArray:[]int = array{1, 2, 3}
Result2 := Identity(IntArray)  # 结果2：[]int

# 即使是嵌套容器也能保留结构
NestedMap:[int][]string = map{1 => array{"a", "b"}}
Result3 := Identity(NestedMap)  # 结果3: [int][]string
```
这与使用 `any` 根本不同，后者会擦除类型信息。

<!--NoCompile-->
<!-- 90-->
```verse
FunctionName(Parameters where TypeParameter:Constraint, ...):ReturnType = Body
```
- *类型参数*出现在 `where` 子句中
- *约束*指定要求（例如，`type`、`subtype(comparable)`）
- *多个类型参数*在 `where` 子句中以逗号分隔

Verse 会自动从您输入的参数中推断出类型参数
pass，在大多数情况下无需显式类型注释
案例：

<!--versetest-->
<!-- 91-->
```verse
# 具有两个类型参数的函数
Pair(X:t, Y:u where t:type, u:type):tuple(t, u) = (X, Y)

# 推断所有类型参数
Pair(1, "one")        # t = int，u = 字符串，返回 (1, "one")
Pair(true, 3.14)      # t = 逻辑，u = 浮点数，返回 (true, 3.14)
```
集合推断：

<!--versetest-->
<!-- 92-->
```verse
# 通用第一元素函数
First(Items:[]t where t:type)<decides>:t = Items[0]

Values := array{1, 2, 3}
Result :int= First[Values]  # t 从 []int 推断为 int
```
当您将多个值传递给需要单个类型参数的参数函数时，Verse 可以推断元组或数组：

<!--versetest-->
<!-- 93-->
```verse
# 返回参数不变
Identity(X:t where t:type):t = X

# 传递多个值创建一个元组
Result1:tuple(int, int) = Identity(1, 2)  # t = 元组(int, int)

# 也可以视为数组
Result2:[]int = Identity(1, 2)  # t = []int 通过转换
```
### 类型约束

类型约束限制哪些类型可以与类型参数一起使用，从而启用需要特定功能的操作。

最宽松的约束接受任何类型：

<!--versetest-->
<!-- 94-->
```verse
# 适用于任何类型
Store(Value:t where t:type):t = Value
```
限制为指定类型的子类型的类型：

<!--versetest
vehicle := class:
    Speed:float = 0.0

car := class(vehicle):
    NumDoors:int = 4

ProcessVehicle(V:t where t:subtype(vehicle)):t =
    Print("Speed: {V.Speed}")
    V
<#
-->
<!-- 95-->
```verse
vehicle := class:
    Speed:float = 0.0

car := class(vehicle):
    NumDoors:int = 4

# 仅接受车辆或其子类型
ProcessVehicle(V:t where t:subtype(vehicle)):t =
    # 可以访问速度，因为我们知道 V 是车辆
    Print("Speed: {V.Speed}")
    V
```
<!-- #>-->

<!--versetest
vehicle := class:
    Speed:float = 0.0

car := class(vehicle):
    NumDoors:int = 4

ProcessVehicle(V:t where t:subtype(vehicle)):t =
    Print("Speed: {V.Speed}")
    V
-->
<!-- 200-->
```verse
# 有效通话
ProcessVehicle(vehicle{})      # t = 车辆
ProcessVehicle(car{})          # t = 汽车（车辆子类型）
```
该函数返回类型 `t`，而不是基本类型。这保留了特定类型：

<!--versetest
vehicle := class:
    Speed:float = 0.0

car := class(vehicle):
    NumDoors:int = 4

ProcessVehicle(V:t where t:subtype(vehicle))<transacts>:t =
    Print("Speed: {V.Speed}")
    V
-->
<!-- 96-->
```verse
# 具有子类型约束的类型保留函数
MyCar := car{NumDoors:=4, Speed:=60.0}
Result:car= ProcessVehicle(MyCar)  # 结果的类型为汽车，而不是车辆
Result.NumDoors                  # 可以访问汽车特定字段
```
`subtype(comparable)` 约束启用相等比较：

<!--versetest-->
<!-- 97-->
```verse
# 可以在 t 上使用 = 和 <> 运算符
FindInArray(Items:[]t, Target:t where t:subtype(comparable))<decides>:[]int =
    for (Index -> Item : Items, Item = Target):
        Index
```
类型参数可以在约束中相互引用：

<!--versetest-->
<!-- 98-->
```verse
# u 必须是 t 的子类型
Convert(Base:t, Derived:u where t:type, u:subtype(t)):t = Base
# 这确保了相关类型的类型安全
```
### 会员访问

使用子类型约束时，您可以访问基类型上存在的成员：

<!--versetest
entity := class:
    Name:string = "Entity"
    Health:int = 100

player := class(entity):
    Score:int = 0
<#
-->
<!-- 99-->
```verse
entity := class:
    Name:string = "Entity"
    Health:int = 100

player := class(entity):
    Score:int = 0

```
<!-- #>-->

<!--versetest
entity := class:
    Name:string = "Entity"
    Health:int = 100

player := class(entity):
    Score:int = 0
-->
<!-- 299-->
```verse
# 可以通过类型参数访问实体成员
GetInfo(E:t where t:subtype(entity)):tuple(t, string, int) =
    (E, E.Name, E.Health)            # 可以访问姓名和健康状况

P := player{Name := "Alice", Health := 100, Score := 1500}
Info := GetInfo(P)                   # Returns (player instance, "Alice", 100)
                                     # Info(0) has type player, not entity 
```
方法调用也有效：

<!--versetest
entity := class:
    GetStatus():string = "Active"

CheckStatus(E:t where t:subtype(entity)):string =
    E.GetStatus()
<#
-->
<!-- 100-->
```verse
entity := class:
    GetStatus():string = "Active"

# 对参数类型值调用方法
CheckStatus(E:t where t:subtype(entity)):string =
    E.GetStatus()  # 通过类型参数调用方法
```
<!-- #>-->

### 极性和方差

类型参数必须根据方差规则一致地使用。 
当函数用作值或作为参数传递时，这可以确保类型安全。

**协变位置**（对于返回类型是安全的）：

- 函数返回类型
- 元组/数组元素类型（作为返回）
- 映射键类型（作为返回）
- 映射值类型（作为返回）

**逆变位置**（对于参数类型是安全的）：

- 函数参数类型

**极性检查：** Verse 验证类型参数是否出现
仅在与其预期用途兼容的位置：

<!--versetest-->
<!-- 101-->
```verse
# 有效：t 协变出现（返回类型）
GetValue(X:t where t:type):t = X

# 有效：t 逆变出现（参数）
Consume(X:t where t:type):void = {}

# 有效：t 出现在两个位置（通过函数参数和返回）
Apply(F:type{_(:t):t}, X:t where t:type):t = F(X)
```
**不变类型会导致错误：**

<!--versetest
assert_semantic_error(3552):
    c(t:type) := class{var X:t}
    MakeContainer(X:t where t:type):c(t) = c(t){X := X}
<#
-->
<!-- 102-->
```verse
# 错误：无法返回 t 中不变的类型
c(t:type) := class{var X:t}  # 可变字段使 c 在 t 中不变
MakeContainer(X:t where t:type):c(t) = c(t){X := X}
```
<!-- #>-->

发生错误的原因是 `c(t)` 包含 `t` 类型的可变字段，
使其保持不变——既不是协变也不是逆变。返回
参数函数中的此类类型是不安全的。

**映射极性：** 映射在键和值上都是协变的：

<!--versetest-->
<!-- 103-->
```verse
# 有效：协变键和值
ProcessMap(M:[t]u where t:subtype(comparable), u:type):[t]u = M
```
## 重载

函数重载允许您定义多个函数
名称相同但参数类型不同。编译器选择
根据提供的参数类型的正确版本
呼叫站点。

定义多个名称相同但参数类型不同的函数：

<!--versetest-->
<!-- 104-->
```verse
# 按参数类型重载
Process(Value:int):string = "Integer: {Value}"
Process(Value:float):string = "Float: {Value}"
Process(Value:string):string = "String: {Value}"

# 调用选择合适的重载
Process(42)        # 返回“整数：42”
Process(3.14)      # 返回“浮点数：3.14”
Process("hello")   # 返回“字符串：你好”
```
编译器根据参数确定调用哪个重载
类型。每个重载必须具有不同的参数类型签名。

### 捕捉

您不能引用重载函数名称：

<!--versetest
assert_semantic_error(3502):
    f(x:int):void = {}
    f(x:float):void = {}
    g := f
<#
-->
<!-- 105-->
```verse
# 错误：无法捕获重载函数
f(x:int):void = {}
f(x:float):void = {}

# 错误：哪个f？
g:void = f
```
<!-- #>-->

存在此限制是因为编译器无法在未查看带有参数的调用站点的情况下确定您所指的重载。

### 效果

您可以重载具有不同效果的函数，但前提是
参数类型也不同：

**有效：不同类型，不同效果：**

<!--versetest-->
<!-- 106-->
```verse
Process(x:float):float = x
Process(x:int)<transacts><decides>:int = x = 1

Process(3.0)   # 返回 3.0（非失败）
Process[1]     # 返回option{1}（失败）
```
**无效：相同类型，不同效果：**

<!--versetest
assert_semantic_error(3532):
    f(x:int):void = {}
    f(x:int)<transacts><decides>:void = {}
<#
-->
<!-- 107-->
```verse
# 错误：相同的参数类型
f(x:int):void = {}
f(x:int)<transacts><decides>:void = {}  # 错误
```
<!-- #>-->

效果本身并不能创造独特性 - 您需要不同的参数类型。

### 子类中的重载

子类可以向方法添加新的重载：

<!--versetest
c0 := class:
    f(X:int):int = X

c1 := class(c0):
    f(X:float):float = X
<#
-->
<!-- 108-->
```verse
c0 := class:
    f(X:int):int = X

c1 := class(c0):
    # 为浮动添加新的重载
    f(X:float):float = X
```
<!-- #>-->

<!--versetest
c0 := class:
    f(X:int):int = X

c1 := class(c0):
    f(X:float):float = X
-->
<!-- 208-->
```verse
c0{}.f(5)     # OK - 过载
c1{}.f(5)     # OK - 继承 int 重载
c1{}.f(5.0)   # 好的 - 新的浮动过载
```
当子类定义共享名称的方法时
对于父方法，它必须：

1.提供**不同的参数类型**（不同于所有父重载）
2. **使用 `<override>` 精确覆盖一个**父级重载

<!--versetest
c := class<allocates>{}
d := class<allocates>(c){}

e := class<allocates>:
    func(C:c):c = C
    func(E:e):e = E

myf := class<allocates>(e):
    func<override>(C:c):d = d{}
<#
-->
<!-- 109-->
```verse
# 具有重载的父类
e := class:
     func(C:c):c = C
     func(E:e):e = E

# 有效：覆盖一个父级重载
myf := class(e):
     func<override>(C:c):d = d{}

# 错误：d 是 c 的子类型，重叠但不覆盖
# g := class(e):
#     func(D:d):d = D  # ERROR - ambiguous with func(C:c)
```
<!-- #>-->

### 具有重载方法的接口

接口可以声明重载方法：

<!--versetest
formatter := interface:
    Format(X:int):string = "{X}"
    Format(X:float):string = "{X}"

entity := class(formatter):
    Format<override>(X:int):string = "Entity-{X}"
    Format<override>(X:float):string = "Entity-{X}"
<#
-->
<!-- 110-->
```verse
formatter := interface:
    Format(X:int):string = "{X}"
    Format(X:float):string = "{X}"

entity := class(formatter):
    Format<override>(X:int):string = "Entity-{X}"
    Format<override>(X:float):string = "Entity-{X}"
```
<!-- #>-->

### 限制


**不能用非函数重载函数：**

名称不能同时是函数和非函数值：

<!--versetest
assert_semantic_error(3532):
    f:int = 0
    f():void = {}
<#
-->
<!-- 112-->
```verse
# 错误：无法使用变量重载
# f:int = 0
# f():void = {}
```
<!-- #>-->

**底层类型无法解决重载：**

底部类型（来自 `return`，没有值）不能用于重载决策：

<!--versetest
assert_semantic_error(3518):
    F(X:int):int = X
    F(X:float):float = X
    G():void =
        F(@ignore_unreachable return)
        0
<#
-->
<!-- 114-->
```verse
# 错误：无法确定哪个过载
F(X:int):int = X
F(X:float):float = X

# G():void =
#     F(@ignore_unreachable return)  # ERROR - which F?
#     0
```
<!-- #>-->

### 使用 `<suspends>` 重载

您可以混合挂起和非挂起重载，如果参数
类型不同：

<!--versetest-->
<!-- 115-->
```verse
f(x:int)<suspends>:void =
    Sleep(1.0)

f(x:float):void =
    Print("Non-suspending")

# 直接调用非挂起
f(1.0)

# 调用暂停并生成
spawn{f(1)}
```
**无法在没有生成的情况下调用暂停重载：**

<!--versetest
assert_semantic_error(3512):
    f(x:int):void = {}
    f(x:float)<suspends>:void = {}
    g():void = f(1.0)
<#
-->
<!-- 116-->
```verse
# 错误：暂停版本需要生成上下文
f(x:int):void = {}
f(x:float)<suspends>:void = {}

g():void = f(1.0)  # 错误 - 浮动版本已暂停
```
<!-- #>-->


### 类型 

每个函数都有一个类型来捕获其参数、效果和
返回值。类型语法使用下划线作为占位符
函数名称：

<!--versetest-->
<!-- 118-->
```verse
type{_(:int,:string)<decides>:float}
```
这表示任何采用整数和字符串的函数，可能
失败，成功时返回浮点数。

多个函数可以通过重载共享一个名称，只要
他们的签名不会造成歧义。编译器可以区分
基于参数类型的重载之间：

<!--versetest-->
<!-- 119-->
```verse
Transform(X:int):string = "I:{X}"
Transform(X:float):string = "F:{X}"
Transform(X:string):string = "S:{X}"

Result1 := Transform(42)        # 调用 int 版本
Result2 := Transform(3.14)      # 调用浮动版本
Result3 := Transform("Hello")   # 调用字符串版本
```
然而，重载有基于**类型的严格限制
独特性**。两种类型被认为是“不同的”过载
仅当没有可能的值可以匹配两者时才用于目的
类型。此限制可防止歧义并确保功能
调用始终可以在编译时明确解析。

Verse 使用精确的规则来确定两个参数类型是否相同
足够明显以允许重载。了解这些规则是
对于设计清晰的 API 至关重要。

以下类型对**不不同**并且不能用于
重载函数：

**1.可选和逻辑。** `?t` 和 `logic` 并不不同，因为
两种类型都包含 `false` 作为值，从而在以下情况下产生重载歧义：
`false` 作为参数传递：

<!--versetest
assert_semantic_error(3532):
    F(:?any):void = {}
    F(:logic):void = {}
<#
-->
<!-- 120-->
```verse
# 错误：不明显
F(:?any):void = {}
F(:logic):void = {}
```
<!-- #>-->

请注意，`?t` 和 `logic` 不是等效类型 - `logic` 包含
`true` 和 `false`，而 `?t` 包含 `false` 和选项值，例如
`option{false}`。然而，它们共享的 `false` 值意味着编译器
无法区分它们以进行重载解析。

**2.数组和映射。** 数组 `[]t` 和映射 `[k]t` 并不不同：

<!--versetest
assert_semantic_error(3532):
    F(:[]int):void = {}
    F(:[string]int):void = {}
<#
-->
<!-- 121-->
```verse
# 错误：不明显
F(:[]int):void = {}
F(:[string]int):void = {}
```
<!-- #>-->

**3.函数和映射。** 函数类型和映射没有区别：

<!--versetest
assert_semantic_error(3532):
    F(:[string]int):void = {}
    F(G(:string)<transacts><decides>:int):void = {}
<#
-->
<!-- 122-->
```verse
# 错误：不明显
F(:[string]int):void = {}
F(G(:string)<transacts><decides>:int):void = {}
```
<!-- #>-->

**4.函数和数组。**函数类型和数组不是
不同，因为重载函数可以匹配两者：

<!--versetest
assert_semantic_error(3532):
    F(:[]int):void = {}
    F(G(:string)<transacts><decides>:int):void = {}
<#
-->
<!-- 123-->
```verse
# 错误：不明显
F(:[]int):void = {}
F(G(:string)<transacts><decides>:int):void = {}
```
<!-- #>-->

**5.接口和类。**接口和任何类都不是
不同的，即使该类没有实现该接口，因为
该类的子类型可能：

<!--versetest
assert_semantic_error(3532):
    i := interface{}
    t := class{}
    f(:i):void = {}
    f(:t):void = {}
<#
-->
<!-- 124-->
```verse
i := interface{}
t := class{}

# 错误：不明确（t 的子类型可能实现 i）
f(:i):void = {}
f(:t):void = {}
```
<!-- #>-->

**6。功能不同效果**功能不分明
仅基于效果。更改或删除效果不会创建
明显的过载：

<!--versetest
assert_semantic_error(3532):
    a := class{}
    b := class{}
    F(G(:a)<transacts><decides>:b):void = {}
    F(G(:a):b):void = {}
<#
-->
<!-- 126-->
```verse
a := class{}
b := class{}

# 错误：不明显
F(G(:a)<transacts><decides>:b):void = {}
F(G(:a):b):void = {}
```
<!-- #>-->

**7.具有不同签名的函数。** 具有不同签名的函数
由于函数的原因，参数或返回类型并不不同
超载：

<!--versetest
assert_semantic_error(3532):
    a := class{}
    b := class{}
    F(G(:b):b):void = {}
    F(G(:a):b):void = {}
<#
-->
<!-- 127-->
```verse
# 错误：不明显
F(G(:b):b):void = {}
F(G(:a):b):void = {}
```
<!-- #>-->

**8. void as Top Type.** `void` 被视为等同于顶部
类型（接受 `any`），因此它与任何其他类型没有区别：

<!--versetest
assert_semantic_error(3532):
    F(:int):void = {}
    F(:void):void = {}
<#
-->
<!-- 128-->
```verse
# 错误：不明显
F(:int):void = {}
F(:void):void = {}
```
<!-- #>-->

**9.子类型关系。** 具有子类型关系的类是
不明显：

<!--versetest
assert_semantic_error(3532):
    a := class{}
    b := class(a){}
    F(:a):void = {}
    F(:b):void = {}
<#
-->
<!-- 129-->
```verse
a := class{}
b := class(a){}

# 错误：不明显
F(:a):void = {}
F(:b):void = {}
```
<!-- #>-->

**10.元组独特性规则。** 元组具有复杂的独特性规则：

**空元组和空数组没有区别：**

<!--versetest
assert_semantic_error(3532):
    a := class{}
    F(:tuple(), :a):void = {}
    F(:[]a, :a):void = {}
<#
-->
<!-- 130-->
```verse
a := class{}

# 错误：不明显
F(:tuple(), :a):void = {}
F(:[]a, :a):void = {}
```
<!-- #>-->

**仅当元组元素类型相同时，元组和数组才是不同的
完全不同：**

<!--versetest
assert_semantic_error(3532):
    a := class{}
    b := class(a){}
    F(:tuple(a, b), :a):void = {}
    F(:[]a, :a):void = {}
<#
-->
<!-- 131-->
```verse
a := class{}
b := class(a){}

# 错误：不明确（b 是 a 的子类型）
F(:tuple(a, b), :a):void = {}
F(:[]a, :a):void = {}
```
<!-- #>-->

**带有 `int` 键的元组和映射不不同：**

<!--versetest
assert_semantic_error(3532):
    a := class{}
    F(:tuple(a), :a):void = {}
    F(:[int]a, :a):void = {}
<#
-->
<!-- 132-->
```verse
a := class{}

# 错误：不明显
F(:tuple(a), :a):void = {}
F(:[int]a, :a):void = {}
```
<!-- #>-->

**具有非 `int` 键的元组和映射是不同的：**

<!--versetest
a := class{}

F(:tuple(a), :a):void = {}
F(:[logic]a, :a):void = {}
<#
-->
<!-- 133-->
```verse
a := class{}

# 有效：不同类型
F(:tuple(a), :a):void = {}
F(:[logic]a, :a):void = {}  # 好的
```
<!-- #>-->

**单例元组和 `int` 的可选元组没有区别：**

<!--versetest
assert_semantic_error(3532):
    a := class{}
    F(:tuple(int), :a):void = {}
    F(:?int, :a):void = {}
<#
-->
<!-- 134-->
```verse
a := class{}

# 错误：不明显
F(:tuple(int), :a):void = {}
F(:?int, :a):void = {}
```
<!-- #>-->

**单元组和非 `int` 的可选元组是不同的：**

<!--versetest
a := class{}
-->
<!-- 135-->
```verse
# 有效：不同类型
F(:tuple(a), :a):void = {}
F(:?a, :a):void = {}  # 好的
```
<a id="publishing-functions"></a>
## 发布功能

发布函数是向后兼容的承诺
该函数及其客户端。考虑这个函数：

<!--versetest-->
<!-- 139-->
```verse
F1<public>(X:int):int = X + 1
```
类型注释（`X:int):int`）告诉我们这个函数承诺：
给定任何整数，它总是返回一个整数。该合同不能
在未来版本的代码中被破坏。因为它有默认的效果，
包括 `<reads>` 效果，将来的实现可能会发生变化，
也许要执行额外的操作或优化，只要它
保留其签名。

不具有 `<reads>` 效果的功能灵活性较差。考虑
这个函数：

<!--versetest-->
<!-- 140-->
```verse
F2<public>(X:int)<computes>:int = X + 1
```
因为它有 `<computes>` 效果说明符，所以它没有
`<reads>` 效果。在给定版本内，这保证了引用
透明度：该函数将始终返回相同的结果
同样的论点。在各个版本中，这会产生更强的约束：
因为编译器无法验证修改后的主体是否保留了
所有可能的参数都具有相同的输入输出映射，它
保守地禁止任何身体改变。因此，改变身体
在未来版本中返回 `X + 2` 将被视为落后而被拒绝
不兼容。

诸如 `F1` 和 `F2` 之类的函数有时被称为 *opaque* 作为返回
type 抽象了函数的主体。 Verse 的未来版本将支持
*透明*功能：

<!--NoCompile-->
<!-- 141-->
```verse
F2<public>(X:int) := X + 1
```
透明函数不声明其返回类型，而是声明
函数的类型是从函数体推断出来的。这意味着一个非常
不同的承诺：永远保证函数体将
在模块代码的整个生命周期中保持完全相同。
