# Verse 编程语言

## 概述

Verse 是 Epic Games 开发的一种多范式编程语言，用于在 Unreal Editor for Fortnite 中创建游戏玩法，以及在元宇宙中构建体验。Verse 融合了函数式、逻辑式和命令式的传统，与传统的编程语言截然不同——它不只着眼于当下需求，更怀揣着跨越数十年甚至数世纪的愿景。

Verse 建立在三个基本原则之上：

- **就是代码**：
  在其他语言中可能需要特殊语法或结构的复杂概念，在 Verse 中都用常规的 Verse 代码来表达。没有魔法——一切都由相同的基本构造构建而成，形成了一个统一且可预测的编程模型。

- **只有一种语言**：
  相同的语言构造在编译时和运行时都有效。没有预处理器。你写什么就执行什么，无论是在编译期间还是在运行时。

- **元宇宙优先**：
  Verse 为代码运行在单一全局模拟（即元宇宙）中的未来而设计。这影响了语言的方方面面，从强大的兼容性保证到追踪副作用并确保安全并发执行的效果系统。

Verse 的目标是：

- **足够简单**，让初次接触的程序员也能学习，拥有一致的规则和最少特例。

- **足够强大**，能处理复杂的游戏逻辑和分布式系统，具备可扩展到大型代码库的高级特性。

- **足够安全**，让不受信任的代码也能在共享环境中运行，拥有强大的沙箱和效果追踪能力。

- **足够快速**，满足实时游戏和模拟的需求，其实现能够积极优化纯计算。

- **足够稳定**，能够持续数十年，拥有强大的向后兼容性保证和谨慎的演进策略。

**为什么选择 Verse？**

传统编程语言背负着数十年的历史包袱和设计妥协。Verse 从零开始，借鉴过去但不受其束缚。它为这样一个未来而设计：

- 代码在持久化的元宇宙中永续存在
- 数百万开发者共同贡献于一个共享的代码库
- 程序在默认情况下必须是安全、并发和可组合的
- 向后兼容性不是可选项，而是必需品
- 编译时和运行时之间的界限是流动的

准备好深入探索了吗？从[内置类型](02_primitives.md)开始了解 Verse 的基本数据类型，或者跳到[表达式](01_expressions.md)看看 Verse 中一切如何计算值。

对于来自其他语言的经验丰富的程序员，[失败系统](08_failure.md)和[效果](13_effects.md)部分突出展示了 Verse 的一些独特特性。

## 核心特性

**一切皆表达式**

在 Verse 中没有语句——一切皆是产生值的表达式。这创建了一个高度可组合的系统，任何代码片段都可以在期望值的地方使用。

<!--versetest
Condition()<computes><decides> :void= {}
Array :[]int= array{1}
-->
<!-- 01 -->
```verse
# Even control flow produces values
Result := if (Condition[]) then "yes" else "no"

# Loops are expressions
Multiply := for (X : Array) { X * 42 }
```

**失败即控制流**

Verse 使用失败作为主要的控制流机制，而非布尔条件和异常。表达式可以成功（产生一个值）或失败（不产生值），从而实现自然的控制流模式：

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
ValidateInput[Data] # Square brackets indicate that this function may fail
ProcessData(Data)   # Data is only processed if valid, parentheses mean must succeed
```
<!-- #> -->

有关可失败表达式和失败上下文的完整细节，请参见[失败](08_failure.md)，关于 if 表达式请参见[控制流](07_control.md)。

**带推断的强静态类型**

Verse 拥有强大的类型系统，在编译时捕获错误，同时通过类型推断最大程度减少类型标注的需求。有关类型系统和子类型的完整细节，请参见[类型](11_types.md)。

<!--versetest-->
<!-- 03 -->
```verse
X := 42                    # Type inferred 
Name := "Verse"            # Type inferred
```

**效果追踪**

函数通过诸如 `<computes>`、`<reads>`、`<writes>`、`<transacts>`、`<decides>` 和 `<suspends>` 等说明符来声明其副作用。这些效果说明符让人一眼就能看出函数除了计算返回值之外还能做什么：

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
PureCompute()<computes>:int = 2 + 2            # No side effects
ReadState()<reads>:int = GetCurrentValue()     # Can read mutable state
UpdateGame()<transacts>:void = set Score += 10 # Can read, write, allocate
```
<!-- #> -->

有关效果系统的完整细节，请参见[效果](13_effects.md)。

**内置并发**

并发是一等特性，拥有结构化并发原语，使并发编程变得安全且可预测。

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
# Run tasks concurrently and wait for all
sync:
    TaskA()
    TaskB()
    TaskC()

# Race tasks and take first result
race:
    FastPath()
    SlowButReliablePath()
```
<!-- #> -->

**推测执行**

Verse 可以推测性地执行代码，并在执行失败时回滚更改，从而实现强大的验证和错误处理模式。

<!--versetest
TryComplexOperation()<computes><decides>:void={}
-->
<!-- 06 -->
```verse
if (TryComplexOperation[]):
    # Changes performed by TryComplexOperation[] are committed
else:
    # Changes are rolled back automatically
```

**基于实时变量的响应式编程**

Verse 通过实时变量为一等响应式编程提供支持，当依赖项发生变化时，实时变量会自动重新计算，从而减少手动事件处理的需求。

<!--versetest
Log(:string)<transacts>:void={}
-->
<!-- 07 -->
```verse
var MaxHealth:int = 100
var Damage:int = 0
var live Health:int = MaxHealth - Damage

# Health automatically updates when dependencies change
set Damage = 20      # Health becomes 80
set MaxHealth = 150  # Health becomes 130

# Reactive constructs for event handling
when(Health < 25):
    Log("Low health warning!")
```

欢迎使用 Verse——一门不仅为今天的游戏而构建，更为未来的元宇宙而生的语言。

## 示例

让我们通过一个展示其核心特性的示例来探索这门语言。我们将为一个游戏构建库存管理系统，展示 Verse 的各种构造如何协同工作，创建健壮、可维护的代码。

<!--NoCompile-->
<!-- 08 -->
```verse
# Module declaration - start by importing utility functions
using { /Verse.org/VerseCLR }

# Define item rarity as an enumeration - showing Verse's type system
item_rarity := enum<persistable>:
    common
    uncommon
    rare
    epic
    legendary

# Struct for immutable item data - functional programming style
item_stats := struct<persistable>:
    Damage:float = 0.0
    Defense:float = 0.0
    Weight:float = 1.0
    Value:int = 0

# Class for game items - object-oriented features with functional constraints
game_item := class<final><unique><persistable>:
    Name:string
    Rarity:item_rarity = item_rarity.common
    Stats:item_stats = item_stats{}
    StackSize:int = 1
    
    # Method with decides effect - can fail
    GetRarityMultiplier()<decides>:float =
        case(Rarity):
            item_rarity.common => 1.0
            item_rarity.uncommon => 1.5
            item_rarity.rare => 2.0
            item_rarity.epic => 3.0
            _ => {false?; 0.0}  # Fails if the item is legenday or unexpected
    
    # Computed property using closed-world function
    GetEffectiveValue()<transacts><decides>:int=
        Floor[Stats.Value * GetRarityMultiplier[]]

# Inventory system with state management and effects
inventory_system := class:
    var Items:[]game_item = array{}
    var MaxWeight:float = 100.0
    var Gold:int = 1000

    # Method demonstrating failure handling and transactional semantics
    AddItem(NewItem:game_item)<transacts><decides>:void =
        # Calculate new weight - speculative execution
        CurrentWeight := GetTotalWeight()
        NewWeight := CurrentWeight + NewItem.Stats.Weight

        # This check might fail, rolling back any changes
        NewWeight <= MaxWeight
        
        # Only executes if weight check passes
        set Items += array{NewItem}
        Print("Added {NewItem.Name} to inventory")

    # Method with query operator and failure propagation
    RemoveItem(ItemName:string)<transacts><decides>:game_item =
        var RemovedItem:?game_item = false
        var NewItems:[]game_item = array{}
        
        for (Item : Items):
            if (Item.Name = ItemName, not RemovedItem?):
                set RemovedItem = option{Item}
            else:
                set NewItems += array{Item}
        set Items = NewItems
        RemovedItem?  # Fails if item not found

    # Purchase with complex failure logic and rollback
    PurchaseItem(ShopItem:game_item)<transacts><decides>:void =
        # Multiple failure points - any failure rolls back all changes
        Price := ShopItem.GetEffectiveValue[]
        Price <= Gold  # Fails if not enough gold
        
        # Tentatively deduct gold
        set Gold = Gold - Price
        
        # Try to add item - might fail due to weight
        AddItem[ShopItem]
        
        # All succeeded - changes are committed
        Print("Purchased {ShopItem.Name} for {Price} gold")

    # Higher-order function with type parameters and where clauses
    FilterItems(Predicate:type{_(:game_item)<decides>:void}):[]game_item =
        for (Item : Items, Predicate[Item]):
            Item

    GetTotalWeight()<transacts>:float =
        var Total:float = 0.0
        for (Item : Items):
            set Total += Item.Stats.Weight
        Total

# Player class using composition
player_character<public> := class:
    Name<public>:string
    var Level:int = 1
    var Experience:int = 0
    var Inventory:inventory_system = inventory_system{}
    
    LevelUpThreshold := 100

    GainExperience(Amount:int)<transacts>:void =
        set Experience += Amount
        
        # Automatic level up check with failure handling
        loop:
            RequiredXP := LevelUpThreshold * Level
            if (Experience >= RequiredXP):
                set Experience -= RequiredXP
                set Level += 1
                Print("{Name} leveled up to {Level}!")
            else:
                break
    
    # Method showing qualified access
    EquipStarterGear()<transacts><decides>:void =
        StarterSword := game_item{
            Name := "Rusty Sword"
            Rarity := item_rarity.common
            Stats := item_stats{Damage := 10.0, Weight := 5.0, Value := 50}
        }
        # These might fail if inventory is full
        Inventory.AddItem[StarterSword]

# Example usage demonstrating control flow and failure handling
RunExample<public>()<suspends>:void =
    # Create a player (can't fail)
    Hero := player_character{Name := "Verse Hero"}
    
    # Try to equip starter gear (might fail)
    if (Hero.EquipStarterGear[]):
        Print("Hero equipped with starter gear")
    
    # Demonstrate transactional behavior
    ExpensiveItem := game_item{
        Name := "Golden Crown"
        Rarity := item_rarity.epic
        Stats := item_stats{Value := 2000, Weight := 90.0}  # Very heavy!
    }
    
    # This might fail due to weight or insufficient gold
    if (Hero.Inventory.PurchaseItem[ExpensiveItem]):
        Print("Purchase successful!")
    else:
        Print("Purchase failed - gold remains at {Hero.Inventory.Gold}")

    # Use higher-order functions with nested function predicate
    IsRareOrLegendary(I:game_item)<decides>:void =
        I.Rarity = item_rarity.rare or I.Rarity = item_rarity.legendary

    RareItems := Hero.Inventory.FilterItems(IsRareOrLegendary)

    Print("Found {RareItems.Length} rare items")
```

<!--

The above has some superfluous <transacts> due to <no_rollback>, in some cases they could be just <computes>.  Apparently an Old VM pathology

Also methods that have an empty return type have weird behavior in some cases. Easily fixed by typing them.
-->

这个示例在实用场景中展示了 Verse。让我们探索一下是什么让这段代码独具 Verse 特色：

**类型系统和数据建模**

示例以 Verse 丰富的类型系统开始。类型自然地贯穿代码；许多类型标注都可以省略，因为它们可以通过推断得出。当我们确实指定类型时，比如 `Items:[]game_item`，它们更多是为了记录意图，而不仅仅是满足编译器。`item_rarity` 枚举提供了类型安全的常量，无需传统枚举的样板代码。标记为 `<persistable>` 的 `item_stats` 结构体可以从持久化存储中保存和加载，这对游戏存档至关重要。`game_item` 类使用 `<unique>` 来确保引用相等语义。

**失败即控制流**

在整个代码中，驱动控制流的是失败，而非异常或错误码。`<decides>` 效果标记了可能失败的函数，失败会在表达式中自然传播。当 `GetRarityMultiplier()` 遇到未知稀有度时，它不会抛出异常或返回一个哨兵值——它只是简单地失败，调用代码会优雅地处理这种情况。

`AddItem` 方法展示了失败如何创建优雅的验证。表达式 `NewWeight <= MaxWeight` 要么成功（允许继续执行），要么失败（阻止添加物品）。没有显式的控制流——只有一个声明式的断言，表明必须满足的条件。

**事务语义和推测执行**

标记为 `<transacts>` 的方法在失败时提供自动回滚。在 `PurchaseItem` 中，我们从玩家身上扣除金币，然后尝试添加物品。如果添加失败（可能由于重量限制），金币扣除会自动回滚。这消除了与部分状态更新相关的整类错误。

这种事务行为扩展到复杂操作。当多个更改需要同时成功或同时失败时，Verse 确保一致性，无需手动清理。

**函数作为一等值**

`FilterItems` 方法接受一个谓词函数，展示了高阶编程。`RunExample` 中的嵌套函数 `IsRareOrLegendary` 展示了函数如何像其他值一样被本地定义和传递。这种函数式编程风格与命令式和面向对象特性自然地结合在一起。

**可选类型和查询运算符**

库存移除逻辑使用可选类型（`?game_item`）来表示可能不存在的值。查询运算符 `?` 从选项中提取值，如果选项为空则失败。这消除了空指针异常，同时为处理空值提供了便捷的语法。

**模式匹配和控制流**

`GetRarityMultiplier` 中的 `case` 表达式展示了模式匹配。与 switch 语句不同，`case` 是一个产生值的表达式。下划线 `_` 提供了一个兜底模式，不过在这个示例中它会导致失败。

`if` 表达式同样会产生值，并且可以在其条件中绑定变量。复合条件展示了多个操作如何通过自动失败传播进行链式调用。

**模块系统和访问控制**

代码以 `using` 语句开始，从其他模块导入功能。基于路径的模块系统确保依赖关系明确且可永久定位。像 `<public>` 这样的访问说明符在细粒度上控制可见性。

**默认不可变**

数据结构默认是不可变的，除非显式地用 `var` 标记。这消除了整类错误，并使并发编程更加安全。当我们需要修改时，它是显式的，并且由效果系统进行追踪。有关 `var` 和 `set` 的完整细节，请参见[可变性](05_mutability.md)。

## 命名约定

Verse 有一套命名约定，使代码可读且可预测。虽然语言不强制执行这些约定，但遵循它们可以确保你的代码与更广泛的 Verse 生态系统良好集成，并且对其他 Verse 开发者来说一目了然。

标识符应使用 PascalCase（首字母大写的驼峰式命名）：

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
# Variables and constants use PascalCase
PlayerHealth:int = 100
MaxInventorySize:int = 50
IsGameActive:logic = true

# Functions use PascalCase
CalculateDamage(Base:float, Multiplier:float):float =
    Base * Multiplier

GetPlayerName(Id:int)<decides>:string =
    PlayerDatabase[Id].Name

# Classes and structs use snake_case
player_character := class:
    Name:string
    Level:int

inventory_item := struct:
    ItemId:int
    Quantity:int

# Enums and their values use snake_case
game_state := enum:
    main_menu
    in_game
    paused
    game_over
```

泛型类型参数使用单个小写字母或简短描述性名称：

<!--versetest-->
<!-- 10 -->
```verse
# Single letter for simple generics
Find(Array:[]t, Target:t where t:type):?int = false

# Descriptive names for complex relationships
Transform(Input:in_t, Processor:type{_(:in_t):out_t} where in_t:type, out_t:type):?out_t = false
```

模块名称始终使用 PascalCase，包括路径段：

<!--NoCompile-->
<!-- 11 -->
```verse
# Module definition
InventorySystem := module:
    # Module contents

# Path segments also use PascalCase
using { /Fortnite.com/Characters/PlayerController }
using { /MyGame.com/Systems/CombatSystem }
using { /Verse.org/Random }
```

类和结构体字段使用 PascalCase，方法遵循与函数相同的 PascalCase 约定：

<!--versetest-->
<!-- 12 -->
```verse
player := class:
    Name:string          # PascalCase for fields
    var Health:float= 0.0

    # Methods use PascalCase like functions
    TakeDamage(Amount:float):void =
        set Health = Max(0.0, Health - Amount)

    IsAlive():logic =
        logic{Health > 0.0}
```

## 代码格式

Verse 代码遵循一致的格式化模式，以强调可读性。

使用四个空格缩进代码块。冒号引入一个块，后续行缩进：

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

复杂表达式受益于能展示结构的清晰格式化：

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

# Multi-line conditionals
Result := if (Player.Health > 50):
    "healthy"
else if (Player.Health > 20):
    "injured"
else:
    "critical"

# Chained operations with clear precedence
FinalDamage :=
    BaseDamage *
    LevelMultiplier *
    (1.0 + BonusPercentage / 100.0)

# Pattern matching with aligned cases
DamageMultiplier := case(Rarity):
    rarity_type.common => 1.0
    rarity_type.uncommon => 1.5
    rarity_type.rare => 2.0
    rarity_type.epic => 3.0
    rarity_type.legendary => 5.0
```

函数遵循一致的模式，明确指定效果和返回类型：

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
# Simple pure function
Add(X:int, Y:int)<computes>:int = X + Y

# Function with effects
ProcessTransaction(Amount:int)<transacts><decides>:void =
    ValidateAmount[Amount]
    DeductBalance(Amount)
    RecordTransaction()

# Multi-line function with clear structure
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

## 注释

注释在执行时被忽略，但对于理解和维护代码非常有价值。Verse 提供了几种注释风格，以满足不同的文档需求。最简单的是单行注释，它以 `#` 开头，一直延伸到行尾：

<!--versetest-->
<!-- 16 -->
```verse
CalculateDamage := 100 * 1.5  # Apply critical hit multiplier
```

当需要在不打断代码的情况下，在一行代码中记录某些内容时，行内块注释提供了完美的解决方案。它们用 `<#` 和 `#>` 括起来：

<!--versetest
BaseValue:int = 100
Multiplier:int = 2
Bonus:int = 10
-->
<!-- 17 -->
```verse
Result := BaseValue <# original amount #> * Multiplier <# scaling factor #> + Bonus
```

同样的语法也可用于编写多行块注释，非常适合解释复杂算法或提供详细上下文：

<!--versetest-->
<!-- 18 -->
```verse
<# This function implements the quadratic damage falloff formula
   used throughout the game. The falloff ensures that damage
   decreases smoothly with distance, creating strategic positioning
   choices for players. #>
CalculateFalloffDamage(Distance:float, MaxDamage:float):float =
    MaxDamage  # Implementation here
```

块注释可以嵌套，这使你可以在不删除或修改现有文档的情况下，暂时禁用已经包含注释的代码：

<!--versetest-->
<!-- 19 -->
```verse
<# Temporarily disabled for testing
   OriginalFunction()  <# This had a bug #>
   NewFunction()       # Testing this approach
#>
```

缩进注释以单独一行的 `<#>` 开头；后续行中缩进四个空格的内容将成为注释的一部分：

<!--versetest
DoSomething():void = {}
-->
<!-- 20 -->
```verse
<#>
    This entire block is a comment because it's indented.
    It provides a clean way to write longer documentation
    without cluttering each line with comment markers.

DoSomething()  # Not part of the comment.
```

## 语法风格

Verse 提供灵活的语法以适应不同的编程风格。相同的逻辑可以使用大括号、缩进或内联形式来表达，让你可以为每种上下文选择最清晰的表示方式。

大括号风格使用花括号来界定代码块，C 系列语言的使用者会很熟悉：

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

缩进风格使用冒号和缩进来定义结构，类似于 Python：

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

对于简单表达式，内联风格将所有内容保持在一行：

<!--versetest
Score:int = 85
-->
<!-- 23 -->
```verse
Result := if (Score > 90) then "excellent" else if (Score > 70) then "good" else "needs improvement"
```

点号风格使用句点来引入表达式：

<!--versetest
Score:int = 85
-->
<!-- 24 -->
```verse
Result := if (Score > 90). "excellent" else if (Score > 70). "good" else. "needs improvement"
```

你甚至可以在有意义时混合使用风格：

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

所有这些形式产生相同的结果。选择哪种取决于可读性和上下文。
当与已有的以大括号为主的代码一起工作时使用大括号，缩进更适合清晰的垂直布局，
内联形式适合简单表达式。这种灵活性让你可以编写读起来自然的代码。
