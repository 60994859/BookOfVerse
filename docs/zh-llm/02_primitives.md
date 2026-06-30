# 基本数据类型

Verse 提供了一套丰富的基本类型，涵盖基础编程需求。数值类型 `int`、`float` 和 `rational` 处理数学运算、计数和度量。`logic` 类型表示条件和标志的布尔值。文本通过 `char`、`char32` 和 `string` 类型处理字符数据、玩家名称和消息。两个特殊类型 `any` 和 `void` 在类型层次结构中分别扮演所有类型的超类型和空类型的独特角色。

让我们从构成游戏逻辑支柱的数值类型开始，逐一详细探索每种基本类型。

## 内在函数

*内在函数（intrinsic functions）* 是由运行时直接提供的内置操作，无法通过纯 Verse 代码实现。这些函数接受编译器的特殊处理，构成许多语言特性的基础。内在函数之所以特殊，是因为：

- **由运行时实现**：使用 C++ 或其他原生代码编写，而非 Verse
- **无法在 Verse 中复现**：需要访问运行时内部或底层操作
- **获得编译器识别**：编译器知道它们的存在，并可能优化其使用

示例包括 `Abs()` 等数学运算、`Find()` 等集合方法，以及 `ToString()` 等类型转换。

大多数内在函数*无法作为一等值引用*。这意味着你可以直接调用它们，但不能将它们存储在变量中或作为函数参数传递：

<!--versetest
assert_semantic_error(3502):
    F := Abs
-->
<!-- 01 -->
```verse
Result := Abs(-42)  # Returns 42

# Invalid: Cannot reference without calling
# F := Abs  # ERROR
# Invalid: Cannot pass as parameter
# ApplyFunction(Abs, -42)  # ERROR
```

此限制的存在是因为内在函数通常需要特殊的调用约定或优化，而这些不适用于标准函数模型。如果需要传递内在函数功能，请将其包装在常规函数或嵌套函数中。

## 整数

`int` 类型表示整型、非小数值。一个 `int` 可以包含正数、负数或零。在运行时，整数是任意精度的，可以超出任何固定大小。然而，整数*字面量*必须适合 64 位有符号范围（`-9,223,372,036,854,775,808` 到 `9,223,372,036,854,775,807`），且超过 64 位的整数支持有限（例如，不能在字符串插值中使用或持久化）。

你可以在代码中将 `int` 值作为字面量包含。

<!--versetest-->
<!-- 02 -->
```verse
A :int= -42                    # civilian size
#B := 42424242424242424242424242424242424242424242424242 # scary numbers...
                                # ...can be computed but not written as literals

AnswerToTheQuestion :int= 42   # A variable that never changes
CoinsPerQuiver :int= 100       # A quiver costs this many coins
ArrowsPerQuiver :int= 15       # A quiver contains this many arrows

# Mutable variables (see Mutability chapter for details on var and set)
var Coins :int= 225           # The player currently has 225 coins
var Arrows :int= 3            # The player currently has 3 arrows
var TotalPurchases :int= 0    # Track total purchases
```

你可以对整数使用四种基本数学运算：`+` 表示加法，`-` 表示减法，`*` 表示乘法，`/` 表示除法。

<!--versetest
MyInt:int=10
MyHugeInt:int=1010100101
-->
<!-- 03 -->
```verse
var C :int= (-MyInt + MyHugeInt - 2) * 3   # arithmetic
set C += 1                                 # like saying, set C = C + 1
set C *= 2                                 # like saying, set C = C * 2
```

对于整数，运算符 `/` 是可失败的，成功时结果类型为 `rational`。

## 有理数

`rational` 类型表示精确分数，以整数的比例形式存储。与 `int` 或 `float` 不同，你不能直接编写 `rational` 字面量——有理数是通过使用 `/` 运算符进行整数除法创建的。

<!--versetest-->
<!-- 04 -->
```verse
X := 7 / 3    # X has type rational, representing exactly 7÷3
```

有理数提供*精确算术*，没有浮点数的精度损失，非常适合需要精确小数计算的游戏逻辑（资源分配、回合制系统、概率计算）。

整数除法使用 `/` 产生有理数值。除以零会失败：

<!--versetest-->
<!-- 05 -->
```verse
Half := 5 / 2           # rational: exactly 5/2
Third := 10 / 3         # rational: exactly 10/3
Quarter := 1 / 4        # rational: exactly 1/4

if (not (1 / 0)):
    # Division by zero fails
```

有理数会自动化简为最简形式以便进行相等比较：

<!--versetest-->
<!-- 06 -->
```verse
# All these are equal - reduced to 5/2
(5 / 2) = (10 / 4)      # true
(5 / 2) = (15 / 6)      # true
(10 / 4) = (15 / 6)     # true
```

这种归一化确保数学上等价的有理数无论通过何种方式构造，都能比较为相等。

负号会被归一化到分子：

<!--versetest-->
<!-- 07 -->
```verse
(1 / -3) = (-1 / 3)     # true: negative moves to numerator
(-1 / -3) = (1 / 3)     # true: double negative becomes positive
```

这种规范形式简化了相等性检查并确保行为一致。

一个重要特性：*`int` 是 `rational` 的子类型*。这意味着任何整数都可以用于期望有理数的地方：

<!--versetest-->
<!-- 08 -->
```verse
ProcessRational(X:rational):rational = X

# Can pass integers directly
ProcessRational(5) = 5/1     # 5 is implicitly 5/1 (rational)
ProcessRational(0) = 0/1     # 0 is implicitly 0/1 (rational)
```

但是，你*不能*在期望 `int` 的地方返回 `rational`——这是缩窄转换：

<!--versetest
assert_semantic_error(3510):
    BadFunction(X:rational):int = X
<#
-->
<!-- 09 -->
```verse
BadFunction(X:rational):int = X  # Error
```
<!-- #> -->

整数值的有理数与其整数等价：

<!--versetest-->
<!-- 10 -->
```verse
(2 / 1) = 2             # true
2 = (2 / 1)             # true
(4 / 2) = 2             # true: 4/2 reduces to 2/1, equals 2
(9 / 3) = 3             # true: 9/3 reduces to 3/1, equals 3
```

这使得整数和有理数值可以在计算中无缝混合。

有两个函数可将有理数转换为整数：

- **`Floor`** — 向负无穷大方向取整（数轴向下）
- **`Ceil`** — 向正无穷大方向取整（数轴向上）

<!--versetest-->
<!-- 11 -->
```verse
# Positive rationals
Floor(5 / 2)= 2         # 2.5 → 2 (down)
Ceil(5 / 2) = 3         # 2.5 → 3 (up)

# Negative rationals - note direction!
Floor((-5) / 2) = -3    # -2.5 → -3 (toward negative infinity)
Ceil((-5) / 2) = -2     # -2.5 → -2 (toward positive infinity)

# With negative denominator
Floor(5 / -2) = -3      # Same as (-5)/2
Ceil(5 / -2) = -2       # Same as (-5)/2

# Both negative
Floor((-5) / -2) = 2    # 2.5 → 2
Ceil((-5) / -2) = 3     # 2.5 → 3
```

`Floor` 向负无穷大方向取整，*而不是*向零取整。这符合数学惯例，但与截断不同。当参数是有理数时，`Floor` 不会失败，但如果传入 `float`，它则是一个 `decides` 函数。

有理数可以用作参数和返回类型：

<!--versetest-->
<!-- 12 -->
```verse
# Function returning rational
Half(X:int)<computes><decides>:rational = X / 2

# Use the result
if (Result := Half[7]):
    Floor(Result) = 3   # 7/2 = 3.5, Floor gives 3
    Ceil(Result) = 4    # 7/2 = 3.5, Ceil gives 4
```


由于 `int` 是 `rational` 的子类型，你*不能*仅基于这些类型进行重载：

<!--versetest
assert_semantic_error(3532):
    ProcessValue(X:int):void = {}
    ProcessValue(X:rational):void = {}
<#
-->
<!-- 13 -->
```verse
ProcessValue(X:int):void = {}
ProcessValue(X:rational):void = {}  # Error!
```
<!-- #> -->

编译器认为 `int` 比 `rational` 更具体，因此签名会有歧义。

有理数擅长资源分配和公平性计算：

<!--versetest-->
<!-- 14 -->
```verse
# Fair resource distribution
DistributeResources(TotalGold:int, NumPlayers:int)<decides>:int =
    GoldPerPlayer := TotalGold / NumPlayers
    Floor(GoldPerPlayer)  # Converts to whole gold pieces (can be 0)

# To fail when there's insufficient gold, check > 0
DistributeResourcesOrFail(TotalGold:int, NumPlayers:int)<decides>:int =
    GoldPerPlayer := TotalGold / NumPlayers
    Floor(GoldPerPlayer) > 0  # Fails if each player gets 0

# Item affordability calculation
Coins:int = 225
CoinsPerQuiver:int = 100
ArrowsPerQuiver:int = 15

if (NumberOfQuivers := Floor(Coins / CoinsPerQuiver)):
    TotalArrows:int = NumberOfQuivers * ArrowsPerQuiver
    # Player can afford 2 quivers = 30 arrows
```

## 浮点数

`float` 类型表示所有非整数的数值。它可以保存大数值和精确分数，如 `1.0`、`-50.5` 和 `3.14159`。浮点数是 IEEE 64 位浮点数，可以包含在范围 `[-2^1024 + 1, … , 0, … , 2^1024 - 1]` 内带小数点的正数或负数，或者值为 `NaN`（非数值）。该实现与 IEEE 标准在以下方面有所不同：

- 只有一个 `NaN` 值。
- `NaN` 等于自身。
- 每个数字都等于自身。
- `0` 不能为负数。

你可以在代码中将浮点数值作为字面量包含：

<!--versetest-->
<!-- 15 -->
```verse
A:float = 1.0
B := 2.14
MaxHealth : float = 100.0

var C:float = A + B
C = 3.14              # succeeds
set C -= 3.14
C = 0.0               # succeeds
# C = 0              # compile error; 0 is not a `float` literal
```

你可以对浮点数使用四种基本数学运算：`+` 表示加法，`-` 表示减法，`*` 表示乘法，`/` 表示除法。还有一些组合运算符用于执行基本数学运算（加法、减法、乘法、除法）并同时更新变量的值：

<!--versetest-->
<!-- 16 -->
```verse
var CurrentHealth : float = 100.0
set CurrentHealth /= 2.0    # Halves the value of CurrentHealth
set CurrentHealth += 10.0   # Adds 10 to CurrentHealth
set CurrentHealth *= 1.5    # Multiplies CurrentHealth by 1.5
```

要将 `int` 转换为 `float`，将其乘以 `1.0`：`MyFloat:=MyInt*1.0`。

## 数学函数

Verse 提供了用于常见数值运算的内在数学函数。这些函数由运行时优化，适用于 `int` 和 `float` 类型。

`Abs()` 函数返回一个数的绝对值——该数到零的距离，不考虑符号：

<!--NoCompile-->
<!-- 17 -->
```verse
# Signatures
Abs(X:int):int
Abs(X:float):float
```

<!--versetest-->
<!-- 18 -->
```verse
Abs(5)    # Returns 5
Abs(-5)   # Returns 5
Abs(0)    # Returns 0
Abs(3.14) # Returns 3.14
```

`Min()` 和 `Max()` 函数返回两个值中的最小值或最大值：

<!--NoCompile-->
<!-- 19 -->
```verse
# Signatures
Min(A:int, B:int):int
Min(A:float, B:float):float
Max(A:int, B:int):int
Max(A:float, B:float):float
```

<!--versetest-->
<!-- 20 -->
```verse
# NaN propagates through comparison
Max(NaN, 5.0)   # Returns NaN
Min(NaN, 5.0)   # Returns NaN
Max(NaN, NaN)   # Returns NaN

# Infinity handling
Max(Inf, 100.0)    # Returns Inf
Min(-Inf, 100.0)   # Returns -Inf
Max(-Inf, -Inf)    # Returns -Inf
Min(Inf, Inf)      # Returns Inf
```

Verse 提供了多个取整函数，将浮点数以不同取整策略转换为整数：

<!--NoCompile-->
<!-- 21 -->
```verse
# Signatures
Floor(X:float)<reads><decides>:int   # Round down
Ceil(X:float)<reads><decides>:int    # Round up
Round(X:float)<reads><decides>:int   # Round to nearest even (IEEE-754)
Int(X:float)<reads><decides>:int     # Truncate toward zero
```

向最近偶数取整（平局时取偶数）：

<!--versetest-->
<!-- 22 -->
```verse
Round[1.5]    # Returns 2 (tie: 1.5 rounds to even 2)
Round[0.5]    # Returns 0 (tie: 0.5 rounds to even 0)
Round[2.5]    # Returns 2 (tie: 2.5 rounds to even 2)
Round[-1.5]   # Returns -2 (tie: -1.5 rounds to even -2)
Round[-0.5]   # Returns 0 (tie: -0.5 rounds to even 0)

Round[1.4]    # Returns 1 (no tie, rounds down)
Round[1.6]    # Returns 2 (no tie, rounds up)
```

"向最近偶数取整"策略（也称为银行家取整）在取整多个平局值时避免了偏差。

一些额外的数学函数：

<!--versetest-->
<!-- 23 -->
```verse
# Signature
# Sqrt(X:float):float

# Negative inputs return NaN
Sqrt(-1.0)    # Returns NaN

# Special values
Sqrt(Inf)     # Returns Inf
Sqrt(NaN)     # Returns NaN

# Signature
# Pow(Base:float, Exponent:float):float

Pow(2.0, 3.0)     # Returns 8.0 (2³)
Pow(10.0, 2.0)    # Returns 100.0
Pow(4.0, 0.5)     # Returns 2.0 (square root)
Pow(2.0, -1.0)    # Returns 0.5 (reciprocal)

# Special cases
Pow(0.0, 0.0)     # Returns 1.0 (by convention)
Pow(NaN, 0.0)     # Returns 1.0 (0 exponent always 1)
Pow(1.0, NaN)     # Returns 1.0 (1 to any power is 1)

# Exp(X:float):float

Exp(0.0)      # Returns 1.0
Exp(1.0)      # Returns 2.718... (e)
Exp(-1.0)     # Returns 0.368... (1/e)

# Special values
Exp(-Inf)     # Returns 0.0
Exp(Inf)      # Returns Inf
Exp(NaN)      # Returns NaN

# Signature
# Ln(X:float):float

Ln(1.0)       # Returns 0.0
# Ln(2.718...)     # Returns 1.0 (ln(e) = 1)
Ln(10.0)      # Returns 2.302...

# Invalid inputs
Ln(-1.0)      # Returns NaN (negative)
Ln(0.0)       # Returns -Inf (log of zero)

# Special values
Ln(Inf)       # Returns Inf
Ln(NaN)       # Returns NaN

# Signature
# Log(Base:float, Value:float):float

Log(10.0, 100.0)   # Returns 2.0 (log₁₀(100) = 2)
Log(2.0, 8.0)      # Returns 3.0 (log₂(8) = 3)
Log(2.0, 2.0)      # Returns 1.0 (logₙ(n) = 1)
```

Verse 提供了标准三角函数，使用弧度：

<!--versetest-->
<!-- 27 -->
```verse
# Signatures
# Sin(Angle:float):float
# Cos(Angle:float):float
# Tan(Angle:float):float

# Common angles (using PiFloat constant)
Sin(0.0)              # Returns 0.0
Sin(PiFloat / 2.0)    # Returns 1.0
Sin(PiFloat)          # Returns 0.0
Sin(-PiFloat / 2.0)   # Returns -1.0

Cos(0.0)              # Returns 1.0
Cos(PiFloat / 2.0)    # Returns 0.0
Cos(PiFloat)          # Returns -1.0

Tan(0.0)              # Returns 0.0
Tan(PiFloat / 4.0)    # Returns 1.0
Tan(-PiFloat / 4.0)   # Returns -1.0

# Special values
Sin(NaN)              # Returns NaN
Sin(Inf)              # Returns NaN

# Signatures
# ArcSin(X:float):float   # Returns angle in [-π/2, π/2]
# ArcCos(X:float):float   # Returns angle in [0, π]
# ArcTan(X:float):float   # Returns angle in [-π/2, π/2]
# ArcTan(Y:float, X:float):float  # Two-argument arctangent

# Inverse relationships
ArcSin(0.0)    # Returns 0.0
ArcSin(1.0)    # Returns π/2
ArcSin(-1.0)   # Returns -π/2

ArcCos(1.0)    # Returns 0.0
ArcCos(0.0)    # Returns π/2
ArcCos(-1.0)   # Returns π

ArcTan(0.0)    # Returns 0.0
ArcTan(1.0)    # Returns π/4
ArcTan(-1.0)   # Returns -π/4

# Verify inverse relationship
Angle := PiFloat / 6.0  # 30 degrees
Sin(ArcSin(Sin(Angle))) = Sin(Angle)  # True

# ArcTan(Y, X) returns angle of point (X, Y) from origin
ArcTan(1.0, 1.0)     # Returns π/4 (45 degrees)
ArcTan(1.0, 0.0)     # Returns π/2 (90 degrees)
ArcTan(0.0, 1.0)     # Returns 0.0 (0 degrees)
ArcTan(1.0, -1.0)    # Returns 3π/4 (135 degrees)
ArcTan(-1.0, -1.0)   # Returns -3π/4 (-135 degrees)
```

双曲函数是三角函数在双曲线上的类似物。它们用于物理模拟、悬链线曲线以及某些数学模型。

<!--versetest-->
<!-- 28 -->
```verse
# Signatures
# Sinh(X:float):float    # Hyperbolic sine
# Cosh(X:float):float    # Hyperbolic cosine
# Tanh(X:float):float    # Hyperbolic tangent
# ArSinh(X:float):float  # Inverse hyperbolic sine
# ArCosh(X:float):float  # Inverse hyperbolic cosine
# ArTanh(X:float):float  # Inverse hyperbolic tangent

Sinh(0.0)     # Returns 0.0
Sinh(1.0)     # Returns 1.175...
Cosh(0.0)     # Returns 1.0
Cosh(1.0)     # Returns 1.543...
Tanh(0.0)     # Returns 0.0
Tanh(1.0)     # Returns 0.761...

# Special values
Sinh(-Inf)    # Returns -Inf
Sinh(Inf)     # Returns Inf
Cosh(-Inf)    # Returns Inf
Cosh(Inf)     # Returns Inf
Tanh(-Inf)    # Returns -1.0
Tanh(Inf)     # Returns 1.0

ArSinh(0.0)   # Returns 0.0
ArCosh(1.0)   # Returns 0.0
ArTanh(0.0)   # Returns 0.0

# Special values
ArSinh(-Inf)  # Returns -Inf
ArSinh(Inf)   # Returns Inf
ArCosh(Inf)   # Returns Inf
ArCosh(-1.0)  # Returns NaN (domain error)
```

对于带余数的整数除法，Verse 提供了 `Mod` 和 `Quotient`。这两个函数都是可失败的——当除数为零时失败。

<!--versetest-->
<!-- 29 -->
```verse
# Signatures
# Mod(Dividend:int, Divisor:int)<decides>:int
# Quotient(Dividend:int, Divisor:int)<decides>:int

# Positive operands
Mod[15, 4]      # Returns 3
Quotient[15, 4] # Returns 3
# Relationship: 15 = 3*4 + 3

# Negative dividend
Mod[-15, 4]      # Returns 1
Quotient[-15, 4] # Returns -4
# Relationship: -15 = -4*4 + 1

# Negative divisor
Mod[-1, -2]      # Returns 1
Quotient[-1, -2] # Returns 1

# Division by zero fails
if (not Mod[10, 0]):
    Print("Cannot mod by zero")
if (not Quotient[10, 0]):
    Print("Cannot divide by zero")
```

取模结果始终满足：

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

- `Mod` 的结果与被除数符号相同（欧几里得除法）
- `Quotient` 相应调整以维持恒等式

还有一些工具函数：

<!--versetest-->
<!-- 31 -->
```verse
# Signatures
# Sgn(X:int):int
# Sgn(X:float):float

Sgn(10)       # Returns 1
Sgn(0)        # Returns 0
Sgn(-5)       # Returns -1

Sgn(3.14)     # Returns 1.0
Sgn(0.0)      # Returns 0.0
Sgn(-2.71)    # Returns -1.0

# Special float values
Sgn(Inf)      # Returns 1.0
Sgn(-Inf)     # Returns -1.0
Sgn(NaN)      # Returns NaN
```

Lerp 在两个值之间插值：

<!--versetest-->
<!-- 32 -->
```verse
# Signature
# Lerp(From:float, To:float, Parameter:float):float

Lerp(0.0, 10.0, 0.0)    # Returns 0.0 (0% = From)
Lerp(0.0, 10.0, 0.5)    # Returns 5.0 (50%)
Lerp(0.0, 10.0, 1.0)    # Returns 10.0 (100% = To)
Lerp(0.0, 10.0, 2.0)    # Returns 20.0 (extrapolation)
Lerp(10.0, 20.0, 0.3)   # Returns 13.0

# Works with negative ranges
Lerp(-10.0, 10.0, 0.5)  # Returns 0.0
```

公式为：`From + Parameter * (To - From)`

`IsFinite` 检查浮点数是否为有限数，如果值不是 NaN、Inf 或 -Inf 则成功，否则失败：

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
# Method on float values
# X.IsFinite()<computes><decides>:float

(5.0).IsFinite[]      # succeeds
(0.0).IsFinite[]      # succeeds
(-100.0).IsFinite[]   # succeeds

(Inf).IsFinite[]  # fails
(-Inf).IsFinite[] # fails
(NaN).IsFinite[]  # fails

# Returns the same number if succeeds
(15.16).IsFinite[] = 15.16 # succeeds, both are equal

# Useful for validation
# SafeCalculation(X:float, Y:float)<decides>:float =
#     X.IsFinite[] and Y.IsFinite[]
#     Result := X / Y
#     Result.IsFinite[]
#     Result
```
<!-- #> -->

Verse 提供了常见数学值的常量：

<!--versetest-->
<!-- 34 -->
```verse
PiFloat # 3.14159265358979323846...
Inf     # Positive infinity
-Inf    # Negative infinity (negation of Inf)
NaN     # Not a Number
```

## 布尔值

`logic` 类型表示布尔值 `true` 和 `false`。

<!--versetest-->
<!-- 35 -->
```verse
A:logic = true
B := false

# A = B          # fails
A?                # succeeds
# B?             # fails

true?             # succeeds
# false?         # fails
```

`logic` 类型仅支持查询操作和比较操作。查询表达式使用查询运算符 `?` 来检查逻辑值是否为真，如果逻辑值为 `false` 则失败。对于比较操作，使用可失败运算符 `=` 测试两个逻辑值是否相同，使用 `<>` 测试是否不等。

许多编程语言习惯使用像 `logic` 这样的类型来表示操作的成功或失败。在 Verse 中，我们尽可能使用成功和失败来达到此目的。条件语句仅在守卫成功时才执行 `then` 分支：

<!--versetest
ShowTargetLockedIcon():void={}
TargetLocked:?int = option{42}
-->
<!-- 36 -->
```verse
if (TargetLocked?):
    ShowTargetLockedIcon()
```

要将带有 `<decides>` 效果的表达式转换为成功时为 `true`、失败时为 `false`，请使用 `logic{ exp }`：

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
GotIt?                                            # then this succeeds
GotIt = false                                     # and this fails
not GotIt?                                        # and this fails too
```
<!-- #> -->

## 字符和字符串

文本以字符和字符串的形式表示。`char` 是一个**UTF-8 编码单元**（而不是一个完整的 Unicode 码点）。因此字符串是字符数组，写作 `[]char`。为方便起见，提供了 `string` 类型别名表示 `[]char`：

<!--versetest-->
<!-- 38 -->
```verse
MyName :string = "Joseph"
MyAlterEgo := "José"
```

UTF-8 用作字符编码方案。每个 UTF-8 编码单元是一个字节。一个 Unicode 码点可能需要一到四个编码单元。码点值越低，使用字节数越少；值越高，所需字节数越多。

例如：

- `"a"` 需要一个字节（`{0o61}`），
- `"á"` 需要两个字节（`{0oC3}{0oA1}`），
- `"🐈"`（猫 emoji）需要四个字节（`{0u1f408}`）。

因此，字符串是编码单元的序列，不一定是抽象意义上的 Unicode 字符序列。

由于字符串是 `char` 数组，你可以使用 `[]` 进行索引。索引具有 `<decides>` 效果：索引有效时成功，否则失败。

<!--versetest
MyName:string="J"
-->
<!-- 39 -->
```verse
TheLetterJ := MyName[0]     # succeeds
TheLetterJ = 'J'            # succeeds
# MyName[100]               # fails
```

字符串的长度是其所含 UTF-8 编码单元的数量，通过 `.Length` 访问。请注意，这*与 Unicode 字符的数量不同*：

<!--versetest-->
<!-- 40 -->
```verse
"José".Length = 5           # succeeds; 5 UTF-8 code units
"Jose".Length = 4           # succeeds; 4 UTF-8 code units
```

因为 `string` 就是 `[]char`，声明为 `var` 的字符串可以修改：

<!--versetest-->
<!-- 41 -->
```verse
var OuterSpaceFriend :string = "Glorblex"
set OuterSpaceFriend[0] = 'F'
```

字符串可以使用 `+` 运算符进行拼接：

<!--versetest
MyName:string="Joe"
MyAlterEgo:string="Jak"
-->
<!-- 42 -->
```verse
MyAttemptAtFormatting := "My name is " + MyName + " but my alter ego is " + MyAlterEgo + "."
```

Verse 还支持字符串插值，以实现更易读的格式化：

<!--versetest
MyName:string="3"
MyAlterEgo:string="asdsa"
-->
<!-- 43 -->
```verse
Formatting := "My name is {MyName} but my alter ego is {MyAlterEgo}."
```

插值适用于任何作用域内具有 `ToString()` 函数的值。

字面量字符使用单引号书写。其类型取决于字符是否在 ASCII 范围（`U+0000`–`U+007F`）内：

- `'e'` 的类型为 `char`，
- `'é'` 的类型为 `char32`。

<!--versetest-->
<!-- 44 -->
```verse
A :char = 'e'                       # ok
B :char32 = 'é'                     # ok
# C :char = 'é'                     # error: type of 'é' is char32
# D :char32 = 'e'                   # error: type of 'e' is char
```

字符字面量也可以使用数字转义序列书写：

<!--versetest-->
<!-- 45 -->
```verse
E :char = 0o65                      # ok; same as 'e'
F :char32 = 0u00E9                  # ok; same as 'é'
```

- `char` 表示一个 UTF-8 编码单元（一个字节，`0oXX`）。
- `char32` 表示一个完整的 Unicode 码点（`0uXXXXX`）。

十六进制表示法：

- `0oXX` 用于 `char`：两个十六进制数字（0o00 到 0off）
- `0uXXXXX` 用于 `char32`：最多六个十六进制数字（0u00000 到 0u10ffff）

与某些语言不同，Verse 不允许字符和整数之间的隐式转换。

**字符转义序列**在字符字面量和字符串字面量中都有效：

| 转义 | 含义 | 码点 |
|--------|---------|-----------|
| `\t` | 制表符 | U+0009 |
| `\n` | 换行符 | U+000A |
| `\r` | 回车符 | U+000D |
| `\"` | 双引号 | U+0022 |
| `\'` | 单引号 | U+0027 |
| `\\` | 反斜杠 | U+005C |
| `\{` | 左花括号 | U+007B |
| `\}` | 右花括号 | U+007D |
| `\<` | 小于号 | U+003C |
| `\>` | 大于号 | U+003E |
| `\&` | & 符号 | U+0026 |
| `\#` | 井号 | U+0023 |
| `\~` | 波浪号 | U+007E |

示例：

<!--versetest-->
<!-- 46 -->
```verse
Tab := '\t'
Newline := '\n'
Quote := '\"'
Brace := '\{'
```

字符串可以使用可失败运算符 `=`（相等）和 `<>（不等）进行比较。比较按码点进行，并区分大小写。相等性取决于精确的编码单元序列，而非视觉外观。Unicode 允许同一抽象字符有多种编码。例如，`"é"` 可能显示为单个码点 `{0u00E9}`，或者由 `"e"`（`{0u0065}`）加一个组合重音符号（`{0u0301}`）的两个码点序列组成。这两个字符串看起来相同，但在 Verse 中它们不相等。

检查玩家是否选择了正确的物品：

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
SecondsString :string = ToString(SecondsLeft)    # convert int to string

var Combined :string = "Time Remaining: "
if (SecondsString.Length > 2):
    set Combined += "99"               # clamp to maximum
else if (SecondsString.Length < 2):
    set Combined += "0{SecondsString}" # pad with zero
else:
    set Combined += SecondsString
```

字符串插值支持复杂表达式，而不仅仅是简单变量：

<!--versetest
Format(D:float, ?Decimals:int):string=""
-->
<!-- 49 -->
```verse
# Expression interpolation
Age := 30
Message := "Next year: {Age + 1}"

# Function calls with named arguments
Distance := 5.5
Formatted := "Distance: {Format(Distance, ?Decimals:=2)}"
```

字符串可以使用插值花括号跨多行：

<!--versetest-->
<!-- 50 -->
```verse
LongMessage := "This is a multi-line {
}string that continues across {
}multiple lines."

# Attention to whitespace:
AnotherMessage := "This is another {
}  multi-line message with     {
    # This comment is ignored
}    many spaces."
```

空插值 `{}` 会被忽略，这在需要行续而不增加内容时很有用。

由于 `string` 就是 `[]char`，字符串和字符数组可以进行比较：

<!--versetest-->
<!-- 51 -->
```verse
"abc" = array{'a', 'b', 'c'}    # Succeeds
"" = array{}                     # Succeeds - empty string equals empty array
```

字符串中的块注释在解析时会被移除：

<!--versetest-->
<!-- 52 -->
```verse
Text := "abc<#this comment is removed#>def"    # Same as "abcdef"
```

### ToString()

`ToString()` 函数将值转换为其字符串表示形式。它是多态的——存在针对不同类型多个重载：

<!--versetest
<#
-->
<!-- 53 -->
```verse
# Signatures
ToString(X:int):string
ToString(X:float):string
ToString(X:char):string
ToString(X:string):string  # Identity function
```
<!-- #> -->

字符串插值会隐式调用嵌入值的 `ToString()`：

<!--versetest-->
<!-- 54 -->
```verse
Age := 25
Score := 98.5

# These are equivalent:
Message1 := "Age: " + ToString(Age) + ", Score: " + ToString(Score)
Message2 := "Age: {Age}, Score: {Score}"
# Both produce: "Age: 25, Score: 98.5"
```

这使得 `ToString()` 对于格式化输出至关重要，即使你不直接调用它也是如此。

`ToString()` 仅适用于基本类型。用户定义的类和结构体没有自动字符串转换。

### ToDiagnostic()

`ToDiagnostic()` 函数将值转换为诊断字符串表示形式，适用于调试和日志记录。与 `ToString()` 类似，但它可能提供更详细或实现特定的信息：

<!--versetest
SomeValue:int=1
-->
<!-- 55 -->
```verse
# Usage (exact signature depends on type)
DiagnosticText := ToDiagnostic(SomeValue)
```

`ToDiagnostic()` 主要用于调试输出，而非面向用户的字符串。其生成的精确格式可能因 VM 实现而异，且不保证跨版本稳定。

## 类型类型

`type` 类型是一种*元类型*——其值本身就是类型。每个 Verse 类型都可以用作 `type` 类型的值。这使得通过参数化函数实现强大的泛型编程成为可能，其中类型是可以传递和约束的参数。

你可以创建保存类型值的变量和参数：

<!--versetest-->
<!-- 75 -->
```verse
# Variable holding a type value
IntType:type = int
StringType:type = string
# Function that takes a type as parameter
CreateDefault(t:type):?t = false
# Usage
X:?int = CreateDefault(int)      # T = int, returns false
Y:?string = CreateDefault(string)  # T = string, returns false
```

所有 Verse 类型都可以作为类型值：

<!-- TODO: Cannot convert - type expressions like []int, [string]int, tuple(), ?int,
     int->string, subtype(), and type{} cannot be assigned to variables at module scope -->

<!--NoCompile-->
<!-- 76 -->
```verse
# Primitives
PrimitiveType:type = int

# User-defined types
my_class := class {}
ClassType:type = my_class

my_struct := struct {Value:int}
StructType:type = my_struct

# Collection types
ArrayType:type = []int
MapType:type = [string]int
TupleType:type = tuple(int, string)
OptionType:type = ?int

# Function types
FuncType:type = int->string

# Parametric types
generic_class(t:type) := class {Data:t}
ParametricType:type = generic_class(int)

# Metatypes
SubtypeValue:type = subtype(my_class)

# Type literals
TypeLiteralValue:type = type{_(:int):string}
```

这种通用性使得 `type` 成为 Verse 泛型编程的基础——任何类型都可以被抽象化。

### 类型参数

`type` 最常见的用途是在 **where 子句**中创建参数化（泛型）函数：

<!--versetest-->
<!-- 77 -->
```verse
# Identity function - works with any type
Identity(X:t where t:type):t = X

# Usage - type parameter inferred
Identity(42)        # t = int
Identity("hello")   # t = string
Identity(true)      # t = logic
```

`where t:type` 约束意味着 "`t` 可以是任何 Verse 类型。" 类型系统从参数推断 `t` 并确保整个函数中的类型安全。

虽然 `where t:type` 接受任何类型，但你可以使用更具体的约束如 `subtype` 来限制哪些类型有效：

<!--versetest
Sort(Items:[]t where t:subtype(comparable)):[]t =
    Items
<#
-->
<!-- 78 -->
```verse
# Only accepts types that are subtypes of comparable
Sort(Items:[]t where t:subtype(comparable)):[]t =
    # Can use comparison operations because t is comparable
    ...
```
<!-- #> -->

有关参数化函数的详细文档，请参见函数章节。

### 类型作为一等值

与许多语言中类型仅存在于编译时不同，Verse 将类型视为*一等值*，可以计算、存储和操作：

<!--versetest-->
<!-- 79 -->
```verse
# Function that returns a type value
GetTypeForSize(Size:int):type =
    if (Size <= 8):
        int
    else:
        string

# Store type in data structure
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
# Helper function that takes a type parameter
CreateArray(ElementType:type, Size:int):[]ElementType =
    # This pattern works in some contexts
    ...

# Function that uses the helper
MakeIntArray():[]int =
    CreateArray(int, 10)
```
<!-- #> -->

### 返回类型参数的可选类型

一种常见模式是让函数返回 `?t`，其中 `t` 是类型参数，允许函数与任何类型一起使用同时可能失败：

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
# return type `t` must be the same type as the `Value` param type
MaybeValue(Value:t, Condition:logic where t:type):?t =
    if (Condition?) then option{Value} else false

# Usage
X:?int = MaybeValue(5, false)  # Returns false as ?int
Y:?float = MaybeValue(3.14, true)  # Returns option{3.14} as ?float
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
# Alternative: explicitly pass the type parameter
MaybeValueExplicit(T:type, Value:t, Condition:logic where t:subtype(T)):?T =
    if (Condition?):
        option{Value}
    else:
        false

# Usage
X:?int = MaybeValueExplicit(int, 5, false)  # Returns false as ?int
Y:?float = MaybeValueExplicit(float, 3.14, true)  # Returns option{3.14} as ?float
# Z:?int = MaybeValueExplicit(int, 3.14, true) # ERROR: float not subtype of int
```
<!-- #> -->

这种模式对于泛型容器和工厂函数尤其有用，它们可能能够也可能无法生成值。

### 类型约束

where 子句中的 `type` 约束是最宽泛的——它接受任何 Verse 类型。对于更具体的要求，Verse 提供了额外的约束：

<!--versetest-->
<!-- 82 -->
```verse
# Most permissive: any type
Generic(X:t where t:type):t = X

# More specific: must be subtype of comparable
RequiresComparison(X:t where t:subtype(comparable))<decides>:void =
    X = X  # Can use = because t is comparable

# Even more specific: must be exact subtype
RequiresExactType(X:t, Y:u where t:type, u:subtype(t)):t =
    X  # Y is guaranteed to be compatible with t
```

类型系统在编译时强制执行这些约束，防止无效的类型使用。

### 限制

虽然 `type` 支持强大的抽象，但也存在一些限制：

**不能泛型地构造任意类型：**

<!--NoCompile-->
<!-- 83 -->
```verse
# Cannot do this - no way to construct a value of arbitrary type t
MakeValue(T:type):T = ???  # What would this return for T=int? T=string?
```

**不能在运行时检查类型结构：**

<!--versetest
<#
-->
<!-- 84 -->
```verse
# Cannot do this - no runtime type introspection
GetFieldNames(T:type):string = ???
```
<!-- #> -->

**类型参数必须被推断或显式指定：**

<!--versetest
Identity(X:t where t:type):t = X

assert:
    Identity(42)

<#
-->
<!-- 85 -->
```verse
# Type parameter must be determinable from usage
Identity(X:t where t:type):t = X

# OK: t inferred from argument
Identity(42)

# ERROR: t cannot be inferred from no arguments
MakeDefault(where t:type):t = ???
```
<!-- #> -->

## Any

`any` 类型是*所有类型的超类型*。语言中的每个类型都是 `any` 的子类型。因此，`any` 本身支持的操作非常少：`any` 提供的任何功能也必须由其他所有类型实现。实际上，你可以直接对 `any` 类型的值进行的操作很少。然而，理解此类型仍然很重要，因为它有时会在处理混合不同类型值的代码中出现，或者当类型检查器无法分配更精确的类型时出现。

`any` 出现的一种情况是组合不共享更具体超类型的值时。例如：

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

在此示例中，`X` 被赋值为 `letters` 类型或 `letter` 类型的值。由于这两种类型不相关，编译器将 `X` 的类型赋为 `any`，即它们的最低公共超类型。

`any` 的另一个更有用的角色是作为语法上需要但实际上未使用的参数类型。当实现需要特定方法签名的接口时，可能会出现这种模式。

<!--versetest-->
<!-- 87 -->
```verse
FirstInt(X:int, :any) : int = X
```

这里，第二个参数被忽略。由于它可以是任何类型的任何值，因此被赋予类型 `any`。

在更通用的代码中，同样的想法可以使用*参数化类型*来表达，使函数既灵活又精确：

<!--versetest-->
<!-- 88 -->
```verse
First(X:t, :any where t:type) : t = X
```

这个版本适用于任何类型 `t`，返回类型为 `t` 的值，同时丢弃 `any` 类型的未使用参数。

## Void

`void` 类型表示缺少有意义的结果，用于不返回结果的场合。从技术上讲，`void` 是一个接受任何值并求值为 `false` 的函数。

这种设计允许返回类型为 `void` 的函数拥有可求值为任何类型的函数体，同时确保调用者无法使用其结果。函数体产生的值会传递给 `void`，它将其丢弃并返回 `false`。

其目的是执行效果而非计算值的函数，其返回类型为 `void`。

<!--versetest-->
<!-- 89 -->
```verse
LogMessage(Msg:string) : void =
    Print(Msg)
```

这里，`LogMessage` 执行一个动作（打印）但不返回结果。`void` 返回类型使这一点明确。
