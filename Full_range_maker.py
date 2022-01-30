from typing import Dict
import requests
from datetime import datetime
import csv
from csv import reader
import configparser

config = configparser.ConfigParser()
config.read('config/config.ini')

Market = config['Full_range_setting']['Market']
Liquidity = float(config['Full_range_setting']['Liquidity'])
Trigger = 1000000

file_name = 'candle_' + Market + '.csv'
path = 'candle/' +file_name

f = open(path, 'r')
crv_price = list(reader(f, delimiter=','))

#輸出設定
output_path_file = 'Full_range_maker_' + Market + '.csv'
output_path ='output/' +output_path_file

with open(output_path, 'w', newline='') as outputfile:
    writer = csv.writer(outputfile)
    writer.writerow(['Date', 'Open', 'High', 'Low', 'Close', 'Mid_price', 'r', 'Impermanent_loss'])

#main Strategy
for i in range(1,len(crv_price)):
    Date = crv_price[i][0]
    Open_price = float(crv_price[i][1])
    High_price = float(crv_price[i][2])
    Low_price = float(crv_price[i][3])
    Close_price = float(crv_price[i][4])

    #計算中間價
    if i > 1 :
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



