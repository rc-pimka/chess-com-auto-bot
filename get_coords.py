import json, os
import time
from pynput import keyboard
CONFIG = r"C:\chess_helper\config.json"
pts=[]
def on_press(key):
    global pts
    try:
        if key==keyboard.Key.space:
            from pynput.mouse import Controller
            m=Controller(); x,y=m.position
            pts.append((x,y)); print(f"point {len(pts)}: {x},{y}")
            if len(pts)>=2:
                (x1,y1),(x2,y2)=pts
                w=abs(x2-x1); h=abs(y2-y1); x=min(x1,x2); y=min(y1,y2)
                rect=[x,y,w,h]
                json.dump({"rect":rect}, open(CONFIG,"w"))
                print(f"\nSaved to config: {rect}")
                print("Now run auto.py - it will use this automatically.")
                return False
    except Exception as e:
        print(e)
print("Move mouse to corner, press SPACE to capture. Need 2 points.")
with keyboard.Listener(on_press=on_press) as l:
    l.join()
