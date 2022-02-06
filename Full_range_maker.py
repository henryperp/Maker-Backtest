from typing import Dict
import requests
from datetime import datetime
import csv
from csv import reader
import configparser

config = configparser.ConfigParser()
config.read('config/config.ini')

Market = config['Full_range_setting']['Market'] + '-PERP'
Time = config['Full_range_setting']['Time']
Liquidity = float(config['Full_range_setting']['Liquidity'])
Starttime = config['Full_range_setting']['Starttime']
Starttime_S = int(datetime.strptime(Starttime, "%Y-%m-%d %H:%M:%S").timestamp())
Endtime = config['Full_range_setting']['Endtime']
if Endtime == 'now' :
    Endtime = str(datetime.strptime(Starttime, "%Y-%m-%d %H:%M:%S"))
    Endtime_S = int(datetime.now().timestamp())
else :
    Endtime_S = int(datetime.strptime(Endtime, "%Y-%m-%d %H:%M:%S").timestamp())
Trigger = 1000000


#讀取K線資料
file_name = 'candle_' + Market + '_Time_' +  str(Time) + '.csv'
path = 'candle/' + file_name
f = open(path, 'r')
crv_price = list(reader(f, delimiter=','))

#輸出檔案設定
output_path_file = 'Full_range_maker_' + Market + '_Time_' +  str(Time) + '.csv'
output_path ='output/' +output_path_file

with open(output_path, 'w', newline='') as outputfile:
    writer = csv.writer(outputfile)
    writer.writerow(['Date', 'Open', 'High', 'Low', 'Close', 'Mid_price', 'r', 'Impermanent_loss'])

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


#main Strategy
for i in range(start_count,end_count):
    Date = crv_price[i][0]
    Open_price = float(crv_price[i][1])
    High_price = float(crv_price[i][2])
    Low_price = float(crv_price[i][3])
    Close_price = float(crv_price[i][4])

    #計算中間價
    if i > start_count :
        #判斷前一小時是否觸及Trigger
        if float(crv_price[i-1][3]) <= (crv_price[i-1][5] / Trigger) :
            Mid_price = Mid_price[i -1] / Trigger

        elif float(crv_price[i-1][2]) >= (crv_price[i-1][5] * Trigger) :
            Mid_price = Mid_price[i -1] * Trigger
        
        else :
            Mid_price = crv_price[i-1][5]
            #價格變化
            k = Close_price / Mid_price
            #無常損失
            Impermanent_loss = Liquidity * (2 * k**0.5 / (1 + k) -1)

    else :
        Mid_price = Open_price
        Impermanent_loss = 0
        k = 1
    
    ouput = [Mid_price, k, Impermanent_loss]
    crv_price[i] = crv_price[i] + ouput
    with open(output_path, 'a', newline='') as outputfile:
            writer = csv.writer(outputfile)
            writer.writerow(crv_price[i])

print(f'File {output_path_file} done')



