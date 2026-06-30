# 控制流程

每个程序都有其执行的自然节奏，即顺序
处理哪些指令并做出决定。在Verse中，
这个流程不仅仅是通过线条的机械进展
代码——这是不同类型之间精心编排的舞蹈
表达式，每个表达式都会影响你的整体行为
程序。

## 块

代码块是一个基本的组织单元，它将相关的
表达式组合在一起并为变量创建一个新的范围
常数。与许多语言不同，块仅仅是语法上的
方便起见，块本身就是表达式，这意味着它们产生
值就像任何其他表达式一样。

范围的概念对于理解代码块至关重要。当你
在块内创建变量或常量，它仅存在于
该块的上下文。这种遏制确保您的代码仍然存在
组织良好，并且名称不会意外地在不同的环境中发生冲突
你的程序的一部分。考虑这个函数，它的主体是一段代码
本身包含一个 if-then-else 表达式的块
由三个不同的代码块组成。

<!--versetest-->
<!-- 01 -->
```verse
CalculateReward(PlayerLevel:int)<reads>:int =
    if:
        PlayerLevel > 10
        Multiplier := 2.0  # 仅存在于该块内
        Base := 100
        Result := Floor[(Base+PlayerLevel) * Multiplier] # 无穷大失败
    then:
        Result  # 该块扩展了 if 的范围
    else:
        50      # 不同分支，不同范围
                # 此处不存在乘数和结果
```
<!-- CalculateReward(11) = 222 -->

Verse 具有灵活的语法，具有三种等效格式
写作块。空格格式是最常见的，使用冒号来表示
引入块和缩进来显示结构：

<!--versetest
IsPlayerReady()<decides><transacts>:void = {}
StartMatch()<transacts>:void = {}
BeginCountdown()<transacts>:void = {}
-->
<!-- 02 -->
```verse
if (IsPlayerReady[]):
    StartMatch()
    BeginCountdown()
```
多行花括号格式让程序员熟悉
来自 C 风格语言：

<!--versetest
IsPlayerReady()<decides><transacts>:void = {}
StartMatch()<transacts>:void = {}
BeginCountdown()<transacts>:void = {}
-->
<!-- 03 -->
```verse
if (IsPlayerReady[]) {
    StartMatch()
    BeginCountdown()
}
```
对于简单的操作，单行点格式使代码简洁：

<!--versetest-->
<!-- 04 -->
```verse
HasPowerup()<computes><decides>:void={}
ApplyBoost():void={}
F():void=
    if (HasPowerup[]). ApplyBoost()
```
由于一切都是表达式，因此块本身具有值。的
块的值由块内执行的最后一个表达式给出
它。这使得可以实现复杂计算的优雅模式
封装在与周围环境无缝集成的块中
代码：

<!--versetest
CalculateScore()<computes>:int = 100
CalculateBonus(Time:float)<computes>:int = 50
CompletionTime:float = 10.0
AccuracyValue:float = 0.95
-->
<!-- 05 -->
```verse
FinalScore := block:              # 该变量具有块的值
    Base := CalculateScore()
    Bonus := CalculateBonus(CompletionTime)
    Accuracy := Floor[AccuracyValue * 100.0]
    Base + Bonus + Accuracy       # 这将成为该块的值
```
## 如果表达式

`if` 表达式使用成功和失败来驱动决策（请参阅
[失败]（08_failure.md）了解详细信息）。当表达式中
条件成功，执行相应分支：

<!--versetest
player := class:
   CanJump()<computes><decides>:void={}
   Jump()<computes>:void={}
   GetEquippedWeapon()<computes><decides>:weapon=weapon{}
   Idle()<computes>:void={}

weapon:=class<computes>{
   Fire():void={}
}
ConsumeAmmo():void={}
PlayJumpSound():void={}
-->
<!-- 07 -->
```verse
HandlePlayerAction(Player:player, Action:string):void =
    if (Action = "jump", Player.CanJump[]):
        Player.Jump()
        PlayJumpSound()
    else if (Action = "attack", Weapon := Player.GetEquippedWeapon[]):
        Weapon.Fire()
        ConsumeAmmo()
    else:
        # 默认操作
        Player.Idle()
```
这种方法允许您链接可能失败的条件，而无需
每一步都有明确的错误处理。

另一种语法使用 `then:` 和 `else:` 关键字显式地
标签分支：

<!--versetest-->
<!-- 08 -->
```verse
ProcessValue(Value:int):string =
    if:
        Value > 0
        Value < 100
    then:
        "Valid"
    else:
        "Out of range"

ProcessValue(50) = "Valid"
```
当您有多个条件时，此语法可以提高可读性
或者想要强调条件与动作的分离。 

`if` 中的条件必须至少包含一个可以
失败。此要求确保 `if` 用于其预期用途
目的——处理不确定的结果：

<!--NoCompile-->
<!-- 10 -->
```verse
# 错误：条件不能失败
if (1 + 1):  # 编译错误 - 没有错误的表达式
    DoSomething()

# 有效：数组访问可能会失败
if (FirstItem := Items[0]):
    Process(FirstItem)
```
空条件也是不允许的——每个 `if` 都必须测试一些东西。

如果条件中的任何表达式失败，控制流将继续到
`else` 分支（如果存在）。评估时执行的任何效果
条件会自动回滚（请参阅
[失败](08_failure.md#speculative-execution)详情):

<!--versetest
GetPlayerScore()<decides><computes>:int=1
-->
<!-- 11 -->
```verse
var Counter:int = 0

if:
    set Counter = Counter + 1  # 临时变更
    Score := GetPlayerScore[]  # 可能会失败
    Score > 100
then:
    # 计数器增加
else:
    # 计数器回滚到原始值 - 增量已撤消！
```
这种推测执行使条件逻辑更安全——您可以
乐观地执行操作，知道如果发生以下情况，操作将会逆转
后续条件失败。

条件中定义的变量可在 `then` 分支中使用
但不在 `else` 分支中：

<!--NoCompile-->
<!-- 12 -->
```verse
if:
    Player := FindPlayer[Name]  # 定义玩家
then:
    AwardBonus(Player)  # 好的 - 玩家可用
else:
    Penalize(Player)  # 编译错误
```
此范围界定反映了逻辑流程：在 `else` 分支中，
条件失败，因此条件期间绑定的任何变量都可能
没有有意义的价值。

由于 `if` 是一个表达式，因此它会产生一个值。当所有分支
返回兼容类型，`if` 可以在值存在的任何地方使用
预期：

<!--versetest
IsCritical:logic= false
BaseDamage:int=0
Health:int=0
-->
<!-- 13 -->
```verse
Damage := if (IsCritical?):
    BaseDamage * 2
else:
    BaseDamage

# 三元式
Status := if (Health > 50). "Healthy" else. "Wounded"
```
当分支具有不兼容的类型时，结果将扩展为 `any`：

<!--versetest
UseNumber:logic=false
-->
<!-- 14 -->
```verse
# 分支中的不同类型产生任何
Result:any = if (UseNumber?) then 42 else "text"
```
所有分支都必须为 `if` 生成一个值，以用作
表达。

## 大小写表达式

当您需要根据多个可能的值做出决策时，
`case` 表达式提供清晰、可读的分支：

<!--versetest-->
<!-- 15 -->
```verse
GetWeaponDamage(WeaponType:string):float =
    case(WeaponType):
        "sword"  => 50.0
        "bow"    => 35.0
        "staff"  => 40.0
        "dagger" => 25.0
        _        => 10.0  # 未知武器的默认伤害

GetWeaponDamage("sword") = 50.0
```
当您有离散值需要匹配时，使用 `case` 表达式
反对，让你的意图比一系列`if-else`更清晰
条件。

Case 表达式适用于支持直接值的特定类型
比较：

- **原语**：`int`、`logic`、`char`
- **字符串**：`string`
- **枚举**：开放和封闭枚举
- **细化类型**：具有约束的自定义类型

由于实现原因，它们不适用于 `float`、对象和元组
限制。

**使用枚举进行详尽检查。** 检查 `case` 和 `enum`
为了详尽无遗。  对于所有值都已知的封闭枚举，
编译器验证您已处理所有情况：

<!--versetest
direction := enum:
    North
    South
    East
    West
-->
<!-- 17 -->
```verse
# 详尽 - 无需通配符
GetVector(Dir:direction):tuple(int, int) =
    case (Dir):
        direction.North => (0, 1)
        direction.South => (0, -1)
        direction.East => (1, 0)
        direction.West => (-1, 0)

GetVector(direction.North) = (0, 1)
```
如果在涵盖所有情况时添加通配符，您将收到警告
通配符无法访问：

<!--versetest
direction := enum:
    North
    South
    East
    West

GetVectorWithUnreachable(Dir:direction):tuple(int, int) =
    case (Dir):
        direction.North => (0, 1)
        direction.South => (0, -1)
        direction.East => (1, 0)
        direction.West => (-1, 0)
        _ => (0, 0)

assert:
    # Test that the function works despite unreachable wildcard
    GetVectorWithUnreachable(direction.North) = (0, 1)
<#
-->
<!-- 18 -->
```verse
    case (Dir):
        direction.North => (0, 1)
        direction.South => (0, -1)
        direction.East => (1, 0)
        direction.West => (-1, 0)
        _ => (0, 0)  # 警告：所有情况均已涵盖
```
<!-- #> -->

`<decides>` 上下文中允许不完整的案例覆盖：

<!--versetest
direction := enum{  North, South, East, West}
-->
<!-- 19 -->
```verse
# <decides>上下文中没有通配符 - 确定
GetPrimaryDirection2(Dir:direction)<decides>:string =
    case (Dir):
        direction.North => "Primary"
        # 其他方向导致功能失败
```
开放枚举可以在发布后添加值，因此它们永远不能
详尽无遗。它们始终需要通配符或 `<decides>`
上下文。

## 循环表达式

`loop` 表达式创建一个无限循环，一直持续到
明确破坏：

<!--versetest
UpdatePlayerPositions()<transacts>:void={}
CheckCollisions()<transacts>:void={}
RenderFrame()<transacts>:void={}
GameOver()<decides><transacts>:void={}
-->
<!-- 22 -->
```verse
GameLoop():void =
    loop:
        UpdatePlayerPositions()
        CheckCollisions()
        RenderFrame()
        if (GameOver[]). break
```
`break` 表达式完全退出循环，终止迭代。
`break` 具有“底部”类型——表示计算的类型
永远不会正常返回。由于底部类型是所有类型的子类型
其他类型，`break` 可以在任何类型上下文中使用：

<!--versetest-->
<!-- 55 -->
```verse
NumberOfBits(X:int):int =
    var B:int = 1
    var C:int = 0
    loop:
        set B = if (B > X) { break } else { 2*B }
        set C = C+1
    C
```
这演示了底部类型：`break` 与 `int` 结合（来自 `2*B`）
在 if 表达式中。赋值 `set B = ...` 使用的值
if 表达式，表明 `break` 在任何类型上下文中都是兼容的。

**循环返回值：**循环表达式本身产生一个类型的值
`true`（顶级型），无论其体内出现什么表情。
这个返回值在实践中很少有用——循环通常用于
他们的副作用。

当`break`出现在嵌套循环中时，只退出最里面的
封闭循环：

<!--versetest-->
<!-- 57 -->
```verse
var Outer:int = 0
loop:
    set Outer += 1
    var Inner:int = 0
    loop:
        set Inner += 1
        if (Inner = 5):
            break        # 退出内循环
    if (Outer = 10):
        break            # 退出外循环
```
以下限制适用。 `break` 语句必须出现在
代码块，而不是复杂表达式的一部分。  必须有一个循环
至少包含一个非中断语句。最后，使用`break`
在 `loop` 之外会产生错误：

<!--versetest
ShouldStop()<decides>:void={}

assert_semantic_error(3506, 3581):
    ProcessData():void =
       if (ShouldStop[]):
               break      # Error
<#
-->
<!-- 58 -->
```verse
ProcessData():void =
   if (ShouldStop[]):
           break      # 错误
```
<!-- #> -->
<a id="for-expressions"></a>
## `for` 表达式

`for` 表达式迭代集合、范围和其他
可迭代类型，提供更结构化的重复方法：

<!--versetest
player:=class{}
GetScore(P:player):int=100
<#
-->
<!-- 23 -->
```verse
CalculateTotalScore(Players:[]player)<transacts>:int =
    var Total:int = 0
    for (Player : Players):
        PlayerScore := GetScore(Player)
        set Total += PlayerScore
    Total
```
<!-- #> -->

虽然它在早期的命令式语言中看起来很熟悉，但 `for` 是
最好将其视为结合迭代的功能结构，
通过推测执行进行过滤，并构建集合
结果。

<!--versetest-->
<!-- 223 -->
```verse
Values:[]float= array{1.0, 10.1, 100.2}
Result := 
   for:
      V : Values
      V >= 10.0
      R := Floor[V]
   do:
      R*2.0

Result = array{20.0, 200.0}
```
上面是用另一种多子句语法编写的，使用
`do:` 关键字用于将迭代规范与主体分开。
`for` 迭代 `Values` 数组，丢弃较小的值
大于 10 并向下舍入数字。它返回一个浮点数组。
`Floor` 函数定义为 `decides` ——如果它失败了
迭代将被丢弃。

还有另一种替代语法：单行点语法
简单的操作：

<!--versetest
Values:[]int = array{1, 2, 3}
DoSomething(V:int):void = {}
-->
<!-- 26 -->
```verse
# 单线点样式
for (V : Values). DoSomething(V)
```
**索引和值对：**

迭代数组或映射时，您可以访问索引/键和值
使用对语法 `Index -> Value` 或 `Key -> Value`：

<!--versetest
player:=struct{ Name:string }
-->
<!-- 28 -->
```verse
PrintRoster(Players:[]player):void =
    for (Index -> Player : Players):
        Print("Player {Index}: {Player.Name}")
```
该索引从零开始，符合 Verse 的数组索引约定。

**在 For 子句中定义变量：**

for 循环允许您定义可以是的中间变量
在后续过滤器或循环体中使用：

<!--versetest-->
<!-- 29 -->
```verse
# 根据 X 定义 Y
Doubled := for (X := 1..5, Y := X * 2):
    Y  # 返回数组{2,4,6,8,10}

# 与过滤相结合
SafeDivision := for (X := -3..3, X <> 0, Y := Floor[10.0 / (X*1.0)]):
    Y  # 跳过 X=0，返回数组{-3, -5, -10, 10, 5, 3}
```
这些中间变量的范围仅限于迭代，并且可以
引用同一子句中较早的变量。

**多重过滤器：**

您可以使用逗号分隔或链接多个过滤条件
以分号分隔的表达式。每个过滤器都必须可失败，如果有一个失败，
迭代被跳过：

<!--versetest-->
<!-- 30 -->
```verse
# 多个独立过滤器
Filtered := for (X := 1..10, X <> 3, X <> 7):
    X  # 返回数组{1,2,4,5,6,8,9,10}

# 带有中间变量的过滤器
Complex := for (X := 1..5, X <> 2, Y := X * 2, Y < 10):
    Y  # 仅包括 X≠2 且 Y<10 的值
```
每个过滤条件按顺序评估，并继续迭代
仅当所有条件都成功时。

**迭代映射：**

可以通过两种方式迭代映射：仅值或键值对
使用对语法：

<!--versetest-->
<!-- 31 -->
```verse
# 仅迭代值
Scores:[int]int = map{1 => 100, 2 => 200, 3 => 150}
TopScores := for (Score : Scores):
    Score  # 返回数组{100, 200, 150}

# 迭代键值对
PlayerScores:[string]int = map{"Alice" => 100, "Bob" => 200}
for (PlayerName -> Score : PlayerScores):
    Print("{PlayerName} scored {Score}")
```
映射保留插入顺序，因此迭代顺序与中的顺序匹配
哪些键已添加到映射中。

**字符串迭代：**

字符串可以逐字符迭代：

<!--versetest-->
<!-- 32 -->
```verse
CountVowels(Text:string):int =
    var Count:int = 0
    for (Char : Text, Char = 'a' or Char = 'e' or Char = 'i' or Char = 'o' or Char = 'u'):
        set Count += 1
    Count
```
**嵌套迭代（笛卡尔积）：**

多个迭代源创建嵌套循环，生成笛卡尔积：

<!--NoCompile-->
<!-- 33 -->
```verse
PrintGrid():void =
    for (X := 1..3, Y := 1..3):
        Print("({X}, {Y})")
    # 产生：(1,1)、(1,2)、(1,3)、(2,1)、(2,2)、(2,3)、(3,1)、(3,2)、(3,3)
```
**过滤失败：**

Verse 的 `for` 表达式在利用
失败上下文，因为它们可以自然地过滤：

<!--versetest
player:=struct{ Name:string }
GetScore(P:player)<computes>:int=0
-->
<!-- 34 -->
```verse
GetHighScorers(Players:[]player):[]player =
    for (Player : Players, Score := GetScore(Player), Score > 1000):
        Player  # 仅包含得分 > 1000 的玩家
```
当迭代头中的任何表达式失败时，该迭代为
跳过了。这允许优雅的过滤，无需显式 `if`
声明：

<!--versetest
item:=struct{Price:float}
-->
<!-- 35 -->
```verse
# 过滤预算内的项目并应用转换
AffordableItems(Items:[]item, Budget:float):[]float =
    for (Item : Items, Item.Price <= Budget):
        Item.Price * 1.1  # 应用 10% 的加价
```
**作为表达式：**

与其他控制流结构一样，`for` 是一个表达式。当主体产生值时，`for` 将它们收集到一个数组中：

<!--versetest
player:=struct{Name:string}
-->
<!-- 36 -->
```verse
# 收集玩家姓名
GetNames(Players:[]player):[]string =
    for (Player : Players):
        Player.Name  # 每次迭代都会产生一个字符串
```
这使得 `for` 成为转换集合的强大工具，而无需
显式累加器变量。

**打破 For 循环：**

`break` 语句无法提前退出 `for` 循环。如果您只需要
迭代的第一个匹配结果，使用 `first` 而不是 `for`
（参见下面的[第一个表达式](#first-expressions)）。

**继续注意：**

与许多语言不同，Verse 目前不支持 `continue`
语句跳到下一次迭代。相反，使用条件
基于逻辑或基于失败的过滤来实现类似的结果：

<!--versetest
item:=struct{IsValid:logic}
ProcessItem(I:item):void={}
-->
<!-- 38 -->
```verse
# 使用条件块而不是继续
ProcessItems(Items:[]item):void =
    for (Item : Items):
        if (Item.IsValid?):
            ProcessItem(Item)
        # 无需继续 - 只需带条件的结构

# 或者在标头中使用基于失败的过滤
ProcessValidItems(Items:[]item):void =
    for (Item : Items, Item.IsValid?):
        ProcessItem(Item)  # 只有有效的物品才能到达这里
```
**范围迭代。** 范围运算符 `..` 提供数字
整数序列上的迭代。范围两端均包含在内：

<!--versetest-->
<!-- 27 -->
```verse
# 迭代：1、2、3、4、5（包括两个边界）
for (I := 1..5):
    Print("Count: {I}")

# 单元素范围
for (I := 42..42):
    Print("Answer: {I}")  # 打印一次：“答案：42”

# 空范围（开始 > 结束不产生迭代）
for (I := 5..1):
    Print("Never executes")  # 循环体永远不会运行
```
`..` 运算符始终包含在内。没有专属范围
语法。

范围边界按特定顺序进行评估，并且会发生副作用
可以预见的是：

1. **首先评估左边界**，然后评估右边界
2. **始终评估两个边界**，即使范围为空
3. **副作用按顺序发生**，无论是否发生迭代

虽然您无法将范围存储为值，但可以使用以下命令创建数组
对于表达式：

<!--versetest-->
<!-- 47 -->
```verse
# 这是有效的，因为对于生成一个吞吐量，而不是因为范围是可存储的
DoubledNumbers:[]int = for (I := 1..5){ I * 2 }

# 然后可以正常迭代数组
for (N : DoubledNumbers):
    Print("{N}")
```
该范围仅在 for 表达式求值期间存在；的
结果数组是存储的内容。

**限制。** for 循环有几个重要的限制：

1. **迭代源必须是可迭代的：** 仅范围（`1..10`），
   数组、映射和字符串可以迭代。 

2. **过滤器必须可失败：** 过滤条件必须包含 at
   至少有一个表达式可能会失败。 

3. **无法重新定义迭代变量：** 无法重新定义迭代变量
   同一子句中的迭代变量。

4. **无法定义可变变量：** 使用 `var` 来声明
   for 子句中不允许使用变量。

范围运算符 `..` 具有严格的限制，使其与众不同
来自其他可迭代类型。范围*不是一流的值*——它们
是迭代地将范围内的每个整数生成为
单独的值。在某些情况下不能使用范围
可能期望它们能够工作：

<!--NoCompile-->
<!-- 40 -->
```verse
# 错误：无法在变量中存储范围
MyRange := 1..10
for (I := MyRange):

# 错误：无法将范围传递给函数
ProcessRange(1..10)

# 错误：无法使用范围作为独立表达式
Result := 1..10

# 错误：无法将范围放入数组中
Ranges := array{1..10}

# 错误：无法索引范围
Value := (1..10)(5)

# 错误：无法访问范围内的成员
Length := (1..10).Length
```
系列专用于 `int` 类型。其他数字类型，
不支持布尔值、类型或对象。

<a id="first-expressions"></a>
## 第一个表达式

!!!注意“未发布的功能”
    `first` 表达式尚未发布。本节记录了当前不可用的计划功能。

`first` 表达式与 `for` 类似，但不是评估
域子句每次迭代的主体，它仅计算
成功的域子句的**第一次**迭代。相反
像 `for` 一样生成数组，它生成主体的值
对于该单次迭代。如果没有迭代到达主体，则 `first`
失败 - 因此它需要 `<decides>` 上下文。

<!--versetest
player:=struct{ Name:string }
GetScore(P:player)<computes><decides>:int=0
-->
<!-- 80 -->
```verse
# 找到第一个得分高于阈值的玩家
FindTopScorer(Players:[]player, Threshold:int)<decides>:player =
    first (Player : Players; GetScore[Player] > Threshold):
        Player
```
与 `for` 一样，`first` 表达式支持三种语法形式。
块形式使用 `do:` 将迭代子句与
身体：

<!--NoCompile-->
<!-- 81 -->
```verse
# 带 do 的块形式：
first:
    X : Collection
    Predicate[X]
do:
    Process(X)

# 牙套形式
first(X : Collection; Predicate[X]){ Process(X) }

# 单个表达式的点形式
first(X : Collection; Predicate[X]). Process(X)
```
`first` 表达式使用与 `for` 相同的绑定语法。你
可以迭代数组、映射、字符串和范围。您可以使用索引值
与 `->` 语法配对，链接多个过滤器并嵌套多个
迭代源：

<!--versetest-->
<!-- 82 -->
```verse
# 使用索引 -> 值绑定查找元素的索引
IndexOf(Arr:[]int, Target:int)<decides>:int =
    first(I -> V : Arr, V = Target). I
```
请注意，`first` 产生 **body** 表达式的值，而不是
迭代变量。这使得搜索成为可能
一个东西并产生另一个东西——例如，通过匹配一个来找到一个索引
值。

**首先与对于：**

| | `for` | `first` |
|-|--------|---------|
|产量 |所有结果的数组 |仅第一个结果 |
|没有匹配 |空数组 | **失败**（需要 `<decides>`）|
|停止 |经过所有迭代 |第一次迭代后 |

**常见模式：**

由于`first`需要`<decides>`，所以一种常见的使用方法是包装
它位于 `if` 或 `option` 中以处理未找到匹配项的情况：

<!--versetest-->
<!-- 83 -->
```verse
# 使用 if 进行回退查找
FindOrDefault(Arr:[]int, Target:int):int =
    if (Index := first(I -> V : Arr, V = Target). I):
        Index
    else:
        -1
```
或者：

<!--versetest-->
<!-- 84 -->
```verse
# 使用 if 进行回退查找
FindOptional(Arr:[]int, Target:int):?int =
    option:
        Index := first(I -> V : Arr, V = Target). I
            Index
```
## 退货声明

`return` 语句提供了从函数中显式提前退出的功能，
允许您在到达之前终止执行并返回一个值
函数体末尾：

<!--versetest-->
<!-- 48 -->
```verse
ValidateInput(Value:int):string =
    if (Value < 0):
        return "Error: Negative value"

    if (Value > 1000):
        return "Error: Value too large"

    "Valid"     # 隐式回报
```
Return 语句只能出现在您的特定位置
代码——它们必须处于“尾部位置”，这意味着它们必须是最后一个
在控制退出范围之前执行的操作。这个限制
确保可预测的控制流：

<!--versetest
GetOrder(:int)<transacts><decides>:order=order{}
order := class<allocates>{ IsValid()<decides><transacts>:logic=false }
-->
<!-- 49 -->
```verse
# 有效：返回是最后一次操作
ProcessOrder(OrderId:int)<transacts>:string =
    if (Order := GetOrder[OrderId]):
        if (Order.IsValid[]):
            return "Processed"
    "Invalid order"

# 有效：在两个分支中返回
GetStatus(Value:int):string =
    if (Value > 0):
        return "Positive"
    else:
        return "Non-positive"
```
Verse 函数隐式返回其最后一个表达式的值，
所以 `return` 仅在提前退出时需要：

<!--versetest
CalculateBonus(Score:int):int={
    if(Score<100)then{return 0}
    Score*10
}
-->
<!-- 51 -->
```verse
# 隐式回报
GetValue():int = 42  # 返回 42

# 明确提前返回
GetDiscount(Price:float):float =
    if (Price < 10.0):
        return 0.0  # 提前退出无折扣

    Price * 0.1  # 隐性回报 10% 折扣
```
在具有 `<decides>` 效果的功能中，`return` 允许您
从早期退出中提供成功的价值，同时仍然允许其他
失败的路径：

<!--versetest
config:=struct{MaxRetries:int}
GetConfig()<transacts><decides>:config=config{MaxRetries:=3}
AttemptOperation(Retry:int)<computes><decides>:string="success"
-->
<!-- 52 -->
```verse
RetryableOperation()<transacts>:string =
    if (Config := GetConfig[]):
        for (Retry := 1..Config.MaxRetries):
            if (Result := AttemptOperation[Retry]):
                return Result  # 成功-立即退出
    "Failed" # 所有重试均已用尽
```
此模式对于要返回的搜索操作很常见
找到匹配项后立即执行，但如果未找到匹配项则失败。

<a id="defer-statements"></a>
## `defer` 语句

`defer` 语句安排代码在封闭范围内运行
退出。这使得它对于关闭等清理操作非常有价值
文件、释放资源或日志记录。

Defer 是**基于范围**，而不是基于功能。 `defer` 块执行
当离开直接包含它的范围时，包括：

- **函数体** — 在函数返回时运行
- **`for` 循环** — `for` 主体在其自己的中运行每个迭代
  范围； `for` 域还引入了词法范围
- **`loop` 块的每次迭代** — 在每个块的末尾运行
  迭代（包括 `break`）
- **`if`/`then`/`else` 子句** — 在离开所选分支时运行
- **`block` 范围** — 离开区块时运行
- **`not` 表达式** — `not e` 在新的词法范围中计算 `e`
- **`or` 表达式** — `e0 or e1` 在新词法中计算 `e0`
  范围
- **`and` 表达式** — `e0 and e1` 计算整个表达式
  在新的词汇范围内
- **`option` 和 `logic` 表达式** — `option{e}` 和 `logic{e}`
  在新的词法范围中评估 `e`
- **`case` 表达式** — `case(e0){e1=>e2, e3=>e4}` 创建一个
  整个 `case` 的词法范围，然后是每个结果
  表达式（`e2`、`e4`）
- **原型实例化** — `my_class{...}` 引入了词法
  身体范围
- **`defer` 阻止自身** — 嵌套延迟在外部延迟运行时运行
  推迟完成
- **结构化并发宏** (`race`、`rush`、`branch`) —
  每个臂都在自己的词法范围内运行
- **`spawn`、`await` 和 `batch` 表达式** — `spawn{e}`、
  `await{e}` 和 `batch{e}` 在新的词法范围中评估 `e`
- **`live` 绑定** — `live Name : e0 = e1` 创建一个新的词法
  `e1` 的范围
- **取消并发作用域** — 在取消期间运行
  展开（参见[并发](14_concurrency.md#cleanup-and-resource-management)）

这是一个基本示例：

<!--versetest
OpenFile(P:string)<computes>:?int=false
CloseFile(P:int)<computes>:void={}
ReadFile(P:int)<computes>:?string=false
ProcessContents(P:string)<computes><decides>:void={}
SaveResults()<computes><decides>:void={}
-->
<!-- 61 -->
```verse
ProcessFile(FileName:string)<transacts><decides>:void =
    File := OpenFile(FileName)?
    defer:
        CloseFile(File)  # 成功或提前退出时运行

    Contents := ReadFile(File)?
    ProcessContents[Contents]
    SaveResults[]
```
当范围成功退出或通过
显式控制流，如 `return`：

<!--versetest
OpenConnection()<transacts>:int=0
CloseConnection(Id:int)<transacts>:void={}
Query(Id:int)<decides><transacts>:string="result"
ProcessResult(R:string)<transacts>:void={}

ProcessQuery()<transacts>:void =
    ConnId := OpenConnection()
    defer:
        CloseConnection(ConnId)  # Cleanup always needed

    for (Attempt := 1..5):
        if (Result := Query[ConnId]):
            ProcessResult(Result)
            return  # defer executes after return being called

    # defer executes before leaving the function scope on success

assert:
    # ProcessQuery is defined and demonstrates defer with return
<#
-->
<!-- 62 -->
```verse
ProcessQuery()<transacts>:void =
    ConnId := OpenConnection()
    defer:
        CloseConnection(ConnId)  # 总是需要清理

    for (Attempt := 1..5):
        if (Result := Query[ConnId]):
            ProcessResult(Result)
            return  # defer executes after return being called

    # defer executes before leaving the function scope on success
```
<!-- #> -->

这是一个微妙但关键的点：如果一个函数由于以下原因而失败
推测执行，延迟代码**不**执行。这是
因为失败会触发回滚，从而撤销所有影响，包括
延迟块的调度：

<!--versetest
AcquireResource()<transacts><decides>:int=0
ReleaseResource(Id:int)<transacts>:void={}
RiskyOperation(Id:int)<transacts><decides>:void={}
-->
<!-- 63 -->
```verse
ExampleWithFailure()<transacts><decides>:void =
    ResourceId := AcquireResource[]
    defer:
        ReleaseResource(ResourceId) # 预定...

    RiskyOperation[ResourceId] # 这失败了！
    # defer does NOT run - entire scope was speculative and rolled back
```
当`RiskyOperation`失效时，整个功能也失效，并且
推测执行会撤销一切——包括延迟
注册。资源清理永远不会发生，因为资源
收购本身被回滚。

这种行为确保了一致性：如果一个函数失败了，就好像它失败了一样
从未运行过，包括计划的任何清理代码。

**执行顺序：**

当同一个作用域存在多个`defer`时，它们执行在
定义的相反顺序（后进先出），模仿
基于堆栈的嵌套资源清理：

<!--versetest
OpenDatabase()<transacts>:int=0
CloseDatabase(Id:int)<transacts>:void={}
BeginTransaction(Id:int)<decides><transacts>:int=0
CommitTransaction(Id:int)<transacts>:void={}
DoWork()<transacts><decides>:void={}
-->
<!-- 64 -->
```verse
DatabaseTransaction()<transacts><decides>:void =
    DbId := OpenDatabase()
    defer:
        CloseDatabase(DbId)  # 执行第二个（外部资源）

    TxnId := BeginTransaction[DbId]
    defer:
        CommitTransaction(TxnId)  # 首先执行（内部资源）

    DoWork[]  # 工作在两个资源都处于活动状态时进行
    # 延迟执行：CommitTransaction，然后CloseDatabase
```
**延迟和异步取消：**

当异步操作被取消时，延迟代码也会执行，例如
当 `race` 完成或 `spawn` 中断时：

<!--versetest
AcquireResource()<transacts>:int=0
ReleaseResource(Resource:int)<transacts>:void={}
LongRunningTask(Resource:int)<suspends><transacts>:void={}

ProcessWithTimeout()<suspends><transacts>:void =
    race:
        block:
            Resource := AcquireResource()
            defer:
                ReleaseResource(Resource)  # Runs if cancelled

            LongRunningTask(Resource)

        block:
            Sleep(10.0)  # Timeout
    # If timeout wins, first block is cancelled and defer runs

assert:
    # ProcessWithTimeout demonstrates defer with async cancellation
<#
-->
<!-- 65 -->
```verse
ProcessWithTimeout()<suspends><transacts>:void =
    race:
        block:
            Resource := AcquireResource()
            defer:
                ReleaseResource(Resource)  # 如果取消则运行

            LongRunningTask(Resource)

        block:
            Sleep(10.0)  # 超时
    # 如果超时获胜，第一个块将被取消并推迟运行
```
<!-- #> -->

这确保即使并发控制中断您的代码时也会进行清理。

**嵌套延迟：**

Defer 语句可以嵌套在其他 defer 块中，从而创建一个
级联清理操作：

<!--versetest
Log(S:string)<transacts>:void={}
-->
<!-- 66 -->
```verse
ProcessWithCleanup():void =
    Log("A")
    defer:
        Log("B")
        defer:
            Log("inner")  # 在 B 之后运行
        Log("C")
    Log("D")
    # 输出：A D B C 内
```
每次嵌套时执行顺序遵循 LIFO 原则
level——内部延迟在外部延迟的代码之后执行，保持
类似堆栈的清理顺序。

**控制流中的延迟：**

延迟在所有控制流结构中都能正常工作：

<!--versetest
Log(S:string)<transacts>:void={}
-->
<!-- 67 -->
```verse
ProcessLoop():void =
    for (I := 0..2):
        Log("Start")
        defer:
            Log("Cleanup")  # 每次迭代后运行
        Log("End")
    # 输出： 开始结束清理 开始结束清理 开始结束清理

ProcessWithIf(Condition:logic):void =
    if (Condition?):
        defer:
            Log("Then cleanup")
        Log("Then body")
    else:
        defer:
            Log("Else cleanup")
        Log("Else body")
```
每个控制流路径独立执行自己的延迟。

**Defer 限制。** defer 语句有重要的限制
确保行为可预测：

1. **不能为空：** Defer块必须至少包含一个
   表达式：

2. **不能用作表达式：** Defer不能用在位置上
   其中预期值。

3. **不能跨越边界：** Defer块不能包含`return`，
   `break`，或其他将退出延迟范围的控制流。

4. **不能失败：** defer 块中的表达式不能失败。

5. **不能直接挂起：** Defer块不能包含挂起
   表达式，但它们可以使用 `spawn` 进行即发即忘异步
   操作。

了解 `defer` 如何与异步取消和并发交互
类似 `race` 和 `spawn` 的结构，请参见
[清理和资源管理](14_concurrency.md#cleanup-and-resource-management)。

## 分析

了解代码的执行方式对于优化至关重要，并且
`profile` 表达式测量执行时间：

<!--versetest-->
<!-- 73 -->
```verse
OptimizedCalculation():float =
    profile("Complex Math"):
        var Result:float = 0.0
        for (I := 1..1000000):
            set Result += Sin(I*1.0) * Cos(I*1.0)
        Result
```
配置文件表达式包含您要测量的代码，
将执行时间记录到输出。您可以添加描述性标签
组织您的分析输出，使其更容易识别
复杂系统中的瓶颈。

配置文件表达式透明地传递其结果，这意味着
您可以将它们包装在任何表达式中，而无需更改程序的
行为：

<!--versetest
BaseDamage:float = 50.0
GetMultiplier()<computes>:float = 1.5
GetCriticalBonus()<computes>:float = 2.0
-->
<!-- 74 -->
```verse
PlayerDamage := profile("Damage Calculation"):
    BaseDamage * GetMultiplier() * GetCriticalBonus()
```
