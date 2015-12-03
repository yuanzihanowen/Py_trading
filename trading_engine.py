___author__ = 'zihanyuanowen'


import pandas as pd
import numpy as np
import os
import sklearn
from matplotlib import pyplot as plt
import rpy2.robjects as ro

def calculate_cci(security_name, period=20):
    px_file_path = os.getcwd() + '/output/' + security_name + '_data.csv'
    df = pd.read_csv(px_file_path)
    
    df_tp = pd.DataFrame(df, columns=['lowAsk', 'highAsk', 'closeAsk', 'time'])
    df_tp = df_tp.set_index('time')
    df_ask_last = pd.DataFrame(df_tp, columns=['closeAsk'])
    df_ask_high = pd.DataFrame(df_tp, columns=['highAsk'])
    df_ask_low = pd.DataFrame(df_tp, columns=['lowAsk'])
    df_tp = df_tp.sum(1)/3
    df_sma_tp = pd.rolling_mean(df_tp, window=period)
    df_md = pd.rolling_mean(df_sma_tp, window=period)
    df_md = abs(df_tp - df_md)*0.015
    df_cci = (df_tp - df_sma_tp)/df_md
    df_cci.columns = ['cci']
    return df_cci


def calculate_volume(security_name, period=15):
    px_file_path = os.getcwd() + '/output/' + security_name + '_data.csv'
    df = pd.read_csv(px_file_path)

    df_volume = pd.DataFrame(df, columns =['volume','time'])
    df_volume = df_volume.set_index(['time'])
    return df_volume


def get_trend(security_name):
    px_file_path = os.getcwd() + '/output/' + security_name + '_data.csv'
    df = pd.read_csv(px_file_path)

    df_tp = pd.DataFrame(df, columns=['lowAsk', 'highAsk', 'closeAsk', 'time'])
    # print(type(df_tp.iloc[1,3]))
    # df_tp['time'] = pd.to_datetime(df_tp['time'],format='%m/%d/%Y% %I:%M:%S')
    # df_tp['time'] = datetime.strptime(df_tp['time'] ,'%m/%d/%Y %I:%M:%S')
    df_tp = df_tp.set_index('time')
    df_tp = pd.DataFrame(df_tp, columns=['closeAsk','highAsk','time'])
    df_tp = df_tp.sum(1)/2
    # print(df_tp)
    df_tp.to_csv(os.getcwd() +'/engine_output/'+security_name+'_px_model.csv')

    # Use Mann-Kendall Test to test the existence of up or down trends
    # there is no package for MannKendall Test in Python
    ro.r("source('getTrend.R')")

    trend = pd.read_csv(os.getcwd()+'/engine_output/'+security_name+'_trend.csv')
    trend = trend.iloc[0,1]
    print(trend)
    return trend


def ts_signal(ts_cci, ts_volume, security_name):
    # time series analysis of the CCI time serie
    ts_cci.index = pd.to_datetime(ts_cci.index)
#    mu_cci = np.mean(ts_cci)
#    sigma_cci = np.std(ts_cci)
    ts_volume = pd.Series(ts_volume['volume'])

    # the model part needs to be worked on
    # Decompose the CCI into two parts (positive and negative)

    signal_cci = pd.DataFrame(index=ts_cci.index,columns=['signal'])

    ts_cci2 =ts_cci.shift(1)
    for idx in ts_cci.index:
        if ts_cci2[idx]<100 and ts_cci[idx]>100:
            signal_cci.loc[idx,'signal']=-1
        elif ts_cci2[idx]>-100 and ts_cci[idx]<-100:
            signal_cci.loc[idx,'signal']=1
    return signal_cci


def backtest(signal_cci,security):
    px_file_path = os.getcwd() + '/output/' + security + '_data.csv'
    df = pd.read_csv(px_file_path)

    initial_cash = 5000
    initial_trade_size = 100

    df_tb = pd.DataFrame(df, columns=['closeAsk', 'closeBid','time'])
    df_tb = df_tb.set_index('time')
    df_tb.index=pd.to_datetime(df_tb.index)
    # print(signal_cci.index)

    df_tb=pd.merge(df_tb,signal_cci,how='left',left_index=True,right_index=True)

    df_tb['quantity'] = initial_trade_size
    trade_buy = df_tb['signal']>0
    trade_buy = trade_buy.astype(int)
    trade_sell = df_tb['signal']<0
    trade_sell = trade_sell.astype(int)
    df_tb = df_tb.fillna(0)
    df_tb['notional'] = trade_buy*df_tb['signal']*df_tb['quantity']*df_tb['closeAsk']+trade_sell*df_tb['signal']*df_tb['quantity']*df_tb['closeBid']
    df_pos = df_tb['signal']*df_tb['quantity']
    df_notional= df_tb['notional']
    df_tb['total pos'] = df_pos.cumsum()
    df_tb['total_notional'] = -df_notional.cumsum()
    df_tb['pnl'] = df_tb['total pos']*df_tb['closeBid']+df_tb['total_notional']
    df_tb.to_csv(os.getcwd() + '/engine_output/' + security + '_blotter.csv')
    signal_cci.to_csv(os.getcwd() + '/engine_output/' + security + '_ccisignal.csv')
    plt.plot(df_tb.index,df_tb['pnl'])
    pnl_plot = plt.gcf()
    pnl_plot.savefig(os.getcwd() + '/engine_output/' + security + '.png')
    plt.close()
    print(df_tb)

if __name__ == '__main__':
    os.chdir(os.path.expanduser('~/Desktop/CCI'))
    # security_list = ['EUR_USD', 'USD_JPY', 'GBP_USD', 'USD_CHF']
    security_list = ['EUR_USD','USD_JPY','GBP_USD','USD_CHF']

    for security in security_list:
        if not os.path.exists(os.getcwd() +'/engine_output/'):
            os.makedirs(os.getcwd() +'/engine_output/')
        df_cci = calculate_cci(security)
        # get_trend(security)
        df_volume = calculate_volume(security)
        df_cci = df_cci.dropna()
        df_cci.name = ['cci']
        # print(df_cci.name)
        df_volume = pd.DataFrame(df_volume, index=df_cci.index)
        df_signal_cci = ts_signal(df_cci, df_volume, security)
        backtest(df_signal_cci,security)
