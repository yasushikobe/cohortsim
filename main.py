# %%
# システムパラメータの設定
import copy
import numpy
import pandas
import scipy
import seaborn
from IPython import get_ipython

PATIENTCOUNT = 10000
OBSERVATIONYEARS = 10
INCIDENCE = 0.010
ELECTPATIENTCOUNT = 100
COHORTREPEAT = 100
# 事前処理
seaborn.set()
# Native Pythonでも実行可能なように対応（ただし、plotは行わない）
try:
    get_ipython().run_line_magic('matplotlib', 'inline')
    get_ipython().run_line_magic('precision', 3)
except:
    print('Warning: Running in Native python environment.')


class Database:
    def __init__(self, incidence: float, patientCount: int, observationYears: int, initData=None):
        """患者データベースコンストラクタ
        Args:
            incidence (float): 発生率
            patientCount (int): 患者数
            observationYears (int): 観察年数
            initData (nparray): 初期化データ（デフォルト None)
        """
        if initData is None:
            randomRate = numpy.random.random((patientCount, observationYears))
            data = numpy.ones((patientCount, observationYears)) * incidence - randomRate
            data = numpy.where(data > 0, 1, 0)
            data = numpy.cumsum(data, axis=1)
            data = numpy.where(data >= 1, 1, 0)
            data = numpy.cumsum(data, axis=1)
            self.__data = data
        else:
            self.__data = initData
        self.__incidence: float = incidence
        self.__patientCount: int = patientCount
        self.__observationYears: int = observationYears

    @property
    def data(self):
        """データベース配列を返却する
        Returns:
            ndarray: データベース配列
        """
        return self.__data

    @property
    def incidence(self):
        """発生率を返却する
        Returns:
            float: 発生率
        """
        return self.__incidence

    @property
    def patientCount(self):
        """患者数を返却する
        Returns:
            int: 患者数
        """
        return self.__patientCount

    @property
    def observationYears(self):
        """観察年数を返却する
        Returns:
            int: 観察年数
        """
        return self.__observationYears

    @property
    def histgramData(self):
        """積層形式に変換したdataを返却する
        Returns:
            ndarray: データベース配列（積層型変換）
        """
        data = numpy.where(self.__data > 0, 1, 0)
        return numpy.sort(data, axis=0)

    def electCohort(self, electPatientCount: int) -> 'Database':
        """コホート選出データをデータベース配列より作成する（ファクトリメソッド）
        Args:
            electPatientCount (int): 選出患者数
        Returns:
            Database: コホート選出データ
        """
        rowlist = list(range(0, self.__patientCount))
        ret = numpy.random.choice(rowlist, electPatientCount)
        ret = self.__data[ret, :]
        return Database(self.__incidence, electPatientCount, self.__observationYears, copy.deepcopy(ret))

    def getOnsetDataFrame(self) -> 'pandas.DataFrame':
        """発症率描画データフレームを作成する
        Returns:
            pandas.DataFrame: lineplot向けデータフレーム
        """
        onsetYearCount = numpy.where(self.__data > 0, 1, 0).sum(axis=0)
        onsetYearRate = onsetYearCount / self.__patientCount
        dataFrame = pandas.DataFrame({
            'year': list(range(0, self.__observationYears)),
            'rate': onsetYearRate.tolist()
        })
        dataFrame['averageRate'] = dataFrame['rate'] / (dataFrame['year'] + 1)
        return dataFrame

    def getRateTheory(self) -> 'pandas.DataFrame':
        """理論発生率描画データフレームを作成する
        Returns:
            pandas.DataFrame: lineplot向けデータフレーム
        """
        rateTheory = [0] * self.__observationYears
        rateTheory[0] = self.__incidence
        for i in range(1, self.__observationYears):
            rateTheory[i] = rateTheory[i - 1] + (1 - rateTheory[i - 1]) * self.__incidence
        dataFrameTheory = pandas.DataFrame({
            'year': list(range(0, self.__observationYears)),
            'rate': rateTheory
        })
        dataFrameTheory['averageRate'] = dataFrameTheory['rate'] / (dataFrameTheory['year'] + 1)
        return dataFrameTheory


# %%
# 全体データベースの作成
database = Database(INCIDENCE, PATIENTCOUNT, OBSERVATIONYEARS)
seaborn.heatmap(database.histgramData)
print("全体症例数={0} 発症率={1} 観察年数={2}".format(
    database.patientCount, database.incidence, database.observationYears
))

# %%
# データベース状況
seaborn.heatmap(database.data)

# %%
# コホート研究の開始（全体データベースからの患者選択のテスト）
cohortTest = database.electCohort(ELECTPATIENTCOUNT)
dataFrameTest = cohortTest.getOnsetDataFrame()
seaborn.lineplot(x="year", y="averageRate", data=dataFrameTest)


# %%
# 発生率から毎年の理論発生率を計算
seaborn.lineplot(x="year", y="averageRate", data=database.getRateTheory())

# %%
# コホート研究の繰り返し実験
averageRates = numpy.zeros((COHORTREPEAT, OBSERVATIONYEARS))
for i in range(0, COHORTREPEAT):
    cohort = database.electCohort(ELECTPATIENTCOUNT)
    dataFrame = cohort.getOnsetDataFrame()
    seaborn.lineplot(x="year", y="averageRate", data=dataFrame)
    averageRates[i, :] = numpy.array(dataFrame['averageRate'])
print("全体症例数={0} 発症率={1} 観察年数={2}".format(PATIENTCOUNT, INCIDENCE, OBSERVATIONYEARS))
print("コホート症例数={0} コホート回数={1}".format(ELECTPATIENTCOUNT, COHORTREPEAT))

# %%
# 真値（理論値）に対するコホート値のばらつきを箱髭図で表現
# boxplotのためにdfをtidy化
# https://qiita.com/ishida330/items/922caa7acb73c1540e28
averageRatesDataFrame = pandas.DataFrame(averageRates)
averageRatesDataFrame['cohortID'] = list(range(0, COHORTREPEAT))
averageRatesDataFrameTidy = pandas.melt(averageRatesDataFrame, ['cohortID'], var_name='year', value_name='rate').sort_values('cohortID')
seaborn.boxplot(x="year", y="rate", data=averageRatesDataFrameTidy)
seaborn.lineplot(x="year", y="averageRate", data=database.getRateTheory())
