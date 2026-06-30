# 模块（Modules）

模块和路径是代码组织、命名空间管理以及跨项目共享和复用代码的基础概念。可以将模块视为将相关功能组合在一起的容器，类似于其他编程语言中的包，但在版本控制和兼容性方面提供了更强的保证。

在游戏开发的情境下，模块允许你将游戏逻辑的不同方面分离成可管理、可复用的部分。例如，你可能有一个用于玩家库存管理的模块，另一个用于战斗机制，还有一个用于 UI 交互。每个模块封装了自己的功能，同时只向代码的其他部分暴露必要的接口。

模块系统的设计旨在支持持久化、共享的 Metaverse 愿景——代码可以被发布一次，然后被任何人、在任何地方使用，并且即便原作者对其进行更新和改进，用户也能确信它将继续正常工作。这是通过严格的向后兼容性规则和全局命名空间系统实现的，确保每一段发布的代码都有一个唯一且永久的地址。

每个模块都与项目的文件系统结构紧密关联。当你在 Verse 项目中创建一个文件夹时，该文件夹会自动成为一个模块。模块的名称就是文件夹的名称，这使得文件组织与代码组织之间的关系完全透明。

同一文件夹中的所有 `.verse` 文件都被视为该模块的一部分，并共享同一个命名空间。这意味着如果你有三个文件——`player.verse`、`inventory.verse` 和 `equipment.verse`——都在名为 `PlayerSystems` 的文件夹中，它们都属于 `PlayerSystems` 模块，并且可以在没有任何 import 语句的情况下相互引用彼此的定义。这种自动分组机制使得在保持模块逻辑统一性的同时，将大型模块拆分到多个文件中以优化组织成为可能。

## 路径（Paths）

路径是使得 Verse 关于共享、持久化 Metaverse 愿景成为可能的寻址系统。正如互联网上的每个网站都有唯一的 URL，每个模块都有唯一标识它的全局路径。这个路径系统不仅仅是一种命名约定——它是 Verse 管理代码分发、版本控制和依赖关系的基础部分。

路径在概念上借鉴了 Web 域名，并针对编程语言的需求进行了调整。路径以正斜杠 `/` 开头，通常包含一个类似域名的标识符，后跟一个或多个路径段。这创建了一个既对人类可读又全局唯一的层次化命名空间。

`/domain/path/to/module` 这种格式服务几个重要目的：

- **持久且唯一的标识**：一旦模块在特定路径上发布，该路径就永久属于它。没有其他模块可以声明相同的路径，确保依赖关系始终解析到正确的代码。

- **所有权和权威**：路径的域部分（如 `Fortnite.com` 或 `Verse.org`）指明了谁拥有和维护该模块。这帮助开发者了解他们所用代码的来源和可信度。

- **可发现性**：由于路径遵循可预测的模式，开发者通常可以推测或轻松找到他们需要的模块。文档和工具也可以利用这种结构提供更好的发现体验。

- **层次化组织**：路径结构天然支持将相关模块组织在一起。例如，所有 UI 相关的模块可能位于 `/YourGame.com/UI/` 下，使它们作为一个组易于查找和理解。

Epic Games 提供了几个常用的标准模块：

- `/Verse.org/Verse` - 核心语言特性和标准库函数
- `/Verse.org/Random` - 随机数生成工具
- `/Verse.org/Simulation` - 模拟和计时工具
- `/Fortnite.com/Devices` - 与 Fortnite Creative 设备的集成
- `/UnrealEngine.com/Temporary/Diagnostics` - 调试和诊断工具
- `/UnrealEngine.com/Temporary/SpatialMath` - 3D 数学和空间运算

某些路径中使用 "Temporary" 表示这些模块是临时的，可能在 Verse 的未来版本中重新组织。这种命名约定有助于设定对 API 稳定性的预期。

当你创建自己的模块时，它们可以位于路径层次结构的不同层级：

- `/YourGame/` - 游戏的最顶层模块
- `/YourGame/Player/` - 玩家相关功能
- `/YourGame/Player/Inventory/` - 特定库存管理
- `/pizlonator@fn.com/NightDeath/` - 个人或实验性模块

允许包含类似邮箱的标识符（例如 `pizlonator@fn.com`）使得个体开发者无需拥有域名即可声明自己的命名空间。这使得模块系统更加民主化，同时仍然保持唯一性保证。

## 创建模块（Creating Modules）

一个模块可以包含：

- 常量和变量
- 函数
- 类、接口和结构体
- 枚举
- 其他模块定义
- 类型定义

当你在 Verse 项目中创建子文件夹时，该文件夹会自动创建一个模块。文件结构直接映射到模块层次结构。

你可以使用以下语法在 `.verse` 文件中创建模块：

<!--versetest
m := module{
module1 := module:
    MyConstant<public>:int = 42

    MyClass<public> := class:
        Value:int = 0

module2 := module
{
    AnotherConstant<public>:string = "Hello"
}
}
<#
-->
<!-- 01 -->
```verse
# Colon syntax
module1 := module:
    # Module contents here
    MyConstant<public>:int = 42

    MyClass<public> := class:
        Value:int = 0

# Bracket syntax (also supported)
module2 := module
{
    # Module contents here
    AnotherConstant<public>:string = "Hello"
}
```
<!-- #> -->

模块可以包含其他模块，从而创建层次结构：

<!--versetest
m := module{
BaseModule<public> := module:
    submodule<public> := module:
        submodule_class<public> := class:
            Value:int = 100

    module_class<public> := class:
        Name:string = ""
}
<#
-->
<!-- 02 -->
```verse
BaseModule<public> := module:
    submodule<public> := module:
        submodule_class<public> := class:
            Value:int = 100

    module_class<public> := class:
        Name:string = ""
```
<!-- #> -->

文件结构 `ModuleFolder/BaseModule` 等价于：

<!--versetest
m := module{
ModuleFolder := module:
    BaseModule := module:
        Submodule := module:
            submodule_class := class:
                Value:int = 0
}
<#
-->
<!-- 03 -->
```verse
ModuleFolder := module:
    BaseModule := module:
        Submodule := module:
            submodule_class := class:
                # Class definition
```
<!-- #> -->

### 限制（Restrictions）

模块体对其能包含的内容有严格的要求。理解这些限制有助于避免在定义模块时出现常见错误。

**模块只能包含定义：**

模块体只能包含定义语句——将名称绑定到值的声明。你不能包含任意表达式或可执行语句：

<!--NoCompile-->
<!-- 04 -->
```verse
# Valid: All definitions
Config := module:
    MaxValue:int = 100
    DefaultName:string = "Player"

    CalculateScore(Base:int):int = Base * 10

    player_class := class:
        Name:string

# Invalid: Contains non-definition expressions
BadModule := module:
    MaxValue:int = 100
    1 + 2  # ERROR 3560: Not a definition

# Invalid: Contains function call
BadModule2 := module:
    InitFunction():void = {}
    InitFunction()  # ERROR 3585: Cannot call function in module body
```

该限制确保模块初始化是确定性的，并且在加载模块时不会执行任意代码。

**需要类型注解：**

模块作用域下的所有数据定义必须显式指定其类型。仅使用 `:=` 进行类型推断是不允许的：

<!--NoCompile-->
<!-- 05 -->
```verse
# Invalid: Missing type annotation
BadModule := module:
    Value := 42  # ERROR 3547: Must specify type domain

# Valid: Explicit type annotation
GoodModule := module:
    Value:int = 42  # OK: Type explicitly specified
```

这一要求使模块接口显式化，并有助于独立编译和模块演化。

**有效的模块内容：**

模块可以包含以下类别的定义：

<!--versetest
m := module{
Utilities := module:
    Version:int = 1
    AppName:string = "MyApp"

    Calculate(X:int):int = X * 2

    data_class := class:
        Value:int

    data_interface := interface:
        GetValue():int

    data_struct := struct:
        X:float
        Y:float

    status := enum:
        Active
        Inactive

    Nested := module:
        NestedFunction():void = {}

    coordinate := tuple(float, float)

    positive_int := type{X:int where X > 0}
}
<#
-->
<!-- 06 -->
```verse
Utilities := module:
    # Constants with explicit types
    Version:int = 1
    AppName:string = "MyApp"

    # Functions
    Calculate(X:int):int = X * 2

    # Classes, interfaces, structs
    data_class := class:
        Value:int

    data_interface := interface:
        GetValue():int

    data_struct := struct:
        X:float
        Y:float

    # Enums
    status := enum:
        Active
        Inactive

    # Nested modules
    Nested := module:
        NestedFunction():void = {}

    # Type aliases
    coordinate := tuple(float, float)

    # Refinement types
    positive_int := type{X:int where X > 0}
```
<!-- #> -->

与函数、类或数据值不同，模块在 Verse 中不是一等公民。你不能将模块视为可以在运行时存储、传递或操作的值。

**不能将模块赋值给变量：**

<!--NoCompile-->
<!-- 07 -->
```verse
MyModule := module:
    Value<public>:int = 42

# Invalid: Cannot treat module as value
M:MyModule = MyModule  # ERROR 
```

模块纯粹作为命名空间和编译时的组织构造存在。模块标识符 `MyModule` 只能在特定上下文中使用。

**不能将模块作为参数传递：**

<!--NoCompile-->
<!-- 08 -->
```verse
MyModule := module:
    X<public>:int = 1

# Invalid: Cannot pass module as parameter
ProcessModule(M:module):void = {}  # ERROR
ProcessModule(MyModule)  # ERROR
```

没有可以在函数签名中使用的 `module` 类型。

**不能创建模块的集合：**

<!--NoCompile-->
<!-- 09 -->
```verse
ModuleA := module:
    Value:int = 1

ModuleB := module:
    Value:int = 2

# Invalid: Cannot create tuple or array of modules
Modules := (ModuleA, ModuleB)  # ERROR
```

## 导入模块（Importing Modules）

导入系统被设计为显式且可预测的。与某些自动导入常用模块或搜索多个位置以查找依赖关系的语言不同，Verse 要求你显式声明要使用的每个外部模块。这种显式性有助于防止命名冲突，并使依赖关系清晰明确。

`using` 语句是将模块导入到 Verse 代码中的主要机制。它通常放在文件顶部、任何其他代码定义之前，并将指定模块的内容引入当前作用域。

基本语法很直接——关键字 `using` 后跟花括号中的模块路径：

<!--NoCompile-->
```verse
using { /Verse.org/Random }
using { /Fortnite.com/Devices }
using { /Verse.org/Simulation }
using { /UnrealEngine.com/Temporary/Diagnostics }
```

当你导入一个模块后，其所有公共成员可以在你的代码中使用。但是，除非名称没有歧义，你仍然需要用模块名来限定它们。这种限定要求有助于保持代码清晰，并防止在多个模块定义了相似名称时意外使用错误的定义。

**using 是语句，不是表达式：**

`using` 指令是一个语句级别的声明，必须出现在代码的顶层。你不能将其用作表达式或嵌入到其他表达式中：

<!--NoCompile-->
<!-- 11 -->
```verse
# Invalid: using in expression context
# f():void = using{MyModule}  # ERROR 3669

# Invalid: using in conditional
# if (using{MyModule}, Condition?):
#     DoSomething()  # ERROR 3669

# Invalid: using in class/struct/interface body
# my_class := class:
#     using{MyModule}  # ERROR 3537
#     Field:int

# Invalid: using module path in function body
# ProcessData():void =
#     using{/MyProject/UtilityModule}  # ERROR 3669
#     Calculate()
```

模块 `using` 语句必须出现在文件或模块级别，不能嵌套在其他结构中。这确保导入在声明的作用域内始终可见且一致。

虽然带有路径的模块导入不允许出现在函数体中，但 Verse 确实支持带有局部变量和参数的**局部作用域 `using`**。详情请参见下面的[局部作用域 Using](#local-scope-using)。

**有效的 using 放置位置：**

<!--NoCompile-->
<!-- 12 -->
```verse
# At file level (most common)
using { /Verse.org/Random }
using { /Verse.org/Simulation }

ProcessData():void =
    # Use imported functions
    Value := GetRandomFloat(0.0, 1.0)

# Within module definition
Utilities := module:
    using { /Verse.org/Random }

    GenerateId<public>():int =
        GetRandomInt(1, 1000000)
```

### 导入解析（Import Resolution）

当 Verse 遇到一个 `using` 语句时，它会遵循特定的解析过程：

1. **绝对路径**（以 `/` 开头）从全局模块注册表中解析
2. **相对路径**（不带前导 `/`）相对于当前模块的位置进行解析
3. **嵌套模块**可以通过其父模块访问

此解析过程在编译时发生，这意味着所有导入在代码编译时必须可解析。Verse 中没有运行时模块加载或动态导入。

### 本地和相对导入（Local and Relative Imports）

对于你自己项目中的模块，在引用方式上有灵活性：

<!--NoCompile-->
<!-- 13 -->
```verse
# Absolute import from your project root
using { /MyGameProject/Systems/Combat }

# Import from a sibling folder
using { ../UI/MainMenu }

# Import from the same directory
using { PlayerController }

# Import from a subdirectory
using { Subsystems/WeaponSystem }
```

在绝对导入和相对导入之间的选择通常取决于你的项目结构以及是否计划重新组织模块。绝对导入在重构时更稳定，而相对导入可以使模块组更具可移植性。

### 嵌套导入（Nested Imports）

嵌套模块在导入时有一些特殊的考虑。导入模块的顺序很重要，并且有多种有效的方法：

<!--versetest
GameSystems := module:
    Inventory<public> := module{}
m:=module{
using { GameSystems }
using { Inventory }

using { GameSystems.Inventory }

using { GameSystems }
}
<#
-->
<!-- 14 -->
```verse
# Method 1: Import parent first, then child
using { GameSystems }
using { Inventory }  # Assumes Inventory is nested in GameSystems

# Method 2: Direct path to nested module
using { GameSystems.Inventory }

# Method 3: Import parent and access child through qualification
using { GameSystems }
# Later in code: GameSystems.Inventory.Item

# IMPORTANT: This order causes an error
# using { Inventory }      # Error: Inventory not found
# using { GameSystems }   # Too late, Inventory import already failed
```
<!-- #> -->

对导入顺序的限制之所以存在，是因为 Verse 按顺序解析导入。当你直接导入一个嵌套模块时，Verse 需要首先知道其父模块。这就是为什么在子模块之前导入父模块总是有效，而相反的顺序则会失败。

### 使用 import 创建模块别名

`import` 表达式为模块创建局部别名，将其路径绑定到一个名称。与 `using` 直接将模块的公共成员引入作用域不同，`import` 允许你通过别名以点号表示法访问它们：

<!--NoCompile-->
<!-- 14b -->
```verse
# using: members available directly
using { /MyProject/Utilities }
Result := HelperFunction()  # HelperFunction is in scope

# import: members accessed through alias
Utils := import(/MyProject/Utilities)
Result := Utils.HelperFunction()  # accessed via alias
```

这在你想避免名称冲突，或者需要在代码中明确某个定义的来源时很有用：

<!--NoCompile-->
<!-- 14c -->
```verse
Physics := import(/MyProject/Systems/Physics)
Graphics := import(/MyProject/Systems/Graphics)

# Clear which Transform is being used
PhysicsTransform := Physics.Transform{}
GraphicsTransform := Graphics.Transform{}
```

使用 `import` 创建的模块别名在同一模块内的所有片段中可见。`import` 也可以与 `using` 结合，既为模块创建别名又将其成员引入作用域：

<!--NoCompile-->
<!-- 14d -->
```verse
Graphics := import(/MyProject/Systems/Graphics)
using { Graphics }  # now Graphics members are also directly available
```

注意 `import` 只适用于模块路径。尝试导入解析为类或其他非模块定义的路径会导致错误。

### 作用域和可见性（Scope and Visibility）

导入具有文件作用域——它们只影响声明所在的文件。如果你在同一模块中有多个 `.verse` 文件，每个文件都需要自己的针对外部模块的 import 语句。然而，同一模块内的文件可以在没有导入的情况下彼此看到对方的定义：

<!--versetest
m := module{
health_component := class:
    CurrentHealth:float = 100.0

armor_component := class:
    HealthComp:health_component = health_component{}
}
<#
-->
<!-- 15 -->
```verse
# File: player_module/health.verse
health_component := class:
    CurrentHealth:float = 100.0

# File: player_module/armor.verse
# No import needed for health_component since it's in the same module
armor_component := class:
    HealthComp:health_component = health_component{}
```
<!-- #> -->

### 导入冲突（Import Conflicts）

当两个导入的模块定义了同名成员时，你需要进行消歧：

<!--NoCompile-->
<!-- 16 -->
```verse
using { /GameA/Combat }
using { /GameB/Combat }

# Both modules might define CalculateDamage
# You must use qualified names:
DamageA := Combat.CalculateDamage(10.0)  # Error: ambiguous
DamageA := (/GameA/Combat:)CalculateDamage(10.0)  # OK: fully qualified
DamageB := (/GameB/Combat:)CalculateDamage(10.0)  # OK: fully qualified
```

### 限定名（Qualified Names）

导入后，你可以使用限定名来引用模块内容。Verse 提供了两种限定形式：大多数情况下使用标准的点号表示法，以及用于消歧的特殊限定访问语法。

当你需要消歧来自不同模块的同名标识符，或者想显式指明标识符的作用域时，使用带括号和冒号的限定访问表达式：


<!-- BUG? Or bad error message?

m := module{ item<public> := class{} }

x := module{
item := class{}
F():void =
    A := (local:)item{} 
    B := (m:)item{}
}


LogVerseBuild: Error: C:/VerseBook/Book/verse/16_modules/17.versetest(8,10, 8,22): Script Error 3506: Unknown identifier `item`. Did you mean any of:
InventoryModule.item
item
LogVerseBuild: Error: C:/VerseBook/Book/verse/16_modules/17.versetest(9,10, 9,33): Script Error 3506: Unknown identifier `item`. Did you mean any of:
InventoryModule.item

-->

<!--NoCompile-->
<!-- 17 -->
```verse
# Qualified access syntax: (qualifier:)identifier

using { CombatModule }
using { MagicModule }

ProcessDamage():void =
    # Both modules define CalculateDamage
    PhysicalDamage := (CombatModule:)CalculateDamage(100.0)
    MagicalDamage := (MagicModule:)CalculateDamage(100.0)

    # Explicitly qualify local vs module identifiers
    LocalItem := item{Name := "Sword"}  # Local definition
    ModuleItem := (InventoryModule:)item{Name := "Shield"}  # From module
```

限定访问表达式 `(module:)identifier` 在以下几种场景中特别有用：

1. **解决命名冲突**：当多个导入模块暴露了相同的标识符时
2. **显式作用域限定**：当你想明确指明标识符来自哪个模块以提高可读性时
3. **访问被遮蔽的名称**：当局部定义遮蔽了模块成员时
4. **泛型编程**：当使用参数化类型且限定符可能是计算得出时

## 模块作用域变量（Module-Scoped Variables）

在模块作用域定义的变量对于变量在作用域内的任何游戏实例都是全局的。

对模块作用域定义的限制：

- 不允许在模块作用域直接声明简单类型的 `var`（例如 `var X:int = 0`）
- 只要 `<unique>` 类的 `<allocates>` 实例的构造实际上没有分配可变内存，就可以在模块作用域创建它们
- 对于持久可变状态，使用带有适当键类型的 `weak_map`（见下文）

对于在游戏会话期间持续的变量，使用 `weak_map(session, t)`：

<!--versetest
session := class<unique>{}
GetSession()<transacts>:session = session{}
-->
<!-- 20 -->
```verse
var GlobalCounter:weak_map(session, int) = map{}

IncrementCounter()<transacts>:void =
    CurrentValue := if (Value := GlobalCounter[GetSession()]) then Value + 1 else 0
    if (set GlobalCounter[GetSession()] = CurrentValue) {}
```

对于跨游戏会话持久化的数据，使用 `weak_map(player, t)`：

<!--versetest
player := class<unique><persistent><module_scoped_var_weak_map_key>{}
var PlayerSaveData:weak_map(player, player_data) = map{}

player_data := class<final><persistable>:
    Level:int = 1
    Experience:int = 0
    UnlockedItems:[]string = array{}

SavePlayerProgress(Player:player, NewData:player_data)<decides>:void =
    set PlayerSaveData[Player] = NewData
<#
-->
<!-- 21 -->
```verse
var PlayerSaveData:weak_map(player, player_data) = map{}

player_data := class<final><persistable>:
    Level:int = 1
    Experience:int = 0
    UnlockedItems:[]string = array{}

SavePlayerProgress(Player:player, NewData:player_data)<decides>:void =
    set PlayerSaveData[Player] = NewData
```
<!-- #> -->

## Metaverse 与发布（Metaverse and Publishing）

当你将模块发布到 Metaverse 时，模块路径变为全局可访问，其公共成员成为模块 API 的一部分，并且从那时起模块必须保持向后兼容性。

以下示例展示了演化是如何工作的：

<!--NoCompile-->
<!-- 22 -->
```verse
# Initial publication
Thing<public>:rational = 1/3

# Valid updates:
# - Change the value (not the type)
Thing<public>:rational = 10/3

# - Make the type more specific (subtype)
Thing<public>:int = 20  # nat is a subtype of int

# Invalid updates (would be rejected):
# - Remove the member
# - Change to incompatible type
# Thing<public>:string = "hello"  # Would fail
```

## 局部限定符（Local Qualifiers）

`(local:)` 限定符可以消歧函数内的标识符。这对演化兼容性至关重要——当外部模块在你的代码发布后添加了新的公共定义时，`(local:)` 确保你的局部定义优先。

<!--versetest
m := module{
ExternalModule<public> := module:
    ShadowX<public>:int = 10

MyModule := module:
    using{ExternalModule}


    Foo():float =
        (local:)ShadowX:float = 0.0
        (local:)ShadowX
}
<#
-->
<!-- 23 -->
```verse
# External module adds ShadowX after your code published
ExternalModule<public> := module:
    ShadowX<public>:int = 10  # Added later!

MyModule := module:
    using{ExternalModule}

    # Without (local:) - shadowing conflict
    # Foo():float =
    #     ShadowX:float = 0.0  # Error: conflicts with ExternalModule.ShadowX
    #     ShadowX

    # With (local:) - clear disambiguation
    Foo():float =
        (local:)ShadowX:float = 0.0  # Local variable
        (local:)ShadowX              # Returns 0.0, not 10
```
<!-- #> -->

`(local:)` 限定符可以在以下上下文中使用：

**函数参数：**

<!--versetest
m := module{
ProcessValue((local:)Value:int):int =
    (local:)Value + 1
}
<#
-->
<!-- 24 -->
```verse
ProcessValue((local:)Value:int):int =
    (local:)Value + 1
```
<!-- #> -->

**函数体数据定义：**

<!--versetest
m := module{
Compute():int =
    (local:)Result:int = 42
    (local:)Result
}
<#
-->
<!-- 25 -->
```verse
Compute():int =
    (local:)Result:int = 42
    (local:)Result
```
<!-- #> -->

**For 循环变量：**

<!--versetest
m := module{
SumValues():int =
    var Total:int = 0
    for ((local:)I := 0..10):
        set Total += (local:)I
    Total
}
<#
-->
<!-- 26 -->
```verse
SumValues():int =
    var Total:int = 0
    for ((local:)I := 0..10):
        set Total += (local:)I
    Total
```
<!-- #> -->

**If 条件：**

<!--versetest
GetValue<public>()<computes><decides>:float = 10.0
-->
<!-- 27 -->
```verse
CheckValue():float =
    if (X := GetValue[], (local:)X > 5.0):
        (local:)X
    else:
        0.0
```

**块作用域：**

<!--versetest
m := module{
ComputeInBlock():int =
    block:
        (local:)Temp:int = 10
        (local:)Temp * 2
}
<#
-->
<!-- 28 -->
```verse
ComputeInBlock():int =
    block:
        (local:)Temp:int = 10
        (local:)Temp * 2
```
<!-- #> -->

**类块：**

<!--NoCompile-->
<!-- 29 -->
```verse
my_class := class:
    var Value<public>:int = 0
    block:
        (local:)Value:int = 42
        set (my_class:)Value = (local:)Value
```

`(local:)` 限定符**不能**在以下上下文中使用：


**嵌套作用域限制：**

当前，你**不能**在嵌套块中重新定义 `(local:)` 限定的标识符：

<!--NoCompile-->
```verse
# Error: cannot redefine local identifier
F((local:)X:int):int =
    block:
        (local:)X:float = 5.5  # Error: X already defined in function
    (local:)X
```

此限制可能在未来的版本中解除，以支持更复杂的作用域模式。

## 自动限定（Automatic Qualification）

!!! warning "未发布的功能（Unreleased Feature）"
    自动限定尚未完全实现。本节记录的是计划中的功能，目前还不可用。此处描述的行为，特别是关于编译器如何转换已发布代码中的标识符，在正式发布之前不应依赖。

当你编写 Verse 代码时，为了清晰和可读性，你使用简单的、非限定的标识符。然而，Verse 编译器将在内部将所有标识符转换为完全限定的形式，明确指定它们的作用域和来源。这个过程称为**自动限定（automatic qualification）**，将确保每个标识符都是无歧义的，并且可以被解析到确切的定义。

理解自动限定将帮助你理解 Verse 如何解析名称、为什么会出现某些错误，以及模块系统如何在即使有多个模块和重名的情况下保持正确性。

编译器将对以下几类标识符进行限定：

1. **顶层定义** - 包作用域下的函数、变量、类、模块
2. **类型引用** - 所有类型，包括内置类型如 `int` 和 `string`
3. **函数参数** - 局部参数获得 `(local:)` 限定符
4. **类和接口成员** - 嵌套在复合类型中的方法、字段
5. **模块成员** - 模块内的公共和内部定义
6. **嵌套作用域** - 嵌套模块、类、函数中的引用

Verse 使用几种模式根据标识符的作用域对其进行限定：

**包级别限定（Package-level qualification）**：包根部的定义使用包路径进行限定：

<!--NoCompile-->
```verse
# What you write:
Function(X:int):int = X

# How the compiler sees it:
(/YourPackage:)Function((local:)X:(/Verse.org/Verse:)int):(/Verse.org/Verse:)int = (local:)X
```

包路径 `/YourPackage` 成为 `Function` 的限定符，而参数 `X` 获得特殊的 `(local:)` 限定符，内置类型 `int` 则用其标准库路径 `/Verse.org/Verse` 进行限定。

**局部作用域限定（Local scope qualification）**：函数参数和局部变量用 `(local:)` 标记：

<!--NoCompile-->
```verse
# What you write:
ProcessValue(Input:int, Multiplier:int):int =
    Input * Multiplier

# How the compiler sees it:
(/YourPackage:)ProcessValue((local:)Input:(/Verse.org/Verse:)int, (local:)Multiplier:(/Verse.org/Verse:)int):(/Verse.org/Verse:)int =
    (local:)Input * (local:)Multiplier
```

**嵌套作用域限定（Nested scope qualification）**：类、接口或模块内的成员使用其容器的路径进行限定：

<!--NoCompile-->
```verse
# What you write:
player_class := class:
    Health:float = 100.0

    TakeDamage(Amount:float):void =
        set Health = Health - Amount

# How the compiler sees it:
(/YourPackage:)player_class := class:
    (/YourPackage/player_class:)Health:(/Verse.org/Verse:)float = 100.0

    (/YourPackage/player_class:)TakeDamage((local:)Amount:(/Verse.org/Verse:)float):(/Verse.org/Verse:)void =
        set (/YourPackage/player_class:)Health = (/YourPackage/player_class:)Health - (local:)Amount
```

注意 `Health` 和 `TakeDamage` 是如何用 `/YourPackage/player_class` 进行限定的，以表明它们是类的成员。

**模块成员限定（Module member qualification）**：模块内的定义使用模块路径进行限定：

<!--MoCompile-->
```verse
# What you write:
Config := module:
    MaxPlayers<public>:int = 100

    GetPlayerLimit<public>():int = MaxPlayers

# How the compiler sees it:
(/YourPackage:)Config := module:
    (/YourPackage/config:)MaxPlayers<public>:(/Verse.org/Verse:)int = 100

    (/YourPackage/config:)GetPlayerLimit<public>():(/Verse.org/Verse:)int =
        (/YourPackage/config:)MaxPlayers
```

所有内置类型都使用其标准库路径进行限定。这使得这些类型的来源明确，并与用户定义的类型保持一致：

<!--NoCompile-->
```verse
# Common built-in types and their full qualifications:
int       → (/Verse.org/Verse:)int
float     → (/Verse.org/Verse:)float
string    → (/Verse.org/Verse:)string
logic     → (/Verse.org/Verse:)logic
message   → (/Verse.org/Verse:)message
```

当你写 `X:int` 时，编译器将其展开为 `X:(/Verse.org/Verse:)int`，使类型的来源显式化。

### 示例（Example）

这里有一个更实际的示例，展示了限定在多个作用域中如何工作：

<!--NoCompile-->
```verse
# What you write:
GameSystem := module:
    BaseValue:int = 42

    Calculator := module:
        Multiplier:int = 2

        Calculate(Input:int):int =
            Input * Multiplier + BaseValue

# How the compiler will see it (when implemented):
(/YourGame:)GameSystem := module:
    (/YourGame/GameSystem:)BaseValue:(/Verse.org/Verse:)int = 42

    (/YourGame/GameSystem:)Calculator := module:
        (/YourGame/GameSystem/Calculator:)Multiplier:(/Verse.org/Verse:)int = 2

        (/YourGame/GameSystem/Calculator:)Calculate((local:)Input:(/Verse.org/Verse:)int):(/Verse.org/Verse:)int =
            (local:)Input * (/YourGame/GameSystem/Calculator:)Multiplier + (/YourGame/GameSystem:)BaseValue
```

注意：

- 参数 `Input` 是 `(local:)`
- `Multiplier` 用其所属模块路径限定
- `BaseValue` 用外部模块路径限定
- 所有类型引用用 Verse 标准库路径限定

**关于遮蔽的重要说明**：自动限定仅适用于已发布的代码，而不适用于你的源代码。Verse 目前强制执行严格的反遮蔽规则，以防止混淆并保持代码清晰。例如，以下代码**不能**编译：

<!--NoCompile-->
```verse
# This does NOT compile - shadowing is not allowed
Thing := module:
    Thing := module:  # ERROR: Cannot shadow outer Thing
        Potato := module{}
```

即使有自动限定，嵌套的定义也不能遮蔽同名的外部定义。如果你想有意遮蔽某个名称，必须使用显式限定符来明确你的意图。这种严格的方法有助于防止错误，并使代码演化更安全。

### 结合 using 的限定

当你使用 `using` 导入模块时，编译器仍然限定所有标识符，但它可以将非限定名称解析到已导入的模块：

<!-- NoCompile-->
```verse
# What you write:
using { /Verse.org/Random }

GenerateRandomValue():float =
    GetRandomFloat(0.0, 1.0)

# How the compiler sees it:
using { /Verse.org/Random }

(/YourGame:)GenerateRandomValue():(/Verse.org/Verse:)float =
    (/Verse.org/Random:)GetRandomFloat(0.0, 1.0)
```

编译器根据 `using` 语句将 `GetRandomFloat` 解析为 `(/Verse.org/Random:)GetRandomFloat`。

### 何时需要关注（When It Matters）

一旦实现，在正常开发过程中你很少需要考虑自动或手动限定，因为编译器会透明地处理它。然而，理解它将在以下几种情况下有所帮助：

**调试名称解析错误**：当编译器报告有歧义或无法解析的标识符时，理解限定可以帮助你看出原因：

<!--NoCompile-->
```verse
using { /ModuleA }
using { /ModuleB }

# Both modules define Calculate
Result := Calculate(10)  # ERROR: Ambiguous - could be either module
```

错误发生的原因是编译器无法自动限定 `Calculate`——它可能是 `(/ModuleA:)Calculate` 或 `(/ModuleB:)Calculate`。

**遮蔽冲突**：当局部变量与模块成员同名时：

<!--NoCompile-->
```verse
MyModule := module:
    Value:int = 100

    Process(Value:int):int =
        # Without explicit qualification, this is ambiguous
        Value + Value  # Which Value? Module or parameter?
```

编译器需要通过限定来区分 `(/MyModule:)Value` 和 `(local:)Value`。

**理解错误消息**：编译器错误消息有时会显示限定名以精确定位涉及的定义：

```
Error: Cannot assign (/Verse.org/Verse:)string to (/Verse.org/Verse:)int at line 42
```

这使得错误涉及的是内置的 `string` 和 `int` 类型而非用户定义的同名类型变得清晰。

**处理生成或反射的代码**：生成 Verse 代码或分析代码结构的工具使用限定形式，因此在使用此类工具时理解它会有帮助。

### 显式限定（Explicit Qualification）

虽然编译器会自动限定标识符，但你也可以使用限定访问语法 `(qualifier:)identifier` 显式地限定它们。这在你想覆盖自动解析或明确你的意图时很有用：

<!-- 45 FAILURE
  Line 11: Verse compiler error V3509: The assignment's left hand expression type `int` cannot be assigned to
-->
```verse
GameSystem := module:
    Value:int = 100

    # Explicitly qualify to avoid any ambiguity
    GetValue():int = (GameSystem:)Value

    # Use local qualifier for parameters
    SetValue((local:)Value:int):void =
        set (GameSystem:)Value = (local:)Value
```

显式限定在以下情况下特别有价值：

- 解决导入模块之间的命名冲突
- 使代码更具自文档性
- 覆盖遮蔽行为
- 处理动态或计算出的限定符

## 局部作用域 Using（Local Scope Using）

虽然模块级别的 `using` 通过路径导入模块，Verse 还支持函数体内的**局部作用域 `using`**，以启用来自局部变量和参数的成员访问推断。这个特性使得在处理具有大量成员访问的对象时代码更简洁。

局部作用域 `using` 接受一个局部变量或参数标识符（而非模块路径），并使其成员无需显式限定即可访问：

<!--versetest
m := module{
entity := class:
    Name:string = "Entity"
    var Health:int = 100

    UpdateHealth(Amount:int):void =
        set Health = Health + Amount

ProcessEntity(E:entity):void =
    Print(E.Name)
    E.UpdateHealth(-10)
    Print("{E.Health}")

    using{E}
    Print(Name)
    UpdateHealth(-10)
    Print("{Health}")
}
<#
-->
<!-- 46 -->
```verse
entity := class:
    Name:string = "Entity"
    var Health:int = 100

    UpdateHealth(Amount:int):void =
        set Health = Health + Amount

ProcessEntity(E:entity):void =
    # Explicit member access
    Print(E.Name)
    E.UpdateHealth(-10)
    Print("{E.Health}")

    # With local using - inferred member access
    using{E}
    Print(Name)         # Inferred as: E.Name
    UpdateHealth(-10)   # Inferred as: E.UpdateHealth(-10)
    Print("{Health}")       # Inferred as: E.Health
```
<!-- #> -->

`using{E}` 表达式使得当前作用域内 `E` 的所有成员无需 `E.` 前缀即可访问。

### 与局部变量一起使用

局部 `using` 可以与同一函数中定义的变量一起使用：

<!--versetest
player := class:
    var Name:string = ""
    var Score:int = 0
-->
<!-- 47 -->
```verse
CreateAndProcess():void =
    Player := player{Name := "Alice", Score := 100}

    # Without using
    Print(Player.Name)
    set Player.Score = Player.Score + 50

    # With using
    using{Player}
    Print(Name)         # Inferred as: Player.Name
    set Score = Score + 50  # Inferred as: Player.Score
```

### 块作用域（Block Scoping）

`using` 的作用域限于其出现的块以及任何嵌套块：

**在同一块中使用 using：**

<!--versetest
data_record := class:
    Value:int = 0
    UpdateField<public>(V:int):void = {}
-->
<!-- 48 -->
```verse
ProcessData():void =
    block:
        Data := data_record{}
        using{Data}
        UpdateField(Value)  # Inferred as: Data.UpdateField(Data.Value)
    # Data members no longer accessible here
```

**从外部块使用 using：**

<!--versetest
data_record := class:
    Value:int = 0
    UpdateField<public>(V:int):void = {}
-->
<!-- 49 -->
```verse
ProcessData():void =
    Data := data_record{}
    block:
        using{Data}  # Can use variable from outer scope
        UpdateField(Value)  # Works - Data in scope
```

**嵌套块继承：**

<!--versetest
data_record := class:
    Value:int = 0
    UpdateField<public>(V:int):void = {}
-->
<!-- 50 -->
```verse
ProcessData():void =
    Data := data_record{}
    using{Data}  # Applies to this block and nested blocks

    block:
        # Inner block inherits outer using
        UpdateField(Value)  # Still infers Data.UpdateField(Data.Value)
```

### 顺序（Order）

成员推断仅在遇到 `using` 表达式**之后**生效：

<!--NoCompile-->
```verse
# ERROR: Cannot infer before using
ProcessData(Data:data_record):void =
    UpdateField()  # ERROR - before using
    using{Data}
    UpdateField()  # OK - after using

# ERROR: Using scope doesn't extend backward
ProcessData(Data:data_record):void =
    block:
        using{Data}
        UpdateField()  # OK - within using scope
    UpdateField()  # ERROR - after using scope ended
```

`using` 语句充当声明点——推断不具有追溯性。

### 冲突解决（Conflict Resolution）

你可以在同一个作用域中有多个 `using` 表达式，但冲突的成员名称必须显式限定：

<!--versetest
m := module{
player_stats := class:
    Health:int = 100
    Mana:int = 50
    GetInfo():string = "Player"

enemy_stats := class:
    Health:int = 80
    Armor:int = 20
    GetInfo():string = "Enemy"

ProcessCombat(Player:player_stats, Enemy:enemy_stats):void =
    using{Player}
    Print(GetInfo())
    Print("{Mana}")

    using{Enemy}
    Print("{Armor}")


    Print("{Player.Health}")
    Print("{Enemy.Health}")
    Print(Player.GetInfo())
    Print(Enemy.GetInfo())
}
<#
-->
<!-- 52 -->
```verse
player_stats := class:
    Health:int = 100
    Mana:int = 50
    GetInfo():string = "Player"

enemy_stats := class:
    Health:int = 80
    Armor:int = 20
    GetInfo():string = "Enemy"

ProcessCombat(Player:player_stats, Enemy:enemy_stats):void =
    using{Player}
    Print(GetInfo())  # Player.GetInfo()
    Print("{Mana}")       # Player.Mana (no conflict)

    using{Enemy}
    # Now both are in scope
    Print("{Armor}")      # Enemy.Armor (no conflict with Player)

    # ERROR: Conflicts must be qualified
    # Print(Health)   # Ambiguous - both have Health
    # Print(GetInfo())  # Ambiguous - both have GetInfo

    # Must qualify conflicting members
    Print("{Player.Health}")
    Print("{Enemy.Health}")
    Print(Player.GetInfo())
    Print(Enemy.GetInfo())
```
<!-- #> -->

当多个 `using` 上下文中存在同名的成员时，你必须显式限定以进行消歧。

### 可变成员（Mutable Member）

局部 `using` 通过 `set` 关键字与可变字段一起使用：

<!--versetest
m := module{
config := class:
    var Volume:float = 1.0
    var Quality:int = 2

UpdateSettings(Settings:config):void =
    using{Settings}

    set Volume = 0.8
    set Quality = 3
}
<#
-->
<!-- 53 -->
```verse
config := class:
    var Volume:float = 1.0
    var Quality:int = 2

UpdateSettings(Settings:config):void =
    using{Settings}

    # Mutable field access
    set Volume = 0.8     # Inferred as: set Settings.Volume = 0.8
    set Quality = 3      # Inferred as: set Settings.Quality = 3
```
<!-- #> -->

## 故障排除（Troubleshooting）

在使用模块时，你可能会遇到各种问题。了解这些常见问题及其解决方案将帮助你更高效地调试模块相关错误。

### 模块未找到错误（Module Not Found Errors）

**问题**：编译器报告在尝试导入模块时找不到该模块。

**常见原因及解决方案**：

1. **路径不正确**：仔细检查 `using` 语句中的模块路径。记住路径是区分大小写的。

<!--NoCompile-->
<!-- 54 -->
```verse
# Wrong: different case
using { /verse.org/random }  # Error: module not found

# Correct: proper case
using { /Verse.org/Random }  # Works
```

2. **缺少父模块导入**：导入嵌套模块时，确保先导入父模块。

<!--NoCompile-->
<!-- 55 -->
```verse
# Wrong: child before parent
using { Inventory }  # Error if Inventory is nested

# Correct: parent first
using { GameSystems }
using { Inventory }
```

3. **文件位置不匹配**：确保你的文件结构与模块结构匹配。如果你有一个名为 `PlayerSystems` 的文件夹，该文件夹中的所有文件都是 `PlayerSystems` 模块的一部分。

### 访问被拒绝错误（Access Denied Errors）

**问题**：你无法访问导入模块的某个成员。

**常见原因及解决方案**：

1. **缺少访问说明符**：没有 `<public>` 说明符的成员默认为内部。

<!--NoCompile-->
<!-- 56 -->
```verse
# In ModuleA
SecretValue:int = 42  # Internal by default
PublicValue<public>:int = 100  # Explicitly public

# In another module
using { ModuleA }
X := ModuleA.SecretValue  # Error: not accessible
Y := ModuleA.PublicValue  # Works
```

2. **受保护或私有成员**：这些成员在其定义所在的作用域之外不可访问。

<!--NoCompile-->
<!-- 57 -->
```verse
# In a class
class_a := class:
    PrivateField<private>:int = 10
    ProtectedField<protected>:int = 20
    PublicField<public>:int = 30

# Outside the class
Obj := class_a{}
X := Obj.PrivateField  # Error: private
Y := Obj.PublicField   # Works
```

### 循环依赖错误（Circular Dependency Errors）

**问题**：两个模块试图相互导入，形成了循环依赖。

**解决方案**：重构代码以避免循环依赖：

1. **提取公共代码**：将共享定义移到一个两个模块都可以导入的第三个模块中。
2. **使用接口**：在单独的模块中定义接口以打破依赖循环。
3. **重新考虑架构**：循环依赖通常表明存在需要重新考虑的设计问题。

### 名称冲突错误（Name Collision Errors）

**问题**：两个导入的模块定义了同名的成员。

**解决方案**：使用完全限定名进行消歧：

<!--NoCompile-->
```verse
using { /GameA/Combat }
using { /GameB/Combat }

# Ambiguous
Damage := CalculateDamage(10.0)  # Error: which CalculateDamage?

# Explicit
DamageA := /GameA/Combat.CalculateDamage(10.0)  # Clear
DamageB := /GameB/Combat.CalculateDamage(10.0)  # Clear
```

### 持久化问题（Persistence Issues）

**问题**：模块作用域变量的持久化不如预期。

**常见原因及解决方案**：

1. **使用了错误的类型**：确保对玩家持久化使用了 `weak_map(player, t)`。
2. **类型不可持久化**：检查你的自定义类型是否具有 `<persistable>` 说明符。
3. **初始化时机**：确保在游戏生命周期的正确时机初始化持久化数据。

### 局部限定符冲突（Local Qualifier Conflicts）

**问题**：当局部标识符与模块成员冲突时出现遮蔽错误。

**解决方案**：使用 `(local:)` 限定符进行消歧：

<!--versetest
m := module{
ModuleX := module:
    Value:int = 10

    ProcessValue((local:)Value:int):int =
        (ModuleX:)Value + (local:)Value
}
<#
-->
<!-- 59 -->
```verse
ModuleX := module:
    Value:int = 10

    ProcessValue((local:)Value:int):int =
        (ModuleX:)Value + (local:)Value  # Clear distinction
```
<!-- #> -->
