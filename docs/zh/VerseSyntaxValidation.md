---
搜索：
  排除：真
---
用它来测试和验证语法突出显示

#### 基础知识
<!--NoCompile-->
```verse
<# 班级#>
Component := class<final_super>(component) {
    @editable Text:string = "Hello";

    OnBeginSimulation<override>():void = {
        Print("{Self.Text}Verse");
    };
};

<# 枚举#>
EAnchor := enum {
    Top,
    Right,
    Bottom,
    Left
};

<# 块#>
block {
    Print("{Self.Text}Verse");
};

block { Print("{Self.Text}Verse"); };

<# 评论#>
Damage := 100 * 1.5  # 应用暴击倍数
Result := BaseValue <# 原始金额 #> * Multiplier <# 比例因子 #> + Bonus
Text := "abc<#comment#>def"     # 允许在字符串中添加注释
<# 暂时禁用以进行测试
   OriginalFunction()  <# 这有一个错误#>
   NewFunction()       # 测试这种方法
#>
<#>
    整个代码块都是注释，因为它使用了缩进。
    这提供了一种整洁的方式来编写较长的文档，
    而无需在每一行都添加注释标记。

DoSomething()  # 不属于评论的一部分。
```
## 现实生活中的例子
<!--NoCompile-->
```verse
# 模块声明 - 从导入实用函数开始
using { /Verse.org/VerseCLR }

# 将项目稀有度定义为枚举 - 显示 Verse 的类型系统
item_rarity := enum<persistable>:
    common
    uncommon
    rare
    epic
    legendary

# 不可变项数据的结构 - 函数式编程风格
item_stats := struct<persistable>:
    Damage:float = 0.0
    Defense:float = 0.0
    Weight:float = 1.0
    Value:int = 0

# 游戏项目类 - 具有功能约束的面向对象特性
game_item := class<final><persistable>:
    Name:string
    Rarity:item_rarity = item_rarity.common
    Stats:item_stats = item_stats{}
    StackSize:int = 1
    
    # 方法决定效果——可能会失败
    GetRarityMultiplier()<decides>:float =
        case(Rarity):
            item_rarity.common => 1.0
            item_rarity.uncommon => 1.5
            item_rarity.rare => 2.0
            item_rarity.epic => 3.0
            _ => false  # 如果该项目是传奇的或意外的，则失败
    
    # 使用封闭世界函数计算属性
    GetEffectiveValue()<transacts><decides> :int=
        Floor[Stats.Value * GetRarityMultiplier[]]

# 库存系统具有状态管理和效果
inventory_system := class:
    var Items:[]game_item = array{}
    var MaxWeight:float = 100.0
    var Gold:int = 1000

    # 演示失败处理和事务语义的方法
    AddItem(NewItem:game_item)<transacts><decides>:void =
        # 计算新权重 - 推测执行
        CurrentWeight := GetTotalWeight()
        NewWeight := CurrentWeight + NewItem.Stats.Weight

        # 此检查可能会失败，回滚所有更改
        NewWeight <= MaxWeight
        
        # 仅当重量检查通过时才执行
        set Items += array{NewItem}
        Print("Added {NewItem.Name} to inventory")

    # 具有查询运算符和失败传播的方法
    RemoveItem(ItemName:string)<transacts><decides>:game_item =
        var RemovedItem:?game_item = false
        var NewItems:[]game_item = array{}
        
        for (Item : Items):
            if (Item.Name = ItemName, not RemovedItem?):
                set RemovedItem = option{Item}
            else:
                set NewItems += array{Item}
        set Items = NewItems
        RemovedItem?  # 如果未找到项目则失败

    # 购买失败逻辑复杂、回滚
    PurchaseItem(ShopItem:game_item)<transacts><decides>:void =
        # 多个失败点 - 任何失败都会回滚所有更改
        Price := ShopItem.GetEffectiveValue[]
        Price <= Gold  # 如果金币不足则失败
        
        # 暂定扣金
        set Gold = Gold - Price
        
        # 尝试添加物品 - 可能会因重量而失败
        AddItem[ShopItem]
        
        # 全部成功 - 更改已提交
        Print("Purchased {ShopItem.Name} for {Price} gold")

    # 具有类型参数和子句的高阶函数
    FilterItems(Predicate:type{_(:game_item)<decides>:void} ) :[]game_item =
        for (Item : Items, Predicate[Item]):
            Item

    GetTotalWeight()<transacts>:float =
        var Total:float = 0.0
        for (Item : Items):
            set Total += Item.Stats.Weight
        Total

# 使用组合的玩家类别
player_character<public> := class:
    Name<public>:string
    var Level:int = 1
    var Experience:int = 0
    var Inventory:inventory_system = inventory_system{}
    
    LevelUpThreshold := 100

    GainExperience(Amount:int)<transacts>:void =
        set Experience += Amount
        
        # 自动升级检查与失败处理
        loop:
            RequiredXP := LevelUpThreshold * Level
            if (Experience >= RequiredXP):
                set Experience -= RequiredXP
                set Level += 1
                Print("{Name} leveled up to {Level}!")
            else:
                break
    
    # 显示合格访问的方法
    EquipStarterGear()<transacts><decides>:void =
        StarterSword := game_item{
            Name := "Rusty Sword"
            Rarity := item_rarity.common
            Stats := item_stats{Damage := 10.0, Weight := 5.0, Value := 50}
        }
        # 如果库存已满，这些可能会失败
        Inventory.AddItem[StarterSword]

# 演示控制流和失败处理的示例用法
RunExample<public>()<suspends>:void =
    # 创建一个玩家（不能失败）
    Hero := player_character{Name := "Verse Hero"}
    
    # 尝试装备启动装置（可能会失败）
    if (Hero.EquipStarterGear[]):
        Print("Hero equipped with starter gear")
    
    # 展示交易行为
    ExpensiveItem := game_item{
        Name := "Golden Crown"
        Rarity := item_rarity.epic
        Stats := item_stats{Value := 2000, Weight := 90.0}  # 很重！
    }
    
    # 这可能会因重量或金币不足而失败
    if (Hero.Inventory.PurchaseItem[ExpensiveItem]):
        Print("Purchase successful!")
    else:
        Print("Purchase failed - gold remains at {Hero.Inventory.Gold}")

    # 将高阶函数与嵌套函数谓词结合使用
    IsRareOrLegendary(I:game_item)<decides>:void =
        I.Rarity = item_rarity.rare or I.Rarity = item_rarity.legendary

    RareItems := Hero.Inventory.FilterItems(IsRareOrLegendary)

    Print("Found {RareItems.Length} rare items")
```
<!--NoCompile-->
```verse
WaypointComponent<public> := class<final_super><abstract>(component) {
    @editable Index:int = 0;

    EditorOnlySessionEnvironmentAllowList:[]session_environment = array{};

    MeshComponent<protected>:castable_subtype((/Verse.org:)SceneGraph.mesh_component) = (/Verse.org:)SceneGraph.mesh_component;

    GetBounds<public>():vector3;

    OnBeginSimulation<override>():void = {
        Self.Entity.GetComponent[Self.MeshComponent] or Err("Invalid SceneGraph.mesh_component");
    };
};
```
### 内嵌文本示例
该示例从 Verse 丰富的类型系统开始。类型自然地在代码中流动；许多类型注释被省略，因为它们是可以推断的。当我们指定类型（例如 `Items:[]game_item`）时，它们会记录意图，而不仅仅是满足编译器的要求。 `item_rarity` 枚举提供类型安全常量，无需传统枚举的样板。标记为 `<persistable>` 的 `item_stats` 结构可以从持久存储中保存和加载，这对于游戏保存至关重要。 `game_item` 类使用 `<unique>` 来确保引用相等语义。

### UnrealEngine.digest.verse（简化）
<!--NoCompile-->
```verse
# 版权所有 Epic Games, Inc. 保留所有权利。
#################################################
# 生成的 Verse API 摘要
# 不要手动修改它！
# 从构建生成：++Fortnite+Release-39.30-CL-50141518
#################################################

Itemization<public> := module:
    using {/Verse.org/Assets}
    using {/Verse.org/Presentation}
    using {/Verse.org/Simulation}
    using {/Verse.org/Native}
    using {/Verse.org/SceneGraph}
    @experimental
    add_item_result<native><public> := class<epic_internal>:
        # 由于交易而新添加到此库存的项目。
        AddedItems<native><public>:[]entity

        # 堆栈大小因事务而更改的项目以及之前的堆栈大小值。
        ModifiedItems<native><public>:[]tuple(entity, int)

    @experimental
    equip_item_result<native><public> := class<epic_internal>:
        Item<native><public>:entity

    @experimental
    # 添加商品时，“find_inventory_event”首先遍历来查找商品的最佳库存。它是延续的。
    # “add_item_query_event”可用于否决库存选择。它是向上发送的。
    find_inventory_event<native><public> := class<epic_internal>(scene_event):
        ItemComponent<native><public>:item_component

        var ChosenInventory<native><public>:?inventory_component = external {}

        var ChosenInventoryPriority<native><public>:float = external {}

    @available {MinUploadedAtFNVersion := 3800}
    @experimental
    (Item:item_component).CanEquip<native><public>()<transacts>:result(false, []equip_item_error)

WebAPI<public> := module:
    # 用途：
    #     允许用户在其模块中创建“client_id”的派生版本。
    #     然后，派生的“client_id”的诗类路径将用于初始化
    #     后端服务中的配置密钥映射到您的端点。
    # 
    #     警告：不要将派生的“client_id”类公开。此物品
    #     输入是您头部的私钥。
    # 
    # 示例：
    #     my_client_id<internal> := class<final><computes>(client_id)
    #     MyClient<internal> := MakeClient(my_client_id)
    client_id<native><public> := class<abstract><computes>:

    client<native><public> := class<final><computes><internal>:
        Get<native><public>(Path:string)<suspends>:response

    response<native><public> := class<internal>:

    body_response<native><public> := class<internal>(response):
        GetBody<native><public>()<computes>:string

    MakeClient<native><public>(ClientId:client_id)<converges>:client

# 模块导入路径：/UnrealEngine.com/SceneGraph
(/UnrealEngine.com:)SceneGraph<public> := module:
    using {/Verse.org/Native}
Temporary<public> := module:
    # 模块导入路径：/UnrealEngine.com/Temporary/UI
    UI<public> := module:
        using {/Verse.org/Assets}
        using {/Verse.org/Colors}
        using {/UnrealEngine.com/Temporary/SpatialMath}
        using {/Verse.org/Simulation}
        # 返回与“Player”关联的“player_ui”。
        # 如果没有与“Player”关联的“player_ui”，则失败。
        GetPlayerUI<native><public>(Player:player)<transacts><decides>:player_ui

        # 文本对齐值：
        #   左：根据当前文化将文本逻辑地向左对齐。
        #   居中：将文本居中对齐。
        #   右：根据当前文化，在逻辑上将文本向右对齐。
        # 当本地文化是从右到左时，“左”和“右”值将会翻转。
        text_justification<native><public> := enum:
            Left
            Center
            Right
            InvariantLeft
            InvariantRight

        # 文本小部件的基础小部件。
        text_base<native><public> := class<abstract>(widget):
            # 设置显示文本的不透明度。
            SetTextOpacity<native><public>(InOpacity:type {_X:float where 0.000000 <= _X, _X <= 1.000000}):void

            # 获取显示文本的不透明度。
            GetTextOpacity<native><public>():type {_X:float where 0.000000 <= _X, _X <= 1.000000}

    # 模块导入路径：/UnrealEngine.com/Temporary/SpatialMath
    (/UnrealEngine.com/Temporary:)SpatialMath<public> := module:
        using {/Verse.org/SpatialMath}
        using {/Verse.org/Native}
        using {/Verse.org/Simulation}
        @editable
        @import_as("/Script/EpicGamesTemporary.FVerseRotation_Deprecated")
        (/UnrealEngine.com/Temporary/SpatialMath:)rotation<native><public> := struct<concrete>:

        @vm_no_effect_token
        # 通过按顺序输入“YawRightDegrees”、“PitchUpDegrees”和“RollClockwiseDegrees”来进行“旋转”：
        #  * 首先是绕 Z 轴的*偏航*，正角度表示从上方观察时顺时针旋转，
        #  * 然后围绕新的 Y 轴进行*俯仰*，正角度表示“机头向上”，
        #  * 随后围绕新的 X 轴进行*滚动*，正角度表示沿 +X 方向观察时顺时针旋转。
        # 请注意，这些约定与“MakeRotation”不同，但与“ApplyYaw”、“ApplyPitch”和“ApplyRoll”匹配。
        (/UnrealEngine.com/Temporary/SpatialMath:)MakeRotationFromYawPitchRollDegrees<native><public>(YawRightDegrees:float, PitchUpDegrees:float, RollClockwiseDegrees:float)<reads><converges>:(/UnrealEngine.com/Temporary/SpatialMath:)rotation

JSON<public> := module:
    value<native><public> := class:
        # 检索对象值，如果值不是 json 对象，则失败
        AsObject<native><public>()<transacts><decides>:[string]value

    # 解析JSON字符串，返回一个值及其内容
    Parse<native><public>(JSONString:string)<transacts><decides>:value

# 模块导入路径：/UnrealEngine.com/ControlInput
ControlInput<public> := module:
    using {/Verse.org/Assets}
    using {/Verse.org/Native}
    using {/Verse.org/Simulation}
    @available {MinUploadedAtFNVersion := 3630}
    # input_events 是可以订阅的用户输入事件的容器。
    #   * 使用“GetPlayerInput”和“GetInputEvents”函数检索给定玩家的 input_events 对象。
    #   * 当前输入用户的低级别通知：DetectionBeginEvent、DetectionOngoingEvent 和DetectionEndEvent。
    #   * 触发事件的高级通知：ActivationTriggeredEvent 和 ActivationCanceledEvent。
    # 
    #                         /—----------<-------\ 
    #  检测开始事件 -> 检测正在进行事件 -> 激活触发事件 -> 检测结束事件
    #            /\                         /\                                            / 
    #              \---------------------> ActivationCanceledEvent ----------------------/
    input_events<native><public>(t:type) := class<epic_internal>:
        (/UnrealEngine.com/ControlInput/input_events:)ControlInput_input_events_Variance<private>:?type {_():tuple(t)} = external {}

        # 此输入已满足所有必需条件并已成功触发。大多数时候，您应该绑定到此事件。
        #  元组有效负载：0：生成此事件的玩家
        #                 1：物理输入产生的值
        ActivationTriggeredEvent<native><public>:listenable(tuple(player, t)) = external {}

    @available {MinUploadedAtFNVersion := 3630}
    # 这是播放器输入相关设置和功能的主要管理器类。
    player_input<native><public> := class:
        GetInputEvents<native><public>(ActionToBind:input_action(t) where t:type):input_events(t)

# 模块导入路径：/UnrealEngine.com/BasicShapes
BasicShapes<public> := module:
    using {/Verse.org/SceneGraph}

    sphere<public> := class<final><public>(mesh_component):

# 模块导入路径：/UnrealEngine.com/Assets
(/UnrealEngine.com:)Assets<public> := module:
    using {/Verse.org/SpatialMath}
    using {/UnrealEngine.com/Temporary/SpatialMath}
    using {/Verse.org/Assets}
    SpawnParticleSystem<native><public>(Asset:particle_system, Position:(/UnrealEngine.com/Temporary/SpatialMath:)vector3, ?Rotation:(/UnrealEngine.com/Temporary/SpatialMath:)rotation = external {}, ?StartDelay:float = external {})<transacts>:cancelable

    SpawnParticleSystem<native><public>(Asset:particle_system, Position:(/Verse.org/SpatialMath:)vector3, ?Rotation:(/Verse.org/SpatialMath:)rotation = external {}, ?StartDelay:float = external {})<transacts>:cancelable
```
