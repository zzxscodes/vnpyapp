import numpy as np
import pandas as pd
from scipy.stats import percentileofscore

# noinspection PyProtectedMember
from .expanding import expanding_slope, expanding_rsquare, expanding_resi
# noinspection PyProtectedMember
from .rolling import rolling_slope, rolling_rsquare, rolling_resi
from .base import Expression, Feature

np.seterr(invalid="ignore")


# noinspection PyAbstractClass
class ExpressionOps(Expression):
    pass


########################################################################################################################
# Element-Wise Operator #
########################################################################################################################

# noinspection PyAbstractClass
class ElemOperator(ExpressionOps):

    def __init__(self, feature):
        self.feature = feature

    def __str__(self):
        return "{}({})".format(type(self).__name__, self.feature)

    def is_root(self):
        return False


class NpElemOperator(ElemOperator):

    def __init__(self, feature, func):
        self.func = func
        super(NpElemOperator, self).__init__(feature)

    def __call__(self, df):
        series = df.loc[:, self.feature.__str__()] if self.feature.__str__() in df.columns else self.feature
        return getattr(np, self.func)(series)

    def is_root(self):
        condition = isinstance(self.feature, (Feature, float, int, pd.Series))
        return condition


class Abs(NpElemOperator):

    def __init__(self, feature):
        super(Abs, self).__init__(feature, "abs")


class Sign(NpElemOperator):

    def __init__(self, feature):
        super(Sign, self).__init__(feature, "sign")


class Log(NpElemOperator):

    def __init__(self, feature):
        super(Log, self).__init__(feature, "log")


########################################################################################################################
# Pair-Wise Operator #
########################################################################################################################

# noinspection PyAbstractClass
class PairOperator(ExpressionOps):

    def __init__(self, feature_left, feature_right):
        self.feature_left = feature_left
        self.feature_right = feature_right

    def __str__(self):
        return "{}({},{})".format(type(self).__name__, self.feature_left, self.feature_right)


class NpPairOperator(PairOperator):

    def __init__(self, feature_left, feature_right, func):
        self.func = func
        super(NpPairOperator, self).__init__(feature_left, feature_right)

    def __call__(self, df):
        series_left = df.loc[:, self.feature_left.__str__()] \
            if self.feature_left.__str__() in df.columns else self.feature_left
        series_right = df.loc[:, self.feature_right.__str__()] \
            if self.feature_right.__str__() in df.columns else self.feature_right
        return getattr(np, self.func)(series_left, series_right)

    def is_root(self):
        condition1 = isinstance(self.feature_left, (Feature, float, int, pd.Series))
        condition2 = isinstance(self.feature_right, (Feature, float, int, pd.Series))
        return condition1 and condition2


class Power(NpPairOperator):

    def __init__(self, feature_left, feature_right):
        super(Power, self).__init__(feature_left, feature_right, "power")


class Add(NpPairOperator):

    def __init__(self, feature_left, feature_right):
        super(Add, self).__init__(feature_left, feature_right, "add")


class Sub(NpPairOperator):

    def __init__(self, feature_left, feature_right):
        super(Sub, self).__init__(feature_left, feature_right, "subtract")


class Mul(NpPairOperator):

    def __init__(self, feature_left, feature_right):
        super(Mul, self).__init__(feature_left, feature_right, "multiply")


class Div(NpPairOperator):

    def __init__(self, feature_left, feature_right):
        super(Div, self).__init__(feature_left, feature_right, "divide")


class Greater(NpPairOperator):

    def __init__(self, feature_left, feature_right):
        super(Greater, self).__init__(feature_left, feature_right, "maximum")


class Less(NpPairOperator):

    def __init__(self, feature_left, feature_right):
        super(Less, self).__init__(feature_left, feature_right, "minimum")


class Gt(NpPairOperator):

    def __init__(self, feature_left, feature_right):
        super(Gt, self).__init__(feature_left, feature_right, "greater")


class Ge(NpPairOperator):

    def __init__(self, feature_left, feature_right):
        super(Ge, self).__init__(feature_left, feature_right, "greater_equal")


class Lt(NpPairOperator):

    def __init__(self, feature_left, feature_right):
        super(Lt, self).__init__(feature_left, feature_right, "less")


class Le(NpPairOperator):

    def __init__(self, feature_left, feature_right):
        super(Le, self).__init__(feature_left, feature_right, "less_equal")


class Eq(NpPairOperator):

    def __init__(self, feature_left, feature_right):
        super(Eq, self).__init__(feature_left, feature_right, "equal")


class Ne(NpPairOperator):

    def __init__(self, feature_left, feature_right):
        super(Ne, self).__init__(feature_left, feature_right, "not_equal")


class And(NpPairOperator):

    def __init__(self, feature_left, feature_right):
        super(And, self).__init__(feature_left, feature_right, "bitwise_and")


class Or(NpPairOperator):

    def __init__(self, feature_left, feature_right):
        super(Or, self).__init__(feature_left, feature_right, "bitwise_or")


########################################################################################################################
# Triple-wise Operator #
########################################################################################################################

class If(ExpressionOps):

    def __init__(self, condition, feature_left, feature_right):
        self.condition = condition
        self.feature_left = feature_left
        self.feature_right = feature_right

    def __str__(self):
        return "If({},{},{})".format(self.condition, self.feature_left, self.feature_right)

    def __call__(self, df):
        return df.loc[:, self.feature_left].where(df.loc[:, self.condition], df.loc[:, self.feature_right])

    def is_root(self):
        condition1 = isinstance(self.feature_left, (Feature, float, int, pd.Series))
        condition2 = isinstance(self.feature_right, (Feature, float, int, pd.Series))
        condition3 = isinstance(self.condition, (Feature, float, int, pd.Series))
        return condition1 and condition2 and condition3


########################################################################################################################
# Rolling #
########################################################################################################################

# NOTE: methods like `rolling.mean` are optimized with cython,
# and are super faster than `rolling.apply(np.mean)`


class Rolling(ExpressionOps):

    def __init__(self, feature, n, func):
        self.feature = feature
        self.n = n
        self.func = func

    def __str__(self):
        return "{}({},{})".format(type(self).__name__, self.feature, self.n)

    def __call__(self, df):
        series = df.loc[:, self.feature.__str__()] if self.feature.__str__() in df.columns else self.feature
        return getattr(series.rolling(self.n, min_periods=1), self.func)()

    def is_root(self):
        condition = isinstance(self.feature, (float, int, pd.Series))
        return condition


class Ref(Rolling):

    def __init__(self, feature, n):
        super(Ref, self).__init__(feature, n, "ref")

    def __call__(self, df):
        series = df.loc[:, self.feature.__str__()] if self.feature.__str__() in df.columns else self.feature
        return series.shift(self.n)


class Mean(Rolling):

    def __init__(self, feature, n):
        super(Mean, self).__init__(feature, n, "mean")


class Sum(Rolling):

    def __init__(self, feature, n):
        super(Sum, self).__init__(feature, n, "sum")


class Std(Rolling):

    def __init__(self, feature, n):
        super(Std, self).__init__(feature, n, "std")


class Var(Rolling):

    def __init__(self, feature, n):
        super(Var, self).__init__(feature, n, "var")


class Skew(Rolling):

    def __init__(self, feature, n):
        if n != 0 and n < 3:
            raise ValueError("The rolling window size of Skewness operation should >= 3")
        super(Skew, self).__init__(feature, n, "skew")


class Kurt(Rolling):

    def __init__(self, feature, n):
        if n != 0 and n < 4:
            raise ValueError("The rolling window size of Kurtosis operation should >= 5")
        super(Kurt, self).__init__(feature, n, "kurt")


class Max(Rolling):

    def __init__(self, feature, n):
        super(Max, self).__init__(feature, n, "max")


class IdxMax(Rolling):

    def __init__(self, feature, n):
        super(IdxMax, self).__init__(feature, n, "idxmax")

    def __call__(self, df):
        series = df.loc[:, self.feature.__str__()] if self.feature.__str__() in df.columns else self.feature
        if self.n == 0:
            series = series.expanding(min_periods=1).apply(lambda x: x.argmin() + 1, raw=True)
        else:
            series = series.rolling(self.n, min_periods=1).apply(lambda x: x.argmin() + 1, raw=True)
        return series


class Min(Rolling):

    def __init__(self, feature, n):
        super(Min, self).__init__(feature, n, "min")


class IdxMin(Rolling):

    def __init__(self, feature, n):
        super(IdxMin, self).__init__(feature, n, "idxmin")

    def __call__(self, df):
        series = df.loc[:, self.feature.__str__()] if self.feature.__str__() in df.columns else self.feature
        if self.n == 0:
            series = series.expanding(min_periods=1).apply(lambda x: x.argmin() + 1, raw=True)
        else:
            series = series.rolling(self.n, min_periods=1).apply(lambda x: x.argmin() + 1, raw=True)
        return series


class Quantile(Rolling):

    def __init__(self, feature, n, qscore):
        super(Quantile, self).__init__(feature, n, "quantile")
        self.qscore = qscore

    def __str__(self):
        return "{}({},{},{})".format(type(self).__name__, self.feature, self.n, self.qscore)

    def __call__(self, df):
        series = df.loc[:, self.feature.__str__()] if self.feature.__str__() in df.columns else self.feature
        if self.n == 0:
            series = series.expanding(min_periods=1).apply(lambda x: np.quantile(x, self.qscore), raw=True)
        else:
            series = series.rolling(self.n, min_periods=1).apply(lambda x: np.quantile(x, self.qscore), raw=True)
        return series


class Med(Rolling):

    def __init__(self, feature, n):
        super(Med, self).__init__(feature, n, "median")


class Mad(Rolling):

    def __init__(self, feature, n):
        super(Mad, self).__init__(feature, n, "mad")

    def __call__(self, df):
        series = df.loc[:, self.feature.__str__()] if self.feature.__str__() in df.columns else self.feature

        def mad(x):
            x1 = x[~np.isnan(x)]
            return np.mean(np.abs(x1 - x1.mean()))

        if self.n == 0:
            series = series.expanding(min_periods=1).apply(mad, raw=True)
        else:
            series = series.rolling(self.n, min_periods=1).apply(mad, raw=True)
        return series


class Rank(Rolling):

    def __init__(self, feature, n):
        super(Rank, self).__init__(feature, n, "rank")

    def __call__(self, df):
        series = df.loc[:, self.feature.__str__()] if self.feature.__str__() in df.columns else self.feature
        rolling_or_expending = series.expanding(min_periods=1) if self.n == 0 else series.rolling(self.n, min_periods=1)
        if hasattr(rolling_or_expending, "rank"):
            return rolling_or_expending.rank(pct=True)

        def rank(x):
            if np.isnan(x[-1]):
                return np.nan
            x1 = x[~np.isnan(x)]
            if x1.shape[0] == 0:
                return np.nan
            return percentileofscore(x1, x1[-1]) / 100

        return rolling_or_expending.apply(rank, raw=True)


class Count(Rolling):

    def __init__(self, feature, n):
        super(Count, self).__init__(feature, n, "count")


class Delta(Rolling):

    def __init__(self, feature, n):
        super(Delta, self).__init__(feature, n, "delta")

    def __call__(self, df):
        series = df.loc[:, self.feature.__str__()] if self.feature.__str__() in df.columns else self.feature
        if self.n == 0:
            series = series - series.iloc[0]
        else:
            series = series - series.shift(self.n)
        return series


# support pair-wise rolling like `Slope(A, B, N)`
class Slope(Rolling):

    def __init__(self, feature, n):
        super(Slope, self).__init__(feature, n, "slope")

    def __call__(self, df):
        series = df.loc[:, self.feature.__str__()] if self.feature.__str__() in df.columns else self.feature
        if self.n == 0:
            series = pd.Series(expanding_slope(series.values), index=series.index)
        else:
            series = pd.Series(rolling_slope(series.values, self.n), index=series.index)
        return series


class Rsquare(Rolling):

    def __init__(self, feature, n):
        super(Rsquare, self).__init__(feature, n, "rsquare")

    def __call__(self, df):
        series = df.loc[:, self.feature.__str__()] if self.feature.__str__() in df.columns else self.feature
        if self.n == 0:
            series = pd.Series(expanding_rsquare(series.values), index=series.index)
        else:
            series = pd.Series(rolling_rsquare(series.values, self.n), index=series.index)
            series.loc[np.isclose(series.rolling(self.n, min_periods=1).std(), 0, atol=2e-05)] = np.nan
        return series


class Resi(Rolling):

    def __init__(self, feature, n):
        super(Resi, self).__init__(feature, n, "resi")

    def __call__(self, df):
        series = df.loc[:, self.feature.__str__()] if self.feature.__str__() in df.columns else self.feature
        if self.n == 0:
            series = pd.Series(expanding_resi(series.values), index=series.index)
        else:
            series = pd.Series(rolling_resi(series.values, self.n), index=series.index)
        return series


class WMA(Rolling):

    def __init__(self, feature, n):
        super(WMA, self).__init__(feature, n, "wma")

    def __call__(self, df):
        series = df.loc[:, self.feature.__str__()] if self.feature.__str__() in df.columns else self.feature

        def weighted_mean(x):
            w = np.arange(len(x)) + 1
            w = w / w.sum()
            return np.nanmean(w * x)

        if self.n == 0:
            series = series.expanding(min_periods=1).apply(weighted_mean, raw=True)
        else:
            series = series.rolling(self.n, min_periods=1).apply(weighted_mean, raw=True)
        return series


class EMA(Rolling):

    def __init__(self, feature, n):
        super(EMA, self).__init__(feature, n, "ema")

    def __call__(self, df):
        series = df.loc[:, self.feature.__str__()] if self.feature.__str__() in df.columns else self.feature

        def exp_weighted_mean(x):
            a = 1 - 2 / (1 + len(x))
            w = a ** np.arange(len(x))[::-1]
            w /= w.sum()
            return np.nansum(w * x)

        if self.n == 0:
            series = series.expanding(min_periods=1).apply(exp_weighted_mean, raw=True)
        elif 0 < self.n < 1:
            series = series.ewm(alpha=self.n, min_periods=1).mean()
        else:
            series = series.ewm(span=self.n, min_periods=1).mean()
        return series


########################################################################################################################
# Pair-Wise Rolling #
########################################################################################################################

class PairRolling(ExpressionOps):

    def __init__(self, feature_left, feature_right, n, func):
        self.feature_left = feature_left
        self.feature_right = feature_right
        self.n = n
        self.func = func

    def __str__(self):
        return "{}({},{},{})".format(type(self).__name__, self.feature_left, self.feature_right, self.n)

    def __call__(self, df):
        series_left = df.loc[:, self.feature_left.__str__()] \
            if self.feature_left.__str__() in df.columns else self.feature_left
        series_right = df.loc[:, self.feature_right.__str__()] \
            if self.feature_right.__str__() in df.columns else self.feature_right

        if self.n == 0:
            series = getattr(series_left.expanding(min_periods=1), self.func)(series_right)
        else:
            series = getattr(series_left.rolling(self.n, min_periods=1), self.func)(series_right)
        return series

    def is_root(self):
        condition1 = isinstance(self.feature_left, (Feature, float, int, pd.Series))
        condition2 = isinstance(self.feature_right, (Feature, float, int, pd.Series))
        return condition1 and condition2


class Corr(PairRolling):

    def __init__(self, feature_left, feature_right, n):
        super(Corr, self).__init__(feature_left, feature_right, n, "corr")


class Cov(PairRolling):

    def __init__(self, feature_left, feature_right, n):
        super(Cov, self).__init__(feature_left, feature_right, n, "cov")


OpsList = [
    Rolling,
    Ref,
    Max,
    Min,
    Sum,
    Mean,
    Std,
    Var,
    Skew,
    Kurt,
    Med,
    Mad,
    Slope,
    Rsquare,
    Resi,
    Rank,
    Quantile,
    Count,
    EMA,
    WMA,
    Corr,
    Cov,
    Delta,
    Abs,
    Sign,
    Log,
    Power,
    Add,
    Sub,
    Mul,
    Div,
    Greater,
    Less,
    And,
    Or,
    Gt,
    Ge,
    Lt,
    Le,
    Eq,
    Ne,
    IdxMax,
    IdxMin,
    If,
]


class OpsWrapper:
    """Ops Wrapper"""

    def __init__(self):
        self._ops = {}

    def reset(self):
        self._ops = {}

    def register(self, ops_list):
        """register operator

        Parameters
        ----------
        ops_list
            - if type(ops_list) is List[Type[ExpressionOps]], each element of ops_list represents the operator class,
            which should be the subclass of `ExpressionOps`.
            - if type(ops_list) is List[dict], each element of ops_list represents the config of operator,
            which has the following format:

                code-block:: text

                    {
                        "class": class_name,
                        "module_path": path,
                    }

                Note: `class` should be the class name of operator, `module_path` should be a python module
                or path of file.
        """
        for _operator in ops_list:

            _ops_class = _operator

            if not issubclass(_ops_class, (ExpressionOps,)):
                raise TypeError("operator must be subclass of ExpressionOps, not {}".format(_ops_class))

            if _ops_class.__name__ in self._ops:
                raise ValueError("The operator [{0}] has already been registered".format(_ops_class.__name__))
            self._ops[_ops_class.__name__] = _ops_class

    def __getattr__(self, key):
        if key not in self._ops:
            raise AttributeError("The operator [{0}] is not registered".format(key))
        return self._ops[key]


Operators = OpsWrapper()
Operators.reset()
Operators.register(OpsList)
