# 📚 概念索引

通过此索引，可以快速访问 Verse 文档中的关键概念、语言功能和重要术语。每个条目都链接到详细定义或解释概念的特定小节。

## 类型系统

### 原始类型
- **任何** - 通用超类型：[基元 - 任何](02_primitives.md#any)，[类型系统](11_types.md)
- **void** - 空类型：[基元 - Void](02_primitives.md#void)，[类型系统](11_types.md)
- **逻辑** - 布尔值：[基元 - 布尔值](02_primitives.md#booleans)，[类型系统](11_types.md)
- **int** - 整数：[概述](00_overview.md)、[基元 - 整数](02_primitives.md#integers)、[类型系统](11_types.md)
- **float** - 浮点：[概述](00_overview.md)、[基元 - 浮点](02_primitives.md#floats)、[类型系统](11_types.md)
- **有理数** - 精确分数：[基元 - 有理数](02_primitives.md#rationals)、[运算符](04_operators.md)、[类型系统](11_types.md)
- **char** - UTF-8 字符：[基元 - 字符和字符串](02_primitives.md#characters-and-strings)，[类型系统](11_types.md)
- **char32** - UTF-32 字符：[基元 - 字符和字符串](02_primitives.md#characters-and-strings)、[类型系统](11_types.md)
- **字符串** - 文本值：[概述](00_overview.md)、[基元 - 字符和字符串](02_primitives.md#characters-and-strings)、[类型系统](11_types.md)

### 复合类型
- **数组** - 有序集合：[概述](00_overview.md)、[容器 - 数组](03_containers.md#arrays)、[类型系统](11_types.md)
- **映射** - 键值对：[容器 - 映射](03_containers.md#maps)、[类型系统](11_types.md)
- **元组** - 固定大小集合：[容器 - 元组](03_containers.md#tuple)、[表达式](01_expressions.md)、[类型系统](11_types.md)
- **选项** - 可为 null 的值：[概述](00_overview.md)、[容器 - 可选](03_containers.md#optionals)、[类型系统](11_types.md)
- **类** - 引用类型：[概述](00_overview.md)、[类 - 类](10_classes_interfaces.md#classes)、[类型系统](11_types.md)
- **结构** - 值类型：[结构 - 结构](09_structs_enums.md#structs)、[类型系统](11_types.md)
- **接口** - 合约：[类 - 接口](10_classes_interfaces.md#interfaces)，[类型系统](11_types.md)
- **枚举** - 命名值：[概述](00_overview.md)，[枚举 - 枚举](09_structs_enums.md#enums)

### 类型特征
- **子类型** - 类型关系：[类型系统 - 了解子类型](11_types.md#understanding-subtyping)
- **可比较** - 相等性测试：[类型系统](11_types.md)
- **参数类型** - 泛型：[类 - 参数类](10_classes_interfaces.md#parametric-classes)、[类型系统](11_types.md)
- **类型{}** - 类型表达式：[表达式](01_expressions.md)、[基元 - 类型 type](02_primitives.md#type-type)、[类型系统](11_types.md)
- **where 子句** - 类型约束：[概述](00_overview.md)、[函数](06_functions.md)、[类 - 高级类型约束](10_classes_interfaces.md#advanced-type-constraints)、[类型系统](11_types.md)

### 类型差异
- **协变** - 类型兼容性：[类 - 协变](10_classes_interfaces.md#covariant)
- **逆变** - 反向兼容性：[类型系统](11_types.md)
- **不变性** - 精确类型匹配：[类型系统](11_types.md)
- **双变量** - 两个方向：[类型系统](11_types.md)

### 类型转换
- **强制转换** - 类型转换：[类型系统 - 类和接口强制转换](11_types.md#class-and-interface-casting)
- **动态强制转换** - 运行时类型检查：[类型系统 - 基于动态类型的强制转换](11_types.md#dynamic-type-based-casting)
- **可失败强制转换** - 可能会失败的强制转换：[类型系统 - 可失败强制转换](11_types.md#fallible-casts)

### 类型谓词和元类型
- **子类型** - 运行时类型值：[类型系统 - 子类型](11_types.md#subtype)
- **concrete_subtype** - 可实例化类型：[类型系统 -crete_subtype](11_types.md#concrete_subtype)
- **castable_subtype** - 可转换关系：[类型系统 -castable_subtype](11_types.md#castable_subtype)，[类 - 使用castable_subtype](10_classes_interfaces.md#using-castable_subtype)
- **可分类子集** - 类型集跟踪：[类型系统 - 可分类子集](11_types.md#classifiable_subset)
- **classABLE_subset_var** - 可变类型集：[类型系统 - classABLE_subset](11_types.md#classifiable_subset)
- **classific_subset_key** - 键入设置键：[类型系统 - classABLE_subset](11_types.md#classifiable_subset)

### 类型查询函数
- **GetCastableFinalSuperClass** - 从实例获取演员根：[类型系统 - GetCastableFinalSuperClass](11_types.md#getcastablefinalsuperclass)
- **GetCastableFinalSuperClassFromType** - 从类型获取转换根：[类型系统 - GetCastableFinalSuperClassFromType](11_types.md#getcastablefinalsuperclassfromtype)
- **MakeClassificSubset** - 创建不可变类型集：[类型系统 - classABLE_subset](11_types.md#classifiable_subset)
- **MakeClassABLESubsetVar** - 创建可变类型集：[类型系统 - classABLE_subset](11_types.md#classifiable_subset)

## 效果

### 效果说明符
- **`<computes>`** - 纯计算：[概述](00_overview.md)、[效果](13_effects.md)、[可变性](05_mutability.md)
- **`<reads>`** - 观察状态：[概述](00_overview.md)、[效果](13_effects.md)、[可变性](05_mutability.md)
- **`<writes>`** - 修改状态：[效果](13_effects.md)，[可变性](05_mutability.md)
- **`<allocates>`** - 创建唯一值：[效果](13_effects.md)
- **`<transacts>`** - 完整堆访问：[概述](00_overview.md)、[类 - 类](10_classes_interfaces.md#classes)、[效果](13_effects.md)
- **`<decides>`** - 可能会失败：[概述](00_overview.md)、[功能](06_functions.md)、[失败](08_failure.md)、[效果](13_effects.md)
- **`<suspends>`** - 异步执行：[概述](00_overview.md)、[效果](13_effects.md)、[并发](14_concurrency.md)
- **`<converges>`** - 保证终止：[效果](13_effects.md)
- **`<diverges>`** - 可能不会终止：[效果](13_effects.md)
- **`<predicts>`** - 客户端执行：[效果](13_effects.md)
- **`<dictates>`** - 仅服务器：[效果](13_effects.md)

## 控制流程

### 基本控制
- **if/then/else** - 条件执行：[概述](00_overview.md)、[表达式](01_expressions.md)、[控制流程](07_control.md)、[失败](08_failure.md)
- **案例** - 模式匹配：[概述](00_overview.md)、[枚举 - 使用枚举](09_structs_enums.md#using-enums)、[控制流](07_control.md)
- **第一个** - 第一个匹配迭代：[控制流](07_control.md)，[失败](08_failure.md)
- **针对** - 迭代：[概述](00_overview.md)、[控制流程](07_control.md)、[失败](08_failure.md)
- **循环** - 无限循环：[控制流](07_control.md)、[失败](08_failure.md)、[并发](14_concurrency.md)
- **块** - 语句序列：[控制流](07_control.md)、[失败](08_failure.md)、[类 - 初始化块](10_classes_interfaces.md#blocks-for-initialization)、[并发](14_concurrency.md)
- **break** - 退出循环：[控制流](07_control.md)
- **继续** - 跳过迭代：[控制流](07_control.md)
- **延迟** - 清理代码：[控制流](07_control.md)
- **返回** - 退出函数：[函数](06_functions.md)

### 失败
- **失败** - 通过失败进行控制：[概述](00_overview.md)、[失败](08_failure.md)、[效果](13_effects.md)
- **可失败表达式** - 可能会失败：[容器 - 可选](03_containers.md#optionals)、[函数](06_functions.md)、[失败](08_failure.md)
- **查询运算符 (?)** - 测试值：[概述](00_overview.md)、[容器 - 可选](03_containers.md#optionals)、[运算符](04_operators.md)、[失败](08_failure.md)
- **推测执行** - 失败时回滚：[概述](00_overview.md)，[失败](08_failure.md)

## 并发

### 结构化并发
- **同步** - 等待全部：[概述](00_overview.md)，[并发](14_concurrency.md)
- **竞赛** - 第一个完成：[概述](00_overview.md)，[并发](14_concurrency.md)
- **冲** - 第一个成功：[并发](14_concurrency.md)
- **分支** - 所有成功：[并发](14_concurrency.md)

### 非结构化并发
- **生成** - 独立任务：[概述](00_overview.md)、[效果](13_effects.md)、[并发](14_concurrency.md)
- **任务** - 并发执行：[并发](14_concurrency.md)
- **异步表达式** - 耗时操作：[并发](14_concurrency.md)
- **取消** - 停止任务：[并发](14_concurrency.md)

### 计时函数
- **Sleep()** - 暂停执行：[并发](14_concurrency.md)
- **Await()** - 挂起以完成任务：[并发](14_concurrency.md)
- **NextTick()** - 推迟到下一次更新：[并发](14_concurrency.md)
- **GetSecondsSinceEpoch** - 获取当前时间：[并发](14_concurrency.md)

## 实时变量

### 反应式编程
- **实时** - 反应变量：[实时变量](15_live_variables.md)
- **等待** - 挂起直到条件：[实时变量 - 等待表达式](15_live_variables.md#the-await-expression)
- **upon** - 一次性反应行为：[实时变量 - on 表达式](15_live_variables.md#the-upon-expression)
- **when** - 连续反应行为：[实时变量 - when 表达式](15_live_variables.md#the-when-expression)
- **批量** - 组变量更新：[实时变量 - 批量表达式](15_live_variables.md#the-batch-expression)

### 实时变量功能
- **输入输出变量** - 双向同步：[实时变量 - 输入输出变量](15_live_variables.md#input-output-variables)
- **实时表达式** - 动态关系：[实时变量 - 实时表达式](15_live_variables.md#live-expressions)

## 可变性

### 突变控制
- **var** - 可变变量：[可变性](05_mutability.md)，[效果](13_effects.md)
- **设置** - 分配：[概述](00_overview.md)，[可变性](05_mutability.md)
- **不变性** - 默认行为：[概述](00_overview.md)、[效果](13_effects.md)、[可变性](05_mutability.md)
- **深度复制** - 结构语义：[可变性](05_mutability.md)，[结构 - 结构](09_structs_enums.md#structs)
- **参考语义** - 类行为：[类 - 类](10_classes_interfaces.md#classes)，[可变性](05_mutability.md)
- **值语义** - 结构行为：[结构 - 结构](09_structs_enums.md#structs)，[可变性](05_mutability.md)

## 类和类型说明符

### 结构说明符
- **`<unique>`** - 身份相等：[概述](00_overview.md)、[类 - 唯一](10_classes_interfaces.md#unique)、[可变性](05_mutability.md)、[访问说明符](12_access.md)
- **`<abstract>`** - 无法实例化：[类 - Abstract](10_classes_interfaces.md#abstract)、[访问说明符](12_access.md)
- **`<concrete>`** - 可以实例化：[类 - 具体](10_classes_interfaces.md#concrete)，[访问说明符](12_access.md)
- **`<final>`** - 无法继承：[类 - Final](10_classes_interfaces.md#final)、[可持久化类型](17_persistable.md)、[访问说明符](12_access.md)
- **`<final_super>`** - 终端继承：[类 - Final](10_classes_interfaces.md#final)，[访问说明符](12_access.md)
- **`<final_super_base>`** - 继承根：[类 - Final](10_classes_interfaces.md#final)
- **`<castable>`** - 运行时类型检查：[类 - 可转换](10_classes_interfaces.md#castable)、[访问说明符](12_access.md)、[代码演化](18_evolution.md)
- **`<persistable>`** - 可保存数据：[概述](00_overview.md)、[类 - 可持久](10_classes_interfaces.md#persistable)、[结构 - 可持久结构](09_structs_enums.md#persistable-structs)、[可持久类型](17_persistable.md)
- **`<constructor>`** - 工厂方法：[类 - 构造函数](10_classes_interfaces.md#constructor-functions)

### 枚举说明符
- **`<open>`** - 可扩展枚举：[枚举 - 开放式与封闭式枚举](09_structs_enums.md#open-vs-closed-enums)、[访问说明符](12_access.md)、[代码演变](18_evolution.md)
- **`<closed>`** - 固定枚举：[枚举 - 开放式与封闭式枚举](09_structs_enums.md#open-vs-closed-enums)、[访问说明符](12_access.md)、[代码演变](18_evolution.md)

## 访问控制

### 可见性说明符
- **`<public>`** - 通用访问：[概述](00_overview.md)、[类 - 访问说明符](10_classes_interfaces.md#access-specifiers)、[模块和路径](16_modules.md)、[访问说明符](12_access.md)
- **`<private>`** - 仅类/模块：[类 - 访问说明符](10_classes_interfaces.md#access-specifiers)、[模块和路径](16_modules.md)、[访问说明符](12_access.md)
- **`<protected>`** - 子类访问：[类 - 访问说明符](10_classes_interfaces.md#access-specifiers)、[模块和路径](16_modules.md)、[访问说明符](12_access.md)
- **`<internal>`** - 模块访问：[模块和路径](16_modules.md)，[访问说明符](12_access.md)
- **`<scoped>`** - 基于路径的访问：[访问说明符](12_access.md)

### 方法说明符
- **`<override>`** - 替换父方法：[类 - 方法重写](10_classes_interfaces.md#method-overriding)，[访问说明符](12_access.md)
- **`<native>`** - 用 C++ 实现：[访问说明符](12_access.md)

## 运算符

### 算术
- **+、-、\*、/、%** - 数学运算：[原语 - 数学函数](02_primitives.md#mathematical-functions)、[运算符](04_operators.md)
- **+=、-=、\*=、/=** - 复合赋值：[运算符](04_operators.md)

### 比较
- **<、<=、>、>=** - 排序：[运算符](04_operators.md)
- **=，<>** - 相等/不等式：[运算符](04_operators.md)，[类型系统](11_types.md)

### 逻辑
- **和** - 逻辑与：[运算符](04_operators.md)，[失败](08_failure.md)
- **或** - 逻辑或：[运算符](04_operators.md)，[失败](08_failure.md)
- **不是** - 逻辑非：[运算符](04_operators.md)，[失败](08_failure.md)

### 访问
- **.** - 成员访问：[运算符](04_operators.md)、[表达式](01_expressions.md)
- **[]** - 索引：[容器 - 数组](03_containers.md#arrays)、[运算符](04_operators.md)、[表达式](01_expressions.md)
- **()** - 函数调用：[运算符](04_operators.md)，[表达式](01_expressions.md)
- **{}** - 对象构造：[运算符](04_operators.md)、[表达式](01_expressions.md)

### 特殊
- **:=** - 初始化：[运算符](04_operators.md)，[表达式](01_expressions.md)
- **..** - 范围运算符：[运算符](04_operators.md)、[表达式](01_expressions.md)
- **?** - 查询运算符：[概述](00_overview.md)、[容器 - 可选](03_containers.md#optionals)、[运算符](04_operators.md)、[失败](08_failure.md)

## 函数

### 功能特点
- **参数** - 功能输入：[功能](06_functions.md)
- **命名参数** - 显式参数名称：[函数](06_functions.md)
- **返回值** - 函数输出：[函数](06_functions.md)
- **函数类型** - 函数签名：[函数](06_functions.md)，[类型系统](11_types.md)
- **重载** - 多个定义：[函数](06_functions.md)，[运算符](04_operators.md)
- **lambdas** - 匿名函数：[函数](06_functions.md)、[表达式](01_expressions.md)
- **嵌套函数** - 本地函数定义：[函数](06_functions.md)
- **高阶函数** - 作为值的函数：[概述](00_overview.md)、[函数](06_functions.md)

## 模块和组织

### 模块系统
- **模块** - 代码组织：[模块和路径](16_modules.md)
- **使用** - 导入语句：[概述](00_overview.md)、[模块和路径](16_modules.md)
- **模块路径** - 分层名称：[模块和路径](16_modules.md)
- **限定名称** - 完整路径：[模块和路径](16_modules.md)
- **合格的访问** - 显式路径：[模块和路径](16_modules.md)
- **嵌套模块** - 模块层次结构：[模块和路径](16_modules.md)

## 坚持

### 保存系统
- **weak_map(player, t)** - 玩家数据：[容器 - 弱映射](03_containers.md#weak-maps)，[可持久化类型](17_persistable.md)
- **weak_map(session, t)** - 会话数据：[容器 - 弱映射](03_containers.md#weak-maps)、[可持久化类型](17_persistable.md)
- **可持久化类型** - 可保存数据：[概述](00_overview.md)、[类 - 可持久化](10_classes_interfaces.md#persistable)、[结构 - 可持久化结构](09_structs_enums.md#persistable-structs)、[可持久化类型](17_persistable.md)
- **模块范围的变量** - 持久存储：[模块和路径](16_modules.md)，[可持久化类型](17_persistable.md)

## 演变与兼容性

### 版本管理
- **向后兼容性** - 保留 API：[概述](00_overview.md)、[效果](13_effects.md)、[代码演变](18_evolution.md)
- **版本控制** - 跟踪更改：[代码演变](18_evolution.md)
- **弃用** - 逐步淘汰功能：[代码演变](18_evolution.md)
- **发布** - 公开代码：[模块和路径](16_modules.md)、[访问说明符](12_access.md)、[代码演变](18_evolution.md)
- **重大更改** - 不兼容的更新：[代码演变](18_evolution.md)
- **模式演变** - 数据结构更改：[类 - 类](10_classes_interfaces.md#classes)，[代码演变](18_evolution.md)

### 注释
- **@deprecated** - 标记为已弃用：[代码演变](18_evolution.md)
- **@experimental** - 标记为实验性：[代码演化](18_evolution.md)
- **@available** - 版本可用性：[代码演变](18_evolution.md)

## 内在函数

### 数学函数
- **Abs()** - 绝对值：[原语 - 数学函数](02_primitives.md#mathematical-functions)
- **Floor()** - 向下舍入：[原语 - 数学函数](02_primitives.md#mathematical-functions)
- **Ceil()** - 向上舍入：[原语 - 数学函数](02_primitives.md#mathematical-functions)
- **Round()** - 舍入到最接近的值：[原语 - 数学函数](02_primitives.md#mathematical-functions)
- **Sqrt()** - 平方根：[原语 - 数学函数](02_primitives.md#mathematical-functions)
- **Min()** - 最小值：[原语 - 数学函数](02_primitives.md#mathematical-functions)
- **Max()** - 最大值：[原语 - 数学函数](02_primitives.md#mathematical-functions)

### 实用函数
- **Print()** - 输出文本：[概述](00_overview.md)、[效果](13_effects.md)
- **ToString()** - 转换为字符串：[基元 - ToString()](02_primitives.md#tostring)
- **GetSession()** - 当前会话：[模块和路径](16_modules.md)

### 数组方法
- **Find()** - 查找元素索引：[容器 - 数组方法](03_containers.md#array-methods)
- **Remove()** - 按索引删除：[容器 - 数组方法](03_containers.md#array-methods)
- **RemoveFirstElement()** - 删除第一个匹配项：[容器 - 数组方法](03_containers.md#array-methods)
- **RemoveAllElements()** - 删除所有出现的情况：[容器 - 数组方法](03_containers.md#array-methods)
- **ReplaceElement()** - 按索引替换：[容器 - 数组方法](03_containers.md#array-methods)
- **ReplaceFirstElement()** - 替换第一次出现的位置：[容器 - 数组方法](03_containers.md#array-methods)
- **ReplaceAllElements()** - 替换所有出现的情况：[容器 - 数组方法](03_containers.md#array-methods)
- **ReplaceAll()** - 基于模式的替换：[容器 - 数组方法](03_containers.md#array-methods)

## 语法元素

### 文字
- **整数文字** - 整数值：[表达式](01_expressions.md)
- **浮点文字** - 十进制值：[表达式](01_expressions.md)
- **字符串文字** - 文本值：[表达式](01_expressions.md)
- **字符文字** - 单个字符：[表达式](01_expressions.md)
- **布尔文字** - 真/假：[表达式](01_expressions.md)

### 特殊值
- **false** - 失败值，空可选：[基元 - 布尔值](02_primitives.md#booleans)、[容器 - 可选](03_containers.md#optionals)、[失败](08_failure.md)
- **true** - 成功值：[基元 - 布尔值](02_primitives.md#booleans)
- **NaN** - 不是数字：[基元 - 浮点数](02_primitives.md#floats)
- **Inf** - 无穷大：[基元 - 浮点数](02_primitives.md#floats)

### 语言结构
- **评论** - 代码文档：[概述](00_overview.md)
- **标识符** - 名称：[表达式](01_expressions.md)

## 特殊概念

### 语言特性
- **原型表达式** - 原型模式：[类 - 对象构造](10_classes_interfaces.md#object-construction)、[表达式](01_expressions.md)
- **字符串插值** - 嵌入表达式：[原语 - 字符和字符串](02_primitives.md#characters-and-strings)
- **模式匹配** - 结构匹配：[概述](00_overview.md)、[枚举 - 使用枚举](09_structs_enums.md#using-enums)、[控制流程](07_control.md)
- **继承** - 类层次结构：[类 - 继承](10_classes_interfaces.md#inheritance)、[类型系统](11_types.md)、[访问说明符](12_access.md)
- **多态性** - 多种形式：[类 - 方法重写](10_classes_interfaces.md#method-overriding)，[类型系统](11_types.md)
- **事务语义** - 回滚行为：[概述](00_overview.md)、[失败](08_failure.md)、[效果](13_effects.md)
- **选项{}** 构造函数：[概述](00_overview.md)、[容器 - 可选](03_containers.md#optionals)
- **数组{}** 构造函数：[概述](00_overview.md)、[容器 - 数组](03_containers.md#arrays)
- **map{}** 构造函数：[容器 - 映射](03_containers.md#maps)

---

*注：该索引涵盖了 Verse 文档中的所有主要概念。每个条目都直接链接到详细定义或解释概念的小节。使用浏览器的搜索功能（Ctrl+F 或 Cmd+F）快速查找特定术语。*
