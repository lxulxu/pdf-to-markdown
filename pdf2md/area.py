'''
Author: lxulxu
Date: 2022-11-17 16:32:27
LastEditors: lxulxu
LastEditTime: 2022-11-22 19:48:39
Description: 

Copyright (c) 2022 by lxulxu, All Rights Reserved. 
'''

import pandas
from fitz import Rect

LINE_RECT_EPS = 3.0

class Area():
  def __init__(self, area:dict) -> None:
    self.type_ = area['type']
    self.rect_ = Rect(area['bbox'])
    self.res_ = area['res']
    self.img_ = area['img'] if 'img' in area else None
    self.lines_ = []
    
  @property
  def is_table(self):
    return self.type_ == 'table'
  
  @property
  def is_figure(self):
    return self.type_ == 'figure'
  
  @property
  def is_header(self):
    return self.type_ == 'header'
  
  @property
  def is_title(self):
    return self.type_ == 'title'
  
  @property
  def is_reference(self):
    return self.type_ == 'reference'
  
  @property
  def is_footer(self):
    return self.type_ == 'footer'
  
  @property
  def is_text(self):
    return self.type_ == 'text'
  
  def is_arranged_vertivally(self) -> bool:
    for i in range(1, len(self.lines_)):
      if self.lines_[i]['rect'].y0 < self.lines_[i - 1]['rect'].y1:
        return False
    return True

  def extract_lines_from_table(self):
    html = self.res_['html']
    table = pandas.read_html(html)[0]    
    table_list = []
    for i in table.to_dict('records'):
      table_list += list(i.values())

    x0 = self.rect_.x0
    y0 = self.rect_.y0

    self.lines_ = []
    for bbox, line in zip(self.res_['cell_bbox'], table_list):
      line = {'rect':Rect(x0 + bbox[0], y0 + bbox[1],\
                          x0 + bbox[4], y0 + bbox[5]),
              'text':line}
      self.lines_.append(line)

  def extract_lines_from_text(self):
    self.lines_ = []
    texts = [i for i in self.res_ if 'text' in i and i['text'] != []]

    for i in texts:
      region = Rect(i['text_region'][0][0],
                    i['text_region'][0][1],
                    i['text_region'][2][0],
                    i['text_region'][2][1])
      if self.lines_ and\
         abs(region.y0 - self.lines_[-1]['rect'].y0) <= LINE_RECT_EPS and\
         abs(region.y1 - self.lines_[-1]['rect'].y1) <= LINE_RECT_EPS:
        #merge span in one line
        self.lines_[-1]['rect'] |= region
        self.lines_[-1]['text'] += ' ' + i['text']
      else:
        #new line
        line = {'rect':region,
                'text':i['text']}
        self.lines_.append(line)


  def parse_table(self):
    if not self.is_table:
      return
    html = self.res_['html']
    table = pandas.read_html(html)[0]
    if table.shape[1] == 1:#fix the error of recognizing text as a table with one column
      self.extract_lines_from_table()
      self.type_ = 'text'

  def parse_figure(self):
    if not self.is_figure:
      return
    self.extract_lines_from_text()
    if self.is_arranged_vertivally():#fix the error of recognizing text as a figure
      self.type_ = 'text'

  def parse(self):
    if self.is_table:
      self.parse_table()
    elif self.is_figure:
      self.parse_figure()
    else:
      self.extract_lines_from_text()
  
  def get_table_dict(self) -> dict:
    return {'type':self.type_,
            'rect':self.rect_,
            'html':self.res_['html']}
  
  def get_figure_dict(self) -> dict:
    return {'type':self.type_,
            'rect':self.rect_,
            'img':self.img_,
            'ext':'jpg',
            'lines':self.lines_}
  
  def get_title_dict(self) -> dict:
    return {'type':'title',
            'rect':self.rect_,
            'level': 1,
            'lines':self.lines_}
  
  def get_text_dict(self) -> dict:
    return {'type':self.type_,
            'rect':self.rect_,
            'level': -1,
            'lines':self.lines_}