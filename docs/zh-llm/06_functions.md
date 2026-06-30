# 函数

函数是可重用的代码块，根据输入执行操作并产生输出。可以将它们视为行为的抽象，就像在餐厅的菜单上点餐一样。当你点餐时，你告诉服务员你想要菜单上的什么，例如 `OrderFood("Ramen")`。你不需要知道厨房如何准备你的菜肴，但你在点餐后期待收到食物。这种抽象就是函数的强大之处——你定义一次指令，然后在代码中的不同上下文中重复使用。

## 参数

函数可以接受任意数量的参数，从零个到多个都可以。语法遵循一个简单的模式，每个参数都有一个标识符和一个类型，用逗号分隔：

<!--versetest-->
<!-- 01-->
```verse
ProcessData(Name:string, Age:int, Score:float):string =
    "{Name} is {Age} years old with a score of {Score}"
```

对于参数较多或需要进行可选配置的函数，Verse 支持命名参数和默认参数。

### 命名参数

带默认值的命名参数使函数更灵活、更符合人体工程学。它们允许你：

- 按名称而非位置指定参数
- 为可选参数提供默认值
- 仅使用你需要的参数调用函数
- 添加新的可选参数而不破坏现有代码

命名参数使用 `?` 前缀声明，调用时使用名称和 `:=` 后跟一个值：

<!--versetest-->
<!-- 02-->
```verse
# A function with named parameters
Greet(?Name:string, ?Greeting:string):string = "{Greeting} {Name}!"

# A call with named arguments 
Greet(?Name := "Alice", ?Greeting := "Hello") 
```

带有默认值的命名参数确实是可选的：

<!--versetest-->
<!-- 03-->
```verse
# Named parameters with defaults
Log(Message:string, ?Level:int=1, ?Color:string="white"):string =
    "[Level {Level}] {Message} ({Color})"

# Call with all defaults
Log("Starting")                          # Returns "[Level 1] Starting (white)"

# Call with some arguments
Log("Warning", ?Level:=2)                # Returns "[Level 2] Warning (white)"

# Call with arguments in any order
Log("Error", ?Color:="red", ?Level:= 3)  # Returns "[Level 3] Error (red)"
```

在第一个命名参数之后，所有后续参数也必须是命名参数：

<!--versetest
assert_semantic_error(3629):
    Invalid(?Named:int, Positional:string):void = {}
<#
-->
<!-- 04-->
```verse
# Invalid: named followed by positional
Invalid(?Named:int, Positional:string):void = {}  # ERROR
```
<!-- #>-->

当调用带有命名参数的函数时，必须使用 `?Name:=Value` 语法。所有没有默认值的参数都必须指定。位置参数在前：

<!--versetest
Configure(Required:int, ?Option1:string = "", ?Option2:logic = false):void = {}
<#
-->
<!-- 07-->
```verse
Configure(Required:int, ?Option1:string, ?Option2:logic):void = { }

# Valid
Configure(42, ?Option1:="test", ?Option2:=true)

# Invalid: named arg before positional
Configure(?Option1:="test", 42, ?Option2:=true)  # ERROR
```
<!-- #>-->

默认值在函数的定义域中求值；它们可以引用：

  - 模块级定义
  - 类或接口成员
  - 之前的参数

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
# Module-level definition
ModuleTimeout:int = 30

# Access module-level definition
Connect(?Host:string, ?Timeout:int = ModuleTimeout):void =...

# Access member definition
game_config := class:
    DefaultLives:int = 3

    StartGame(?Lives:int = DefaultLives):void =...

# Access earlier parameter
CreateRange(?Start:int, ?End:int = Start + 10):[]int =...
```
<!-- #>-->

默认值在类层次结构中与重写的成员一起工作：

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
    # Uses DefaultSpeed from current instance

fast_game := class(base_game):
    DefaultSpeed<override>:float = 2.0

base_game{}.Move()         # Uses 1.0
fast_game{}.Move()         # Uses 2.0 (overridden value)
```
<!-- #>-->

命名参数和默认参数与类型系统交互。带有默认参数的函数是不带这些参数的同一函数的子类型：

<!--versetest-->
<!-- 14-->
```verse
Process(?Required:int, ?Optional:int = 0):int = Required + Optional

# Can assign to type without optional parameter
F1:type{_(?Required:int):int} = Process
F1(?Required := 5)                          # Returns 5 (uses default)

# Can assign to type with optional parameter
F2:type{_(?Required:int, ?Optional:int):int} = Process
F2(?Required := 5, ?Optional := 3)          # Returns 8

# Can even assign to type with no parameters (all have defaults)
DefaultAll(?A:int = 1, ?B:int = 2):int = A + B
F3:type{_():int} = DefaultAll
F3()                                        # Returns 3
```

函数类型保留命名参数的名称：

<!--versetest-->
<!-- 15-->
```verse
Calculate(?Amount:float, ?Rate:float):float = Amount * Rate

# Valid: names match
F1:type{_(?Amount:float, ?Rate:float):float} = Calculate

# Invalid: different names
# F2:type{_(?Value:float, ?Factor:float):float} = Calculate  # ERROR
```

函数类型不包含默认值：

<!--versetest-->
<!-- 16-->
```verse
F1(?X:int=1):int = X

F2:type{_(?X:int=99):int} = F1    # F1 and F2 are of the same type
```

命名参数参与函数重载解析：

<!--versetest-->
<!-- 17-->
```verse
Process(Value:int):string = "One parameter"
Process(Value:int, ?Option:string):string = "Two parameters"
Process(Value:int, ?Option1:string, ?Option2:logic):string = "Three parameters"

Process(42)                                        # Calls first overload
Process(42, ?Option := "test")                     # Calls second overload
Process(42, ?Option1 := "test", ?Option2 := true)  # Calls third overload
```

编译器选择与提供的参数匹配的重载。命名参数使重载解析更精确，因为名称必须完全匹配。

命名参数在**重载区分度**方面有特定的规则，这些规则与位置参数不同。如果两个函数签名可以用相同的参数调用，则认为它们是**不区分的**（不能重载）。

**命名参数的顺序无关紧要：** 命名参数按名称而非位置匹配，因此重新排序不会产生区分度：

<!--versetest
assert_semantic_error(3532):
    F(?Y:int, ?X:int):int = X + Y
    F(?X:int, ?Y:int):int = X - Y
<#
-->
<!-- 18-->
```verse
# Not distinct - same parameters, different order
F(?Y:int, ?X:int):int = X + Y
F(?X:int, ?Y:int):int = X - Y  # ERROR
```
<!-- #>-->

**默认值不产生区分度：** 如果参数名称相同，默认值的存在与否不会使签名产生区分度：

<!--versetest
assert_semantic_error(3532):
    F(?X:int=42):int = X
    F(?X:int):int = X
<#
-->
<!-- 19-->
```verse
# Same parameter name with/without default
F(?X:int=42):int = X
F(?X:int):int = X  # ERROR
```
<!-- #>-->

**全默认值规则：** 如果两个重载中所有参数都有默认值，则签名是不区分的，因为两者都可以不带参数调用：

<!--versetest
assert_semantic_error(3532):
    F(?X:int=42):int = X
    F(?Y:int=42):int = Y
<#
-->
<!-- 20-->
```verse
# ERROR Both can be called as F()
# F(?X:int=42):int = X
# F(?Y:int=42):int = Y         # ERROR

# ERROR Both callable with no args
# F(?X:int=42):int = X
# F(?X:float=3.14):float = X  # ERROR
```
<!-- #>-->

**不同的参数名称是区分的：** 具有不同命名参数名称的函数可以重载：

<!--versetest-->
<!-- 22-->
```verse
# Valid: Different names
F(?X:int):int = X
F(?Y:int):int = Y  # OK - distinct parameter names
```

**命名参数与位置参数是区分的：** 命名参数与位置参数是区分的，即使名称和类型相同：

<!--versetest-->
<!-- 23-->
```verse
# Valid: Named vs positional
F(?X:int):int = X
F(X:int):int = X  # OK
```

**至少有一个必需参数必须不同：** 如果必需（无默认值）命名参数集合不同，则重载是区分的：

<!--versetest-->
<!-- 24-->
```verse
# Valid: First requires ?Y, second doesn't
F(?Y:int, ?X:int=42):int = X
F(?X:int):int = X  # OK - different required parameter set
```

**位置参数产生区分度：** 不同的位置参数类型使签名具有区分度，即使命名参数相同：

<!--versetest-->
<!-- 25-->
```verse
# Valid: Different positional parameter types
F(Arg:float, ?X:int):int = X
F(Arg:int, ?X:int):int = X  # OK
```

**调用的超集：** 如果一个签名可以处理另一个签名的所有调用，则它们是不区分的：

<!--versetest
assert_semantic_error(3532):
    F(?Y:int=42, ?X:int=42):int = X
    F(?X:int):int = X
<#
-->
<!-- 26-->
```verse
# ERROR 3532: First can handle all calls to second
# F(?Y:int=42, ?X:int=42):int = X
# F(?X:int):int = X  # ERROR - can call first as F(?X := 10)
```
<!-- #>-->

### 元组作为参数

元组可用于提供位置参数。但是，你不能将预先构建的元组变量与额外的命名参数混合使用：

<!--versetest-->
<!-- 28-->
```verse
Calculate(A:int, B:int, ?C:int = 0):int = A + B + C

# Valid: tuple provides positional arguments
Args:tuple(int, int) = (1, 2)
Calculate(Args)  # Returns 3

# Valid: all arguments provided directly
Calculate(1, 2, ?C := 5)  # Returns 8

# Invalid: cannot mix tuple variable with named arguments
# Calculate(Args, ?C := 5)  # ERROR
```

函数可以在参数列表中直接解构元组参数，从而无需手动索引即可内联提取元组元素：

<!--versetest-->
<!-- 29-->
```verse
# Destructure tuple parameter in place
Func(A:int, (B:int, C:int), D:int):int =
    A + B + C + D

Func(1, (2, 3), 4)        # Direct tuple literal - returns 10
X := (2, 3)
Func(1, X, 4)             # Tuple variable - returns 10
Y := (1, (2, 3), 4)
Func(Y)                   # Entire argument list as tuple - returns 10
```

参数 `(B:int, C:int)` 解构了元组，可以直接访问 `B` 和 `C`，而不需要使用 `Tuple(0)` 和 `Tuple(1)` 进行索引。

元组可以解构到任意深度：

<!--versetest-->
<!-- 30-->
```verse
# Simple nesting
H(A:int, (B:int, (C:int, D:int)), E:int):int =
    A + B + C + D + E

H(1, (2, (3, 4)), 5)              # Returns 15
T := (2, (3, 4))
H(1, T, 5)                        # Returns 15
T2 := (1, (2, (3, 4)), 5)
H(T2)                             # Returns 15
```

你可以将解构的元组参数与未解构的常规元组参数混合使用：

<!--versetest-->
<!-- 31-->
```verse
# Destructured form - access elements directly
F(A:int, (B:int, C:int), D:int):int =
    A + B + C + D

# Non-destructured form - use tuple indexing
G(A:int, T:tuple(int, int), D:int):int =
    A + T(0) + T(1) + D

# Both work identically
F(1, (2, 3), 4)  # Returns 10
G(1, (2, 3), 4)  # Returns 10
```

当你需要直接访问单个元素时选择解构形式，当需要将元组作为整体传递给其他函数时选择非解构形式。

元组参数可以包含命名/可选参数，从而允许将结构分解与可选值相结合的灵活 API：

<!--versetest-->
<!-- 32-->
```verse
# Named parameter inside nested tuple
SumValues(A:int, (X:int, (Y:int, ?Z:int = 0))):int =
    A + X + Y + Z

# Can provide Z explicitly
SumValues(1, (2, (3, ?Z := 4)))  # Returns 10

# Can omit Z to use default
SumValues((1, (2, 3)))           # Returns 6
```

一个元组可以包含多个命名参数，并且可以按任意顺序指定：

<!--versetest-->
<!-- 33-->
```verse
ProcessData(Base:int, (Items:[]int, ?Scale:int = 1, ?Offset:int = 0)):int =
    if (First := Items[0]):
        First * Scale + Offset + Base
    else:
        Base

Data := array{100, 200}

ProcessData(10, Data)                              # Uses defaults: 110
ProcessData(10, (Data, ?Scale := 2))               # 210
ProcessData(10, (Data, ?Offset := 5))              # 115
ProcessData(10, (Data, ?Scale := 2, ?Offset := 5)) # 215
ProcessData(10, (Data, ?Offset := 5, ?Scale := 2)) # 215 (order doesn't matter)
```

当元组参数**只包含**命名参数（没有位置参数）时，即使使用全部默认值，也必须提供一个空元组 `()`：

<!--versetest-->
<!-- 34-->
```verse
# Tuple with only named parameters
Configure(Base:int, (?Width:int = 10, ?Height:int = 20)):int =
    Base + Width + Height

# Must provide empty tuple when using all defaults
Configure(5, ())  # Returns 35

# Cannot omit the tuple entirely
# Configure(5)  # ERROR - tuple parameter required
```

这是当前实现中的一个已知限制。当元组至少包含一个位置参数时，此限制不适用。

### 展平与反展平

Verse 在函数调用点提供元组和多个参数之间的自动转换，从而实现灵活的调用约定，而无需显式的打包或解包。

**展平：** 期望多个参数的函数可以用单个元组调用。下面，元组 `Args` 被自动解包到 `Add` 函数的参数中：

<!--versetest-->
<!-- 36-->
```verse
Add(X:int, Y:int):int= X + Y
Args:= (3, 5)
Add(Args)       # Returns 8 - tuple automatically flattened
```

**反展平：** 期望单个元组参数的函数可以用展开的参数调用。对 `F` 调用的各个参数被自动打包到元组参数中：

<!--versetest-->
<!-- 37-->
```verse
F(P:tuple(int, int)):int = P(0) + P(1)

F(3, 5)  # Returns 8 - args automatically packed into tuple
```

空元组具有相同的展平行为：

<!--versetest-->
<!-- 39-->
```verse
F(X:tuple()):int = 42

F(())   # Explicit empty tuple
F()     # No arguments - automatically creates empty tuple
```

**重载限制：** 由于自动展平和反展平，你不能定义会产生歧义的重载。如果你定义了 `F(P:tuple(int, int))`，就不能再定义 `F(X:int, Y:int)`，因为调用 `F(3, 5)` 可能匹配任一签名。类似地，`F(P:tuple(int, int))` 和 `F(Xs:[]int)` 是不区分的，因为数组也可以用相同的语法调用。

### 求值顺序

参数按特定顺序求值以保持可预测的行为：

1. **位置参数**：在调用中从左到右
2. **命名参数**：在调用中遇到时从左到右
3. **默认值**：为省略的参数填充，按参数顺序从左到右

如果命名参数出现的顺序与参数不同，编译器会使用临时变量来保持你指定的求值顺序：

<!--versetest-->
<!-- 40-->
```verse
Process(A:int, ?B:int, ?C:int, ?D:int):string =
    "{A}, {B}, {C}, {D}"

# Call with reordered named args
Process(1, ?D := 4, ?B := 2, ?C := 3)

# Evaluation order: 1, 4, 2, 3 (as written)
# But passed to function in parameter order: 1, 2, 3, 4
```

这确保了参数表达式中的副作用按照你编写它们的顺序发生，而不是按参数顺序。

## 扩展方法

扩展方法允许你向现有类型添加新方法，而无需修改其原始定义。这一强大功能使你能够扩展 Verse 中的任何类型——包括内置类型如 `int`、`string`、数组和映射——添加自定义功能，同时保持不同关注点的清晰分离。

扩展方法在以下场景中特别有价值：

- 你想为内置类型添加领域特定的操作
- 你需要扩展来自你无法控制的库的类型
- 你正在构建流畅式或构建器风格的 API
- 你想将相关功能与类型定义分开组织

扩展方法使用一种特殊的语法，其中被扩展的类型出现在方法名之前的括号中：

<!--versetest-->
<!-- 41-->
```verse
# Extend int with a custom method
(Value:int).Double()<computes>:int = Value * 2

# Call the extension method using dot notation
X := 5
Y := X.Double()  # Returns 10

# Can also call on literals
Z := 7.Double()  # Returns 14
```

括号中的类型可以是任何 Verse 类型：基本类型、元组、类、接口、数组、映射或结构体。

扩展基本类型：

<!--versetest-->
<!-- 42-->
```verse
(N:int).IsEven()<decides><computes>:void = Mod[N,2] = 0
(S:string).FirstChar()<decides><computes>:char = S[0]

42.IsEven[]           # Succeeds
"Hello".FirstChar[] = 'H' 
```

扩展元组：

<!--versetest-->
<!-- 43-->
```verse
# Extend a specific tuple type (Note: Sqrt is <reads>)
(Point:tuple(int, int)).Distance()<reads>:float =
    Sqrt( (Point(0) * Point(0) + Point(1) * Point(1)) * 1.0)

(3, 4).Distance()  # Returns 5.0
```

扩展元组时，必须显式指定元组类型（例如 `(Point:tuple(int, int))`）。你不能在扩展方法上下文中使用解构参数语法（例如 `(X:int, Y:int)`）。

空元组 `tuple()` 表示单元类型，可以有扩展方法：

<!--versetest-->
<!-- 49-->
```verse
(Unit:tuple()).GetMagicNumber():int = 42

().GetMagicNumber()  # Returns 42
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

array{1, 2, 3, 4, 5}.Sum()  # Returns 15
```

扩展映射：

<!--versetest-->
<!-- 45-->
```verse
(M:[int]string).Keys()<computes>:[]int =
    for (Key->X:M):
        Key

map{1=>"a", 2=>"b", 3=>"c"}.Keys()  # Returns array{1, 2, 3}
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
# Add method to existing class
(P:player).AddScore(Points:int):void =
    set P.Score += Points

Player1 := player{Name := "Alice", Score := 100}
Player1.AddScore(50)  # Score becomes 150
```

扩展方法支持所有参数特性，包括命名参数和默认参数：

<!--versetest
<#
-->
<!-- 47-->
```verse
#(Text:string).Pad(?Left:int = 0, ?Right:int = 0):string = ...

"Hello".Pad(?Left:=5)               # "     Hello"
"Hello".Pad(?Right:=5)              # "Hello     "
"Hello".Pad(?Left:= 2, ?Right:=3)   # "  Hello   "
```
<!-- #>-->

### 重载

你可以为不同类型定义多个同名扩展方法：

<!--versetest-->
<!-- 48-->
```verse
# Overloaded Extension method for different types
(N:int).Format():string = "int:{N}"
(B:logic).Format():string = if (B?) {"logic:true"} else {"logic:false"}

42.Format()      # Returns "int:42"
true.Format()    # Returns "logic:true"
```

编译器根据接收者类型选择适当的重载。

### 规则

**必须调用：** 扩展方法不能在未调用的情况下作为一等值引用：

<!--versetest-->
<!-- 50-->
```verse
(N:int).Double():int = N * 2

# Valid: calling the method
X := 5.Double()

# Invalid: referencing without calling
# F := 5.Double  # ERROR
```

**与类方法的冲突：** 扩展方法不能与直接在类或接口中定义的方法具有相同的签名：

<!--versetest
player := class:
    Health():int = 100

<#
-->
<!-- 51-->
```verse
player := class:
    Health():int = 100

# Invalid: Conflicts with class method
# (P:player).Health():int = 50  # ERROR
```
<!-- #>-->

这可以防止歧义，并确保类方法始终优先。

**作用域和可见性：** 扩展方法像普通函数一样有作用域。它们只在定义或导入的地方可见：

<!--versetest
Utils := module:
    (S:string).Reverse<public>():string = S
<#
-->
<!-- 52-->
```verse
# In module A
Utils := module:
    (S:string).Reverse<public>():string =
        # Implementation

# In module B
using { Utils }

"Hello".Reverse()  # Available after importing
```
<!-- #>-->

**类作用域中的扩展方法：** 扩展方法可以在类内部定义并访问类成员：

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
        Score * Multiplier  # Accesses class field

    ProcessScore(Value:int)<computes>:int =
        Value.ScaledScore()  # Uses extension method

GM := game_manager{}
GM.ProcessScore(5)  # Returns 50
```
<!-- #>-->

这会创建一个词法闭包，扩展方法可以引用封闭类的成员。

**元组参数转换：** 当扩展方法有多个参数时，你可以传递一个元组来一次性提供所有参数：

<!--versetest-->
<!-- 54 -->
```verse
point := class<computes>{ X:int; Y:int }

(P:point).Translate(DX:int, DY:int)<allocates>:point =
    point{X := P.X + DX, Y := P.Y + DY}

Origin := point{X := 0, Y := 0}
Delta := (5, 10)
NewPoint := Origin.Translate(Delta)  # Tuple expands to two arguments
```

当元组类型与参数列表匹配时，此功能有效。

## Lambda 表达式

在当前的 Verse 版本中，不支持使用 `=>` 运算符的 lambda 表达式。要创建函数值和闭包，请改用嵌套函数。

函数是一等值；它们可以存储在变量中、作为参数传递、以及从其他函数返回。这实现了强大的函数式编程模式，包括高阶函数、回调和可组合操作。目前，这些能力是通过嵌套函数而非 lambda 表达式提供的。

### 类型、变型和效果

函数类型遵循基于**变型**的特定子类型规则：

- **参数是逆变**：接受更通用类型的函数可以替代接受特定类型的函数。

- **返回值是协变**：返回更具体类型的函数可以替代返回通用类型的函数。

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

以及一些使用场景：

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
# Some functions on animals
AnimalToDog(X:animal):dog = dog{Name := X.Name, Breed := "Unknown"}
DogToWorkingDog(X:dog):working_dog = working_dog{Name := X.Name, Breed := "Unknown", Work := "Guard"}
DogToAnimal(X:dog):animal = X
WorkingDogToDog(X:working_dog):dog = X

# Example of valid assignments
var ProcessDog:type{_(:dog):dog} = AnimalToDog

# Valid: Accepts more general (animal), returns exact (dog)
# Contravariant parameter: animal <: dog allows this
set ProcessDog = AnimalToDog  # OK: tuple(animal)->dog <: tuple(dog)->dog

# Valid: Accepts exact (dog), returns more specific (working_dog)
# Covariant return: working_dog <: dog allows this
set ProcessDog = DogToWorkingDog  # OK: tuple(dog)->working_dog <: tuple(dog)->dog


ProcessDog1 := AnimalToDog  # Inferred as type{_(:animal):dog}
set ProcessDog1 = DogToAnimal  # ERROR: incompatible assignment

ProcessDog2 := AnimalToDog  # Inferred as type{_(:animal):dog}
set ProcessDog2 = WorkingDogToDog  # ERROR: incompatible assignment
```
<!--  #> -->

效果是函数类型的一部分。效果较少的函数可以在期望效果较多的函数的地方使用——效果是**协变的**（效果越少 = 子类型）：

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
UsePure(Pure)                    # OK
UseTransactional(Transactional)  # OK
UseSuspendable(Suspendable)      # OK

# Covariance: fewer effects can substitute for more effects
UseTransactional(Pure)           # OK: ():int <: ()<transacts>:int

# Invalid: more effects cannot substitute for fewer
# UsePure(Transactional)         # ERROR: ()<transacts>:int </: ():int
```
`<computes>` 函数可以在期望 `<transacts>` 的地方传递，因为更少的效果意味着函数受到更多约束。

当你有条件地分配不同的函数时，Verse 会找到它们类型的最小上界（join）：

<!--versetest
base := class:
    Value:int

derived := class(base):
    Extra:string
-->	
<!-- 66-->
```verse
# Assume the following:
# base := class{Value:int}
# derived := class(base){Extra:string}

F1():base = base{Value:=1}
F2():derived = derived{Value:=2, Extra:="test"}

# Join: ()->base (common supertype)
G := if(true?) {F1} else {F2}
G().Value  # Can access base members
```

### 使用 `type{}`

`type{_(...):...}` 语法声明了具有完整细节的函数类型。这是创建包含参数类型、返回类型和效果的函数类型签名的机制。下划线 `_` 是函数名称的占位符，强调它描述的是签名，而不是特定的函数：

<!--versetest-->
<!-- 72-->
```verse
# Function type variable
var Handler:?type{_(:string, :int)<decides>:void} = false

# Nested function matching the signature
MakeHandler(Name:string, Count:int)<decides>:void =
    Print("{Name}: {Count}")
    Count > 0  # Decides effect

set Handler = option{MakeHandler}

# Function accepting function parameter
Process(F:type{_(:int):int}, Value:int):int =
    F(Value)

# Nested function to pass
Double(X:int):int = X * 2
Process(Double, 5)  # Returns 10
```

`type{}` 构造**声明函数类型签名**：

<!--versetest
m:= module:
    ValidType1 := type{_():int}
    ValidType2 := type{_(:string, :int):float}
    ValidType3 := type{_()<transacts><decides>:void}
<#    
-->
<!-- 73-->
```verse
# Type definitions for function signatures
ValidType1 := type{_():int}
ValidType2 := type{_(:string, :int):float}
ValidType3 := type{_()<transacts><decides>:void}
```
<!-- #>-->

在 `type{}` 内部，函数声明必须有返回类型，但**不能有函数体**。

函数类型可以作为类中的字段类型使用：

<!--versetest
calculator := class:
    Operation:type{_(:int,:int):int}
-->
<!-- 74-->
```verse
# Assume:
# calculator := class:
#    Operation:type{_(:int,:int):int}

Add(X:int, Y:int):int = X + Y
Multiply(X:int, Y:int):int = X * Y

# Create instances with different operations
Adder := calculator{Operation := Add}
Multiplier := calculator{Operation := Multiply}

Adder.Operation(5, 3)      # Returns 8
Multiplier.Operation(5, 3) # Returns 15
```

函数类型可以用于局部变量，从而实现有条件的函数选择：

<!--versetest-->
<!-- 75-->
```verse
ProcessA():int = 10
ProcessB():int = 20

SelectFunction(UseA:logic):int =
    # Choose function based on condition
    Fn:type{_():int} =
        if (UseA?):
            ProcessA
        else:
            ProcessB
    Fn()

SelectFunction(true)   # Returns 10
SelectFunction(false)  # Returns 20
```

将 `type{}` 与 `?` 结合使用可以创建可选函数类型：

<!--versetest-->
<!-- 76-->
```verse
DefaultHandler()<computes>:int = -1
CustomHandler()<computes>:int = 42

Process(Handler:?type{_()<computes>:int})<computes><decides>:int =
    # Use handler if provided, otherwise use default
    Handler?() or DefaultHandler()

Process[false]                   # Returns -1 (no handler)
Process[option{CustomHandler}]   # Returns 42 (custom handler)
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

SumFunctions(array{GetZero, GetOne, GetTwo})  # Returns 3
```

### 示例

**映射-过滤-归约（Map-Filter-Reduce）：**

<!--versetest-->
<!-- 78-->
```verse
# Generic map
Map(Items:[]t, F(:t)<transacts>:u where t:type, u:type)<transacts>:[]u =
    for (Item:Items):
        F(Item)

# Generic filter
Filter(Items:[]t, Pred(:t)<computes><decides>:void where t:type)<computes>:[]t =
    for (Item:Items, Pred[Item]):
        Item

# Generic fold/reduce
Fold(Items:[]t, Initial:u, F(:u, :t)<transacts>:u where t:type, u:type)<transacts>:u =
    var Acc:u = Initial
    for (Item:Items):
        set Acc = F(Acc, Item)
    Acc

# Usage with nested functions
Values := array{1, 2, 3, 4, 5}

# Define nested functions for operations
Square(X:int)<computes>:int = X * X
IsEven(X:int)<computes><decides>:void = X = 0 or Mod[X,2] = 0
AddTo(Acc:int, X:int)<computes>:int = Acc + X

Squared := Map(Values, Square)
Evens := Filter(Values, IsEven)
Sum := Fold(Values, 0, AddTo)
```

**函数组合：**

<!--versetest-->
<!-- 79-->
```verse
Compose(F(:b):c, G(:a):b where a:type, b:type, c:type):type{_(:a):c} =
    # Return a nested function that composes F and G
    Composed(X:a):c = F(G(X))
    Composed

Add1(X:int):int = X + 1
Double(X:int):int = X * 2

# Compose: first doubles, then adds 1
DoubleThenIncrement := Compose(Add1, Double)
DoubleThenIncrement(5)  # Returns 11 (5*2 + 1)
```

**偏应用：**

<!--versetest-->
<!-- 80-->
```verse
Partial(F(:a, :b):c, X:a where a:type, b:type, c:type):type{_(:b):c} =
    # Return a nested function with X captured
    PartialFunc(Y:b):c = F(X, Y)
    PartialFunc

Add(X:int, Y:int):int = X + Y
Add5 := Partial(Add, 5)
Add5(3)  # Returns 8
```

## 嵌套函数

!!! warning "未发布的功能"
    嵌套函数尚未发布。本节记录的是当前尚不可用的计划中的功能。

嵌套函数（也称为局部函数）是在其他函数内部定义的函数。它们提供封装性，支持对局部变量的闭包，并帮助在函数作用域内组织复杂逻辑。嵌套函数有名称，可以是递归的，是在 Verse 中创建函数值和闭包的主要方式。

嵌套函数的声明方式与顶层函数相同，但在另一个函数体内：

<!--versetest-->
<!-- 81-->
```verse
Outer(X:int):int =
    # Nested function definition
    Inner(Y:int):int = Y * 2

    # Call nested function
    Inner(X)

Outer(5)  # Returns 10
```

嵌套函数仅在其封闭函数的作用域内可见。它们不能从外部访问。

嵌套函数会捕获（封闭）来自任何封闭作用域的变量，从而创建强大的闭包：

<!--versetest-->
<!-- 82-->
```verse
MakeGreeter(Name:string):type{_():string} =
    # Greeting captures Name from outer scope
    Greeting():string = "Hello, {Name}!"

    # Return the nested function
    Greeting

SayHello := MakeGreeter("Alice")
SayHello()  # Returns "Hello, Alice!"

SayHi := MakeGreeter("Bob")
SayHi()  # Returns "Hello, Bob!"
```

每次调用 `MakeGreeter` 都会创建一个新的闭包，其中包含其自己的捕获的 `Name` 值。

嵌套函数支持按参数类型的重载：

<!--versetest-->
<!-- 83-->
```verse
Process(X:int):string =
    # Overloaded nested functions
    Format(Value:int):string = "int: {Value}"
    Format(Value:float):string = "float: {Value}"

    # Calls appropriate overload
    IntResult := Format(42)       # Calls int version
    FloatResult := Format(3.14)   # Calls float version

    "{IntResult}, {FloatResult}"

Process(1)  # Returns "Int: 42, Float: 3.14"
```

重载解析与顶层函数的工作方式相同。

### 带状态的闭包

嵌套函数可以捕获 `var` 变量并对其进行修改，从而创建有状态的闭包：

<!--versetest-->
<!-- 84-->
```verse
MakeCounter(Initial:int):tuple(type{_():int}, type{_():void}) =
    var Count:int = Initial

    # Getter captures Count
    GetCount():int = Count

    # Incrementer mutates captured Count
    Increment():void = set Count = Count + 1

    (GetCount, Increment)

Counter := MakeCounter(0)
GetValue := Counter(0)
IncrementValue := Counter(1)

GetValue()        # Returns 0
IncrementValue()  # Increments count
GetValue()        # Returns 1
IncrementValue()  # Increments count
GetValue()        # Returns 2
```

这种模式创建了一个维护私有可变状态的闭包。

### 限制

嵌套函数有若干重要的限制，将其与顶层函数区分开来：

- 嵌套函数**不能**具有访问说明符，如 `<public>`、`<internal>` 或 `<private>`：
- 嵌套函数对其封闭函数始终是私有的。
- 你不能在函数内部定义类（无论是嵌套函数还是其他方式）：

<!--versetest
assert_semantic_error(3502):
    F():void =
        my_class := class {}
<#
-->
<!-- 86-->
```verse
# ERROR: Cannot define classes in local scope
F():void =
    my_class := class {}  # ERROR

# Correct: Define classes at module level
my_class := class {}

F():void =
    Instance := my_class{}  # OK - can use class
```
<!-- #>-->

- 嵌套函数不能引用在同一作用域中稍后定义的变量或其他嵌套函数（这也意味着不允许相互递归的嵌套函数）：

<!--versetest
assert_semantic_error(3506):
    F():void =
        X := G()
        G():int = 42
<#
-->
<!-- 87-->
```verse
# ERROR 3506: G used before defined
F():void =
    X := G()     # ERROR: G not yet defined
    G():int = 42

# Correct: Define before use
F():void =
    G():int = 42
    X := G()     # OK: G is defined
```
<!-- #>-->

- `(super:)` 语法用于调用父类方法，**不能**在嵌套函数中使用：

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
# ERROR 3612: super not allowed in nested function
base_class := class:
    F(X:int):int = X

derived_class := class(base_class):
    F<override>(X:int):int =
        G():int =
            (super:)F(X)  # ERROR: super not allowed here
        G()

# Correct: Use super directly in the overriding method
derived_class := class(base_class):
    F<override>(X:int):int =
        BaseResult := (super:)F(X)  # OK
        G():int = BaseResult * 2
        G()
```
<!-- #>-->

## 参数化函数

参数化函数（也称为泛型函数）允许你编写适用于多种类型的代码，同时保持完整的类型安全。你无需为每种类型编写单独的函数，而是定义一个带有类型参数的单一函数，这些类型参数会适应你使用它们的任何类型。

参数化函数使用 `where` 子句声明类型参数，该子句指定对这些类型的约束：

<!--versetest-->
<!-- 89-->
```verse
# Simple identity function - works with any type
Identity(X:t where t:type):t = X
# Usage - type parameter inferred automatically
Identity(42)        # t inferred as int, returns 42
Identity("hello")   # t inferred as string, returns "hello"
```

`where t:type` 子句将 `t` 声明为一个类型参数，约束为 `type`，意味着它可以是任何 Verse 类型。函数签名 `(X:t):t` 的意思是"接受一个类型为 `t` 的值，并返回一个同样类型 `t` 的值"。

泛型类型参数 `t` 捕获完整的类型信息，而不仅仅是顶层类型。这意味着传递给泛型函数的容器会保留其内部结构：

<!--versetest-->
<!-- 901-->
```verse
# The Identity function preserves exact container types
Identity(X:t where t:type):t = X

# Maps maintain their key and value types
IntToString:[int]string = map{1 => "one"}
Result1 := Identity(IntToString)  # Result1: [int]string

# Arrays maintain element types
IntArray:[]int = array{1, 2, 3}
Result2 := Identity(IntArray)  # Result2: []int

# Even nested containers preserve structure
NestedMap:[int][]string = map{1 => array{"a", "b"}}
Result3 := Identity(NestedMap)  # Result3: [int][]string
```

这与使用 `any` 有根本性的不同，后者会擦除类型信息。

<!--NoCompile-->
<!-- 90-->
```verse
FunctionName(Parameters where TypeParameter:Constraint, ...):ReturnType = Body
```

- **类型参数**出现在 `where` 子句中
- **约束**指定要求（例如 `type`、`subtype(comparable)`）
- **多个类型参数**在 `where` 子句中用逗号分隔

Verse 会自动从你传递的参数中推断类型参数，在大多数情况下无需显式类型注解：

<!--versetest-->
<!-- 91-->
```verse
# Function with two type parameters
Pair(X:t, Y:u where t:type, u:type):tuple(t, u) = (X, Y)

# All type parameters inferred
Pair(1, "one")        # t = int, u = string, returns (1, "one")
Pair(true, 3.14)      # t = logic, u = float, returns (true, 3.14)
```

与集合一起的推断：

<!--versetest-->
<!-- 92-->
```verse
# Generic first element function
First(Items:[]t where t:type)<decides>:t = Items[0]

Values := array{1, 2, 3}
Result :int= First[Values]  # t inferred as int from []int
```

当你向期望单个类型参数的参数化函数传递多个值时，Verse 可以推断出元组或数组：

<!--versetest-->
<!-- 93-->
```verse
# Returns the argument unchanged
Identity(X:t where t:type):t = X

# Passing multiple values creates a tuple
Result1:tuple(int, int) = Identity(1, 2)  # t = tuple(int, int)

# Can also be treated as an array
Result2:[]int = Identity(1, 2)  # t = []int via conversion
```

### 类型约束

类型约束限制了哪些类型可以与类型参数一起使用，从而允许需要特定能力的操作。

最宽松的约束接受任何类型：

<!--versetest-->
<!-- 94-->
```verse
# Works with absolutely any type
Store(Value:t where t:type):t = Value
```

限制为指定类型的子类型：

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

# Only accepts vehicle or its subtypes
ProcessVehicle(V:t where t:subtype(vehicle)):t =
    # Can access Speed because we know V is a vehicle
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
# Valid calls
ProcessVehicle(vehicle{})      # t = vehicle
ProcessVehicle(car{})          # t = car (subtype of vehicle)
```

该函数返回类型 `t`，而不是基类型。这保留了具体的类型：

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
# Type-preserving function with subtype constraint
MyCar := car{NumDoors:=4, Speed:=60.0}
Result:car= ProcessVehicle(MyCar)  # Result has type car, not vehicle
Result.NumDoors                  # Can access car-specific fields
```

`subtype(comparable)` 约束启用相等比较：

<!--versetest-->
<!-- 97-->
```verse
# Can use = and <> operators on t
FindInArray(Items:[]t, Target:t where t:subtype(comparable))<decides>:[]int =
    for (Index -> Item : Items, Item = Target):
        Index
```

类型参数可以在约束中相互引用：

<!--versetest-->
<!-- 98-->
```verse
# u must be a subtype of t
Convert(Base:t, Derived:u where t:type, u:subtype(t)):t = Base
# This ensures type safety across related types
```

### 成员访问

使用子类型约束时，你可以访问基类型上存在的成员：

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
# Can access entity members through type parameter
GetInfo(E:t where t:subtype(entity)):tuple(t, string, int) =
    (E, E.Name, E.Health)            # Can access Name and Health

P := player{Name := "Alice", Health := 100, Score := 1500}
Info := GetInfo(P)                   # Returns (player instance, "Alice", 100)
                                     # Info(0) has type player, not entity 
```

方法调用也可以工作：

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

# Call methods on parametrically-typed values
CheckStatus(E:t where t:subtype(entity)):string =
    E.GetStatus()  # Method call through type parameter
```
<!-- #>-->

### 极性和变型

类型参数必须根据变型规则一致地使用。这确保了函数作为值使用或作为参数传递时的类型安全。

**协变位置**（对返回类型安全）：

- 函数返回类型
- 元组/数组元素类型（作为返回）
- 映射键类型（作为返回）
- 映射值类型（作为返回）

**逆变位置**（对参数类型安全）：

- 函数参数类型

**极性检查：** Verse 验证类型参数仅出现在与其预期用途兼容的位置：

<!--versetest-->
<!-- 101-->
```verse
# Valid: t appears covariantly (return type)
GetValue(X:t where t:type):t = X

# Valid: t appears contravariantly (parameter)
Consume(X:t where t:type):void = {}

# Valid: t appears in both positions (through function parameter and return)
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
# ERROR: Cannot return type that's invariant in t
c(t:type) := class{var X:t}  # Mutable field makes c invariant in t
MakeContainer(X:t where t:type):c(t) = c(t){X := X}
```
<!-- #>-->

错误发生是因为 `c(t)` 包含一个类型为 `t` 的可变字段，使其成为不变的——既不是协变也不是逆变。从参数化函数返回这样的类型是不安全的。

**映射极性：** 映射在键和值上都是协变的：

<!--versetest-->
<!-- 103-->
```verse
# Valid: covariant key and value
ProcessMap(M:[t]u where t:subtype(comparable), u:type):[t]u = M
```

## 重载

函数重载允许你定义多个同名但参数类型不同的函数。编译器根据调用点提供的参数类型选择正确的版本。

定义多个同名但参数类型不同的函数：

<!--versetest-->
<!-- 104-->
```verse
# Overload by parameter type
Process(Value:int):string = "Integer: {Value}"
Process(Value:float):string = "Float: {Value}"
Process(Value:string):string = "String: {Value}"

# Calls select the appropriate overload
Process(42)        # Returns "Integer: 42"
Process(3.14)      # Returns "Float: 3.14"
Process("hello")   # Returns "String: hello"
```

编译器根据参数类型确定要调用哪个重载。每个重载必须具有不同的参数类型签名。

### 捕获

你不能获取重载函数名称的引用：

<!--versetest
assert_semantic_error(3502):
    f(x:int):void = {}
    f(x:float):void = {}
    g := f
<#
-->
<!-- 105-->
```verse
# ERROR: Cannot capture overloaded function
f(x:int):void = {}
f(x:float):void = {}

# Error: which f?
g:void = f
```
<!-- #>-->

此限制的存在是因为编译器无法确定你指的是哪个重载，除非看到带有参数的调用点。

### 效果

你可以重载具有不同效果的函数，但前提是参数类型也不同：

**有效：不同类型，不同效果：**

<!--versetest-->
<!-- 106-->
```verse
Process(x:float):float = x
Process(x:int)<transacts><decides>:int = x = 1

Process(3.0)   # Returns 3.0 (non-failable)
Process[1]     # Returns option{1} (failable)
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
# ERROR: Same parameter type
f(x:int):void = {}
f(x:int)<transacts><decides>:void = {}  # ERROR
```
<!-- #>-->

仅凭效果不能产生区分度——你需要不同的参数类型。

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
    # Add new overload for float
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
c0{}.f(5)     # OK - int overload
c1{}.f(5)     # OK - inherited int overload
c1{}.f(5.0)   # OK - new float overload
```

当子类定义了一个与父类方法同名的方法时，它必须：

1. 提供一个**不同的参数类型**（与所有父类重载不同）
2. 使用 `<override>` **精确重写一个**父类重载

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
# Parent class with overloads
e := class:
     func(C:c):c = C
     func(E:e):e = E

# Valid: Overrides one parent overload
myf := class(e):
     func<override>(C:c):d = d{}

# ERROR: d is subtype of c, overlaps but doesn't override
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

**不能将函数与非函数重载：**

一个名称不能同时是函数和非函数值：

<!--versetest
assert_semantic_error(3532):
    f:int = 0
    f():void = {}
<#
-->
<!-- 112-->
```verse
# ERROR: Cannot overload with variable
# f:int = 0
# f():void = {}
```
<!-- #>-->

**底部类型不能解析重载：**

底部类型（来自不带值的 `return`）不能用于重载解析：

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
# ERROR: Cannot determine which overload
F(X:int):int = X
F(X:float):float = X

# G():void =
#     F(@ignore_unreachable return)  # ERROR - which F?
#     0
```
<!-- #>-->

### 与 `<suspends>` 的重载

如果参数类型不同，你可以混合挂起和非挂起重载：

<!--versetest-->
<!-- 115-->
```verse
f(x:int)<suspends>:void =
    Sleep(1.0)

f(x:float):void =
    Print("Non-suspending")

# Call non-suspending directly
f(1.0)

# Call suspending with spawn
spawn{f(1)}
```

**不能在无 spawn 的情况下调用挂起重载：**

<!--versetest
assert_semantic_error(3512):
    f(x:int):void = {}
    f(x:float)<suspends>:void = {}
    g():void = f(1.0)
<#
-->
<!-- 116-->
```verse
# ERROR: suspends version needs spawn context
f(x:int):void = {}
f(x:float)<suspends>:void = {}

g():void = f(1.0)  # ERROR - float version is suspends
```
<!-- #>-->

### 类型

每个函数都有一个类型，捕获其参数、效果和返回值。类型语法使用下划线作为函数名称的占位符：

<!--versetest-->
<!-- 118-->
```verse
type{_(:int,:string)<decides>:float}
```

这表示任何接受一个整数和一个字符串、可能失败、并在成功时返回一个浮点数的函数。

多个函数可以通过重载共享一个名称，只要它们的签名不产生歧义即可。编译器可以根据参数类型区分不同的重载：

<!--versetest-->
<!-- 119-->
```verse
Transform(X:int):string = "I:{X}"
Transform(X:float):string = "F:{X}"
Transform(X:string):string = "S:{X}"

Result1 := Transform(42)        # Calls int version
Result2 := Transform(3.14)      # Calls float version
Result3 := Transform("Hello")   # Calls string version
```

然而，重载有严格的限制，基于**类型区分度**。两个类型只有在没有可能的值同时匹配两个类型时，才被认为是"区分的"。此限制防止了歧义，并确保函数调用始终可以在编译时无歧义地解析。

Verse 使用精确的规则来确定两个参数类型是否足够区分以允许重载。理解这些规则对于设计清晰的 API 至关重要。

以下类型对是**不区分的**，不能用于重载函数：

**1. 可选类型和逻辑类型（Optional and Logic）。** `?t` 和 `logic` 是不区分的，因为两种类型都包含 `false` 作为值，当 `false` 作为参数传递时会产生重载歧义：

<!--versetest
assert_semantic_error(3532):
    F(:?any):void = {}
    F(:logic):void = {}
<#
-->
<!-- 120-->
```verse
# ERROR: Not distinct
F(:?any):void = {}
F(:logic):void = {}
```
<!-- #>-->

注意 `?t` 和 `logic` 不是等价的类型——`logic` 包含 `true` 和 `false`，而 `?t` 包含 `false` 和可选值如 `option{false}`。然而，它们共享的 `false` 值意味着编译器无法在重载解析时区分它们。

**2. 数组和映射（Arrays and Maps）。** 数组 `[]t` 和映射 `[k]t` 是不区分的：

<!--versetest
assert_semantic_error(3532):
    F(:[]int):void = {}
    F(:[string]int):void = {}
<#
-->
<!-- 121-->
```verse
# ERROR: Not distinct
F(:[]int):void = {}
F(:[string]int):void = {}
```
<!-- #>-->

**3. 函数和映射（Functions and Maps）。** 函数类型和映射是不区分的：

<!--versetest
assert_semantic_error(3532):
    F(:[string]int):void = {}
    F(G(:string)<transacts><decides>:int):void = {}
<#
-->
<!-- 122-->
```verse
# ERROR: Not distinct
F(:[string]int):void = {}
F(G(:string)<transacts><decides>:int):void = {}
```
<!-- #>-->

**4. 函数和数组（Functions and Arrays）。** 函数类型和数组是不区分的，因为一个重载函数可能同时匹配两者：

<!--versetest
assert_semantic_error(3532):
    F(:[]int):void = {}
    F(G(:string)<transacts><decides>:int):void = {}
<#
-->
<!-- 123-->
```verse
# ERROR: Not distinct
F(:[]int):void = {}
F(G(:string)<transacts><decides>:int):void = {}
```
<!-- #>-->

**5. 接口和类（Interfaces and Classes）。** 一个接口和任何类永远是不区分的，即使该类没有实现该接口，因为该类的子类型可能实现它：

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

# ERROR: Not distinct (subtype of t might implement i)
f(:i):void = {}
f(:t):void = {}
```
<!-- #>-->

**6. 具有不同效果的函数（Functions with Different Effects）。** 函数不仅仅基于效果来区分。更改或移除效果不会创建区分的重载：

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

# ERROR: Not distinct
F(G(:a)<transacts><decides>:b):void = {}
F(G(:a):b):void = {}
```
<!-- #>-->

**7. 具有不同签名的函数（Functions with Different Signatures）。** 具有不同参数或返回类型的函数是不区分的，因为函数重载的原因：

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
# ERROR: Not distinct
F(G(:b):b):void = {}
F(G(:a):b):void = {}
```
<!-- #>-->

**8. void 作为顶层类型（void as Top Type）。** `void` 被视为与顶层类型（接受 `any`）等价，因此它与任何其他类型都不区分：

<!--versetest
assert_semantic_error(3532):
    F(:int):void = {}
    F(:void):void = {}
<#
-->
<!-- 128-->
```verse
# ERROR: Not distinct
F(:int):void = {}
F(:void):void = {}
```
<!-- #>-->

**9. 子类型关系（Subtype Relationships）。** 具有子类型关系的类是不区分的：

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

# ERROR: Not distinct
F(:a):void = {}
F(:b):void = {}
```
<!-- #>-->

**10. 元组区分度规则（Tuple Distinctness Rules）。** 元组有复杂的区分度规则：

**空元组和数组是不区分的：**

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

# ERROR: Not distinct
F(:tuple(), :a):void = {}
F(:[]a, :a):void = {}
```
<!-- #>-->

**元组和数组只有在元组元素类型完全不同时才区分：**

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

# ERROR: Not distinct (b is subtype of a)
F(:tuple(a, b), :a):void = {}
F(:[]a, :a):void = {}
```
<!-- #>-->

**元组和带有 `int` 键的映射是不区分的：**

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

# ERROR: Not distinct
F(:tuple(a), :a):void = {}
F(:[int]a, :a):void = {}
```
<!-- #>-->

**元组和带有非 `int` 键的映射是区分的：**

<!--versetest
a := class{}

F(:tuple(a), :a):void = {}
F(:[logic]a, :a):void = {}
<#
-->
<!-- 133-->
```verse
a := class{}

# Valid: Distinct types
F(:tuple(a), :a):void = {}
F(:[logic]a, :a):void = {}  # OK
```
<!-- #>-->

**单元素元组和 `int` 的可选类型是不区分的：**

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

# ERROR: Not distinct
F(:tuple(int), :a):void = {}
F(:?int, :a):void = {}
```
<!-- #>-->

**单元素元组和非 `int` 的可选类型是区分的：**

<!--versetest
a := class{}
-->
<!-- 135-->
```verse
# Valid: Distinct types
F(:tuple(a), :a):void = {}
F(:?a, :a):void = {}  # OK
```

## 发布函数

发布函数是对函数与其客户端之间向后兼容性的承诺。考虑以下函数：

<!--versetest-->
<!-- 139-->
```verse
F1<public>(X:int):int = X + 1
```

类型注解 `(X:int):int` 告诉我们，该函数承诺给定任何整数，它总是返回一个整数。该契约在代码的未来版本中不能被打破。由于它具有默认效果（包括 `<reads>` 效果），实现可以在未来更改，也许是为了执行额外的操作或优化，只要它保持其签名。

没有 `<reads>` 效果的函数灵活性较低。考虑以下函数：

<!--versetest-->
<!-- 140-->
```verse
F2<public>(X:int)<computes>:int = X + 1
```

因为它具有 `<computes>` 效果说明符，所以它没有 `<reads>` 效果。在给定版本内，这保证了引用透明性：该函数对于相同的参数总是返回相同的结果。跨版本，这创建了更强的约束：由于编译器无法验证修改后的函数体对于所有可能的参数是否保持相同的输入-输出映射，它保守地禁止任何函数体更改。因此，在未来版本中将函数体改为返回 `X + 2` 将被拒绝，视为向后不兼容。

像 `F1` 和 `F2` 这样的函数有时被称为*不透明*函数，因为返回类型抽象了函数体。未来的 Verse 版本将支持*透明*函数：

<!--NoCompile-->
<!-- 141-->
```verse
F2<public>(X:int) := X + 1
```

透明函数不声明其返回类型，而是从函数体推断函数类型。这意味着一个非常不同的承诺：永远保证函数体在模块代码的整个生命周期内保持完全不变。
