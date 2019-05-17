import os
import gi
import re
import math
# import talib
import pandas as pd
from pylab import *
from datetime import datetime
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from matplotlib import pyplot as plt
from matplotlib import ticker
import matplotlib.font_manager as fm
mpl.rcParams['font.sans-serif'] = ['WenQuanYi Zen Hei Mono']  # Solve the problem of Chinese messy code.

def filterIndustry(dataFrame, str):
    return dataFrame[dataFrame.industry == str]

def filterSymbol(dataFrame, str):
    return dataFrame[dataFrame.symbol == str]

def filterTsCode(dataFrame, str):
    return dataFrame[dataFrame.ts_code == str]

def concatDataFrame(dataFrame1, dataFrame2):
    return dataFrame1.append(dataFrame2)

def cutHead(str, char = " "):
    start = str.rfind(char)
    return str[start+1:]

def addBorder(inner, lab = ""):
    """Border the Gtk widget."""
    frame = Gtk.Frame.new(lab)
    frame.add(inner)
    return frame

def strIsNanOrNone(_str):
    if(_str == "NaN" or _str == "None"):
        return True
    return False

def checkDirectory(dirName):
    """Check that the directory exists, and if it does not, create it"""
    index = dirName.rfind(os.sep)
    if (index != -1):
        checkDirectory(dirName[:index])
        if (not os.path.isdir(dirName)):
            os.mkdir(dirName)
    else:
        if (not os.path.isdir(dirName)):
            os.mkdir(dirName)

def packing(_dict):
    box = Gtk.Grid()
    i = 0
    if _dict is None:
        box.add(Gtk.Label("There is no report.", selectable=True))
    else:
        for s in _dict:
            if(strIsNanOrNone(_dict[s][1])):
                continue
            box.attach(addBorder(Gtk.Label(_dict[s][0] + ":", selectable=True)), 0, i, 1, 1)
            box.attach(addBorder(Gtk.Label(_dict[s][1], selectable=True)), 1, i, 1, 1)
            i += 1

    return box

def drawMainBusinessStructurePieChart(src):
    """
    Main business structure
    Used to draw pie charts. Three temporary files are saved in the data/cache:
    mainbusinessincome.png, mainbusinessprofit.png, and mainbusinesscost.png.
    These three files are not deleted, but do not use them anywhere else
    because you cannot determine which company's graph is.
    :param src: A pandas.core.frame.DataFrame type, there must be bz_item, bz_sales, bz_profit, bz_cost four columns.
    :return:Return a dictionary in which three Gtk.Image objects are stored.
            The corresponding key values are bz_sales, bz_profit and bz_cost,
            respectively representing Main Business Income,
            pie charts corresponding to Main Business Profit and Main Business Cost.
    """
    font = fm.FontProperties(fname='/usr/lib/python3.7/site-packages/matplotlib/mpl-data/fonts/ttf/wenquan.ttf')
    colors = ['red', 'yellowgreen', 'lightskyblue', 'magenta', 'yellow', 'green', 'khaki', 'white', 'brown', 'hotpink', 'palegoldenrod', 'lightskyblue', 'magenta', 'yellow', 'green', 'khaki', 'white', 'brown', 'hotpink', 'palegoldenrod']  # 每块颜色定义
    plt.figure(figsize=(8, 8))  # resize.
    labels = []
    sizes1 = []
    sizes2 = []
    sizes3 = []
    color = []

    checkDirectory("data/cache")
    for i in range(0, src.iloc[:,0].size):
        # labels.append(src.iloc[i]["bz_item"].encode('utf-8').decode('gb18030'))       # 定义标签
        labels.append(str(bytes(src.iloc[i]["bz_item"], 'gb18030'), 'gb18030'))       # 定义标签
        if not math.isnan(src.iloc[i]["bz_sales"]):
            sizes1.append(src.iloc[i]["bz_sales"])      # 收入每块值
        if not math.isnan(src.iloc[i]["bz_profit"]):
            sizes2.append(src.iloc[i]["bz_profit"])     # 利润每块值
        if not math.isnan(src.iloc[i]["bz_cost"]):
            sizes3.append(src.iloc[i]["bz_cost"])       # 成本每块值
        if(src.iloc[:,0].size == len(colors)+1 and i == src.iloc[:,0].size-1):
            color.append(colors[4])
            continue
        color.append(colors[i % len(colors)])
    if not len(sizes1) == 0:
        plt.cla()
        patches, text1, text2 = plt.pie(sizes1,
                                        labels=labels,
                                        colors=color,
                                        labeldistance=1.2,  # 图例距圆心半径倍距离
                                        autopct='%3.2f%%',  # 数值保留固定小数位
                                        shadow=False,  # 无阴影设置
                                        startangle=90,  # 逆时针起始角度设置
                                        pctdistance=0.6)  # 数值距圆心半径倍数距离
        # patches饼图的返回值，texts1饼图外label的文本，texts2饼图内部文本
        # x，y轴刻度设置一致，保证饼图为圆形
        plt.axis('equal')
        plt.legend(prop=font)
        plt.title(u'主营业务收入')  # 绘制标题
        plt.savefig(u'data/cache/mainBusinessIncome.png')  # 保存图片

    if not len(sizes2) == 0:
        plt.cla()
        patches, text1, text2 = plt.pie(sizes2,
                                        labels=labels,
                                        colors=color,
                                        labeldistance=1.2,  # 图例距圆心半径倍距离
                                        autopct='%3.2f%%',  # 数值保留固定小数位
                                        shadow=False,  # 无阴影设置
                                        startangle=90,  # 逆时针起始角度设置
                                        pctdistance=0.6)  # 数值距圆心半径倍数距离
        # patches饼图的返回值，texts1饼图外label的文本，texts2饼图内部文本
        # x，y轴刻度设置一致，保证饼图为圆形
        plt.axis('equal')
        plt.legend(prop=font)
        plt.title(u'主营业务利润')  # 绘制标题
        plt.savefig(u'data/cache/mainBusinessProfit.png')  # 保存图片

    if not len(sizes3) == 0:
        plt.cla()
        patches, text1, text2 = plt.pie(sizes3,
                                        labels=labels,
                                        colors=color,
                                        labeldistance=1.2,  # 图例距圆心半径倍距离
                                        autopct='%3.2f%%',  # 数值保留固定小数位
                                        shadow=False,  # 无阴影设置
                                        startangle=90,  # 逆时针起始角度设置
                                        pctdistance=0.6)  # 数值距圆心半径倍数距离
        # patches饼图的返回值，texts1饼图外label的文本，texts2饼图内部文本
        # x，y轴刻度设置一致，保证饼图为圆形
        plt.axis('equal')
        plt.legend(prop=font)
        plt.title(u'主营业务成本')  # 绘制标题
        plt.savefig(u'data/cache/mainBusinessCost.png')  # 保存图片

    ret_Dict = {
        "mainBusinessIncome": Gtk.Image.new_from_file("data/cache/mainBusinessIncome.png"),
        "mainBusinessProfit": Gtk.Image.new_from_file("data/cache/mainBusinessProfit.png"),
        "mainBusinessCost": Gtk.Image.new_from_file("data/cache/mainBusinessCost.png")
    }

    return ret_Dict

def searchByNameOrFullname(dataFrame, n_str):
    """
    Used to screen qualified companies.
    :param dataFrame:Select from dataFrame.
    :param n_str:Keywords for filtering.
    :return:DataFrame.
    """
    ret = dataFrame.loc[(dataFrame['fullname'].str.contains(n_str)) | (dataFrame['name'].str.contains(n_str))]
    if (ret.empty):
        return None
    else:
        return ret

def getCurrentYear():
    return datetime.now().year


def convertELogStrToValue(eLogStr):
    """
    convert string of natural logarithm base of E to value
    return convertedValue
    eg:
    input:  -1.1694737e-03
    output: -0.001169
    input:  8.9455025e-04
    output: 0.000895
    """
    s_sp = eLogStr.split('E')
    if s_sp[0] is 'NaN':
        print(eLogStr)
        return 0
    else:
        base = float(s_sp[0])
        mul = int(s_sp[1])
        return base*math.pow(10, mul)

def toNumber(s):
    up = s.upper()
    if 'E' not in up:    # 非科学计数法
        return float(up)
    else:                   # 科学计数法
        convertedValue = convertELogStrToValue(up)
        return convertedValue

def getAssetLiabilityRatio(dataFrame):
    # 资产负债率 = 负债总额/资产总额
    if dataFrame is None:
        return " "
    elif dataFrame:
        total_assets = dataFrame['total_assets'][1]     # 资产总额
        total_liab = dataFrame['total_liab'][1]       # 负债总额
        if not total_assets.strip() or not total_liab.strip():     # 字符串为空
            return " "
        else:
            ret = str((toNumber(total_liab)/toNumber(total_assets))*100)[:5] + "%"
            return ret
    else:
        return " "

def getCurrentLiabilitiesRate(dataFrame):
    # 流动负债率 = 流动负债合计/负债合计
    if dataFrame is None:
        return " "
    elif dataFrame:
        total_cur_liab = dataFrame['total_cur_liab'][1]     # 流动负债合计
        total_liab = dataFrame['total_liab'][1]             # 负债总额
        if not total_cur_liab.strip() or not total_liab.strip():     # 字符串为空
            return " "
        else:
            ret = str((toNumber(total_cur_liab)/toNumber(total_liab))*100)[:5] + "%"
            return ret
    else:
        return " "

def getSourceDivOccupation(dataFrame):
    # 长期资金来源/长期资金占用
    # 长期资金占用=存货+非流动资产;长期资金来源=长期负债+股东权益
    if dataFrame is None:
        return " "
    elif dataFrame:
        total_nca = dataFrame['total_nca'][1]       # 非流动资产合计
        inventories = dataFrame['inventories'][1]   # 存货
        total_ncl = dataFrame['total_ncl'][1]       # 非流动负债合计
        total_hldr_eqy_inc_min_int = dataFrame['total_hldr_eqy_inc_min_int'][1]  # 股东权益合计

        if not total_nca.strip() \
                or not inventories.strip()\
                or not total_ncl.strip() \
                or not total_hldr_eqy_inc_min_int.strip():     # 字符串为空
            return " "
        else:
            ret = str(((toNumber(total_ncl)+toNumber(total_hldr_eqy_inc_min_int))/(toNumber(total_nca)+toNumber(inventories)))*100)[:5] + "%"
            return ret
    else:
        return " "

def getGrossProfitMargin(dataFrame):
    if dataFrame is None:
        return " "
    elif dataFrame:
        grossprofit_margin = dataFrame['grossprofit_margin'][1] # 毛利率
        if not grossprofit_margin.strip():     # 字符串为空
            return " "
        else:
            ret = grossprofit_margin[:5] + "%"
            return ret
    else:
        return " "

def getNetProfitMarginOnSales(dataFrame):
    if dataFrame is None:
        return " "
    elif dataFrame:
        netprofit_margin = dataFrame['netprofit_margin'][1] # 销售净利率
        if not netprofit_margin.strip():     # 字符串为空
            return " "
        else:
            ret = netprofit_margin[:5] + "%"
            return ret
    else:
        return " "

def getReturnOnEquity(dataFrame):
    if dataFrame is None:
        return " "
    elif dataFrame:
        roe = dataFrame['roe'][1] # 净资产收益率
        if not roe.strip():     # 字符串为空
            return " "
        else:
            ret = roe[:5] + "%"
            return ret
    else:
        return " "

def getLineChartImg(x, y, _title="", _label="", _xlabel="", _ylabel=""):
    plt.cla()
    tick_spacing = 6
    fig, ax = plt.subplots(1, 1)
    ax.plot(x, y, label=_label)
    plt.title(_title)
    ax.xaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))
    _x = np.linspace(min(x), max(x), 5)
    plt.xticks(_x)
    _y = np.linspace(min(y), max(y), 5)
    plt.yticks(_y)
    plt.xlabel(_xlabel)
    plt.ylabel(_ylabel)
    plt.legend()
    checkDirectory("data/cache")
    ax.figure.savefig(u'data/cache/lineChartImg.png')  # 保存图片
    return Gtk.Image.new_from_file("data/cache/lineChartImg.png")

def getTotalAssets(dataFrame):
    if dataFrame is None:
        return " "
    elif dataFrame:
        total_assets = dataFrame['total_assets'][1]  # 资产总计
        if not total_assets.strip():  # 字符串为空
            return " "
        else:
            return total_assets
    else:
        return " "

def getTotalAssetsGrowthRate(dataFrame):
    if dataFrame is None:
        return " "
    elif dataFrame:
        assets_yoy = dataFrame['assets_yoy'][1]  # 总资产增长率
        if not assets_yoy.strip():  # 字符串为空
            return " "
        else:
            ret = assets_yoy[:5] + "%"
            return ret
    else:
        return " "

def getMainBusinessIncome(dataFrame):
    if dataFrame is None:
        return " "
    if isinstance(dataFrame, pd.DataFrame):
        if not dataFrame.empty:
            bz_sales = dataFrame['bz_sales'][1]  # 主营业务收入
            if isinstance(bz_sales, np.float64):
                bz_sales = str(bz_sales)
            if not bz_sales.strip():  # 字符串为空
                return " "
            else:
                return bz_sales
        else:
            return " "
    else:
        if dataFrame:
            bz_sales = dataFrame['bz_sales'][1]  # 主营业务收入
            if isinstance(bz_sales, np.float64):
                bz_sales = str(bz_sales)
            if not bz_sales.strip():  # 字符串为空
                return " "
            else:
                return bz_sales
        else:
            return " "


def getNetProfit(dataFrame):
    if dataFrame is None:
        return " "
    if isinstance(dataFrame, pd.DataFrame):
        if not dataFrame.empty:
            profit_to_gr = dataFrame['profit_to_gr'][1]  # 净利润
            if isinstance(profit_to_gr, np.float64):
                profit_to_gr = str(profit_to_gr)
            if not profit_to_gr.strip():  # 字符串为空
                return " "
            else:
                return profit_to_gr
        else:
            return " "
    else:
        if dataFrame:
            profit_to_gr = dataFrame['profit_to_gr'][1]  # 净利润
            if isinstance(profit_to_gr, np.float64):
                profit_to_gr = str(profit_to_gr)
            if not profit_to_gr.strip():  # 字符串为空
                return " "
            else:
                return profit_to_gr
        else:
            return " "

def getInventoryTurnover(dataFrame):
    if dataFrame is None:
        return " "
    if isinstance(dataFrame, pd.DataFrame):
        if not dataFrame.empty:
            inv_turn = dataFrame['inv_turn'][1]  # 存货周转率
            if isinstance(inv_turn, np.float64):
                inv_turn = str(inv_turn)
            if not inv_turn.strip():  # 字符串为空
                return " "
            else:
                return str(float(inv_turn)*100)[:9]+"%"
        else:
            return " "
    else:
        if dataFrame:
            inv_turn = dataFrame['inv_turn'][1]  # 存货周转率
            if isinstance(inv_turn, np.float64):
                inv_turn = str(inv_turn)
            if not inv_turn.strip():  # 字符串为空
                return " "
            else:
                return str(float(inv_turn)*100)[:9]+"%"
        else:
            return " "

def getAccountsReceivableTurnover(dataFrame):
    if dataFrame is None:
        return " "
    if isinstance(dataFrame, pd.DataFrame):
        if not dataFrame.empty:
            ar_turn = dataFrame['ar_turn'][1]  # 应收账款周转率
            if isinstance(ar_turn, np.float64):
                if math.isnan(ar_turn):
                    return " "
                ar_turn = str(ar_turn)
            if not ar_turn.strip():  # 字符串为空
                return " "
            else:
                return str(float(ar_turn)*100)[:9]+"%"
        else:
            return " "
    else:
        if dataFrame:
            ar_turn = dataFrame['ar_turn'][1]  # 应收账款周转率
            if isinstance(ar_turn, np.float64):
                ar_turn = str(ar_turn)
            if not ar_turn.strip():  # 字符串为空
                return " "
            else:
                return str(float(ar_turn)*100)[:9]+"%"
        else:
            return " "

def getTotalAssetTurnover(dataFrame):
    if dataFrame is None:
        return " "
    if isinstance(dataFrame, pd.DataFrame):
        if not dataFrame.empty:
            assets_turn = dataFrame['assets_turn'][1]  # 总资产周转率
            if isinstance(assets_turn, np.float64):
                assets_turn = str(assets_turn)
            if not assets_turn.strip():  # 字符串为空
                return " "
            else:
                return str(float(assets_turn)*100)[:9]+"%"
        else:
            return " "
    else:
        if dataFrame:
            assets_turn = dataFrame['assets_turn'][1]  # 总资产周转率
            if isinstance(assets_turn, np.float64):
                assets_turn = str(assets_turn)
            if not assets_turn.strip():  # 字符串为空
                return " "
            else:
                return str(float(assets_turn)*100)[:9]+"%"
        else:
            return " "


def getCurrentRatio(dataFrame):
    if dataFrame is None:
        return " "
    if isinstance(dataFrame, pd.DataFrame):
        if not dataFrame.empty:
            current_ratio = dataFrame['current_ratio'][1]  # 流动比率
            if isinstance(current_ratio, np.float64):
                current_ratio = str(current_ratio)
            if not current_ratio.strip():  # 字符串为空
                return " "
            else:
                return str(float(current_ratio)*100)[:9]+"%"
        else:
            return " "
    else:
        if dataFrame:
            current_ratio = dataFrame['current_ratio'][1]  # 流动比率
            if isinstance(current_ratio, np.float64):
                current_ratio = str(current_ratio)
            if not current_ratio.strip():  # 字符串为空
                return " "
            else:
                return str(float(current_ratio)*100)[:9]+"%"
        else:
            return " "


def getQuickRatio(dataFrame):
    if dataFrame is None:
        return " "
    if isinstance(dataFrame, pd.DataFrame):
        if not dataFrame.empty:
            quick_ratio = dataFrame['quick_ratio'][1]  # 速动比率
            if isinstance(quick_ratio, np.float64):
                quick_ratio = str(quick_ratio)
            if not quick_ratio.strip():  # 字符串为空
                return " "
            else:
                return str(float(quick_ratio)*100)[:9]+"%"
        else:
            return " "
    else:
        if dataFrame:
            quick_ratio = dataFrame['quick_ratio'][1]  # 速动比率
            if isinstance(quick_ratio, np.float64):
                quick_ratio = str(quick_ratio)
            if not quick_ratio.strip():  # 字符串为空
                return " "
            else:
                return str(float(quick_ratio)*100)[:9]+"%"
        else:
            return " "


def getAssetLiabilityRatio(dataFrame):
    if dataFrame is None:
        return " "
    if isinstance(dataFrame, pd.DataFrame):
        if not dataFrame.empty:
            debt_to_assets = dataFrame['debt_to_assets'][1]  # 速动比率
            if isinstance(debt_to_assets, np.float64):
                debt_to_assets = str(debt_to_assets)
            if not debt_to_assets.strip():  # 字符串为空
                return " "
            else:
                return str(float(debt_to_assets)*100)[:9]+"%"
        else:
            return " "
    else:
        if dataFrame:
            debt_to_assets = dataFrame['debt_to_assets'][1]  # 速动比率
            if isinstance(debt_to_assets, np.float64):
                debt_to_assets = str(debt_to_assets)
            if not debt_to_assets.strip():  # 字符串为空
                return " "
            else:
                return str(float(debt_to_assets)*100)[:9]+"%"
        else:
            return " "

def getNetCashOfBusinessActivities(dataFrame):
    if dataFrame is None:
        return " "
    if isinstance(dataFrame, pd.DataFrame):
        if not dataFrame.empty:
            n_cashflow_act = dataFrame['n_cashflow_act'][1]  # 经营活动产生的现金流量净额
            if isinstance(n_cashflow_act, np.float64):
                n_cashflow_act = str(n_cashflow_act)
            if not n_cashflow_act.strip():  # 字符串为空
                return " "
            else:
                return n_cashflow_act
        else:
            return " "
    else:
        if dataFrame:
            n_cashflow_act = dataFrame['n_cashflow_act'][1]  # 经营活动产生的现金流量净额
            if isinstance(n_cashflow_act, np.float64):
                n_cashflow_act = str(n_cashflow_act)
            if not n_cashflow_act.strip():  # 字符串为空
                return " "
            else:
                return n_cashflow_act
        else:
            return " "