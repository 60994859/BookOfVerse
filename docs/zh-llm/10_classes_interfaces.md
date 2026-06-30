# 类与接口

类与接口是 Verse 面向对象编程的构建块，它们通过继承、多态和基于接口的契约实现了丰富的类型层次结构。类提供了带有字段、方法和单继承的面向对象编程，使你能够对具有共享行为和专门化实现的复杂游戏实体层次结构进行建模。接口定义了类必须履行的契约，促进了松散耦合，并实现了行为规约的多重继承。

类与接口共同构成了一个强大的系统，用于对游戏实体、组件和系统进行建模，既包含"is-a"关系（通过类继承），也包含"can-do"契约（通过接口实现）。

先来探索类，然后深入了解接口以及它们如何相互补充。

## 类

类是 Verse 中面向对象编程的骨干。类作为创建具有共同属性和行为的对象的蓝图。当你定义一个类时，你是在创建一个新类型，它将数据（字段）和操作该数据的方法（方法）捆绑在一起，将相关功能封装成一个内聚的单元。

类定义发生在模块作用域。你不能在另一个类、结构体、接口或函数内部定义类。类是顶级类型定义，它们建立了类型系统的结构：

<!--versetest-->
<!-- 01-->
```verse
# Valid: class at module scope
MyModule := module:
    entity := class:
        ID:int

# Invalid: class inside another class
# outer := class:
#     inner := class:  # ERROR: classes must be at module scope
#         Value:int
```

最简单的类形式是将相关数据组合在一起。考虑在你的游戏中建模一个角色：

<!--versetest-->
<!-- 02-->
```verse
character := class:
    Name : string
    var Health : int = 100
    var Level : int = 1
    MaxHealth : int = 100
```

这个类定义确立了几个重要概念。没有 `var` 修饰符的字段在构造后是不可变的——一旦你创建了一个具有特定名称的角色，该名称就不能更改。标记为 `var` 的字段是可变的，可以在对象创建后修改（关于 `var` 和 `set` 的详细信息，请参阅[可变性](05_mutability.md)）。默认值提供了合理的起始点，使对象构造更加方便，同时确保对象从有效状态开始。

### 对象构造

创建类的实例涉及通过原型表达式为其字段指定值：

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
Villager := character{Name := "Martha"}  # default values for unspecified fields
```

原型语法使用命名参数，使构造显式且自文档化。任何具有默认值的字段都可以在原型中省略，此时将使用默认值。没有默认值的字段必须指定，确保对象始终被完全初始化。字段可以按任意顺序传递给原型。

### 方法

当你添加操作类数据的方法时，类才真正变得强大：

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
        set Health = MaxHealth  # Full heal on level up
```

方法可以访问类的所有字段，并可以修改可变字段。它们封装了类对象应该如何行为的逻辑，确保状态变化以可控、可预测的方式进行。

非抽象类中的所有方法都必须有实现。与接口（可以声明抽象方法）不同，具体类中没有实现的方法声明是错误的：

<!--versetest-->
<!-- 05-->
```verse
# Valid: method with implementation
valid_class := class:
    Compute():int = 42

# Invalid: method without implementation in concrete class
# invalid_class := class:
#     Compute():int  # ERROR: needs implementation
```

### 初始化块

类可以在其主体中包含 `block` 子句，这些子句在创建实例时执行。这些块运行超出简单字段赋值的初始化代码，允许你在构造期间执行设置逻辑、验证或副作用：

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
        # This executes when an instance is created
        Print("Creating entity with ID: {ID}")
        set CreationTime = GetCurrentTime()

# Entity := logged_entity{ID := 42}
# Prints: "Creating entity with ID: 42"
```
<!-- #>-->

块子句可以访问类的所有字段，包括 `Self`，并且可以修改可变字段。它们按照在类定义中出现的顺序执行：

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
        set Step2 = Step1 + 5  # Can access earlier fields
        set Step3 = Step2 * 2

# Instance := multi_step_init{}
# Instance.Step1 = 10, Step2 = 15, Step3 = 30
```

**继承时的执行顺序：** 当一个类继承自另一个类时，Verse VM 以子类优先于父类的顺序执行块，而 BP VM 使用父类优先于子类的顺序。对于可移植代码，应避免依赖继承层次结构中块的执行顺序。

**为什么使用块而不是构造函数？** 块子句可以访问 `Self` 和类的所有字段，而构造函数函数无法访问 `Self`。这使得块成为需要引用正在构造的对象的初始化逻辑的天然选择——例如将 `Self` 注册到全局系统或从多个字段计算派生值。

此外，字段默认值不能使用分歧调用——可能无法完成的调用。这意味着你不能写：

<!--NoCompile-->
<!-- 06a-->
```verse
# ERROR V3582: Divergent calls cannot be used to define data-members
bar := class:
    Foo:foo = MakeFoo()
```

相反，你应该给字段一个简单的默认值，并将初始化逻辑移到块中：

<!--NoCompile-->
<!-- 06b-->
```verse
bar := class:
    var Foo:foo = foo{}

    block:
        set Foo = MakeFoo()  # Block can call divergent functions
```

**块子句的约束：**

- 块不能包含失败（`<decides>`）操作
- 块不能调用挂起（`<suspends>`）函数
- 块可以使用 `defer` 语句，这些语句在块退出时执行
- 块子句仅在类中允许，不能在接口、结构体或模块中使用

块子句对于以下情况特别有用：

- 记录对象创建日志
- 在初始化期间计算派生值
- 将对象注册到全局系统
- 执行需要 `Self` 或分歧调用的初始化

### 原型中的 Let 子句

原型表达式（用于构造类和结构体实例）可以包含 `let` 子句，引入局部变量绑定。这些绑定对于计算多个字段初始化器使用的中间值非常有用，可以避免重复：

<!--NoCompile-->
<!-- 06c-->
```verse
MkWord8<constructor>(I:int)<decides><transacts> := Word8:
    let:
        MaxU8:int = Int[Pow(2.0, 8.0)] - 1 or Impossible("MkWord8")
    B := 0 <= I and I <= MaxU8
```

`let` 子句引入的绑定（上面示例中的 `MaxU8`）对同一原型中后续的字段初始化器可见。与 `block` 子句不同，`let` 子句仅限于变量声明——`let` 内部不允许使用独立表达式。

### Self

在类方法中，`Self` 是一个特殊关键字，指向类的当前实例。每个方法调用都有自己的 `Self`，指向调用该方法的特定对象。

你可以在方法体中以多种方式使用 `Self`：

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
        # Using Self to pass the whole object
        LogCharacterAction(Self, "announced")


    SetOption(Key:string, Value:string):character =
        set Config[Key] = Value
        Self  # Return this instance for method chaining


    SetName(NewName:string):void =
       set Self.Name = NewName	  # Set the name of this instance
	   Self.Announce()            # Call a method of this instance
```

你可以在创建嵌套对象时捕获 `Self`：

<!--versetest-->
<!-- 12-->
```verse
container := class:
    ID:int

    CreateChild():child_with_parent =
        child_with_parent{Parent := Self}  # Capture this instance

child_with_parent := class:
    Parent:container

# C := container{ID := 42}
# Child := C.CreateChild()
# Child.Parent.ID = 42  # Child stores reference to C
```

### 继承

类支持单继承，允许你创建现有类的专门化版本。这创建了一种"is-a"关系，其中子类是父类的更具体类型：

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
```
<!-- #>-->

继承创建了一个类型层次结构，其中 `player` 同时也是 `character`，而 `character` 同时也是 `entity`。这意味着你可以在任何期望 `character` 或 `entity` 的地方使用 `player` 对象，从而实现多态行为。

**继承的重要约束：**

1. **仅单类继承：** 一个类最多只能继承自一个其他类，但可以实现多个接口。不支持多重类继承：

<!--versetest-->
<!-- 14-->
```verse
base1 := class:
    Value1:int

base2 := class:
    Value2:int

# Valid: inherit from one class and multiple interfaces
interface1 := interface:
    Method1():void

interface2 := interface:
    Method2():void

derived := class<abstract>(base1, interface1, interface2):
    # Valid: one class, multiple interfaces
    Method1<override>():void = {}
    Method2<override>():void = {}

# Invalid: cannot inherit from multiple classes
# invalid := class(base1, base2):  # ERROR
```

2. **不允许遮蔽数据成员：** 子类不能声明与父类同名的字段。这防止了歧义并确保清晰的数据所有权：

<!--versetest-->
<!-- 15-->
```verse
base := class:
    Value:int

# Invalid: cannot shadow parent's field
# derived := class(base):
#     Value:int  # ERROR: shadowing base.Value
```

3. **不允许更改方法签名：** 覆盖方法时，必须使用完全相同的签名。更改参数类型或返回类型会造成遮蔽错误：

<!--versetest-->
<!-- 16-->
```verse
base := class:
    Compute():int = 42

# Invalid: different return type
# derived := class(base):
#     Compute():float = 3.14  # ERROR: signature doesn't match
```

要覆盖一个方法，请使用带有匹配签名的 `<override>` 说明符。

### Super

在子类中，你可以使用 `super` 关键字来引用父类类型。这主要用于访问父类的实现或构造父类实例：

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
        # Create a superclass instance to call its method
        super{ID := ID, Name := Name}.Display()
        Print("Health: {Health}")
```

`super` 关键字代表父类类型本身。当你写 `super{...}` 时，你正在创建一个具有指定字段值的父类实例。这使你能够委托给父类行为，同时添加子类特有的功能。

在覆盖方法中，你可以使用 `(super:)` 语法调用父类的实现。这是在添加或修改行为时调用父类方法实现的主要方式：

<!--versetest-->
<!-- 18-->
```verse
base := class:
    Method():void =
        Print("Base implementation")

derived := class(base):
    Method<override>():void =
        # Call parent implementation first
        (super:)Method()
        Print("Derived implementation")

# Creates instance and calls Method()
# derived{}.Method()
# Output:
# Base implementation
# Derived implementation

```

`(super:)` 语法显式调用当前方法的父类版本。当你只需要调用父类方法时，这比使用 `super{...}` 构造父类实例更简洁、更高效。

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
        # Update position logic here

character := class(entity):
    var Stamina:float = 100.0

    Move<override>(Delta:vector3):void =
        # Call parent movement logic
        (super:)Move(Delta)
        # Add character-specific behavior
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
```
<!-- #>-->

**通过父类方法的虚分发：**

当父类方法调用其他方法时，虚分发仍然基于实际对象类型进行。这意味着即使通过 `(super:)` 调用，`Self` 仍然绑定到派生实例：

<!--versetest-->
<!-- 21-->
```verse
base := class:
    # Virtual method that can be overridden
    GetValue()<computes>:int = 10

    # Parent method that uses GetValue
    ComputeDouble()<computes>:int =
        2 * GetValue()  # Calls derived GetValue if overridden

derived := class(base):
    # Override GetValue to return different value
    GetValue<override>()<computes>:int = 20

    # Override ComputeDouble to call parent, but GetValue dispatch is virtual
    ComputeDouble<override>()<computes>:int =
        # Calls base.ComputeDouble, which calls derived.GetValue!
        (super:)ComputeDouble()

# derived{}.ComputeDouble()  # Returns 40, not 20
```

在这个示例中，即使 `ComputeDouble` 调用的是父类实现，其中的 `GetValue()` 调用也使用了虚分发，并调用了派生版本。

**带有重载方法：**

`(super:)` 语法与重载方法配合使用，调用父类的同一重载版本：

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
        (super:)Process(X)  # Calls parent's int overload
        Print("Derived int: {X}")

    Process<override>(S:string):void =
        (super:)Process(S)  # Calls parent's string overload
        Print("Derived string: {S}")
```

**返回类型协变：**

当使用 `(super:)` 覆盖方法时，返回类型可以是父类返回类型的子类型（协变返回类型）：

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
    # Override with more specific return type
    Create<override>():derived_type =
        # Can still call parent even with different return type
        Parent := (super:)Create()
        derived_type{Name := Parent.Name, Value := 42}
```

### 方法覆盖

子类可以覆盖父类中定义的方法以提供专门化行为：

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
    OnUpdate<public>() : void = {}  # Default no-op implementation

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

覆盖机制确保根据对象的实际类型（而非持有该对象的变量类型）调用正确的方法实现。这是面向对象编程中多态行为的基础。

### 构造函数函数

类没有传统意义上的构造函数方法（如其他面向对象语言中常见的那样）。相反，Verse 提供了三种对象构造方式，每种适用于不同的需求：

- **原型表达式** — 用于简单情况的直接字段初始化。直接了当，无需额外定义。
- **块子句** — 类主体中的初始化代码，在每次构造时运行。可以访问 `Self` 和所有字段，非常适合注册对象、计算派生值或调用无法出现在字段默认值中的分歧函数。
- **构造函数函数** — 使用 `<constructor>` 注解，这些是一等函数，可以验证输入、委托给其他构造函数（包括父类构造函数）、支持重载，并可以作为值传递。它们是最强大的选项，对于子类构造函数需要初始化父类字段的继承层次结构至关重要。

这些方式可以组合使用：构造函数函数返回一个原型表达式，其中可以包含 `let` 和 `block` 子句，而类主体也可以有自己的 `block` 子句，无论使用哪个构造函数都会执行。

对于只需要设置字段值的简单情况，直接使用原型表达式：

<!--versetest-->
<!-- 25-->
```verse
player := class:
    Name:string
    var Health:int = 100
    Level:int = 1

# Direct construction with archetype
# Hero := player{Name := "Aldric", Health := 150, Level := 5}
```

当你需要验证、计算或复杂的初始化逻辑时，使用带有 `<constructor>` 注解的构造函数函数：

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

以下是调用此构造函数的示例：

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
Hero := MakePlayer("Aldric", 5) # Call constructor function 
```

构造函数函数是返回类实例的普通函数，但 `<constructor>` 注解启用了特殊能力，例如委托给其他构造函数。从普通代码调用构造函数函数时，只需使用函数名——`<constructor>` 注解仅出现在定义中。

构造函数函数可以具有控制其行为的效果。常用的效果包括 `<computes>`、`<allocates>` 和 `<transacts>`。一个特别有用的效果是 `<decides>`，它允许构造函数在不满足前置条件时失败：

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

以下是使用带失败处理的经过验证的构造函数的示例：

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
# Constructor can fail - use with failure syntax
if (Player := MakeValidPlayer["Hero", 5]):
    # Construction succeeded
    AddPlayer(Player)
else:
    # Construction failed - level out of range
```

构造函数函数不能使用 `<suspends>` 效果。构造必须同步完成以保持对象一致性。

### 重载构造函数

你可以提供多个具有不同参数签名的构造函数函数，从而实现灵活的对象创建：

<!--versetest
vector3:=class<final>{ X:float=0.0; Y:float=0.0; Z:float=0.0 }
-->
<!-- 28-->
```verse
entity := class:
    Name:string
    var Health:int = 100
    Position:vector3

# Constructor with all parameters
MakeEntity<constructor>(Name:string, Health:int, Position:vector3) := entity:
    Name := Name
    Health := Health
    Position := Position

# Constructor with defaults
MakeEntity<constructor>(Name:string, Position:vector3) := entity:
    Name := Name
    Health := 100
    Position := Position

# Constructor for origin placement
MakeEntity<constructor>(Name:string) := entity:
    Name := Name
    Health := 100
    Position := vector3{X := 0.0, Y := 0.0, Z := 0.0}

# Each overload can be called based on arguments
# Enemy1 := MakeEntity("Goblin", 50, SpawnPoint)
# Enemy2 := MakeEntity("Guard", PatrolPoint)
# NPC := MakeEntity("Shopkeeper")
```

### 委托构造函数

构造函数函数可以委托给其他构造函数，从而实现代码复用和构造函数链式调用。这对于子类构造函数需要初始化父类字段的继承层次结构尤为重要。

当从子类委托给父类构造函数时，你必须先初始化子类字段，然后使用原型中的限定 `<constructor>` 语法调用父类构造函数：

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

# Subclass constructor delegates to parent constructor
MakeCharacter<constructor>(Name:string, Class:string, Level:int) := character:
    # Initialize subclass fields first
    Class := Class
    Level := Level
    # Then delegate to parent constructor
    MakeEntity<constructor>(Name, Level * 100)

Hero := MakeCharacter("Aldric", "Warrior", 5)
```
<!-- #>-->

构造函数函数也可以转发到同一个类的其他构造函数：

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

# Primary constructor
MakePlayer<constructor>(Name:string, Score:int) := player:
    Name := Name
    Score := Score

# Convenience constructor forwards to primary
MakeNewPlayer<constructor>(Name:string) := player:
    # Delegate to another constructor of the same class
    MakePlayer<constructor>(Name, 0)
```
<!-- #>-->

以下是调用构造函数的示例：

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

当委托给同一个类的构造函数时，委托将替换所有字段初始化——你在委托之前初始化的任何字段都将被忽略。当委托给父类构造函数时，你的子类字段初始化将被保留，父类构造函数初始化父类字段。

### 执行顺序

理解执行顺序对于正确的初始化至关重要：

1. **原型表达式：** 字段初始化器按照在原型中编写的顺序执行
2. **委托构造函数：** 子类字段先被初始化，然后父类构造函数运行
3. **类主体块：** 当使用直接原型构造时，类定义中的块在字段初始化之前执行

对于委托给父类的构造函数：

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
    # This executes first
    DerivedValue := Derived
    # Then parent constructor executes
    MakeBase<constructor>(Base)
```
<!-- #>-->

以下是展示执行顺序的示例：

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
# Prints: "Base constructor"
# Results in: derived{BaseValue := 10, DerivedValue := 20}
Instance := MakeDerived(10, 20)
```

对于具有可变字段的类，初始化设置了在整个对象生命周期中可以更改的起始值。不可变字段必须在构造期间初始化，之后不能修改。这种区别使得构造阶段对于建立将在对象整个存在期间保持不变的不变量至关重要。

## 影子命名与限定

Verse 有严格的规定来防止名称歧义并保持代码清晰。理解这些规则和限定语法对于使用继承层次结构、多个接口和嵌套模块至关重要。

在大多数上下文中，你**不能重新定义**已在外层作用域中存在的名称。这适用于函数、变量、类、接口和模块：

<!--versetest-->
<!-- 32-->
```verse
# ERROR: Function at module level shadows class method
# F(X:int):int = X + 1
# c := class:
#     F(X:int):int = X + 2  # ERROR - shadows outer F
```

这个禁止规定延伸到各种上下文：

<!--NoCompile-->
<!-- 33-->
```verse
# ERROR: Cannot shadow classes
something := class {}

M := module:
    something := class {}  # ERROR

# ERROR: Cannot shadow variables
Value:int = 1

M := module:
     Value:int = 2        # ERROR

# ERROR: Cannot shadow data members
c := class { A:int }

A():void = {}             # ERROR - order doesn't matter

# ERROR: Module and function cannot share name

Id():void = {}
Id := module {}           # ERROR
```

影子禁止规定**与定义顺序无关**——无论外层名称是在内层作用域之前还是之后定义，都不允许。

要在不同上下文中定义同名方法，请使用**限定名称**，语法为 `(ClassName:)MethodName`：

<!--versetest-->
<!-- 34-->
```verse
# Class with qualified method of same name
c := class:
   (c:)F(X:int):int = X + 2

# Module-level function
F(X:int):int = X + 1

# Call the module-level function
F(10)  # Returns 11

# Call the class method
c{}.F(10)  # Returns 12

# Explicit qualification (optional here)
c{}.(c:)F(10)  # Returns 12
```

`(c:)` 限定符表明这个 `F` 是在 `c` 类上下文中专门定义的，将其与模块级的 `F` 区分开来。这使得同名名称可以共存而不产生影子错误。

### 同名方法

使用限定符，你可以定义与继承方法同名的*新方法*，在同一个类中创建多个不同的方法：

<!--versetest-->
<!-- 35-->
```verse
c := class<abstract> { F(X:int):int }

d := class(c):
    F<override>(X:int):int = X + 1

e := class(d):
    (e:)F(X:int):int = X + 2 # NEW method with same name, not an override

# e now contains BOTH methods:
#    - (d:)F inherited from d
#    - (e:)F newly defined in e
```

使用上述定义：

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
E.(c:)F(10)  # Returns 11 (inherited from d's override)
E.(e:)F(10)  # Returns 12 (new method in e)
```

关键区别：

- 不带限定符的 `F<override>`：覆盖继承的 `F`
- 不带 `<override>` 的 `(e:)F`：定义了一个特定于 `e` 的**新** `F`

这使得一个类可以拥有多个同名方法，通过它们的限定符来区分，每个方法在类层次结构中服务于不同的目的。

### `(super:)` 限定

`(super:)` 限定符与限定方法名配合使用，来调用父类的方法实现：

<!--versetest-->
<!-- 36-->
```verse
i := interface { F(X:int):int }

ci := class(i):
    (i:)F<override>(X:int):int = X + 1
    (ci:)F(X:int):int = X + 2

dci := class(ci):
    # Override both inherited methods, calling super implementations
    (i:)F<override>(X:int):int = 100 + (super:)F(X)
    (ci:)F<override>(X:int):int = 200 + (super:)F(X)

```

以及使用场景：

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
DCI.(i:)F(10)  # Returns 111 (100 + ci's 11)
DCI.(ci:)F(10)  # Returns 212 (200 + ci's 12)
```

在限定方法中，`(super:)F(X)` 调用父类对该同一限定方法的实现。这使你能够独立地扩展多个方法变体的行为。

### 接口冲突

当实现多个具有同名方法的接口时，限定符可以消除歧义，指明你在实现哪个接口的方法：

<!--versetest-->
<!-- 37-->
```verse
i := interface:
    B(X:int):int

j := interface:
    B(X:int):int

collision := class(i, j):
    # Implement both B methods separately
    (i:)B<override>(X:int):int = 20 + X
    (j:)B<override>(X:int):int = 30 + X
```

以及使用场景：

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
Obj.(i:)B(1)  # Returns 21
Obj.(j:)B(1)  # Returns 31
```

没有限定符，编译器无法确定你在实现哪个接口的方法，从而导致错误。限定符使你的意图显式化。

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
    (k:)C(X:int):int  # k redefines C

multi := class(j, k):
    A<override>(X:int):int = 10 + X
    B<override>(X:int):int = 20 + X
    # Must implement C from both inheritance paths
    (i:)C<override>(X:int):int = 30 + X
    (k:)C<override>(X:int):int = 40 + X
```

使用场景：

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
Obj.(i:)C(1)  # Returns 31
Obj.(k:)C(1)  # Returns 41
```

当一个接口使用限定符 `(k:)C` 从父接口重新定义方法时，实现类必须为这两个变体提供独立的实现。

### 嵌套模块限定

模块可以嵌套，深度限定的名称通过整个层次结构引用成员：

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

以及使用场景：

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
# using { Top.M }
# using { Top.M.M }

# Access with full qualification
(Top.M:)F(0)          # Returns 10
(Top.M.M:)F(0)        # Returns 100

# Access via path
Top.M.F(1)            # Returns 11
Top.M.M.F(1)          # Returns 101
```

嵌套模块可以具有相同的简单名称（例如，都是 `M`），当使用其完整路径限定时，允许层次化组织而不会产生命名冲突。

### 限制

限定符只能在适当的上下文中使用。你不能对局部变量使用类限定符：

<!--NoCompile-->
<!-- 40-->
```verse
C := class:
    f():void =
        (C:)X:int = 0  # ERROR - wrong context
```

某些限定符不受支持。对局部变量不允许使用函数限定符：

<!--NoCompile-->
<!-- 41-->
```verse
C := class:
    f():void =
        (C.f:)X:int = 0  # ERROR - unsupported pattern
```

类似地，使用模块函数路径作为限定符也不受支持：

<!--NoCompile-->
<!-- 42-->
```verse
M := module:
    f():void =
        (M.f:)X:int = 0  # ERROR
```

局部变量不能遮蔽类成员：

<!--NoCompile-->
<!-- 43-->
```verse
A := class:
    I:int
    F(X:int):void =
        I:int = 5  # ERROR - shadows member I
```

目前不存在 `(local:)` 限定符来消除歧义，因此这种模式不受支持。你必须为局部变量和成员使用不同的名称。

## 参数化类

参数化类，也称为泛型类，允许你定义可以与任何类型一起工作的类。不必为整数、字符串、玩家以及每种其他类型编写单独的容器类，你可以编写一个接受类型参数的参数化类。

参数化类在其定义中接受一个或多个类型参数：

<!--versetest
# Simple container that holds a single value
container(t:type) := class:
    Value:t
<#
-->
<!-- 46-->
```verse
# Simple container that holds a single value
container(t:type) := class:
    Value:t
```
<!-- #>-->

以下是用不同类型实例化此参数化类的示例：

<!--versetest
container(t:type) := class:
    Value:t

player := class:
    Name:string
    var Health:int = 100
-->
<!-- 461-->
```verse
# Can be instantiated with any type
IntContainer := container(int){Value := 42}
StringContainer := container(string){Value := "hello"}
PlayerContainer := container(player){Value := player{Name := "Hero", Health := 100}}
```

语法 `container(t:type)` 定义了一个由类型 `t` 参数化的类。在类定义中，`t` 可以出现在任何具体类型可能出现的位置——在字段声明、方法签名或返回类型中。

**多个类型参数：**

类可以接受多个类型参数：

<!--NoCompile-->
<!-- 47-->
```verse
pair(t:type, u:type) := class:
    First:t
    Second:u
```

以下是使用参数化 pair 类的示例：

<!--versetest
pair(t:type, u:type) := class:
    First:t
    Second:u
-->
<!-- 471-->
```verse
# Different types for each parameter
Coordinate := pair(int, int){First := 10, Second := 20}
NamedValue := pair(string, float){First := "score", Second := 99.5}
```

**方法中的类型参数：**

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

方法会自动从类定义中获知类型参数——你不必在方法签名中重新声明。

### 实例化与类型同一性

当你使用特定的类型参数实例化一个参数化类时，Verse 会创建一个具体类型。关键是，**使用相同类型参数的多次实例化产生相同的类型**：

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

# These are the same type
Type1 := container(int)
Type2 := container(int)
Type3 := container(int)

# All three are equal - they're the same type
```
<!-- #>-->

这种类型同一性在整个程序中都有保证：

<!--versetest
container(t:type) := class:
    Value:t
-->
<!-- 50-->
```verse
# Create instances
C1 := container(int){Value := 1}
C2 := container(int){Value := 2}

# Both have the same type: container(int)
# Type checking treats them identically
```

实例化过程是**确定性的且经过记忆化的**。第一次写 `container(int)` 时，Verse 会生成一个具体类型。之后每次使用 `container(int)` 都引用同一个类型，而不是一个新副本。

这对于以下方面很重要：

- **类型兼容性**：两个 `container(int)` 的值可以互换使用
- **内存效率**：不创建重复的类型定义
- **语义正确性**：相同的类型参数始终意味着相同的类型

虽然相同的类型参数总是产生相同的类型，但不同的类型参数会产生不同且不兼容的类型：

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

以下示例展示不同的实例化会创建不同的类型：

<!--versetest
container(t:type) := class:
    Value:t
-->
<!-- 521-->
```verse
IntContainer := container(int){Value := 42}
StringContainer := container(string){Value := "text"}

# These are different types and cannot be mixed
# IntContainer = StringContainer  # Type error!
```

`container(int)` 和 `container(string)` 是完全不同的类型，没有子类型关系。它们碰巧具有相同的结构（都从 `container` 定义而来），但这并不使它们兼容。

虽然参数化类的不同实例化是不同的类型，但 Verse 允许某些实例化根据**变型**在需要其他实例化的地方使用。变型决定了何时可以在期望 `parametric_class(supertype)` 的地方使用 `parametric_class(subtype)`（或相反）。

参数化类型的变型取决于类型参数在类定义中的使用方式：

#### 协变

当类型参数只出现在**返回位置**（方法返回类型、被读取的字段类型）时，参数化类在该参数上是**协变的**（关于变型的详细信息，请参阅[类型](11_types.md#understanding-subtyping)）。这意味着实例化遵循与其类型参数相同的子类型方向：

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
```
<!-- #>-->

以下是演示协变的示例：

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
# Covariance allows subtype → supertype
PlayerProducer:producer(player) = producer(player){Value := player{ID := 1, Name := "Alice"}}
EntityProducer:producer(entity) = PlayerProducer  # Valid!

Result := ProcessProducer(PlayerProducer)  # Works!
```

**为什么这是安全的：** 如果你期望从一个生产者那里获得 `entity`，接收一个 `player`（它是 `entity` 的子类型）总是有效的——`player` 拥有 `entity` 的所有属性。

**方向：** `producer(player)` → `producer(entity)` ✓（与子类型方向一致）

#### 逆变

当类型参数只出现在**参数位置**（方法参数被消费）时，参数化类在该参数上是**逆变的**（关于变型的详细信息，请参阅[类型](11_types.md#understanding-subtyping)）。这意味着实例化遵循**相反**的子类型方向：

<!--versetest-->
<!-- 54-->
```verse
entity := class:
    ID:int

player := class(entity):
    Name:string

# Contravariant class - type parameter only in parameter position
consumer(t:type) := class:
    Process(Item:t):void = {}  # Accepts t - contravariant position
```

以及使用场景：

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
# Contravariance allows supertype → subtype
EntityConsumer:consumer(entity) = consumer(entity){}
PlayerConsumer:consumer(player) = EntityConsumer  # Valid!

# Can use consumer(entity) where consumer(player) expected
ProcessPlayers(C:consumer(player)):void =
    C.Process(player{ID := 1, Name := "Bob"})

ProcessPlayers(EntityConsumer)                    # Works!
```

**为什么这是安全的：** 如果你有一个接受任何 `entity` 的函数，它当然可以处理更具体的 `player` 类型。一个 `consumer(entity)` 可以消费任何 `consumer(player)` 可以消费的东西，甚至更多。

**方向：** `consumer(entity)` → `consumer(player)` ✓（与子类型方向相反）

#### 不变

当类型参数同时出现在**参数和返回位置**时，参数化类在该参数上是**不变的**。不同实例化之间不存在子类型关系：

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

# Invariant class - type parameter in both positions
transformer(t:type) := class:
    Transform(Input:t):t = Input  # Both parameter and return
```
<!-- #>-->

以下示例展示不同实例化之间不存在变型关系：

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
# No variance - cannot convert in either direction
EntityTransformer:transformer(entity) = transformer(entity){}
PlayerTransformer:transformer(player) = transformer(player){}

# Invalid: Cannot use one where the other is expected
# X:transformer(entity) = PlayerTransformer  # ERROR 3509
# Y:transformer(player) = EntityTransformer  # ERROR 3509
```

**为什么这是必要的：** 如果 `transformer(player)` 可以用作 `transformer(entity)`，你可以将任何 `entity` 传递给它的 `Transform` 方法，而该方法期望的是 `player` 类型。这将是不安全的。

**方向：** 任何方向都不允许转换

#### 双变

当类型参数没有在任何方法签名中使用（仅在私有实现细节中或根本没有使用）时，参数化类是**双变的**。任何实例化都可以转换为任何其他实例：

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

# Bivariant class - type parameter not used in public interface
container(t:type) := class:
    DoSomething():void = {}  # Doesn't use t at all
```
<!-- #>-->

以下示例展示双变类允许双向转换：

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
# Bivariant allows conversion in both directions
EntityContainer:container(entity) = container(entity){}
PlayerContainer:container(player) = container(player){}

# Both directions work
X:container(entity) = PlayerContainer  # Valid
Y:container(player) = EntityContainer  # Also valid
```

**为什么这样可行：** 由于类型参数不影响可观察的行为，这些实例化是可以互换的。

### 递归参数化类型

参数化类可以在其字段类型中引用自身，从而实现递归的泛型数据结构，如链表、树和图。关键要求是自引用使用**相同的类型参数**——这是 Verse 允许的唯一递归形式。它能工作，因为编译器可以在单次传递中解析类型结构：`list_node(int)` 包含一个 `?list_node(int)`，后者又包含一个 `?list_node(int)`，依此类推。可选类型（`?`）提供了在运行时终止递归的基础情况。

以下是一个构建为递归参数化类的泛型链表：

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
```
<!-- #>-->

以下是使用该链表的示例：

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
# Usage
IntList := list_node(int){
    Value := 1
    Next := option{list_node(int){
        Value := 2
        Next := false
    }}
}
```

**不允许：直接类型别名递归**

你不能定义一个直接别名为包含自身的结构化类型的参数化类型：

<!--versetest-->
<!-- 71-->
```verse
# Invalid: Direct array recursion
# t(u:type) := []t(u)  # ERROR 3502

# Invalid: Direct map recursion
# t(u:type) := [int]t(u)  # ERROR 3502

# Invalid: Direct optional recursion
# t(u:type) := ?t(u)  # ERROR 3502

# Invalid: Direct function recursion
# t(u:type) := u->t(u)  # ERROR 3502
# t(u:type) := t(u)->u  # ERROR 3502
```

这些会失败，因为它们创建了无限的类型扩展——编译器无法确定类型的实际结构。

**有效的替代方案：** 将递归引用包装在类中。例如，每个节点持有一个子节点列表的树是一个递归参数化类型——每个 `nested_list(t)` 包含一个 `nested_list(t)` 数组：

<!-- NoCompile-->
<!-- 72-->
```verse
# Valid: Indirect recursion through class
nested_list(t:type) := class:
    Items:[]nested_list(t)  # OK - wrapped in class
```

以下是构造一个包含两个子节点的树的示例：

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

当参数化类型使用**不同的类型参数**引用自身时，就会发生多态递归：

<!--NoCompile-->
<!-- 73-->
```verse
# Invalid: Type parameter changes
# my_type(t:type) := class:
#     Next:my_type(?t)  # ERROR 3509 - ?t is different from t

# Invalid: Alternating type parameters
# bi_list(t:type, u:type) := class:
#     Value:t
#     Next:?bi_list(u, t)  # ERROR 3509 - parameters swapped
```

**为什么不允许：** 多态递归使类型推断不可判定，并且可能创建无限复杂的类型。当你实例化 `my_type(int)` 时，它需要 `my_type(?int)`，后者又需要 `my_type(??int)`，如此无限循环。

**当前限制：** 虽然多态递归在某些类型系统中理论上是合理的，但 Verse 目前不支持它，以保持类型检查的可处理性。

**不允许：互递归**

多个参数化类型之间的互递归不受支持：

<!--versetest-->
<!-- 74-->
```verse
# Invalid: Mutual recursion
# t1(t:type) := class:
#     Next:?t2(t)  # References t2
#
# t2(t:type) := class:
#     Next:?t1(t)  # References t1
```

**为什么不允许：** 与多态递归类似，互递归使类型推断复杂化，并且可能创建编译器难以解析的循环依赖。

**解决方案：** 合并为单一类型：

<!-- NoCompile-->
<!-- 75-->
```verse
# Valid: Single type with multiple cases
node_type := enum:
    TypeA
    TypeB

combined_node(t:type) := class:
    Type:node_type
    Value:t
    Next:?combined_node(t)
```

**不允许：继承递归**

你不能从类型变量继承或通过参数化类型创建递归继承：

<!--versetest-->
<!-- 76-->
```verse
# Invalid: Inheriting from parametric self
# t(u:type) := class(t(u)){}  # ERROR 3590

# Invalid: Inheriting from type variable
# inherits_from_variable(t:type) := class(t){}  # ERROR 3590
```

**为什么不允许：** 继承需要知道父类的结构，但使用参数化递归时，该结构在被定义之前就是自引用的。

### 参数化接口

虽然参数化类获得了大部分关注，但接口也可以是参数化的，从而实现与任何类型一起工作的抽象契约：

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
# Generic equality interface
equivalence(t:type, u:type) := interface:
    Equal(Left:t, Right:u)<transacts><decides>:t

# Generic collection interface
collection_ifc(t:type) := interface:
    Add(Item:t)<transacts>:void
    Remove(Item:t)<transacts><decides>:void
    Has(Item:t)<reads>:logic
```
<!-- #>-->

类通过为参数提供具体类型来实现参数化接口：

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

# Implement with specific types
int_equivalence := class(equivalence(int, comparable)):
    Equal<override>(Left:int, Right:comparable)<transacts><decides>:int =
        Left = Right

# Or with type parameters matching the class
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
# Usage
Eq := comparable_equivalence(int){}
Eq.Equal[5, 5]  # Succeeds
```

参数化接口遵循与参数化类相同的变型规则：

<!-- NoCompile-->
<!-- 82-->
```verse
entity := class:
    ID:int

player := class(entity):
    Name:string

# Covariant interface - returns t
producer_interface(t:type) := interface:
    Produce():t

player_producer := class(producer_interface(player)):
    Produce<override>():player = player{ID := 1, Name := "Test"}
```

以下是协变子类型化的示例：

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
# Covariant subtyping works
EntityProducer:producer_interface(entity) = player_producer{}
```

你可以从参数化接口创建专门化（非参数化）接口：

<!-- NoCompile-->
<!-- 83-->
```verse
generic_handler(t:type) := interface:
    Handle(Item:t):void

# Specialize to a concrete type
int_handler := interface(generic_handler(int)):
    # Inherits Handle(Item:int):void
    # Can add more methods here

int_processor := class(int_handler):
    Handle<override>(Item:int):void =
        Print("Handling: {Item}")
```

以下是在类型转换中使用专门化接口的示例：

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
# Can use in casts now (specialized interfaces are non-parametric)
Base := int_processor{}
if (Handler := int_handler[Base]):
    Handler.Handle(42)
```

#### 多个类型参数

接口可以有多个具有独立变型的类型参数：

<!-- NoCompile-->
<!-- 84-->
```verse
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
```

使用示例：

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
# Variance allows flexible usage
C:converter_interface(player, entity) = player_to_entity{}
```

### 高级参数化类型

#### 效果

参数化类型可以具有适用于所有实例化的效果说明符：

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
# Parametric class with effects
async_container(t:type) := class<computes>:
    Property:t

# All instantiations inherit the effect
X:async_container(int) = async_container(int){Property := 1}  # <computes> effect

# Multiple effects
transactional_container(t:type) := class<transacts>:
    Property:t

# Constructor inherits effects
# Y:transactional_container(int) = transactional_container(int){Property := 2}
```
<!-- #> -->

**允许的效果：**

- `<computes>` - 允许非终止计算
- `<transacts>` - 参与事务
- `<reads>` - 读取可变状态
- `<writes>` - 写入可变状态
- `<allocates>` - 分配资源

**不允许：**

- `<decides>` - 可以失败
- `<suspends>` - 可以挂起执行
- `<converges>` - `<converges>` 效果保证函数终止（参见[效果](13_effects.md)章节）。参数化类不能使用它，因为实例化参数化类型可能涉及任意计算——编译器无法保证构造 `my_type(t)` 对所有可能的 `t` 都会终止。

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
# Effect on parametric type propagates to constructor
my_type(t:type) := class<computes>:
    Property:t

# This requires <computes> in the context
CreateInstance()<computes>:my_type(int) =
    my_type(int){Property := 1}
```
<!-- #> -->

效果成为类型契约的一部分——所有构造或使用实例的代码都必须考虑这些效果。

#### 别名

你可以创建简化复杂参数化类型表达式的类型别名：

<!--versetest-->
<!-- 92-->
```verse
# Alias for map type
string_map(t:type) := [string]t

# Use the alias
PlayerScores:string_map(int) = map{
    "Alice" => 100,
    "Bob" => 95
}

# Alias for optional array
optional_array(t:type) := []?t

# Simplifies type signatures
FilterValid(Items:optional_array(int)):[]int =
    for (Item : Items; Value := Item?):
        Value
```

**结构化类型别名：**

<!--versetest-->
<!-- 94-->
```verse
# Function type aliases
transformer(input:type, output:type) := input -> output
predicate(t:type) := t -> logic

# Tuple type aliases
pair(t:type, u:type) := tuple(t, u)
triple(t:type) := tuple(t, t, t)

# Use in signatures
ApplyTransform(T:transformer(int, string), Value:int):string =
    T(Value)

CheckCondition(P:predicate(int), Value:int):logic =
    P(Value)
```

类型别名提高了复杂泛型类型的可读性和可维护性。

#### 高级类型约束

除了基本的 `subtype` 约束之外，参数化类型还支持专门的约束：

**子类型约束：**

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
# Constrain to subtype of a class
bounded_container(t:subtype(entity)) := class:
    Value:t

    GetID():int = Value.ID  # Can access entity members

# Valid: player is subtype of entity
# PlayerContainer := bounded_container(player){}

# Invalid: int is not subtype of entity
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
# Requires castable subtype
dynamic_handler(t:castable_subtype(component)) := class:
    Handle(Item:component):void =
        if (Typed := t[Item]):
            # Typed has the specific subtype
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
# Constraints propagate through function calls
wrapper(t:subtype(comparable)) := class:
    Data:t

Process(W:wrapper(t) where t:subtype(comparable))<computes><decides>:void =
    # Compiler knows t is comparable here
    W.Data = W.Data
```
<!-- #> -->

当定义使用参数化类型的参数化函数时，约束必须是兼容的：

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

# Valid: Constraint matches
UseConstrained(C:constrained(t) where t:subtype(base_class)):int =
    C.Data.ID

# Invalid: Missing or incompatible constraint
UseConstrained(C:constrained(t) where t:type):int =  # ERROR 
    C.Data.ID
```
<!-- #> -->

### 访问说明符

类支持通过访问说明符对成员可见性进行细粒度控制：

<!--versetest-->
<!-- 100-->
```verse
game_state := class:
    Score<public> : int = 0                    # Anyone can read
    var Lives<private> : int = 3               # Only this class can access
    var Shield<protected> : float = 100.0      # This class and subclasses
    DebugInfo<internal> : string = ""          # Same module only

    # Public method - anyone can call
    GetLives<public>() : int = Lives

    # Protected method - subclasses can override
    OnLifeLost<protected>() : void = {}

    # Private helper - only this class
    ValidateState<private>() : void = {}
```

访问说明符适用于字段和方法，控制谁可以读取字段和调用方法。默认可见性是 `internal`，限制为同一模块的访问。这种封装对于维护类不变性和隐藏实现细节至关重要。

### 具体类

`<concrete>` 说明符强制所有字段都有默认值，从而允许使用空原型进行构造：

<!--versetest-->
<!-- 101-->
```verse
config := class<concrete>:
    MaxPlayers : int = 8
    TimeLimit : float = 300.0
    FriendlyFire : logic = false

# Can construct with empty archetype
DefaultConfig := config{}
```

这对于所有值都存在合理默认值的配置类特别有用。

具体类 `C` 可以通过写 `C{}` 来构造，即使用空原型。

具体类可以有非具体的子类。

### 唯一类

`<unique>` 说明符创建具有引用语义的类和接口，其中每个实例具有不同的身份。当类或接口被标记为 `<unique>` 时，实例可以使用相等运算符（= 和 <>）进行比较，相等性基于对象身份而非字段值。

标记为 `<unique>` 的类按身份而非按值进行比较：

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

E1 = E2  # Fails - different instances despite identical field values
E1 = E3  # Succeeds - same instance
```
<!-- #>-->

没有 `<unique>` 时，类实例根本无法进行相等性比较——语言会防止无意义的比较。有了 `<unique>`，你可以将实例用作映射键、存储到集合中以及执行身份检查，这对于在整个生命周期中跟踪特定对象至关重要。

#### 接口

接口也可以标记为 `<unique>`，这使得实现该接口的所有类的实例都按身份进行比较：

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

以及使用场景：

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
# Instances are comparable because component is unique
P1 := physics_component{}
P2 := physics_component{}

P1 <> P2  # true - different instances
P1 = P1   # true - same instance
```

`<unique>` 属性通过接口继承传播。如果父接口标记为 `<unique>`，所有子接口以及实现这些接口的类自动变得可比较：

<!--versetest-->
<!-- 104-->
```verse
base_component := interface<unique>:
    Update():void

# Child interface inherits <unique> from parent
advanced_component := interface(base_component):
    AdvancedUpdate():void

# Classes implementing any interface in the hierarchy become comparable
player_component := class(advanced_component):
    Update<override>():void = {}
    AdvancedUpdate<override>():void = {}
```

以及使用场景：

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
C1 <> C2  # true - comparable due to base_component being unique
```

当一个类实现多个接口时，可比较性由继承的接口中是否有 ANY 一个是 `<unique>` 来决定：

<!--versetest-->
<!-- 105-->
```verse
updateable := interface:  # Not unique
    Update():void

renderable := interface<unique>:  # Unique
    Render():void

game_object := class(updateable, renderable):
    Update<override>():void = {}
    Render<override>():void = {}
```

以及使用场景：

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
# game_object is comparable because renderable is unique
G1 := game_object{}
G2 := game_object{}
G1 <> G2  # true - comparable due to renderable interface
```

即使大多数接口是非唯一的，只要层次结构中有一个 `<unique>` 接口，就能使整个类可比较。

#### 默认值中的唯一类

当 `<unique>` 类出现在字段的默认值中时，每个包含对象都会收到自己独立的实例。即使唯一类嵌套在复杂的参数化类型中，此保证也适用：

<!--versetest-->
<!-- 106-->
```verse
token := class<unique>:
    ID:int = 0

container := class:
    MyToken:token = token{}
```

以及使用场景：

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
C1.MyToken <> C2.MyToken  # true - each container has its own unique token
```

此行为扩展到数组、可选类型、元组和映射中的 `<unique>` 实例：

<!--versetest-->
<!-- 107-->
```verse
item := class<unique>{}

# Each class instantiation creates fresh unique instances in default values
with_array := class:
    Items:[]item = array{item{}}

with_optional := class:
    MaybeItem:?item = option{item{}}

with_map := class:
    ItemMap:[int]item = map{0 => item{}}
```

以及使用场景：

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
A.Items[0] <> B.Items[0]  # true - different unique instances

C := with_optional{}
D := with_optional{}
if (ItemC := C.MaybeItem?, ItemD := D.MaybeItem?):
    ItemC <> ItemD  # true - different unique instances
```

同样的原则适用于参数化类在其字段中包含唯一实例时：

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
R1.DefaultEntity <> R2.DefaultEntity  # true

R3 := registry(string){Data:="hi"}
R3.DefaultEntity <> R1.DefaultEntity  # true - even across different type parameters
```

此保证确保基于身份的操作保持可靠。如果你将对象存储在以唯一实例为键的映射中，或者维护唯一对象的集合，每个容器真正拥有独立的实例，而不是共享引用。语言防止了多个对象可能意外共享同一身份这种微妙的错误。

#### 重载解析

标记为 `<unique>` 的类型是内置 `comparable` 类型的子类型。这可能会造成重载歧义：

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
# Valid: non-unique interface doesn't conflict with comparable
regular_interface := interface:
    Method():void

Process(A:comparable, B:comparable):void = {}
Process(A:regular_interface, B:regular_interface):void = {}  # OK - no conflict

# Invalid: unique interface conflicts with comparable
unique_interface := interface<unique>:
    Method():void

Handle(A:comparable, B:comparable):void = {}
# Handle(A:unique_interface, B:unique_interface):void = {}  # ERROR - ambiguous!
```
<!-- #>-->

由于 `unique_interface` 是 `comparable` 的子类型，当使用 `unique_interface` 参数调用时，两个重载都可能匹配，导致编译错误。在设计重载函数时，请注意 `<unique>` 类型参与了 `comparable` 类型层次结构。

#### 使用场景

`<unique>` 说明符非常适合：

**游戏实体：** 世界中的每个实体必须是可区分的，无论当前状态如何

<!--versetest
vector3:=class<final>{ X:float=0.0; Y:float=0.0; Z:float=0.0 }
entity := class<unique>:
    var Health:int = 100
    var Position:vector3
-->
<!-- 110-->
```verse
#entity := class<unique>:
#    var Health:int = 100
#    var Position:vector3

# Can track specific entities in collections
var ActiveEntities:[entity]logic = map{}
```

**组件接口：** 当你需要接口类型的基于身份的相等性时

<!--versetest
entity:=class:

component := interface<unique>:
    Owner:entity
    Update():void
-->
<!-- 111-->
```verse
#component := interface<unique>:
#    Owner:entity

# Can use interface references as map keys
var ComponentRegistry:[component]string = map{}
```

**会话对象：** 当身份比当前属性值更重要时

<!--versetest
connection_info := class:

player_session := class<unique>:
    PlayerID:string
    var ConnectionTime:float
-->
<!-- 112-->
```verse
#player_session := class<unique>:
#    PlayerID:string
#    var ConnectionTime:float

# Track specific sessions
var ActiveSessions:[player_session]connection_info = map{}
```

**资源句柄：** 当你需要跟踪特定实例而非等价值时

<!--versetest
gpu_resource:=class:

texture_handle := class<unique>:
    ResourceID:int
    FilePath:string
-->
<!-- 113-->
```verse
#texture_handle := class<unique>:
#    ResourceID:int
#    FilePath:string

# Manage resource lifecycle
var LoadedTextures:[texture_handle]gpu_resource = map{}
```

`<unique>` 说明符通过提供基于身份的相等性语义来实现这些模式，使得可以将实例用作映射键、维护唯一对象集合，以及区分不同实例（即使它们的数据相同）。

### 抽象类

`<abstract>` 说明符标记那些不能直接实例化的类——它们仅作为用于继承的基类存在。当你声明带有 `<abstract>` 的类时，你正在创建一个模板，定义子类继承和实现的结构与行为。

抽象类作为类型层次结构中的架构基础。它们通过子类必须实现的抽象方法来定义契约，同时可能提供子类继承的具体方法和字段。这为代码复用和多态行为创建了一个强大的模式。

<!-- versetest-->
<!-- 114-->
```verse
vehicle := class<abstract>:
      Speed():float             # Abstract method
      MaxPassengers:int = 1

      # Concrete method all vehicles share
      CanTransport(Count:int)<decides>:void =
          Count <= MaxPassengers

car := class(vehicle):
      Speed<override>():float = 60.0
      MaxPassengers<override>:int = 4

bicycle := class(vehicle):
      Speed<override>():float = 15.0
```

抽象类中的抽象方法没有实现——它们是纯粹的声明，确立了子类必须提供什么。抽象方法创建了一个契约：任何非抽象子类必须覆盖所有抽象方法，否则代码将无法编译。

### 可转换类

`<castable>` 说明符支持运行时的类型检查和安全的向下转换。当类被标记为 `<castable>` 时，你可以使用动态类型测试和转换来确定运行时对象是否是该类或其子类的实例。

没有 `<castable>` 时，Verse 的类型系统纯粹在编译时运行。`<castable>` 说明符增加了运行时类型信息，使得代码可以在执行期间检查和响应实际的对象类型。这弥合了静态类型安全与动态多态之间的差距。

Verse 提供了两种形式的类型转换：**可失败转换**（可能在运行时失败）和**不可失败转换**（在编译时验证）。

**可失败转换**使用方括号语法 `Type[Value]` 并返回一个可选结果。这些是运行时检查，仅当值实际是目标类型的实例时才成功：

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
    # Attempt to cast to physics_component
    if (PhysicsComp := physics_component[Comp]):
        # Cast succeeded - PhysicsComp has type physics_component
        Print("Physics component with velocity: {PhysicsComp.Velocity}")
    else if (RenderComp := render_component[Comp]):
        # Cast succeeded - RenderComp has type render_component
        Print("Render component with material: {RenderComp.Material}")
    else:
        # Neither cast succeeded
        Print("Unknown component type")
```

转换表达式具有 `<decides>` 效果——如果对象不是目标类型的实例，则失败。这与 Verse 的失败处理自然集成：

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
    # Returns physics_component or fails
    physics_component[Comp]

# Use with failure handling
if (Physics := GetPhysicsComponent[SomeComponent]):
    UpdatePhysics(Physics)
```

**不可失败转换**使用括号语法 `Type(Value)`，仅在编译器可以验证转换安全时才能工作——即值类型是目标类型的子类型：

<!--versetest-->
<!-- 117-->
```verse
base := class:
    ID:int

derived := class(base):
    Name:string

GetDerived():derived = derived{ID := 1, Name := "Test"}
```

使用场景：

<!--versetest
base := class:
    ID:int

derived := class(base):
    Name:string

GetDerived():derived = derived{ID := 1, Name := "Test"}
-->
<!-- 1171-->
```verse
# Infallible upcast - derived is a subtype of base
BaseRef:base = base(GetDerived())  # Always safe
```

尝试不可失败的向下转换（从父类型到子类型）是编译时错误，因为编译器无法保证安全：

<!--NoCompile-->
<!-- 118-->
```verse
DerivedRef := derived(BaseRef)  # ERROR: not a subtype relationship
```

#### 可转换与继承

`<castable>` 属性由所有子类继承。当你将类标记为 `<castable>` 时，每个继承自它的类自动变得可转换：

<!--versetest-->
<!-- 119-->
```verse
base := class<castable>:
    Value:int

child := class(base):
    # Automatically castable - inherits from castable base
    Name:string

grandchild := class(child):
    # Also automatically castable
    Extra:string

# Can cast through the hierarchy
ProcessBase(Instance:base):void =
    if (AsChild := child[Instance]):
        Print("It's a child: {AsChild.Name}")
    if (AsGrandchild := grandchild[Instance]):
        Print("It's a grandchild: {AsGrandchild.Extra}")
```

**重要约束：** 参数化类型不能是 `<castable>`。`<castable>` 说明符启用了运行时类型检查（动态转换），但 Verse 在运行时擦除类型参数——只有具体类存在，而非特定的参数化实例化。这意味着运行时无法区分 `container(int)` 和 `container(string)`，因此允许对参数化类型进行动态转换是不安全的：

<!--versetest-->
<!-- 120-->
```verse
# Valid: non-parametric castable class
valid_castable := class<castable>:
    Data:int

# Invalid: parametric classes cannot be castable
# invalid_castable(t:type) := class<castable>:  # ERROR
#     Data:t
```

然而，非参数化类即使继承自或包含参数化类型，也可以是 `<castable>`：

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

# Valid: concrete instantiation of parametric type
int_container := class<castable>(container(int)):
    Extra:string
```
<!-- #>-->

#### 使用 castable_subtype

`castable_subtype` 类型构造函数与 `<castable>` 类配合使用，实现类型安全的过滤查询和动态类型分发：

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

当你调用 `FindDescendantEntities(player)` 时，该函数仅返回实际是 `player` 实例或其子类的实体，通过可转换机制在运行时验证。类型参数确保了类型安全——返回的值具有你请求的特定子类型。

#### 可转换的持久性

一旦类以 `<castable>` 发布，这个决定就是永久的。你不能在发布后添加或移除 `<castable>` 说明符，因为这样做会破坏依赖运行时类型检查的现有代码。如果可转换属性发生变化，执行转换的代码会突然失败或行为不正确。

这种持久性是通过版本控制系统强制执行的——尝试更改已发布类的 `<castable>` 状态将导致兼容性错误。

### 最终类

`<final>` 说明符阻止继承，在类层次结构中创建一个终止点。当你将类标记为 `<final>` 时，没有其他类可以继承自它。对于方法，`<final>` 阻止在子类中覆盖，将实现锁定在层次结构的该级别。

标记为 `<final>` 的类作为不能扩展的具体实现。这对于需要 `<final>` 以确保其结构保持稳定的可持久化类尤其重要：

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

可持久化类的 `<final>` 要求防止了模式演变问题。如果子类可以扩展可持久化类，序列化系统将面临持久化哪些字段以及如何处理多态反序列化的歧义。

对于方法，`<final>` 将行为锁定在继承链的特定点：

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
      # Any subclass of game_object cannot override GetName
```
<!-- #>-->

对于字段，`<final>` 阻止通过原型构造进行修改。当字段被标记为 `<final>` 并具有默认值时，该值被锁定，在创建实例时无法更改：

<!-- versetest-->
<!-- 1241-->
```verse
foo := class<computes>:
    Val<final>:int = 0
    X:int = 5

# Valid: X can be changed during construction
ValidFoo := foo{X := 10}

# COMPILE ERROR: Cannot override final field Val
# InvalidFoo := foo{Val := 10}
```

此限制确保最终字段在其整个生命周期中保持其保证值。具有默认值的最终字段作为每个实例的不可变常量。如果你需要字段在构造期间可定制，不要将其标记为 `<final>`。最终字段还必须提供默认值——你不能声明未初始化的最终字段。

相关的 `<final_super>` 说明符并**不**阻止进一步的子类化。相反，它保证该类的所有子类将始终直接继承自它——在 `<final_super>` 类与其后代之间的继承链中不会有中间类插入。子类本身可以被进一步子类化：

<!-- NoCompile-->
<!-- 125-->
```verse
component := class<abstract><unique><castable><final_super_base>:
      Parent:entity

physics_component := class<final_super>(component):
      Mass:float = 1.0

# Valid: further subclassing is allowed
gravity_component := class(physics_component):
      GravityScale:float = 1.0
```

`<final_super_base>` 标记一个受限继承树的根。其目的是与 `GetCastableFinalSuperClass` 配合使用，后者为给定实例查找层次结构中的 `<final_super>` 类。这使得组件架构成为可能，你需要在运行时识别组件的"类别"：

<!-- NoCompile-->
<!-- 126-->
```verse
#            base_type<castable>
#               /         \
#  a_class<final_super>   w_class
#         |                  |
#      b_class            x_class<final_super>
#         |                  |
#      c_class            y_class

# GetCastableFinalSuperClass[base_type, c_class{}]
# returns a_class — the <final_super> ancestor under base_type
```

这种设计在需要运行时系统可以依赖的层次结构中稳定的"类别"类，同时仍然允许其下进一步专门化的组件架构中特别有价值。

### 可持久化

`<persistable>` 说明符标记可以跨游戏会话保存和恢复的类型，实现玩家进度、成就和游戏状态的永久存储。此说明符将短暂的玩法转化为持久的进展，为有意义的玩家投入奠定基础。

持久化通过模块作用域的 `weak_map(player, t)` 变量工作，其中 `t` 是任何可持久化类型。这些特殊映射自动与后端存储同步——当玩家加入时，他们的数据加载；当他们离开或数据变化时，数据保存。系统透明地处理所有序列化、网络传输和存储管理。

<!--versetest
player:=string
-->
<!-- 127-->
```verse
player_inventory := class<final><persistable>:
      Gold:int = 0
      Items:[]string = array{}
      UnlockedAreas:[]string = array{}

# This variable automatically persists across sessions
SavedInventories : weak_map(player, player_inventory) = map{}
```

`<persistable>` 说明符强制执行严格的结构要求，以保证跨版本的数据完整性。类必须是 `<final>` 的，因为继承会使序列化模式复杂化。它们不能包含 `var` 字段，即使在持久化存储中也保持不可变性保证。它们不能是 `<unique>` 的，因为基于身份的相等性在序列化后无法保持。这些约束确保你今天保存的内容可以在明天、下个月或明年可靠地加载。

## 接口

接口定义了类可以实现（implement）的契约，规定了实现类必须提供的数据和行为。与许多传统语言中接口只声明方法签名不同，Verse 的接口是丰富的契约，可以包含字段、默认方法实现，甚至自定义访问器逻辑。

接口可以声明方法签名、提供默认实现以及定义数据成员：

<!--versetest-->
<!-- 128-->
```verse
damageable := interface:
    # Abstract method - implementing classes must provide
    TakeDamage(Amount:int)<transacts>:void

    # Method with default implementation
    GetHealth()<computes>:int = 100

    # Data member - implementing classes inherit or must provide
    MaxHealth:int = 100

    IsAlive()<computes>:logic = logic{GetHealth() > 0}

healable := interface:
    Heal(Amount:int):void
    GetMaxHealth():int
```

接口建立的契约可以是纯抽象的（仅方法签名）、部分具体的（一些默认实现）、或完全实现的（类继承的完整行为）。任何实现接口的类必须为抽象方法提供实现，但会继承具体实现和默认字段值。

### 实现接口

类通过继承接口并在需要的地方提供具体实现来实现接口：

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

一个类可以实现多个接口，从而有效地实现行为契约和数据规约的多重继承。这提供了比单类继承更多的灵活性，同时保持了类型安全。

### 接口字段

接口可以声明实现类必须提供或继承的数据成员。这些字段可以是不可变的或可变的，并可以包含默认值：

<!--versetest-->
<!-- 130-->
```verse
# Interface with various field types
entity_properties := interface:
    # Immutable field with default - classes inherit this value
    EntityID:int = 0

    # Mutable field with default
    var Health:float = 100.0

    # Field without default - classes must provide a value
    Name:string

    # Field that can be overridden
    MaxHealth:float = 100.0

player_entity := class(entity_properties):
    # Must provide Name (no default in interface)
    Name<override>:string = "Player"

    # Can override to change default
    MaxHealth<override>:float = 150.0

    # Inherits EntityID and Health with their defaults
```

当接口字段具有默认值时，实现类自动继承该默认值，除非它们覆盖它。没有默认值的字段必须由实现类或通过构造参数提供。

### 默认实现

接口可以提供完整的、实现类自动继承的方法实现：

<!--versetest-->
<!-- 131-->
```verse
animated := interface:
    var CurrentFrame:int = 0
    TotalFrames:int = 10

    # Concrete implementation provided by interface
    NextFrame()<transacts><decides>:void =
        set CurrentFrame = Mod[(CurrentFrame + 1),TotalFrames] or 0

    # Can access interface fields
    ProgressPercent()<reads><decides>:rational =
        CurrentFrame / TotalFrames

sprite := class(animated):
    TotalFrames<override>:int = 20
    # Automatically inherits NextFrame and ProgressPercent implementations
```

类无需修改即可继承这些实现，允许接口提供可复用的行为。如果实现类需要专门化行为，可以覆盖这些方法，但接口提供可用的默认实现。

### 覆盖成员

类可以覆盖接口中的字段和方法以提供专门化实现：

<!--versetest-->
<!-- 132-->
```verse
base_stats := interface:
    BaseHealth:int = 100

    CalculateFinalHealth():int = BaseHealth

warrior := class(base_stats):
    # Override field with different default
    BaseHealth<override>:int = 150

    # Override method for specialized calculation
    CalculateFinalHealth<override>():int =
        BaseHealth * 2  # Warriors get double health

mage := class(base_stats):
    BaseHealth<override>:int = 75

    CalculateFinalHealth<override>():int =
        BaseHealth + MagicBonus

    MagicBonus:int = 25
```

字段覆盖可以提供不同的默认值或专门化为子类型。方法覆盖完全替换接口的实现。所有覆盖必须保持类型兼容性——字段只能被子类型覆盖，方法签名必须完全匹配。

### 多个接口的共享成员

Verse 的接口比许多其他语言更宽松——它们可以声明数据字段，提供具体的方法实现，一个类可以实现多个接口，即使它们共享成员名称。这种设计避免了要求所有接口之间使用全局唯一名称的摩擦。在实践中，独立的接口作者可能自然地使用相同的名称（`Enable`、`Disable`、`Power`、`Update`），要求每个接口都使用不同的名称会造成人为的命名冲突，且随着接口形成具有专门化变体的深层层次结构，这种问题会更加严重。

当一个类实现多个声明了同名字段或方法的接口时，你可以使用限定名称来消除歧义：

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
       MagicPower := (magical:)Power         # Access magical's Power
       PhysicalPower := (physical:)Power     # Access physical's Power
       MagicLevel := (magical:)GetPowerLevel()
       PhysicalLevel := (physical:)GetPowerLevel()
```

限定名称语法 `(InterfaceName:)MemberName` 指定你正在访问哪个接口的成员。每个接口维护自己的字段实例，使得类可以同时支持两个契约而不会产生冲突。

### 接口层次结构

接口可以扩展其他接口，创建结合了数据和行为需求的契约层次结构：

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

实现 `boss` 的类继承整个层次结构中的所有字段和方法——`boss`、`combatant`、`damageable` 和 `healable`。菱形继承（接口通过多条路径被继承）得到完全支持，字段会被正确合并，使得每个字段在实现类中只存在一次。

**重要提示：** 类不能直接多次继承同一接口（例如，`class(interface1, interface1)` 是错误的），但可以通过菱形继承间接继承。这意味着 `class(interface2, interface3)` 是有效的，即使 `interface2` 和 `interface3` 都继承自同一个基接口。

### 带访问器的字段

接口可以定义具有自定义 getter 和 setter 逻辑的字段，将复杂行为封装在简单的字段访问语法之后：

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
```
<!-- #>-->

`external{}` 关键字指示该字段没有直接存储——所有访问都通过访问器方法进行。这种模式对于实现属性更改通知、验证、计算属性和其他需要围绕字段访问逻辑的场景非常强大。

**重要提示：** 接口中定义了访问器的字段不能在实现类中被覆盖。访问器实现由接口固定。
