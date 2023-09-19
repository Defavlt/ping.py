import subprocess
import signal
import sys
import atexit

import matplotlib.pyplot as plt
import matplotlib.animation as anim
import threading
import time

from plot import plot_cont, set

times = []
argv = []
args = {}

def usage():
  print("Usage: ping target_name [-s log_name] [-l log_name] [-p period]")
  print("")
  print("Options:")
  print("\t-s log_name\tSave log to the specified file")
  print("\t-l log_name\tLoad previous log so as to continue from previous history")
  print("\t-p period\tNumber of replies to average")
  print("\t-d title\tDraw a graph with a specified title")
  print("")
  
def sigint():
  if "-s" in args:
    log_name = args["-s"]
    with open(log_name, "w") as file:
      file.writelines([f'{str(t)}\n' for t in times])
    
    print(f'\nWrote {len(times)} lines to {log_name}')

atexit.register(sigint)

args_l = len(sys.argv)
if args_l < 2:
  usage()
  sys.exit()
  
argv = sys.argv[2:]

if len(argv) % 2:
  print("Illegal arguments;")
  usage()
  sys.exit()

while len(argv):
  args[argv.pop()] = argv.pop()

addr = sys.argv[1]
cmd = ["ping", addr, "/t"]
p = subprocess.Popen(cmd, stdout=subprocess.PIPE)

append, get, reset = set()
lock = threading.Lock()

if "-l" in args:
  with open(args["-l"]) as file:
    for line in list(file):
      r = float(line.rstrip())
      times.append(r)
      append(r)

def poll():
  counter = 0
  for line in p.stdout:
    counter += 1
    line = line.decode("UTF-8")
    line = str(line)
    line = line.rstrip()
    # ping on windows output 2 lines before ping respons
    if counter > 2:
      s = line.split(" ")
      time = -1

      if "Reply" == s[0]:
        time = float(s[4].split("=")[1].replace("ms", ""))
      
      times.append(time)
      n_times = len(times)

      if "-d" in args:
        if len(times):
          with lock:
            append(times[-1])
    
      elif not "-p" in args or not counter % int(args["-p"]):
        replies = [t for t in times if t > -1]
        n_replies = len(replies)
        if n_replies:
          s = sum(replies)
          avg = round(s / n_replies, 1)
          print(f'{n_replies}/{n_times} packages avg {avg} min {min(replies)} max {max(replies)}')
          
        else:
          print(f'{n_times - n_replies} requests timed out.')

if "-d" in args:
  t = threading.Thread(target=poll, daemon=True)
  t.start()
  plot_cont(get, lock)

else:
  poll()
