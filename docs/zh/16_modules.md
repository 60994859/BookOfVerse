# 模块

模块和路径是代码组织的基本概念，
命名空间管理，以及跨域共享和重用代码的能力
项目。将模块视为分组相关的容器
功能在一起，类似于其他编程中的包
语言，但对版本控制和
兼容性。

在游戏开发的背景下，模块允许您分离
将游戏逻辑的不同方面转化为可管理、可重用的
件。例如，您可能有一个用于玩家库存的模块
管理，另一个用于战斗机制，另一个用于用户界面
互动。每个模块都封装了自己的功能，同时
仅向代码的其他部分公开必要的接口。该模块系统旨在支持持久、
共享的 Metaverse，其中代码可以发布一次并可供任何人使用，
任何地方，相信它会继续工作，即使
原作者对其进行了更新和改进。这是通过以下方式实现的
严格的向后兼容性规则和全局命名空间系统
确保每一段已发布的代码都有一个唯一的永久地址。

每个模块都与文件系统结构有着内在的联系
你的项目。当您在 Verse 项目中创建文件夹时，
文件夹自动成为一个模块。该模块的名称很简单
文件夹的名称，使您的文件组织之间的关系
并且您的代码组织完全透明。同一文件夹中的所有 `.verse` 文件均被视为该文件夹的一部分
模块并共享相同的命名空间。这意味着如果你有三个
文件 - `player.verse`、`inventory.verse` 和 `equipment.verse` - 所有
在名为 `PlayerSystems` 的文件夹中，它们都有助于
`PlayerSystems`模块并可以互相引用定义
没有任何进口声明。这种自动分组很容易
将大模块拆分到多个文件中以便更好地组织
同时保持模块的逻辑统一性。

## 路径

路径是寻址系统，它使 Verse 的愿景成为共享的、
持久的元宇宙成为可能。就像互联网上的每个网站一样
有一个唯一的 URL，每个模块都有一个唯一的路径来标识它
全球。这个路径系统不仅仅是一个命名约定 -
这是 Verse 管理代码分发的基本部分，
版本控制和依赖项。路径在概念上借鉴了网络域，并针对
编程语言的需求。路径以正斜杠开头
`/` 通常包括一个类似域的标识符，后跟一个或
更多路径段。这创建了一个分层命名空间，它既
人类可读且全球唯一。

格式 `/domain/path/to/module` 有几个重要的用途：

- **持久且唯一的标识**：模块发布后
  在某条特定的路径上，该路径永远属于它。没有其他
  模块可以声明相同的路径，确保依赖关系
  始终解析为正确的代码。

- **所有权和权限**：路径的域部分（例如
  `Fortnite.com` 或 `Verse.org`) 指示谁拥有并维护
  模块。这有助于开发人员了解来源和
  他们使用的代码的可信度。- **可发现性**：因为路径遵循可预测的模式，
  开发人员通常可以猜测或轻松找到他们想要的模块
  需要。文档和工具也可以利用这种结构
  提供更好的发现体验。

- **层级组织**：路径结构天然支持
  将相关模块组织在一起。例如，所有与 UI 相关的
  模块可能位于 `/YourGame.com/UI/` 下，使它们易于
  作为一个群体去发现和理解。

Epic Games 提供了几个常用的标准模块：

- `/Verse.org/Verse` - 核心语言特性和标准库函数
- `/Verse.org/Random` - 随机数生成实用程序
- `/Verse.org/Simulation` - 模拟和计时实用程序
- `/Fortnite.com/Devices` - 与 Fortnite Creative 设备集成
- `/UnrealEngine.com/Temporary/Diagnostics` - 调试和诊断工具
- `/UnrealEngine.com/Temporary/SpatialMath` - 3D 数学和空间运算在某些路径中使用“Temporary”表示这些模块是
临时的，可能会在 Verse 的未来版本中重新组织。这个
命名约定有助于设定对稳定性的期望
API。

当您创建自己的模块时，它们可以存在于各个级别
路径层次结构：

- `/YourGame/` - 游戏的顶级模块
- `/YourGame/Player/` - 播放器相关功能
- `/YourGame/Player/Inventory/` - 特定库存管理
- `/pizlonator@fn.com/NightDeath/` - 个人或实验模块

能够包含类似电子邮件的标识符（例如
`pizlonator@fn.com`) 允许个人开发者声明自己的
命名空间而不需要拥有域。这使民主化
模块系统，同时仍保持唯一性保证。

## 创建模块

一个模块可以包含：

- 常量和变量
- 功能
- 类、接口和结构
- 枚举
- 其他模块定义
- 类型定义当您在 Verse 项目中创建子文件夹时，会生成一个模块
为该文件夹自动创建。直接查看文件结构
映射到模块层次结构。

您可以使用以下语法在 `.verse` 文件中创建模块：

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
# 冒号语法
module1 := module:
    # 模块内容在这里
    MyConstant<public>:int = 42

    MyClass<public> := class:
        Value:int = 0

# 括号语法（也支持）
module2 := module
{
    # 模块内容在这里
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

文件结构 `ModuleFolder/BaseModule` 相当于：

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
                # 类定义
```
<!-- #> -->

### 限制

模块主体对其功能有严格的要求
包含。了解这些限制有助于避免常见错误
定义模块时。

**模块只能包含定义：**

模块主体只能包含定义语句 - 声明
将名称绑定到值。您不能包含任意表达式或
可执行语句：

<!--NoCompile-->
<!-- 04 -->
```verse
# 有效：所有定义
Config := module:
    MaxValue:int = 100
    DefaultName:string = "Player"

    CalculateScore(Base:int):int = Base * 10

    player_class := class:
        Name:string

# 无效：包含非定义表达式
BadModule := module:
    MaxValue:int = 100
    1 + 2  # 错误 3560：不是定义

# 无效：包含函数调用
BadModule2 := module:
    InitFunction():void = {}
    InitFunction()  # 错误 3585：无法调用模块主体中的函数
```
该限制确保模块初始化是确定性的，并且在加载模块时不会执行任意代码。

**所需的类型注释：**

模块范围内的所有数据定义必须显式指定其类型。不允许单独使用 `:=` 进行类型推断：

<!--NoCompile-->
<!-- 05 -->
```verse
# 无效：缺少类型注释
BadModule := module:
    Value := 42  # 错误 3547：必须指定类型域

# 有效：显式类型注释
GoodModule := module:
    Value:int = 42  # OK：指定明确类型
```
这一要求使模块接口变得明确，并有助于单独编译和模块演化。

**有效模块内容：**

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
    # 具有显式类型的常量
    Version:int = 1
    AppName:string = "MyApp"

    # 功能
    Calculate(X:int):int = X * 2

    # 类、接口、结构
    data_class := class:
        Value:int

    data_interface := interface:
        GetValue():int

    data_struct := struct:
        X:float
        Y:float

    # 枚举
    status := enum:
        Active
        Inactive

    # 嵌套模块
    Nested := module:
        NestedFunction():void = {}

    # 类型别名
    coordinate := tuple(float, float)

    # 细化类型
    positive_int := type{X:int where X > 0}
```
<!-- #> -->

与函数、类或数据值不同，模块不是一流的
Verse中的公民。您不能将模块视为可以
在运行时存储、传递或操作。

**无法将模块分配给变量：**

<!--NoCompile-->
<!-- 07 -->
```verse
MyModule := module:
    Value<public>:int = 42

# 无效：不能将模块视为值
M:MyModule = MyModule  # 错误
```
模块纯粹作为命名空间和组织结构存在
编译时间。模块标识符 `MyModule` 只能用于
具体情况。

**无法将模块作为参数传递：**

<!--NoCompile-->
<!-- 08 -->
```verse
MyModule := module:
    X<public>:int = 1

# 无效：无法将模块作为参数传递
ProcessModule(M:module):void = {}  # 错误
ProcessModule(MyModule)  # 错误
```
没有可以在函数签名中使用的 `module` 类型。

**无法创建模块集合：**

<!--NoCompile-->
<!-- 09 -->
```verse
ModuleA := module:
    Value:int = 1

ModuleB := module:
    Value:int = 2

# 无效：无法创建模块元组或数组
Modules := (ModuleA, ModuleB)  # 错误
```
## 导入模块

导入系统的设计是明确且可预测的。不像
一些自动导入常用模块的语言或
搜索多个位置的依赖项，Verse 要求您
显式声明您要使用的每个外部模块。这个
明确性有助于防止命名冲突并建立依赖关系
清楚。

`using` 语句是导入模块的主要机制
进入你的Verse代码。它通常放置在文件的顶部，之前
任何其他代码定义，并使指定模块的内容
在您当前的范围内可用。

基本语法很简单 - 关键字 `using` 后跟
大括号中的模块路径：

<!--NoCompile-->
```verse
using { /Verse.org/Random }
using { /Fortnite.com/Devices }
using { /Verse.org/Simulation }
using { /UnrealEngine.com/Temporary/Diagnostics }
```
当您导入模块时，其所有公共成员都可以在
你的代码。但是，您仍然需要使用模块来限定它们
名称，除非名称明确。本资格要求
有助于保持代码清晰并防止意外使用错误
当多个模块定义相似名称时的定义。

**使用是一个语句，而不是一个表达式：**

`using` 指令是一个语句级声明，必须
显示在代码的顶层。您不能将其用作
表达式或将其嵌入到其他表达式中：

<!--NoCompile-->
<!-- 11 -->
```verse
# 无效：在表达式上下文中使用
# f():void = using{MyModule}  # ERROR 3669

# 无效：在有条件的情况下使用
# if (using{MyModule}, Condition?):
#     DoSomething()  # ERROR 3669

# 无效：在类/结构体/接口体中使用
# my_class := class:
#     使用 {MyModule} # 错误 3537
#     字段：整数

# 无效：在函数体中使用模块路径
# ProcessData():void =
#     使用{/MyProject/UtilityModule} # 错误 3669
#     Calculate()
```
模块 `using` 语句必须出现在文件或模块级别，而不是
嵌套在其他构造中。这确保导入是可见的
并且在声明的整个范围内保持一致。

虽然函数体中不允许使用路径导入模块，
Verse 确实支持带有局部变量的 **局部范围 `using`**
参数。请参阅下面的 [本地范围使用](#local-scope-using)
详细信息。

**使用放置有效：**

<!--NoCompile-->
<!-- 12 -->
```verse
# 在文件级别（最常见）
using { /Verse.org/Random }
using { /Verse.org/Simulation }

ProcessData():void =
    # 使用导入的函数
    Value := GetRandomFloat(0.0, 1.0)

# 在模块定义内
Utilities := module:
    using { /Verse.org/Random }

    GenerateId<public>():int =
        GetRandomInt(1, 1000000)
```
### 导入解析

当 Verse 遇到 `using` 语句时，它遵循特定的解析过程：

1. **绝对路径**（以 `/` 开头）从全局模块注册表解析
2. **相对路径**（不带前导 `/`）相对于当前模块的位置进行解析
3. **嵌套模块**可以通过其父模块访问

这个解析过程发生在编译时，这意味着所有
编译代码时，导入必须是可解析的。没有
Verse 中的运行时模块加载或动态导入。

### 本地与相对导入

对于您自己项目中的模块，您可以灵活地引用它们：

<!--NoCompile-->
<!-- 13 -->
```verse
# 从项目根目录绝对导入
using { /MyGameProject/Systems/Combat }

# 从同级文件夹导入
using { ../UI/MainMenu }

# 从同一目录导入
using { PlayerController }

# 从子目录导入
using { Subsystems/WeaponSystem }
```
绝对导入和相对导入之间的选择通常取决于您的
项目结构以及您是否计划重组您的项目
模块。重构时绝对导入更加稳定，而
相对导入可以使模块组更加可移植。

### 嵌套导入

嵌套模块在导入时需要特别注意。订单
在其中导入模块很重要，并且有多个有效的
方法：

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
# 方法一：先导入parent，再导入child
using { GameSystems }
using { Inventory }  # 假设库存在 GameSystems 中

# 方法 2：嵌套模块的直接路径
using { GameSystems.Inventory }

# 方法3：通过资格导入父级并访问子级
using { GameSystems }
# 稍后的代码：GameSystems.Inventory.Item

# 重要提示：此命令会导致错误
# 使用 { 库存 } # 错误：缺少库存
# using { GameSystems } # 太晚了，库存导入已经失败
```
<!-- #> -->

存在导入订单限制，因为 Verse 解析导入
依次。当您直接导入嵌套模块时，Verse 需要
首先了解其父模块。这就是为什么导入父级
在孩子总是工作之前，而相反的顺序失败。

### 带有 import 的模块别名

`import` 表达式为模块创建本地别名，绑定
它的名称路径。与 `using` 不同，它带来了模块的公共
成员直接进入范围，`import`允许您通过
带点符号的别名：

<!--NoCompile-->
<!-- 14b -->
```verse
# 使用：会员可直接使用
using { /MyProject/Utilities }
Result := HelperFunction()  # HelperFunction 在范围内

# 导入：通过别名访问的成员
Utils := import(/MyProject/Utilities)
Result := Utils.HelperFunction()  # 通过别名访问
```
当您想要避免名称冲突，或者当您
需要在代码中明确定义的来源：

<!--NoCompile-->
<!-- 14c -->
```verse
Physics := import(/MyProject/Systems/Physics)
Graphics := import(/MyProject/Systems/Graphics)

# 明确正在使用哪个变换
PhysicsTransform := Physics.Transform{}
GraphicsTransform := Graphics.Transform{}
```
使用 `import` 创建的模块别名在所有片段中都可见
在同一模块内。 `import` 也可以与 `using` 组合使用
为模块添加别名并将其成员纳入范围：

<!--NoCompile-->
<!-- 14d -->
```verse
Graphics := import(/MyProject/Systems/Graphics)
using { Graphics }  # 现在图形会员也可以直接使用
```
请注意， `import` 仅适用于模块路径。正在尝试导入
解析为类或其他非模块定义的路径是
错误。

### 范围和可见性

导入具有文件范围 - 它们仅影响它们所在的文件
出现。如果同一模块中有多个 `.verse` 文件，每个文件
文件需要自己的外部模块导入语句。然而，
同一模块内的文件可以看到彼此的定义，而无需
进口：

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
# 文件：player_module/health.verse
health_component := class:
    CurrentHealth:float = 100.0

# 文件：player_module/armor.verse
# health_component 不需要导入，因为它位于相同模块中
armor_component := class:
    HealthComp:health_component = health_component{}
```
<!-- #> -->

### 导入冲突

当两个导入的模块定义同名成员时，需要消除歧义：

<!--NoCompile-->
<!-- 16 -->
```verse
using { /GameA/Combat }
using { /GameB/Combat }

# 都模块可以定义计算两个损坏
# 您必须使用限定名称：
DamageA := Combat.CalculateDamage(10.0)  # 错误：不明确
DamageA := (/GameA/Combat:)CalculateDamage(10.0)  # OK：完全合格
DamageB := (/GameB/Combat:)CalculateDamage(10.0)  # OK：完全合格
```
### 限定名称

导入后，您可以使用限定的引用模块内容
名称。 Verse 提供两种形式的限定： 标准点
大多数情况下的表示法，以及特殊限定的访问语法
消歧义。

当您需要消除同名标识符之间的歧义时
来自不同的模块，或者当您想明确指定
标识符的范围，使用限定访问表达式
括号和冒号：


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
# 限定语法访问：(qualifier:)identifier

using { CombatModule }
using { MagicModule }

ProcessDamage():void =
    # 都模块定义了计算两个损坏
    PhysicalDamage := (CombatModule:)CalculateDamage(100.0)
    MagicalDamage := (MagicModule:)CalculateDamage(100.0)

    # 显式限定本地标识符与模块标识符
    LocalItem := item{Name := "Sword"}  # 本地定义
    ModuleItem := (InventoryModule:)item{Name := "Shield"}  # 来自模块
```
限定访问表达式 `(module:)identifier` 在以下几种情况下特别有用：

1. **解决命名冲突**：当多个导入的模块导出相同的标识符时
2. **显式作用域**：当你想要明确标识符来自哪个模块以提高可读性时
3. **访问隐藏名称**：当本地定义隐藏模块成员时
4. **通用编程**：使用可能计算限定符的参数类型时

## 模块作用域变量

在模块范围内定义的变量对于该变量在范围内的任何游戏实例都是全局的。

对模块范围定义的限制：- 模块范围内不允许直接 `var` 声明简单类型（如 `var X:int = 0`）
- 具有 `<allocates>` 的 `<unique>` 类的实例可以在模块范围内创建，只要它们的构造实际上不分配可变内存
- 对于持久可变状态，请使用 `weak_map` 和适当的键类型（见下文）

使用 `weak_map(session, t)` 作为在游戏会话期间持续存在的变量：

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
使用 `weak_map(player, t)` 获取跨游戏会话持续存在的数据：

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

## 元宇宙和出版

当您将模块发布到Metaverse时，模块路径变为
全局可访问，其公共成员成为模块的一部分
API，从那时起模块必须保持向后
兼容性。

下面的例子展示了进化是如何运作的：

<!--NoCompile-->
<!-- 22 -->
```verse
# 初次发表
Thing<public>:rational = 1/3

# 有效更新：
# - 更改值（而不是类型）
Thing<public>:rational = 10/3

# - 使类型更加具体（子类型）
Thing<public>:int = 20  # nat 是 int 的子类型

# 无效更新（将被拒绝）：
# - 删除该成员
# - 更改为不兼容的类型
# Thing<public>:string = "hello"  # Would fail
```
## 局部限定符

`(local:)` 限定符可以消除内部标识符的歧义
功能。这对于进化兼容性至关重要——当外部
模块在代码发布后添加新的公共定义，
`(local:)` 确保您的本地定义优先。

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
# 外部模块在您的代码发布后添加 ShadowX
ExternalModule<public> := module:
    ShadowX<public>:int = 10  # 稍后添加！

MyModule := module:
    using{ExternalModule}

    # 不使用 (local:)——发生遮蔽冲突
    # Foo():float =
    #     ShadowX:float = 0.0 # 错误：与ExternalModule.ShadowX冲突
    #     影子X

    # 使用 (local:)——可明确消除歧义
    Foo():float =
        (local:)ShadowX:float = 0.0  # 局部变量
        (local:)ShadowX              # 返回 0.0，而不是 10
```
<!-- #> -->

`(local:)` 限定符可以在以下上下文中使用：

**功能参数：**

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

**对于循环变量：**

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

**如果条件：**

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
**块范围：**

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
`(local:)` 限定符 **不能** 在这些上下文中使用：


**嵌套范围限制：**

目前，您**无法**在嵌套块中重新定义 `(local:)` 限定标识符：

<!--NoCompile-->
```verse
# 错误：无法重新定义本地标识符
F((local:)X:int):int =
    block:
        (local:)X:float = 5.5  # 错误：X 已在函数中定义
    (local:)X
```
此限制可能会在未来版本中取消，以支持更复杂的范围模式。

## 自动限定

!!!警告“未发布的功能”
    自动资格尚未完全实施。本节记录了当前不可用的计划功能。在正式发布之前，不应依赖此处描述的行为，特别是有关编译器如何转换已发布代码中的标识符的行为。

当您编写 Verse 代码时，您可以使用简单的、非限定的标识符
清晰度和可读性。然而，Verse 编译器会在内部
将所有标识符转换为明确的完全限定形式
明确其范围和来源。这个过程，称为**自动
资格**，将确保每个标识符都是明确的并且可以
被精确地解析为一个定义。了解自动限定将帮助您了解 Verse 如何
将解析名称、为什么会发生某些错误以及模块系统如何
即使在具有许多模块的复杂代码库中也能保持正确性
重叠的名字。

编译器将限定几类标识符：

1. **顶级定义** - 包范围内的函数、变量、类、模块
2. **类型引用** - 所有类型，包括内置类型，例如 `int` 和 `string`
3. **函数参数** - 局部参数获取 `(local:)` 限定符
4. **类和接口成员** - 方法、字段、嵌套在复合类型中
5. **模块成员** - 模块内的公共和内部定义
6. **嵌套作用域** - 嵌套模块、类和函数内的引用

Verse 使用多种模式根据标识符的范围来限定标识符：**包级限定**：包根部的定义
符合包路径：

<!--NoCompile-->
```verse
# 你写的：
Function(X:int):int = X

# 编译器如何看待它：
(/YourPackage:)Function((local:)X:(/Verse.org/Verse:)int):(/Verse.org/Verse:)int = (local:)X
```
包路径 `/YourPackage` 成为 `Function` 的限定符，
而参数 `X` 获得特殊的 `(local:)` 限定符，并且
内置类型 `int` 通过其标准库路径进行限定
`/Verse.org/Verse`。

**局部作用域限定**：函数参数和局部变量用`(local:)`标记：

<!--NoCompile-->
```verse
# 你写的：
ProcessValue(Input:int, Multiplier:int):int =
    Input * Multiplier

# 编译器如何看待它：
(/YourPackage:)ProcessValue((local:)Input:(/Verse.org/Verse:)int, (local:)Multiplier:(/Verse.org/Verse:)int):(/Verse.org/Verse:)int =
    (local:)Input * (local:)Multiplier
```
**嵌套范围限定**：类、接口或模块中的成员通过其容器的路径进行限定：

<!--NoCompile-->
```verse
# 你写的：
player_class := class:
    Health:float = 100.0

    TakeDamage(Amount:float):void =
        set Health = Health - Amount

# 编译器如何看待它：
(/YourPackage:)player_class := class:
    (/YourPackage/player_class:)Health:(/Verse.org/Verse:)float = 100.0

    (/YourPackage/player_class:)TakeDamage((local:)Amount:(/Verse.org/Verse:)float):(/Verse.org/Verse:)void =
        set (/YourPackage/player_class:)Health = (/YourPackage/player_class:)Health - (local:)Amount
```
请注意 `Health` 和 `TakeDamage` 如何用 `/YourPackage/player_class` 进行限定以表明它们是该类的成员。

**模块成员资格**：模块内的定义通过模块路径进行限定：

<!--MoCompile-->
```verse
# 你写的：
Config := module:
    MaxPlayers<public>:int = 100

    GetPlayerLimit<public>():int = MaxPlayers

# 编译器如何看待它：
(/YourPackage:)Config := module:
    (/YourPackage/config:)MaxPlayers<public>:(/Verse.org/Verse:)int = 100

    (/YourPackage/config:)GetPlayerLimit<public>():(/Verse.org/Verse:)int =
        (/YourPackage/config:)MaxPlayers
```
所有内置类型均符合其标准库的要求
路径。这使得这些类型的来源变得明确
与用户定义的类型保持一致：

<!--NoCompile-->
```verse
# 常见的内置类型及其完整资格：
int       → (/Verse.org/Verse:)int
float     → (/Verse.org/Verse:)float
string    → (/Verse.org/Verse:)string
logic     → (/Verse.org/Verse:)logic
message   → (/Verse.org/Verse:)message
```
当您编写 `X:int` 时，编译器会将其扩展为 `X:(/Verse.org/Verse:)int`，从而使类型的来源明确。

### 示例

这是一个更现实的示例，展示了资格如何在多个范围内发挥作用：

<!--NoCompile-->
```verse
# 你写的：
GameSystem := module:
    BaseValue:int = 42

    Calculator := module:
        Multiplier:int = 2

        Calculate(Input:int):int =
            Input * Multiplier + BaseValue

# 编译器将如何看待它（实现时）：
(/YourGame:)GameSystem := module:
    (/YourGame/GameSystem:)BaseValue:(/Verse.org/Verse:)int = 42

    (/YourGame/GameSystem:)Calculator := module:
        (/YourGame/GameSystem/Calculator:)Multiplier:(/Verse.org/Verse:)int = 2

        (/YourGame/GameSystem/Calculator:)Calculate((local:)Input:(/Verse.org/Verse:)int):(/Verse.org/Verse:)int =
            (local:)Input * (/YourGame/GameSystem/Calculator:)Multiplier + (/YourGame/GameSystem:)BaseValue
```
注意如何：

- 参数 `Input` 为 `(local:)`
- `Multiplier` 通过其包含的模块路径进行限定
- `BaseValue` 使用外部模块路径进行限定
- 所有类型引用均符合 Verse 标准库路径

**有关影子的重要说明**：自动资格仅适用于已发布的代码，不适用于您的源代码。 Verse 目前执行严格的反阴影规则，以防止混淆并保持代码清晰度。例如，以下代码**无法**编译：

<!--NoCompile-->
```verse
# 这不会编译 - 不允许隐藏
Thing := module:
    Thing := module:  # 错误：无法隐藏外部事物
        Potato := module{}
```
即使使用自动限定，嵌套定义也不能隐藏具有相同名称的外部定义。如果您想故意隐藏某些内容，则必须使用显式限定符来明确您的意图。这种严格的方法有助于防止错误并使代码演进更安全。

### 使用 `using` 限定

当您使用 `using` 导入模块时，编译器仍然限定所有标识符，但它可以将非限定名称解析为导入的模块：

<!-- NoCompile-->
```verse
# 你写的：
using { /Verse.org/Random }

GenerateRandomValue():float =
    GetRandomFloat(0.0, 1.0)

# 编译器如何看待它：
using { /Verse.org/Random }

(/YourGame:)GenerateRandomValue():(/Verse.org/Verse:)float =
    (/Verse.org/Random:)GetRandomFloat(0.0, 1.0)
```
编译器根据 `using` 语句将 `GetRandomFloat` 解析为 `(/Verse.org/Random:)GetRandomFloat`。

### 何时需要限定

一旦实施，您将很少需要在正常情况下考虑自动或手动资格
开发，因为编译器将透明地处理它。然而，
理解它在几种情况下会有所帮助：

**调试名称解析错误**：当编译器报告时
不明确或未解析的标识符，了解资格有助于
你明白为什么：

<!--NoCompile-->
```verse
using { /ModuleA }
using { /ModuleB }

# 两个模块都定义了计算
Result := Calculate(10)  # 错误：不明确 - 可能是任一模块
```
发生错误的原因是编译器无法自动限定 `Calculate` - 它可能是 `(/ModuleA:)Calculate` 或 `(/ModuleB:)Calculate`。

**隐藏冲突**：当局部变量与模块成员同名时：

<!--NoCompile-->
```verse
MyModule := module:
    Value:int = 100

    Process(Value:int):int =
        # 如果没有明确的限定，这是不明确的
        Value + Value  # 哪个值？模块还是参数？
```
编译器需要限定来区分 `(/MyModule:)Value` 和 `(local:)Value`。

**理解错误消息**：编译器有时会出现错误消息
显示限定名称以准确识别哪个定义
涉及：
```
Error: Cannot assign (/Verse.org/Verse:)string to (/Verse.org/Verse:)int at line 42
```
这清楚地表明错误涉及内置 `string` 和
`int` 类型，而不是具有相同名称的用户定义类型。

**使用生成的或反射的代码**：生成的工具
Verse代码或分析代码结构以限定形式工作，因此
了解它有助于使用此类工具。

### 显式限定

虽然编译器会自动限定标识符，但您也可以
使用限定访问语法显式限定它们
`(qualifier:)identifier`。当您想要覆盖时这很有用
自动解决或明确您的意图：

<!-- 45 FAILURE
  Line 11: Verse compiler error V3509: The assignment's left hand expression type `int` cannot be assigned to
-->
```verse
GameSystem := module:
    Value:int = 100

    # 明确限定以避免任何歧义
    GetValue():int = (GameSystem:)Value

    # 使用参数的本地限定符
    SetValue((local:)Value:int):void =
        set (GameSystem:)Value = (local:)Value
```
在以下情况下，明确的资格特别有价值：

- 解决导入模块之间的命名冲突
- 使代码更加自文档化
- 覆盖阴影行为
- 使用动态或计算限定符

<a id="local-scope-using"></a>
## 局部作用域的 `using`

虽然模块级 `using` 通过路径导入模块，但 Verse 也
支持函数体内的**局部作用域 `using`** 以启用
从局部变量和参数进行成员访问推断。这个
当处理具有多个对象的对象时，该功能使代码更加清晰
会员访问。

局部作用域 `using` 采用局部变量或参数标识符
（不是模块路径）并使其成员无需显式即可访问
资质：

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
    # 显式成员访问
    Print(E.Name)
    E.UpdateHealth(-10)
    Print("{E.Health}")

    # 通过本地使用 - 推断成员访问
    using{E}
    Print(Name)         # 推断为：E.Name
    UpdateHealth(-10)   # 推断为：E.UpdateHealth(-10)
    Print("{Health}")       # 推断为：E.Health
```
<!-- #> -->

`using{E}` 表达式使 `E` 的所有成员在当前范围内无需 `E.` 前缀即可访问。

### 使用局部变量

本地 `using` 适用于同一函数中定义的变量：

<!--versetest
player := class:
    var Name:string = ""
    var Score:int = 0
-->
<!-- 47 -->
```verse
CreateAndProcess():void =
    Player := player{Name := "Alice", Score := 100}

    # 不使用
    Print(Player.Name)
    set Player.Score = Player.Score + 50

    # 随着使用
    using{Player}
    Print(Name)         # 推断为：Player.Name
    set Score = Score + 50  # 推断为：Player.Score
```
### 块作用域

`using` 范围仅限于它出现的块和任何嵌套块：

**在同一块中使用：**

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
        UpdateField(Value)  # 推断为：Data.UpdateField(Data.Value)
    # 此处无法再访问数据成员
```
**从外部块使用：**

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
        using{Data}  # 可以使用外部作用域的变量
        UpdateField(Value)  # 作品 - 范围内的数据
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
    using{Data}  # 适用于此块和嵌套块

    block:
        # 内部块继承外部使用
        UpdateField(Value)  # 残余推断 Data.UpdateField(Data.Value)
```
### 顺序

成员推断仅在遇到 `using` 表达式之后才起作用：

<!--NoCompile-->
```verse
# 错误：使用前无法推断
ProcessData(Data:data_record):void =
    UpdateField()  # 错误 - 使用前
    using{Data}
    UpdateField()  # 好的 - 使用后

# 错误：使用范围不会向后扩展
ProcessData(Data:data_record):void =
    block:
        using{Data}
        UpdateField()  # OK - 在使用范围内
    UpdateField()  # 错误 - 使用范围结束后
```
`using` 语句充当声明点 - 推理不具有追溯力。

### 冲突解决

同一范围内可以有多个 `using` 表达式，但必须显式限定冲突的成员名称：

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
    # 现在两者都在范围内
    Print("{Armor}")      # Enemy.Armor (no conflict with Player)

    # 错误：必须限定冲突
    # Print(Health)   # Ambiguous - both have Health
    # Print(GetInfo())  # Ambiguous - both have GetInfo

    # 必须限定冲突成员
    Print("{Player.Health}")
    Print("{Enemy.Health}")
    Print(Player.GetInfo())
    Print(Enemy.GetInfo())
```
<!-- #> -->

当成员存在于多个 `using` 上下文中时，您必须明确限定以消除歧义。

### 可变成员

本地 `using` 通过 `set` 关键字处理可变字段：

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

    # 可变字段访问
    set Volume = 0.8     # 推断为：设置Settings.Volume = 0.8
    set Quality = 3      # 推断为：设置Settings.Quality = 3
```
<!-- #> -->

## 故障排除

使用模块时，您可能会遇到各种问题。了解这些常见问题及其解决方案将帮助您更有效地调试与模块相关的错误。

### 模块未找到错误

**问题**：当您尝试导入模块时，编译器报告找不到该模块。

**常见原因和解决方案**：

1. **路径不正确**：仔细检查 `using` 语句中的模块路径。请记住，路径区分大小写。

<!--NoCompile-->
<!-- 54 -->
```verse
# 错误：不同情况
using { /verse.org/random }  # 错误：找不到模块

# 正确：正确的情况
using { /Verse.org/Random }  # 作品
```
2. **缺少父模块导入**：导入嵌套模块时，确保先导入父模块。

<!--NoCompile-->
<!-- 55 -->
```verse
# 错误：孩子先于父母
using { Inventory }  # 如果库存，则出现错误

# 正确：父母第一
using { GameSystems }
using { Inventory }
```
3. **文件位置不匹配**：确保您的文件结构与模块结构匹配。如果您有一个名为 `PlayerSystems` 的文件夹，则该文件夹中的所有文件都是 `PlayerSystems` 模块的一部分。

### 访问被拒绝错误

**问题**：您无法访问导入模块的成员。

**常见原因和解决方案**：

1. **缺少访问说明符**：没有 `<public>` 说明符的成员默认为内部成员。

<!--NoCompile-->
<!-- 56 -->
```verse
# 在模块A中
SecretValue:int = 42  # 默认为内部
PublicValue<public>:int = 100  # 明确公开

# 在另一个模块中
using { ModuleA }
X := ModuleA.SecretValue  # 错误：无法访问
Y := ModuleA.PublicValue  # 作品
```
2. **受保护或私有成员**：这些成员在其定义范围之外不可访问。

<!--NoCompile-->
<!-- 57 -->
```verse
# 在一个班级里
class_a := class:
    PrivateField<private>:int = 10
    ProtectedField<protected>:int = 20
    PublicField<public>:int = 30

# 课外
Obj := class_a{}
X := Obj.PrivateField  # 错误：私人
Y := Obj.PublicField   # 作品
```
### 循环依赖错误

**问题**：两个模块尝试相互导入，从而创建循环依赖关系。

**解决方案**：重构代码以避免循环依赖：

1. **提取公共代码**：将共享定义移动到两者都可以导入的第三个模块。
2. **使用接口**：在单独的模块中定义接口以打破依赖循环。
3. **重新考虑架构**：循环依赖通常表明需要重新思考的设计问题。

### 名称冲突错误

**问题**：两个导入的模块定义了具有相同名称的成员。

**解决方案**：使用完全限定名称来消除歧义：

<!--NoCompile-->
```verse
using { /GameA/Combat }
using { /GameB/Combat }

# 暧昧
Damage := CalculateDamage(10.0)  # 错误：哪个计算损坏？

# 显式的
DamageA := /GameA/Combat.CalculateDamage(10.0)  # 清除
DamageB := /GameB/Combat.CalculateDamage(10.0)  # 清除
```
### 持久性问题

**问题**：模块范围的变量没有按预期持续存在。

**常见原因和解决方案**：

1. **使用了错误的类型**：确保您使用 `weak_map(player, t)` 来实现玩家持久性。
2. **类型不可持久**：检查您的自定义类型是否具有 `<persistable>` 说明符。
3. **初始化时机**：确保您在游戏生命周期中的正确时间初始化持久数据。

### 本地限定符冲突

**问题**：本地标识符与模块成员冲突时出现隐藏错误。

**解决方案**：使用 `(local:)` 限定符来消除歧义：

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
        (ModuleX:)Value + (local:)Value  # 明显区分
```
<!-- #> -->
