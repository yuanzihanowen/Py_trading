__author__ = 'zihanyuanowen'

import pandas as pd
import numpy as np
import os


def calculate_cci(security_name, period=15):
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
    df_cci.to_csv(os.getcwd() +'/engine_output/' + security_name + '_cci.csv')
    return df_cci


def ts_model(df_cci, security_name):
    #time series analysis of the CCI time series
    
    print(df_cci)


if __name__ == '__main__':
    os.chdir(os.path.expanduser('~/Desktop/PyScrap'))
    # security_list = ['EUR_USD', 'USD_JPY', 'GBP_USD', 'USD_CHF']
    security_list = ['EUR_USD']

    for security in security_list:
        if not os.path.exists(os.getcwd() +'/engine_output/'):
            os.makedirs(os.getcwd() +'/engine_output/')
        df_cci = calculate_cci(security)
        ts_model(df_cci, security)
