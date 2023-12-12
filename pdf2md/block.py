
from __future__ import annotations

import os
import re

import PIL
import pandas as pd
import Levenshtein as lev
from fitz import Rect
from mdutils.tools.Header import Header
from mdutils.tools.Image import Image

IMAGE_FOLDER = 'images'
OVERLAP_ERR = 5.0


class Line():
  def __init__(self, line:dict) -> None:
      self.rect_ = line['rect']
      self.text_ = line['text'].strip('\n')




class Block():
  def __init__(self, block:dict) -> None:
    self.type_ = block['type']
    self.rect_ = block['rect']

  @property
  def is_paragraph(self):
    return self.type_ != 'figure' and self.type_ != 'table'
  
  @property
  def is_figure(self):
    return self.type_ == 'figure'
  
  @property
  def is_table(self):
    return self.type_ == 'table'

  def close_to(self, block:Block) -> bool:
    return abs(self.rect_.x0 - block.rect_.x0) <= OVERLAP_ERR and\
           abs(self.rect_.y0 - block.rect_.y0) <= OVERLAP_ERR and\
           abs(self.rect_.x1 - block.rect_.x1) <= OVERLAP_ERR and\
           abs(self.rect_.y1 - block.rect_.y1) <= OVERLAP_ERR
    
  
  

class FigureBlock(Block):
  def __init__(self, block: dict) -> None:
    super().__init__(block)
    self.img_ = block['img']
    self.ext_ = block['ext']
    self.lines_ = [Line(line) for line in block['lines']]

  @property
  def text(self):
    return '\n'.join([i.text_ for i in self.lines_])
 
  def save_image(self, root_dir:str, index:int) -> str:
    '''
    description: save image
    param {str} root_dir: markdown file dir
    param {int} index: index of images in document
    return {str}: image filepath
    '''
    image_dir = os.path.join(root_dir, IMAGE_FOLDER)
    if not os.path.exists(image_dir):
      os.makedirs(image_dir)

    basename = str(index) + '.' + self.ext_
    filename = os.path.join(image_dir, basename)
    img = PIL.Image.fromarray(self.img_)
    img.save(filename)
    return os.path.join('.', IMAGE_FOLDER, basename)

  def gen_image_syntax(self, root_dir:str, index:int) -> str:
    '''
    description: generate image markdown syntax
    param {str} root_dir: markdown file dir
    param {int} index: index of images in document
    return {str}:image markdown syntax
    '''
    filename = self.save_image(root_dir, index)
    syntax = Image.new_inline_image(filename, filename) + '\n'
    syntax += purify(self.text) + '\n'
    return syntax

def is_header_similar(df1, df2, similarity_threshold=0.7):
  for col1, col2 in zip(df1.columns, df2.columns):
    similarity = lev.ratio(str(col1), str(col2))
    if similarity < similarity_threshold:
        return False

  return True

def are_coordinates_sequential(rect1, rect2, threshold=20):
    return abs(rect1.x0 - rect2.x0) <= threshold and abs(rect1.x1 - rect2.x1) <= threshold

def is_same_table_continued(table1, table2):
  df1 = pd.read_html(table1.html_, header=0)[0]
  df2 = pd.read_html(table2.html_, header=0)[0]

  if df1 is None or df2 is None or len(df1.columns) != len(df2.columns):
      return False

  return are_coordinates_sequential(table1.rect_, table2.rect_)

def merge_html_tables(html1, html2):
  df1 = pd.read_html(html1, header=0)[0]
  df2 = pd.read_html(html2, header=0)[0]

  if not is_header_similar(df1, df2):
      df2 = pd.read_html(html2, header=None)[0]

  df2.columns = df1.columns

  return pd.concat([df1, df2], ignore_index=True).to_html(index=False)

def update_coordinates(rect1, rect2):
  x0 = min(rect1.x0, rect2.x0)
  y0 = min(rect1.y0, rect2.y0)
  x1 = max(rect1.x1, rect2.x1)
  y1 = max(rect1.y1, rect2.y1)

  return Rect(x0, y0, x1, y1)
  
class TabelBlock(Block):
  def __init__(self, block):
    super().__init__(block)
    self.html_ = block['html']

  def merge_with(self, other_block):
    self.html_ = merge_html_tables(self.html_, other_block.html_)
    self.rect_ = update_coordinates(self.rect_, other_block.rect_)

  def gen_table_syntax(self) -> str:
    df_list = pd.read_html(self.html_, header=0)
    for df in df_list:
      df.fillna('', inplace=True)
      df.columns = ['' if 'Unnamed:' in col else col for col in df.columns]
    return df_list[0].to_markdown(index=False) + '\n'
  


class TextBlock(Block):
  def __init__(self, block):
    super().__init__(block)
    self.lines_ = [Line(line) for line in block['lines']]
    self.level_ = block['level']

  @property
  def text(self):
    return '\n'.join([i.text_ for i in self.lines_])
  
  def gen_paragraph_syntax(self, has_footer:bool) -> str:
    '''
    description: generate paragraph markdown syntax
    param {bool} has_footer: whether to write footer or not
    return {str}: paragraph markdown syntax
    '''
    syntax = ''

    if self.type_ == 'title':
      title = ' '.join([i.text_ for i in self.lines_])
      syntax = Header.choose_header(level=self.level_, title=title)

    elif self.type_ == 'footer' and has_footer:
      syntax = self.text
      
    else:
      syntax = purify(self.text) + '\n'

    return syntax
  

def purify(text:str) -> str:
  '''
  description: substitute special character
  param {str} text
  return {str}
  '''
  text = re.sub(r'([\\`\*_#\|>\-\$\+])', r'\\\1', text)
  text = re.sub(r'(\d+)\.', r'\1\\.', text)
  return text