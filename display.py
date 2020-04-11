import digitalio
import board
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.st7789 as st7789

# Based on https://learn.adafruit.com/adafruit-mini-pitft-135x240-color-tft-add-on-for-raspberry-pi/python-stats

class Display:
  def __init__(self, background="black", foreground="white",
               rotation=270, padding=-2,
               width=135, height=240, x_offset=53, y_offset=40,
               baudrate=64000000, ttfont='dejavu/DejaVuSans.ttf', fontsize=24):
    # Configuration for CS and DC pins (these are FeatherWing defaults on M0/M4):
    cs_pin = digitalio.DigitalInOut(board.CE0)
    dc_pin = digitalio.DigitalInOut(board.D25)
    reset_pin = None

    # Setup SPI bus using hardware SPI:
    spi = board.SPI()

    # Create the ST7789 display:
    self.__disp = st7789.ST7789(spi, cs=cs_pin, dc=dc_pin, rst=reset_pin,
                                baudrate=baudrate, width=width, height=height,
                                x_offset=x_offset, y_offset=y_offset)

    # Create blank image for drawing.
    # Make sure to create image with mode 'RGB' for full color.
    self.__height = self.__disp.width   # we swap height/width to rotate it to landscape!
    self.__width = self.__disp.height
    self.__image = Image.new('RGB', (self.__width, self.__height))
    self.__rotation = rotation
    self.__padding = padding
    self.__background = background
    self.__foreground = foreground

    # Get drawing object to draw on image.
    self.__draw = ImageDraw.Draw(self.__image)
    self.clear()
    self.backlight(False)
    
    self.setFont(fontsize, ttfont)


  def setFont(self, fontsize=24, ttfont='dejavu/DejaVuSans.ttf'):
    self.__fontsize = fontsize
    self.__ttfont = '/usr/share/fonts/truetype/%s' % ttfont
    self.__font = ImageFont.truetype(self.__ttfont, self.__fontsize)
    
  def show(self):
    self.__disp.image(self.__image, self.__rotation)
    if not self.backlightState():
        self.backlight(True)

  def clear(self, backlight=True, color=None):
    # Draw a filled box to clear the image.
    if not color:
      color = self.__background
    self.__draw.rectangle((0, 0, self.__width, self.__height), outline=0, fill=color)
    if not backlight:
        self.backlight(False)

  def getBacklight(self):
    backlight = digitalio.DigitalInOut(board.D22)
    backlight.switch_to_output()
    return backlight

  def backlightState(self):
    return self.getBacklight().value

  def backlight(self, on=True):
    backlight = self.getBacklight()
    backlight.value = on

  def write(self, text, colors=None, font=None):
    x, y = 0, self.__padding
    lines = text
    if type(lines) == str:
        lines = [lines]
    if type(colors) != list:
      colors = [colors] * len(lines)
    self.clear()
    for l,c in zip(lines, colors):
      y = self.writeline(l, (x,y), c, font)
    
    self.show()
  
  def writeline(self, s, pos, color=None, font=None):
    if not font:
      font = self.__font
    if not color:
      color = self.__foreground
    self.__draw.text(pos, s, font=font, fill=color)
    return pos[1] + font.getsize(s)[1]
