# 失败

大多数编程语言将控制流视为真或假的问题
假、是或否、一或零。他们评估布尔条件并
相应地分支，创建一个二元决策的世界，这些决策经常
需要检查条件两次 - 一次看看是否有东西
可能，并再次实际做到这一点。Verse采取不同的方式
方法。 Verse 没有问“这是真的吗？”，而是问“这是真的吗？”
成功了吗？”

这种区别可能看起来很微妙，但它改变了程序的方式
写出并进行推理。失败不是一个错误或一个
例外——它是驱动控制流的一流概念。当
表达式失败，它不会使您的程序崩溃或引发异常
需要抓住它。相反，失败是正常的、预期的
您的代码通过结构优雅地处理的结果
语言本身。

考虑访问数组元素的简单行为。在传统语言中，您可能会这样写：

<!--NoCompile-->
<!-- 01 -->
```verse
if (Index < Array.Length) {  # 传统的、非Verse的
    Value = Array[Index]
    Process(Value)
}
```
这将检查有效性与访问权限分开，从而创造机会
如果检查和访问分离或者数组
他们之间的变化。在 Verse 中，验证和访问是统一的：

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
数组访问要么成功并绑定该值，要么失败并绑定该值
执行继续进行。没有单独的验证步骤，因此
检查和访问不能不一致，也不能出现未定义的情况
访问无效索引的行为。

<a id="failable-expressions"></a>
## 可失败表达式

可失败表达式是指要么成功并产生一个值，要么失败但不产生任何结果的表达式。这与返回 null 或错误代码不同 - 当表达式失败时，它实际上根本不产生任何值。计算在该特定执行路径中的该点停止。

许多操作自然会失败。当索引越界时，数组索引会失败。当键不存在时，映射查找会失败。当值不相等时比较失败。除以零时除法失败。即使是简单的文字也可能会失败：

<!--versetest
M()<decides>:void =
    42
    false?
    true?
<#
-->
<!-- 03 -->
```verse
42      # 总是以 42 值成功
false?  # 总是失败——错误的查询
true?   # 总是成功 - true 的查询
```
<!-- #> -->

查询运算符 `?` 将任何值转换为可失败表达式。当应用于`false`时，总是失败。当应用于任何其他值时，它会以该值成功。这种简单的机制为控制程序流程提供了巨大的力量。

您可以通过标有 `<decides>` 效果的函数创建自己的失败表达式：

<!--versetest-->
<!-- 04 -->
```verse
ValidateAge(Age:int)<decides>:int =
    Age >= 0    # 如果年龄为负数则失败
    Age <= 150  # 如果年龄不切实际则失败
    Age         # 如果两项检查都通过则返回年龄
```
<!-- ValidateAge[10] -->

这个函数不只是检查条件——它体现了它们。如果年龄无效，则该功能失败。如果有效，则成功并显示年龄值。验证和价值是密不可分的。

## 失败上下文

并非程序的每个部分都可以执行可失败表达式。它们只能出现在失败环境中——语言知道如何处理成功和失败的地方。每个失败上下文定义了当其中的表达式失败时会发生什么。

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
此 `if` 条件包含三个可能可失败表达式。一切都必须成功，身体才能执行。如果任何一个失败，则整个条件失败，并且控制将移至 `else` 分支（如果存在）或完全越过 `if`。美妙之处在于每个表达式都可以使用先前表达式的结果 - 仅当我们成功找到 `Player` 时才会计算 `Score`。

`for` 表达式为域子句的每次迭代创建失败上下文：

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
每次迭代都会尝试可失败表达式。如果它们全部成功，则主体会针对该项目执行。如果有任何失败，则跳过该迭代，并继续循环执行下一项。这创建了一种自然的过滤机制，无需明确的条件逻辑。


!!!注意“未发布的功能”
    `first` 尚未发布。以下记录了当前不可用的计划功能。

与 `for` 类似，`first` 表达式为域子句创建失败上下文：
<!--versetest
Inventory:[]int= array{1}
IsWeapon:[]int= array{1}
GetDamage(:int)<computes><decides>:int=1
-->
<!-- 100 -->
```verse
PowerfulWeapon := option. first(Item : Inventory, IsWeapon[Item], Damage := GetDamage[Item], Damage > 50). Item
```
与 `for` 不同，如果没有成功的迭代，`first` 本身将会失败，因此必须在失败上下文中使用。在上面的例子中，`option`用于处理`first`的失败。

标有 `<decides>` 的函数为其整个主体创建失败上下文：

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

    BestWeapon?  # 如果没有找到武器则失败
```
函数体是一个失败上下文，允许整个表达式失败。最后一行从选项中提取值，如果没有找到武器则失败。

<a id="speculative-execution"></a>
## 推测执行

当您在失败上下文中执行代码时，对可变变量的更改是临时的，只有在整个上下文成功时它们才会成为永久性的。在失败上下文中修改状态的函数必须使用 `<transacts>` 或 `<writes>` 效果说明符（请参阅[效果](13_effects.md)）：

<!--NoCompile-->
<!-- 08 -->
```verse
m:=module:
    buyer := class:
        var PlayerGold:int
        AttemptPurchase(Cost:int)<transacts><decides>:void =
           set PlayerGold = PlayerGold - Cost  # 临时变更
           PlayerGold >= 0                     # 检查是否仍然有效
           # 如果失败，PlayerGold将恢复为原始值
```
如果检查失败，减法将自动回滚。你
不需要手动恢复原始值或检查条件
修改状态之前。

这种事务行为使得复杂的状态更新变得安全且
可预测的。要么一切成功，所有改变都被承诺，
或者某事失败并且没有任何改变。

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
       ModifyHealth()       # 所有这些操作
       UpdateInventory()    # 是临时的
       ChargeResources()    # 直到一切成功
       ValidateFinalState[] # 如果失败，一切都会回滚
```
<!-- #> -->

`game` 类有多种更新 `game_state` 的方法，
返回 `ComplexOperation` 之前验证该对象位于
有效状态，如果不是，则该方法中执行的所有更改都是
回滚了。

## 失败的逻辑

Verse 提供了处理失败的逻辑运算符，创建了
用于组合失败表达式的代数。

`and` 运算符确保两个表达式都成功。
`not` 运算符反转成功和失败：

<!--versetest
Score:int=10
GetNearestEnemy()<decides><computes>:int=0
-->
<!-- 10 -->
```verse
if (not (Enemy := GetNearestEnemy[]) and Score > 0):
    Print("Coast is clear!")  # 当 GetNearestEnemy 失败时执行
```
值得注意的是，`Enemy` 不在 `then` 分支的范围内
因为它位于 `not` 下。

`or` 运算符提供替代方案：

<!--versetest
DefaultWeapon:?string=false
PrimaryWeapon()<decides><computes>:string="primary"
SecondaryWeapon()<decides><computes>:string="sword"
-->
<!-- 11 -->
```verse
Weapon := PrimaryWeapon[] or SecondaryWeapon[] or DefaultWeapon?
```
这将按顺序尝试每个选项，并在第一次成功时停止。这是
不评估布尔条件 - 它正在尝试计算并且
采取第一个成功的。

您可以组合这些运算符来创建复杂的控制流：

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
此功能仅在玩家还活着、没有被击晕并且
有弹药或近战武器。每行都是一个单独的
失败但必须成功的表达式。

另一个有趣的用例是 `not not Exp`——如果 `Exp` 则成功
成功，但 `Exp` 的所有效果都被丢弃。这是一种方法
尝试看看复杂的操作是否会成功。

## Decides 中的表达式

一个微妙的特征是关系表达式在决策中的行为方式
上下文。当比较出现在可以处理的上下文中时
失败时，它不只是测试一个条件——它会产生一个值，
具体来说，它返回其左侧。所以 `X>0` 返回 `X` 并且
`0<=X` 返回 `0`。  此行为适用于所有比较运算符
在决定上下文中：

<!--versetest-->
<!-- 14 -->
```verse
GetIfNotEqual(X:int, Y:int)<decides>:int =
    X <> Y  # 当 X ≠ Y 时返回 X，当 X = Y 时返回失败

GetIfLessOrEqual(X:int, Limit:int)<decides>:int =
    X <= Limit  # 当X≤Limit时返回X，否则失败

GetIfGreaterThan(X:int, Threshold:int)<decides>:int =
    X > Threshold  # 当 X > 阈值时返回 X，否则失败
```
<!--
GetIfNotEqual[1,2]
GetIfGreaterThan[11,2]
GetIfLessOrEqual[1,2]
-->

当 `A op B` 形式的比较表达式返回 `A` 时
比较成功，比较失败则失败。

这将创建简洁的验证函数，要么返回 `Value`，要么失败：

<!--versetest-->
<!-- 16 -->
```verse
ValidateInRange(Value:int, LwrBnd:int, UprBnd:int)<decides>:int =
    Value >= LwrBnd and Value <= UprBnd
```
<!-- ValidateInRange[5,0,10] -->

## 选项类型

选项类型和失败密切相关。一个选项
包含值或为空（用 `false` 表示）。查询
运算符 `?` 在选项和失败之间进行转换：

<!--versetest-->
<!-- 18 -->
```verse
M()<decides>:void=
    MaybeValue:?int = option{42}  # 可选的整数
    Value := MaybeValue?          # 成功42

    Empty:?int = false            # 空值
    Other := Empty?               # 失败
```
`option{}` 构造函数反向工作，将失败转换为空选项：

<!--versetest
RiskyComputation()<computes><decides>:int=1
-->
<!-- 19 -->
```verse
Result := option{RiskyComputation[]} # option{value} 如果计算成功
                                     # 否则为假
```
<!-- Result -->

这种双向转换使选择和失败
可互换，让您选择最合适的
代表您的特定用例。

选项类型 `?T` 表示可能存在也可能不存在的值。
问号出现在类型*之前*，而不是之后：

<!--versetest-->
<!-- 20 -->
```verse
ValidSyntax:?int = option{42}      # 正确
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
使用 `option{}` 构造函数来包装一个值：

<!--versetest
RiskyComputation()<computes><decides>:int=1
-->
<!-- 22 -->
```verse
Filled:?int = option{42}
Empty:?int  = false
Result:?int = option{RiskyComputation[]}  # 如果计算失败则返回 false
```
空选项和 `false` 是等效的——空选项*是* `false`：

<!--versetest-->
<!-- 23 -->
```verse
EmptyOption:?int = false
EmptyOption = false  # 这次比较成功
```
Verse 具有丰富而灵活的语法，有时也会导致
微妙的错误。逗号产生 `option` 中的元组，而
分号计算所有值，但仅保留最后一个值：

<!--versetest-->
<!-- 24 -->
```verse
# 逗号创建元组
option{1, 2}? = (1, 2)

# 分号创建序列 - 使用最后一个值
option{1; 2}? = 2
```
### 展开

查询运算符 `?` 从选项中提取值，如果选项为空则失败：

<!--versetest-->
<!-- 25 -->
```verse
M()<decides>:void=
    MaybeValue:?int = option{42}
    Value := MaybeValue?  # 成功42

    Empty:?int = false
    Other := Empty?  # 失败 - 无法解开空选项
```
仅允许在失败上下文中展开：

<!--versetest
MaybeInt:?int = option{42}
UseItem(I:int):void={}
ProcessItem(I:int)<computes>:?int=option{3}
Items:[]int = array{1,2,3}
-->
<!-- 26 -->
```verse
# 有效：在 if 条件下（失败上下文）
if (Value := MaybeInt?):
    Print("Got {Value}")

# 有效：在循环中（失败上下文）
for (Item : Items, ValidItem := ProcessItem(Item)?):
    UseItem(Item)

# 有效：在 <decides> 函数体中（失败上下文）
GetRequired(Maybe:?int)<decides>:int =
    Maybe?  # 如果也许为空则失败
```
### 嵌套

选项可以嵌套来表示多层缺席：

<!--versetest-->
<!-- 27 -->
```verse
# 双嵌套选项
Double:??int = option{option{42}}

# 单次展开获得外部选项
if (Inner := Double?):
    if (TheValue := Inner?):
        # TheValue的类型为int，等于42

# double unwrap 直接获取值
Value := Double??  # 如果任一层为空，则失败
```
辅助函数也适用于嵌套选项：

<!--versetest-->
<!-- 28 -->
```verse
UnpackNested(MaybeValue:??int):?int =
    if (Inner := MaybeValue?):
        Inner
    else:
        option{-1}  # 默认为外部空

DirectUnpack(MaybeValue:??int):int =
    if (Value := MaybeValue??):
        Value
    else:
        -1  # 任何级别默认为空
```
<!--
UnpackNested(option{option{1}})
DirectUnpack(option{option{2}})
-->

### 链式访问

`?.` 运算符提供对可选值的安全成员访问：

<!--NoCompile-->
<!-- 29 -->
```verse
entity := class:
    Name:string = "Unknown"
    Health:int = 100

MaybeEntity:?entity = option{entity{}}

# 安全的现场访问
if (Name := MaybeEntity?.Name):
    Print("Entity: {Name}")  # 成功

# 安全方法调用
MaybeEntity?.TakeDamage(10)  # 仅当实体存在时才调用

# 通过多个选项链接
linked_list := class:
    Value:int = 0
    Next:?linked_list = false

Head:?linked_list = option{linked_list{Value := 1}}
SecondValue := Head?.Next?.Value  # 如果任何链接为空，则失败
```
`?.` 运算符短路——如果该选项为空，则整个
表达式失败而不评估成员访问权限。

### 默认值

使用 `or` 运算符为空选项提供后备值：

<!--versetest-->
<!-- 30 -->
```verse
MaybeValue:?int = false
Value := MaybeValue? or 42  # 产量 42

# 链接多个选项
Primary:?string = false
Secondary:?string = option{"backup"}
Default:string = "default"

Result := Primary? or Secondary? or Default
```
### 比较

正确比较时，空选项等于 `false`，填充选项等于其展开值：

<!--versetest-->
<!-- 40 -->
```verse
EmptyOption:?int = false
EmptyOption = false  # 成功

FilledOption:?int = option{1}
FilledOption? = 1  # 成功 - 打开然后比较
```
但是，您不能在不展开的情况下直接比较可选值和非可选值：

<!--versetest-->
<!-- 41 -->
```verse
Opt:?int = option{42}
Regular:int = 42

# 必须拆开才能比较
if (Opt? = Regular):
    Print("Equal")
```
## 选项失败

将决定函数与可选返回类型相结合，创建一个系统
多层失败。这种模式可以表达复杂的条件
简洁，同时保持清晰。

一个函数可能会在两个层面上失败：

- *功能级失败*：使用 `<decides>` 整个功能失败
- *值级失败*：函数成功但返回空选项

<!--versetest
player := string
IsActive(S:string)<transacts><decides>:string=""
LookupPlayer(S:string)<transacts><decides>:string="player"
-->
<!-- 42 -->
```verse
FindEligiblePlayer(Name:string)<decides>:?player =
    Name <> ""           # 第 1 层：如果名称为空则失败
    Player := LookupPlayer[Name]  # 第 1 层：如果未找到玩家则失败
    option{IsActive[Player]}      # 第 2 层：如果玩家不活动则为空选项
```
<!-- FindEligiblePlayer["Someone"] -->

该函数有三种可能的结果：

- *功能失败*：名称为空或未找到玩家
- *功能成功但选项为空*：找到玩家但不活动
- *功能成功并填充选项*：玩家已找到并处于活动状态

调用此函数演示了分层失败：

<!--versetest
FindEligiblePlayer(S:string)<transacts><decides>:?string=option{S}
-->
<!-- 43 -->
```verse
# 功能级失败
Result1 := FindEligiblePlayer[""]  # 失败，结果1从未分配

# 函数成功，返回空选项
if (Player := FindEligiblePlayer["InactiveUser"]?):
    # 不会执行 - 函数成功但是？查询失败
else:
    # 在这里执行

# 函数成功，返回填充选项
if (Player := FindEligiblePlayer["ActiveUser"]?):
    # 在玩家绑定到活动玩家的情况下执行
```
此模式对于验证不同的失败模式特别强大：

<!--versetest-->
<!-- 44 -->
```verse
ValidateScore(Score:int)<decides>:?int =
    Score >= 0           # 第一层：拒绝负分（无效输入）
    option{Score <= 100} # 第2层：拒绝高分（超出范围）
```
功能级失败和价值级失败之间的区别让
你表达了不同类型的错误。功能级失败
通常意味着“此操作无法完成”，而值级别
失败的意思是“操作完成但结果不满足
预期标准。”

## 类型转换作为决定

Verse 中的类型转换已集成到失败系统中。动态类型转换
行为就像 `<decides>` 函数调用并且类似地使用括号
语法。例如，`Type[value]` 尝试将 `value` 的类型转换为 `Type` 并
如果不成功则失败。

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

# 类型转换作为决定操作
TryGetPhysics(Comp:component)<decides>:physics_component =
    physics_component[Comp]  # 如果Comp显然是物理组件，则成功
```
<!-- #> -->

这使得基于类型的调度很容易表达：

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
        # 未知的组件类型
        UpdateGeneric(Comp)
```
<!-- ProcessComponent(component{}) -->

强制转换本身就是条件——不需要单独的类型检查。当转换成功时，您既确认了类型又获得了正确类型的引用。

您可以将强制转换与其他决定操作链接起来：

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
    Comp := Entity.GetComponent[]  # 如果没有组件则失败
    Physics := physics_component[Comp]  # 如果不是物理的话就会失败
    IsActive[Physics]  # 如果不活动则失败
    Physics
```
每个步骤都必须成功，函数才能返回值。这将创建自记录验证链，其中类型要求是明确的。

强制转换与 `or` 组合器一起用于后备类型：

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

这会按顺序尝试每个转换，返回第一个成功的转换。它是类型安全的，因为所有选项都共享通用的 `component` 基本类型。



## 习语和模式

当你面对失败时，某些模式会出现，可以优雅地解决常见问题。

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
每行都必须成功才能继续执行。这将创建自记录代码，其中前提条件是明确的并按顺序检查。

第一次成功模式会尝试替代方案，直到其中一个有效为止：

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
这自然表示先尝试简单的解决方案，然后再尝试复杂的解决方案。

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
结果中仅包含具有等级且等级至少为 10 的敌人。

事务模式组相关变化：

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
要么整个​​交易成功，要么什么都没有改变。

**可选索引**

使用可选容器时，您可以访问其内容
使用专门的查询语法，将可选检查与
元素访问。  可选元组支持直接元素访问
查询运算符：

<!--versetest-->
<!-- 58 -->
```verse
MaybePair:?tuple(int, string) = option{(42, "answer")}

# 访问第一个元素
if (FirstValue := MaybePair?(0)):
    # FirstValue 为 42（类型：int）
    Print("First: {FirstValue}")

# 访问第二个元素
if (SecondValue := MaybePair?(1)):
    # SecondValue 是“答案”（类型：字符串）
    Print("Second: {SecondValue}")
```
同时语法`Option?(index)`：

- 查询选项是否非空
- 访问给定索引处的元组元素
- 如果两者都成功则绑定元素值

**组合和调用链**

决定函数自然组合，允许复杂的操作
由简单、可重复使用的部件构建而成。当决定函数调用时
另一个决定功能，失败会自动传播。

<!--versetest-->
<!-- 52 -->
```verse
ValidatePositive(X:int)<decides>:int =
    X > 0

Double(X:int)<decides>:int =
    Validated := ValidatePositive[X]  # 如果 X ≤ 0，则失败
    Validated * 2
```
<!-- Double[2] -->

如果 `ValidatePositive` 失败，`Double` 立即失败。经过验证的价值在链条中流动。

**保留失败上下文：**

当在非决定上下文中调用决定函数时，必须显式处理失败：

<!--versetest
FindPlayer(Name:string)<transacts><decides>:string=Name
GetDefaultPlayer():string="Default"
UsePlayer(P:string):void=return
-->
<!-- 57 -->
```verse
# 这不会编译 - ProcessPlayer 没有 <decides>
# BadProcessPlayer(Name:string):void =
#    Player := FindPlayer[Name]  # ERROR: Unhandled failure

# 使用 if 处理
ProcessPlayerWithIf(Name:string):void =
    if (Player := FindPlayer[Name]):
        UsePlayer(Player)

# 用 或 处理
ProcessPlayerWithOr(Name:string):void =
    Player := FindPlayer[Name] or GetDefaultPlayer()
    UsePlayer(Player)
```
<!--
PlayerOne := "PlayerOne"
ProcessPlayerWithIf(PlayerOne)
ProcessPlayerWithOr(PlayerOne)
-->

了解组合可以帮助您构建复杂的验证逻辑
从简单的、可测试的部分开始。

## 运行时错误

而失败（`<decides>`）代表正常控制流
事务回滚，*运行时错误*表示不可恢复
终止执行的条件。运行时错误向上传播
调用堆栈，绕过正常的失败处理，并且无法被捕获或
在Verse代码中恢复。

`Err()` 函数显式触发运行时错误，并带有可选消息：

<!--versetest-->
<!-- 66 -->
```verse
ValidateInput(Value:int):int =
    if (Value < 0):
        Err("Negative values not allowed")
    Value
```
当发生运行时错误时，执行将通过调用堆栈展开，
终止当前操作：

<!--versetest
Log(Message:string)<transacts>:void = {}
-->
<!-- 68 -->
```verse
DeepFunction()<transacts>:int =
    Log("C")
    Err("Fatal error")  # 这里运行时错误
    Log("D")            # 从不执行
    return 1

MiddleFunction():int =
    Log("B")
    Result := DeepFunction()  # 错误通过这里传播
    Log("E")                  # 从不执行
    return Result

TopFunction():void =
    Log("A")
    Value := MiddleFunction()  # 错误传播到这里
    Log("F")                   # 从不执行

# 执行顺序：A、B、C，然后终止
# 输出：“ABC”
```
运行时错误立即传播，绕过调用链中的所有后续代码。

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
    Err("Async error")  # 异步执行期间运行时错误
    WaitTicks(1)        # 从不执行
    return 1

KickOff()<suspends>:void=
    # 错误从生成的任务传播出去
    spawn{ AsyncOperation() }

```
当生成的任务遇到运行时错误时，该特定任务
终止。运行时错误不会自动传播到
生成上下文。

## 与失败共存

Verse 的失败方法源于逻辑编程，其中
计算寻找解决方案而不是执行步骤。当一个
路径失败，计算回溯并尝试替代方案。这个
非确定性模型虽然强大，但可能很难推理
完全具有普遍性。  Verse通过失败来驯服这种力量
上下文明确并限制回溯到特定的
构造。您可以获得逻辑编程的好处 - 声明式
代码、自动搜索、优雅地处理替代方案 - 无需
完全统一和无限回溯的复杂性。

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
如果不能满足任何约束，则整个尝试都会失败。在完整的逻辑编程语言中，这可能会触发复杂的回溯。在 Verse 中，失败模型更简单、更可预测，同时对于大多数问题仍然具有足够的表现力。

在 Verse 中有效地应对失败需要转变心态。不要考虑需要避免的错误条件，而要考虑需要满足的成功条件。与其在采取行动之前检查所有内容的防御性编程，不如编写尝试操作并优雅地处理失败的乐观代码。

这种视角使代码更具可读性，意图更清晰。当您看到标有 `<decides>` 的函数时，您就知道它表示可能没有结果的计算。当您在失败上下文中按顺序看到表达式时，您就知道它们代表必须全部满足的条件。当您看到 `or` 运算符时，您就知道它代表了可以尝试的替代方案。

Verse 中的失败并不是值得恐惧或避免的事情，而是一种值得拥抱的工具。它通过消除某些类别的错误来使程序更安全。它通过统一验证和操作使代码更加清晰。它通过提供自动回滚使复杂的操作变得更加简单。最重要的是，它使我们编写程序的方式与我们思考现实世界中的行动和决策的方式保持一致。

当你编写更多的 Verse 代码时，你会发现失败成为你的第二天性。在表达条件时，您会自然而然地使用可失败表达式。您将构建您的函数，以便在不满足先决条件时尽早失败。您将在没有嵌套条件的情况下编写失败来创建复杂的控制流。您将欣赏到这种关于控制流的不同思考方式如何产生比传统方法更健壮且更具表现力的代码。
