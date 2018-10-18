# -*- coding: utf-8 -*-
from jqdatasdk import *

from datetime import datetime
from dateutil.relativedelta import relativedelta

import numpy as np
import pandas as pd

from jqdata import *

RANK_COUNT_MAX = 35  # 前多少名的股票可以购买
INTIME_COUNT_MAX = 30  # 最多持有多少支股票
YEARS = 1  # 持有年
MONTHS = 0  # 持有月
DAYS = 0  # 持有日
MARKET_CAP_MIN = 0  # 总市值超过多少的股票可以购买


# 初始化函数，设定基准等等
def initialize(context):
    # 设定沪深300作为基准
    set_benchmark('000300.XSHG')
    # 开启动态复权模式(真实价格)
    set_option('use_real_price', True)
    # 输出内容到日志 log.info()
    log.info('初始函数开始运行且全局只运行一次')
    # 过滤掉order系列API产生的比error级别低的log
    # log.set_level('order', 'error')

    # 常量
    g.rank_stocks = None  # 评分前几名的股票
    g.all_stocks = dict()  # 所有持有的股票
    g.buy_stocks = set()  # 当天需要购买的股票
    g.sell_stocks = set()  # 当天需要出售的股票

    # ### 股票相关设定 ###
    # 股票类每笔交易时的手续费是：买入时佣金万分之三，卖出时佣金万分之三加千分之一印花税, 每笔交易佣金最低扣5块钱
    set_order_cost(OrderCost(close_tax=0.001, open_commission=0.0003, close_commission=0.0003,
                             min_commission=5), type='stock')

    # 运行函数（reference_security为运行时间的参考标的；传入的标的只做种类区分，因此传入'000300.XSHG'或'510300.XSHG'是一样的）
    # 开盘前运行
    run_daily(before_market_open, time='before_open', reference_security='000300.XSHG')
    # run_monthly(before_market_open, monthday=1, time='before_open', reference_security='000300.XSHG')
    # 开盘时运行
    run_daily(market_open, time='open', reference_security='000300.XSHG')
    # run_monthly(market_open, monthday=1, time='open', reference_security='000300.XSHG')
    # 收盘后运行
    # run_daily(after_market_close, time='after_close', reference_security='000300.XSHG')


## 开盘前运行函数
def before_market_open(context):
    # 输出运行时间
    log.info('RUN(before_market_open)：' + str(context.current_dt.time()))

    # 给微信发送消息（添加模拟交易，并绑定微信生效）
    # send_message('美好的一天~')
    current_date = context.current_dt
    current_positions = context.portfolio.positions
    current_data = get_current_data()

    # 出售持仓超过一年的股票
    g.intime_stocks = set()  # 所有未到期的股票
    overtime_stocks = set()  # 所有到期的股票
    paused_stocks_intime = set()
    st_stocks_intime = set()
    paused_stocks_overtime = set()
    st_stocks_overtime = set()
    for stock, position in current_positions.items():
        if stock not in g.all_stocks:
            raise ValueError('positions 股票不在all_stocks 股票内: {}'.format(stock))

        overtime = g.all_stocks[stock]
        if current_date < overtime:
            g.intime_stocks.add(stock)
        else:
            overtime_stocks.add(stock)

        sell_time = position.init_time + relativedelta(years=YEARS, months=MONTHS, days=DAYS)

    for stock in g.intime_stocks:
        if current_data[stock].paused:
            paused_stocks_intime.add(stock)
        elif current_data[stock].is_st:
            st_stocks_intime.add(stock)

    for stock in overtime_stocks:
        if current_data[stock].paused:
            paused_stocks_overtime.add(stock)
        else:
            g.sell_stocks.add(stock)
        if current_data[stock].is_st:
            st_stocks_overtime.add(stock)

    log.info('股票总数: {}'.format(len(g.all_stocks)))
    log.info('期内股票: {} 停牌:{} ST: {}'.format(len(g.intime_stocks),
                                            len(paused_stocks_intime),
                                            len(st_stocks_intime)))
    log.info('到期股票: {} 停牌:{} ST: {}'.format(len(overtime_stocks),
                                            len(paused_stocks_overtime),
                                            len(st_stocks_overtime)))

    # 计算股票评分排名,并求出可交易的股票
    if len(g.intime_stocks) < INTIME_COUNT_MAX:
        # 要操作的股票
        stocks = get_index_stocks('399317.XSHE')

        # 计算价值排名
        stock_data = get_stocks_data(stocks, current_date, MARKET_CAP_MIN)
        roc_ey_rank = get_roc_ey(stock_data)

        # 过滤停牌股票和ST股票
        drop_stocks = []
        for stock in roc_ey_rank.index[:]:
            current_data_stock = current_data[stock]
            if current_data_stock.paused or current_data_stock.is_st:
                drop_stocks.append(stock)
        roc_ey_rank = roc_ey_rank.drop(index=drop_stocks)
        print(len(roc_ey_rank))

        g.rank_stocks = roc_ey_rank.index[0:RANK_COUNT_MAX]  # 评分排名在多少的股票, 可进行交易


## 开盘时运行函数
def market_open(context):
    log.info('RUN(market_open):' + str(context.current_dt.time()))

    # 平仓
    if g.sell_stocks:
        print('-*' * 20)
        for stock in g.sell_stocks:
            stock_info = get_security_info(stock)
            stock_name = stock_info.display_name

            log.info('SELL: code: {}, name: {}'.format(stock, stock_name))
            print('-' * 20)
            result = order_target(stock, 0)
            if result is not None:
                pass

    # 开仓
    if len(g.valid_stocks) < INTIME_COUNT_MAX:
        current_data = get_current_data()

        # 取得当前的现金
        cash = context.portfolio.available_cash
        one_stock_cash = cash / (g.valid_count - len(g.valid_stocks))
        print('-*' * 20)
        print('CASH: {}'.format(cash))
        print('ONE_STOCK_CASH: {}'.format(one_stock_cash))
        print('-*' * 20)

        for stock in g.rank_stocks:
            if len(g.valid_stocks) >= INTIME_COUNT_MAX:
                break

            if stock in g.valid_stocks:
                continue

            stock_info = get_security_info(stock)
            stock_name = stock_info.display_name

            log.info('-' * 20)
            log.info('BUY: code: {}, name: {}'.format(stock, stock_name))
            result = order_target_value(stock, one_stock_cash)
            if result is not None:
                g.valid_stocks.add(stock)


## 收盘后运行函数
def after_market_close(context):
    log.info(str('函数运行时间(after_market_close):' + str(context.current_dt.time())))
    # 得到当天所有成交记录
    trades = get_trades()
    for _trade in trades.values():
        log.info('成交记录：' + str(_trade))
    log.info('一天结束')
    log.info('##############################################################')


def get_stocks_data(stocks, date, market_cap_min):
    q = query(
        valuation.code,  # 股票代码

        # 税息前利润(EBIT) = 营业利润
        income.operating_profit,  # 营业利润(元)  独自代表企业业务的盈利能力 EBIT

        # 净流动资本 + 净固定资产 = 资产总计 - 商誉 - 无形资产
        # 投资回报率 = EBIT / (净流动资本 + 净固定资产)
        balance.total_assets,  # 资产总计(元)
        balance.good_will,  # 商誉(元)
        balance.intangible_assets,  # 无形资产(元)

        # 企业价值 = 总市值 + 负债合计
        # 收益率 = EBIT / 企业价值
        valuation.market_cap,  # 总市值(亿元)
        balance.total_liability,  # 负债合计(元)

    ).filter(
        income.operating_profit > 0,
        valuation.market_cap > market_cap_min,
        valuation.code.in_(stocks)
    )
    data = get_fundamentals(q, date=date).fillna(value=0).set_index('code')
    return data


def get_roc_ey(stock_data):
    d = stock_data
    # 息税前利润(EBIT) = 营业利润
    EBIT = d['operating_profit']

    # 净流动资本 + 净固定资产 = 资产总计 - 商誉 - 无形资产
    ALL_CAPITAL = d['total_assets'] - d['good_will'] - d['intangible_assets']

    # 企业价值 = 总市值 + 负债合计
    EV = d['market_cap'] + d['total_liability']

    # 剔除 ALL_CAPITAL 和 EV 非正的股票
    tmp = set(d.index.values) - set(EBIT[EBIT <= 0].index.values) - set(
        EV[EV <= 0].index.values) - set(ALL_CAPITAL[ALL_CAPITAL <= 0].index.values)
    EBIT = EBIT[tmp]
    ALL_CAPITAL = ALL_CAPITAL[tmp]
    EV = EV[tmp]

    # 投资回报率 = EBIT / (净流动资本 + 净固定资产)
    ROC = EBIT / ALL_CAPITAL
    # 收益率 = EBIT / 企业价值
    EY = EBIT / EV

    # 按ROC 和 EY 构建表格
    ROC_EY = pd.DataFrame({'ROC': ROC, 'EY': EY})

    # 对 ROC进行降序排序, 记录序号
    ROC_EY = ROC_EY.sort('ROC', ascending=False)
    idx = pd.Series(np.arange(1, len(ROC) + 1), index=ROC_EY['ROC'].index.values)
    ROC_I = pd.DataFrame({'ROC_I': idx})
    ROC_EY = pd.concat([ROC_EY, ROC_I], axis=1)

    # 对 EY进行降序排序, 记录序号
    ROC_EY = ROC_EY.sort('EY', ascending=False)
    idx = pd.Series(np.arange(1, len(EY) + 1), index=ROC_EY['EY'].index.values)
    EY_I = pd.DataFrame({'EY_I': idx})
    ROC_EY = pd.concat([ROC_EY, EY_I], axis=1)

    # 对序号求和，并记录之
    roci = ROC_EY['ROC_I']
    eyi = ROC_EY['EY_I']
    idx = roci + eyi
    SUM_I = pd.DataFrame({'SUM_I': idx})
    ROC_EY = pd.concat([ROC_EY, SUM_I], axis=1)

    # 按序号和，进行升序排序，然后选出排名靠前的20只股票
    ROC_EY = ROC_EY.sort('SUM_I')
    return ROC_EY[0:100]

