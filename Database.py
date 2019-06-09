import copy
import numpy
import pandas

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
