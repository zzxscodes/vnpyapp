import unittest

import lightgbm as lgb
import pandas as pd


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.features = pd.read_pickle('../mean_train.pkl').index
        self.model = lgb.Booster(model_file='../model.txt')
        print(pd.Series(self.model.feature_importance(), index=self.features).sort_values())
        """
p_roll_w50_fsum       0
wap2_l1_w15_fsum      0
wap1_l1_w15_fsum      0
p_roll_w15_fsum       0
wap2_l5_w10_fsum      0
                   ... 
wap1_l1_w10_fstd    451
p_roll_w15_fskew    520
wap1_l1_w15_fstd    807
r_roll_w10_fmean    872
r_roll_w15_fmean    944
        """

if __name__ == '__main__':
    unittest.main()
