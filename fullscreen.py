import eel
import os
import sys

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
    
loc = resource_path('ludaringinGUI')
eel.init(loc)
eel.start('index.html', mode='chrome', cmdline_args=['--kiosk'])