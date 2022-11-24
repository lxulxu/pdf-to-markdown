
from __future__ import annotations

import os
import re

import PIL
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

  

class TabelBlock(Block):
  def __init__(self, block):
    super().__init__(block)
    self.html_ = block['html']

  def gen_table_syntax(self) -> str:
    table = re.match(r'.*(<table>.*?</table>).*', self.html_)
    return '\n' + table[1] + '\n'
  


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