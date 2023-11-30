from signal import signal, SIGTERM, SIGHUP, pause
from rpi_lcd import LCD
from datetime import datetime
import time
import queue

lcd = LCD()

def safe_exit(signum, frame):
    exit(0)

def lcd_time(lcd_queue):
    lcd = LCD()
    lcd.clear()

    while True:
        try:
            mode = lcd_queue.get_nowait()
        except queue.Empty:
            mode = 0 

        now = datetime.now()
        current_time = now.strftime("%I:%M:%S %p")
        current_date = now.strftime("%b %d, %Y")

        lcd.text(current_time, 1)
        lcd.text(current_date, 2)

        if mode == 1:
            lcd_load(lcd_queue)
            lcd_queue.task_done() 
        if mode == 2:
            lcd_listen(lcd_queue)
            lcd_queue.task_done() 

        time.sleep(1)

def lcd_load(lcd_queue):
    lcd = LCD()
    lcd.clear()

    while True:
        try:
            mode = lcd_queue.get_nowait()
        except queue.Empty:
            mode = 1 
        if mode == 0:
            return  
        lcd.text("Computing", 1)
        time.sleep(0.5)
        lcd.text("Computing.", 1)
        time.sleep(0.5)
        lcd.text("Computing..", 1)
        time.sleep(0.5)
        lcd.text("Computing...", 1)
        time.sleep(0.5)

def lcd_listen(lcd_queue):
    lcd = LCD()
    lcd.clear()

    while True:
        try:
            mode = lcd_queue.get_nowait()
        except queue.Empty:
            mode = 2 
        if mode == 0:
            return  
        lcd.text("Listening", 1)
        time.sleep(0.5)
        lcd.text("Listening.", 1)
        time.sleep(0.5)
        lcd.text("Listening..", 1)
        time.sleep(0.5)
        lcd.text("Listening...", 1)
        time.sleep(0.5)
