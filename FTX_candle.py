from typing import Dict
import requests
from datetime import datetime
import csv
import configparser


config = configparser.ConfigParser()
config.read('config/config.ini')

Market = config['Setting']['Market'] + '-PERP'
Time = int(config['Setting']['Time'])
Start = int(datetime.strptime(config['Setting']['Starttime'], "%Y-%m-%d %H:%M:%S").timestamp())
End = config['Setting']['Endtime']
if End == 'now' :
    End = int(datetime.now().timestamp())
else :
    End = int(datetime.strptime(End, "%Y-%m-%d %H:%M:%S").timestamp())


x = 0
Start2 = Start
file_name = 'candle_' + Market + '_Time_' +  str(Time) + '.csv'
path = 'candle/' +file_name

with open(path, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Date', 'Open', 'High', 'Low', 'Close'])

while x < 999999 :
    Time0 = Start + x * (Time*1000) + Time
    Time1 = Start + (x + 1) * (Time*1000)
    if Time1 >= End :
        Time1 = End
        x = 1000000

    print(f'Time0: {Time0}  Time1: {Time1}, End {End}')
    URL = 'https://ftx.com/api/markets/'+  Market  + '/candles?resolution=' + str(Time) + '&start_time=' + str(Time0) + '&end_time=' + str(Time1)
    resp_F = (requests.get(URL)).json()
    
    try :
        for i in range(len(resp_F['result'])):
            with open(path, 'a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([resp_F['result'][i]['startTime'][0:10:]+" "+resp_F['result'][i]['startTime'][11:19:], str(resp_F['result'][i]['open']), str(resp_F['result'][i]['high']), str(resp_F['result'][i]['low']), str(resp_F['result'][i]['close'])])
    except :
        print('Unsupported candle resolution, time : 1, 60, 300, 3600')
        x = 1000000

    x = x +1

print(f'File {file_name} done')
