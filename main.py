import pandas as pd
from datetime import datetime
import datetime as dt
import re
from scipy.signal import argrelextrema
import numpy as np
import matplotlib.pyplot as plt
import os

# These are all "Regular Expressions" designed to detect Mirth
mirth = "|".join([r'(\bl+o+l+\b)', r'\bl+m+a+o+\b', r'(\bro+f+l+\b)', r'(\bha\b)', r'(\ba*(h+a+)+\b)',
                  r'(\bfunny\b)', 'love', 'great', 'incredible', 'joke', r'\bom+g+\b'])

questionable_mirth = ['good']

count = 0
df = []
# --------
# This part loads chat data from all the chat files
# --------
for filename in os.listdir('chat_data'):
    count += 1
    timelist = []
    namelist = []
    msglist = []
    vidlist = []
    with open('chat_data\\' + filename, encoding="utf8") as file:
        for line in file:
            msg = re.search(r">.*", line)[0][1:]

            # Only accept data that contains Mirth
            if re.search(mirth, msg, re.IGNORECASE) is not None:
                vidlist += [filename.split('.')[0]]
                namelist += [re.search("<.*?>", line)[0][1:-1]]
                time = datetime.strptime(re.search(r"\[(.*?)\]", line)[0][1:-1], "%H:%M:%S")
                timelist += [time + dt.timedelta(days=count * 2)]
                msglist += [re.search(r">.*", line)[0][1:]]
    if len(msglist) > 0:
        data = {'Video': vidlist, 'Name': namelist, 'Time': timelist, 'Message': msglist}
        df += [pd.DataFrame(data)]

# --------
# This part does the anlysis
# --------
first = True

# Analyze every vod loaded (70 current)
for i in range(len(df) - 1):
    # Start off by grouping everything into buckets of 10 seconds
    grouped_time = df[i].groupby(pd.Grouper(key='Time', freq='10s'))
    size = grouped_time.size()

    # Calculate a rolling sum of our buckets (this smooths out the data. i dont like my data chunky
    rollingsum = size.rolling('60s').sum()

    # This is how far apart each hilight has to be
    # In this case n=50 means "500 seconds" apart (10s buckets * 50)
    n = 50

    rollingsum = rollingsum.reset_index()

    # This part identifies high-points using the rolling sums
    extremes = argrelextrema(rollingsum[0].values, np.greater_equal, order=n)
    sanitized_extremes = []  # Remove duplicate extremes
    for j in range(1, len(extremes[0]) - 1):
        if (extremes[0][j] - extremes[0][j - 1] > 3):
            sanitized_extremes += [extremes[0][j - 1]]
    sanitized_extremes += [extremes[0][len(extremes[0])-1]]

    rollingsum['maxes'] = rollingsum.iloc[sanitized_extremes][0]
    rollingsum = rollingsum[rollingsum.maxes.notna()]
    rollingsum.sort_values('maxes',ascending=False)
    # This part normalizes the maximums to a scale of 1-100; where 100 is the Funniest Moment in each vod
    rollingsum['maxes'] = range(1,rollingsum.shape[0]+1)
    vodID = df[i].iloc[0]['Video']
    rollingsum['vidID'] = vodID

    # I'm subtracting one minute here because the chat laughter detected usually comes *after* the joke
    # Also im subtracting a minute because of the width of the rolling sum but thats whatever
    t = (rollingsum['Time'] - pd.Timedelta(minutes=1)).dt

    # Chunk up our datetimes into nicer packets
    rollingsum['h'] = t.strftime('%H')
    rollingsum['m'] = t.strftime('%M')
    rollingsum['s'] = t.strftime('%S')


    for index, row in rollingsum.iterrows():
        rollingsum.loc[index,'VidLink'] = r'https://www.twitch.tv/videos/' + vodID + r'?t=' + rollingsum['h'][index] + 'h' + rollingsum['m'][index] + 'm' + rollingsum['s'][index] + 's'

    # Roll it all up into one dataframe
    if first:
        rollingsums = rollingsum
        first = False
    else:
        rollingsums = rollingsums.append(rollingsum)
rollingsums = rollingsums.sort_values('maxes')