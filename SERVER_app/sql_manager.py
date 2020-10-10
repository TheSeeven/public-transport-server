import configparser as conf
import mysql.connector as sql
from decimal import *
from constants import *
import datetime
import time
import threading

getcontext().prec=16
config = conf.ConfigParser()
config.read('db_program_config.ini')


""" DB Options """
GPS_ACCUARACY = Decimal(str(config['DB Settings']['GPS_ACCUARACY']))
HOSTNAME =  str(config['DB Settings']['HOSTNAME'])
USERNAME = str(config['DB Settings']['USERNAME'])
PASSWORD = str(config['DB Settings']['PASSWORD'])
PORT= int(config['DB Settings']['PORT'])
BUFFERED = config.getboolean('DB Settings','BUFFERED')
AUTOCOMIT = config.getboolean('DB Settings','AUTOCOMIT')
""" DB Options """

DEBUGER_MODE=False  # Turning this on will result in more debuging output on CLI


""" Working variables """
TOD = 1
TOD_CHANGE = False

VEHICLES_JOB=[]
""" Working variables """

class Vehicle:
    def __init__(self,id,time_elapsed,current):
        self.id=id
        self.time_elapsed=time_elapsed
        self.current=current

    def __str__(self):
        if self.time_elapsed is not None:
            x=time.time()-self.time_elapsed
            return "Vehicle ID: " + str(self.id) + " time "  + str() + " station " + str(self.current)
        else:
            return "Vehicle ID: " + str(self.id) + " time "  + str(x.time) + " station " + str(self.current)


def get_connection(): # OK

    """Returns a connection object for the DB"""

    while True:
        try:
            DB=sql.connect(host=HOSTNAME,user=USERNAME,passwd=PASSWORD,buffered=BUFFERED,database="public_transport",auth_plugin='mysql_native_password')
            DB.autocommit = AUTOCOMIT
            return DB
        except:
            print("Error creating connection ", datetime.datetime.now())

def check_vehicle(id,pathId): 

    """ Makes a decision based on the id and pathid. Adds time_sample only if id and pathid are non existent in the current buffer. """

    global VEHICLES_JOB
    for i in VEHICLES_JOB:
        if i.id == id :
            if i.current != pathId:
                execute_procedure(get_connection(),"management_time_sample",[i.current,pathId,(time.time()-i.time_elapsed)/60,id])
                i.current=pathId
                i.time_elapsed=time.time()
                return 0
            else:
                return 1
    return 2

def remove_vehicle(id):

    """ Removes a vehicle from array for a given id. """

    for i in VEHICLES_JOB:
        if i.id == id:
            VEHICLES_JOB.remove(i)

def sample_adder():

    """ Thread - This vehicle handles the current of the vehicle and adds time in the time sample. """

    while True:
        vehicleList = execute_procedure(get_connection(),"vehicle_in_station",[GPS_ACCUARACY,TOD])
        
        vehicleDepo = execute_procedure(get_connection(),"vehicle_in_depo",[])
        for depo_veh in vehicleDepo:
            for vehicle in VEHICLES_JOB:
                if depo_veh[0]==vehicle.id:
                    remove_vehicle(depo_veh[0])
                    break

        vehicleListLength = len(vehicleList)
        iterator = 0 
        while vehicleListLength != iterator:
            i=vehicleList[iterator]

            if check_vehicle(i[0],i[1]) == 0 :
                vehicleList.remove(i)
                iterator=iterator-1
                vehicleListLength=vehicleListLength-1

            elif check_vehicle(i[0],i[1]) == 1:
                if i[2] == 1:
                    remove_vehicle(i[0])

            elif check_vehicle(i[0],i[1]) == 2 and i[2] != 1:
                VEHICLES_JOB.append(Vehicle(i[0],time.time(),i[1]))
            iterator=iterator+1

        time.sleep(3)

def calculate_average(): 
    
    """Thread - This thread updates the average times between stations."""
    
    while True:
        if TOD != None:  
            try:    
                execute_procedure(get_connection(),"update_path_avg",[TOD])
                print("Average calculated succesfull\n")
                time.sleep(60)
            except Exception as e:
                print(datetime.datetime.now()," average calculation error --> ",e)
                time.sleep(2)

def clear_buffers(): 

    """Thread - This function clears the buffer at the end of the day"""

    global VEHICLES_JOB
    while True:
        if(datetime.datetime.now().hour >= 1 and datetime.datetime.now().hour < 4):
            VEHICLES_JOB = []
            print(datetime.datetime.now(),"\nBuffer cleared \n")
        time.sleep(7200)
    else:
        time.sleep(7)

def count_vehicle():
    
    """Thread - Updates vehicle_type tabel count column"""

    while True:
        DB=get_connection()
        try:
            #execute_querry(DB,"call public_transport.update_vehicle_count()")
            execute_procedure(DB,"update_vehicle_count",[])
            print("Vehicles Counted\n")
            time.sleep(7200)
        except Exception as e:
            print(datetime.datetime.now()," error updating vehicle count --> ", e)
            time.sleep(2)

def set_TOD(): 

    """Thread - This function adjusts the value of TOD based on the time of day."""

    global TOD
    while True:
        current_TOD = get_TOD()
        if current_TOD!=TOD:
            TOD=current_TOD
        print("Tod set to:{a}\n".format(a=str(TOD)))
        time.sleep(30)

def park_vehicles():

    """Thread - This function sets lat,long,current,arrival to NULL and problem=0 
        where the inactivity time is greater than 1 hour """

    while True:
        execute_procedure(get_connection(),"vehicle_timeout",[])
        time.sleep(400)

 
def get_TOD():

    """This function transforms Time of day in TOD"""

    current = datetime.datetime.now()
    if current.hour<=10 and current.hour>0:
        return 1
    elif current.hour<=14 and current.hour>10:
        return 2
    elif current.hour<=18 and current.hour>14:
        return 3
    elif current.hour<=23 and current.hour>18:
        return 4
    else:
        return 1


def start():

    print("Starting proceses!\n")

    TOD_UPDATER = threading.Thread(target=set_TOD)
    AVERAGE_UPDATER = threading.Thread(target=calculate_average)
    COUNT_UPDATER = threading.Thread(target=count_vehicle)
    CLEAR_BUFFER = threading.Thread(target=clear_buffers)
    SAMPLE_ADDER = threading.Thread(target=sample_adder)
    VEHICLE_PARKER = threading.Thread(target=park_vehicles)

    TOD_UPDATER.start()
    print("Time of day updater started.\n")
    AVERAGE_UPDATER.start()
    print("Average time updater started.\n")
    COUNT_UPDATER.start()
    print("Vehicle counter started.\n")
    CLEAR_BUFFER.start()
    SAMPLE_ADDER.start()
    print("Sample adder started.\n")
    VEHICLE_PARKER.start()
    print("Vehicle parker started.\n")


start()

if DEBUGER_MODE is True:
    def print_array():
        while True:
            time.sleep(5)
            print("---------------------------------------------")
            for i in VEHICLES_JOB:
                print("working : ",i)
            print("---------------------------------------------")

    x = threading.Thread(target=print_array)
    x.start()
