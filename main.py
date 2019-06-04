# %%
# 数値計算ライブラリ
import numpy as np
import scipy as sp
import pandas as pd
from scipy import stats
from IPython import get_ipython

# グラフ描画
from matplotlib import pyplot as plt
import seaborn as sns
sns.set()

# Native Pythonでも実行可能なように対応（ただし、plotは行わない）
try:
    get_ipython().run_line_magic('matplotlib', 'inline')
    get_ipython().run_line_magic('precision', 3)
except:
    print('Warning: Running in Native python environment.')

# %%
# 関数　患者データベース作成


def dataYear(incidence, num, year):  # 発生率、患者数、観察年数
    dataYearRand = np.random.random((num, year))  # 毎年乱数生成
    dataYearIncidence = np.ones((num, year))*incidence - dataYearRand  # 発生率から乱数マイナス
    dataYearOnset = np.where(dataYearIncidence > 0, 1, 0)

    # コピーを作成
    dataYearOnset_cumulative = np.copy(dataYearOnset)

    # 年度ごとに発生を積み上げる
    for slide in range(0, year-1):
        dataYearOnset_cumulative[:, slide+1] += dataYearOnset_cumulative[:, slide]

    # 1以上をすべて1に
    dataYearOnset_cumulative2 = np.where(dataYearOnset_cumulative >= 1, 1, 0)

    # コピーを作成
    dataYearOnset_cumulative3 = np.copy(dataYearOnset_cumulative2)

    # 発生年数で埋めていく
    for slide in range(0, year-1):
        dataYearOnset_cumulative3[:, slide+1] += dataYearOnset_cumulative3[:, slide]

    return dataYearOnset_cumulative3


# テスト
#dataY = dataYear(0.1,50,10) # 発生率、患者数、観察年数
#sns.heatmap(dataY)

# 関数 非復元抽出
def patientRandomChoice(numPatient, numChoice):
    l = list(range(0, numPatient))  # 0からnumの数字をリストで生成
    randomPtientNumber = np.random.choice(l, numChoice)  # 選択
    return randomPtientNumber

# %%
## 全体データベースの作成
# 設定


totalPatientNum = 10000  # 症例数
maxObservation = 10  # 最大観察機関
incidence = 0.010  # 発生率

# 全体データベースの作成

dataY = dataYear(incidence, totalPatientNum, maxObservation)
#sns.heatmap(dataY)
dataY_ZeroOne = np.where(dataY > 0, 1, 0)
#sns.heatmap(dataY_ZeroOne)
dataY_ZeroOne_Sort = np.sort(dataY_ZeroOne, axis=0)
sns.heatmap(dataY_ZeroOne_Sort)

print("全体症例数=", totalPatientNum, end="")
print("  発症率=", incidence, end="")
print("  観察年数=", maxObservation)

# %%
sns.heatmap(dataY)

# %%
## コホート研究の開始
# 全体データベースからの患者選択

numSelectedPatients = 100


def dataCohort(numSelectedPatients, dataY):
    # 乱数を用いて患者を取得
    patientList = patientRandomChoice(totalPatientNum, numSelectedPatients)
    dataYCohort = dataY[patientList, :]

    # コピー
    dataSelected = np.copy(dataYCohort)

    # データべースの患者数、年度を取得
    colNum = dataSelected.shape  # 要素数の取得 [患者数,年度]
    dataSetected_ZeroOne = np.where(dataSelected > 0, 1, 0)
    #sns.heatmap(dataSetected_ZeroOne) # ゼロワン後

    dataSetected_ZeroOne_Sort = np.sort(dataSetected_ZeroOne, axis=0)
    #sns.heatmap(dataSetected_ZeroOne_Sort) # ソート後の確認

    # 発生頻度の集計
    onsetYear = dataSetected_ZeroOne.sum(axis=0)  # 患者方向に集計

    # 症例数で割って頻度に変換
    onsetYearRate = onsetYear/colNum[0]  # 0 = 症例数

    # データフレーム形式に変換
    dataFrame = pd.DataFrame({
        'year': list(range(0, colNum[1])),
        'rate': onsetYearRate.tolist()  # ndarray 形式をlistに
    })
    #dataFrame
    # 平均発生頻度の追加
    dataFrame['averageRate'] = dataFrame['rate']/(dataFrame['year']+1)

    # プロット
    #g = sns.lineplot(x="year",y="rate",data=dataFrame) # 積み上げの推移
    g = sns.lineplot(x="year", y="averageRate", data=dataFrame)  # 発生率の推移

    # 戻り値
    return dataFrame, g


## 関数のテスト
dataFrame, g = dataCohort(numSelectedPatients, dataY)
#dataFrame

# %%
# 発生率から毎年の理論発生率を計算


def plotRateTheroy(maxObservation, incidence):
    rateTheory = [0] * maxObservation
    rateTheory[0] = incidence

    for i in range(1, maxObservation):
        rateTheory[i] = rateTheory[i-1] + (1-rateTheory[i-1])*incidence

    year = list(range(0, maxObservation))
    dataFrameTheory = pd.DataFrame({
        'year': year,
        'rate': rateTheory  # ndarray 形式をlistに
    })

    dataFrameTheory['averageRate'] = dataFrameTheory['rate']/(dataFrameTheory['year']+1)

    #sns.lineplot(x="year",y="rate",data=dataFrameTheory) # 積み上げの推移
    g = sns.lineplot(x="year", y="averageRate", data=dataFrameTheory)  # 発生率の推移
    #g.set(ylim=[0,incidence*1.1])

    return dataFrameTheory, g


dataFrameTheory = plotRateTheroy(maxObservation, incidence)

# %%
# コホート研究の繰り返し実験

repeat = 100
dataCohort_repeat = np.zeros((repeat, maxObservation))  # コホートごとのrateを記録

for i in range(0, repeat):
    dataFrame, g1 = dataCohort(numSelectedPatients, dataY)  # コホートごとの観測値を描出
    dataCohort_repeat[i, :] = np.array(dataFrame['averageRate'])

g1 = plotRateTheroy(maxObservation, incidence)  # 理論値を描出
#g1.set(ylim=[0,1])

print("全体症例数=", totalPatientNum, end="")
print("  発症率=", incidence, end="")
print("  観察年数=", maxObservation)
print("コホート症例数=", numSelectedPatients, end="")
print("  コホート回数=", repeat)

# %%
## 真値（理論値）に対するコホート値のばらつきを箱髭図で表現
# boxplotのためにdfをtidy化
# https://qiita.com/ishida330/items/922caa7acb73c1540e28

dataCohort_repeat_df = pd.DataFrame(dataCohort_repeat)  # 各年度の平均発生率
dataCohort_repeat_df['cohortID'] = list(range(0, repeat))  # コホート研究番号

# melt でコホート研究番号をIDに tidy化
dataCohort_repeat_df_tidy = pd.melt(dataCohort_repeat_df, ['cohortID'], var_name='year', value_name='rate')

dataCohort_repeat_df_tidy = dataCohort_repeat_df_tidy.sort_values('cohortID')  # 年で並び替え
g2 = sns.boxplot(x="year", y="rate", data=dataCohort_repeat_df_tidy)  # 箱髭図
g2 = plotRateTheroy(maxObservation, incidence)  # 理論値を描出
