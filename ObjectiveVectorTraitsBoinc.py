# -*- coding: utf-8 -*-
import os, shutil, errno,math,sqlite3,csv,random
import logging
from datetime import datetime
from math import sqrt
from math import floor
import tempfile
import urllib
import zipfile

from boincmechanized import *

logging.basicConfig(filename='evolve.log',level=logging.DEBUG)

entry_set = set()

def nObjectives():
  return 3

td =[{"min":1 , "max":100}, #fwdBufferSize
 {"min":1 , "max":30}, # maxMonitorNodes
 {"min":0.01 , "max":0.99}, # treshold
 {"min":1 , "max":10},] #min packets

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

def report(inp,rep):
    print rep

def minmax(num,min,max):
  if num > max:
    return max
  if num < min:
    return min
  return num

def minmaxi(num,i):
  return minmax(num,td[i]["min"],td[i]["max"])

def create_name(maxMonitoredNodes,bufferSize,treshold,minpackets):
    return "wsnevo-testboinc10-mmn-"+str(maxMonitoredNodes) + "bfs-" + str(bufferSize) +"z"
  
def process(br,maxMonitoredNodes,bufferSize,treshold,minpackets):
  logging.info("Processing: "+ str((maxMonitoredNodes,bufferSize,treshold,minpackets)))  
  bufferSize = minmaxi(float(math.floor(bufferSize)),0)
  maxMonitoredNodes = minmaxi(float(math.floor(maxMonitoredNodes)),1)
  treshold = minmaxi(float(math.floor(treshold*100))/100,2)
  minpackets = minmaxi(float(math.floor(minpackets)),3)

  name = create_name(maxMonitoredNodes,bufferSize,treshold,minpackets)

  tf = tempfile.NamedTemporaryFile(delete = False)
  config_content = """[Config TestLab]
sim-time-limit = 3600s
**.appl.headerLength = 1B                 
**.node[*].nic.ids.fwdBufferSize=%s
**.node[*].nic.ids.fwdMinPacketsReceived = %s
**.node[*].nic.ids.maxMonitoredNodes=%s
"""%(str(bufferSize),str(minpackets),str(maxMonitoredNodes))

  command_line = "-individual FILE_0 --cmdenv-config-name TestLab"
  result_file = "results.zip"
  
  return create_wu(br,name,"10",config_content,command_line,result_file)

def completed(br,maxMonitoredNodes,bufferSize,treshold,minpackets):
    bufferSize = minmaxi(float(math.floor(bufferSize)),0)
    maxMonitoredNodes = minmaxi(float(math.floor(maxMonitoredNodes)),1)
    treshold = minmaxi(float(math.floor(treshold*100))/100,2)
    minpackets = minmaxi(float(math.floor(minpackets)),3)
    logging.info("Testing: "+ str((maxMonitoredNodes,bufferSize,treshold,minpackets))) 
    
    name = create_name(maxMonitoredNodes,bufferSize,treshold,minpackets)
    return wu_completed(br, name)
        
def collect(br,maxMonitoredNodes,bufferSize,treshold,minpackets):
    logging.info("Collecting: "+ str((maxMonitoredNodes,bufferSize,treshold,minpackets))) 
    bufferSize = minmaxi(float(math.floor(bufferSize)),0)
    maxMonitoredNodes = minmaxi(float(math.floor(maxMonitoredNodes)),1)
    treshold = minmaxi(float(math.floor(treshold*100))/100,2)
    minpackets = minmaxi(float(math.floor(minpackets)),3)
    name = create_name(maxMonitoredNodes,bufferSize,treshold,minpackets)
    
    print "collecting:",name
    tf = wu_collect(br,name)
    
    td =  tempfile.mkdtemp()
    sourceZip = zipfile.ZipFile(tf.name, 'r')
    sourceZip.extractall(td)
    db = sqlite3.connect(td+"/resultdb")
    cur = db.cursor()
    cur.execute("select fp,fn from precomputed where treshold = ? and minPackets = ?",(treshold,minpackets))
    result = cur.fetchall()
    return [(maxMonitoredNodes*8+bufferSize*16),result[0][0],result[0][1]]

def popeval(pop):
  br = login()
  for i in pop:
    print "processing:", i
    process(br,i[0],i[1],i[2],i[3])
  s = list(pop)
  while len(s)>0:
    print "round"
    for i in s:
      print "checking:", i
      if completed(br,i[0],i[1],i[2],i[3]):
        print "done:",i
        s.remove(i)
  print "collecting"
  out =[]      
  for i in pop:
     out.append(collect(br,i[0],i[1],i[2],i[3]))
  logout(br)
  return out

