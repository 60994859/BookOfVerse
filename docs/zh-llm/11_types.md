# 类型

每个值都有类型，理解类型系统是掌握任何语言的基础。类型不仅仅是标签——它们构成了一个丰富的层次结构，控制着值在程序中的流动方式、允许哪些操作以及编译器如何推理你的代码。类型系统将静态验证与实用的灵活性相结合，在编译时捕获错误，同时允许复杂的代码复用和抽象模式。

在这个层次结构的顶端是 `any`，所有其他类型都由此通用超类型派生。底部是 `false`，即不包含任何值的空类型（无人居住的类型）。在这两个极端之间是一个精心设计的类型格，每种类型都有自己的能力和约束。

## 理解子类型

子类型是类型层次结构的基础。当我们说类型 A 是类型 B 的子类型时，意味着类型 A 的每个值都可以在需要类型 B 值的地方使用。这种关系在类型之间创建了一种自然的排序，从最具体到最通用。

考虑 `rational` 和 `int` 之间的关系。每个整数都是有理数，但并非每个有理数都是整数。因此，`int` 是 `rational` 的子类型。这意味着你可以将 `int` 传递给任何需要 `rational` 的函数，但反之则不然：

<!--versetest
GetInt(X:int):void = Print("Integer: {X}")
GetRat(X:rational):void = Print("Rational")
assert:
    MyRat:rational = 1/3
    MyInt:int = -10
    GetRat(MyInt)
<# 
-->
<!-- 01 -->
```verse
GetInt(X:int):void = Print("Integer: {X}")
GetRat(X:rational):void = Print("Rational")

MyRat:rational = 1/3
MyInt:int = -10

GetRat(MyInt)  # OK -- int 是 rational 的子类型
GetInt(MyRat)  # 编译错误 - rational 不是 int 的子类型
```
<!-- #> -->

子类型关系以复杂的方式扩展到复合类型。数组和元组对其元素遵循协变子类型规则。这意味着 `[]int` 是 `[]rational` 的子类型。类似地，`tuple(int, int)` 是 `tuple(rational, rational)` 的子类型。这种协变性允许更具体类型的集合在需要更通用类型集合的地方使用。

映射表现出更复杂的子类型行为。当 `K2` 是 `K1` 的子类型（键逆变）且 `V1` 是 `V2` 的子类型（值协变）时，映射类型 `[K1]V1` 是 `[K2]V2` 的子类型。键的逆变乍看起来可能违反直觉，但它确保了类型安全：如果你可以使用更通用的键类型查找值，你也必须能够处理更具体的键类型。

类和接口通过继承引入名义子类型。当一个类继承自另一个类或实现接口时，它显式声明了一个子类型关系：

<!--versetest 02 -->
<!-- 02 -->
```verse
vehicle := class:
    Speed:float = 0.0

car := class(vehicle):  # car 是 vehicle 的子类型
    NumDoors:int = 4

sports_car := class(car):  # sports_car 是 car（及 vehicle）的子类型
    Turbo:logic = true
```

这种继承层次结构意味着 `sports_car` 可以在任何需要 `car` 或 `vehicle` 的地方使用，但不能反过来。子类型从其超类型继承所有字段和方法，同时可能添加新的或覆盖现有的。

## 数值与字符串转换

所有类型转换都必须显式进行，这一设计选择消除了整类错误，同时使程序员的意图清晰明了。数值类型之间的转换清楚地说明了这一原则。要将整数转换为浮点数，乘以 1.0：

<!--versetest-->
<!-- 03 -->
```verse
MyI:int   = 42
MyF:float = MyI * 1.0  # 显式转换为 float
```

!!! note
    禁止隐式转换的最主要原因是，当函数新增重载时，隐式转换可能导致代码出现问题。想象一个调用函数 `f`（接受 float）的场景，如 `f(1)`，如果整数参数被隐式转换为 float，并且在未来的某个库版本中添加了重载 `f(:int)`，那么该调用将静默地调用新函数，并可能改变计算结果。

反向转换（从 float 到 integer）需要选择舍入策略：

<!--versetest-->
<!-- 04 -->
```verse
MyF:float = 3.7
Opt1:int = Floor[MyF]  # 结果为 3
Opt2:int = Ceil[MyF]   # 结果为 4
Opt3:int = Round[MyF]  # 结果为 4（四舍五入到最接近的整数）
```

这些转换函数是可失败的——它们具有 `<decides>` 效果，并且在传入像 `NaN` 或 `Inf` 这样的非有限值时将失败。显式的失败迫使你处理边缘情况：

<!--versetest 05 -->
<!-- 05 -->
```verse
SafeConvert(Value:float):int =
    if:
       Value <> NaN
       Value <> Inf
       Result:= Floor[Value]
    then:
       Result
    else:
       0  # 假设这是安全值
```

字符串转换遵循类似的原则。`ToString()` 函数将各种类型转换为其字符串表示形式，而字符串插值提供了一种便捷的语法用于在字符串中嵌入值：

<!--versetest-->
<!-- 06 -->
```verse
Score:int  = 1500
Msg:string = "Your score: {Score}"  # 隐式 ToString() 调用
```

## 类型 `any`

<!-- TODO add a link to the builtin types -->

`any` 类型位于类型层次结构的顶端，它是可以持有任何类型值的通用超类型。Verse 中的每个类型都是 `any` 的子类型，使其成为最具包容性的类型。当你确实需要处理未知或不同类型值时，它充当逃生出口。

一旦一个值被类型化为 `any`，你就有效地告诉了编译器"我不知道这是什么"，而编译器通过阻止大多数操作来回应。这是有意为之——在不知道实际类型的情况下，编译器无法验证操作是否安全。

你可以使用函数调用语法 `any(42)` 将任何值显式强制转换为 `any`。

当值的类型否则会不兼容时，Verse 会自动将值强制转换为 `any`。理解这些规则有助于处理异构数据。

混合类型的数组和映射会自动强制转换为最具体的共享类型，如果未找到通用类型，则数组强制转换为 `any`：

<!--versetest
SomeFunction():void={}
-->
<!-- 09 -->
```verse
MixedArray := array{42, "hello", true, 3.14} # []comparable
MixedMap := map{0=>"zero", 1=>1, 2=>2.0} # [int]comparable
ConfigMap := map{"count"=>42, "process"=>SomeFunction, "name"=>"Player"} # [string]any
```

分支类型不相交的条件表达式会产生 `any`：

<!--versetest-->
<!-- 11 -->
```verse
# 如果分支返回不同类型
GetValue(UseString:logic):any =
    if (UseString?):
        "text result"
    else:
        42
```

具有不相交类型的逻辑 OR 会强制转换为 `any`：

<!--versetest-->
<!-- 12 -->
```verse
# 返回 int 或 string
OneOf(Flag:logic, I:int, S:string):any =
    (if (Flag?) then {option{I}} else {1=2}) or S
```

`any` 类型有一些限制，反映了其作为通用容器的角色：

- 不能对 `any` 使用相等运算符
- 因为 `any` 不可比较，所以不能用作映射键类型
- 因为 `any` 不可转换，所以它是一种粘性类型

### 泛型函数与类型保留

带有 `where t:type` 约束的泛型函数与接受 `any` 的函数具有根本不同的行为。理解这种区别对于编写类型安全的代码至关重要。

当你将值传递给参数类型为 `any` 的函数时，类型信息会丢失：

<!--versetest-->
<!-- 53 -->
```verse
AcceptAny(X:any):any = X

MyMap:[int]string = map{1 => "one"}
Result := AcceptAny(MyMap)  # Result 的类型为 any - 类型信息丢失
```

相比之下，泛型函数会保留精确的类型：

<!--versetest-->
<!-- 54 -->
```verse
Identity(X:t where t:type):t = X

MyMap:[int]string = map{1 => "one"}
Result := Identity(MyMap)  # Result 的类型为 [int]string - 类型已保留
MyMap = Result  # 成功 - 相同类型
```

这种保留扩展到所有容器类型，包括数组、映射、元组和结构体。泛型类型参数捕获完整类型，包括：

- 映射键和值类型
- 数组元素类型
- 元组组件类型
- 结构体字段类型

**实际影响：**

通过泛型函数传递的容器类型会完全保持其结构：

<!--versetest-->
<!-- 55 -->
```verse
Identity(X:t where t:type):t = X

# 所有键类型都被保留
IntMap:[int]int = map{1 => 2, 3 => 4}
IntMap = Identity(IntMap)  # 相同类型

FloatMap:[float]string = map{1.0 => "one", 2.5 => "two"}
FloatMap = Identity(FloatMap)  # 相同类型

TupleMap:[tuple(int, string)]int = map{(1, "a") => 100}
TupleMap = Identity(TupleMap)  # 相同类型

# 迭代和相等操作按预期工作
for (Key->Value : IntMap):
    Identity(IntMap)[Key] = Value  # 所有查找均成功
```

这使得泛型函数成为编写可复用代码时的首选方法，能够在处理容器时保持类型安全。

## 类和接口的转换

Verse 为类和接口提供了两种不同的转换机制：用于运行时类型检查的可失败转换，以及用于编译时验证的无失败转换。理解何时以及如何使用每种转换对于使用继承层次结构和多态代码至关重要。

可失败转换使用方括号语法 `TargetType[value]` 执行运行时类型检查。如果值不是有效目标类型或其子类型，这些转换会成功并返回转换后的值（`TargetType`），否则失败：

<!--versetest
component := class<castable>:
    Name:string = "Component"

physics_component := class<castable>(component):
    Velocity:float = 0.0

render_component := class<castable>(component):
    Material:string = "default"

ProcessComponent(Comp:component):void =
    if (PhysicsComp := physics_component[Comp]):
        Print("Physics velocity: {PhysicsComp.Velocity}")
    else if (RenderComp := render_component[Comp]):
        Print("Render material: {RenderComp.Material}")
    else:
        Print("Unknown component type")
<#
-->
<!-- 17 -->
```verse
# 定义类层次结构
component := class<castable>:
    Name:string = "Component"

physics_component := class<castable>(component):
    Velocity:float = 0.0

render_component := class<castable>(component):
    Material:string = "default"

# 使用可失败转换进行运行时类型检查
ProcessComponent(Comp:component):void =
    if (PhysicsComp := physics_component[Comp]):
        # 成功转换 - PhysicsComp 是 physics_component
        Print("Physics velocity: {PhysicsComp.Velocity}")
    else if (RenderComp := render_component[Comp]):
        # 不同类型 - RenderComp 是 render_component
        Print("Render material: {RenderComp.Material}")
    else:
        # 两种类型都不匹配
        Print("Unknown component type")
```
<!-- #> -->

如果运行时类型不匹配，转换表达式会求值为 `false`，允许你直接在条件语句中使用它。可选的绑定模式 `(Variable := Expression)` 既执行转换，又在成功时将结果绑定到变量。

对于标记为 `<unique>` 的类，可失败转换会保留标识——成功的转换返回同一实例，而不是副本：

<!--versetest
entity := class<unique><castable>:
    ID:int
player := class<unique>(entity):
    Name:string
assert:
	P := player{ID := 1, Name := "Alice"}
	if (E := entity[P]):
		E = P
<#
-->
<!-- 18 -->
```verse
entity := class<unique><castable>:
    ID:int

player := class<unique>(entity):
    Name:string

# 创建实例
P := player{ID := 1, Name := "Alice"}

# 转换为基类型
if (E := entity[P]):
    E = P  # True - 同一实例
```
<!-- #> -->

可失败转换**仅适用于类和接口类型**。你不能从原始类型、结构体、数组或其他值类型动态转换：

<!--versetest
assert_semantic_error(3512, 3509, 3547):
    component := class<castable>{}
    Comp := component[42]

assert_semantic_error(3512, 3509, 3547):
    component := class<castable>{}
    Comp := component[3.14]

assert_semantic_error(3512, 3509, 3547):
    component := class<castable>{}
    Comp := component["text"]

assert_semantic_error(3512, 3509, 3547):
    component := class<castable>{}
    Comp := component[array{1,2}]

assert_semantic_error(3512, 3509, 3547, 3512):
    component := class<castable>{}
    Value := int[component{}]

assert_semantic_error(3512, 3552, 3547, 3512):
    component := class<castable>{}
    Value := logic[component{}]

assert_semantic_error(3512, 3552, 3547, 3512):
    component := class<castable>{}
    Value := (?int)[component{}]
<#
-->
<!-- 19 -->
```verse
component := class<castable>{}

# 错误：不能从原始类型转换
Comp := component[42]          # int 到 class - 不允许
Comp := component[3.14]        # float 到 class - 不允许
Comp := component["text"]      # string 到 class - 不允许
Comp := component[array{1,2}]  # array 到 class - 不允许

# 错误：不能转换到非类类型
Value := int[component{}]      # class 到 int - 不允许
Value := logic[component{}]    # class 到 logic - 不允许
Value := (?int)[component{}]   # class 到 option - 不允许
```
<!-- #>-->

这个限制存在是因为可失败转换依赖于只有类和接口维护的运行时类型信息。像整数和结构体这样的值类型没有运行时类型标签。

*无失败*转换使用括号语法 `TargetType(value)` 进行编译器可验证始终成功的转换。这些转换要求源类型在编译时是目标类型的子类型：

<!--versetest-->
<!-- 20 -->
```verse
component := class<castable>:
    Name:string = "Component"

physics_component := class<castable>(component):
    Velocity:float = 0.0

# 向上转换：始终安全，始终成功
Base:physics_component = physics_component{Velocity := 10.0}

BaseComp:component = component(Base) # 表达式中的向上转换
# 或
AlsoBaseComp:component = Base # 赋值时的向上转换
```

任何类型都可以无失败地转换为 `void`，这会丢弃值：

<!--versetest
component:=class{}
-->
<!-- 21 -->
```verse
void(42)           # 丢弃整数
void("result")     # 丢弃字符串
void(component{})  # 丢弃对象
```

当你调用一个函数是为了其副作用而希望忽略其返回值时，这种情况隐式发生。

### 基于动态类型的转换

Verse 中的类型是一等值，这意味着你可以将类型存储在变量中并动态用于转换。这为运行时多态性提供了强大的模式：

<!--versetest
component := class<castable>{}
physics_component := class<castable>(component){}
render_component := class<castable>(component){}

ComponentType:castable_subtype(component) = physics_component

TestComponent(Comp:component, ExpectedType:castable_subtype(component)):logic =
    if (Specific := ExpectedType[Comp]):
        true
    else:
        false

assert:
   P := physics_component{}
   TestComponent(P, physics_component)
   TestComponent(P, render_component)
<#
-->
<!-- 22 -->
```verse
# 类型层次结构
component := class<castable>{}
physics_component := class<castable>(component){}
render_component := class<castable>(component){}

# 将类型存储为值
ComponentType:castable_subtype(component) = physics_component

# 使用存储的类型进行转换
Test(Comp:component, ExpectedType:castable_subtype(component)):logic =
    if (Specific := ExpectedType[Comp]):
        true  # 组件匹配期望的类型
    else:
        false

# 与不同类型一起使用
P := physics_component{}
Test(P, physics_component)  # true
Test(P, render_component)   # false
```
<!-- #> -->

当需要检查的类型直到运行时才可知时，这种模式特别强大：

<!--versetest
entity:=class{}
component := class<castable>:
    Owner:entity
physics_component := class<castable>(component){}
render_component := class<castable>(component){}
Components:[]component=array{}
ProcessSpecific(:component)<computes>:void={}
LoadedConfig:string=""
-->
<!-- 23 -->
```verse
# 基于配置选择类型
GetComponentType(Config:string):castable_subtype(component) =
    if (Config = "physics"):
        physics_component
    else if (Config = "render"):
        render_component
    else:
        component

# 使用动态选择的类型
RequiredType := GetComponentType(LoadedConfig)
for (Comp : Components):
    if (Specific := RequiredType[Comp]):
        # 处理所需类型的组件
        ProcessSpecific(Specific)
```

这桥接了编译时类型安全与运行时灵活性，允许基于程序状态做出类型决策，同时保持类型正确性。

## Where 子句

Where 子句是约束泛型代码中类型参数的机制。它们出现在类型参数之后，指定类型必须满足的要求才能成为有效参数。这为编写既灵活又类型安全的泛型代码创建了一个强大的系统。

<!--versetest-->
<!-- 24 -->
```verse
# 简单的子类型约束
Process(Value:t where t:subtype(comparable)):void =
    if (Value = Value):  # 我们知道它支持相等性
        Print("Value equals itself")
```

对同一类型使用多个约束尚未得到支持，实现后将允许编写如下代码：

<!--versetest
assert_semantic_error(3588, 3588, 3503, 3503, 3506, 3532):
    printable := interface:
        PrintIt():void
    F(In:t where t:subtype(comparable), t:subtype(printable)):t =
        Print("Processing: {In}")
        In
<#
-->
<!-- 25 -->
```verse
# 对同一类型的多个约束
F(In:t where t:subtype(comparable), t:subtype(printable)):t = # 不支持
    Print("Processing: {In}")
    In
```
<!-- #> -->

在多个类型参数上工作时，where 子句变得更加强大：

<!--versetest-->
<!-- 26 -->
```verse
# 对不同参数的独立约束
Combine(A:t1, B:t2 where t1:type, t2:type):tuple(t1, t2) =
    (A, B)

# 相关约束
Convert(From:t1, Converter:type{_(:t1):t2} where t1:type, t2:type):t2 =
    Converter(From)
```

Where 子句可以表达类型之间的复杂关系：

<!--versetest
Contains(Arr:[]t, Item:t where t:type)<decides><computes>:logic = false
-->
<!-- 27 -->
```verse
# 确保操作类型兼容的约束
Merge(Container1:[]t, Container2:[]t where t:subtype(comparable)):[]t =
    var Result:[]t = Container1
    for (Element : Container2, not Contains[Result, Element]):
        set Result += array{Element}
    Result

# 函数类型约束
ApplyTwice(F:type{_(:t):t}, Value:t where t:type):t =
    F(F(Value))
```

Where 子句支持复杂的泛型编程模式：

<!--versetest-->
<!-- 28 -->
```verse
MapFunction(F:type{_(:a):b}, Container:[]a where a:type, b:type):[]b =
    for (Element : Container):
        F(Element)
```
## 精炼类型

虽然 `where` 子句约束泛型代码中的类型参数，但**精炼类型**使用 `where` 来约束类型可以持有的*值*。这创建了只接受满足特定条件的值的子类型，实现了由类型系统强制执行的领域特定约束。

一个自然的问题是：当你可以直接截断时，为什么要在超出范围的值上失败？答案是截断会静默传播错误的值，这在某些领域（UI 透明度）是可接受的，但在其他领域是危险的。在精确值至关重要的算法中——位操作、哈希、Unicode 码点操作、坐标系数学——静默截断超出范围的值会产生极难追踪的错误结果。精炼类型使约束显式化，并强制调用者处理违规，从源头捕获错误，而不是让它们传播。

在实践中，像 `positive_int` 或 `zero_to_one_float` 这样的类型别名使得精炼类型在整个代码库中方便复用，无需每次都重复约束表达式。

精炼类型使用值谓词定义受约束的子类型：

<!--versetest
percent := type{_X:float where 0.0 <= _X, _X <= 1.0} 
-->
<!-- 29 -->
```verse
# 百分比：0.0 到 1.0 之间的浮点数
# percent := type{_X:float where 0.0 <= _X, _X <= 1.0}

# 有效赋值
Opacity:percent = 0.5
Alpha:percent = 1.0

# 无效：超出范围（运行时检查失败）
# BadPercent:percent = 1.5  # 赋值时失败
```

**语法结构：**

<!--NoCompile-->
<!-- 30 -->
```verse
TypeName := type{_Variable:BaseType where Constraint1, Constraint2, ...}
```

- `_Variable` 是被约束值的占位符
- `BaseType` 是 `int` 或 `float`
- 约束是使用 `<=`、`<`、`>=` 或 `>` 的比较表达式

整数精炼将 int 值限制在特定范围内：

<!--versetest
age := type{_X:int where 0 <= _X, _X <= 120}
ValidAge:age = 25
positive_int := type{_X:int where _X > 0}
Count:positive_int = 42
small_int := type{_X:int where _X < 100}
<#
-->
<!-- 31 -->
```verse
# 年龄在 0 到 120 之间
age := type{_X:int where 0 <= _X, _X <= 120}

ValidAge:age = 25
# InvalidAge:age = 150  # 不满足约束

# 正整数
positive_int := type{_X:int where _X > 0}

Count:positive_int = 42
# Zero:positive_int = 0  # 失败：不是正数

# 单边界范围
small_int := type{_X:int where _X < 100}
```
<!-- #> -->

浮点数精炼处理具有 IEEE 754 语义的连续范围：

<!--versetest
normalized := type{_X:float where 0.0 <= _X, _X <= 1.0}
positive := type{_X:float where _X > 0.0}
celsius := type{_X:float where _X >= -273.15}
<#
-->
<!-- 32 -->
```verse
# 单位区间 [0.0, 1.0]
normalized := type{_X:float where 0.0 <= _X, _X <= 1.0}

# 正浮点数
positive := type{_X:float where _X > 0.0}

# 绝对零度以上的摄氏温度
celsius := type{_X:float where _X >= -273.15}
```
<!-- #> -->

有限浮点数（排除无穷大）：

<!--versetest
finite := type{_X:float where -Inf < _X, _X < Inf}
assert:
	MaxFinite:finite = 1.7976931348623157e+308
	MinFinite:finite = -1.7976931348623157e+308
<#
-->
<!-- 33 -->
```verse
# 仅限有限值（无 ±Inf）
finite := type{_X:float where -Inf < _X, _X < Inf}

# 最大和最小有限 IEEE 754 双精度数
MaxFinite:finite = 1.7976931348623157e+308
MinFinite:finite = -1.7976931348623157e+308

# 无效：无穷大被排除
# Infinite:finite = Inf  # 不满足约束
```
<!-- #> -->

### IEEE 754 边缘情况

**负零和正零：**

IEEE 754 区分 `+0.0` 和 `-0.0`。在 Verse 中，零就是零，没有正负之分。

<!--versetest-->
当任何表达式求值为零时，符号被丢弃：
<!-- 34 -->
```verse
# 整数零（type{0}）
Value1 := -0
Value2 := +0

Value1 = Value2 # 成功
-0 = +0         # 成功

# 浮点零（type{0.0}）
Value3 := -0.0
Value4 := +0.0

Value3 = Value4 # 成功
-0.0 = +0.0     # 成功
```

**浮点精度：**

约束尊重精确的 IEEE 754 表示：

<!--versetest
small_float := type{_X:float where _X < 0.1}
assert:
    Tiny:small_float = 0.09999999999999999167332731531132594682276248931884765625
<#
-->
<!-- 36 -->
```verse
# 严格小于 0.1 的值
small_float := type{_X:float where _X < 0.1}

# 有效：0.1 之前的最大浮点数
Tiny:small_float = 0.09999999999999999167332731531132594682276248931884765625

# 无效：0.1 的实际表示略高于 0.1
# NotSmall:small_float = 0.1000000000000000055511151231257827021181583404541015625
```
<!-- #> -->

十进制 `0.1` 无法在二进制浮点数中精确表示，因此实际存储的值略高于数学上的 0.1。

### 约束表达式限制

精炼类型约束对允许的表达式有严格限制：

**仅限字面值：** 约束必须使用字面数字，不能使用变量或表达式：

<!--versetest
bounded := type{_X:float where _X < 100.0}

assert_semantic_error(3502):
    Limit:float = 100.0
    bad_type := type{_X:float where _X < Limit}

assert_semantic_error(3512, 3502):
    GetMax():float = 100.0
    bad_type := type{_X:float where _X < GetMax()}

assert_semantic_error(3506, 3502):
    Config := module{Max:float = 100.0}
    bad_type := type{_X:float where _X < (Config:)Max}
<#
-->
<!-- 37 -->
```verse
# 有效：浮点字面值
bounded := type{_X:float where _X < 100.0}

# 无效：不能使用变量
Limit:float = 100.0
bad_type := type{_X:float where _X < Limit}  # ERROR

# 无效：不能使用函数调用
GetMax():float = 100.0
bad_type := type{_X:float where _X < GetMax()}  # ERROR

# 无效：不能使用限定名
Config := module{Max:float = 100.0}
bad_type := type{_X:float where _X < (Config:)Max}  # ERROR
```
<!-- #> -->

这确保约束在编译时是静态已知的。

**浮点类型需要浮点字面值：** 在约束浮点数时，边界必须是浮点字面值（带小数点）：

<!--versetest
good_float := type{_X:float where _X <= 142.0}

assert:
     1
<#
-->
<!-- 38 -->
```verse
# 无效：浮点约束中的整数字面值
# bad_float := type{_X:float where _X <= 142}  # ERROR 3502

# 有效：浮点字面值
good_float := type{_X:float where _X <= 142.0}
```
<!-- #> -->

**不允许 NaN：** 非数字不能出现在约束中：

<!--versetest-->
<!-- 39 -->
```verse
# 无效：约束中的 NaN
# nan_type := type{_X:float where _X <= NaN}      # ERROR 3502
# nan_type := type{_X:float where NaN <= _X}      # ERROR 3502
# nan_type := type{_X:float where 0.0/0.0 <= _X}  # ERROR 3502
```

由于 `NaN` 比较总是 false，这样的约束将无意义。

**允许的字面值形式：**

- 浮点字面值：`1.0`、`3.14`、`-2.5`、`1.7976931348623157e+308`
- 整数字面值：`0`、`42`、`-100`（用于 int 精炼）
- 特殊浮点值：`Inf`、`-Inf`

### 可失败转换

精炼类型在赋值和通过可失败转换时进行检查：

<!--versetest-->
<!--versetest
percent := type{_X:float where 0.0 <= _X, _X <= 1.0}
GetInputFromUser<public>()<computes>:float = 50.0
ProcessPercent<public>(P:percent):void = {}
ShowError<public>(Msg:string):void = {}
assert:
   Valid:percent = 0.5
   UserInput:float = GetInputFromUser()
   if (Value := percent[UserInput]):
       ProcessPercent(Value)
   else:
       ShowError()
<#
-->
<!-- 40 -->
```verse
percent := type{_X:float where 0.0 <= _X, _X <= 1.0}

# 直接赋值（编译时已知）
Valid:percent = 0.5  # OK

# 使用可失败转换进行运行时检查
UserInput:float = GetInputFromUser()
if (Value := percent[UserInput]):
    # UserInput 在 [0.0, 1.0] 范围内
    ProcessPercent(Value)
else:
    # 超出范围
    ShowError()
```
<!-- #> -->

转换 `percent[UserInput]` 返回 `percent`，如果值满足约束则成功，否则失败。

### 示例

精炼类型可作为参数和返回类型：

<!--versetest
finite := type{_X:float where -Inf < _X, _X < Inf}
Half(X:finite):float = X / 2.0
assert:
   Half(100.0)
   Half(1.0)
<#
-->
<!-- 41 -->
```verse
finite := type{_X:float where -Inf < _X, _X < Inf}

# 带约束的参数
Half(X:finite):float = X / 2.0

Half(100.0)  # 返回 50.0
Half(1.0)    # 返回 0.5

# 不能传递无穷大
# Half(Inf)  # ERROR 3509: Inf 不在 finite 中
```
<!-- #> -->

**强制转换与取反：**

<!--versetest
percent := type{_X:float where 0.0 <= _X, _X <= 1.0}
negative_percent := type{_X:float where _X <= 0.0, _X >= -1.0}

assert:
   MakePercent():percent = 0.5
   NegValue:negative_percent = -MakePercent()
   NegValue2:negative_percent = ---0.7
<#
-->
<!-- 42 -->
```verse
percent := type{_X:float where 0.0 <= _X, _X <= 1.0}
negative_percent := type{_X:float where _X <= 0.0, _X >= -1.0}

MakePercent():percent = 0.5

# 取反保持约束兼容性
NegValue:negative_percent = -MakePercent()  # -0.5 有效

# 多次取反
NegValue2:negative_percent = ---0.7  # 三次取反 = -0.7
```
<!-- #> -->

### 重载限制

重叠的精炼类型不能用于函数重载——它们会产生歧义：

<!--versetest
assert_semantic_error(3532):
    percent := type{_X:float where 0.0 <= _X, _X <= 1.0}
    not_infinity := type{_X:float where Inf > _X}
    F(X:percent):float = 0.0
    F(X:not_infinity):float = X
<#
-->
<!-- 43 -->
```verse
percent := type{_X:float where 0.0 <= _X, _X <= 1.0}
not_infinity := type{_X:float where Inf > _X}

# ERROR 3532: 无法区分 - percent ⊂ not_infinity
# F(X:percent):float = 0.0
# F(X:not_infinity):float = X

# 调用 F(0.5) 会产生歧义 - 哪个重载？
```
<!-- #>-->

然而，**不相交**的精炼类型可以重载：
<!--versetest
positive := type{_X:float where _X > 0.0}
negative := type{_X:float where _X < 0.0}
F(X:positive):float = X
F(X:negative):float = X + 1.0
assert:
   F(1.0)=1.0
   F(-1.0)=0.0
<#
-->
<!-- 44 -->
```verse
positive := type{_X:float where _X > 0.0}
negative := type{_X:float where _X < 0.0}

# 有效：范围不重叠（零被两者排除）
F(X:positive):float = X
F(X:negative):float = X + 1.0

F(1.0)   # 返回 1.0（正数重载）
F(-1.0)  # 返回 0.0（负数重载）
# F(0.0)  # 会失败 - 两者都不匹配
```
<!-- #> -->

## Comparable 与相等性

`comparable` 类型代表支持相等比较的特殊类型子集。并非所有类型都可以进行相等比较——这是一个深思熟虑的设计选择，防止无意义的比较并确保相等性具有明确定义的语义。

如果类型的值可以有意义地测试相等性，则该类型是可比较的。基本标量类型都是可比较的：`int`、`float`、`rational`、`logic`、`char` 和 `char32`。如果复合类型的所有组件都是可比较的，那么该复合类型也是可比较的。这意味着整数数组是可比较的，浮点数和字符串的元组是可比较的，具有可比较键和值的映射也是可比较的。

相等运算符 `=` 和 `<>` 是根据 comparable 类型定义的：

<!--NoCompile-->
<!-- 45 -->
```verse
operator'='(X:t, Y:t where t:subtype(comparable))<decides>:t
operator'<>'(X:t, Y:t where t:subtype(comparable))<decides>:t
```

签名要求两个操作数都是 comparable 的子类型，并且返回类型是它们类型的最近公共上界。

<!--versetest
assert:
    0 = 0
    0.0 = 0.0

<#
-->
<!-- 46 -->
```verse
0 = 0        # 成功 - 两者都是 int
0.0 = 0.0    # 成功 - 两者都是 float
0 = 0.0      # 失败 - 没有从 int 到 float 的隐式转换
```
<!-- #> -->

以下示例展示了 `=` 的返回类型如何计算：

<!--46b -->
```verse
I:int=1
R:rational=1/3
X:rational= (I=R)  # 编译通过，运行时失败

I:int=1
S:string="hi"
Y:comparable= (I=S)  # 编译通过，运行时失败
```

在变量 `X` 的情况下，其类型可以是 `rational` 或 `comparable`。对于变量 `Y`，`int` 和 `string` 之间的唯一公共类型是 `comparable`。

类需要特殊处理才能具有可比性。默认情况下，类的实例不可比较，因为没有通用方法来定义用户定义类型的相等性。但是，你可以使用 `unique` 说明符使类可比较：

<!--versetest
entity := class<unique>:
    ID:int
    Name:string

F()<decides>:void={
Player1 := entity{ID := 1, Name := "Alice"}
Player2 := entity{ID := 1, Name := "Alice"}
Player3 := Player1

Player1 = Player2  # Fails - different instances
Player1 = Player3  # Succeeds - same instance
}<#
-->
<!-- 47 -->
```verse
entity := class<unique>:
    ID:int
    Name:string

Player1 := entity{ID := 1, Name := "Alice"}
Player2 := entity{ID := 1, Name := "Alice"}
Player3 := Player1

Player1 = Player2  # 失败 - 不同实例
Player1 = Player3  # 成功 - 同一实例
```
<!--versetest
#>
-->

使用 `unique` 说明符时，实例只与自身相等（标识相等），而不是与具有相同字段值的其他实例相等（结构相等）。这为类相等性提供了清晰、可预测的语义。

### Comparable 作为泛型约束

`comparable` 类型通常用作泛型函数中的约束，以确保相等性测试等操作可用：

<!--versetest
Find(Items:[]t, Target:t where t:subtype(comparable))<decides>:int =
    Results := for (Index->Item:Items, Item = Target):
        Index
    Results[0]

assert:
    # Works with any comparable type
    Position := Find[array{"apple", "banana", "cherry"}, "banana"]  # Succeeds and returns 1
    Position = 1
<#
-->
<!-- 48 -->
```verse
Find(Items:[]t, Target:t where t:subtype(comparable))<decides>:int =
    Results := for (Index->Item:Items, Item = Target):
        Index
    Results[0]

# 适用于任何可比较类型
Position := Find[array{"apple", "banana", "cherry"}, "banana"]  # 成功并返回 1
```
<!-- #>-->

### 数组-元组比较

Verse 相等性系统的一个显著特性是，可比较元素的数组和元组可以相互比较：

<!--versetest-->
<!-- 49 -->
```verse
# 数组可以等于元组
array{1, 2, 3} = (1, 2, 3)       # 成功
(4, 5, 6) = array{4, 5, 6}       # 成功 - 双向

# 不等性也同样有效
array{1, 2, 3} <> (1, 2, 4)      # 成功 - 不同值
```

这种比较是结构性的——序列必须具有相同的长度且对应元素必须相等。此特性允许需要数组的函数接受元组，提高了灵活性。

### 带 Comparable 的重载区分

你不能创建其中一个参数是具体 comparable 类型而另一个是通用 `comparable` 类型的重载，因为这会产生歧义：

<!--versetest
assert_semantic_error(3532):
    F(X:int):void = {}
    F(X:comparable):void = {}

assert_semantic_error(3532):
    unique_class := class<unique>{}
    G(X:unique_class):void = {}
    G(X:comparable):void = {}
<#
-->
<!-- 50 -->
```verse
# 不允许 - 歧义重载
F(X:int):void = {}
F(X:comparable):void = {}  # ERROR: int 已经是 comparable 的

# 对于 unique 类也不允许
unique_class := class<unique>{}
G(X:unique_class):void = {}
G(X:comparable):void = {}  # ERROR: unique_class 是 comparable 的
```
<!-- #> -->

但是，你可以使用非 comparable 类型进行重载：

<!--versetest-->
<!-- 51 -->
```verse
# 这是允许的
regular_class := class{}  # 不可比较
H(X:regular_class):void = {}
H(X:comparable):void = {}  # OK：无歧义
```

### 动态 Comparable 值

在处理异构集合时，你可能需要将 comparable 值显式装箱到 `comparable` 类型中。这些装箱后的值保持其相等性语义：

<!--versetest-->
<!-- 52 -->
```verse
AsComparable(X:comparable):comparable = X

# 装箱后的值在装箱和未装箱状态下都能正确比较
array{AsComparable(1)} = array{1}              # 成功
array{AsComparable(1)} = array{AsComparable(1)} # 成功
array{AsComparable(1)} <> array{2}             # 成功

# 直接向上转换：
comparable(15) = comparable(15)     # 成功
comparable("Hello") = "Hello"       # 成功
```

这允许你通过将所有值装箱到 `comparable` 来创建混合不同 comparable 类型的集合。

### 映射键与 Comparable

映射键必须是可比较类型。大多数可比较类型都可以用作映射键，包括：

- 所有数值类型：`int`、`float`、`rational`
- 字符类型：`char`、`char32`
- 文本：`string`
- 枚举
- `<unique>` 类
- 可比较类型的可选类型：`?t` 其中 `t` 是可比较的
- 可比较类型的数组：`[]t` 其中 `t` 是可比较的
- 可比较类型的元组
- 具有可比较键和值的映射：`[k]v`
- 具有可比较字段的结构体

注意，虽然 `float` 可以用作映射键，但浮点特殊值具有特定的相等性语义（有关 `NaN` 和零处理的详细信息，请参阅[映射文档](02_primitives.md#floats)）。

目前无法通过编写自定义比较方法使普通类可比较。只有 `<unique>` 说明符通过标识相等性启用类的可比性。

## 类型层次结构

类型系统形成了一个格（lattice）而不是简单的树。这意味着类型可以有多个超类型，尽管多重继承目前仅限于接口。理解这些关系有助于你设计灵活、可复用的代码。

### 理解 void

与擦除类型信息的 `any` 不同，`void` 充当"丢弃"类型，表示值的具体类型无关紧要。

返回类型为 `void` 的函数可以返回任何值，这些值随后会被类型系统丢弃：

<!--versetest
WriteToFile(:string)<transacts>:void = {}
-->
<!-- 77 -->
```verse
LogEvent(Message:string)<transacts>:void =
    WriteToFile(Message)
    42                   # 返回 int，但类型化为 void

F():void = 1             # 有效 - 返回 int，类型化为 void
F()                      # 结果为 void
```

尽管类型化为 `void`，这些函数仍然会产生其计算的值——只是这些值无法通过类型系统访问。这确保了即使返回值被丢弃，副作用和计算也会发生：

<!--versetest-->
<!-- 78 -->
```verse
MakePair(X:string, Y:string):void = (X, Y)

# 函数仍会计算该对，即使返回类型是 void
MakePair("hello", "world")  # 仍然创建 ("hello", "world")
```

参数类型为 `void` 的函数接受任何参数类型：

<!--versetest-->
<!-- 79 -->
```verse
Discard(X:void):int = 42

Discard(0)               # int -> void 
Discard(1.5)             # float -> void 
Discard("test")          # string -> void 
```

类字段可以类型化为 `void`，接受任何初始化值：

<!--versetest-->
<!-- 80 -->
```verse
config := class:
    Setting:void = array{1, 2}  # 使用数组作为默认值
```

在函数类型中，`void` 参与变异性：

<!--versetest-->
<!-- 81 -->
```verse
IntIdentity(X:int):int = X

# 逆变返回：返回位置的超类型
F:int->void = IntIdentity  # int->int -> int->void ✓
# void 是 int 的超类型，所以这可以工作

AcceptVoid(X:void):int = 19

# 逆变参数：参数位置的超类型
G:int->int = AcceptVoid    # void->int -> int->int ✓
# 可以在需要 int->int 的地方使用接受 void->int 的函数
```

然而，参数位置中的 `void` 不允许反向转换：

<!--versetest
# Test that this conversion is not allowed
assert_semantic_error(3509):
    IntFunction(X:int):int = X
    F:void->int = IntFunction  # ERROR: Cannot convert int->int to void->int
<#
-->
<!-- 82 -->
```verse
IntFunction(X:int):int = X
# F:void->int = IntFunction  # ERROR
# 不能将 int 参数转换为函数类型中的 void 参数
```
<!-- #>-->

**void 与 false 对比**：`false` 类型是空/底部类型（无人居住的类型），不包含任何值。它与 `void` 相反：

- **`void`**：通用超类型——所有类型都是 void 的子类型，包含所有值
- **`false`**：底部类型——是所有类型的子类型，包含零个值

在通用超类型（`any`、`void`）和底部类型（`false`）之间，类型形成了自然的组合。数值类型（`int`、`float`、`rational`）共享常见的算术运算，但并未形成单一的层次结构——它们是同级而非祖先和后代关系。容器类型（数组、映射、元组、可选类型）各自基于其元素类型拥有自己的子类型规则。

理解变异性对于使用泛型容器至关重要。数组和可选类型在其元素类型上是协变的——如果 A 是 B 的子类型，那么 `[]A` 是 `[]B` 的子类型，`?A` 是 `?B` 的子类型。这允许像这样的自然代码：

<!--versetest
RationalPrinter(X:rational):string=""
-->
<!-- 89 -->
```verse
ProcessNumbers(Nums:[]rational):void =
    for (N : Nums):
        Print("{RationalPrinter(N)}")

IntArray:[]int = array{1, 2, 3}
ProcessNumbers(IntArray)  # 由于协变性而有效
```

函数表现出更复杂的变异性。它们在其参数类型上是逆变的，在其返回类型上是协变的。如果 T2 是 T1 的子类型（逆变）且 R1 是 R2 的子类型（协变），那么函数类型 `(T1)->R1` 是 `(T2)->R2` 的子类型。这确保了函数子类型保持了类型安全：

<!--versetest
function_type1 := type{_(:any):int}
function_type2 := type{_(:int):any}
# Concrete function that matches function_type1
ConcreteFunc(Input:any):int = 42
# Function that takes function_type2 and uses it
UseFunction(F:function_type2, Value:int):void =
    Result:any = F(Value)  # Call with int, get any
TestSubtyping():void =
    UseFunction(ConcreteFunc, 5)
<#
-->
<!-- 90 -->
```verse
function_type1 := type{_(:any):int}
function_type2 := type{_(:int):any}

# function_type1 是 function_type2 的子类型
# 它接受更通用的输入（any vs int）——逆变
# 并返回更具体的输出（int vs any）——协变

# 演示：匹配 type1 的函数可以在需要 type2 的地方使用
ConcreteFunc(Input:any):int = 42

UseFunction(F:function_type2, Value:int):void =
    Result:any = F(Value)

UseFunction(ConcreteFunc, 5)  # 有效：function_type1 <: function_type2
```
<!-- #>-->

## 类型别名

类型别名允许你为类型创建替代名称，使复杂的类型签名更具可读性和可维护性。它们对于函数类型、参数化类型和经常使用的类型组合尤其有价值。

类型别名在模块作用域使用简单的赋值语法创建：

<!--versetest
# At module scope
entity:=struct{}

# Simple type aliases
coordinate := tuple(float, float, float)
entity_map := [string]entity
player_id := int

# Function type aliases
update_handler := type{_(:float):void}
validator := int -> logic
transformer := type{_(:string):int}
<#
-->
<!-- 91 -->
```verse
# 在模块作用域
entity:=struct{}

# 简单类型别名
coordinate := tuple(float, float, float)
entity_map := [string]entity
player_id := int

# 函数类型别名
update_handler := type{_(:float):void}
validator := int -> logic
transformer := type{_(:string):int}
```
<!-- #> -->

类型别名仅在编译时存在——它们不产生运行时开销，纯粹是为了程序员的便利和代码清晰度。

**类型别名是替代名称，而不是新类型。** 它们不像某些语言中的 `newtype` 那样创建不同的类型。别名和原始类型的值完全可以互换：

<!--versetest
player_id := int
game_id := int
-->
<!-- 92 -->
```verse
# 假设
# player_id := int
# game_id := int

ProcessPlayer(ID:player_id):void = {}
ProcessGame(ID:game_id):void = {}

PID:player_id = 42
GID:game_id = 42

# 所有这些都有效——别名只是名称
ProcessPlayer(PID)      # OK
ProcessPlayer(GID)      # OK - game_id 也是 int
ProcessPlayer(42)       # OK - int 字面值也可以
ProcessGame(PID)        # OK - player_id 也是 int
```

类型别名可以具有访问说明符，控制其在模块间的可见性：

<!--versetest
# Public alias - accessible from other modules
PublicAlias<public> := int

# Internal alias - only accessible within defining module
InternalAlias<internal> := string

# Note: Protected/private are for classes and interfaces, not type aliases at module scope
<#
-->
<!-- 93 -->
```verse
# 公有别名 - 可从其他模块访问
PublicAlias<public> := int

# 内部别名 - 仅在定义模块内可访问
InternalAlias<internal> := string

# Protected/private 也有效
ProtectedAlias<protected> := float  # 仅在类与接口中
```
<!-- #> -->

**类型别名不能比其别名的类型具有更高的可见性：**

<!--versetest
private_class := class{}

InternalToInternal<internal> := private_class
InternalAlias := private_class  # Defaults to internal

# Test that public alias to internal type produces error
assert_semantic_error(3593):
    M<public> := module:
        internal_class := class{}
        PublicToInternal<public> := internal_class
<#
-->
<!-- 94 -->
```verse
private_class := class{}      # 无说明符 = internal 作用域

# 无效：公有别名指向内部类型
# PublicToPrivate<public> := private_class

# 有效：相同或更低可见性
InternalToInternal<internal> := private_class
InternalAlias := private_class  # 默认为 internal
```
<!-- #> -->

### 要求

- **类型别名只能在模块作用域定义。** 它们不能在类、函数或任何嵌套作用域内定义。此限制确保类型别名具有一致的可见性，并防止依赖于作用域的类型解释。

- 类型别名必须在其**使用之前**定义。不允许前向引用。

- 类型别名不是一等值，不能这样使用。

## 元类型

Verse 提供了高级类型构造器，允许你将类型作为值使用，从而实现运行时多态性和泛型实例化的强大模式。这些元类型——`subtype`、`concrete_subtype` 和 `castable_subtype`——桥接了编译时类型安全与运行时灵活性。

### subtype

`subtype(T)` 类型构造器表示 `T` 的子类型的运行时类型值。与专门用于类和接口的 `concrete_subtype` 和 `castable_subtype` 不同，`subtype(T)` 适用于 Verse 中的**任何类型**，包括原始类型、枚举、集合和函数类型。

<!--versetest
animal := class<computes> {}
dog := class<computes>(animal) {}

registry := class<computes><allocates>:
    var AnimalType:subtype(animal) = animal

    # Assign class types
    F0()<transacts>:void = set AnimalType = animal
    F1()<transacts>:void = set AnimalType = dog

    # Accept as parameter
    F3(ClassArg:subtype(animal))<transacts>:void = set AnimalType = ClassArg
<#
-->
<!-- 100 -->
```verse
animal := class {}
dog := class(animal) {}

# 使用 subtype 作为字段类型的示例
var AnimalType:subtype(animal)  # 可以持有 animal、dog 或 animal 的任何子类型

# 分配类类型
F0():void = set AnimalType = animal
F1():void = set AnimalType = dog  # dog 是 animal 的子类型

# 作为参数接受
F3(ClassArg:subtype(animal)):void = set AnimalType = ClassArg
```
<!-- #>-->

`subtype(T)` 的关键能力是在运行时持有类型值，同时通过子类型关系保持类型安全。

与其他元类型不同，`subtype(T)` 接受任何类型作为其参数：

<!--versetest
my_enum := enum { A, B, C }
my_class := class {}
my_interface := interface {}
-->
<!-- 101 -->
```verse
# 原始类型
IntType:subtype(int) = int
LogicType:subtype(logic) = logic
FloatType:subtype(float) = float

# 枚举
EnumType:subtype(my_enum) = my_enum

# 类和接口
ClassType:subtype(my_class) = my_class
InterfaceType:subtype(my_interface) = my_interface

# 注意：subtype() 中的集合类型和函数类型目前存在问题：
# ArrayType:subtype([]int) = []int  # 错误：无法定义
# OptionType:subtype(?string) = ?string  # 错误：无法定义
# FuncType:subtype(type{_():void}) = type{_():void}  # 错误：无法定义
```

这种通用性使 `subtype(T)` 成为元类型中最灵活的一个，适用于任何需要存储或传递类型值的场景。

**子类型关系：**

`subtype` 构造器保留了子类型关系：`subtype(T) <: subtype(U)` 当且仅当 `T <: U`。这意味着你可以将更具体的子类型赋值给不太具体的子类型：

<!--versetest-->
<!-- 102 -->
```verse
super_class := class{}
sub_class := class(super_class) {}

# 协变：sub_class <: super_class
SubtypeVar:subtype(sub_class) = sub_class
SupertypeVar:subtype(super_class) = SubtypeVar  # 有效

# 反向失败 - super_class 不是 <: sub_class
# SubtypeVar2:subtype(sub_class) = super_class
```

这也适用于接口：

<!--versetest-->
<!-- 103 -->
```verse
super_interface := interface{}
sub_interface := interface(super_interface) {}

class_impl := class(sub_interface) {}

# 通过接口层次结构的协变
SpecificType:subtype(sub_interface) = class_impl
GeneralType:subtype(super_interface) = SpecificType  # 有效
```

**与接口一起使用：**

当使用接口时，`subtype(T)` 可以持有任何实现该接口的类：

<!--versetest-->
<!-- 104 -->
```verse
printable := interface:
    PrintIt():void

document := class(printable):
    PrintIt<override>():void = {}

# 可以持有任何实现 printable 的类型
DocumentType:subtype(printable) = document
```

**与 `type` 的关系：**

`subtype(T)` 和 `castable_subtype(T)` 都是 `type` 的子类型，这意味着它们可以在需要 `type` 的地方使用：

<!--versetest-->
<!-- 105 -->
```verse
c := class:
    f(C:subtype(c)):type = return(C)  # 有效：subtype(c) <: type

t := interface {}
g(x:subtype(t)):type = x  # 有效：subtype(t) <: type
```

**限制：**

虽然 `subtype(T)` 很灵活，但它有一些重要的限制：

1. **不能作为值使用：** `subtype(T)` 是类型构造器，而不是值。你不能将 `subtype(T)` 本身作为值使用。
2. **恰好一个参数：** `subtype` 需要恰好一个类型参数。
3. **不能与属性一起使用：** `subtype` 不能用于继承自 `attribute` 的类。

### concrete_subtype

`concrete_subtype(t)` 类型构造器创建一个表示 `t` 的具体（可实例化）子类的类型。具体类是可以直接实例化的类——它具有 `<concrete>` 说明符并为所有字段提供默认值：

<!--versetest-->
<!-- 110 -->
```verse
# 抽象基类
entity := class<abstract>:
    Name:string
    GetDescription():string

# 具体实现
player := class<concrete>(entity):
    Name<override>:string = "Player"
    GetDescription<override>():string = "A player character"

enemy := class<concrete>(entity):
    Name<override>:string = "Enemy"
    GetDescription<override>():string = "An enemy creature"

# 存储类型并可实例化的类
spawner := class:
    EntityType:concrete_subtype(entity)

    Spawn():entity =
        # 使用存储的类型实例化
        EntityType{}

# 使用
# NewEntity := spawner{EntityType := player}.Spawn()
```

`concrete_subtype` 的关键特性是确保存储的类型可以被实例化。没有这个约束，你不能安全地调用 `EntityType{}`，因为抽象类不能被实例化。

#### 要求

一个类型只有在是类或接口类型时才能与 `concrete_subtype` 一起使用。此外，实际赋值的类型值必须是具体类——即标记了 `<concrete>` 并且所有字段都有默认值：

<!--versetest-->
<!-- 111 -->
```verse
# 有效：具有所有默认值的具体类
config := class<concrete>:
    MaxPlayers:int = 8
    TimeLimit:float = 300.0

ConfigType:concrete_subtype(config) = config  # 有效

# 无效：抽象类不能作为 concrete_subtype
abstract_base := class<abstract>:
    Value:int

# 这会是一个错误：
# BaseType:concrete_subtype(abstract_base) = abstract_base
```

当你有一个 `concrete_subtype` 时，你可以使用空原型 `{}` 实例化它，但不能提供字段初始化器——具体类必须提供所有必要的默认值：

<!--versetest-->
<!-- 112 -->
```verse
entity_base := class<abstract>:
    Health:int

warrior := class<concrete>(entity_base):
    Health<override>:int = 100

EntityType:concrete_subtype(entity_base) = warrior

# 有效：空原型使用默认值
# Instance := EntityType{}

# 无效：不能通过元类型初始化字段
# Instance := EntityType{Health := 150}
```

### castable_subtype

`castable_subtype(t)` 类型构造器表示 `t` 的子类型并标记了 `<castable>` 说明符的类型。这启用了运行时类型查询和动态转换，对于组件系统多态层次结构至关重要：

<!--versetest
entity:=class{}
vector3:=class{}
-->
<!-- 113 -->
```verse
# 可转换的基类
component := class<abstract><castable>:
    Owner:entity

# 可转换的子类型
physics_component := class<castable>(component):
    Velocity:vector3

render_component := class<castable>(component):
    Material:string

# 接受可转换子类型的函数
ProcessComponent(CompType:castable_subtype(component), Comp:component):void =
    # 可以使用 CompType 执行类型安全的转换
    if (Specific := CompType[Comp]):
        # Comp 现在已知是 CompType 类型
```

### final_super 与类型查询

`castable_subtype` 与 `<final_super>` 说明符和 `GetCastableFinalSuperClass` 函数配合使用，实现复杂的运行时类型查询。这种组合为组件系统多态架构提供了强大的机制。

`<final_super>` 说明符将类标记为继承层次结构中的稳定锚点。这些"最终超类"作为相关类型族的规范代表：

<!--versetest
entity:=class{}
vector3:=class{}
-->
<!-- 114 -->
```verse
component := class<castable>:
    Owner:entity

# 物理组件族的稳定锚点
physics_component := class<final_super>(component):
    Velocity:vector3

# 具体实现继承自锚点
rigid_body := class(physics_component):
    Mass:float

soft_body := class(physics_component):
    SpringConstant:float
```

通过将 `physics_component` 标记为 `<final_super>`，你声明它是所有物理相关组件的规范代表。即使 `rigid_body` 和 `soft_body` 是不同的类型，它们都属于锚定在 `physics_component` 的"physics_component 族"。

#### GetCastableFinalSuperClass

`GetCastableFinalSuperClass` 函数查询类型层次结构，找到基类型和派生类型之间的 `<final_super>` 类。存在两个变体：

<!--NoCompile-->
<!-- 115 -->
```verse
# 接受实例
GetCastableFinalSuperClass(BaseType, instance)<decides>:castable_subtype(BaseType)

# 接受类型
GetCastableFinalSuperClassFromType(BaseType, Type)<decides>:castable_subtype(BaseType)
```

两者都返回一个 `castable_subtype`，表示最不具体的 `<final_super>` 类，该类满足：

1. 直接从指定的基类型继承
2. 在实例/类型的继承链中

如果不存在合适的 `<final_super>` 类，函数失败。

考虑这个层次结构：

<!--versetest
vector3:=class{}
-->
<!-- 116 -->
```verse
component := class<castable>:
    ID:int

# component 的直接 final_super 子类
physics_component := class<final_super>(component):
    Velocity:vector3

# physics_component 的后代
rigid_body := class(physics_component):
    Mass:float

character_body := class(rigid_body):
    Health:int
```

查询结果：

<!--versetest
entity:=class{}
vector3:=class{}
component:=class{}
character_body:=class(component){ID :int, Velocity :vector3, Mass :float, Health :int}
-->
<!-- 117 -->
```verse
# physics_component 族中的所有实例都返回 physics_component
Body := character_body{ID:=1, Velocity:=vector3{}, Mass:=10.0, Health:=100}

if (Family := GetCastableFinalSuperClass[component, Body]):
    # Family = physics_component（final_super 锚点）
    # 即使 Body 是 character_body，族锚点是 physics_component
```

函数沿着继承链从 `character_body` -> `rigid_body` -> `physics_component` "向上走"，停在 `physics_component` 因为：

1. 它具有 `<final_super>`
2. 它直接从查询的基类型（`component`）继承

**查询何时成功和失败？**

**成功时：**

- 一个 `<final_super>` 类直接从基类型继承
- 实例/类型继承自该 `<final_super>` 类

<!--versetest
base := class<castable>:
    Value:int=1
anchor := class<final_super>(base):
    Extra:string=""
derived := class(anchor){ More:string="" }

# Test that the calls succeed (don't fail)
TestQueries()<decides>:void =
    if:
        Result1 := GetCastableFinalSuperClass[base, derived{}]  # Returns anchor
        Result2 := GetCastableFinalSuperClass[base, anchor{}]   # Returns anchor
    then:
        void
<#
-->
<!-- 118 -->
```verse
base := class<castable>:
    Value:int

anchor := class<final_super>(base):
    Extra:string

derived := class(anchor):
    More:string

# 有效：anchor 是 base 的 final_super，derived 继承自 anchor
GetCastableFinalSuperClass[base, derived{}]  # 返回 anchor
GetCastableFinalSuperClass[base, anchor{}]   # 返回 anchor
```
<!-- #>-->

**失败时：**

- 基类型和实例之间不存在 `<final_super>` 类
- 查询的类型本身就是实例类型（不能从同一层级查询）
- 实例不是基类型的子类型

#### 多重 Final Super

你可以在不同层级有多个 `<final_super>` 类。函数返回直接从查询的基类型继承的那一个：

<!--versetest
base := class<castable>:
    ID:int=1
first_anchor := class<final_super>(base):
    Category:string=""
second_anchor := class<final_super>(first_anchor):
    Subcategory:string=""
leaf := class(second_anchor){ Specific:string="" }

# Test that the calls succeed
TestQueries()<decides>:void =
    if:
        Result1 := GetCastableFinalSuperClass[base, leaf{}]  # Returns first_anchor
        Result2 := GetCastableFinalSuperClass[first_anchor, leaf{}]  # Returns second_anchor
    then:
        void
<#
-->
<!-- 120 -->
```verse
base := class<castable>:
    ID:int

first_anchor := class<final_super>(base):
    Category:string

second_anchor := class<final_super>(first_anchor):
    Subcategory:string

leaf := class(second_anchor):
    Specific:string

# 从 base 查询返回 first_anchor
GetCastableFinalSuperClass[base, leaf{}]  # 返回 first_anchor

# 从 first_anchor 查询返回 second_anchor
GetCastableFinalSuperClass[first_anchor, leaf{}]  # 返回 second_anchor
```
<!-- #>-->

这种分层方法允许层次化分类，不同层级代表不同粒度的类型族。

#### GetCastableFinalSuperClassFromType

基于类型的变体工作方式相同，但接受类型而不是实例：

<!--versetest
component:=class<castable>{}
physics_component := class<final_super>(component){}
rigid_body := class(physics_component){}

# Test both functions work
TestBothVariants()<decides>:void =
    if:
        TypeFamily := GetCastableFinalSuperClassFromType[component, rigid_body]
        InstanceFamily := GetCastableFinalSuperClass[component, rigid_body{}]
    then:
        void
<#
-->
<!-- 123 -->
```verse
# 相同的行为，不同的语法
TypeFamily := GetCastableFinalSuperClassFromType[component, rigid_body]
InstanceFamily := GetCastableFinalSuperClass[component, rigid_body{}]

# 两者返回相同的 castable_subtype
```
<!-- #>-->

这在直接使用类型值而不是实例时很有用。

### castable_concrete_subtype

`castable_concrete_subtype(t)` 类型构造器结合了 `castable_subtype` 和 `concrete_subtype` 的要求，表示同时满足以下条件的类型：
- `t` 的子类型
- 标记了 `<castable>`（启用运行时类型查询）
- 标记了 `<concrete>`（启用实例化）

当需要确保类型参数既可转换又可实例化时，这很有用：

<!--versetest
entity := class{}

component := class<abstract>:
    Owner:entity

physics_component := class<castable><concrete>(component):
    Velocity:float = 0.0

assert:
    # Must be both castable (for type queries) and concrete (for instantiation)
    CreateAndCast(CompType:castable_concrete_subtype(component)):component =
        # Can instantiate because it's concrete
        Instance := CompType{}
        # Can cast because it's castable
        if (Specific := CompType[Instance]):
            Specific
        else:
            Instance
<#
-->
<!-- 138 -->
```verse
entity := class{}

component := class<abstract>:
    Owner:entity

physics_component := class<castable><concrete>(component):
    Velocity:float = 0.0

# 需要同时满足 <castable> 和 <concrete> 的函数
CreateAndCast(CompType:castable_concrete_subtype(component)):component =
    # 可以实例化因为 CompType 是 <concrete>
    Instance := CompType{}
    # 可以转换因为 CompType 是 <castable>
    if (Specific := CompType[Instance]):
        Specific
    else:
        Instance
```
<!-- ERROR:
Line 23: Script Error 3100: vErr:S04: Block comment beginning at "<#" never ends
-->
#>

### classifiable_subset

在 `castable_subtype` 引入的运行时类型查询概念基础上，Verse 提供了 `classifiable_subset`——一种用于维护运行时类型集合的复杂机制。`castable_subtype` 表示单个类型值，而 `classifiable_subset` 表示类型的集合，跟踪系统中存在哪些类，并支持基于类型层次结构的查询。

此特性对于基于组件的架构尤其有价值，其中你需要跟踪实体拥有哪些组件类型、查询特定能力或根据类型兼容性过滤操作。`classifiable_subset` 不是维护单独的布尔标志或类型标签，而是提供了一个类型安全、具有层次结构感知的运行时类型注册表。

三种相关类型协同工作，提供不可变和可变的类型集合：

**`classifiable_subset(t)`** 表示不可变的运行时类型集合，其中 `t` 必须是 `<castable>` 基类型。创建后，集合不能被修改，适用于配置、能力描述或类型集合应保持稳定的任何场景。

**`classifiable_subset_var(t)`** 提供了带有 `Read()` 和 `Write()` 操作的可变变体，支持在程序执行期间动态变化。这对于运行时系统至关重要，其中组件类型随实体演化而添加或移除。

**`classifiable_subset_key(t)`** 表示在向可变集合添加特定实例时用于标识这些实例的键。这些键支持以后移除特定实例，支持已注册类型的生命周期管理。

与普通类不同，`classifiable_subset` 类型不能直接实例化。你必须使用构造函数 `MakeClassifiableSubset()` 和 `MakeClassifiableSubsetVar()`：

<!--versetest
component:=class<castable>{}
physics_component := class<final_super>(component){}
rigid_body := class(physics_component){}
render_component := class<castable>(component){}
-->
<!-- 124 -->
```verse
# 不可变集合，初始为空
EmptySet:classifiable_subset(component) = MakeClassifiableSubset()

# 具有初始实例的不可变集合
InitialSet:classifiable_subset(component) =
    MakeClassifiableSubset(array{physics_component{}, render_component{}})

# 可变集合
DynamicSet:classifiable_subset_var(component) = MakeClassifiableSubsetVar()
```

基类型 `t` 必须是 `<castable>`，确保运行时类型查询是可能的。此限制在编译时强制执行：

<!--versetest
component:=class<computes><castable>{}
f()<reads>:void =
    ComponentSet:classifiable_subset(component) = MakeClassifiableSubset()

<#
-->
<!-- 1215 -->
```verse
ComponentSet:classifiable_subset(component) = MakeClassifiableSubset()

# 无效：不可转换的类型不能使用
regular_class := class:
    Value:int

# 这会是一个错误：
# BadSet:classifiable_subset(regular_class) = MakeClassifiableSubset()
```
<!-- #> -->

你不能子类化这些类型或通过普通构造语法创建实例。这确保所有集合使用正确的内部表示以实现高效的类型查询。

#### 类型层次结构语义

`classifiable_subset` 的关键洞察是它跟踪运行时类型，而不是单个实例。当你向集合添加一个实例时，系统会记录该实例的实际运行时类型。更重要的是，类型查询尊重继承层次结构：

<!--versetest
entity:=class{}
vector3:=class{}
component := class<castable>{}
physics_component := class<castable>(component):
    Velocity:vector3=vector3{}

rigid_body_component := class<castable>(physics_component):
    Mass:float=0.0
-->
<!-- 126 -->
```verse
# 添加一个刚体实例
Set:classifiable_subset(component) =
    MakeClassifiableSubset(array{rigid_body_component{}})

# 查询结果尊重层次结构
Set.Contains[component]             # true - rigid_body 是一个 component
Set.Contains[physics_component]     # true - rigid_body 是一个 physics_component
Set.Contains[rigid_body_component]  # true - 直接存在
```

这种层次结构感知使 `classifiable_subset` 从根本上区别于简单的类型标签集合。`Contains` 操作询问"这个集合中是否包含任何是-T 的类型？"而不是"这个集合中是否恰好包含 T？"。

当你添加不同类型的实例时，每个不同的运行时类型被分别跟踪：

<!--versetest
component := class<castable>{}
physics_component := class<castable>(component){}
rigid_body_component := class<castable>(physics_component){ }
render_component := class<castable>(component){}
audio_component := class<castable>(component){}
-->
<!-- 127 -->
```verse
# 添加多个不同类型
TheSet:classifiable_subset_var(component) = MakeClassifiableSubsetVar()
Key1 := TheSet.Add(physics_component{})
Key2 := TheSet.Add(render_component{})
Key3 := TheSet.Add(audio_component{})

TheSet.Contains[component]          # 成功 - 三者都是 component
TheSet.Contains[physics_component]  # 成功 - physics_component 存在
TheSet.Contains[render_component]   # 成功 - render_component 存在
```

集合会记住添加的每个不同类型。当你通过键移除一个实例时，只有在该类型是最后一个实例时，该特定类型才会被移除：

<!--versetest
component := class<castable>{}
physics_component := class<castable>(component){}
rigid_body_component := class<castable>(physics_component){ }
-->
<!-- 128 -->
```verse
# 添加同一类型的多个实例
TheSet:classifiable_subset_var(component) = MakeClassifiableSubsetVar()
Key1 := TheSet.Add(physics_component{})
Key2 := TheSet.Add(physics_component{})

TheSet.Contains[physics_component]  # 成功

TheSet.Remove[Key1]
TheSet.Contains[physics_component]  # 仍然成功 - Key2 仍在

TheSet.Remove[Key2]
# TheSet.Contains[physics_component]  # 失败 - 最后一个实例已被移除
```

#### 核心操作

`classifiable_subset` 类型提供了几种查询和操作类型集合的操作：

**Contains** 检查集合中是否有任何类型匹配或是指定类型的子类型：

<!--versetest
component := class<castable>{}
physics_component := class<castable>(component){}
render_component := class<castable>(component){}
-->
<!-- 129 -->
```verse
TheSet:classifiable_subset(component) =
    MakeClassifiableSubset(array{physics_component{}})

if (TheSet.Contains[component]):
    # 物理组件存在（并且是一个 component）

if (TheSet.Contains[render_component]):
    # 不存在渲染组件
```

**ContainsAll** 验证数组中的所有类型是否都存在于集合中：

<!--versetest
component := class<castable>{}
physics_component := class<castable>(component){}
render_component := class<castable>(component){}
-->
<!-- 130 -->
```verse
TheSet:classifiable_subset(component) =
    MakeClassifiableSubset(array{physics_component{}})

if (TheSet.ContainsAll[array{physics_component, render_component}]):
    # 物理和渲染组件都存在
```

**ContainsAny** 检查数组中是否至少存在一个类型：

<!--NoCompile-->
<!-- 131 -->
```verse
if (TheSet.ContainsAny[array{physics_component, audio_component}]):
    # 物理或音频组件（或两者）存在
```

**Add**（仅可变集合）添加一个实例并返回一个键以供后续移除：

<!--versetest
component := class<castable>{ Name:string = "Component"}
physics_component := class<castable>(component){}
-->
<!-- 132 -->
```verse
TheSet:classifiable_subset_var(component) = MakeClassifiableSubsetVar()
Key := TheSet.Add(physics_component{})
# 以后可以使用 Key 移除
```

**Remove**（仅可变集合）通过键移除先前添加的实例：

<!--versetest
component := class<castable>{}
physics_component := class<castable>(component){}
-->
<!-- 133 -->
```verse
TheSet:classifiable_subset_var(component) = MakeClassifiableSubsetVar()

Key := TheSet.Add(physics_component{})

if (TheSet.Remove[Key]):
    # 成功移除
else:
    # 键不存在（已被移除或从未添加）
```

**FilterByType** 创建一个新集合，仅包含与指定类型兼容（可赋值给或从其赋值）的类型：

<!--versetest
component := class<castable>{}
physics_component := class<castable>(component){}
render_component := class<castable>(component){}
audio_component := class<castable>(component){}

# Test FilterByType
TestFilterByType()<decides>:void =
    TheSet:classifiable_subset(component) = MakeClassifiableSubset(array{
        physics_component{}, render_component{}, audio_component{}})

    # Filter to physics-related types
    PhysicsSet := TheSet.FilterByType(physics_component)
    if:
        PhysicsSet.Contains[physics_component]  # true
        not PhysicsSet.Contains[render_component]   # false - unrelated sibling
        PhysicsSet.Contains[component]          # true - base type compatible
    then:
        void
<#
-->
<!-- 134 -->
```verse
TheSet:classifiable_subset(component) = MakeClassifiableSubset(array{
    physics_component{}, render_component{}, audio_component{}})

# 过滤为与物理相关的类型
PhysicsSet := TheSet.FilterByType(physics_component)
PhysicsSet.Contains[physics_component]  # true
PhysicsSet.Contains[render_component]   # false - 无关的兄弟类型
PhysicsSet.Contains[component]          # true - 基类型兼容
```
<!-- #>-->

过滤在类型层次结构中同时尊重向上和向下兼容性，保留可赋值给过滤类型或从其赋值的类型。

**Union** 使用 `+` 运算符组合两个集合：

<!--versetest
component := class<castable>{}
physics_component := class<castable>(component){}
render_component := class<castable>(component){}
audio_component := class<castable>(component){}
entity := class{}
-->
<!-- 135 -->
```verse
Set1:classifiable_subset(component) =
    MakeClassifiableSubset(array{physics_component{}})
Set2:classifiable_subset(component) =
    MakeClassifiableSubset(array{render_component{}})

Combined := Set1 + Set2
Combined.Contains[physics_component]  # true
Combined.Contains[render_component]   # true
```

对于可变集合，Read/Write 操作支持复制和更新：

<!--versetest
component := class<castable>{}
physics_component := class<castable>(component){}
render_component := class<castable>(component){}
audio_component := class<castable>(component){}
-->
<!-- 136 -->
```verse
Set1:classifiable_subset_var(component) = MakeClassifiableSubsetVar()
Set1.Add(physics_component{})

Set2:classifiable_subset_var(component) = MakeClassifiableSubsetVar()
Set2.Write(Set1.Read())  # 将 Set1 的内容复制到 Set2
```

#### 设计考虑

有几个重要的约束控制着 `classifiable_subset` 的使用：

基类型必须是 `<castable>` 才能启用运行时类型查询。此要求确保类型检查可以高效执行。

你不能子类化 `classifiable_subset` 类型，也不能通过指定的构造函数以外的其他方式创建实例。此限制维护了正确类型跟踪所需的内部不变量。

来自一个集合的键不能与不同的集合一起使用——它们绑定到添加元素的特定集合实例。

类型参数必须在操作之间保持一致。你不能将 `physics_component` 添加到 `classifiable_subset(render_component)`，即使两者都继承自 `component`：

<!--versetest
component := class<castable>{}
physics_component := class<castable>(component){}
render_component := class<castable>(component){}
audio_component := class<castable>(component){}
-->
<!-- 137 -->
```verse
render_set:classifiable_subset(render_component) = MakeClassifiableSubset()
physics_comp:physics_component = physics_component{}

# 这会是类型错误 - physics_component 不是 render_component
# render_set.Add(physics_comp)
```

可变集合需要谨慎的生命周期管理。键在其实例被移除后变为无效，尝试移除已移除的键会触发失败。

对于大型类型集合，性能特征很重要。虽然 `Contains` 查询由于内部表示而高效，但像 `FilterByType` 这样的操作可能需要检查集合中的每个类型。

在设计使用 `classifiable_subset` 的系统时，考虑不可变和可变集合哪个更适合你的需求。不可变集合提供更强的保证，适用于配置，而可变集合支持组件类型频繁变化的动态系统。

层次结构感知的语义意味着添加派生类型会使基类型的查询成功。这通常是可取的，但需要注意——如果你只想要精确的类型匹配，`classifiable_subset` 可能不是正确的工具。
