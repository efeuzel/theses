# -*- coding: utf-8 -*-
"""
Created on Sat Jul 29 17:51:25 2017

Engine for forex trade simulation

initialize: get price timeseries and set up trade log
openPos: post an open trade account with opening time, buy/sell
     opening price, tp, sl 
closePos: modify trade log to close a pos with closing time, closing price, pnl

next: move onto next point in time and price, execute TP and SL, update account

@author: Efe
"""

import datetime

class Engine(object):

    def __init__(self,args,histLen, maxHistLen):
        self.log = []
        self.alldata = args.values.tolist()
        self.hist = self.alldata[:maxHistLen]
        self.hist = self.hist[-histLen:]
        self.priceData = self.alldata[maxHistLen:]
        self.t = 0
        self.hasNext = True
#        [0 'time',1 'c', 2 'o', 3 'h', 4 'l', 5 range, 6 tprice]
        
    def openPos(self,side,comment = ""):
        #side: 1 for buy, -1 for sell
#        tPrice = self.priceData[self.t][6] #self.priceData.ix[self.t].tPrice
        o =  self.priceData[self.t][2]
        atr = sum([row[5] for row in self.hist[-3:]])/len(self.hist[-5:])
        tp = o + side*atr/3
        sl = o - side*atr/4
#       [0 'openTime', 1 'side', 2 'openPrice', 3 'SL', 4 'TP', 5 'closeTime', 6 'closePrice', 7 'pnl', 8 'comment']) #open at tPrice of the period    
#        self.log.append([self.priceData[self.t][0].strftime("%d.%m.%Y"), side, o ,sl,tp,datetime.datetime(9999,12,31).strftime("%d.%m.%Y"),0.0,0.0,comment])
        self.log.append([self.priceData[self.t][0], side, o ,sl,tp,datetime.datetime(9999,12,31).strftime("%d.%m.%Y"),0.0,0.0,comment])        

    def closePos(self):
        openPrice = self.log[-1][2]
        side = self.log[-1][1]
        sl = self.log[-1][3]
        tp = self.log[-1][4]

        high = self.priceData[self.t][3] #self.priceData.h[self.t]
        low = self.priceData[self.t][4]
        close = self.priceData[self.t][1]

        if ((high >= tp and side == 1) or (low <= tp and side == -1)):
            self.log[-1][6] = tp
        elif ((low <= sl and side == 1) or (high >= sl and side == -1)):
            self.log[-1][6] = sl
        else:
            self.log[-1][6] = close
        
        self.log[-1][7] = side * (self.log[-1][6] - openPrice)
#        self.log[-1][5] = self.priceData[self.t][0].strftime("%d.%m.%Y")
        self.log[-1][5] = self.priceData[self.t][0]
        
    def next(self):
        if(self.t+1 < len(self.priceData)):          
            del self.hist[0]
            self.hist.append(self.priceData[self.t])
            self.t = self.t+1
        else:
            self.hasNext = False
            
    def getPTR(self):
        ptr = len([elem for elem in self.log if elem[7] > 0])/len(self.log)
        return ptr

    def getPPT(self):
        ppt = sum([row[7]/row[2] for row in self.log]) / len(self.log)
        return ppt