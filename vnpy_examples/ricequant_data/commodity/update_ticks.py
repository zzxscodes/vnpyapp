from datetime import datetime

from vnpy.trader.datafeed import get_datafeed
from vnpy.trader.object import HistoryRequest
from vnpy.trader.setting import SETTINGS
from vnpy_app.utility.database.mysql.loader import upload_ticks
from vnpy_app.utility.functions import get_exchange, get_interval

setting = SETTINGS

setting["datafeed.name"] = "rqdata"
setting["datafeed.username"] = "13533374736"
setting["datafeed.password"] = "asdas!54984@315gf"

symbol = 'AG88'
exchange = get_exchange('SHFE')
interval = get_interval('TICK')
# 2022-12-30 15:00:00
start = datetime(2022, 12, 30)
end = datetime(2023, 3, 1)

req: HistoryRequest = HistoryRequest(
    symbol=symbol,
    exchange=exchange,
    interval=interval,
    start=start,
    end=end
)

datafeed = get_datafeed()
datafeed.init()
ticks = datafeed.query_tick_history(req, output=print)
upload_ticks(ticks)