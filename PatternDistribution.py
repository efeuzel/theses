# -*- coding: utf-8 -*-
"""
Created on Sat Jul 29 22:23:35 2017

PaternDistribution

@author: Efe
"""
import numpy
import itertools
import Engine
import Utils
import re


#represent timeseries with categorical attributes
def convertTimeseries(df):
    string = ''
        
    returns = numpy.diff([row[6] for row in df])         
    for index in range(0, len(returns)):
        if returns[index] >= 0:
            string = string + "u"
        else:
            string = string + "d"
    return string

#generate patterns of categorical attributes and calculate probabilities for each
def generateDistribution(string,patternLen, normalized = True):
    terms = []
    tmp = ''
#    for i in itertools.product(itertools.product('ud','Vv'), repeat = patternLen):
#    for i in itertools.product(itertools.product('udUD','V'), repeat = patternLen):
#        for ii in i:
#            tmp= tmp + ii[0]+ii[1]
#        terms.append(tmp)
#        tmp = ''     
    for i in itertools.product(itertools.product('ud'), repeat = patternLen):
        for ii in i:
            tmp= tmp + ii[0]
        terms.append(tmp)
        tmp = ''  
    distribution = dict()
    for t in terms:
        distribution[t] = countOverlapping(string,t)
    total = sum(distribution.values())
    if normalized:
        for key, value in distribution.items():
            distribution[key] = value / total
    return distribution

#Funtion to count overlapping ocuurences of substring in string. Built in fun. counts non overlapping
def countOverlapping(s, sub_s):
    return sum(1 for m in re.finditer('(?=%s)' % sub_s, s))

#re-calculate probabilities given part of the pattern has been observed
def distributionGivenFirstTerm(firstTerm, distribution):
    newDict = dict()
    ftLen = len(firstTerm)
    for key, value in distribution.items():
        if key.startswith(firstTerm):
            newDict[key[ftLen:]] = value
    total = sum(newDict.values())
    for key, value in newDict.items():
        if total != 0:
            newDict[key] = value / total  
        else:
            newDict[key] = 0  
    return newDict

def suggestTrade(string,distribution,patternLen):
    newDist =  distributionGivenFirstTerm(
            string[-patternLen+1:], distribution) #feed the last realized terms as fisrst terms to get suggestion
#    print(string[-termLen*(patternLen-1):])
#    print(newDist)
    buy = 0
    sell = 0
    for key, value in newDist.items():
        if key.startswith('u') or key.startswith('U'):
            buy = buy + value
        if key.startswith('d') or key.startswith('D'):
            sell = sell + value
    total = sum(newDist.values())
    if total != 0:
        buy = buy / total  
    else:
        buy = 0  

    if total != 0:
        sell = sell / total  
    else:
        sell = 0

    if (buy>=sell):
        #print("Price increase with probability:",buy)
        return 1 
    else:
        #print("Price decrease with probability:",sell)
        return -1

    
#df = Utils.readMT4data("USDTRY-1440-HLOC-lag0.csv")
#string = convertTimeseries(df)
#distribution = generateDistribution(string)
#sug = suggestTrade(string,distribution)

def run(data,histSize,runPeriods,patternLen,maxHistLen):
    e = Engine.Engine(data,histSize,maxHistLen)
    counter = 0
    while e.hasNext == True and counter < runPeriods:
        string = convertTimeseries(e.hist)
        distribution = generateDistribution(string,patternLen)
        sug = suggestTrade(string,distribution,patternLen)
#        sug = random.sample([-1,1],1)[0]
#        sug = 1
        e.openPos(side = sug, comment=string[-patternLen+1:])
        #e.next() open and close pos. on the same day
        e.closePos()
        e.next()
        counter = counter + 1
    return e, distribution, string

def runBuy(data,histSize,maxHistLen, runPeriods=5000):
    e = Engine.Engine(data,histSize,maxHistLen)
    counter = 0
    while e.hasNext == True and counter < runPeriods:
        sug = 1
        e.openPos(side = sug, comment="")
        e.next()
        e.closePos()
        counter = counter + 1
    ptr = e.getPTR()
    ppt = e.getPPT()
    print("Buy Only: History: " + "{0:3.0f}".format(histSize) +
      " PTR: " + "{0:.3f}".format(ptr)+
      " PPT: %" + "{0: .2f}".format(ppt*100))
    return e

def getSuggestedTrade(data, histSize, patternLen):
    e = Engine.Engine(data,histSize,histSize)
    while e.hasNext == True:
        e.next()
    string = convertTimeseries(e.hist)
    distribution = generateDistribution(string,patternLen)
    sug = suggestTrade(string,distribution,patternLen)
    e.openPos(side = sug, comment=string[-patternLen+1:])
    Utils.printlog(e.log)
    return string

#threedee = plt.figure().gca(projection='3d')
#threedee.scatter(results.histSize,results.patternLen,results.ptr)

#e = test("USDTRY-1440-HLOC-lag0-2017.08.08.csv",-1000,histSize = 200, testSize = 10, patternLen = 4)
#
#print(e.log)
#print(sum(e.log.pnl))
#print("Profitable trades % " + str(e.log[e.log.pnl>0].shape[0]/e.log.shape[0]))
#print("Buy ratio: " +  str(e.log[e.log.side == 1].sum().side/e.log.shape[0]))
#print("Profit per trade: "+ str(e.log.pnl.sum()/e.log.shape[0]))
#plt.plot(e.log.pnl.cumsum())    
