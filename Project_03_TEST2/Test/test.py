import os
import pandas as pd

df = pd.read_csv('d:/#DAVIDE/#PROGRAMMAZIONE/LearningInPublic/Python/Project_03_TEST2/data/mystats.csv')
print(df)

profit  = (df['P/L'].sum()).round(2)

def calc_winrate(df):
    gain_calc = []
    lose_calc = []
    what = df['P/L'].tolist()

    for i in what:
        if i > 0:
            gain_calc.append(i)
        else:
            lose_calc.append(i)
        win_rate = len(gain_calc)/(len(lose_calc)+len(gain_calc))
    return win_rate


print('Max DD', df['P/L'].min())
print('Max Profit', df['P/L'].max())
print('Final P\L', profit)

