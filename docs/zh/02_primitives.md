# 原始数据类型

Verse 提供了一组丰富的基本类型，涵盖了基本类型
编程需求。数字类型 `int`、`float` 和 `rational`
处理数学运算、计数器和测量。的
`logic` 类型表示条件和标志的布尔值。文字
通过 `char`、`char32` 和 `string` 类型处理字符
数据、玩家姓名和消息。两种特殊类型，`any` 和 `void`，
作为所有类型的超类型，在类型层次结构中发挥独特的作用
和空类型分别。

让我们从构成游戏逻辑支柱的数字类型开始详细探讨每种基本类型。

## 内在函数

*内在函数*是由直接提供的内置操作
无法在纯 Verse 代码中实现的运行时。这些功能
接受特殊的编译器处理并为许多
语言特征。内部函数很特殊，因为它们：

- **由运行时实现**：用 C++ 或其他本机代码编写，而不是 Verse
- **无法在 Verse 中复制**：需要访问运行时内部或低级操作
- **接收编译器识别**：编译器了解它们并可能优化它们的使用

示例包括数学运算，例如 `Abs()`、集合
像 `Find()` 这样的方法，以及像 `ToString()` 这样的类型转换。

大多数内部函数*不能被引用为一等函数
值*。这意味着您可以直接调用它们，但不能存储
它们在变量中或作为函数参数传递：

<!--versetest
assert_semantic_error(3502):
    F := Abs
-->
<!-- 01 -->
```verse
Result := Abs(-42)  # 返回 42

# 无效：不调用就无法引用
# F := Abs  # ERROR
# 无效：无法作为参数传递
# ApplyFunction(Abs, -42)  # ERROR
```
存在此限制是因为内在函数通常需要特殊的
不符合标准的调用约定或优化
功能模型。如果您需要传递内在功能，
将其包装在常规函数或嵌套函数中。

<a id="integers"></a>
## 整数

`int` 类型表示整数、非小数值。 `int` 可以
包含正数、负数或零。在运行时，
整数是任意精度的，并且可以增长到超出任何固定大小。
但是，整数*文字*必须位于 64 位有符号范围内
（`-9,223,372,036,854,775,808` 至 `9,223,372,036,854,775,807`），以及
超过 64 位的整数的支持有限（例如，不能使用
在字符串插值或持续）。

您可以在代码中包含 `int` 值作为文字。

<!--versetest-->
<!-- 02 -->
```verse
A :int= -42                    # 民用尺寸
#B := 42424242424242424242424242424242424242424242424242 # scary numbers...
                               # ...可以计算但不能写成文字

AnswerToTheQuestion :int= 42   # 永远不会改变的变量
CoinsPerQuiver :int= 100       # 一个箭袋需要这么多金币
ArrowsPerQuiver :int= 15       # 一个箭袋里有这么多箭

# 可变变量（有关 var 和 set 的详细信息，请参见可变性章节）
var Coins :int= 225           # 玩家目前拥有225金币
var Arrows :int= 3            # 玩家目前拥有 3 支箭
var TotalPurchases :int= 0    # 追踪总购买量
```
您可以对整数使用四种基本数学运算：`+`
另外，`-` 用于减法，`*` 用于乘法，`/` 用于
师。

<!--versetest
MyInt:int=10
MyHugeInt:int=1010100101
-->
<!-- 03 -->
```verse
var C :int= (-MyInt + MyHugeInt - 2) * 3   # 算术
set C += 1                                 # 就像说的，设置 C = C + 1
set C *= 2                                 # 就像说的，设置 C = C * 2
```
对于整数，运算符 `/` 是失败的，结果是
如果成功则输入 `rational`。

<a id="rationals"></a>
## 有理数

`rational` 类型将精确分数表示为
整数。与 `int` 或 `float` 不同，您不能写入 `rational`
直接字面量——有理数是通过整数除法创建的
`/` 运算符。

<!--versetest-->
<!-- 04 -->
```verse
X := 7 / 3    # X 的类型为有理数，正好代表 7÷3
```
有理数提供*精确的算术*，而不会损失精度
浮点数，使它们非常适合需要的游戏逻辑
精确的分数计算（资源分配、回合制
系统、概率计算）。

用 `/` 进行整数除法会产生一个有理值。除以零失败：

<!--versetest-->
<!-- 05 -->
```verse
Half := 5 / 2           # 有理数：正好 5/2
Third := 10 / 3         # 有理数：正好 10/3
Quarter := 1 / 4        # 有理数：正好 1/4

if (not (1 / 0)):
    # 除以零失败
```
有理数会自动简化为最低项以进行相等比较：

<!--versetest-->
<!-- 06 -->
```verse
# 所有这些都是相等的 - 减少到 5/2
(5 / 2) = (10 / 4)      # 真实
(5 / 2) = (15 / 6)      # 真实
(10 / 4) = (15 / 6)     # 真实
```
这种标准化确保了数学上等价的有理数
无论它们是如何构造的，都比较相等。

负号标准化为分子：

<!--versetest-->
<!-- 07 -->
```verse
(1 / -3) = (-1 / 3)     # true：负向分子移动
(-1 / -3) = (1 / 3)     # true：双重否定肯定
```
这种规范形式简化了相等性检查并确保
一致的行为。

重要属性：*`int` 是 `rational`* 的子类型。这意味着
在需要有理数的地方可以使用任何整数：

<!--versetest-->
<!-- 08 -->
```verse
ProcessRational(X:rational):rational = X

# 可以直接传递整数
ProcessRational(5) = 5/1     # 5 隐式为 5/1（有理数）
ProcessRational(0) = 0/1     # 0 隐式为 0/1（有理数）
```
然而，你*不能*返回一个需要int的有理数——即
将是一个缩小转换：

<!--versetest
assert_semantic_error(3510):
    BadFunction(X:rational):int = X
<#
-->
<!-- 09 -->
```verse
BadFunction(X:rational):int = X  # 错误
```
<!-- #> -->

整数有理数等于它们的整数等价物：

<!--versetest-->
<!-- 10 -->
```verse
(2 / 1) = 2             # 真实
2 = (2 / 1)             # 真实
(4 / 2) = 2             # true：4/2 减少为2/1，等于2
(9 / 3) = 3             # true：9/3 减少到 3/1，等于 3
```
这使得计算中整数和有理值能够无缝混合。

有两个函数将有理数转换为整数：

- **`Floor`** — 向负无穷大舍入（在数轴上向下）
- **`Ceil`** — 向正无穷大舍入（在数轴上）

<!--versetest-->
<!-- 11 -->
```verse
# 积极理性
Floor(5 / 2)= 2         # 2.5→2（下）
Ceil(5 / 2) = 3         # 2.5 → 3（上）

# 负理性——注意方向！
Floor((-5) / 2) = -3    # -2.5 → -3（朝向负无穷大）
Ceil((-5) / 2) = -2     # -2.5 → -2（朝向正无穷大）

# 带负分母
Floor(5 / -2) = -3      # 与 (-5)/2 相同
Ceil(5 / -2) = -2       # 与 (-5)/2 相同

# 均为阴性
Floor((-5) / -2) = 2    # 2.5 → 2
Ceil((-5) / -2) = 3     # 2.5 → 3
```
`Floor` 向负无穷大舍入，*而不是*向零舍入。这个
符合数学约定，但与截断不同。  当
参数是有理数，`Floor`不会失败，但是如果传递了一个`float`
它是 `decides` 函数。

有理数可用作参数和返回类型：

<!--versetest-->
<!-- 12 -->
```verse
# 返回有理数的函数
Half(X:int)<computes><decides>:rational = X / 2

# 使用结果
if (Result := Half[7]):
    Floor(Result) = 3   # 7/2 = 3.5，下限为 3
    Ceil(Result) = 4    # 7/2 = 3.5，Ceil 给出 4
```
因为 `int` 是 `rational` 的子类型，所以您“不能”基于重载
仅针对这些类型：

<!--versetest
assert_semantic_error(3532):
    ProcessValue(X:int):void = {}
    ProcessValue(X:rational):void = {}
<#
-->
<!-- 13 -->
```verse
ProcessValue(X:int):void = {}
ProcessValue(X:rational):void = {}  # 错误！
```
<!-- #> -->

编译器认为 `int` 比 `rational` 更具体，因此
签名会含糊不清。

Rational 擅长资源分配和公平计算：

<!--versetest-->
<!-- 14 -->
```verse
# 公平的资源分配
DistributeResources(TotalGold:int, NumPlayers:int)<decides>:int =
    GoldPerPlayer := TotalGold / NumPlayers
    Floor(GoldPerPlayer)  # 转换为完整金币（可以为 0）

# 要在金币不足时失败，请检查 > 0
DistributeResourcesOrFail(TotalGold:int, NumPlayers:int)<decides>:int =
    GoldPerPlayer := TotalGold / NumPlayers
    Floor(GoldPerPlayer) > 0  # 如果每个玩家都获得 0 则失败

# 物品承受能力计算
Coins:int = 225
CoinsPerQuiver:int = 100
ArrowsPerQuiver:int = 15

if (NumberOfQuivers := Floor(Coins / CoinsPerQuiver)):
    TotalArrows:int = NumberOfQuivers * ArrowsPerQuiver
    # 玩家可以负担 2 个箭袋 = 30 支箭
```
<a id="floats"></a>
## 浮点数

`float` 类型表示所有非整数数值。它可以容纳大数值和精确的小数，
例如 `1.0`、`-50.5` 和 `3.14159`。`float` 是 IEEE 64 位浮点数，
可以表示范围为 `[-2^1024 + 1, … , 0, … , 2^1024 - 1]` 的带小数点
正数或负数，也可以表示 `NaN`（非数字）。其实现与 IEEE 标准的差异
如下：

- 只有一个 `NaN` 值。
- `NaN` 等于其自身。
- 每个数字都等于它自己。
- `0` 不能为负数。

可以在代码中将浮点值写成字面量：

<!--versetest-->
<!-- 15 -->
```verse
A:float = 1.0
B := 2.14
MaxHealth : float = 100.0

var C:float = A + B
C = 3.14              # 成功
set C -= 3.14
C = 0.0               # 成功
# C = 0 # 编译错误; 0 不是“float”文字
```
您可以对浮点数使用四种基本数学运算：`+`
另外，`-` 用于减法，`*` 用于乘法，`/` 用于
师。还有组合运算符用于进行基本数学运算
运算（加法、减法、乘法和除法），以及
更新变量的值：

<!--versetest-->
<!-- 16 -->
```verse
var CurrentHealth : float = 100.0
set CurrentHealth /= 2.0    # CurrentHealth 的价值减半
set CurrentHealth += 10.0   # 当前健康状况增加 10
set CurrentHealth *= 1.5    # 当前健康状况乘以 1.5
```
要将 `int` 转换为 `float`，请将其乘以 `1.0`：`MyFloat:=MyInt*1.0`。

<a id="mathematical-functions"></a>
## 数学函数

Verse 提供常见数值的内在数学函数
操作。这些函数由运行时优化并与
`int` 和 `float` 类型。

`Abs()` 函数返回数字的绝对值——其
与零的距离，不考虑符号：

<!--NoCompile-->
<!-- 17 -->
```verse
# 签名
Abs(X:int):int
Abs(X:float):float
```
<!--versetest-->
<!-- 18 -->
```verse
Abs(5)    # 返回 5
Abs(-5)   # 返回 5
Abs(0)    # 返回 0
Abs(3.14) # 返回 3.14
```
`Min()` 和 `Max()` 函数返回两个值的最小值或最大值：

<!--NoCompile-->
<!-- 19 -->
```verse
# 签名
Min(A:int, B:int):int
Min(A:float, B:float):float
Max(A:int, B:int):int
Max(A:float, B:float):float
```
<!--versetest-->
<!-- 20 -->
```verse
# NaN通过比较传播
Max(NaN, 5.0)   # 返回NaN
Min(NaN, 5.0)   # 返回NaN
Max(NaN, NaN)   # 返回NaN

# 无限操控
Max(Inf, 100.0)    # 返回信息
Min(-Inf, 100.0)   # 返回-Inf
Max(-Inf, -Inf)    # 返回-Inf
Min(Inf, Inf)      # 返回信息
```
Verse 提供了多个舍入函数，可以使用不同的舍入策略将浮点数转换为整数：

<!--NoCompile-->
<!-- 21 -->
```verse
# 签名
Floor(X:float)<reads><decides>:int   # 向下舍入
Ceil(X:float)<reads><decides>:int    # 四舍五入
Round(X:float)<reads><decides>:int   # 四舍五入到最接近的偶数 (IEEE-754)
Int(X:float)<reads><decides>:int     # 向零截断
```
舍入到最接近的偶数（恰好位于中点时取偶数）：

<!--versetest-->
<!-- 22 -->
```verse
Round[1.5]    # 返回 2（平局：1.5 轮为偶数 2）
Round[0.5]    # 返回 0（平局：0.5 舍入为偶数 0）
Round[2.5]    # 返回 2（平局：2.5 轮为偶数 2）
Round[-1.5]   # 返回 -2（平局：-1.5 轮为偶数 -2）
Round[-0.5]   # 返回 0（平局：-0.5 舍入到偶数 0）

Round[1.4]    # 返回 1（无平局，向下舍入）
Round[1.6]    # 返回 2（无平局，向上舍入）
```
“四舍五入到最接近的偶数”策略（也称为银行家四舍五入）
避免在对许多平局值进行舍入时出现偏差。

一些附加的数学函数：

<!--versetest-->
<!-- 23 -->
```verse
# 签名
# Sqrt(X:float):float

# 负输入返回 NaN
Sqrt(-1.0)    # 返回NaN

# 特殊值
Sqrt(Inf)     # 返回信息
Sqrt(NaN)     # 返回NaN

# 签名
# Pow(Base:float, Exponent:float):float

Pow(2.0, 3.0)     # 返回 8.0 (2³)
Pow(10.0, 2.0)    # 返回 100.0
Pow(4.0, 0.5)     # 返回 2.0（平方根）
Pow(2.0, -1.0)    # 返回 0.5（倒数）

# 特殊情况
Pow(0.0, 0.0)     # 返回 1.0（按照惯例）
Pow(NaN, 0.0)     # 返回 1.0（0 指数始终为 1）
Pow(1.0, NaN)     # 返回 1.0（1 的任意次方均为 1）

# Exp(X:float):float

Exp(0.0)      # 返回 1.0
Exp(1.0)      # 返回 2.718... (e)
Exp(-1.0)     # 返回 0.368... (1/e)

# 特殊值
Exp(-Inf)     # 返回 0.0
Exp(Inf)      # 返回信息
Exp(NaN)      # 返回NaN

# 签名
# Ln(X:float):float

Ln(1.0)       # 返回 0.0
# Ln(2.718...)     # Returns 1.0 (ln(e) = 1)
Ln(10.0)      # 返回 2.302...

# 输入无效
Ln(-1.0)      # 返回NaN（负）
Ln(0.0)       # 返回 -Inf（零的对数）

# 特殊值
Ln(Inf)       # 返回信息
Ln(NaN)       # 返回NaN

# 签名
# Log(Base:float, Value:float):float

Log(10.0, 100.0)   # 返回2.0（log₁₀(100) = 2）
Log(2.0, 8.0)      # 返回3.0（log2(8) = 3）
Log(2.0, 2.0)      # 返回 1.0（logₙ(n) = 1）
```
Verse 提供以弧度为单位进行运算的标准三角函数：

<!--versetest-->
<!-- 27 -->
```verse
# 签名
# Sin(Angle:float):float
# Cos(Angle:float):float
# Tan(Angle:float):float

# 常见角度（使用 PiFloat ）
Sin(0.0)              # 返回 0.0
Sin(PiFloat / 2.0)    # 返回 1.0
Sin(PiFloat)          # 返回 0.0
Sin(-PiFloat / 2.0)   # 返回-1.0

Cos(0.0)              # 返回 1.0
Cos(PiFloat / 2.0)    # 返回 0.0
Cos(PiFloat)          # 返回-1.0

Tan(0.0)              # 返回 0.0
Tan(PiFloat / 4.0)    # 返回 1.0
Tan(-PiFloat / 4.0)   # 返回-1.0

# 特殊值
Sin(NaN)              # 返回NaN
Sin(Inf)              # 返回NaN

# 签名
# ArcSin(X:float):float   # Returns angle in [-π/2, π/2]
# ArcCos(X:float):float   # Returns angle in [0, π]
# ArcTan(X:float):float   # Returns angle in [-π/2, π/2]
# ArcTan(Y:float, X:float):float  # Two-argument arctangent

# 逆关系
ArcSin(0.0)    # 返回 0.0
ArcSin(1.0)    # 返回 π/2
ArcSin(-1.0)   # 返回 -π/2

ArcCos(1.0)    # 返回 0.0
ArcCos(0.0)    # 返回 π/2
ArcCos(-1.0)   # 返回 π

ArcTan(0.0)    # 返回 0.0
ArcTan(1.0)    # 返回 π/4
ArcTan(-1.0)   # 返回 -π/4

# 验证逆关系
Angle := PiFloat / 6.0  # 30度
Sin(ArcSin(Sin(Angle))) = Sin(Angle)  # 真实

# ArcTan(Y, X) returns angle of point (X, Y) from origin
ArcTan(1.0, 1.0)     # 返回 π/4（45 度）
ArcTan(1.0, 0.0)     # 返回 π/2（90 度）
ArcTan(0.0, 1.0)     # 返回 0.0（0 度）
ArcTan(1.0, -1.0)    # 返回 3π/4（135 度）
ArcTan(-1.0, -1.0)   # 返回 -3π/4（-135 度）
```
双曲函数是三角函数的类似物
双曲线。它们在物理模拟、悬链线、
以及某些数学模型。

<!--versetest-->
<!-- 28 -->
```verse
# 签名
# Sinh(X:float):float    # Hyperbolic sine
# Cosh(X:float):float    # Hyperbolic cosine
# Tanh(X:float):float    # Hyperbolic tangent
# ArSinh(X:float):float  # Inverse hyperbolic sine
# ArCosh(X:float):float  # Inverse hyperbolic cosine
# ArTanh(X:float):float  # Inverse hyperbolic tangent

Sinh(0.0)     # 返回 0.0
Sinh(1.0)     # 返回 1.175...
Cosh(0.0)     # 返回 1.0
Cosh(1.0)     # 返回 1.543...
Tanh(0.0)     # 返回 0.0
Tanh(1.0)     # 返回 0.761...

# 特殊值
Sinh(-Inf)    # 返回-Inf
Sinh(Inf)     # 返回信息
Cosh(-Inf)    # 返回信息
Cosh(Inf)     # 返回信息
Tanh(-Inf)    # 返回-1.0
Tanh(Inf)     # 返回 1.0

ArSinh(0.0)   # 返回 0.0
ArCosh(1.0)   # 返回 0.0
ArTanh(0.0)   # 返回 0.0

# 特殊值
ArSinh(-Inf)  # 返回-Inf
ArSinh(Inf)   # 返回信息
ArCosh(Inf)   # 返回信息
ArCosh(-1.0)  # 返回 NaN（域错误）
```
对于带余数的整数除法，Verse 提供了 `Mod` 和
`Quotient`。这两个函数都是会失败的——当除数为
零。

<!--versetest-->
<!-- 29 -->
```verse
# 签名
# Mod(Dividend:int, Divisor:int)<decides>:int
# Quotient(Dividend:int, Divisor:int)<decides>:int

# 正操作数
Mod[15, 4]      # 返回 3
Quotient[15, 4] # 返回 3
# 关系：15 = 3*4 + 3

# 负股息
Mod[-15, 4]      # 返回 1
Quotient[-15, 4] # 返回-4
# 关系：-15 = -4*4 + 1

# 负除数
Mod[-1, -2]      # 返回 1
Quotient[-1, -2] # 返回 1

# 除以零失败
if (not Mod[10, 0]):
    Print("Cannot mod by zero")
if (not Quotient[10, 0]):
    Print("Cannot divide by zero")
```
模结果始终满足：

<!--versetest
assert:
    Dividend:int = 15
    Divisor:int = 4
    Dividend = Quotient[Dividend, Divisor] * Divisor + Mod[Dividend, Divisor]

assert:
    Dividend:int = -15
    Divisor:int = 4
    Dividend = Quotient[Dividend, Divisor] * Divisor + Mod[Dividend, Divisor]

assert:
    Dividend:int = -1
    Divisor:int = -2
    Dividend = Quotient[Dividend, Divisor] * Divisor + Mod[Dividend, Divisor]
<#
-->
<!-- 30 -->
```verse
Dividend = Quotient[Dividend, Divisor] * Divisor + Mod[Dividend, Divisor]
```
<!-- #> -->

结果的符号遵循特定规则：

- `Mod` 结果与除数具有相同的符号（欧几里得除法）
- `Quotient` 相应调整以保持身份

还有一些实用函数：

<!--versetest-->
<!-- 31 -->
```verse
# 签名
# Sgn(X:int):int
# Sgn(X:float):float

Sgn(10)       # 返回 1
Sgn(0)        # 返回 0
Sgn(-5)       # 返回-1

Sgn(3.14)     # 返回 1.0
Sgn(0.0)      # 返回 0.0
Sgn(-2.71)    # 返回-1.0

# 特殊浮点值
Sgn(Inf)      # 返回 1.0
Sgn(-Inf)     # 返回-1.0
Sgn(NaN)      # 返回NaN
```
Lerp 在两个值之间进行插值：

<!--versetest-->
<!-- 32 -->
```verse
# 签名
# Lerp(From:float, To:float, Parameter:float):float

Lerp(0.0, 10.0, 0.0)    # 返回 0.0（0% = 来自）
Lerp(0.0, 10.0, 0.5)    # 回报 5.0 (50%)
Lerp(0.0, 10.0, 1.0)    # 返回 10.0（100% = 至）
Lerp(0.0, 10.0, 2.0)    # 返回 20.0（推断）
Lerp(10.0, 20.0, 0.3)   # 返回 13.0

# 适用于负范围
Lerp(-10.0, 10.0, 0.5)  # 返回 0.0
```
公式为：`From + Parameter * (To - From)`

`IsFinite` 检查浮点数是否有限，如果该值则成功
不是 NaN、Inf 或 -Inf。否则会失败：

<!--versetest

assert:
    (5.0).IsFinite[]
    (0.0).IsFinite[]
    (-100.0).IsFinite[]
    not (Inf).IsFinite[]
    not (-Inf).IsFinite[]
    not (NaN).IsFinite[]
    (15.16).IsFinite[] = 15.16
<#
-->
<!-- 33 -->
```verse
# 浮点值的方法
# X.IsFinite()<computes><decides>:float

(5.0).IsFinite[]      # 成功
(0.0).IsFinite[]      # 成功
(-100.0).IsFinite[]   # 成功

(Inf).IsFinite[]  # 失败
(-Inf).IsFinite[] # 失败
(NaN).IsFinite[]  # 失败

# 如果成功则返回相同的数字
(15.16).IsFinite[] = 15.16 # 成功，两者相等

# 对于验证有用
# SafeCalculation(X:float, Y:float)<decides>:float =
#     X.IsFinite[] 和 Y.IsFinite[]
#     Result := X / Y
#     结果.IsFinite[]
#     结果
```
<!-- #> -->

Verse 提供常见数学值的常量：

<!--versetest-->
<!-- 34 -->
```verse
PiFloat # 3.14159265358979323846...
Inf     # 正无穷大
-Inf    # 负无穷大（Inf 的否定）
NaN     # 不是一个数字
```
<a id="booleans"></a>
## 布尔值

`logic` 类型表示布尔值 `true` 和 `false`。

<!--versetest-->
<!-- 35 -->
```verse
A:logic = true
B := false

# A = B # 失败
A?                # 成功
# 乙？             # 失败

true?             # 成功
# 假的？         # 失败
```
`logic`类型仅支持查询操作和比较
操作。  查询表达式使用查询运算符 `?` 来检查是否
如果逻辑值为 `false`，则逻辑值为真且失败。  对于
比较操作，使用可失败运算符 `=` 来测试两个是否
逻辑值相同，并用 `<>` 来测试不等式。

许多编程语言发现使用这样的类型是惯用的
`logic` 表示操作成功或失败。在Verse中，我们
无论何时，都可以使用成功和失败来达到此目的
可能的。如果守卫条件成立，则条件仅执行 `then` 分支
成功：

<!--versetest
ShowTargetLockedIcon():void={}
TargetLocked:?int = option{42}
-->
<!-- 36 -->
```verse
if (TargetLocked?):
    ShowTargetLockedIcon()
```
将具有 `<decides>` 效果的表达式转换为 `true`
成功或 `false` 失败时，使用 `logic{ exp }`：

<!--versetest
using{ /Verse.org/Random }
Frequency:int = 10
F()<decides>:void=
    GotIt := logic{GetRandomInt(0, Frequency) <> 0}
    GotIt?
<#
-->
<!-- 37 -->
```verse
GotIt := logic{GetRandomInt(0, Frequency) <> 0}   # if success
GotIt?                                            # 那么这就成功了
GotIt = false                                     # 这失败了
not GotIt?                                        # 这也失败了
```
<!-- #> -->

<a id="characters-and-strings"></a>
## 字符和字符串

文本以字符和字符串的形式表示。  `char` 是
单个 **UTF-8 代码单元**（不是完整的 Unicode 代码点）。一个字符串
因此是一个字符数组，写为 `[]char`。对于
为了方便起见，为 `[]char` 提供了类型别名 `string`：

<!--versetest-->
<!-- 38 -->
```verse
MyName :string = "Joseph"
MyAlterEgo := "José"
```
使用 UTF-8 作为字符编码方案。每个 UTF-8 代码单元
是一个字节。 Unicode 代码点可能需要 1 到 4 个
代码单位。值较低的代码点使用较少的字节，而
更高的值需要更多。

例如：

- `"a"` 需要一个字节 (`{0o61}`),
- `"á"` 需要两个字节 (`{0oC3}{0oA1}`),
- `"🐈"`（猫表情符号）需要四个字节（`{0u1f408}`）。

因此，字符串是代码单元的序列，而不一定是序列
抽象意义上的 Unicode 字符。

因为字符串是 `char` 的数组，所以您可以使用以下命令对它们进行索引
`[]`。索引具有 `<decides>` 效果：索引成功时
有效，否则失败。

<!--versetest
MyName:string="J"
-->
<!-- 39 -->
```verse
TheLetterJ := MyName[0]     # 成功
TheLetterJ = 'J'            # 成功
# 我的名字[100] # 失败
```
字符串的长度是它包含的 UTF-8 代码单元的数量，
通过 `.Length` 访问。请注意，这与 * 数字不同
Unicode 字符数*：

<!--versetest-->
<!-- 40 -->
```verse
"José".Length = 5           # 成功；5个UTF-8代码单元
"Jose".Length = 4           # 成功；4个UTF-8代码单元
```
因为 `string` 只是 `[]char`，所以声明为 `var` 的字符串可以发生变化：

<!--versetest-->
<!-- 41 -->
```verse
var OuterSpaceFriend :string = "Glorblex"
set OuterSpaceFriend[0] = 'F'
```
可以使用 `+` 运算符连接字符串：

<!--versetest
MyName:string="Joe"
MyAlterEgo:string="Jak"
-->
<!-- 42 -->
```verse
MyAttemptAtFormatting := "My name is " + MyName + " but my alter ego is " + MyAlterEgo + "."
```
Verse 还支持字符串插值以实现更易读的格式：

<!--versetest
MyName:string="3"
MyAlterEgo:string="asdsa"
-->
<!-- 43 -->
```verse
Formatting := "My name is {MyName} but my alter ego is {MyAlterEgo}."
```
插值适用于范围内具有 `ToString()` 函数的任何值。

文字字符用单引号书写。类型取决于
字符是否在 ASCII 范围内 (`U+0000`–`U+007F`)
或不：

- `'e'` 的类型为 `char`，
- `'é'` 的类型为 `char32`。

<!--versetest-->
<!-- 44 -->
```verse
A :char = 'e'                       # 好的
B :char32 = 'é'                     # 好的
# C :char = 'é' # 错误：'é' 的类型是 char32
# D :char32 = 'e' # 错误：'e' 的类型是 char
```
字符文字也可以使用数字转义序列编写：

<!--versetest-->
<!-- 45 -->
```verse
E :char = 0o65                      # 好的；与“e”相同
F :char32 = 0u00E9                  # 好的；与“é”相同
```
- `char` 表示单个 UTF-8 代码单元（一个字节，`0oXX`）。
- `char32` 表示完整的 Unicode 代码点 (`0uXXXXX`)。

十六进制表示法：

- `0oXX` 对于 `char`：两个十六进制数字（0o00 到 0off）
- `0uXXXXX` 对于 `char32`：最多 6 个十六进制数字（0u00000 到 0u10ffff）

与某些语言不同，Verse 不允许字符和整数之间的隐式转换。

**字符转义序列**适用于字符和字符串文字：

|逃亡|意义|代码点 |
|--------|---------|------------|
| `\t` |选项卡| U+0009 |
| `\n` |换行 | U+000A |
| `\r` |回车| U+000D |
| `\"` |双引号 | U+0022 |
| `\'` |单引号 | U+0027 |
| `\\` |反斜杠| U+005C |
| `\{` |左大括号 | U+007B |
| `\}` |右大括号| U+007D |
| `\<` |小于| U+003C |
| `\>` |大于| U+003E |
| `\&` | & 符号 | U+0026 |
| `\#` |哈希值/磅 | U+0023 |
| `\~` |波形符| U+007E |

示例：

<!--versetest-->
<!-- 46 -->
```verse
Tab := '\t'
Newline := '\n'
Quote := '\"'
Brace := '\{'
```
可以使用可失败运算符 `=`（相等）来比较字符串
和 `<>`（不等式）。比较是通过代码点完成的，并且是大小写
敏感。  平等取决于确切的代码单元序列，而不是视觉上的
外观。 Unicode 允许同一摘要有多种编码
性格。例如，`"é"` 可能显示为单个代码点
`{0u00E9}`，或作为两码点序列 `"e"` (`{0u0065}`) 加上
组合重音 (`{0u0301}`)。这两个字符串看起来相同，但是
他们在Verse中并不平等。

检查玩家是否选择了正确的项目：

<!--versetest-->
<!-- 47 -->
```verse
ExpectedItemInternalName :string = "RedPotion"
SelectedItemInternalName :string = "BluePotion"

if (SelectedItemInternalName = ExpectedItemInternalName):
    true
else:
    false
```
用前导零填充计时器：

<!--versetest-->
<!-- 48 -->
```verse
SecondsLeft :int = 30
SecondsString :string = ToString(SecondsLeft)    # 将 int 转换为字符串

var Combined :string = "Time Remaining: "
if (SecondsString.Length > 2):
    set Combined += "99"               # 钳位至最大值
else if (SecondsString.Length < 2):
    set Combined += "0{SecondsString}" # 用零填充
else:
    set Combined += SecondsString
```
字符串插值支持复杂的表达式，而不仅仅是简单的变量：

<!--versetest
Format(D:float, ?Decimals:int):string=""
-->
<!-- 49 -->
```verse
# 表达式插值
Age := 30
Message := "Next year: {Age + 1}"

# 带命名参数的函数调用
Distance := 5.5
Formatted := "Distance: {Format(Distance, ?Decimals:=2)}"
```
字符串可以使用插值大括号来跨越多行以进行延续：

<!--versetest-->
<!-- 50 -->
```verse
LongMessage := "This is a multi-line {
}string that continues across {
}multiple lines."

# 注意空白：
AnotherMessage := "This is another {
}  multi-line message with     {
    # 此评论被忽略
}    many spaces."
```
空插值 `{}` 被忽略，这对于线很有用
继续而不添加内容。

由于 `string` 是 `[]char`，因此可以比较字符串和字符数组：

<!--versetest-->
<!-- 51 -->
```verse
"abc" = array{'a', 'b', 'c'}    # 成功
"" = array{}                     # 成功 - 空字符串等于空数组
```
字符串中的块注释在解析过程中被删除：

<!--versetest-->
<!-- 52 -->
```verse
Text := "abc<#this comment is removed#>def"    # 与“abcdef”相同
```
<a id="tostring"></a>
### ToString()

`ToString()` 函数将值转换为其字符串
交涉。它是多态的——存在多个重载
不同类型：

<!--versetest
<#
-->
<!-- 53 -->
```verse
# 签名
ToString(X:int):string
ToString(X:float):string
ToString(X:char):string
ToString(X:string):string  # 恒等函数
```
<!-- #> -->

字符串插值在嵌入值上隐式调用 `ToString()`：

<!--versetest-->
<!-- 54 -->
```verse
Age := 25
Score := 98.5

# 这些是等效的：
Message1 := "Age: " + ToString(Age) + ", Score: " + ToString(Score)
Message2 := "Age: {Age}, Score: {Score}"
# 两者都产生：“年龄：25，分数：98.5”
```
这使得 `ToString()` 对于格式化输出至关重要，即使您
不要直接调用它。

`ToString()` 仅适用于原始类型。用户定义的类和
结构体没有自动字符串转换功能。

### ToDiagnostic()

`ToDiagnostic()` 函数将值转换为诊断字符串
表示，对于调试和日志记录很有用。虽然类似于
`ToString()`，它可能提供更详细或特定于实现的
信息：

<!--versetest
SomeValue:int=1
-->
<!-- 55 -->
```verse
# 用法（精确签名取决于类型）
DiagnosticText := ToDiagnostic(SomeValue)
```
`ToDiagnostic()` 主要用于调试输出而不是
面向用户的字符串。它生成的确切格式可能因虚拟机而异
实现，并且不保证跨版本稳定。

<a id="type-type"></a>
## `type` 类型

`type` 类型是一个*元类型* - 其值是其本身的类型
类型。每个 Verse 类型都可以用作 `type` 类型的值。这个
通过参数函数实现强大的通用编程，
其中类型是可以传递和约束的参数。

您可以创建保存类型值的变量和参数：

<!--versetest-->
<!-- 75 -->
```verse
# 保存类型值的变量
IntType:type = int
StringType:type = string
# 以类型作为参数的函数
CreateDefault(t:type):?t = false
# 用途
X:?int = CreateDefault(int)      # T = int，返回 false
Y:?string = CreateDefault(string)  # T = 字符串，返回 false
```
所有 Verse 类型都可以是类型值：

<!-- TODO: Cannot convert - type expressions like []int, [string]int, tuple(), ?int,
     int->string, subtype(), and type{} cannot be assigned to variables at module scope -->

<!--NoCompile-->
<!-- 76 -->
```verse
# 基元
PrimitiveType:type = int

# 用户定义类型
my_class := class {}
ClassType:type = my_class

my_struct := struct {Value:int}
StructType:type = my_struct

# 收藏类型
ArrayType:type = []int
MapType:type = [string]int
TupleType:type = tuple(int, string)
OptionType:type = ?int

# 功能类型
FuncType:type = int->string

# 参数类型
generic_class(t:type) := class {Data:t}
ParametricType:type = generic_class(int)

# 元类型
SubtypeValue:type = subtype(my_class)

# 类型文字
TypeLiteralValue:type = type{_(:int):string}
```
这种通用性使得 `type` 成为 Verse 通用的基础
编程-任何类型都可以被抽象。

### 类型参数

`type` 最常见的用法是在 **where 子句** 中创建
参数（通用）函数：

<!--versetest-->
<!-- 77 -->
```verse
# 身份函数 - 适用于任何类型
Identity(X:t where t:type):t = X

# 用法 - 推断类型参数
Identity(42)        # t = 整数
Identity("hello")   # t = 字符串
Identity(true)      # t = 逻辑
```
`where t:type` 约束意味着“`t` 可以是任何 Verse 类型”。的
类型系统从参数推断 `t` 并确保类型安全
整个函数。

虽然 `where t:type` 接受任何类型，但您可以使用更具体的
像 `subtype` 这样的约束来限制哪些类型是有效的：

<!--versetest
Sort(Items:[]t where t:subtype(comparable)):[]t =
    Items
<#
-->
<!-- 78 -->
```verse
# 只接受可比较子类型的类型
Sort(Items:[]t where t:subtype(comparable)):[]t =
    # 可以使用比较运算，因为 t 是可比较的
    ...
```
<!-- #> -->

有关参数函数的综合文档，请参阅
函数章节。

### 输入为一流值

与许多类型仅在编译时存在的语言不同，Verse
将类型视为可以计算、存储和使用的“一流值”
操纵：

<!--versetest-->
<!-- 79 -->
```verse
# 返回类型值的函数
GetTypeForSize(Size:int):type =
    if (Size <= 8):
        int
    else:
        string

# 在数据结构中存储类型
TypeRegistry:[string]type = map{
    "Integer" => int,
    "Text" => string,
    "Flag" => logic
}
```
**在函数之间传递类型：**

<!--versetest
CreateArray(ElementType:type, Size:int):[]ElementType =
    array{}

MakeIntArray():[]int =
    CreateArray(int, 10)
<#
-->
<!-- 80 -->
```verse
# 带有类型参数的辅助函数
CreateArray(ElementType:type, Size:int):[]ElementType =
    # 这种模式在某些情况下有效
    ...

# 使用助手的函数
MakeIntArray():[]int =
    CreateArray(int, 10)
```
<!-- #> -->

### 返回类型参数的选项

常见的模式是让函数返回 `?t`，其中 `t` 是一种类型
参数，允许函数使用任何类型
可能失败：

<!--versetest
MaybeValue(Value:t, Condition:logic where t:type):?t =
    if (Condition?) then option{Value} else false

assert:
    X:?int = MaybeValue(5, false)
    Y:?float = MaybeValue(3.14, true)
<#
-->
<!-- 817 -->
```verse
# 返回类型 `t` 必须与 `Value` 参数的类型相同
MaybeValue(Value:t, Condition:logic where t:type):?t =
    if (Condition?) then option{Value} else false

# 用途
X:?int = MaybeValue(5, false)  # 返回 false 作为 ?int
Y:?float = MaybeValue(3.14, true)  # 以 ?float 形式返回option{3.14}
```
<!-- #> -->


<!--versetest
MaybeValueExplicit(T:type, Value:t, Condition:logic where t:subtype(T)):?T =
    if (Condition?):
        option{Value}
    else:
        false

assert:
    X:?int = MaybeValueExplicit(int, 5, false)
    Y:?float = MaybeValueExplicit(float, 3.14, true)
<#
-->
<!-- 818 -->
```verse
# 替代方案：显式传递类型参数
MaybeValueExplicit(T:type, Value:t, Condition:logic where t:subtype(T)):?T =
    if (Condition?):
        option{Value}
    else:
        false

# 用途
X:?int = MaybeValueExplicit(int, 5, false)  # 返回 false 作为 ?int
Y:?float = MaybeValueExplicit(float, 3.14, true)  # 以 ?float 形式返回option{3.14}
# Z:?int = MaybeValueExplicit(int, 3.14, true) # 错误：float 不是 int 的子类型
```
<!-- #> -->

此模式对于通用容器和工厂特别有用
函数可能会也可能不会产生值。

### 类型约束

where 子句中的 `type` 约束是最宽松的 - 它
接受任何Verse类型。对于更具体的要求，Verse 提供
附加限制：

<!--versetest-->
<!-- 82 -->
```verse
# 最宽松：任何类型
Generic(X:t where t:type):t = X

# 更具体：必须是可比较的子类型
RequiresComparison(X:t where t:subtype(comparable))<decides>:void =
    X = X  # 可以使用 = 因为 t 是可比较的

# 更具体：必须是精确的子类型
RequiresExactType(X:t, Y:u where t:type, u:subtype(t)):t =
    X  # Y 保证与 t 兼容
```
类型系统在编译时强制执行这些约束，从而防止
无效的类型使用。

### 限制

虽然 `type` 可实现强大的抽象，但也存在一些限制：

**一般不能构造任意类型：**

<!--NoCompile-->
<!-- 83 -->
```verse
# 无法执行此操作 - 无法构造任意类型 t 的值
MakeValue(T:type):T = ???  # For T=int 会返回什么？ T=字符串？
```
**无法在运行时检查类型结构：**

<!--versetest
<#
-->
<!-- 84 -->
```verse
# 无法执行此操作 - 没有运行时类型自省
GetFieldNames(T:type):string = ???
```
<!-- #> -->

**类型参数必须是推断的或显式的：**

<!--versetest
Identity(X:t where t:type):t = X

assert:
    Identity(42)

<#
-->
<!-- 85 -->
```verse
# 类型参数必须可以根据使用情况确定
Identity(X:t where t:type):t = X

# OK：从杠杆中推算出t
Identity(42)

# 错误：无法从无参数中推断出 t
MakeDefault(where t:type):t = ???
```
<!-- #> -->

<a id="any"></a>
## `any` 类型

`any` 类型是*所有类型的超类型*。中的每个类型
语言是 `any` 的子类型。正因为如此，`any`本身支持
很少的操作：`any` 提供的任何功能也必须
由所有其他类型实现。实际应用中，很少有
您可以直接使用 `any` 类型的值进行操作。尽管如此，还是很重要的
理解类型，因为它有时会在使用时出现
混合不同类型值的代码，或者当类型检查器
没有更精确的类型可以分配。

`any` 出现的一种方式是组合不共享同一个值的值时
更具体的超类型。例如：

<!--versetest
letters := enum:
    A
    B
    C

letter := class:
    Value : char
-->
<!-- 86 -->
```verse
Main(Arg : int) : void =
    X := if (Arg > 0) then:
        letters.A
    else:
        letter{Value := 'D'}
```
在此示例中，`X` 被分配 `letters` 类型的值或
类型为 `letter`。由于这两种类型不相关，编译器
为 `X` 分配类型 `any`，这是它们的最低公共超类型。

`any` 的一个更有用的角色是作为参数的类型，
语法上需要但实际没有使用。这种模式可能会出现
当实现需要特定方法签名的接口时。

<!--versetest-->
<!-- 87 -->
```verse
FirstInt(X:int, :any) : int = X
```
这里，第二个参数被忽略。因为它可以是任何值
任何类型，它的类型为 `any`。

在更通用的代码中，可以使用 *parametric 来表达相同的想法
types*，使函数既灵活又精确：

<!--versetest-->
<!-- 88 -->
```verse
First(X:t, :any where t:type) : t = X
```
此版本适用于任何类型 `t`，返回 `t` 类型的值
同时丢弃 `any` 类型的未使用参数。

<a id="void"></a>
## `void` 类型

`void` 类型表示没有有意义的结果，并且是
用在没有返回结果的地方。从技术上讲，`void` 是
接受任何值并计算结果为 `false` 的函数。

此设计允许返回类型为 `void` 的函数具有主体
计算结果为任何类型，同时确保调用者不能使用
结果。本体产生的值传递给`void`，
丢弃它并返回 `false`。

其目的是执行效果而不是计算的函数
一个值，返回类型为 `void`。

<!--versetest-->
<!-- 89 -->
```verse
LogMessage(Msg:string) : void =
    Print(Msg)
```
此处，`LogMessage` 执行操作（打印）但不返回
结果。 `void` 返回类型使这一点变得明确。
