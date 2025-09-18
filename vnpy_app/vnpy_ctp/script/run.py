from time import sleep

from vnpy.event import EventEngine
from vnpy.trader.engine import MainEngine
from vnpy.trader.event import EVENT_ACCOUNT
from vnpy_ctp import CtpGateway


class AccountQueryDemo:
    def __init__(self):
        self.event_engine = EventEngine()
        self.main_engine = MainEngine(self.event_engine)
        self.ctp_gateway = self.main_engine.add_gateway(CtpGateway)

        # 注册账户事件监听
        self.event_engine.register(EVENT_ACCOUNT, self.on_account)

        self.accounts = {}

    def on_account(self, event):
        """处理账户更新事件"""
        account = event.data
        self.accounts[account.accountid] = account
        self.print_account_info(account)

    @staticmethod
    def print_account_info(account):
        """打印账户信息"""
        print("\n=== 账户信息更新 ===")
        print(f"账户ID: {account.accountid}")
        print(f"余额: {account.balance:.2f}")
        print(f"可用资金: {account.available:.2f}")
        print(f"冻结资金: {account.frozen:.2f}")
        print(f"上次结算权益: {account.pre_balance:.2f}")
        print(f"入金金额: {account.deposit:.2f}")
        print(f"出金金额: {account.withdraw:.2f}")
        print(f"今日盈亏: {account.today_profit:.2f}")
        print(f"占用保证金: {account.margin:.2f}")
        print(f"手续费: {account.commission:.2f}")
        print(f"冻结保证金: {account.frozen_margin:.2f}")

    def connect_ctp(self, setting):
        """连接CTP"""
        print("正在连接CTP...")
        self.main_engine.connect(setting, "CTP")

    def query_account(self):
        """主动查询账户"""
        print("主动查询账户...")
        self.ctp_gateway.query_account()


# 使用示例
if __name__ == "__main__":
    # CTP连接配置
    ctp_setting = {
        "用户名": "237831",
        "密码": "sim8441SIM#",
        "经纪商代码": "9999",
        "交易服务器": "tcp://182.254.243.31:30001",
        "行情服务器": "tcp://182.254.243.31:30011",
        "产品名称": "simnow_client_test",
        "授权编码": "0000000000000000"
    }

    demo = AccountQueryDemo()
    demo.connect_ctp(ctp_setting)

    # 等待连接和数据更新
    sleep(5)

    # 主动查询
    demo.query_account()

    # 等待更多数据
    sleep(3)

    # 保持运行
    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        print("程序退出")
