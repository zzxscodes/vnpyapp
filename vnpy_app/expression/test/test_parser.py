import unittest

import pandas as pd

from vnpy_app.expression.parser import calculate_field


def parse_config_to_fields(config=None):
    if config is None:
        config = {
            "kbar": {},
            "price": {
                "windows": [0],
                "feature": ["OPEN", "HIGH", "LOW", "VWAP"],
            },
            "rolling": {},
        }
    fields = []
    names = []
    if "kbar" in config:
        fields += [
            "($close-$open)/$open",
            "($high-$low)/$open",
            "($close-$open)/($high-$low+1e-12)",
            "($high-Greater($open, $close))/$open",
            "($high-Greater($open, $close))/($high-$low+1e-12)",
            "(Less($open, $close)-$low)/$open",
            "(Less($open, $close)-$low)/($high-$low+1e-12)",
            "(2*$close-$high-$low)/$open",
            "(2*$close-$high-$low)/($high-$low+1e-12)",
        ]
        names += [
            "KMID",
            "KLEN",
            "KMID2",
            "KUP",
            "KUP2",
            "KLOW",
            "KLOW2",
            "KSFT",
            "KSFT2",
        ]
    if "price" in config:
        windows = config["price"].get("windows", range(5))
        feature = config["price"].get("feature", ["OPEN", "HIGH", "LOW", "CLOSE", "VWAP"])
        for field in feature:
            # noinspection PyUnresolvedReferences
            field = field.lower()
            fields += ["Ref($%s, %d)/$close" % (field, d) if d != 0 else "$%s/$close" % field for d in windows]
            names += [field.upper() + str(d) for d in windows]
    if "volume" in config:
        windows = config["volume"].get("windows", range(5))
        fields += ["Ref($volume, %d)/$volume" % d if d != 0 else "$volume/$volume" for d in windows]
        names += ["VOLUME" + str(d) for d in windows]
    if "rolling" in config:
        windows = config["rolling"].get("windows", [5, 10, 20, 30, 60])
        include = config["rolling"].get("include", None)
        exclude = config["rolling"].get("exclude", [])
        # `exclude` in dataset config unnecessary filed
        # `include` in dataset config necessary field
        use = lambda x: x not in exclude and (include is None or x in include)
        if use("ROC"):
            fields += ["Ref($close, %d)/$close" % d for d in windows]
            names += ["ROC%d" % d for d in windows]
        if use("MA"):
            fields += ["Mean($close, %d)/$close" % d for d in windows]
            names += ["MA%d" % d for d in windows]
        if use("STD"):
            fields += ["Std($close, %d)/$close" % d for d in windows]
            names += ["STD%d" % d for d in windows]
        if use("BETA"):
            fields += ["Slope($close, %d)/$close" % d for d in windows]
            names += ["BETA%d" % d for d in windows]
        if use("RSQR"):
            fields += ["Rsquare($close, %d)" % d for d in windows]
            names += ["RSQR%d" % d for d in windows]
        if use("RESI"):
            fields += ["Resi($close, %d)/$close" % d for d in windows]
            names += ["RESI%d" % d for d in windows]
        if use("MAX"):
            fields += ["Max($high, %d)/$close" % d for d in windows]
            names += ["MAX%d" % d for d in windows]
        if use("LOW"):
            fields += ["Min($low, %d)/$close" % d for d in windows]
            names += ["MIN%d" % d for d in windows]
        if use("QTLU"):
            fields += ["Quantile($close, %d, 0.8)/$close" % d for d in windows]
            names += ["QTLU%d" % d for d in windows]
        if use("QTLD"):
            fields += ["Quantile($close, %d, 0.2)/$close" % d for d in windows]
            names += ["QTLD%d" % d for d in windows]
        if use("RANK"):
            fields += ["Rank($close, %d)" % d for d in windows]
            names += ["RANK%d" % d for d in windows]
        if use("RSV"):
            fields += ["($close-Min($low, %d))/(Max($high, %d)-Min($low, %d)+1e-12)" % (d, d, d) for d in windows]
            names += ["RSV%d" % d for d in windows]
        if use("IMAX"):
            fields += ["IdxMax($high, %d)/%d" % (d, d) for d in windows]
            names += ["IMAX%d" % d for d in windows]
        if use("IMIN"):
            fields += ["IdxMin($low, %d)/%d" % (d, d) for d in windows]
            names += ["IMIN%d" % d for d in windows]
        if use("IMXD"):
            fields += ["(IdxMax($high, %d)-IdxMin($low, %d))/%d" % (d, d, d) for d in windows]
            names += ["IMXD%d" % d for d in windows]
        if use("CORR"):
            fields += ["Corr($close, Log($volume+1), %d)" % d for d in windows]
            names += ["CORR%d" % d for d in windows]
        if use("CORD"):
            fields += ["Corr($close/Ref($close,1), Log($volume/Ref($volume, 1)+1), %d)" % d for d in windows]
            names += ["CORD%d" % d for d in windows]
        if use("CNTP"):
            fields += ["Mean($close>Ref($close, 1), %d)" % d for d in windows]
            names += ["CNTP%d" % d for d in windows]
        if use("CNTN"):
            fields += ["Mean($close<Ref($close, 1), %d)" % d for d in windows]
            names += ["CNTN%d" % d for d in windows]
        if use("CNTD"):
            fields += ["Mean($close>Ref($close, 1), %d)-Mean($close<Ref($close, 1), %d)" % (d, d) for d in windows]
            names += ["CNTD%d" % d for d in windows]
        if use("SUMP"):
            fields += [
                "Sum(Greater($close-Ref($close, 1), 0), %d)/(Sum(Abs($close-Ref($close, 1)), %d)+1e-12)" % (d, d)
                for d in windows
            ]
            names += ["SUMP%d" % d for d in windows]
        if use("SUMN"):
            fields += [
                "Sum(Greater(Ref($close, 1)-$close, 0), %d)/(Sum(Abs($close-Ref($close, 1)), %d)+1e-12)" % (d, d)
                for d in windows
            ]
            names += ["SUMN%d" % d for d in windows]
        if use("SUMD"):
            fields += [
                "(Sum(Greater($close-Ref($close, 1), 0), %d)-Sum(Greater(Ref($close, 1)-$close, 0), %d))"
                "/(Sum(Abs($close-Ref($close, 1)), %d)+1e-12)" % (d, d, d)
                for d in windows
            ]
            names += ["SUMD%d" % d for d in windows]
        if use("VMA"):
            fields += ["Mean($volume, %d)/($volume+1e-12)" % d for d in windows]
            names += ["VMA%d" % d for d in windows]
        if use("VSTD"):
            fields += ["Std($volume, %d)/($volume+1e-12)" % d for d in windows]
            names += ["VSTD%d" % d for d in windows]
        if use("WVMA"):
            fields += [
                "Std(Abs($close/Ref($close, 1)-1)*$volume, %d)/(Mean(Abs($close/Ref($close, 1)-1)*$volume, %d)+1e-12)"
                % (d, d)
                for d in windows
            ]
            names += ["WVMA%d" % d for d in windows]
        if use("VSUMP"):
            fields += [
                "Sum(Greater($volume-Ref($volume, 1), 0), %d)/(Sum(Abs($volume-Ref($volume, 1)), %d)+1e-12)"
                % (d, d)
                for d in windows
            ]
            names += ["VSUMP%d" % d for d in windows]
        if use("VSUMN"):
            fields += [
                "Sum(Greater(Ref($volume, 1)-$volume, 0), %d)/(Sum(Abs($volume-Ref($volume, 1)), %d)+1e-12)"
                % (d, d)
                for d in windows
            ]
            names += ["VSUMN%d" % d for d in windows]
        if use("VSUMD"):
            fields += [
                "(Sum(Greater($volume-Ref($volume, 1), 0), %d)-Sum(Greater(Ref($volume, 1)-$volume, 0), %d))"
                "/(Sum(Abs($volume-Ref($volume, 1)), %d)+1e-12)" % (d, d, d)
                for d in windows
            ]
            names += ["VSUMD%d" % d for d in windows]

    return fields, names


class MyTestCase(unittest.TestCase):
    def setUp(self):
        fields, names = parse_config_to_fields()
        self.calculate_field = calculate_field
        self.fields, self.names = fields, names

    def test_something(self):
        # Sample DataFrame
        data = {
            '$close': [100, 101, 102, 103, 104, 105, 106, 107, 108, 109],
            '$open': [99, 100, 101, 102, 103, 104, 105, 106, 107, 108],
            '$high': [101, 102, 103, 104, 105, 106, 107, 108, 109, 110],
            '$low': [98, 99, 100, 101, 102, 103, 104, 105, 106, 107],
            '$volume': [1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000],
            '$vwap': [100, 100, 100, 100, 100, 100, 100, 100, 100, 100],
        }
        date_idx = pd.date_range('2019-01-01', '2019-01-10')
        df = pd.DataFrame(data, index=date_idx)
        for index, field in enumerate(self.fields):
            print(index)
            print(field)
            print(self.calculate_field(df, field))


if __name__ == '__main__':
    unittest.main()
