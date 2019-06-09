# %%
# システムパラメータの設定
import numpy
import pandas
import scipy
import seaborn
from IPython import get_ipython
from Database import Database

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
