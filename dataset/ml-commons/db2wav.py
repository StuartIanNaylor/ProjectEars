#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import glob
from shutil import which
import subprocess
import uuid
import sqlite3


def db2wav(table, source_dir='en/clips', dest_dir='./out', rate=16000, limit=4, database='ml-commons.db'):

  if not os.path.exists(source_dir):
    print("Source_dir " + source_dir + " does not exist")
    exit()

  if not os.path.exists(dest_dir):
    os.makedirs(dest_dir)

  if not os.path.exists(dest_dir + "/" + table):
    os.makedirs(dest_dir + "/" + table)
  else:
    print("Word dir " + table + " already exists")
    exit()
      
  if which('opusdec') == None:
    print("opusdec not installed sudo apt-get install opusdec")
    exit()
    
  dest_path = os.path.abspath(dest_dir + "/" + table)
   
  con = sqlite3.connect(database)
  cur = con.cursor()
  SQL = "SELECT * from \"" + table + "\""
  cur.execute(SQL)
  records = cur.fetchall()
  
  last_word = ""
  word_count = 0
  table_count = 0
  for row in records:
    if last_word != row[0]:
      last_word = row[0]
      word_count = 0
    if word_count < limit:
      source_path = os.path.abspath(source_dir + "/" + row[0] + "/" + row[1])
      bashCommand = "opusdec --quiet --rate " + str(rate) + " " + source_path + " " + dest_path + "/" + str(uuid.uuid4()) + ".wav"  
      process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
      output, error = process.communicate()
      if error == None:
        print(source_path, "Converted to " + dest_path + "/" + str(uuid.uuid4()) + ".wav")
      else:
        print(error)
      word_count += 1
      table_count += 1
  if 'row' not in locals():
    print(table + " returned no files")
    exit()
  print(str(table_count) + " total files converted")
  

  
def main_body():
  parser = argparse.ArgumentParser()
  parser.add_argument('--source_dir', type=str, default='en/clips', help='source dir location default=en/clips')
  parser.add_argument('--dest_dir', type=str, default='./out', help='dest dir for word dir default=out')
  parser.add_argument('--table', type=str, help='db table to convert')
  parser.add_argument('--rate', type=int, default=16000, help='sample rate to convert to default=16000')
  parser.add_argument('--limit', type=int, default=4, help='limit to x number of files default=-1')
  parser.add_argument('--database', type=str, default='ml-commons.db', help='database name default=ml-commons.db')
  args = parser.parse_args()

   
  
  db2wav(args.table, args.source_dir, args.dest_dir, args.rate, args.limit)

    
if __name__ == '__main__':
  main_body()
  
  
  

