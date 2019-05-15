import os, time, datetime
import pandas as pd
import tushare as ts
from analyze import *

pd.set_option('max_colwidth',500)
pd.options.display.max_columns = 10


class Data():
    __token = "8092ff2edbbd5b2dd960ea2e16ce8dfafa60f319f2bc27652a119087"
    __SavedFileNameOfPublicCompanies = "data/publicCompanies.csv"
    __SavedFileNameOfCompanyInformation_SSE = "data/companyInformation_SSE.csv"
    __SavedFileNameOfCompanyInformation_SZSE = "data/companyInformation_SZSE.csv"
    __SavedFileNameOfCompanyInformation = "data/companyInformation.csv"
    __DataUpdateFrequency = 60
    pro = None
    publicCompanies = None
    companyInformation = None
    companyInformation_SSE = None
    companyInformation_SZSE = None
    def __init__(self):
        # Set my TOKEN and initialize the pro api of TuShare.
        ts.set_token(self.__token)
        Data.pro = ts.pro_api()

        # Make sure that the necessary directories exist to store the information retrieved to avoid duplicate retrieval.
        checkDirectory("data")
        # If the data is saved as a file and the last update interval of the data is less than the update frequency,the data is read directly from the file.
        if(os.path.isfile(self.__SavedFileNameOfPublicCompanies) and Data.__getTimeDifference(self.__SavedFileNameOfPublicCompanies) < self.__DataUpdateFrequency):
            Data.publicCompanies = pd.read_csv(self.__SavedFileNameOfPublicCompanies, header=0, dtype={'symbol':str}, index_col=0)
        else:
            Data.publicCompanies = self.pro.stock_basic(exchange='', list_status='L',
                                                        fields='ts_code,symbol,name,fullname,area,industry,market,list_date')
            Data.publicCompanies.to_csv(self.__SavedFileNameOfPublicCompanies)

        if (os.path.isfile(self.__SavedFileNameOfCompanyInformation_SSE) and Data.__getTimeDifference(self.__SavedFileNameOfCompanyInformation_SSE) < self.__DataUpdateFrequency):
            Data.companyInformation_SSE = pd.read_csv(self.__SavedFileNameOfCompanyInformation_SSE, header=0, dtype={'symbol':str}, index_col=0)
        else:
            Data.companyInformation_SSE = Data.pro.stock_company(exchange='SSE',
                                                                 fields='ts_code,chairman,manager,secretary,reg_capital,setup_date,province,city,introduction,website,email,office,employees,main_business,business_scope')
            Data.companyInformation_SSE.to_csv(self.__SavedFileNameOfCompanyInformation_SSE)

        if (os.path.isfile(self.__SavedFileNameOfCompanyInformation_SZSE) and Data.__getTimeDifference(self.__SavedFileNameOfCompanyInformation_SZSE) < self.__DataUpdateFrequency):
            Data.companyInformation_SZSE = pd.read_csv(self.__SavedFileNameOfCompanyInformation_SZSE, header=0, dtype={'symbol':str}, index_col=0)
        else:
            Data.companyInformation_SZSE = Data.pro.stock_company(exchange='SZSE',
                                                                  fields='ts_code,chairman,manager,secretary,reg_capital,setup_date,province,city,introduction,website,email,office,employees,main_business,business_scope')
            Data.companyInformation_SZSE.to_csv(self.__SavedFileNameOfCompanyInformation_SZSE)

        if (os.path.isfile(self.__SavedFileNameOfCompanyInformation) and Data.__getTimeDifference(self.__SavedFileNameOfCompanyInformation_SZSE) < self.__DataUpdateFrequency):
            Data.companyInformation = pd.read_csv(self.__SavedFileNameOfCompanyInformation)
        else:
            Data.companyInformation = Data.companyInformation_SSE.append(self.companyInformation_SZSE)
            Data.companyInformation.to_csv(self.__SavedFileNameOfCompanyInformation)

    def __getTimeDifference(filenm):
        #Gets the last modification time.
        modifiedTime = time.localtime(os.stat(filenm).st_mtime)
        y = time.strftime('%Y', modifiedTime)
        m = time.strftime('%m', modifiedTime)
        d = time.strftime('%d', modifiedTime)
        d1 = datetime(int(y), int(m), int(d))

        now = time.localtime(time.time())
        y = time.strftime('%Y', now)
        m = time.strftime('%m', now)
        d = time.strftime('%d', now)
        d2 = datetime(int(y), int(m), int(d))

        return (d2 - d1).days

    def getListOfPublicCompanies(self):
        return Data.publicCompanies

    def getTsCodeBySymbol(self, symbol):
        return filterSymbol(Data.publicCompanies, symbol).iat[0, 0]

    def getCompanyFullNameByTsCode(self, TsCode):
        return filterTsCode(Data.publicCompanies, TsCode).iat[0, 5]

    def getCompanyInformationByTsCode(self, TsCode):
        ret_Dict = None
        ret = filterTsCode(Data.companyInformation, TsCode)
        for index, row in ret.iterrows():
            #Basic information of listed companies.
            ret_Dict = {
                "stockCode": ret["ts_code"],                     #Stock code
                "legalRepresentative": ret["chairman"],          #Legal representative
                "generalManager": ret["manager"],                #General manager
                "chairmanSecretary": ret["secretary"],           #Chairman secretary
                "registeredCapital": ret["reg_capital"],        #Registered capital
                "registrationDate": ret["setup_date"],          #Registration date
                "province": ret["province"],
                "city": ret["city"],
                "companyIntroduction": ret["introduction"],     #Company introduction
                "website": ret["website"],                      #Company's home page
                "email": ret["email"],
                "office": ret["office"],
                "numberOfEmployees": ret["employees"],          #Number of employees
                "mainBusinessAndProducts": ret["main_business"],#Main business and products
                "scopeOfBusiness": ret["business_scope"]        #Scope of business
            }

        return ret_Dict

    def getIncomeStatement(self, tsCode, year):
        dir = "data" + os.sep + self.getCompanyFullNameByTsCode(tsCode) + os.sep + str(year)
        fileName = dir + os.sep + "incomeStatement.csv"
        ret_Dict = None
        checkDirectory(dir)
        if(os.path.isfile(fileName)):
            incomeStatement = pd.read_csv(fileName, header=0, index_col=0)
        else:
            incomeStatement = Data.pro.income(ts_code = tsCode, period = str(year)+"1231",
                                              fields="ann_date,"            # str 	公告日期
                                                     "f_ann_date,"          # str 	实际公告日期，即发生过数据变更的最终日期
                                                     "end_date,"            # str 	报告期
                                                     "basic_eps,"           # float 	基本每股收益
                                                     "diluted_eps,"         # float 	稀释每股收益
                                                     "total_revenue,"       # float 	营业总收入 (元，下同)
                                                     "revenue,"             # float 	营业收入
                                                     "int_income,"          # float 	利息收入
                                                     "prem_earned,"         # float 	已赚保费
                                                     "comm_income,"         # float 	手续费及佣金收入
                                                     "n_commis_income,"     # float 	手续费及佣金净收入
                                                     "n_oth_income,"        # float 	其他经营净收益
                                                     "n_oth_b_income,"      # float 	加:其他业务净收益
                                                     "prem_income,"         # float 	保险业务收入
                                                     "out_prem,"            # float 	减:分出保费
                                                     "une_prem_reser,"      # float 	提取未到期责任准备金
                                                     "reins_income,"        # float 	其中:分保费收入
                                                     "n_sec_tb_income,"     # float 	代理买卖证券业务净收入
                                                     "n_sec_uw_income,"     # float 	证券承销业务净收入
                                                     "n_asset_mg_income,"   # float 	受托客户资产管理业务净收入
                                                     "oth_b_income,"        # float 	其他业务收入
                                                     "fv_value_chg_gain,"   # float 	加:公允价值变动净收益
                                                     "invest_income,"       # float 	加:投资净收益
                                                     "ass_invest_income,"   # float 	其中:对联营企业和合营企业的投资收益
                                                     "forex_gain,"          # float 	加:汇兑净收益
                                                     "total_cogs,"          # float 	营业总成本
                                                     "oper_cost,"           # float 	减:营业成本
                                                     "int_exp,"             # float 	减:利息支出
                                                     "comm_exp,"            # float 	减:手续费及佣金支出
                                                     "biz_tax_surchg,"      # float 	减:营业税金及附加
                                                     "sell_exp,"            # float 	减:销售费用
                                                     "admin_exp,"           # float 	减:管理费用
                                                     "fin_exp,"             # float 	减:财务费用
                                                     "assets_impair_loss,"  # float 	减:资产减值损失
                                                     "prem_refund,"         # float 	退保金
                                                     "compens_payout,"      # float 	赔付总支出
                                                     "reser_insur_liab,"    # float 	提取保险责任准备金
                                                     "div_payt,"            # float 	保户红利支出
                                                     "reins_exp,"           # float 	分保费用
                                                     "oper_exp,"            # float 	营业支出
                                                     "compens_payout_refu,"      # float 	减:摊回赔付支出
                                                     "insur_reser_refu,"    # float 	减:摊回保险责任准备金
                                                     "reins_cost_refund,"   # float 	减:摊回分保费用
                                                     "other_bus_cost,"      # float 	其他业务成本
                                                     "operate_profit,"      # float 	营业利润
                                                     "non_oper_income,"     # float 	加:营业外收入
                                                     "non_oper_exp,"        # float 	减:营业外支出
                                                     "nca_disploss,"        # float 	其中:减:非流动资产处置净损失
                                                     "total_profit,"        # float 	利润总额
                                                     "income_tax,"          # float 	所得税费用
                                                     "n_income,"            # float 	净利润(含少数股东损益)
                                                     "n_income_attr_p,"     # float 	净利润(不含少数股东损益)
                                                     "minority_gain,"       # float 	少数股东损益
                                                     "oth_compr_income,"    # float 	其他综合收益
                                                     "t_compr_income,"      # float 	综合收益总额
                                                     "compr_inc_attr_p,"    # float 	归属于母公司(或股东)的综合收益总额
                                                     "compr_inc_attr_m_s,"  # float 	归属于少数股东的综合收益总额
                                                     "ebit,"                # float 	息税前利润
                                                     "ebitda,"              # float 	息税折旧摊销前利润
                                                     "insurance_exp,"       # float 	保险业务支出
                                                     "undist_profit,"       # float 	年初未分配利润
                                                     "distable_profit"      # float 	可分配利润
                                              )
            incomeStatement.to_csv(fileName)

        for index, row in incomeStatement.iterrows():
            # Store the income statement data in the dictionary.
            ret_Dict = {
                "ann_date": ("公告日期", cutHead(incomeStatement["ann_date"].to_string())),
                "f_ann_date": ("实际公告日期", cutHead(incomeStatement["f_ann_date"].to_string())),
                "end_date": ("报告期", cutHead(incomeStatement["end_date"].to_string())),
                "basic_eps": ("基本每股收益", cutHead(incomeStatement["basic_eps"].to_string())),
                "diluted_eps": ("稀释每股收益", cutHead(incomeStatement["diluted_eps"].to_string())),
                "total_revenue": ("营业总收入", cutHead(incomeStatement["total_revenue"].to_string())),
                "revenue": ("营业收入", cutHead(incomeStatement["revenue"].to_string())),
                "int_income": ("利息收入", cutHead(incomeStatement["int_income"].to_string())),
                "prem_earned": ("已赚保费", cutHead(incomeStatement["prem_earned"].to_string())),
                "comm_income": ("手续费及佣金收入", cutHead(incomeStatement["comm_income"].to_string())),
                "n_commis_income": ("手续费及佣金净收入", cutHead(incomeStatement["n_commis_income"].to_string())),
                "n_oth_income": ("其他经营净收益", cutHead(incomeStatement["n_oth_income"].to_string())),
                "n_oth_b_income": ("加:其他业务净收益", cutHead(incomeStatement["n_oth_b_income"].to_string())),
                "prem_income": ("保险业务收入", cutHead(incomeStatement["prem_income"].to_string())),
                "out_prem": ("减:分出保费", cutHead(incomeStatement["out_prem"].to_string())),
                "une_prem_reser": ("提取未到期责任准备金", cutHead(incomeStatement["une_prem_reser"].to_string())),
                "reins_income": ("其中:分保费收入", cutHead(incomeStatement["reins_income"].to_string())),
                "n_sec_tb_income": ("代理买卖证券业务净收入", cutHead(incomeStatement["n_sec_tb_income"].to_string())),
                "n_sec_uw_income": ("证券承销业务净收入", cutHead(incomeStatement["n_sec_uw_income"].to_string())),
                "n_asset_mg_income": ("受托客户资产管理业务净收入", cutHead(incomeStatement["n_asset_mg_income"].to_string())),
                "oth_b_income": ("其他业务收入", cutHead(incomeStatement["oth_b_income"].to_string())),
                "fv_value_chg_gain": ("加:公允价值变动净收益", cutHead(incomeStatement["fv_value_chg_gain"].to_string())),
                "invest_income": ("加:投资净收益", cutHead(incomeStatement["invest_income"].to_string())),
                "ass_invest_income": ("其中:对联营企业和合营企业的投资收益",cutHead(incomeStatement["ass_invest_income"].to_string())),
                "forex_gain": ("加:汇兑净收益", cutHead(incomeStatement["forex_gain"].to_string())),
                "total_cogs": ("营业总成本", cutHead(incomeStatement["total_cogs"].to_string())),
                "oper_cost": ("减:营业成本", cutHead(incomeStatement["oper_cost"].to_string())),
                "int_exp": ("减:利息支出", cutHead(incomeStatement["int_exp"].to_string())),
                "comm_exp": ("减:手续费及佣金支出", cutHead(incomeStatement["comm_exp"].to_string())),
                "biz_tax_surchg": ("减:营业税金及附加", cutHead(incomeStatement["biz_tax_surchg"].to_string())),
                "sell_exp": ("减:销售费用", cutHead(incomeStatement["sell_exp"].to_string())),
                "admin_exp": ("减:管理费用", cutHead(incomeStatement["admin_exp"].to_string())),
                "fin_exp": ("减:财务费用", cutHead(incomeStatement["fin_exp"].to_string())),
                "assets_impair_loss": ("减:资产减值损失", cutHead(incomeStatement["assets_impair_loss"].to_string())),
                "prem_refund": ("退保金", cutHead(incomeStatement["prem_refund"].to_string())),
                "compens_payout": ("赔付总支出", cutHead(incomeStatement["compens_payout"].to_string())),
                "reser_insur_liab": ("提取保险责任准备金", cutHead(incomeStatement["reser_insur_liab"].to_string())),
                "div_payt": ("保户红利支出", cutHead(incomeStatement["div_payt"].to_string())),
                "reins_exp": ("分保费用", cutHead(incomeStatement["reins_exp"].to_string())),
                "oper_exp": ("营业支出", cutHead(incomeStatement["oper_exp"].to_string())),
                "compens_payout_refu": ("减:摊回赔付支出", cutHead(incomeStatement["compens_payout_refu"].to_string())),
                "insur_reser_refu": ("减:摊回保险责任准备金", cutHead(incomeStatement["insur_reser_refu"].to_string())),
                "reins_cost_refund": ("减:摊回分保费用", cutHead(incomeStatement["reins_cost_refund"].to_string())),
                "other_bus_cost": ("其他业务成本", cutHead(incomeStatement["other_bus_cost"].to_string())),
                "operate_profit": ("营业利润", cutHead(incomeStatement["operate_profit"].to_string())),
                "non_oper_income": ("加:营业外收入", cutHead(incomeStatement["non_oper_income"].to_string())),
                "non_oper_exp": ("减:营业外支出", cutHead(incomeStatement["non_oper_exp"].to_string())),
                "nca_disploss": ("其中:减:非流动资产处置净损失", cutHead(incomeStatement["nca_disploss"].to_string())),
                "total_profit": ("利润总额", cutHead(incomeStatement["total_profit"].to_string())),
                "income_tax": ("所得税费用", cutHead(incomeStatement["income_tax"].to_string())),
                "n_income": ("净利润(含少数股东损益)", cutHead(incomeStatement["n_income"].to_string())),
                "n_income_attr_p": ("净利润(不含少数股东损益)", cutHead(incomeStatement["n_income_attr_p"].to_string())),
                "minority_gain": ("少数股东损益", cutHead(incomeStatement["minority_gain"].to_string())),
                "oth_compr_income": ("其他综合收益", cutHead(incomeStatement["oth_compr_income"].to_string())),
                "t_compr_income": ("综合收益总额", cutHead(incomeStatement["t_compr_income"].to_string())),
                "compr_inc_attr_p": ("归属于母公司(或股东)的综合收益总额", cutHead(incomeStatement["compr_inc_attr_p"].to_string())),
                "compr_inc_attr_m_s": ("归属于少数股东的综合收益总额", cutHead(incomeStatement["compr_inc_attr_m_s"].to_string())),
                "ebit": ("息税前利润", cutHead(incomeStatement["ebit"].to_string())),
                "ebitda": ("息税折旧摊销前利润", cutHead(incomeStatement["ebitda"].to_string())),
                "insurance_exp": ("保险业务支出", cutHead(incomeStatement["insurance_exp"].to_string())),
                "undist_profit": ("年初未分配利润", cutHead(incomeStatement["undist_profit"].to_string())),
                "distable_profit": ("可分配利润", cutHead(incomeStatement["distable_profit"].to_string()))
            }

        return ret_Dict

    def getBalanceSheet(self, tsCode, year):
        dir = "data" + os.sep + self.getCompanyFullNameByTsCode(tsCode) + os.sep + str(year)
        fileName = dir + os.sep + "balanceSheet.csv"
        ret_Dict = None
        checkDirectory(dir)
        if(os.path.isfile(fileName)):
            balanceSheet = pd.read_csv(fileName, header=0, index_col=0)
        else:
            balanceSheet = Data.pro.balancesheet(ts_code = tsCode, period = str(year)+"1231",
                                                 fields="ann_date,"                     # str 	公告日期
                                                        "f_ann_date,"                   # str 	实际公告日期
                                                        "end_date,"                     # str 	报告期
                                                        "total_share,"                  # float 	期末总股本
                                                        "cap_rese,"                     # float 	资本公积金 (元，下同)
                                                        "undistr_porfit,"               # float 	未分配利润
                                                        "surplus_rese,"                 # float 	盈余公积金
                                                        "special_rese,"                 # float 	专项储备
                                                        "money_cap,"                    # float 	货币资金
                                                        "trad_asset,"                   # float 	交易性金融资产
                                                        "notes_receiv,"                 # float 	应收票据
                                                        "accounts_receiv,"              # float 	应收账款
                                                        "oth_receiv,"                   # float 	其他应收款
                                                        "prepayment,"                   # float 	预付款项
                                                        "div_receiv,"                   # float 	应收股利
                                                        "int_receiv,"                   # float 	应收利息
                                                        "inventories,"                  # float 	存货
                                                        "amor_exp,"                     # float 	长期待摊费用
                                                        "nca_within_1y,"                # float 	一年内到期的非流动资产
                                                        "sett_rsrv,"                    # float 	结算备付金
                                                        "loanto_oth_bank_fi,"           # float 	拆出资金
                                                        "premium_receiv,"               # float 	应收保费
                                                        "reinsur_receiv,"               # float 	应收分保账款
                                                        "reinsur_res_receiv,"           # float 	应收分保合同准备金
                                                        "pur_resale_fa,"                # float 	买入返售金融资产
                                                        "oth_cur_assets,"               # float 	其他流动资产
                                                        "total_cur_assets,"             # float 	流动资产合计
                                                        "fa_avail_for_sale,"            # float 	可供出售金融资产
                                                        "htm_invest,"                   # float 	持有至到期投资
                                                        "lt_eqt_invest,"                # float 	长期股权投资
                                                        "invest_real_estate,"           # float 	投资性房地产
                                                        "time_deposits,"                # float 	定期存款
                                                        "oth_assets,"                   # float 	其他资产
                                                        "lt_rec,"                       # float 	长期应收款
                                                        "fix_assets,"                   # float 	固定资产
                                                        "cip,"                          # float 	在建工程
                                                        "const_materials,"              # float 	工程物资
                                                        "fixed_assets_disp,"            # float 	固定资产清理
                                                        "produc_bio_assets,"            # float 	生产性生物资产
                                                        "oil_and_gas_assets,"           # float 	油气资产
                                                        "intan_assets,"                 # float 	无形资产
                                                        "r_and_d,"                      # float 	研发支出
                                                        "goodwill,"                     # float 	商誉
                                                        "lt_amor_exp,"                  # float 	长期待摊费用
                                                        "defer_tax_assets,"             # float 	递延所得税资产
                                                        "decr_in_disbur,"               # float 	发放贷款及垫款
                                                        "oth_nca,"                      # float 	其他非流动资产
                                                        "total_nca,"                    # float 	非流动资产合计
                                                        "cash_reser_cb,"                # float 	现金及存放中央银行款项
                                                        "depos_in_oth_bfi,"             # float 	存放同业和其它金融机构款项
                                                        "prec_metals,"                  # float 	贵金属
                                                        "deriv_assets,"                 # float 	衍生金融资产
                                                        "rr_reins_une_prem,"            # float 	应收分保未到期责任准备金
                                                        "rr_reins_outstd_cla,"          # float 	应收分保未决赔款准备金
                                                        "rr_reins_lins_liab,"           # float 	应收分保寿险责任准备金
                                                        "rr_reins_lthins_liab,"         # float 	应收分保长期健康险责任准备金
                                                        "refund_depos,"                 # float 	存出保证金
                                                        "ph_pledge_loans,"              # float 	保户质押贷款
                                                        "refund_cap_depos,"             # float 	存出资本保证金
                                                        "indep_acct_assets,"            # float 	独立账户资产
                                                        "client_depos,"                 # float 	其中：客户资金存款
                                                        "client_prov,"                  # float 	其中：客户备付金
                                                        "transac_seat_fee,"             # float 	其中:交易席位费
                                                        "invest_as_receiv,"             # float 	应收款项类投资
                                                        "total_assets,"                 # float 	资产总计
                                                        "lt_borr,"                      # float 	长期借款
                                                        "st_borr,"                      # float 	短期借款
                                                        "cb_borr,"                      # float 	向中央银行借款
                                                        "depos_ib_deposits,"            # float 	吸收存款及同业存放
                                                        "loan_oth_bank,"                # float 	拆入资金
                                                        "trading_fl,"                   # float 	交易性金融负债
                                                        "notes_payable,"                # float 	应付票据
                                                        "acct_payable,"                 # float 	应付账款
                                                        "adv_receipts,"                 # float 	预收款项
                                                        "sold_for_repur_fa,"            # float 	卖出回购金融资产款
                                                        "comm_payable,"                 # float 	应付手续费及佣金
                                                        "payroll_payable,"              # float 	应付职工薪酬
                                                        "taxes_payable,"                # float 	应交税费
                                                        "int_payable,"                  # float 	应付利息
                                                        "div_payable,"                  # float 	应付股利
                                                        "oth_payable,"                  # float 	其他应付款
                                                        "acc_exp,"                      # float 	预提费用
                                                        "deferred_inc,"                 # float 	递延收益
                                                        "st_bonds_payable,"             # float 	应付短期债券
                                                        "payable_to_reinsurer,"         # float 	应付分保账款
                                                        "rsrv_insur_cont,"              # float 	保险合同准备金
                                                        "acting_trading_sec,"           # float 	代理买卖证券款
                                                        "acting_uw_sec,"                # float 	代理承销证券款
                                                        "non_cur_liab_due_1y,"          # float 	一年内到期的非流动负债
                                                        "oth_cur_liab,"                 # float 	其他流动负债
                                                        "total_cur_liab,"               # float 	流动负债合计
                                                        "bond_payable,"                 # float 	应付债券
                                                        "lt_payable,"                   # float 	长期应付款
                                                        "specific_payables,"            # float 	专项应付款
                                                        "estimated_liab,"               # float 	预计负债
                                                        "defer_tax_liab,"               # float 	递延所得税负债
                                                        "defer_inc_non_cur_liab,"       # float 	递延收益-非流动负债
                                                        "oth_ncl,"                      # float 	其他非流动负债
                                                        "total_ncl,"                    # float 	非流动负债合计
                                                        "depos_oth_bfi,"                # float 	同业和其它金融机构存放款项
                                                        "deriv_liab,"                   # float 	衍生金融负债
                                                        "depos,"                        # float 	吸收存款
                                                        "agency_bus_liab,"              # float 	代理业务负债
                                                        "oth_liab,"                     # float 	其他负债
                                                        "prem_receiv_adva,"             # float 	预收保费
                                                        "depos_received,"               # float 	存入保证金
                                                        "ph_invest,"                    # float 	保户储金及投资款
                                                        "reser_une_prem,"               # float 	未到期责任准备金
                                                        "reser_outstd_claims,"          # float 	未决赔款准备金
                                                        "reser_lins_liab,"              # float 	寿险责任准备金
                                                        "reser_lthins_liab,"            # float 	长期健康险责任准备金
                                                        "indept_acc_liab,"              # float 	独立账户负债
                                                        "pledge_borr,"                  # float 	其中:质押借款
                                                        "indem_payable,"                # float 	应付赔付款
                                                        "policy_div_payable,"           # float 	应付保单红利
                                                        "total_liab,"                   # float 	负债合计
                                                        "treasury_share,"               # float 	减:库存股
                                                        "ordin_risk_reser,"             # float 	一般风险准备
                                                        "forex_differ,"                 # float 	外币报表折算差额
                                                        "invest_loss_unconf,"           # float 	未确认的投资损失
                                                        "minority_int,"                 # float 	少数股东权益
                                                        "total_hldr_eqy_exc_min_int,"   # float 	股东权益合计(不含少数股东权益)
                                                        "total_hldr_eqy_inc_min_int,"   # float 	股东权益合计(含少数股东权益)
                                                        "total_liab_hldr_eqy,"          # float 	负债及股东权益总计
                                                        "lt_payroll_payable,"           # float 	长期应付职工薪酬
                                                        "oth_comp_income,"              # float 	其他综合收益
                                                        "oth_eqt_tools,"                # float 	其他权益工具
                                                        "oth_eqt_tools_p_shr,"          # float 	其他权益工具(优先股)
                                                        "lending_funds,"                # float 	融出资金
                                                        "acc_receivable,"               # float 	应收款项
                                                        "st_fin_payable,"               # float 	应付短期融资款
                                                        "payables,"                     # float 	应付款项
                                                        "hfs_assets,"                   # float 	持有待售的资产
                                                        "hfs_sales"                     # float 	持有待售的负债
                                                 )
            balanceSheet.to_csv(fileName)

        for index, row in balanceSheet.iterrows():
            # Store the balance sheet data in the dictionary.
            ret_Dict = {
                 "ann_date": ("公告日期", cutHead(balanceSheet["ann_date"].to_string())),
                 "f_ann_date": ("实际公告日期", cutHead(balanceSheet["f_ann_date"].to_string())),
                 "end_date": ("报告期", cutHead(balanceSheet["end_date"].to_string())),
                 "total_share": ("期末总股本", cutHead(balanceSheet["total_share"].to_string())),
                 "cap_rese": ("资本公积金", cutHead(balanceSheet["cap_rese"].to_string())),
                 "undistr_porfit": ("未分配利润", cutHead(balanceSheet["undistr_porfit"].to_string())),
                 "surplus_rese": ("盈余公积金", cutHead(balanceSheet["surplus_rese"].to_string())),
                 "special_rese": ("专项储备", cutHead(balanceSheet["special_rese"].to_string())),
                 "money_cap": ("货币资金", cutHead(balanceSheet["money_cap"].to_string())),
                 "trad_asset": ("交易性金融资产", cutHead(balanceSheet["trad_asset"].to_string())),
                 "notes_receiv": ("应收票据", cutHead(balanceSheet["notes_receiv"].to_string())),
                 "accounts_receiv": ("应收账款", cutHead(balanceSheet["accounts_receiv"].to_string())),
                 "oth_receiv": ("其他应收款", cutHead(balanceSheet["oth_receiv"].to_string())),
                 "prepayment": ("预付款项", cutHead(balanceSheet["prepayment"].to_string())),
                 "div_receiv": ("应收股利", cutHead(balanceSheet["div_receiv"].to_string())),
                 "int_receiv": ("应收利息", cutHead(balanceSheet["int_receiv"].to_string())),
                 "inventories": ("存货", cutHead(balanceSheet["inventories"].to_string())),
                 "amor_exp": ("长期待摊费用", cutHead(balanceSheet["amor_exp"].to_string())),
                 "nca_within_1y": ("一年内到期的非流动资产", cutHead(balanceSheet["nca_within_1y"].to_string())),
                 "sett_rsrv": ("结算备付金", cutHead(balanceSheet["sett_rsrv"].to_string())),
                 "loanto_oth_bank_fi": ("拆出资金", cutHead(balanceSheet["loanto_oth_bank_fi"].to_string())),
                 "premium_receiv": ("应收保费", cutHead(balanceSheet["premium_receiv"].to_string())),
                 "reinsur_receiv": ("应收分保账款", cutHead(balanceSheet["reinsur_receiv"].to_string())),
                 "reinsur_res_receiv": ("应收分保合同准备金", cutHead(balanceSheet["reinsur_res_receiv"].to_string())),
                 "pur_resale_fa": ("买入返售金融资产", cutHead(balanceSheet["pur_resale_fa"].to_string())),
                 "oth_cur_assets": ("其他流动资产", cutHead(balanceSheet["oth_cur_assets"].to_string())),
                 "total_cur_assets": ("流动资产合计", cutHead(balanceSheet["total_cur_assets"].to_string())),
                 "fa_avail_for_sale": ("可供出售金融资产", cutHead(balanceSheet["fa_avail_for_sale"].to_string())),
                 "htm_invest": ("持有至到期投资", cutHead(balanceSheet["htm_invest"].to_string())),
                 "lt_eqt_invest": ("长期股权投资", cutHead(balanceSheet["lt_eqt_invest"].to_string())),
                 "invest_real_estate": ("投资性房地产", cutHead(balanceSheet["invest_real_estate"].to_string())),
                 "time_deposits": ("定期存款", cutHead(balanceSheet["time_deposits"].to_string())),
                 "oth_assets": ("其他资产", cutHead(balanceSheet["oth_assets"].to_string())),
                 "lt_rec": ("长期应收款", cutHead(balanceSheet["lt_rec"].to_string())),
                 "fix_assets": ("固定资产", cutHead(balanceSheet["fix_assets"].to_string())),
                 "cip": ("在建工程", cutHead(balanceSheet["cip"].to_string())),
                 "const_materials": ("工程物资", cutHead(balanceSheet["const_materials"].to_string())),
                 "fixed_assets_disp": ("固定资产清理", cutHead(balanceSheet["fixed_assets_disp"].to_string())),
                 "produc_bio_assets": ("生产性生物资产", cutHead(balanceSheet["produc_bio_assets"].to_string())),
                 "oil_and_gas_assets": ("油气资产", cutHead(balanceSheet["oil_and_gas_assets"].to_string())),
                 "intan_assets": ("无形资产", cutHead(balanceSheet["intan_assets"].to_string())),
                 "r_and_d": ("研发支出", cutHead(balanceSheet["r_and_d"].to_string())),
                 "goodwill": ("商誉", cutHead(balanceSheet["goodwill"].to_string())),
                 "lt_amor_exp": ("长期待摊费用", cutHead(balanceSheet["lt_amor_exp"].to_string())),
                 "defer_tax_assets": ("递延所得税资产", cutHead(balanceSheet["defer_tax_assets"].to_string())),
                 "decr_in_disbur": ("发放贷款及垫款", cutHead(balanceSheet["decr_in_disbur"].to_string())),
                 "oth_nca": ("其他非流动资产", cutHead(balanceSheet["oth_nca"].to_string())),
                 "total_nca": ("非流动资产合计", cutHead(balanceSheet["total_nca"].to_string())),
                 "cash_reser_cb": ("现金及存放中央银行款项", cutHead(balanceSheet["cash_reser_cb"].to_string())),
                 "depos_in_oth_bfi": ("存放同业和其它金融机构款项", cutHead(balanceSheet["depos_in_oth_bfi"].to_string())),
                 "prec_metals": ("贵金属", cutHead(balanceSheet["prec_metals"].to_string())),
                 "deriv_assets": ("衍生金融资产", cutHead(balanceSheet["deriv_assets"].to_string())),
                 "rr_reins_une_prem": ("应收分保未到期责任准备金", cutHead(balanceSheet["rr_reins_une_prem"].to_string())),
                 "rr_reins_outstd_cla": ("应收分保未决赔款准备金", cutHead(balanceSheet["rr_reins_outstd_cla"].to_string())),
                 "rr_reins_lins_liab": ("应收分保寿险责任准备金", cutHead(balanceSheet["rr_reins_lins_liab"].to_string())),
                 "rr_reins_lthins_liab": ("应收分保长期健康险责任准备金", cutHead(balanceSheet["rr_reins_lthins_liab"].to_string())),
                 "refund_depos": ("存出保证金", cutHead(balanceSheet["refund_depos"].to_string())),
                 "ph_pledge_loans": ("保户质押贷款", cutHead(balanceSheet["ph_pledge_loans"].to_string())),
                 "refund_cap_depos": ("存出资本保证金", cutHead(balanceSheet["refund_cap_depos"].to_string())),
                 "indep_acct_assets": ("独立账户资产", cutHead(balanceSheet["indep_acct_assets"].to_string())),
                 "client_depos": ("其中：客户资金存款", cutHead(balanceSheet["client_depos"].to_string())),
                 "client_prov": ("其中：客户备付金", cutHead(balanceSheet["client_prov"].to_string())),
                 "transac_seat_fee": ("其中:交易席位费", cutHead(balanceSheet["transac_seat_fee"].to_string())),
                 "invest_as_receiv": ("应收款项类投资", cutHead(balanceSheet["invest_as_receiv"].to_string())),
                 "total_assets": ("资产总计", cutHead(balanceSheet["total_assets"].to_string())),
                 "lt_borr": ("长期借款", cutHead(balanceSheet["lt_borr"].to_string())),
                 "st_borr": ("短期借款", cutHead(balanceSheet["st_borr"].to_string())),
                 "cb_borr": ("向中央银行借款", cutHead(balanceSheet["cb_borr"].to_string())),
                 "depos_ib_deposits": ("吸收存款及同业存放", cutHead(balanceSheet["depos_ib_deposits"].to_string())),
                 "loan_oth_bank": ("拆入资金", cutHead(balanceSheet["loan_oth_bank"].to_string())),
                 "trading_fl": ("交易性金融负债", cutHead(balanceSheet["trading_fl"].to_string())),
                 "notes_payable": ("应付票据", cutHead(balanceSheet["notes_payable"].to_string())),
                 "acct_payable": ("应付账款", cutHead(balanceSheet["acct_payable"].to_string())),
                 "adv_receipts": ("预收款项", cutHead(balanceSheet["adv_receipts"].to_string())),
                 "sold_for_repur_fa": ("卖出回购金融资产款", cutHead(balanceSheet["sold_for_repur_fa"].to_string())),
                 "comm_payable": ("应付手续费及佣金", cutHead(balanceSheet["comm_payable"].to_string())),
                 "payroll_payable": ("应付职工薪酬", cutHead(balanceSheet["payroll_payable"].to_string())),
                 "taxes_payable": ("应交税费", cutHead(balanceSheet["taxes_payable"].to_string())),
                 "int_payable": ("应付利息", cutHead(balanceSheet["int_payable"].to_string())),
                 "div_payable": ("应付股利", cutHead(balanceSheet["div_payable"].to_string())),
                 "oth_payable": ("其他应付款", cutHead(balanceSheet["oth_payable"].to_string())),
                 "acc_exp": ("预提费用", cutHead(balanceSheet["acc_exp"].to_string())),
                 "deferred_inc": ("递延收益", cutHead(balanceSheet["deferred_inc"].to_string())),
                 "st_bonds_payable": ("应付短期债券", cutHead(balanceSheet["st_bonds_payable"].to_string())),
                 "payable_to_reinsurer": ("应付分保账款", cutHead(balanceSheet["payable_to_reinsurer"].to_string())),
                 "rsrv_insur_cont": ("保险合同准备金", cutHead(balanceSheet["rsrv_insur_cont"].to_string())),
                 "acting_trading_sec": ("代理买卖证券款", cutHead(balanceSheet["acting_trading_sec"].to_string())),
                 "acting_uw_sec": ("代理承销证券款", cutHead(balanceSheet["acting_uw_sec"].to_string())),
                 "non_cur_liab_due_1y": ("一年内到期的非流动负债", cutHead(balanceSheet["non_cur_liab_due_1y"].to_string())),
                 "oth_cur_liab": ("其他流动负债", cutHead(balanceSheet["oth_cur_liab"].to_string())),
                 "total_cur_liab": ("流动负债合计", cutHead(balanceSheet["total_cur_liab"].to_string())),
                 "bond_payable": ("应付债券", cutHead(balanceSheet["bond_payable"].to_string())),
                 "lt_payable": ("长期应付款", cutHead(balanceSheet["lt_payable"].to_string())),
                 "specific_payables": ("专项应付款", cutHead(balanceSheet["specific_payables"].to_string())),
                 "estimated_liab": ("预计负债", cutHead(balanceSheet["estimated_liab"].to_string())),
                 "defer_tax_liab": ("递延所得税负债", cutHead(balanceSheet["defer_tax_liab"].to_string())),
                 "defer_inc_non_cur_liab": ("递延收益-非流动负债", cutHead(balanceSheet["defer_inc_non_cur_liab"].to_string())),
                 "oth_ncl": ("其他非流动负债", cutHead(balanceSheet["oth_ncl"].to_string())),
                 "total_ncl": ("非流动负债合计", cutHead(balanceSheet["total_ncl"].to_string())),
                 "depos_oth_bfi": ("同业和其它金融机构存放款项", cutHead(balanceSheet["depos_oth_bfi"].to_string())),
                 "deriv_liab": ("衍生金融负债", cutHead(balanceSheet["deriv_liab"].to_string())),
                 "depos": ("吸收存款", cutHead(balanceSheet["depos"].to_string())),
                 "agency_bus_liab": ("代理业务负债", cutHead(balanceSheet["agency_bus_liab"].to_string())),
                 "oth_liab": ("其他负债", cutHead(balanceSheet["oth_liab"].to_string())),
                 "prem_receiv_adva": ("预收保费", cutHead(balanceSheet["prem_receiv_adva"].to_string())),
                 "depos_received": ("存入保证金", cutHead(balanceSheet["depos_received"].to_string())),
                 "ph_invest": ("保户储金及投资款", cutHead(balanceSheet["ph_invest"].to_string())),
                 "reser_une_prem": ("未到期责任准备金", cutHead(balanceSheet["reser_une_prem"].to_string())),
                 "reser_outstd_claims": ("未决赔款准备金", cutHead(balanceSheet["reser_outstd_claims"].to_string())),
                 "reser_lins_liab": ("寿险责任准备金", cutHead(balanceSheet["reser_lins_liab"].to_string())),
                 "reser_lthins_liab": ("长期健康险责任准备金", cutHead(balanceSheet["reser_lthins_liab"].to_string())),
                 "indept_acc_liab": ("独立账户负债", cutHead(balanceSheet["indept_acc_liab"].to_string())),
                 "pledge_borr": ("其中:质押借款", cutHead(balanceSheet["pledge_borr"].to_string())),
                 "indem_payable": ("应付赔付款", cutHead(balanceSheet["indem_payable"].to_string())),
                 "policy_div_payable": ("应付保单红利", cutHead(balanceSheet["policy_div_payable"].to_string())),
                 "total_liab": ("负债合计", cutHead(balanceSheet["total_liab"].to_string())),
                 "treasury_share": ("减:库存股", cutHead(balanceSheet["treasury_share"].to_string())),
                 "ordin_risk_reser": ("一般风险准备", cutHead(balanceSheet["ordin_risk_reser"].to_string())),
                 "forex_differ": ("外币报表折算差额", cutHead(balanceSheet["forex_differ"].to_string())),
                 "invest_loss_unconf": ("未确认的投资损失", cutHead(balanceSheet["invest_loss_unconf"].to_string())),
                 "minority_int": ("少数股东权益", cutHead(balanceSheet["minority_int"].to_string())),
                 "total_hldr_eqy_exc_min_int": ("股东权益合计(不含少数股东权益)", cutHead(balanceSheet["total_hldr_eqy_exc_min_int"].to_string())),
                 "total_hldr_eqy_inc_min_int": ("股东权益合计(含少数股东权益)", cutHead(balanceSheet["total_hldr_eqy_inc_min_int"].to_string())),
                 "total_liab_hldr_eqy": ("负债及股东权益总计", cutHead(balanceSheet["total_liab_hldr_eqy"].to_string())),
                 "lt_payroll_payable": ("长期应付职工薪酬", cutHead(balanceSheet["lt_payroll_payable"].to_string())),
                 "oth_comp_income": ("其他综合收益", cutHead(balanceSheet["oth_comp_income"].to_string())),
                 "oth_eqt_tools": ("其他权益工具", cutHead(balanceSheet["oth_eqt_tools"].to_string())),
                 "oth_eqt_tools_p_shr": ("其他权益工具(优先股)", cutHead(balanceSheet["oth_eqt_tools_p_shr"].to_string())),
                 "lending_funds": ("融出资金", cutHead(balanceSheet["lending_funds"].to_string())),
                 "acc_receivable": ("应收款项", cutHead(balanceSheet["acc_receivable"].to_string())),
                 "st_fin_payable": ("应付短期融资款", cutHead(balanceSheet["st_fin_payable"].to_string())),
                 "payables": ("应付款项", cutHead(balanceSheet["payables"].to_string())),
                 "hfs_assets": ("持有待售的资产", cutHead(balanceSheet["hfs_assets"].to_string())),
                 "hfs_sales": ("持有待售的负债", cutHead(balanceSheet["hfs_sales"].to_string()))
            }

        return ret_Dict

    def getCashFlowStatement(self, tsCode, year):
        dir = "data" + os.sep + self.getCompanyFullNameByTsCode(tsCode) + os.sep + str(year)
        fileName = dir + os.sep + "cashFlowStatement.csv"
        ret_Dict = None
        checkDirectory(dir)
        if (os.path.isfile(fileName)):
            cashFlowStatement = pd.read_csv(fileName, header=0, index_col=0)
        else:
            cashFlowStatement = Data.pro.cashflow(ts_code=tsCode, period=str(year) + "1231",
                                                     fields="ann_date,"                     # str 	公告日期
                                                            "f_ann_date,"                   # str 	实际公告日期
                                                            "end_date,"                     # str 	报告期
                                                            "net_profit,"                   # float 	净利润 (元，下同)
                                                            "finan_exp,"                    # float 	财务费用
                                                            "c_fr_sale_sg,"                 # float 	销售商品、提供劳务收到的现金
                                                            "recp_tax_rends,"               # float 	收到的税费返还
                                                            "n_depos_incr_fi,"              # float 	客户存款和同业存放款项净增加额
                                                            "n_incr_loans_cb,"              # float 	向中央银行借款净增加额
                                                            "n_inc_borr_oth_fi,"            # float 	向其他金融机构拆入资金净增加额
                                                            "prem_fr_orig_contr,"           # float 	收到原保险合同保费取得的现金
                                                            "n_incr_insured_dep,"           # float 	保户储金净增加额
                                                            "n_reinsur_prem,"               # float 	收到再保业务现金净额
                                                            "n_incr_disp_tfa,"              # float 	处置交易性金融资产净增加额
                                                            "ifc_cash_incr,"                # float 	收取利息和手续费净增加额
                                                            "n_incr_disp_faas,"             # float 	处置可供出售金融资产净增加额
                                                            "n_incr_loans_oth_bank,"        # float 	拆入资金净增加额
                                                            "n_cap_incr_repur,"             # float 	回购业务资金净增加额
                                                            "c_fr_oth_operate_a,"           # float 	收到其他与经营活动有关的现金
                                                            "c_inf_fr_operate_a,"           # float 	经营活动现金流入小计
                                                            "c_paid_goods_s,"               # float 	购买商品、接受劳务支付的现金
                                                            "c_paid_to_for_empl,"           # float 	支付给职工以及为职工支付的现金
                                                            "c_paid_for_taxes,"             # float 	支付的各项税费
                                                            "n_incr_clt_loan_adv,"          # float 	客户贷款及垫款净增加额
                                                            "n_incr_dep_cbob,"              # float 	存放央行和同业款项净增加额
                                                            "c_pay_claims_orig_inco,"       # float 	支付原保险合同赔付款项的现金
                                                            "pay_handling_chrg,"            # float 	支付手续费的现金
                                                            "pay_comm_insur_plcy,"          # float 	支付保单红利的现金
                                                            "oth_cash_pay_oper_act,"        # float 	支付其他与经营活动有关的现金
                                                            "st_cash_out_act,"              # float 	经营活动现金流出小计
                                                            "n_cashflow_act,"               # float 	经营活动产生的现金流量净额
                                                            "oth_recp_ral_inv_act,"         # float 	收到其他与投资活动有关的现金
                                                            "c_disp_withdrwl_invest,"       # float 	收回投资收到的现金
                                                            "c_recp_return_invest,"         # float 	取得投资收益收到的现金
                                                            "n_recp_disp_fiolta,"           # float 	处置固定资产、无形资产和其他长期资产收回的现金净额
                                                            "n_recp_disp_sobu,"             # float 	处置子公司及其他营业单位收到的现金净额
                                                            "stot_inflows_inv_act,"         # float 	投资活动现金流入小计
                                                            "c_pay_acq_const_fiolta,"       # float 	购建固定资产、无形资产和其他长期资产支付的现金
                                                            "c_paid_invest,"                # float 	投资支付的现金
                                                            "n_disp_subs_oth_biz,"          # float 	取得子公司及其他营业单位支付的现金净额
                                                            "oth_pay_ral_inv_act,"          # float 	支付其他与投资活动有关的现金
                                                            "n_incr_pledge_loan,"           # float 	质押贷款净增加额
                                                            "stot_out_inv_act,"             # float 	投资活动现金流出小计
                                                            "n_cashflow_inv_act,"           # float 	投资活动产生的现金流量净额
                                                            "c_recp_borrow,"                # float 	取得借款收到的现金
                                                            "proc_issue_bonds,"             # float 	发行债券收到的现金
                                                            "oth_cash_recp_ral_fnc_act,"    # float 	收到其他与筹资活动有关的现金
                                                            "stot_cash_in_fnc_act,"         # float 	筹资活动现金流入小计
                                                            "free_cashflow,"                # float 	企业自由现金流量
                                                            "c_prepay_amt_borr,"            # float 	偿还债务支付的现金
                                                            "c_pay_dist_dpcp_int_exp,"      # float 	分配股利、利润或偿付利息支付的现金
                                                            "incl_dvd_profit_paid_sc_ms,"   # float 	其中:子公司支付给少数股东的股利、利润
                                                            "oth_cashpay_ral_fnc_act,"      # float 	支付其他与筹资活动有关的现金
                                                            "stot_cashout_fnc_act,"         # float 	筹资活动现金流出小计
                                                            "n_cash_flows_fnc_act,"         # float 	筹资活动产生的现金流量净额
                                                            "eff_fx_flu_cash,"              # float 	汇率变动对现金的影响
                                                            "n_incr_cash_cash_equ,"         # float 	现金及现金等价物净增加额
                                                            "c_cash_equ_beg_period,"        # float 	期初现金及现金等价物余额
                                                            "c_cash_equ_end_period,"        # float 	期末现金及现金等价物余额
                                                            "c_recp_cap_contrib,"           # float 	吸收投资收到的现金
                                                            "incl_cash_rec_saims,"          # float 	其中:子公司吸收少数股东投资收到的现金
                                                            "uncon_invest_loss,"            # float 	未确认投资损失
                                                            "prov_depr_assets,"             # float 	加:资产减值准备
                                                            "depr_fa_coga_dpba,"            # float 	固定资产折旧、油气资产折耗、生产性生物资产折旧
                                                            "amort_intang_assets,"          # float 	无形资产摊销
                                                            "lt_amort_deferred_exp,"        # float 	长期待摊费用摊销
                                                            "decr_deferred_exp,"            # float 	待摊费用减少
                                                            "incr_acc_exp,"                 # float 	预提费用增加
                                                            "loss_disp_fiolta,"             # float 	处置固定、无形资产和其他长期资产的损失
                                                            "loss_scr_fa,"                  # float 	固定资产报废损失
                                                            "loss_fv_chg,"                  # float 	公允价值变动损失
                                                            "invest_loss,"                  # float 	投资损失
                                                            "decr_def_inc_tax_assets,"      # float 	递延所得税资产减少
                                                            "incr_def_inc_tax_liab,"        # float 	递延所得税负债增加
                                                            "decr_inventories,"             # float 	存货的减少
                                                            "decr_oper_payable,"            # float 	经营性应收项目的减少
                                                            "incr_oper_payable,"            # float 	经营性应付项目的增加
                                                            "others,"                       # float 	其他
                                                            "im_net_cashflow_oper_act,"     # float 	经营活动产生的现金流量净额(间接法)
                                                            "conv_debt_into_cap,"           # float 	债务转为资本
                                                            "conv_copbonds_due_within_1y,"  # float 	一年内到期的可转换公司债券
                                                            "fa_fnc_leases,"                # float 	融资租入固定资产
                                                            "end_bal_cash,"                 # float 	现金的期末余额
                                                            "beg_bal_cash,"                 # float 	减:现金的期初余额
                                                            "end_bal_cash_equ,"             # float 	加:现金等价物的期末余额
                                                            "beg_bal_cash_equ,"             # float 	减:现金等价物的期初余额
                                                            "im_n_incr_cash_equ"            # float 	现金及现金等价物净增加额(间接法)
                                                  )
            cashFlowStatement.to_csv(fileName)

        for index, row in cashFlowStatement.iterrows():
            # Store the cash flow statement in the dictionary.
            ret_Dict = {
                "ann_date": ("公告日期", cutHead(cashFlowStatement["ann_date"].to_string())),
                 "f_ann_date": ("实际公告日期", cutHead(cashFlowStatement["f_ann_date"].to_string())),
                 "end_date": ("报告期", cutHead(cashFlowStatement["end_date"].to_string())),
                 "net_profit": ("净利润", cutHead(cashFlowStatement["net_profit"].to_string())),
                 "finan_exp": ("财务费用", cutHead(cashFlowStatement["finan_exp"].to_string())),
                 "c_fr_sale_sg": ("销售商品、提供劳务收到的现金", cutHead(cashFlowStatement["c_fr_sale_sg"].to_string())),
                 "recp_tax_rends": ("收到的税费返还", cutHead(cashFlowStatement["recp_tax_rends"].to_string())),
                 "n_depos_incr_fi": ("客户存款和同业存放款项净增加额", cutHead(cashFlowStatement["n_depos_incr_fi"].to_string())),
                 "n_incr_loans_cb": ("向中央银行借款净增加额", cutHead(cashFlowStatement["n_incr_loans_cb"].to_string())),
                 "n_inc_borr_oth_fi": ("向其他金融机构拆入资金净增加额", cutHead(cashFlowStatement["n_inc_borr_oth_fi"].to_string())),
                 "prem_fr_orig_contr": ("收到原保险合同保费取得的现金", cutHead(cashFlowStatement["prem_fr_orig_contr"].to_string())),
                 "n_incr_insured_dep": ("保户储金净增加额", cutHead(cashFlowStatement["n_incr_insured_dep"].to_string())),
                 "n_reinsur_prem": ("收到再保业务现金净额", cutHead(cashFlowStatement["n_reinsur_prem"].to_string())),
                 "n_incr_disp_tfa": ("处置交易性金融资产净增加额", cutHead(cashFlowStatement["n_incr_disp_tfa"].to_string())),
                 "ifc_cash_incr": ("收取利息和手续费净增加额", cutHead(cashFlowStatement["ifc_cash_incr"].to_string())),
                 "n_incr_disp_faas": ("处置可供出售金融资产净增加额", cutHead(cashFlowStatement["n_incr_disp_faas"].to_string())),
                 "n_incr_loans_oth_bank": ("拆入资金净增加额", cutHead(cashFlowStatement["n_incr_loans_oth_bank"].to_string())),
                 "n_cap_incr_repur": ("回购业务资金净增加额", cutHead(cashFlowStatement["n_cap_incr_repur"].to_string())),
                 "c_fr_oth_operate_a": ("收到其他与经营活动有关的现金", cutHead(cashFlowStatement["c_fr_oth_operate_a"].to_string())),
                 "c_inf_fr_operate_a": ("经营活动现金流入小计", cutHead(cashFlowStatement["c_inf_fr_operate_a"].to_string())),
                 "c_paid_goods_s": ("购买商品、接受劳务支付的现金", cutHead(cashFlowStatement["c_paid_goods_s"].to_string())),
                 "c_paid_to_for_empl": ("支付给职工以及为职工支付的现金", cutHead(cashFlowStatement["c_paid_to_for_empl"].to_string())),
                 "c_paid_for_taxes": ("支付的各项税费", cutHead(cashFlowStatement["c_paid_for_taxes"].to_string())),
                 "n_incr_clt_loan_adv": ("客户贷款及垫款净增加额", cutHead(cashFlowStatement["n_incr_clt_loan_adv"].to_string())),
                 "n_incr_dep_cbob": ("存放央行和同业款项净增加额", cutHead(cashFlowStatement["n_incr_dep_cbob"].to_string())),
                 "c_pay_claims_orig_inco": ("支付原保险合同赔付款项的现金", cutHead(cashFlowStatement["c_pay_claims_orig_inco"].to_string())),
                 "pay_handling_chrg": ("支付手续费的现金", cutHead(cashFlowStatement["pay_handling_chrg"].to_string())),
                 "pay_comm_insur_plcy": ("支付保单红利的现金", cutHead(cashFlowStatement["pay_comm_insur_plcy"].to_string())),
                 "oth_cash_pay_oper_act": ("支付其他与经营活动有关的现金", cutHead(cashFlowStatement["oth_cash_pay_oper_act"].to_string())),
                 "st_cash_out_act": ("经营活动现金流出小计", cutHead(cashFlowStatement["st_cash_out_act"].to_string())),
                 "n_cashflow_act": ("经营活动产生的现金流量净额", cutHead(cashFlowStatement["n_cashflow_act"].to_string())),
                 "oth_recp_ral_inv_act": ("收到其他与投资活动有关的现金", cutHead(cashFlowStatement["oth_recp_ral_inv_act"].to_string())),
                 "c_disp_withdrwl_invest": ("收回投资收到的现金", cutHead(cashFlowStatement["c_disp_withdrwl_invest"].to_string())),
                 "c_recp_return_invest": ("取得投资收益收到的现金", cutHead(cashFlowStatement["c_recp_return_invest"].to_string())),
                 "n_recp_disp_fiolta": ("处置固定资产、无形资产和其他长期资产收回的现金净额", cutHead(cashFlowStatement["n_recp_disp_fiolta"].to_string())),
                 "n_recp_disp_sobu": ("处置子公司及其他营业单位收到的现金净额", cutHead(cashFlowStatement["n_recp_disp_sobu"].to_string())),
                 "stot_inflows_inv_act": ("投资活动现金流入小计", cutHead(cashFlowStatement["stot_inflows_inv_act"].to_string())),
                 "c_pay_acq_const_fiolta": ("购建固定资产、无形资产和其他长期资产支付的现金", cutHead(cashFlowStatement["c_pay_acq_const_fiolta"].to_string())),
                 "c_paid_invest": ("投资支付的现金", cutHead(cashFlowStatement["c_paid_invest"].to_string())),
                 "n_disp_subs_oth_biz": ("取得子公司及其他营业单位支付的现金净额", cutHead(cashFlowStatement["n_disp_subs_oth_biz"].to_string())),
                 "oth_pay_ral_inv_act": ("支付其他与投资活动有关的现金", cutHead(cashFlowStatement["oth_pay_ral_inv_act"].to_string())),
                 "n_incr_pledge_loan": ("质押贷款净增加额", cutHead(cashFlowStatement["n_incr_pledge_loan"].to_string())),
                 "stot_out_inv_act": ("投资活动现金流出小计", cutHead(cashFlowStatement["stot_out_inv_act"].to_string())),
                 "n_cashflow_inv_act": ("投资活动产生的现金流量净额", cutHead(cashFlowStatement["n_cashflow_inv_act"].to_string())),
                 "c_recp_borrow": ("取得借款收到的现金", cutHead(cashFlowStatement["c_recp_borrow"].to_string())),
                 "proc_issue_bonds": ("发行债券收到的现金", cutHead(cashFlowStatement["proc_issue_bonds"].to_string())),
                 "oth_cash_recp_ral_fnc_act": ("收到其他与筹资活动有关的现金", cutHead(cashFlowStatement["oth_cash_recp_ral_fnc_act"].to_string())),
                 "stot_cash_in_fnc_act": ("筹资活动现金流入小计", cutHead(cashFlowStatement["stot_cash_in_fnc_act"].to_string())),
                 "free_cashflow": ("企业自由现金流量", cutHead(cashFlowStatement["free_cashflow"].to_string())),
                 "c_prepay_amt_borr": ("偿还债务支付的现金", cutHead(cashFlowStatement["c_prepay_amt_borr"].to_string())),
                 "c_pay_dist_dpcp_int_exp": ("分配股利、利润或偿付利息支付的现金", cutHead(cashFlowStatement["c_pay_dist_dpcp_int_exp"].to_string())),
                 "incl_dvd_profit_paid_sc_ms": ("其中:子公司支付给少数股东的股利、利润", cutHead(cashFlowStatement["incl_dvd_profit_paid_sc_ms"].to_string())),
                 "oth_cashpay_ral_fnc_act": ("支付其他与筹资活动有关的现金", cutHead(cashFlowStatement["oth_cashpay_ral_fnc_act"].to_string())),
                 "stot_cashout_fnc_act": ("筹资活动现金流出小计", cutHead(cashFlowStatement["stot_cashout_fnc_act"].to_string())),
                 "n_cash_flows_fnc_act": ("筹资活动产生的现金流量净额", cutHead(cashFlowStatement["n_cash_flows_fnc_act"].to_string())),
                 "eff_fx_flu_cash": ("汇率变动对现金的影响", cutHead(cashFlowStatement["eff_fx_flu_cash"].to_string())),
                 "n_incr_cash_cash_equ": ("现金及现金等价物净增加额", cutHead(cashFlowStatement["n_incr_cash_cash_equ"].to_string())),
                 "c_cash_equ_beg_period": ("期初现金及现金等价物余额", cutHead(cashFlowStatement["c_cash_equ_beg_period"].to_string())),
                 "c_cash_equ_end_period": ("期末现金及现金等价物余额", cutHead(cashFlowStatement["c_cash_equ_end_period"].to_string())),
                 "c_recp_cap_contrib": ("吸收投资收到的现金", cutHead(cashFlowStatement["c_recp_cap_contrib"].to_string())),
                 "incl_cash_rec_saims": ("其中:子公司吸收少数股东投资收到的现金", cutHead(cashFlowStatement["incl_cash_rec_saims"].to_string())),
                 "uncon_invest_loss": ("未确认投资损失", cutHead(cashFlowStatement["uncon_invest_loss"].to_string())),
                 "prov_depr_assets": ("加:资产减值准备", cutHead(cashFlowStatement["prov_depr_assets"].to_string())),
                 "depr_fa_coga_dpba": ("固定资产折旧、油气资产折耗、生产性生物资产折旧", cutHead(cashFlowStatement["depr_fa_coga_dpba"].to_string())),
                 "amort_intang_assets": ("无形资产摊销", cutHead(cashFlowStatement["amort_intang_assets"].to_string())),
                 "lt_amort_deferred_exp": ("长期待摊费用摊销", cutHead(cashFlowStatement["lt_amort_deferred_exp"].to_string())),
                 "decr_deferred_exp": ("待摊费用减少", cutHead(cashFlowStatement["decr_deferred_exp"].to_string())),
                 "incr_acc_exp": ("预提费用增加", cutHead(cashFlowStatement["incr_acc_exp"].to_string())),
                 "loss_disp_fiolta": ("处置固定、无形资产和其他长期资产的损失", cutHead(cashFlowStatement["loss_disp_fiolta"].to_string())),
                 "loss_scr_fa": ("固定资产报废损失", cutHead(cashFlowStatement["loss_scr_fa"].to_string())),
                 "loss_fv_chg": ("公允价值变动损失", cutHead(cashFlowStatement["loss_fv_chg"].to_string())),
                 "invest_loss": ("投资损失", cutHead(cashFlowStatement["invest_loss"].to_string())),
                 "decr_def_inc_tax_assets": ("递延所得税资产减少", cutHead(cashFlowStatement["decr_def_inc_tax_assets"].to_string())),
                 "incr_def_inc_tax_liab": ("递延所得税负债增加", cutHead(cashFlowStatement["incr_def_inc_tax_liab"].to_string())),
                 "decr_inventories": ("存货的减少", cutHead(cashFlowStatement["decr_inventories"].to_string())),
                 "decr_oper_payable": ("经营性应收项目的减少", cutHead(cashFlowStatement["decr_oper_payable"].to_string())),
                 "incr_oper_payable": ("经营性应付项目的增加", cutHead(cashFlowStatement["incr_oper_payable"].to_string())),
                 "others": ("其他", cutHead(cashFlowStatement["others"].to_string())),
                 "im_net_cashflow_oper_act": ("经营活动产生的现金流量净额(间接法)", cutHead(cashFlowStatement["im_net_cashflow_oper_act"].to_string())),
                 "conv_debt_into_cap": ("债务转为资本", cutHead(cashFlowStatement["conv_debt_into_cap"].to_string())),
                 "conv_copbonds_due_within_1y": ("一年内到期的可转换公司债券", cutHead(cashFlowStatement["conv_copbonds_due_within_1y"].to_string())),
                 "fa_fnc_leases": ("融资租入固定资产", cutHead(cashFlowStatement["fa_fnc_leases"].to_string())),
                 "end_bal_cash": ("现金的期末余额", cutHead(cashFlowStatement["end_bal_cash"].to_string())),
                 "beg_bal_cash": ("减:现金的期初余额", cutHead(cashFlowStatement["beg_bal_cash"].to_string())),
                 "end_bal_cash_equ": ("加:现金等价物的期末余额", cutHead(cashFlowStatement["end_bal_cash_equ"].to_string())),
                 "beg_bal_cash_equ": ("减:现金等价物的期初余额", cutHead(cashFlowStatement["beg_bal_cash_equ"].to_string())),
                 "im_n_incr_cash_equ": ("现金及现金等价物净增加额(间接法)", cutHead(cashFlowStatement["im_n_incr_cash_equ"].to_string()))
            }

        return ret_Dict

    def getFinancialIndicator(self, tsCode, year):
        dir = "data" + os.sep + self.getCompanyFullNameByTsCode(tsCode) + os.sep + str(year)
        fileName = dir + os.sep + "financialIndicator.csv"
        ret_Dict = None
        checkDirectory(dir)
        if (os.path.isfile(fileName)):
            financialIndicator = pd.read_csv(fileName, header=0, index_col=0)
        else:
            financialIndicator = Data.pro.fina_indicator(ts_code=tsCode, period=str(year) + "1231",
                                                         fields="ann_date,"                      # str 	公告日期
                                                                "end_date,"                      # str 	报告期
                                                                "eps,"                           # float 	基本每股收益
                                                                "dt_eps,"                        # float 	稀释每股收益
                                                                "total_revenue_ps,"              # float 	每股营业总收入
                                                                "revenue_ps,"                    # float 	每股营业收入
                                                                "capital_rese_ps,"               # float 	每股资本公积
                                                                "surplus_rese_ps,"               # float 	每股盈余公积
                                                                "undist_profit_ps,"              # float 	每股未分配利润
                                                                "extra_item,"                    # float 	非经常性损益
                                                                "profit_dedt,"                   # float 	扣除非经常性损益后的净利润
                                                                "gross_margin,"                  # float 	毛利
                                                                "current_ratio,"                 # float 	流动比率
                                                                "quick_ratio,"                   # float 	速动比率
                                                                "cash_ratio,"                    # float 	保守速动比率
                                                                "invturn_days,"                  # float 	存货周转天数
                                                                "arturn_days,"                   # float 	应收账款周转天数
                                                                "inv_turn,"                      # float 	存货周转率
                                                                "ar_turn,"                       # float 	应收账款周转率
                                                                "ca_turn,"                       # float 	流动资产周转率
                                                                "fa_turn,"                       # float 	固定资产周转率
                                                                "assets_turn,"                   # float 	总资产周转率
                                                                "op_income,"                     # float 	经营活动净收益
                                                                "valuechange_income,"            # float 	价值变动净收益
                                                                "interst_income,"                # float 	利息费用
                                                                "daa,"                           # float 	折旧与摊销
                                                                "ebit,"                          # float 	息税前利润
                                                                "ebitda,"                        # float 	息税折旧摊销前利润
                                                                "fcff,"                          # float 	企业自由现金流量
                                                                "fcfe,"                          # float 	股权自由现金流量
                                                                "current_exint,"                 # float 	无息流动负债
                                                                "noncurrent_exint,"              # float 	无息非流动负债
                                                                "interestdebt,"                  # float 	带息债务
                                                                "netdebt,"                       # float 	净债务
                                                                "tangible_asset,"                # float 	有形资产
                                                                "working_capital,"               # float 	营运资金
                                                                "networking_capital,"            # float 	营运流动资本
                                                                "invest_capital,"                # float 	全部投入资本
                                                                "retained_earnings,"             # float 	留存收益
                                                                "diluted2_eps,"                  # float 	期末摊薄每股收益
                                                                "bps,"                           # float 	每股净资产
                                                                "ocfps,"                         # float 	每股经营活动产生的现金流量净额
                                                                "retainedps,"                    # float 	每股留存收益
                                                                "cfps,"                          # float 	每股现金流量净额
                                                                "ebit_ps,"                       # float 	每股息税前利润
                                                                "fcff_ps,"                       # float 	每股企业自由现金流量
                                                                "fcfe_ps,"                       # float 	每股股东自由现金流量
                                                                "netprofit_margin,"              # float 	销售净利率
                                                                "grossprofit_margin,"            # float 	销售毛利率
                                                                "cogs_of_sales,"                 # float 	销售成本率
                                                                "expense_of_sales,"              # float 	销售期间费用率
                                                                "profit_to_gr,"                  # float 	净利润/营业总收入
                                                                "saleexp_to_gr,"                 # float 	销售费用/营业总收入
                                                                "adminexp_of_gr,"                # float 	管理费用/营业总收入
                                                                "finaexp_of_gr,"                 # float 	财务费用/营业总收入
                                                                "impai_ttm,"                     # float 	资产减值损失/营业总收入
                                                                "gc_of_gr,"                      # float 	营业总成本/营业总收入
                                                                "op_of_gr,"                      # float 	营业利润/营业总收入
                                                                "ebit_of_gr,"                    # float 	息税前利润/营业总收入
                                                                "roe,"                           # float 	净资产收益率
                                                                "roe_waa,"                       # float 	加权平均净资产收益率
                                                                "roe_dt,"                        # float 	净资产收益率(扣除非经常损益)
                                                                "roa,"                           # float 	总资产报酬率
                                                                "npta,"                          # float 	总资产净利润
                                                                "roic,"                          # float 	投入资本回报率
                                                                "roe_yearly,"                    # float 	年化净资产收益率
                                                                "roa2_yearly,"                   # float 	年化总资产报酬率
                                                                "roe_avg,"                       # float 	平均净资产收益率(增发条件)
                                                                "opincome_of_ebt,"               # float 	经营活动净收益/利润总额
                                                                "investincome_of_ebt,"           # float 	价值变动净收益/利润总额
                                                                "n_op_profit_of_ebt,"            # float 	营业外收支净额/利润总额
                                                                "tax_to_ebt,"                    # float 	所得税/利润总额
                                                                "dtprofit_to_profit,"            # float 	扣除非经常损益后的净利润/净利润
                                                                "salescash_to_or,"               # float 	销售商品提供劳务收到的现金/营业收入
                                                                "ocf_to_or,"                     # float     经营活动产生的现金流量净额/营业收入
                                                                "ocf_to_opincome,"               # float 	经营活动产生的现金流量净额/经营活动净收益
                                                                "capitalized_to_da,"             # float 	资本支出/折旧和摊销
                                                                "debt_to_assets,"                # float 	资产负债率
                                                                "assets_to_eqt,"                 # float 	权益乘数
                                                                "dp_assets_to_eqt,"              # float 	权益乘数(杜邦分析)
                                                                "ca_to_assets,"                  # float 	流动资产/总资产
                                                                "nca_to_assets,"                 # float 	非流动资产/总资产
                                                                "tbassets_to_totalassets,"       # float 	有形资产/总资产
                                                                "int_to_talcap,"                 # float 	带息债务/全部投入资本
                                                                "eqt_to_talcapital,"             # float 	归属于母公司的股东权益/全部投入资本
                                                                "currentdebt_to_debt,"           # float 	流动负债/负债合计
                                                                "longdeb_to_debt,"               # float 	非流动负债/负债合计
                                                                "ocf_to_shortdebt,"              # float 	经营活动产生的现金流量净额/流动负债
                                                                "debt_to_eqt,"                   # float 	产权比率
                                                                "eqt_to_debt,"                   # float 	归属于母公司的股东权益/负债合计
                                                                "eqt_to_interestdebt,"           # float 	归属于母公司的股东权益/带息债务
                                                                "tangibleasset_to_debt,"         # float 	有形资产/负债合计
                                                                "tangasset_to_intdebt,"          # float 	有形资产/带息债务
                                                                "tangibleasset_to_netdebt,"      # float 	有形资产/净债务
                                                                "ocf_to_debt,"                   # float 	经营活动产生的现金流量净额/负债合计
                                                                "ocf_to_interestdebt,"           # float 	经营活动产生的现金流量净额/带息债务
                                                                "ocf_to_netdebt,"                # float 	经营活动产生的现金流量净额/净债务
                                                                "ebit_to_interest,"              # float 	已获利息倍数(EBIT/利息费用)
                                                                "longdebt_to_workingcapital,"    # float 	长期债务与营运资金比率
                                                                "ebitda_to_debt,"                # float 	息税折旧摊销前利润/负债合计
                                                                "turn_days,"                     # float 	营业周期
                                                                "roa_yearly,"                    # float 	年化总资产净利率
                                                                "roa_dp,"                        # float 	总资产净利率(杜邦分析)
                                                                "fixed_assets,"                  # float 	固定资产合计
                                                                "profit_prefin_exp,"             # float 	扣除财务费用前营业利润
                                                                "non_op_profit,"                 # float 	非营业利润
                                                                "op_to_ebt,"                     # float 	营业利润／利润总额
                                                                "nop_to_ebt,"                    # float 	非营业利润／利润总额
                                                                "ocf_to_profit,"                 # float 	经营活动产生的现金流量净额／营业利润
                                                                "cash_to_liqdebt,"               # float 	货币资金／流动负债
                                                                "cash_to_liqdebt_withinterest,"  # float 	货币资金／带息流动负债
                                                                "op_to_liqdebt,"                 # float 	营业利润／流动负债
                                                                "op_to_debt,"                    # float 	营业利润／负债合计
                                                                "roic_yearly,"                   # float 	年化投入资本回报率
                                                                "profit_to_op,"                  # float 	利润总额／营业收入
                                                                "q_opincome,"                    # float 	经营活动单季度净收益
                                                                "q_investincome,"                # float 	价值变动单季度净收益
                                                                "q_dtprofit,"                    # float 	扣除非经常损益后的单季度净利润
                                                                "q_eps,"                         # float 	每股收益(单季度)
                                                                "q_netprofit_margin,"            # float 	销售净利率(单季度)
                                                                "q_gsprofit_margin,"             # float 	销售毛利率(单季度)
                                                                "q_exp_to_sales,"                # float 	销售期间费用率(单季度)
                                                                "q_profit_to_gr,"                # float 	净利润／营业总收入(单季度)
                                                                "q_saleexp_to_gr,"               # float 	销售费用／营业总收入 (单季度)
                                                                "q_adminexp_to_gr,"              # float 	管理费用／营业总收入 (单季度)
                                                                "q_finaexp_to_gr,"               # float 	财务费用／营业总收入 (单季度)
                                                                "q_impair_to_gr_ttm,"            # float 	资产减值损失／营业总收入(单季度)
                                                                "q_gc_to_gr,"                    # float 	营业总成本／营业总收入 (单季度)
                                                                "q_op_to_gr,"                    # float 	营业利润／营业总收入(单季度)
                                                                "q_roe,"                         # float     净资产收益率(单季度)
                                                                "q_dt_roe,"                      # float 	净资产单季度收益率(扣除非经常损益)
                                                                "q_npta,"                        # float 	总资产净利润(单季度)
                                                                "q_opincome_to_ebt,"             # float 	经营活动净收益／利润总额(单季度)
                                                                "q_investincome_to_ebt,"         # float 	价值变动净收益／利润总额(单季度)
                                                                "q_dtprofit_to_profit,"          # float 	扣除非经常损益后的净利润／净利润(单季度)
                                                                "q_salescash_to_or,"             # float 	销售商品提供劳务收到的现金／营业收入(单季度)
                                                                "q_ocf_to_sales,"                # float 	经营活动产生的现金流量净额／营业收入(单季度)
                                                                "q_ocf_to_or,"                   # float 	经营活动产生的现金流量净额／经营活动净收益(单季度)
                                                                "basic_eps_yoy,"                 # float 	基本每股收益同比增长率(%)
                                                                "dt_eps_yoy,"                    # float 	稀释每股收益同比增长率(%)
                                                                "cfps_yoy,"                      # float 	每股经营活动产生的现金流量净额同比增长率(%)
                                                                "op_yoy,"                        # float 	营业利润同比增长率(%)
                                                                "ebt_yoy,"                       # float 	利润总额同比增长率(%)
                                                                "netprofit_yoy,"                 # float 	归属母公司股东的净利润同比增长率(%)
                                                                "dt_netprofit_yoy,"              # float 	归属母公司股东的净利润-扣除非经常损益同比增长率(%)
                                                                "ocf_yoy,"                       # float 	经营活动产生的现金流量净额同比增长率(%)
                                                                "roe_yoy,"                       # float 	净资产收益率(摊薄)同比增长率(%)
                                                                "bps_yoy,"                       # float 	每股净资产相对年初增长率(%)
                                                                "assets_yoy,"                    # float 	资产总计相对年初增长率(%)   # 总资产增长率
                                                                "eqt_yoy,"                       # float 	归属母公司的股东权益相对年初增长率(%)
                                                                "tr_yoy,"                        # float 	营业总收入同比增长率(%)
                                                                "or_yoy,"                        # float 	营业收入同比增长率(%)
                                                                "q_gr_yoy,"                      # float 	营业总收入同比增长率(%)(单季度)
                                                                "q_gr_qoq,"                      # float 	营业总收入环比增长率(%)(单季度)
                                                                "q_sales_yoy,"                   # float 	营业收入同比增长率(%)(单季度)
                                                                "q_sales_qoq,"                   # float 	营业收入环比增长率(%)(单季度)
                                                                "q_op_yoy,"                      # float 	营业利润同比增长率(%)(单季度)
                                                                "q_op_qoq,"                      # float 	营业利润环比增长率(%)(单季度)
                                                                "q_profit_yoy,"                  # float 	净利润同比增长率(%)(单季度)
                                                                "q_profit_qoq,"                  # float 	净利润环比增长率(%)(单季度)
                                                                "q_netprofit_yoy,"               # float 	归属母公司股东的净利润同比增长率(%)(单季度)
                                                                "q_netprofit_qoq,"               # float 	归属母公司股东的净利润环比增长率(%)(单季度)
                                                                "equity_yoy,"                    # float 	净资产同比增长率
                                                                "rd_exp"                         # float 	研发费用
                                                         )

            financialIndicator.to_csv(fileName)

        for index, row in financialIndicator.iterrows():
            # Store the financial indicator in the dictionary.
            ret_Dict = {
                "ann_date": ("公告日期", cutHead(financialIndicator["ann_date"].to_string())),
                "end_date": ("报告期", cutHead(financialIndicator["end_date"].to_string())),
                "eps": (" 基本每股收益", cutHead(financialIndicator["eps"].to_string())),
                "dt_eps": ("稀释每股收益", cutHead(financialIndicator["dt_eps"].to_string())),
                "total_revenue_ps": ("每股营业总收入", cutHead(financialIndicator["total_revenue_ps"].to_string())),
                "revenue_ps": ("每股营业收入", cutHead(financialIndicator["revenue_ps"].to_string())),
                "capital_rese_ps": ("每股资本公积", cutHead(financialIndicator["capital_rese_ps"].to_string())),
                "surplus_rese_ps": ("每股盈余公积", cutHead(financialIndicator["surplus_rese_ps"].to_string())),
                "undist_profit_ps": ("每股未分配利润", cutHead(financialIndicator["undist_profit_ps"].to_string())),
                "extra_item": ("非经常性损益", cutHead(financialIndicator["extra_item"].to_string())),
                "profit_dedt": ("扣除非经常性损益后的净利润", cutHead(financialIndicator["profit_dedt"].to_string())),
                "gross_margin": ("毛利", cutHead(financialIndicator["gross_margin"].to_string())),
                "current_ratio": ("流动比率", cutHead(financialIndicator["current_ratio"].to_string())),
                "quick_ratio": ("速动比率", cutHead(financialIndicator["quick_ratio"].to_string())),
                "cash_ratio": ("保守速动比率", cutHead(financialIndicator["cash_ratio"].to_string())),
                "invturn_days": ("存货周转天数", cutHead(financialIndicator["invturn_days"].to_string())),
                "arturn_days": ("应收账款周转天数", cutHead(financialIndicator["arturn_days"].to_string())),
                "inv_turn": ("存货周转率", cutHead(financialIndicator["inv_turn"].to_string())),
                "ar_turn": ("应收账款周转率", cutHead(financialIndicator["ar_turn"].to_string())),
                "ca_turn": ("流动资产周转率", cutHead(financialIndicator["ca_turn"].to_string())),
                "fa_turn": ("固定资产周转率", cutHead(financialIndicator["fa_turn"].to_string())),
                "assets_turn": ("总资产周转率", cutHead(financialIndicator["assets_turn"].to_string())),
                "op_income": ("经营活动净收益", cutHead(financialIndicator["op_income"].to_string())),
                "valuechange_income": ("价值变动净收益", cutHead(financialIndicator["valuechange_income"].to_string())),
                "interst_income": ("利息费用", cutHead(financialIndicator["interst_income"].to_string())),
                "daa": ("折旧与摊销", cutHead(financialIndicator["daa"].to_string())),
                "ebit": ("息税前利润", cutHead(financialIndicator["ebit"].to_string())),
                "ebitda": ("息税折旧摊销前利润", cutHead(financialIndicator["ebitda"].to_string())),
                "fcff": ("企业自由现金流量", cutHead(financialIndicator["fcff"].to_string())),
                "fcfe": ("股权自由现金流量", cutHead(financialIndicator["fcfe"].to_string())),
                "current_exint": ("无息流动负债", cutHead(financialIndicator["current_exint"].to_string())),
                "noncurrent_exint": ("无息非流动负债", cutHead(financialIndicator["noncurrent_exint"].to_string())),
                "interestdebt": ("带息债务", cutHead(financialIndicator["interestdebt"].to_string())),
                "netdebt": ("净债务", cutHead(financialIndicator["netdebt"].to_string())),
                "tangible_asset": ("有形资产", cutHead(financialIndicator["tangible_asset"].to_string())),
                "working_capital": ("营运资金", cutHead(financialIndicator["working_capital"].to_string())),
                "networking_capital": ("营运流动资本", cutHead(financialIndicator["networking_capital"].to_string())),
                "invest_capital": ("全部投入资本", cutHead(financialIndicator["invest_capital"].to_string())),
                "retained_earnings": ("留存收益", cutHead(financialIndicator["retained_earnings"].to_string())),
                "diluted2_eps": ("期末摊薄每股收益", cutHead(financialIndicator["diluted2_eps"].to_string())),
                "bps": ("每股净资产", cutHead(financialIndicator["bps"].to_string())),
                "ocfps": ("每股经营活动产生的现金流量净额", cutHead(financialIndicator["ocfps"].to_string())),
                "retainedps": ("每股留存收益", cutHead(financialIndicator["retainedps"].to_string())),
                "cfps": ("每股现金流量净额", cutHead(financialIndicator["cfps"].to_string())),
                "ebit_ps": ("每股息税前利润", cutHead(financialIndicator["ebit_ps"].to_string())),
                "fcff_ps": ("每股企业自由现金流量", cutHead(financialIndicator["fcff_ps"].to_string())),
                "fcfe_ps": ("每股股东自由现金流量", cutHead(financialIndicator["fcfe_ps"].to_string())),
                "netprofit_margin": ("销售净利率", cutHead(financialIndicator["netprofit_margin"].to_string())),
                "grossprofit_margin": ("销售毛利率", cutHead(financialIndicator["grossprofit_margin"].to_string())),
                "cogs_of_sales": ("销售成本率", cutHead(financialIndicator["cogs_of_sales"].to_string())),
                "expense_of_sales": ("销售期间费用率", cutHead(financialIndicator["expense_of_sales"].to_string())),
                "profit_to_gr": ("净利润/营业总收入", cutHead(financialIndicator["profit_to_gr"].to_string())),
                "saleexp_to_gr": ("销售费用/营业总收入", cutHead(financialIndicator["saleexp_to_gr"].to_string())),
                "adminexp_of_gr": ("管理费用/营业总收入", cutHead(financialIndicator["adminexp_of_gr"].to_string())),
                "finaexp_of_gr": ("财务费用/营业总收入", cutHead(financialIndicator["finaexp_of_gr"].to_string())),
                "impai_ttm": ("资产减值损失/营业总收入", cutHead(financialIndicator["impai_ttm"].to_string())),
                "gc_of_gr": ("营业总成本/营业总收入", cutHead(financialIndicator["gc_of_gr"].to_string())),
                "op_of_gr": ("营业利润/营业总收入", cutHead(financialIndicator["op_of_gr"].to_string())),
                "ebit_of_gr": ("息税前利润/营业总收入", cutHead(financialIndicator["ebit_of_gr"].to_string())),
                "roe": ("净资产收益率", cutHead(financialIndicator["roe"].to_string())),
                "roe_waa": ("加权平均净资产收益率", cutHead(financialIndicator["roe_waa"].to_string())),
                "roe_dt": ("净资产收益率(扣除非经常损益)", cutHead(financialIndicator["roe_dt"].to_string())),
                "roa": ("总资产报酬率", cutHead(financialIndicator["roa"].to_string())),
                "npta": ("总资产净利润", cutHead(financialIndicator["npta"].to_string())),
                "roic": ("投入资本回报率", cutHead(financialIndicator["roic"].to_string())),
                "roe_yearly": ("年化净资产收益率", cutHead(financialIndicator["roe_yearly"].to_string())),
                "roa2_yearly": ("年化总资产报酬率", cutHead(financialIndicator["roa2_yearly"].to_string())),
                "roe_avg": ("平均净资产收益率(增发条件)", cutHead(financialIndicator["roe_avg"].to_string())),
                "opincome_of_ebt": ("经营活动净收益/利润总额", cutHead(financialIndicator["opincome_of_ebt"].to_string())),
                "investincome_of_ebt": ("价值变动净收益/利润总额", cutHead(financialIndicator["investincome_of_ebt"].to_string())),
                "n_op_profit_of_ebt": ("营业外收支净额/利润总额", cutHead(financialIndicator["n_op_profit_of_ebt"].to_string())),
                "tax_to_ebt": ("所得税/利润总额", cutHead(financialIndicator["tax_to_ebt"].to_string())),
                "dtprofit_to_profit": ("扣除非经常损益后的净利润/净利润", cutHead(financialIndicator["dtprofit_to_profit"].to_string())),
                "salescash_to_or": ("销售商品提供劳务收到的现金/营业收入", cutHead(financialIndicator["salescash_to_or"].to_string())),
                "ocf_to_or": ("经营活动产生的现金流量净额/营业收入", cutHead(financialIndicator["ocf_to_or"].to_string())),
                "ocf_to_opincome": ("经营活动产生的现金流量净额/经营活动净收益", cutHead(financialIndicator["ocf_to_opincome"].to_string())),
                "capitalized_to_da": ("资本支出/折旧和摊销", cutHead(financialIndicator["capitalized_to_da"].to_string())),
                "debt_to_assets": ("资产负债率", cutHead(financialIndicator["debt_to_assets"].to_string())),
                "assets_to_eqt": ("权益乘数", cutHead(financialIndicator["assets_to_eqt"].to_string())),
                "dp_assets_to_eqt": ("权益乘数(杜邦分析)", cutHead(financialIndicator["dp_assets_to_eqt"].to_string())),
                "ca_to_assets": ("流动资产/总资产", cutHead(financialIndicator["ca_to_assets"].to_string())),
                "nca_to_assets": ("非流动资产/总资产", cutHead(financialIndicator["nca_to_assets"].to_string())),
                "tbassets_to_totalassets": ("有形资产/总资产", cutHead(financialIndicator["tbassets_to_totalassets"].to_string())),
                "int_to_talcap": ("带息债务/全部投入资本", cutHead(financialIndicator["int_to_talcap"].to_string())),
                "eqt_to_talcapital": ("归属于母公司的股东权益/全部投入资本", cutHead(financialIndicator["eqt_to_talcapital"].to_string())),
                "currentdebt_to_debt": ("流动负债/负债合计", cutHead(financialIndicator["currentdebt_to_debt"].to_string())),
                "longdeb_to_debt": ("非流动负债/负债合计", cutHead(financialIndicator["longdeb_to_debt"].to_string())),
                "ocf_to_shortdebt": ("经营活动产生的现金流量净额/流动负债", cutHead(financialIndicator["ocf_to_shortdebt"].to_string())),
                "debt_to_eqt": ("产权比率", cutHead(financialIndicator["debt_to_eqt"].to_string())),
                "eqt_to_debt": ("归属于母公司的股东权益/负债合计", cutHead(financialIndicator["eqt_to_debt"].to_string())),
                "eqt_to_interestdebt": ("归属于母公司的股东权益/带息债务", cutHead(financialIndicator["eqt_to_interestdebt"].to_string())),
                "tangibleasset_to_debt": ("有形资产/负债合计", cutHead(financialIndicator["tangibleasset_to_debt"].to_string())),
                "tangasset_to_intdebt": ("有形资产/带息债务", cutHead(financialIndicator["tangasset_to_intdebt"].to_string())),
                "tangibleasset_to_netdebt": ("有形资产/净债务", cutHead(financialIndicator["tangibleasset_to_netdebt"].to_string())),
                "ocf_to_debt": ("经营活动产生的现金流量净额/负债合计", cutHead(financialIndicator["ocf_to_debt"].to_string())),
                "ocf_to_interestdebt": ("经营活动产生的现金流量净额/带息债务", cutHead(financialIndicator["ocf_to_interestdebt"].to_string())),
                "ocf_to_netdebt": ("经营活动产生的现金流量净额/净债务", cutHead(financialIndicator["ocf_to_netdebt"].to_string())),
                "ebit_to_interest": ("已获利息倍数(EBIT/利息费用)", cutHead(financialIndicator["ebit_to_interest"].to_string())),
                "longdebt_to_workingcapital": ("长期债务与营运资金比率", cutHead(financialIndicator["longdebt_to_workingcapital"].to_string())),
                "ebitda_to_debt": ("息税折旧摊销前利润/负债合计", cutHead(financialIndicator["ebitda_to_debt"].to_string())),
                "turn_days": ("营业周期", cutHead(financialIndicator["turn_days"].to_string())),
                "roa_yearly": ("年化总资产净利率", cutHead(financialIndicator["roa_yearly"].to_string())),
                "roa_dp": ("总资产净利率(杜邦分析)", cutHead(financialIndicator["roa_dp"].to_string())),
                "fixed_assets": ("固定资产合计", cutHead(financialIndicator["fixed_assets"].to_string())),
                "profit_prefin_exp": ("扣除财务费用前营业利润", cutHead(financialIndicator["profit_prefin_exp"].to_string())),
                "non_op_profit": ("非营业利润", cutHead(financialIndicator["non_op_profit"].to_string())),
                "op_to_ebt": ("营业利润／利润总额", cutHead(financialIndicator["op_to_ebt"].to_string())),
                "nop_to_ebt": ("非营业利润／利润总额", cutHead(financialIndicator["nop_to_ebt"].to_string())),
                "ocf_to_profit": ("经营活动产生的现金流量净额／营业利润", cutHead(financialIndicator["ocf_to_profit"].to_string())),
                "cash_to_liqdebt": ("货币资金／流动负债", cutHead(financialIndicator["cash_to_liqdebt"].to_string())),
                "cash_to_liqdebt_withinterest": ("货币资金／带息流动负债", cutHead(financialIndicator["cash_to_liqdebt_withinterest"].to_string())),
                "op_to_liqdebt": ("营业利润／流动负债", cutHead(financialIndicator["op_to_liqdebt"].to_string())),
                "op_to_debt": ("营业利润／负债合计", cutHead(financialIndicator["op_to_debt"].to_string())),
                "roic_yearly": ("年化投入资本回报率", cutHead(financialIndicator["roic_yearly"].to_string())),
                "profit_to_op": ("利润总额／营业收入", cutHead(financialIndicator["profit_to_op"].to_string())),
                "q_opincome": ("经营活动单季度净收益", cutHead(financialIndicator["q_opincome"].to_string())),
                "q_investincome": ("价值变动单季度净收益", cutHead(financialIndicator["q_investincome"].to_string())),
                "q_dtprofit": ("扣除非经常损益后的单季度净利润", cutHead(financialIndicator["q_dtprofit"].to_string())),
                "q_eps": ("每股收益(单季度)", cutHead(financialIndicator["q_eps"].to_string())),
                "q_netprofit_margin": ("销售净利率(单季度)", cutHead(financialIndicator["q_netprofit_margin"].to_string())),
                "q_gsprofit_margin": ("销售毛利率(单季度)", cutHead(financialIndicator["q_gsprofit_margin"].to_string())),
                "q_exp_to_sales": ("销售期间费用率(单季度)", cutHead(financialIndicator["q_exp_to_sales"].to_string())),
                "q_profit_to_gr": ("净利润／营业总收入(单季度)", cutHead(financialIndicator["q_profit_to_gr"].to_string())),
                "q_saleexp_to_gr": ("销售费用／营业总收入 (单季度)", cutHead(financialIndicator["q_saleexp_to_gr"].to_string())),
                "q_adminexp_to_gr": ("管理费用／营业总收入 (单季度)", cutHead(financialIndicator["q_adminexp_to_gr"].to_string())),
                "q_finaexp_to_gr": ("财务费用／营业总收入 (单季度)", cutHead(financialIndicator["q_finaexp_to_gr"].to_string())),
                "q_impair_to_gr_ttm": ("资产减值损失／营业总收入(单季度)", cutHead(financialIndicator["q_impair_to_gr_ttm"].to_string())),
                "q_gc_to_gr": ("营业总成本／营业总收入 (单季度)", cutHead(financialIndicator["q_gc_to_gr"].to_string())),
                "q_op_to_gr": ("营业利润／营业总收入(单季度)", cutHead(financialIndicator["q_op_to_gr"].to_string())),
                "q_roe": ("净资产收益率(单季度)", cutHead(financialIndicator["q_roe"].to_string())),
                "q_dt_roe": ("净资产单季度收益率(扣除非经常损益)", cutHead(financialIndicator["q_dt_roe"].to_string())),
                "q_npta": ("总资产净利润(单季度)", cutHead(financialIndicator["q_npta"].to_string())),
                "q_opincome_to_ebt": ("经营活动净收益／利润总额(单季度)", cutHead(financialIndicator["q_opincome_to_ebt"].to_string())),
                "q_investincome_to_ebt": ("价值变动净收益／利润总额(单季度)", cutHead(financialIndicator["q_investincome_to_ebt"].to_string())),
                "q_dtprofit_to_profit": ("扣除非经常损益后的净利润／净利润(单季度)", cutHead(financialIndicator["q_dtprofit_to_profit"].to_string())),
                "q_salescash_to_or": ("销售商品提供劳务收到的现金／营业收入(单季度)", cutHead(financialIndicator["q_salescash_to_or"].to_string())),
                "q_ocf_to_sales": ("经营活动产生的现金流量净额／营业收入(单季度)", cutHead(financialIndicator["q_ocf_to_sales"].to_string())),
                "q_ocf_to_or": ("经营活动产生的现金流量净额／经营活动净收益(单季度)", cutHead(financialIndicator["q_ocf_to_or"].to_string())),
                "basic_eps_yoy": ("基本每股收益同比增长率(%)", cutHead(financialIndicator["basic_eps_yoy"].to_string())),
                "dt_eps_yoy": ("稀释每股收益同比增长率(%)", cutHead(financialIndicator["dt_eps_yoy"].to_string())),
                "cfps_yoy": ("每股经营活动产生的现金流量净额同比增长率(%)", cutHead(financialIndicator["cfps_yoy"].to_string())),
                "op_yoy": ("营业利润同比增长率(%)", cutHead(financialIndicator["op_yoy"].to_string())),
                "ebt_yoy": ("利润总额同比增长率(%)", cutHead(financialIndicator["ebt_yoy"].to_string())),
                "netprofit_yoy": ("归属母公司股东的净利润同比增长率(%)", cutHead(financialIndicator["netprofit_yoy"].to_string())),
                "dt_netprofit_yoy": ("归属母公司股东的净利润-扣除非经常损益同比增长率(%)", cutHead(financialIndicator["dt_netprofit_yoy"].to_string())),
                "ocf_yoy": ("经营活动产生的现金流量净额同比增长率(%)", cutHead(financialIndicator["ocf_yoy"].to_string())),
                "roe_yoy": ("净资产收益率(摊薄)同比增长率(%)", cutHead(financialIndicator["roe_yoy"].to_string())),
                "bps_yoy": ("每股净资产相对年初增长率(%)", cutHead(financialIndicator["bps_yoy"].to_string())),
                "assets_yoy": ("资产总计相对年初增长率(%)", cutHead(financialIndicator["assets_yoy"].to_string())),
                "eqt_yoy": ("归属母公司的股东权益相对年初增长率(%)", cutHead(financialIndicator["eqt_yoy"].to_string())),
                "tr_yoy": ("营业总收入同比增长率(%)", cutHead(financialIndicator["tr_yoy"].to_string())),
                "or_yoy": ("营业收入同比增长率(%)", cutHead(financialIndicator["or_yoy"].to_string())),
                "q_gr_yoy": ("营业总收入同比增长率(%)(单季度)", cutHead(financialIndicator["q_gr_yoy"].to_string())),
                "q_gr_qoq": ("营业总收入环比增长率(%)(单季度)", cutHead(financialIndicator["q_gr_qoq"].to_string())),
                "q_sales_yoy": ("营业收入同比增长率(%)(单季度)", cutHead(financialIndicator["q_sales_yoy"].to_string())),
                "q_sales_qoq": ("营业收入环比增长率(%)(单季度)", cutHead(financialIndicator["q_sales_qoq"].to_string())),
                "q_op_yoy": ("营业利润同比增长率(%)(单季度)", cutHead(financialIndicator["q_op_yoy"].to_string())),
                "q_op_qoq": ("营业利润环比增长率(%)(单季度)", cutHead(financialIndicator["q_op_qoq"].to_string())),
                "q_profit_yoy": ("净利润同比增长率(%)(单季度)", cutHead(financialIndicator["q_profit_yoy"].to_string())),
                "q_profit_qoq": ("净利润环比增长率(%)(单季度)", cutHead(financialIndicator["q_profit_qoq"].to_string())),
                "q_netprofit_yoy": ("归属母公司股东的净利润同比增长率(%)(单季度)", cutHead(financialIndicator["q_netprofit_yoy"].to_string())),
                "q_netprofit_qoq": ("归属母公司股东的净利润环比增长率(%)(单季度)", cutHead(financialIndicator["q_netprofit_qoq"].to_string())),
                "equity_yoy": ("净资产同比增长率", cutHead(financialIndicator["equity_yoy"].to_string())),
                "rd_exp": ("研发费用", cutHead(financialIndicator["rd_exp"].to_string()))
            }

        return ret_Dict

    def getPreliminaryEarningsEstimate(self, tsCode, year):
        dir = "data" + os.sep + self.getCompanyFullNameByTsCode(tsCode) + os.sep + str(year)
        fileName = dir + os.sep + "preliminaryEarningsEstimate.csv"
        ret_Dict = None
        checkDirectory(dir)
        if(os.path.isfile(fileName)):
            preliminaryEarningsEstimate = pd.read_csv(fileName, header=0, index_col=0)
        else:
            preliminaryEarningsEstimate = Data.pro.express(ts_code = tsCode, period = str(year)+"1231",
                                                             fields="ann_date,"                     # str 	公告日期
                                                                    "end_date,"                     # str 	报告期
                                                                    "revenue,"                      # float 	营业收入(元)
                                                                    "operate_profit,"               # float 	营业利润(元)
                                                                    "total_profit,"                 # float 	利润总额(元)
                                                                    "n_income,"                     # float 	净利润(元)
                                                                    "total_assets,"                 # float 	总资产(元)
                                                                    "total_hldr_eqy_exc_min_int,"   # float 	股东权益合计(不含少数股东权益)(元)
                                                                    "diluted_eps,"                  # float 	每股收益(摊薄)(元)
                                                                    "diluted_roe,"                  # float 	净资产收益率(摊薄)(%)
                                                                    "yoy_net_profit,"               # float 	去年同期修正后净利润
                                                                    "bps,"                          # float 	每股净资产
                                                                    "yoy_sales,"                    # float 	同比增长率:营业收入
                                                                    "yoy_op,"                       # float 	同比增长率:营业利润
                                                                    "yoy_tp,"                       # float 	同比增长率:利润总额
                                                                    "yoy_dedu_np,"                  # float 	同比增长率:归属母公司股东的净利润
                                                                    "yoy_eps,"                      # float 	同比增长率:基本每股收益
                                                                    "yoy_roe,"                      # float 	同比增减:加权平均净资产收益率
                                                                    "growth_assets,"                # float 	比年初增长率:总资产
                                                                    "yoy_equity,"                   # float 	比年初增长率:归属母公司的股东权益
                                                                    "growth_bps,"                   # float 	比年初增长率:归属于母公司股东的每股净资产
                                                                    "or_last_year,"                 # float 	去年同期营业收入
                                                                    "op_last_year,"                 # float 	去年同期营业利润
                                                                    "tp_last_year,"                 # float 	去年同期利润总额
                                                                    "np_last_year,"                 # float 	去年同期净利润
                                                                    "eps_last_year,"                # float 	去年同期每股收益
                                                                    "open_net_assets,"              # float 	期初净资产
                                                                    "open_bps,"                     # float 	期初每股净资产
                                                                    "perf_summary,"                 # str 	业绩简要说明
                                                                    "is_audit,"                     # int 	是否审计： 1是 0否
                                                                    "remark"                        # str 	备注
                                                           )
            preliminaryEarningsEstimate.to_csv(fileName)

        for index, row in preliminaryEarningsEstimate.iterrows():
            # Store the Preliminary Earnings Estimate in the dictionary.
            ret_Dict = {
                "ann_date": ("公告日期", cutHead(preliminaryEarningsEstimate["ann_date"].to_string())),
                "end_date": ("报告期", cutHead(preliminaryEarningsEstimate["end_date"].to_string())),
                "revenue": ("营业收入", cutHead(preliminaryEarningsEstimate["revenue"].to_string())),
                "operate_profit": ("营业利润", cutHead(preliminaryEarningsEstimate["operate_profit"].to_string())),
                "total_profit": ("利润总额", cutHead(preliminaryEarningsEstimate["total_profit"].to_string())),
                "n_income": ("净利润", cutHead(preliminaryEarningsEstimate["n_income"].to_string())),
                "total_assets": ("总资产", cutHead(preliminaryEarningsEstimate["total_assets"].to_string())),
                "total_hldr_eqy_exc_min_int": (
                "股东权益合计(不含少数股东权益)", cutHead(preliminaryEarningsEstimate["total_hldr_eqy_exc_min_int"].to_string())),
                "diluted_eps": ("每股收益(摊薄)", cutHead(preliminaryEarningsEstimate["diluted_eps"].to_string())),
                "diluted_roe": ("净资产收益率(摊薄)(%)", cutHead(preliminaryEarningsEstimate["diluted_roe"].to_string())),
                "yoy_net_profit": ("去年同期修正后净利润", cutHead(preliminaryEarningsEstimate["yoy_net_profit"].to_string())),
                "bps": ("每股净资产", cutHead(preliminaryEarningsEstimate["bps"].to_string())),
                "yoy_sales": ("同比增长率:营业收入", cutHead(preliminaryEarningsEstimate["yoy_sales"].to_string())),
                "yoy_op": ("同比增长率:营业利润", cutHead(preliminaryEarningsEstimate["yoy_op"].to_string())),
                "yoy_tp": ("同比增长率:利润总额", cutHead(preliminaryEarningsEstimate["yoy_tp"].to_string())),
                "yoy_dedu_np": ("同比增长率:归属母公司股东的净利润", cutHead(preliminaryEarningsEstimate["yoy_dedu_np"].to_string())),
                "yoy_eps": ("同比增长率:基本每股收益", cutHead(preliminaryEarningsEstimate["yoy_eps"].to_string())),
                "yoy_roe": ("同比增减:加权平均净资产收益率", cutHead(preliminaryEarningsEstimate["yoy_roe"].to_string())),
                "growth_assets": ("比年初增长率:总资产", cutHead(preliminaryEarningsEstimate["growth_assets"].to_string())),
                "yoy_equity": ("比年初增长率:归属母公司的股东权益", cutHead(preliminaryEarningsEstimate["yoy_equity"].to_string())),
                "growth_bps": ("比年初增长率:归属于母公司股东的每股净资产", cutHead(preliminaryEarningsEstimate["growth_bps"].to_string())),
                "or_last_year": ("去年同期营业收入", cutHead(preliminaryEarningsEstimate["or_last_year"].to_string())),
                "op_last_year": ("去年同期营业利润", cutHead(preliminaryEarningsEstimate["op_last_year"].to_string())),
                "tp_last_year": ("去年同期利润总额", cutHead(preliminaryEarningsEstimate["tp_last_year"].to_string())),
                "np_last_year": ("去年同期净利润", cutHead(preliminaryEarningsEstimate["np_last_year"].to_string())),
                "eps_last_year": ("去年同期每股收益", cutHead(preliminaryEarningsEstimate["eps_last_year"].to_string())),
                "open_net_assets": ("期初净资产", cutHead(preliminaryEarningsEstimate["open_net_assets"].to_string())),
                "open_bps": ("期初每股净资产", cutHead(preliminaryEarningsEstimate["open_bps"].to_string())),
                "perf_summary": ("业绩简要说明", cutHead(preliminaryEarningsEstimate["perf_summary"].to_string())),
                "is_audit": ("是否审计： 1是 0否", cutHead(preliminaryEarningsEstimate["is_audit"].to_string())),
                "remark": ("备注", cutHead(preliminaryEarningsEstimate["remark"].to_string()))
            }

        return ret_Dict

    def getMainBusinessComposition(self, tsCode, year, _type = "P"):
        """
        Obtain the main business composition.
        :param _type: Type: P by product D by district (please enter capital "P" or "D")
        :return: DataFrame
        """
        dir = "data" + os.sep + self.getCompanyFullNameByTsCode(tsCode) + os.sep + str(year)
        fileName = dir + os.sep + "mainBusinessComposition.csv"
        checkDirectory(dir)
        if(os.path.isfile(fileName)):
            mainBusinessComposition = pd.read_csv(fileName, header=0, index_col=0)
        else:
            mainBusinessComposition = Data.pro.fina_mainbz(ts_code=tsCode,
                                                           period=str(year)+"1231",
                                                           type=_type,
                                                           fields="bz_item,"    # str 	主营业务来源
                                                                  "bz_sales,"   # float 	主营业务收入(元)
                                                                  "bz_profit,"  # float 	主营业务利润(元)
                                                                  "bz_cost,"    # float 	主营业务成本(元)
                                                                  "curr_type"   # str 	货币代码"
                                                           )
            mainBusinessComposition.to_csv(fileName)

        return mainBusinessComposition
