# -*- coding: GB18030 -*-
import os,time,string
from Instrument_Control import *
from CONSTANTS import *
from Analyse import *
import os

#��ȡ�ϼ�Ŀ¼callInterface
curr_path = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)),os.path.pardir))
RFID_power_path = os.path.join(curr_path,"result_file\wireless-indicator"+"\RFID-power.xls")
RFID_ACPR_path_40 = os.path.join(curr_path,"result_file\wireless-indicator"+"\RFID-ACPR_40.xls")
RFID_ACPR_path_80 = os.path.join(curr_path,"result_file\wireless-indicator"+"\RFID-ACPR_80.xls")

agilent_client = Agilent()
agilent_client.OpenInstrument()
agilent_client.Initialize()
#��ȡƵ���Ƿ�ֵ���ʺ�Ƶ��,�����ź�Ƶ���ȶ��Ⱥͷ��书�ʲ���
def testFrqPower(fCenterFrequency,fRefer,fPower,fChannelIndex,curr_col):
    print u"=============Ƶ���ǿ�ʼץȡ����Ϊ��{0}��Ƶ��Ϊ��{1}������==========".format(fPower,fChannelIndex)
    agilent_client.SA_SetOffset(fOffset)
    agilent_client.SA_SetCenterFrequency(fCenterFrequency)
    agilent_client.SA_SetSpan(0.5) #����X���ֵ
    agilent_client.SA_SetTraceMode(1)
    agilent_client.SA_SetReferenceLevel(fRefer) #���òο�ֵY��
    time.sleep(2)
    agilent_client.SA_PeakSearch()
    x,y = agilent_client.SA_GetMark()
    x = '{:.3f}'.format(float(x)/1000000)
    y = '{:.3f}'.format(float(y))
    num = 5
    while float(y) < 0:
        print u"Peak Searchʧ�ܣ�����ȡֵ"
        agilent_client.SA_PeakSearch()
        x,y = agilent_client.SA_GetMark()
        x = '{:.3f}'.format(float(x)/1000000)
        y = '{:.3f}'.format(float(y))
        num = num - 1
        if float(y) > 0 or num == 0:
            break

    write_PowerResult(fPower,RFID_power_path,curr_col,y)
    print u"Ƶ���ǲ��Խ��������Ƶ��ֵ{0}".format(x)
    print u"Ƶ���ǲ��Խ��������ֵ{0}".format(y)

#����Ƶ�ʷ�Χ�ͷ����ź�ƽ̹�Ȳ���
def testFrqSignalFlatness(fCenterFrequency):
    agilent_client.SA_SetMeas(1) #ѡ��Ƶ���ǵĲ���ģʽΪ����ɨƵģʽ
    agilent_client.SA_SetCenterFrequency(fCenterFrequency) #��������Ƶ��
    agilent_client.SA_SetSpan(0.5)  #����Ƶ�״���
    agilent_client.SA_SetRBW(100) #���÷ֱ��ʴ�����100KHz��
    agilent_client.SA_SetTraceMode(1) #����Ƶ����Ϊ���ֵ����ģʽ
    agilent_client.SA_SetCont(1) #����Ƶ����Ϊ����ɨƵģʽ
    #��ȡ����Ƶ�ʷ�Χ�ͷ����ź�ƽ̹��
    agilent_client.SA_PeakSearch()
    x,y = agilent_client.SA_GetMark()
    print x,y

def analyze_ACPR_40(data,ModulationType_text,curr_num):
    acpr_result = data.split(",")
    lower_num1 = '{:.3f}'.format(float(acpr_result[4]))
    lower_num2 = '{:.3f}'.format(float(acpr_result[8]))
    upper_num1 = '{:.3f}'.format(float(acpr_result[6]))
    upper_num2 = '{:.3f}'.format(float(acpr_result[10]))
    print u"��һ�����ڵ���й©��:{0}".format(lower_num1)
    print u"�ڶ������ڵ���й©��:{0}".format(lower_num2)
    print u"��һ�����ڵ���й©��:{0}".format(upper_num1)
    print u"�ڶ������ڵ���й©��:{0}".format(upper_num2)
    write_file(ModulationType_text,RFID_ACPR_path_40,curr_num,lower_num2,lower_num1,upper_num1,upper_num2)

#�ڵ�����й©��
def testACPR_40(ModulationType_text,curr_num):
    agilent_client.SA_SetMeas(3) #ѡ��Ƶ���ǵĲ���ģʽΪACPģʽ
    #����ACP����������������
    #���ŵ�������250KHz��
    #���ŵ�����루250KHz��
    #�ֱ��ʴ�����10KHz��
    #Ĭ�ϲ�����
    #ɨƵʱ�䣨�Զ�����ɨƵ���ȣ�1.5 MHz��
    #ɨƵ������1001��	SA_SetACPR
    agilent_client.SA_SetACPR()
    acpr = agilent_client.SA_GetACPRPower()
    analyze_ACPR_40(acpr,ModulationType_text,curr_num)

def analyze_ACPR_80(data,ModulationType_text,curr_num):
    acpr_result = data.split(",")
    lower_num1 = '{:.3f}'.format(float(acpr_result[4]))
    lower_num2 = '{:.3f}'.format(float(acpr_result[8]))
    upper_num1 = '{:.3f}'.format(float(acpr_result[6]))
    upper_num2 = '{:.3f}'.format(float(acpr_result[10]))
    print u"��һ�����ڵ���й©��:{0}".format(lower_num1)
    print u"�ڶ������ڵ���й©��:{0}".format(lower_num2)
    print u"��һ�����ڵ���й©��:{0}".format(upper_num1)
    print u"�ڶ������ڵ���й©��:{0}".format(upper_num2)
    write_file(ModulationType_text,RFID_ACPR_path_80,curr_num,lower_num2,lower_num1,upper_num1,upper_num2)

#�ڵ�����й©��
def testACPR_80(ModulationType_text,curr_num):
    agilent_client.SA_SetMeas(3) #ѡ��Ƶ���ǵĲ���ģʽΪACPģʽ
    #����ACP����������������
    #���ŵ�������250KHz��
    #���ŵ�����루250KHz��
    #�ֱ��ʴ�����10KHz��
    #Ĭ�ϲ�����
    #ɨƵʱ�䣨�Զ�����ɨƵ���ȣ�1.5 MHz��
    #ɨƵ������1001��	SA_SetACPR
    agilent_client.SA_SetACPR()
    acpr = agilent_client.SA_GetACPRPower()
    analyze_ACPR_80(acpr,ModulationType_text,curr_num)

#ռ�ô�������
def testOBW():
    agilent_client.SA_SetMeas(2)  #����Ƶ���ǵĲ���ģʽΪOBWģʽ
    #����OBW����������������
    #�ֱ��ʴ�����10KHz��
    #Ĭ�ϲ�����
    #ɨƵʱ�䣨�Զ���ɨƵ������1001��
    #ɨƵ���ȣ�2MHz�����������ȣ�99%��
    agilent_client.SA_SetOBW(2,10)
    obw = agilent_client.SA_GetOBW()

def resetSA():
    agilent_client.SAInit()

def set_protocol_conformance():
    agilent_client.Set_Analyze()
    agilent_client.Set_trigger()
    agilent_client.scale_position()
    agilent_client.Set_marker()

def Save_waveform(filename):
    agilent_client.Save_waveformtoDisk(filename)