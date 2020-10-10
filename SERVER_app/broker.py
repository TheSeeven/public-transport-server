import constants as const
import paho.mqtt.client as MQTT
import mysql.connector as sql
import configparser as conf
from decimal import *
getcontext().prec=16

config = conf.ConfigParser()
config.read('db_program_config.ini')

""" MQTT Options """
HOSTNAME_V = str(config['MQTT Settings']['HOSTNAME_V'])
USERNAME_V = str(config['MQTT Settings']['USERNAME_V'])
USERNAME_VS = str(config['MQTT Settings']['USERNAME_VS'])
PASSWORD_V =  str(config['MQTT Settings']['PASSWORD_V'])
PASSWORD_VS =  str(config['MQTT Settings']['PASSWORD_VS'])
BUFFERED_V = config.getboolean('MQTT Settings','BUFFERED_V')
AUTOCOMIT_V = config.getboolean('MQTT Settings','AUTOCOMIT_V')
PORT_V=int(config['MQTT Settings']['PORT_V'])
PORT_VS=int(config['MQTT Settings']['PORT_VS'])
""" MQTT Options """

def get_connection():

    """Returns a connection object for the global params DB."""

    while True:
        try:
            DB=sql.connect(host=HOSTNAME_V,user=USERNAME_VS,passwd=PASSWORD_VS,buffered=BUFFERED_V,database='public_transport',auth_plugin='mysql_native_password')
            DB.autocommit = AUTOCOMIT_V
            return DB
        except:
            print("Error creating connection ", datetime.datetime.now())


def on_connect(client, userdata, flags, rc):
    try:
        client.subscribe("transportp8")
        print("Connected to MQTT Broker")
    except Exception as e:
        print("Broker connection error --> ",e)

def on_disconnect():
    print("Disconnected from the MQTT Broker")

def parse_data(string):

    """Transforms the string in a touple that represents data."""

    idv = ""
    lat = ""
    long = ""
    problems=""
    sep_count=0
    for i in string:
        if(i == ":"):
            sep_count+=1
            continue
        if(i=="@"):
            sep_count=-1;
        if(i == "$"):
            break
        if(sep_count==0):
            idv+=i
            continue
        if(sep_count==1):
            lat+=i
            continue
        if(sep_count==2):
            long+=i
            continue
        if(sep_count==3):
            problems+=i
            continue
    idv=int(idv)
    if(problems == 'N'):
        problems = 0
    else:
        problems = 1
    if sep_count!=-1:
        return (idv,Decimal(lat),Decimal(long),problems)
    else:
        return (idv)
  
def on_message(client, userdata, message): 
    DATA = parse_data(message.payload.decode())
    try:
        const.execute_procedure(get_connection(),"set_vehicle_location",[DATA[0],DATA[1],DATA[2],DATA[3]])
    except:
        const.execute_procedure(get_connection(),"set_vehicle_in_depo",[DATA])

def conector():
    client = MQTT.Client("MQTT > SQL.publicTransport")
    client.username_pw_set(username=USERNAME_V,password=PASSWORD_V)
    client.connect(host=HOSTNAME_V, port=PORT_V) 
    client.on_connect=on_connect                      
    client.on_message=on_message 
    client.on_disconnect=on_disconnect 
    client.loop_forever()        
conector()