from __future__ import division
import pandas as pd 
import numpy as np
from apyori import apriori
from collections import Counter
import re
import itertools
import operator
import matplotlib.pyplot as plt
from collections import defaultdict


nameofitemsDF = pd.read_csv("/monthwisePriceList.csv")
nameofItemsDict = nameofitemsDF.set_index('ItemID')['ItemName'].to_dict()
df = pd.read_csv("/AugtoNov.csv")

SellingHourDF = df['SellingDate'].str[11:13] + "H"
df['Hours'] = pd.Series(SellingHourDF, index=df.index)
SegmentDF = df['StudentID'].str[0:2]
df['Segment'] = pd.Series(SegmentDF, index=df.index)
df.sort_values(['ItemID', 'Hours', 'Segment'], ascending=[True, True, True], inplace=True)
#del df['Unnamed: 0']
SellingDatesDF = df['SellingDate'].str[:10]
df['SellingDates'] = pd.Series(SellingDatesDF, index=df.index)
print (df.head())

#new = old[['A', 'C', 'D']].copy()
newDF = df[['Hours', 'Segment', 'ItemID']]
newDF = newDF.values.tolist()

transactions = newDF
print transactions[0]
results = list(apriori(transactions, min_support =0.0001))

apDF = pd.DataFrame.from_records(results)
print apDF.head()
apDF.to_csv("/Q1apriori.csv", index = False)

df = pd.read_csv("/AugtoNov.csv")
itemIDandfreq = df['ItemID'].value_counts()
print "The number of distinct items is: ", len(itemIDandfreq)
uniqueItemIDlist = set(df['ItemID'])


freqItem = pd.value_counts(df.ItemID)
s1 = pd.Series({'nunique': len(freqItem), 'unique values': freqItem.index.tolist()})
freqItem.append(s1)

freqItemDict = freqItem.to_dict()

overallAvg = df['final_rating'].mean()

iteminDict = freqItemDict.keys()
freqinDict = freqItemDict.values()

freqavg = sum(freqinDict)/len(iteminDict)

rating_dict ={}
for key, value in freqItemDict.iteritems():
    rating= (sum(df.loc[df['ItemID']== key, 'final_rating']))/freqItemDict.get(key)
    rating_dict.update({key: rating})


pricedf = pd.read_csv("/monthwisePriceList.csv")
price_dict = dict(zip(pricedf['ItemID'], pricedf['SellingPriceDec']))


segment_dict = {'F1': 12, 'F2': 32, 'F3': 30, 'F4': 20, 'F5': 3, 'H1':2, 'H2':2}

hour_dict = {1: 1, 2: 4, 3: 9, 4: 16, 5: 25, 6:36, 0:0}

apriori_list =[]
apriori_byname_list = []
label_list = []
support_list = []
quantities_list = []
itemNoList = []
revenue_list = []
penalty_list = []
segment_list = []
hour_list = []
for i in range(len(results)):
    label = ""
    a= (list(iter(results[i]).next()))
    #print (type(a[0]))
    #print (a[0])
    #print len(a)
    if len(a)==3:
        apriori_list.insert(i, a)
        if (type(a[0]) == int):
            itemNoList.append(a[0])
            if (a[1][0]=='F'):
                hour_list.append(a[2])
                segment_list.append(a[1])
                apriori_byname = [nameofItemsDict.get(a[0]), a[1], a[2]]
            else :
                hour_list.append(a[1])
                segment_list.append(a[2])
                apriori_byname = [nameofItemsDict.get(a[0]), a[2], a[1]]
        elif (type(a[1]) == int):
            itemNoList.append(a[1])
            if (a[0][0]=='F'):
                hour_list.append(a[2])
                segment_list.append(a[0])
                apriori_byname = [nameofItemsDict.get(a[1]), a[0], a[2]]
            else :
                hour_list.append(a[0])
                segment_list.append(a[2])
                apriori_byname = [nameofItemsDict.get(a[1]), a[2], a[0]]
        else:
            itemNoList.append(a[2])
            if (a[0][0]=='F'):
                hour_list.append(a[1])
                segment_list.append(a[0])
                apriori_byname = [nameofItemsDict.get(a[2]), a[0], a[1]]
            else :
                hour_list.append(a[0])
                segment_list.append(a[1])
                apriori_byname = [nameofItemsDict.get(a[2]), a[1], a[0]]
        apriori_byname_list.insert(i, apriori_byname)
        #df.loc[df['a'] == 1, 'b'].sum()
        #quantities = df.loc[(df['ItemID']== itemNoList[len(itemNoList)-1]) & (df['Hours'] + "H" is apriori_byname[2]) & (df['Segment'] is apriori_byname[1]), 'Quantity'].sum()
        quantities = df.loc[(df['ItemID']== itemNoList[len(itemNoList)-1]) & ((df['Hours'].map(str) + 'H') == apriori_byname[2]) & (df['Segment'] == apriori_byname[1]) , 'Quantity'].sum()
        quantities_list.insert(i, quantities)
        revenue = quantities*price_dict.get(itemNoList[len(itemNoList)-1])
        revenue_list.append(revenue)
        penalty = 0.1*price_dict.get(itemNoList[len(itemNoList)-1])*segment_dict.get(segment_list[len(segment_list)-1],  1)*1
        penalty_list.append(penalty)
        support_list.insert(i, apDF[1].iloc[i])

quantities_list = map(int, quantities_list)
ratio = [x/y for x, y in zip(revenue_list, penalty_list)]

combinationFromApriori = pd.DataFrame(
    {'ComboCode': apriori_list,
     'ComboName': apriori_byname_list,
     'Support': support_list,
     'Quantity': quantities_list,
     'Revenue' : revenue_list,
     'Penalty' : penalty_list,
     'Ratio': ratio,
     'Segment': segment_list
    })

#combinationFromApriori['AprioriResult'] = apDF[2]
combinationFromApriori =combinationFromApriori[combinationFromApriori.Segment != "F0"]
combinationFromApriori.sort_values('Support', ascending=False, inplace=True)
combinationFromApriori.sort_values('Ratio', ascending=False, inplace=True)
combinationFromApriori.to_csv("/Q1DynamicIncrease.csv", index = False)

print (combinationFromApriori.head())
