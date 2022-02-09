from typing import Dict
import requests
from datetime import datetime
import csv
from csv import reader
import configparser

config = configparser.ConfigParser()
config.read('config/config.ini')

Market = config['Fixed_range_setting']['Market'] + '-PERP'
Time = config['Fixed_range_setting']['Time']
Liquidity = float(config['Fixed_range_setting']['Liquidity'])
Starttime = config['Fixed_range_setting']['Starttime']
Starttime_S = int(datetime.strptime(Starttime, "%Y-%m-%d %H:%M:%S").timestamp())
Endtime = config['Fixed_range_setting']['Endtime']
if Endtime == 'now' :
    Endtime = str(datetime.strptime(Starttime, "%Y-%m-%d %H:%M:%S"))
    Endtime_S = int(datetime.now().timestamp())
else :
    Endtime_S = int(datetime.strptime(Endtime, "%Y-%m-%d %H:%M:%S").timestamp())
Trigger = 1000000
Upper = float(config['Fixed_range_setting']['Upper'])
Lower = float(config['Fixed_range_setting']['Lower'])
Trigger_Upper = float(config['Fixed_range_setting']['Trigger_Upper'])
Trigger_Lower  = float(config['Fixed_range_setting']['Trigger_Lower'])
k = ((1 + Upper) * (1 + Lower)) **0.5
r = 1+Trigger_Upper

###############################################################
#讀取K線資料
file_name = 'candle_' + Market + '_Time_' +  str(Time) + '.csv'
path = 'candle/' + file_name
f = open(path, 'r')
crv_price = list(reader(f, delimiter=','))

#輸出檔案設定
output_path_file = 'Fixed_range_maker_' + Market + '_Time_' +  str(Time) + '.csv'
output_path ='output/' +output_path_file
with open(output_path, 'w', newline='') as outputfile:
    writer = csv.writer(outputfile)
    writer.writerow(['Date', 'Open', 'High', 'Low', 'Close', 'Mid_price', 'Upper_price', 'Lower_price', 'Upper_Trigger', 'Lower_Trigger', 'r', 'Impermanent_loss', 'Total_IL'])

#回測時間過濾
Data_Start = crv_price[1][0]
Data_Start_S = int(datetime.strptime(Data_Start, "%Y-%m-%d %H:%M:%S").timestamp())
time_priod = int(datetime.strptime(crv_price[2][0], "%Y-%m-%d %H:%M:%S").timestamp()) -int(datetime.strptime(Data_Start, "%Y-%m-%d %H:%M:%S").timestamp())
#過濾開始時間
if Data_Start_S <= Starttime_S :
    start_count = int((Starttime_S - Data_Start_S) / time_priod) +1
else :
    start_count = 1

#過濾結束時間
Data_End = crv_price[len(crv_price)-1][0]
Data_End_S = int(datetime.strptime(Data_End, "%Y-%m-%d %H:%M:%S").timestamp())
if Data_End_S >= Endtime_S :
    end_count = int((Endtime_S - Data_Start_S) / time_priod) +1
else :
    end_count = len(crv_price)-1

###############################################################

def IL_calculate (Liquidity, k, r):
    formula = k **0.5 / ( k **0.5 - 1) * ( 2 * r **0.5 / ( r + 1) - 1)
    Il = formula * Liquidity * r / 2
    return Il


#main Strategy
for i in range(start_count,end_count):
    Date = crv_price[i][0]
    Open_price, High_price, Low_price, Close_price = float(crv_price[i][1]), float(crv_price[i][2]), float(crv_price[i][3]), float(crv_price[i][4])
    Open_Last, High_Last, Low_Last, Close_Last = float(crv_price[i-1][1]), float(crv_price[i-1][2]), float(crv_price[i-1][3]), float(crv_price[i-1][4])

    #計算中間價, if判斷式用於設定第一根K線
    if i > start_count :
        Mid_Last, Trigger_Upper_Last, Trigger_Lower_Last, Total_IL = float(crv_price[i-1][5]), float(crv_price[i-1][8]), float(crv_price[i-1][9]), float(crv_price[i-1][12])
        
        #判斷前一小時是否觸及Trigger, 假定價格移動方式為 Open->High->Low->Close, 依序讓價格經過這些點來模擬開關倉狀況
        #價格自Open ->High
        if High_price >= Trigger_Upper_Last : #觸發平衡
            Il_High =  IL_calculate(Liquidity, k, r)
            Mid_price = Trigger_Upper_Last
            Upper_price = Mid_price * (Upper+1)
            Lower_price = Mid_price / (Lower+1)
            Upper_Trigger = Mid_price * (Trigger_Upper+1)
            Lower_Trigger = Mid_price / (Trigger_Lower+1)
            alpha = 1
        else :
            Il_High = 0
            Mid_price = Mid_Last
            Upper_price = Mid_price * (Upper+1)
            Lower_price = Mid_price / (Lower+1)
            Upper_Trigger = Trigger_Upper_Last
            Lower_Trigger = Trigger_Lower_Last
        
        #價格自 High -> Low
        if Low_price <= Lower_Trigger : #觸發平衡
            Il_low =  IL_calculate(Liquidity, k, r)
            Mid_price = Lower_Trigger
            Upper_price = Mid_price * (Upper+1)
            Lower_price = Mid_price / (Lower+1)
            Upper_Trigger = Mid_price * (Trigger_Upper+1)
            Lower_Trigger = Mid_price / (Trigger_Lower+1)
            alpha = 1
        else :
            Il_low = 0

        #價格自 Low -> Close
        if Close_price >= Upper_Trigger :
            Il_close =  IL_calculate(Liquidity, k, r)
            Mid_price = Upper_Trigger
            Upper_price = Mid_price * (Upper+1)
            Lower_price = Mid_price / (Lower+1)
            Upper_Trigger = Mid_price * (Trigger_Upper+1)
            Lower_Trigger = Mid_price / (Trigger_Lower+1)
            alpha = 1
        else :
            Il_close = 0

        alpha = Close_price / Mid_price
        Impermanent_loss = IL_calculate(Liquidity, k, alpha)
        Total_IL = Total_IL + Il_High + Il_low + Il_close

    else : #第一根K線
        Mid_price = Open_price
        Upper_price = Mid_price * (Upper+1)
        Lower_price = Mid_price / (Lower+1)
        Upper_Trigger = Mid_price * (Trigger_Upper+1)
        Lower_Trigger = Mid_price / (Trigger_Lower+1)
        Impermanent_loss = 0
        Total_IL = 0
        alpha = 1
    
    ouput = [Mid_price, Upper_price, Lower_price, Upper_Trigger, Lower_Trigger, alpha, Impermanent_loss, Total_IL]
    crv_price[i] = crv_price[i] + ouput
    with open(output_path, 'a', newline='') as outputfile:
            writer = csv.writer(outputfile)
            writer.writerow(crv_price[i])

print(f'File {output_path_file} done')



