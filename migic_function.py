#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2018/10/14
@Author  : AnNing
"""
import query
import valuation
import income
import balance
import get_index_stocks
import get_fundamentals
import get_security_info
import get_price

from datetime import datetime
from dateutil.relativedelta import relativedelta
import numpy as np
import pandas as pd

# 选择所有A股股票
STOCK_CODES = get_index_stocks('000002.XSHG')


def get_stocks_data(stocks_code, date):
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
        valuation.code.in_(stocks_code)
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
    ROC_EY = pd.DataFrame({'ROC': ROC,'EY': EY})

    # 对 ROC进行降序排序, 记录序号
    ROC_EY = ROC_EY.sort('ROC',ascending=False)
    idx = pd.Series(np.arange(1,len(ROC)+1), index=ROC_EY['ROC'].index.values)
    ROC_I = pd.DataFrame({'ROC_I': idx})
    ROC_EY = pd.concat([ROC_EY, ROC_I], axis=1)

    # 对 EY进行降序排序, 记录序号
    ROC_EY = ROC_EY.sort('EY',ascending=False)
    idx = pd.Series(np.arange(1,len(EY)+1), index=ROC_EY['EY'].index.values)
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


def one_year_profit(start_date, end_date, stock_codes, test_count=30):
    profit = 0
    for stock_code in stock_codes:
        stock_info = get_security_info(stock_code)
        stock_name = stock_info.display_name
        stock_price = get_price(stock_code, start_date=start_date, end_date=end_date,
                                frequency='daily', fields=['open','close'])
        first_price = stock_price.open[0]
        last_price = stock_price.close[-1]
        bias = first_price - last_price
        r_bias = (first_price - last_price) / first_price * 100

        print('code: {}, name: {}, first_price: {}, last_price: {}, bias: {}, r_bias:{}'.format(
            stock_code, stock_name, first_price, last_price, bias, r_bias
        ))

        profit = profit + r_bias
        test_count -= 1
        if test_count == 0:
            break
    print(profit)
    return profit


def main(start_year=2005):
    date_format_str = '%Y-%m-%d'
    start_date = datetime(year=start_year, month=1, day=1)
    end_date = start_date + relativedelta(years=1) - relativedelta(days=1)
    now_date = datetime.utcnow()
    start_ymd = start_date.strftime(date_format_str)
    end_ymd = end_date.strftime(date_format_str)

    stock_data = get_stocks_data(STOCK_CODES, start_ymd)
    roc_ey = get_roc_ey(stock_data)
    one_year_profit(start_ymd, end_ymd, roc_ey.index)


main()
