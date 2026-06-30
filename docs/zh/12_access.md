# 访问说明符

访问说明符控制代码的可见性和可访问性
元素。它们提供了一系列细致入微的访问级别，
反映现代软件开发的复杂现实，
特别是在一个持久的、全球性的元宇宙的背景下
来自许多作者的代码必须安全共存。

定义了五个主要可见性级别，形成了仔细的
设计的层次结构，每个层次结构服务于特定的架构
需要。了解何时以及为何使用每个级别对于
创建结构良好、可维护的代码。

|说明符|能见度|用途 |
|------------|------------|--------|
| `<public>` |普遍可用 |供外部使用的成员 |
| `<internal>` |仅在模块内（默认） |模块私有实现 |
| `<private>` |仅在直接封闭范围内 |本地到类/结构 |
| `<protected>` |当前类别和亚型|继承层次结构 |
| `<scoped>` |当前范围和封闭范围 |特殊用例|
| `<epic_internal>` | /Verse.org、/UnrealEngine.com 和 /Fortnite.com 域的范围 | `<epic_internal>` 只能由 Epic 编写的代码使用 |

## 公共

`<public>` 说明符代表最广泛的访问级别，
使任何代码都可以普遍访问标识符
引用包含的模块或类型。当您将某物标记为
公开，您对其可用性做出了坚定的承诺，并且
稳定性：

<!--versetest
Test01 := module:
    PlayerManager<public> := module:
        MaxPlayers<public>:int = 100

        player<public> := class:
            Name<public>:string
            Level<public>:int = 1
<#
-->
<!-- 01 -->
```verse
PlayerManager<public> := module:
    MaxPlayers<public>:int = 100

    player<public> := class:
        Name<public>:string
        Level<public>:int = 1
```
<!-- #> -->

公共成员构成了您的代码与外部之间的契约
世界。在元宇宙背景下，公开声明尤其重要
重要的是因为它们代表了潜在的扩展的保证
永远——一旦发布，删除或不兼容地改变公众
会员违背了您对依赖其他开发者的承诺
在你的代码上。

public 说明符可以应用于模块、类、接口、
结构体、枚举、方法和数据成员。当应用于类型时
定义本身，它使该类型可以在其外部使用
定义模块。当应用于类型中的成员时，它使这些
任何有权访问该实例的代码都可以访问该成员
类型。

## 受保护

`<protected>` 说明符在公共和
私有，允许在定义类和任何类中访问
继承自它。该级别专门用于支持
继承层次结构同时保持封装：

<!--versetest
vector3:=class{}
MaxHealth:int=1
-->
```verse
game_entity := class:
    var Position<protected>:vector3 = vector3{x:=0.0, y:=0.0, z:=0.0}
    var Health<protected>:int = 100

    UpdatePosition<protected>(NewPos:vector3):void =
        set Position = NewPos
        OnPositionChanged()

    OnPositionChanged<protected>():void = {}  # 可被子类覆盖

player := class(game_entity):
    MoveToSpawn():void =
        UpdatePosition(GetSpawnLocation())  # 可以访问受保护的成员
        set Health = MaxHealth              # 可以修改受保护的变量
```
受保护的访问启用模板方法模式和其他
基于继承的设计，同时防止外部代码
访问应保留在类中的实现细节
层次结构。这对于游戏实体和其他实体尤其有价值
父类需要共享行为的分层结构
与孩子们在一起，而不将这种行为暴露给世界。

## 私人

`<private>` 说明符提供最严格的访问控制，
限制直接封闭范围的可见性。私人
成员是真正可以更改的内部实现细节
自由地不影响任何外部代码：

<!--versetest
item:=struct{Weight:float=0.0}
inventory := class:
    var Items<private>:[]item = array{}
    var Capacity<private>:int = 20
    var CurrentWeight<private>:float = 0.0
    MaxWeight:float=20.0

    AddItem<public>(NewItem:item, At:int)<transacts><decides>:void =
        ValidateCapacity[NewItem]
        set Items[At] = NewItem
        set CurrentWeight = CurrentWeight + NewItem.Weight

    ValidateCapacity<private>(NewItem:item)<reads><decides>:void =
        Items.Length < Capacity
        CurrentWeight + NewItem.Weight <= MaxWeight
<#
-->
<!-- 03 -->
```verse
inventory := class:
    var Items<private>:[]item = array{}
    var Capacity<private>:int = 20
    var CurrentWeight<private>:float = 0.0
    MaxWeight:float=20.0

    AddItem<public>(NewItem:item, At:int)<transacts><decides>:void =
        ValidateCapacity[NewItem]
        set Items[At] = NewItem
        set CurrentWeight = CurrentWeight + NewItem.Weight

    ValidateCapacity<private>(NewItem:item)<reads><decides>:void =
        Items.Length < Capacity
        CurrentWeight + NewItem.Weight <= MaxWeight
```
<!-- #> -->

私有成员是封装的构建块。他们允许
您可以维护不变量、隐藏复杂性并创建干净的
抽象。对私有成员的更改永远不会破坏外部代码，
让您可以自由地重构和优化实施细节
根据需要。

## 内部

`<internal>` 说明符，这是没有时的默认访问级别
提供了说明符，使成员可以在定义范围内访问
模块但不在其外部。这创造了一个自然的边界
需要共享实现细节的协作代码，而无需
公开曝光他们：

<!--versetest
game_entity:=class{}
collision_info:=class{}
ApplyGravity(:game_entity,:float):void={}
CheckCollisions(:game_entity):void={}

Physics := module:
    gravity_constant:float = 9.81

    collision_detector := class<abstract>:
        DetectCollision<internal>(A:game_entity, B:game_entity):?collision_info

    physics_world := class:
        var Entities<internal>:[]game_entity = array{}

        SimulateStep<internal>(DeltaTime:float):void =
            for (Entity : Entities):
                ApplyGravity(Entity, DeltaTime)
                CheckCollisions(Entity)
<#
-->
<!-- 04 -->
```verse
Physics := module:
    # 内部类型和常量
    gravity_constant:float = 9.81

    collision_detector := class<abstract>:
        DetectCollision<internal>(A:game_entity, B:game_entity):?collision_info

    physics_world := class:
        var Entities<internal>:[]game_entity = array{}

        SimulateStep<internal>(DeltaTime:float):void =
            for (Entity : Entities):
                ApplyGravity(Entity, DeltaTime)
                CheckCollisions(Entity)
```
<!-- #> -->

内部访问非常适合模块范围的实用程序、共享
实现细节，以及多个类的辅助函数
模块内需要但不应该暴露给外部代码。它
在模块的公共接口和
其实施机制。

## 范围

`<scoped>` 说明符创建自定义访问边界
模块或代码位置。与固定可见度级别不同
`public`、`internal` 和 `private`、`scoped` 访问允许您
显式授予对特定模块的访问权限，同时排除所有模块
other——在程序之间创建一种“朋友”关系
实体。

### 范围定义

使用 `scoped{...}` 表达式创建范围访问级别，
它需要一个或多个模块引用：

<!-- NoCompile -->
```verse
Collaboration := module:
    # 创建一个包含 ModuleA 和 ModuleB 的范围
    Shared<public> := scoped{ModuleA, ModuleB}

    # 此类只能在ModuleA和ModuleB中访问
    SharedResource<Shared> := class:
        Data<public>:int = 42
```
作用域定义创建一个访问级别，然后可以将其用作
类、函数、变量和其他的说明符
定义。任何列出的实体中的代码都可以访问
作用域成员，而这些模块之外的代码则不能——即使可以
查看包含范围。

### 跨模块协作

范围访问最强大的用途是启用受控
模块之间的协作。可以在一个定义中创建一个
模块但作用域为另一个模块，使其可以在需要的地方访问
同时将其隐藏在其他地方：

<!--versetest
bounding_box:=class{}
Graphics := module:
    CollidableShape<scoped{Physics}> := interface:
        GetBounds():bounding_box

Physics := module:
    using{Graphics}

    sphere_collider := class<abstract>(CollidableShape):
        GetBounds<override>():bounding_box
<#
-->
<!-- 06 -->
```verse
Graphics := module:
    # 定义物理模块范围内的接口
    CollidableShape<scoped{Physics}> := interface:
        GetBounds():bounding_box

Physics := module:
    using{Graphics}

    # 即使界面是在图形中定义的，物理也可以实现该界面
    sphere_collider := class<abstract>(CollidableShape):
        GetBounds<override>():bounding_box
```
<!-- #> -->

这种模式允许图形定义物理上的契约
实施而不公开公开这些实施细节。的
接口存在于两个模块之间的边界处，但实际上并不存在
任一模块的公共 API 的一部分。

您可以将定义范围限定到多个模块，从而创建共享的
私人协作空间：

<!--versetest
Gameplay := module:
    SharedGameplayScope := scoped{Inventory, Crafting}

    Item<SharedGameplayScope> := class:
        ID<public>:int
        Properties<public>:[string]string

    CreateItem<SharedGameplayScope>(TheID:int):Item = Item{ID:=TheID, Properties:=map{}}

Inventory := module:
    using{Gameplay}

    AddToInventory(ItemID:int):void =
        NewItem := CreateItem(ItemID)

Crafting := module:
    using{Gameplay}

    CraftItem(Recipe:[]int)<decides>:Item =
        CreateItem(Recipe[0])
<#
-->
<!-- 07 -->
```verse
Gameplay := module:
    # 此范围包括库存和制作模块
    SharedGameplayScope := scoped{Inventory, Crafting}

    # 物品可以通过库存和制作来访问
    Item<SharedGameplayScope> := class:
        ID<public>:int
        Properties<public>:[string]string

    # 两个系统均可使用工厂功能
    CreateItem<SharedGameplayScope>(TheID:int):Item = Item{ID:=TheID, Properties:=map{}}

Inventory := module:
    using{Gameplay}

    AddToInventory(ItemID:int):void =
        NewItem := CreateItem(ItemID)  # 可以访问作用域函数
        # 实施...

Crafting := module:
    using{Gameplay}

    CraftItem(Recipe:[]int)<decides>:Item =
        # 可以创建项目并访问其属性
        CreateItem(Recipe[0])
```
<!-- #> -->

### 范围读或写访问

与其他访问说明符一样，作用域可以单独应用来读取
并对变量进行写操作：

<!--  BUG?  Or at least unhelpful error message

a:=class<computes>{}
F()<computes>:a= a{}
b := class{ G:a = F() }

Gives:
  Line 8: Verse compiler error V3582: Divergent calls (calls that might not complete) cannot be used to define data-members.
-->


<!--versetest
ModuleA:=module{}
ModuleB:=module{}
game_state:=class{}

SharedScope := scoped{ModuleA, ModuleB}

state_manager := class:
    var<SharedScope> GameState<public>:game_state = game_state{}

    var<SharedScope> SyncCounter<SharedScope>:int = 0
<#
-->
<!-- 08 -->
```verse
SharedScope := scoped{ModuleA, ModuleB}

state_manager := class:
    # 公共读取权限，但只有 ModuleA 和 ModuleB 可以读取
    var<SharedScope> GameState<public>:game_state = game_state{}

    # 只有 ModuleA 和 ModuleB 可以读取或写入该内部状态
    var<SharedScope> SyncCounter<SharedScope>:int = 0
```
<!-- #> -->

此模式对于多个共享状态特别有用
模块需要在不公开公开写访问权限的情况下进行协调。

### 可见性和访问路径

范围访问的一个重要微妙之处在于它授予对
特定成员，但不创建中间类型或模块
可见。要访问作用域成员，您必须能够看到整个
它的路径：

<!-- NoCompile -->
```verse
Outer := module:
    # 内部到外部
    Inner := module:
        # 范围限定为 TargetModule
        SharedClass<scoped{TargetModule}> := class:
            Value:int = 42

TargetModule := module:
    using{Outer}

    # 错误：看不到 Outer.Inner，因为 Inner 是 Outer 的内部
    # 即使 SharedClass 的范围仅限于我们
    UseShared():void = Outer.Inner.SharedClass{}
```
对于工作范围内的访问，包含范围必须是
可访问（公共或也适当地限定范围），或限定范围的成员
必须通过公开它的公共接口进行访问。

一个定义只能有一个范围访问级别 - 您不能应用
多作用域说明符：

<!-- NoCompile-->
```verse
# 错误：不能有多个访问级别说明符
InvalidScope<scoped{ModuleA}><scoped{ModuleB}> := class{}
```
### 作用域访问和继承

当类成员具有范围访问权限时，重写中的成员
子类可以按照正常情况维持或缩小访问范围
继承规则：

<!--versetest
ModuleA:=module{}
ModuleB:=module{}
SharedScope := scoped{ModuleA, ModuleB}

base := class:
    ComputeValue<SharedScope>():int = 42

derived := class(base):
    ComputeValue<override>():int = 100
<#
-->
<!-- 11 -->
```verse
SharedScope := scoped{ModuleA, ModuleB}

base := class:
    # 仅可在 ModuleA 和 ModuleB 中访问
    ComputeValue<SharedScope>():int = 42

derived := class(base):
    # 可以使用相同或更严格的访问权限进行覆盖
    ComputeValue<override>():int = 100  # 现在位于该模块的内部
```
<!-- #> -->

### 使用 Scoped 作为 API 边界

范围访问擅长创建受控 API 边界，其中
某些功能应该在特定模块之间共享，但是
不作为公共接口的一部分公开：

<!-- NoCompile -->
```verse
Networking := module:
    # 需要网络访问的模块的公共范围
    NetworkScope<public> := scoped{PlayerSystem, Matchmaking, Telemetry}

    # 适用于特定系统的核心网络
    SendPacket<NetworkScope>(Data:[]uint8):void =
        # 实施...

    # 内部统计
    var<NetworkScope> BytesSent<NetworkScope>:int = 0
```
这创建了一个明确的架构边界——只有模块
范围中列出的可以访问网络原语，而其他
代码必须使用更高级别的公共 API。

### 设计考虑因素

范围访问代表了架构之间的承诺
模块。有效使用时：

- 使用范围进行合法的跨模块协作，但不这样做
  属于公共API
- 将范围定义保留在可以记录和维护的模块级别
- 更喜欢显式模块的作用域而不是深度嵌套的作用域
- 考虑受保护访问或内部访问对于您的用例是否更简单
- 记录为什么特定模块包含在范围内

作用域说明符填补了内部和公共之间的独特空白
访问，实现复杂的模块架构，其中多个
组件需要密切协作而不暴露那些
更广泛的代码库的实现细节。

## 分离读写访问

一项创新功能是能够应用不同的访问权限
对同一对象进行读写操作的说明符
变量。这种细粒度的控制允许您创建变量
具有广泛的可读性但可写性较窄，实现了常见的
类似只读属性的模式优雅地：

<!--versetest
game_state := class:
    var<protected> Score<public>:int = 0

    var<private> PlayerCount<public>:int = 0

    var<private> SessionID<internal>:string
<#
-->
<!-- 13 -->
```verse
game_state := class:
    # 公共读，保护写
    var<protected> Score<public>:int = 0

    # 公共读，私有写
    var<private> PlayerCount<public>:int = 0

    # 内部读、私有写
    var<private> SessionID<internal>:string
```
<!-- #> -->

这个双说明符系统解决了面向对象中的一个常见问题
在您想要公开状态以供读取的地方进行编程，而无需
允许外部修改。而不是需要 getter 方法
或属性语法，Verse 使这种模式成为一流的语言
功能。

该语法将写访问说明符放在 `var` 关键字上，并且
标识符本身的读访问说明符。这个视觉
分离使阅读时访问级别立即清晰
代码。写说明符必须至少与读说明符一样受到限制
说明符 — 您不能写入私有可读的变量
但可公开写入，因为这会违反基本封装
原则。

## 最佳实践

了解何时使用每个访问级别需要考虑
您的代码的架构和演变。最小原则
特权建议从最严格的访问权限开始
有效，并且只在必要时扩大它。

对于公共 API，每个公共成员都是一种承诺。  制作前
公共的东西，考虑它是否真的需要成为你的一部分
模块的合同或者如果它是一个实现细节
暂时需要去其他地方。  公众成员应该稳定，
有详细记录，并且专为长寿而设计。

在继承中应谨慎使用受保护的访问
层次结构。并非基类中的所有内容都需要受到保护——仅
构成父母与子女之间继承契约的成员
儿童班。过度使用受保护的访问会造成紧密耦合
层次结构中的类之间。

私有访问是实现细节的默认设置。最帮手
函数、中间计算和状态管理应该
私人的。这为您提供了最大的重构和优化灵活性
不破坏依赖代码。

变量的双说明符模式对于
维持不变量。通过使变量公开可读，但是
私有或保护性可写，您可以公开状态
观察，同时保持对修改的完全控制：

<!--versetest
resource_manager := class:
    var<private> TotalResources<public>:int = 1000
    var<private> AllocatedResources<public>:int = 0
    var<private> AvailableResources<public>:int = 1000

    AllocateResources<public>(Amount:int)<decides><transacts>:void =
        Amount <= AvailableResources
        set AllocatedResources = AllocatedResources + Amount
        set AvailableResources = AvailableResources - Amount
<#
-->
<!-- 14 -->
```verse
resource_manager := class:
    var<private> TotalResources<public>:int = 1000
    var<private> AllocatedResources<public>:int = 0
    var<private> AvailableResources<public>:int = 1000

    AllocateResources<public>(Amount:int)<decides><transacts>:void =
        Amount <= AvailableResources
        set AllocatedResources = AllocatedResources + Amount
        set AvailableResources = AvailableResources - Amount
```
<!-- #> -->

## 注释和元数据

Verse 提供了一个注释系统，用于将元数据附加到
使用 `@` 前缀语法的定义。注释提供编译器
影响代码处理方式的指令和元数据
编译和演变。

### 内置注释

#### @已弃用

!!!警告“内部功能”
    @deprecated 属性目前是内部功能，最终用户无法使用。

`@deprecated` 注释标记不应再使用的定义
被使用。当代码引用已弃用的定义时，编译器
产生警告，提醒开发人员更新他们的代码：

<!--versetest
@deprecated
OldFunction():void =
    Print("This function is deprecated")

@deprecated
legacy_player := class:
    Name:string

UseDeprecated():void =
    OldFunction()
<#
-->
<!-- 15 -->
```verse
# 将定义标记为已弃用
@deprecated
OldFunction():void =
    Print("This function is deprecated")

# 将类标记为已弃用
@deprecated
legacy_player := class:
    Name:string

# 尝试使用已弃用的代码会产生警告
UseDeprecated():void =
    OldFunction()  # 警告：OldFunction 已弃用
```
<!-- #> -->

已弃用的定义可以使用其他已弃用的定义，而无需
警告，但未弃用的代码不能使用已弃用的定义
而不触发警告。这允许逐渐迁移
已弃用的 API：

<!--versetest
@deprecated
OldAPI():int = 42
@deprecated
MigrateOldAPI():int = OldAPI()


<#
-->
<!-- 16 -->
```verse
@deprecated
OldAPI():int = 42

# Valid: deprecated 可以调用deprecated
@deprecated
MigrateOldAPI():int = OldAPI()

# 警告：未弃用的调用已弃用
# NewCode():int = OldAPI()
```
<!-- #> -->

`@deprecated` 注释可应用于：
- 函数和方法
- 类、接口、结构和枚举
- 单独的枚举值
- 数据成员
- 模块

#### @实验

!!!警告“内部功能”
    @deprecated 属性目前是内部功能，最终用户无法使用。

`@experimental`注释标记尚未稳定的功能
并可能在未来版本中更改或删除。实验特点
仅当启用 `AllowExperimental` 封装标志时才能使用：

<!-- NoCompile -->
```verse
# 将功能标记为实验性
@experimental
experimental_class := class:
    NewFeature:int

# 使用实验性功能需要AllowExperimental标志
# 没有标志：错误
# 使用 AllowExperimental:=true：允许
UseExperimental(Obj:experimental_class):void =
    Print("Using experimental feature")
```
实验定义的行为与已弃用的定义类似
one—实验定义可以自由使用其他实验
定义，但稳定代码不能使用实验定义
除非设置了 `AllowExperimental` 标志。

`@experimental` 注释不能应用于：
- 局部变量
- 覆盖方法（基本方法的实验状态被继承）

#### @可用

`@available` 注释控制定义何时变为
根据版本号可用。这使得 API 能够逐步推出
和版本特定的功能：

<!--versetest
using { /Verse.org/Native }
@available{MinUploadedAtFNVersion := 3000}
NewFeature():void =
    Print("New feature")
@available{MinUploadedAtFNVersion := 2900}
OldImplementation():int = 42

@available{MinUploadedAtFNVersion := 3000}
NewImplementation():int = 100

<#
-->
<!-- 18 -->
```verse
using { /Verse.org/Native }  # @available 是简单的

# 仅适用于版本 3000 及更高版本
@available{MinUploadedAtFNVersion := 3000}
NewFeature():void =
    Print("New feature")

# 不同版本的多个定义可以共存
@available{MinUploadedAtFNVersion := 2900}
OldImplementation():int = 42

@available{MinUploadedAtFNVersion := 3000}
NewImplementation():int = 100
```
<!-- #> -->

`@available`注释可以应用于相同类型的
定义为 `@deprecated`。

### 自定义属性

!!!警告“内部功能”
    自定义属性目前是内部功能，最终用户无法创建。

您可以通过继承特殊属性来创建自定义属性
`attribute` 级。自定义属性允许您附加
您的代码的特定于域的元数据：

<!--versetest
@attribscope_class
gameplay_element := class<computes>(attribute):
    Category:string
    Priority:int
@gameplay_element{Category := "Combat", Priority := 1}
weapon_system := class:
    Damage:int
<#
-->
<!-- 19 -->
```verse
# 定义自定义属性
@attribscope_class
gameplay_element := class<computes>(attribute):
    Category:string
    Priority:int

# 使用自定义属性
@gameplay_element{Category := "Combat", Priority := 1}
weapon_system := class:
    Damage:int
```
<!-- #> -->

#### 属性范围

定义自定义属性时，必须指定它们的位置
使用范围注释应用：

- **@attribscope_class** - 可应用于常规类
- **@attribscope_attribclass** - 可应用于属性类（从 `attribute` 继承的类）
- **@attribscope_enum** - 可应用于枚举
- **@attribscope_interface** - 可应用于接口
- **@attribscope_function** - 可应用于函数和方法
- **@attribscope_data** - 可应用于数据成员

范围自定义属性的示例：

<!--versetest
@attribscope_function
performance_critical := class<computes>(attribute):
    MaxExecutionTimeMs:int

@attribscope_data
serializable_field := class<computes>(attribute):
    SerializationKey:string

entity := class<abstract>:
    @serializable_field{SerializationKey := "entity_id"}
    ID:int

    @performance_critical{MaxExecutionTimeMs := 16}
    Update():void

<#
-->
<!-- 20 -->
```verse
# 只能应用于函数的属性
@attribscope_function
performance_critical := class(attribute):
    MaxExecutionTimeMs:int

# 只能应用于数据成员的属性
@attribscope_data
serializable_field := class(attribute):
    SerializationKey:string

# 适当地使用它们
entity := class<abstract>:
    @serializable_field{SerializationKey := "entity_id"}
    ID:int

    @performance_critical{MaxExecutionTimeMs := 16}
    Update():void
```
<!-- #> -->

尝试在错误的位置使用属性会产生
编译器错误。例如，函数范围的属性不能是
应用于一个类。

**读取属性：** 自定义属性目前是元数据
外部工具 - 编译器、LSP 和虚幻编辑器可以读取
并对其采取行动，但没有 Verse API 来查询属性
运行时。属性用于应用规则、约束或额外的内容
语言之外的工具使用的数据，例如序列化
提示、编辑器注释或性能指令。

### Getter 和 Setter 访问器

!!!警告“内部功能”
    Getter 和 setter 访问器当前是内部功能，最终用户无法使用。

虽然不是严格的注释，但 `<getter(...)>` 和
`<setter(...)>` 说明符提供相关形式的元数据
控制现场访问。这些可以应用于类和
定义自定义访问逻辑的接口字段：

<!--versetest
entity := class:
    var Health<getter(GetHealth)><setter(SetHealth)>:int = external{}

    var InternalHealth:int = 100

    GetHealth(:accessor):int = InternalHealth

    SetHealth(:accessor, NewValue:int):void =
        if (NewValue >= 0, NewValue <= 100):
            set InternalHealth = NewValue

<#
-->
<!-- 21 -->
```verse
entity := class:
    # 具有自定义访问器的外部字段
    var Health<getter(GetHealth)><setter(SetHealth)>:int = external{}

    var InternalHealth:int = 100

    GetHealth(:accessor):int = InternalHealth

    SetHealth(:accessor, NewValue:int):void =
        if (NewValue >= 0, NewValue <= 100):
            set InternalHealth = NewValue
```
<!-- #> -->

对访问器的限制：

- 必须同时包含 `<getter(...)>` 和 `<setter(...)>` - 不能只有一个
- 该字段必须具有 `= external{}` 或没有默认值（需要原型初始化）
- 带有访问器的字段不能在子类中被覆盖
- 该字段必须是可变的（标记为 `var`）
- 并非所有类型都支持访问器字段
- 访问器字段当前仅允许在 Epid_internal 范围内

有关访问器模式的更多详细信息，请参阅[带有访问器的字段](10_classes_interfaces.md)。

### 本地化

`<localizes>` 说明符将定义标记为可本地化消息
为了国际化。本地化消息使用 `message` 类型
并且可以提取并翻译成不同的语言：

<!--versetest
WelcomeMessage<localizes> : message = "Welcome to the game!"

ShowWelcome():void =
    Print(Localize(WelcomeMessage))
<#
-->
<!-- 22 -->
```verse
# 简单的本地化消息
WelcomeMessage<localizes> : message = "Welcome to the game!"

# 调用 Localize 获取字符串
ShowWelcome():void =
    Print(Localize(WelcomeMessage))
```
<!-- #> -->

#### 消息参数

本地化消息可以接受动态内容插值的参数：

<!--versetest
GreetPlayer<localizes>(PlayerName:string) : message = "Hello, {PlayerName}!"

ShowGreeting(Name:string):void =
    Print(Localize(GreetPlayer(Name)))
<#
-->
<!-- 23 -->
```verse
# 带参数插值的消息
GreetPlayer<localizes>(PlayerName:string) : message = "Hello, {PlayerName}!"

# 与参数一起使用
ShowGreeting(Name:string):void =
    Print(Localize(GreetPlayer(Name)))
    # 输出：“你好，Aldric！”（如果名称=“Aldric”）
```
<!-- #> -->

**支持的参数类型：**
- `string` - 文本值
- `int` - 整数值（使用逗号分隔符格式化）
- `float` - 浮点值

**参数插值语法：**
- 使用`{ParameterName}`插入参数值
- 参数可以多次使用或根本不使用
- 大括号中只允许参数名称和 Unicode 代码点

<!--versetest
# Multiple parameters, some repeated
ScoreMessage<localizes>(Player:string, Score:int) : message =
    "Congratulations {Player}! Your score is {Score}. Great job, {Player}!"

# Outputs: "Congratulations Alice! Your score is 1,500. Great job, Alice!"

# Not all parameters required in message text
OptionalParam<localizes>(Name:string, Score:int) : message =
    "Thanks for playing!"  # Score parameter ignored
<#
-->
<!-- 24 -->
```verse
# 多个参数，有些重复
ScoreMessage<localizes>(Player:string, Score:int) : message =
    "Congratulations {Player}! Your score is {Score}. Great job, {Player}!"

# 输出：“恭喜Alice！你的分数是1,500。干得好，Alice！”

# 并非消息文本中需要所有参数
OptionalParam<localizes>(Name:string, Score:int) : message =
    "Thanks for playing!"  # 忽略分数参数
```
<!-- #> -->

#### 整数格式

为了便于阅读，整数参数会自动使用逗号分隔符进行格式化：

<!--versetest
HighScore<localizes>(Points:int) : message = "New record: {Points} points!"

<#
-->
<!-- 25 -->
```verse
HighScore<localizes>(Points:int) : message = "New record: {Points} points!"

# Localize(HighScore(190091)) 生成："New record: 190,091 points!"
```
<!-- #> -->

#### 命名参数和默认参数

本地化消息支持命名参数和默认值：

<!--versetest
ConfigMessage<localizes>(?MaxPlayers:int = 8, ?TimeLimit:int = 300):message =
    "Game settings: {MaxPlayers} players, {TimeLimit} seconds"

assert:
    Localize(ConfigMessage())                           # Uses defaults
    Localize(ConfigMessage(?MaxPlayers := 16))          # Override one
    Localize(ConfigMessage(?TimeLimit := 600, ?MaxPlayers := 32))  # Override both
<#
-->
<!-- 26 -->
```verse
ConfigMessage<localizes>(?MaxPlayers:int = 8, ?TimeLimit:int = 300):message =
    "Game settings: {MaxPlayers} players, {TimeLimit} seconds"

# 可以任意组合调用
Localize(ConfigMessage())                           # 使用默认值
Localize(ConfigMessage(?MaxPlayers := 16))          # 覆盖一
Localize(ConfigMessage(?TimeLimit := 600, ?MaxPlayers := 32))  # 覆盖两者
```
<!-- #> --> 

#### 元组参数

消息可以接受元组参数，这些参数在参数列表中被解构：

<!--versetest
LocationMessage<localizes>(Player:string, (X:int, Y:int)) : message =
    "{Player} is at position ({X}, {Y})"

# Test the call
TestTupleParam():void =
    Localize(LocationMessage("Hero", (10, 20)))
<#
-->
<!-- 27 -->
```verse
LocationMessage<localizes>(Player:string, (X:int, Y:int)) : message =
    "{Player} is at position ({X}, {Y})"

# 使用元组调用
Localize(LocationMessage("Hero", (10, 20)))
# 输出：“英雄位于位置 (10, 20)”
```
<!-- #>-->

#### 字符串转义和 Unicode

**Unicode 代码点：**

<!--versetest
UnicodeMessage<localizes> : message = "The letter is {0u004d}"
<#
-->
<!-- 28 -->
```verse
UnicodeMessage<localizes> : message = "The letter is {0u004d}"
# 输出：“字母是 M”
```
<!-- #> -->

**转义大括号**（显示文字大括号）：

<!--versetest
EscapedMessage<localizes>(Name:string) : message =
    "Use \{Name\} to insert {Name}"
<#
-->
<!-- 29 -->
```verse
EscapedMessage<localizes>(Name:string) : message =
    "Use \{Name\} to insert {Name}"
# Localize(EscapedMessage("value")) produces: "Use {Name} to insert value"
```
<!-- #> -->

**特殊字符：**

<!--versetest
SpecialChars<localizes> : message =
    "Supports: \\r\\n\\t\\\"\\'\\#\\<\\>\\&\\~"
<#
-->
<!-- 30 -->
```verse
SpecialChars<localizes> : message =
    "Supports: \\r\\n\\t\\\"\\'\\#\\<\\>\\&\\~"
```
<!-- #> -->

**插值中允许使用空格和注释**：

<!--versetest
SpacedParam<localizes>(Name:string) : message = "Hello { Name }"
CommentedParam<localizes>(Name:string) : message = "Hello {Name}"
<#
-->
<!-- 31 -->
```verse
SpacedParam<localizes>(Name:string) : message = "Hello { Name }"
CommentedParam<localizes>(Name:string) : message = "Hello {<# comment #>Name}"
```
<!-- #> -->

#### 范围要求

本地化消息**必须在模块或代码片段范围内定义**。它们不能在函数内部定义：

<!-- NoCompile -->
```verse
# 有效：模块范围
MyModule := module:
    ModuleMessage<localizes> : message = "Valid"

# 有效：片段范围
TopLevelMessage<localizes> : message = "Valid"

BadFunction():void =
    LocalMessage<localizes> : message = "Invalid"  # 错误
```
#### 继承和覆盖

本地化消息可以在类层次结构中被覆盖：

<!--versetest
base_ui := class:
    Title<localizes>:message = "Base Title"
    Description<localizes>:message = "Base description"

derived_ui := class(base_ui):
    Title<localizes><override>:message = "Derived Title"
<#
-->
<!-- 33 -->
```verse
base_ui := class:
    Title<localizes>:message = "Base Title"
    Description<localizes>:message = "Base description"

derived_ui := class(base_ui):
    # 覆盖标题消息
    Title<localizes><override>:message = "Derived Title"
    # 从基础继承描述
```
<!-- #> -->

本地化消息也可以是抽象的：

<!--versetest
quest_base := class<abstract>:
    TaskDescription<localizes><public> : message
    CompletionMessage<localizes><protected> : message = "Quest complete!"

fetch_quest := class<final>(quest_base):
    TaskDescription<localizes><override> : message = "Collect 10 items"
<#
-->
<!-- 34 -->
```verse
quest_base := class<abstract>:
    # 抽象消息 - 必须由子类实现
    TaskDescription<localizes><public> : message
    # 默认的具体消息
    CompletionMessage<localizes><protected> : message = "Quest complete!"

fetch_quest := class<final>(quest_base):
    TaskDescription<localizes><override> : message = "Collect 10 items"
```
<!-- #> -->

#### 限制和错误

**必须使用显式类型注释：**

需要类型注释 `: message`。不支持隐式键入：

<!--versetest

GoodMessage<localizes> : message = "Text"
<#
-->
<!-- 35 -->
```verse
# 错误：缺少类型注释
# BadMessage<localizes> := "Text"  # ERROR 3639

# 有效：显式类型
GoodMessage<localizes> : message = "Text"
```
<!-- #> -->

**RHS 必须是字符串文字：**

<!--versetest

ValidMessage<localizes> : message = "AB"
<#
-->
<!-- 36 -->
```verse
# 错误：不允许表达式
# InvalidMessage<localizes> : message = "A" + "B"  # ERROR 3638

# 有效：仅字面量
ValidMessage<localizes> : message = "AB"
```
<!-- #> -->

**限制参数类型：**

并非所有类型都支持作为参数：

<!--versetest

my_class := class{Value:int}
<#
-->
<!-- 37 -->
```verse
# 错误：不支持可选类型
# OptionalMsg<localizes>(Player:?string) : message = "{Player}" # 错误 3509

# 错误：不支持自定义类
my_class := class{Value:int}
# ClassMsg<本地化>(Obj:my_class) : message = "{Object}" # 错误 3509
```
<!-- #> -->

**插值语法限制：**

`{}` 内只允许参数名称和 Unicode 代码点：

<!--versetest

ParamMessage<localizes>(Name:string) : message = "{Name}"
<#
-->
<!-- 38 -->
```verse
# 错误：不允许使用表达式
# ExprMessage<本地化>(名称:字符串) : message = "{"Hello"}" # 错误 3652

# 有效：仅参数名称
ParamMessage<localizes>(Name:string) : message = "{Name}"
```
<!-- #> -->

**非参数标识符被转义：**

如果您引用不是参数的标识符，它将在输出中转义：

<!--versetest
GlobalName:string = "World"

RefMessage<localizes>(Greeting:string) : message =
    "{Greeting} to {GlobalName}"

<#
-->
<!-- 39 -->
```verse
GlobalName:string = "World"

RefMessage<localizes>(Greeting:string) : message =
    "{Greeting} to {GlobalName}"

# Localize(RefMessage("Hello")) produces: "Hello to \{GlobalName\}"
# 注意：GlobalName 被转义，因为它不是参数
```
<!-- #> -->

#### 访问说明符

本地化消息支持标准访问说明符：

<!--versetest
MyModule := module:
    PublicMessage<localizes><public> : message = "Public message"
    InternalMessage<localizes> : message = "Internal message"

    some_class := class:
        PrivateMessage<localizes><private> : message = "Private message"
<#
-->
<!-- 40 -->
```verse
MyModule := module:
    PublicMessage<localizes><public> : message = "Public message"
    InternalMessage<localizes> : message = "Internal message"

    some_class := class:
        PrivateMessage<localizes><private> : message = "Private message"  # 模块范围内允许私人使用
```
<!-- #> -->

#### 最佳实践

**保持消息可翻译：**
- 使用完整的句子，而不是可能串联的片段
- 避免无法很好翻译的性别或数字假设
- 通过参数名称提供上下文

**针对不同语言的设计：**
- 不要假设词序 - 让翻译人员重新排列参数位置
- 允许对需要的语言重复使用参数
- 保持代码格式（如逗号分隔符）自动化

**组织：**
- 在同一模块中对相关消息进行分组
- 使用表明消息目的的描述性名称
- 考虑使用消息族的抽象基类

<!--versetest
PlayerJoined<localizes>(PlayerName:string, TeamName:string) : message =
    "{PlayerName} joined team {TeamName}"

<#
-->
<!-- 41 -->
```verse
# 好：清晰、完整、灵活
PlayerJoined<localizes>(PlayerName:string, TeamName:string) : message =
    "{PlayerName} joined team {TeamName}"

# 避免：可能串联的片段
# PlayerPrefix<localizes>(Name:string) : message = "玩家 {Name}"
# JoinedSuffix<localizes>(Team:string) : message = "已加入 {Team}"
```
<!-- #> -->

## 进化

访问说明符在代码演化中起着至关重要的作用。改变
发布后的访问级别可能会破坏兼容性：

- 缩小访问范围（从公共到私有）会破坏外部代码
  取决于会员
- 扩大访问范围（从私人到公共）通常是安全的，但会产生
  新的承诺
- 变更受保护成员会影响继承契约

类上的 `<castable>` 说明符具有特殊的兼容性
要求——一旦发布，就不能添加或删除，因为这
会影响整个代码库动态转换的安全性。

在设计长期演进时，请考虑使用内部访问
对于最终可能公开的成员。这可以让您
在公开之前测试和完善模块中的 API
曝光。
