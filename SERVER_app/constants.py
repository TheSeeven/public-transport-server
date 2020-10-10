import configparser as conf
import mysql.connector as sql
from decimal import *
getcontext().prec=16

def create_config():
    config = conf.ConfigParser()
    config['DB Settings']={
                    'GPS_ACCUARACY': '',
                    'HOSTNAME':'',
                    'PORT':'',
                    'USERNAME':'',
                    'PASSWORD':'',
                    'BUFFERED' : '',
                    'AUTOCOMIT': ''}

    config.set('DB Settings','; DO NOT DELETE THIS SECTION','')
    config.set('DB Settings','; GPS_ACCUARACY','This value sets the GPS checking precision for finding current of vehicles (Default = 0.0000002)')
    config.set('DB Settings','; HOSTNAME','The IP of the server on which the program manages the database')
    config.set('DB Settings','; PORT','The PORT of the server on which the program manages the database')
    config.set('DB Settings','; USERNAME','The username used by the program to acces database')
    config.set('DB Settings','; PASSWORD','The password used by the program to acces database')
    config.set('DB Settings','; BUFFERED','Sets if the commands should be beffered or not (Default = True)')
    config.set('DB Settings','; AUTOCOMIT','Sets autocomit on or off (Default = True) ! Might make the program crash if set to False !')

    config['MQTT Settings']={
                    'HOSTNAME_V':'',
                    'PORT_V':'',
                    'PORT_VS':'',
                    'USERNAME_V':'',
                    'USERNAME_VS':'',
                    'PASSWORD_V':'',
                    'PASSWORD_VS':'',
                    'BUFFERED_V': '',
                    'AUTOCOMIT_V' : ''}

    config.set('MQTT Settings','; DO NOT DELETE THIS SECTION','')
    config.set('MQTT Settings','; HOSTNAME_V','The IP on which broker is listening for data')
    config.set('MQTT Settings','; PORT_V','The PORT used by the brokker to listen for data')
    config.set('MQTT Settings','; PORT_VS','The PORT used by the MQTT to send data to server')
    config.set('MQTT Settings','; USERNAME_V','The username used by the program to acces the broker')
    config.set('MQTT Settings','; USERNAME_VS','The username used by the program to acces the DB')
    config.set('MQTT Settings','; PASSWORD_V','The password used by the program to acces broker subscriber')
    config.set('MQTT Settings','; PASSWORD_VS','The password used by the program to acces DB')
    config.set('MQTT Settings','; BUFFERED_V','Sets if the commands should be beffered or not (Default = True)')
    config.set('MQTT Settings','; AUTOCOMIT_V','Sets autocomit on or off (Default = True) ! Might make the program crash if set to False !')

    with open('db_program_config.ini','w') as configfile:
        config.write(configfile)

def check_config():
    config = conf.ConfigParser()
    if(len(config.read('db_program_config.ini')) == 0):
        create_config()
        print("Config file created!")
        input("Press any key to exit the program.")
        quit()
    else:
        vals=[]
        vals.append(config.has_option('DB Settings','GPS_ACCUARACY'))
        
        vals.append(config.has_option('DB Settings','HOSTNAME'))
        vals.append(config.has_option('DB Settings','PORT'))
        vals.append(config.has_option('DB Settings','USERNAME'))
        vals.append(config.has_option('DB Settings','PASSWORD'))
        vals.append(config.has_option('DB Settings','BUFFERED'))
        vals.append(config.has_option('DB Settings','AUTOCOMIT'))

        vals.append(config.has_option('MQTT Settings','HOSTNAME_V'))
        vals.append(config.has_option('MQTT Settings','PORT_V'))
        vals.append(config.has_option('MQTT Settings','PORT_VS'))
        vals.append(config.has_option('MQTT Settings','USERNAME_V'))
        vals.append(config.has_option('MQTT Settings','USERNAME_VS'))
        vals.append(config.has_option('MQTT Settings','PASSWORD_V'))
        vals.append(config.has_option('MQTT Settings','PASSWORD_VS'))
        vals.append(config.has_option('MQTT Settings','BUFFERED_V'))
        vals.append(config.has_option('MQTT Settings','AUTOCOMIT_V'))
        for i in vals:
            if i == False:
                create_config()
                input("Config file recreated!\nConfigure file and relaunch the app.\nPress enter to close this window.")
                quit("")
        try:
            Decimal(str(config['DB Settings']['GPS_ACCUARACY']))
            str(config['DB Settings']['HOSTNAME'])
            str(config['DB Settings']['PASSWORD'])
            int(config['DB Settings']['PORT'])
            str(config['DB Settings']['USERNAME'])
            config['DB Settings'].getboolean('BUFFERED')
            config['DB Settings'].getboolean('AUTOCOMIT')
    
            str(config['MQTT Settings']['HOSTNAME_V'])
            str(config['MQTT Settings']['PASSWORD_V'])
            str(config['MQTT Settings']['PASSWORD_VS'])
            int(config['MQTT Settings']['PORT_V'])
            int(config['MQTT Settings']['PORT_VS'])
            str(config['MQTT Settings']['USERNAME_V'])
            str(config['MQTT Settings']['USERNAME_VS'])
            config['MQTT Settings'].getboolean('BUFFERED_V')
            config['MQTT Settings'].getboolean('AUTOCOMIT_V')
        except:
            input("Wrong values given to config settings!\nPress enter key to exit.")
            quit("")


def execute_querry(connection,querry):

    """Executes a querry for a specific connection."""

    try:
        DBCURSOR=connection.cursor()
        DBCURSOR.execute(querry,multi=True)
        try:
            rez=DBCURSOR.fetchall()
            DBCURSOR.close()
            return rez
        except:
            DBCURSOR.close()
    except Exception as e :
        print("error executing query -->",e)

def execute_procedure(DB,procName,parameters):
    DBCURSOR = DB.cursor()
    DBCURSOR.callproc(procName,parameters)
    try:
        for i in DBCURSOR.stored_results():
            rez=i.fetchall()
        DB.close()
        return rez
    except:
        DB.close()

VEHICLE_SUBSCRIBER_SCRIPT="""$folder = Get-ChildItem | Select-Object Name;
$found = $FALSE
$path = ''
foreach ($i in $folder)
{ 
    if($i.Name -eq "mosquitto.conf")
    {
        $path = $i.Name
        $found = $TRUE 
    }
} 

if (-not $found)
{
    Write-Output "Subscriber config file does not exist!";
    exit;
}

if ($found)
{
    Write-Output "Mosquitto started!";
    mosquitto -c $path;
    Write-Output "Mosquitto stoped working.";
}"""

