# -*- coding: utf-8 -*-
"""
Created on Sat Dec  9 14:44:13 2017

@author: Efe
"""

#load results

import pickle

with open('C:\\Users\\max\\Google Drive\\Thesis\\Content\\ipython notebooks\\result.pickle', 'rb') as f:
    # The protocol version used is detected automatically, so we do not
    # have to specify it.
    result = pickle.load(f)

mylist = [i[5][0].log for i in result]

with open("C:\\Users\\max\\Google Drive\\Thesis\\Content\\ipython notebooks\\logs.txt", 'w') as myfile:
    for l in mylist:
        for ll in l:
            print(ll, file = myfile)
        print('', file = myfile)
    