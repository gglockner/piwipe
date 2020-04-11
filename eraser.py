#!/usr/bin/python3

from dialog import *
import subprocess
import signal
import re
import time


dev = "sda"
dlg = Dialog()
pat = re.compile('\d{2,3}\.\d{2}%')

def progress(msg):
  dlg.clear()
  dlg.writeline(msg, (20,40))
  dlg.show()
  time.sleep(5)
  

# Get disk model
with open("/sys/block/%s/device/model" % dev, "r") as fp:
  model = fp.read()

dlg.prompt(model, "Start nwipe")

method = dlg.options([
  ("dodshort","3-pass DOD"),
  ("dod", "7-pass DOD"),
  ("gutmann", "Guttman"),
  ("ops2", "OPS-II"),
  ("prng", "PRNG stream"),
  ("quick", "Quick zeros")
])

verify = dlg.options([
  ("last", "Verify last"),
  ("all",  "Verify every"),
  ("off",  "Do not verify")
])

dlg.setFont(fontsize=45)

cmd = "stdbuf -oL /usr/sbin/nwipe --autonuke --nogui --method=%s --verify=%s /dev/%s" \
      % (method, verify, dev)

# Start the wipe
print("Running wipe: %s" % cmd)
with subprocess.Popen(cmd.split(" "), stdout=subprocess.PIPE) as proc:
  while proc.poll() is None:
    dlg.backlight(False)
    dlg.getButtons() # wait for button input
    proc.send_signal(signal.SIGUSR1)
    while True:
      result = pat.search(proc.stdout.readline().decode('utf8'))
      if result:
        break
    progress(result.group())
  print("Return code: %s" % str(proc.poll()))

progress("Done")
