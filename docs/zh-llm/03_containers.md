# 容器类型

Verse 中的容器类型管理集合和结构化数据。可选类型表示可能存在或不存在的值。元组将多个不同类型的值分组为有序序列。数组持有零个或多个值，并支持高效的索引访问。映射将键与值关联以实现快速查找。弱映射在普通映射的基础上扩展了弱引用语义，适用于持久化存储。

下面我们逐一详细介绍每种容器类型，首先从优雅地处理值存在或不存在的可选类型开始。

## 可选类型

可选类型（optional）是一个不可变容器，要么持有 `t` 类型的值，要么什么都不持有。其类型写作 `?t`。当某个值可能存在也可能不存在时——例如在映射中查找键，或调用可能失败的函数时——可选类型非常有用。通过在类型中明确这一可能性，Verse 让程序员能够直接且一致地处理"无结果"的情况，而不是依赖临时的错误码或特殊值。

你可以使用 `option{...}` 创建非空可选类型，它把值包装到可选类型中。例如：

<!--versetest-->
<!-- 01 -->
```verse
A:?int = option{42}    # an optional containing the integer 42
```

如果要表示"没有值"，可以使用特殊常量 `false`。这就是 Verse 表示空可选类型的方式：

<!--versetest-->
<!-- 02 -->
```verse
var B:?int = false     # this optional has no element
B = false              # still empty
```

要提取可选类型的元素，可以在可选表达式后写 `?`。这会生成一个 `<decides>` 表达式，如果可选类型有元素则成功，否则失败。例如：

<!--versetest
A:?int = option{42}
-->
<!-- 03 -->
```verse
S := A? + 2            # succeeds with 44 because A contains 42
```

如果 `A` 是 `false`，那么尝试使用 `A?` 会失败，整个计算也会随之失败。一个失败的情况可以把这一点说得更清楚：

<!--versetest
B:?int = false
-->
<!-- 04 -->
```verse
# X := B? + 1       # Fails because B is false and has no element
```

这说明 Verse 如何将可选类型与效果系统紧密集成：值的存在或不存在可以导致整个计算成功或失败。

`option{...}` 形式也可以反向工作。当你有一个带有 `<decides>` 效果的计算时，将其包装在 `option{...}` 中会将其转换为可选类型。成功时得到非空可选类型；失败时得到 `false`：

<!--versetest
GetAFloatOrFail()<transacts><decides>:float = 3.14
-->
<!-- 05 -->
```verse
MaybeAFloat := option{GetAFloatOrFail[]}
```

这种对称性很重要。`?` 操作符将可选类型解包为 `<decides>` 表达式，而 `option{...}` 将 `<decides>` 表达式包装为可选类型。两者共同提供了可能失败的计算与可能缺失的值之间的平滑桥梁。

虽然可选值本身是不可变的，但你可以将其保存在变量中，并更改变量指向哪个可选类型。关键字 `set` 用于此目的：

<!--versetest-->
<!-- 06 -->
```verse
var C:?int = false
set C = option{2}      # C now refers to an optional containing 2
C? = 2                 # succeeds, since C is not empty
```

当你想要随时间跟踪成功或失败时——例如逐步计算结果，仅在成功时更新变量——这种能力非常有用。

一个常见用例是搜索可能存在也可能不存在的东西。设想一个函数 `Find`，它在整数数组中查找并返回所需元素的索引。如果元素存在，函数返回 `option{index}`；如果不存在，返回 `false`。调用者可以安全地决定后续操作：

<!--versetest
NumberArray:[]int = array{10, 20, 30}
-->
<!-- 07 -->
```verse
Find(N:[]int, X:int):?int =
    for (I := 0..N.Length-1):
        if (N[I] = X) then return option{I}
    return false
    
Idx:?int = Find(NumberArray, 20)    # returns option{1}
Y := Idx?                           # unwraps the optional
Y = 1
```

这里可选类型直接在类型中表明失败的可能性。`?` 操作符使结果可以方便地在表达式中使用，`option{...}` 则允许你将条件计算转换回可选类型。其效果是，"可能有值，可能没有"这一概念成为语言的一等公民，而不是事后才考虑的问题，程序员被鼓励以规范的方式处理值的缺失。

## 元组

元组（tuple）是一种将两个或多个值分组在一起的容器。与数组不同，元组允许你组合混合类型的值，并将它们作为一个整体处理。元组的元素按列出的顺序排列，你可以通过位置（称为索引）来访问它们。由于元素数量在编译时始终已知，元组既易于创建又使用安全。

*元组*（tuple）这个术语是从*四元组*（quadruple）、*五元组*（quintuple）、*六元组*（sextuple）等反向构词而来。从概念上讲，元组就像一个带有有序字段的未命名数据结构，或者像一个每个元素可以是不同类型的固定大小数组。

元组字面量通过将逗号分隔的表达式列表括在圆括号中来编写。例如：

<!--versetest-->
<!-- 08 -->
```verse
Tuple1 := (1, 2, 3)
```

元素的顺序很重要，因此 `(3, 2, 1)` 是一个完全不同的值。由于元组允许混合类型，你可以这样写：

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

当你想要从函数返回多个值，或者想要轻量级地对值进行分组而无需定义结构体或类的开销时，元组非常有用。元组的类型使用 `tuple` 关键字后跟元素类型来书写，但在大多数情况下可以推断。例如，你可以写 `MyTuple : tuple(int, float, string) = (1, 2.0, "three")`，或者简单地写 `MyTuple := (1, 2.0, "three")` 让编译器推断类型。

元组的元素使用基于零的索引操作符（以圆括号表示）来访问。如果 `MyTuple := (1, 2.0, "three")`，那么 `MyTuple(0)` 是整数 `1`，`MyTuple(1)` 是浮点数 `2.0`，`MyTuple(2)` 是字符串 `"three"`。由于编译器知道每个元组中的元素数量，元组索引不可能失败：任何使用越界索引的尝试都会导致编译时错误。

元组的另一个特性是*展开*（expansion）。当元组作为单个参数传递给函数时，其元素会自动展开，就好像每个元素分别传递给函数一样。例如：

<!--versetest-->
<!-- 11 -->
```verse
F(Arg1:int, Arg2:string):void =
    Print("{Arg1}, {Arg2}")

G():void =
    MyTuple := (1, "two")
    F(MyTuple)   # expands to F(1, "two")
```

元组在结构化并发中也发挥作用。`sync` 表达式产生一个结果元组，允许同时求值多个随时间展开的计算。这样，元组不仅提供了一种便捷的分组机制，还为组合并发计算奠定了基础。

元组在与数组连接操作符 `+` 和 `+=` 一起使用时，可以自动转换为数组。更多细节请参见[从元组到数组](#from-tuples-to-arrays)。

## 数组

数组（array）是一个不可变容器，持有零个或多个相同类型 `t` 的值。数组的元素是有序的，每个元素可以通过基于零的索引访问。数组的类型使用方括号书写，例如 `[]int` 或 `[]float`，并使用 `array{...}` 字面量形式创建。例如，`A : []int = array{}` 创建一个空数组，`B : []int = array{1, 2, 3}` 创建一个包含三个整数的数组。通过索引访问元素是一个可失败操作：`B[0]` 成功返回 `1`，而 `B[10]` 失败，因为索引越界。

数组可以使用 `+` 操作符连接，当声明为 `var` 时，可以使用简写操作符 `+=` 扩展。例如，`var C:[]int= B + array{4}` 使 `C` 的值为 `array{1,2,3,4}`，`set C += array{5}` 将其更新为 `array{1,2,3,4,5}`。元组也可以直接与这些操作符一起使用，并会自动转换为数组。数组的长度可以通过 `.Length` 成员获得，因此这里 `C.Length` 为 `5`。元素始终按插入顺序存储，索引从 `0` 开始。因此 `array{10,20,30}[0]` 是 `10`，任何数组的最后一个有效索引总是比其长度小一。

虽然数组本身是不可变的，但使用 `var` 声明的变量可以重新赋值给新数组，或者看起来像是改变了元素。例如，`var D:[]int = array{1,2,3}` 允许更新 `set D[0] = 3`，之后 `D` 将持有 `array{3,2,3}`。实际发生的情况是在底层创建了一个全新的数组，其中指定的元素已被更新。实际上，`set D[0] = 3` 被编译为 `set D = array{3,D[1],D[2]}`。如果有另一个变量仍在引用旧数组，它将继续存在，这意味着如果 `A` 和 `B` 都初始化为 `array{1}` 然后我们更新 `A[0]`，那么 `A` 和 `B` 将分叉：`A[0]` 现在是 `2`，而 `B[0]` 仍然是 `1`。

当你想要存储多个相同类型的值时，数组非常有用，例如游戏中的玩家列表：`Players:[]player = array{Player1,Player2}`。通过索引访问，例如 `Players[0]` 是第一个玩家。由于索引是可失败操作，它通常与 `if` 表达式或迭代结合使用。例如，以下代码安全地打印出数组的每个元素：

<!--versetest-->
<!-- 12 -->
```verse
ExampleArray : []int = array{10, 20, 30}
for (Index := 0..ExampleArray.Length - 1):
    if (Element := ExampleArray[Index]):
        Print("{Element} in ExampleArray at index {Index}")
```

输出为：

```
10 in ExampleArray at index 0
20 in ExampleArray at index 1
30 in ExampleArray at index 2
```

由于数组是值，"改变"它们总是意味着用新数组替换旧数组。使用 `var` 时，这感觉很自然，因为变量可以重新赋值。例如，你可以连接数组，然后更新一个元素：

<!--versetest-->
<!-- 13 -->
```verse
Array1 : []int = array{10, 11, 12}
var Array2 : []int = array{20, 21, 22}
set Array2 = Array1 + Array2 + array{30, 31}
if (set Array2[1] = 77) {}
```

这段代码运行后，遍历 `Array2` 将打印 `10, 77, 12, 20, 21, 22, 30, 31`。

元组可以直接用于数组的 `+` 和 `+=` 操作符，并会自动转换为数组。这提供了一种简洁的方式来添加多个元素，而无需将它们包装在 `array{...}` 中：

<!--versetest-->
<!-- 77 -->
```verse
var Numbers:[]int = array{1, 2, 3}

# Concatenate using a tuple - automatically converted to array
set Numbers = Numbers + (4, 5, 6)

# Shorthand form also works with tuples
set Numbers += (7, 8, 9)

# Result: array{1, 2, 3, 4, 5, 6, 7, 8, 9}
```

这种通过操作符进行的元组到数组的转换与函数调用中的元组展开是不同的。对于操作符，元组元素作为单独项添加到数组中，就像你写了 `array{4, 5, 6}` 一样。

数组也可以嵌套形成多维结构，类似于表格的行和列。例如，以下代码创建一个二维 4×3 整数数组：

<!--versetest-->
<!-- 14 -->
```verse
var Counter : int = 0
Example : [][]int =
    for (Row := 0..3):
        for (Column := 0..2):
            set Counter += 1
```

此数组可以可视化为：

```
Row 0:  1  2  3
Row 1:  4  5  6
Row 2:  7  8  9
Row 3: 10 11 12
```

并通过两个索引访问：`Example[0][0]` 是 `1`，`Example[0][1]` 是 `2`，`Example[1][0]` 是 `4`。你可以通过嵌套迭代遍历所有行和列。Verse 中的数组不限于矩形形状：每行可以有不同长度，形成锯齿状结构。例如：

<!--versetest-->
<!-- 15 -->
```verse
Example : [][]int =
    for (Row := 0..3):
        for (Column := 0..Row):
            Row * Column
```

生成一个行长度递增的三角形数组：第 0 行没有元素，第 1 行有一个 `0`，第 2 行有 `0, 2, 4`，第 3 行有 `0, 3, 6, 9`。

具有复杂初始化逻辑的嵌套数组可以自然地用作类字段默认值：

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
# Game board with tile grid
tile_class := class:
    Position:tuple(int, int)
    var IsOccupied:logic = false

game_board := class:
    # Initialize 10×10 grid of tiles
    Tiles:[][]tile_class =
        for (Y := 0..9):
            for (X := 0..9):
                tile_class{Position := (X, Y)}

    # Get tile at specific position
    GetTile(X:int, Y:int)<computes><decides>:tile_class =
        Row := Tiles[Y]
        Row[X]

# Create board instance
Board := game_board{}

# Access specific tile
if (CenterTile := Board.GetTile[5, 5]):
    set CenterTile.IsOccupied = true
```
<!--
#>
   Board := game_board{}
   if (CenterTile := Board.GetTile[5, 5]):
       set CenterTile.IsOccupied = true
-->

当你使用 `array{}` 创建空数组时，Verse 会根据变量的类型注解推断元素类型：

<!--versetest-->
<!-- 17 -->
```verse
IntArray : []int = array{}       # Empty array of integers
FloatArray : []float = array{}   # Empty array of floats
```

如果没有类型注解，编译器无法确定你想要什么类型的数组，因此你必须显式提供类型，或至少包含一个能确定类型的元素。

数组根据所有元素的公共超类型来确定其元素类型。当你创建的数组包含不同但相关的类型的值时，Verse 会找到能包含所有元素的最具体类型：

<!--versetest
class1 := class {}
class2 := class(class1) {}
class3 := class(class1) {}
-->
<!-- 18 -->
```verse
# Array element type is class1 (common supertype)
MixedArray : []class1 = array{class2{}, class3{}}
```

这适用于任何类型层次结构，包括接口。如果你混合完全不相关的类型，元素类型将变为 `any`：

<!--versetest-->
<!-- 19 -->
```verse
# Array of comparable - different types sharing comparable in common
DisjointArray : []comparable = array{42, 13.37, true}

# Array of any - different types with no common supertype
AnyArray : []any = array{15.61, "Message", void}
```

### 从元组到数组

Verse 在特定上下文中提供元组和数组之间的自动转换，使得函数调用更加灵活，同时保持类型安全。这种转换是**单向的**：元组可以变为数组，但数组不能变为元组。

当所有元组元素与数组的元素类型兼容时，元组可以直接赋值给数组变量：

<!--versetest-->
<!-- 20 -->
```verse
# Homogeneous tuple to array
X:tuple(int, int) = (1, 2)
Y:[]int = X            # Valid - both elements are int
Y[1] = 2               # Can use as normal array

# Longer tuples work too
NumTuple:tuple(int, int, int, int) = (1, 2, 3, 4)
NumberArray:[]int = NumTuple
NumberArray.Length = 4
```

此转换会创建一个包含元组所有元素（按顺序）的数组。

当一个函数只有一个数组参数时，你可以使用多个参数调用它，这些参数会自动形成一个数组：

<!--versetest-->
<!-- 21 -->
```verse
ProcessNumbers(Nums:[]int):int = Nums.Length

# All these are equivalent:
ProcessNumbers(1, 2, 3)           # Multiple args → array
ProcessNumbers((1, 2, 3))         # Tuple literal → array
Values := (1, 2, 3)
ProcessNumbers(Values)             # Tuple variable → array
```

这种"类可变参数"语法提供了便利，同时保持了函数签名的简洁：

<!--versetest-->
<!-- 22 -->
```verse
Sum(Nums:[]int):int =
    var Total:int = 0
    for (N : Nums):
        set Total += N
    Total

Sum(1, 2, 3, 4)                   # Returns 10
Sum((5, 6))                       # Returns 11
Values := (10, 20, 30)
Sum(Values)                       # Returns 60
```

数组转换仅在**所有元组元素都与数组的元素类型兼容**时成功：

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
# Homogeneous tuple - all int
F(X:[]int):int = X.Length
F(1, 2, 3)                        # Valid

# Subtype compatibility
entity := class:
    ID:int

player := class(entity):
    Name:string

ProcessEntities(E:[]entity):int = E.Length

P := player{ID := 1, Name := "Alice"}
E := entity{ID := 2}
ProcessEntities(P, E)             # Valid - player is subtype of entity
```
<!-- #> -->

接受 `[]any` 的函数可以接受**任何元组**，无论元素类型如何：

<!--versetest-->
<!-- 24 -->
```verse
GetLength(Items:[]any):int = Items.Length

# All valid - any tuple works
GetLength(1, 2.0)                 # Mixed types OK
GetLength("a", 42, true)          # Different types OK
GetLength((1, 2.0, "hello"))      # Explicit tuple OK
```

这使得可以编写处理异构数据的泛型函数。

当元组元素共享公共超类型（通过继承或接口）时，它们会转换为该超类型的数组：

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

# Valid - both classes implement interface1
ProcessInterfaces(X, Y)           # Returns 2
```
<!-- #> -->

编译器找到最具体的公共超类型，并将其用作数组的元素类型。

元组到数组的转换适用于嵌套结构：

**嵌套数组：**

<!--versetest
ProcessMatrix(Matrix:[][]int):int = Matrix.Length
-->
<!-- 26 -->
```verse
# Nested tuples → nested arrays
MatrixData := ((1, 2), (3, 4))
ProcessMatrix(MatrixData)             # Valid

# Or with explicit nesting
ProcessMatrix((1, 2), (3, 4))   # Valid
```

**可选数组：**

<!--versetest-->
<!-- 27 -->
```verse
ProcessOptional(Items:?[]int)<decides>:int = Items?[0]

# Optional tuple → optional array
Values := option{(1, 2)}
ProcessOptional[Values]           # Valid
```

**包含数组的元组：**

<!--versetest-->
<!-- 28 -->
```verse
ProcessComplex(Data:tuple([]int, int)):int = Data(0).Length

# First element of tuple becomes array
ProcessComplex(((1, 2), 3))       # Valid - (1,2) becomes []int
```

### 数组切片

数组通过 `.Slice` 方法支持切片操作，用于提取数组的连续部分。切片是一个可失败操作——只有在索引有效时才会成功。

双参数形式 `Array.Slice[Start, End]` 返回从索引 `Start` 到 `End`（不包括 `End`）的元素：

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

如果索引为负数、越界，或者 `Start` 大于 `End`，切片会失败。当 `Start` 等于 `End` 时，创建空切片是有效的：

<!--versetest
NumArray:[]int = array{10, 20, 30, 40, 50}
-->
<!-- 31 -->
```verse
NumArray.Slice[2, 2]  # Succeeds with array{}
# NumArray.Slice[2, 1]  # Would fail - Start > End
# NumArray.Slice[-1, 2] # Would fail - negative index
# NumArray.Slice[0, 10] # Would fail - End beyond array length
```

切片也适用于字符串和字符元组，返回字符串：

<!--versetest-->
<!-- 32 -->
```verse
"hello".Slice[1, 4] = "ell"
```

### 数组方法

数组提供了用于搜索、移除和替换元素的内在方法。这些操作会创建新数组而不是修改现有数组，从而保持 Verse 的不可变性保证。

`Find()` 方法搜索元素的第一个出现位置并返回其索引，如果未找到则失败：

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
    # Index is 1 (first occurrence)
    Print("Found at index {Index}")

if (not NumArray.Find[0]):
    # Element not in array
    Print("Not found")

# With strings
Strings := array{"Apple", "Orange", "Strawberry"}

if (Index := Strings.Find["Strawberry"]):
    Print("Found at {Index}") # Prints "Found at 2"
```

`Find()` 在成功时返回第一个找到的索引（`int`），如果未找到元素则失败，从而无需异常或特殊哨兵值即可安全处理缺失元素。

`RemoveFirstElement()` 移除第一个出现位置：

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
    # Updated is array{1, 3, 1, 2, 3}
    Print("Removed first 2")

if (not NumArray.RemoveFirstElement[0]):
    # Element not found
    Print("Element not in array")
```

`RemoveAllElements()` 移除所有出现位置：

<!--versetest-->
<!-- 37 -->
```verse
NumArray := array{1, 2, 3, 1, 2, 3}
Updated := NumArray.RemoveAllElements(2)
Updated = array{1, 3, 1, 3}

# Returns unchanged array if element not found
Same := NumArray.RemoveAllElements(0)
Same = array{1, 2, 3, 1, 2, 3}
```

`Remove()` 移除指定位置的元素：

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
    # Updated is array{10, 30, 40}

# Negative index would fail
# if (not NumArray.Remove[-1,0]):

# Out of bounds would fail
# if (not NumArray.Remove[6,10]):
```

`ReplaceFirstElement()` 替换第一个出现位置：

<!--NoCompile-->
```verse
Array.ReplaceFirstElement(OldValue:t, NewValue:t where t:subtype(comparable))<decides>:[]t
```

<!--versetest-->
<!-- 39 -->
```verse
NumArray := array{1, 2, 3, 1, 2, 3}

if (Updated := NumArray.ReplaceFirstElement[2, 99]):
    # Updated is array{1, 99, 3, 1, 2, 3}

if (not NumArray.ReplaceFirstElement[0, 99]):
    # Element not found - fail
```

`ReplaceAllElements()` 替换所有出现位置：

<!--NoCompile-->
```verse
Array.ReplaceAllElements(OldValue:t, NewValue:t where t:subtype(comparable)):[]t
```

<!--versetest-->
<!-- 40 -->
```verse
NumArray := array{1, 2, 3, 1, 2, 3}
Updated := NumArray.ReplaceAllElements(2, 99)
# Updated is array{1, 99, 3, 1, 99, 3}

# Returns unchanged array if element not found
Same := NumArray.ReplaceAllElements(0, 99)
# Same is array{1, 2, 3, 1, 2, 3}
```

`ReplaceElement()` 替换指定索引处的元素：

<!--NoCompile-->
```verse
Array.ReplaceElement(Index:int, NewValue:t)<decides>:[]t
```

<!--versetest-->
<!-- 41 -->
```verse
NumArray := array{10, 20, 30, 40}

if (Updated := NumArray.ReplaceElement[1, 99]):
    # Updated is array{10, 99, 30, 40}

if (not NumArray.ReplaceElement[-1, 99]):
    # Negative index fails

if (not NumArray.ReplaceElement[10, 99]):
    # Out of bounds fails
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

# Works with different length patterns
NumArray2 := array{1, 2, 2, 1, 2, 2, 1}
Updated2 := NumArray2.ReplaceAll(array{2, 2}, array{9, 9, 9})
Updated2 = array{1, 9, 9, 9, 1, 9, 9, 9, 1}

# Strings are []char
SomeMessage := "Hey, this is a string, Hello!"
NewMessage := SomeMessage.ReplaceAll("He", "Apples") # Note: Case sensitive!
NewMessage = "Applesy, this is a string, Applesllo!"
```

`ReplaceAll()` 查找与 `Pattern` 匹配的连续子序列，并将每个匹配替换为 `Replacement`。替换内容可以是任意长度，包括空。

`Insert()` 在指定位置插入一个元素：

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
    # Updated is array{10, 20, 30, 40}
    # Inserted at index 2, existing elements shift right

# Can insert at start
if (Updated2 := NumArray.Insert[0, array{5}]):
    # Updated2 is array{5, 10, 20, 40}

# Can insert at end (index = Length is valid)
if (Updated3 := NumArray.Insert[NumArray.Length, array{50}]):
    # Updated3 is array{10, 20, 40, 50}

# Out of bounds fails
if (not NumArray.Insert[-1, array{5}]):
    # Negative index fails

if (not NumArray.Insert[NumArray.Length + 1, array{5}]):
    # Beyond Length fails
```

`Concatenate()` 函数将一个数组的数组组合成一个扁平的数组：

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

得益于元组到数组的强制转换，你可以直接传递多个数组参数，它们会自动收集到数组的数组参数中。与仅连接两个数组的 `+` 操作符不同，`Concatenate()` 接受任意数量的数组参数：

<!--versetest-->
<!-- 45 -->
```verse
# Empty call returns empty array
Empty := Concatenate()
Empty = array{}

# Single array passed as an array-of-arrays
Single := Concatenate(array{array{1, 2, 3}})
Single = array{1, 2, 3}

# Two arrays
TwoArrays := Concatenate(array{1, 2}, array{3, 4})
TwoArrays = array{1, 2, 3, 4}

# Multiple arrays
Many := Concatenate(array{1}, array{2, 3}, array{4}, array{5, 6})
Many = array{1, 2, 3, 4, 5, 6}
```

空数组被无缝处理：

<!--versetest-->
<!-- 46 -->
```verse
# Empty arrays contribute nothing
Result1 := Concatenate(array{1, 2}, array{}, array{3})
Result1 = array{1, 2, 3}
Result2 := Concatenate(array{}, array{}, array{})
Result2 = array{}

# Can concatenate many empty arrays
# EmptyResult := Concatenate(for (I := 0..100): array{})
# EmptyResult = array{}
```

**与 `+` 操作符的比较：**

<!--versetest-->
<!-- 48 -->
```verse
# Using + operator (binary)
First := array{1, 2}
Second := array{3, 4}
Third := array{5, 6}
ChainedResult := First + Second + Third  # Works but requires multiple operations

# Using Concatenate
ConcatenatedResult := Concatenate(First, Second, Third)  # Single operation

ChainedResult = ConcatenatedResult
```

因此，Verse 中的数组是不可变的值，具有可预测的行为，但通过 `var` 提供了可变变量的便利。它们可以连接、迭代、切片、搜索和操作，成为语言中最灵活、最基础的数据结构之一。

## 映射

映射（map）是核心容器类型之一，与数组和可选类型并列。如果说数组是由整数索引的有序序列，可选类型是最小的容器（持有零个或一个值），那么映射则概括了这两种概念：像数组一样，映射提供高效的查找，但不受限于整数索引，而是允许任何*可比较*（comparable）类型作为键。你可以把映射看作是由任意键索引的数组，或者是一个更大的、可以同时持有多个键值对的可选类型。

映射是一个不可变的关联容器，存储零个或多个类型为 `[k]v` 的键值对，写作 `(Key:k, Value:v)`。映射是将值与值关联的标准方式：你提供一个键，映射返回与该键关联的值。

当你想存储自然以非整数位置为索引的数据时，映射非常有用。例如，你可能想存储不同对象的重量，以它们的名称为键：

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

在映射中查找值使用方括号。如果键存在，表达式成功；如果键不存在，则失败。查找被设计为快速执行，具有摊还 *O(1)* 的时间复杂度：

<!--versetest
Weights:[string]float = map{"ant" => 0.0001}
-->
<!-- 51 -->
```verse
Weights["ant"]  # succeeds, since "ant" key exists in map
# Weights["car"] would fail
```

如果你想更新存储在变量中的映射，使用 `set`。这既适用于添加新的键值对，也适用于更改现有键的值。如果你尝试修改不存在的键，操作会失败：

<!--versetest-->
<!-- 52 -->
```verse
var Friendliness:[string]int = map{"peach" => 1000}

set Friendliness["pelican"] = 17     # succeed: add a new value with the given key
set Friendliness["peach"] += 2000    # succeed: update an existing value with the given key
# set Friendliness["tomato"] += 1000   # would fail: can't update a value which key does not exist
```

每个映射还带有其大小，可通过 `Length` 字段访问：

<!--versetest
Friendliness:[string]int = map{"peach" => 1000, "pelican" => 17}
-->
<!-- 53 -->
```verse
Friendliness.Length = 2         # succeed: the map has 2 entries
```

当构造包含重复键的映射时，仅保留最后一个值。这是因为映射强制键的唯一性，因此较早的条目会被静默覆盖：

<!--versetest-->
<!-- 54 -->
```verse
WordCount:[string]int = map{
    "apple" => 0,
    "apple" => 1,
    "apple" => 2
}
# WordCount contains only {"apple" => 2}
```

映射也可以被迭代，让你按插入顺序遍历所有键值对：

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

输出为：

- "apple in ExampleMap at key a"
- "bear in ExampleMap at key b"
- "candy in ExampleMap at key c"

有时你想从映射中移除一个条目。由于映射是不可变的，"移除"意味着创建一个排除指定键的新映射。例如，以下是一个从 `[string]int` 映射中移除元素的函数：

<!--versetest-->
<!-- 56 -->
```verse
RemoveKeyFromMap(TheMap:[string]int, ToRemove:string):[string]int =
    var NewMap:[string]int = map{}
    for (Key -> Value : TheMap, Key <> ToRemove):
        set NewMap = ConcatenateMaps(NewMap, map{Key => Value})
    return NewMap
```

映射的键类型必须属于 `comparable` 类，这保证两个键可以进行相等性检查。所有基本标量类型（如 `int`、`float`、`rational`、`logic`、`char` 和 `char32`）都是可比较的，组合类型（如数组、映射、元组以及其所有组件可比较的 `struct`）也是如此。类（class）和接口（interface）（没有 `<unique>` 说明符）不能用作键，因为它们的实例没有内置的相等性概念。然而，标记了 `<unique>` 的类和接口可以用作键，因为它们支持基于身份的相等性检查。

并非所有类型都可以用作映射键。类型必须是可比较的——这意味着该类型的值可以进行相等性检查。以下是关于哪些类型可以用作映射键的全面指南：

**可用作映射键的类型：**

- `logic` - 布尔值
- `int`、`float`、`rational` - 数值类型
- `char`、`char32` - 字符类型
- `string` - 文本
- 枚举（enum） - 自定义枚举类型
- 标记了 `<unique>` 的类和接口
- `?t` 其中 `t` 可比较 - 可比较类型的可选类型
- `[]t` 其中 `t` 可比较 - 可比较元素的数组
- `tuple(t0, t1, ...)` 其中所有元素可比较 - 可比较类型的元组
- `struct` 类型，其中所有字段可比较

### 映射键类型示例

以下示例展示了用作映射键的各种可比较类型：

**元组作为键：**

<!--versetest-->
<!-- 71 -->
```verse
# Coordinate system using tuple keys
Grid:[tuple(int, int)]string = map{
    (0, 0) => "origin",
    (1, 0) => "east",
    (0, 1) => "north",
    (-1, 0) => "west"
}
```

**结构体作为键：**

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

等价的有理数（如 `1/1` 和 `2/2`）被视为同一个键。

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

**特殊浮点数值：**

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

- `false` - 空类型
- `type` - 类型值本身
- 函数类型，如 `t -> u`
- `subtype(t)` - 子类型表达式
- 类（没有 `<unique>`）
- 接口（没有 `<unique>`）

尝试使用不可比较的类型作为键会导致编译时错误。

与数组类似，映射根据所有键和值的公共超类型推断其键和值类型。当你创建的映射包含混合但相关的类型时，Verse 会找到能包含所有键和所有值的最具体类型：

<!--versetest
class1 := class<unique> {}
class2 := class<unique>(class1) {}
class3 := class<unique>(class1) {}
-->
<!-- 57 -->
```verse
    Instance2 := class2{}
    Instance3 := class3{}

    # Key type is class1 (common supertype of class2 and class3)
    # Value type remains int
    MixedKeyMap : [class1]int = map{Instance2 => 1, Instance3 => 2}
```

### 顺序与相等性

映射保持插入顺序，这对于迭代和相等性检查都很重要。当你向映射插入条目时，它们保持插入时的顺序。两个映射相等仅当它们包含相同的键值对**且顺序相同**：

<!--versetest-->
<!-- 58 -->
```verse
var Scores:[string]int = map{}
set Scores["Alice"] = 100
set Scores["Bob"] = 90
set Scores["Carol"] = 95

# This map equals Scores
Map1 := map{"Alice" => 100, "Bob" => 90, "Carol" => 95}
Scores = Map1

# This map does NOT equal Scores - different order
Map2 := map{"Bob" => 90, "Alice" => 100, "Carol" => 95}
not Scores = Map2
```

当映射字面量包含重复键时，最后一个值会覆盖前面的值，但该键的位置保持在其**首次**出现的位置：

<!--versetest
-->
<!-- 59 -->
```verse
Map := map{0 => "zero", 1 => "one", 0 => "ZERO", 2 => "two"}
# Equivalent to map{0 => "ZERO", 1 => "one", 2 => "two"}
# The key 0 stays in its original position
```

对映射的迭代将按照保留的插入顺序访问条目。

### 空映射类型

空映射可以从上下文中推断其键和值类型，类似于数组：

<!--versetest
-->
<!-- 60 -->
```verse
StringToInt : [string]int = map{}  # Empty map with inferred types

var Scores : [string]int = map{}
set Scores = ConcatenateMaps(Scores, map{"Alice" => 100})
```

如果没有类型上下文，你可能需要显式提供类型注解。

### 协变性

映射在键类型和值类型上都是**协变的**（covariant）。当满足以下条件时，映射类型 `[K1]V1` 是 `[K2]V2` 的子类型：

- **键是协变的**：`K1` 是 `K2` 的子类型（更具体的键 → 更一般的键）
- **值是协变的**：`V1` 是 `V2` 的子类型（更具体值 → 更一般的值）

这种协变性是必要的，因为映射迭代会暴露键类型。当你迭代映射时，你会收到实际的键对象，这些对象必须能安全地用作声明的键类型。

虽然映射类型是协变的，但映射查找操作接受与键类型`可比较`的键，这看起来可能是逆变的。这是为查找提供的便利，但不影响映射类型本身的协变性。

<!--versetest
animal := class<unique> {}
dog := class<unique>(animal) {}
-->
<!-- 61 -->
```verse
# assume
# animal := class<unique> {}
# dog := class<unique>(animal) {}

# Map TYPE variance is COVARIANT
DogMap : [dog]int = map{dog{} => 1}
AnimalMap : [animal]int = DogMap  # ✓ Works - covariant assignment

# Map LOOKUP operations appear contravariant-like
MyDogMap : [dog]int = map{dog{} => 42}
DogKey : dog = dog{}
SupertypeKey : animal = DogKey  # Points to the same dog instance

# Lookup with exact key type:
if (Val1 := MyDogMap[DogKey]) {}  # ✓ Works

# Lookup with supertype key - also works!
if (Val2 := MyDogMap[SupertypeKey]) {}  # ✓ Also works

# This works because lookup only requires the key to be `comparable`
# to the map's key type. Both keys refer to the same unique object.
```

通过 `set` 修改可变映射时，你只能插入与映射声明类型匹配的键和值：

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

set Map[Key2] = 1      # Valid - exact type match
# set Map[Key1] = 2    # ERROR - cannot use supertype as key
```

### 嵌套映射

映射可以包含其他映射作为值，从而实现多级关联：

<!--versetest
-->
<!-- 63 -->
```verse
# Map from strings to maps of ints to strings
NestedMap : [string][int]string = map{
    "numbers" => map{1 => "one", 2 => "two"},
    "letters" => map{0 => "a", 1 => "b"}
}

if (InnerMap := NestedMap["numbers"]):
    if (Value := InnerMap[1]):
        Value = "one"
```

如果映射的所有值和键都是可比较的，则该映射可以用作其他映射的键。

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

`ConcatenateMaps()` 接受恰好两个映射并将它们合并为一个。当映射包含重复键时，**第二个**映射中的值会覆盖第一个映射中的值：

<!--versetest-->
<!-- 65 -->
```verse
Map1 := map{1 => "one", 2 => "two"}
Map2 := map{3 => "three", 4 => "four"}

Combined := ConcatenateMaps(Map1, Map2)
Combined = map{1 => "one", 2 => "two", 3 => "three", 4 => "four"}

# To merge more than two maps, chain calls
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
# Key 2 was overridden by the later map
```

这种从右到左的优先级确保后面的映射优先，实现了自然的覆盖模式。

**空映射：**

<!--versetest-->
<!-- 67 -->
```verse
# Empty maps contribute nothing
FirstMap := map{1 => "a"}
EmptyMap : [int]string = map{}

Combined := ConcatenateMaps(FirstMap, EmptyMap)
Combined = map{1 => "a"}
```

**类型约束：**

结果映射类型会强制转换为输入映射中最具体的共享类型：

<!--versetest-->
<!-- 68 -->
```verse
# Maps with the same key and value types
FirstMap := map{1 => "a"}
SecondMap := map{2 => "b"}
Combined := ConcatenateMaps(FirstMap, SecondMap)
Combined = map{1 => "a", 2 => "b"}
```

## 弱映射

`weak_map` 类型是 `map` 的一个专门超类型，专为具有弱键引用的持久化数据存储而设计。它在单个条目的访问上行为与普通映射类似，但有意限制了批量操作。你不能获取其长度，不能迭代其条目，也不能使用 `ConcatenateMaps`。这些限制使得高效的弱引用语义以及与 Verse 持久化系统的集成成为可能。

`weak_map` 使用 `weak_map(k,v)` 声明，可以从普通的 `map{}` 初始化。更新和访问单个条目的方式与常规映射相同：

<!--versetest
-->
<!-- 69 -->
```verse
var MyWeakMap:weak_map(int,int) = map{}

set MyWeakMap[0] = 1
Value := MyWeakMap[0]         # succeeds with 1

set MyWeakMap = map{0 => 2}   # reassignment still works (for local variables)
```

由于 `weak_map` 是 `map` 的超类型，你可以在需要时将常规映射赋值给 weak_map 变量，但一旦使用弱映射，你将失去计数或迭代的能力。

### 限制

**没有 Length 属性：**

<!--versetest
M():void =
    var MyWeakMap:weak_map(int,int) = map{1 => 2}
<#
-->
<!-- 70 -->
```verse
var MyWeakMap:weak_map(int,int) = map{1 => 2}
# ERROR: weak_map has no Length property
# Size := MyWeakMap.Length
```
<!-- #> -->

**不能迭代：**

<!--versetest
M():void =
    var MyWeakMap:weak_map(int,int) = map{1 => 2, 3 => 4}
<#
-->
<!-- 71 -->
```verse
var MyWeakMap:weak_map(int,int) = map{1 => 2, 3 => 4}
# ERROR: Cannot iterate over weak_map
# for (Entry : MyWeakMap) {}
```
<!-- #> -->

**不能转换为 comparable：**

<!--versetest
M():void =
    var MyWeakMap:weak_map(int,int) = map{}
<#
-->
<!-- 72 -->
```verse
var MyWeakMap:weak_map(int,int) = map{}
# ERROR: weak_map cannot be converted to comparable
# C:comparable = MyWeakMap
```
<!-- #> -->

**不能与常规映射连接：**

<!--versetest
M():void =
    var MyWeakMap:weak_map(int,int) = map{1 => 2}
<#
-->
<!-- 73 -->
```verse
var MyWeakMap:weak_map(int,int) = map{1 => 2}

# ERROR: Cannot join weak_map with regular map to produce regular map
# Result:[int]int = if (true?) then MyWeakMap else map{3 => 4}
```
<!-- #> -->

### 模块作用域的 weak_map 变量

当使用 `weak_map` 作为模块作用域变量（用于持久化数据）时，还有额外的限制：

**不能读取完整映射：**

<!--versetest
M():void =
    var LocalData:weak_map(int, int) = map{}
    if (set LocalData[1] = 100) {}
<#
-->
<!-- 74 -->
```verse
# Module-scoped persistent weak_map
var PlayerData:weak_map(player, int) = map{}

GetAllData():weak_map(player, int) =
    # ERROR: Cannot read complete module-scoped weak_map
    # PlayerData
    map{}  # Must construct new map instead
```
<!-- #> -->

**不能写入完整映射：**

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
    # ERROR: Cannot replace module-scoped weak_map
    # set PlayerData = map{}
    {}
```
<!-- #> -->

**单个条目访问有效：**

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

# OK: Can read individual entries
GetPlayerScore(Player:player):int =
    if (Score := PlayerData[Player]):
        Score
    else:
        0

# OK: Can write individual entries
SetPlayerScore(Player:player, Score:int):void =
    set PlayerData[Player] = Score
```
<!-- #> -->

此限制存在的原因是模块作用域的 weak_map 与持久化系统集成，该系统只跟踪单个条目的更新，而不是完整的映射替换。

对于模块作用域的 `var weak_map` 变量，键和值类型都有严格的要求：

**键类型必须具有 `<module_scoped_var_weak_map_key>` 说明符：**

<!--versetest
regular_class := class<unique> {}

M():void =
    var LocalData:weak_map(regular_class, int) = map{}
<#
-->
<!-- 77 -->
```verse
# Valid key type
persistent_class := class<unique><allocates><computes><persistent><module_scoped_var_weak_map_key> {}

var ValidData:weak_map(persistent_class, int) = map{}

# Invalid key type - missing specifier
regular_class := class<unique><allocates><computes> {}

# ERROR: Key type lacks <module_scoped_var_weak_map_key>
# var InvalidData:weak_map(regular_class, int) = map{}
```
<!-- #> -->

**值类型必须是可持久化的：**

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

# Valid: persistable value type
persistable_struct := struct<persistable>:
    Value:int

var ValidData:weak_map(persistent_class, persistable_struct) = map{}

# Invalid: non-persistable value type
regular_struct := struct:
    Value:int

# ERROR: Value type must be persistable
# var InvalidData:weak_map(persistent_class, regular_struct) = map{}
```
<!-- #> -->

满足要求的常见键类型：

- **`player`** - 玩家特定数据的标准键类型
- **`persistent_key`** - 具有有效性跟踪的自定义持久化键
- **`session_key`** - 不会跨会话持久化的临时键

### 协变性

`weak_map` 类型在其键类型上是**协变的**，这意味着你可以使用子类键类型的 weak_map，其中期望的是父类键类型：

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

# OK: weak_map is covariant in key type
BaseMap:weak_map(base_class, value_struct) = CreateDerivedMap()

# ERROR 3509: Cannot go the other way (contravariance)
# DerivedMap:weak_map(derived_class, value_struct) = BaseMap
```
<!-- #> -->

这种协变性也允许将常规映射赋值给具有兼容键类型的 weak_map：

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

# OK: Regular map converts to weak_map with covariant key
WeakMap:weak_map(base_class, value_struct) = RegularMap
```
<!-- #> -->

### 部分字段更新

当值类型是结构体或类时，你可以更新存储值的单个字段：

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
    # Set entire struct first
    set PlayerData[Player] = player_data{Level := NewLevel, Score := 0}

    # Then update just one field
    set PlayerData[Player].Level = NewLevel + 1
```
<!-- #> -->

### 事务与回滚语义

与 Verse 中所有可变状态一样，`weak_map` 的更新参与事务语义。如果 `<decides>` 表达式失败，所有更改都会回滚：

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
        false?  # Transaction fails

    # Both updates rolled back
    # GameData[1] still does not exist
    # GameData[2] still does not exist
```
<!-- #> -->

这适用于完整的映射替换（对于局部变量）、单个条目以及部分字段更新。
