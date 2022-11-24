'''
Author: lxulxu
Date: 2022-09-13 10:28:31
LastEditors: lxulxu
LastEditTime: 2022-11-22 19:18:16
Description: 

Copyright (c) 2022 by lxulxu, All Rights Reserved. 
'''
import fitz
from fitz import Matrix, Page, Rect
from paddleocr import PPStructure

from .area import Area
from .block import FigureBlock, TabelBlock, TextBlock

HEADER_STEP = 5
EXPANDING = 10

def get_page_areas(page:Page) -> list[Area]:
  pix = page.get_pixmap(matrix=Matrix(1, 1), alpha=False)
  img = pix.tobytes()
  engine = PPStructure()
  areas = []

  for i in engine(img):
    if i['res'] != []:
      area = Area(i)
      area.parse()
      areas.append(area)
      
  return areas

def get_page_blocks(page:Page, is_scan_ver:bool) -> list:
  blocks = []

  for area in get_page_areas(page):
    if area.is_table:
      d = area.get_table_dict()
      block = TabelBlock(d)
    elif area.is_figure:
      d = area.get_figure_dict()
      block = FigureBlock(d)
    elif area.is_title or area.is_header:
      d = area.get_title_dict()
      block = TextBlock(d)
    else:
      d = area.get_text_dict()
      if not is_scan_ver:
        clip = Rect(area.rect_.x0 - EXPANDING, area.rect_.y0 - EXPANDING,\
                    area.rect_.x1 + EXPANDING, area.rect_.y1 + EXPANDING)
        text_dict = page.get_text('blocks', clip=clip)
        d['lines'] = [{'rect':Rect(line[0], line[1],line[2], line[3]),
                       'text':line[4]} for line in text_dict]
      block = TextBlock(d)

    blocks.append(block)
  
  blocks.sort(key=lambda x:(x.rect_.y0, x.rect_.x0))
  return blocks
  
def add_title_level(blocks:list):
  titles = [i for i in blocks if i.type_ == 'title']
  if not titles:
    return
  titles.sort(key=lambda x:-x.rect_.height)
  level = 1
  end_h = titles[0].rect_.height

  for title in titles:
    if end_h - title.rect_.height > HEADER_STEP:
      end_h = title.rect_.height
      level += 1
    title.level_ = level if level <= 6 else 6

def vertically_merge_block(blocks:list) -> list:
  if blocks == []:
    return []
  res = [blocks[0]]
  for block in blocks[1:]:
    if not res[-1].close_to(block) and not res[-1].rect_.contains(block.rect_):
      res.append(block)

  return res
    
  
def parse_file(filename:str, is_scan_ver:bool) -> list:
  doc = fitz.open(filename)
  
  blocks = []
  for page in doc:
    blocks += get_page_blocks(page, is_scan_ver)

  add_title_level(blocks)
  blocks = vertically_merge_block(blocks)

  return blocks