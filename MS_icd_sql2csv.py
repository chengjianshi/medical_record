#!/usr/bin/env python
# coding: utf-8

import sqlite3
import pandas as pd
import numpy as np
import glob
from scipy.stats import chi2
import time
import sys

sys.setrecursionlimit(10000)

conn = sqlite3.connect('/project2/arzhetsky/ylong/MarketScan/DX/MSDX_day_20180922_dx.db')

c = conn.cursor()
cur = conn.cursor()

conn2 = sqlite3.connect('/project2/arzhetsky/ylong/MarketScan/DX/MSDX_day_20180922_DEMO.db')
c2 = conn2.cursor()

ICD = pd.read_csv('2018_I10gem.txt',sep=' ')
col = ICD.columns

Mapp = ICD[[col[0],col[1]]]

icd10 = pd.Series.tolist(Mapp.iloc[:,0])
icd9  = pd.Series.tolist(Mapp.iloc[:,1])

Mapp2 = {'icd9':[]}

for ii in icd9:
    if 'E' in ii:
        if ii[:4] not in Mapp2['icd9']:
            Mapp2['icd9'].append(ii[:4])
    elif ii[:3] not in Mapp2['icd9']:
        Mapp2['icd9'].append(ii[:3])

Mapp2['icd9'].sort()
Mapp2['icd9'].append('Total')

Diabetes = ['250','E08','E09','E10','E11','E13','E13']

INDEX = []

class Association:
    
    global Mapp2
    global icd9
    global icd10
    global Diabetes
    global INDEX
    
    def __init__(self,threshold,age_range):
        """
        epoch: number of epochs
        N: number of patients
        P: at least fixed proportion of 427* patients 
        """
        global Index
        
        self.Matrix = np.zeros((len(INDEX),4))
        self.th = threshold
        self.age_range = age_range
        
    def is_number(self,n):
        
        try:
            float(n)
            return True
        except:
            return False
        
    def update_index(self,dx):
        
        global INDEX
        
        try:
            float(dx)
            dx_int = dx[:dx.index('.')]
                
            if dx in INDEX:
                return INDEX.index(dx)
                
            elif dx not in INDEX:
                
                INDEX.append(dx)
                self.Matrix = np.concatenate((self.Matrix,np.zeros((1,4))),axis=0)
                return INDEX.index(dx)
            else:
                return False
            
        except:
            
            return False
        
    def Gate(self,code):
        
        global INDEX
        
        if self.is_number(code):
            return self.update_index(code)
        
        elif 'E' in code:
            code_save = code[:code.index('.')]
            if len(code_save) == 3:
                try:
                    code = code.replace('.','')
                    idx = icd10.index(code)
                    newcode = icd9[idx]
                    code = newcode[:3]+'.'+newcode[3:]
                    return self.update_index(code)
                except:
                    return False
            else:
                return False

        elif 'V' in code:
            
            if 'A' in code:
                try:
                    code = code.replace('.','')
                    idx = icd10.index(code)
                    newcode = icd9[idx]
                    code = newcode[:3]+'.'+newcode[3:]
                    return self.update_index(code)
                except:
                    return False
            else:
                return self.update_index(code)
                
        else:
            try:
                code = code.replace('.','')
                idx = icd10.index(code)
                newcode = icd9[idx]
                code = newcode[:3]+'.'+newcode[3:]
                return self.update_index(code)
            except:
                return False
           
    
    def is_Diabetes(self,distinct_dx):
        
        a = list(map(lambda f: f[0][:f[0].index('.')] in Diabetes, distinct_dx))
        b = (True in a)
        return b
    
    def MatBuilder(self):
        
        general = c.execute("SELECT DISTINCT(studyid) from dx WHERE age between "+self.age_range+";")        
        count = np.zeros((1,4))
        
        print('Group | Studyid | Gender | Age | DX | Ratio | Total \n')
        
        while True:
            
            """
            Sampling
            """
            
            idn = str(general.fetchone()[0])
            if len(idn) == 0:
                print('No Case found anymore, done!')
                break

            distinctdi = cur.execute("SELECT distinct(dx) from dx where studyid ='"+idn+"';").fetchall()

            if self.is_Diabetes(distinctdi) == True:
                k = 0
            else:
                k = 1
            
            info = cur.execute("SELECT dx,age from dx where studyid ='"+idn+"' and age between 18 and 65;").fetchall()
            gender = c2.execute("SELECT gender from DEMO where studyid='"+idn.zfill(11)+"';").fetchone()[0]
            
            if len(gender) == 0:
                continue
            elif gender == 'F':
                kk = k + 2
            else:
                kk = k
                
            count[0,kk] += 1
            
            mem = set() 
            for di in info:
                
                icdi,agei = di
                
                idx = self.Gate(icdi)
                if idx == False:
                    continue
                if idx not in mem:
                    mem.add(idx)
                    self.Matrix[idx,kk] += 1
                    tot = np.sum(count)
                    print('%.0f | %s | %s | %s | %s | %.0f/%.0f | %.0f \r ' %(kk,idn,gender,self.age_range,icdi,self.Matrix[idx,kk],count[0,kk],tot))
                    
            if np.sum(count)>self.th:
                break 
                
        self.Matrix = np.concatenate((self.Matrix,np.zeros((1,4))),axis=0)
        self.Matrix[-1,:] = count
        
        INDEX.append('Total')
        
        df = {'Disease':INDEX,
            'Case-Male':self.Matrix[:,0],
            'Control-Male':self.Matrix[:,1],
            'Case-Female':self.Matrix[:,2],
            'Control-Female':self.Matrix[:,3]
            }
        
        df = pd.DataFrame.from_dict(df,orient='columns')
        file_name = self.age_range.replace(' ','_')+'.csv'
        df.to_csv(file_name)
            
        return print('Done!')

age_range = ['34 AND 41','50 AND 57']

for i in range(2):
        test = Association(5e6,age_range[i])
        test.MatBuilder()
