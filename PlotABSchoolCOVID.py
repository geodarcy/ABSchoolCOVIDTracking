# track Alberta's school COVID outbreaks
# download daily COVID report from:
# https://www.alberta.ca/schools/covid-19-school-status-map.htm#list-of-school-outbreaks-by-region

import pandas as pd
from pandas import DataFrame
import os
import datetime
import matplotlib.pyplot as plt

path = '/Users/darcy/Documents/ABSchoolCOVIDTracking'
today = datetime.date.today()
# today = datetime.date(2021, 3, 30)
df_columns = ['Watch Edm', 'Watch Cgy', 'Watch Other', 'Outbreak Edm', 'Outbreak Cgy', 'Outbreak Other']
colours = ['#3182bd', '#de2d26', '#636363', '#9ecae1', '#fc9272', '#bdbdbd']

if os.path.exists(os.path.join(path, 'ABSchoolCOVIDDFPickle')):
  df = pd.read_pickle(os.path.join(path, 'ABSchoolCOVIDDFPickle'))
else:
  df = DataFrame(index = pd.to_datetime([]), columns = df_columns)

# import most recent data
try:
  schoolDF = pd.read_csv(os.path.join(path, 'covid19dataexport-schools.csv'))
except:
  print("Couldn't read in new data")

watches = DataFrame(schoolDF.loc[(schoolDF['School status'] == 'Outbreak (5-9 cases)') | (schoolDF['School status'] == 'Outbreak (10+ cases)'), 'Region name'].value_counts())
outbreaks = DataFrame(schoolDF.loc[schoolDF['School status'] == 'Alert (2-4 cases)', 'Region name'].value_counts())

for i in ['City Of Edmonton', 'City Of Calgary']:
  if i not in watches.index:
    watches.loc[i, 'Region name'] = 0
  if i not in outbreaks.index:
    outbreaks.loc[i, 'Region name'] = 0

watch_edm, watch_cal = watches.loc[['City Of Edmonton', 'City Of Calgary'], 'Region name']
watch_other = watches['Region name'].sum() - watch_edm - watch_cal
outbreak_edm, outbreak_cal = outbreaks.loc[['City Of Edmonton', 'City Of Calgary'], 'Region name']
outbreak_other = outbreaks['Region name'].sum() - outbreak_edm - outbreak_cal
df.loc[pd.Timestamp(today), df_columns] = [watch_edm, watch_cal, watch_other, outbreak_edm, outbreak_cal, outbreak_other]

## plot data as lines all together
# df.plot(color=colours, title='COVID-19 Outbreaks in Alberta Schools', figsize=(8, 8))
# plt.ylabel('Number of Outbreaks (2-4 cases)/Watches (5+ cases)')
# plt.xlabel('Date')
# plt.legend(loc='upper left')
# plt.savefig(os.path.join(path, 'Plots', '{}.png'.format(today.strftime('%Y%m%d'))))

## plot each region as a stacked area plot
colours = [['#fc9272', '#de2d26'], ['#9ecae1', '#3182bd'], ['#bdbdbd', '#636363']]
ymax = 0
for j in ['Cgy', 'Edm', 'Other']:
  case_sum = df[['Outbreak ' + j, 'Watch ' + j]].sum(axis=1).max()
  if case_sum > ymax:
    ymax = case_sum
figure, axes = plt.subplots(1, 3, sharey='row', figsize=(11,8.5))
for i,j in enumerate(['Cgy', 'Edm', 'Other']):
  df[['Outbreak ' + j, 'Watch ' + j]].plot.area(ax=axes[i], ylim=(0, ymax + 2), title=j, legend='reverse', color=colours[i])
figure.text(0.06, 0.5, 'Number of Outbreaks (2-4 cases)/Watches (5+ cases)\nHeight represents total number of schools affected', ha='center', va='center', rotation='vertical')
plt.savefig(os.path.join(path, 'Plots', '{}.png'.format(today.strftime('%Y%m%d'))))

df.to_pickle(os.path.join(path, 'ABSchoolCOVIDDFPickle'))
df.to_pickle(os.path.join(path, 'Backups',  'ABSchoolCOVIDDFPickle_backup_{}'.format(today.strftime('%Y%m%d'))))

# syntax to update my map
# schoolDF.loc[schoolDF['Region name'] == 'City Of Edmonton', ['School status', 'Schools details']]
