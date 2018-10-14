#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2018/10/14
@Author  : AnNing
"""
# 导入函数库
from datetime import datetime

from jqdata import *


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

    ### 股票相关设定 ###
    # 股票类每笔交易时的手续费是：买入时佣金万分之三，卖出时佣金万分之三加千分之一印花税, 每笔交易佣金最低扣5块钱
    set_order_cost(OrderCost(close_tax=0.001, open_commission=0.0003, close_commission=0.0003,
                             min_commission=5), type='stock')

    ## 运行函数（reference_security为运行时间的参考标的；传入的标的只做种类区分，因此传入'000300.XSHG'或'510300.XSHG'是一样的）
    # 开盘前运行
    # run_daily(before_market_open, time='before_open', reference_security='000300.XSHG')
    run_monthly(before_market_open, monthday=1, time='before_open',
                reference_security='000300.XSHG')
    # 开盘时运行
    # run_daily(market_open, time='open', reference_security='000300.XSHG')
    run_monthly(market_open, monthday=1, time='open', reference_security='000300.XSHG')
    # 收盘后运行
    # run_daily(after_market_close, time='after_close', reference_security='000300.XSHG')

    # 常量
    g.rank_count = 30
    g.trade = None


## 开盘前运行函数
def before_market_open(context):
    # 输出运行时间
    log.info('函数运行时间(before_market_open)：' + str(context.current_dt.time()))

    # 给微信发送消息（添加模拟交易，并绑定微信生效）
    send_message('美好的一天~')

    # 要操作的股票
    stocks = get_index_stocks('399317.XSHE')

    # 计算价值排名
    current_date = context.current_dt
    stock_data = get_stocks_data(stocks, current_date)
    roc_ey = get_roc_ey(stock_data)

    rank_count = g.rank_count  # 评分排名在多少,进行交易

    stocks = roc_ey.index[0:rank_count]  # 需要进行交易的股票

    g.stocks = stocks

    if g.trade is None:
        g.trade = True
    else:
        g.grade = False


## 开盘时运行函数
def market_open(context):
    log.info('函数运行时间(market_open):' + str(context.current_dt.time()))

    # 如果不需要交易,直接退出函数
    if not g.trade:
        return

    stocks = g.stocks
    rank_count = g.rank_count

    # 取得当前的现金
    cash = context.portfolio.available_cash

    one_stock_cash = cash / rank_count

    for stock in stocks:
        stock_info = get_security_info(stock_code)
        stock_name = stock_info.display_name

        log.info('BUY: code: {}, name: {}'.format(stock_code, stock_name))
        order_value(stock, one_stock_cash)


## 收盘后运行函数
def after_market_close(context):
    log.info(str('函数运行时间(after_market_close):' + str(context.current_dt.time())))
    # 得到当天所有成交记录
    trades = get_trades()
    for _trade in trades.values():
        log.info('成交记录：' + str(_trade))
    log.info('一天结束')
    log.info('##############################################################')


def get_stocks_data(stocks, date):
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
        income.net_profit > 0,
        #     valuation.market_cap > 50,
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

    # 投资回报率 = EBIT / (净流动资本 + 净固定资产)
    ROC = EBIT / ALL_CAPITAL

    # 企业价值 = 总市值 + 负债合计
    EV = d['market_cap'] + d['total_liability']
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
    return ROC_EY

