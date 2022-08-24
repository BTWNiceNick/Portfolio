# Import Other .py library
import csv
import pandas as pd
import numpy as np
import os

def core():
    df = pd.read_csv('LearningInPublic/Python/Project_03_TEST2/data/mystats.csv')
    #print(df.head())

    gain_calc = []
    lose_calc  =[]
    what = df['P/L'].tolist()

    for i in what:
        if i>0:
            gain_calc.append(i)
        else:
            lose_calc.append(i)

    win_rate = len(gain_calc)/(len(lose_calc)+len(gain_calc))

    initial_cash = df['initial_Cash'][0]
    final_cash  = initial_cash

    for i in what:
        final_cash += i

    gros_profit = final_cash-initial_cash 
    fees_calc = len(what)*2
    net_calc = (gros_profit*0.74)-fees_calc+initial_cash


    print('----------BACK TRADER RESUME------------')
    print('Initial Cash: ', initial_cash)
    print('Final Cash: %.2f' % final_cash)
    print('Gross Profit: %.2f' % gros_profit)
    print('Total Fees: ', fees_calc)
    print('Net Profit: %.2f' % net_calc)
    print('----------------LOSE----------------')
    print('Max Drawdonw: ' ,df['P/L'].min())
    print('Mean Drawdonw: %.2f' % np.mean(lose_calc))
    print('Min Drawdonw: ?')
    print('----------------GAIN----------------')
    print('Max Gain: ', df['P/L'].max())
    print('Mean Gain: %.2f' % np.mean(gain_calc))
    print('Min Gain: ?')
    print('------------------------------------')
    print('Number of Total trade: ', len(what))
    print('Number of gain trade: ',len(gain_calc))
    print('Number of lose trade: ',len(lose_calc))
    print('Winrate from 0 to 1 (more is better): %.2f' % win_rate)
    print('------------------------------------')

    directory = 'd:/#DAVIDE/#PROGRAMMAZIONE/LearningInPublic/Python/Project_03_TEST2/Test'

    if not os.path.isfile(os.path.join(directory, "report.csv")):
        with open(os.path.join(directory, "report.csv"), "w", newline="") as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow([
                'Initial_Cash',
                'Final_Cash',
                'Gross_Profit',
                'Net_Profit',
                'Total_Fees',
                'Stop_Loss',
                'Take_Profit',
                'Max_Drawdown',
                'Mean_Drawdonw',
                'Max_Gain',
                'Mean_Gain',
                'total_trade',
                'gain_trade',
                'lose_trade',
                'WinRate'])

    with open(os.path.join(directory, "report.csv"), "a", newline="") as f:
        fieldnames = [
            'Initial_Cash',
            'Final_Cash',
            'Gross_Profit',
            'Net_Profit',
            'Total_Fees',
            'Stop_Loss',
            'Take_Profit',
            'Max_Drawdown',
            'Mean_Drawdonw',
            'Max_Gain',
            'Mean_Gain',
            'total_trade',
            'gain_trade',
            'lose_trade',
            'WinRate']

        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writerow(
            {'Initial_Cash': df['initial_Cash'][0],
            'Final_Cash': int(final_cash),
            'Gross_Profit': int(gros_profit),
            'Net_Profit': int(net_calc),
            'Stop_Loss': (df['Stop_Loss'][0]),
            'Take_Profit': (df['Take_Profit'][0]),
            'Total_Fees': fees_calc,
            'Max_Drawdown': df['P/L'].min(),
            'Mean_Drawdonw': np.mean(lose_calc),
            'Max_Gain': df['P/L'].max(),
            'Mean_Gain': np.mean(gain_calc),
            'total_trade': len(what),
            'gain_trade': len(gain_calc),
            'lose_trade': len(lose_calc),
            'WinRate': win_rate
            }
        )
if __name__ == '__main__':
    core()