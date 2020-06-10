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
#--------
#This part loads chat data from all the chat files
#--------
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

#--------
#This part does the anlysis
#--------
first = True

for i in range(len(df)-1):
    #Start off by grouping everything into buckets of 10 seconds
    grouped_time = df[i].groupby(pd.Grouper(key='Time',freq='10s'))
    size = grouped_time.size()

    #Calculate a rolling sum of our buckets (this smooths out the data. i dont like my data chunky
    rollingsum = size.rolling('60s').sum()

    #This is how far apart each hilight has to be
    #In this case n=15 means "150 seconds" apart (10s buckets * 15)
    n = 15

    rollingsum = rollingsum.reset_index()

    #This part identifies high-points using the rolling sums
    extremes = argrelextrema(rollingsum[0].values, np.greater_equal, order=n)
    rollingsum['maxes'] = rollingsum.iloc[extremes[0]][0]
    rollingsum['maxes'] = rollingsum['maxes']*100//rollingsum['maxes'].max()
    rollingsum['vidID'] = df[i].iloc[0]['Video']

    #I'm subtracting one minute here because the chat laughter detected usually comes *after* the joke
    #Also im subtracting a minute because of the width of the rolling sum but thats whatever
    t = (rollingsum['Time'] - pd.Timedelta(minutes=1)).dt

    #Chunk up our datetimes into nicer packets
    rollingsum['h'] = t.strftime('%H')
    rollingsum['m'] = t.strftime('%M')
    rollingsum['s'] = t.strftime('%S')

    #Roll it all up into one dataframe
    if first:
        rollingsums = rollingsum[rollingsum.maxes.notna()]
        first = False
    else:
        rollingsums = rollingsums.append(rollingsum[rollingsum.maxes.notna()])