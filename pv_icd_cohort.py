import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from scipy.stats import chi2
import glob
from scipy.stats import norm
from scipy.stats import fisher_exact

def contigency_table(df,i):
    
    """
    row - Di/NoDi
    Col - Arr/NoArr
    """
    
    tot = df.iloc[-1,:].tolist()
    tot = np.array(tot)
    dx = df.iloc[i,0]
    di = df.iloc[i,:].tolist()
    di = np.array(di)
    table = np.zeros((2,4))
    table[0,:] = di
    table[1,:] = tot - di
    
    return table,dx


def pvalue(table):
    
    Sum = np.sum(table)
    colsum = np.sum(table,axis=0)
    rowsum = np.sum(table,axis=1)
    
    phat = table[0,1]/colsum[1]
    err = 1.96*(np.sqrt(phat*(1-phat)/colsum[1]))
    
    """
    Null Hypothesis: thetahat = phat
    """
    
    muhat = colsum[0]*phat
    sigmahat = np.sqrt(colsum[0]*phat*(1-phat))
    
    pvalue = fisher_exact(table)[1]
    
    return pvalue,phat,err


file = glob.glob('/home/chengjian/scratch-midway2/project/Diabetes/AgeGroup/*_AND_*.csv')
file.sort()

MAP_Count = {
    'Disease':[],
            }
    
for i in range(2,len(file)):
    print('Starting file: %s' %file[i])
    df = pd.read_csv(file[i])
    df.set_index('Disease',drop=True,inplace=True)
    df = df.drop(['Unnamed: 0'],axis=1)
    print('Number of Dieases: %.0f' %len(df))
    
    mapp = df.index.tolist()
    
    DB = {'Disease':[],
          'P-value(M)':[],
          'Phat(M)':[],
          'Err(M)':[],
          'P-value(F)':[],
          'Phat(F)':[],
          'Err(F)':[]
         }
    
    for di in range(len(mapp)-1):
        
        if mapp[di] not in MAP_Count['Disease']:
            MAP_Count['Disease'].append(mapp[di])
    
        print(di,end='\r')
        tablei,dx = contigency_table(df,di)
    
        M = tablei[:,:2]
        F = tablei[:,2:]
            
        p1,ph1,er1 = pvalue(M)
        p2,ph2,er2 = pvalue(F)
        
        DB['Disease'].append(mapp[di])
        DB['P-value(M)'].append(p1)
        DB['P-value(F)'].append(p2)
        DB['Phat(M)'].append(ph1)
        DB['Phat(F)'].append(ph2)
        DB['Err(M)'].append(er1)
        DB['Err(F)'].append(er2)
        
    file_name = str(i)+'_PValue'+'.csv'
    save = pd.DataFrame.from_dict(DB,orient='columns')
    save.to_csv(file_name)

with open('save_index.txt','a') as f:
    for di in MAP_Count['Disease']:
        f.write(di+'\n')
        
    f.close()


