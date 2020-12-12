# -*- coding: utf-8 -*-
"""
Created on Mon Oct  9 21:42:20 2017

@author: Efe
"""

#Get latest suggestion

import PatternDistribution
import Utils

datafile  = r"C:\Users\max\Google Drive\Thesis\Investing_latest.csv"
data = Utils.readInvData(datafile)

string = PatternDistribution.getSuggestedTrade(data,100,5)