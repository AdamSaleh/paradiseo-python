import os, shutil, errno,math,sqlite3,csv,random
import logging
from datetime import datetime
from math import sqrt
from math import floor
import tempfile
import urllib
import zipfile
import mechanize

def login():
  br = mechanize.Browser()
  br.open("http://centaur.fi.muni.cz:8000/boinc/labak_management/") 
  br.select_form(nr=0)
  br.form['login'] = 'xsaleh'
  br.form['password'] = '*cygnusolor*'
  br.submit()
  return br
  
def logout(br):
  br.open("http://centaur.fi.muni.cz:8000/boinc/labak_management/auth/logout")
  br.select_form(nr=0)
  br.submit()

def create_wu(br,name,appid,config_content,command_line,result_file):
  if inprogress(br,name):
        print name, " already exists"
        return True

  retry = 5
  while retry > 0:
      print "Trying to create ", name
      try:
        br.open("http://centaur.fi.muni.cz:8000/boinc/labak_management/work/create")
      	br.select_form(nr=0)
      	br.form["step0[appid]"] = [appid] # select wsn-evo app id
      	br.form["step0[name]"] = name
      	br.submit()

      	tf = tempfile.NamedTemporaryFile(delete = False)
      	tf.write(config_content)
      	tf.close()

      	br.select_form(nr=0)
      	br.form.add_file(file_object = open(tf.name),content_type='text/plain',filename = tf.name,id="infiles_upload-0")
      	br.submit() # 7

      	br.select_form(nr=0)

      	br.submit("next-step") # 5 no transform

      	br.select_form(nr=0)
      	br.form["command_line"] = command_line
      	br.form["outfiles"] = result_file
      	br.submit() # 9
      	return True
      except:
        print "Unexpected error:", sys.exc_info()[0]
        print "retrying"
        retry-=1

def inprogress(br,name):
    br.open("http://centaur.fi.muni.cz:8000/boinc/labak_management/result/list")
    br.select_form(nr=0)
    br.form["name"] = name
    br.submit() # 8
    out = False
    for i in br.links():
        if name in i.text:
                out = True
    return out

def wu_completed(br,name):
    br.open("http://centaur.fi.muni.cz:8000/boinc/labak_management/result/list")
    br.select_form(nr=0)
    br.form["name"] = name
    br.submit() # 8
    out = False
    for i in br.links():
        if i.text == "results.zip":
             if (name in i.url):
                out = True
    return out

def wu_collect(br,name):
    br.open("http://centaur.fi.muni.cz:8000/boinc/labak_management/result/list")
    br.select_form(nr=0)
    br.form["name"] = name
    br.submit() # 8
    url = ""
    for i in br.links():
        if i.text == "results.zip":
             if (name in i.url):
                url = i.url
    if len(url) > 0:
        tf = tempfile.NamedTemporaryFile(delete=False)
        urllib.urlretrieve("http://centaur.fi.muni.cz:8000"+url, tf.name)
        return tf
    return ""
