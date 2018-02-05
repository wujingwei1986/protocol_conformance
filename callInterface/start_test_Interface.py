# -*- coding: GB18030 -*-
from ctypes import *
from common.structfile import *
import logging,threading,time
from common.constant import *
from aglient_control import Device_Test,Instrument_Control,CONSTANTS,WaveformData_Analyse
from common.Opxml import *
import os
import ConfigParser

#��ȡrun_main��·��
curr_path = os.path.dirname(os.path.realpath(__file__))
configData_path = os.path.join(curr_path,"config")
testData_abspath = os.path.join(configData_path,"test_data.xml")
configData_abspath = os.path.join(configData_path,"config_data.xml")
readerDevice_config = os.path.join(configData_path,"Reader_Device.ini")

cfg = ConfigParser.ConfigParser()
cfg.read(readerDevice_config)
powerlist_paramer = eval(cfg.get("Reader","Powerlist"))
Frequency = float(cfg.get("Reader","Frequency"))
ModulationType_GB_paramer = eval(cfg.get("Reader","ModulationType_GB"))
DataEncodeType_GB_paramer = eval(cfg.get("Reader","DataEncodeType_GB"))
ModulationDepth_GB_paramer = eval(cfg.get("Reader","ModulationDepth_GB"))
ForwardReverseDataRate_GB_40 = eval(cfg.get("Reader","ForwardReverseDataRate_GB_40"))
ForwardReverseDataRate_GB_80 = eval(cfg.get("Reader","ForwardReverseDataRate_GB_80"))

def DealRoReport(report):
    if report.contents.type == RO_REPORT:
        ResRoReport = cast(report.contents.report,POINTER(RoReport))
        if report.contents.type == 0:
            print u"���ڲ�����ǩ��"
            if ResRoReport.contents.restype == INVENTORY:
                print u"����ǩ����{0}".format(ResRoReport.contents.tagid)
            elif ResRoReport.contents.restype == READ_OP:
                print u"����ǩ��ǩ�����{0}".format(ResRoReport.contents.res)
                if ResRoReport.contents.res == 0:
                    print u"����ǩ��ǩbuf��{0}".format(ResRoReport.contents.opbuf)
            elif ResRoReport.contents.restype == WRITE_OP:
                print u"д��ǩ�����{0}".format(ResRoReport.contents.res)
                if ResRoReport.contents.res == 0:
                    print u"������д��ǩ�ɹ�������"
                else:
                    print u"������д��ǩʧ�ܣ�����"
            elif ResRoReport.contents.restype == LOCK_OP:
                print u"����ǩ�����{0}".format(ResRoReport.contents.res)
                if ResRoReport.contents.res == 0:
                    print u"����������ǩ�ɹ�������"
                else:
                    print u"����������ǩʧ�ܣ�����"
            elif ResRoReport.contents.restype == KILL_OP:
                print u"������ǩ�����{0}".format(ResRoReport.contents.res)
                if ResRoReport.contents.res == 0:
                    print u"������ɱ����ǩ�ɹ�������"
                else:
                    print u"������ɱ����ǩʧ�ܣ�����"
            elif ResRoReport.contents.restype == BLOCK_ERASE_OP:
                print u"������ǩ�����{0}".format(ResRoReport.contents.res)
                if ResRoReport.contents.res == 0:
                    print u"������������ǩ�ɹ�������"
                else:
                    print u"������������ǩʧ�ܣ�����"
            print ResRoReport.contents.restype

def DealPeriodInventory(report):
    StarTime = 0
    if report.contents.type == RO_REPORT:
        ResRoReport = cast(report.contents.report,POINTER(RoReport))
        print ResRoReport.contents.restype
        if ResRoReport.contents.restype == INVENTORY:
            print u"����ǩ����{0}".format(ResRoReport.contents.tagid)
        elif ResRoReport.contents.restype == READ_OP:
            print u"����ǩ�����{0}".format(ResRoReport.contents.res)
            if ResRoReport.contents.res == 0:
                print u"����ǩbuf��{0}".format(ResRoReport.contents.opbuf)
            else:
                print u"��������ǩ��ʧ�ܣ�����"
        elif ResRoReport.contents.restype == WRITE_OP:
            if ResRoReport.contents.res == 0:
                print u"д��ǩ�ɹ������Ϊ��{0}".format(ResRoReport.contents.res)
            else:
                print u"��������ǩдʧ�ܣ�����"
    elif report.contents.type == EVENT_REPORT:
        ResEventReport = cast(report.contents.report,POINTER(EventReport))
        if ResEventReport.contents.type == START_OF_ROSPEC:
            StarTime = ResEventReport.contents.time
            #print u"�¼���ʼʱ�䣺{0}".format(StarTime)
        elif ResEventReport.contents.type == END_OF_ROSPEC:
            EndTime = ResEventReport.contents.time
            peroidTime = (EndTime - StarTime)/1000.0
            #print u"����������һ������ʱ�䣺{0}".format(peroidTime)

#�����豸
def connectReader(addr):
    newdevhandle = c_int(0) #�����豸�����ʼֵ
    if (InstLibrary.connectToReader(c_char_p(addr),byref(newdevhandle))) == 0:
        s_nDevHandle = newdevhandle
        return s_nDevHandle
    else:
        logging.info("connect failed!")
        return  False

def disconnectReader():
    InstLibrary.disconnectFromReader(s_nDevHandle)

#һ�����
def testOneShotInv():
    antid = AntIDSet()
    tAntId = antid.antID[0] = c_uint16(1)
    InstLibrary.startInventory(s_nDevHandle,byref(tAntId),CB(DealRoReport))

#ֹͣ�����Բ���
def stopPeroidInventory():
    time.sleep(15)
    InstLibrary.stopPeriodInventory(s_nDevHandle)

#�����Զ�/����ǩ
def testperoidRead(membank,StartPointer,length,passwd):
    antid = AntIDSet()
    tAntId = antid.antID[0] = c_uint16(1)
    peroid = 1  #�������ڣ���λms
    opparamlist = OpParamList()
    opparamlist.opcount = 1  #OP��������

    #���Ӷ�����
    tReadParam = ReadParam()
    tReadParam.membank = membank   #�ڴ����򣬱�ǩ��Ϣ��
    tReadParam.pointer = StartPointer  #��ʼ��ַ
    tReadParam.length = length #��������
    tReadParam.password = passwd # ��������

    opparamlist.element[0].optype = READ_OP
    opparamlist.element[0].op = cast(byref(tReadParam),c_void_p)
    opparamlist.element[0].protocol = EPC_GB

    #����һ���߳�ֹͣ�������
    quitThread = threading.Thread(target=stopPeroidInventory)
    quitThread.start()

    InstLibrary.startPeriodInventory(s_nDevHandle,byref(tAntId),peroid,byref(opparamlist),CB(DealPeriodInventory))
    quitThread.join()
#д����
def testWrite(membank,StartPointer,length,data,passwd):
    antid = AntIDSet()
    tAntId = antid.antID[0] = c_uint16(1)
    #opparamlist = OpParamList()
    #opparamlist.opcount = 2  #�ݲ�֧�ֶ�OP����
    opparam = OpParam()

    writeparam = WriteParam()
    writeparam.password = passwd  #0xffffffff
    writeparam.membank  = membank
    writeparam.pointer  = StartPointer
    writeparam.length   = length
    writeparam.writedata = data

    opparam.opparamelement.optype = WRITE_OP
    opparam.opparamelement.op = cast(byref(writeparam),c_void_p)
    opparam.opparamelement.protocol = EPC_GB
    #opparamlist.element[0].optype = WRITE_OP
    #opparamlist.element[0].op = cast(byref(writeparam),c_void_p)
    #opparamlist.element[0].protocol = EPC_GB

    InstLibrary.writeTag(s_nDevHandle, byref(tAntId), byref(opparam), CB(DealRoReport))

def testLockTag(lockarea,locktype,password):
    antid = AntIDSet()
    tAntId = antid.antID[0] = c_uint16(1)
    opparam = OpParam()

    locktag = LockParam()
    locktag.password = password
    locktag.lockarea = lockarea
    locktag.locktype = locktype

    opparam.opparamelement.optype = LOCK_OP
    opparam.opparamelement.op = cast(byref(locktag),c_void_p)
    opparam.opparamelement.protocol = EPC_GB

    InstLibrary.lockTag(s_nDevHandle, byref(tAntId), byref(opparam), CB(DealRoReport))

def testKillTag(password):
    antid = AntIDSet()
    tAntId = antid.antID[0] = c_uint16(1)
    opparam = OpParam()

    killparam = KillParam()
    killparam.password = password

    opparam.opparamelement.optype = KILL_OP
    opparam.opparamelement.op = cast(byref(killparam),c_void_p)
    opparam.opparamelement.protocol = EPC_GB

    InstLibrary.killTag(s_nDevHandle, byref(tAntId), byref(opparam), CB(DealRoReport))

def testBlockErase(membank,StartPointer,length,data,passwd):
    antid = AntIDSet()
    tAntId = antid.antID[0] = c_uint16(1)
    opparam = OpParam()

    blockeraseparam = BlockEraseParam()
    blockeraseparam.membank = membank   #�ڴ����򣬱�ǩ��Ϣ��
    blockeraseparam.pointer = StartPointer  #��ʼ��ַ
    blockeraseparam.length = length #��������
    blockeraseparam.password = passwd # ��������

    opparam.opparamelement.optype = BLOCK_ERASE_OP
    opparam.opparamelement.op = cast(byref(blockeraseparam),c_void_p)
    opparam.opparamelement.protocol = EPC_GB

    InstLibrary.blockEraseTag(s_nDevHandle, byref(tAntId), byref(opparam), CB(DealRoReport))

def testSetTransmitPower(antidindex,powerval):
    antid = AntIDSet()
    tAntId = antidindex
    InstLibrary.setTransmitPower(s_nDevHandle,tAntId,powerval)

def testGetTransmitPower(antidindex):
    antid = AntIDSet()
    tAntId = antidindex
    powerbuf = c_char_p()
    InstLibrary.getTransmitPower(s_nDevHandle,tAntId,byref(powerbuf))
    power = powerbuf
    return power

def checkTransmitPower(antidindex,powerval):
    testSetTransmitPower(antidindex,powerval)
    power = testGetTransmitPower(antidindex)
    print power
    print powerval
    powervalue = c_char_p(powerval)
    if power == powervalue:
        print u"�������óɹ�"
    else:
        print u"���������߹�������ʧ�ܣ�����"

def testFrequencyPower():

    powerlist = powerlist_paramer
    for powernum in powerlist:
        for i in range(20):
            #��ȡxml�ļ�
            tree = read_xml(testData_abspath)
            curr_data = find_nodes(tree, "Data")[0].text #��ȡ��ǰ����ֵ
            new_data = change_Power_ChannelIndex_text(curr_data,powernum,i) #�޸ķ��书�ʺ�Ƶ��ֵ
            #�޸Ľڵ��ı�
            change_node_text(find_nodes(tree, "Data"), new_data) #���޸ĵ�ֵ����ָ���Ľڵ�
            #���������ļ�
            write_xml(tree, configData_abspath)
            power = powernum
            channelIndex = i #��ǰƵ��
            curr_col = i #��ȡexcel��ǰ��

            #send *.xml�ļ�
            time.sleep(1)
            InstLibrary.sendLlrpMsgFromFile(s_nDevHandle, configData_abspath, None)
            threadlist = []
            CenterFrequency = Frequency + i*0.25
            #���������
            ReaderThread = threading.Thread(target=testperoidRead,args=(GB_CODE,1,6,0))
            threadlist.append(ReaderThread)

            #����һ���̵߳�����
            getThread = threading.Thread(target=Device_Test.testFrqPower,args=((CenterFrequency,33,power,channelIndex,curr_col)))
            threadlist.append(getThread)

            for thread_instance in threadlist:
                thread_instance.start()

            time.sleep(15)

#����ACPRֵ
def test_AllParame_ACPR_40():
    ModulationType_GB = ModulationType_GB_paramer  #ǰ����·���Ʒ�ʽ
    DataEncodeType_GB = DataEncodeType_GB_paramer  #���뷽ʽ
    ForwardReverseDataRate_GB = ForwardReverseDataRate_GB_40 #���ݴ�������
    #ModulationType_GB = [1,3]  #ǰ����·���Ʒ�ʽ
    #DataEncodeType_GB = [0,1,2,3]
    #ForwardReverseDataRate_GB = [(40,80),(40,128),(40,137),(40,160),(40,274),(40,320),(40,349),(40,640)] #���ݴ�������
    tree = read_xml(testData_abspath)
    curr_data = find_nodes(tree, "Data")[0].text #��ȡ��ǰ����ֵ
    power = get_power_text(curr_data) #��ȡ��ǰ����ֵ
    curr_num = 0 #���嵱ǰִ�е��ǵڼ������
    for ModulationType_text in ModulationType_GB:
        for DataEncodeType_text in DataEncodeType_GB:
            for ForwardReverseDataRate_text in ForwardReverseDataRate_GB:
                curr_num += 1
                new_data = change_Modulation_DataEncode_ForwardReverse_text(curr_data,ModulationType_text,DataEncodeType_text,ForwardReverseDataRate_text) #�޸Ĳ���ֵ
                #�޸Ľڵ��ı�
                change_node_text(find_nodes(tree, "Data"), new_data) #���޸ĵ�ֵ����ָ���Ľڵ�
                #���������ļ�
                write_xml(tree, configData_abspath)
                time.sleep(1)
                InstLibrary.sendLlrpMsgFromFile(s_nDevHandle, configData_abspath, None)
                print u"==========��ʼACPR����=========="
                if ModulationType_text == 1:
                    ModulationName = "DSB-ASK"
                elif ModulationType_text == 3:
                    ModulationName = "PR-ASK"

                if DataEncodeType_text == 0:
                    DataEncodeName = "FM0"
                elif DataEncodeType_text == 1:
                    DataEncodeName = "M2"
                elif DataEncodeType_text == 2:
                    DataEncodeName = "M4"
                elif DataEncodeType_text == 3:
                    DataEncodeName = "M8"


                print u"��ǰ�Ķ�������Ϊ:ǰ����·���Ʒ�ʽ:{0},���뷽ʽ:{1},���ݴ�������{2}".format(ModulationName,DataEncodeName,ForwardReverseDataRate_text)
                threadlist = []
                #���������
                ReaderThread = threading.Thread(target=testperoidRead,args=(GB_CODE,1,6,0))
                threadlist.append(ReaderThread)

                #ACPR����
                getThread = threading.Thread(target=Device_Test.testACPR,args=(ModulationType_text,curr_num))
                threadlist.append(getThread)

                for thread_instance in threadlist:
                    thread_instance.start()

                time.sleep(25)

def test_AllParame_ACPR_80():
    ModulationType_GB = ModulationType_GB_paramer  #ǰ����·���Ʒ�ʽ
    DataEncodeType_GB = DataEncodeType_GB_paramer  #���뷽ʽ
    ForwardReverseDataRate_GB = ForwardReverseDataRate_GB_80
    #ModulationType_GB = [1,3]  #ǰ����·���Ʒ�ʽ
    #DataEncodeType_GB = [0,1,2,3]
    #ForwardReverseDataRate_GB = [(80,80),(80,128),(80,137),(80,160),(80,274),(80,320),(80,349),(80,640)]
    tree = read_xml(testData_abspath)
    curr_data = find_nodes(tree, "Data")[0].text #��ȡ��ǰ����ֵ
    power = get_power_text(curr_data) #��ȡ��ǰ����ֵ
    curr_num = 0 #���嵱ǰִ�е��ǵڼ������
    for ModulationType_text in ModulationType_GB:
        for DataEncodeType_text in DataEncodeType_GB:
            for ForwardReverseDataRate_text in ForwardReverseDataRate_GB:
                curr_num += 1
                new_data = change_Modulation_DataEncode_ForwardReverse_text(curr_data,ModulationType_text,DataEncodeType_text,ForwardReverseDataRate_text) #�޸Ĳ���ֵ
                #�޸Ľڵ��ı�
                change_node_text(find_nodes(tree, "Data"), new_data) #���޸ĵ�ֵ����ָ���Ľڵ�
                #���������ļ�
                write_xml(tree, configData_abspath)
                time.sleep(1)
                InstLibrary.sendLlrpMsgFromFile(s_nDevHandle, configData_abspath, None)
                print u"==========��ʼACPR����=========="
                if ModulationType_text == 1:
                    ModulationName = "DSB-ASK"
                elif ModulationType_text == 3:
                    ModulationName = "PR-ASK"

                if DataEncodeType_text == 0:
                    DataEncodeName = "FM0"
                elif DataEncodeType_text == 1:
                    DataEncodeName = "M2"
                elif DataEncodeType_text == 2:
                    DataEncodeName = "M4"
                elif DataEncodeType_text == 3:
                    DataEncodeName = "M8"


                print u"��ǰ�Ķ�������Ϊ:ǰ����·���Ʒ�ʽ:{0},���뷽ʽ:{1},���ݴ�������{2}".format(ModulationName,DataEncodeName,ForwardReverseDataRate_text)
                threadlist = []
                #���������
                ReaderThread = threading.Thread(target=testperoidRead,args=(GB_CODE,1,6,0))
                threadlist.append(ReaderThread)

                #ACPR����
                getThread = threading.Thread(target=Device_Test.testACPR_80,args=(ModulationType_text,curr_num))
                threadlist.append(getThread)

                for thread_instance in threadlist:
                    thread_instance.start()

                time.sleep(25)

#����Э��һ����
def test_Protocol_Conformance_80():
    Device_Test.set_protocol_conformance() #����ʾ��������
    time.sleep(3)

    ModulationType_GB = ModulationType_GB_paramer  #ǰ����·���Ʒ�ʽ
    DataEncodeType_GB = DataEncodeType_GB_paramer  #���뷽ʽ
    ModulationDepth_GB = ModulationDepth_GB_paramer #�������
    ForwardReverseDataRate_GB = ForwardReverseDataRate_GB_80

    tree = read_xml(testData_abspath)
    curr_data = find_nodes(tree, "Data")[0].text #��ȡ��ǰ����ֵ
    power = get_power_text(curr_data) #��ȡ��ǰ����ֵ
    curr_num = 0 #���嵱ǰִ�е��ǵڼ������
    for ModulationDepth_text in ModulationDepth_GB:
        for ModulationType_text in ModulationType_GB:
            for DataEncodeType_text in DataEncodeType_GB:
                for ForwardReverseDataRate_text in ForwardReverseDataRate_GB:
                    curr_num += 1
                    new_data = change_Modulation_DataEncode_ForwardReverse_text(curr_data,ModulationType_text,DataEncodeType_text,ForwardReverseDataRate_text,ModulationDepth_text) #�޸Ĳ���ֵ
                    #�޸Ľڵ��ı�
                    change_node_text(find_nodes(tree, "Data"), new_data) #���޸ĵ�ֵ����ָ���Ľڵ�
                    #���������ļ�
                    write_xml(tree, configData_abspath)
                    time.sleep(1)
                    InstLibrary.sendLlrpMsgFromFile(s_nDevHandle, configData_abspath, None)
                    print u"==========��ʼ����=========="
                    if ModulationType_text == 1:
                        ModulationName = "DSB-ASK"
                    elif ModulationType_text == 3:
                        ModulationName = "PR-ASK"

                    if DataEncodeType_text == 0:
                        DataEncodeName = "FM0"
                    elif DataEncodeType_text == 1:
                        DataEncodeName = "M2"
                    elif DataEncodeType_text == 2:
                        DataEncodeName = "M4"
                    elif DataEncodeType_text == 3:
                        DataEncodeName = "M8"


                    print u"��ǰ�Ķ�������Ϊ:ǰ����·���Ʒ�ʽ:{0},���뷽ʽ:{1},���ݴ�������{2},�������{3}".format(ModulationName,DataEncodeName,ForwardReverseDataRate_text,ModulationDepth_text)
                    filename = ModulationName+DataEncodeName+ForwardReverseDataRate_text+ModulationDepth_text
                    testOneShotInv() #�������
                    time.sleep(3)
                    Device_Test.Save_waveform(filename)

def test_Protocol_Conformance_40():
    Device_Test.set_protocol_conformance() #����ʾ��������
    time.sleep(3)

    ModulationType_GB = ModulationType_GB_paramer  #ǰ����·���Ʒ�ʽ
    DataEncodeType_GB = DataEncodeType_GB_paramer  #���뷽ʽ
    ModulationDepth_GB = ModulationDepth_GB_paramer #�������
    ForwardReverseDataRate_GB = ForwardReverseDataRate_GB_40

    tree = read_xml(testData_abspath)
    curr_data = find_nodes(tree, "Data")[0].text #��ȡ��ǰ����ֵ
    power = get_power_text(curr_data) #��ȡ��ǰ����ֵ
    curr_num = 0 #���嵱ǰִ�е��ǵڼ������
    for ModulationDepth_text in ModulationDepth_GB:
        for ModulationType_text in ModulationType_GB:
            for DataEncodeType_text in DataEncodeType_GB:
                for ForwardReverseDataRate_text in ForwardReverseDataRate_GB:
                    curr_num += 1
                    new_data = change_Modulation_DataEncode_ForwardReverse_text(curr_data,ModulationType_text,DataEncodeType_text,ForwardReverseDataRate_text,ModulationDepth_text) #�޸Ĳ���ֵ
                    #�޸Ľڵ��ı�
                    change_node_text(find_nodes(tree, "Data"), new_data) #���޸ĵ�ֵ����ָ���Ľڵ�
                    #���������ļ�
                    write_xml(tree, configData_abspath)
                    time.sleep(1)
                    InstLibrary.sendLlrpMsgFromFile(s_nDevHandle, configData_abspath, None)
                    print u"==========��ʼ����=========="
                    if ModulationType_text == 1:
                        ModulationName = "DSB-ASK"
                    elif ModulationType_text == 3:
                        ModulationName = "PR-ASK"

                    if DataEncodeType_text == 0:
                        DataEncodeName = "FM0"
                    elif DataEncodeType_text == 1:
                        DataEncodeName = "M2"
                    elif DataEncodeType_text == 2:
                        DataEncodeName = "M4"
                    elif DataEncodeType_text == 3:
                        DataEncodeName = "M8"


                    print u"��ǰ�Ķ�������Ϊ:ǰ����·���Ʒ�ʽ:{0},���뷽ʽ:{1},���ݴ�������{2},�������{3}".format(ModulationName,DataEncodeName,ForwardReverseDataRate_text,ModulationDepth_text)
                    filename = ModulationName+DataEncodeName+ForwardReverseDataRate_text+ModulationDepth_text
                    testOneShotInv() #�������
                    time.sleep(3)
                    Device_Test.Save_waveform(filename)

if __name__ == '__main__':
    dllfile = 'calldll/did.dll'
    InstLibrary = windll.LoadLibrary(dllfile)
    InstLibrary.initLib(1)
    s_nDevHandle = connectReader("192.168.1.203") #�Ķ�����ַ
    CB = WINFUNCTYPE(None, POINTER(ReportRes))
    #testFrequencyPower() #���Թ���ֵ
    #test_AllParame_ACPR_40() #����ACPR
    #test_AllParame_ACPR_80()
    test_Protocol_Conformance_80() #���ɲ��β�����Ϊcsv�ļ�
    WaveformData_Analyse.analyse_80_waveform() #���������csv�����ļ�
    test_Protocol_Conformance_40()
    WaveformData_Analyse.analyse_40_waveform()