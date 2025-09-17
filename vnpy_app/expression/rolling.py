import numpy as np


class Rolling:
    def __init__(self, window: int):
        self.window = window
        self.na_count = window
        self.barv = list()
        for i in range(window):
            self.barv.append(np.nan)

    def update(self, val: float) -> float:
        pass


class Mean(Rolling):
    """
    1-D array rolling mean
    """

    def __init__(self, window: int):
        super(Mean, self).__init__(window=window)
        self.vsum = 0

    def update(self, val: float) -> float:
        self.barv.append(val)
        if not np.isnan(self.barv[0]):
            self.vsum -= self.barv[0]
        else:
            self.na_count -= 1
        self.barv = self.barv[1:]
        if np.isnan(val):
            self.na_count += 1
        else:
            self.vsum += val
        return self.vsum / (self.window - self.na_count)


# noinspection PyPep8Naming
class Slope(Rolling):
    """

    """

    def __init__(self, window: int):
        super(Slope, self).__init__(window)
        self.i_sum = 0
        self.x_sum = 0
        self.x2_sum = 0
        self.y_sum = 0
        self.xy_sum = 0

    def update(self, val: float) -> float:
        self.barv.append(val)
        self.xy_sum = self.xy_sum - self.y_sum
        self.x2_sum = self.x2_sum + self.i_sum - 2 * self.x_sum
        self.x_sum = self.x_sum - self.i_sum
        _val = self.barv[0]
        if not np.isnan(_val):
            self.i_sum -= 1
            self.y_sum -= _val
        else:
            self.na_count -= 1
        self.barv = self.barv[1:]
        if np.isnan(val):
            self.na_count += 1
        else:
            self.i_sum += 1
            self.x_sum += self.window
            self.x2_sum += self.window * self.window
            self.y_sum += val
            self.xy_sum += self.window * val
        N = self.window - self.na_count
        return (N * self.xy_sum - self.x_sum * self.y_sum) / (N * self.x2_sum - self.x_sum * self.x_sum)


# noinspection PyPep8Naming
class Resi(Rolling):
    """

    """

    def __init__(self, window: int):
        super(Resi, self).__init__(window)
        self.i_sum = 0
        self.x_sum = 0
        self.x2_sum = 0
        self.y_sum = 0
        self.xy_sum = 0

    def update(self, val: float) -> float:
        self.barv.append(val)
        self.xy_sum = self.xy_sum - self.y_sum
        self.x2_sum = self.x2_sum + self.i_sum - 2 * self.x_sum
        self.x_sum = self.x_sum - self.i_sum
        _val = self.barv[0]
        if not np.isnan(_val):
            self.i_sum -= 1
            self.y_sum -= _val
        else:
            self.na_count -= 1
        self.barv = self.barv[1:]
        if np.isnan(val):
            self.na_count += 1
            # return NAN
        else:
            self.i_sum += 1
            self.x_sum += self.window
            self.x2_sum += self.window * self.window
            self.y_sum += val
            self.xy_sum += self.window * val
        N = self.window - self.na_count
        slope = (N * self.xy_sum - self.x_sum * self.y_sum) / (N * self.x2_sum - self.x_sum * self.x_sum)
        x_mean = self.x_sum / N
        y_mean = self.y_sum / N
        interp = y_mean - slope * x_mean
        return val - (slope * self.window + interp)


# noinspection PyPep8Naming
class Rsquare(Rolling):
    """

    """

    def __init__(self, window: int):
        super(Rsquare, self).__init__(window)
        self.i_sum = 0
        self.x_sum = 0
        self.x2_sum = 0
        self.y_sum = 0
        self.y2_sum = 0
        self.xy_sum = 0

    def update(self, val: float) -> float:
        self.barv.append(val)
        self.xy_sum = self.xy_sum - self.y_sum
        self.x2_sum = self.x2_sum + self.i_sum - 2 * self.x_sum
        self.x_sum = self.x_sum - self.i_sum
        _val = self.barv[0]
        if not np.isnan(_val):
            self.i_sum -= 1
            self.y_sum -= _val
            self.y2_sum -= _val * _val
        else:
            self.na_count -= 1
        self.barv = self.barv[1:]
        if np.isnan(val):
            self.na_count += 1
            # return NAN
        else:
            self.i_sum += 1
            self.x_sum += self.window
            self.x2_sum += self.window * self.window
            self.y_sum += val
            self.y2_sum += val * val
            self.xy_sum += self.window * val
        N = self.window - self.na_count
        rvalue = (N * self.xy_sum - self.x_sum * self.y_sum) / np.sqrt(
            (N * self.x2_sum - self.x_sum * self.x_sum) * (N * self.y2_sum - self.y_sum * self.y_sum))
        return rvalue * rvalue


# noinspection PyPep8Naming
def rolling(r: Rolling, a: np.array) -> np.array:
    N = len(a)
    ret = np.empty(N)
    for i in range(N):
        try:
            ret[i] = r.update(a[i])
        except ZeroDivisionError:
            ret[i] = ret[i - 1]
    return ret


def rolling_mean(a: np.array, window: int) -> np.array:
    r = Mean(window)
    return rolling(r, a)


def rolling_slope(a: np.array, window: int) -> np.array:
    r = Slope(window)
    return rolling(r, a)


def rolling_rsquare(a: np.array, window: int) -> np.array:
    r = Rsquare(window)
    return rolling(r, a)


def rolling_resi(a: np.array, window: int) -> np.array:
    r = Resi(window)
    return rolling(r, a)
