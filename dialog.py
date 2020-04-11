import digitalio
import board
import time
from display import *

class Dialog(Display):
  def __init__(self, indent=5, **kwargs):
    super().__init__(**kwargs)
    self.setFont(fontsize=30)
    self.__indent = indent
    self.__update = False
  
  def prompt(self, line1, line2):
    self.clear()
    self.writeline(line1, (self.__indent, 5))
    self.writeline(line2, (self.__indent, 80))
    self.show()
    return self.getButtons()
  
  def getButtons(self):
    buttons = [digitalio.DigitalInOut(b) for b in (board.D24, board.D23)]
    for b in buttons:
      b.switch_to_input()
    if self.__update:
        time.sleep(0.2)
    else:
      self.__update = True
    while True:
      for k,b in enumerate(buttons):
        if not b.value:
          return k
  
  def options(self, vals):
    while True:
      for k,v in vals:
        if self.prompt(v, "Select") == 1:
          self.clear()
          self.show()
          return k
