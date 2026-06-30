# 可持久化类型

可持久化类型（persistable types）允许你存储超出当前游戏会话的数据。这对于保存玩家进度、偏好设置以及应在多个游戏会话间保持的其他游戏状态至关重要。

可持久化数据通过模块作用域的 `weak_map(player, t)` 变量来存储，其中 `t` 是任意的可持久化类型。当玩家加入游戏时，其先前保存的数据会自动加载到所有类型为 `weak_map(player, t)` 的模块作用域变量中。

<!--NoCompile-->
<!-- 01 -->
```verse
using { /Fortnite.com/Devices }
using { /UnrealEngine.com/Temporary/Diagnostics }
using { /Verse.org/Simulation }

# Global persistable variable storing player data
MySavedPlayerData : weak_map(player, int) = map{}

# Initialize data for a player if not already present
InitializePlayerData(Player : player) : void =
    if (not MySavedPlayerData[Player]):
        if (set MySavedPlayerData[Player] = 0) {}
```

## 内置可持久化类型

以下基本类型默认可持久化：

- 数值类型：

   - **`logic`** - 布尔值（true/false）
   - **`int`** - 整数值（持久化时必须在 64 位有符号范围内）
   - **`float`** - 浮点数

- 字符类型：

   - **`string`** - 文本值
   - **`char`** - 单个 UTF-8 字符
   - **`char32`** - 单个 UTF-32 字符

- 容器类型：

   - **`array`** - 若元素类型可持久化，则可持久化
   - **`map`** - 若键和值类型均可持久化，则可持久化
   - **`option`** - 若包装的类型可持久化，则可持久化
   - **`tuple`** - 若所有元素类型均可持久化，则可持久化

## 自定义可持久化类型

你可以使用 `<persistable>` 说明符为类、结构体和枚举创建自定义的可持久化类型。

类必须满足特定要求才能成为可持久化：

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

可持久化类的要求：

- 必须具有 `<persistable>` 说明符
- 必须是 `<final>`（不允许有子类）
- 不能是 `<unique>`
- 不能有超类（包括接口）
- 不能是参数化（泛型）类型
- 只能包含可持久化的字段类型
- 不能有可变成员（`var` 字段）
- 字段初始化器必须无效果（不能使用 `<transacts>`、`<decides>` 等）

结构体适用于发布后不会更改的简单数据结构：

<!--versetest-->
<!-- 03 -->
```verse
coordinates := struct<persistable>:
    X:float = 0.0
    Y:float = 0.0
```

可持久化结构体的要求：

- 必须具有 `<persistable>` 说明符
- 不能是参数化（泛型）类型
- 只能包含可持久化的字段类型（参见下面的禁止字段类型）
- 字段初始化器必须无效果（不能使用 `<transacts>`、`<decides>` 等）
- 岛屿发布后不可修改

枚举表示一组固定的命名值：

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

重要说明：

- `<closed>` 可持久化枚举在发布后不能更改为 open
- 只有 `<open>` 可持久化枚举可以在发布后添加新值

## 禁止的字段类型

可持久化类型对其可包含的字段类型有严格限制。以下类型**不能**用作可持久化类或结构体的字段：

- 抽象和动态类型：

   - **`any`** - 无法持久化（过于动态）
   - **`comparable`** - 抽象接口类型
   - **`type`** - 类型值无法持久化

- 不可序列化类型：

   - **`rational`** - 精确有理数（不可持久化）
   - **函数类型**（例如 `int -> int`）- 函数无法序列化
   - **`weak_map`** - 弱引用不可持久化
   - **接口类型** - 抽象接口无法持久化

- 不可持久化的用户类型

   - **不可持久化枚举** - 没有 `<persistable>` 说明符的枚举无法使用
   - **不可持久化类** - 没有 `<persistable>` 说明符的类无法使用
   - **不可持久化结构体** - 没有 `<persistable>` 说明符的结构体无法使用


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
# Define a persistable player stats structure
player_stats := struct<persistable>:
    Level:int = 1
    Experience:int = 0
    GamesPlayed:int = 0

# Global persistent storage
PlayerData : weak_map(player, player_stats) = map{}

# Initialize or retrieve player data
GetOrCreatePlayerStats(Player : player) : player_stats =
    if (ExistingStats := PlayerData[Player]):
        ExistingStats
    else:
        NewStats := player_stats{}
        if (set PlayerData[Player] = NewStats):
            NewStats
        else:
            player_stats{}  # Fallback
```
<!-- #> -->


## JSON 序列化

!!! note "未发布的功能"
    JSON 序列化尚未发布，目前不公开可用。

Verse 提供了针对可持久化类型的 JSON 序列化函数，支持手动序列化和反序列化数据。虽然主要的持久化机制使用 `weak_map(player, t)` 进行自动玩家数据处理，但 JSON 序列化可用于调试、数据迁移或与外部系统集成。

将可持久化值转换为 JSON 字符串：

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
# Serialize persistable data to JSON
Data := player_data{Level := 5, Score := 250}
JsonString := PersistenceModule.ToJson[Data]
# Produces: {"$package_name":"/...", "$class_name":"player_data", "x_Level":5, "x_Score":250}
```

将 JSON 字符串反序列化为类型化值：

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
# Deserialize JSON to typed value
JsonString := ""
if (Restored := PersistenceModule.FromJson[JsonString, player_data]):
    # Restored.Level = 10
    # Restored.Score = 500
```

所有序列化的可持久化对象包含元数据字段：

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
- `$class_name` - 限定类/结构体名称

**字段名称：**

- 当前格式以 `x_` 为前缀
- 旧格式使用混乱的名称，如 `i___verse_0x123_FieldName`

### 类型特定序列化

**基本类型：**

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
# Serialized as JSON number
JsonString := PersistenceModule.ToJson[int_ref{Value := 42}]
# {"$package_name":"...", "$class_name":"int_ref", "x_Value":42}
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
# None serialized as false
PersistenceModule.ToJson[optional_ref{Value := false}]
# {..., "x_Value":false}

# Some serialized as object with empty key
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
# Serialized as JSON array
PersistenceModule.ToJson(tuple_ref{Pair := (4, 5)})
# {..., "x_Pair":[4,5]}

# Empty tuple
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
# {..., "x_Day":"day::Monday"}
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
# Old JSON without NewField
OldJson := ""

# Deserializes successfully with default for NewField
if (Data := PersistenceModule.FromJson[OldJson, versioned_data]):
    Data.Version = 1
    Data.NewField = 0  # Uses default value
```

这实现了前向兼容的模式演变（schema evolution）——带有默认值的新字段可以在不破坏旧保存数据的情况下添加。

### 反序列化期间的块子句

从 JSON 反序列化时，块子句（block clauses）不会执行：

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
# Normal construction triggers block
Instance1 := logged_class{Value := 1}

# Deserialization does NOT trigger block
Json := PersistenceModule.ToJson(Instance1)
Instance2 := PersistenceModule.FromJson(Json, logged_class)  # No print
```

块子句仅在正常构造期间执行，反序列化期间不会执行。这意味着加载数据时，块中的初始化逻辑不会运行。

### 整数范围限制

Verse 在序列化期间防止整数溢出。超出安全序列化范围的整数会导致运行时错误：

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
# Safe range integers work fine
SafeData := int_ref{Value := 1000000000000000000}
PersistenceModule.ToJson[SafeData]  # OK

# Very large integers may cause runtime errors during serialization
# to prevent silent precision loss
```

这可以防止在大整数的浮点数表示中可能发生的静默精度丢失。


## 最佳实践

- **模式稳定性：** 仔细设计你的可持久化类型，因为它们在发布后不易更改。考虑为后续更新制定版本管理策略。

- **对简单数据使用结构体：** 对于不需要继承或复杂行为的数据，优先使用可持久化结构体而不是类。

- **处理缺失数据：** 在访问玩家数据之前，始终检查数据是否存在，并提供适当的默认值。

- **原子更新：** 更新持久数据时，创建新实例而不是试图修改现有实例（Verse 使用不可变数据结构）。

- **注意内存使用：** 持久化数据会在所有玩家加入时加载，因此要注意每个玩家存储的数据量。