import tkinter.filedialog
import tkinter as tk
import pandas as pd
from datetime import datetime
import re
from scipy.signal import argrelextrema
import numpy as np
import matplotlib.pyplot as plt
root = tk.Tk()
root.update()
filename = tkinter.filedialog.askopenfilename()
root.destroy()

timelist = []
namelist = []
msglist = []
with open(filename, encoding="utf8") as file:
    for line in file:
        namelist += [re.search("<.*?>", line)[0][1:-1]]
        time = datetime.strptime(re.search(r"\[(.*?)\]", line)[0][1:-1], "%H:%M:%S")
        timelist += [time]
        msglist += [re.search(r">.*", line)[0][1:]]

data = {'Name': namelist, 'Time': timelist, 'Message': msglist}
df = pd.DataFrame(data)

grouped_time = df.groupby(pd.Grouper(key='Time',freq='1s'))
size = grouped_time.size()
rollingsum = size.rolling('120s').sum()
n=180

df = rollingsum.reset_index()
extremes = argrelextrema(df[0].values, np.greater_equal, order=n)
df['maxes'] = df.iloc[extremes[0]][0]

plt.scatter(df.index, df['maxes'], c='r')
plt.plot(df.index, df[0])

prevbiggest=-9999
for index in extremes[0]:
    if (index-prevbiggest > 60):
        prevbiggest = index
        plt.annotate(df.iloc[index]['Time'].__format__('%H:%M:%S'), xy=(index, df.iloc[index][0]), xytext=(index, df.iloc[index][0]+5),
            arrowprops=dict(facecolor='black', shrink=0.05),
            )

plt.show()