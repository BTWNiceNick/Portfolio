from __future__ import (absolute_import, division, print_function,unicode_literals)
'''--------------------------------
@BTWNiceNick
Test Treding Strategy
--------------------------------'''

# Base Import
import datetime  # For datetime objects
import os
import pandas as pd
import csv
import numpy as np
import time

# Import the backtrader platform
import backtrader as bt
import backtrader.indicators as btind
 
# Import for visual rappresentation cerebro.plot()
from matplotlib.dates import (HOURS_PER_DAY, MIN_PER_HOUR, SEC_PER_MIN, MONTHS_PER_YEAR, DAYS_PER_WEEK,
                              SEC_PER_HOUR, SEC_PER_DAY, num2date, rrulewrapper, YearLocator, MicrosecondLocator)

# Other Import
# from report import core

#-------------------------------------------------------------------------------------

# Commission Trading System
class CommInfo_Stocks_PercAbs(bt.CommInfoBase):
    params = (
        ('stocklike', True),
        ('commtype', bt.CommInfoBase.COMM_FIXED),
        ('percabs', True),
    )

# Create a Stratey
class TestStrategy(bt.Strategy):
    params = dict(
        ma=bt.ind.SMA,
        cash = 20000,
        p1=5,
        p2=15,
        limit=0.005,
        limdays=3,
        limdays2=1000,
        hold=10,
        usebracket=False,  # use order_target_size
        switchp1p2=False,  # switch prices of order1 and order2
        pfast=50,  # period for the fast moving average
        pslow=200   # period for the slow moving average
    )

    def start(self):
        # WRITE REPORT
        self.mystats = open('./RandomTest/Project_Backtrader_1.0/my_stats.csv', 'a')
        #self.mystats.write('datetime,initial_Cash,P/L,Stop_Loss,Take_Profit\n')

    def log(self, csv, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), csv))

    def __init__(self,stoploss,takeprofit):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close

        #TEST
        self.stopLoss=stoploss
        self.takeProfit = takeprofit

        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None
        #self.stopLoss = 0.02
        #self.takeProfit = 0.05

        # Add a MovingAverageSimple indicator
        # subplot per decidere dove vuoi farlo stampare : True Sopra il grafico del prezzo
        self.sma = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=21,subplot=False)

        self.sma50 = btind.SMA(period=self.p.pfast, subplot=False)  # fast moving average
        self.sma200 = btind.SMA(period=self.p.pslow, subplot=False)  # slow moving average

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Write down: no pending order
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))

        # WRITE REPORT
        self.mystats.write(self.data.datetime.date(0).strftime('%Y-%m-%d'))
        self.mystats.write(',%.0f' % self.p.cash)
        #self.mystats.write(',%.2f' % self.stats.drawdown.drawdown[-1])
        #self.mystats.write(',%.2f' % self.stats.drawdown.maxdrawdown[-1])
        self.mystats.write(',%.2f' % trade.pnl)
        self.mystats.write(',%.2f' % self.stopLoss)
        self.mystats.write(',%.2f' % self.takeProfit)
        self.mystats.write('\n')
        

    def next(self):
        

        # Simply log the closing price of the series from the reference
        self.log('Close, %.2f' % self.dataclose[0])

        # Access -1, because drawdown[0] will be calculated after "next"
        self.log('DrawDown: %.2f' % self.stats.drawdown.drawdown[-1])
        self.log('MaxDrawDown: %.2f' % self.stats.drawdown.maxdrawdown[-1])

        '''# Set SL and TP
        self.stopLoss = 0.10
        self.takeProfit = 0.12'''
        
        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return

        # Check if we are in the market
        if not self.position:

            if self.sma50[0] > self.sma200[0]:

                # Not yet ... we MIGHT BUY if ...
                if self.data.open[3] > self.data.open[2]:
                    if self.data.open[2] > self.data.open[1]:
                        if self.data.close[0] > self.data.open[1]:
                            if self.data.close[0] > self.sma[0]:
                    
                                close = self.data.close[0]
                                p1 = close * (1.0 - self.p.limit)
                                p2 = p1 - self.stopLoss * close
                                p3 = p1 + self.takeProfit * close

                                valid1 = datetime.timedelta(self.p.limdays)
                                valid2 = valid3 = datetime.timedelta(self.p.limdays2)

                                if self.p.switchp1p2:
                                    p1, p2 = p2, p1
                                    valid1, valid2 = valid2, valid1

                                if not self.p.usebracket:
                                    o1 = self.buy(exectype=bt.Order.Limit,
                                                price=p1,
                                                valid=valid1,
                                                transmit=False)

                                    print('{}: Oref {} / Buy at {}'.format(
                                        self.datetime.date(), o1.ref, p1))

                                    o2 = self.sell(exectype=bt.Order.Stop,
                                                price=p2,
                                                valid=valid2,
                                                parent=o1,
                                                transmit=False)

                                    print('{}: Oref {} / Sell Stop at {}'.format(
                                        self.datetime.date(), o2.ref, p2))

                                    o3 = self.sell(exectype=bt.Order.Limit,
                                                price=p3,
                                                valid=valid3,
                                                parent=o1,
                                                transmit=True)

                                    print('{}: Oref {} / Sell Limit at {}'.format(
                                        self.datetime.date(), o3.ref, p3))

                                    self.orefs = [o1.ref, o2.ref, o3.ref]

                                else:
                                    os = self.buy_bracket(
                                        price=p1, valid=valid1,
                                        stopprice=p2, stopargs=dict(valid=valid2),
                                        limitprice=p3, limitargs=dict(valid=valid3),)

                                    self.orefs = [o.ref for o in os]    

            


def main(ticker, initial_cash, stoploss, takeprofit):

    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Add a strategy
    cerebro.addstrategy(TestStrategy, stoploss,takeprofit)

    # ticker = 'FDX'
    # Create a Data Feed
    data = bt.feeds.YahooFinanceCSVData(
        dataname=f'./RandomTest/Project_Backtrader_1.0/data/{ticker}.csv',
        # Do not pass values before this date
        fromdate=datetime.datetime(2017, 1, 1),
        # Do not pass values before this date
        todate=datetime.datetime(2022, 3, 31),
        # Do not pass values after this date
        reverse=False)

    # Add the Data Feed to Cerebro
    cerebro.adddata(data)

    # Plot Drawdonw ?
    cerebro.addobserver(bt.observers.DrawDown)

    # Set our desired cash start
    # initial_cash = 20000
    cerebro.broker.setcash(initial_cash)

    # Add a FixedSize sizer according to the stake
    #cerebro.addsizer(bt.sizers.FixedSize, stake=10)
    # Add a PercSize sizer according to the stake
    cerebro.addsizer(bt.sizers.PercentSizer, percents=80)

    # Set the commission
    #cerebro.broker.setcommission(commission=0.01)

    comminfo = CommInfo_Stocks_PercAbs(commission=0.08)
    cerebro.broker.addcommissioninfo(comminfo)

    # Run over everything
    cerebro.run()
    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % initial_cash)

    # Print out the final result
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    print('On this Ticker:', ticker)

    # Plot the result
    # Line Plot
    # cerebro.plot()
    # Candelstick Plot
    # cerebro.plot(style='candlestick', barup='green', bardown='red')

def core():
    list_ticker = ['MMM']
    for k in range(1,5,1):
        #k/=10
        for j in range(0,1,1):
            #j/=10
            #j-=10
            j=round(j,1)
            for i in list_ticker:

                #TICKER, Initial cash, stop loss, take profitt
                main(i, 20000,j,k)
                # setup time to wait before start another cycle
                time.sleep(1)

                df = pd.read_csv('./RandomTest/Project_Backtrader_1.0/my_stats.csv')
                #print(df.head())

                #profit_loss  = df['P/L'].sum()

                #Write report using pandas
                write_report(i,j,k)

'''
                initial_cash = df['initial_Cash'][0]
                final_cash = initial_cash

                for i in what:
                    final_cash += i

                gros_profit = final_cash-initial_cash
                fees_calc = len(what)*2
                net_calc = (gros_profit*0.74)-fees_calc+initial_cash


                print('----------BACK TRADER RESUME------------')
                print('TICKER: ', list_ticker)
                print('Initial Cash: ', initial_cash)
                print('Final Cash: %.2f' % final_cash)
                print('Gross Profit: %.2f' % gros_profit)
                print('Total Fees: ', fees_calc)
                print('Net Profit: %.2f' % net_calc)
                print('----------------LOSE----------------')
                print('Max Drawdonw: ', df['P/L'].min())
                print('Mean Drawdonw: %.2f' % np.mean(lose_calc))
                print('Min Drawdonw: ?')
                print('----------------GAIN----------------')
                print('Max Gain: ', df['P/L'].max())
                print('Mean Gain: %.2f' % np.mean(gain_calc))
                print('Min Gain: ?')
                print('------------------------------------')
                print('Number of Total trade: ', len(what))
                print('Number of gain trade: ', len(gain_calc))
                print('Number of lose trade: ', len(lose_calc))
                print('Winrate from 0 to 1 (more is better): %.2f' % win_rate)
                print('------------------------------------')'''
        
def setup_stats():
    path = os.getcwd()
    directory = path +'/RandomTest/Project_Backtrader_1.0'
    if not os.path.isfile(os.path.join(directory, "my_stats.csv")):
        with open(os.path.join(directory, "my_stats.csv"), "w", newline="") as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow([
                'datetime',
                'initial_Cash',
                'P/L',
                'Stop_Loss',
                'Take_Profit'])

def setup_report():
    path = os.getcwd()
    directory = path +'/RandomTest/Project_Backtrader_1.0'
    if not os.path.isfile(os.path.join(directory, "my_report.csv")):
        with open(os.path.join(directory, "my_report.csv"), "w", newline="") as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow([
                'Ticker',
                'WinRate',
                'P/L',
                'Stop_Loss',
                'Take_Profit'])

def write_report(tk,sl,tp):
    df = pd.read_csv('./RandomTest/Project_Backtrader_1.0/my_stats.csv')
    gain_calc = []
    lose_calc = []
    what = df['P/L'].tolist()

    for i in what:
        if i > 0:
            gain_calc.append(i)
        else:
            lose_calc.append(i)

    #win_rate = len(gain_calc)/(len(lose_calc)+len(gain_calc))

    #Only for test
    win_rate=1

    with open(os.path.join('./RandomTest/Project_Backtrader_1.0', "my_report.csv"), "a", newline="") as f:
        fieldnames = [
            'Ticker',
            'WinRate',
            'P/L',
            'Stop_Loss',
            'Take_Profit']

        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writerow(
            {'Ticker':tk,
            'WinRate':round(win_rate,2),
            'P/L':round(df['P/L'].sum(),2),
            'Stop_Loss':sl,
            'Take_Profit':tp
            }
        )

if __name__ == '__main__':
    start = time.time()
    setup_stats()
    setup_report()
    core()
    end = time.time()
    print(round(end - start),2)