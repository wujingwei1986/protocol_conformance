# -*- coding: GB18030 -*-
import visa,time,string,sys,struct
from pyvisa.resources.usb import USBInstrument
from pyvisa.constants import  *

debug = 0

rm = visa.ResourceManager()
my_instrument = rm.open_resource('TCPIP0::192.168.1.137::inst0::INSTR')
#my_instrument.clear()
my_instrument.timeout = 30000
print my_instrument.query('*IDN?')  #get device info
'''
#config f1
#print my_instrument.write(":FUNCTION1:ADD CHANNEL1,CHANNEL2")
#print my_instrument.write(":FUNCtion1:ABSolute CHANnel4") #operator为Absolute Value，Source channel4
#print my_instrument.query(":FUNCtion1?")

#config f2 parameters
my_instrument.write("FUNCtion2:DISPlay ON")
my_instrument.write(":FUNCtion2:LOWPass FUNCtion1,2E6") #低通，source为Function1，bandwidth 2MHZ
my_instrument.write("FUNCtion2:VERTical MANual") #vertical手动模式
print my_instrument.query(":FUNCtion2:VERTical:RANGe?")
print my_instrument.query(":FUNCtion2:VERTical:OFFSet?")
my_instrument.write(":FUNCtion2:VERTical:RANGe 1600E-3") #与scale是8倍的关系：scale*8=Range
my_instrument.write(":FUNCtion2:VERTical:OFFSet 300E-3")
'''
def do_query_string(query):
    if debug:
        print "Qys = '%s'" % query
    result = my_instrument.query("%s" % query)
    check_instrument_errors(query)
    return result

def do_command(command, hide_params=False):
    if hide_params:
        (header, data) = string.split(command, " ", 1)
        if debug:
            print "\nCmd = '%s'" % header
    else:
        if debug:
            print "\nCmd = '%s'" % command

    my_instrument.write("%s" % command)

    if hide_params:
        check_instrument_errors(header)
    else:
        check_instrument_errors(command)

def do_query_number(query):
    if debug:
        print "Qyn = '%s'" % query
    results = my_instrument.query("%s" % query)
    check_instrument_errors(query)
    return float(results)


# =========================================================
# Send a query, check for errors, return binary values:
# =========================================================
def do_query_ieee_block(query):
    if debug:
        print "Qyb = '%s'" % query
    result = my_instrument.query_binary_values("%s" % query, datatype='s')
    check_instrument_errors(query)
    return result[0]

def check_instrument_errors(command):
    while True:
        error_string = my_instrument.query(":SYSTem:ERRor? STRing")
        if error_string:   # If there is an error string value.
            if error_string.find("0,", 0, 2) == -1:   # Not "No error".
                print "ERROR: %s, command: '%s'" % (error_string, command)
                print "Exited because of error."
                sys.exit(1)
            else:   # "No error"
                break

        else:   # :SYSTem:ERRor? STRing should always return string.
            print "ERROR: :SYSTem:ERRor? STRing returned nothing, command: '%s'" % command
            print "Exited because of error."
            sys.exit(1)


#print my_instrument.query(":TRIGger:EDGE:SLOPe?")
#print my_instrument.write(":TRIGger:MODE EDGE")
#print my_instrument.write(":TRIGger:EDGE:SOURce CHANnel4")
#print my_instrument.write(":TRIGger:LEVel CHANnel4,480E-3")
#print my_instrument.write(":TRIGger:EDGE:SLOPe POSitive")
#print my_instrument.write(":TIMebase:SCALe 2E-3")
#print my_instrument.write(":TIMebase:POSition 6.5E-3")

#print my_instrument.query(":TRIGger:EDGE:SOURce?")
#print my_instrument.query(":TRIGger:LEVel? CHANnel4")
#print my_instrument.query(":MEASure:FREQuency? FUNCtion2")
#print my_instrument.query(":MEASure:BWIDth? FUNCtion2")
'''
do_command(":TIMebase:RANGe 5E-4")   #Time base to 500 us/div.
do_command(":TIMebase:DELay 0")   #  ' Delay to zero.
do_command(":TIMebase:REFerence CENTer")#   ' Display ref. at ' center.

do_command(":ACQuire:MODE RTIMe")#   ' Normal acquisition.
do_command(":SYSTem:HEADer OFF")#   ' Turn system headers off.
do_command(":DISPlay:GRATicule FRAMe")#   ' Grid off.
'''
print "111111"
#print my_instrument.query(":MEASure:PERiod? FUNCtion2,RISing")
#do_command(":MEASure:NPERiod FUNCtion2,RISing, 1")
#print my_instrument.query(":MEASure:NPERiod?")
#print my_instrument.query(":MEASure:NPERiod FUNCtion2,RISing, 3")
#print my_instrument.query(":MARKer:TSTArt?")
#print do_query_string(":FUNCtion2:HORizontal:RANGe?")
#print do_query_string(":TIMebase:RANGe?")
#print do_query_string(":MARKer:TSTArt?") #测量AX的位置
#print do_query_string(":MARKer:TSTOp?") #测量AX的位置

do_command(":SYSTem:HEADer OFF")
qresult = do_query_string(":WAVeform:TYPE?")
print "Waveform type: %s" % qresult
# Get the number of waveform points.
qresult = do_query_string(":WAVeform:POINts?")
print "Waveform points: %s" % qresult

 # Get the waveform data.
do_command(":WAVeform:STReaming OFF")
print "22222222"
do_command(":WAVeform:SOURce FUNCtion2") #' Select source.
do_command(":WAVeform:FORMat WORD")#   ' Select word format.

sData = do_query_ieee_block(":WAVeform:DATA?")

# Get numeric values for later calculations.
x_increment = do_query_number(":WAVeform:XINCrement?")
x_origin = do_query_number(":WAVeform:XORigin?")
y_increment = do_query_number(":WAVeform:YINCrement?")
y_origin = do_query_number(":WAVeform:YORigin?")
print x_increment,x_origin,y_increment,y_origin



 # Unpack signed byte data.
values = struct.unpack("%db" % len(sData), sData)
#print values
print "Number of data values: %d" % len(values)

#f = open("waveform_data.csv", "w")

for i in xrange(0, 5):
    time_val = x_origin + (i * x_increment)
    print x_origin,x_increment
    print time_val
    voltage = (values[i] * y_increment) + y_origin
    print values[i]
   # print time_val,voltage
    #f.write("%E, %f\n" % (time_val, voltage))

#print do_query_string(":MEASure:DELTatime FUNCtion2")
#do_command(":MEASure:VTOP FUNCtion2")
#print do_query_string(":MEASure:VTOP? FUNCtion2")
#print do_query_string(":MEASure:NPERiod FUNCtion2,RISing, 3")
#print my_instrument.query(":WAVeform:COUNt?")
#print my_instrument.query(":MEASure:BPERiod? FUNCtion2,2.5E-03")

#print my_instrument.query(":MARKer:X1Y1source?")
#print my_instrument.query(":MARKer:X2Y2source?")
#print my_instrument.query(":MARKer:X1Position?")
#print my_instrument.query(":MARKer:X2Position?")
#print my_instrument.query(":MARKer:Y1Position?")
#print my_instrument.query(":MARKer:Y2Position?")

#print my_instrument.query(":STOP;*OPC?")

