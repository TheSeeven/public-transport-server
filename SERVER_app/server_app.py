import time,datetime,re, subprocess,threading,configparser as conf
from constants import *
config = conf.ConfigParser()
config.read('db_program_config.ini')

SUBSCRIBER_SUBPROCESS=subprocess.Popen(["powershell.exe",VEHICLE_SUBSCRIBER_SCRIPT])
def start_subscriber():
    SUBSCRIBER_SUBPROCESS.communicate()
t=threading.Thread(target=start_subscriber)
t.start()

time.sleep(5)
if(t.is_alive()):
    check_config()
    print("SQLManager app is working.\nWelcome to transport app!")
    from sql_manager import *
    from broker import *
else:
    check_config()
    input("Failed to start the subscriber!\nPress enter key to exit.")
    quit("")









