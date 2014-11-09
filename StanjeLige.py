from Liga import *
from os import path
import csv
stanjeLigeA={}
stanjeLigeB={}
stanjeLigeC={}
with open('zacetek.txt',encoding='utf-8') as f:
    k=0
    for line in f:
        if k!=0:                
            a=line.split(';')
            ime=a[1]
            priimek=a[0]
            klub=a[2]
            kat=a[3]
            tocke=round(int(a[4][:-1]) + (int(a[4][:-1])-900)/4)
            if priimek=='Piltaver' and ime=='Jaka':
                tocke=1250
            elif priimek=='Hribar' and ime =='Andraž':
                tocke=1400
            elif ime=='Peter' and priimek=='Tušar':
                tocke=1150  
            if kat=='ELITE':
                stanjeLigeA[(sumniki(ime),sumniki(priimek))]={'ime':ime,'priimek':priimek,'klub':klub,0:[0,tocke,False]}
            elif kat=='B':
                stanjeLigeB[(sumniki(ime),sumniki(priimek))]={'ime':ime,'priimek':priimek,'klub':klub,0:[0,tocke,False]}
            elif kat=='C':
                stanjeLigeC[(sumniki(ime),sumniki(priimek))]={'ime':ime,'priimek':priimek,'klub':klub,0:[0,tocke,False]}
        k=1

#print(stanjeLigeA)
st_tekem=0
IP = 1
for st_lige in range(1,20):
    if st_lige == 17:
        IP = 1.15
    if path.isfile('./Rezultati/olp'+str(st_lige)+'.csv'):
        c=rezultati(st_lige,{'ELITE':stanjeLigeA,'B':stanjeLigeB,'C':stanjeLigeC})
        stanjeLigeA=izracunLigeA(c['ELITE'],st_lige,stanjeLigeA, IP)
        st_tekem+=1
        #mankajociKlubi(stanjeLigeA)
        #mankajociKlubi(stanjeLigeB)
        #mankajociKlubi(stanjeLigeC)
        stanjeLige={'ELITE':stanjeLigeA,'B':stanjeLigeB,'C':stanjeLigeC}
        vCsv(stanjeLige,st_tekem)

if path.isfile('./ResnaStanja/StanjeLige'+str(st_tekem)+'.csv'):
    g=open('OLP_2015.csv','w+',encoding='utf-8')
    with open('./ResnaStanja/StanjeLige'+str(st_tekem)+'.csv','r+',encoding='utf-8') as f:
        for i in f.readlines():
            g.write(i)
    g.close()
