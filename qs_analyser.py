"""
Python script to analyse irregular, personal Quantified Self data collected over months.
Gianluca Truda
November 2016
"""

import json
import csv
import time
import numpy as np
import matplotlib.pyplot as plt
import os


class Record:
    """
    A record holds a grouping of JSON data for a specific entry.
    e.g. 1 record would hold one evening's worth of data points.
    """
    def __init__(self, year, month, day, steps, prod_score, day_score):
        """
        Simple constructor.
        """
        self.time_string = ""
        self.year = year
        self.month = month
        self.day = day
        self.steps = steps
        self.productivity_score = prod_score
        self.day_score = day_score
        self.habits = []
        self.vector_habits = []

    def vectorise(self):
        for e in self.habits:
            if e == "Yes":
                self.vector_habits.append(1.0)
            elif e == "No":
                self.vector_habits.append(-1.0)
            else:
                self.vector_habits.append(0.0)

# Pull JSON data from file
data_file = open('reporter.json')
data = json.load(data_file)
snapshots = data['snapshots']
questions = data['questions']
record_list = []

# Iterates though the snapshots in imported from JSON data and creates Record objects with some data.
for e in snapshots:
    timestamp = time.strptime(e['date'], "%Y-%m-%dT%H:%M:%S+0200")
    step_count = int(e['steps'])
    for r in e['responses']:
        if r['questionPrompt'] == "How was today overall? (/5)":
            day_score = int(r['answeredOptions'][0])
        if r['questionPrompt'] == "How productive was today? (/5)":
            productivity_score = int(int(r['answeredOptions'][0]))
    if timestamp.tm_hour < 4 or timestamp.tm_hour > 18:
        if timestamp.tm_hour >= 0 and timestamp.tm_hour <= 4:
            record_list.append(Record(timestamp.tm_year, timestamp.tm_mon, timestamp.tm_mday-1, step_count,
                                      productivity_score, day_score))

# Pulling in CSV data and adding to matching records.
with open('way_of_life.csv') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',', quotechar='|')
    for row in reader:
        timestamp = time.strptime(row['Date'], "%Y/%m/%d")
        time_string = str(row['Date'])
        for rec in record_list:
            if rec.year == timestamp.tm_year and rec.month == timestamp.tm_mon and rec.day == timestamp.tm_mday:
                rec.time_string = time_string
                rec.habits = [row["Up before 8 am"], row["Wellbutrin"], row["Nutribullet shake"],
                              row["Meditation (AM)"], row["Intentional exercise"], row["Attended all lectures"],
                              row["Listened to music"], row["Socialised"], row["Radom act of Kindness"],
                              row["Did something creative"], row["Did something fun"], row["Went for a walk"],
                              row["Spent 15+ minutes outdoors"], row["Deep work"], row["Hit flow state today"],
                              row["Undistracted thinking time"], row["Healthy eating"],
                              row["Skipped meals (not fasting)"], row["Google Course"], row["Meditation (PM)"],
                              row["Read net 5 Pocket articles"], row["Podcasts / audiobook"], row["Read a book"],
                              row["Guitar"], row["Supplements"], row["Fap"], row["Tender Time"]]
                rec.vectorise()

# Remove record objects with incomplete data.
for r in record_list:
    if r.time_string == "" or len(r.habits) < 1:
        record_list.remove(r)

# Create a single matrix from the parameters of all records.
a = np.ndarray(shape=(len(record_list), 27), dtype=float)
for i in range(len(record_list)):
    a[i] = record_list[i].vector_habits


# Create a vector matrix from the Productivity scores.
b = np.ndarray(shape=(len(record_list), 1),  dtype=float)
for i in range(len(record_list)):
    b[i] = record_list[i].productivity_score

# Create a vector matrix from the Overall scores.
c = np.ndarray(shape=(len(record_list), 1),  dtype=float)
for i in range(len(record_list)):
    b[i] = record_list[i].day_score

# Matrix solving performed using Numpy
x = np.linalg.lstsq(a, b, rcond=-1)
result_prod = x[0]
y = np.linalg.lstsq(a, c, rcond=-1)
result_day = y[0]

for j in range(len(record_list)):
    total = 0
    for i in range(27):
        total += record_list[j].vector_habits[i]*result_prod[i]
    print(total, record_list[j].productivity_score)

#Plotting the data using pyplot
names = ["Up before 8 am", "Wellbutrin", "Nutribullet shake", "Meditation (AM)", "Intentional exercise",
         "Attended all lectures", "Listened to music", "Socialised", "Radom act of Kindness", "Did something creative",
         "Did something fun", "Went for a walk", "Spent 15+ minutes outdoors", "Deep work", "Hit flow state today",
         "Undistracted thinking time", "Healthy eating", "Skipped meals (not fasting)", "Google Course",
         "Meditation (PM)", "Read net 5 Pocket articles", "Podcasts / audiobook", "Read a book", "Guitar",
         "Supplements", "Param. F", "Param. S"]

plt.clf()
fig, ax = plt.subplots()
plt.style.use('ggplot')
x = names
y = result_prod
fig, ax = plt.subplots()
width = 0.90
ind = np.arange(len(y))
ax.barh(ind, y, width, color="blue")
ax.set_yticks(ind+width/2)
ax.set_yticklabels(x, minor=False)
plt.title('HABIT ANALYSIS : Habit Effect Model — Productivity', y=1.05)
plt.text(-2.5, 29, str(len(record_list))+" data points")
plt.text(-2.5, 30, time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))
#plt.tight_layout()
#plt.show()
plt.savefig(os.path.join('HabitModel_productivity.png'), dpi=300, format='png', bbox_inches='tight')
