from signal import signal, SIGTERM, SIGHUP, pause
from rpi_lcd import LCD

def safe_exit(signum, frame):
    exit(0)

def get_lcd():
    lcd = LCD()
    signal(SIGTERM, safe_exit)
    signal(SIGHUP, safe_exit)

    lcd.text("CYBOT GALACTICA", 1)
    lcd.text("C-3DK", 2)

