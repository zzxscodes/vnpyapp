import numpy as np


class Expanding:
    """
    1-D array expanding
    """

    def __init__(self):
        self.barv = list()
        self.na_count = 0

    def update(self, val: float) -> float:
        pass


class Mean(Expanding):
    def __init__(self):
        super(Mean, self).__init__()
        self.vsum = 0

    def update(self, val: float) -> float:
        self.barv.append(val)
        if np.isnan(val):
            self.na_count += 1
        else:
            self.vsum += val
        return self.vsum / (len(self.barv) - self.na_count)


# noinspection PyPep8Naming
class Slope(Expanding):
    """

    """

    def __init__(self):
        super(Slope, self).__init__()
        self.x_sum = 0
        self.x2_sum = 0
        self.y_sum = 0
        self.xy_sum = 0

    def update(self, val: float) -> float:
        self.barv.append(val)
        size = len(self.barv)
        if np.isnan(val):
            self.na_count += 1
        else:
            self.x_sum += size
            self.x2_sum += size * size
            self.y_sum += val
            self.xy_sum += size * val
        N = size - self.na_count
        return (N * self.xy_sum - self.x_sum * self.y_sum) / (N * self.x2_sum - self.x_sum * self.x_sum)


# noinspection PyPep8Naming
class Resi(Expanding):
    """

    """

    def __init__(self):
        super(Resi, self).__init__()
        self.x_sum = 0
        self.x2_sum = 0
        self.y_sum = 0
        self.xy_sum = 0

    def update(self, val: float) -> float:
        self.barv.append(val)
        size = len(self.barv)
        if np.isnan(val):
            self.na_count += 1
        else:
            self.x_sum += size
            self.x2_sum += size * size
            self.y_sum += val
            self.xy_sum += size * val
        N = size - self.na_count
        slope = (N * self.xy_sum - self.x_sum * self.y_sum) / (N * self.x2_sum - self.x_sum * self.x_sum)
        x_mean = self.x_sum / N
        y_mean = self.y_sum / N
        interp = y_mean - slope * x_mean
        return val - (slope * size + interp)


# noinspection PyPep8Naming
class Rsquare(Expanding):
    """

    """

    def __init__(self):
        super(Rsquare, self).__init__()
        self.x_sum = 0
        self.x2_sum = 0
        self.y_sum = 0
        self.y2_sum = 0
        self.xy_sum = 0

    def update(self, val: float) -> float:
        self.barv.append(val)
        size = len(self.barv)
        if np.isnan(val):
            self.na_count += 1
        else:
            self.x_sum += size
            self.x2_sum += size * size
            self.y_sum += val
            self.y2_sum += val * val
            self.xy_sum += size * val
        N = size - self.na_count
        rvalue = (N * self.xy_sum - self.x_sum * self.y_sum) / np.sqrt(
            (N * self.x2_sum - self.x_sum * self.x_sum) * (N * self.y2_sum - self.y_sum * self.y_sum))
        return rvalue * rvalue


# noinspection PyPep8Naming
def expanding(r: Expanding, a: np.array) -> np.array:
    N = len(a)
    ret = np.empty(N)
    for i in range(N):
        ret[i] = r.update(a[i])
    return ret


def expanding_mean(a: np.array) -> np.array:
    r = Mean()
    return expanding(r, a)


def expanding_slope(a: np.array) -> np.array:
    r = Slope()
    return expanding(r, a)


def expanding_rsquare(a: np.array) -> np.array:
    r = Rsquare()
    return expanding(r, a)


def expanding_resi(a: np.array) -> np.array:
    r = Resi()
    return expanding(r, a)
