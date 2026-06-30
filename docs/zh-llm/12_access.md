# 访问说明符

访问说明符控制代码元素的可见性和可访问性。它们提供了一套精细的访问级别光谱，反映了现代软件开发中的复杂现实，特别是在多个作者的代码必须安全共存的持久化全局元宇宙的背景下。

此处定义了五种主要的可见性级别，它们构成了一个精心设计的层次结构，每种级别服务于特定的架构需求。理解何时以及为何使用每种级别，对于创建结构良好、可维护的代码至关重要。

| 说明符 | 可见性 | 用途 |
|-----------|------------|-------|
| `<public>` | 全局可访问 | 供外部使用的成员 |
| `<internal>` | 仅模块内（默认） | 模块私有实现 |
| `<private>` | 仅在直接封闭作用域内 | 局部于类/结构体 |
| `<protected>` | 当前类及其子类型 | 继承层次结构 |
| `<scoped>` | 当前作用域及封闭作用域 | 特殊用例 |
| `<epic_internal>` | 具有 /Verse.org、/UnrealEngine.com 和 /Fortnite.com 域名的作用域 | `<epic_internal>` 仅可由 Epic 编写的代码使用 |

## Public

`<public>` 说明符代表最广泛的访问级别，使标识符可以从任何能引用包含模块或类型的代码中全局访问。当你将某个内容标记为 public 时，你对其可用性和稳定性做出了强有力的承诺：

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

Public 成员构成了你的代码与外部世界之间的契约。在元宇宙语境中，public 声明尤为重要，因为它们代表了可能无限延续的保证——一旦发布，移除或不兼容地更改一个 public 成员，就破坏了你对依赖你代码的其他开发者所做的承诺。

public 说明符可应用于模块、类、接口、结构体、枚举、方法和数据成员。当应用于类型定义本身时，它使得该类型可以在定义模块之外使用。当应用于类型内部的成员时，它使得这些成员可以被任何能访问该类型实例的代码所访问。

## Protected

`<protected>` 说明符在 public 和 private 之间创建了一个中间地带，允许在定义类及其任何继承类中访问。这个级别专门用于支持继承层次结构，同时保持封装性：

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

    OnPositionChanged<protected>():void = {}  # 可被子类重写

player := class(game_entity):
    MoveToSpawn():void =
        UpdatePosition(GetSpawnLocation())  # 可以访问 protected 成员
        set Health = MaxHealth              # 可以修改 protected 变量
```
<!-- #> -->

Protected 访问支持模板方法模式和其他基于继承的设计，同时防止外部代码访问应保留在类层次结构内部的实现细节。这对于游戏实体和其他层次结构尤其有价值，父类需要与子类共享行为，但又不将该行为暴露给外部。

## Private

`<private>` 说明符提供了最严格的访问控制，将可见性限制在直接封闭作用域内。Private 成员是真正的内部实现细节，可以随意更改而不会影响任何外部代码：

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

Private 成员是封装的基本构建块。它们允许你维持不变量、隐藏复杂性以及创建清晰的抽象。对 private 成员的更改从不会破坏外部代码，让你能够按需自由地重构和优化实现细节。

## Internal

`<internal>` 说明符（当未提供说明符时的默认访问级别）使成员可以在定义模块内访问，但不能在模块外部访问。这为需要共享实现细节但又不公开暴露的协作代码创建了一个自然的边界：

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

Internal 访问非常适合模块级工具函数、共享实现细节以及模块内多个类需要但不应暴露给外部代码的辅助函数。它在模块的公共接口与其实现机制之间提供了清晰的分离。

## Scoped

`<scoped>` 说明符在模块或代码位置之间创建自定义的访问边界。与 `public`、`internal` 和 `private` 的固定可见性级别不同，`scoped` 访问允许你显式地向特定模块授予访问权限，同时排除所有其他模块——在程序实体之间创建了一种"友元"关系。

### Scoped 定义

使用 `scoped{...}` 表达式创建 scoped 访问级别，该表达式接受一个或多个模块引用：

<!-- NoCompile -->
```verse
Collaboration := module:
    # 创建一个包含 ModuleA 和 ModuleB 的作用域
    Shared<public> := scoped{ModuleA, ModuleB}

    # 此类仅可在 ModuleA 和 ModuleB 中访问
    SharedResource<Shared> := class:
        Data<public>:int = 42
```

Scoped 定义创建一个访问级别，随后可用作类、函数、变量和其他定义的说明符。列出的任何实体中的代码都可以访问该 scoped 成员，而列在这些模块之外的代码则不能——即使它可以看到包含该成员的作用域。

### 跨模块协作

Scoped 访问最强大的用途是支持模块之间受控的协作。可以在一个模块中创建定义，但将其作用域限定到另一个模块，使其在需要的地方可访问，同时在其他地方保持隐藏：

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
    # 定义一个作用域限定到 physics 模块的接口
    CollidableShape<scoped{Physics}> := interface:
        GetBounds():bounding_box

Physics := module:
    using{Graphics}

    # Physics 模块可以实现该接口，尽管它定义在 graphics 模块中
    sphere_collider := class<abstract>(CollidableShape):
        GetBounds<override>():bounding_box
```
<!-- #> -->

这种模式允许 graphics 模块定义由 physics 模块实现的契约，而无需公开暴露这些实现细节。该接口存在于两个模块之间的边界上，但不属于任一模块的公共 API。

你可以将定义的作用域限定到多个模块，创建一个共享的私有协作空间：

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
    # 此作用域同时包含 inventory 和 crafting 模块
    SharedGameplayScope := scoped{Inventory, Crafting}

    # Item 可被 inventory 和 crafting 两者访问
    Item<SharedGameplayScope> := class:
        ID<public>:int
        Properties<public>:[string]string

    # 工厂函数对两个系统都可用
    CreateItem<SharedGameplayScope>(TheID:int):Item = Item{ID:=TheID, Properties:=map{}}

Inventory := module:
    using{Gameplay}

    AddToInventory(ItemID:int):void =
        NewItem := CreateItem(ItemID)  # 可以访问 scoped 函数
        # 实现...

Crafting := module:
    using{Gameplay}

    CraftItem(Recipe:[]int)<decides>:Item =
        # 可以创建 item 并访问其属性
        CreateItem(Recipe[0])
```
<!-- #> -->

### Scoped 读或写访问

与其他访问说明符类似，scoped 可以分别应用于变量的读操作和写操作：

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
    # 公开的读访问，但只有 ModuleA 和 ModuleB 可以写入
    var<SharedScope> GameState<public>:game_state = game_state{}

    # 只有 ModuleA 和 ModuleB 可以读或写此内部状态
    var<SharedScope> SyncCounter<SharedScope>:int = 0
```
<!-- #> -->

这种模式对于多个模块需要协调但又不公开暴露写访问权限的共享状态特别有用。

### 可见性与访问路径

Scoped 访问的一个重要微妙之处在于，它授予对特定成员的访问权限，但并不会使中间类型或模块可见。要访问 scoped 成员，必须能看到通往该成员的完整路径：

<!-- NoCompile -->
```verse
Outer := module:
    # 内部于 outer
    Inner := module:
        # 作用域限定到 TargetModule
        SharedClass<scoped{TargetModule}> := class:
            Value:int = 42

TargetModule := module:
    using{Outer}

    # 错误：无法看到 Outer.Inner，因为 Inner 是 outer 内部的
    # 即使 SharedClass 的作用域已限定给我们
    UseShared():void = Outer.Inner.SharedClass{}
```

要使 scoped 访问生效，要么包含该成员的作用域必须是可访问的（public 或同样适当地 scoped），要么必须通过公开它的公共接口来访问 scoped 成员。

一个定义只能有一个 scoped 访问级别——你不能应用多个 scoped 说明符：

<!-- NoCompile-->
```verse
# 错误：不能有多个访问级别说明符
InvalidScope<scoped{ModuleA}><scoped{ModuleB}> := class{}
```

### Scoped 访问与继承

当类成员具有 scoped 访问权限时，子类中的重写成员可以维持或收窄该访问权限，遵循正常的继承规则：

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
    # 可以用相同或更严格的访问权限重写
    ComputeValue<override>():int = 100  # 现在限定为此模块内部
```
<!-- #> -->

### 使用 Scoped 定义 API 边界

Scoped 访问擅长创建受控的 API 边界，在特定模块之间共享某些功能，但不作为公共接口的一部分暴露：

<!-- NoCompile -->
```verse
Networking := module:
    # 为需要网络访问的模块定义的公共作用域
    NetworkScope<public> := scoped{PlayerSystem, Matchmaking, Telemetry}

    # 核心网络功能对特定系统可用
    SendPacket<NetworkScope>(Data:[]uint8):void =
        # 实现...

    # 内部统计
    var<NetworkScope> BytesSent<NetworkScope>:int = 0
```

这创建了一个明确的架构边界——只有作用域中列出的模块可以访问网络原语，而其他代码必须使用更高级别的公共 API。

### 设计考量

Scoped 访问代表了模块之间的架构承诺。有效使用时：

- 对不属于公共 API 的合理跨模块协作使用 scoped
- 将作用域定义保持在模块级别，便于文档化和维护
- 优先将作用域限定到显式模块，而非深层嵌套的作用域
- 考虑 `protected` 或 `internal` 访问是否对你的用例更简单
- 记录为什么特定模块被包含在作用域中

Scoped 说明符在 internal 和 public 访问之间填补了一个独特的空白，支持复杂的模块架构，其中多个组件需要紧密协作，但又不必将这些实现细节暴露给更广泛的代码库。

## 分离读和写访问

一个创新的特性是能够对同一变量的读和写操作应用不同的访问说明符。这种细粒度的控制允许你创建广泛可读但严格可写的变量，优雅地实现了诸如只读属性等常见模式：

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
    # 公开读，protected 写
    var<protected> Score<public>:int = 0

    # 公开读，private 写
    var<private> PlayerCount<public>:int = 0

    # 内部读，private 写
    var<private> SessionID<internal>:string
```
<!-- #> -->

这种双说明符系统解决了面向对象编程中的一个常见问题：希望暴露状态供读取，同时不允许外部修改。Verse 不要求使用 getter 方法或属性语法，而是将此模式作为语言的一等特性。

语法将写访问说明符放在 `var` 关键字上，读访问说明符放在标识符本身上。这种视觉分离在阅读代码时使访问级别一目了然。写说明符必须至少与读说明符一样严格——你不能写入一个私有可读但公开可写的变量，因为这会违反基本的封装原则。

## 最佳实践

理解何时使用每种访问级别需要思考代码的架构和演进。最小权限原则建议从最严格的可用访问开始，只在必要时放宽。

对于公共 API，每个 public 成员都是一个承诺。在将某个东西设为 public 之前，考虑它是否真的需要成为模块契约的一部分，或者它是否只是一个碰巧暂时在其他地方需要的实现细节。Public 成员应该是稳定的、文档良好的，并为长期使用而设计。

Protected 访问应在继承层次结构中审慎使用。基类中并非所有内容都需要是 protected——只有那些构成父类和子类之间继承契约的成员才需要。过度使用 protected 访问可能会在层次结构中的类之间创建紧密耦合。

Private 访问是实现细节的默认选择。大多数辅助函数、中间计算和状态管理应该是 private 的。这为你提供了最大的灵活性，可以在不破坏依赖代码的情况下进行重构和优化。

变量的双说明符模式在维护不变量方面特别强大。通过使变量公开可读但私有或受保护可写，你可以暴露状态供观察，同时保持对修改的完全控制：

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

## 注解与元数据

Verse 提供了一个注解系统，用于使用 `@` 前缀语法将元数据附加到定义上。注解提供了编译器指令和元数据，影响代码在编译和演进过程中的处理方式。

### 内置注解

#### @deprecated

!!! warning "内部功能"
    @deprecated 属性目前是内部功能，最终用户无法使用。

`@deprecated` 注解标记不再应该使用的定义。当代码引用已弃用的定义时，编译器会产生警告，提醒开发者更新其代码：

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

已弃用的定义可以使用其他已弃用的定义而不产生警告，但非弃用代码使用已弃用定义时会触发警告。这允许逐步迁移已弃用的 API：

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

# 有效：已弃用代码可以调用已弃用代码
@deprecated
MigrateOldAPI():int = OldAPI()

# 警告：非弃用代码调用已弃用代码
# NewCode():int = OldAPI()
```
<!-- #> -->

`@deprecated` 注解可以应用于：
- 函数和方法
- 类、接口、结构体和枚举
- 单个枚举值
- 数据成员
- 模块

#### @experimental

!!! warning "内部功能"
    @deprecated 属性目前是内部功能，最终用户无法使用。

`@experimental` 注解标记尚未稳定且可能在将来版本中更改或移除的特性。实验性特性仅在启用了 `AllowExperimental` 包标志时才能使用：

<!-- NoCompile -->
```verse
# 将特性标记为实验性
@experimental
experimental_class := class:
    NewFeature:int

# 使用实验性特性需要 AllowExperimental 标志
# 无标志：错误
# 设置 AllowExperimental:=true：允许
UseExperimental(Obj:experimental_class):void =
    Print("Using experimental feature")
```

实验性定义的行为与已弃用定义类似——实验性定义可以自由使用其他实验性定义，但除非设置了 `AllowExperimental` 标志，否则稳定代码不能使用实验性定义。

`@experimental` 注解不能应用于：
- 局部变量
- 重写方法（基方法的实验性状态会被继承）

#### @available

`@available` 注解根据版本号控制定义何时可用。这使得 API 可以逐步推出及实现特定版本的功能：

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
using { /Verse.org/Native }  # @available 需要此行

# 仅在版本 3000 及之后可用
@available{MinUploadedAtFNVersion := 3000}
NewFeature():void =
    Print("New feature")

# 多个定义可以为不同版本共存
@available{MinUploadedAtFNVersion := 2900}
OldImplementation():int = 42

@available{MinUploadedAtFNVersion := 3000}
NewImplementation():int = 100
```
<!-- #> -->

`@available` 注解可以应用于与 `@deprecated` 相同类型的定义。

### 自定义属性

!!! warning "内部功能"
    自定义属性目前是内部功能，最终用户无法创建。

你可以通过继承特殊的 `attribute` 类来创建自定义属性。自定义属性允许你向代码附加领域特定的元数据：

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

#### 属性作用域

在定义自定义属性时，必须使用作用域注解指定它们可以应用的位置：

- **@attribscope_class** - 可应用于常规类
- **@attribscope_attribclass** - 可应用于属性类（继承自 `attribute` 的类）
- **@attribscope_enum** - 可应用于枚举
- **@attribscope_interface** - 可应用于接口
- **@attribscope_function** - 可应用于函数和方法
- **@attribscope_data** - 可应用于数据成员

作用域限定自定义属性示例：

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

# 正确地使用它们
entity := class<abstract>:
    @serializable_field{SerializationKey := "entity_id"}
    ID:int

    @performance_critical{MaxExecutionTimeMs := 16}
    Update():void
```
<!-- #> -->

尝试在错误的位置使用属性会产生编译器错误。例如，函数作用域属性不能应用于类。

**读取属性：** 自定义属性目前是供外部工具使用的元数据——编译器、LSP 和 Unreal Editor 可以读取并对其作出响应，但不存在用于在运行时查询属性的 Verse API。属性用于应用语言外部工具消费的规则、约束或额外数据，例如序列化提示、编辑器注解或性能指令。

### Getter 和 Setter 访问器

!!! warning "内部功能"
    Getter 和 setter 访问器目前是内部功能，最终用户无法使用。

虽然严格来说不是注解，但 `<getter(...)>` 和 `<setter(...)>` 说明符提供了控制字段访问的相关元数据形式。这些可以应用于类和接口字段，以定义自定义访问逻辑：

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

对访问器的约束：

- 必须同时包含 `<getter(...)>` 和 `<setter(...)>`——不能只有一个
- 字段必须有 `= external{}` 或没有默认值（需要原型初始化）
- 带有访问器的字段不能在子类中被重写
- 字段必须是可变的（用 `var` 标记）
- 并非所有类型都支持用于访问器字段
- 访问器字段目前仅在 epic_internal 作用域中允许

更多关于访问器模式的细节，请参阅[具有访问器的字段](10_classes_interfaces.md)。

### 本地化

`<localizes>` 说明符将定义标记为用于国际化的可本地化消息。本地化消息使用 `message` 类型，并且可以被提取出来翻译成不同语言：

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

本地化消息可以接受参数，用于动态内容插值：

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

# 带参数使用
ShowGreeting(Name:string):void =
    Print(Localize(GreetPlayer(Name)))
    # 输出："Hello, Aldric!"（如果 Name = "Aldric"）
```
<!-- #> -->

**支持的参数类型：**
- `string` - 文本值
- `int` - 整数值（使用逗号分隔符格式化）
- `float` - 浮点值

**参数插值语法：**
- 使用 `{ParameterName}` 插入参数值
- 参数可以多次使用或不使用
- 花括号内仅允许参数名称和 Unicode 码点

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
# 多个参数，部分重复使用
ScoreMessage<localizes>(Player:string, Score:int) : message =
    "Congratulations {Player}! Your score is {Score}. Great job, {Player}!"

# 输出："Congratulations Alice! Your score is 1,500. Great job, Alice!"

# 并非所有参数都必须在消息文本中使用
OptionalParam<localizes>(Name:string, Score:int) : message =
    "Thanks for playing!"  # Score 参数被忽略
```
<!-- #> -->

#### 整数格式化

整数参数会自动添加逗号分隔符以增强可读性：

<!--versetest
HighScore<localizes>(Points:int) : message = "New record: {Points} points!"

<#
-->
<!-- 25 -->
```verse
HighScore<localizes>(Points:int) : message = "New record: {Points} points!"

# Localize(HighScore(190091)) 产生："New record: 190,091 points!"
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

# 可以以任意组合调用
Localize(ConfigMessage())                           # 使用默认值
Localize(ConfigMessage(?MaxPlayers := 16))          # 覆盖一个
Localize(ConfigMessage(?TimeLimit := 600, ?MaxPlayers := 32))  # 覆盖两个
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
# 输出："Hero is at position (10, 20)"
```
<!-- #>-->

#### 字符串转义和 Unicode

**Unicode 码点：**

<!--versetest
UnicodeMessage<localizes> : message = "The letter is {0u004d}"
<#
-->
<!-- 28 -->
```verse
UnicodeMessage<localizes> : message = "The letter is {0u004d}"
# 输出："The letter is M"
```
<!-- #> -->

**转义花括号**（用于显示字面花括号）：

<!--versetest
EscapedMessage<localizes>(Name:string) : message =
    "Use \{Name\} to insert {Name}"
<#
-->
<!-- 29 -->
```verse
EscapedMessage<localizes>(Name:string) : message =
    "Use \{Name\} to insert {Name}"
# Localize(EscapedMessage("value")) 产生："Use {Name} to insert value"
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

**插值中允许空白和注释：**

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

#### 作用域要求

本地化消息**必须在模块或片段作用域中定义**。它们不能在函数内部定义：

<!-- NoCompile -->
```verse
# 有效：模块作用域
MyModule := module:
    ModuleMessage<localizes> : message = "Valid"

# 有效：片段作用域
TopLevelMessage<localizes> : message = "Valid"

BadFunction():void =
    LocalMessage<localizes> : message = "Invalid"  # 错误
```

#### 继承和重写

本地化消息可以在类层次结构中被重写：

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
    # 重写标题消息
    Title<localizes><override>:message = "Derived Title"
    # 继承基类的 Description
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
    # 抽象消息——必须由子类实现
    TaskDescription<localizes><public> : message
    # 具有默认值的具体消息
    CompletionMessage<localizes><protected> : message = "Quest complete!"

fetch_quest := class<final>(quest_base):
    TaskDescription<localizes><override> : message = "Collect 10 items"
```
<!-- #> -->

#### 限制和错误

**必须使用显式类型注解：**

类型注解 `: message` 是必需的。不支持隐式类型：

<!--versetest

GoodMessage<localizes> : message = "Text"
<#
-->
<!-- 35 -->
```verse
# 错误：缺少类型注解
# BadMessage<localizes> := "Text"  # ERROR 3639

# 有效：显式类型
GoodMessage<localizes> : message = "Text"
```
<!-- #> -->

**RHS 必须是字符串字面量：**

<!--versetest

ValidMessage<localizes> : message = "AB"
<#
-->
<!-- 36 -->
```verse
# 错误：不允许使用表达式
# InvalidMessage<localizes> : message = "A" + "B"  # ERROR 3638

# 有效：仅字面量
ValidMessage<localizes> : message = "AB"
```
<!-- #> -->

**受限的参数类型：**

并非所有类型都支持作为参数：

<!--versetest

my_class := class{Value:int}
<#
-->
<!-- 37 -->
```verse
# 错误：不支持可选类型
# OptionalMsg<localizes>(Player:?string) : message = "{Player}"  # ERROR 3509

# 错误：不支持自定义类
my_class := class{Value:int}
# ClassMsg<localizes>(Obj:my_class) : message = "{Object}"  # ERROR 3509
```
<!-- #> -->

**插值语法限制：**

`{}` 内部仅允许参数名称和 Unicode 码点：

<!--versetest

ParamMessage<localizes>(Name:string) : message = "{Name}"
<#
-->
<!-- 38 -->
```verse
# 错误：不允许表达式
# ExprMessage<localizes>(Name:string) : message = "{"Hello"}"  # ERROR 3652

# 有效：仅参数名称
ParamMessage<localizes>(Name:string) : message = "{Name}"
```
<!-- #> -->

**非参数标识符会被转义：**

如果你引用的标识符不是参数，它会在输出中被转义：

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

# Localize(RefMessage("Hello")) 产生："Hello to \{GlobalName\}"
# 注意：GlobalName 被转义，因为它不是参数
```
<!-- #> -->

#### 访问说明符

本地化消息支持标准的访问说明符：

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
        PrivateMessage<localizes><private> : message = "Private message"  # 模块作用域中不允许 private
```
<!-- #> -->

#### 最佳实践

**保持消息可翻译：**
- 使用完整句子，而不是可能被拼接的片段
- 避免不易翻译的性别或数量假设
- 通过参数名称提供上下文

**为不同语言设计：**
- 不要假定词序——让翻译人员重新排列参数位置
- 允许重复使用参数，为需要如此的语言提供支持
- 保持格式化代码（如逗号分隔符）自动化

**组织：**
- 在同一模块中对相关消息进行分组
- 使用能表明消息用途的描述性名称
- 考虑对消息族使用抽象基类

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

# 避免：可能被拼接的片段
# PlayerPrefix<localizes>(Name:string) : message = "Player {Name}"
# JoinedSuffix<localizes>(Team:string) : message = "joined {Team}"
```
<!-- #> -->

## 演进

访问说明符在代码演进中扮演着关键角色。发布后更改访问级别可能会破坏兼容性：

- 收窄访问权限（从 public 到 private）会破坏依赖该成员的外部代码
- 放宽访问权限（从 private 到 public）通常是安全的，但会创建新的承诺
- 更改 protected 成员会影响继承契约

类上的 `<castable>` 说明符有特殊的兼容性要求——一旦发布，它就不能被添加或移除，因为这会影响整个代码库中动态转换的安全性。

在设计长期演进时，考虑对可能最终成为 public 的成员使用 internal 访问。这允许你在模块内部测试和完善 API，然后再承诺公开暴露。
