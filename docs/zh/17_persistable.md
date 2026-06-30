# 持久化类型

持久类型允许您存储超出范围的持久数据
当前游戏会话。这对于保存玩家进度至关重要，
偏好设置以及其他应保持的游戏状态
多个游戏会话。

使用模块范围的 `weak_map(player, t)` 存储持久数据
变量，其中 `t` 是任何持久类型。当玩家加入
游戏中，他们之前保存的数据会自动加载到所有
`weak_map(player, t)` 类型的模块范围变量。

<!--NoCompile-->
<!-- 01 -->
```verse
using { /Fortnite.com/Devices }
using { /UnrealEngine.com/Temporary/Diagnostics }
using { /Verse.org/Simulation }

# 存储玩家数据的全局持久变量
MySavedPlayerData : weak_map(player, int) = map{}

# 初始化玩家数据（如果尚不存在）
InitializePlayerData(Player : player) : void =
    if (not MySavedPlayerData[Player]):
        if (set MySavedPlayerData[Player] = 0) {}
```
## 内置持久类型

默认情况下，以下基元类型是可持久的：

- 数字类型：

   - **`logic`** - 布尔值（真/假）
   - **`int`** - 整数值（必须符合 64 位有符号范围才能持久）
   - **`float`** - 浮点数

- 角色类型：

   - **`string`** - 文本值
   - **`char`** - 单个 UTF-8 字符
   - **`char32`** - 单个 UTF-32 字符

- 集装箱类型：

   - **`array`** - 如果元素类型是可持久的，则可持久
   - **`map`** - 如果键和值类型都是可持久的，则可持久
   - **`option`** - 如果包装类型是可持久的，则可持久
   - **`tuple`** - 如果所有元素类型都是可持久的，则可持久

## 自定义持久类型

您可以使用 `<persistable>` 创建自定义持久类型
带有类、结构和枚举的说明符。

类必须满足特定要求才能持久：

<!--versetest-->
<!-- 02 -->
```verse
player_class := enum<persistable>:
    Villager

player_profile_data := class<final><persistable>:
    Version:int = 1
    Class:player_class = player_class.Villager
    XP:int = 0
    Rank:int = 0
    CompletedQuestCount:int = 0
```
对持久类的要求：

- 必须具有 `<persistable>` 说明符
- 必须是 `<final>`（不允许有子类）
- 不能是 `<unique>` 
- 不能有超类（包括接口） 
- 不能是参数化的（通用） 
- 只能包含持久字段类型 
- 不能有变量成员（`var` 字段） 
- 字段初始化器必须是无效果的（不能使用 `<transacts>`、`<decides>` 等） 

结构对于简单的数据结构来说是理想的选择，这些数据结构之后不会改变。
出版物：

<!--versetest-->
<!-- 03 -->
```verse
coordinates := struct<persistable>:
    X:float = 0.0
    Y:float = 0.0
```
对持久结构的要求：

- 必须具有 `<persistable>` 说明符
- 不能是参数化的（通用） 
- 只能包含持久字段类型（请参阅下面的禁止字段类型） 
- 字段初始化器必须是无效果的（不能使用 `<transacts>`、`<decides>` 等）
- 岛屿发布后无法修改

枚举代表一组固定的命名值：

<!--versetest-->
<!-- 04 -->
```verse
day := enum<persistable>:
    Monday
    Tuesday
    Wednesday
    Thursday
    Friday
    Saturday
    Sunday
```
重要提示：

- `<closed>` 持久枚举在发布后无法更改为打开
- 只有 `<open>` 持久枚举可以在发布后添加新值

## 禁止的字段类型

持久类型对其字段类型有严格的限制
可以包含。以下类型**不能**用作字段
可持久的类或结构：

- 抽象和动态类型：

   - **`any`** - 无法持久化（太动态）
   - **`comparable`** - 抽象接口类型
   - **`type`** - 类型值无法持久

- 不可序列化类型：

   - **`rational`** - 精确有理数（不可持久）
   - **函数类型**（例如，`int -> int`） - 函数无法序列化
   - **`weak_map`** - 弱引用不可持久
   - **接口类型** - 抽象接口无法持久化

- 不可持久的用户类型

   - **非持久枚举** - 无法使用没有 `<persistable>` 说明符的枚举
   - **非持久类** - 无法使用没有 `<persistable>` 说明符的类
   - **非持久结构** - 无法使用没有 `<persistable>` 说明符的结构


## 示例

初始化玩家数据：

<!--versetest
player := class<unique><persistent><module_scoped_var_weak_map_key>{}
player_stats := struct<persistable>:
    Level:int = 1
    Experience:int = 0
    GamesPlayed:int = 0

var PlayerData : weak_map(player, player_stats) = map{}

GetOrCreatePlayerStats(Player : player) : player_stats =
    if (ExistingStats := PlayerData[Player]):
        ExistingStats
    else:
        NewStats := player_stats{}
        if (set PlayerData[Player] = NewStats):
            NewStats
        else:
            player_stats{}
<#
-->
<!-- 06 -->
```verse
# 定义持久的玩家统计数据结构
player_stats := struct<persistable>:
    Level:int = 1
    Experience:int = 0
    GamesPlayed:int = 0

# 全局持久存储
PlayerData : weak_map(player, player_stats) = map{}

# 初始化或检索玩家数据
GetOrCreatePlayerStats(Player : player) : player_stats =
    if (ExistingStats := PlayerData[Player]):
        ExistingStats
    else:
        NewStats := player_stats{}
        if (set PlayerData[Player] = NewStats):
            NewStats
        else:
            player_stats{}  # 回退
```
<!-- #> -->


## JSON 序列化

!!!注意“未发布的功能”
    JSON 序列化尚未发布，尚未公开。

Verse 为持久类型提供 JSON 序列化函数，
启用数据的手动序列化和反序列化。虽然
主要持久性机制使用 `weak_map(player, t)` 进行自动
玩家数据、JSON 序列化可用于调试、数据
迁移或与外部系统集成。

将持久值转换为 JSON 字符串：

<!--versetest
player := class<unique>{}
player_data := class<final><persistable>:
    Level:int = 1
    Score:int = 100
PersistenceModule := module{
    ToJson<public>(Data:player_data)<decides>:string = ""
}
-->
<!-- 08 -->
```verse
# 将持久数据序列化为 JSON
Data := player_data{Level := 5, Score := 250}
JsonString := PersistenceModule.ToJson[Data]
# 产生：{"$package_name":"/...", "$class_name":"player_data", "x_Level":5, "x_Score":250}
```
将 JSON 字符串反序列化为键入的值：

<!--versetest
player := class<unique>{}
player_data := class<final><persistable>:
    Level:int = 1
    Score:int = 100
PersistenceModule := module{
    FromJson<public>(JsonStr:string, T:type)<transacts><decides>:player_data =
        false?
        player_data{Level := 1, Score := 100}
}
-->
<!-- 09 -->
```verse
# 将 JSON 反序列化为键入的值
JsonString := ""
if (Restored := PersistenceModule.FromJson[JsonString, player_data]):
    # 恢复等级 = 10
    # 已恢复。分数 = 500
```
所有序列化的持久对象都包含元数据字段：
```json
{
  "$package_name": "/SolIdeDataSources/_Verse",
  "$class_name": "player_data",
  "x_Level": 5,
  "x_Score": 250
}
```
**元数据字段：**

- `$package_name` - 类型的包路径
- `$class_name` - 限定类/结构名称

**字段名称：**

- 当前格式中带有 `x_` 前缀
- 旧格式使用损坏的名称，例如 `i___verse_0x123_FieldName`

### 特定类型的序列化

**原语：**

<!--versetest
player := class<unique>{}
int_ref := class<final><persistable>:
    Value:int
PersistenceModule := module{
    ToJson<public>(Data:int_ref)<decides>:string = ""
}
-->
<!-- 11 -->
```verse
# 序列化为 JSON 数字
JsonString := PersistenceModule.ToJson[int_ref{Value := 42}]
# {“$package_name”：“...”，“$class_name”：“int_ref”，“x_Value”：42}
```
**可选类型：**

<!--versetest
player := class<unique>{}
optional_ref := class<final><persistable>:
    Value:?int
PersistenceModule := module{
    ToJson<public>(Data:optional_ref)<decides>:string = ""
}
-->
<!-- 12 -->
```verse
# 没有序列化为 false
PersistenceModule.ToJson[optional_ref{Value := false}]
# {...，“x_Value”：假}

# 一些序列化为带有空键的对象
PersistenceModule.ToJson[optional_ref{Value := option{42}}]
# {..., "x_Value":{"":42}}
```
**元组：**

<!--versetest
player := class<unique>{}
tuple_ref := class<final><persistable>:
    Pair:tuple(int, int)
empty_tuple_ref := class<final><persistable>:
    Empty:tuple()
PersistenceModule := module{
    ToJson<public>(Data:tuple_ref):string = ""
    ToJson<public>(Data:empty_tuple_ref):string = ""
}
-->
<!-- 13 -->
```verse
# 序列化为 JSON 存储
PersistenceModule.ToJson(tuple_ref{Pair := (4, 5)})
# {..., "x_Pair":[4,5]}

# 空元组
PersistenceModule.ToJson(empty_tuple_ref{Empty := ()})
# {..., "x_Empty":[]}
```
**数组：**
<!--versetest
player := class<unique>{}
array_ref := class<final><persistable>:
    Values:[]int
PersistenceModule := module{
    ToJson<public>(Data:array_ref)<decides>:string = ""
}
-->
<!-- 14 -->
```verse
PersistenceModule.ToJson[array_ref{Values := array{1, 2, 3}}]
# {..., "x_Values":[1,2,3]}
```
**映射：**

<!--versetest
player := class<unique>{}
map_ref := class<final><persistable>:
    Lookup:[string]int
PersistenceModule := module{
    ToJson<public>(Data:map_ref)<decides>:string = ""
}
-->
<!-- 15 -->
```verse
PersistenceModule.ToJson[map_ref{Lookup := map{"a" => 1, "b" => 2}}]
# {..., "x_Lookup":[{"k":{"":"a"},"v":{"":1}}, {"k":{"":"b"},"v":{"":2}}]}
```
**枚举：**

<!--versetest
player := class<unique>{}
day := enum<persistable>:
    Monday
    Tuesday
enum_ref := class<final><persistable>:
    Day:day
PersistenceModule := module{
    ToJson<public>(Data:enum_ref)<decides>:string = ""
}
-->
<!-- 16 -->
```verse
PersistenceModule.ToJson[enum_ref{Day := day.Monday}]
# {..., "x_Day":"日:: 星期一"}
```
### 默认值处理

反序列化时，缺失的字段会自动填充其默认值：

<!--versetest
player := class<unique>{}
versioned_data := class<final><persistable>:
    Version:int = 1
    NewField:int = 0
PersistenceModule := module{
    FromJson<public>(JsonStr:string, T:type)<transacts><decides>:versioned_data =
        false?
        versioned_data{Version := 1, NewField := 0}
}
-->
<!-- 17 -->
```verse
# 没有 NewField 的旧 JSON
OldJson := ""

# 使用NewField的默认值成功反序列化
if (Data := PersistenceModule.FromJson[OldJson, versioned_data]):
    Data.Version = 1
    Data.NewField = 0  # 使用默认值
```
这使得向前兼容的模式演化成为可能——新的领域
可以在不破坏旧保存数据的情况下添加默认值。

### 反序列化期间的块子句

从 JSON 反序列化时，块子句不会执行：

<!--versetest
player := class<unique>{}
logged_class := class<final><persistable>:
    Value:int
PersistenceModule := module{
    ToJson<public>(Data:logged_class):string = ""
    FromJson<public>(JsonStr:string, T:type)<transacts>:logged_class = logged_class{Value := 1}
}
-->
<!-- 18 -->
```verse
# 正常施工会触发区块
Instance1 := logged_class{Value := 1}

# 反序列化不会触发块
Json := PersistenceModule.ToJson(Instance1)
Instance2 := PersistenceModule.FromJson(Json, logged_class)  # 无打印
```
块子句仅在正常构造期间执行，而不是在
反序列化。这意味着块中的初始化逻辑将不会运行
对于加载的数据。

### 整数范围限制

Verse 可防止序列化期间的整数溢出。整数
超出安全序列化范围会导致运行时错误：

<!--versetest
player := class<unique>{}
int_ref := class<final><persistable>:
    Value:int
PersistenceModule := module{
    ToJson<public>(Data:int_ref)<decides>:string = ""
}
-->
<!-- 19 -->
```verse
# 安全范围整数工作正常
SafeData := int_ref{Value := 1000000000000000000}
PersistenceModule.ToJson[SafeData]  # 好的

# 非常大的整数可能会在序列化期间导致运行时错误
# 以防止无声精度损失
```
这可以防止可能发生的静默精度损失
大整数的浮点表示。


## 最佳实践

- **架构稳定性：** 仔细设计您的持久类型，如
它们在发布后不能轻易更改。考虑版本控制
未来更新的策略。

- **对简单数据使用结构：**对于不需要的数据
继承或复杂的行为，更喜欢持久结构
类。

- **处理丢失数据：** 始终检查玩家的数据是否存在
在访问它之前，并提供适当的默认值。

- **原子更新：** 更新持久数据时，创建新的
实例而不是尝试修改现有实例（Verse 使用
不可变的数据结构）。

- **考虑内存使用情况：** 为所有玩家加载持久数据
当他们加入时，请注意每个玩家存储的数据量。