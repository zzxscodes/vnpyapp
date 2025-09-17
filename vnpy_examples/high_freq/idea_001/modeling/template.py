import lightgbm as lgb
import numpy as np
import pandas as pd
from scipy.stats import pearsonr
from scipy.stats import spearmanr

from vnpy_app.processor import *
from vnpy_app.utility.log import TimeInspector
from vnpy_app.utility.log import get_module_logger
from vnpy_examples.high_freq.idea_001.modeling.factors import FactorCollection

logger = get_module_logger('user.' + __name__)
timer_logger = get_module_logger('system.timer')
logger.logger.disabled = False
timer_logger.logger.disabled = True


def spearman_metric(y_true, y_pred):
    corr, _ = spearmanr(y_true, y_pred.label)
    if np.isnan(corr):
        corr = 0.0
    return "spearman", corr, True


def pearson_metric(y_true, y_pred):
    corr, _ = pearsonr(y_true, y_pred.label)
    if np.isnan(corr):
        corr = 0.0
    return "pearson", corr, True


def mse(y_true, y_pred):
    return 'mse', np.mean((y_true - y_pred.label) ** 2), False


def get_factors(df):
    fc = FactorCollection(df)
    windows = fc.rolling_windows
    functions = fc.functions
    levels = [i for i in range(1, 6)]
    c = dict()
    logger.info('calculating collection001')
    for l in levels:
        for w in windows:
            for f in functions:
                with TimeInspector.logt(f'calculating {f} {w} {l}'):
                    c[f'wap1_l{l}_w{w}_f{f}'] = fc.calc_wap1(l, w, f)
                    c[f'wap2_l{l}_w{w}_f{f}'] = fc.calc_wap2(l, w, f)
                    c[f'vr_l{l}_w{w}_f{f}'] = fc.volume_ratio(l, w, f)
    logger.info('calculating collection002')
    for w in windows:
        for f in functions:
            with TimeInspector.logt(f'calculating {f} {w}'):
                c[f'p_roll_w{w}_f{f}'] = fc.p_rolling_stat(w, f)
                c[f'r_roll_w{w}_f{f}'] = fc.rtn_rolling_stat(w, f)
    logger.info('calculating collection003')
    for w in windows:
        with TimeInspector.logt(f'calculating {w}'):
            c[f'rv_roll_w{w}'] = fc.rv_rolling_corr(w)
    c['label'] = fc.label()
    c['datetime'] = df['datetime']
    c['instrument'] = df['symbol']
    df_factors = pd.DataFrame(c)
    return df_factors


def get_segments():
    logger.info('loading dataset')
    df = pd.read_parquet('dataset.parquet')
    segments = {
        'train': ('2022-07-05', '2022-08-01'),
        'valid': ('2022-08-01', '2022-08-10'),
        'test': ('2022-08-10', '2022-09-01')
    }
    df = df.loc[segments['train'][0]:segments['test'][1]]
    df.sort_index(inplace=True)
    df.columns = pd.MultiIndex.from_tuples([('feature', i) if i != 'label' else ('label', i) for i in df.columns])
    logger.info('normalizing')
    p1 = RobustZScoreNorm(segments['train'][0], segments['train'][1], fields_group='feature')
    p1.fit(df)
    mean_train = p1.mean_train
    std_train = p1.std_train
    feature_names = df['feature'].columns
    pd.Series(mean_train, index=feature_names).to_pickle('mean_train.pkl')
    pd.Series(std_train, index=feature_names).to_pickle('std_train.pkl')
    df = p1(df)
    logger.info('filling na')
    p2 = Fillna(fields_group='feature')
    df = p2(df)
    logger.info('dropping na label')
    p3 = DropnaLabel()
    df = p3(df)
    c = dict()
    for k, v in segments.items():
        beg, end = v
        c[k] = df.loc[beg:end].copy()
    return c


def train_regress_model():
    c = get_segments()
    train_ds = lgb.Dataset(c['train']['feature'], label=c['train']['label'])
    valid_ds = lgb.Dataset(c['valid']['feature'], label=c['valid']['label'])
    callbacks = [
        lgb.log_evaluation(period=10),
        lgb.early_stopping(stopping_rounds=10)
    ]
    model = lgb.train(
        params={
            'objective': 'mse',
            'verbosity': -1,
            'boosting_type': 'gbdt',
            'learning_rate': 0.01,
            'num_leaves': 31,
            'feature_fraction': 0.8,
            'bagging_fraction': 0.8,
            'bagging_freq': 5,
            'min_child_samples': 20,
        },
        train_set=train_ds,
        valid_sets=[train_ds, valid_ds],
        valid_names=['train', 'valid'],
        feval=[mse, pearson_metric, spearman_metric],
        callbacks=callbacks,
        num_boost_round=1000,
    )
    model.save_model('model.txt')


def regress_model():
    c = get_segments()
    model = lgb.Booster(model_file='model.txt')
    test = lgb.Dataset(c['test']['feature'], label=c['test']['label'])
    logger.info('predicting')
    predictions = model.predict(test.data).reshape(-1, 1)
    logger.info('calculating metrics')
    labels = c['test']['label'].values
    df = pd.DataFrame({'predictions': predictions[:, 0], 'labels': labels[:, 0]}, index=c['test'].index)
    print(df)
    print(df.describe())
    print(df.corr())
    print(df.corr('spearman'))
    if df.query('predictions > 0.0001').__len__() < 10 or df.query('predictions < -0.0001').__len__() < 10:
        logger.info('predictions too small')
        q90 = df['predictions'].quantile(0.90)
        q10 = df['predictions'].quantile(0.10)
        logger.info(df.query(f"predictions > {q90}").labels.mean())
        logger.info(df.query(f"predictions < {q10}").labels.mean())
        logger.info((df.query(f"predictions > {q90}")['labels'] > 0).mean())
        logger.info((df.query(f"predictions < {q10}")['labels'] < 0).mean())
        logger.info(df.query(f"predictions > {q90}").__len__())
        logger.info(df.query(f"predictions < {q10}").__len__())
    else:
        logger.info('predictions normal')
        logger.info(df.query('predictions > 0.0001')['labels'].mean())
        logger.info(df.query('predictions < -0.0001')['labels'].mean())
        logger.info((df.query('predictions > 0.0001')['labels'] > 0).mean())
        logger.info((df.query('predictions < -0.0001')['labels'] < 0).mean())
        logger.info(df.query('predictions > 0.0001').__len__())
        logger.info(df.query('predictions < -0.0001').__len__())


__all__ = [
    'get_factors',
    'get_segments',
    'train_regress_model',
    'regress_model',
]
