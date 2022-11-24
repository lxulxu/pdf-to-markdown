'''
Author: lxulxu
Date: 2022-10-20 14:10:14
LastEditors: lxulxu
LastEditTime: 2022-11-17 16:19:32
Description: 

Copyright (c) 2022 by lxulxu, All Rights Reserved. 
'''
import os

from mdutils.mdutils import MdUtils


class Writer(object):

  def __init__(self, filename:str, blocks:list) -> None:
    '''
    description: 
    param {str} filename: filename of pdf document
    param {list} blocks: list of Blocks
    '''
    self.blocks_ = blocks

    #root_dir
    self.root_dir_ = os.path.splitext(filename)[0]
    if not os.path.exists(self.root_dir_):
        os.makedirs(self.root_dir_)

    #md_file
    basename, _ = os.path.splitext(os.path.basename(filename))
    md_name = os.path.join(self.root_dir_, basename)
    self.md_file_ = MdUtils(file_name=md_name, title=basename)

  def gen_markdown(self, has_footer:bool=False):
    '''
    description: 
    param {bool} has_footer: whether to write footer or not
    '''
    img_id = 0

    for block in self.blocks_:
      syntax = ''
      
      if block.is_figure:
        syntax = block.gen_image_syntax(self.root_dir_, img_id)
        img_id += 1
      
      elif block.is_table:
        syntax = block.gen_table_syntax() + '\n'

      elif block.is_paragraph:
        syntax = block.gen_paragraph_syntax(has_footer)

      self.md_file_.write(syntax)

  def write_markdown(self):
    self.gen_markdown()
    self.md_file_.create_md_file()