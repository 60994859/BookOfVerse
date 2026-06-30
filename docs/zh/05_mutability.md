# 可变性

不变性是 Verse 中的默认设置。当您创造价值时，它会永远保持该价值——不变、可预测且可以安全共享。这一基本原则使程序更容易推理，消除了整个类别的错误，并实现了强大的优化。但游戏是一个动态世界，状态不断变化：生命值下降、分数增加、库存变化。 Verse 包含这两种范式，默认提供不变性，同时在需要时提供受控的显式突变。

Verse 中不可变数据和可变数据之间的区别不仅仅是值是否可以更改。它从根本上影响数据如何流经程序、函数之间如何共享值以及编译器如何推理代码。理解这种区别对于编写高效、正确的 Verse 程序至关重要。

## 纯净基础

在 Verse 的纯片段中，计算的发生没有副作用。值被创建但从未被修改。函数将输入转换为输出，而无需更改任何内容。这不是限制——它是使代码可预测和可组合的强大基础。

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
# 不可变的值和结构
point := struct<computes>:
    X:float = 0.0
    Y:float = 0.0

# 这些值是永恒的 - 原点永远是 (0, 0)
Origin := point{}
UnitX := point{X := 1.0}
UnitY := point{Y := 1.0}

Distance(P1:point, P2:point)<reads>:float =
    DX := P2.X - P1.X
    DY := P2.Y - P1.Y
    Sqrt(DX * DX + DY * DY)
```
<!-- #> -->

在这个纯粹的世界里，平等意味着结构平等——如果两个价值具有相同的形式和内容，那么它们就是平等的。对于原始类型和结构，这会自动发生。对于具有超出其内容的同一性的类来说，平等需要更仔细的考虑。

<!--versetest-->
<!-- 02 -->
```verse
# 使用类的递归数据结构
linked_list := class:
    Value:int = 0
    Next:?linked_list = false

    # 用于结构比较的自定义相等性检查
    Equals(Other:linked_list)<computes><decides>:void =
        Self.Value = Other.Value
        # 两者都没有 next，或者两者都有 next 并且它们都适合
        if (Self.Next?):
            Tmp := Self.Next?
            OtherNext := Other.Next?
            Tmp.Equals[OtherNext]
        else:
            not Other.Next?

List1 := linked_list{Value := 1, Next := option{linked_list{Value := 2}}}
List2 := linked_list{Value := 1, Next := option{linked_list{Value := 2}}}

List1.Equals[List2] # 这样就成功了
```
纯计算构成了 Verse 中函数式编程的支柱。它是可预测的、可测试的和可并行的。当一个函数被标记为 `<computes>` 时，您知道它总是会为相同的输入产生相同的输出，没有隐藏的依赖关系或令人惊讶的行为。

## 突变介绍

突变通过两个关键字进入：`var`和`set`。 `var` 注释声明变量可以重新分配。 `set` 关键字执行该重新分配。它们共同提供了具有清晰可见性的受控突变。

<!--versetest-->
<!-- 03 -->
```verse
Score:int = 100   # 不可变变量 - 不能重新分配
                  # 可变变量 - 可以重新分配
var Health:float = 100.0       # 需要类型注释
set Health = 75.0              # 允许
```
`var` 和 `set` 的每次使用都会对效果产生影响。从 `var` 变量读取需要 `<reads>` 效果。使用 `set` 需要 `<reads>` 和 `<writes>` 效果。这不是官僚主义——而是透明度。这些效果使突变在函数签名中可见，因此调用者知道函数何时可能观察或修改状态。

### var 声明的要求

可变变量声明有严格的要求，可以防止常见错误：

**必须提供显式类型：**

<!--versetest-->
<!-- 04 -->
```verse
# 有效 - 显式类型
var X:int = 0

# 无效——不能将 := 语法与 var 一起使用
# var X := 0  # Error
```
类型推断语法 `:=` 不能与 `var` 一起使用。您必须显式声明类型。

**必须提供初始值（在本地范围内）：**

<!--versetest-->
<!-- 05 -->
```verse
# 有效-初始化
var Health:float = 100.0

# 无效 - 局部范围内没有初始值
# var Score:int # 错误
```
在局部作用域（函数、控制流块）中，每个 `var` 声明都需要一个初始值。但是，在类或接口中声明可变字段时，可以省略初始值并在实例化期间提供初始值（有关详细信息，请参阅“类和接口”一章）。

**不能完全无类型：**

<!--versetest
assert_semantic_error(3502):
    F():void=
        var X
<#
-->
<!-- 06 -->
```verse
# 无效 - 类型和值均无效
# 变量X
```
<!-- #> -->

### var 声明作为表达式

使用 `var` 的变量声明可以用作表达式，计算其初始值：

<!--versetest-->
<!-- 07 -->
```verse
X := (var Y:int = 42)  # X = 42，Y 已声明且可变
X = 42
```
但是，`var` 声明**不能是 `set`** 的目标：

<!--versetest
assert_semantic_error(3509):
    F():void=
        set (var Z:int = 0) = 1
<#
-->
<!-- 08 -->
```verse
# 无效 -var 报表计算为值，而不是变量
# set (var Z:int = 0) = 1  # Error: cannot use set on a value
```
<!-- #> -->

由于 `var` 声明将其初始值作为表达式结果返回，因此您不能对其使用 `set` - `set` 需要可变变量，而不是值。

### 使用块表达式设置

`set` 语句可以使用块表达式，这允许复杂的计算和副作用：

<!--versetest-->
<!-- 09 -->
```verse
var X:int = 0
var Y:int = 1

set X = block:
    set Y = X      # 副作用：Y 变为 0
    2              # 区块结果：X变为2

X = 2 and Y = 0
```
当新值需要中间计算或在分配期间需要多个副作用时，此模式非常有用。

**重要提示：** `set` 的左侧在块执行之前进行评估，块的返回值就是被分配的值。在某些情况下，这可能会导致令人困惑的行为：

<!--versetest-->
<!-- 10 -->
```verse
# 令人困惑：在块内设置相同的变量
var X:int = 0
set X = block:
    set X = 5  # X暂时变为5
    2          # 但X将被设置为2（区块结果）
X = 2          # 内部集合被覆盖！

# 令人困惑：修改数组访问中使用的索引变量
var Xs:[]int = array{10, 20, 30}
var Index:int = 1
set Xs[Index] = block:
    set Index = 2  # 索引发生变化，但不影响设置哪个元素
    99
Xs[1] = 99         # 原始索引 (1) 处的元素被修改，而不是 Xs[2]
Index = 2          # 索引现在为 2，但为时已晚，无法影响分配
```
为了避免混淆，最好避免修改目标变量或块内目标表达式中使用的任何变量。

### 范围和重新声明限制

**无变量阴影：**

Verse 不允许变量阴影。一旦声明了标识符，您就无法在同一作用域或任何嵌套作用域中的任何位置使用 `:=` 重新声明它。这比许多允许内部作用域隐藏外部作用域变量的语言更具限制性。

<!--versetest-->
<!-- 11 -->
```verse
var X:int = 0

# 无效 - X 已存在于当前范围内
# X := 1  # Error
```
与许多语言不同，即使在嵌套块中也不能隐藏变量：

<!--versetest
SomeCondition:logic=false
-->
<!-- 12 -->
```verse
var A:int = 1

if (SomeCondition?):
    # 无效 - A 已在外部作用域中声明
    # A := 2  # Error: cannot shadow A

block:
    # 也无效 - 也不能在这里阴影
    # var A:int = 2 # 错误：标识符不明确
```
如果您需要具有相似用途的多个标识符，请使用描述性名称（例如，`InitialHealth`、`CurrentHealth`）或使用限定名称来创建单独的范围（有关限定名称和消歧的详细信息，请参阅[模块和路径](16_modules.md)一章）。

**无法使用赋值语法重新声明：**

<!--versetest-->
<!-- 13 -->
```verse
var A:int = 1
var B:int = 2

# 无效 - 看起来像赋值，但 A 已经存在
# A := B  # ERROR
```
使用 `set A = B` 来分配给现有的可变变量。

**不能嵌套 var 声明：**

<!--versetest
assert_semantic_error(3549):
    var (var X):int = 0
<#
-->
<!-- 14 -->
```verse
# 无效
# var (var X):int = 0  # ERROR 3549
```
<!-- #> -->

`var` 关键字不能嵌套在其自身内。

## 深可变性与浅可变性

Verse 的可变性方法在结构和类之间存在显着差异，反映了它们在语言中的不同角色。

### 结构可变性：深层和结构性

当您使用 `var` 声明结构变量时，您将整个结构声明为可变的 - 变量本身及其所有嵌套字段，递归地。这种深度可变性意味着您可以修改结构树的任何部分。

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

# 不可变的结构变量 - 没有什么可以改变
Stats1:player_stats = player_stats{}
# set Stats1.Level = 2  # ERROR: Cannot modify immutable struct

# 可变结构变量 - 一切都可以改变
var Stats2:player_stats = player_stats{}
set Stats2.Level = 2  # 好的
set Stats2.Position.X = 100.0  # 好的 - 嵌套字段是可变的
set Stats2.Inventory = Stats2.Inventory + array{"Sword"}  # 好的
```
<!-- #> -->

当您将一个结构变量分配给另一个结构变量时，Verse 会执行深层复制。这两个变量变得独立，每个变量都有自己的数据副本。其中一项的更改不会影响另一项。

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
Original.Level = 5   # 不变，它们是独立的副本
```
这种深度复制语义扩展到所有值类型：结构、数组、映射和元组。当您将结构传递给函数时，该函数会收到自己的副本。当您将结构存储在容器中时，容器会保存一个副本。这可以防止混叠，并使结构突变的推理局部化且可预测。

### 类可变性：参考语义

类的行为不同。它们具有引用语义——当您分配一个类实例时，您将共享对同一对象的引用，而不是创建副本。类变量上的 `var` 注释仅影响该变量是否可以重新分配以引用不同的对象。它不影响对象字段的可变性。

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
    var Health:float = 100.0  # 该字段始终是可变的
    MaxHealth:float = 100.0   # 该字段始终是不可变的

# 不可变变量，但可变字段仍然可以更改
Player1:game_character = game_character{}
# set Player1 = game_character{}  # ERROR: Cannot reassign non-var variable
set Player1.Health = 50.0  # OK：健康字段是可变的

# 可变变量允许重新分配
var Player2:game_character = Player1  # 同一物体
set Player2 = game_character{Name := "Villain"}  # 好的：可以重新分配
set Player2.Health = 75.0  # OK：修改新对象

# Player1 和原始 Player2 引用是同一个对象
# 重新分配后，Player2引用了不同的对象
```
<!-- #> -->

关键见解：对于类，字段可变性是在类定义时确定的，而不是在变量声明时确定的。无论您如何访问它，`var` 字段始终是可变的。非 `var` 字段始终是不可变的，即使通过 `var` 变量访问也是如此。

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
    ImmutableData:point= point{}  # 永远不变
    var MutableData:int = 0       # 总是可变的

# 即使通过不可变变量，可变字段也可以更改
Box:container = container{}
set Box.MutableData = 42         # 允许
# set Box.ImmutableData = Point{X := 1.0}  # ERROR: Field is immutable
```
<!-- #> -->

### 集合可变性：数组和映射

数组和映射遵循结构语义——它们是值，而不是引用。当您复制集合时，您会获得一个独立的副本。一个副本的突变不会影响另一个副本。

#### 基本数组突变

可变数组允许元素替换：

<!--versetest-->
<!-- 19 -->
```verse
var Nums:[]int = array{0, 1}
Nums[0] = 0
Nums[1] = 1

set Nums[0] = 42
Nums[0] = 42
Nums[1] = 1  # 不变

set Nums[1] = 666
Nums[0] = 42
Nums[1] = 666
```
您不能添加超出数组当前长度的元素：

<!--versetest-->
<!-- 20 -->
```verse
var A:[]int = array{0}
not (set A[1] = 1)  # 失败 - 索引超出范围
# 必须使用中央：set A = A + array{1}
```
#### 基本映射突变

可变映射允许更新现有键和添加新键：

<!--versetest-->
<!-- 21 -->
```verse
var Scores:[int]int = map{0 => 1, 1 => 2}
set Scores[1] = 42
Scores[1] = 42

# 添加新键
set Scores[2] = 100
Scores[2] = 100

# 带有字符串键的映射
var Config:[string]int = map{"volume" => 50}
set Config["brightness"] = 75
```
查找不存在的键不会添加它：

<!--versetest-->
<!-- 22 -->
```verse
M:[int]int := map{}
not (M[0] = 0)  # 键不存在，比较失败
# M 仍然是空的 - 查找没有添加密钥
```
**从映射中删除键：**

Verse 没有直接对映射进行“删除”或“移除”操作。要删除键，请创建一个新映射，通过迭代原始映射来排除不需要的键：

<!--versetest-->
<!-- 23 -->
```verse
var Scores:[string]int = map{"Alice" => 100, "Bob" => 85, "Charlie" => 92}

# 通过创建一个没有该键的新映射来删除“Bob”
var NewScores:[string]int = map{}
for (Name->Score:Scores):
    if (Name <> "Bob"):
        set NewScores[Name] = Score

set Scores = NewScores

# 分数现在只包含爱丽丝和查理
Scores["Alice"] = 100
Scores["Charlie"] = 92
```
该模式可以包装在辅助函数中以实现可重用性。有关 `for` 循环的更多详细信息，请参阅[控制流](07_control.md)一章。

#### 嵌套集合突变

集合可以嵌套，`set` 通过多个级别工作：

**数组映射：**

<!--versetest-->
<!-- 24 -->
```verse
var Data:[int][]int = map{}
set Data[666] = array{42}
Data[666] = array{42}

# 改变嵌套数组元素
set Data[666][0] = 1234
Data = map{666 => array{1234}}
Data[666] = array{1234}
```
**映射数组：**

<!--versetest-->
<!-- 25 -->
```verse
var Grid:[][int]int = array{map{}}

# 替换索引处的整个映射
set Grid[0] = map{42 => 666}
Grid[0] = map{42 => 666}
Grid[0][42] = 666

# 向嵌套映射添加新键
set Grid[0][1234] = 4321
Grid[0] = map{42 => 666, 1234 => 4321}
Grid[0][42] = 666
Grid[0][1234] = 4321

# 更新嵌套映射中的现有键
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

# 替换内部数组
set Matrix[0] = array{666}
Matrix[0] = array{666}
Matrix[0][0] = 666
```
所有嵌套级别都应该存在才能使用 `set`，如果任何更高级别不存在，则整个集合将失败。

<!--versetest-->
<!-- 27 -->
```verse
var Grid:[string][]int = map{"apples"=>array{1,2,3,4}}

set Grid["bananas"] = array{}  # 好的 - 没有嵌套，只是添加新键
set Grid["apples"][2] = 7      # 确定 - 将嵌套数组元素“3”更改为“7”

# 这会失败：设置 Grid["oranges"][0] = 10
# 错误：“oranges”键不存在，因此 Grid[“oranges”] 失败
```
#### 集合的值语义

从可变集合中提取值会创建一个独立的副本：

<!--versetest-->
<!-- 28 -->
```verse
var X:[][int]int = array{map{42 => 1122, 1234 => 4321}}

# Y 获得映射的副本，而不是参考
Y := X[0]
Y = map{42 => 1122, 1234 => 4321}

# 改变 X 不会影响 Y
set X[0][0] = 111
X[0] = map{42 => 1122, 1234 => 4321, 0 => 111}
Y = map{42 => 1122, 1234 => 4321}  # 不变

# 替换整个元素不会影响 Y
set X[0] = map{42 => 4242}
X[0] = map{42 => 4242}
Y = map{42 => 1122, 1234 => 4321}  # 依然不变
```
这与类引用语义不同——集合复制，类共享。

#### 具有可变值的集合

当集合包含具有可变字段的类或结构时，您可以通过集合进行变异：

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
**将值映射到可变成员：**

<!--versetest
my_class := class{  var X:int = 0 }
-->
<!-- 30 -->
```verse
var M:[int]my_class = map{0 => my_class{}}
M[0].X = 0

# 通过映射改变类字段
set M[0].X = 30
M[0].X = 30
```
从 `var` 构造的映射不跟踪源变量的更改：

<!--versetest-->
<!-- 31 -->
```verse
var I:int = 42
M:[int]int = map{0 => I}
M[0] = 42

set I = 0
M[0] = 42  # 还是42岁！映射有值的副本
```
### 结构数组：独立副本

当您将结构存储在数组中时，每个元素都是一个独立的副本：

<!--versetest
my_struct := struct<computes>:
    I:int = 10
-->
<!-- 32 -->
```verse
S := my_struct{I := 88}
var A : []my_struct = array{S, S}

# 这三个值都是 88，但是是独立的
S.I = 88
A[0].I = 88
A[1].I = 88

# 改变一个不会影响其他
set A[0].I = 99
S.I = 88     # 不变
A[0].I = 99  # 改变了
A[1].I = 88  # 不变
```
### 类数组：共享引用

类数组的行为非常不同——对同一对象的所有引用都共享突变：

<!--versetest
my_class := class:
    var I:int = 20
-->
<!-- 33 -->
```verse
C := my_class{}
var A:[]my_class = array{C, C, C}

# 所有三个数组元素都引用同一个对象
A[0].I = 20
A[1].I = 20
A[2].I = 20

# 修改一个引用会影响所有引用
set A[0].I = 30
A[0].I = 30
A[1].I = 30  # 改变了！
A[2].I = 30  # 改变了！

set A[1].I = 40
A[0].I = 40  # 三个人都看到了变化
A[1].I = 40
A[2].I = 40

# 替换元素会破坏该元素的共享
set A[1] = my_class{}
A[0].I = 40  # 仍参考原文
A[1].I = 20  # 具有默认值的新对象
A[2].I = 40  # 仍参考原文
```
这是一个关键的区别：**集合中的结构是副本，集合中的类是共享引用**。

### 复合赋值运算符

Verse 支持将算术与变异相结合的复合赋值运算符：

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
- `set /= ` - 除法分配（仅限浮点数）

**重要**：`set /=` 不适用于整数，因为整数除法是失败的。

复合作业适用于常规作业的任何地方：

<!--versetest-->
<!-- 35 -->
```verse
var Score:int = 100
set Score += 50
set Score *= 2

var Data:[]int = array{1, 2, 3}
set Data += array{4, 5}  # 数组串联
Data = array{1, 2, 3, 4, 5}

var Nums:[][]int = array{array{1}}
set Nums[0][0] *= 42
Nums[0][0] = 42
```
与 `+=` 的数组串联适用于结构字段、嵌套字段、
和集合值，就像常规 `set` 所做的那样：

<!--versetest-->
<!-- 35b -->
```verse
my_struct := struct<computes>:
    X:[]int = array{}

my_nested := struct<computes>:
    Inner:my_struct = my_struct{}

# 附加到结构体字段
var S:my_struct = my_struct{}
set S.X += array{1, 2, 3}
S.X = array{1, 2, 3}

# 附加到嵌套结构字段
var N:my_nested = my_nested{}
set N.Inner.X += array{10, 20}
N.Inner.X = array{10, 20}

# 附加到映射值
var M:[int][]int = map{}
set M[42] = array{}
set M[42] += array{1}
set M[42] += array{2}
M[42] = array{1, 2}

# 附加到嵌套数组值
var A:[][]int = array{array{}}
set A[0] += array{1}
set A[0] += array{2}
A[0] = array{1, 2}
```
### 元组可变性：仅替换

元组可以完全替换，但单个元素不能改变：

<!--versetest-->
<!-- 36 -->
```verse
var T0:tuple(int, int) = (10, 20)
T0(0) = 10
T0(1) = 20

# 可以替换整个元组
set T0 = (30, 40)
T0(0) = 30
T0(1) = 40
```
**不能改变元素：**

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
set T0(0) = 70  # 错误：无法改变元组元素
```
<!-- #> -->

即使元组是可变的，此限制也适用。您必须替换整个元组才能更改其内容。

### 映射排序和变异

映射保留**插入顺序**，并且该顺序通过突变来维持：

#### 新键追加到末尾

<!--versetest-->
<!-- 38 -->
```verse
var M:[int]int = map{2 => 2}

set M[1] = 1  # 追加到末尾
set M[0] = 0  # 追加到末尾

# 迭代顺序是插入顺序：2, 1, 0
Keys := array{2, 1, 0}
var Index:int = 0
for (Key->Value : M):
    Keys[Index] = Key
    set Index += 1

M = map{2 => 2, 1 => 1, 0 => 0}
```
#### 更新现有密钥保留位置

<!--versetest-->
<!-- 39 -->
```verse
var M:[string]int = map{"a" => 3, "b" => 1, "c" => 2}

# 变异值保持关键位置
set M["a"] = 0
M = map{"a" => 0, "b" => 1, "c" => 2}  # 相同订单

# 另一个更新
set M["c"] = 0
set M["a"] = 2
M = map{"a" => 2, "b" => 1, "c" => 0}  # 还是一样的顺序
```
#### 秩序对于平等至关重要

映射相等性考虑键/值**和顺序**：

<!--versetest-->
<!-- 40 -->
```verse
var M:[string]int = map{"a" => 3, "b" => 1, "c" => 2}
set M["a"] = 0

# 相同的键和值，相同的顺序 = 相等
M = map{"a" => 0, "b" => 1, "c" => 2}

# 相同的键和值，不同的顺序 = 不相等
M <> map{"b" => 1, "c" => 2, "a" => 0}
```
## 关键的可变性限制

Verse 对突变发生的地点和方式施加了几个重要的限制。这些并不是任意的——它们可以防止不健全的行为并维护类型安全。

### 无法改变不可变类字段

类可能包含唯一的指针或其他无法安全克隆的资源。因此，您不能改变类实例的不可变字段：

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
    X:int = 20  # 不可变字段

C:= classX{}
C.X = 20
set C.X = 30  # 错误：无法改变不可变类字段
```
<!-- #> -->

即使类实例本身是可变的，此限制也适用。只能更改类的 `var` 字段。

### 只有 <computes> 结构允许字段突变

只有标记为 `<computes>`（纯结构）的结构才允许通过变量进行字段突变：

<!--versetest-->
<!-- 42 -->
```verse
# OK：<computes>允许结构字段突变
my_mutable_struct := struct<computes>{M:int = 0, J:float = 3.0}

var S:my_mutable_struct = my_mutable_struct{}

Old := S # 制作结构体的副本

set S.M = 1 # 制作结构体的副本，但在此过程中更新“M”

S.M = 1 # 成功
not (Old = S) # 结构不作为引用传递
```
构造新结构时，会为其分配更新的值并复制其他字段。
如果有其他地方引用旧结构，它们将不会有更新的值（与类不同）

此限制确保只有可预测的、无影响的结构才能发生突变。

### 无法通过不可变类字段进行变异

改变嵌套结构时，不能通过类的不可变字段（未使用 `var` 声明的字段）进行改变：

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
class0 := class{CI:struct1 = struct1{}}  # 具有不可变字段 CI 的类
struct2 := struct<computes>{C0:class0 = class0{}}
struct3 := struct<computes>{S2:struct2 = struct2{}}

var S3:[]struct3 = array{struct3{}, struct3{}}
set S3[1].S2.C0.CI.S0.A = 7  # 错误：无法通过不可变字段 CI 进行变异
```
<!-- #> -->

发生错误的原因是 `CI` 是不可变字段（未使用 `var` 声明）。 **但是**，您可以通过突变路径中类的 `var` 字段进行突变。

即使使用可变索引，也无法更改不可变数组：

<!--NoCompile-->
<!-- 44 -->
```verse
var I:int = 2  # 可变索引
A:[]int = array{5, 6, 7}  # 不可变数组
set A[I] = 2  # 错误：A 不是 var - I 的可变性并不重要
```
数组本身必须声明为 `var` 以允许元素突变：

<!--versetest-->
<!-- 45 -->
```verse
I:int = 2
var A:[]int = array{5, 6, 7}
set A[I] = 2  # OK：A是var
```
## 身份和独特性

`<unique>` 说明符赋予类基于身份的平等性。如果没有它，根本无法比较类的相等性（您需要编写自定义比较方法）。有了它，相等就意味着同一性——只有当两个引用引用完全相同的对象时，它们才是相等的。

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
Item2:unique_item = Item1  # 同一物体
Item3:unique_item = unique_item{}  # 不同的对象

if (Item1 = Item2):
    Print("Same object")  # 这打印

if (Item1 = Item3):
    Print("Same object")  # 这不会打印 - 不同的对象
```
<!-- #> -->

这种基于身份的平等对于需要不同身份的游戏对象至关重要，即使它们的数据相同。两个怪物可能具有相同的属性，但它们仍然是不同的怪物。
