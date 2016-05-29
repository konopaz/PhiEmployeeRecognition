import PIL
from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw

from tempfile import NamedTemporaryFile
from shutil import copyfileobj
import os

class pdfcert:
  def __init__(self, imgfile):
    self.img = Image.open(imgfile)

  def writeAward(self, award):
    self.write(award['recipientName'], position=(None, 250), color=(54, 67, 47))
    self.write(award['date'], position=(None, 400), color=(54, 67, 47))
    self.write(award['type'], position=(None, 100), color=(54, 67, 47), fontsize=75)

  def write(self, text, position, color=(0, 0, 0), ttfFile='broken_planew.ttf', fontsize=50):
    draw = ImageDraw.Draw(self.img)
    font = ImageFont.truetype(ttfFile, fontsize)
    posx, posy = position
    if (posx == None):
      textw, texth =draw.textsize(text, font=font)
      posx = (self.img.size[0] - textw) / 2
    draw.text((posx, posy), text, color, font=font)

  def save(self):
    tmp = NamedTemporaryFile(mode='w+b', suffix='pdf')
    self.img.save(tmp, 'PDF', Quality = 100)
    tmp.seek(0, 0)
    return tmp
