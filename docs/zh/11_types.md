# 类型

每个值都有一个类型，理解类型系统是
掌握任何语言的基础。类型不仅仅是标签 -
它们形成了丰富的层次结构，控制着价值如何在你的组织中流动。
程序，允许哪些操作，以及编译器如何推理
关于你的代码。该类型系统将静态验证与
实用的灵活性，在编译时捕获错误，同时仍然
允许复杂的代码重用和抽象模式。

位于该层次结构的顶部的是 `any`，它是来自
所有其他类型都会下降。底部是`false`，空的
根本不包含任何值的类型（无人居住类型）。之间
这些极端存在着精心设计的类型网格，每种类型都有
自身的能力和限制。

<a id="understanding-subtyping"></a>
## 理解子类型

子类型化是类型层次结构的基础。当我们这么说的时候
类型 A 是类型 B 的子类型，我们的意思是类型 A 的每个值都可以
在需要 B 类型值的任何地方使用。这种关系
在类型之间创建从最具体到最具体的自然排序
最一般。

考虑`rational`和`int`之间的关系。每个
整数是有理数，但并非所有有理数都是整数。
因此，`int` 是 `rational` 的子类型。这意味着您可以
将 `int` 传递给任何需要 `rational` 的函数，但反之则不然：

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

GetRat(MyInt)  # OK——int是有理数的子类型
GetInt(MyRat)  # 编译错误-rational不是int的子类型
```
<!-- #> -->

子类型关系扩展到复杂的复合类型
方式。数组和元组遵循协变子类型规则
元素。这意味着 `[]int` 是 `[]rational` 的子类型。
类似地，`tuple(int, int)` 是 `tuple(rational,
理性）`。这种协方差允许更具体类型的集合
用于需要更通用类型的集合的地方。

映射表现出更复杂的子类型行为。映射类型 `[K1]V1` 是
当 `K2` 是 `K1` 的子类型时，`[K2]V2` 的子类型（逆变）
键），`V1` 是 `V2` 的子类型（值的协变）。的
键的逆变乍一看似乎违反直觉，但它
确保类型安全：如果您可以使用更通用的方式查找值
键类型，您还必须能够处理更具体的键类型。

类和接口通过以下方式引入名义子类型
继承。当一个类继承另一个类或实现一个类时
接口，它显式声明了子类型关系：

<!--versetest 02 -->
<!-- 02 -->
```verse
vehicle := class:
    Speed:float = 0.0

car := class(vehicle):  # 汽车是车辆的子类型
    NumDoors:int = 4

sports_car := class(car):  # sports_car 是汽车（和车辆）的子类型
    Turbo:logic = true
```
这种继承层次结构意味着可以使用 `sports_car`
任何需要 `car` 或 `vehicle` 的地方，但反之则不然。的
子类型继承其超类型的所有字段和方法，而
可能会添加新的或覆盖现有的。

## 数字和字符串转换

所有类型转换都必须是显式的，这种设计选择消除了
整个类别的错误，同时实现程序员的意图
清楚。数字类型之间的转换说明了这一原理
清楚地。要将整数转换为浮点数，请乘以 1.0：

<!--versetest-->
<!-- 03 -->
```verse
MyI:int   = 42
MyF:float = MyI * 1.0  # 显式转换为 float
```
!!!注释 
    禁止隐式转换的最主要原因是
	当函数有新的重载时，它们可能会导致代码中断
	被添加。想象一下对函数 `f` 的调用，该函数采用这样的浮点数
	如 `f(1)`，如果整数参数被隐式转换为 
	浮动，并且在未来的某些库版本中，重载 `f(:int)` 
	添加后，该调用将静默调用该新函数
	并可能改变计算结果。

从浮点到整数的反向转换需要选择一个
舍入策略：

<!--versetest-->
<!-- 04 -->
```verse
MyF:float = 3.7
Opt1:int = Floor[MyF]  # 结果 3
Opt2:int = Ceil[MyF]   # 结果 4
Opt3:int = Round[MyF]  # 结果为 4（四舍五入到最接近的值）
```
这些转换函数是可能失败的 - 它们具有 `<decides>`
如果传递非有限值（例如 `NaN` 或
`Inf`。显式失败迫使您处理边缘情况：

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
字符串转换遵循类似的原则。 `ToString()`
函数将各种类型转换为其字符串表示形式，而
字符串插值为嵌入值提供了方便的语法
在字符串中：

<!--versetest-->
<!-- 06 -->
```verse
Score:int  = 1500
Msg:string = "Your score: {Score}"  # 隐式 ToString() 调用
```
## 类型 `any`

<!-- TODO add a link to the builtin types -->

类型 `any` 位于类型层次结构的顶部，它是通用的
可以保存任何类型值的超类型。 Verse 中的每种类型都是
`any` 的子类型，使其成为最宽松的类型。  它充当
当您真正需要使用未知或未知的值时，可以使用逃生舱口
不同类型。

一旦一个值被输入为 `any`，你就有效地告诉了编译器
“我不知道这是什么”，编译器通过阻止来响应
大多数操作。这是设计使然——在不知道实际类型的情况下，
编译器无法验证操作是否安全。

您可以使用函数调用将任何值显式强制为 `any`
语法，`any(42)`。 

当值的类型发生变化时，Verse 会自动将值强制转换为 `any`
否则不兼容。了解这些规则对工作有帮助
具有异构数据。

混合类型数组和映射自动强制到最具体的共享
类型，如果没有找到公共类型，则数组强制为 `any`：

<!--versetest
SomeFunction():void={}
-->
<!-- 09 -->
```verse
MixedArray := array{42, "hello", true, 3.14} # []可比
MixedMap := map{0=>"zero", 1=>1, 2=>2.0} # [int]可比较
ConfigMap := map{"count"=>42, "process"=>SomeFunction, "name"=>"Player"} # [字符串]任意
```
具有不相交分支类型的条件表达式生成 `any`：

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
具有不相交类型的逻辑 OR 强制为 `any`：

<!--versetest-->
<!-- 12 -->
```verse
# 返回整数或字符串
OneOf(Flag:logic, I:int, S:string):any =
    (if (Flag?) then {option{I}} else {1=2}) or S
```
`any` 类型具有反映其作为通用角色的限制
容器：

- 不能将相等运算符与 `any` 一起使用
- 由于`any`不具有可比性，因此不能用作映射键类型
- 因为`any`不是可浇注的，所以它是粘性类型。

### 泛型函数和类型保留

具有 `where t:type` 约束的通用函数的行为与接受 `any` 的函数有根本不同。理解这种差异对于编写类型安全代码至关重要。

当您将值传递给参数类型为 `any` 的函数时，类型信息将丢失：

<!--versetest-->
<!-- 53 -->
```verse
AcceptAny(X:any):any = X

MyMap:[int]string = map{1 => "one"}
Result := AcceptAny(MyMap)  # 结果类型为任意 - 类型信息丢失
```
相反，泛型函数保留精确类型：

<!--versetest-->
<!-- 54 -->
```verse
Identity(X:t where t:type):t = X

MyMap:[int]string = map{1 => "one"}
Result := Identity(MyMap)  # 结果的类型为 [int]string - 保留类型
MyMap = Result  # 成功 - 相同类型
```
这种保留扩展到所有容器类型，包括数组、映射、元组和结构。泛型类型参数捕获完整类型，包括：

- 映射键和值类型
- 数组元素类型
- 元组组件类型
- 结构字段类型

**实际影响：**

通过泛型函数传递的容器类型完全保持其结构：

<!--versetest-->
<!-- 55 -->
```verse
Identity(X:t where t:type):t = X

# 保留所有密钥类型
IntMap:[int]int = map{1 => 2, 3 => 4}
IntMap = Identity(IntMap)  # 同类型

FloatMap:[float]string = map{1.0 => "one", 2.5 => "two"}
FloatMap = Identity(FloatMap)  # 同类型

TupleMap:[tuple(int, string)]int = map{(1, "a") => 100}
TupleMap = Identity(TupleMap)  # 同类型

# 迭代和相等按预期工作
for (Key->Value : IntMap):
    Identity(IntMap)[Key] = Value  # 所有查找均成功
```
当您需要编写与容器一起使用的可重用代码并同时保持类型安全时，这使得泛型函数成为首选方法。

<a id="class-and-interface-casting"></a>
## 类和接口转换

Verse 为类和类提供了两种不同的转换机制
接口：运行时类型检查的易错转换，并且绝对可靠
编译时验证转换的强制转换。了解何时以及
如何使用每个对于处理继承层次结构至关重要
和多态代码。

易出错的转换使用方括号语法 `TargetType[value]` 来
执行运行时类型检查。这些转换成功并返回
强制转换值 (`TargetType`)，如果该值不是
有效的目标类型或子类型：

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

# 使用易出错的强制转换进行运行时类型检查
ProcessComponent(Comp:component):void =
    if (PhysicsComp := physics_component[Comp]):
        # 成功投射 -PhysicsComp 为物理组件
        Print("Physics velocity: {PhysicsComp.Velocity}")
    else if (RenderComp := render_component[Comp]):
        # 不同类型 - RenderComp 是 render_component
        Print("Render material: {RenderComp.Material}")
    else:
        # 两种类型都不匹配
        Print("Unknown component type")
```
<!-- #> -->

如果运行时类型不存在，则转换表达式的计算结果为 `false`
match，允许您直接在条件中使用它。可选的
绑定模式 `(Variable := Expression)` 都执行强制转换和
成功时将结果绑定到变量。

对于标记为 `<unique>` 的类，易出错的类型转换会保留身份 -
成功的转换返回相同的实例，而不是副本：

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

# 转换为基本类型
if (E := entity[P]):
    E = P  # 真实 - 实例相同
```
<!-- #> -->

易错的转换**仅适用于类和接口类型**。你
不能动态转换为基本类型、结构、数组，
或其他值类型：

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

# 错误：无法从基元进行转换
Comp := component[42]          # int 到类 - 允许
Comp := component[3.14]        # 浮动到班级 - 不允许
Comp := component["text"]      # 字符串到类 - 不允许
Comp := component[array{1,2}]  # 数组到类 - 不允许

# 错误：无法转换为非类类型
Value := int[component{}]      # 类为 int - 允许
Value := logic[component{}]    # 类到逻辑 - 不允许
Value := (?int)[component{}]   # 类别到选项 - 不允许
```
<!-- #>-->

存在限制是因为易错的强制转换依赖于运行时类型
只有类和接口维护的信息。值类型
像整数和结构没有运行时类型标签。

*可靠* 转换使用括号语法 `TargetType(value)`
编译器可以验证的转换始终会成功。这些
强制转换要求源类型是该类型的编译时子类型
目标类型：

<!--versetest-->
<!-- 20 -->
```verse
component := class<castable>:
    Name:string = "Component"

physics_component := class<castable>(component):
    Velocity:float = 0.0

# 上传：永远安全，永远成功
Base:physics_component = physics_component{Velocity := 10.0}

BaseComp:component = component(Base) # 表达期间向上转换
# 或
AlsoBaseComp:component = Base # 分配期间向上转型
```
任何类型都可以正确地转换为 `void`，这会丢弃该值：

<!--versetest
component:=class{}
-->
<!-- 21 -->
```verse
void(42)           # 丢弃一个整数
void("result")     # 丢弃字符串
void(component{})  # 丢弃一个对象
```
当您调用函数以获得其副作用时，就会隐式发生这种情况
并想忽略它的返回值。

<a id="dynamic-type-based-casting"></a>
### 基于动态类型的强制转换

Verse 中的类型是一流的值，这意味着您可以存储类型
变量并动态使用它们进行转换。这使得
运行时多态性的强大模式：

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
        true  # 组件与预期类型匹配
    else:
        false

# 与不同类型一起使用
P := physics_component{}
Test(P, physics_component)  # 真实
Test(P, render_component)   # 假的
```
<!-- #> -->

当要检查的类型不是
直到运行时才知道：

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
# 根据配置选择类型
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
        # 所需类型的过程组件
        ProcessSpecific(Specific)
```
这将编译时类型安全性与运行时灵活性联系起来，
允许根据程序状态做出类型决策，同时
保持类型的正确性。

## `where` 子句

Where 子句是约束类型参数的机制
通用代码。它们出现在类型参数之后并指定
类型必须满足的要求才能成为有效的参数。这个
创建了一个强大的系统来编写通用代码
灵活且类型安全。

<!--versetest-->
<!-- 24 -->
```verse
# 简单子类型约束
Process(Value:t where t:subtype(comparable)):void =
    if (Value = Value):  # 我们知道它支持平等
        Print("Value equals itself")
```
尚不支持在多个约束中使用相同类型，当
实现后，它将允许编写如下代码：

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
# 同一类型的多个约束
F(In:t where t:subtype(comparable), t:subtype(printable)):t = # 不支持
    Print("Processing: {In}")
    In
```
<!-- #> -->

当使用多个类型参数时，Where 子句变得更加强大：

<!--versetest-->
<!-- 26 -->
```verse
# 不同参数的独立约束
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
where 子句支持复杂的通用编程模式：

<!--versetest-->
<!-- 28 -->
```verse
MapFunction(F:type{_(:a):b}, Container:[]a where a:type, b:type):[]b =
    for (Element : Container):
        F(Element)
```
## 细化类型

虽然 `where` 子句限制泛型代码中的类型参数，
**细化类型**使用 `where` 来约束类型可以的*值*
坚持。这将创建只接受满足以下条件的值的子类型
特定条件，启用特定于域的约束
类型系统。

一个自然的问题是：当你可以时，为什么会在超出范围的值上失败？
只是夹住？答案是钳位默默传播错误
值，这对于某些域来说是可以接受的（UI 不透明度），但是
对其他人来说是危险的。在精确值很重要的算法中——位
操作、散列、Unicode 代码点操作、坐标
系统数学——默默地限制超出范围的值产生
错误的结果极难追踪。细化
类型使约束显式并强制调用者处理
违规行为，从源头捕获错误而不是放任它们发生
传播。

实际上，键入 `positive_int` 或 `zero_to_one_float` 等别名
使细化类型可以方便地在代码库中重用，而无需
每次重复约束表达式。

细化类型使用值谓词定义受约束的子类型：

<!--versetest
percent := type{_X:float where 0.0 <= _X, _X <= 1.0} 
-->
<!-- 29 -->
```verse
# 百分比：在 0.0 和 1.0 之间浮动
# percent := type{_X:float where 0.0 <= _X, _X <= 1.0}

# 有效作业
Opacity:percent = 0.5
Alpha:percent = 1.0

# 无效：超出范围（运行时检查失败）
# BadPercent:percent = 1.5 # 分配失败
```
**语法结构：**

<!--NoCompile-->
<!-- 30 -->
```verse
TypeName := type{_Variable:BaseType where Constraint1, Constraint2, ...}
```
- `_Variable` 是受约束值的占位符
- `BaseType` 是 `int` 或 `float`
- 约束是使用 `<=`、`<`、`>=` 或 `>` 的比较表达式

整数细化将 int 值限制在特定范围内：

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
# 年龄在0到120之间
age := type{_X:int where 0 <= _X, _X <= 120}

ValidAge:age = 25
# InvalidAge:age = 150 # 约束失败

# 正整数
positive_int := type{_X:int where _X > 0}

Count:positive_int = 42
# Zero:positive_int = 0 # 失败：非正数

# 单边界范围
small_int := type{_X:int where _X < 100}
```
<!-- #> -->

浮点细化使用 IEEE 754 语义处理连续范围：

<!--versetest
normalized := type{_X:float where 0.0 <= _X, _X <= 1.0}
positive := type{_X:float where _X > 0.0}
celsius := type{_X:float where _X >= -273.15}
<#
-->
<!-- 32 -->
```verse
# 单位间隔[0.0,1.0]
normalized := type{_X:float where 0.0 <= _X, _X <= 1.0}

# 正浮点数
positive := type{_X:float where _X > 0.0}

# 绝对零以上的摄氏度温度
celsius := type{_X:float where _X >= -273.15}
```
<!-- #> -->

有限浮点数（不包括无穷大）：

<!--versetest
finite := type{_X:float where -Inf < _X, _X < Inf}
assert:
	MaxFinite:finite = 1.7976931348623157e+308
	MinFinite:finite = -1.7976931348623157e+308
<#
-->
<!-- 33 -->
```verse
# 仅有人力资源（无±Inf）
finite := type{_X:float where -Inf < _X, _X < Inf}

# 最大和最小限度 IEEE 754 双精度
MaxFinite:finite = 1.7976931348623157e+308
MinFinite:finite = -1.7976931348623157e+308

# 无效：排除无穷大
# Infinite:finite = Inf # 约束失败
```
<!-- #> -->

### IEEE 754 边缘情况

**负零和正零：**

IEEE 754 区分 `+0.0` 和 `-0.0`。在Verse中，零就是零，
没有正负之分。

<!--versetest-->
当任何表达式的计算结果为零时，该符号将被丢弃：
<!-- 34 -->
```verse
# 整数零（类型{0}）
Value1 := -0
Value2 := +0

Value1 = Value2 # 成功
-0 = +0         # 成功

# 浮点零（类型{0.0}）
Value3 := -0.0
Value4 := +0.0

Value3 = Value4 # 成功
-0.0 = +0.0     # 成功
```
**浮点精度：**

约束遵循精确的 IEEE 754 表示：

<!--versetest
small_float := type{_X:float where _X < 0.1}
assert:
    Tiny:small_float = 0.09999999999999999167332731531132594682276248931884765625
<#
-->
<!-- 36 -->
```verse
# 值严格小于 0.1
small_float := type{_X:float where _X < 0.1}

# 有效：0.1 之前的最大浮点数
Tiny:small_float = 0.09999999999999999167332731531132594682276248931884765625

# 无效：0.1的实际表示略高于0.1
# NotSmall：small_float = 0.1000000000000000055511151231257827021181583404541015625
```
<!-- #> -->

十进制的`0.1`不能用二进制精确表示
浮点数，因此实际存储的值略高于
数学0.1。

### 约束表达式限制

细化类型约束对什么有严格的限制
允许的表达式：

**仅文字值：** 约束必须使用文字数字，而不是
变量或表达式：

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
# 有效：字面量浮点数
bounded := type{_X:float where _X < 100.0}

# 无效：不能使用变量
Limit:float = 100.0
bad_type := type{_X:float where _X < Limit}  # 错误

# 无效：不能使用函数调用
GetMax():float = 100.0
bad_type := type{_X:float where _X < GetMax()}  # 错误

# 无效：不能使用限定名称
Config := module{Max:float = 100.0}
bad_type := type{_X:float where _X < (Config:)Max}  # 错误
```
<!-- #> -->

这确保了约束在编译时是静态已知的。

**浮点类型所需的浮点文字：** 当约束浮点时，
边界必须是浮点文字（带小数点）：

<!--versetest
good_float := type{_X:float where _X <= 142.0}

assert:
     1
<#
-->
<!-- 38 -->
```verse
# 无效：浮点约束中的整数文字
# bad_float := type{_X:float where _X <= 142}  # ERROR 3502

# 有效：浮点文字
good_float := type{_X:float where _X <= 142.0}
```
<!-- #> -->

**不允许 NaN：** 不是一个数字不能出现在
限制：

<!--versetest-->
<!-- 39 -->
```verse
# 无效：约束中为 NaN
# nan_type := type{_X:float where _X <= NaN}      # ERROR 3502
# nan_type := type{_X:float where NaN <= _X}      # ERROR 3502
# nan_type := type{_X:float where 0.0/0.0 <= _X}  # ERROR 3502
```
由于 `NaN` 比较始终为 false，因此此类约束毫无意义。

**允许的文字形式：**

- 浮点文字：`1.0`、`3.14`、`-2.5`、`1.7976931348623157e+308`
- 整数文字：`0`、`42`、`-100`（用于 int 细化）
- 特殊浮点值：`Inf`、`-Inf`

<a id="fallible-casts"></a>
### 可失败强制转换

细化类型在分配时和通过易错的强制类型转换进行检查：

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
Valid:percent = 0.5  # 好的

# 运行时检查易出错的演员表
UserInput:float = GetInputFromUser()
if (Value := percent[UserInput]):
    # UserInput 位于 [0.0, 1.0] 范围内
    ProcessPercent(Value)
else:
    # 超出范围
    ShowError()
```
<!-- #> -->

如果转换 `percent[UserInput]` 成功，则返回 `percent`
值满足约束，否则失败。

### 示例

细化类型用作参数和返回类型：

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

# 无法通过无穷大
# Half(Inf)  # ERROR 3509: Inf not in finite
```
<!-- #> -->

**强制与否定：**

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

# 否定保留约束兼容性
NegValue:negative_percent = -MakePercent()  # -0.5有效

# 多重否定
NegValue2:negative_percent = ---0.7  # 三重否定=-0.7
```
<!-- #> -->

### 重载限制

重叠的细化类型不能用于函数
重载——它们是不明确的：

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

# 错误 3532：无法区分 - 百分比 ⊂ not_infinity
# F(X:percent):float = 0.0
# F(X:not_infinity):float = X

# 调用 F(0.5) 会产生歧义 - 哪个重载？
```
<!-- #>-->

但是，**不相交**细化类型可能会超载：
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

# 有效：范围不重叠（两者均排除零）
F(X:positive):float = X
F(X:negative):float = X + 1.0

F(1.0)   # 返回 1.0（正过载）
F(-1.0)  # 返回 0.0（负过载）
# F(0.0)  # Would fail - neither overload matches
```
<!-- #> -->

## 可比性和平等性

`comparable` 类型表示类型的特殊子集
支持平等比较。并非所有类型都可以进行比较
平等 - 这是一个故意的设计选择，可以防止
无意义的比较并确保平等具有明确的定义
语义。

如果一个类型的值可以进行有意义的测试，则该类型是可比较的
平等。基本标量类型都是可比较的：`int`、`float`、
`rational`、`logic`、`char` 和 `char32`。化合物类型有
如果它们的所有组件都具有可比性，则具有可比性。这意味着数组
整数的元组是可比较的，浮点数和字符串的元组是
可比较，并且具有可比较键和值的映射也是可比较的。

相等运算符 `=` 和 `<>` 是根据
类似类型：

<!--NoCompile-->
<!-- 45 -->
```verse
operator'='(X:t, Y:t where t:subtype(comparable))<decides>:t
operator'<>'(X:t, Y:t where t:subtype(comparable))<decides>:t
```
签名要求两个操作数都是可比较操作数的子类型
返回类型是它们类型的最小上限。

<!--versetest
assert:
    0 = 0
    0.0 = 0.0

<#
-->
<!-- 46 -->
```verse
0 = 0        # 成功 - 两者都是 int
0.0 = 0.0    # 成功 - 两者都是浮动的
0 = 0.0      # 失败 - 没有从 int 到 float 的隐式转换
```
<!-- #> -->

以下示例重点介绍了如何计算 `=` 的返回类型：

<!--46b -->
```verse
I:int=1
R:rational=1/3
X:rational= (I=R)  # 编译并在运行时失败

I:int=1
S:string="hi"
Y:comparable= (I=S)  # 编译并在运行时失败
```
对于变量 `X`，其类型可以是 `rational` 或
`comparable`。对于变量`Y`，`int`和`int`之间唯一的公共类型
`string` 是 `comparable`。


类需要特殊处理以实现可比性。默认情况下，类
实例不具有可比性，因为没有通用的方法
定义用户定义类型的相等性。不过，你可以上一堂课
使用 `unique` 说明符进行比较：

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

Player1 = Player2  # 失败 - 不同的实例
Player1 = Player3  # 成功 - 同一实例
```
<!--versetest
#>
-->

使用 `unique` 说明符，实例仅等于其自身
（身份平等），不与具有相同字段值的其他实例
（结构平等）。这提供了清晰的、可预测的语义
为了阶级平等。

### 将 `comparable` 用作泛型约束

`comparable` 类型通常用作泛型中的约束
确保相等测试等操作可用的函数：

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

# 适用于任何类似类型
Position := Find[array{"apple", "banana", "cherry"}, "banana"]  # 成功并返回1
```
<!-- #>-->

### 数组元组比较

Verse 相等系统的一个显着特征是数组和元组
可比较的元素可以相互比较：

<!--versetest-->
<!-- 49 -->
```verse
# 数组可以等于元组
array{1, 2, 3} = (1, 2, 3)       # 成功
(4, 5, 6) = array{4, 5, 6}       # 成功 - 双向

# 不平等也起作用
array{1, 2, 3} <> (1, 2, 4)      # 成功——不同的价值观
```
这种比较在结构上有效 - 序列必须具有相同的
长度和相应的元素必须相等。此功能允许
函数期望数组接受元组，从而提高灵活性。

### 重载可比性的区别

您不能创建其中一个参数是特定可比较类型而另一个参数是通用 `comparable` 类型的重载，因为这会产生歧义：

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
# 不允许 - 不明确的重载
F(X:int):void = {}
F(X:comparable):void = {}  # 错误：int 已经可以比较

# 也不允许使用独特的类别
unique_class := class<unique>{}
G(X:unique_class):void = {}
G(X:comparable):void = {}  # 错误：unique_class 具有可比性
```
<!-- #> -->

但是，您可以使用不可比较的类型进行重载：

<!--versetest-->
<!-- 51 -->
```verse
# 这是允许的
regular_class := class{}  # 没有可比性
H(X:regular_class):void = {}
H(X:comparable):void = {}  # 好的：没有歧义
```
### 动态可比值

当使用异构集合时，您可能需要装箱
显式地将可比值转换为 `comparable` 类型。这些盒装的
值保持其相等语义：

<!--versetest-->
<!-- 52 -->
```verse
AsComparable(X:comparable):comparable = X

# 装箱值与装箱值和未装箱值进行正确比较
array{AsComparable(1)} = array{1}              # 成功
array{AsComparable(1)} = array{AsComparable(1)} # 成功
array{AsComparable(1)} <> array{2}             # 成功

# 直接向上转换：
comparable(15) = comparable(15)     # 成功
comparable("Hello") = "Hello"       # 成功
```
这允许您创建混合不同可比较的集合
类型，将它们全部装箱到 `comparable`。

### 映射键与可比较性

映射键必须是可比较的类型。可以使用大多数可比较的类型
作为映射键，包括：

- 所有数字类型：`int`、`float`、`rational`
- 字符类型：`char`、`char32`
- 文本：`string`
- 枚举
- `<unique>` 类
- 类似类型的选项：`?t`，其中 `t` 是类似的
- 可比较类型的数组：`[]t`，其中 `t` 可比较
- 可比较类型的元组
- 具有可比键和值的映射：`[k]v`
- 具有可比字段的结构

请注意，虽然 `float` 可以用作映射键，但浮点
特殊值具有特定的相等语义（参见[Map
文档](02_primitives.md#floats) 了解详细信息
`NaN` 和零处理）。

目前还没有办法使常规课程与
编写自定义比较方法。仅 `<unique>` 说明符
通过身份平等实现阶级可比性。

## 类型层次结构

类型系统形成一个格子而不是一个简单的树。这意味着
类型可以有多个超类型，但多重继承是
目前仅限于接口。了解这些关系
帮助您设计灵活、可重用的代码。

### 理解 `void`

与擦除类型信息的 `any` 不同，`void` 充当
“discard”类型表示值的特定类型并不重要。

返回类型为 `void` 的函数可以返回任意值，然后
被类型系统丢弃：

<!--versetest
WriteToFile(:string)<transacts>:void = {}
-->
<!-- 77 -->
```verse
LogEvent(Message:string)<transacts>:void =
    WriteToFile(Message)
    42                   # 返回 int，但类型为 void

F():void = 1             # 有效 - 返回 int，类型为 void
F()                      # 结果无效
```
尽管类型为 `void`，这些函数仍然产生它们的
计算值——这些值根本无法通过类型访问
系统。这确保了即使在
返回值被丢弃：

<!--versetest-->
<!-- 78 -->
```verse
MakePair(X:string, Y:string):void = (X, Y)

# 即使返回类型为 void，函数也计算该对
MakePair("hello", "world")  # 仍然创建（“你好”，“世界”）
```
具有 `void` 参数的函数接受任何参数类型：

<!--versetest-->
<!-- 79 -->
```verse
Discard(X:void):int = 42

Discard(0)               # 整数 → 无效
Discard(1.5)             # 浮动→无效
Discard("test")          # 字符串 → 无效
```
类字段可以键入为 `void`，接受任何初始化
值：

<!--versetest-->
<!-- 80 -->
```verse
config := class:
    Setting:void = array{1, 2}  # 默认使用数组
```
在函数类型中，`void` 参与方差：

<!--versetest-->
<!-- 81 -->
```verse
IntIdentity(X:int):int = X

# 逆变返回：返回位置的超类型
F:int->void = IntIdentity  # int->int → int->void ✓
# void 是 int 的超类型，所以这很有效

AcceptVoid(X:void):int = 19

# 逆变参数：参数位置的超类型
G:int->int = AcceptVoid    # void->int → int->int ✓
# 可以在需要接受 int 的函数的地方使用接受 void 的函数
```
但是，参数位置中的 `void` 不允许转换
其他方式：

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
# F:void->int = IntFunction # 错误
# 无法将函数类型中的 int 参数转换为 void 参数
```
<!-- #>-->

**void vs false**：`false` 类型是空/底部类型
（无人居住类型）没有值。它与 `void` 相反：

- **`void`**：通用超类型 - 所有类型都是 void 的子类型，包含所有值
- **`false`**：底部类型 - 所有类型的子类型，包含零值

通用超类型（`any`、`void`）和底层类型之间
(`false`)，类型形成自然分组。数字类型（`int`，
`float`、`rational`) 共享公共算术运算但不形成
单一的等级制度——他们是兄弟姐妹而不是祖先
后代。每个容器类型（数组、映射、元组、选项）
根据其元素类型有自己的子类型规则。

了解方差对于使用泛型至关重要
容器。数组和选项的元素类型是协变的 -
如果 A 是 B 的子类型，则 `[]A` 是 `[]B` 的子类型，而 `?A` 是
`?B` 的亚型。这允许自然代码，例如：


<!--versetest
RationalPrinter(X:rational):string=""
-->
<!-- 89 -->
```verse
ProcessNumbers(Nums:[]rational):void =
    for (N : Nums):
        Print("{RationalPrinter(N)}")

IntArray:[]int = array{1, 2, 3}
ProcessNumbers(IntArray)  # 由于协方差而起作用
```
函数表现出更复杂的方差。它们是逆变的
它们的参数类型和返回类型的协变。一个功能
如果 T2 是 T1 的子类型，则类型 `(T1)->R1` 是 `(T2)->R2` 的子类型
（逆变），R1 是 R2（协方差）的子类型。这确保了
该函数子类型保留了类型安全：

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
# 它接受更通用的输入（any vs int） - 显示屏
# 并返回更具体的输出（int vs any）-协考古

# 演示：可以在需要 type2 的地方使用匹配 type1 的函数
ConcreteFunc(Input:any):int = 42

UseFunction(F:function_type2, Value:int):void =
    Result:any = F(Value)

UseFunction(ConcreteFunc, 5)  # 工作原理： function_type1 <: function_type2
```
<!-- #>-->

## 类型别名

类型别名允许您为类型创建替代名称，从而使
复杂类型签名更具可读性和可维护性。他们是
对于函数类型、参数类型和
常用的类型组合。

类型别名是在模块范围内使用简单的赋值语法创建的：

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
# 在模块范围内
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

类型别名仅在编译时有效 - 它们不会产生运行时开销
纯粹是为了程序员的方便和代码的清晰度。

**类型别名是替代名称，而不是新类型。**它们不
在某些语言中创建不同的类型，例如 `newtype`。的价值观
别名和原始类型是完全可以互换的：

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

# 这些都有效 - 别名只是名称
ProcessPlayer(PID)      # 好的
ProcessPlayer(GID)      # 好的 - game_id 也是 int
ProcessPlayer(42)       # 好的 - int 文字也可以工作
ProcessGame(PID)        # 好的 -player_id 也是 int
```
类型别名可以具有控制其跨模块可见性的访问说明符：

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
# 公共别名 - 可从其他模块访问
PublicAlias<public> := int

# 内部别名 - 只能在定义模块内访问
InternalAlias<internal> := string

# 受保护/私有也有效
ProtectedAlias<protected> := float  # 仅在类和接口中
```
<!-- #> -->

**类型别名不能比它们别名的类型更公开：**

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
private_class := class{}      # 无说明符 = 内部范围

# 无效：内部类型的公共别名
# PublicToPrivate<public> := private_class

# 有效：可见度相同或较低
InternalToInternal<internal> := private_class
InternalAlias := private_class  # 默认为内部
```
<!-- #> -->

### 要求

- **类型别名只能在模块范围内定义。**它们不能
在类、函数或任何嵌套范围内定义。
此限制确保类型别名具有一致的可见性和
防止范围相关的类型解释。

- 类型别名必须在使用之前定义。前进
不允许引用。

- 类型别名不是一流的值，不能这样使用。

## 元类型

Verse 提供了高级类型构造函数，允许您使用
类型作为值，为运行时多态性提供强大的模式
和通用实例化。这些元类型—`subtype`，
`concrete_subtype` 和 `castable_subtype`—弥补了两者之间的差距
编译时类型安全性和运行时灵活性。

<a id="subtype"></a>
### 子类型

`subtype(T)` 类型构造函数表示运行时类型值
是 `T` 的子类型。与 `concrete_subtype` 和 `castable_subtype` 不同，
专门用于类和接口，`subtype(T)` 有效
Verse 中的**任何类型**，包括基元、枚举、集合、
和函数类型。

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

# 使用子类型作为字段类型的示例
var AnimalType:subtype(animal)  # 可容纳动物、狗或任何动物亚型

# 分配班级类型
F0():void = set AnimalType = animal
F1():void = set AnimalType = dog  # 狗是动物的亚型

# 接受作为参数
F3(ClassArg:subtype(animal)):void = set AnimalType = ClassArg
```
<!-- #>-->

`subtype(T)` 的关键功能是在运行时保存类型值
同时通过子类型关系维护类型安全。

与其他元类型不同，`subtype(T)` 接受任何类型作为其参数：

<!--versetest
my_enum := enum { A, B, C }
my_class := class {}
my_interface := interface {}
-->
<!-- 101 -->
```verse
# 基元
IntType:subtype(int) = int
LogicType:subtype(logic) = logic
FloatType:subtype(float) = float

# 枚举
EnumType:subtype(my_enum) = my_enum

# 类和接口
ClassType:subtype(my_class) = my_class
InterfaceType:subtype(my_interface) = my_interface

# 注意： subtype() 中的集合类型和函数类型目前存在问题：
# ArrayType:subtype([]int) = []int # 错误：无法定义
# OptionType:subtype(?string) = ?string # 错误：无法定义
# FuncType:subtype(type{_():void}) = type{_():void} # 错误：无法定义
```
这种通用性使得 `subtype(T)` 成为最灵活的元类型，适合任何需要存储或传递类型值的场景。

**子类型关系：**

`subtype` 构造函数保留子类型关系：
`subtype(T) <: subtype(U)` 当且仅当 `T <: U`。这意味着您可以
将更具体的子类型分配给不太具体的子类型：

<!--versetest-->
<!-- 102 -->
```verse
super_class := class{}
sub_class := class(super_class) {}

# 协方差：子类<：超类
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

# 通过接口层次结构实现协变
SpecificType:subtype(sub_interface) = class_impl
GeneralType:subtype(super_interface) = SpecificType  # 有效
```
**与接口一起使用：**

当使用接口时，`subtype(T)` 可以保存任何实现该接口的类：

<!--versetest-->
<!-- 104 -->
```verse
printable := interface:
    PrintIt():void

document := class(printable):
    PrintIt<override>():void = {}

# 可以容纳任何实现可打印的类型
DocumentType:subtype(printable) = document
```
**与 `type` 的关系：**

`subtype(T)` 和 `castable_subtype(T)` 都是 `type` 的子类型，这意味着它们可以在需要 `type` 的地方使用：

<!--versetest-->
<!-- 105 -->
```verse
c := class:
    f(C:subtype(c)):type = return(C)  # 有效：子类型(c) <：类型

t := interface {}
g(x:subtype(t)):type = x  # 有效：子类型(t) <：类型
```
**限制：**

虽然 `subtype(T)` 很灵活，但它有重要的限制：

1. **不能用作值：** `subtype(T)` 是类型构造函数，而不是
   值。您不能使用 `subtype(T)` 本身作为值。
2. **恰好一个参数：** `subtype` 需要恰好一个类型参数。
3. **不能与属性一起使用：** `subtype` 不能与
   从 `attribute` 继承的类。

<a id="concrete_subtype"></a>
### 具体子类型

`concrete_subtype(t)` 类型构造函数创建一个类型
表示 `t` 的具体（可实例化）子类。具体类
是一个可以直接实例化的——它有 `<concrete>`
说明符并为所有字段提供默认值：

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

# 存储类型并可以实例化它的类
spawner := class:
    EntityType:concrete_subtype(entity)

    Spawn():entity =
        # 使用存储的类型实例化
        EntityType{}

# 使用它
# NewEntity := spawner{EntityType := player}.Spawn()
```
`concrete_subtype`的关键特性是它确保存储的类型可以被实例化。如果没有这个约束，您就无法安全地调用 `EntityType{}`，因为抽象类无法实例化。

#### 要求

仅当类型是类或
接口类型。此外，分配的实际类型值必须是
具体类 - 标有 `<concrete>` 且所有字段都带有
默认值：

<!--versetest-->
<!-- 111 -->
```verse
# 有效：具有所有默认值的具体类
config := class<concrete>:
    MaxPlayers:int = 8
    TimeLimit:float = 300.0

ConfigType:concrete_subtype(config) = config  # 有效

# 无效：抽象类不能是crete_subtype
abstract_base := class<abstract>:
    Value:int

# 这将是一个错误：
# 基础类型：具体子类型（抽象基础）=抽象基础
```
当您有 `concrete_subtype` 时，您可以使用以下命令实例化它
空原型 `{}`，但您无法提供字段初始值设定项 -
具体类必须提供所有必要的默认值：

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

# 无效：无法通过元类型初始化字段
# Instance := EntityType{Health := 150}
```
<a id="castable_subtype"></a>
### `castable_subtype`

`castable_subtype(t)` 类型构造函数表示的类型
`t` 的子类型并用 `<castable>` 说明符标记。这个
启用运行时类型查询和动态转换，这是必不可少的
对于组件系统和多态层次结构：

<!--versetest
entity:=class{}
vector3:=class{}
-->
<!-- 113 -->
```verse
# 可转换基类
component := class<abstract><castable>:
    Owner:entity

# 可转换子类型
physics_component := class<castable>(component):
    Velocity:vector3

render_component := class<castable>(component):
    Material:string

# 接受可转换子类型的函数
ProcessComponent(CompType:castable_subtype(component), Comp:component):void =
    # 可以使用 CompType 执行类型安全转换
    if (Specific := CompType[Comp]):
        # Comp 现在已知为 CompType 类型
```
### Final_super 和类型查询

`castable_subtype` 与 `<final_super>` 说明符一起使用，并且
`GetCastableFinalSuperClass` 功能可实现复杂的运行时
类型查询。这种组合提供了强大的机制
组件系统和多态架构。

`<final_super>` 说明符将类标记为稳定锚点
继承层次结构。这些“最终超级类”充当规范
相关类别家庭代表：

<!--versetest
entity:=class{}
vector3:=class{}
-->
<!-- 114 -->
```verse
component := class<castable>:
    Owner:entity

# 物理组件系列的稳定锚点
physics_component := class<final_super>(component):
    Velocity:vector3

# 具体实现继承自anchor
rigid_body := class(physics_component):
    Mass:float

soft_body := class(physics_component):
    SpringConstant:float
```
通过将 `physics_component` 标记为 `<final_super>`，您可以将其声明为所有物理相关组件的规范代表。尽管 `rigid_body` 和 `soft_body` 是不同的类型，但它们都属于锚定于 `physics_component` 的“物理组件系列”。

<a id="getcastablefinalsuperclass"></a>
#### 获取CastableFinalSuperClass

`GetCastableFinalSuperClass` 函数查询类型层次结构以查找基类型和派生类型之间的 `<final_super>` 类。存在两种变体：

<!--NoCompile-->
<!-- 115 -->
```verse
# 举个例子
GetCastableFinalSuperClass(BaseType, instance)<decides>:castable_subtype(BaseType)

# 需要一个类型
GetCastableFinalSuperClassFromType(BaseType, Type)<decides>:castable_subtype(BaseType)
```
两者都返回一个 `castable_subtype` ，表示最不具体的 `<final_super>` 类：

1.直接继承指定的基类型
2. 位于实例/类型的继承链中

如果不存在适当的 `<final_super>` 类，则该函数将失败。

考虑这个层次结构：


<!--versetest
vector3:=class{}
-->
<!-- 116 -->
```verse
component := class<castable>:
    ID:int

# 组件的直接final_super子类
physics_component := class<final_super>(component):
    Velocity:vector3

# 物理组件的后代
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
# 物理组件系列中的所有实例都返回物理组件
Body := character_body{ID:=1, Velocity:=vector3{}, Mass:=10.0, Health:=100}

if (Family := GetCastableFinalSuperClass[component, Body]):
    # Family =物理组件（final_super联系点）
    # Body 是character_body，但族某个点是Physics_Component
```
该函数沿着继承链从 `character_body` → `rigid_body` → `physics_component` 向上“走”，并在 `physics_component` 处停止，因为：

1.它有`<final_super>`
2.直接继承自查询的基数(`component`)

**查询何时成功和失败？**

**成功时：**

- `<final_super>` 类直接继承自基类型
- 实例/类型继承自 `<final_super>` 类

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

# 有效：anchor是base的final_super，衍生自anchor继承
GetCastableFinalSuperClass[base, derived{}]  # 返回锚点
GetCastableFinalSuperClass[base, anchor{}]   # 返回锚点
```
<!-- #>-->

**失败时：**

- 基础和实例之间不存在 `<final_super>` 类
- 查询的类型本身就是实例类型（不能同级查询）
- 实例不是基础的子类型


#### 多个最终超级

您可以在不同级别拥有多个 `<final_super>` 类。的
函数返回直接从查询的基类继承的一个：

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

# 从基地返回查询first_anchor
GetCastableFinalSuperClass[base, leaf{}]  # 返回first_anchor

# 从first_anchor的查询返回second_anchor
GetCastableFinalSuperClass[first_anchor, leaf{}]  # 返回第二个锚点
```
<!-- #>-->


这种分层方法允许分层分类，其中
不同的级别代表类型族的不同粒度。

<a id="getcastablefinalsuperclassfromtype"></a>
#### GetCastableFinalSuperClassFromType

基于类型的变体工作原理相同，但采用类型而不是实例：

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

# 两者都返回相同的castable_subtype
```
<!-- #>-->

当直接使用类型值而不是实例时，这非常有用。

### `castable_concrete_subtype`

`castable_concrete_subtype(t)` 类型构造函数结合了 `castable_subtype` 和 `concrete_subtype` 的要求，表示类型：
- `t` 的子类型
- 标记为 `<castable>`（启用运行时类型查询）
- 标记为 `<concrete>`（启用实例化）

当您需要确保类型参数既可转换又具体时，这非常有用：

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

# 同时需要 <castable> 和 <concrete> 的函数
CreateAndCast(CompType:castable_concrete_subtype(component)):component =
    # 可以实例化，因为 CompType 是 <concrete>
    Instance := CompType{}
    # 可以强制转换，因为 CompType 是 <castable>
    if (Specific := CompType[Instance]):
        Specific
    else:
        Instance
```
<!-- ERROR:
Line 23: Script Error 3100: vErr:S04: Block comment beginning at "<#" never ends
-->
#>

<a id="classifiable_subset"></a>
### 可分类子集

建立在 引入的运行时类型查询的概念之上
`castable_subtype`，Verse 提供 `classifiable_subset`—a
用于维护运行时类型集的复杂机制。哪里
`castable_subtype` 表示单一类型值，
`classifiable_subset` 表示类型的集合，跟踪哪些
类存在于系统中并支持基于类型的查询
层次结构。

此功能对于基于组件的特别有价值
架构，您需要跟踪实体的组件类型
拥有、查询特定功能或基于过滤操作
关于类型兼容性。而不是维护单独的布尔标志
或类型标签，`classifiable_subset` 提供类型安全、
运行时类型的层次结构感知注册表。

三种相关类型共同提供不可变和
可变类型集：

**`classifiable_subset(t)`** 表示一组不可变的运行时
类型，其中 `t` 必须是 `<castable>` 基本类型。一旦创建，
set 无法修改，适合配置，
功能描述，或者类型集应该的任何场景
保持稳定。

**`classifiable_subset_var(t)`** 提供了一个可变变体
`Read()` 和 `Write()` 操作，启用动态类型集
程序执行期间改变。这对于运行时系统至关重要
随着实体的发展，组件类型会被添加或删除。

**`classifiable_subset_key(t)`**表示用于识别的密钥
将它们添加到可变集时的特定实例。这些键
稍后可以删除特定实例，支持生命周期
注册类型的管理。

与普通类不同，`classifiable_subset` 类型不能
直接实例化。您必须使用构造函数
`MakeClassifiableSubset()` 和 `MakeClassifiableSubsetVar()`：

<!--versetest
component:=class<castable>{}
physics_component := class<final_super>(component){}
rigid_body := class(physics_component){}
render_component := class<castable>(component){}
-->
<!-- 124 -->
```verse
# 不可变集，最初为空
EmptySet:classifiable_subset(component) = MakeClassifiableSubset()

# 具有初始实例的不可变集
InitialSet:classifiable_subset(component) =
    MakeClassifiableSubset(array{physics_component{}, render_component{}})

# 可变集
DynamicSet:classifiable_subset_var(component) = MakeClassifiableSubsetVar()
```
基本类型 `t` 必须是 `<castable>`，确保运行时类型查询
是可能的。此限制在编译时强制执行：

<!--versetest
component:=class<computes><castable>{}
f()<reads>:void =
    ComponentSet:classifiable_subset(component) = MakeClassifiableSubset()

<#
-->
<!-- 1215 -->
```verse
ComponentSet:classifiable_subset(component) = MakeClassifiableSubset()

# 无效：不能使用不可转换类型
regular_class := class:
    Value:int

# 这将是一个错误：
# BadSet:classific_subset(regular_class) = MakeClassABLESubset()
```
<!-- #> -->

您不能对这些类型进行子类化或通过普通的方式创建实例
构造语法。这确保所有集合都使用正确的
高效类型查询的内部表示。

#### 类型层次结构语义

`classifiable_subset` 的关键洞察在于它跟踪运行时
类型，而不是单个实例。当您将实例添加到集合中时，
系统记录该实例的实际运行时类型。更多
重要的是，类型查询尊重继承层次结构：


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
# 添加刚体实例
Set:classifiable_subset(component) =
    MakeClassifiableSubset(array{rigid_body_component{}})

# 查询结果尊重层次结构
Set.Contains[component]             # true -rigid_body 是一个组件
Set.Contains[physics_component]     # true - 只是一个物理组件
Set.Contains[rigid_body_component]  # true——直接表达
```
这种层次意识使得 `classifiable_subset` 从根本上
与一组简单的类型标签不同。 `Contains`操作
询问“该集合是否包含 T 类型？”而不是“
该集合恰好包含 T？”。

当您添加不同类型的实例时，每个不同的运行时类型
单独跟踪：

<!--versetest
component := class<castable>{}
physics_component := class<castable>(component){}
rigid_body_component := class<castable>(physics_component){ }
render_component := class<castable>(component){}
audio_component := class<castable>(component){}
-->
<!-- 127 -->
```verse
# 添加多种不同类型
TheSet:classifiable_subset_var(component) = MakeClassifiableSubsetVar()
Key1 := TheSet.Add(physics_component{})
Key2 := TheSet.Add(render_component{})
Key3 := TheSet.Add(audio_component{})

TheSet.Contains[component]          # 成功 - 所有三个都是组件
TheSet.Contains[physics_component]  # 成功 - 物理组件存在
TheSet.Contains[render_component]   # 成功 - render_component 存在
```
该集合会记住添加的每个不同类型。当您通过其键删除实例时，仅当该特定类型是该类型的最后一个实例时才会删除该特定类型：

<!--versetest
component := class<castable>{}
physics_component := class<castable>(component){}
rigid_body_component := class<castable>(physics_component){ }
-->
<!-- 128 -->
```verse
# 添加多个相同类型的实例
TheSet:classifiable_subset_var(component) = MakeClassifiableSubsetVar()
Key1 := TheSet.Add(physics_component{})
Key2 := TheSet.Add(physics_component{})

TheSet.Contains[physics_component]  # 成功

TheSet.Remove[Key1]
TheSet.Contains[physics_component]  # 仍然成功 - Key2 仍然存在

TheSet.Remove[Key2]
# TheSet.Contains[physical_component] # 失败 - 最后一个实例被删除
```
#### 核心操作

`classifiable_subset` 类型提供了多种操作
查询和操作类型集：

**包含** 检查集合中的任何类型是否匹配或者是一个
查询类型的子类型：

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
    # 物理组件存在（并且是一个组件）

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
**ContainsAny** 检查数组中是否至少存在一种类型：

<!--NoCompile-->
<!-- 131 -->
```verse
if (TheSet.ContainsAny[array{physics_component, audio_component}]):
    # 存在物理或音频组件（或两者）
```
**添加**（仅限可变集）添加一个实例并返回一个键以供以后删除：


<!--versetest
component := class<castable>{ Name:string = "Component"}
physics_component := class<castable>(component){}
-->
<!-- 132 -->
```verse
TheSet:classifiable_subset_var(component) = MakeClassifiableSubsetVar()
Key := TheSet.Add(physics_component{})
# 稍后可以使用按键删除
```
**删除**（仅限可变集）通过其键删除先前添加的实例：

<!--versetest
component := class<castable>{}
physics_component := class<castable>(component){}
-->
<!-- 133 -->
```verse
TheSet:classifiable_subset_var(component) = MakeClassifiableSubsetVar()

Key := TheSet.Add(physics_component{})

if (TheSet.Remove[Key]):
    # 已成功删除
else:
    # 密钥不存在（已删除或从未添加）
```
**FilterByType** 创建一个新集，仅包含与指定类型兼容（可分配给指定类型或从指定类型分配）的类型：


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

# 过滤物理相关类型
PhysicsSet := TheSet.FilterByType(physics_component)
PhysicsSet.Contains[physics_component]  # 真实
PhysicsSet.Contains[render_component]   # false - 无血缘关系的兄弟
PhysicsSet.Contains[component]          # true - 基本类型兼容
```
<!-- #>-->

过滤尊重向上和向下兼容性
类型层次结构，保留可以分配给或来自的类型
过滤器类型。

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
Combined.Contains[physics_component]  # 真实
Combined.Contains[render_component]   # 真实
```
对于可变集，读/写操作启用复制和更新：

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
#### 设计考虑因素

`classifiable_subset` 使用的几个重要约束：

基本类型必须是 `<castable>` 才能启用运行时类型
查询。此要求确保可以执行类型检查
高效。

您不能对 `classifiable_subset` 类型进行子类化或创建实例
除非通过指定的构造函数。这个限制
维护正确类型跟踪所需的内部不变量。

一组钥匙不能与另一组钥匙一起使用——它们必须
添加元素的特定集合实例。

不同操作之间的类型参数必须一致。你不能
将 `physics_component` 添加到 `classifiable_subset(render_component)`
即使两者都继承自 `component`：

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

# 这将是一个类型错误 -物理组件不是渲染组件
# render_set.Add(physics_comp)
```
可变集需要仔细的生命周期管理。密钥失效
当它们对应的实例被删除时，并尝试
删除已删除的密钥会触发失败。

性能特征对于大型字体集很重要。同时
由于内部表示，`Contains` 查询是高效的，
像 `FilterByType` 这样的操作可能需要检查中的每种类型
设置。

使用 `classifiable_subset` 设计系统时，请考虑是否
不可变或可变集更适合您的需求。不可变集
为配置提供更有力的保证和良好的运行，同时
可变集支持组件类型发生变化的动态系统
经常。

层次结构感知语义意味着添加派生类型使得
基本类型查询成功。这通常是可取的，但需要
意识 - 如果您只想精确类型匹配，`classifiable_subset`
可能不是正确的工具。
