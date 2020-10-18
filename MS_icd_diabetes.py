import sqlite3
import numpy as np
import pandas as pd
import glob as glob
from Patient import Patient

DB = sqlite3.connect("/project2/arzhetsky/ylong/MarketScan/DX/MSDX_day_20200116_dx.db")
idCursor = DB.cursor()
dxCursor = DB.cursor()
#panc = {
#        'K85.9':'acute pancreatitis',
#        'K86.1':'other pancreatities'
#    }
diab = ['E11','E10']

with open('timeStamp.log','x') as f:
	id_ = idCursor.execute("SELECT distinct(studyid) from dx where dx like 'K85%' or dx like '577.0%';")
	th_ = 1e5;
	tot = 0;
	f.write('%s|%s|%s|%s|%s|%s\n' %('STUDYID','SEX','YOB','day_of_AP','day_of_diab','diab_type'))
	while tot<th_:
		studyid = id_.fetchone()[0]
		patient = Patient(str(studyid), dxCursor, abb = True)
		dx = patient.fetchDX()
		sex, yob = patient.fetchDemo();
		timestamp = 0;
		for dxi,day in dx:
			if dxi == 'K85' and timestamp == 0:
				timestamp = day
			if dxi in diab:
				if timestamp == 0:
					break
				print('%s|%s|%s|%s|%s|%s\n' %(str(studyid),sex,str(yob),str(timestamp),str(day),dxi))
				f.write('%s|%s|%s|%s|%s|%s\n' %(str(studyid),sex,str(yob),str(timestamp),str(day),dxi))
		print('Process: %.0f/%.0f' %(tot,th_), end='\r')
		tot += 1
