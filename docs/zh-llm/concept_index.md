# 📚 概念索引

本索引提供 Verse 文档中关键概念、语言特性和重要术语的快速访问。每个条目链接到该概念被定义或详细解释的具体小节。

## 类型系统

### 基本类型
- **any** — 通用超类型：[基本类型 — Any](02_primitives.md#any)、[类型系统](11_types.md)
- **void** — 空类型：[基本类型 — Void](02_primitives.md#void)、[类型系统](11_types.md)
- **logic** — 布尔值：[基本类型 — 布尔值](02_primitives.md#booleans)、[类型系统](11_types.md)
- **int** — 整数：[概述](00_overview.md)、[基本类型 — 整数](02_primitives.md#integers)、[类型系统](11_types.md)
- **float** — 浮点数：[概述](00_overview.md)、[基本类型 — 浮点数](02_primitives.md#floats)、[类型系统](11_types.md)
- **rational** — 精确分数：[基本类型 — 有理数](02_primitives.md#rationals)、[运算符](04_operators.md)、[类型系统](11_types.md)
- **char** — UTF-8 字符：[基本类型 — 字符与字符串](02_primitives.md#characters-and-strings)、[类型系统](11_types.md)
- **char32** — UTF-32 字符：[基本类型 — 字符与字符串](02_primitives.md#characters-and-strings)、[类型系统](11_types.md)
- **string** — 文本值：[概述](00_overview.md)、[基本类型 — 字符与字符串](02_primitives.md#characters-and-strings)、[类型系统](11_types.md)

### 复合类型
- **array** — 有序集合：[概述](00_overview.md)、[容器 — 数组](03_containers.md#arrays)、[类型系统](11_types.md)
- **map** — 键值对：[容器 — 映射](03_containers.md#maps)、[类型系统](11_types.md)
- **tuple** — 固定大小集合：[容器 — 元组](03_containers.md#tuple)、[表达式](01_expressions.md)、[类型系统](11_types.md)
- **option** — 可空值：[概述](00_overview.md)、[容器 — 可选类型](03_containers.md#optionals)、[类型系统](11_types.md)
- **class** — 引用类型：[概述](00_overview.md)、[类 — 类](10_classes_interfaces.md#classes)、[类型系统](11_types.md)
- **struct** — 值类型：[结构体 — 结构体](09_structs_enums.md#structs)、[类型系统](11_types.md)
- **interface** — 合约：[类 — 接口](10_classes_interfaces.md#interfaces)、[类型系统](11_types.md)
- **enum** — 命名值：[概述](00_overview.md)、[枚举 — 枚举](09_structs_enums.md#enums)

### 类型特性
- **subtyping** — 类型关系：[类型系统 — 理解子类型](11_types.md#understanding-subtyping)
- **comparable** — 相等性测试：[类型系统](11_types.md)
- **parametric types** — 泛型：[类 — 参数化类](10_classes_interfaces.md#parametric-classes)、[类型系统](11_types.md)
- **type{}** — 类型表达式：[表达式](01_expressions.md)、[基本类型 — Type 类型](02_primitives.md#type-type)、[类型系统](11_types.md)
- **where clauses** — 类型约束：[概述](00_overview.md)、[函数](06_functions.md)、[类 — 高级类型约束](10_classes_interfaces.md#advanced-type-constraints)、[类型系统](11_types.md)

### 类型变型
- **covariance** — 协变：[类 — 协变](10_classes_interfaces.md#covariant)
- **contravariance** — 逆变：[类型系统](11_types.md)
- **invariance** — 不变：[类型系统](11_types.md)
- **bivariance** — 双变：[类型系统](11_types.md)

### 类型转换
- **casting** — 类型转换：[类型系统 — 类与接口转换](11_types.md#class-and-interface-casting)
- **dynamic casts** — 运行时类型检查：[类型系统 — 基于动态类型的转换](11_types.md#dynamic-type-based-casting)
- **fallible casts** — 可能失败的转换：[类型系统 — 可失败转换](11_types.md#fallible-casts)

### 类型谓词与元类型
- **subtype** — 运行时类型值：[类型系统 — subtype](11_types.md#subtype)
- **concrete_subtype** — 可实例化类型：[类型系统 — concrete_subtype](11_types.md#concrete_subtype)
- **castable_subtype** — 可转换关系：[类型系统 — castable_subtype](11_types.md#castable_subtype)、[类 — 使用 castable_subtype](10_classes_interfaces.md#using-castable_subtype)
- **classifiable_subset** — 类型集合追踪：[类型系统 — classifiable_subset](11_types.md#classifiable_subset)
- **classifiable_subset_var** — 可变类型集合：[类型系统 — classifiable_subset](11_types.md#classifiable_subset)
- **classifiable_subset_key** — 类型集合键：[类型系统 — classifiable_subset](11_types.md#classifiable_subset)

### 类型查询函数
- **GetCastableFinalSuperClass** — 从实例获取转换根：[类型系统 — GetCastableFinalSuperClass](11_types.md#getcastablefinalsuperclass)
- **GetCastableFinalSuperClassFromType** — 从类型获取转换根：[类型系统 — GetCastableFinalSuperClassFromType](11_types.md#getcastablefinalsuperclassfromtype)
- **MakeClassifiableSubset** — 创建不可变类型集合：[类型系统 — classifiable_subset](11_types.md#classifiable_subset)
- **MakeClassifiableSubsetVar** — 创建可变类型集合：[类型系统 — classifiable_subset](11_types.md#classifiable_subset)

## 效果

### 效果说明符
- **`<computes>`** — 纯计算：[概述](00_overview.md)、[效果](13_effects.md)、[可变性](05_mutability.md)
- **`<reads>`** — 观察状态：[概述](00_overview.md)、[效果](13_effects.md)、[可变性](05_mutability.md)
- **`<writes>`** — 修改状态：[效果](13_effects.md)、[可变性](05_mutability.md)
- **`<allocates>`** — 创建唯一值：[效果](13_effects.md)
- **`<transacts>`** — 完整堆访问：[概述](00_overview.md)、[类 — 类](10_classes_interfaces.md#classes)、[效果](13_effects.md)
- **`<decides>`** — 可失败：[概述](00_overview.md)、[函数](06_functions.md)、[失败](08_failure.md)、[效果](13_effects.md)
- **`<suspends>`** — 异步执行：[概述](00_overview.md)、[效果](13_effects.md)、[并发](14_concurrency.md)
- **`<converges>`** — 保证终止：[效果](13_effects.md)
- **`<diverges>`** — 可能不终止：[效果](13_effects.md)
- **`<predicts>`** — 客户端执行：[效果](13_effects.md)
- **`<dictates>`** — 仅服务端：[效果](13_effects.md)

## 控制流

### 基本控制
- **if/then/else** — 条件执行：[概述](00_overview.md)、[表达式](01_expressions.md)、[控制流](07_control.md)、[失败](08_failure.md)
- **case** — 模式匹配：[概述](00_overview.md)、[枚举 — 使用枚举](09_structs_enums.md#using-enums)、[控制流](07_control.md)
- **first** — 首个匹配迭代：[控制流](07_control.md)、[失败](08_failure.md)
- **for** — 迭代：[概述](00_overview.md)、[控制流](07_control.md)、[失败](08_failure.md)
- **loop** — 无限循环：[控制流](07_control.md)、[失败](08_failure.md)、[并发](14_concurrency.md)
- **block** — 语句序列：[控制流](07_control.md)、[失败](08_failure.md)、[类 — 用于初始化的块](10_classes_interfaces.md#blocks-for-initialization)、[并发](14_concurrency.md)
- **break** — 退出循环：[控制流](07_control.md)
- **continue** — 跳过迭代：[控制流](07_control.md)
- **defer** — 清理代码：[控制流](07_control.md)
- **return** — 退出函数：[函数](06_functions.md)

### 失败系统
- **failure** — 通过失败控制：[概述](00_overview.md)、[失败](08_failure.md)、[效果](13_effects.md)
- **failable expressions** — 可失败：[容器 — 可选类型](03_containers.md#optionals)、[函数](06_functions.md)、[失败](08_failure.md)
- **query operator (?)** — 测试值：[概述](00_overview.md)、[容器 — 可选类型](03_containers.md#optionals)、[运算符](04_operators.md)、[失败](08_failure.md)
- **speculative execution** — 失败时回滚：[概述](00_overview.md)、[失败](08_failure.md)

## 并发

### 结构化并发
- **sync** — 等待全部完成：[概述](00_overview.md)、[并发](14_concurrency.md)
- **race** — 先完成者获胜：[概述](00_overview.md)、[并发](14_concurrency.md)
- **rush** — 先成功者获胜：[并发](14_concurrency.md)
- **branch** — 所有成功者：[并发](14_concurrency.md)

### 非结构化并发
- **spawn** — 独立任务：[概述](00_overview.md)、[效果](13_effects.md)、[并发](14_concurrency.md)
- **task** — 并发执行：[并发](14_concurrency.md)
- **async expressions** — 耗时操作：[并发](14_concurrency.md)
- **cancellation** — 停止任务：[并发](14_concurrency.md)

### 计时函数
- **Sleep()** — 暂停执行：[并发](14_concurrency.md)
- **Await()** — 等待任务完成：[并发](14_concurrency.md)
- **NextTick()** — 推迟到下一更新：[并发](14_concurrency.md)
- **GetSecondsSinceEpoch** — 获取当前时间：[并发](14_concurrency.md)

## 实时变量

### 响应式编程
- **live** — 响应式变量：[实时变量](15_live_variables.md)
- **await** — 挂起直至条件满足：[实时变量 — await 表达式](15_live_variables.md#the-await-expression)
- **upon** — 一次性响应行为：[实时变量 — upon 表达式](15_live_variables.md#the-upon-expression)
- **when** — 持续响应行为：[实时变量 — when 表达式](15_live_variables.md#the-when-expression)
- **batch** — 分组变量更新：[实时变量 — batch 表达式](15_live_variables.md#the-batch-expression)

### 实时变量特性
- **input-output variables** — 双向同步：[实时变量 — 输入输出变量](15_live_variables.md#input-output-variables)
- **live expressions** — 动态关系：[实时变量 — 实时表达式](15_live_variables.md#live-expressions)

## 可变性

### 可变性控制
- **var** — 可变变量：[可变性](05_mutability.md)、[效果](13_effects.md)
- **set** — 赋值：[概述](00_overview.md)、[可变性](05_mutability.md)
- **immutability** — 默认行为：[概述](00_overview.md)、[效果](13_effects.md)、[可变性](05_mutability.md)
- **deep copying** — 结构体语义：[可变性](05_mutability.md)、[结构体 — 结构体](09_structs_enums.md#structs)
- **reference semantics** — 类行为：[类 — 类](10_classes_interfaces.md#classes)、[可变性](05_mutability.md)
- **value semantics** — 结构体行为：[结构体 — 结构体](09_structs_enums.md#structs)、[可变性](05_mutability.md)

## 类与类型说明符

### 结构说明符
- **`<unique>`** — 标识相等性：[概述](00_overview.md)、[类 — 唯一](10_classes_interfaces.md#unique)、[可变性](05_mutability.md)、[访问说明符](12_access.md)
- **`<abstract>`** — 不可实例化：[类 — 抽象](10_classes_interfaces.md#abstract)、[访问说明符](12_access.md)
- **`<concrete>`** — 可实例化：[类 — 具体](10_classes_interfaces.md#concrete)、[访问说明符](12_access.md)
- **`<final>`** — 不可继承：[类 — 终态](10_classes_interfaces.md#final)、[可持久化类型](17_persistable.md)、[访问说明符](12_access.md)
- **`<final_super>`** — 终端继承：[类 — 终态](10_classes_interfaces.md#final)、[访问说明符](12_access.md)
- **`<final_super_base>`** — 继承根：[类 — 终态](10_classes_interfaces.md#final)
- **`<castable>`** — 运行时类型检查：[类 — 可转换](10_classes_interfaces.md#castable)、[访问说明符](12_access.md)、[代码演化](18_evolution.md)
- **`<persistable>`** — 可保存数据：[概述](00_overview.md)、[类 — 可持久化](10_classes_interfaces.md#persistable)、[结构体 — 可持久化结构体](09_structs_enums.md#persistable-structs)、[可持久化类型](17_persistable.md)
- **`<constructor>`** — 工厂方法：[类 — 构造函数](10_classes_interfaces.md#constructor-functions)

### 枚举说明符
- **`<open>`** — 可扩展枚举：[枚举 — 开放枚举与封闭枚举](09_structs_enums.md#open-vs-closed-enums)、[访问说明符](12_access.md)、[代码演化](18_evolution.md)
- **`<closed>`** — 固定枚举：[枚举 — 开放枚举与封闭枚举](09_structs_enums.md#open-vs-closed-enums)、[访问说明符](12_access.md)、[代码演化](18_evolution.md)

## 访问控制

### 可见性说明符
- **`<public>`** — 通用访问：[概述](00_overview.md)、[类 — 访问说明符](10_classes_interfaces.md#access-specifiers)、[模块与路径](16_modules.md)、[访问说明符](12_access.md)
- **`<private>`** — 仅类/模块内：[类 — 访问说明符](10_classes_interfaces.md#access-specifiers)、[模块与路径](16_modules.md)、[访问说明符](12_access.md)
- **`<protected>`** — 子类访问：[类 — 访问说明符](10_classes_interfaces.md#access-specifiers)、[模块与路径](16_modules.md)、[访问说明符](12_access.md)
- **`<internal>`** — 模块内访问：[模块与路径](16_modules.md)、[访问说明符](12_access.md)
- **`<scoped>`** — 基于路径的访问：[访问说明符](12_access.md)

### 方法说明符
- **`<override>`** — 替换父类方法：[类 — 方法覆盖](10_classes_interfaces.md#method-overriding)、[访问说明符](12_access.md)
- **`<native>`** — 以 C++ 实现：[访问说明符](12_access.md)

## 运算符

### 算术
- **+, -, \*, /, %** — 数学运算：[基本类型 — 数学函数](02_primitives.md#mathematical-functions)、[运算符](04_operators.md)
- **+=, -=, \*=, /=** — 复合赋值：[运算符](04_operators.md)

### 比较
- **<, <=, >, >=** — 排序：[运算符](04_operators.md)
- **=, <>** — 相等/不等：[运算符](04_operators.md)、[类型系统](11_types.md)

### 逻辑
- **and** — 逻辑与：[运算符](04_operators.md)、[失败](08_failure.md)
- **or** — 逻辑或：[运算符](04_operators.md)、[失败](08_failure.md)
- **not** — 逻辑非：[运算符](04_operators.md)、[失败](08_failure.md)

### 访问
- **.** — 成员访问：[运算符](04_operators.md)、[表达式](01_expressions.md)
- **[]** — 索引：[容器 — 数组](03_containers.md#arrays)、[运算符](04_operators.md)、[表达式](01_expressions.md)
- **()** — 函数调用：[运算符](04_operators.md)、[表达式](01_expressions.md)
- **{}** — 对象构造：[运算符](04_operators.md)、[表达式](01_expressions.md)

### 特殊
- **:=** — 初始化：[运算符](04_operators.md)、[表达式](01_expressions.md)
- **..** — 范围运算符：[运算符](04_operators.md)、[表达式](01_expressions.md)
- **?** — 查询运算符：[概述](00_overview.md)、[容器 — 可选类型](03_containers.md#optionals)、[运算符](04_operators.md)、[失败](08_failure.md)

## 函数

### 函数特性
- **parameters** — 函数输入：[函数](06_functions.md)
- **named arguments** — 显式参数名：[函数](06_functions.md)
- **return values** — 函数输出：[函数](06_functions.md)
- **function types** — 函数签名：[函数](06_functions.md)、[类型系统](11_types.md)
- **overloading** — 多重定义：[函数](06_functions.md)、[运算符](04_operators.md)
- **lambdas** — 匿名函数：[函数](06_functions.md)、[表达式](01_expressions.md)
- **nested functions** — 局部函数定义：[函数](06_functions.md)
- **higher-order functions** — 函数作为值：[概述](00_overview.md)、[函数](06_functions.md)

## 模块与组织

### 模块系统
- **module** — 代码组织：[模块与路径](16_modules.md)
- **using** — 导入语句：[概述](00_overview.md)、[模块与路径](16_modules.md)
- **module paths** — 层级化名称：[模块与路径](16_modules.md)
- **qualified names** — 完整路径：[模块与路径](16_modules.md)
- **qualified access** — 显式路径：[模块与路径](16_modules.md)
- **nested modules** — 模块层次结构：[模块与路径](16_modules.md)

## 持久化

### 保存系统
- **weak_map(player, t)** — 玩家数据：[容器 — 弱映射](03_containers.md#weak-maps)、[可持久化类型](17_persistable.md)
- **weak_map(session, t)** — 会话数据：[容器 — 弱映射](03_containers.md#weak-maps)、[可持久化类型](17_persistable.md)
- **persistable types** — 可保存数据：[概述](00_overview.md)、[类 — 可持久化](10_classes_interfaces.md#persistable)、[结构体 — 可持久化结构体](09_structs_enums.md#persistable-structs)、[可持久化类型](17_persistable.md)
- **module-scoped variables** — 持久存储：[模块与路径](16_modules.md)、[可持久化类型](17_persistable.md)

## 演化与兼容性

### 版本管理
- **backward compatibility** — 保留 API：[概述](00_overview.md)、[效果](13_effects.md)、[代码演化](18_evolution.md)
- **versioning** — 变更追踪：[代码演化](18_evolution.md)
- **deprecation** — 淘汰特性：[代码演化](18_evolution.md)
- **publication** — 公开代码：[模块与路径](16_modules.md)、[访问说明符](12_access.md)、[代码演化](18_evolution.md)
- **breaking changes** — 不兼容更新：[代码演化](18_evolution.md)
- **schema evolution** — 数据结构变更：[类 — 类](10_classes_interfaces.md#classes)、[代码演化](18_evolution.md)

### 注解
- **@deprecated** — 标记为已弃用：[代码演化](18_evolution.md)
- **@experimental** — 标记为实验性：[代码演化](18_evolution.md)
- **@available** — 版本可用性：[代码演化](18_evolution.md)

## 内置函数

### 数学函数
- **Abs()** — 绝对值：[基本类型 — 数学函数](02_primitives.md#mathematical-functions)
- **Floor()** — 向下取整：[基本类型 — 数学函数](02_primitives.md#mathematical-functions)
- **Ceil()** — 向上取整：[基本类型 — 数学函数](02_primitives.md#mathematical-functions)
- **Round()** — 四舍五入：[基本类型 — 数学函数](02_primitives.md#mathematical-functions)
- **Sqrt()** — 平方根：[基本类型 — 数学函数](02_primitives.md#mathematical-functions)
- **Min()** — 最小值：[基本类型 — 数学函数](02_primitives.md#mathematical-functions)
- **Max()** — 最大值：[基本类型 — 数学函数](02_primitives.md#mathematical-functions)

### 工具函数
- **Print()** — 输出文本：[概述](00_overview.md)、[效果](13_effects.md)
- **ToString()** — 转换为字符串：[基本类型 — ToString()](02_primitives.md#tostring)
- **GetSession()** — 当前会话：[模块与路径](16_modules.md)

### 数组方法
- **Find()** — 查找元素索引：[容器 — 数组方法](03_containers.md#array-methods)
- **Remove()** — 按索引移除：[容器 — 数组方法](03_containers.md#array-methods)
- **RemoveFirstElement()** — 移除首个匹配项：[容器 — 数组方法](03_containers.md#array-methods)
- **RemoveAllElements()** — 移除所有匹配项：[容器 — 数组方法](03_containers.md#array-methods)
- **ReplaceElement()** — 按索引替换：[容器 — 数组方法](03_containers.md#array-methods)
- **ReplaceFirstElement()** — 替换首个匹配项：[容器 — 数组方法](03_containers.md#array-methods)
- **ReplaceAllElements()** — 替换所有匹配项：[容器 — 数组方法](03_containers.md#array-methods)
- **ReplaceAll()** — 基于模式的替换：[容器 — 数组方法](03_containers.md#array-methods)

## 语法元素

### 字面量
- **integer literals** — 整数值：[表达式](01_expressions.md)
- **float literals** — 小数值：[表达式](01_expressions.md)
- **string literals** — 文本值：[表达式](01_expressions.md)
- **character literals** — 单个字符：[表达式](01_expressions.md)
- **boolean literals** — true/false：[表达式](01_expressions.md)

### 特殊值
- **false** — 失败值、空可选类型：[基本类型 — 布尔值](02_primitives.md#booleans)、[容器 — 可选类型](03_containers.md#optionals)、[失败](08_failure.md)
- **true** — 成功值：[基本类型 — 布尔值](02_primitives.md#booleans)
- **NaN** — 非数值：[基本类型 — 浮点数](02_primitives.md#floats)
- **Inf** — 无穷大：[基本类型 — 浮点数](02_primitives.md#floats)

### 语言构造
- **comments** — 代码文档：[概述](00_overview.md)
- **identifiers** — 名称：[表达式](01_expressions.md)

## 特殊概念

### 语言特性
- **archetype expression** — 原型模式：[类 — 对象构造](10_classes_interfaces.md#object-construction)、[表达式](01_expressions.md)
- **string interpolation** — 嵌入表达式：[基本类型 — 字符与字符串](02_primitives.md#characters-and-strings)
- **pattern matching** — 结构匹配：[概述](00_overview.md)、[枚举 — 使用枚举](09_structs_enums.md#using-enums)、[控制流](07_control.md)
- **inheritance** — 类层次结构：[类 — 继承](10_classes_interfaces.md#inheritance)、[类型系统](11_types.md)、[访问说明符](12_access.md)
- **polymorphism** — 多种形态：[类 — 方法覆盖](10_classes_interfaces.md#method-overriding)、[类型系统](11_types.md)
- **transactional semantics** — 回滚行为：[概述](00_overview.md)、[失败](08_failure.md)、[效果](13_effects.md)
- **option{}** 构造函数：[概述](00_overview.md)、[容器 — 可选类型](03_containers.md#optionals)
- **array{}** 构造函数：[概述](00_overview.md)、[容器 — 数组](03_containers.md#arrays)
- **map{}** 构造函数：[容器 — 映射](03_containers.md#maps)

---

*注：本索引涵盖 Verse 文档中的所有主要概念。每个条目直接链接到该概念被定义或详细解释的具体小节。使用浏览器的查找功能（Ctrl+F 或 Cmd+F）可以快速定位特定术语。*
