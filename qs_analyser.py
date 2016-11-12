"""
Python script to analyse irregular, personal Quantified Self data collected over months.
Gianluca Truda
November 2016
"""

import json
import time
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np


class Record:
    """
    A record holds a grouping of JSON data for a specific entry.
    e.g. 1 record would hold one evening's worth of data points.
    """
    def __init__(self, year, month, day, steps):
        """
        Simple constructor.
        """
        self.year = year
        self.month = month
        self.day = day
        self.steps = steps



# Pull JSON data from file
data_file = open('reporter.json')
data = json.load(data_file)

snapshots = data['snapshots']
questions = data['questions']
record_list = []

for e in snapshots:
    timestamp = time.strptime(e['date'], "%Y-%m-%dT%H:%M:%S+0200")
    step_count = int(e['steps'])
    if timestamp.tm_hour < 4 or timestamp.tm_hour > 18:
        if timestamp.tm_hour >= 0 and timestamp.tm_hour <= 4:
            record_list.append(Record(timestamp.tm_year, timestamp.tm_mon, timestamp.tm_mday-1, step_count))

steps_list = []
days_list = []
index_list = []

for r in record_list:
    steps_list.append(r.steps)
    days_list.append(str(r.month)+"/"+str(r.day))
    index_list.append(r.month*31+r.day-220)

# Configuring the output graphic parameters
plt.clf()
plt.style.use('fivethirtyeight')
plt.scatter(index_list, steps_list)
plt.gca().xaxis.grid(False)
plt.ylim(ymin=0)
plt.xlim(xmin=0)
plt.xlabel("Day")
plt.ylabel("Steps")
plt.title(r'Scatterplot of Steps by Day')

# Generating image from graph

"""
# Saving the image as .png file
fig.savefig(fname)
"""


plt.show()
