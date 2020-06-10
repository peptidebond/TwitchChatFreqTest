import tkinter.filedialog
import tkinter as tk
import pandas as pd
from datetime import datetime
import datetime as dt
import re
from scipy.signal import argrelextrema
import numpy as np
import matplotlib.pyplot as plt
import os
root = tk.Tk()
root.update()
root.destroy()

mirth = "|".join([r'(\bl+o+l+\b)',r'\bl+m+a+o+\b',r'(\bro+f+l+\b)',r'(\b(he)+\b)',r'(\bha\b)',r'(\ba*(h+a+)+\b)', r'(\bfunny\b)', 'love', 'good', 'great', 'incredible', r'\bom+g+\b'])

count = 0
df = []
for filename in os.listdir('chat_data'):
    count += 1
    timelist = []
    namelist = []
    msglist = []
    vidlist = []
    with open('chat_data\\' + filename, encoding="utf8") as file:
        for line in file:
            msg = re.search(r">.*", line)[0][1:]
            if re.search(mirth,msg, re.IGNORECASE) is not None:
                vidlist += [filename.split('.')[0]]
                namelist += [re.search("<.*?>", line)[0][1:-1]]
                time = datetime.strptime(re.search(r"\[(.*?)\]", line)[0][1:-1], "%H:%M:%S")
                timelist += [time + dt.timedelta(days=count*2)]
                msglist += [re.search(r">.*", line)[0][1:]]
    if len(msglist) > 0:
        data = {'Video': vidlist, 'Name': namelist, 'Time': timelist, 'Message': msglist}
        df += [pd.DataFrame(data)]

first = True

for i in range(len(df)-1):
    grouped_time = df[i].groupby(pd.Grouper(key='Time',freq='10s'))
    size = grouped_time.size()
    rollingsum = size.rolling('60s').sum()
    n=15

    rollingsum = rollingsum.reset_index()
    extremes = argrelextrema(rollingsum[0].values, np.greater_equal, order=n)
    rollingsum['maxes'] = rollingsum.iloc[extremes[0]][0]
    rollingsum['maxes'] = rollingsum['maxes']*100//rollingsum['maxes'].max()
    rollingsum['vidID'] = df[i].iloc[0]['Video']
    t = (rollingsum['Time'] - pd.Timedelta(minutes=1)).dt
    rollingsum['h'] = t.strftime('%H')
    rollingsum['m'] = t.strftime('%M')
    rollingsum['s'] = t.strftime('%S')
    if first:
        rollingsums = rollingsum[rollingsum.maxes.notna()]
        first = False
    else:
        rollingsums = rollingsums.append(rollingsum[rollingsum.maxes.notna()])

'''
plt.scatter(df.index, df['maxes'], c='r')
plt.plot(df.index, df[0])

prevbiggest=-9999
for index in extremes[0]:
    if (index-prevbiggest > 60):
        prevbiggest = index
        plt.annotate(df.iloc[index]['Time'].__format__('%H:%M:%S'), xy=(index, df.iloc[index][0]), xytext=(index, df.iloc[index][0]+5),
            arrowprops=dict(facecolor='black', shrink=0.05),
            )

plt.show()'''