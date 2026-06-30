# 类和接口

类和接口是 Verse 的面向对象构建块
通过继承、多态性和实现丰富的类型层次结构
基于接口的合约。类提供面向对象的编程
具有字段、方法和单继承，使您能够建模
具有共享行为的游戏实体的复杂层次结构
专门的实施。接口定义类的合约
必须满足，促进松耦合并启用多个
行为规范的继承。

类和接口共同构成了强大的建模系统
具有 is-a 关系的游戏实体、组件和系统
（通过类继承）和can-do契约（通过接口
实施）。

让我们首先探索类，然后深入研究接口以及它们如何
相辅相成。

<a id="classes"></a>
## 类

类构成了 Verse 中面向对象编程的支柱。一个
类作为创建共享公共对象的蓝图
属性和行为。当你定义一个类时，你就创建了一个
将数据（字段）与对该数据的操作捆绑在一起的新类型
（方法），将相关功能封装到一个内聚单元中。

类定义发生在模块范围内。你不能定义一个类
在另一个类、结构、接口或函数内部。类是
建立类型系统结构的顶级类型定义：

<!--versetest-->
<!-- 01-->
```verse
# 有效：模块范围内的类
MyModule := module:
    entity := class:
        ID:int

# 无效：类位于另一个类中
# outer := class:
#     inner := class:  # ERROR: classes must be at module scope
#         值：整数
```
类的最简单形式将相关数据组合在一起。考虑
在游戏中建模角色：

<!--versetest-->
<!-- 02-->
```verse
character := class:
    Name : string
    var Health : int = 100
    var Level : int = 1
    MaxHealth : int = 100
```
这个类定义建立了几个重要的概念。领域
如果没有 `var` 修饰符，则在构造后是不可变的 - 一旦您
创建一个具有特定名称的角色，该名称不能
改变。标有 `var` 的字段是可变的，可以在之后修改
对象已创建（有关详细信息，请参阅[可变性](05_mutability.md)
在 `var` 和 `set` 上）。默认值提供了合理的起点，
在保证对象的同时让对象构建更加便捷
从有效状态开始。

<a id="object-construction"></a>
### 对象构造

创建类的实例涉及为其指定值
通过原型表达式的字段：

<!--versetest
character := class:
    Name : string
    var Health : int = 100
    var Level : int = 1
    MaxHealth : int = 100
	
Ignore:int=1
-->
<!-- 03-->
```verse
Hero := character{Name := "Aldric", Health := 100, Level := 5}
Villager := character{Name := "Martha"}  # 未指定字段的默认值
```
原型语法使用命名参数，使得构造
明确且自记录。任何具有默认值的字段都可以
从原型中省略，将使用默认值。领域
必须指定没有默认值的情况，确保对象始终是完整的
已初始化。字段可以按任何顺序传递给原型。

### 方法

当您添加对类进行操作的方法时，类就会变得真正强大
班级数据：

<!--versetest-->
<!-- 04-->
```verse
character := class:
    Name : string
    var Health : int = 100
    var Level : int = 1
    var MaxHealth : int = 100

    TakeDamage(Amount : int) : void =
        set Health = Max(0, Health - Amount)

    Heal(Amount : int) : void =
        set Health = Min(MaxHealth, Health + Amount)

    IsAlive()<decides>:void= Health > 0

    LevelUp() : void =
        set Level += 1
        set MaxHealth = 100 + (Level * 10)
        set Health = MaxHealth  # 升级时完全治愈
```
方法可以访问类的所有字段并且可以修改可变的
字段。它们封装了类的对象应该如何进行的逻辑
行为，确保状态变化以受控、可预测的方式发生
方式。

非抽象类中的所有方法都必须有实现。不像
接口（可以声明抽象方法）、具体类
没有实现的方法声明是一个错误：

<!--versetest-->
<!-- 05-->
```verse
# 有效：方法与实现
valid_class := class:
    Compute():int = 42

# 无效：具体类中没有实现的方法
# invalid_class := class:
#     Compute():int  # ERROR: needs implementation
```
<a id="blocks-for-initialization"></a>
### 初始化块

类可以在其主体中包含 `block` 子句，该子句在以下情况下执行
创建一个实例。这些块运行初始化代码
除了简单的字段分配之外，还允许您执行设置逻辑，
验证或构建过程中的副作用：

<!--versetest
GetCurrentTime()<computes>:float=0.0

logged_entity := class:
    ID:int
    var CreationTime:float = 0.0

    block:
        # This executes when an instance is created
        Print("Creating entity with ID: {ID}")
        set CreationTime = GetCurrentTime()

M()<transacts>:void =
    Entity := logged_entity{ID := 42}
    # Prints: "Creating entity with ID: 42"
<#
-->
<!-- 06-->
```verse
logged_entity := class:
    ID:int
    var CreationTime:float = 0.0

    block:
        # 创建实例时执行
        Print("Creating entity with ID: {ID}")
        set CreationTime = GetCurrentTime()

# Entity := logged_entity{ID := 42}
# 打印：“正在创建 ID 为 42 的实体”
```
<!-- #>-->

块子句可以访问该类的所有字段，包括
`Self`，并且可以修改可变字段。他们按照他们的顺序执行
出现在类定义中：

<!--versetest-->
<!-- 07-->
```verse
multi_step_init := class:
    var Step1:int = 0
    var Step2:int = 0

    block:
        set Step1 = 10

    var Step3:int = 0

    block:
        set Step2 = Step1 + 5  # 可以访问较早的字段
        set Step3 = Step2 * 2

# Instance := multi_step_init{}
# 实例.Step1 = 10，Step2 = 15，Step3 = 30
```
**具有继承的执行顺序：**当一个类继承自
另一个类，Verse VM 执行块
子类在超类之前的顺序，而 BP VM 使用
超类在子类之前的顺序。对于可移植代码，避免依赖
关于跨继承层次结构的块的执行顺序。

**为什么是块而不是构造函数？** 块子句可以访问
`Self` 和类的所有字段，而构造函数则这样做
无法访问 `Self`。这使得街区成为自然的场所
需要引用对象的初始化逻辑
构建 - 例如向全局系统注册 `Self` 或
计算来自多个字段的派生值。

此外，字段默认值不能使用发散调用 — 调用
这可能不完整。这意味着你不能写：

<!--NoCompile-->
<!-- 06a-->
```verse
# 错误 V3582：发散调用不能用于定义数据成员
bar := class:
    Foo:foo = MakeFoo()
```
相反，您可以为该字段提供一个简单的默认值，然后将
初始化逻辑到块中：

<!--NoCompile-->
<!-- 06b-->
```verse
bar := class:
    var Foo:foo = foo{}

    block:
        set Foo = MakeFoo()  # 块可以调用发散函数
```
**块条款的约束：**

- 块不能包含失败（`<decides>`）操作
- 块不能调用挂起（`<suspends>`）函数
- 块可以使用 `defer` 语句，该语句在块退出时执行
- 块子句只允许在类中使用，不允许在接口中使用，
  结构体或模块

块子句对于以下情况特别有用：

- 记录对象创建
- 在初始化期间计算派生值
- 向全局系统注册对象
- 执行需要 `Self` 或发散调用的初始化

### 原型中的 Let 子句

原型表达式（用于构造类和结构实例）
可以包含引入局部变量绑定的 `let` 子句。
这些对于计算多个使用的中间值很有用
字段初始值设定项，避免重复：

<!--NoCompile-->
<!-- 06c-->
```verse
MkWord8<constructor>(I:int)<decides><transacts> := Word8:
    let:
        MaxU8:int = Int[Pow(2.0, 8.0)] - 1 or Impossible("MkWord8")
    B := 0 <= I and I <= MaxU8
```
`let` 子句引入了绑定（上例中的 `MaxU8`）
对同一区域中的后续字段初始值设定项可见
原型。与 `block` 子句不同，`let` 子句仅限于
仅变量声明 - 不允许独立表达式
`let` 内。

### 自我

在类方法中，`Self` 是一个特殊关键字，指的是
类的当前实例。每个方法调用都有自己的
`Self` 指的是调用该方法的特定对象。

您可以在方法体内以多种方式使用 `Self`：

- 访问实例的字段
- 调用实例的方法
- 将实例传递给其他函数
- 返回实例

<!--NoCompile-->
<!-- 08-->
```verse
character := class:
    var Name : string
    var Config:[string]string = map{}
	
    Announce() : void =
        # 使用 Self 传递整个对象
        LogCharacterAction(Self, "announced")


    SetOption(Key:string, Value:string):character =
        set Config[Key] = Value
        Self  # 返回此实例以进行方法链接


    SetName(NewName:string):void =
       set Self.Name = NewName	  # 设置该实例的名称
	   Self.Announce()            # 调用该实例的方法
```
创建嵌套对象时可以捕获 `Self`：

<!--versetest-->
<!-- 12-->
```verse
container := class:
    ID:int

    CreateChild():child_with_parent =
        child_with_parent{Parent := Self}  # 捕获此实例

child_with_parent := class:
    Parent:container

# C := container{ID := 42}
# Child := C.CreateChild()
# Child.Parent.ID = 42 # Child 存储对 C 的引用
```
<a id="inheritance"></a>
### 继承

类支持单继承，允许您创建专门的
现有类的版本。这创建了“is-a”关系
其中子类是超类的更具体类型：

<!--versetest
vector3:=struct{}

entity := class:
    var Position : vector3 = vector3{}
    var IsActive : logic = true

    Activate() : void = set IsActive = true
    Deactivate() : void = set IsActive = false

character := class(entity):  # character inherits from entity
    Name : string
    var Health : int = 100

    TakeDamage(Amount : int) : void =
        set Health = Max(0, Health - Amount)
        if (Health = 0):
            Deactivate()  # Can call inherited methods

player := class(character):  # player inherits from character
    var Score : int = 0
    var Lives : int = 3

    AddScore(Points : int) : void =
        set Score += Points
<#
-->
<!-- 13-->
```verse
entity := class:
    var Position : vector3 = vector3{}
    var IsActive : logic = true

    Activate() : void = set IsActive = true
    Deactivate() : void = set IsActive = false

character := class(entity):  # 角色继承自实体
    Name : string
    var Health : int = 100

    TakeDamage(Amount : int) : void =
        set Health = Max(0, Health - Amount)
        if (Health = 0):
            Deactivate()  # 可以调用继承的方法

player := class(character):  # 玩家继承自角色
    var Score : int = 0
    var Lives : int = 3

    AddScore(Points : int) : void =
        set Score += Points
```
<!-- #>-->

继承创建了一个类型层次结构，其中 `player` 也是
`character`，`character` 也是 `entity`。这意味着您可以
在需要 `character` 或 `entity` 的任何地方使用 `player` 对象，
启用多态行为。

**继承的重要限制：**

1. **仅单类继承：** 一个类最多可以继承自
   另一个类，尽管它可以实现多个
   接口。不支持多类继承：

<!--versetest-->
<!-- 14-->
```verse
base1 := class:
    Value1:int

base2 := class:
    Value2:int

# 有效：继承一个类和多个接口
interface1 := interface:
    Method1():void

interface2 := interface:
    Method2():void

derived := class<abstract>(base1, interface1, interface2):
    # 有效：一个类，多个接口
    Method1<override>():void = {}
    Method2<override>():void = {}

# 无效：不能从多个类继承
# invalid := class(base1, base2):  # ERROR
```
2. **数据成员没有阴影：** 子类不能声明字段
   与其超类中的字段同名。这可以防止
   模糊性并确保明确的数据所有权：

<!--versetest-->
<!-- 15-->
```verse
base := class:
    Value:int

# 无效：无法隐藏父级的字段
# derived := class(base):
#     值：int # 错误：遮蔽base.Value
```
3. **没有方法签名更改：** 重写方法时，必须
   使用完全相同的签名。更改参数类型或返回
   类型会产生阴影错误：

<!--versetest-->
<!-- 16-->
```verse
base := class:
    Compute():int = 42

# 无效：返回类型不同
# derived := class(base):
#     Compute():float = 3.14  # ERROR: signature doesn't match
```
要覆盖方法，请使用 `<override>` 说明符和匹配的签名。

### `super`

在子类中，您可以使用 `super` 关键字来引用
超类类型。这主要用于访问超类的
实现或构造超类实例：

<!--versetest-->
<!-- 17-->
```verse
entity := class:
    ID:int
    Name:string

    Display():void =
        Print("Entity {ID}: {Name}")

character := class(entity):
    Health:int

    Display<override>():void =
        # 创建一个超类实例来调用其方法
        super{ID := ID, Name := Name}.Display()
        Print("Health: {Health}")
```
`super` 关键字表示超类类型本身。当你
写 `super{...}`，您正在创建超类的实例
指定的字段值。这允许您委托给超类
添加子类特定功能时的行为。

在重写方法中，您可以调用父类的
使用 `(super:)` 语法实现。这是主要方法
添加或修改时调用父方法实现
行为：

<!--versetest-->
<!-- 18-->
```verse
base := class:
    Method():void =
        Print("Base implementation")

derived := class(base):
    Method<override>():void =
        # 首先调用父实现
        (super:)Method()
        Print("Derived implementation")

# 创建实例并调用Method()
# 派生{}.Method()
# 输出：
# 基地实施
# 派生实现

```
`(super:)` 语法显式调用父类的版本
当前的方法。这比
当您只需要时，使用 `super{...}` 构造父实例
调用父方法。

**基本用法：**

<!--versetest
ToString(:vector3)<computes>:string=""
vector3:=class<final>{ X:float=0.0; Y:float=0.0; Z:float=0.0 }

entity := class:
    Position:vector3

    Move(Delta:vector3):void =
        Print("Entity moving by {Delta}")
        # Update position logic here

character := class(entity):
    var Stamina:float = 100.0

    Move<override>(Delta:vector3):void =
        # Call parent movement logic
        (super:)Move(Delta)
        # Add character-specific behavior
        set Stamina -= 1.0
<#
-->
<!--versetest-->
<!-- 19-->
```verse
entity := class:
    Position:vector3

    Move(Delta:vector3):void =
        Print("Entity moving by {Delta}")
        # 在此更新持仓逻辑

character := class(entity):
    var Stamina:float = 100.0

    Move<override>(Delta:vector3):void =
        # 调用父级移动逻辑
        (super:)Move(Delta)
        # 添加特定于角色的行为
        set Stamina -= 1.0
```
<!-- #>-->

**带有效果说明符：**

`(super:)` 语法与所有效果说明符无缝协作：

<!--versetest
async_base := class:
    Process()<suspends>:void =
        Sleep(1.0)
        Print("Base processing")

async_derived := class(async_base):
    Process<override>()<suspends>:void =
        # Parent method suspends, so this suspends too
        (super:)Process()
        Print("Derived processing")

transactional_base := class:
    var Value:int = 0

    Update()<transacts>:void =
        set Value += 1

transactional_derived := class(transactional_base):
    var Counter:int = 0

    Update<override>()<transacts>:void =
        (super:)Update()
        set Counter += 1
<#
-->
<!--versetest-->
<!-- 20-->
```verse
async_base := class:
    Process()<suspends>:void =
        Sleep(1.0)
        Print("Base processing")

async_derived := class(async_base):
    Process<override>()<suspends>:void =
        # 父方法挂起，所以这个也挂起
        (super:)Process()
        Print("Derived processing")

transactional_base := class:
    var Value:int = 0

    Update()<transacts>:void =
        set Value += 1

transactional_derived := class(transactional_base):
    var Counter:int = 0

    Update<override>()<transacts>:void =
        (super:)Update()
        set Counter += 1
```
<!-- #>-->

**通过父方法进行虚拟调度：**

当父方法调用其他方法时，虚拟调度仍然适用
基于实际的对象类型。这意味着 `Self` 绑定到
即使通过 `(super:)` 调用时也派生实例：

<!--versetest-->
<!-- 21-->
```verse
base := class:
    # 可重写的虚拟方法
    GetValue()<computes>:int = 10

    # 使用 GetValue 的父方法
    ComputeDouble()<computes>:int =
        2 * GetValue()  # 如果被覆盖，则调用派生的GetValue

derived := class(base):
    # 重写 GetValue 以返回不同的值
    GetValue<override>()<computes>:int = 20

    # 重写ComputeDouble来调用父级，但GetValue调度是虚拟的
    ComputeDouble<override>()<computes>:int =
        # 调用base.ComputeDouble，它调用derivative.GetValue！
        (super:)ComputeDouble()

# 派生{}.ComputeDouble() # 返回 40，而不是 20
```
在此示例中，即使 `ComputeDouble` 调用父级
实现中，父级内部的 `GetValue()` 调用使用虚拟
调度并调用派生版本。

**使用重载方法：**

`(super:)` 语法适用于重载方法，调用
相同重载的父版本：

<!--versetest-->
<!-- 22-->
```verse
base := class:
    Process(X:int):void =
        Print("Base int: {X}")

    Process(S:string):void =
        Print("Base string: {S}")

derived := class(base):
    Process<override>(X:int):void =
        (super:)Process(X)  # 调用级父的int重载
        Print("Derived int: {X}")

    Process<override>(S:string):void =
        (super:)Process(S)  # 调用父级的字符串重载
        Print("Derived string: {S}")
```
**返回类型协方差：**

当使用 `(super:)` 重写方法时，返回类型可以是父级返回类型的子类型（协变返回类型）：

<!--versetest-->
<!-- 23-->
```verse
base_type := class:
    Name:string

derived_type := class(base_type):
    Value:int

base := class:
    Create():base_type =
        base_type{Name := "base"}

derived := class(base):
    # 使用更具体的返回类型覆盖
    Create<override>():derived_type =
        # 即使返回类型不同，仍然可以调用父级
        Parent := (super:)Create()
        derived_type{Name := Parent.Name, Value := 42}
```
<a id="method-overriding"></a>
### 方法重写

子类可以重写其超类中定义的方法以提供专门的行为：

<!--versetest
character:=class:
    IsAlive()<decides><transacts>:void={}
MoveToward(:?character)<transacts>:void={}
Patrol()<transacts>:void={}
ScanForTargets()<transacts>:void={}
-->
<!-- 24-->
```verse
entity := class:
    OnUpdate<public>() : void = {}  # 默认无操作实现

enemy := class(entity):
    var Target : ?character = false

    OnUpdate<override>()<transacts> : void =
        if (Target?.IsAlive[]):
            MoveToward(Target)
        else:
            Patrol()

turret := class(entity):
    var Rotation:int= 0

    OnUpdate<override>()<transacts>: void =
        if (V:= Mod[Rotation, 360]):
            set Rotation = V
        ScanForTargets()
```
重写机制保证了正确的方法实现
是根据对象的实际类型而不是对象的类型来调用的
变量持有它。这是多态行为的基础
面向对象编程。

<a id="constructor-functions"></a>
### 构造函数

类没有您可能会发现的传统构造函数方法
在其他面向对象语言中。相反，Verse 提供了三种
对象构造方法，每种方法适合不同的需求：

- **原型表达式** — 直接字段初始化以实现简单
  案例。简单明了，不需要额外的定义。
- **块子句** — 运行的类主体中的初始化代码
  在每一个建筑上。有权访问 `Self` 和所有字段，
  使其成为注册对象、计算派生的理想选择
  值，或调用不能出现在字段中的发散函数
  默认值。
- **构造函数** — 用 `<constructor>` 注释，这些
  是可以验证输入的一流函数，委托给
  其他构造函数（包括父类构造函数），是
  重载，并作为值传递。他们是最
  强大的选项，对于继承层次结构至关重要
  子类构造函数需要初始化超类字段。

这些方法组成：构造函数返回原型
表达式，可以包含 `let` 和 `block` 子句，以及
类体也可以有自己的 `block` 子句来执行
无论使用哪个构造函数。

对于只需要设置字段值的简单情况，请使用
直接原型表达式：

<!--versetest-->
<!-- 25-->
```verse
player := class:
    Name:string
    var Health:int = 100
    Level:int = 1

# 使用原型直接构建
# Hero := player{Name := "Aldric", Health := 150, Level := 5}
```
当您需要验证、计算或复杂的初始化时
逻辑，使用用 `<constructor>` 注释的构造函数：

<!--versetest
player := class:
    Name:string
    var Health:int = 100
    Level:int = 1

MaxLevel:int = 99
-->
<!-- 26-->
```verse
MakePlayer<constructor>(InName:string, InLevel:int)<transacts> := player:
    Name := InName
    Level := InLevel
    Health := InLevel * 100
```
这是调用此构造函数的示例：

<!--versetest
player := class:
    Name:string
    var Health:int = 100
    Level:int = 1
MaxLevel:int = 99
MakePlayer<constructor>(InName:string, InLevel:int)<transacts> := player:
    Name := InName
    Level := InLevel
    Health := InLevel * 100
-->
<!-- 261-->
```verse
Hero := MakePlayer("Aldric", 5) # 调用构造函数
```
构造函数是返回类的常规函数
实例，但 `<constructor>` 注释启用特殊
诸如委托给其他构造函数之类的功能。当呼叫
普通代码中的构造函数，仅使用函数名称 -
`<constructor>` 注释仅出现在定义中。

构造函数可以产生控制它们的效果
行为。常见效果包括 `<computes>`、`<allocates>` 和
`<transacts>`。一个特别有用的效果是 `<decides>`，它
如果不满足先决条件，则允许构造函数失败：

<!--versetest
player := class:
    Name:string
    var Health:int = 100
    Level:int = 1

MaxLevel:int = 99
-->
<!-- 27-->
```verse
MakeValidPlayer<constructor>(InName:string, InLevel:int)<transacts><decides> := 
    player:
         Name := InName
         Level := block:
                 InLevel > 0
                 InLevel <= MaxLevel
                 InLevel
         Health := InLevel * 100
```
下面是一个使用经过验证的构造函数和失败处理的示例：

<!--versetest
player := class:
    Name:string
    var Health:int = 100
    Level:int = 1
MaxLevel:int = 99
MakeValidPlayer<constructor>(InName:string, InLevel:int)<transacts><decides> := 
    player:
         Name := InName
         Level := block:
                 InLevel > 0
                 InLevel <= MaxLevel
                 InLevel
         Health := InLevel * 100
AddPlayer(:player):void={}
-->
<!-- 271-->
```verse
# 构造函数可能会失败 - 使用失败语法
if (Player := MakeValidPlayer["Hero", 5]):
    # 施工成功
    AddPlayer(Player)
else:
    # 施工失败 - 水平超出范围
```
构造函数不能使用 `<suspends>` 效果。建筑工程
必须同步完成以保持对象一致性。

### 重载构造函数

您可以提供多个不同的构造函数
参数签名，允许灵活的对象创建：

<!--versetest
vector3:=class<final>{ X:float=0.0; Y:float=0.0; Z:float=0.0 }
-->
<!-- 28-->
```verse
entity := class:
    Name:string
    var Health:int = 100
    Position:vector3

# 具有所有参数的构造函数
MakeEntity<constructor>(Name:string, Health:int, Position:vector3) := entity:
    Name := Name
    Health := Health
    Position := Position

# 带默认值的构造函数
MakeEntity<constructor>(Name:string, Position:vector3) := entity:
    Name := Name
    Health := 100
    Position := Position

# 原点放置的构造函数
MakeEntity<constructor>(Name:string) := entity:
    Name := Name
    Health := 100
    Position := vector3{X := 0.0, Y := 0.0, Z := 0.0}

# 每个重载都可以根据参数调用
# Enemy1 := MakeEntity("Goblin", 50, SpawnPoint)
# Enemy2 := MakeEntity("Guard", PatrolPoint)
# NPC := MakeEntity("Shopkeeper")
```
### 委托构造函数

构造函数可以委托给其他构造函数，从而使
代码重用和构造函数链接。这一点尤为重要
对于子类构造函数需要的继承层次结构
初始化超类字段。

当从子类委托给父类构造函数时，您
必须先初始化子类字段，然后调用父类
在构造函数中使用合格的 `<constructor>` 语法
原型：

<!--versetest
entity := class:
    Name:string
    var Health:int

character := class(entity):
    Class:string
    Level:int

MakeEntity<constructor>(Name:string, Health:int) := entity:
    Name := Name
    Health := Health

# Subclass constructor delegates to parent constructor
MakeCharacter<constructor>(Name:string, Class:string, Level:int) := character:
    # Initialize subclass fields first
    Class := Class
    Level := Level
    # Then delegate to parent constructor
    MakeEntity<constructor>(Name, Level * 100)
<#
-->
<!-- 29-->
```verse
entity := class:
    Name:string
    var Health:int

MakeEntity<constructor>(Name:string, Health:int) := entity:
    Name := Name
    Health := Health

character := class(entity):
    Class:string
    Level:int

# 子类构造函数委托给父类构造函数
MakeCharacter<constructor>(Name:string, Class:string, Level:int) := character:
    # 首先初始化子类字段
    Class := Class
    Level := Level
    # 然后委托给父构造函数
    MakeEntity<constructor>(Name, Level * 100)

Hero := MakeCharacter("Aldric", "Warrior", 5)
```
<!-- #>-->

构造函数还可以转发给同一类的其他构造函数：

<!--versetest
player := class:
    Name:string
    var Score:int

# Primary constructor
MakePlayer<constructor>(Name:string, Score:int) := player:
    Name := Name
    Score := Score

# Convenience constructor forwards to primary
MakeNewPlayer<constructor>(Name:string) := player:
    # Delegate to another constructor of the same class
    MakePlayer<constructor>(Name, 0)
<#
-->
<!-- 30-->
```verse
player := class:
    Name:string
    var Score:int

# 主构造函数
MakePlayer<constructor>(Name:string, Score:int) := player:
    Name := Name
    Score := Score

# 方便构造函数转发到主构造函数
MakeNewPlayer<constructor>(Name:string) := player:
    # 委托给同一个类的另一个构造函数
    MakePlayer<constructor>(Name, 0)
```
<!-- #>-->

下面是调用构造函数的示例：

<!--versetest
player := class:
    Name:string
    var Score:int

# Primary constructor
MakePlayer<constructor>(Name:string, Score:int) := player:
    Name := Name
    Score := Score

# Convenience constructor forwards to primary
MakeNewPlayer<constructor>(Name:string) := player:
    # Delegate to another constructor of the same class
    MakePlayer<constructor>(Name, 0)
-->
<!-- 301-->
```verse
NewPlayer := MakeNewPlayer("Alice")
```
当委托给同一个类的构造函数时，委托
替换所有字段初始化——您在之前初始化的任何字段
代表团被忽略。当委托给父类构造函数时，
您的子类字段初始化被保留，并且父类
构造函数初始化父字段。

### 执行顺序

了解执行顺序对于正确初始化至关重要：

1. **原型表达式：** 字段初始值设定项按顺序执行
   它们被写在原型中
2. **委托构造函数：** 首先初始化子类字段，
   然后父构造函数运行
3. **类主体块：** 当使用直接原型构造时，
   类定义中的块在字段初始化之前执行

将构造函数委托给父类：

<!--versetest
base := class:
    BaseValue:int

derived := class(base):
    DerivedValue:int

MakeBase<constructor>(Value:int) := base:
    block:
        Print("Base constructor")
    BaseValue := Value

MakeDerived<constructor>(Base:int, Derived:int) := derived:
    # This executes first
    DerivedValue := Derived
    # Then parent constructor executes
    MakeBase<constructor>(Base)
<#
-->
<!-- 31-->
```verse
base := class:
    BaseValue:int

MakeBase<constructor>(Value:int) := base:
    block:
        Print("Base constructor")
    BaseValue := Value

derived := class(base):
    DerivedValue:int

MakeDerived<constructor>(Base:int, Derived:int) := derived:
    # 这首先执行
    DerivedValue := Derived
    # 然后执行父构造函数
    MakeBase<constructor>(Base)
```
<!-- #>-->

这是显示执行顺序的示例：

<!--versetest
base := class:
    BaseValue:int

MakeBase<constructor>(Value:int) := base:
    block:
        Print("Base constructor")
    BaseValue := Value

derived := class(base):
    DerivedValue:int

MakeDerived<constructor>(Base:int, Derived:int) := derived:
    # This executes first
    DerivedValue := Derived
    # Then parent constructor executes
    MakeBase<constructor>(Base)
-->
<!-- 311-->
```verse
# 打印：“基本构造函数”
# 结果为：derived{BaseValue := 10, DerivedValue := 20}
Instance := MakeDerived(10, 20)
```
对于具有可变字段的类，初始化设置起始值
在对象的生命周期中可能会发生变化。不可变字段必须是
构造时初始化，之后不能修改。这个
区别使得施工阶段对于建立
在对象的整个存在过程中都保持不变的不变量。

## 影子和资格

Verse 对名称隐藏有严格的规则，以防止歧义和
保持代码清晰。了解这些规则和资格
语法对于处理继承层次结构、多重继承至关重要
接口和嵌套模块。

在大多数情况下，您**无法重新定义已存在于的名称**
一个封闭的范围。这适用于函数、变量、类、
接口和模块：

<!--versetest-->
<!-- 32-->
```verse
# 错误：模块级别的函数隐藏了类方法
# F(X:int):int = X + 1
# c := class:
#     F(X:int):int = X + 2  # ERROR - shadows outer F
```
该禁令适用于多种情况：

<!--NoCompile-->
<!-- 33-->
```verse
# 错误：无法影子类
something := class {}

M := module:
    something := class {}  # 错误

# 错误：无法隐藏变量
Value:int = 1

M := module:
     Value:int = 2        # 错误

# 错误：无法隐藏数据成员
c := class { A:int }

A():void = {}             # 错误 - 顺序无关紧要

# 错误：模块和函数无法共享名称

Id():void = {}
Id := module {}           # 错误
```
存在阴影禁止**无论定义顺序如何** -
外部名称是在之前还是之后定义并不重要
内部范围。

要在不同上下文中定义具有相同名称的方法，请使用
**限定名称**，语法为 `(ClassName:)MethodName`：

<!--versetest-->
<!-- 34-->
```verse
# 具有同名限定方法的类
c := class:
   (c:)F(X:int):int = X + 2

# 模块级功能
F(X:int):int = X + 1

# 调用模块级函数
F(10)  # 返回 11

# 调用类方法
c{}.F(10)  # 返回 12

# 显式限定（此处可选）
c{}.(c:)F(10)  # 返回 12
```
`(c:)` 限定符表示此 `F` 是在
`c` 类上下文，将其与模块级区分开来
`F`。这允许相同的名称共存而不会出现阴影错误。

### 同名方法

使用限定符，您可以定义同名的*新方法*
继承方法，在同一个方法中创建多个不同的方法
类：

<!--versetest-->
<!-- 35-->
```verse
c := class<abstract> { F(X:int):int }

d := class(c):
    F<override>(X:int):int = X + 1

e := class(d):
    (e:)F(X:int):int = X + 2 # 具有相同名称的新方法，而不是覆盖

# e 现在包含两种方法：
#    - (d:)F 继承自 d
#    - (e:)F 在 e 中新定义
```
使用上面的：

<!--versetest
c := class<abstract> { F(X:int):int }
d := class(c):
    F<override>(X:int):int = X + 1
e := class(d):
    (e:)F(X:int):int = X + 2 # NEW method with same name, not an override
-->
<!-- 351-->
```verse
E := e{}
E.(c:)F(10)  # 返回 11（继承自 d 的重写）
E.(e:)F(10)  # 返回 12（e 中的新方法）
```
主要区别：

- `F<override>` 不带限定符：覆盖继承的 `F`
- `(e:)F` 不带 `<override>`：定义特定于 `e` 的**新** `F`

这允许一个类有多个同名的方法，
根据其限定符进行区分，每个限定符都有不同的用途
类层次结构。

### `(super:)` 合格

`(super:)` 限定符与限定方法名称一起调用
父类的实现：

<!--versetest-->
<!-- 36-->
```verse
i := interface { F(X:int):int }

ci := class(i):
    (i:)F<override>(X:int):int = X + 1
    (ci:)F(X:int):int = X + 2

dci := class(ci):
    # 覆盖两个继承的方法，调用超级实现
    (i:)F<override>(X:int):int = 100 + (super:)F(X)
    (ci:)F<override>(X:int):int = 200 + (super:)F(X)

```
以及一个用例：

<!--versetest
i := interface { F(X:int):int }

ci := class(i):
    (i:)F<override>(X:int):int = X + 1
    (ci:)F(X:int):int = X + 2

dci := class(ci):
    # Override both inherited methods, calling super implementations
    (i:)F<override>(X:int):int = 100 + (super:)F(X)
    (ci:)F<override>(X:int):int = 200 + (super:)F(X)
-->
<!-- 361-->
```verse
DCI := dci{}
DCI.(i:)F(10)  # 返回 111（100 + ci 的 11）
DCI.(ci:)F(10)  # 返回 212（200 + ci 的 12）
```
`(super:)F(X)` 限定方法内调用父类的
实施相同的合格方法。这使您能够
独立扩展多个方法变体的行为。

### 接口冲突

当使用同名方法实现多个接口时，
限定符可以消除您正在实现的接口方法的歧义：


<!--versetest-->
<!-- 37-->
```verse
i := interface:
    B(X:int):int

j := interface:
    B(X:int):int

collision := class(i, j):
    # 分别实现两个B方法
    (i:)B<override>(X:int):int = 20 + X
    (j:)B<override>(X:int):int = 30 + X
```
以及一个用例：

<!--versetest
i := interface:
    B(X:int):int
j := interface:
    B(X:int):int
collision := class(i, j):
    (i:)B<override>(X:int):int = 20 + X
    (j:)B<override>(X:int):int = 30 + X
-->
<!-- 371-->
```verse
Obj := collision{}
Obj.(i:)B(1)  # 返回 21
Obj.(j:)B(1)  # 返回 31
```
如果没有限定符，编译器无法确定哪个接口
您正在实施的方法，导致错误。资质
使你的意图明确。

**复杂的接口层次结构：**

<!--versetest-->
<!-- 38-->
```verse
i := interface:
    C(X:int):int

j := interface(i):
    A(X:int):int

k := interface(i):
    B(X:int):int
    (k:)C(X:int):int  # k 重新定义 C

multi := class(j, k):
    A<override>(X:int):int = 10 + X
    B<override>(X:int):int = 20 + X
    # 必须从两个继承路径实现 C
    (i:)C<override>(X:int):int = 30 + X
    (k:)C<override>(X:int):int = 40 + X
```
一个用例：

<!--versetest
i := interface:
    C(X:int):int

j := interface(i):
    A(X:int):int

k := interface(i):
    B(X:int):int
    (k:)C(X:int):int  # k redefines C

multi := class(j, k):
    A<override>(X:int):int = 10 + X
    B<override>(X:int):int = 20 + X
    # Must implement C from both inheritance paths
    (i:)C<override>(X:int):int = 30 + X
    (k:)C<override>(X:int):int = 40 + X
-->
<!-- 381-->
```verse
Obj := multi{}
Obj.(i:)C(1)  # 返回 31
Obj.(k:)C(1)  # 返回 41
```
当接口使用父接口重新定义方法时
资质 `(k:)C`，实施类必须提供
两种变体的单独实现。

### 嵌套模块资格

模块可以嵌套，深度限定名称引用成员
贯穿整个层次结构：

<!--versetest-->
<!-- 39-->
```verse
Top := module:
    (Top:)M<public> := module:
        (Top.M:)Value<public>:int = 1
        (Top.M:)F<public>(X:int):int = X + 10

        (Top.M:)M<public> := module:
            (Top.M.M:)Value<public>:int = 3
            (Top.M.M:)F<public>(X:int):int = X + 100
```
以及一个用例：

<!--versetest
Top := module:
    (Top:)M<public> := module:
        (Top.M:)Value<public>:int = 1
        (Top.M:)F<public>(X:int):int = X + 10

        (Top.M:)M<public> := module:
            (Top.M.M:)Value<public>:int = 3
            (Top.M.M:)F<public>(X:int):int = X + 100

using { Top.M }
using { Top.M.M }

-->
<!-- 391-->
```verse
# 使用 { Top.M }
# 使用 { 顶.M.M }

# 完全资质准入
(Top.M:)F(0)          # 返回 10
(Top.M.M:)F(0)        # 返回 100

# 通过路径访问
Top.M.F(1)            # 返回 11
Top.M.M.F(1)          # 返回 101
```
嵌套模块可以具有相同的简单名称（例如，都是 `M`）
当符合其完整路径时，允许分层
组织没有命名冲突。

### 限制

限定词只能在适当的上下文中使用。你不能使用
局部变量的类限定符：

<!--NoCompile-->
<!-- 40-->
```verse
C := class:
    f():void =
        (C:)X:int = 0  # 错误 - 错误的上下文
```
不支持某些限定符。本地函数限定符
不允许使用变量：

<!--NoCompile-->
<!-- 41-->
```verse
C := class:
    f():void =
        (C.f:)X:int = 0  # 错误 - 不支持的模式
```
同样，不支持使用模块函数路径作为限定符：

<!--NoCompile-->
<!-- 42-->
```verse
M := module:
    f():void =
        (M.f:)X:int = 0  # 错误
```
局部变量不能隐藏类成员：

<!--NoCompile-->
<!-- 43-->
```verse
A := class:
    I:int
    F(X:int):void =
        I:int = 5  # 错误 - 影子成员 I
```
目前，没有 `(local:)` 限定符来消除歧义，因此这
不支持模式。您必须为本地使用不同的名称
变量和成员。

<a id="parametric-classes"></a>
## 参数类

参数类，也称为泛型类，允许您定义
适用于任何类型的类。而不是单独写
整数、字符串、玩家等的容器类
类型，您可以编写一个接受类型参数的参数类。

参数类在其定义中采用一个或多个类型参数：

<!--versetest
# Simple container that holds a single value
container(t:type) := class:
    Value:t
<#
-->
<!-- 46-->
```verse
# 保存单个值的简单容器
container(t:type) := class:
    Value:t
```
<!-- #>-->

以下是使用不同类型实例化此参数类的示例：

<!--versetest
container(t:type) := class:
    Value:t

player := class:
    Name:string
    var Health:int = 100
-->
<!-- 461-->
```verse
# 可以用任何类型实例化
IntContainer := container(int){Value := 42}
StringContainer := container(string){Value := "hello"}
PlayerContainer := container(player){Value := player{Name := "Hero", Health := 100}}
```
语法 `container(t:type)` 定义一个由类型 `t` 参数化的类。在类定义中，`t` 可以在任何具体类型出现的地方使用——在字段声明、方法签名或返回类型中。

**多种类型参数：**

类可以接受多个类型参数：

<!--NoCompile-->
<!-- 47-->
```verse
pair(t:type, u:type) := class:
    First:t
    Second:u
```
以下是使用参数对类的示例：

<!--versetest
pair(t:type, u:type) := class:
    First:t
    Second:u
-->
<!-- 471-->
```verse
# 每个参数有不同的类型
Coordinate := pair(int, int){First := 10, Second := 20}
NamedValue := pair(string, float){First := "score", Second := 99.5}
```
**在方法中键入参数：**

类型参数在整个类中可用，包括在方法中：

<!--versetest
optional_container(t:type) := class:
    var MaybeValue:?t = false

    Set(Value:t):void =
        set MaybeValue = option{Value}

    Get()<decides>:t =
        MaybeValue?

    Clear():void =
        set MaybeValue = false
<#
-->
<!-- 48-->
```verse
optional_container(t:type) := class:
    var MaybeValue:?t = false

    Set(Value:t):void =
        set MaybeValue = option{Value}

    Get()<decides>:t =
        MaybeValue?

    Clear():void =
        set MaybeValue = false
```
<!-- #> -->

方法自动了解类中的类型参数
定义——您不必在方法签名中重新声明它。

### 实例化和身份

当您使用特定类型参数实例化参数类时，
Verse创造了一种具体的类型。至关重要的是，**多个实例化
使用相同类型的参数会产生相同的类型**：

<!--versetest
container(t:type) := class:
    Value:t

# These are the same type
Type1 := container(int)
Type2 := container(int)
Type3 := container(int)

# All three are equal - they're the same type
<#
-->
<!-- 49-->
```verse
container(t:type) := class:
    Value:t

# 这些是同一类型
Type1 := container(int)
Type2 := container(int)
Type3 := container(int)

# 三者都是平等的——它们是同一类型
```
<!-- #>-->

这种类型的一致性在整个程序中得到保证：

<!--versetest
container(t:type) := class:
    Value:t
-->
<!-- 50-->
```verse
# 创建实例
C1 := container(int){Value := 1}
C2 := container(int){Value := 2}

# 两者具有相同的类型：container(int)
# 类型检查对它们一视同仁
```
实例化过程是**确定性和记忆化的**。第一个
当您写入 `container(int)` 时，Verse 会生成一个具体的
类型。 `container(int)` 的每次后续使用均指相同的
类型，而不是新副本。

这对于：

- **类型兼容性**：可以使用 `container(int)` 的两个值
  可互换地
- **内存效率**：不创建重复的类型定义
- **语义正确性**：相同类型的参数始终意味着相同的类型

虽然相同类型的参数总是产生相同的类型，但不同的
类型参数产生不同的、不兼容的类型：

<!--versetest
container(t:type) := class:
    Value:t
<#
-->
<!-- 52-->
```verse
container(t:type) := class:
    Value:t
```
<!-- #>-->


下面的示例显示不同的实例化创建不同的类型：

<!--versetest
container(t:type) := class:
    Value:t
-->
<!-- 521-->
```verse
IntContainer := container(int){Value := 42}
StringContainer := container(string){Value := "text"}

# 这些是不同的类型，不能混合使用
# IntContainer = StringContainer # 类型错误！
```
`container(int)` 和 `container(string)` 完全不同
类型，没有子类型关系。他们碰巧拥有相同的
结构（均由 `container` 定义），但这并不意味着它们
兼容。

虽然参数类的不同实例是不同的
类型，Verse 允许使用某些实例化来代替
其他基于**方差**。方差决定何时
`parametric_class(subtype)` 可用于以下场合
预期为 `parametric_class(supertype)`（反之亦然）。

参数类型的方差取决于类型参数的方式
在类定义中使用：

<a id="covariant"></a>
#### 协变

当类型参数仅出现在**返回位置**时（方法
返回类型，正在读取的字段类型），参数类是
该参数中的 **协变** （参见
[类型](11_types.md#understanding-subtyping) 了解详细信息
方差）。这意味着实例化遵循相同的子类型
方向作为它们的类型参数：

<!--versetest
entity := class:
    ID:int
player := class(entity):
    Name:string
producer(t:type) := class:
    Value:t
    Get():t = Value  # Returns t - covariant position
ProcessProducer(P:producer(entity)):int = P.Get().ID
<#
-->
<!-- 53-->
```verse
# 基类层次结构
entity := class:
    ID:int

player := class(entity):
    Name:string

# 协变类 - 仅在返回位置键入参数
producer(t:type) := class:
    Value:t

    Get():t = Value  # 返回 t - 协变位置

# 可以在生产者（实体）期望的地方使用生产者（玩家）
ProcessProducer(P:producer(entity)):int = P.Get().ID
```
<!-- #>-->

这是演示协方差的示例：

<!--versetest
# Base class hierarchy
entity := class:
    ID:int

player := class(entity):
    Name:string

# Covariant class - type parameter only in return position
producer(t:type) := class:
    Value:t

    Get():t = Value  # Returns t - covariant position

# Can use producer(player) where producer(entity) expected
ProcessProducer(P:producer(entity)):int = P.Get().ID
-->
<!-- 531-->
```verse
# 协方差允许子类型→超类型
PlayerProducer:producer(player) = producer(player){Value := player{ID := 1, Name := "Alice"}}
EntityProducer:producer(entity) = PlayerProducer  # 有效！

Result := ProcessProducer(PlayerProducer)  # 有效！
```
**为什么这是安全的：** 如果您希望从
生产者，接收 `player` （它是 `entity` 的子类型）是
始终有效 — `player` 具有 `entity` 的所有属性。

**方向：** `producer(player)` → `producer(entity)` ✓（如下
亚型方向）

#### 逆变

当类型参数仅出现在**参数位置**时（方法
被消耗的参数），参数类是**逆变**
在该参数中（请参阅[类型](11_types.md#understanding-subtyping)
有关方差的详细信息）。这意味着实例化遵循
**相反**子类型方向：


<!--versetest-->
<!-- 54-->
```verse
entity := class:
    ID:int

player := class(entity):
    Name:string

# 逆变类 - 仅在参数位置键入参数
consumer(t:type) := class:
    Process(Item:t):void = {}  # 接受 t - 逆变位置
```
以及一个用例：

<!--versetest
entity := class:
    ID:int
player := class(entity):
    Name:string
consumer(t:type) := class:
    Process(Item:t):void = {}
-->
<!-- 54-->
```verse
# 逆变允许超类型 → 子类型
EntityConsumer:consumer(entity) = consumer(entity){}
PlayerConsumer:consumer(player) = EntityConsumer  # 有效！

# 可以在消费者（玩家）期望的地方使用消费者（实体）
ProcessPlayers(C:consumer(player)):void =
    C.Process(player{ID := 1, Name := "Bob"})

ProcessPlayers(EntityConsumer)                    # 有效！
```
**为什么这是安全的：** 如果您有一个接受任何
`entity`，它当然可以处理更具体的 `player` 类型。一个
`consumer(entity)` 可以消耗 `consumer(player)` 可以消耗的任何东西
消耗，再加上更多。

**方向：** `consumer(entity)` → `consumer(player)` ✓（与
亚型方向）

#### 不变式

当类型参数出现在**参数和返回中时
位置**，参数类是**不变的**
参数。不同类型之间不存在子类型关系
实例化：

<!--versetest
entity := class:
    ID:int

player := class(entity):
    Name:string

# Invariant class - type parameter in both positions
transformer(t:type) := class:
    Transform(Input:t):t = Input  # Both parameter and return
<#
-->
<!-- 55-->
```verse
entity := class:
    ID:int

player := class(entity):
    Name:string

# 不变类 - 两个位置的类型参数
transformer(t:type) := class:
    Transform(Input:t):t = Input  # 参数和返回值都一样
```
<!-- #>-->

下面的示例显示不同实例化之间不存在差异：

<!--versetest
entity := class:
    ID:int

player := class(entity):
    Name:string

# Invariant class - type parameter in both positions
transformer(t:type) := class:
    Transform(Input:t):t = Input  # Both parameter and return
-->
<!-- 551-->
```verse
# 无方差 - 不能在任一方向上转换
EntityTransformer:transformer(entity) = transformer(entity){}
PlayerTransformer:transformer(player) = transformer(player){}

# 无效：不能在需要其中之一的地方使用另一个
# X:transformer(实体) = PlayerTransformer # 错误 3509
# Y:transformer(玩家) = EntityTransformer # 错误 3509
```
**为什么这是必要的：** 如果 `transformer(player)` 可以用作
`transformer(entity)`，您可以将任何 `entity` 传递给其
`Transform` 方法，特别需要 `player`。这会
不安全。

**方向：** 任一方向均不允许转换

#### 双变量

当类型参数未在任何方法签名中使用时（仅在
私有实现细节或根本没有），参数类是
**双变量**。任何实例化都可以转换为任何其他实例化：

<!--versetest
entity := class:
    ID:int

player := class(entity):
    Name:string

# Bivariant class - type parameter not used in public interface
container(t:type) := class:
    DoSomething():void = {}  # Doesn't use t at all
<#
-->
<!-- 56-->
```verse
entity := class:
    ID:int

player := class(entity):
    Name:string

# 双变类 - 公共接口中未使用类型参数
container(t:type) := class:
    DoSomething():void = {}  # 根本不使用t
```
<!-- #>-->


下面的示例显示双变量类允许双向转换：

<!--versetest
entity := class:
    ID:int

player := class(entity):
    Name:string

# Bivariant class - type parameter not used in public interface
container(t:type) := class:
    DoSomething():void = {}  # Doesn't use t at all
-->
<!-- 561-->
```verse
# 双变量允许双向转换
EntityContainer:container(entity) = container(entity){}
PlayerContainer:container(player) = container(player){}

# 两个方向都有效
X:container(entity) = PlayerContainer  # 有效
Y:container(player) = EntityContainer  # 也有效
```
**为什么会这样：** 因为类型参数不会影响
可观察的行为，实例化是可以互换的。

### 递归参数类型

参数类可以在其字段类型中引用自身，
支持递归通用数据结构，如链表、树、
和图表。关键要求是自引用使用
**相同类型参数** — 这是唯一的递归形式
Verse 允许。它之所以有效，是因为编译器可以解析类型
一次传递的结构：`list_node(int)` 包含一个
`?list_node(int)`，其中包含`?list_node(int)`，依此类推。
可选的（`?`）提供终止的基本情况
运行时递归。

这是一个作为递归参数类构建的通用链表：

<!--versetest
# Linked list node
list_node(t:type) := class:
    Value:t
    Next:?list_node(t)  # Same type parameter 't'

# Helper to create lists
Cons(Head:t, Tail:?list_node(t) where t:type):list_node(t) =
    list_node(t){Value := Head, Next := Tail}

# Sum a linked list
SumList(List:?list_node(int)):int =
    if (Head := List?):
        Head.Value + SumList(Head.Next)
    else:
        0
<#
-->
<!-- 69-->
```verse
# 链表节点
list_node(t:type) := class:
    Value:t
    Next:?list_node(t)  # 相同类型参数“t”

# 创建列表的助手
Cons(Head:t, Tail:?list_node(t) where t:type):list_node(t) =
    list_node(t){Value := Head, Next := Tail}

# 对链表求和
SumList(List:?list_node(int)):int =
    if (Head := List?):
        Head.Value + SumList(Head.Next)
    else:
        0
```
<!-- #>-->

下面是使用链表的示例：

<!--versetest
# Linked list node
list_node(t:type) := class:
    Value:t
    Next:?list_node(t)  # Same type parameter 't'

# Helper to create lists
Cons(Head:t, Tail:?list_node(t) where t:type):list_node(t) =
    list_node(t){Value := Head, Next := Tail}

# Sum a linked list
SumList(List:?list_node(int)):int =
    if (Head := List?):
        Head.Value + SumList(Head.Next)
    else:
        0
-->
<!-- 691-->
```verse
# 用途
IntList := list_node(int){
    Value := 1
    Next := option{list_node(int){
        Value := 2
        Next := false
    }}
}
```
**不允许：直接类型别名递归**

您不能定义直接别名为
包含自身的结构类型：

<!--versetest-->
<!-- 71-->
```verse
# 无效：直接数组递归
# t(u:type) := []t(u)  # ERROR 3502

# 无效：直接映射递归
# t(u:type) := [int]t(u)  # ERROR 3502

# 无效：直接可选递归
# t(u:type) := ?t(u)  # ERROR 3502

# 无效：直接函数递归
# t(u:type) := u->t(u)  # ERROR 3502
# t(u:type) := t(u)->u  # ERROR 3502
```
这些失败是因为它们创建了无限的类型扩展——编译器
无法确定类型的实际结构。

**有效的替代方案：** 将递归引用包装在类中。对于
例如，每个节点都保存子节点列表的树是
递归参数类型 — 每个 `nested_list(t)` 包含一个数组
`nested_list(t)`：

<!-- NoCompile-->
<!-- 72-->
```verse
# 有效：通过类间接递归
nested_list(t:type) := class:
    Items:[]nested_list(t)  # 好的 - 上课了
```
这是构建具有两个子节点的树的示例：

<!--versetest
# Valid: Indirect recursion through class
nested_list(t:type) := class:
    Items:[]nested_list(t)  # OK - wrapped in class
-->
<!-- 721-->
```verse
Tree := nested_list(int){
    Items := array{
        nested_list(int){Items := array{}},
        nested_list(int){Items := array{}}
    }
}
```
**不允许：多态递归**

当参数类型引用自身时，就会发生多态递归
使用**不同类型的参数**：

<!--NoCompile-->
<!-- 73-->
```verse
# 无效：类型参数更改
# my_type(t:type) := class:
#     下一页：my_type(?t) # 错误 3509 - ?t 与 t 不同

# 无效：交替类型参数
# bi_list(t:type, u:type) := class:
#     值：t
#     下一步：?bi_list(u, t) # 错误 3509 - 参数交换
```
**为什么这是不允许的：** 多态递归进行类型推断
不可判定，并且可以创建无限复杂的类型。当你
实例化`my_type(int)`，需要`my_type(?int)`，这需要
`my_type(??int)`，等等永远。

**当前限制：** 虽然多态递归理论上是
某些类型系统中的声音，Verse 目前不支持
保持类型检查易于处理。

**不允许：相互递归**

不支持多个参数类型之间的相互递归：

<!--versetest-->
<!-- 74-->
```verse
# 无效：互递归
# t1(t:type) := class:
#     下一篇：?t2(t) # 参考文献 t2
#
# t2(t:type) := class:
#     下一篇：?t1(t) # 参考文献 t1
```
**为什么这是不允许的：** 与多态递归类似，相互
递归使类型推断复杂化并可能产生循环
编译器难以解决的依赖关系。

**解决方法：** 合并为单一类型：

<!-- NoCompile-->
<!-- 75-->
```verse
# 有效：单一类型，多种情况
node_type := enum:
    TypeA
    TypeB

combined_node(t:type) := class:
    Type:node_type
    Value:t
    Next:?combined_node(t)
```
**不允许：继承递归**

您不能从类型变量继承或创建递归
通过参数类型继承：

<!--versetest-->
<!-- 76-->
```verse
# 无效：从参数 self 继承
# t(u:type) := class(t(u)){}  # ERROR 3590

# 无效：从类型变量继承
# inherits_from_variable(t:type) := class(t){}  # ERROR 3590
```
**为什么这是不允许的：** 继承需要知道父母的
结构，但是使用参数递归，该结构将是
在定义之前先自我指涉。


### 参数化接口

虽然参数类最受关注，但接口也可以
也可以是参数化的，从而使抽象合约能够与任何
类型：

<!-- TODO why is this not working?-->

<!--versetest
equivalence(t:type, u:type) := interface:
    Equal(Left:t, Right:u)<transacts><decides>:t

# Generic collection interface
collection_ifc(t:type) := interface:
    AddItem(Item:t)<transacts>:void
    RemoveItem(Item:t)<transacts><decides>:void
    Has(Item:t)<reads>:logic
<#
-->
<!-- 80-->
```verse
# 通用平等接口
equivalence(t:type, u:type) := interface:
    Equal(Left:t, Right:u)<transacts><decides>:t

# 通用采集接口
collection_ifc(t:type) := interface:
    Add(Item:t)<transacts>:void
    Remove(Item:t)<transacts><decides>:void
    Has(Item:t)<reads>:logic
```
<!-- #>-->

类通过提供具体类型来实现参数化接口
对于参数：

<!-- versetest 
equivalence(t:type, u:type) := interface:
    Equal(Left:t, Right:u)<transacts><decides>:t

int_equivalence := class(equivalence(int, comparable)):
    Equal<override>(Left:int, Right:comparable)<transacts><decides>:int =
        Left = Right

# Or with type parameters matching the class
comparable_equivalence(t:subtype(comparable)) := class(equivalence(t, comparable)):
    Equal<override>(Left:t, Right:comparable)<transacts><decides>:t =
        Left = Right
<#
-->
<!-- 81-->
```verse
equivalence(t:type, u:type) := interface:
    Equal(Left:t, Right:u)<transacts><decides>:t

# 使用特定类型实现
int_equivalence := class(equivalence(int, comparable)):
    Equal<override>(Left:int, Right:comparable)<transacts><decides>:int =
        Left = Right

# 或者使用与类匹配的类型参数
comparable_equivalence(t:subtype(comparable)) := class(equivalence(t, comparable)):
    Equal<override>(Left:t, Right:comparable)<transacts><decides>:t =
        Left = Right
```
<!-- #> -->

以下是使用参数化接口的示例：

<!--versetest
equivalence(t:type, u:type) := interface:
    Equal(Left:t, Right:u)<transacts><decides>:t

# Implement with specific types
int_equivalence := class(equivalence(int, comparable)):
    Equal<override>(Left:int, Right:comparable)<transacts><decides>:int =
        Left = Right

# Or with type parameters matching the class
comparable_equivalence(t:subtype(comparable)) := class(equivalence(t, comparable)):
    Equal<override>(Left:t, Right:comparable)<transacts><decides>:t =
        Left = Right
-->
<!-- 811-->
```verse
# 用途
Eq := comparable_equivalence(int){}
Eq.Equal[5, 5]  # 成功
```
参数接口遵循与参数类相同的方差规则：

<!-- NoCompile-->
<!-- 82-->
```verse
entity := class:
    ID:int

player := class(entity):
    Name:string

# 协变接口 - 返回 t
producer_interface(t:type) := interface:
    Produce():t

player_producer := class(producer_interface(player)):
    Produce<override>():player = player{ID := 1, Name := "Test"}
```
这是协变子类型的示例：

<!--versetest
entity := class:
    ID:int

player := class(entity):
    Name:string

# Covariant interface - returns t
producer_interface(t:type) := interface:
    Produce():t

player_producer := class(producer_interface(player)):
    Produce<override>():player = player{ID := 1, Name := "Test"}
-->
<!-- 821-->
```verse
# 协变子类型工作
EntityProducer:producer_interface(entity) = player_producer{}
```
您可以从参数化接口创建专用（非参数化）接口：

<!-- NoCompile-->
<!-- 83-->
```verse
generic_handler(t:type) := interface:
    Handle(Item:t):void

# 专门针对具体类型
int_handler := interface(generic_handler(int)):
    # 继承句柄(Item:int):void
    # 可以在这里添加更多方法

int_processor := class(int_handler):
    Handle<override>(Item:int):void =
        Print("Handling: {Item}")
```
下面是在强制转换中使用专用接口的示例：

<!--versetest
generic_handler(t:type) := interface:
    Handle(Item:t):void

# Specialize to a concrete type
int_handler := interface(generic_handler(int)):
    # Inherits Handle(Item:int):void
    # Can add more methods here

int_processor := class(int_handler):
    Handle<override>(Item:int):void =
        Print("Handling: {Item}")
-->
<!-- 831-->
```verse
# 现在可以在强制转换中使用（专用接口是非参数的）
Base := int_processor{}
if (Handler := int_handler[Base]):
    Handler.Handle(42)
```
#### 多种类型参数

接口可以有多个具有独立方差的类型参数：

<!-- NoCompile-->
<!-- 84-->
```verse
converter_interface(input:type, output:type) := interface:
    Convert(In:input):output
    # 输入是逆变的，输出是协变的

entity := class:
    ID:int

player := class(entity):
    Name:string

# 使用特定类型实现
player_to_entity := class(converter_interface(player, entity)):
    Convert<override>(In:player):entity = entity{ID := In.ID}
```
这里使用的是：

<!--versetest
converter_interface(input:type, output:type) := interface:
    Convert(In:input):output
    # input is contravariant, output is covariant

entity := class:
    ID:int

player := class(entity):
    Name:string

# Implement with specific types
player_to_entity := class(converter_interface(player, entity)):
    Convert<override>(In:player):entity = entity{ID := In.ID}

-->
<!-- 841-->
```verse
# 方差允许灵活使用
C:converter_interface(player, entity) = player_to_entity{}
```
### 高级参数类型

#### 效果

参数类型可以具有适用于所有实例化的效果说明符：

<!-- versetest 
# Parametric class with effects
async_container(t:type) := class<computes>:
    Property:t

# All instantiations inherit the effect
X:async_container(int) = async_container(int){Property := 1}  # <computes> effect

# Multiple effects
transactional_container(t:type) := class<transacts>:
    Property:t

assert:
    Y:transactional_container(int) = transactional_container(int){Property := 2}
<#
-->
<!-- 88-->
```verse
# 带效果的参数类
async_container(t:type) := class<computes>:
    Property:t

# 所有实例化都会继承效果
X:async_container(int) = async_container(int){Property := 1}  # <computes>效果

# 多种效果
transactional_container(t:type) := class<transacts>:
    Property:t

# 构造函数继承效果
# Y:transactional_container(int) = transactional_container(int){Property := 2}
```
<!-- #> -->

**允许的效果：**

- `<computes>` - 允许非终止计算
- `<transacts>` - 参与交易
- `<reads>` - 读取可变状态
- `<writes>` - 写入可变状态
- `<allocates>` - 分配资源

**不允许：**

- `<decides>` - 可能会失败
- `<suspends>` - 可以暂停执行
- `<converges>` - `<converges>` 效果保证函数终止（请参阅[效果](13_effects.md) 章节）。参数类不能使用它，因为实例化参数类型可能涉及任意计算 - 编译器无法保证为所有可能的 `t` 构造 `my_type(t)` 将终止。

**效果传播：**

<!-- versetest 
my_type(t:type) := class<computes>:
    Property:t

# This requires <computes> in the context
CreateInstance()<computes>:my_type(int) =
    my_type(int){Property := 1}
<#
-->
<!-- 89-->
```verse
# 对参数类型的影响会传播到构造函数
my_type(t:type) := class<computes>:
    Property:t

# 这需要上下文中的<computes>
CreateInstance()<computes>:my_type(int) =
    my_type(int){Property := 1}
```
<!-- #> -->

该效果成为类型契约的一部分——所有构建或使用实例的代码都必须考虑这些效果。

#### 别名

您可以创建类型别名来简化复杂的参数类型表达式：

<!--versetest-->
<!-- 92-->
```verse
# 映射类型的别名
string_map(t:type) := [string]t

# 使用别名
PlayerScores:string_map(int) = map{
    "Alice" => 100,
    "Bob" => 95
}

# 可选数组的别名
optional_array(t:type) := []?t

# 简化类型签名
FilterValid(Items:optional_array(int)):[]int =
    for (Item : Items; Value := Item?):
        Value
```
**结构类型别名：**

<!--versetest-->
<!-- 94-->
```verse
# 函数类型别名
transformer(input:type, output:type) := input -> output
predicate(t:type) := t -> logic

# 元组类型别名
pair(t:type, u:type) := tuple(t, u)
triple(t:type) := tuple(t, t, t)

# 在签名中使用
ApplyTransform(T:transformer(int, string), Value:int):string =
    T(Value)

CheckCondition(P:predicate(int), Value:int):logic =
    P(Value)
```
类型别名提高了复杂泛型类型的可读性和可维护性。

<a id="advanced-type-constraints"></a>
#### 高级类型约束

除了基本的 `subtype` 约束之外，参数类型还支持特殊约束：

**子类型限制：**

<!--versetest
entity:=class{ID:int=0}
player:=class(entity){}

# Constrain to subtype of a class
bounded_container(t:subtype(entity)) := class:
    Value:t

    GetID():int = Value.ID  # Can access entity members

# Valid: player is subtype of entity
# PlayerContainer := bounded_container(player){}

# Invalid: int is not subtype of entity
# IntContainer := bounded_container(int){}  # Type error

<#
-->
<!-- 95-->
```verse
# 限制为类的子类型
bounded_container(t:subtype(entity)) := class:
    Value:t

    GetID():int = Value.ID  # 可以访问实体成员

# 有效：玩家是实体的子类型
# PlayerContainer := bounded_container(player){}

# 无效：int 不是实体的子类型
# IntContainer := bounded_container(int){}  # Type error
```
<!-- #>-->

**可转换子类型约束：**

<!--versetest
component:=class<castable>{}
ProcessTyped(:component)<computes>:void={}

# Requires castable subtype
dynamic_handler(t:castable_subtype(component)) := class:
    Handle(Item:component):void =
        if (Typed := t[Item]):
            # Typed has the specific subtype
            ProcessTyped(Typed)

<#
-->
<!-- 96-->
```verse
# 需要可浇注子类型
dynamic_handler(t:castable_subtype(component)) := class:
    Handle(Item:component):void =
        if (Typed := t[Item]):
            # 具有特定子类型的类型
            ProcessTyped(Typed)
```
<!-- #> -->

**约束传播：**

<!--versetest
# Constraints propagate through function calls
wrapper(t:subtype(comparable)) := class:
    Data:t

Process(W:wrapper(t) where t:subtype(comparable))<computes><decides>:void =
    # Compiler knows t is comparable here
    W.Data = W.Data
<#
-->
<!-- 98-->
```verse
# 约束通过函数调用传播
wrapper(t:subtype(comparable)) := class:
    Data:t

Process(W:wrapper(t) where t:subtype(comparable))<computes><decides>:void =
    # 编译器知道 t 在这里是可比较的
    W.Data = W.Data
```
<!-- #> -->

定义与参数类型一起使用的参数函数时，
约束必须兼容：

<!--versetest
base_class := class:
    ID:int
constrained(t:subtype(base_class)) := class:
    Data:t
UseConstrained(C:constrained(t) where t:subtype(base_class)):int =
    C.Data.ID
<#
-->
<!-- 99-->
```verse
base_class := class:
    ID:int

constrained(t:subtype(base_class)) := class:
    Data:t

# 有效：约束匹配
UseConstrained(C:constrained(t) where t:subtype(base_class)):int =
    C.Data.ID

# 无效：约束缺失或不兼容
UseConstrained(C:constrained(t) where t:type):int =  # 错误
    C.Data.ID
```
<!-- #> -->
<a id="access-specifiers"></a>
### 访问说明符

类通过以下方式支持对成员可见性的细粒度控制
访问说明符：

<!--versetest-->
<!-- 100-->
```verse
game_state := class:
    Score<public> : int = 0                    # 任何人都可以阅读
    var Lives<private> : int = 3               # 只有这个类可以访问
    var Shield<protected> : float = 100.0      # 这个类和子类
    DebugInfo<internal> : string = ""          # 仅相同模块

    # 公共方法——任何人都可以调用
    GetLives<public>() : int = Lives

    # 受保护的方法 - 子类可以重写
    OnLifeLost<protected>() : void = {}

    # 私人帮手 - 仅限此类
    ValidateState<private>() : void = {}
```
访问说明符适用于字段和方法，控制谁
可以读取字段并调用方法。默认可见性是
`internal`，限制对同一模块的访问。这种封装
对于维护类不变性和隐藏实现至关重要
详细信息。

<a id="concrete"></a>
### 具体

`<concrete>` 说明符强制所有字段都具有默认值
值，允许使用空原型进行构造：

<!--versetest-->
<!-- 101-->
```verse
config := class<concrete>:
    MaxPlayers : int = 8
    TimeLimit : float = 300.0
    FriendlyFire : logic = false

# 可以用空原型构建
DefaultConfig := config{}
```
这对于合理的配置类特别有用
所有值都存在默认值。

可以通过编写 `C{}` 来构造具体类 `C`，即使用空原型。

具体类可以有非具体子类。

<a id="unique"></a>
### 唯一

`<unique>` 说明符创建引用的类和接口
每个实例都有不同标识的语义。当上课或
接口被标记为 `<unique>`，实例可以使用
相等运算符（= 和 <>），基于对象的相等
身份而不是字段值。

标有 `<unique>` 的类按标识进行比较，而不是按值进行比较：

<!-- versetest
vector3:=struct{X:float,Y:float,Z:float}
entity := class<unique>:
   Name : string
   Position : vector3
F()<decides>:void={
E1 := entity{Name := "Guard", Position := vector3{X := 0.0, Y := 0.0, Z := 0.0}}
E2 := entity{Name := "Guard", Position := vector3{X := 0.0, Y := 0.0, Z := 0.0}}
E3 := E1

not(E1 = E2 ) # Fails - different instances despite identical field values
E1 = E3  # Succeeds - same instance
}
<#
-->
<!-- 102-->
```verse
entity := class<unique>:
   Name : string
   Position : vector3

E1 := entity{Name := "Guard", Position := vector3{X := 0.0, Y := 0.0, Z := 0.0}}
E2 := entity{Name := "Guard", Position := vector3{X := 0.0, Y := 0.0, Z := 0.0}}
E3 := E1

E1 = E2  # 失败 - 尽管字段值相同但实例不同
E1 = E3  # 成功 - 同一实例
```
<!-- #>-->

如果没有 `<unique>`，则无法比较类实例的相等性
all——语言避免了无意义的比较。使用 `<unique>`，
您可以使用实例作为映射键，将它们存储在集合中，
并执行身份检查，这对于跟踪特定对象至关重要
在他们的一生中。

#### 接口

接口还可以标记为 `<unique>`，这使得所有
实现该接口的类的实例可比较
身份：

<!--versetest-->
<!-- 103-->
```verse
component := interface<unique>:
    Update():void
    Render():void

physics_component := class(component):
    Update<override>():void = {}
    Render<override>():void = {}
```
以及一个用例：

<!--versetest
component := interface<unique>:
    Update():void
    Render():void

physics_component := class(component):
    Update<override>():void = {}
    Render<override>():void = {}
-->
<!-- 1031-->
```verse
# 实例具有可比性，因为组件是唯一的
P1 := physics_component{}
P2 := physics_component{}

P1 <> P2  # true - 不同的情况
P1 = P1   # true - 实例相同
```
`<unique>` 属性通过接口继承传播。如果一个
父接口标记为 `<unique>`，所有子接口和
实现这些接口的类会自动变得具有可比性：

<!--versetest-->
<!-- 104-->
```verse
base_component := interface<unique>:
    Update():void

# 子接口从父接口继承<unique>
advanced_component := interface(base_component):
    AdvancedUpdate():void

# 实现层次结构中任何接口的类都具有可比性
player_component := class(advanced_component):
    Update<override>():void = {}
    AdvancedUpdate<override>():void = {}
```
以及一个用例：

<!--versetest
base_component := interface<unique>:
    Update():void

# Child interface inherits <unique> from parent
advanced_component := interface(base_component):
    AdvancedUpdate():void

# Classes implementing any interface in the hierarchy become comparable
player_component := class(advanced_component):
    Update<override>():void = {}
    AdvancedUpdate<override>():void = {}
-->
<!-- 104-->
```verse
C1 := player_component{}
C2 := player_component{}
C1 <> C2  # true - 由于 base_component 是唯一的，因此可具有比性
```
当一个类实现多个接口时，可比性是
根据任何继承接口是否为 `<unique>` 来确定：

<!--versetest-->
<!-- 105-->
```verse
updateable := interface:  # 不唯一
    Update():void

renderable := interface<unique>:  # 唯一
    Render():void

game_object := class(updateable, renderable):
    Update<override>():void = {}
    Render<override>():void = {}
```
以及一个用例：

<!--versetest
updateable := interface:  # Not unique
    Update():void

renderable := interface<unique>:  # Unique
    Render():void

game_object := class(updateable, renderable):
    Update<override>():void = {}
    Render<override>():void = {}
-->
<!-- 105-->
```verse
# game_object 是可比较的，因为可渲染是唯一的
G1 := game_object{}
G2 := game_object{}
G1 <> G2  # true - 由于可渲染界面且具有可比性
```
即使大多数接口不是唯一的，单个 `<unique>` 接口
层次结构使整个班级具有可比性。

#### 默认值是唯一的

当 `<unique>` 类出现在字段的默认值中时，每个
包含对象接收其自己的唯一实例。这个保证
即使唯一类嵌套在复杂的参数中也适用
类型：

<!--versetest-->
<!-- 106-->
```verse
token := class<unique>:
    ID:int = 0

container := class:
    MyToken:token = token{}
```
以及一个用例：

<!--versetest
token := class<unique>:
    ID:int = 0

container := class:
    MyToken:token = token{}
-->
<!-- 106-->
```verse
C1 := container{}
C2 := container{}
C1.MyToken <> C2.MyToken  # true - 每个容器都有自己的唯一令牌
```
此行为扩展到数组中的 `<unique>` 实例，
选项、元组和映射：

<!--versetest-->
<!-- 107-->
```verse
item := class<unique>{}

# 每个类实例化都会以默认值创建新的唯一实例
with_array := class:
    Items:[]item = array{item{}}

with_optional := class:
    MaybeItem:?item = option{item{}}

with_map := class:
    ItemMap:[int]item = map{0 => item{}}
```
以及一个用例：

<!--versetest
item := class<unique>{}

# Each class instantiation creates fresh unique instances in default values
with_array := class:
    Items:[]item = array{item{}}

with_optional := class:
    MaybeItem:?item = option{item{}}

with_map := class:
    ItemMap:[int]item = map{0 => item{}}
-->
<!-- 107-->
```verse
A := with_array{}
B := with_array{}
A.Items[0] <> B.Items[0]  # true - 不同的唯一实例

C := with_optional{}
D := with_optional{}
if (ItemC := C.MaybeItem?, ItemD := D.MaybeItem?):
    ItemC <> ItemD  # true - 不同的唯一实例
```
当参数类包含唯一的时，同样的原则适用
各自领域的实例：

<!--versetest
entity := class<unique>{}

registry(t:type) := class:
    DefaultEntity:entity = entity{}
    Data:t
<#
-->
<!-- 108-->
```verse
entity := class<unique>{}

registry(t:type) := class:
    DefaultEntity:entity = entity{}
    Data:t
```
<!-- #>-->

<!--versetest
entity := class<unique>{}

registry(t:type) := class:
    DefaultEntity:entity = entity{}
    Data:t
-->
<!-- 1081-->
```verse
R1 := registry(int){Data:=1}
R2 := registry(int){Data:=2}
R1.DefaultEntity <> R2.DefaultEntity  # 真实

R3 := registry(string){Data:="hi"}
R3.DefaultEntity <> R1.DefaultEntity  # true - 即使跨不同类型的参数
```
这种保证确保基于身份的操作仍然存在
可靠。如果您将对象存储在由唯一实例键控的映射中，或者
维护一组唯一的对象，每个容器真正拥有
不同的实例而不是共享引用。语言
防止多个对象可能意外共享的细微错误
相同的身份。

#### 过载解析

标有 `<unique>` 的类型是内置 `comparable` 的子类型
类型。这可能会产生重载歧义：

<!--versetest
# Valid: non-unique interface doesn't conflict with comparable
regular_interface := interface:
    Method():void

Process(A:comparable, B:comparable):void = {}
Process(A:regular_interface, B:regular_interface):void = {}  # OK - no conflict

# Invalid: unique interface conflicts with comparable
assert_semantic_error(3532):
    my_unique_interface := interface<unique>:
        Method():void

    Handle(A:comparable, B:comparable):void = {}
    Handle(A:my_unique_interface, B:my_unique_interface):void = {}  # ERROR - ambiguous!
<#
-->
<!-- 109-->
```verse
# 有效：非唯一接口与可比接口不冲突
regular_interface := interface:
    Method():void

Process(A:comparable, B:comparable):void = {}
Process(A:regular_interface, B:regular_interface):void = {}  # 好的 - 没有冲突

# 无效：唯一接口与可比较接口冲突
unique_interface := interface<unique>:
    Method():void

Handle(A:comparable, B:comparable):void = {}
# Handle(A:unique_interface, B:unique_interface):void = {}  # ERROR - ambiguous!
```
<!-- #>-->

由于 `unique_interface` 是 `comparable` 的子类型，因此两者都会重载
使用 `unique_interface` 参数调用时可能会匹配，从而导致
编译错误。设计重载函数时，请注意
`<unique>` 类型参与 `comparable` 类型层次结构。

#### 用例

`<unique>` 说明符非常适合：

**游戏实体：** 世界上每个实体必须所在的位置
无论当前状态如何均可区分

<!--versetest
vector3:=class<final>{ X:float=0.0; Y:float=0.0; Z:float=0.0 }
entity := class<unique>:
    var Health:int = 100
    var Position:vector3
-->
<!-- 110-->
```verse
#entity := class<unique>:
#    var 健康状况：int = 100
#    var 位置：支持3

# 可以跟踪集合中的特定实体
var ActiveEntities:[entity]logic = map{}
```
**组件接口：**当您需要基于身份的平等时
接口类型

<!--versetest
entity:=class:

component := interface<unique>:
    Owner:entity
    Update():void
-->
<!-- 111-->
```verse
#component := interface<unique>:
#    所有者：实体

# 可以使用接口引用作为映射键
var ComponentRegistry:[component]string = map{}
```
**会话对象：** 身份比当前属性值更重要

<!--versetest
connection_info := class:

player_session := class<unique>:
    PlayerID:string
    var ConnectionTime:float
-->
<!-- 112-->
```verse
#player_session := class<unique>:
#    玩家ID：字符串
#    var 连接时间:float

# 跟踪特定会话
var ActiveSessions:[player_session]connection_info = map{}
```
**资源句柄：**您需要跟踪特定实例的地方
而不是等值

<!--versetest
gpu_resource:=class:

texture_handle := class<unique>:
    ResourceID:int
    FilePath:string
-->
<!-- 113-->
```verse
#texture_handle := class<unique>:
#    资源ID：int
#    文件路径：字符串

# 管理资源生命周期
var LoadedTextures:[texture_handle]gpu_resource = map{}
```
`<unique>` 说明符通过提供来启用这些模式
基于身份的平等语义，使得使用实例成为可能
作为映射键，维护一组唯一的对象，并区分
不同的实例，即使它们的数据相同。

<a id="abstract"></a>
### 抽象

`<abstract>` 说明符标记无法实例化的类
直接——它们仅作为继承的基类而存在。当你
使用 `<abstract>` 声明一个类，您正在创建一个模板
定义子类继承和的结构和行为
实施。

抽象类充当类型的架构基础
层次结构。他们通过抽象方法定义合约
子类必须实现，同时可能提供具体的
子类继承的方法和字段。这创造了一个强大的
代码重用和多态行为的模式。

<!-- versetest-->
<!-- 114-->
```verse
vehicle := class<abstract>:
      Speed():float             # 抽象方法
      MaxPassengers:int = 1

      # 具体方法全车共享
      CanTransport(Count:int)<decides>:void =
          Count <= MaxPassengers

car := class(vehicle):
      Speed<override>():float = 60.0
      MaxPassengers<override>:int = 4

bicycle := class(vehicle):
      Speed<override>():float = 15.0
```
抽象类中的抽象方法没有实现 -
它们是纯粹的声明，确定子类必须做什么
提供。抽象方法创建契约：任何非抽象方法
子类必须重写所有抽象方法，否则代码将无法编译。

<a id="castable"></a>
### 可转换

`<castable>` 说明符支持运行时类型检查和安全
对班级感到沮丧。当类标记为 `<castable>` 时，您
可以使用动态类型测试和强制转换来确定对象是否是
该类或其子类在运行时的实例。

如果没有 `<castable>`，Verse 的类型系统纯粹在编译时运行
时间。 `<castable>` 说明符添加运行时类型信息，
允许代码在期间检查实际对象类型并对其做出反应
执行。这弥合了静态类型安全性和动态类型安全性之间的差距
多态性。

Verse 提供两种形式的类型转换： **易错类型转换**（其中
可能在运行时失败）和**可靠的转换**（在
编译时间）。

**错误的转换**使用括号语法 `Type[Value]` 并返回
可选结果。这些是运行时检查，只有在以下情况下才会成功
value 实际上是目标类型的实例：

<!-- versetest
vector3:=class<final>{ X:float=0.0; Y:float=0.0; Z:float=0.0 }
ToString(:vector3):string=""
-->
<!-- 115-->
```verse
component := class<abstract><castable><allocates>:
    Name:string

physics_component := class<allocates>(component):
    Name<override>:string = "Physics"
    Velocity:vector3

render_component := class<allocates>(component):
    Name<override>:string = "Render"
    Material:string

ProcessComponent(Comp:component):void =
    # 尝试转换为物理组件
    if (PhysicsComp := physics_component[Comp]):
        # 转换成功 -PhysicsComp 的类型为Physics_Component
        Print("Physics component with velocity: {PhysicsComp.Velocity}")
    else if (RenderComp := render_component[Comp]):
        # 转换成功 - RenderComp 的类型为 render_component
        Print("Render component with material: {RenderComp.Material}")
    else:
        # 类型转换均未成功
        Print("Unknown component type")
```
强制转换表达式具有 `<decides>` 效果 - 如果对象
不是目标类型的实例。这自然地与
Verse的失败处理：

<!--versetest
vector3:=class<final><allocates>{ X:float=0.0; Y:float=0.0; Z:float=0.0 }
component := class<abstract><castable><allocates>:
    Name:string

physics_component := class<allocates>(component):
    Name<override>:string = "Physics"
    Velocity:vector3=vector3{}

SomeComponent:component=physics_component{}
UpdatePhysics(:physics_component)<computes>:void={}
-->
<!-- 116-->
```verse
GetPhysicsComponent(Comp:component)<computes><decides>:physics_component =
    # 返回物理组件或失败
    physics_component[Comp]

# 与失败处理一起使用
if (Physics := GetPhysicsComponent[SomeComponent]):
    UpdatePhysics(Physics)
```
**可靠的转换**使用括号语法 `Type(Value)` 并且仅
当编译器可以验证强制转换是否安全时，即当
值类型是目标类型的子类型：


<!--versetest-->
<!-- 117-->
```verse
base := class:
    ID:int

derived := class(base):
    Name:string

GetDerived():derived = derived{ID := 1, Name := "Test"}
```
使用案例：

<!--versetest
base := class:
    ID:int

derived := class(base):
    Name:string

GetDerived():derived = derived{ID := 1, Name := "Test"}
-->
<!-- 1171-->
```verse
# Infallible upcast - 派生是基础的子类型
BaseRef:base = base(GetDerived())  # 永远安全
```
尝试无误的向下转型（从超类型到子类型）是一种
编译错误，因为编译器不能保证安全：

<!--NoCompile-->
<!-- 118-->
```verse
DerivedRef := derived(BaseRef)  # 错误：不是子类型关系
```
#### 可转换和继承

`<castable>` 属性由所有子类继承。当你
将一个类标记为 `<castable>`，每个继承自它的类
也自动变为可铸造：

<!--versetest-->
<!-- 119-->
```verse
base := class<castable>:
    Value:int

child := class(base):
    # 自动可浇铸 - 继承自可浇铸底座
    Name:string

grandchild := class(child):
    # 也可自动施放
    Extra:string

# 可以通过层次结构进行投射
ProcessBase(Instance:base):void =
    if (AsChild := child[Instance]):
        Print("It's a child: {AsChild.Name}")
    if (AsGrandchild := grandchild[Instance]):
        Print("It's a grandchild: {AsGrandchild.Extra}")
```
**重要约束：** 参数类型不能是 `<castable>`。
`<castable>` 说明符启用运行时类型检查（动态
强制转换），但 Verse 在运行时删除类型参数 — 仅删除
存在具体类，而不是特定的参数实例化。
这意味着运行时无法区分 `container(int)`
和 `container(string)`，因此允许对参数进行动态转换
类型是不健全的：

<!--versetest-->
<!-- 120-->
```verse
# 有效：非参数的可转换类
valid_castable := class<castable>:
    Data:int

# 无效：参数类不能被转换
# invalid_castable(t:type) := class<castable>:  # ERROR
#     数据：t
```
然而，非参数类可以是 `<castable>`，即使它
继承自或包含参数类型：

<!--versetest
container(t:type) := class:
    Value:t
int_container := class<castable>(container(int)):
    Extra:string
<#
-->
<!-- 121-->
```verse
container(t:type) := class:
    Value:t

# Valid：参数类型的具体实例化
int_container := class<castable>(container(int)):
    Extra:string
```
<!-- #>-->

<a id="using-castable_subtype"></a>
#### 使用castable_subtype

`castable_subtype` 类型构造函数与 `<castable>` 配合使用
启用类型安全过滤查询和动态类型的类
调度：

<!--versetest
  component<public> := class<abstract><unique><castable>:
      Parent<public>:entity

  entity<public> := class<concrete><unique><transacts><castable>:
      FindDescendantEntities(entity_type:castable_subtype(entity)):[]entity_type = array{}
<#
-->
<!-- 122-->
```verse
  component<public> := class<abstract><unique><castable>:
      Parent<public>:entity

  entity<public> := class<concrete><unique><transacts><castable>:
      FindDescendantEntities(entity_type:castable_subtype(entity)):[]entity_type
```
<!-- #> -->

当调用`FindDescendantEntities(player)`时，函数返回
仅实际是玩家实例或子类的实体
其通过可转换机制在运行时进行验证。类型
参数确保类型安全——返回值具有特定的
您请求的子类型。

#### `castable` 的永久性

一旦使用 `<castable>` 发布了一个类，该决定就变为
永久的。您无法在之后添加或删除 `<castable>` 说明符
发布，因为这样做会破坏依赖于的现有代码
运行时类型检查。执行强制转换的代码会突然失败或
如果可铸件属性发生更改，则行为不正确。

这种持久性是通过版本控制系统强制执行的——尝试
更改已发布类的 `<castable>` 状态将导致
兼容性错误。

<a id="final"></a>
### 最终

`<final>` 说明符防止继承，创建终端
类层次结构中的点。当您用 `<final>` 标记类别时，没有
其他类可以继承它。对于方法，`<final>` 可以防止
在子类中重写，将实现锁定在该级别
层次结构。

标有 `<final>` 的类作为具体实现
不能延长。这对于持久性尤为重要
类，需要 `<final>` 以确保其结构保持不变
序列化稳定：

<!--versetest
player_stats:=struct<persistable>{}

player_profile := class<final><persistable>:
    Username:string = "Player"
    Level:int = 1
    Gold:int = 0

player_data := class<final><persistable>:
    Version:int = 1
    LastLogin:string = ""
    Statistics:player_stats = player_stats{}
<#
-->
<!-- 123-->
```verse
  player_profile := class<final><persistable>:
      Username:string = "Player"
      Level:int = 1
      Gold:int = 0

  player_data := class<final><persistable>:
      Version:int = 1
      LastLogin:string = ""
      Statistics:player_stats = player_stats{}
```
<!-- #>-->

可持久化类的 `<final>` 要求会阻止架构
进化问题。如果子类可以扩展可持久化类，
序列化系统将面临哪些字段的模糊性
持久化以及如何处理多态反序列化。

对于方法，`<final>` 将行为锁定在方法中的特定点
继承链：

<!--versetest
base_entity := class:
    GetName():string = "Entity"

game_object := class(base_entity):
    GetName<override><final>():string = "GameObject"
    # Any subclass of game_object cannot override GetName
<#
-->
<!-- 124-->
```verse
  base_entity := class:
      GetName():string = "Entity"

  game_object := class(base_entity):
      GetName<override><final>():string = "GameObject"
      # game_object 的任何子类都不能覆盖 GetName
```
<!-- #>-->

对于字段，`<final>` 防止通过原型进行修改
建设。当字段标记为 `<final>` 并具有默认值时，
该值已被锁定，在创建实例时无法更改：

<!-- versetest-->
<!-- 1241-->
```verse
foo := class<computes>:
    Val<final>:int = 0
    X:int = 5

# 有效：X可以在构建期间更改
ValidFoo := foo{X := 10}

# 编译错误：无法覆盖最终字段Val
# InvalidFoo := foo{Val := 10}
```
此限制确保最终字段保持其保证
值贯穿对象的整个生命周期。默认的最终字段
值充当每个实例的不可变常量。如果您需要一个
字段在构建过程中可自定义，不要将其标记为
`<final>`。 Final 字段还必须提供默认值 - 您不能
声明一个最终字段而不初始化它。

相关的 `<final_super>` 说明符**不会**阻止进一步
子类化。相反，它保证该类的所有子类
将始终直接继承它 - 不会有中间
插入到 `<final_super>` 类及其类之间的类
继承链上的后代。子类本身可以是
进一步细分：

<!-- NoCompile-->
<!-- 125-->
```verse
component := class<abstract><unique><castable><final_super_base>:
      Parent:entity

physics_component := class<final_super>(component):
      Mass:float = 1.0

# 有效：允许进一步子类化
gravity_component := class(physics_component):
      GravityScale:float = 1.0
```
`<final_super_base>` 标记受限继承树的根。
其目的是与 `GetCastableFinalSuperClass` 配合使用，
在给定的层次结构中查找 `<final_super>` 类
实例。这使得您需要的组件架构成为可能
在运行时识别组件的“类别”：

<!-- NoCompile-->
<!-- 126-->
```verse
#            基本类型<可转换>
#               /         \
#  a_class<final_super> w_class
#         |                  |
#      b_class x_class<final_super>
#         |                  |
#      c_class y_class

# GetCastableFinalSuperClass[base_type, c_class{}]
# 返回 a_class — base_type 下的 <final_super> 祖先
```
这种设计在组件架构中特别有价值
在层次结构中您需要一个稳定的“类别”类
运行时系统可以依赖，同时仍然允许进一步
专业低于它。

<a id="persistable"></a>
### 可持久化

`<persistable>` 说明符标记可以保存和
跨游戏会话恢复，实现玩家的永久存储
进度、成就和游戏状态。该说明符转换
将短暂的游戏玩法转变为持久的进程，奠定基础
进行有意义的玩家投资。

持久性通过模块范围的 `weak_map(player, t)` 进行
变量，其中 `t` 是任何可持久化类型。  这些特殊的映射
自动与后端存储同步——当玩家加入时，
他们的数据负载；当他们离开或数据发生变化时，它会保存。的
系统处理所有序列化、网络传输和存储
管理透明。

<!--versetest
player:=string
-->
<!-- 127-->
```verse
player_inventory := class<final><persistable>:
      Gold:int = 0
      Items:[]string = array{}
      UnlockedAreas:[]string = array{}

# 该变量自动在会话中保留
SavedInventories : weak_map(player, player_inventory) = map{}
```
`<persistable>` 说明符强制执行严格的结构要求
以保证跨版本的数据完整性。类必须是 `<final>`
因为继承会使序列化模式变得复杂。他们
不能包含 `var` 字段，甚至保留不变性保证
在持久存储中。它们不能是 `<unique>`，因为基于身份
平等无法在序列化中生存。这些限制确保
您今天保存的内容可以在明天、下个月或者
明年。

<a id="interfaces"></a>
## 接口

接口定义类可以实现的契约，指定
实现类必须的数据和行为
提供。与许多仅提供接口的传统语言不同
声明方法签名，Verse 接口是丰富的契约，
可以包含字段、默认方法实现，甚至自定义
访问器逻辑。

接口可以声明方法签名，提供默认值
实现，并定义数据成员：

<!--versetest-->
<!-- 128-->
```verse
damageable := interface:
    # 抽象方法 - 实现类必须提供
    TakeDamage(Amount:int)<transacts>:void

    # 默认实现的方法
    GetHealth()<computes>:int = 100

    # 数据成员 - 实现类继承或必须提供
    MaxHealth:int = 100

    IsAlive()<computes>:logic = logic{GetHealth() > 0}

healable := interface:
    Heal(Amount:int):void
    GetMaxHealth():int
```
接口建立可以纯粹抽象的契约（方法
仅签名），部分具体（一些默认实现），
或完全实现（类继承的完整行为）。任意
实现接口的类必须提供以下实现
抽象方法，但继承具体实现和默认值
字段值。

### 实现接口

类通过继承并提供接口来实现接口
需要时具体实施：

<!--versetest
healable:=interface:
    TakeDamage(Amount:int)<transacts>:void ={}
    GetHealth():int = 0
    Heal(Amount:int)<transacts>:void ={}

damageable:=interface{}
-->
<!-- 129-->
```verse
character := class(damageable, healable):
    var Health : int = 100
    MaxHealth : int = 100

    TakeDamage<override>(Amount:int)<transacts>:void =
        set Health = Max(0, Health - Amount)

    GetHealth<override>()<reads>:int = Health

    Heal<override>(Amount:int)<transacts>:void =
        set Health = Min(MaxHealth, Health + Amount)
```
一个类可以实现多个接口，有效实现
行为契约和数据的多重继承
规格。这比单一类提供了更多的灵活性
继承同时保持类型安全。

### 接口字段

接口可以声明实现类必须的数据成员
提供或继承。这些字段可以是不可变的或可变的，
并且可能包括默认值：

<!--versetest-->
<!-- 130-->
```verse
# 与各种字段类型的接口
entity_properties := interface:
    # 具有默认值的不可变字段 - 类继承此值
    EntityID:int = 0

    # 具有默认值的可变字段
    var Health:float = 100.0

    # 没有默认值的字段 - 类必须提供一个值
    Name:string

    # 可覆盖的字段
    MaxHealth:float = 100.0

player_entity := class(entity_properties):
    # 必须提供名称（界面中无默认值）
    Name<override>:string = "Player"

    # 可以覆盖以更改默认值
    MaxHealth<override>:float = 150.0

    # 继承 EntityID 和 Health 的默认值
```
当接口字段有默认值时，实现类
自动继承该默认值，除非他们覆盖它。领域
没有默认值必须由实现类提供或
通过施工参数。

### 默认实现

接口可以提供完整的方法实现
实现类自动继承：

<!--versetest-->
<!-- 131-->
```verse
animated := interface:
    var CurrentFrame:int = 0
    TotalFrames:int = 10

    # 接口提供的具体实现
    NextFrame()<transacts><decides>:void =
        set CurrentFrame = Mod[(CurrentFrame + 1),TotalFrames] or 0

    # 可以访问接口字段
    ProgressPercent()<reads><decides>:rational =
        CurrentFrame / TotalFrames

sprite := class(animated):
    TotalFrames<override>:int = 20
    # 自动继承NextFrame和ProgressPercent实现
```
类继承这些实现而不进行修改，允许
提供可重用行为的接口。实现类可以
如果这些方法需要专门的行为，则重写它们，但是
接口提供了一个工作默认值。

### 覆盖成员

类可以重写接口中的字段和方法
提供专门的实现：

<!--versetest-->
<!-- 132-->
```verse
base_stats := interface:
    BaseHealth:int = 100

    CalculateFinalHealth():int = BaseHealth

warrior := class(base_stats):
    # 使用不同的默认值覆盖字段
    BaseHealth<override>:int = 150

    # 专门计算的重写方法
    CalculateFinalHealth<override>():int =
        BaseHealth * 2  # 战士获得双倍生命值

mage := class(base_stats):
    BaseHealth<override>:int = 75

    CalculateFinalHealth<override>():int =
        BaseHealth + MagicBonus

    MagicBonus:int = 25
```
字段覆盖可以提供不同的默认值或专门用于
亚型。方法重写替换接口的实现
完全。所有覆盖必须保持类型兼容性——字段可以
只能用子类型覆盖，并且方法签名必须匹配
正是如此。

### 多接口共享

Verse 界面比许多其他语言更宽松 —
他们可以声明数据字段，提供具体的方法实现，
并且一个类可以实现多个接口，即使它们共享
成员姓名。这种设计避免了全局要求的摩擦
所有接口的唯一名称。实际应用中，独立接口
作者自然可以使用相同的名称（`Enable`、`Disable`、
`Power`、`Update`），并要求每个接口使用不同的
名称会造成人为的命名冲突，规模很差——
特别是当接口与子接口形成深层层次结构时
对于专门的变体。

当一个类实现多个声明字段或接口的接口时
具有相同名称的方法，您可以使用限定名称
消除歧义：

<!--versetest-->
<!-- 133-->
```verse
magical := interface:
    Power:int = 50
    GetPowerLevel()<computes>:int = Power

physical := interface:
    Power:int = 75
    GetPowerLevel()<computes>:int = Power * 2

hybrid := class(magical, physical):
    UseHybridPowers():void =
       MagicPower := (magical:)Power         # 获得魔法的力量
       PhysicalPower := (physical:)Power     # 获取物理力量
       MagicLevel := (magical:)GetPowerLevel()
       PhysicalLevel := (physical:)GetPowerLevel()
```
限定名称语法 `(InterfaceName:)MemberName` 指定哪个
您正在访问的接口的成员。每个接口都维护自己的
该字段的实例，允许该类支持两个合约
同时不冲突。

### 接口层次结构

接口可以扩展其他接口，创建层次结构
结合数据和行为要求的合约：

<!--NoCompile-->
<!-- 134-->
```verse
combatant := interface(damageable, healable):
    var AttackPower:int = 10

    Attack(Target:damageable):void =
        Target.TakeDamage(AttackPower)

    GetAttackPower():int = AttackPower

boss := interface(combatant):
    Phase:int = 1

    UseSpecialAbility():void
    GetPhase():int = Phase
```
实现 `boss` 的类继承了所有字段和方法
整个层次结构 - `boss`、`combatant`、`damageable` 和
`healable`。钻石继承（接口被继承
通过多个路径）完全支持，字段正确
合并，因此每个字段在实现类中仅存在一次。

**重要：** 类不能直接继承同一个接口
多次（例如，`class(interface1, interface1)` 是一个错误），
但可以通过钻石继承间接继承。这意味着
即使 `interface2` 和 `interface2` 都有效，`class(interface2, interface3)` 也有效
`interface3`继承自相同的基础接口。

### 带有访问器的字段

接口可以使用自定义 getter 和 setter 逻辑定义字段，
将复杂的行为封装在简单的字段访问语法后面：

<!--versetest
subscribable_property := interface:
    # External field with accessor methods
    var Value<getter(GetValue)><setter(SetValue)>:int = external{}

    # Internal storage
    var Storage:int = 100

    # Getter adds computation
    GetValue(:accessor):int = Storage + 10

    # Setter adds validation
    SetValue(:accessor, NewValue:int):void =
        if (NewValue >= 0):
            set Storage = NewValue

tracked_value := class(subscribable_property):

UseTrackedValue():void =
    Object := tracked_value{}

    # Uses getter - returns 110 (Storage + 10)
    Current := Object.Value

    # Uses setter - validates and updates Storage
    set Object.Value = 150
<#
-->
<!-- 135-->
```verse
subscribable_property := interface:
    # 具有访问器方法的外部字段
    var Value<getter(GetValue)><setter(SetValue)>:int = external{}

    # 内部存储
    var Storage:int = 100

    # Getter 增加计算
    GetValue(:accessor):int = Storage + 10

    # Setter添加验证
    SetValue(:accessor, NewValue:int):void =
        if (NewValue >= 0):
            set Storage = NewValue

tracked_value := class(subscribable_property):

UseTrackedValue():void =
    Object := tracked_value{}

    # 使用 getter - 返回 110（存储 + 10）
    Current := Object.Value

    # 使用setter - 验证和更新存储
    set Object.Value = 150
```
<!-- #>-->

`external{}` 关键字表示该字段没有直接存储 - 所有
访问通过访问器方法进行。这种模式非常强大
实现属性更改通知、验证、计算
属性，以及其他需要围绕字段访问逻辑的场景。

**重要：** 接口中定义的具有访问器的字段不能
在实现类时被覆盖。访问器的实现是
由接口固定。
