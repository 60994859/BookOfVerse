# 可变性

在 Verse 中，不可变性是默认行为。当你创建一个值后，它将永远保持该值——不变、可预测、可安全共享。这一基础性原则使程序更易于推理，消除了一整类 bug，并支持强大的优化。但游戏是动态的世界，状态不断演化：生命值减少、分数增加、背包变化。Verse 兼顾了这两种范式，默认提供不可变性，同时在你需要时提供受控、显式的可变性。

Verse 中不可变数据与可变数据的区别不仅在于值能否改变。它从根本上影响数据在程序中的流动方式、值在函数间的共享方式，以及编译器对你代码的推理方式。理解这一区别对于编写高效、正确的 Verse 程序至关重要。

## 纯函数基础

在 Verse 的纯函数片段中，计算在无副作用的情况下进行。值被创建，但永不修改。函数将输入转换为输出，过程中不改变任何东西。这不是限制——而是使代码可预测、可组合的强大基础。

<!--versetest
point := struct{X:float, Y:float}
Distance(P1:point, P2:point)<reads>:float =
    DX := P2.X - P1.X
    DY := P2.Y - P1.Y
    Sqrt(DX * DX + DY * DY)

assert:
    Origin := point{X:=0.0, Y:=0.0}
    UnitX := point{X := 1.0, Y:=0.0}
    UnitY := point{X:=0.0, Y := 1.0}
<#
-->
<!-- 01 -->
```verse
# Immutable values and structures
point := struct<computes>:
    X:float = 0.0
    Y:float = 0.0

# These values are eternal - Origin will always be (0, 0)
Origin := point{}
UnitX := point{X := 1.0}
UnitY := point{Y := 1.0}

Distance(P1:point, P2:point)<reads>:float =
    DX := P2.X - P1.X
    DY := P2.Y - P1.Y
    Sqrt(DX * DX + DY * DY)
```
<!-- #> -->

在这个纯函数世界中，相等意味着结构相等——两个值如果具有相同的形状和内容，则它们相等。对于基本类型和结构体，这是自动发生的。对于具有超越其内容的标识的类，相等性需要更仔细的考量。

<!--versetest-->
<!-- 02 -->
```verse
# Recursive data structures using classes
linked_list := class:
    Value:int = 0
    Next:?linked_list = false

    # Custom equality check for structural comparison
    Equals(Other:linked_list)<computes><decides>:void =
        Self.Value = Other.Value
        # Both have no next, or both have next and those are equal
        if (Self.Next?):
            Tmp := Self.Next?
            OtherNext := Other.Next?
            Tmp.Equals[OtherNext]
        else:
            not Other.Next?

List1 := linked_list{Value := 1, Next := option{linked_list{Value := 2}}}
List2 := linked_list{Value := 1, Next := option{linked_list{Value := 2}}}

List1.Equals[List2] # This succeeds
```

纯计算构成了 Verse 中函数式编程的骨干。它是可预测、可测试、可并行的。当一个函数被标记为 `<computes>` 时，你知道它对相同的输入总是产生相同的输出，没有隐藏的依赖或意外的行为。

## 引入可变性

可变性通过两个关键字进入视野：`var` 和 `set`。`var` 注解声明变量可以被重新赋值。`set` 关键字执行该重新赋值。它们共同提供了受控的可变性，具有清晰的可见性。

<!--versetest-->
<!-- 03 -->
```verse
Score:int = 100   # Immutable variable - cannot be reassigned
                  # Mutable variable - can be reassigned 
var Health:float = 100.0       # type annotation is required
set Health = 75.0              # Allowed
```

每次使用 `var` 和 `set` 都会对效果产生影响。读取 `var` 变量需要 `<reads>` 效果。使用 `set` 需要 `<reads>` 和 `<writes>` 两种效果。这不是繁文缛节——这是透明性。效果使可变性在函数签名中可见，因此调用者知道函数何时可能观察或修改状态。

### var 声明的要求

可变变量声明有严格的要求，以防止常见错误：

**必须提供显式类型：**

<!--versetest-->
<!-- 04 -->
```verse
# Valid - explicit type
var X:int = 0

# Invalid - cannot use := syntax with var
# var X := 0  # Error
```

类型推断语法 `:=` 不能与 `var` 一起使用。你必须显式声明类型。

**必须在局部作用域中提供初始值：**

<!--versetest-->
<!-- 05 -->
```verse
# Valid - initialized
var Health:float = 100.0

# Invalid - no initial value in local scope
# var Score:int  # Error
```

在局部作用域（函数、控制流块）中，每个 `var` 声明都需要一个初始值。但是，在类或接口中声明可变字段时，可以省略初始值并在实例化时提供（详见类和接口章节）。

**不能完全无类型：**

<!--versetest
assert_semantic_error(3502):
    F():void=
        var X
<#
-->
<!-- 06 -->
```verse
# Invalid - neither type nor value
# var X  
```
<!-- #> -->

### var 声明作为表达式

使用 `var` 的变量声明可以作为表达式使用，求值为其初始值：

<!--versetest-->
<!-- 07 -->
```verse
X := (var Y:int = 42)  # X = 42, Y declared and mutable
X = 42
```

但是，`var` 声明**不能作为 `set` 的目标**：

<!--versetest
assert_semantic_error(3509):
    F():void=
        set (var Z:int = 0) = 1
<#
-->
<!-- 08 -->
```verse
# Invalid - var declarations evaluate to values, not variables
# set (var Z:int = 0) = 1  # Error: cannot use set on a value
```
<!-- #> -->

由于 `var` 声明将其初始值作为表达式结果返回，因此你不能对它们使用 `set`——`set` 需要的是可变变量，而不是值。

### set 与块表达式

`set` 语句可以使用块表达式，这允许进行复杂的计算和副作用：

<!--versetest-->
<!-- 09 -->
```verse
var X:int = 0
var Y:int = 1

set X = block:
    set Y = X      # Side effect: Y becomes 0
    2              # Block result: X becomes 2

X = 2 and Y = 0
```

当新值需要中间计算或在赋值时需要多个副作用时，这种模式很有用。

**重要提示：** `set` 的左侧在块执行之前求值，块返回的值才是实际赋值的值。这在某些情况下可能导致令人困惑的行为：

<!--versetest-->
<!-- 10 -->
```verse
# Confusing: Setting the same variable inside the block
var X:int = 0
set X = block:
    set X = 5  # X temporarily becomes 5
    2          # But X will be set to 2 (the block result)
X = 2          # The inner set was overwritten!

# Confusing: Modifying index variables used in array access
var Xs:[]int = array{10, 20, 30}
var Index:int = 1
set Xs[Index] = block:
    set Index = 2  # Index changes, but doesn't affect which element is set
    99
Xs[1] = 99         # Element at original Index (1) was modified, not Xs[2]
Index = 2          # Index is now 2, but too late to affect the assignment
```

为避免混淆，最好不要在块内部修改目标变量或目标表达式中使用的任何变量。

### 作用域与重新声明限制

**不允许变量遮蔽：**

Verse 不允许变量遮蔽。一旦声明了一个标识符，你就不能在同一个作用域或任何嵌套作用域中使用 `:=` 重新声明它。这比许多允许内部作用域遮蔽外部作用域变量的语言更为严格。

<!--versetest-->
<!-- 11 -->
```verse
var X:int = 0

# Invalid - X already exists in current scope
# X := 1  # Error
```

与许多语言不同，即使在嵌套块中也不能遮蔽变量：

<!--versetest
SomeCondition:logic=false
-->
<!-- 12 -->
```verse
var A:int = 1

if (SomeCondition?):
    # Invalid - A already declared in outer scope
    # A := 2  # Error: cannot shadow A

block:
    # Also invalid - cannot shadow here either
    # var A:int = 2  # Error: ambiguous identifier
```

如果你需要多个用途相似的标识符，请使用描述性名称（例如 `InitialHealth`、`CurrentHealth`），或使用限定名称创建单独的作用域（详情请参见[模块与路径](16_modules.md)章节中关于限定名称和消歧的内容）。

**不能使用赋值语法重新声明：**

<!--versetest-->
<!-- 13 -->
```verse
var A:int = 1
var B:int = 2

# Invalid - looks like assignment but A already exists
# A := B  # ERROR
```

应使用 `set A = B` 来给现有的可变变量赋值。

**不能嵌套 var 声明：**

<!--versetest
assert_semantic_error(3549):
    var (var X):int = 0
<#
-->
<!-- 14 -->
```verse
# Invalid
# var (var X):int = 0  # ERROR 3549
```
<!-- #> -->

`var` 关键字不能嵌套在自身内部。

## 深层可变性与浅层可变性

Verse 处理可变性的方式在结构体和类之间存在显著差异，这反映了它们在语言中的不同角色。

### 结构体可变性：深层且结构化

当你用 `var` 声明一个结构体变量时，你是在声明整个结构为可变的——变量本身及其所有嵌套字段，递归地。这种深层可变性意味着你可以修改结构树中的任何部分。

<!--versetest
point:=struct<computes>{X:float, Y:float}
player_stats := struct<computes>:
    Level:int = 1
    Position:point = point{X:=0.0, Y:=0.0}
    Inventory:[]string = array{}

assert:
    Stats1:player_stats = player_stats{}
    var Stats2:player_stats = player_stats{}
    set Stats2.Level = 2
    Stats2.Level = 2
    set Stats2.Position.X = 100.0
    Stats2.Position.X = 100.0
    set Stats2.Inventory = Stats2.Inventory + array{"Sword"}
    Stats2.Inventory = array{"Sword"}
<#
-->
<!-- 15 -->
```verse
player_stats := struct<computes>:
    Level:int = 1
    Position:point = point{}
    Inventory:[]string = array{}

# Immutable struct variable - nothing can change
Stats1:player_stats = player_stats{}
# set Stats1.Level = 2  # ERROR: Cannot modify immutable struct

# Mutable struct variable - everything can change
var Stats2:player_stats = player_stats{}
set Stats2.Level = 2  # OK
set Stats2.Position.X = 100.0  # OK - nested fields are mutable
set Stats2.Inventory = Stats2.Inventory + array{"Sword"}  # OK
```
<!-- #> -->

当你将一个结构体变量赋值给另一个时，Verse 会执行深拷贝。这两个变量互不依赖，各自拥有自己的数据副本。对一个变量的修改不会影响另一个。

<!--versetest
point:=struct<computes>{}
player_stats := struct<computes>:
    Level:int = 1
    Position:point = point{}
    Inventory:[]string = array{}

-->
<!-- 16 -->
```verse
var Original:player_stats = player_stats{Level := 5}
var Copy:player_stats = Original

set Copy.Level = 10
Original.Level = 5   # unchanged, they're independent copies
```

这种深拷贝语义适用于所有值类型：结构体、数组、映射和元组。当你将一个结构体传递给函数时，函数会收到其自己的副本。当你将一个结构体存储在容器中时，容器持有的是副本。这防止了别名问题，并使对结构体变异的推理局限在局部且可预测。

### 类可变性：引用语义

类的行为不同。它们具有引用语义——当你赋值一个类实例时，你是在共享对同一对象的引用，而不是创建副本。类变量上的 `var` 注解仅影响该变量能否被重新赋值以引用不同的对象。它不影响对象字段的可变性。

<!--versetest
game_character := class:
    Name:string = "Hero"
    var Health:float = 100.0
    MaxHealth:float = 100.0

assert:
    Player1:game_character = game_character{}
    set Player1.Health = 50.0
    Player1.Health = 50.0
    var Player2:game_character = Player1
    set Player2 = game_character{Name := "Villain"}
    Player2.Name = "Villain"
    set Player2.Health = 75.0
    Player2.Health = 75.0
<#
-->
<!-- 17 -->
```verse
game_character := class:
    Name:string = "Hero"
    var Health:float = 100.0  # This field is always mutable
    MaxHealth:float = 100.0   # This field is always immutable

# Immutable variable, but mutable fields can still change
Player1:game_character = game_character{}
# set Player1 = game_character{}  # ERROR: Cannot reassign non-var variable
set Player1.Health = 50.0  # OK: Health field is mutable

# Mutable variable allows reassignment
var Player2:game_character = Player1  # Same object
set Player2 = game_character{Name := "Villain"}  # OK: Can reassign
set Player2.Health = 75.0  # OK: Modifies the new object

# Player1 and the original Player2 reference were the same object
# After reassignment, Player2 references a different object
```
<!-- #> -->

关键点：对于类，字段可变性是在类定义时确定的，而不是变量声明时。`var` 字段始终是可变的，无论你如何访问它。非 `var` 字段始终是不可变的，即使通过 `var` 变量访问也是如此。

<!--versetest
point:=struct<computes>{X:float}
container := class:
    ImmutableData:point= point{X:=1.0}
    var MutableData:int = 0
assert:
    Box:container = container{}
    set Box.MutableData = 42
    Box.MutableData = 42
<#
-->
<!-- 18 -->
```verse
container := class:
    ImmutableData:point= point{}  # Always immutable
    var MutableData:int = 0       # Always mutable

# Even through an immutable variable, mutable fields can change
Box:container = container{}
set Box.MutableData = 42         # Allowed
# set Box.ImmutableData = Point{X := 1.0}  # ERROR: Field is immutable
```
<!-- #> -->

### 集合可变性：数组与映射

数组和映射遵循结构体语义——它们是值，而不是引用。当你复制一个集合时，你得到的是独立的副本。对一个副本的修改不会影响另一个。

#### 基本数组修改

可变数组允许替换元素：

<!--versetest-->
<!-- 19 -->
```verse
var Nums:[]int = array{0, 1}
Nums[0] = 0
Nums[1] = 1

set Nums[0] = 42
Nums[0] = 42
Nums[1] = 1  # Unchanged

set Nums[1] = 666
Nums[0] = 42
Nums[1] = 666
```

你不能添加超出数组当前长度的元素：

<!--versetest-->
<!-- 20 -->
```verse
var A:[]int = array{0}
not (set A[1] = 1)  # Fails - index out of bounds
# Must use concatenation: set A = A + array{1}
```

#### 基本映射修改

可变映射允许更新现有键和添加新键：

<!--versetest-->
<!-- 21 -->
```verse
var Scores:[int]int = map{0 => 1, 1 => 2}
set Scores[1] = 42
Scores[1] = 42

# Adding new keys
set Scores[2] = 100
Scores[2] = 100

# Map with string keys
var Config:[string]int = map{"volume" => 50}
set Config["brightness"] = 75
```

查找不存在的键不会添加它：

<!--versetest-->
<!-- 22 -->
```verse
M:[int]int := map{}
not (M[0] = 0)  # Key doesn't exist, comparison fails
# M is still empty - lookup didn't add the key
```

**从映射中删除键：**

Verse 没有直接的映射"删除"或"移除"操作。要删除键，通过遍历原始映射创建一个排除不需要键的新映射：

<!--versetest-->
<!-- 23 -->
```verse
var Scores:[string]int = map{"Alice" => 100, "Bob" => 85, "Charlie" => 92}

# Remove "Bob" by creating a new map without that key
var NewScores:[string]int = map{}
for (Name->Score:Scores):
    if (Name <> "Bob"):
        set NewScores[Name] = Score

set Scores = NewScores

# Scores now only contains Alice and Charlie
Scores["Alice"] = 100
Scores["Charlie"] = 92
```

这种模式可以封装到辅助函数中以实现复用。更多关于 `for` 循环的详细信息，请参见[控制流](07_control.md)章节。

#### 嵌套集合修改

集合可以嵌套，`set` 可以操作多个层级：

**映射的数组：**

<!--versetest-->
<!-- 24 -->
```verse
var Data:[int][]int = map{}
set Data[666] = array{42}
Data[666] = array{42}

# Mutate nested array element
set Data[666][0] = 1234
Data = map{666 => array{1234}}
Data[666] = array{1234}
```

**数组的映射：**

<!--versetest-->
<!-- 25 -->
```verse
var Grid:[][int]int = array{map{}}

# Replace entire map at index
set Grid[0] = map{42 => 666}
Grid[0] = map{42 => 666}
Grid[0][42] = 666

# Add new key to nested map
set Grid[0][1234] = 4321
Grid[0] = map{42 => 666, 1234 => 4321}
Grid[0][42] = 666
Grid[0][1234] = 4321

# Update existing key in nested map
set Grid[0][42] = 1122
Grid[0][42] = 1122
```

**数组的数组：**

<!--versetest-->
<!-- 26 -->
```verse
var Matrix:[][]int = array{array{1234}}
set Matrix[0][0] = 42
Matrix = array{array{42}}
Matrix[0] = array{42}
Matrix[0][0] = 42

# Replace inner array
set Matrix[0] = array{666}
Matrix[0] = array{666}
Matrix[0][0] = 666
```

所有嵌套层级都必须存在才能使用 `set`，如果任何较高层级不存在，整个 set 操作将失败。

<!--versetest-->
<!-- 27 -->
```verse
var Grid:[string][]int = map{"apples"=>array{1,2,3,4}}

set Grid["bananas"] = array{}  # OK - no nesting, just adds new key
set Grid["apples"][2] = 7      # OK - changes nested array element "3" to "7"

# This would fail: set Grid["oranges"][0] = 10
# Error: "oranges" key doesn't exist, so Grid["oranges"] fails
```

#### 集合的值语义

从可变集合中提取值会创建一个独立的副本：

<!--versetest-->
<!-- 28 -->
```verse
var X:[][int]int = array{map{42 => 1122, 1234 => 4321}}

# Y gets a copy of the map, not a reference
Y := X[0]
Y = map{42 => 1122, 1234 => 4321}

# Mutating X doesn't affect Y
set X[0][0] = 111
X[0] = map{42 => 1122, 1234 => 4321, 0 => 111}
Y = map{42 => 1122, 1234 => 4321}  # Unchanged

# Replacing entire element doesn't affect Y
set X[0] = map{42 => 4242}
X[0] = map{42 => 4242}
Y = map{42 => 1122, 1234 => 4321}  # Still unchanged
```

这与类的引用语义不同——集合复制，类共享。

#### 包含可变值的集合

当集合包含具有可变字段的类或结构体时，你可以通过集合进行修改：

<!--versetest
my_class := class:
    var X:[]int = array{0}
-->
<!-- 29 -->
```verse
C := my_class{}
set C.X[0] = 4266642
C.X[0] = 4266642
```

**具有可变成员的映射值：**

<!--versetest
my_class := class{  var X:int = 0 }
-->
<!-- 30 -->
```verse
var M:[int]my_class = map{0 => my_class{}}
M[0].X = 0

# Mutate class field through map
set M[0].X = 30
M[0].X = 30
```

从 `var` 构建的映射不会跟踪源变量的变化：

<!--versetest-->
<!-- 31 -->
```verse
var I:int = 42
M:[int]int = map{0 => I}
M[0] = 42

set I = 0
M[0] = 42  # Still 42! Map has a copy of the value
```

### 结构体数组：独立副本

当你将结构体存储在数组中时，每个元素都是一个独立的副本：

<!--versetest
my_struct := struct<computes>:
    I:int = 10
-->
<!-- 32 -->
```verse
S := my_struct{I := 88}
var A : []my_struct = array{S, S}

# All three have the value 88, but are independent
S.I = 88
A[0].I = 88
A[1].I = 88

# Mutating one doesn't affect the others
set A[0].I = 99
S.I = 88     # Unchanged
A[0].I = 99  # Changed
A[1].I = 88  # Unchanged
```

### 类数组：共享引用

类数组的行为截然不同——所有对同一对象的引用共享修改：

<!--versetest
my_class := class:
    var I:int = 20
-->
<!-- 33 -->
```verse
C := my_class{}
var A:[]my_class = array{C, C, C}

# All three array elements reference the same object
A[0].I = 20
A[1].I = 20
A[2].I = 20

# Mutating through one affects all references
set A[0].I = 30
A[0].I = 30
A[1].I = 30  # Changed!
A[2].I = 30  # Changed!

set A[1].I = 40
A[0].I = 40  # All three see the change
A[1].I = 40
A[2].I = 40

# Replacing an element breaks the sharing for that element
set A[1] = my_class{}
A[0].I = 40  # Still references original
A[1].I = 20  # New object with default value
A[2].I = 40  # Still references original
```

这是一个关键区别：**集合中的结构体是副本，集合中的类是共享引用**。

### 复合赋值运算符

Verse 支持结合算术运算与修改的复合赋值运算符：

<!--versetest
my_struct:= struct<computes>:
    A:int = 10
-->
<!-- 34 -->
```verse
var S:my_struct = my_struct{}

set S.A += 10
S.A = 20

set S.A -= 3
S.A = 17

set S.A *= 4
S.A = 68
```

可用的复合运算符：

- `set += ` - 加法赋值（int、float、string、array）
- `set -= ` - 减法赋值（int、float）
- `set *= ` - 乘法赋值（int、float）
- `set /= ` - 除法赋值（仅 float）

**重要提示**：`set /=` 不适用于整数，因为整数除法是可失败的。

复合赋值可以在任何普通赋值有效的地方使用：

<!--versetest-->
<!-- 35 -->
```verse
var Score:int = 100
set Score += 50
set Score *= 2

var Data:[]int = array{1, 2, 3}
set Data += array{4, 5}  # Array concatenation
Data = array{1, 2, 3, 4, 5}

var Nums:[][]int = array{array{1}}
set Nums[0][0] *= 42
Nums[0][0] = 42
```

使用 `+=` 的数组连接可以作用于结构体字段、嵌套字段和集合值，就像普通 `set` 一样：

<!--versetest-->
<!-- 35b -->
```verse
my_struct := struct<computes>:
    X:[]int = array{}

my_nested := struct<computes>:
    Inner:my_struct = my_struct{}

# Append to a struct field
var S:my_struct = my_struct{}
set S.X += array{1, 2, 3}
S.X = array{1, 2, 3}

# Append to a nested struct field
var N:my_nested = my_nested{}
set N.Inner.X += array{10, 20}
N.Inner.X = array{10, 20}

# Append to a map value
var M:[int][]int = map{}
set M[42] = array{}
set M[42] += array{1}
set M[42] += array{2}
M[42] = array{1, 2}

# Append to a nested array value
var A:[][]int = array{array{}}
set A[0] += array{1}
set A[0] += array{2}
A[0] = array{1, 2}
```

### 元组可变性：仅可整体替换

元组可以整体替换，但不能修改单个元素：

<!--versetest-->
<!-- 36 -->
```verse
var T0:tuple(int, int) = (10, 20)
T0(0) = 10
T0(1) = 20

# Can replace entire tuple
set T0 = (30, 40)
T0(0) = 30
T0(1) = 40
```

**不能修改元素：**

<!--versetest
assert_semantic_error(3509):
    TestTupleMutation()<transacts>:void =
        var T0:tuple(int, int) = (50, 60)
        set T0(0) = 70
<#
-->
<!-- 37 -->
```verse
var T0:tuple(int, int) = (50, 60)
set T0(0) = 70  # ERROR: Cannot mutate tuple elements
```
<!-- #> -->

即使元组本身是可变的，也适用此限制。你必须替换整个元组来更改其内容。

### 映射顺序与可变性

映射保持**插入顺序**，并且此顺序通过修改得以维护：

#### 新键追加到末尾

<!--versetest-->
<!-- 38 -->
```verse
var M:[int]int = map{2 => 2}

set M[1] = 1  # Appends to end
set M[0] = 0  # Appends to end

# Iteration order is insertion order: 2, 1, 0
Keys := array{2, 1, 0}
var Index:int = 0
for (Key->Value : M):
    Keys[Index] = Key
    set Index += 1

M = map{2 => 2, 1 => 1, 0 => 0}
```

#### 更新现有键保持位置

<!--versetest-->
<!-- 39 -->
```verse
var M:[string]int = map{"a" => 3, "b" => 1, "c" => 2}

# Mutating value keeps key position
set M["a"] = 0
M = map{"a" => 0, "b" => 1, "c" => 2}  # Same order

# Another update
set M["c"] = 0
set M["a"] = 2
M = map{"a" => 2, "b" => 1, "c" => 0}  # Still same order
```

#### 顺序影响相等性

映射的相等性既考虑键/值，**也考虑顺序**：

<!--versetest-->
<!-- 40 -->
```verse
var M:[string]int = map{"a" => 3, "b" => 1, "c" => 2}
set M["a"] = 0

# Same keys and values, same order = equal
M = map{"a" => 0, "b" => 1, "c" => 2}

# Same keys and values, different order = not equal
M <> map{"b" => 1, "c" => 2, "a" => 0}
```

## 关键可变性限制

Verse 对可变性的位置和方式施加了几个重要限制。这些限制并非随意——它们防止不健全的行为并维护类型安全。

### 不能修改不可变的类字段

类可能包含无法安全克隆的唯一指针或其他资源。因此，你不能修改类实例的不可变字段：

<!--versetest
assert_semantic_error(3509):
    classX := class:
        AI:int = 20

    F()<transacts>:void=
        CX:classX = classX{}
        set CX.AI = 30
<#
-->
<!-- 41 -->
```verse
classX := class:
    X:int = 20  # Immutable field

C:= classX{}
C.X = 20
set C.X = 30  # Error: Cannot mutate immutable class field
```
<!-- #> -->

即使类实例本身是可变的，此限制也同样适用。只有类的 `var` 字段才能被修改。

### 仅 <computes> 结构体允许字段修改

只有标记为 `<computes>`（纯结构体）的结构体允许通过变量修改字段：

<!--versetest-->
<!-- 42 -->
```verse
# OK: <computes> struct allows field mutation
my_mutable_struct := struct<computes>{M:int = 0, J:float = 3.0}

var S:my_mutable_struct = my_mutable_struct{}

Old := S # makes a copy of the struct

set S.M = 1 # makes a copy of the struct, but updates `M` in the process

S.M = 1 # Succeeds
not (Old = S) # Structs do not pass as references
```

当构造新的结构体时，它会被赋予更新后的值并复制其他字段。
如果有其他地方引用了旧的结构体，它们不会获得更新后的值（与类不同）。

此限制确保只有可预测、无效果的结构体才能被修改。

### 不能通过不可变的类字段进行修改

当修改嵌套结构时，你不能通过类的不可变字段（未用 `var` 声明的字段）进行修改：

<!--versetest
assert_semantic_error(3509):
    inner_struct := struct<computes>{Value:int = 0}
    immutable_class := class:
        Field:inner_struct = inner_struct{}
    outer_struct := struct<computes>:
        C:immutable_class

    F()<transacts>:void=
        var S:outer_struct = outer_struct{C := immutable_class{}}
        set S.C.Field.Value = 10
<#
-->
<!-- 43 -->
```verse
struct0 := struct<computes>{A:int = 10}
struct1 := struct<computes>{S0:struct0 = struct0{}}
class0 := class{CI:struct1 = struct1{}}  # Class with immutable field CI
struct2 := struct<computes>{C0:class0 = class0{}}
struct3 := struct<computes>{S2:struct2 = struct2{}}

var S3:[]struct3 = array{struct3{}, struct3{}}
set S3[1].S2.C0.CI.S0.A = 7  # ERROR: Cannot mutate through immutable field CI
```
<!-- #> -->

错误发生是因为 `CI` 是一个不可变字段（未用 `var` 声明）。**但是**，你可以通过修改路径中类的 `var` 字段进行修改。

即使使用可变索引，也不能修改不可变数组：

<!--NoCompile-->
<!-- 44 -->
```verse
var I:int = 2  # Mutable index
A:[]int = array{5, 6, 7}  # Immutable array
set A[I] = 2  # ERROR: A is not var - mutability of I doesn't matter
```

数组本身必须声明为 `var` 才能允许元素修改：

<!--versetest-->
<!-- 45 -->
```verse
I:int = 2
var A:[]int = array{5, 6, 7}
set A[I] = 2  # OK: A is var
```

## 标识与唯一性

`<unique>` 说明符赋予类基于标识的相等性。没有它，类根本不能被比较相等性（你需要编写自定义的比较方法）。有了它，相等性意味着标识——只有当两个引用指向完全相同的对象时，它们才相等。

<!--versetest
unique_item := class<unique>:
    var Count:int = 0
assert:
    Item1:unique_item = unique_item{}
    Item2:unique_item = Item1
    Item3:unique_item = unique_item{}
    Item1 = Item2
    not (Item1 = Item3)
<#
-->
<!-- 46 -->
```verse
unique_item := class<unique>:
    var Count:int = 0

Item1:unique_item = unique_item{}
Item2:unique_item = Item1  # Same object
Item3:unique_item = unique_item{}  # Different object

if (Item1 = Item2):
    Print("Same object")  # This prints

if (Item1 = Item3):
    Print("Same object")  # This doesn't print - different objects
```
<!-- #> -->

这种基于标识的相等性对于即使数据相同也需要不同标识的游戏对象至关重要。两个怪物可能有相同的属性，但它们仍然是不同的怪物。
