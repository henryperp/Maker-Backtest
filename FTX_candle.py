from typing import Dict
import requests
from datetime import datetime
import csv
import configparser
import os


config = configparser.ConfigParser()
config.read('config/config.ini')

Market = config['Setting']['Market']
Start = int(datetime.strptime(config['Setting']['Starttime'], "%Y-%m-%d %H:%M").timestamp())
End = config['Setting']['Endtime']
if End == 'now' :
    End = int(datetime.now().timestamp())
else :
    End = int(datetime.strptime(End, "%Y-%m-%d %H:%M").timestamp())


x = 0
Start2 = Start
file_name = 'candle_' + Market + '.csv'
path = 'candle/' +file_name

with open(path, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Date', 'Open', 'High', 'Low', 'Close'])

while x < 999 :
    Time0 = Start + x * (3600000) + 3600
    Time1 = Start + (x + 1) * (3600000)
    if Time1 >= End :
        Time1 = End
        x = 1000

    print(f'Time0: {Time0}  Time1: {Time1}, End {End}')
    URL = 'https://ftx.com/api/indexes/'+  Market + '/candles?resolution=3600&start_time=' + str(Time0) + '&end_time=' + str(Time1)
    resp_F = (requests.get(URL)).json()
    
    for i in range(len(resp_F['result'])):
        with open(path, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([resp_F['result'][i]['startTime'][0:10:]+" "+resp_F['result'][i]['startTime'][11:19:], str(resp_F['result'][i]['open']), str(resp_F['result'][i]['high']), str(resp_F['result'][i]['low']), str(resp_F['result'][i]['close'])])

    x = x +1

print(f'File {file_name} done')
