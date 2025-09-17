from vnpy.trader.setting import SETTINGS


def backtest_setting():
    setting = SETTINGS
    setting["database.name"] = 'sqlite'
    setting["database.database"] = '/home/yangcheng/.vntrader/database.db'
    setting["database.user"] = ''
    setting["database.password"] = ''
    setting["database.host"] = ''
    setting["database.port"] = ''

    # setting["datafeed.name"] = "tushare"
    # setting["datafeed.username"] = "15626517329"
    # setting["datafeed.password"] = "3e916a75320c74679e0d5d07b47dd4ce686288258d864104259e0907"

    setting["datafeed.name"] = "rqdata"
    setting["datafeed.username"] = "13533374736"
    setting["datafeed.password"] = "asdas!54984@315gf"

    setting["database.timezone"] = "Asia/Shanghai"
    return setting
