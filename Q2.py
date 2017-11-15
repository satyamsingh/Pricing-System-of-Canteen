from __future__ import division
import pandas as pd 
import numpy as np
from apyori import apriori
from collections import Counter
from apyori import apriori
import re
import itertools
import operator

df = pd.read_csv("/AugtoNov.csv")
pricedf = pd.read_csv("/monthwisePriceList.csv")
price_dict = dict(zip(pricedf['ItemID'], pricedf['SellingPriceDec']))

SellingHourDF = df['SellingDate'].str[11:13]
df['Hours'] = pd.Series(SellingHourDF, index=df.index)
SegmentDF = df['StudentID'].str[0:2]
df['Segment'] = pd.Series(SegmentDF, index=df.index)
df.sort_values(['ItemID', 'Hours', 'Segment'], ascending=[True, True, True], inplace=True)
#del df['Unnamed: 0']
SellingDatesDF = df['SellingDate'].str[:10]
df['SellingDates'] = pd.Series(SellingDatesDF, index=df.index)


#df = pd.read_csv("/AugtoNov.csv")
df['UniqueID'] = df['BillNo'].map(str) + df['SellingDates']
df['UniqueID'] = pd.Series(df['UniqueID'], index=df.index)
#print df.head()
df.to_csv("/AugtoNov.csv", index = False)


df = pd.read_csv("/AugtoNov.csv")


UniqueUsers = set(df['UniqueID'])

transcationDF = pd.DataFrame(columns=['Users', 'Items'])
k=0

for i in UniqueUsers:
    trndf = df.loc[df['UniqueID']== str(i), 'ItemID'].tolist()
    transcationDF.loc[k] = [i, trndf]
    k=k+1

print ((transcationDF.head()))

transcationDF.to_csv("/AugtoNovUniqueTransactions.csv", index = False)

nameofitemsDF = pd.read_csv("/monthwisePriceList.csv")
nameofItemsDict = nameofitemsDF.set_index('ItemID')['ItemName'].to_dict()
df = pd.read_csv("/AugtoNovDaytoDay.csv")

tlistt =df['Items'].tolist()
d = []
for i in range(len(df)):
    d.append((re.findall('\d+', tlistt[i])))

transactions = d
#print (transactions)
results = list(apriori(transactions, min_support =0.0001))


apDF = pd.DataFrame.from_records(results)
#print apDF.tail()


apDF.to_csv("/aprioriResult2.csv", index = False)

df = pd.read_csv("/AugtoNov.csv")
itemIDandfreq = df['ItemID'].value_counts()
print "The number of distinct items is: ", len(itemIDandfreq)
uniqueItemIDlist = set(df['ItemID'])



freqItem = pd.value_counts(df.ItemID)
s1 = pd.Series({'nunique': len(freqItem), 'unique values': freqItem.index.tolist()})
freqItem.append(s1)

freqItemDict = freqItem.to_dict()
#print freqItemDict

overallAvg = df['final_rating'].mean()

iteminDict = freqItemDict.keys()
freqinDict = freqItemDict.values()

freqavg = sum(freqinDict)/len(iteminDict)

#print overallAvg

rating_dict ={}
for key, value in freqItemDict.iteritems():
    rating= (sum(df.loc[df['ItemID']== key, 'final_rating']))/freqItemDict.get(key)
    rating_dict.update({key: rating})

print (rating_dict)

freqDF = pd.DataFrame(freqItemDict.items(),  columns=['Item', 'Freq'])
ratingDF = pd.DataFrame(rating_dict.items(),  columns=['Item', 'Rating'])
DFforCluster = pd.merge(freqDF, ratingDF)

DFforCluster.to_csv("/Clustering.csv", index = False)

itemlabel = {}
freqlabel = {}
low_rating_dict = {}
high_rating_dict = {}
frequent = {}
rare = {}
for key, value in rating_dict.iteritems():
    if value < overallAvg:
        low_rating_dict.update({key: value})
        itemlabel.update({key: 'L'})
    else:
        high_rating_dict.update({key: value})
        itemlabel.update({key: 'H'})
for key, value in freqItemDict.iteritems():
    if value > freqavg:
        frequent.update({key: value})
        freqlabel.update({key: 'F'})
    else:
        rare.update({key: value})
        freqlabel.update({key: 'R'})

#plt.bar(range(len(freqItemDict)), freqItemDict.values(), align='center')
#plt.xticks(range(len(freqItemDict)), freqItemDict.keys())

#plt.show()

high_rating_item_list = high_rating_dict.keys()
low_rating_item_list = low_rating_dict.keys()

apriori_list =[]
rating_for_combo_list = []
apriori_byname_list = []
label_list = []
support_list = []
newprice_list = []
for i in range(len(results)):
    label = ""
    a= (list(iter(results[i]).next()))
    a = map(int, a)
    if len(a)>1:
        apriori_list.insert(i, a)
        rating_for_combo = (sum(rating_dict.get(item) for item in a))/len(a)
        rating_for_combo_list.insert(i, rating_for_combo)
        apriori_byname = [nameofItemsDict.get(t) for t in a]
        apriori_byname_list.insert(i, apriori_byname)
        price = 0
        for k in a:
            label += itemlabel.get(k)
            price+= price_dict.get(k)

        label_list.insert(i, label)
        support_list.insert(i, apDF[1].iloc[i])
        newprice_list.append(price*(1-(0.20/len(a))))
        

combinationFromApriori = pd.DataFrame(
    {'ComboCode': apriori_list,
     'ComboName': apriori_byname_list,     
     'Support': support_list,
     'Favoured': label_list,
     'NewPrice' : newprice_list
     #'Rating': rating_for_combo_list
    })

#combinationFromApriori['AprioriResult'] = apDF[2]

combinationFromApriori.sort_values('Support', ascending=False, inplace=True)

combinationFromApriori.to_csv("/NonSingleComboApriori.csv", index = False)

combinationFromApriori = combinationFromApriori[~combinationFromApriori.Favoured.str.contains("HH")]
ffallowed = combinationFromApriori
ffallowed.to_csv("/FFallowed.csv", index = False)
combinationFromApriori = combinationFromApriori[~combinationFromApriori.Favoured.str.contains("FF")]

combinationFromApriori.to_csv("/LessFavouredCombos.csv", index = False)


#combinationFromApriori = combinationFromApriori[~combinationFromApriori.Favoured.str.contains("LHFR")]
#combinationFromApriori = combinationFromApriori[~combinationFromApriori.Favoured.str.contains("HLRF")]
print combinationFromApriori.head()
