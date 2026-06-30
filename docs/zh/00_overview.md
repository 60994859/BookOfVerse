# Verse 编程语言

## 概述

Verse 是 Epic Games 开发的一种多范式编程语言，用于在 Fortnite 的虚幻编辑器中创建游戏玩法并在元宇宙中构建体验。 Verse 借鉴了函数式、逻辑式和命令式传统，代表着对传统编程语言的背离，其设计不仅是为了满足当今的需求，而且还着眼于未来几十年甚至几个世纪的愿景。

Verse 建立在三个基本原则之上：

- **这只是代码**：
可能需要特殊语法或其他语言结构的复杂概念被表达为常规 Verse 代码。这并不神奇——一切都是由相同的原始构造构建的，创建了一个统一且可预测的编程模型。

- **只有一种语言**：
相同的语言构造在编译时和运行时都有效。没有预处理器。无论是在编译期间还是在运行时，您编写的内容都会执行。

- **元宇宙第一**：
Verse 是为未来代码在单一全局模拟（元宇宙）中运行而设计的。这影响了语言的各个方面，从强大的兼容性保证到跟踪副作用并确保安全并发执行的效果系统。

Verse的目标是：

- **足够简单**，适合初次程序员学习，具有一致的规则和最少的特殊情况。

- **对于复杂的游戏逻辑和分布式系统来说足够强大**，具有可扩展到大型代码库的高级功能。

- **足够安全**，不受信任的代码可以在共享环境中运行，具有强大的沙箱和效果跟踪功能。

- 对于实时游戏和模拟来说**足够快**，并且实现可以积极优化纯计算。

- **足够稳定**可以持续数十年，具有强大的向后兼容性保证和精心的演进。

**为什么是Verse？**

传统的编程语言带有数十年的历史包袱和设计妥协。Verse以全新的方式开始，向过去学习，但不受其束缚。它是为未来而设计的：

- 代码永远存在于持久的元宇宙中
- 数百万开发人员为共享代码库做出贡献
- 程序默认必须是安全的、并发的、可组合的
- 向后兼容不是可选的而是必需的
- 编译时和运行时之间的界限是不稳定的

准备好潜入了吗？从[内置类型](02_primitives.md)开始了解 Verse 的基本数据类型，或跳转到[表达式](01_expressions.md)以了解 Verse 中的所有内容如何计算值。

对于来自其他语言的经验丰富的程序员来说，[失败](08_failure.md) 和[效果](13_effects.md) 部分重点介绍了 Verse 的一些独特功能。

## 主要特点

**一切都是表达**

在 Verse 中，没有语句——一切都是产生值的表达式。这创建了一个高度可组合的系统，其中任何代码都可以在任何需要值的地方使用。

<!--versetest
Condition()<computes><decides> :void= {}
Array :[]int= array{1}
-->
<!-- 01 -->
```verse
# 甚至控制流也会产生价值
Result := if (Condition[]) then "yes" else "no"

# 循环是表达式
Multiply := for (X : Array) { X * 42 }
```

**作为控制流的失败**

Verse 使用失败作为主要控制流机制，而不是布尔条件和异常。表达式可以成功（产生值）或失败（不产生值），从而实现自然的控制流模式：

<!--versetest
ValidateInput(x:string)<computes><decides>:void= {}
ProcessData(x:string)<computes>:void= {}
myclass := class{
Data:string="hi"
M()<decides>:void=
    ValidateInput[Data] # Square brackets indicate that this function may fail
    ProcessData(Data)   # Data is only processed if valid, parentheses mean must succeed
}
<#
-->
<!-- 02 -->
```verse
ValidateInput[Data] # 方括号表示该函数可能会失败
ProcessData(Data)   # 仅当数据有效时才处理数据，括号表示必须成功
```
<!-- #> -->

有关可失败表达式和失败上下文的完整详细信息，请参阅[失败](08_failure.md)，有关 if 表达式的完整详细信息，请参阅[控制流](07_control.md)。

**强静态类型与推理**

Verse 具有强大的类型系统，可以在编译时捕获错误，同时通过推理最大限度地减少对类型注释的需求。有关类型系统和子类型的完整详细信息，请参阅[类型](11_types.md)。

<!--versetest-->
<!-- 03 -->
```verse
X := 42                    # 类型推断
Name := "Verse"            # 类型推断
```

**效果追踪**

函数通过 `<computes>`、`<reads>`、`<writes>`、`<transacts>`、`<decides>` 和 `<suspends>` 等说明符声明其副作用。这些效果说明符使我们立即清楚函数除了计算其返回值之外还能做什么：

<!--versetest
x := class:
    GetCurrentValue()<reads>:int=1
    var Score:int=0
    PureCompute()<computes>:int = 2 + 2            # No side effects
    ReadState()<reads>:int = GetCurrentValue()     # Can read mutable state
    UpdateGame()<transacts>:void = set Score += 10 # Can read, write, allocate
<#
-->
<!-- 04 -->
```verse
PureCompute()<computes>:int = 2 + 2            # 无副作用
ReadState()<reads>:int = GetCurrentValue()     # 可以读取可变状态
UpdateGame()<transacts>:void = set Score += 10 # 可以读、写、分配
```
<!-- #> -->

有关效果系统的完整详细信息，请参阅[效果](13_effects.md)。

**内置并发**

并发性是具有结构化并发原语的一流功能，使并发编程变得安全且可预测。

<!--versetest
TaskA()<suspends>:void={}
TaskB()<suspends>:void={}
TaskC():void={}
FastPath()<suspends>:void={}
SlowButReliablePath()<suspends>:void={}
M()<suspends>:void=
    # Run tasks concurrently and wait for all
    sync:
        TaskA()
        TaskB()
        TaskC()

    # Race tasks and take first result
    race:
        FastPath()
        SlowButReliablePath()
<#
-->
<!-- 05 -->
```verse
# 同时运行任务并等待所有任务
sync:
    TaskA()
    TaskB()
    TaskC()

# 竞赛任务并获得第一个结果
race:
    FastPath()
    SlowButReliablePath()
```
<!-- #> -->

**推测执行**

Verse 可以推测性地执行代码，并在执行失败时回滚更改，从而启用强大的验证和错误处理模式。

<!--versetest
TryComplexOperation()<computes><decides>:void={}
-->
<!-- 06 -->
```verse
if (TryComplexOperation[]):
    # 由 TryComplexOperation[] 执行的更改已提交
else:
    # 更改会自动回滚
```

**使用实时变量进行响应式编程**

Verse 通过实时变量为反应式编程提供一流的支持，当依赖项发生变化时，实时变量会自动重新计算，从而减少手动事件处理的需要。

<!--versetest
Log(:string)<transacts>:void={}
-->
<!-- 07 -->
```verse
var MaxHealth:int = 100
var Damage:int = 0
var live Health:int = MaxHealth - Damage

# 当依赖关系发生变化时，运行状况会自动更新
set Damage = 20      # 健康变成80
set MaxHealth = 150  # 健康值变为130

# 用于事件处理的反应式结构
when(Health < 25):
    Log("Low health warning!")
```

欢迎使用 Verse——一种不仅为今天的游戏而构建的语言，而且还为明天的元宇宙而构建。

## 一个例子

让我们通过一个演示其主要功能的示例来探索该语言。我们将为游戏构建一个库存管理系统，展示 Verse 的构造如何组合在一起创建健壮、可维护的代码。

<!--NoCompile-->
<!-- 08 -->
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
game_item := class<final><unique><persistable>:
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
            _ => {false?; 0.0}  # 如果该项目是传奇的或意外的，则失败
    
    # 使用封闭世界函数计算属性
    GetEffectiveValue()<transacts><decides>:int=
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
    FilterItems(Predicate:type{_(:game_item)<decides>:void}):[]game_item =
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
<!--

The above has some superfluous <transacts> due to <no_rollback>, in some cases they could be just <computes>.  Apparently an Old VM pathology

Also methods that have an empty return type have weird behavior in some cases. Easily fixed by typing them.
-->

此示例展示了实际环境中的 Verse。让我们探讨一下这段代码的独特之处是什么：

**类型系统和数据建模**

该示例从 Verse 丰富的类型系统开始。类型自然地在代码中流动；许多类型注释被省略，因为它们是可以推断的。当我们指定类型（例如 `Items:[]game_item`）时，它们会记录意图，而不仅仅是满足编译器的要求。 `item_rarity` 枚举提供类型安全常量，无需传统枚举的样板。标记为 `<persistable>` 的 `item_stats` 结构可以从持久存储中保存和加载，这对于游戏保存至关重要。 `game_item` 类使用 `<unique>` 来确保引用相等语义。  

**作为控制流的失败**

在整个代码中，失败驱动控制流，而不是异常或错误代码。 `<decides>` 效果标记可能失败的函数，并且失败通过表达式自然传播。当 `GetRarityMultiplier()` 遇到未知的稀有度时，它不会抛出异常或返回哨兵值 - 它只是失败，并且调用代码会优雅地处理此问题。
`AddItem` 方法演示了失败如何创建优雅的验证。表达式 `NewWeight <= MaxWeight` 要么成功（允许继续执行），要么失败（阻止添加项目）。没有明确的控制流程——只是对必须为真的声明性断言。

**事务语义和推测执行**

标有 `<transacts>` 的方法提供失败时的自动回滚。在`PurchaseItem`中，我们从玩家身上扣除金币，然后尝试添加该物品。如果添加失败（可能是由于重量限制），金币扣除额将自动回滚。这消除了与部分状态更新相关的整个类别的错误。
这种事务行为扩展到复杂的操作。当多个更改需要同时成功或失败时，Verse 可确保一致性，而无需手动清理。

**函数作为一流的值**

`FilterItems` 方法接受谓词函数，演示高阶编程。 `RunExample` 中的嵌套函数 `IsRareOrLegendary` 显示了如何在本地定义函数并像任何其他值一样传递函数。这种函数式编程风格与命令式和面向对象的特性自然地结合在一起。

**可选类型和查询运算符**

库存删除逻辑使用可选类型 (`?game_item`) 来表示可能不存在的值。查询运算符 `?` 从选项中提取值，如果选项为空，则失败。这消除了空指针异常，同时提供了处理缺失值的便捷语法。

**模式匹配和控制流**

`GetRarityMultiplier` 中的 `case` 表达式演示了模式匹配。与 switch 语句不同，`case` 是一个生成值的表达式。下划线 `_` 提供了一种包罗万象的模式，尽管在本例中它会导致失败。
`if` 表达式类似地生成值并可以在其条件下绑定变量。复合条件显示了如何通过自动失败传播来链接多个操作。

**模块系统和访问控制**

该代码以 `using` 语句开头，这些语句从其他模块导入功能。基于路径的模块系统确保依赖关系明确且可永久寻址。 `<public>` 等访问说明符可在细粒度级别控制可见性。

**默认情况下不可变**数据结构是不可变的，除非明确标记为 `var`。这消除了大量的错误并使并发编程更安全。当我们确实需要突变时，它是明确的并由效果系统跟踪。有关 `var` 和 `set` 的完整详细信息，请参阅[可变性](05_mutability.md)。

## 命名约定

Verse 有一组命名约定，使代码可读且可预测。虽然该语言不强制执行这些约定，但遵循它们可确保您的代码与更广泛的 Verse 生态系统良好集成，并立即为其他 Verse 开发人员所熟悉。

标识符应采用 PascalCase（驼峰式命名法，大写开头）：

<!--versetest
player_record := struct:
    Name:string

PlayerDatabase(Id:int)<decides>:player_record =
    if (Id = 0):
        player_record{Name := "Alice"}
    else if (Id = 1):
        player_record{Name := "Bob"}
    else:
        false?
        player_record{Name := ""}
-->
<!-- 09 -->
```verse
# 变量和常量使用 PascalCase
PlayerHealth:int = 100
MaxInventorySize:int = 50
IsGameActive:logic = true

# 函数使用 PascalCase
CalculateDamage(Base:float, Multiplier:float):float =
    Base * Multiplier

GetPlayerName(Id:int)<decides>:string =
    PlayerDatabase[Id].Name

# 类和结构使用snake_case
player_character := class:
    Name:string
    Level:int

inventory_item := struct:
    ItemId:int
    Quantity:int

# 枚举其值使用snake_case
game_state := enum:
    main_menu
    in_game
    paused
    game_over
```

通用类型参数使用单个小写字母或简短的描述性名称：

<!--versetest-->
<!-- 10 -->
```verse
# 简单泛型的单个字母
Find(Array:[]t, Target:t where t:type):?int = false

# 复杂关系的描述性名称
Transform(Input:in_t, Processor:type{_(:in_t):out_t} where in_t:type, out_t:type):?out_t = false
```
模块名称始终使用 PascalCase，包括路径段：

<!--NoCompile-->
<!-- 11 -->
```verse
# 模块定义
InventorySystem := module:
    # 模块内容

# 路径段也使用 PascalCase
using { /Fortnite.com/Characters/PlayerController }
using { /MyGame.com/Systems/CombatSystem }
using { /Verse.org/Random }
```

类和结构体字段使用 PascalCase，方法遵循与函数相同的 PascalCase 约定：

<!--versetest-->
<!-- 12 -->
```verse
player := class:
    Name:string          # 字段的帕斯卡命名法
    var Health:float= 0.0

    # 方法使用类似 PascalCase 的函数
    TakeDamage(Amount:float):void =
        set Health = Max(0.0, Health - Amount)

    IsAlive():logic =
        logic{Health > 0.0}
```

## 代码格式化

Verse代码遵循一致的格式模式以强调可读性。

使用四个空格来缩进代码块。冒号引入一个块，后续行缩进：

<!--versetest
Condition()<decides><transacts>:void = {}
DoSomething()<transacts>:void = {}
DoSomethingElse()<transacts>:void = {}
Inventory:[]int = array{1, 2, 3}
ProcessItem(Item:int)<transacts>:void = {}
UpdateDisplay()<transacts>:void = {}
ImplementationHere()<transacts>:void = {}

-->
<!-- 13 -->
```verse
if (Condition[]):
    DoSomething()
    DoSomethingElse()

for (Item : Inventory):
    ProcessItem(Item)
    UpdateDisplay()

class_definition := class:
    Field1:int
    Field2:string

    Method():void =
        ImplementationHere()
```
复杂的表达式受益于显示结构的清晰格式：

<!--versetest
player_type := struct{Health:int = 75}
BaseDamage:float = 100.0
LevelMultiplier:float = 1.5
BonusPercentage:float = 10.0
rarity_type := enum{common; uncommon; rare; epic; legendary}
-->
<!-- 14 -->
```verse
Player:player_type = player_type{}
Rarity:rarity_type = rarity_type.rare

# 多行条件语句
Result := if (Player.Health > 50):
    "healthy"
else if (Player.Health > 20):
    "injured"
else:
    "critical"

# 具有明确优先级的链式操作
FinalDamage :=
    BaseDamage *
    LevelMultiplier *
    (1.0 + BonusPercentage / 100.0)

# 与对齐案例的模式匹配
DamageMultiplier := case(Rarity):
    rarity_type.common => 1.0
    rarity_type.uncommon => 1.5
    rarity_type.rare => 2.0
    rarity_type.epic => 3.0
    rarity_type.legendary => 5.0
```
函数遵循一致的模式，并明确指定效果和返回类型：

<!--versetest
difficulty_level := enum{easy; medium; hard}
ValidateAmount(Amount:int)<transacts><decides>:void = {}
DeductBalance(Amount:int)<transacts>:void = {}
RecordTransaction()<transacts>:void = {}
GetBaseReward(Difficulty:difficulty_level)<decides>:?int = option{100}
CalculateTimeBonus(CompletionTime:float):int = 50
-->
<!-- 15 -->
```verse
# 简单的纯函数
Add(X:int, Y:int)<computes>:int = X + Y

# 功能与效果
ProcessTransaction(Amount:int)<transacts><decides>:void =
    ValidateAmount[Amount]
    DeductBalance(Amount)
    RecordTransaction()

# 多行功能，结构清晰
CalculateReward(
    PlayerLevel:int,
    Difficulty:difficulty_level,
    CompletionTime:float
)<decides>:int =
    BaseReward := GetBaseReward[Difficulty]?
    LevelBonus := PlayerLevel * 10
    TimeBonus := CalculateTimeBonus(CompletionTime)
    BaseReward + LevelBonus + TimeBonus
```

## 评论

注释在执行过程中会被忽略，但对于理解和维护代码很有价值。 Verse 提供多种注释风格，以满足不同的文档需求。最简单的是单行注释，以 `#` 开头，一直到行尾：

<!--versetest-->
<!-- 16 -->
```verse
CalculateDamage := 100 * 1.5  # 应用暴击倍数
```
当您需要在一行代码中记录某些内容而不将其分解时，内联块注释提供了完美的解决方案。这些包含在 `<#` 和 `#>` 之间：

<!--versetest
BaseValue:int = 100
Multiplier:int = 2
Bonus:int = 10
-->
<!-- 17 -->
```verse
Result := BaseValue <# 原始金额 #> * Multiplier <# 比例因子 #> + Bonus
```
同样可以用来编写多行块注释，使它们成为解释复杂算法或提供详细上下文的理想选择：

<!--versetest-->
<!-- 18 -->
```verse
<# 该函数实现了二次伤害衰减公式
   used throughout the game. The falloff ensures that damage
   decreases smoothly with distance, creating strategic positioning
   choices for players. #>
CalculateFalloffDamage(Distance:float, MaxDamage:float):float =
    MaxDamage  # 实施这里
```
块注释嵌套，它允许您暂时禁用已包含注释的代码，而无需删除或修改现有文档：

<!--versetest-->
<!-- 19 -->
```verse
<# 暂时禁用以进行测试
   OriginalFunction()  <# 这有一个错误#>
   NewFunction()       # 测试这种方法
#>
```
缩进注释以 `<#>` 开头；后续行中缩进四个空格的所有内容都将成为注释的一部分：

<!--versetest
DoSomething():void = {}
-->
<!-- 20 -->
```verse
<#>
    This entire block is a comment because it's indented.
    It provides a clean way to write longer documentation
    without cluttering each line with comment markers.

DoSomething()  # 不属于评论的一部分。
```
## 句法风格

Verse 提供灵活的语法来适应不同的编程风格。可以使用大括号、缩进或内联形式来表达相同的逻辑，从而允许您为每个上下文选择最清晰的表示形式。

大括号样式使用花括号来分隔块，这在 C 系列语言中很常见：

<!--versetest
Score:int = 85
-->
<!-- 21 -->
```verse
Result := if (Score > 90) {
    "excellent"
} else if (Score > 70) {
    "good"
} else {
    "needs improvement"
}
```
缩进样式使用冒号和缩进来定义结构，类似于Python：

<!--versetest
Score:int = 85
-->
<!-- 22 -->
```verse
Result := if (Score > 90):
    "excellent"
else if (Score > 70):
    "good"
else:
    "needs improvement"
```
对于简单的表达式，内联样式将所有内容保持在一行上：

<!--versetest
Score:int = 85
-->
<!-- 23 -->
```verse
Result := if (Score > 90) then "excellent" else if (Score > 70) then "good" else "needs improvement"
```
点式样式使用句点来引入表达式：

<!--versetest
Score:int = 85
-->
<!-- 24 -->
```verse
Result := if (Score > 90). "excellent" else if (Score > 70). "good" else. "needs improvement"
```
您甚至可以在有意义时混合样式：

<!--versetest
ComplexCondition()<transacts><decides>:void = {}
AnotherCheck()<transacts><decides>:void = {}
YetAnotherValidation()<transacts><decides>:void = {}
-->
<!-- 25 -->
```verse
Result := if:
    ComplexCondition[] and
    AnotherCheck[] and
    YetAnotherValidation[]
then { "condition met" } else { "condition not met" }
```
所有这些形式都会产生相同的结果。它们之间的选择取决于可读性和上下文。 
使用现有的大括号代码时使用大括号，缩进以实现更清晰的垂直布局，
以及简单表达式的内联形式。这种灵活性使您可以编写易于阅读的代码。
