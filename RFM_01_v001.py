#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 27 14:37:51 2021

@author: aram
"""

### importing necessary libraries
import pandas as pd
import datetime as dt
import numpy as np

path_s= '/home/aram/Desktop/Dropbox/01_SampleDatasets/'
###############################################################
### importing the data
df = pd.read_csv(path_s+'cdnow_data_year1.csv')
df.dtypes
df['Date'] = pd.to_datetime(df['Date'] , format='%Y%M%d')


###############################################################
###Calculating Recency
df_recency = df.groupby(by= 'ID' , as_index=False)['Date'].max()
df_recency.columns = ['ID','LastPurchase']
df_recency['Recency'] = df_recency['LastPurchase'].apply(lambda x: (df_recency['LastPurchase'].max() - x).days  )


###############################################################
###Calculating Frequency
df_frq = df.groupby(by = 'ID', as_index=False)['Date'].count()
# df_frq = df.drop_duplicates().groupby(by= ['ID'], as_index=False )['Date'].count()
# len(df['ID'].unique())
df_frq.columns = ['ID', 'Freq']


###############################################################
###Calculating Monetary Value
df_mont = df.groupby(by = 'ID', as_index=False)['Amount Spent'].sum()


df_rfm = pd.DataFrame()
df_rfm = df_recency.merge(df_frq, on='ID')
df_rfm = df_rfm.merge(df_mont, on='ID')


###############################################################
###Ranking Customer’s based upon their 

df_rfm['R_rank'] = df_rfm['Recency'].rank(ascending=False)
df_rfm['F_rank'] = df_rfm['Freq'].rank(ascending=True)
df_rfm['M_rank'] = df_rfm['Amount Spent'].rank(ascending=True)


# normalizing the rank of the customers
df_rfm['r_rank_norm'] = ( df_rfm['R_rank'] / df_rfm['R_rank'].max()*100  )
df_rfm['f_rank_norm'] = ( df_rfm['F_rank'] / df_rfm['F_rank'].max()*100  )
df_rfm['m_rank_norm'] = ( df_rfm['M_rank'] / df_rfm['M_rank'].max()*100  )



###############################################################
### Calculate RFM Score 
"""
RFM score is calculated based upon recency, frequency, monetary value normalize ranks. 
Based upon this score we divide our customers. Here we rate them on a scale of 5. 
Formula used for calculating rfm score is : 0.15*Recency score + 0.28*Frequency score + 0.57 *Monetary score
"""

df_rfm['RFM_Score'] = (0.15*df_rfm['r_rank_norm'])+ (0.28 *df_rfm['f_rank_norm'])+ (0.57*df_rfm['m_rank_norm'])

###Rescalre RFM between 0 and 5 
df_rfm['RFM_Score'] *= 0.05
df_rfm = df_rfm.round(2)            #TODO round a float to 2 decimals 


###############################################################
### Rating Customer based upon the RFM score
"""
rfm score >4.5 : Top Customer
4.5 > rfm score > 4 : High Value Customer
4>rfm score >3 : Medium value customer
3>rfm score>1.6 : Low-value customer
rfm score<1.6 :Lost Customer
"""

#customer segmentation 
df_rfm["Customer_segment"] = np.where(df_rfm['RFM_Score'] >	4.5, "Top Customers",
                                      (np.where(df_rfm['RFM_Score'] > 4, "High value Customer",
                                                (np.where(df_rfm['RFM_Score'] > 3, "Medium Value Customer",
                                                          np.where(df_rfm['RFM_Score'] > 1.6, 'Low Value Customers', 'Lost Customers'))))))

df_rfm[['CustomerName', 'RFM_Score', 'Customer_segment']].head(20)


###############################################################
### Plotting
import matplotlib.pyplot as plt
plt.pie(df_rfm.Customer_segment.value_counts(),
        labels=df_rfm.Customer_segment.value_counts().index,
        autopct='%.0f%%')
plt.show()

















