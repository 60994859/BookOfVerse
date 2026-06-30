# 失败

大多数编程语言将控制流视为真或假、是或否、一或零的问题。它们评估布尔条件并根据结果进行分支，创建了一个二元决策的世界，这通常需要两次检查条件——一次是查看某事是否可能，另一次是实际执行它。Verse 采取了不同的方法。它不问"这是真的吗？"，而是问"这会成功吗？"

这个区别看似微妙，但它改变了程序的编写和推理方式。失败不是错误或异常——它是驱动控制流的一等概念。当一个表达式失败时，它不会使程序崩溃或抛出需要捕获的异常。相反，失败是一种正常、预期的结果，你的代码通过语言本身的结构优雅地处理它。

考虑访问数组元素这一简单操作。在传统语言中，你可能会这样写：

<!--NoCompile-->
<!-- 01 -->
```verse
if (Index < Array.Length) {  # Traditional, non-Verse
    Value = Array[Index]
    Process(Value)
}
```

这将有效性检查与访问分离开来，如果检查与访问之间出现分离，或者数组在两者之间发生变化，就会产生错误的机会。在 Verse 中，验证和访问是统一的：

<!--versetest
Array:[]int = array{1,2,3}
Index:int = 1
Process(V:int):void = {}
-->
<!-- 02 -->
```verse
if (Value := Array[Index]):
    Process(Value)
```

数组访问要么成功并绑定该值，要么失败并继续执行。没有单独的验证步骤，因此检查与访问不会变得不一致，也不会因访问无效索引而产生未定义行为。

## 可失败表达式

可失败表达式是可以成功并产生一个值，或者失败而不产生任何值的表达式。这与返回 null 或错误代码不同——当一个表达式失败时，它根本不产生任何值。计算在该执行路径上的这一点停止。

许多操作天然是可失败的。数组索引在索引越界时失败。映射查找在键不存在时失败。比较在值不相等时失败。除零时除法失败。甚至简单的字面量也可以被设为失败：

<!--versetest
M()<decides>:void =
    42
    false?
    true?
<#
-->
<!-- 03 -->
```verse
42      # Always succeeds with value 42
false?  # Always fails - the query of false
true?   # Always succeeds - the query of true
```
<!-- #> -->

查询操作符 `?` 将任何值转换为可失败表达式。当应用于 `false` 时，它总是失败。当应用于任何其他值时，它成功并返回该值。这个简单的机制为控制程序流提供了巨大的能力。

你可以通过标记为 `<decides>` 效果的函数创建自己的可失败表达式：

<!--versetest-->
<!-- 04 -->
```verse
ValidateAge(Age:int)<decides>:int =
    Age >= 0    # Fails if age is negative
    Age <= 150  # Fails if age is unrealistic
    Age         # Returns the age if both checks pass
```
<!-- ValidateAge[10] -->

这个函数不仅仅是检查条件——它体现了条件本身。如果年龄无效，函数失败。如果有效，它成功并返回年龄值。验证和值是不可分割的。

## 失败上下文

并非程序的每个部分都能执行可失败表达式。它们只能出现在失败上下文中——即语言知道如何处理成功和失败的地方。每个失败上下文定义了当其内部的表达式失败时会发生什么。

最常见的失败上下文是 `if` 表达式的条件：

<!--versetest
Name:string="Joe"
GetPlayerByName(B:string)<decides><transacts>:int = 0
GetPlayerScore(B:int)<transacts><decides>:int = 0
-->
<!-- 05 -->
```verse
if (Player := GetPlayerByName[Name], Score := GetPlayerScore[Player], Score > 100):
    Print("High scorer: {Name} with {Score} points!")
```

这个 `if` 条件包含三个潜在的可失败表达式。所有表达式都必须成功，主体才能执行。如果任何一个失败，整个条件就会失败，控制流将转到 `else` 分支（如果存在）或完全跳过 `if`。精妙之处在于每个表达式都可以使用前一个表达式的结果——`Score` 只有在我们成功找到 `Player` 后才计算。

`for` 表达式为域子句的每次迭代创建一个失败上下文：

<!--versetest
Inventory:[]int= array{1}
IsWeapon:[]int= array{1}
GetDamage(:int)<computes><decides>:int=1
-->
<!-- 06 -->
```verse
for (Item : Inventory, IsWeapon[Item], Damage := GetDamage[Item], Damage > 50):
    Print("Powerful weapon: {Item} with {Damage} damage")
```

每次迭代都会尝试可失败表达式。如果它们全部成功，则针对该物品执行主体。如果任何一个失败，则跳过该次迭代，循环继续处理下一个物品。这创建了一种自然的过滤机制，无需显式的条件逻辑。

!!! note "未发布的功能"
    `first` 尚未发布。以下记录了尚不可用的计划功能。

与 `for` 类似，`first` 表达式为域子句创建一个失败上下文：
<!--versetest
Inventory:[]int= array{1}
IsWeapon:[]int= array{1}
GetDamage(:int)<computes><decides>:int=1
-->
<!-- 100 -->
```verse
PowerfulWeapon := option. first(Item : Inventory, IsWeapon[Item], Damage := GetDamage[Item], Damage > 50). Item
```
与 `for` 不同，如果没有成功的迭代，`first` 本身将失败，因此必须用在失败上下文中。在上面的示例中，`option` 用于处理 `first` 的失败。

标记为 `<decides>` 的函数为其整个主体创建一个失败上下文：

<!--versetest
item:=struct{}
IsWeapon(i:item)<computes><decides>:void={}
GetDamage(i:item)<computes><decides>:int=0
-->
<!-- 07 -->
```verse
FindBestWeapon(Inventory:[]item)<decides>:item =
    var BestWeapon:?item = false
    var MaxDamage:int = 0

    for (Item : Inventory, IsWeapon[Item], Damage := GetDamage[Item]):
        if (Damage > MaxDamage):
            set BestWeapon = option{Item}
            set MaxDamage = Damage

    BestWeapon?  # Fails if no weapon was found
```

函数体是一个失败上下文，允许在整个函数中使用可失败表达式。最后一行从可选类型中提取值，如果未找到武器则失败。

## 推测执行

当你在失败上下文中执行代码时，对可变变量的更改是临时的——只有当整个上下文成功时它们才会成为永久性的。在失败上下文中修改状态的函数必须使用 `<transacts>` 或 `<writes>` 效果说明符（参见[效果](13_effects.md)）：

<!--NoCompile-->
<!-- 08 -->
```verse
m:=module:
    buyer := class:
        var PlayerGold:int
        AttemptPurchase(Cost:int)<transacts><decides>:void =
           set PlayerGold = PlayerGold - Cost  # Provisional change
           PlayerGold >= 0                     # Check if still valid
           # If this fails, PlayerGold reverts to original value
```

如果检查失败，减法会自动回滚。你无需在修改状态前手动恢复原始值或检查条件。

这种事务性行为使得复杂的状态更新既安全又可预测。要么所有操作成功且所有更改被提交，要么某个操作失败且没有任何变化。

<!--versetest
game_state := struct{}
game := class:
    var State:game_state = game_state{}
    ModifyHealth()<transacts>:void = {}
    UpdateInventory()<transacts>:void = {}
    ChargeResources()<transacts>:void = {}
    ValidateFinalState()<transacts><decides>:void = {}
    ComplexOperation()<transacts><decides>:void =
       ModifyHealth()
       UpdateInventory()
       ChargeResources()
       ValidateFinalState[]
<#
-->
<!-- 09 -->
```verse
game := class:
    var State:game_state
    ComplexOperation()<transacts><decides>:void =
       ModifyHealth()       # All these operations
       UpdateInventory()    # are provisional
       ChargeResources()    # until all succeed
       ValidateFinalState[] # If this fails, everything rolls back
```
<!-- #> -->

`game` 类有多个更新 `game_state` 的方法，在返回之前，`ComplexOperation` 会验证对象是否处于有效状态，如果不是，则方法中执行的所有更改都会被回滚。

## 失败的逻辑

Verse 提供了与失败一起工作的逻辑操作符，创建了一种组合可失败表达式的代数。

`and` 操作符确保两个表达式都成功。
`not` 操作符反转成功和失败：

<!--versetest
Score:int=10
GetNearestEnemy()<decides><computes>:int=0
-->
<!-- 10 -->
```verse
if (not (Enemy := GetNearestEnemy[]) and Score > 0):
    Print("Coast is clear!")  # Executes when GetNearestEnemy fails
```

值得注意的是，`Enemy` 在 `then` 分支中不在作用域内，因为它位于 `not` 之下。

`or` 操作符提供替代方案：

<!--versetest
DefaultWeapon:?string=false
PrimaryWeapon()<decides><computes>:string="primary"
SecondaryWeapon()<decides><computes>:string="sword"
-->
<!-- 11 -->
```verse
Weapon := PrimaryWeapon[] or SecondaryWeapon[] or DefaultWeapon?
```

这会按顺序尝试每个选项，在第一个成功处停止。它不是评估布尔条件——它是在尝试计算，并取第一个成功的计算。

你可以组合这些操作符来创建复杂的控制流：

<!--versetest
player := struct{}
IsAlive(P:player)<computes><decides>:void = {}
IsStunned(P:player)<computes><decides>:void = {}
HasAmmunition(P:player)<computes><decides>:void = {}
HasMeleeWeapon(P:player)<computes><decides>:void = {}
-->
<!-- 12 -->
```verse
ValidatePlayer(Player:player)<decides>:void =
    IsAlive[Player]
    not IsStunned[Player]
    HasAmmunition[Player] or HasMeleeWeapon[Player]
```

这个函数仅在玩家存活、未被眩晕、并且拥有弹药或近战武器时成功。每一行都是一个必须成功的独立可失败表达式。

另一个有趣的用例是 `not not Exp`——如果 `Exp` 成功，它成功，但 `Exp` 的所有效果都被丢弃。这是一种尝试查看复杂操作是否会成功的方法。

## 决定上下文中的表达式

一个微妙的特性是关系表达式在决定上下文中如何表现。当比较出现在可以处理失败的上下文中时，它不仅测试条件——它还产生一个值，具体来说是返回其左侧操作数。所以 `X>0` 返回 `X`，`0<=X` 返回 `0`。此行为适用于决定上下文中的所有比较操作符：

<!--versetest-->
<!-- 14 -->
```verse
GetIfNotEqual(X:int, Y:int)<decides>:int =
    X <> Y  # Returns X when X ≠ Y, fails when X = Y

GetIfLessOrEqual(X:int, Limit:int)<decides>:int =
    X <= Limit  # Returns X when X ≤ Limit, fails otherwise

GetIfGreaterThan(X:int, Threshold:int)<decides>:int =
    X > Threshold  # Returns X when X > Threshold, fails otherwise
```
<!--
GetIfNotEqual[1,2]
GetIfGreaterThan[11,2]
GetIfLessOrEqual[1,2]
-->

形式为 `A op B` 的比较表达式在比较成功时返回 `A`，在比较为假时失败。

这创建了简洁的验证函数，要么返回 `Value`，要么失败：

<!--versetest-->
<!-- 16 -->
```verse
ValidateInRange(Value:int, LwrBnd:int, UprBnd:int)<decides>:int =
    Value >= LwrBnd and Value <= UprBnd
```
<!-- ValidateInRange[5,0,10] -->

## 可选类型

可选类型和失败紧密相连。可选类型要么包含一个值，要么为空（由 `false` 表示）。查询操作符 `?` 在可选类型和失败之间进行转换：

<!--versetest-->
<!-- 18 -->
```verse
M()<decides>:void=
    MaybeValue:?int = option{42}  # An optional int
    Value := MaybeValue?          # Succeeds with 42

    Empty:?int = false            # An empty value
    Other := Empty?               # Failure
```

`option{}` 构造器以相反的方式工作，将失败转换为空可选类型：

<!--versetest
RiskyComputation()<computes><decides>:int=1
-->
<!-- 19 -->
```verse
Result := option{RiskyComputation[]} # option{value} if computation succeeds
                                     # otherwise false
```
<!-- Result -->

这种双向转换使得可选类型和失败可以互换，让你可以为特定用例选择最合适的表示形式。

可选类型 `?T` 表示可能存在也可能不存在的值。问号出现在类型*之前*，而不是之后：

<!--versetest-->
<!-- 20 -->
```verse
ValidSyntax:?int = option{42}      # Correct
```
<!-- ValidSyntax? -->

`?` 前缀适用于任何类型：

<!--versetest
player := struct{}
-->
<!-- 21 -->
```verse
MaybeNumber:?int = option{42}
MaybeText:?string = option{"hello"}
MaybePlayer:?player = option{player{}}
```

使用 `option{}` 构造器来包装一个值：

<!--versetest
RiskyComputation()<computes><decides>:int=1
-->
<!-- 22 -->
```verse
Filled:?int = option{42}
Empty:?int  = false
Result:?int = option{RiskyComputation[]}  # false if computation fails
```

空可选类型和 `false` 是等价的——空可选类型*就是* `false`：

<!--versetest-->
<!-- 23 -->
```verse
EmptyOption:?int = false
EmptyOption = false  # This comparison succeeds
```

Verse 拥有丰富且灵活的语法，但有时也可能导致细微的错误。在 `option` 中使用逗号会生成元组，而使用分号会计算所有值但只保留最后一个：

<!--versetest-->
<!-- 24 -->
```verse
# Comma creates tuple
option{1, 2}? = (1, 2)

# Semicolon creates sequence - last value is used
option{1; 2}? = 2
```

### 解包

查询操作符 `?` 从可选类型中提取值，如果可选类型为空则失败：

<!--versetest-->
<!-- 25 -->
```verse
M()<decides>:void=
    MaybeValue:?int = option{42}
    Value := MaybeValue?  # Succeeds with 42

    Empty:?int = false
    Other := Empty?  # Fails - cannot unwrap empty option
```

解包只允许在失败上下文中进行：

<!--versetest
MaybeInt:?int = option{42}
UseItem(I:int):void={}
ProcessItem(I:int)<computes>:?int=option{3}
Items:[]int = array{1,2,3}
-->
<!-- 26 -->
```verse
# Valid: In if condition (failure context)
if (Value := MaybeInt?):
    Print("Got {Value}")

# Valid: In for loop (failure context)
for (Item : Items, ValidItem := ProcessItem(Item)?):
    UseItem(Item)

# Valid: In <decides> function body (failure context)
GetRequired(Maybe:?int)<decides>:int =
    Maybe?  # Fails if Maybe is empty
```

### 嵌套

可选类型可以嵌套以表示多层缺失：

<!--versetest-->
<!-- 27 -->
```verse
# Double-nested option
Double:??int = option{option{42}}

# Single unwrap gets outer option
if (Inner := Double?):
    if (TheValue := Inner?):
        # TheValue has type int, equals 42

# Double unwrap gets the value directly
Value := Double??  # Fails if either layer is empty
```

辅助函数也可以处理嵌套可选类型：

<!--versetest-->
<!-- 28 -->
```verse
UnpackNested(MaybeValue:??int):?int =
    if (Inner := MaybeValue?):
        Inner
    else:
        option{-1}  # Default for outer empty

DirectUnpack(MaybeValue:??int):int =
    if (Value := MaybeValue??):
        Value
    else:
        -1  # Default for any level empty
```
<!--
UnpackNested(option{option{1}})
DirectUnpack(option{option{2}})
-->

### 链式访问

`?.` 操作符提供对可选类型值的安全成员访问：

<!--NoCompile-->
<!-- 29 -->
```verse
entity := class:
    Name:string = "Unknown"
    Health:int = 100

MaybeEntity:?entity = option{entity{}}

# Safe field access
if (Name := MaybeEntity?.Name):
    Print("Entity: {Name}")  # Succeeds

# Safe method call
MaybeEntity?.TakeDamage(10)  # Only calls if entity present

# Chaining through multiple optionals
linked_list := class:
    Value:int = 0
    Next:?linked_list = false

Head:?linked_list = option{linked_list{Value := 1}}
SecondValue := Head?.Next?.Value  # Fails if any link is empty
```

`?.` 操作符会短路——如果可选类型为空，整个表达式失败，而不评估成员访问。

### 默认值

使用 `or` 操作符为空可选类型提供后备值：

<!--versetest-->
<!-- 30 -->
```verse
MaybeValue:?int = false
Value := MaybeValue? or 42  # Yields 42

# Chaining multiple options
Primary:?string = false
Secondary:?string = option{"backup"}
Default:string = "default"

Result := Primary? or Secondary? or Default
```
### 比较

空可选类型等于 `false`，而填充的可选类型在正确比较时等于其解包后的值：

<!--versetest-->
<!-- 40 -->
```verse
EmptyOption:?int = false
EmptyOption = false  # Succeeds

FilledOption:?int = option{1}
FilledOption? = 1  # Succeeds - unwrap then compare
```

但是，你不能在不解包的情况下直接比较可选类型和非可选类型的值：

<!--versetest-->
<!-- 41 -->
```verse
Opt:?int = option{42}
Regular:int = 42

# Must unwrap to compare
if (Opt? = Regular):
    Print("Equal")
```

## 可选类型与失败

将决定函数与可选返回类型结合使用，创建了一个具有多层失败的系统。这种模式使得在保持清晰性的同时，可以简洁地表达复杂条件。

一个函数可以在两个层次上失败：

- *函数级失败*：整个函数使用 `<decides>` 失败
- *值级失败*：函数成功但返回空可选类型

<!--versetest
player := string
IsActive(S:string)<transacts><decides>:string=""
LookupPlayer(S:string)<transacts><decides>:string="player"
-->
<!-- 42 -->
```verse
FindEligiblePlayer(Name:string)<decides>:?player =
    Name <> ""           # Layer 1: Fail if name is empty
    Player := LookupPlayer[Name]  # Layer 1: Fail if player not found
    option{IsActive[Player]}      # Layer 2: Empty option if player inactive
```
<!-- FindEligiblePlayer["Someone"] -->

这个函数有三种可能的输出：

- *函数失败*：名称为空或未找到玩家
- *函数成功但返回空可选类型*：找到玩家但不活跃
- *函数成功并返回填充的可选类型*：找到玩家且活跃

调用这个函数展示了分层的失败：

<!--versetest
FindEligiblePlayer(S:string)<transacts><decides>:?string=option{S}
-->
<!-- 43 -->
```verse
# Function-level failure
Result1 := FindEligiblePlayer[""]  # Fails, Result1 never assigned

# Function succeeds, returns empty option
if (Player := FindEligiblePlayer["InactiveUser"]?):
    # Won't execute - function succeeds but ? query fails
else:
    # Executes here

# Function succeeds, returns filled option
if (Player := FindEligiblePlayer["ActiveUser"]?):
    # Executes with Player bound to the active player
```

这种模式对于具有不同失败模式的验证特别有用：

<!--versetest-->
<!-- 44 -->
```verse
ValidateScore(Score:int)<decides>:?int =
    Score >= 0           # Layer 1: Reject negative scores (invalid input)
    option{Score <= 100} # Layer 2: Reject high scores (out of range)
```

函数级失败和值级失败之间的区别让你可以表达不同类型的错误。函数级失败通常意味着"此操作无法完成"，而值级失败意味着"操作已完成，但结果不符合预期标准"。

## 转换作为决定

Verse 中的类型转换已集成到失败系统中。动态转换的行为就像 `<decides>` 函数调用一样，同样使用方括号语法。例如，`Type[value]` 尝试将 `value` 的类型转换为 `Type`，如果不成功则失败。

这也适用于必须指定 `<castable>` 的用户定义类型：

<!--versetest
component := class<castable>:
    Name:string = "Component"

physics_component := class<castable>(component):
    Velocity:float = 0.0

TryGetPhysics(Comp:component)<decides>:physics_component =
    physics_component[Comp]
<#
-->
<!-- 48 -->
```verse
component := class<castable>:
    Name:string = "Component"

physics_component := class<castable>(component):
    Velocity:float = 0.0

# Casting as a decides operation
TryGetPhysics(Comp:component)<decides>:physics_component =
    physics_component[Comp]  # Succeeds if Comp is actually a physics_component
```
<!-- #> -->

这使得基于类型的分发易于表达：

<!--versetest
component := class<castable>:
    Name:string = "Component"
physics_component := class<castable>(component):
    Velocity:float = 0.0
render_component := class<castable>(component):
    Renderer:string = "RayTrace"
UpdatePhysics(P:physics_component):void={}
UpdateRendering(R:render_component):void={}
UpdateGeneric(G:component):void={}
-->
<!-- 49 -->
```verse
ProcessComponent(Comp:component):void =
    if (Physics := physics_component[Comp]):
        UpdatePhysics(Physics)
    else if (Render := render_component[Comp]):
        UpdateRendering(Render)
    else:
        # Unknown component type
        UpdateGeneric(Comp)
```
<!-- ProcessComponent(component{}) -->

转换本身就是条件——无需单独的类型检查。当转换成功时，你既确认了类型，又获得了正确类型的引用。

你可以将转换与其他决定操作链接起来：

<!--versetest
component := class<castable>:
    Name:string = "Component"
physics_component := class<castable>(component):
    Velocity:float = 0.0
render_component := class<castable>(component):
    Renderer:string = "RayTrace"
UpdatePhysics(P:physics_component):void=return
UpdateRendering(R:render_component):void=return
UpdateGeneric(G:component):void=return
entity := class:
    GetComponent()<transacts><decides>:component=
        component{}
IsActive(c:component)<transacts><decides>:logic=true
-->
<!-- 50 -->
```verse
GetActivePhysicsComponent(Entity:entity)<decides>:physics_component =
    Comp := Entity.GetComponent[]  # Fails if no component
    Physics := physics_component[Comp]  # Fails if not physics
    IsActive[Physics]  # Fails if inactive
    Physics
```

每一步都必须成功，函数才能返回值。这创建了自我文档化的验证链，其中类型要求是显式的。

转换可以与 `or` 组合器一起用于后备类型：

<!--versetest
component := class<castable>:
    Name:string = "Component"
physics_component := class<castable>(component):
    Velocity:float = 0.0
trigger_component := class<castable>(component):
    Trigger:float = 0.0
scripted_component := class<castable>(component):
    Scripted:string = "Something"
UpdatePhysics(P:physics_component):void=return
UpdateGeneric(G:component):void=return
entity := class:
    GetComponent()<transacts><decides>:component=
        component{}
IsActive(c:component)<transacts><decides>:logic=true
GetInteractable(Entity:entity)<decides><transacts>:component =
    physics_component[Entity] or
    trigger_component[Entity] or
    scripted_component[Entity]
<#
-->
<!-- 51 -->
```verse
GetInteractable(Entity:entity)<decides>:component =
    physics_component[Entity] or
    trigger_component[Entity] or
    scripted_component[Entity]
```
<!--
#>
GetInteractable[entity{}]
-->

这会按顺序尝试每个转换，返回第一个成功的转换。它是类型安全的，因为所有选项都共享共同的 `component` 基类型。

## 惯用用法和模式

当你使用失败时，会出现某些模式，它们能优雅地解决常见问题。

验证链模式使用顺序失败来确保满足所有条件：

<!--versetest
action := struct{}
player := struct{}
location := struct{}
GetActingPlayer(A:action)<transacts><decides>:player = player{}
IsValidTurn(P:player)<computes><decides>:void = {}
HasRequiredResources(P:player, A:action)<computes><decides>:void = {}
GetTargetLocation(A:action)<transacts><decides>:location = location{}
IsValidLocation(L:location)<computes><decides>:void = {}
ExecuteAction(A:action)<transacts><decides>:void = {}
-->
<!-- 62 -->
```verse
ProcessAction(Action:action)<decides>:void =
    Player := GetActingPlayer[Action]
    IsValidTurn[Player]
    HasRequiredResources[Player, Action]
    Location := GetTargetLocation[Action]
    IsValidLocation[Location]
    ExecuteAction[Action]
```

每一行都必须成功，执行才能继续。这创建了自我文档化的代码，其中前置条件被显式地按顺序检查。

首次成功模式尝试替代方案直到一个有效：

<!--versetest
location := struct{}
path := struct{}
DirectPath(S:location, E:location)<transacts><decides>:path = path{}
PathAroundObstacles(S:location, E:location)<transacts><decides>:path = path{}
ComplexPathfinding(S:location, E:location)<transacts><decides>:path = path{}
-->
<!-- 63 -->
```verse
FindPath(Start:location, End:location)<decides>:path =
    DirectPath[Start, End] or
    PathAroundObstacles[Start, End] or
    ComplexPathfinding[Start, End]
```

这自然地表达了先尝试简单解决方案再尝试复杂解决方案的思路。

过滤模式使用失败来选择项目：

<!--versetest
enemy := struct{}
GetLevel(E:enemy)<computes><decides>:int = 10
-->
<!-- 64 -->
```verse
GetEliteEnemies(Enemies:[]enemy):[]enemy =
    for (Enemy : Enemies, Level := GetLevel[Enemy], Level >= 10):
        Enemy
```

只有那些有等级且等级至少为 10 的敌人才会被包含在结果中。

事务模式将相关更改分组：

<!--versetest
player := class:
    var Inventory:[]item = array{}
item := struct{}
RemoveItem(P:player, I:item)<transacts><decides>:void = {}
AddItem(P:player, I:item)<transacts>:void = {}
ValidateTrade(P1:player, P2:player)<computes><decides>:void = {}
-->
<!-- 65 -->
```verse
TradeItems(PlayerA:player, PlayerB:player, ItemA:item, ItemB:item)<transacts><decides>:void =
    RemoveItem[PlayerA, ItemA]
    RemoveItem[PlayerB, ItemB]
    AddItem(PlayerA, ItemB)
    AddItem(PlayerB, ItemA)
    ValidateTrade[PlayerA, PlayerB]
```

要么整个交易成功，要么没有任何变化。

**可选索引**

当处理可选容器时，你可以使用专门的查询语法来访问其内容，该语法将可选检查与元素访问结合在一起。可选元组支持通过查询操作符直接访问元素：

<!--versetest-->
<!-- 58 -->
```verse
MaybePair:?tuple(int, string) = option{(42, "answer")}

# Access first element
if (FirstValue := MaybePair?(0)):
    # FirstValue is 42 (type: int)
    Print("First: {FirstValue}")

# Access second element
if (SecondValue := MaybePair?(1)):
    # SecondValue is "answer" (type: string)
    Print("Second: {SecondValue}")
```

语法 `Option?(index)` 同时完成以下操作：

- 查询可选类型是否非空
- 访问给定索引处的元组元素
- 如果两者都成功，绑定元素值

**组合与调用链**

决定函数自然地进行组合，允许从简单、可重用的部分构建复杂操作。当一个决定函数调用另一个决定函数时，失败会自动传播。

<!--versetest-->
<!-- 52 -->
```verse
ValidatePositive(X:int)<decides>:int =
    X > 0

Double(X:int)<decides>:int =
    Validated := ValidatePositive[X]  # Fails if X ≤ 0
    Validated * 2
```
<!-- Double[2] -->

如果 `ValidatePositive` 失败，`Double` 立即失败。验证后的值在链中传递。

**保留失败上下文：**

在非决定上下文中调用决定函数时，必须显式处理失败：

<!--versetest
FindPlayer(Name:string)<transacts><decides>:string=Name
GetDefaultPlayer():string="Default"
UsePlayer(P:string):void=return
-->
<!-- 57 -->
```verse
# This won't compile - ProcessPlayer doesn't have <decides>
# BadProcessPlayer(Name:string):void =
#    Player := FindPlayer[Name]  # ERROR: Unhandled failure

# Handle with if
ProcessPlayerWithIf(Name:string):void =
    if (Player := FindPlayer[Name]):
        UsePlayer(Player)

# Handle with or
ProcessPlayerWithOr(Name:string):void =
    Player := FindPlayer[Name] or GetDefaultPlayer()
    UsePlayer(Player)
```
<!--
PlayerOne := "PlayerOne"
ProcessPlayerWithIf(PlayerOne)
ProcessPlayerWithOr(PlayerOne)
-->

理解组合有助于你从简单、可测试的部件构建复杂的验证逻辑。

## 运行时错误

失败（`<decides>`）代表具有事务回滚的正常控制流，而*运行时错误*代表终止执行的不可恢复条件。运行时错误沿调用栈向上传播，绕过正常的失败处理，并且在 Verse 代码中无法捕获或恢复。

`Err()` 函数显式触发运行时错误，并附带可选消息：

<!--versetest-->
<!-- 66 -->
```verse
ValidateInput(Value:int):int =
    if (Value < 0):
        Err("Negative values not allowed")
    Value
```

当发生运行时错误时，执行沿调用栈展开，终止当前操作：

<!--versetest
Log(Message:string)<transacts>:void = {}
-->
<!-- 68 -->
```verse
DeepFunction()<transacts>:int =
    Log("C")
    Err("Fatal error")  # Runtime error here
    Log("D")            # Never executes
    return 1

MiddleFunction():int =
    Log("B")
    Result := DeepFunction()  # Error propagates through here
    Log("E")                  # Never executes
    return Result

TopFunction():void =
    Log("A")
    Value := MiddleFunction()  # Error propagates to here
    Log("F")                   # Never executes

# Execution order: A, B, C, then terminates
# Output: "ABC"
```

运行时错误立即传播，绕过调用链中所有后续代码。

运行时错误通过异步操作传播，终止生成的任务：

<!--versetest
Log(Message:string)<transacts>:void = {}
WaitTicks(Count:int)<suspends>:void = {}
-->
<!-- 69 -->
```verse
AsyncOperation()<suspends>:int =
    Log("Start")
    WaitTicks(1)
    Err("Async error")  # Runtime error during async execution
    WaitTicks(1)        # Never executes
    return 1

KickOff()<suspends>:void=
    # Error propagates out of spawned task
    spawn{ AsyncOperation() }

```

当生成的任务遇到运行时错误时，该特定任务终止。运行时错误不会自动传播到生成上下文。

## 与失败共存

Verse 对失败的处理方式源于逻辑编程，在逻辑编程中，计算是寻找解决方案而非执行步骤。当一条路径失败时，计算会回溯并尝试替代方案。这种非确定性模型虽然强大，但在其完全通用性下可能难以推理。Verse 通过使失败上下文显式化并将回溯限制在特定构造上来驯服这种力量。你获得了逻辑编程的好处——声明式代码、自动搜索、优雅地处理替代方案——而没有完全统一化和无界回溯的复杂性。

考虑一个简单的逻辑谜题求解器：

<!--versetest
constraint := struct{}
solution := struct{}
InitialState()<transacts>:solution = solution{}
ApplyConstraint(S:solution, C:constraint)<transacts>:void = {}
ValidateSolution(S:solution)<computes><decides>:void = {}
-->
<!-- 73 -->
```verse
SolvePuzzle(Constraints:[]constraint)<decides>:solution =
    var State:solution = InitialState()
    for (Constraint : Constraints):
        ApplyConstraint(State, Constraint)
    ValidateSolution[State]
    State
```

如果任何约束无法满足，整个尝试就会失败。在完整的逻辑编程语言中，这可能会触发复杂的回溯。在 Verse 中，失败模型更简单、更可预测，同时仍然足够表达大多数问题。

在 Verse 中有效地使用失败需要转变思维方式。不是思考需要避免的错误条件，而是思考需要满足的成功条件。不是采用防御性编程，在执行前检查一切，而是编写乐观的代码，尝试操作并优雅地处理失败。

这种视角使代码更可读，意图更清晰。当你看到一个标记为 `<decides>` 的函数时，你知道它代表可能没有结果的计算。当你在失败上下文中看到顺序的表达式时，你知道它们代表必须全部满足的条件。当你看到 `or` 操作符时，你知道它代表需要尝试的替代方案。

Verse 中的失败不是需要害怕或避免的东西——它是需要拥抱的工具。它通过消除某些类别的错误使程序更安全。它通过统一验证和操作使代码更清晰。它通过提供自动回滚使复杂操作更简单。最重要的是，它使编写程序的方式与我们思考现实世界中的操作和决策的方式保持一致。

随着你编写更多的 Verse 代码，你会发现失败变得自然而然的。你在表达条件时会自然地使用可失败表达式。你会将函数设计为在前置条件不满足时尽早失败。你会组合失败来创建复杂的控制流，而无需嵌套的条件语句。你会欣赏这种不同的控制流思维方式如何产生比传统方法更健壮、更具表现力的代码。
