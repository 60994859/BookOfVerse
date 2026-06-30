# 容器类型

Verse 中的容器类型管理集合和结构化数据。可选值表示可能存在或不存在的值。元组将不同类型的多个值分组为有序序列。数组通过高效的索引访问保存零个或多个值。映射将键与值关联起来以进行快速查找。弱映射使用弱引用语义扩展常规映射以实现持久存储。

让我们详细探讨每种容器类型，从优雅地处理值存在或不存在的选项开始。

<a id="optionals"></a>
## 可选类型

可选的是一个不可变的容器，它要么保存 `t` 类型的值，要么什么也不保存。类型写为 `?t`。当值可能存在或不存在时，可选值很有用，例如在映射中查找键或调用可能失败的函数时。通过在类型中明确这种可能性，Verse 允许程序员直接且一致地处理“无结果”情况，而不是依赖临时错误代码或特殊值。

您可以使用 `option{...}` 创建一个非空可选，它将一个值包装到一个可选中。例如：

<!--versetest-->
<!-- 01 -->
```verse
A:?int = option{42}    # 包含整数 42 的可选值
```
如果要表示“无值”，请使用特殊常量 `false`。这就是 Verse 拼写空可选的方式：

<!--versetest-->
<!-- 02 -->
```verse
var B:?int = false     # 该选项没有元素
B = false              # 仍然空着
```
要提取可选元素，请在可选表达式后面写入 `?`。这会生成一个 `<decides>` 表达式，如果可选项具有元素，则该表达式成功，否则失败。例如：

<!--versetest
A:?int = option{42}
-->
<!-- 03 -->
```verse
S := A? + 2            # 44 成功，因为 A 包含 42
```
如果 `A` 为 `false`，则尝试使用 `A?` 将会失败，整个计算也会失败。一个失败的案例让这一点更加清晰：

<!--versetest
B:?int = false
-->
<!-- 04 -->
```verse
# X := B? + 1       # Fails because B is false and has no element
```
这展示了 Verse 如何将选项与效果系统紧密集成：值的存在或不存在可能导致整个计算成功或失败。

`option{...}` 形式也可以以相反的方向工作。当您使用 `<decides>` 效果进行计算时，将其包装在 `option{...}` 中会将其转换为可选值。成功后你会得到一个非空可选；失败时，您会得到 `false`：

<!--versetest
GetAFloatOrFail()<transacts><decides>:float = 3.14
-->
<!-- 05 -->
```verse
MaybeAFloat := option{GetAFloatOrFail[]}
```
这种对称性很重要。 `?` 运算符将可选值拆包为 `<decides>` 表达式，而 `option{...}` 将 `<decides>` 表达式包装为可选值。它们共同在可能失败的计算和可能不存在的值之间提供了一座平滑的桥梁。

尽管可选值本身是不可变的，但您可以将一个可选值保留在变量中并更改该变量指向的可选值。关键字 `set` 用于此目的：

<!--versetest-->
<!-- 06 -->
```verse
var C:?int = false
set C = option{2}      # C 现在指的是包含 2 的可选值
C? = 2                 # 成功，因为 C 不为空
```
当您想要跟踪一段时间内的成功或失败时，此功能非常有用，例如逐渐计算结果并仅在成功时更新变量。

一个常见的用例是搜索可能存在或不存在的东西。想象一个函数 `Find` 查找整数数组并返回所需元素的索引。如果该元素存在，函数返回`option{index}`；如果不是，则返回 `false`。然后调用者可以安全地决定要做什么：

<!--versetest
NumberArray:[]int = array{10, 20, 30}
-->
<!-- 07 -->
```verse
Find(N:[]int, X:int):?int =
    for (I := 0..N.Length-1):
        if (N[I] = X) then return option{I}
    return false
    
Idx:?int = Find(NumberArray, 20)    # 返回option{1}
Y := Idx?                           # 解开可选的
Y = 1
```
这里的可选信号直接在类型中表示失败的可能性。 `?` 运算符可以轻松地在表达式中使用结果，而 `option{...}` 允许您将条件计算转回可选值。其效果是“也许有值，也许没有”的想法成为语言的首要部分，而不是事后的想法，并且鼓励程序员以有纪律的方式处理值的缺失。

<a id="tuple"></a>
## 元组

元组是对两个或多个值进行分组的容器。与数组不同，元组允许您组合混合类型的值并将它们视为一个单元。元组的元素按照列出它们的顺序出现，并且可以通过它们的位置（称为索引）访问它们。由于元素的数量在编译时始终已知，因此元组的创建既简单又使用安全。

术语*元组* 是*四元组*、*五元组*、*六元组* 等的后向形式。从概念上讲，元组就像具有有序字段的未命名数据结构，或者像固定大小的数组，其中每个元素可能具有不同的类型。

元组文字是通过将逗号分隔的表达式列表括在括号中来编写的。例如：

<!--versetest-->
<!-- 08 -->
```verse
Tuple1 := (1, 2, 3)
```
元素的顺序很重要，因此 `(3, 2, 1)` 是一个完全不同的值。由于元组允许混合类型，您可以编写：

<!--versetest-->
<!-- 09 -->
```verse
Tuple2 := (1, 2.0, "three")
```
元组也可以相互嵌套：

<!--versetest-->
<!-- 10 -->
```verse
X:tuple(int,tuple(int,float,string),string) = (1, (10, 20.0, "thirty"), "three")
```
当您想要从函数返回多个值或者想要对值进行轻量级分组而不需要定义结构或类的开销时，元组非常有用。元组的类型由 `tuple` 关键字编写，后跟元素的类型，但在大多数情况下可以推断出来。例如，您可以编写 `MyTuple : tuple(int, float, string) = (1, 2.0, "three")`，或者简单地编写 `MyTuple := (1, 2.0, "three")` 并让编译器推断类型。

使用用括号编写的从零开始的索引运算符来访问元组的元素。如果是 `MyTuple := (1, 2.0, "three")`，则 `MyTuple(0)` 是整数 `1`，`MyTuple(1)` 是浮点数 `2.0`，`MyTuple(2)` 是字符串 `"three"`。由于编译器知道每个元组中的元素数量，因此元组索引不会失败：任何使用越界索引的尝试都会导致编译时错误。

元组的另一个特性是*扩展*。当元组作为单个参数传递给函数时，它的元素会自动扩展，就好像该函数是用每个元素单独调用的一样。例如：

<!--versetest-->
<!-- 11 -->
```verse
F(Arg1:int, Arg2:string):void =
    Print("{Arg1}, {Arg2}")

G():void =
    MyTuple := (1, "two")
    F(MyTuple)   # 展开为 F(1, “二”)
```
元组在结构化并发中也发挥着作用。 `sync` 表达式生成一个结果元组，允许同时评估随时间展开的多个计算。这样，元组不仅提供了方便的分组机制，而且为组合并发计算奠定了基础。

当与数组串联运算符 `+` 和 `+=` 一起使用时，元组也可以自动转换为数组。更多详细信息请参见[从元组到数组](#from-tuples-to-arrays)。

<a id="arrays"></a>
## 数组

数组是一个不可变的容器，它保存零个或多个相同类型 `t` 的值。数组的元素是有序的，并且每个元素都可以通过从零开始的索引进行访问。数组在其类型中使用方括号编写，例如 `[]int` 或 `[]float`，并使用 `array{...}` 文字形式创建。例如，`A : []int = array{}` 创建一个空数组，而 `B : []int = array{1, 2, 3}` 创建一个包含三个整数的数组。通过索引访问元素是一个可能失败的操作：`B[0]` 成功，值为 `1`，而 `B[10]` 失败，因为索引越界。

数组可以使用 `+` 运算符连接，并且当声明为 `var` 时，可以使用速记运算符 `+=` 对其进行扩展。例如，`var C:[]int= B + array{4}` 为 `C` 赋予值 `array{1,2,3,4}`，`set C += array{5}` 将其更新为 `array{1,2,3,4,5}`。元组也可以直接与这些运算符一起使用，并且会自动转换为数组。数组的长度可通过 `.Length` 成员获得，因此此处的 `C.Length` 将为 `5`。元素始终按照插入顺序存储，索引从 `0` 开始。因此，`array{10,20,30}[0]` 是 `10`，并且任何数组的最后一个有效索引始终比其长度小 1。

尽管数组本身是不可变的，但使用 `var` 声明的变量可以重新分配给新数组，或者看起来其元素已更改。例如，`var D:[]int = array{1,2,3}` 允许更新 `set D[0] = 3`，之后 `D` 将保留 `array{3,2,3}`。实际发生的情况是，在后台创建了一个全新的数组，并更新了指定的元素。实际上，`set D[0] = 3` 被编译为 `set D = array{3,D[1],D[2]}`。如果另一个变量引用旧数组，则旧数组将继续存在，这意味着如果 `A` 和 `B` 均以 `array{1}` 开头，并且我们更新 `A[0]`，则 `A` 和 `B` 将出现分歧： `A[0]` 现在是 `2`，而 `B[0]` 仍然是 `1`。

当您想要存储相同类型的多个值时，数组非常有用，例如游戏中的玩家列表：`Players:[]player = array{Player1,Player2}`。按索引访问，例如 `Players[0]` 是第一个玩家。由于索引是失败的，因此它通常与 `if` 表达式或迭代结合使用。例如，以下代码安全地打印出数组的每个元素：

<!--versetest-->
<!-- 12 -->
```verse
ExampleArray : []int = array{10, 20, 30}
for (Index := 0..ExampleArray.Length - 1):
    if (Element := ExampleArray[Index]):
        Print("{Element} in ExampleArray at index {Index}")
```
产生
```
10 in ExampleArray at index 0
20 in ExampleArray at index 1
30 in ExampleArray at index 2
```
因为数组是值，所以“更改”它们总是意味着用新数组替换旧数组。对于 `var`，这感觉很自然，因为可以重新分配变量。例如，您可以连接数组然后更新元素：

<!--versetest-->
<!-- 13 -->
```verse
Array1 : []int = array{10, 11, 12}
var Array2 : []int = array{20, 21, 22}
set Array2 = Array1 + Array2 + array{30, 31}
if (set Array2[1] = 77) {}
```
此代码运行后，迭代 `Array2` 会打印 `10, 77, 12, 20, 21, 22, 30, 31`。

元组可以直接与数组上的 `+` 和 `+=` 运算符一起使用，并且会自动转换为数组。这提供了一种添加多个元素的简洁方法，而无需将它们包装在 `array{...}` 中：

<!--versetest-->
<!-- 77 -->
```verse
var Numbers:[]int = array{1, 2, 3}

# 使用元组连接 - 自动转换为数组
set Numbers = Numbers + (4, 5, 6)

# 速记形式也适用于元组
set Numbers += (7, 8, 9)

# 结果：数组{1,2,3,4,5,6,7,8,9}
```
这种使用运算符的元组到数组的转换与函数调用中的元组扩展不同。使用运算符，元组元素将作为单独的项目添加到数组中，就像您编写了 `array{4, 5, 6}` 一样。

数组还可以嵌套形成多维结构，类似于表的行和列。例如，以下创建一个二维 4×3 整数数组：

<!--versetest-->
<!-- 14 -->
```verse
var Counter : int = 0
Example : [][]int =
    for (Row := 0..3):
        for (Column := 0..2):
            set Counter += 1
```
该数组可以可视化为
```
Row 0:  1  2  3
Row 1:  4  5  6
Row 2:  7  8  9
Row 3: 10 11 12
```
并通过两个索引进行访问：`Example[0][0]` 为 `1`，`Example[0][1]` 为 `2`，`Example[1][0]` 为 `4`。您可以使用嵌套迭代循环遍历所有行和列。 Verse 中的数组不限于矩形：每行可以有不同的长度，从而产生锯齿状结构。例如，

<!--versetest-->
<!-- 15 -->
```verse
Example : [][]int =
    for (Row := 0..3):
        for (Column := 0..Row):
            Row * Column
```
生成一个三角形数组，行长度不断增加：第 0 行没有，第 1 行有一个 `0`，第 2 行有 `0, 2, 4`，第 3 行有 `0, 3, 6, 9`。

具有复杂初始化的嵌套数组自然地作为类字段默认值工作：

<!--versetest
tile_class := class:
    Position:tuple(int, int)
    var IsOccupied:logic = false

game_board := class:
    Tiles:[][]tile_class =
        for (Y := 0..9):
            for (X := 0..9):
                tile_class{Position := (X, Y)}

    GetTile(X:int, Y:int)<computes><decides>:tile_class =
        Row := Tiles[Y]
        Row[X]
assert:
<# 
-->
<!-- 16 -->
```verse
# 带瓷砖网格的游戏板
tile_class := class:
    Position:tuple(int, int)
    var IsOccupied:logic = false

game_board := class:
    # 初始化 10×10 的图块网格
    Tiles:[][]tile_class =
        for (Y := 0..9):
            for (X := 0..9):
                tile_class{Position := (X, Y)}

    # 获取特定位置的图块
    GetTile(X:int, Y:int)<computes><decides>:tile_class =
        Row := Tiles[Y]
        Row[X]

# 创建板实例
Board := game_board{}

# 访问特定图块
if (CenterTile := Board.GetTile[5, 5]):
    set CenterTile.IsOccupied = true
```
<!--
#>
   Board := game_board{}
   if (CenterTile := Board.GetTile[5, 5]):
       set CenterTile.IsOccupied = true
-->

当您使用 `array{}` 创建空数组时，Verse 会根据变量的类型注释推断元素类型：

<!--versetest-->
<!-- 17 -->
```verse
IntArray : []int = array{}       # 空整数数组
FloatArray : []float = array{}   # 空的浮点数数组
```
如果没有类型注释，编译器无法确定所需的数组类型，因此您必须显式提供类型或至少包含一个建立该类型的元素。

数组根据所有元素的公共超类型确定其元素类型。当您创建包含不同但相关类型的值的数组时，Verse 会查找包含所有元素的最具体类型：

<!--versetest
class1 := class {}
class2 := class(class1) {}
class3 := class(class1) {}
-->
<!-- 18 -->
```verse
# 备份元素类型为class1（公共超类型）
MixedArray : []class1 = array{class2{}, class3{}}
```
这适用于任何类型层次结构，包括接口。如果混合完全不相关的类型，元素类型将变为 `any`：

<!--versetest-->
<!-- 19 -->
```verse
# 可比较的数组 - 不同类型共享可比较的共同点
DisjointArray : []comparable = array{42, 13.37, true}

# 任何类型的数组 - 没有共同超类型的不同类型
AnyArray : []any = array{15.61, "Message", void}
```
<a id="from-tuples-to-arrays"></a>
### 从元组到数组

Verse 提供特定上下文中元组和数组之间的自动转换，实现灵活的函数调用，同时保持类型安全。这种转换是*单向*：元组可以变成数组，但数组不能变成元组。

当所有元组元素与数组的元素类型兼容时，元组可以直接分配给数组变量：

<!--versetest-->
<!-- 20 -->
```verse
# 同构元组到数组
X:tuple(int, int) = (1, 2)
Y:[]int = X            # 有效 - 两个元素都是 int
Y[1] = 2               # 可以用作普通数组

# 更长的元组也可以工作
NumTuple:tuple(int, int, int, int) = (1, 2, 3, 4)
NumberArray:[]int = NumTuple
NumberArray.Length = 4
```
此转换创建一个按顺序包含所有元组元素的数组。

当函数具有单个数组参数时，您可以使用多个参数调用它，这些参数会自动形成一个数组：

<!--versetest-->
<!-- 21 -->
```verse
ProcessNumbers(Nums:[]int):int = Nums.Length

# 所有这些都是等价的：
ProcessNumbers(1, 2, 3)           # 多个参数 → 数组
ProcessNumbers((1, 2, 3))         # 元组文字 → 数组
Values := (1, 2, 3)
ProcessNumbers(Values)             # 元组变量 → 数组
```
这种“类似可变参数”的语法提供了便利，同时保持函数签名简单：

<!--versetest-->
<!-- 22 -->
```verse
Sum(Nums:[]int):int =
    var Total:int = 0
    for (N : Nums):
        set Total += N
    Total

Sum(1, 2, 3, 4)                   # 返回 10
Sum((5, 6))                       # 返回 11
Values := (10, 20, 30)
Sum(Values)                       # 返回 60
```
仅当**所有元组元素都与数组的元素类型兼容**时，数组转换才会成功：

<!--versetest
F(X:[]int):int = X.Length
entity := class:
    ID:int

player := class(entity):
    Name:string

ProcessEntities(E:[]entity):int = E.Length
GetP()<transacts>:player = player{ID := 1, Name := "Alice"}
GetE()<transacts>:entity = entity{ID := 2}
<#
-->
<!-- 23 -->
```verse
# 同构元组 - 全部 int
F(X:[]int):int = X.Length
F(1, 2, 3)                        # 有效

# 子类型兼容性
entity := class:
    ID:int

player := class(entity):
    Name:string

ProcessEntities(E:[]entity):int = E.Length

P := player{ID := 1, Name := "Alice"}
E := entity{ID := 2}
ProcessEntities(P, E)             # 有效 - 玩家是实体的子类型
```
<!-- #> -->

采用 `[]any` 的函数接受**任何元组**，无论元素类型如何：

<!--versetest-->
<!-- 24 -->
```verse
GetLength(Items:[]any):int = Items.Length

# 全部有效 - 任何元组都有效
GetLength(1, 2.0)                 # 混合类型 OK
GetLength("a", 42, true)          # 不同类型 OK
GetLength((1, 2.0, "hello"))      # 显式元组 OK
```
这使得通用函数能够处理异构数据。

当元组元素共享一个公共超类型（通过继承或接口）时，它们会转换为该超类型的数组：

<!--versetest
interface1 := interface:
    GetID():int

class1 := class(interface1):
    GetID<override>():int = 1

class2 := class(interface1):
    GetID<override>():int = 2

ProcessInterfaces(Items:[]interface1):int = Items.Length

assert:
    X:class1 = class1{}
    Y:class2 = class2{}
    ProcessInterfaces(X, Y) = 2
<#
-->
<!-- 25 -->
```verse
interface1 := interface:
    GetID():int

class1 := class(interface1):
    GetID<override>():int = 1

class2 := class(interface1):
    GetID<override>():int = 2

ProcessInterfaces(Items:[]interface1):int = Items.Length

X:class1 = class1{}
Y:class2 = class2{}

# 有效 - 两个类都实现接口1
ProcessInterfaces(X, Y)           # 返回 2
```
<!-- #> -->

编译器找到最具体的公共超类型并将其用于数组元素类型。

元组到数组的转换适用于嵌套结构：

**嵌套数组：**

<!--versetest
ProcessMatrix(Matrix:[][]int):int = Matrix.Length
-->
<!-- 26 -->
```verse
# 嵌套元组 → 嵌套数组
MatrixData := ((1, 2), (3, 4))
ProcessMatrix(MatrixData)             # 有效

# 或者显式嵌套
ProcessMatrix((1, 2), (3, 4))   # 有效
```
**可选数组：**

<!--versetest-->
<!-- 27 -->
```verse
ProcessOptional(Items:?[]int)<decides>:int = Items?[0]

# 可选元组 → 可选数组
Values := option{(1, 2)}
ProcessOptional[Values]           # 有效
```
**包含数组的元组：**

<!--versetest-->
<!-- 28 -->
```verse
ProcessComplex(Data:tuple([]int, int)):int = Data(0).Length

# 元组的第一个元素变成数组
ProcessComplex(((1, 2), 3))       # 有效 - (1,2) 评估 []int
```
### 数组切片

数组通过 `.Slice` 方法支持切片操作，该方法提取数组的连续部分。切片是一个可能失败的操作——只有当索引有效时它才会成功。

二参数形式 `Array.Slice[Start, End]` 返回索引 `Start` 到但不包括索引 `End` 的元素：

<!--versetest-->
<!-- 29 -->
```verse
NumArray : []int = array{10, 20, 30, 40, 50}
if (Slice := NumArray.Slice[1, 4]):
    Slice = array{20, 30, 40}
```
单参数形式 `Array.Slice[Start]` 返回从 `Start` 到末尾的所有元素：

<!--versetest
NumArray : []int = array{10, 20, 30, 40, 50}
-->
<!-- 30 -->
```verse
if (Slice := NumArray.Slice[2]):
    Slice = array{30, 40, 50}
```
如果索引为负、越界或 `Start` 大于 `End`，则切片失败。当 `Start` 等于 `End` 时，创建空切片有效：

<!--versetest
NumArray:[]int = array{10, 20, 30, 40, 50}
-->
<!-- 31 -->
```verse
NumArray.Slice[2, 2]  # 数组成功{}
# NumArray.Slice[2, 1] # 会失败 - 开始 > 结束
# NumArray.Slice[-1, 2] # 会失败 - 负指数
# NumArray.Slice[0, 10] # 会失败 - 超出存储容量
```
切片也适用于字符串和字符元组，返回一个字符串：

<!--versetest-->
<!-- 32 -->
```verse
"hello".Slice[1, 4] = "ell"
```
<a id="array-methods"></a>
### 数组方法

数组提供了搜索、删除和替换元素的内在方法。这些操作创建新数组而不是修改现有数组，从而保持 Verse 的不变性保证。

`Find()` 方法搜索元素的第一次出现并返回其索引，如果未找到则失败：

<!--versetest
M():void =
    SomeArray:[]int = array{1, 2, 3}
    if (Example := SomeArray.Find[2]) {}
<#
-->
<!-- 33 -->
```verse
Array.Find(Element:t where t:subtype(comparable))<decides>:int
```
<!-- #> -->

<!--versetest-->
<!-- 34 -->
```verse
NumArray := array{1, 2, 3, 1, 2, 3}

if (Index := NumArray.Find[2]):
    # 索引为 1（第一次出现）
    Print("Found at index {Index}")

if (not NumArray.Find[0]):
    # 元素不在数组中
    Print("Not found")

# 带弦
Strings := array{"Apple", "Orange", "Strawberry"}

if (Index := Strings.Find["Strawberry"]):
    Print("Found at {Index}") # 打印“2 点发现”
```
`Find()` 成功时返回第一个找到的索引 (`int`)，如果未找到元素则失败，从而可以安全处理丢失的元素，而不会出现异常或特殊标记值。

`RemoveFirstElement()` 删除第一个出现的位置：

<!--versetest
M():void =
    SomeArray:[]int = array{1, 2, 3}
    if (Updated := SomeArray.RemoveFirstElement[2]) {}
<#
-->
<!-- 35 -->
```verse
Array.RemoveFirstElement(Element:t where t:subtype(comparable))<decides>:[]t
```
<!-- #> -->

<!--versetest-->
<!-- 36 -->
```verse
NumArray := array{1, 2, 3, 1, 2, 3}

if (Updated := NumArray.RemoveFirstElement[2]):
    # 更新为数组{1, 3, 1, 2, 3}
    Print("Removed first 2")

if (not NumArray.RemoveFirstElement[0]):
    # 未找到元素
    Print("Element not in array")
```
`RemoveAllElements()` 删除所有出现的情况：

<!--versetest-->
<!-- 37 -->
```verse
NumArray := array{1, 2, 3, 1, 2, 3}
Updated := NumArray.RemoveAllElements(2)
Updated = array{1, 3, 1, 3}

# 如果未找到元素，则返回未更改的数组
Same := NumArray.RemoveAllElements(0)
Same = array{1, 2, 3, 1, 2, 3}
```
`Remove()` 删除特定位置的元素：

<!--NoCompile-->
<!--00-->
```verse
Array.Remove(From:int, To:int)<decides>:[]t
```
<!--versetest-->
<!-- 38 -->
```verse
NumArray := array{10, 20, 30, 40}

if (Updated := NumArray.Remove[1,2]):
    # 更新为数组{10, 30, 40}

# 负索引会失败
# if (not NumArray.Remove[-1,0]):

# 越界就会失败
# if (not NumArray.Remove[6,10]):
```
`ReplaceFirstElement()` 替换第一次出现的位置：

<!--NoCompile-->
```verse
Array.ReplaceFirstElement(OldValue:t, NewValue:t where t:subtype(comparable))<decides>:[]t
```
<!--versetest-->
<!-- 39 -->
```verse
NumArray := array{1, 2, 3, 1, 2, 3}

if (Updated := NumArray.ReplaceFirstElement[2, 99]):
    # 更新为数组{1, 99, 3, 1, 2, 3}

if (not NumArray.ReplaceFirstElement[0, 99]):
    # 未找到元素 - 失败
```
`ReplaceAllElements()` 替换所有出现的情况：

<!--NoCompile-->
```verse
Array.ReplaceAllElements(OldValue:t, NewValue:t where t:subtype(comparable)):[]t
```
<!--versetest-->
<!-- 40 -->
```verse
NumArray := array{1, 2, 3, 1, 2, 3}
Updated := NumArray.ReplaceAllElements(2, 99)
# 更新为数组{1, 99, 3, 1, 99, 3}

# 如果未找到元素，则返回未更改的数组
Same := NumArray.ReplaceAllElements(0, 99)
# 同样是数组{1, 2, 3, 1, 2, 3}
```
`ReplaceElement()` 在特定索引处替换：

<!--NoCompile-->
```verse
Array.ReplaceElement(Index:int, NewValue:t)<decides>:[]t
```
<!--versetest-->
<!-- 41 -->
```verse
NumArray := array{10, 20, 30, 40}

if (Updated := NumArray.ReplaceElement[1, 99]):
    # 更新为数组{10, 99, 30, 40}

if (not NumArray.ReplaceElement[-1, 99]):
    # 负索引失败

if (not NumArray.ReplaceElement[10, 99]):
    # 越界失败
```
`ReplaceAll()` 是基于模式的替换：

<!--versetest-->
<!-- 42 -->
```verse
NumArray := array{1, 2, 3, 4, 2, 3, 5}
Pattern := array{2, 3}
Replacement := array{99}
Updated := NumArray.ReplaceAll(Pattern, Replacement)
Updated = array{1, 99, 4, 99, 5}

# 适用于不同长度的图案
NumArray2 := array{1, 2, 2, 1, 2, 2, 1}
Updated2 := NumArray2.ReplaceAll(array{2, 2}, array{9, 9, 9})
Updated2 = array{1, 9, 9, 9, 1, 9, 9, 9, 1}

# 字符串是[]char
SomeMessage := "Hey, this is a string, Hello!"
NewMessage := SomeMessage.ReplaceAll("He", "Apples") # 注意：区分大小写！
NewMessage = "Applesy, this is a string, Applesllo!"
```
`ReplaceAll()` 找到与 `Pattern` 匹配的连续子序列，并将每个子序列替换为 `Replacement`。替换可以是任意长度，包括空的。

`Insert()` 在特定位置插入元素：

<!--NoCompile-->
<!-- 00 -->
```verse
Array.Insert(Index:int, Element:[]t)<decides>:[]t
```
<!--versetest-->
<!-- 43 -->
```verse
NumArray := array{10, 20, 40}

if (Updated := NumArray.Insert[2, array{30}]):
    # 更新为数组{10, 20, 30, 40}
    # 插入到索引 2 处，现有元素右移

# 可以在开始处插入
if (Updated2 := NumArray.Insert[0, array{5}]):
    # 已更新2 是数据库{5, 10, 20, 40}

# 可以在末尾插入（索引=长度有效）
if (Updated3 := NumArray.Insert[NumArray.Length, array{50}]):
    # 已更新3 是数据库{10, 20, 40, 50}

# 越界失败
if (not NumArray.Insert[-1, array{5}]):
    # 负索引失败

if (not NumArray.Insert[NumArray.Length + 1, array{5}]):
    # 超出长度失败
```
`Concatenate()` 函数将数组数组组合成单个平面数组：

<!--versetest
M():void =
    Result := Concatenate(array{1}, array{2, 3})
<#
-->
<!-- 44 -->
```verse
Concatenate(Arrays:[][]t):[]t
```
<!-- #> -->

由于元组到数组的强制转换，您可以直接传递多个数组参数，它们会自动聚集到数组数组参数中。与连接两个数组的 `+` 运算符不同，`Concatenate()` 接受任意数量的数组参数：

<!--versetest-->
<!-- 45 -->
```verse
# 空调用返回空数组
Empty := Concatenate()
Empty = array{}

# 单个数组作为数组数组传递
Single := Concatenate(array{array{1, 2, 3}})
Single = array{1, 2, 3}

# 两个数组
TwoArrays := Concatenate(array{1, 2}, array{3, 4})
TwoArrays = array{1, 2, 3, 4}

# 多个阵列
Many := Concatenate(array{1}, array{2, 3}, array{4}, array{5, 6})
Many = array{1, 2, 3, 4, 5, 6}
```
空数组被无缝处理：

<!--versetest-->
<!-- 46 -->
```verse
# 空数组没有任何贡献
Result1 := Concatenate(array{1, 2}, array{}, array{3})
Result1 = array{1, 2, 3}
Result2 := Concatenate(array{}, array{}, array{})
Result2 = array{}

# 可以连接许多空数组
# EmptyResult := Concatenate(for (I := 0..100): array{})
# 空结果 = 数组{}
```
**与`+`操作员比较：**

<!--versetest-->
<!-- 48 -->
```verse
# 使用 + 运算符（二进制）
First := array{1, 2}
Second := array{3, 4}
Third := array{5, 6}
ChainedResult := First + Second + Third  # 有效，但需要多次操作

# 使用连接
ConcatenatedResult := Concatenate(First, Second, Third)  # 单人操作

ChainedResult = ConcatenatedResult
```
因此，Verse 中的数组是具有可预测行为的不可变值，但通过 `var`，它们提供了可变变量的便利。它们可以被连接、迭代、切片、搜索和操作，使它们成为该语言中最灵活和基本的数据结构之一。

<a id="maps"></a>
## 映射

映射是核心容器类型之一，与数组和选项一起。如果数组是由整数索引的有序序列，并且可选值是所有容器中最小的容器，保存零个或一个值，那么 Maps 概括了这两种想法：像数组一样，它们提供高效的查找，但不限于整数索引，它们允许任何“可比较”类型作为键。您可以将映射视为由任意键索引的数组，或者视为可以同时保存许多键值关联的更大的可选值。

映射是一个不可变的关联容器，它存储零个或多个 `[k]v` 类型的键值对，写为 `(Key:k, Value:v)`。映射是将值与其他值关联的标准方法：您提供一个键，映射将返回与其关联的值。

每当您想要存储由整数位置以外的其他内容自然索引的数据时，映射就很有用。例如，您可能想要存储按名称键入的不同对象的权重：

<!--versetest-->
<!-- 50 -->
```verse
Empty := map{}

var Weights:[string]float = map{
    "ant" => 0.0001,
    "elephant" => 500.0,
    "galaxy" => 500000000000.0
}
```
使用方括号在映射中查找值。如果键存在，则表达式成功；如果不存在，则表达式失败。查找的设计速度很快，时间复杂度为摊销 *O(1)*：

<!--versetest
Weights:[string]float = map{"ant" => 0.0001}
-->
<!-- 51 -->
```verse
Weights["ant"]  # 成功，因为映射中存在“ant”键
# 权重[“car”]会失败
```
如果要更新存储在变量中的映射，请使用 `set`。这既适用于添加新的键值对，也适用于更改现有键的值。如果您尝试修改不存在的密钥，操作将失败：

<!--versetest-->
<!-- 52 -->
```verse
var Friendliness:[string]int = map{"peach" => 1000}

set Friendliness["pelican"] = 17     # 成功：使用给定的键添加新值
set Friendliness["peach"] += 2000    # 成功：使用给定的键更新现有值
# set Friendliness["tomato"] += 1000   # would fail: can't update a value which key does not exist
```
每张映射还带有其大小，可通过 `Length` 字段访问：

<!--versetest
Friendliness:[string]int = map{"peach" => 1000, "pelican" => 17}
-->
<!-- 53 -->
```verse
Friendliness.Length = 2         # 成功：映射有 2 个条目
```
当构造具有重复键的映射时，仅保留最后一个值。这是因为映射强制键的唯一性，因此较早的条目会被悄悄覆盖：

<!--versetest-->
<!-- 54 -->
```verse
WordCount:[string]int = map{
    "apple" => 0,
    "apple" => 1,
    "apple" => 2
}
# WordCount 仅包含 {"apple" => 2}
```
映射还可以迭代，让您可以完全按照插入的顺序遍历所有键值对：

<!--versetest-->
<!-- 55 -->
```verse
ExampleMap:[string]string = map{
    "a" => "apple",
    "b" => "bear",
    "c" => "candy"
}

for (Key -> Value : ExampleMap):
    Print("{Value} in ExampleMap at key {Key}")
```
这会产生：

- “ExampleMap 中的 apple 位于键 a”
- “在ExampleMap中按b键熊”
- “ExampleMap 中 c 键处的糖果”

有时您想从映射中删除条目。由于映射是不可变的，因此“删除”意味着创建一个排除给定键的新映射。例如，下面是从 `[string]int` 映射中删除元素的函数：

<!--versetest-->
<!-- 56 -->
```verse
RemoveKeyFromMap(TheMap:[string]int, ToRemove:string):[string]int =
    var NewMap:[string]int = map{}
    for (Key -> Value : TheMap, Key <> ToRemove):
        set NewMap = ConcatenateMaps(NewMap, map{Key => Value})
    return NewMap
```
映射的键类型必须属于类 `comparable`，这保证可以检查两个键是否相等。所有基本标量类型（例如 `int`、`float`、`rational`、`logic`、`char` 和 `char32`）都是可比较的，复合类型（例如数组、映射、元组和`struct` 其组件具有可比性。  类和接口（没有 `<unique>` 说明符）不能用作键，因为它们的实例不提供内置的相等概念。但是，标有 `<unique>` 的类和接口可以用作键，因为它们支持基于身份的相等性。

并非所有类型都可以用作映射键。类型必须是可比较的——这意味着可以检查该类型的值是否相等。以下是有关什么可以用作映射键、什么不能用作映射键的综合指南：

**可用作映射键的类型：**

- `logic` - 布尔值
- `int`、`float`、`rational` - 数字类型
- `char`、`char32` - 字符类型
- `string` - 文本
- 枚举 - 自定义枚举类型
- 标有 `<unique>` 的类和接口
- `?t`，其中 `t` 是可比较的 - 可比较类型的选项
- `[]t`，其中 `t` 是可比较的 - 可比较元素的数组
- `tuple(t0, t1, ...)`，其中所有元素都是可比较的 - 可比较类型的元组
- `struct` 类型，其中所有字段都具有可比性

### 映射键类型示例

以下示例演示了用作映射键的各种类似类型：

**元组作为键：**

<!--versetest-->
<!-- 71 -->
```verse
# 使用元组键的坐标系
Grid:[tuple(int, int)]string = map{
    (0, 0) => "origin",
    (1, 0) => "east",
    (0, 1) => "north",
    (-1, 0) => "west"
}
```
**结构作为键：**

<!--versetest-->
<!-- 72 -->
```verse
point := struct{X:int, Y:int}
Landmarks:[point]string = map{
    point{X := 0, Y := 0} => "origin",
    point{X := 10, Y := 20} => "tower"
}
```
**枚举作为键：**

<!--versetest-->
<!-- 73 -->
```verse
direction := enum{North, South, East, West}
Instructions:[direction]string = map{
    direction.North => "Go up",
    direction.South => "Go down",
    direction.East => "Turn right",
    direction.West => "Turn left"
}
```
**有理数作为键：**

<!--versetest-->
<!-- 74 -->
```verse
Fractions:[rational]string = map{
    1/2 => "half",
    1/3 => "third",
    2/3 => "two thirds",
    1/1 => "whole"
}
```
等效的有理数（如 `1/1` 和 `2/2`）被视为相同的密钥。

**Unicode 字符作为键：**

<!--versetest-->
<!-- 75 -->
```verse
Translations:[char32]string = map{
    '😀' => "grinning face",
    '你' => "you (Chinese)",
    '好' => "good (Chinese)"
}
```
**特殊浮点值：**

浮点特殊值（例如 `NaN` 和 `Inf`）可以用作映射键：

<!--versetest-->
<!-- 76 -->
```verse
SpecialFloats:[float]string = map{
    Inf => "positive infinity",
    -Inf => "negative infinity",
    0.0 => "zero"
}
```
**不能用作映射键的类型：**

- `false` - 空型
- `type` - 输入值本身
- 函数类型如 `t -> u`
- `subtype(t)` - 子类型表达式
- 类（无 `<unique>`）
- 接口（无 `<unique>`）

尝试使用不可比较类型作为键会导致编译时错误。

与数组一样，映射从所有键和值的公共超类型推断其键和值类型。当您创建具有混合但相关类型的映射时，Verse 会查找包含所有键和所有值的最具体类型：

<!--versetest
class1 := class<unique> {}
class2 := class<unique>(class1) {}
class3 := class<unique>(class1) {}
-->
<!-- 57 -->
```verse
    Instance2 := class2{}
    Instance3 := class3{}

    # 键类型为class1（class2和class3的公共超类型）
    # 值类型仍为 int
    MixedKeyMap : [class1]int = map{Instance2 => 1, Instance3 => 2}
```
### 顺序和平等

映射保留插入顺序，这对于迭代和相等检查都很重要。当您将条目插入映射时，它们会保持插入顺序。仅当两个映射包含相同的键值对**且顺序相同**时，它们才是相等的：

<!--versetest-->
<!-- 58 -->
```verse
var Scores:[string]int = map{}
set Scores["Alice"] = 100
set Scores["Bob"] = 90
set Scores["Carol"] = 95

# 这张映射等于分数
Map1 := map{"Alice" => 100, "Bob" => 90, "Carol" => 95}
Scores = Map1

# 这张映射不等于分数 - 顺序不同
Map2 := map{"Bob" => 90, "Alice" => 100, "Carol" => 95}
not Scores = Map2
```
当映射文字包含重复的键时，最后一个值会覆盖较早的值，但键的位置仍保持其**第一次**出现时的位置：

<!--versetest
-->
<!-- 59 -->
```verse
Map := map{0 => "zero", 1 => "one", 0 => "ZERO", 2 => "two"}
# 等价于 map{0 => "ZERO", 1 => "one", 2 => "two"}
# 键 0 保持在原来的位置
```
映射上的迭代将按照保留的插入顺序访问条目。

### 空映射类型

空映射可以从上下文推断它们的键和值类型，类似于数组：

<!--versetest
-->
<!-- 60 -->
```verse
StringToInt : [string]int = map{}  # 具有推断类型的空映射

var Scores : [string]int = map{}
set Scores = ConcatenateMaps(Scores, map{"Alice" => 100})
```
如果没有类型上下文，您可能需要提供显式类型注释。

### 方差

映射的键和值类型都是**协变**的。在以下情况下，映射类型 `[K1]V1` 是 `[K2]V2` 的子类型：

- **密钥是协变的**：`K1` 是 `K2` 的子类型（更具体的密钥 → 更通用的密钥）
- **值是协变的**：`V1` 是 `V2` 的子类型（更具体的值 → 更通用的值）

这种协方差是必要的，因为映射迭代公开了键类型。当您迭代映射时，您会收到实际的键对象，该对象必须可以作为声明的键类型安全地使用。

虽然映射类型是协变的，但映射查找操作接受的键为 `comparable` 的键类型，这可能看起来是逆变的。这为查找提供了便利，但不会影响映射类型本身的差异。

<!--versetest
animal := class<unique> {}
dog := class<unique>(animal) {}
-->
<!-- 61 -->
```verse
# 假设
# animal := class<unique> {}
# dog := class<unique>(animal) {}

# 映射类型借款为 COVARIANT
DogMap : [dog]int = map{dog{} => 1}
AnimalMap : [animal]int = DogMap  # ✓ 作品 - 协变分配

# 映射查找操作看起来像逆变
MyDogMap : [dog]int = map{dog{} => 42}
DogKey : dog = dog{}
SupertypeKey : animal = DogKey  # 指向同一个狗实例

# 使用确切的键类型查找：
if (Val1 := MyDogMap[DogKey]) {}  # ✓ 作品

# 使用超类型键查找 - 也有效！
if (Val2 := MyDogMap[SupertypeKey]) {}  # ✓ 也有效

# 这是可行的，因为查找只需要键“可比较”
# 映射的键类型。两个键都引用同一个唯一对象。
```
通过 `set` 修改可变映射时，只能插入与映射声明类型匹配的键和值：

<!--versetest

animal := class<unique> {}
dog := class<unique>(animal) {}

class1 := class<unique> {}
class2 := class<unique>(class1) {}
-->
<!-- 62 -->
```verse
var Map : [dog]int = map{}
Key2 : dog = dog{}
Key1 : animal = Key2

set Map[Key2] = 1      # 有效 - 精确类型匹配
# set Map[Key1] = 2    # ERROR - cannot use supertype as key
```
### 嵌套映射

映射可以包含其他映射作为值，从而实现多级关联：

<!--versetest
-->
<!-- 63 -->
```verse
# 从字符串映射到整数到字符串的映射
NestedMap : [string][int]string = map{
    "numbers" => map{1 => "one", 2 => "two"},
    "letters" => map{0 => "a", 1 => "b"}
}

if (InnerMap := NestedMap["numbers"]):
    if (Value := InnerMap[1]):
        Value = "one"
```
如果映射中的所有值和键都是可比较的，则映射可以用作其他映射的键。

### 连接映射

`ConcatenateMaps()` 函数将两个映射合并为一个映射：

<!--versetest
M():void =
    Map1 := map{1 => "one"}
    Map2 := map{2 => "two"}
    Result := ConcatenateMaps(Map1, Map2)
<#
-->
<!-- 64 -->
```verse
ConcatenateMaps(Map1:[k]v, Map2:[k]v):[k]v
```
<!-- #> -->

`ConcatenateMaps()` 恰好使用两张映射并将它们合并为一张。当映射包含重复键时，**第二个**映射中的值会覆盖第一个映射中的值：

<!--versetest-->
<!-- 65 -->
```verse
Map1 := map{1 => "one", 2 => "two"}
Map2 := map{3 => "three", 4 => "four"}

Combined := ConcatenateMaps(Map1, Map2)
Combined = map{1 => "one", 2 => "two", 3 => "three", 4 => "four"}

# 要合并两个以上的映射，链式调用
Map3 := map{5 => "five"}
All := ConcatenateMaps(ConcatenateMaps(Map1, Map2), Map3)
All = map{1 => "one", 2 => "two", 3 => "three", 4 => "four", 5 => "five"}
```
**处理重复键：**

<!--versetest-->
<!-- 66 -->
```verse
Base := map{1 => "original", 2 => "base"}
Override := map{2 => "updated", 3 => "new"}

Result := ConcatenateMaps(Base, Override)
Result = map{1 => "original", 2 => "updated", 3 => "new"}
# 关键2被后来的映射覆盖了
```
从右到左的优先级确保后面的映射优先，从而实现自然的覆盖模式。

**空映射：**

<!--versetest-->
<!-- 67 -->
```verse
# 空映射没有任何贡献
FirstMap := map{1 => "a"}
EmptyMap : [int]string = map{}

Combined := ConcatenateMaps(FirstMap, EmptyMap)
Combined = map{1 => "a"}
```
**类型限制：**

生成的映射类型将强制为输入映射中最具体的共享类型：

<!--versetest-->
<!-- 68 -->
```verse
# 具有相同键和值类型的映射
FirstMap := map{1 => "a"}
SecondMap := map{2 => "b"}
Combined := ConcatenateMaps(FirstMap, SecondMap)
Combined = map{1 => "a", 2 => "b"}
```
<a id="weak-maps"></a>
## 弱映射

`weak_map` 类型是 `map` 的专用超类型，专为具有弱键引用的持久数据存储而设计。它的行为与用于单独条目访问的普通映射类似，但故意限制批量操作。您不能询问其长度，不能迭代其条目，也不能使用 `ConcatenateMaps`。这些限制可实现高效的弱引用语义以及与 Verse 持久性系统的集成。

`weak_map` 使用 `weak_map(k,v)` 进行声明，并且可以从普通的 `map{}` 进行初始化。更新和访问单个条目的工作方式与常规映射相同：

<!--versetest
-->
<!-- 69 -->
```verse
var MyWeakMap:weak_map(int,int) = map{}

set MyWeakMap[0] = 1
Value := MyWeakMap[0]         # 成功为 1

set MyWeakMap = map{0 => 2}   # 重新分配仍然有效（对于局部变量）
```
由于 `weak_map` 是 `map` 的超类型，因此您可以在需要时将常规映射分配给weak_map 变量，但一旦使用弱映射，您将失去计数或迭代的能力。

### 限制

**无长度属性：**

<!--versetest
M():void =
    var MyWeakMap:weak_map(int,int) = map{1 => 2}
<#
-->
<!-- 70 -->
```verse
var MyWeakMap:weak_map(int,int) = map{1 => 2}
# 错误：weak_map 没有 Length 属性
# Size := MyWeakMap.Length
```
<!-- #> -->

**无迭代：**

<!--versetest
M():void =
    var MyWeakMap:weak_map(int,int) = map{1 => 2, 3 => 4}
<#
-->
<!-- 71 -->
```verse
var MyWeakMap:weak_map(int,int) = map{1 => 2, 3 => 4}
# 错误：无法迭代weak_map
# for (Entry : MyWeakMap) {}
```
<!-- #> -->

**无法强制比较：**

<!--versetest
M():void =
    var MyWeakMap:weak_map(int,int) = map{}
<#
-->
<!-- 72 -->
```verse
var MyWeakMap:weak_map(int,int) = map{}
# 错误：weak_map 无法转换为可比较的
# C:可比较 = MyWeakMap
```
<!-- #> -->

**无法加入常规映射：**

<!--versetest
M():void =
    var MyWeakMap:weak_map(int,int) = map{1 => 2}
<#
-->
<!-- 73 -->
```verse
var MyWeakMap:weak_map(int,int) = map{1 => 2}

# 错误：无法将weak_map与常规映射连接以生成常规映射
# Result:[int]int = if (true?) then MyWeakMap else map{3 => 4}
```
<!-- #> -->

### 模块范围的weak_map变量

当使用 `weak_map` 作为模块范围变量（用于持久数据）时，还有其他限制：

**无法阅读完整映射：**

<!--versetest
M():void =
    var LocalData:weak_map(int, int) = map{}
    if (set LocalData[1] = 100) {}
<#
-->
<!-- 74 -->
```verse
# 中间范围的持久weak_map
var PlayerData:weak_map(player, int) = map{}

GetAllData():weak_map(player, int) =
    # 错误：无法读取weak_map的完整模块范围
    # 玩家数据
    map{}  # 必须构建新映射
```
<!-- #> -->

**无法写出完整的映射：**

<!--versetest
M():void =
    var LocalData:weak_map(int, int) = map{}
    set LocalData = map{}
<#
-->
<!-- 75 -->
```verse
var PlayerData:weak_map(player, int) = map{}

ResetAllData():void =
    # 错误：无法替换模块范围的weak_map
    # set PlayerData = map{}
    {}
```
<!-- #> -->

**个人入场访问作品：**

<!--versetest
M()<transacts>:void =
    var LocalData:weak_map(int, int) = map{}

    GetScore(Key:int):int =
        if (Score := LocalData[Key]):
            Score
        else:
            0

    SetScore(Key:int, Score:int)<transacts>:void =
        if (set LocalData[Key] = Score) {}
<#
-->
<!-- 76 -->
```verse
var PlayerData:weak_map(player, int) = map{}

# 好的：可以读取单个条目
GetPlayerScore(Player:player):int =
    if (Score := PlayerData[Player]):
        Score
    else:
        0

# 好的：可以写单独的条目
SetPlayerScore(Player:player, Score:int):void =
    set PlayerData[Player] = Score
```
<!-- #> -->

存在此限制是因为模块范围的weak_maps与持久性系统集成，该系统仅跟踪单个条目更新，而不是完整的映射替换。

对于模块范围的 `var weak_map` 变量，键和值类型都有严格的要求：

**密钥类型必须具有 `<module_scoped_var_weak_map_key>` 说明符：**

<!--versetest
regular_class := class<unique> {}

M():void =
    var LocalData:weak_map(regular_class, int) = map{}
<#
-->
<!-- 77 -->
```verse
# 有效的密钥类型
persistent_class := class<unique><allocates><computes><persistent><module_scoped_var_weak_map_key> {}

var ValidData:weak_map(persistent_class, int) = map{}

# 无效的密钥类型 - 缺少说明符
regular_class := class<unique><allocates><computes> {}

# 错误：关键类型缺失 <module_scoped_var_weak_map_key>
# var InvalidData:weak_map(regular_class, int) = map{}
```
<!-- #> -->

**值类型必须是持久的：**

<!--versetest
regular_struct := struct:
    Value:int

M():void =
    var LocalData:weak_map(int, regular_struct) = map{}
<#
-->
<!-- 78 -->
```verse
persistent_class := class<unique><allocates><computes><persistent><module_scoped_var_weak_map_key> {}

# Valid：持久值类型
persistable_struct := struct<persistable>:
    Value:int

var ValidData:weak_map(persistent_class, persistable_struct) = map{}

# 无效：非持久值类型
regular_struct := struct:
    Value:int

# 错误：值类型必须是持久的
# var InvalidData：weak_map（persistent_class，regular_struct）=map{}
```
<!-- #> -->

满足要求的常见密钥类型：

- **`player`** - 玩家特定数据的标准密钥类型
- **`persistent_key`** - 具有有效性跟踪的自定义持久密钥
- **`session_key`** - 不会跨会话持续存在的瞬态密钥

### 协方差

`weak_map` 类型的键类型是**协变**，这意味着您可以将weak_map 与子类键类型一起使用，其中需要父类键类型：

<!--versetest
base_class := class<unique> {}
derived_class := class(base_class) {}

value_struct := struct {}

CreateDerivedMap():weak_map(derived_class, value_struct) =
    map{}

F():void=
    BaseMap:weak_map(base_class, value_struct) = CreateDerivedMap()
<#
-->
<!-- 79 -->
```verse
base_class := class<unique> {}
derived_class := class(base_class) {}

value_struct := struct {}

CreateDerivedMap():weak_map(derived_class, value_struct) =
    map{}

# OK：weak_map在按键类型上是协变的
BaseMap:weak_map(base_class, value_struct) = CreateDerivedMap()

# 错误 3509：不能走相反的路（逆变）
# DerivedMap：weak_map（派生类，value_struct）= BaseMap
```
<!-- #> -->

这种协方差还允许将常规映射分配给具有兼容键类型的weak_map：

<!--versetest
base_class := class<unique> {}
derived_class := class(base_class) {}
value_struct := struct {}

F():void=
    DerivedKey := derived_class{}
    RegularMap:[derived_class]value_struct = map{DerivedKey => value_struct{}}

    WeakMap:weak_map(base_class, value_struct) = RegularMap
<#
-->
<!-- 80 -->
```verse
DerivedKey := derived_class{}
RegularMap:[derived_class]value_struct = map{DerivedKey => value_struct{}}

# OK：映射变换转换为带有协变键的weak_map
WeakMap:weak_map(base_class, value_struct) = RegularMap
```
<!-- #> -->

### 部分字段更新

当值类型是结构体或类时，您可以更新存储值的各个字段：

<!--versetest
player_data := class:
    var Level:int = 0
    var Score:int = 0

GetPlayerData()<transacts>:player_data = player_data{}

M()<transacts>:void =
    var LocalData:weak_map(int, player_data) = map{}

    UpdateLevel(Key:int, NewLevel:int)<transacts>:void =
        Data := GetPlayerData()
        set Data.Level = NewLevel
        set Data.Score = 0
        if (set LocalData[Key] = Data) {}

        if (Stored := LocalData[Key]):
            set Stored.Level = NewLevel + 1
<#
-->
<!-- 81 -->
```verse
player_data := struct<persistable>:
    Level:int
    Score:int

var PlayerData:weak_map(player, player_data) = map{}

UpdatePlayerLevel(Player:player, NewLevel:int):void =
    # 首先设置整个结构
    set PlayerData[Player] = player_data{Level := NewLevel, Score := 0}

    # 然后只更新一个字段
    set PlayerData[Player].Level = NewLevel + 1
```
<!-- #> -->

### 事务和回滚语义

与 Verse 中的所有可变状态一样，`weak_map` 更新参与事务语义。如果 `<decides>` 表达式失败，则回滚所有更改：

<!--versetest
player := class<unique> {}

F():void=
    var GameData:weak_map(player, int) = map{}
    AttemptUpdate():void =
        if:
            set GameData[player{}] = 100
            set GameData[player{}] = 200
            false?
    AttemptUpdate()
<#
-->
<!-- 82 -->
```verse
var GameData:weak_map(int, int) = map{}

AttemptUpdate():void =
    if:
        set GameData[1] = 100
        set GameData[2] = 200
        false?  # 交易失败

    # 两个更新均已回滚
    # GameData[1] 仍然不存在
    # GameData[2] 仍然不存在
```
<!-- #> -->

这适用于完整的映射替换（对于局部变量）、单个条目和部分字段更新。
