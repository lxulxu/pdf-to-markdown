'''
Author: lxulxu
Date: 2022-09-13 10:03:52
LastEditors: lxulxu
LastEditTime: 2023-12-18 18:55:41
Description: 

Copyright (c) 2022 by lxulxu, All Rights Reserved. 
'''

import argparse
import os

from pdf2md.parser import parse_file
from pdf2md.writer import Writer

def parse_pdf(filename:str):
  blocks = parse_file(filename)
  writer = Writer(filename, blocks)
  writer.write_markdown()

def get_parser():
  parser = argparse.ArgumentParser()
  parser.add_argument('-f', '--file', help='filename or dirname', required=True)
  args = parser.parse_args()
  return args


def start(args):
  if not args.file or not os.path.exists(args.file):
    raise Exception('file or folder does not exist')
    
  if os.path.isfile(args.file):
    if not args.file.endswith('.pdf'):
      raise Exception('not a pdf file')
    parse_pdf(args.file)

  elif os.path.isdir(args.file):
    filenames = [os.path.join(args.file, i) for i in os.listdir(args.file) if i.endswith('.pdf')]
    for filename in filenames:
      parse_pdf(filename)

if __name__ == '__main__':
    args = get_parser()
    try:
      start(args)
    except Exception as e:
      print(e)