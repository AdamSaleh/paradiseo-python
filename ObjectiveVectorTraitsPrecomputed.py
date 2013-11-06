# -*- coding: utf-8 -*-
import os, shutil, errno,math,sqlite3,csv,random
import logging
from datetime import datetime
from math import sqrt
from math import floor

logging.basicConfig(filename='evolve.log',level=logging.DEBUG)

entry_set = set()

def minimizing(i): #minimizing everything 
		return True
def maximizing(i):
		return False

def nObjectives():
	return 3

td =[{"min":1 , "max":51}, #fwdBufferSize
 {"min":1 , "max":30}, # maxMonitorNodes
 {"min":0.01 , "max":0.99}, # treshold
 {"min":1 , "max":99},] #min packets

def minimumBounds(i):
	return td[i]["min"]
def maximumBounds(i):
	return td[i]["max"]

 
def nParams():
	return 4

def minmax(num,min,max):
	if num > max:
		return max
	if num < min:
		return min
	return num

def minmaxi(num,i):
	return minmax(num,td[i]["min"],td[i]["max"])

def round_pareto(num):
	return float(math.floor(num*10000))/10000

NAME = "experiment-lab-1b"
def evaluate(fwdBufferSize,maxMonitorNodes,treshold,packets):
    db = sqlite3.connect(NAME+".db")
    fwdBufferSize = minmaxi(float(math.floor(fwdBufferSize)),0)
    maxMonitorNodes = minmaxi(float(math.floor(maxMonitorNodes)),1)
    treshold = minmaxi(float(math.floor(treshold*100))/100,2)
    packets = minmaxi(float(math.floor(packets)),3)
    entry_set.add((fwdBufferSize,maxMonitorNodes,treshold,packets))

    logging.info((fwdBufferSize,maxMonitorNodes,treshold,packets))

    cur = db.cursor()
    cur.execute("Select (bufferSize*16+maxMonitorNodes*8) as memory,fp, fn from precomputed where bufferSize = ? and maxMonitorNodes = ? and treshold = ? and minPackets  = ? ", (fwdBufferSize,maxMonitorNodes,treshold,packets))
    result = cur.fetchall();
    if len(result)>0:
      logging.info("Result: "+ str(result[0]))  
    return result[0]

def arg_dict(args,arg_numbers):
    d = {}
    lines = args.split("\n")
    for line in lines:
        vals = line.split(":")
        if len(vals)>1:
          if vals[0] in arg_numbers:
            d[vals[0]] = float(vals[1])
          else:
            d[vals[0]] = vals[1]
    return d;

def get_pareto_csv(fname):
    fpareto = open(fname) #NAME+"-pareto.csv")
    fparetostr = fpareto.read()
    fparetolines = fparetostr.split("\n")
    pareto = []
    for line in fparetolines:
        vals = line.split(',')
        if len(vals) > 1:
            pareto.append([round_pareto(float(vals[0])),round_pareto(float(vals[1])),round_pareto(float(vals[2]))])
    return pareto;


def better(p1,p2):
  onebetter = False
  for (i1,i2) in zip(p1,p2):
    if i2 < i1:
      return False
    if i1 < i2:
      onebetter = True
  return onebetter

def dominates(front,p):
  for i in front:
    if better(i,p):
      return True
  return False  

def nondominated(front):
  return filter(lambda p: not dominates(front,p),front)

def dominatedbit(p0,front,R):
  out = []
  for p1 in front:
    p3 = [max(i0,i1) for (i0,i1) in zip(p0,p1)]
    if p3!=p0 and not p3 in out:
      out.append(p3)
  return hv(nondominated(out),R)



def improves_last(p1,p2):
  for (i,j) in zip(p1,p2)[::-1]:
    if i < j:
      return -1;
    if i > j:
      return 1;
  return 0

def inclHV(p,R):
  return reduce(lambda x, y: x*y,
    [r-i for (i,r) in zip(p,R)])

def exclHV(p,front,R):
  volume = inclHV(p,R)
  dom = dominatedbit(p,front,R)
  return volume - dom

def hv(front,R):
  if front == []:
    return 0
  f = sorted(front,cmp=improves_last) 
  return exclHV(f[0],f[1:],R) + hv(f[1:],R)

def distanceindi(p1, p2,maximum):
    return max([max([(v2-v1)/m for (v1,v2,m)
        in zip(o1,o2,maximum)]) for (o1,o2) in zip(p1,p2)])

def average(xs):
    return float(sum(xs))/float(len(xs))

def ndistance(i1,i2,maximum):
    t = [abs((v2-v1))/m for (v1,v2,m)
        in zip(i1,i2,maximum)]
    return (reduce(lambda x,y:x*y,t))**(1.0/len(i1))

def distanceavg(o1, o2, maximum):
    return average(
        [min([ndistance(i1,i2,maximum)
            for i2 in o2])
                for i1 in o1])

def distance_aggregate(indi,nb,maximum):
    return sum([abs((i-n))/r for (i,n,r) in zip(indi,nb,maximum)])

def spacing(approximation,maximum):
    dist_indi = []
    for indi in approximation:
        neighbor_dist = [distance_aggregate(indi,nb,maximum)
            for nb in approximation if nb != indi]
        dist_indi.append(min(neighbor_dist))
    return sum(dist_indi)/len(dist_indi)

def dist(approximation,maximum):
    split = zip(*approximation)
    aggregate = 0
    for (objective,r) in zip(split,maximum):
        aggregate +=sum([abs(prev-next)/r
                        for (prev,next) in zip(
                           [prev for prev in objective[:-2]],
                           [nxt for nxt in objective[2:]])])
    return aggregate/len(split)


REFERENCE = [1032.0,0.4,1.0] # memory, fp, fn

def report(inp,rep):

    db = sqlite3.connect(NAME+"-results.db")
    cur = db.cursor()
    uuid = str(datetime.now()) 
    print "uuid:",uuid
    cur.execute('CREATE TABLE IF NOT EXISTS reportin (uuid VARCHAR(30),popSize REAL,maxGen REAL,mutEpsilon REAL,mutProb REAL,pMut Real,crossProb REAL,pCross REAL, pAlgo VARCHAR(10),evaluations INT,numberofresults INT,hypervolume REAL,paretodist REAL,avgparetodist REAL,distance REAL,spacing REAL)')


    cur.execute('CREATE TABLE IF NOT EXISTS reportres (uuid VARCHAR(30),bufferSize REAL,maxMonitorNodes REAL,treshold REAL,minPackets REAL,memory REAL,fp REAL,fn REAL)')
    print "inp:",inp
    print "rep:",rep

    arg_numbers = ["popSize","maxGen","mutEpsilon","pCross","crossProb","pMut","mutProb"]
    d = arg_dict(inp, arg_numbers)
    pareto = get_pareto_csv(NAME+"-pareto.csv")
    pareto_result = []

    lines2 = rep.split("\n")
    for line in lines2:
        vals = line.split()
        if len(vals) > 1:
            memory = round_pareto(int(vals[0]))
            fp = round_pareto(float(vals[1]))
            fn = round_pareto(float(vals[2]))

            fwdBufferSize = float(vals[4])
            maxMonitorNodes = float(vals[5])
            treshold = float(vals[6])
            packets = float(vals[7])
            pareto_result.append([memory,fp,fn])
            cur.execute('INSERT OR IGNORE INTO reportres (uuid,bufferSize,maxMonitorNodes,treshold,minPackets,memory,fp,fn) VALUES (?,?,?,?,?,?,?,?)',(uuid,fwdBufferSize,maxMonitorNodes,treshold,packets,memory,fp,fn))

    hypervolumeindi = hv(pareto_result,REFERENCE)
    print "hv:",hypervolumeindi
    distindi = distanceindi(pareto_result,pareto,REFERENCE)
    print "distindi:",distindi
    avgdist = distanceavg(pareto_result,pareto,REFERENCE)
    print "avgdist:",avgdist
    dis = dist(pareto_result,REFERENCE)
    print "dist:",dis
    space = spacing(pareto_result,REFERENCE)
    print "space:",space

    cur.execute('INSERT OR IGNORE INTO reportin (uuid, popSize, maxGen, mutEpsilon, mutProb, pMut, crossProb, pCross, pAlgo, evaluations, numberofresults, hypervolume, paretodist, avgparetodist, distance,spacing) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',(uuid,d["popSize"],d["maxGen"],d["mutEpsilon"],d["mutProb"],d["pMut"],d["crossProb"],d["pCross"],d["pAlgo"],len(entry_set),len(pareto_result),hypervolumeindi,distindi,avgdist,dis,space))


    db.commit()

def process(maxMonitoredNodes,bufferSize,treshold,minpackets):
    return True

def completed(maxMonitoredNodes,bufferSize,treshold,minpackets):
    return True

def collect(maxMonitoredNodes,bufferSize,treshold,minpackets):
    return ()
