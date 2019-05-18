#!/usr/bin/env python3.7

from spider import Data
import gi
import re
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject, Gdk
from analyze import *

class UI_Menu(Gtk.MenuBar):
    # The members of File menu.
    file_Menu = Gtk.Menu()
    file_MenuItem = Gtk.MenuItem("File")
    file_Menu_Set = Gtk.MenuItem("Preferences")

    # The members of Help menu.
    help_Menu = Gtk.Menu()
    help_MenuItem = Gtk.MenuItem("Help")
    help_Menu_About = Gtk.MenuItem("About")

    def __init__(self):
        Gtk.MenuBar.__init__(self)
        # Unuseable
        # self.set_vexpend(False)

        # Set the module of File menu and add it into the menubar.
        self.file_MenuItem.set_submenu(self.file_Menu)
        self.file_Menu.append(self.file_Menu_Set)
        self.add(self.file_MenuItem)

        # Set the module of Help menu and add it into the menubar.
        self.help_MenuItem.set_submenu(self.help_Menu)
        self.help_Menu_About.connect("activate", self.on_menu_About_clicked)
        self.help_Menu.append(self.help_Menu_About)
        self.add(self.help_MenuItem)

    def on_menu_Set_clicked(self, widget):
        pass

    def on_menu_About_clicked(self, widget):
        print("About is clicked.")

class UI_Search(Gtk.Box):
    # A members who the area of select.
    # The members above, including refresh button and select input field and you what can you set to search by.
    data = Data()
    upper = Gtk.Box()
    evt = Gtk.EventBox()
    search = Gtk.Button()
    refresh = Gtk.Button()
    __changeByClick = True
    searchEntry = Gtk.Entry()
    scrolledWindow = Gtk.ScrolledWindow()
    storeOfSearchShow = Gtk.ListStore(str, str, str)
    searchShow = Gtk.TreeView(storeOfSearchShow)
    companyList_DataFrame = data.getListOfPublicCompanies()
    selection = searchShow.get_selection()
    i = 0
    __gsignals__ = {
        'selection_changed': (GObject.SIGNAL_RUN_FIRST, None,
                      (str,))
    }

    def __init__(self):
        # Initialize the box and set it's property.
        Gtk.Box.__init__(self)
        self.set_spacing(6)
        self.set_orientation(Gtk.Orientation.VERTICAL)

        # Set the image of refresh button and add it into the upper box.
        self.refresh.set_image(Gtk.Image.new_from_file("Icons/refresh.png"))
        # Set relief can remove the border of the gtk.button.
        self.refresh.set_relief(Gtk.ReliefStyle.NONE)
        self.refresh.get_style_context().add_class("circular")
        self.refresh.set_halign(Gtk.Align.CENTER)
        self.refresh.set_valign(Gtk.Align.CENTER)
        self.refresh.connect("clicked", self.on_refresh_clicked)
        self.upper.pack_start(self.refresh, False, False, 0)

        self.search.set_image(Gtk.Image.new_from_file("Icons/search.png"))
        # Set relief can remove the border of the gtk.button.
        self.search.set_relief(Gtk.ReliefStyle.NONE)
        self.search.get_style_context().add_class("circular")
        self.search.set_halign(Gtk.Align.CENTER)
        self.search.set_valign(Gtk.Align.CENTER)
        self.search.connect("clicked", self.on_search_clicked)

        self.scrolledWindow.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        self.scrolledWindow.set_policy(Gtk.PolicyType.NEVER,
                        Gtk.PolicyType.AUTOMATIC)

        # Set column
        column = Gtk.TreeViewColumn("Symbol | Name | Industry")
        symbol = Gtk.CellRendererText()
        name = Gtk.CellRendererText()
        industry = Gtk.CellRendererText()
        column.pack_start(symbol, True)
        column.pack_start(name, True)
        column.pack_start(industry, True)
        column.add_attribute(symbol, "text", 0)
        column.add_attribute(name, "text", 1)
        column.add_attribute(industry, "text", 2)
        self.searchShow.append_column(column)
        self.scrolledWindow.add(self.searchShow)
        # self.evt.add(self.scrolledWindow)
        self.selection.connect("changed", self.on_treeview_selection_changed)
        # self.evt.connect("button_press_event", self.on_treeview_selection_changed)

        # Set the search entry and the menu button and add they into the searchbar.
        # Init searchBar and add it into the upper box.
        self.upper.pack_start(self.searchEntry, True, True, 2)
        self.upper.pack_start(self.search, False, False, 1)

        self.pack_start(self.upper, False, False, 0)
        self.pack_start(self.scrolledWindow, True, True, 3)

    def searchShowRefresh(self, rows_dataFrame):
        self.storeOfSearchShow.clear()
        for index, row in rows_dataFrame.iterrows():
            self.storeOfSearchShow.append([row["symbol"], row["name"], row["industry"]])

    def on_refresh_clicked(self, *argument):
        self.__changeByClick = False
        cl = self.companyList_DataFrame
        # self.searchShowRefresh(concatDataFrame(filterIndustry(cl, "全国地产"), filterIndustry(cl, "区域地产")))
        self.searchShowRefresh(cl)
        self.__changeByClick = True

    def on_search_clicked(self, *argument):
        self.__changeByClick = False
        self.searchShowRefresh(searchByNameOrFullname(self.companyList_DataFrame, self.searchEntry.get_text()))
        self.__changeByClick = True

    def on_treeview_selection_changed(self, *argument):
        if (self.__changeByClick):
            selected = self.selection.get_selected()[1]

            TsCode = self.data.getTsCodeBySymbol(self.storeOfSearchShow[selected][0])
            self.emit("selection_changed", TsCode)

class TabItem(Gtk.Box):
    # *使用relief设置移动到button上的浮雕
    __gsignals__ = {
        'close_clicked': (GObject.SIGNAL_RUN_FIRST, None,
                      (str,)),
        'tab_clicked': (GObject.SIGNAL_RUN_FIRST, None,
                        (str,))
    }

    def __init__(self, ts_code):
        super(Gtk.Box, self).__init__()
        self.data = Data()
        self.name = Gtk.Button()
        self.close = Gtk.Button()
        self.closeImg = Gtk.Image.new_from_file("Icons/close.png")
        self.name.set_label(self.data.getCompanyFullNameByTsCode(ts_code))
        self.name.set_focus_on_click(False)
        self.close.set_image(self.closeImg)
        self.close.set_always_show_image(True)
        self.close.set_relief(Gtk.ReliefStyle.NONE)
        self.close.get_style_context().add_class("circular")
        self.name.set_name("button")
        self.close.set_name("button")
        screen = Gdk.Screen.get_default()
        provider = Gtk.CssProvider()
        style_context = Gtk.StyleContext()
        style_context.add_provider_for_screen(
            screen, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        css = b"""
                #button:hover {
                    background-color: gray;
                }
                """
        provider.load_from_data(css)

        self.add(self.name)
        self.add(self.close)

    def getFullName(self):
        return self.name.get_label()

class StatementInformationBox(Gtk.Box):
    data = Data()
    def __init__(self, ts_code):
        super(Gtk.Box, self).__init__()
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.tsCode = ts_code
        self.incomeStatementExpBox = None
        self.balanceSheetExpBox = None
        self.cashFlowStatementExpBox = None
        self.financialIndicatorExpBox = None
        self.preliminaryEarningsEstimateExpBox = None
        self.mainBusinessCompositionExpBox = None
        self.store = Gtk.ListStore(int)
        for i in (1, 2, 3, 4, 5):
            self.store.append( [getCurrentYear()-i] )

        # Add a ComboBox for selecting the year.
        self.combo = Gtk.ComboBox.new_with_model(self.store)
        renderer = Gtk.CellRendererText()
        self.combo.set_active(0)
        self.combo.pack_start(renderer, True)
        self.combo.add_attribute(renderer, 'text', 0)
        self.combo.connect("changed", self.refreshStatementInformation)
        self.add(self.combo)

        # Add profit statement.
        self.incomeStatementExpander = Gtk.Expander.new("income statement")
        self.incomeStatementExpander.set_spacing(1)
        self.add(self.incomeStatementExpander)
        self.refreshProfitStatement()

        # Add balance sheet.
        self.balanceSheetExpander = Gtk.Expander.new("balance sheet")
        self.balanceSheetExpander.set_spacing(1)
        self.add(self.balanceSheetExpander)
        self.refreshBalanceSheet()

        # Add cash flow statement.
        self.cashFlowStatementExpander = Gtk.Expander.new("cash flow statement")
        self.cashFlowStatementExpander.set_spacing(1)
        self.add(self.cashFlowStatementExpander)
        self.refreshCashFlowStatement()

        # Add financial indicator data.
        self.financialIndicatorExpander = Gtk.Expander.new("financial indicator")
        self.financialIndicatorExpander.set_spacing(1)
        self.add(self.financialIndicatorExpander)
        self.refreshFinancialIndicator()

        # Add Preliminary Earnings Estimate.
        self.preliminaryEarningsEstimateExpander = Gtk.Expander.new("Preliminary Earnings Estimate")
        self.preliminaryEarningsEstimateExpander.set_spacing(1)
        self.add(self.preliminaryEarningsEstimateExpander)
        self.refreshPreliminaryEarningsEstimate()

        # Add main business composition.
        self.mainBusinessCompositionExpander = Gtk.Expander.new("main business composition")
        self.mainBusinessCompositionExpander.set_spacing(1)
        self.add(self.mainBusinessCompositionExpander)
        self.refreshMainBusinessComposition()

    def getSelectedYear(self):
        _iter = self.combo.get_active_iter()
        if iter is not None:
            return self.combo.get_model()[_iter][0]
        else:
            return None

    def refreshProfitStatement(self):
        if self.incomeStatementExpBox is not None:
            self.incomeStatementExpander.remove(self.incomeStatementExpBox)
        incomeStatement = self.data.getIncomeStatement(self.tsCode, self.getSelectedYear())
        self.incomeStatementExpBox = packing(incomeStatement)
        self.incomeStatementExpBox.set_name("indentation_2em")
        self.incomeStatementExpander.add(self.incomeStatementExpBox)

    def refreshBalanceSheet(self):
        if self.balanceSheetExpBox is not None:
            self.balanceSheetExpander.remove(self.balanceSheetExpBox)
        balanceSheet = self.data.getBalanceSheet(self.tsCode, self.getSelectedYear())
        self.balanceSheetExpBox = packing(balanceSheet)
        self.balanceSheetExpBox.set_name("indentation_2em")
        self.balanceSheetExpander.add(self.balanceSheetExpBox)

    def refreshCashFlowStatement(self):
        if self.cashFlowStatementExpBox is not None:
            self.cashFlowStatementExpander.remove(self.cashFlowStatementExpBox)
        cashFlow = self.data.getCashFlowStatement(self.tsCode, self.getSelectedYear())
        self.cashFlowStatementExpBox = packing(cashFlow)
        self.cashFlowStatementExpBox.set_name("indentation_2em")
        self.cashFlowStatementExpander.add(self.cashFlowStatementExpBox)

    def refreshFinancialIndicator(self):
        if self.financialIndicatorExpBox is not None:
            self.financialIndicatorExpander.remove(self.financialIndicatorExpBox)
        financialIndicator = self.data.getFinancialIndicator(self.tsCode, self.getSelectedYear())
        self.financialIndicatorExpBox = packing(financialIndicator)
        self.financialIndicatorExpBox.set_name("indentation_2em")
        self.financialIndicatorExpander.add(self.financialIndicatorExpBox)

    def refreshPreliminaryEarningsEstimate(self):
        if self.preliminaryEarningsEstimateExpBox is not None:
            self.preliminaryEarningsEstimateExpander.remove(self.preliminaryEarningsEstimateExpBox)
        preliminaryEarningsEstimateExpander = self.data.getPreliminaryEarningsEstimate(self.tsCode, self.getSelectedYear())
        self.preliminaryEarningsEstimateExpBox = packing(preliminaryEarningsEstimateExpander)
        self.preliminaryEarningsEstimateExpBox.set_name("indentation_2em")
        self.preliminaryEarningsEstimateExpander.add(self.preliminaryEarningsEstimateExpBox)

    def refreshMainBusinessComposition(self):
        if self.mainBusinessCompositionExpBox is not None:
            self.mainBusinessCompositionExpander.remove(self.mainBusinessCompositionExpBox)
        mainBusinessComposition = self.data.getMainBusinessComposition(self.tsCode, self.getSelectedYear())
        self.mainBusinessCompositionExpBox = Gtk.Box()
        self.mainBusinessCompositionExpBox.set_orientation(Gtk.Orientation.VERTICAL)
        self.mainBusinessCompositionExpBox.modify_bg(Gtk.StateFlags(0), Gdk.Color(65535, 65535, 65535))
        if (mainBusinessComposition.empty):
            self.mainBusinessCompositionExpBox.add(Gtk.Label("There is no report.", selectable=True))
        else:
            pieChartDict = drawMainBusinessStructurePieChart(mainBusinessComposition)
            for i in pieChartDict:
                self.mainBusinessCompositionExpBox.add(pieChartDict[i])
        self.mainBusinessCompositionExpander.add(self.mainBusinessCompositionExpBox)

    def refreshStatementInformation(self, *args):
        """
        This callback function is called when the ComboBox option changes
        and the financial data is refreshed based on the changed information.
        """
        self.refreshProfitStatement()
        self.refreshBalanceSheet()
        self.refreshCashFlowStatement()
        self.refreshFinancialIndicator()
        self.refreshPreliminaryEarningsEstimate()
        self.refreshMainBusinessComposition()
        self.show_all()

class assetStructureAnalysisBox(Gtk.Box):
    data = Data()
    def __init__(self, ts_code):
        super(Gtk.Box, self).__init__()
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.tsCode = ts_code

        cur_year = getCurrentYear()
        balanceSheet_five_age = self.data.getBalanceSheet(self.tsCode, cur_year-5)
        balanceSheet_four_age = self.data.getBalanceSheet(self.tsCode, cur_year-4)
        balanceSheet_three_age = self.data.getBalanceSheet(self.tsCode, cur_year-3)
        balanceSheet_two_age = self.data.getBalanceSheet(self.tsCode, cur_year-2)
        balanceSheet_one_age = self.data.getBalanceSheet(self.tsCode, cur_year-1)
        storeOfcapitalStructureAnalysis = Gtk.ListStore(str, str, str, str, str, str)
        assetStructureStatement = Gtk.TreeView(storeOfcapitalStructureAnalysis, name="indentation")
        center_one = 38
        center_other = 15
        column_proj = Gtk.TreeViewColumn("项目".center(center_one))
        column_five = Gtk.TreeViewColumn((str(cur_year-5)+"年").center(center_other))
        column_four = Gtk.TreeViewColumn((str(cur_year-4)+"年").center(center_other))
        column_three = Gtk.TreeViewColumn((str(cur_year-3)+"年").center(center_other))
        column_two = Gtk.TreeViewColumn((str(cur_year-2)+"年").center(center_other))
        column_one = Gtk.TreeViewColumn((str(cur_year-1)+"年").center(center_other))

        project = Gtk.CellRendererText()
        five_ago = Gtk.CellRendererText()
        four_ago = Gtk.CellRendererText()
        three_ago = Gtk.CellRendererText()
        two_ago = Gtk.CellRendererText()
        one_ago = Gtk.CellRendererText()
        column_proj.pack_start(project, True)
        column_five.pack_start(five_ago, True)
        column_four.pack_start(four_ago, True)
        column_three.pack_start(three_ago, True)
        column_two.pack_start(two_ago, True)
        column_one.pack_start(one_ago, True)
        column_proj.add_attribute(project, "text", 0)
        column_five.add_attribute(five_ago, "text", 1)
        column_four.add_attribute(four_ago, "text", 2)
        column_three.add_attribute(three_ago, "text", 3)
        column_two.add_attribute(two_ago, "text", 4)
        column_one.add_attribute(one_ago, "text", 5)
        assetStructureStatement.append_column(column_proj)
        assetStructureStatement.append_column(column_five)
        assetStructureStatement.append_column(column_four)
        assetStructureStatement.append_column(column_three)
        assetStructureStatement.append_column(column_two)
        assetStructureStatement.append_column(column_one)

        self.add(Gtk.Label("资本结构表", name="center"))
        self.add(assetStructureStatement)
        ALR_five = getAssetLiabilityRatioByBalanceSheet(balanceSheet_five_age)
        ALR_four = getAssetLiabilityRatioByBalanceSheet(balanceSheet_four_age)
        ALR_three = getAssetLiabilityRatioByBalanceSheet(balanceSheet_three_age)
        ALR_two = getAssetLiabilityRatioByBalanceSheet(balanceSheet_two_age)
        ALR_one = getAssetLiabilityRatioByBalanceSheet(balanceSheet_one_age)

        CLR_five = getCurrentLiabilitiesRate(balanceSheet_five_age)
        CLR_four = getCurrentLiabilitiesRate(balanceSheet_four_age)
        CLR_three = getCurrentLiabilitiesRate(balanceSheet_three_age)
        CLR_two = getCurrentLiabilitiesRate(balanceSheet_two_age)
        CLR_one = getCurrentLiabilitiesRate(balanceSheet_one_age)

        SDO_five = getSourceDivOccupation(balanceSheet_five_age)
        SDO_four = getSourceDivOccupation(balanceSheet_four_age)
        SDO_three = getSourceDivOccupation(balanceSheet_three_age)
        SDO_two = getSourceDivOccupation(balanceSheet_two_age)
        SDO_one = getSourceDivOccupation(balanceSheet_one_age)

        storeOfcapitalStructureAnalysis.append(["资产负债率".center(center_one),
                                                ALR_five.center(center_other),
                                                ALR_four.center(center_other),
                                                ALR_three.center(center_other),
                                                ALR_two.center(center_other),
                                                ALR_one.center(center_other)
                                                ])
        temporary = []
        tem = [ALR_five, ALR_four, ALR_three, ALR_two, ALR_one]
        for n in range(len(tem)):
            if tem[n] is ' ':
                temporary.append(' ')
            else:
                temporary.append(str(100-float(tem[n][:tem[n].find('%')]))[:5]+'%')

        storeOfcapitalStructureAnalysis.append(["所有者权益占总资产比例".center(center_one),
                                                temporary[0].center(center_other),
                                                temporary[1].center(center_other),
                                                temporary[2].center(center_other),
                                                temporary[3].center(center_other),
                                                temporary[4].center(center_other)
                                                ])
        storeOfcapitalStructureAnalysis.append(["流动负债占总负债比例".center(center_one),
                                                CLR_five.center(center_other),
                                                CLR_four.center(center_other),
                                                CLR_three.center(center_other),
                                                CLR_two.center(center_other),
                                                CLR_one.center(center_other)
                                                ])

        temporary = []
        tem = [CLR_five, CLR_four, CLR_three, CLR_two, CLR_one]
        for n in range(len(tem)):
            if tem[n] is ' ':
                temporary.append(' ')
            else:
                temporary.append(str(100 - float(tem[n][:tem[n].find('%')]))[:5] + '%')

        storeOfcapitalStructureAnalysis.append(["非流动负债占总负债比例".center(center_one),
                                                temporary[0].center(center_other),
                                                temporary[1].center(center_other),
                                                temporary[2].center(center_other),
                                                temporary[3].center(center_other),
                                                temporary[4].center(center_other)
                                                ])
        storeOfcapitalStructureAnalysis.append(["长期资金来源/长期资金占用".center(center_one),
                                                SDO_five.center(center_other),
                                                SDO_four.center(center_other),
                                                SDO_three.center(center_other),
                                                SDO_two.center(center_other),
                                                SDO_one.center(center_other)
                                                ])


class profitabilityAnalysisBox(Gtk.Box):
    data = Data()

    def __init__(self, ts_code):
        super(Gtk.Box, self).__init__()
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.tsCode = ts_code

        cur_year = getCurrentYear()
        financialIndicator_five_age = self.data.getFinancialIndicator(self.tsCode, cur_year - 5)
        financialIndicator_four_age = self.data.getFinancialIndicator(self.tsCode, cur_year - 4)
        financialIndicator_three_age = self.data.getFinancialIndicator(self.tsCode, cur_year - 3)
        financialIndicator_two_age = self.data.getFinancialIndicator(self.tsCode, cur_year - 2)
        financialIndicator_one_age = self.data.getFinancialIndicator(self.tsCode, cur_year - 1)
        storeOfprofitabilityAnalysis = Gtk.ListStore(str, str, str, str, str, str)
        profitabilityAnalysisStatement = Gtk.TreeView(storeOfprofitabilityAnalysis)

        center_one = 38
        center_other = 15
        column_proj = Gtk.TreeViewColumn("财务指标".center(center_one))
        column_five = Gtk.TreeViewColumn((str(cur_year - 5) + "年").center(center_other))
        column_four = Gtk.TreeViewColumn((str(cur_year - 4) + "年").center(center_other))
        column_three = Gtk.TreeViewColumn((str(cur_year - 3) + "年").center(center_other))
        column_two = Gtk.TreeViewColumn((str(cur_year - 2) + "年").center(center_other))
        column_one = Gtk.TreeViewColumn((str(cur_year - 1) + "年").center(center_other))

        indicators = Gtk.CellRendererText()
        five_ago = Gtk.CellRendererText()
        four_ago = Gtk.CellRendererText()
        three_ago = Gtk.CellRendererText()
        two_ago = Gtk.CellRendererText()
        one_ago = Gtk.CellRendererText()
        column_proj.pack_start(indicators, True)
        column_five.pack_start(five_ago, True)
        column_four.pack_start(four_ago, True)
        column_three.pack_start(three_ago, True)
        column_two.pack_start(two_ago, True)
        column_one.pack_start(one_ago, True)
        column_proj.add_attribute(indicators, "text", 0)
        column_five.add_attribute(five_ago, "text", 1)
        column_four.add_attribute(four_ago, "text", 2)
        column_three.add_attribute(three_ago, "text", 3)
        column_two.add_attribute(two_ago, "text", 4)
        column_one.add_attribute(one_ago, "text", 5)
        profitabilityAnalysisStatement.append_column(column_proj)
        profitabilityAnalysisStatement.append_column(column_five)
        profitabilityAnalysisStatement.append_column(column_four)
        profitabilityAnalysisStatement.append_column(column_three)
        profitabilityAnalysisStatement.append_column(column_two)
        profitabilityAnalysisStatement.append_column(column_one)
        self.add(Gtk.Label("盈利能力指标对比", name="center"))
        self.add(profitabilityAnalysisStatement)

        GPM_five = getGrossProfitMargin(financialIndicator_five_age)
        GPM_four = getGrossProfitMargin(financialIndicator_four_age)
        GPM_three = getGrossProfitMargin(financialIndicator_three_age)
        GPM_two = getGrossProfitMargin(financialIndicator_two_age)
        GPM_one = getGrossProfitMargin(financialIndicator_one_age)

        storeOfprofitabilityAnalysis.append(["主营业务毛利率".center(center_one),
                                             GPM_five.center(center_other),
                                             GPM_four.center(center_other),
                                             GPM_three.center(center_other),
                                             GPM_two.center(center_other),
                                             GPM_one.center(center_other)
                                             ])

        NPMS_five = getNetProfitMarginOnSales(financialIndicator_five_age)
        NPMS_four = getNetProfitMarginOnSales(financialIndicator_four_age)
        NPMS_three = getNetProfitMarginOnSales(financialIndicator_three_age)
        NPMS_two = getNetProfitMarginOnSales(financialIndicator_two_age)
        NPMS_one = getNetProfitMarginOnSales(financialIndicator_one_age)

        storeOfprofitabilityAnalysis.append(["销售净利率".center(center_one),
                                             NPMS_five.center(center_other),
                                             NPMS_four.center(center_other),
                                             NPMS_three.center(center_other),
                                             NPMS_two.center(center_other),
                                             NPMS_one.center(center_other)
                                             ])

        ROE_five = getReturnOnEquity(financialIndicator_five_age)
        ROE_four = getReturnOnEquity(financialIndicator_four_age)
        ROE_three = getReturnOnEquity(financialIndicator_three_age)
        ROE_two = getReturnOnEquity(financialIndicator_two_age)
        ROE_one = getReturnOnEquity(financialIndicator_one_age)

        storeOfprofitabilityAnalysis.append(["净资产收益率".center(center_one),
                                             ROE_five.center(center_other),
                                             ROE_four.center(center_other),
                                             ROE_three.center(center_other),
                                             ROE_two.center(center_other),
                                             ROE_one.center(center_other)
                                             ])

        x = [cur_year-5, cur_year-4, cur_year-3, cur_year-2, cur_year-1]
        temporary = []
        tem = [GPM_five, GPM_four, GPM_three, GPM_two, GPM_one]
        for n in range(len(tem)):
            if tem[n] is " ":
                temporary.append(0)
            else:
                temporary.append(float(tem[n][:tem[n].find('%')]))

        self.add(Gtk.Label("注:图表中y轴为0表示数据缺失", name="remind"))
        y = [
            temporary[0],
            temporary[1],
            temporary[2],
            temporary[3],
            temporary[4]
             ]
        self.add(getLineChartImg(x, y, "主营业务毛利率变化趋势", "主营业务毛利率", "年份", "比率"))

        temporary = []
        tem = [NPMS_five, NPMS_four, NPMS_three, NPMS_two, NPMS_one]
        for n in range(len(tem)):
            if tem[n] is ' ':
                temporary.append(0)
            else:
                temporary.append(float(tem[n][:tem[n].find('%')]))

        y = [
            temporary[0],
            temporary[1],
            temporary[2],
            temporary[3],
            temporary[4]
        ]
        self.add(getLineChartImg(x, y, "销售净利率变化趋势", "销售净利率", "年份", "比率"))

        temporary = []
        tem = [ROE_five, ROE_four, ROE_three, ROE_two, ROE_one]
        for n in range(len(tem)):
            if tem[n] is ' ':
                temporary.append(0)
            else:
                temporary.append(float(tem[n][:tem[n].find('%')]))

        y = [
            temporary[0],
            temporary[1],
            temporary[2],
            temporary[3],
            temporary[4]
        ]
        self.add(getLineChartImg(x, y, "净资产收益率变化趋势", "净资产收益率", "年份", "比率"))

class growthAnalysisBox(Gtk.Box):
    data = Data()

    def __init__(self, ts_code):
        super(Gtk.Box, self).__init__()
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.tsCode = ts_code

        cur_year = getCurrentYear()
        financialIndicator_five_age_before = self.data.getFinancialIndicator(self.tsCode, cur_year - 6)
        financialIndicator_five_age = self.data.getFinancialIndicator(self.tsCode, cur_year - 5)
        financialIndicator_four_age = self.data.getFinancialIndicator(self.tsCode, cur_year - 4)
        financialIndicator_three_age = self.data.getFinancialIndicator(self.tsCode, cur_year - 3)
        financialIndicator_two_age = self.data.getFinancialIndicator(self.tsCode, cur_year - 2)
        financialIndicator_one_age = self.data.getFinancialIndicator(self.tsCode, cur_year - 1)
        balanceSheet_five_age = self.data.getBalanceSheet(self.tsCode, cur_year - 5)
        balanceSheet_four_age = self.data.getBalanceSheet(self.tsCode, cur_year - 4)
        balanceSheet_three_age = self.data.getBalanceSheet(self.tsCode, cur_year - 3)
        balanceSheet_two_age = self.data.getBalanceSheet(self.tsCode, cur_year - 2)
        balanceSheet_one_age = self.data.getBalanceSheet(self.tsCode, cur_year - 1)
        mainBusinessComposition_five_age_before = self.data.getMainBusinessComposition(self.tsCode, cur_year - 6)
        mainBusinessComposition_five_age = self.data.getMainBusinessComposition(self.tsCode, cur_year - 5)
        mainBusinessComposition_four_age = self.data.getMainBusinessComposition(self.tsCode, cur_year - 4)
        mainBusinessComposition_three_age = self.data.getMainBusinessComposition(self.tsCode, cur_year - 3)
        mainBusinessComposition_two_age = self.data.getMainBusinessComposition(self.tsCode, cur_year - 2)
        mainBusinessComposition_one_age = self.data.getMainBusinessComposition(self.tsCode, cur_year - 1)


        storeOfgrowthAnalysis = Gtk.ListStore(str, str, str, str, str, str)
        growthAnalysisStatement = Gtk.TreeView(storeOfgrowthAnalysis)

        center_one = 38
        center_other = 15
        column_proj = Gtk.TreeViewColumn("指标".center(center_one))
        column_five = Gtk.TreeViewColumn((str(cur_year - 5) + "年").center(center_other))
        column_four = Gtk.TreeViewColumn((str(cur_year - 4) + "年").center(center_other))
        column_three = Gtk.TreeViewColumn((str(cur_year - 3) + "年").center(center_other))
        column_two = Gtk.TreeViewColumn((str(cur_year - 2) + "年").center(center_other))
        column_one = Gtk.TreeViewColumn((str(cur_year - 1) + "年").center(center_other))

        indicators = Gtk.CellRendererText()
        five_ago = Gtk.CellRendererText()
        four_ago = Gtk.CellRendererText()
        three_ago = Gtk.CellRendererText()
        two_ago = Gtk.CellRendererText()
        one_ago = Gtk.CellRendererText()
        column_proj.pack_start(indicators, True)
        column_five.pack_start(five_ago, True)
        column_four.pack_start(four_ago, True)
        column_three.pack_start(three_ago, True)
        column_two.pack_start(two_ago, True)
        column_one.pack_start(one_ago, True)
        column_proj.add_attribute(indicators, "text", 0)
        column_five.add_attribute(five_ago, "text", 1)
        column_four.add_attribute(four_ago, "text", 2)
        column_three.add_attribute(three_ago, "text", 3)
        column_two.add_attribute(two_ago, "text", 4)
        column_one.add_attribute(one_ago, "text", 5)
        growthAnalysisStatement.append_column(column_proj)
        growthAnalysisStatement.append_column(column_five)
        growthAnalysisStatement.append_column(column_four)
        growthAnalysisStatement.append_column(column_three)
        growthAnalysisStatement.append_column(column_two)
        growthAnalysisStatement.append_column(column_one)

        self.add(Gtk.Label("成长性分析", name="center"))
        self.add(growthAnalysisStatement)

        TA_five = getTotalAssets(balanceSheet_five_age)
        TA_four = getTotalAssets(balanceSheet_four_age)
        TA_three = getTotalAssets(balanceSheet_three_age)
        TA_two = getTotalAssets(balanceSheet_two_age)
        TA_one = getTotalAssets(balanceSheet_one_age)

        storeOfgrowthAnalysis.append(["总资产".center(center_one),
                                      TA_five.center(center_other),
                                      TA_four.center(center_other),
                                      TA_three.center(center_other),
                                      TA_two.center(center_other),
                                      TA_one.center(center_other)
                                      ])

        TAGR_five = getTotalAssetsGrowthRate(financialIndicator_five_age)
        TAGR_four = getTotalAssetsGrowthRate(financialIndicator_four_age)
        TAGR_three = getTotalAssetsGrowthRate(financialIndicator_three_age)
        TAGR_two = getTotalAssetsGrowthRate(financialIndicator_two_age)
        TAGR_one = getTotalAssetsGrowthRate(financialIndicator_one_age)

        storeOfgrowthAnalysis.append(["总资产增长率".center(center_one),
                                      TAGR_five.center(center_other),
                                      TAGR_four.center(center_other),
                                      TAGR_three.center(center_other),
                                      TAGR_two.center(center_other),
                                      TAGR_one.center(center_other)
                                      ])

        MBI_five_before = getMainBusinessIncome(mainBusinessComposition_five_age_before)
        MBI_five = getMainBusinessIncome(mainBusinessComposition_five_age)
        MBI_four = getMainBusinessIncome(mainBusinessComposition_four_age)
        MBI_three = getMainBusinessIncome(mainBusinessComposition_three_age)
        MBI_two = getMainBusinessIncome(mainBusinessComposition_two_age)
        MBI_one = getMainBusinessIncome(mainBusinessComposition_one_age)

        storeOfgrowthAnalysis.append(["主营业务收入".center(center_one),
                                      MBI_five.center(center_other),
                                      MBI_four.center(center_other),
                                      MBI_three.center(center_other),
                                      MBI_two.center(center_other),
                                      MBI_one.center(center_other)
                                      ])

        MBI_temporary = []
        tem = [MBI_five_before, MBI_five, MBI_four, MBI_three, MBI_two, MBI_one]
        for n in range(len(tem)-1):
            if tem[n] is " " or tem[n+1] is " ":
                MBI_temporary.append(" ")
            else:
                MBI_temporary.append(str(((float(tem[n+1])-float(tem[n]))/float(tem[n]))*100)[:9]+"%")

        storeOfgrowthAnalysis.append(["主营业务收入增长率".center(center_one),
                                      MBI_temporary[0].center(center_other),
                                      MBI_temporary[1].center(center_other),
                                      MBI_temporary[2].center(center_other),
                                      MBI_temporary[3].center(center_other),
                                      MBI_temporary[4].center(center_other)
                                      ])

        NP_five_before = getNetProfit(financialIndicator_five_age_before)
        NP_five = getNetProfit(financialIndicator_five_age)
        NP_four = getNetProfit(financialIndicator_four_age)
        NP_three = getNetProfit(financialIndicator_three_age)
        NP_two = getNetProfit(financialIndicator_two_age)
        NP_one = getNetProfit(financialIndicator_one_age)

        storeOfgrowthAnalysis.append(["净利润".center(center_one),
                                      NP_five.center(center_other),
                                      NP_four.center(center_other),
                                      NP_three.center(center_other),
                                      NP_two.center(center_other),
                                      NP_one.center(center_other)
                                      ])

        NP_temporary = []
        tem = [NP_five_before, NP_five, NP_four, NP_three, NP_two, NP_one]
        for n in range(len(tem) - 1):
            if tem[n] is " " or tem[n + 1] is " ":
                NP_temporary.append(" ")
            else:
                NP_temporary.append(str(((float(tem[n + 1]) - float(tem[n])) / float(tem[n])) * 100)[:9] + "%")

        storeOfgrowthAnalysis.append(["净利润增长率".center(center_one),
                                      NP_temporary[0].center(center_other),
                                      NP_temporary[1].center(center_other),
                                      NP_temporary[2].center(center_other),
                                      NP_temporary[3].center(center_other),
                                      NP_temporary[4].center(center_other)
                                      ])

        self.add(Gtk.Label("注:图表中y轴为0表示数据缺失", name="remind"))
        # 总资产折线图
        x = [cur_year - 5, cur_year - 4, cur_year - 3, cur_year - 2, cur_year - 1]
        temporary = []
        tem = [TA_five, TA_four, TA_three, TA_two, TA_one]
        for n in range(len(tem)):
            if tem[n] is " ":
                temporary.append(0)
            else:
                temporary.append(toNumber(tem[n]))

        y = [
            temporary[0],
            temporary[1],
            temporary[2],
            temporary[3],
            temporary[4]
        ]
        self.add(getLineChartImg(x, y, "总资产变化趋势", "总资产", "年份", "总量"))

        # 主营业务收入增长率折线图
        x = [cur_year - 5, cur_year - 4, cur_year - 3, cur_year - 2, cur_year - 1]
        temporary = []
        tem = MBI_temporary
        for n in range(len(tem)):
            if tem[n] is " ":
                temporary.append(0)
            else:
                temporary.append(float(tem[n][:tem[n].find('%')]))

        y = [
            temporary[0],
            temporary[1],
            temporary[2],
            temporary[3],
            temporary[4]
        ]
        self.add(getLineChartImg(x, y, "主营业务收入增长率变化趋势", "主营业务收入增长率", "年份", "增长率"))

        # 净利润增长率折线图
        x = [cur_year - 5, cur_year - 4, cur_year - 3, cur_year - 2, cur_year - 1]
        temporary = []
        tem = NP_temporary
        for n in range(len(tem)):
            if tem[n] is " ":
                temporary.append(0)
            else:
                temporary.append(float(tem[n][:tem[n].find('%')]))

        y = [
            temporary[0],
            temporary[1],
            temporary[2],
            temporary[3],
            temporary[4]
        ]
        self.add(getLineChartImg(x, y, "净利润增长率变化趋势", "净利润增长率", "年份", "增长率"))


class operationalCapabilityAnalysisBox(Gtk.Box):
    data = Data()

    def __init__(self, ts_code):
        super(Gtk.Box, self).__init__()
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.tsCode = ts_code

        cur_year = getCurrentYear()
        financialIndicator_five_age = self.data.getFinancialIndicator(self.tsCode, cur_year - 5)
        financialIndicator_four_age = self.data.getFinancialIndicator(self.tsCode, cur_year - 4)
        financialIndicator_three_age = self.data.getFinancialIndicator(self.tsCode, cur_year - 3)
        financialIndicator_two_age = self.data.getFinancialIndicator(self.tsCode, cur_year - 2)
        financialIndicator_one_age = self.data.getFinancialIndicator(self.tsCode, cur_year - 1)

        storeOfoperationalCapabilityAnalysis = Gtk.ListStore(str, str, str, str, str, str)
        operationalCapabilityAnalysisStatement = Gtk.TreeView(storeOfoperationalCapabilityAnalysis)

        center_one = 38
        center_other = 15
        column_proj = Gtk.TreeViewColumn("指标".center(center_one))
        column_five = Gtk.TreeViewColumn((str(cur_year - 5) + "年").center(center_other))
        column_four = Gtk.TreeViewColumn((str(cur_year - 4) + "年").center(center_other))
        column_three = Gtk.TreeViewColumn((str(cur_year - 3) + "年").center(center_other))
        column_two = Gtk.TreeViewColumn((str(cur_year - 2) + "年").center(center_other))
        column_one = Gtk.TreeViewColumn((str(cur_year - 1) + "年").center(center_other))

        indicators = Gtk.CellRendererText()
        five_ago = Gtk.CellRendererText()
        four_ago = Gtk.CellRendererText()
        three_ago = Gtk.CellRendererText()
        two_ago = Gtk.CellRendererText()
        one_ago = Gtk.CellRendererText()
        column_proj.pack_start(indicators, True)
        column_five.pack_start(five_ago, True)
        column_four.pack_start(four_ago, True)
        column_three.pack_start(three_ago, True)
        column_two.pack_start(two_ago, True)
        column_one.pack_start(one_ago, True)
        column_proj.add_attribute(indicators, "text", 0)
        column_five.add_attribute(five_ago, "text", 1)
        column_four.add_attribute(four_ago, "text", 2)
        column_three.add_attribute(three_ago, "text", 3)
        column_two.add_attribute(two_ago, "text", 4)
        column_one.add_attribute(one_ago, "text", 5)
        operationalCapabilityAnalysisStatement.append_column(column_proj)
        operationalCapabilityAnalysisStatement.append_column(column_five)
        operationalCapabilityAnalysisStatement.append_column(column_four)
        operationalCapabilityAnalysisStatement.append_column(column_three)
        operationalCapabilityAnalysisStatement.append_column(column_two)
        operationalCapabilityAnalysisStatement.append_column(column_one)

        self.add(Gtk.Label("运营能力重要指标", name="center"))
        self.add(operationalCapabilityAnalysisStatement)

        IT_five = getInventoryTurnover(financialIndicator_five_age)
        IT_four = getInventoryTurnover(financialIndicator_four_age)
        IT_three = getInventoryTurnover(financialIndicator_three_age)
        IT_two = getInventoryTurnover(financialIndicator_two_age)
        IT_one = getInventoryTurnover(financialIndicator_one_age)

        storeOfoperationalCapabilityAnalysis.append(["存货周转率".center(center_one),
                                                     IT_five.center(center_other),
                                                     IT_four.center(center_other),
                                                     IT_three.center(center_other),
                                                     IT_two.center(center_other),
                                                     IT_one.center(center_other)
                                                     ])

        ART_five = getAccountsReceivableTurnover(financialIndicator_five_age)
        ART_four = getAccountsReceivableTurnover(financialIndicator_four_age)
        ART_three = getAccountsReceivableTurnover(financialIndicator_three_age)
        ART_two = getAccountsReceivableTurnover(financialIndicator_two_age)
        ART_one = getAccountsReceivableTurnover(financialIndicator_one_age)

        storeOfoperationalCapabilityAnalysis.append(["应收账款周转率".center(center_one),
                                                     ART_five.center(center_other),
                                                     ART_four.center(center_other),
                                                     ART_three.center(center_other),
                                                     ART_two.center(center_other),
                                                     ART_one.center(center_other)
                                                     ])

        TAT_five = getTotalAssetTurnover(financialIndicator_five_age)
        TAT_four = getTotalAssetTurnover(financialIndicator_four_age)
        TAT_three = getTotalAssetTurnover(financialIndicator_three_age)
        TAT_two = getTotalAssetTurnover(financialIndicator_two_age)
        TAT_one = getTotalAssetTurnover(financialIndicator_one_age)

        storeOfoperationalCapabilityAnalysis.append(["总资产周转率".center(center_one),
                                                     TAT_five.center(center_other),
                                                     TAT_four.center(center_other),
                                                     TAT_three.center(center_other),
                                                     TAT_two.center(center_other),
                                                     TAT_one.center(center_other)
                                                     ])

        self.add(Gtk.Label("注:图表中y轴为0表示数据缺失", name="remind"))
        # 存货周转率趋势图
        x = [cur_year - 5, cur_year - 4, cur_year - 3, cur_year - 2, cur_year - 1]
        temporary = []
        tem = [IT_five, IT_four, IT_three, IT_two, IT_one]
        for n in range(len(tem)):
            if tem[n] is " " or tem[n] is "NaN":
                temporary.append(0)
            else:
                temporary.append(toNumber(tem[n][:tem[n].find('%')]))

        y = [
            temporary[0],
            temporary[1],
            temporary[2],
            temporary[3],
            temporary[4]
        ]
        self.add(getLineChartImg(x, y, "存货周转率趋势图", "存货周转率", "年份", "周转率"))

        # 应收账款周转率趋势图
        x = [cur_year - 5, cur_year - 4, cur_year - 3, cur_year - 2, cur_year - 1]
        temporary = []
        tem = [ART_five, ART_four, ART_three, ART_two, ART_one]
        for n in range(len(tem)):
            if tem[n] is " " or tem[n] is "NaN":
                temporary.append(0)
            else:
                temporary.append(toNumber(tem[n][:tem[n].find('%')]))

        y = [
            temporary[0],
            temporary[1],
            temporary[2],
            temporary[3],
            temporary[4]
        ]
        self.add(getLineChartImg(x, y, "应收账款周转率趋势图", "应收账款周转率", "年份", "周转率"))

        # 总资产周转率趋势图
        x = [cur_year - 5, cur_year - 4, cur_year - 3, cur_year - 2, cur_year - 1]
        temporary = []
        tem = [TAT_five, TAT_four, TAT_three, TAT_two, TAT_one]
        for n in range(len(tem)):
            if tem[n] is " " or tem[n] is "NaN":
                temporary.append(0)
            else:
                temporary.append(toNumber(tem[n][:tem[n].find('%')]))

        y = [
            temporary[0],
            temporary[1],
            temporary[2],
            temporary[3],
            temporary[4]
        ]
        self.add(getLineChartImg(x, y, "总资产周转率趋势图", "总资产周转率", "年份", "周转率"))
 

class solvencyAnalysisBox(Gtk.Box):
    """偿债能力分析的内容"""
    data = Data()

    def __init__(self, ts_code):
        super(Gtk.Box, self).__init__()
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.tsCode = ts_code

        cur_year = getCurrentYear()
        financialIndicator_five_age = self.data.getFinancialIndicator(self.tsCode, cur_year - 5)
        financialIndicator_four_age = self.data.getFinancialIndicator(self.tsCode, cur_year - 4)
        financialIndicator_three_age = self.data.getFinancialIndicator(self.tsCode, cur_year - 3)
        financialIndicator_two_age = self.data.getFinancialIndicator(self.tsCode, cur_year - 2)
        financialIndicator_one_age = self.data.getFinancialIndicator(self.tsCode, cur_year - 1)

        storeOfSolvencyAnalysis = Gtk.ListStore(str, str, str, str, str, str)
        solvencyAnalysisStatement = Gtk.TreeView(storeOfSolvencyAnalysis)

        center_one = 38
        center_other = 15
        column_proj = Gtk.TreeViewColumn("指标".center(center_one))
        column_five = Gtk.TreeViewColumn((str(cur_year - 5) + "年").center(center_other))
        column_four = Gtk.TreeViewColumn((str(cur_year - 4) + "年").center(center_other))
        column_three = Gtk.TreeViewColumn((str(cur_year - 3) + "年").center(center_other))
        column_two = Gtk.TreeViewColumn((str(cur_year - 2) + "年").center(center_other))
        column_one = Gtk.TreeViewColumn((str(cur_year - 1) + "年").center(center_other))

        indicators = Gtk.CellRendererText()
        five_ago = Gtk.CellRendererText()
        four_ago = Gtk.CellRendererText()
        three_ago = Gtk.CellRendererText()
        two_ago = Gtk.CellRendererText()
        one_ago = Gtk.CellRendererText()
        column_proj.pack_start(indicators, True)
        column_five.pack_start(five_ago, True)
        column_four.pack_start(four_ago, True)
        column_three.pack_start(three_ago, True)
        column_two.pack_start(two_ago, True)
        column_one.pack_start(one_ago, True)
        column_proj.add_attribute(indicators, "text", 0)
        column_five.add_attribute(five_ago, "text", 1)
        column_four.add_attribute(four_ago, "text", 2)
        column_three.add_attribute(three_ago, "text", 3)
        column_two.add_attribute(two_ago, "text", 4)
        column_one.add_attribute(one_ago, "text", 5)
        solvencyAnalysisStatement.append_column(column_proj)
        solvencyAnalysisStatement.append_column(column_five)
        solvencyAnalysisStatement.append_column(column_four)
        solvencyAnalysisStatement.append_column(column_three)
        solvencyAnalysisStatement.append_column(column_two)
        solvencyAnalysisStatement.append_column(column_one)

        self.add(Gtk.Label("偿债能力指标", name="center"))
        self.add(solvencyAnalysisStatement)

        CR_five = getCurrentRatio(financialIndicator_five_age)
        CR_four = getCurrentRatio(financialIndicator_four_age)
        CR_three = getCurrentRatio(financialIndicator_three_age)
        CR_two = getCurrentRatio(financialIndicator_two_age)
        CR_one = getCurrentRatio(financialIndicator_one_age)

        storeOfSolvencyAnalysis.append(["流动比率".center(center_one),
                                                     CR_five.center(center_other),
                                                     CR_four.center(center_other),
                                                     CR_three.center(center_other),
                                                     CR_two.center(center_other),
                                                     CR_one.center(center_other)
                                                     ])

        QR_five = getQuickRatio(financialIndicator_five_age)
        QR_four = getQuickRatio(financialIndicator_four_age)
        QR_three = getQuickRatio(financialIndicator_three_age)
        QR_two = getQuickRatio(financialIndicator_two_age)
        QR_one = getQuickRatio(financialIndicator_one_age)

        storeOfSolvencyAnalysis.append(["速动比率".center(center_one),
                                                     QR_five.center(center_other),
                                                     QR_four.center(center_other),
                                                     QR_three.center(center_other),
                                                     QR_two.center(center_other),
                                                     QR_one.center(center_other)
                                                     ])
                                    
        ALR_five = getAssetLiabilityRatioByFinancialIndicator(financialIndicator_five_age)
        ALR_four = getAssetLiabilityRatioByFinancialIndicator(financialIndicator_four_age)
        ALR_three = getAssetLiabilityRatioByFinancialIndicator(financialIndicator_three_age)
        ALR_two = getAssetLiabilityRatioByFinancialIndicator(financialIndicator_two_age)
        ALR_one = getAssetLiabilityRatioByFinancialIndicator(financialIndicator_one_age)

        storeOfSolvencyAnalysis.append(["资产负债率".center(center_one),
                                                     ALR_five.center(center_other),
                                                     ALR_four.center(center_other),
                                                     ALR_three.center(center_other),
                                                     ALR_two.center(center_other),
                                                     ALR_one.center(center_other)
                                                     ])

        # 看情况添加房地产公司实际负债率   additional

        self.add(Gtk.Label("注:图表中y轴为0表示数据缺失", name="remind"))
        # 流动比率变化趋势图
        x = [cur_year - 5, cur_year - 4, cur_year - 3, cur_year - 2, cur_year - 1]
        temporary = []
        tem = [CR_five, CR_four, CR_three, CR_two, CR_one]
        for n in range(len(tem)):
            if tem[n] is " " or tem[n] is "NaN":
                temporary.append(0)
            else:
                temporary.append(toNumber(tem[n][:tem[n].find('%')]))

        y = [
            temporary[0],
            temporary[1],
            temporary[2],
            temporary[3],
            temporary[4]
        ]
        self.add(getLineChartImg(x, y, "流动比率变化趋势图", "流动比率", "年份", "比率"))

        # 速动比率变化趋势图
        x = [cur_year - 5, cur_year - 4, cur_year - 3, cur_year - 2, cur_year - 1]
        temporary = []
        tem = [ALR_five, ALR_four, ALR_three, ALR_two, ALR_one]
        for n in range(len(tem)):
            if tem[n] is " " or tem[n] is "NaN":
                temporary.append(0)
            else:
                temporary.append(toNumber(tem[n][:tem[n].find('%')]))

        y = [
            temporary[0],
            temporary[1],
            temporary[2],
            temporary[3],
            temporary[4]
        ]
        self.add(getLineChartImg(x, y, "速动比率变化趋势图", "速动比率", "年份", "比率"))


class cashFlowAnalysisBox(Gtk.Box):
    """现金流量分析的内容"""
    data = Data()

    def __init__(self, ts_code):
        super(Gtk.Box, self).__init__()
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.tsCode = ts_code

        cur_year = getCurrentYear()
        cashFlow_five_age = self.data.getCashFlowStatement(self.tsCode, cur_year - 5)
        cashFlow_four_age = self.data.getCashFlowStatement(self.tsCode, cur_year - 4)
        cashFlow_three_age = self.data.getCashFlowStatement(self.tsCode, cur_year - 3)
        cashFlow_two_age = self.data.getCashFlowStatement(self.tsCode, cur_year - 2)
        cashFlow_one_age = self.data.getCashFlowStatement(self.tsCode, cur_year - 1)

        storeOfCashFlowAnalysis = Gtk.ListStore(str, str, str, str, str, str)
        cashFlowAnalysisStatement = Gtk.TreeView(storeOfCashFlowAnalysis)

        center_one = 38
        center_other = 15
        column_proj = Gtk.TreeViewColumn("指标".center(center_one))
        column_five = Gtk.TreeViewColumn((str(cur_year - 5) + "年").center(center_other))
        column_four = Gtk.TreeViewColumn((str(cur_year - 4) + "年").center(center_other))
        column_three = Gtk.TreeViewColumn((str(cur_year - 3) + "年").center(center_other))
        column_two = Gtk.TreeViewColumn((str(cur_year - 2) + "年").center(center_other))
        column_one = Gtk.TreeViewColumn((str(cur_year - 1) + "年").center(center_other))

        indicators = Gtk.CellRendererText()
        five_ago = Gtk.CellRendererText()
        four_ago = Gtk.CellRendererText()
        three_ago = Gtk.CellRendererText()
        two_ago = Gtk.CellRendererText()
        one_ago = Gtk.CellRendererText()
        column_proj.pack_start(indicators, True)
        column_five.pack_start(five_ago, True)
        column_four.pack_start(four_ago, True)
        column_three.pack_start(three_ago, True)
        column_two.pack_start(two_ago, True)
        column_one.pack_start(one_ago, True)
        column_proj.add_attribute(indicators, "text", 0)
        column_five.add_attribute(five_ago, "text", 1)
        column_four.add_attribute(four_ago, "text", 2)
        column_three.add_attribute(three_ago, "text", 3)
        column_two.add_attribute(two_ago, "text", 4)
        column_one.add_attribute(one_ago, "text", 5)
        cashFlowAnalysisStatement.append_column(column_proj)
        cashFlowAnalysisStatement.append_column(column_five)
        cashFlowAnalysisStatement.append_column(column_four)
        cashFlowAnalysisStatement.append_column(column_three)
        cashFlowAnalysisStatement.append_column(column_two)
        cashFlowAnalysisStatement.append_column(column_one)

        self.add(Gtk.Label("现金流量指标", name="center"))
        self.add(cashFlowAnalysisStatement)

        CBA_five = getNetCashOfBusiness(cashFlow_five_age)
        CBA_four = getNetCashOfBusiness(cashFlow_four_age)
        CBA_three = getNetCashOfBusiness(cashFlow_three_age)
        CBA_two = getNetCashOfBusiness(cashFlow_two_age)
        CBA_one = getNetCashOfBusiness(cashFlow_one_age)

        storeOfCashFlowAnalysis.append(["经营活动产生的现金净额".center(center_one),
                                                     CBA_five.center(center_other),
                                                     CBA_four.center(center_other),
                                                     CBA_three.center(center_other),
                                                     CBA_two.center(center_other),
                                                     CBA_one.center(center_other)
                                                     ])

        CIA_five = getNetCashOfInvestment(cashFlow_five_age)
        CIA_four = getNetCashOfInvestment(cashFlow_four_age)
        CIA_three = getNetCashOfInvestment(cashFlow_three_age)
        CIA_two = getNetCashOfInvestment(cashFlow_two_age)
        CIA_one = getNetCashOfInvestment(cashFlow_one_age)

        storeOfCashFlowAnalysis.append(["投资活动产生的现金净额".center(center_one),
                                                     CIA_five.center(center_other),
                                                     CIA_four.center(center_other),
                                                     CIA_three.center(center_other),
                                                     CIA_two.center(center_other),
                                                     CIA_one.center(center_other)
                                                     ])
                                                     
        CFA_five = getNetCashOfFinancing(cashFlow_five_age)
        CFA_four = getNetCashOfFinancing(cashFlow_four_age)
        CFA_three = getNetCashOfFinancing(cashFlow_three_age)
        CFA_two = getNetCashOfFinancing(cashFlow_two_age)
        CFA_one = getNetCashOfFinancing(cashFlow_one_age)

        storeOfCashFlowAnalysis.append(["筹资活动产生的现金净额".center(center_one),
                                                     CFA_five.center(center_other),
                                                     CFA_four.center(center_other),
                                                     CFA_three.center(center_other),
                                                     CFA_two.center(center_other),
                                                     CFA_one.center(center_other)
                                                     ])

        NICE_five = getNetIncreaseInCashAndCashEquivalents(cashFlow_five_age)
        NICE_four = getNetIncreaseInCashAndCashEquivalents(cashFlow_four_age)
        NICE_three = getNetIncreaseInCashAndCashEquivalents(cashFlow_three_age)
        NICE_two = getNetIncreaseInCashAndCashEquivalents(cashFlow_two_age)
        NICE_one = getNetIncreaseInCashAndCashEquivalents(cashFlow_one_age)

        storeOfCashFlowAnalysis.append(["现金及现金等价物的净增加额".center(center_one),
                                                     NICE_five.center(center_other),
                                                     NICE_four.center(center_other),
                                                     NICE_three.center(center_other),
                                                     NICE_two.center(center_other),
                                                     NICE_one.center(center_other)
                                                     ])

        self.add(Gtk.Label("注:图表中y轴为0表示数据缺失", name="remind"))
        # 经营活动产生的现金净额变化图
        x = [cur_year - 5, cur_year - 4, cur_year - 3, cur_year - 2, cur_year - 1]
        temporary = []
        tem = [CBA_five, CBA_four, CBA_three, CBA_two, CBA_one]
        for n in range(len(tem)):
            if tem[n] is " " or tem[n] is "NaN":
                temporary.append(0)
            else:
                temporary.append(toNumber(tem[n][:tem[n].find('%')]))

        y = [
            temporary[0],
            temporary[1],
            temporary[2],
            temporary[3],
            temporary[4]
        ]
        self.add(getLineChartImg(x, y, "经营活动产生的现金净额变化图", "现金净额", "年份", "净额"))

        # 投资活动产生的现金净额变化图
        x = [cur_year - 5, cur_year - 4, cur_year - 3, cur_year - 2, cur_year - 1]
        temporary = []
        tem = [CIA_five, CIA_four, CIA_three, CIA_two, CIA_one]
        for n in range(len(tem)):
            if tem[n] is " " or tem[n] is "NaN":
                temporary.append(0)
            else:
                temporary.append(toNumber(tem[n][:tem[n].find('%')]))

        y = [
            temporary[0],
            temporary[1],
            temporary[2],
            temporary[3],
            temporary[4]
        ]
        self.add(getLineChartImg(x, y, "投资活动产生的现金净额变化图", "现金净额", "年份", "净额"))

        # 筹资活动产生的现金净额变化图
        x = [cur_year - 5, cur_year - 4, cur_year - 3, cur_year - 2, cur_year - 1]
        temporary = []
        tem = [CFA_five, CFA_four, CFA_three, CFA_two, CFA_one]
        for n in range(len(tem)):
            if tem[n] is " " or tem[n] is "NaN":
                temporary.append(0)
            else:
                temporary.append(toNumber(tem[n][:tem[n].find('%')]))

        y = [
            temporary[0],
            temporary[1],
            temporary[2],
            temporary[3],
            temporary[4]
        ]
        self.add(getLineChartImg(x, y, "筹资活动产生的现金净额变化图", "现金净额", "年份", "净额"))

        # 现金及现金等价物的净增加额变化图
        x = [cur_year - 5, cur_year - 4, cur_year - 3, cur_year - 2, cur_year - 1]
        temporary = []
        tem = [NICE_five, NICE_four, NICE_three, NICE_two, NICE_one]
        for n in range(len(tem)):
            if tem[n] is " " or tem[n] is "NaN":
                temporary.append(0)
            else:
                temporary.append(toNumber(tem[n][:tem[n].find('%')]))

        y = [
            temporary[0],
            temporary[1],
            temporary[2],
            temporary[3],
            temporary[4]
        ]
        self.add(getLineChartImg(x, y, "现金及现金等价物的净增加额变化图", "净增加额", "年份", "净增加额"))


class Content(Gtk.ScrolledWindow):
    # Initialize the page layout.
    def __init__(self, ts_code):
        # Initialize the box and set it's property.
        super(Gtk.ScrolledWindow, self).__init__()
        self.contentList = Gtk.ListBox()
        self.data = Data()
        self.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        self.contentList.set_selection_mode(Gtk.SelectionMode.NONE)
        self.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)

        screen = Gdk.Screen.get_default()
        provider = Gtk.CssProvider()
        style_context = Gtk.StyleContext()
        style_context.add_provider_for_screen(
            screen, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        css = b"""
        #indentation_2em {
            margin-left:2em;
        }

        #bg_odd {
            background-color: #C1D2F0;
            border:1px;
        }
        
        #center {
            margin-left:3em;
        }
        
        #remind {
            padding-right:0em;
            font-size:1em;
            color:yellow;
        }
        """
        provider.load_from_data(css)

        self.fullName = self.data.getCompanyFullNameByTsCode(ts_code)
        self.companyInformation = self.data.getCompanyInformationByTsCode(ts_code)

        # The following is the specific company information.
        # The full name of the company in the first line.
        self.fullnameLab = Gtk.Label(self.fullName)
        self.fullnameLab.set_selectable(True)
        fullNameRow = Gtk.ListBoxRow()
        fullNameRow.add(self.fullnameLab)
        self.contentList.insert(fullNameRow, -1)

        # Company details.
        self.companyInformationGrid = Gtk.Grid()
        self.companyInformationGrid.set_column_spacing(10)
        self.companyInformationGrid.add(Gtk.Label("法定代表人:", xalign=0, name="bg_odd"))
        # modify_bg(Gtk.StateFlags(0), Gdk.Color(49601, 53970, 61680))
        self.companyInformationGrid.attach(Gtk.Label(cutHead(self.companyInformation["legalRepresentative"].to_string()), xalign=0, selectable=True, name="bg_odd"), 1, 0, 1, 1)
        self.companyInformationGrid.attach(Gtk.Label("总经理:", xalign=0, name="bg_odd"), 2, 0, 1, 1)
        self.companyInformationGrid.attach(Gtk.Label(cutHead(self.companyInformation["generalManager"].to_string()),
                                                     xalign=0, selectable=True, name="bg_odd"), 3, 0, 1, 1)
        self.companyInformationGrid.attach(Gtk.Label("董事长秘书:", xalign=0, name="bg_odd"), 4, 0, 1, 1)
        self.companyInformationGrid.attach(Gtk.Label(cutHead(self.companyInformation["chairmanSecretary"].to_string()),
                                                     xalign=0, selectable=True, name="bg_odd"), 5, 0, 1, 1)
        self.companyInformationGrid.attach(Gtk.Label("注册资本:", xalign=0, name="bg_even"), 0, 1, 1, 1)
        self.companyInformationGrid.attach(Gtk.Label(cutHead(self.companyInformation["registeredCapital"].to_string())+'万',
                                                     xalign=0, selectable=True, name="bg_even"), 1, 1, 1, 1)
        self.companyInformationGrid.attach(Gtk.Label("注册日期:", xalign=0, name="bg_even"), 2, 1, 1, 1)
        self.companyInformationGrid.attach(Gtk.Label(cutHead(self.companyInformation["registrationDate"].to_string()),
                                                     xalign=0, selectable=True, name="bg_even"), 3, 1, 1, 1)
        self.companyInformationGrid.attach(Gtk.Label("股票代码:", xalign=0, name="bg_even"), 4, 1, 1, 1)
        self.companyInformationGrid.attach(Gtk.Label(cutHead(self.companyInformation["stockCode"].to_string()),
                                                     xalign=0, selectable=True, name="bg_even"), 5, 1, 1, 1)
        self.companyInformationGrid.attach(Gtk.Label("所在省份:", xalign=0, name="bg_odd"), 0, 2, 1, 1)
        self.companyInformationGrid.attach(Gtk.Label(cutHead(self.companyInformation["province"].to_string()),
                                                     xalign=0, selectable=True, name="bg_odd"), 1, 2, 1, 1)
        self.companyInformationGrid.attach(Gtk.Label("所在城市:", xalign=0, name="bg_odd"), 2, 2, 1, 1)
        city = cutHead(self.companyInformation["city"].to_string())
        self.companyInformationGrid.attach(Gtk.Label(city, xalign=0, selectable=True, name="bg_odd"), 3, 2, 1, 1)
        self.companyInformationGrid.attach(Gtk.Label("地址:", xalign=0, name="bg_odd"), 4, 2, 1, 1)  # *要设置最大宽度, 超出的点击...显示全部
        address = re.sub(',', '\n', cutHead(self.companyInformation["office"].to_string()))
        self.companyInformationGrid.attach(Gtk.Label(address[address.find(city[-1:])+1:], xalign=0, selectable=True, name="bg_odd"), 5, 2, 1, 1)
        self.companyInformationGrid.attach(Gtk.Label("邮箱:", xalign=0, name="bg_even"), 0, 3, 1, 1)   # *要设置最大宽度, 超出的点击...显示全部
        self.companyInformationGrid.attach(Gtk.Label(re.sub(';', '\n', cutHead(self.companyInformation["email"].to_string()), 5),
                                                     xalign=0, selectable=True, name="bg_even"), 1, 3, 1, 1)
        self.companyInformationGrid.attach(Gtk.Label("公司主页:", xalign=0, name="bg_even"), 2, 3, 1, 1)
        mailPage = Gtk.Label(xalign=0, selectable=True, name="bg_even")
        mailPageUrl = cutHead(self.companyInformation["website"].to_string())
        mailPage.set_markup("<a href=\"" + mailPageUrl + "\" title=\"official website\">" + mailPageUrl + "</a>")
        self.companyInformationGrid.attach(mailPage, 3, 3, 1, 1)
        self.companyInformationGrid.attach(Gtk.Label("员工人数:", xalign=0, name="bg_even"), 4, 3, 1, 1)
        self.companyInformationGrid.attach(Gtk.Label(cutHead(self.companyInformation["numberOfEmployees"].to_string()),
                                                     xalign=0, selectable=True, name="bg_even"), 5, 3, 1, 1)

        # *这里要隐藏多余的字并且可点击显示
        #How to set max width of GtkLabel properly?
        #https://stackoverflow.com/questions/27462926/how-to-set-max-width-of-gtklabel-properly

        companyIntroduction = Gtk.Label(cutHead(self.companyInformation["companyIntroduction"].to_string()))
        companyIntroduction.set_xalign(0)
        companyIntroduction.set_selectable(True)
        companyIntroduction.set_line_wrap(True)
        companyIntroduction.set_width_chars(40)
        scopeOfBusiness = Gtk.Label(cutHead(self.companyInformation["scopeOfBusiness"].to_string()))
        scopeOfBusiness.set_xalign(0)
        scopeOfBusiness.set_selectable(True)
        scopeOfBusiness.set_line_wrap(True)
        mainBusinessAndProducts = Gtk.Label(cutHead(self.companyInformation["mainBusinessAndProducts"].to_string()))
        mainBusinessAndProducts.set_xalign(0)
        mainBusinessAndProducts.set_selectable(True)
        mainBusinessAndProducts.set_line_wrap(True)
        companyIntroductionLbEvtBox = Gtk.EventBox()
        companyIntroductionLbEvtBox.add(Gtk.Label("公司介绍:", xalign=0))
        companyIntroductionLbEvtBox.modify_bg(Gtk.StateFlags(0), Gdk.Color(49601, 53970, 61680))
        companyIntroductionEvtBox = Gtk.EventBox()
        companyIntroductionEvtBox.add(companyIntroduction)
        companyIntroductionEvtBox.modify_bg(Gtk.StateFlags(0), Gdk.Color(49601, 53970, 61680))
        self.companyInformationGrid.attach(companyIntroductionLbEvtBox, 0, 4, 1, 1)  #(1, 4, 5, 1)
        self.companyInformationGrid.attach(companyIntroductionEvtBox, 1, 4, 5, 1)
        self.companyInformationGrid.attach(Gtk.Label("经营范围:", xalign=0), 0, 5, 1, 1)  #(1, 5, 5, 1)
        self.companyInformationGrid.attach(scopeOfBusiness, 1, 5, 5, 1)
        mainBusinessAndProductsLbEvtBox = Gtk.EventBox()
        mainBusinessAndProductsLbEvtBox.add(Gtk.Label("主营业务:", xalign=0))
        mainBusinessAndProductsLbEvtBox.modify_bg(Gtk.StateFlags(0), Gdk.Color(49601, 53970, 61680))
        mainBusinessAndProductsEvtBox = Gtk.EventBox()
        mainBusinessAndProductsEvtBox.add(mainBusinessAndProducts)
        mainBusinessAndProductsEvtBox.modify_bg(Gtk.StateFlags(0), Gdk.Color(49601, 53970, 61680))
        self.companyInformationGrid.attach(mainBusinessAndProductsLbEvtBox, 0, 6, 1, 1)  #(1, 6, 5, 1)
        self.companyInformationGrid.attach(mainBusinessAndProductsEvtBox, 1, 6, 5, 1)

        companyInformationRow = Gtk.ListBoxRow()
        companyInformationRow.add(self.companyInformationGrid)
        self.contentList.insert(companyInformationRow, -1)

        statementInformation = Gtk.Expander.new("statement information")    # 财务数据
        statementInformation.set_expanded(True)
        statementInformationBox = StatementInformationBox(ts_code)
        statementInformationBox.set_name("indentation_2em")

        statementInformation.add(statementInformationBox)
        statementInformationRow = Gtk.ListBoxRow()
        statementInformationRow.add(statementInformation)
        self.contentList.insert(statementInformationRow, -1)

        assetStructureAnalysisExp = Gtk.Expander.new("asset structure analysis")   # 资产结构分析
        assetStructureAnalysisExp.set_expanded(True)
        assetStructureAnalysisExp.add(assetStructureAnalysisBox(ts_code))
        assetStructureAnalysisRow = Gtk.ListBoxRow()
        assetStructureAnalysisRow.add(assetStructureAnalysisExp)
        self.contentList.insert(assetStructureAnalysisRow, -1)

        profitabilityAnalysisExp = Gtk.Expander.new("analysis of profitability")  # 盈利能力分析
        profitabilityAnalysisExp.set_expanded(True)
        profitabilityAnalysisExp.add(profitabilityAnalysisBox(ts_code))
        profitabilityAnalysisRow = Gtk.ListBoxRow()
        profitabilityAnalysisRow.add(profitabilityAnalysisExp)
        self.contentList.insert(profitabilityAnalysisRow, -1)

        growthAnalysisExp = Gtk.Expander.new("growth analysis")  # 成长性分析
        growthAnalysisExp.set_expanded(True)
        growthAnalysisExp.add(growthAnalysisBox(ts_code))
        growthAnalysisRow = Gtk.ListBoxRow()
        growthAnalysisRow.add(growthAnalysisExp)
        self.contentList.insert(growthAnalysisRow, -1)

        operationalCapabilityAnalysisExp = Gtk.Expander.new("operational capability analysis")  # 运营能力分析
        operationalCapabilityAnalysisExp.set_expanded(True)
        operationalCapabilityAnalysisExp.add(operationalCapabilityAnalysisBox(ts_code))
        operationalCapabilityAnalysisRow = Gtk.ListBoxRow()
        operationalCapabilityAnalysisRow.add(operationalCapabilityAnalysisExp)
        self.contentList.insert(operationalCapabilityAnalysisRow, -1)

        solvencyAnalysisExp = Gtk.Expander.new("Solvency analysis")  # 偿债能力分析
        solvencyAnalysisExp.set_expanded(True)
        solvencyAnalysisExp.add(solvencyAnalysisBox(ts_code))
        solvencyAnalysisRow = Gtk.ListBoxRow()
        solvencyAnalysisRow.add(solvencyAnalysisExp)
        self.contentList.insert(solvencyAnalysisRow, -1)

        cashFlowAnalysisExp = Gtk.Expander.new("Cash flow analysis")  # 现金流量分析
        cashFlowAnalysisExp.set_expanded(True)
        cashFlowAnalysisExp.add(cashFlowAnalysisBox(ts_code))
        cashFlowAnalysisRow = Gtk.ListBoxRow()
        cashFlowAnalysisRow.add(cashFlowAnalysisExp)
        self.contentList.insert(cashFlowAnalysisRow, -1)


        self.add(self.contentList)

class Card(Gtk.Box):
    __gsignals__ = {
        'close_clicked': (GObject.SIGNAL_RUN_FIRST, None,
                      (str,)),
        'tab_clicked': (GObject.SIGNAL_RUN_FIRST, None,
                        (str,))
    }
    def __init__(self, ts_code):
        super(Gtk.Box, self).__init__()
        self.tabItem = TabItem(ts_code)
        self.content = Content(ts_code)
        self.tabItem.close.connect("clicked", self.on_close_clicked)
        self.tabItem.name.connect("clicked", self.on_tab_clicked)

    def on_close_clicked(self, *str):
        self.emit("close_clicked", self.tabItem.getFullName())

    def on_tab_clicked(self, *str):
        self.emit("tab_clicked", self.tabItem.getFullName())

class UI_Display(Gtk.Box):
    cards = {}
    data = Data()
    tabBar = Gtk.Box()
    contentArea = Gtk.Box()
    current = None      # Current page title

    # Init of UI_Display
    def __init__(self):
        super(Gtk.Box, self).__init__()
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.pack_start(self.tabBar, False, False, 1)
        self.pack_start(self.contentArea, True, True, 0)

    def addCardByTsCode(self, ts_code):
        name = self.data.getCompanyFullNameByTsCode(ts_code)
        if(name not in self.cards):
            self.cards[name] = Card(ts_code)
            self.cards[name].connect("close_clicked", self.on_close_clicked, str)
            self.cards[name].connect("tab_clicked", self.on_tab_clicked, str)
            self.__addPage(name)

        self.switch(name)

    def __addPage(self, name):
        self.tabBar.pack_start(self.cards[name].tabItem, False, False, 1)

    def switch(self, name):
        if (name == self.current):
            pass
        elif(self.current == None):
            self.current = name
            self.contentArea.pack_start(self.cards[name].content, True, True, 0)
            self.show_all()
        else:
            self.contentArea.remove(self.cards[self.current].content)
            self.contentArea.pack_start(self.cards[name].content, True, True, 0)
            self.current = name
            self.show_all()

    def deleteCardByName(self, name):
        if (name in self.cards):
            self.removeCardFromDisplayByName(name)
            del self.cards[name]
            if(self.current == name):
                self.current = None
                if(self.cards):
                    # If the tabbar is not empty, switch to the first TAB.
                    for key, value in self.cards.items():
                        self.switch(key)
                        break
        else:
            raise ValueError("Invalid arguments!", nameStr)

    def removeCardFromDisplayByName(self, name):
        self.tabBar.remove(self.cards[name].tabItem)
        self.contentArea.remove(self.cards[name].content)

    def on_search_selection_changed(self, *args):
        self.addCardByTsCode(args[1])
        self.show_all()

    def on_close_clicked(self, *str):
        self.deleteCardByName(str[1])

    def on_tab_clicked(self, *str):
        self.switch(str[1])


class UI_Window(Gtk.Window):
    menu = UI_Menu()
    display = UI_Display()
    search = UI_Search()
    searchTreeViewSelection = search.searchShow.get_selection()
    data = Data()
    low_right = Gtk.Box()
    test = None

    # Initialize of the main window. Add menu, search field and display field
    def init_ui(self):
        mainBox = Gtk.Box()
        mainBox.set_spacing(6)
        mainBox.set_orientation(Gtk.Orientation.VERTICAL)
        mainBox.pack_start(self.menu, False, False, 0)

        self.search.connect("selection_changed", self.display.on_search_selection_changed, str)
        low = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        low.pack1(self.search, False, False)
        self.low_right.pack_start(self.display, True, True, 0)

        low.add(self.low_right)
        mainBox.pack_start(low, True, True, 0)
        self.add(mainBox)
        GObject.timeout_add(1000, self.whenOpenProgram)

        self.show_all()
        Gtk.main()

    def __init__(self):
        Gtk.Window.__init__(self)
        self.set_icon_from_file("Icons/Icon.png")
        self.set_title("GraduationDesign")
        self.set_border_width(1)
        self.set_default_size(1350, 900)
        self.connect("destroy", Gtk.main_quit)
        self.init_ui()

    def whenOpenProgram(self):
        self.search.on_refresh_clicked(self.search)
        return False

    # *欢迎界面
    # *设置token