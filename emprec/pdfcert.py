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

  def write(self, text, position, color=(0, 0, 0), ttfFile='DroidSansMono.ttf'):
    draw = ImageDraw.Draw(self.img)
    font = ImageFont.truetype(ttfFile, 50)
    draw.text(position, text, color, font=font)

  def save(self):
    tmp = NamedTemporaryFile(mode='w+b', suffix='pdf')
    self.img.save(tmp, 'PDF', Quality = 100)
    tmp.seek(0, 0)
    return tmp
