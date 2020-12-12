# -*- coding: utf-8 -*-
"""
Created on Wed Aug 23 19:28:10 2017

@author: Efe
"""
import pandas as pd
import time
import pickle

import Utils 
import PatternDistribution as pattern

def evaluatePerfomance(cvSet,histRange,patternLenRange):
    perfomances = pd.DataFrame();
    for histSize in histRange:
        for patternLen in patternLenRange:
            perf = cvSet.loc[cvSet.patternLen==patternLen].loc[cvSet.histSize==histSize].ptr.mean()
            perfomances = perfomances.append(pd.DataFrame([[histSize, patternLen, perf]],columns = ["histSize", "patternLen", "perf"]))
    return perfomances

def evalPatternDistribution(data, histRange, patternLenRange):
    result = pd.DataFrame()
    for histSize in histRange:
        for patternLen in patternLenRange:
            e, distribution, string, ptr, ppt = runPatternDistribution(data,
                histSize, patternLen, 5000, max(histRange), printStats = True )
            new_result = pd.DataFrame([[histSize,patternLen,ptr,ppt,e.log]],columns = ["histSize","patternLen","ptr","ppt","log"])
            result = result.append(new_result)
    result.reset_index(drop=True, inplace=True)
    return result

def runPatternDistribution(data,histSize,patternLen,runPeriods,maxHistLen,printStats = False):
    e, distribution, string = pattern.run(data, histSize, runPeriods, patternLen, maxHistLen )
    ptr = e.getPTR()
    ppt = e.getPPT()
    if printStats:   
        print("History: " + "{0:3.0f}".format(histSize) +
          " Pattern length: " + str(patternLen)+ 
          " PTR: " + "{0:.3f}".format(ptr)+
          " PPT: %" + "{0: .2f}".format(ppt*100))
    return e, distribution, string, ptr, ppt

def testBuyOnly(data,histRange):
    perfomances = pd.DataFrame()
    for histSize in histRange:
        eBuy = pattern.runBuy(data,histSize,max(histRange))
        perfomances = perfomances.append(pd.DataFrame([[histSize, 0, eBuy.getPTR()]],columns = ["histSize", "patternLen", "perf"]))
    Utils.plotPerfHeatmap(perfomances)
    return eBuy

def getBestModel(cvSet):
    cvSet = cvSet.reindex(index=cvSet.index[::-1]) #reverse cvSet to get large hist and p length in case of equality
    return cvSet.loc[cvSet['ptr'].idxmax()]

#datafile  = "C:\\Users\\max\\Google Drive\\Thesis\\Data\\Investing.csv"
#data = Utils.readInvData(datafile)
histRange = (50, 100, 150, 200, 250)
patternLenRange = (3, 4, 5, 6, 7)

datafile  = "C:\\Users\\max\\Google Drive\\Thesis\\USDTRY-1440-HLOC-lag0-2017.12.08.csv"
filedata = Utils.readMT4data(datafile, 50000)

runPeriods = 20
result = []
counter = 0
#len(filedata)-runPeriods-1
for i in range(1, len(filedata)-(max(histRange)+runPeriods) , max(histRange)+runPeriods):
    counter += 1
    alldata = filedata[:-i]
    alldata = alldata [-(max(histRange)+2*runPeriods):]  #262
    data = alldata[:-runPeriods]
    valData = alldata[-(max(histRange)+runPeriods):]
    
    cvSet= evalPatternDistribution(data,histRange, patternLenRange)
    modelPerf= evaluatePerfomance(cvSet,histRange,patternLenRange)
    modelPerf.columns = ['Örüntü Uzunluğu', 'Geçmiş Veri Periyot Sayısı', 'Performans']
    plt = Utils.plotPerfHeatmap(modelPerf,i,counter)
    #eBuy = testBuyOnly(data,histRange)
    
    print("\nvalidation\n")
    #
    #valcvSet= evalPatternDistribution(valData,histRange, patternLenRange)
    #valmodelPerf= evaluatePerfomance(valcvSet,histRange,patternLenRange)
    #Utils.plotPerfHeatmap(valmodelPerf)
    #valeBuy = testBuyOnly(valData,histRange)
    best =  getBestModel(cvSet)
    bestValResult = runPatternDistribution(valData,best.histSize,best.patternLen,5000,max(histRange),printStats=True)
    time.sleep(1)
    result.append([data, cvSet, modelPerf, valData, best, bestValResult])
    # 0 data, 1 cvSet, 2 modelPerf, 3 valData, 4 best, 5 bestValResult
    #bestValResult 0 e, 1 distribution, 2 string, 3 ptr, 4 ppt
with open('C:\\Users\\max\\Google Drive\\Thesis\\Content\\ipython notebooks\\result.pickle', 'wb') as f:
    # Pickle the 'data' dictionary using the highest protocol available.
    pickle.dump(result, f, pickle.HIGHEST_PROTOCOL)

