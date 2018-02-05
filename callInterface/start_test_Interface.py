# -*- coding: GB18030 -*-
from ctypes import *
from common.structfile import *
import logging,threading,time
from common.constant import *
from aglient_control import Device_Test,Instrument_Control,CONSTANTS,WaveformData_Analyse
from common.Opxml import *
import os
import ConfigParser

#获取run_main的路径
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
            print u"正在操作标签！"
            if ResRoReport.contents.restype == INVENTORY:
                print u"清点标签内容{0}".format(ResRoReport.contents.tagid)
            elif ResRoReport.contents.restype == READ_OP:
                print u"读标签标签结果：{0}".format(ResRoReport.contents.res)
                if ResRoReport.contents.res == 0:
                    print u"读标签标签buf：{0}".format(ResRoReport.contents.opbuf)
            elif ResRoReport.contents.restype == WRITE_OP:
                print u"写标签结果：{0}".format(ResRoReport.contents.res)
                if ResRoReport.contents.res == 0:
                    print u"！！！写标签成功！！！"
                else:
                    print u"！！！写标签失败！！！"
            elif ResRoReport.contents.restype == LOCK_OP:
                print u"锁标签结果：{0}".format(ResRoReport.contents.res)
                if ResRoReport.contents.res == 0:
                    print u"！！！锁标签成功！！！"
                else:
                    print u"！！！锁标签失败！！！"
            elif ResRoReport.contents.restype == KILL_OP:
                print u"擦除标签结果：{0}".format(ResRoReport.contents.res)
                if ResRoReport.contents.res == 0:
                    print u"！！！杀死标签成功！！！"
                else:
                    print u"！！！杀死标签失败！！！"
            elif ResRoReport.contents.restype == BLOCK_ERASE_OP:
                print u"擦除标签结果：{0}".format(ResRoReport.contents.res)
                if ResRoReport.contents.res == 0:
                    print u"！！！擦除标签成功！！！"
                else:
                    print u"！！！擦除标签失败！！！"
            print ResRoReport.contents.restype

def DealPeriodInventory(report):
    StarTime = 0
    if report.contents.type == RO_REPORT:
        ResRoReport = cast(report.contents.report,POINTER(RoReport))
        print ResRoReport.contents.restype
        if ResRoReport.contents.restype == INVENTORY:
            print u"清点标签内容{0}".format(ResRoReport.contents.tagid)
        elif ResRoReport.contents.restype == READ_OP:
            print u"读标签结果：{0}".format(ResRoReport.contents.res)
            if ResRoReport.contents.res == 0:
                print u"读标签buf：{0}".format(ResRoReport.contents.opbuf)
            else:
                print u"！！！标签读失败！！！"
        elif ResRoReport.contents.restype == WRITE_OP:
            if ResRoReport.contents.res == 0:
                print u"写标签成功，结果为：{0}".format(ResRoReport.contents.res)
            else:
                print u"！！！标签写失败！！！"
    elif report.contents.type == EVENT_REPORT:
        ResEventReport = cast(report.contents.report,POINTER(EventReport))
        if ResEventReport.contents.type == START_OF_ROSPEC:
            StarTime = ResEventReport.contents.time
            #print u"事件开始时间：{0}".format(StarTime)
        elif ResEventReport.contents.type == END_OF_ROSPEC:
            EndTime = ResEventReport.contents.time
            peroidTime = (EndTime - StarTime)/1000.0
            #print u"结束操作，一共持续时间：{0}".format(peroidTime)

#连接设备
def connectReader(addr):
    newdevhandle = c_int(0) #设置设备句柄初始值
    if (InstLibrary.connectToReader(c_char_p(addr),byref(newdevhandle))) == 0:
        s_nDevHandle = newdevhandle
        return s_nDevHandle
    else:
        logging.info("connect failed!")
        return  False

def disconnectReader():
    InstLibrary.disconnectFromReader(s_nDevHandle)

#一次清点
def testOneShotInv():
    antid = AntIDSet()
    tAntId = antid.antID[0] = c_uint16(1)
    InstLibrary.startInventory(s_nDevHandle,byref(tAntId),CB(DealRoReport))

#停止周期性操作
def stopPeroidInventory():
    time.sleep(15)
    InstLibrary.stopPeriodInventory(s_nDevHandle)

#周期性读/清点标签
def testperoidRead(membank,StartPointer,length,passwd):
    antid = AntIDSet()
    tAntId = antid.antID[0] = c_uint16(1)
    peroid = 1  #操作周期，单位ms
    opparamlist = OpParamList()
    opparamlist.opcount = 1  #OP操作数量

    #添加读操作
    tReadParam = ReadParam()
    tReadParam.membank = membank   #内存区域，标签信息区
    tReadParam.pointer = StartPointer  #起始地址
    tReadParam.length = length #操作长度
    tReadParam.password = passwd # 操作密码

    opparamlist.element[0].optype = READ_OP
    opparamlist.element[0].op = cast(byref(tReadParam),c_void_p)
    opparamlist.element[0].protocol = EPC_GB

    #创建一个线程停止周期清点
    quitThread = threading.Thread(target=stopPeroidInventory)
    quitThread.start()

    InstLibrary.startPeriodInventory(s_nDevHandle,byref(tAntId),peroid,byref(opparamlist),CB(DealPeriodInventory))
    quitThread.join()
#写操作
def testWrite(membank,StartPointer,length,data,passwd):
    antid = AntIDSet()
    tAntId = antid.antID[0] = c_uint16(1)
    #opparamlist = OpParamList()
    #opparamlist.opcount = 2  #暂不支持多OP操作
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
    blockeraseparam.membank = membank   #内存区域，标签信息区
    blockeraseparam.pointer = StartPointer  #起始地址
    blockeraseparam.length = length #操作长度
    blockeraseparam.password = passwd # 操作密码

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
        print u"天线设置成功"
    else:
        print u"！！！天线功率设置失败！！！"

def testFrequencyPower():

    powerlist = powerlist_paramer
    for powernum in powerlist:
        for i in range(20):
            #读取xml文件
            tree = read_xml(testData_abspath)
            curr_data = find_nodes(tree, "Data")[0].text #获取当前参数值
            new_data = change_Power_ChannelIndex_text(curr_data,powernum,i) #修改发射功率和频点值
            #修改节点文本
            change_node_text(find_nodes(tree, "Data"), new_data) #将修改的值插入指定的节点
            #输出到结果文件
            write_xml(tree, configData_abspath)
            power = powernum
            channelIndex = i #当前频点
            curr_col = i #获取excel当前列

            #send *.xml文件
            time.sleep(1)
            InstLibrary.sendLlrpMsgFromFile(s_nDevHandle, configData_abspath, None)
            threadlist = []
            CenterFrequency = Frequency + i*0.25
            #周期性清点
            ReaderThread = threading.Thread(target=testperoidRead,args=(GB_CODE,1,6,0))
            threadlist.append(ReaderThread)

            #创建一个线程调仪器
            getThread = threading.Thread(target=Device_Test.testFrqPower,args=((CenterFrequency,33,power,channelIndex,curr_col)))
            threadlist.append(getThread)

            for thread_instance in threadlist:
                thread_instance.start()

            time.sleep(15)

#测试ACPR值
def test_AllParame_ACPR_40():
    ModulationType_GB = ModulationType_GB_paramer  #前向链路调制方式
    DataEncodeType_GB = DataEncodeType_GB_paramer  #编码方式
    ForwardReverseDataRate_GB = ForwardReverseDataRate_GB_40 #数据传输速率
    #ModulationType_GB = [1,3]  #前向链路调制方式
    #DataEncodeType_GB = [0,1,2,3]
    #ForwardReverseDataRate_GB = [(40,80),(40,128),(40,137),(40,160),(40,274),(40,320),(40,349),(40,640)] #数据传输速率
    tree = read_xml(testData_abspath)
    curr_data = find_nodes(tree, "Data")[0].text #获取当前参数值
    power = get_power_text(curr_data) #获取当前功率值
    curr_num = 0 #定义当前执行的是第几组参数
    for ModulationType_text in ModulationType_GB:
        for DataEncodeType_text in DataEncodeType_GB:
            for ForwardReverseDataRate_text in ForwardReverseDataRate_GB:
                curr_num += 1
                new_data = change_Modulation_DataEncode_ForwardReverse_text(curr_data,ModulationType_text,DataEncodeType_text,ForwardReverseDataRate_text) #修改参数值
                #修改节点文本
                change_node_text(find_nodes(tree, "Data"), new_data) #将修改的值插入指定的节点
                #输出到结果文件
                write_xml(tree, configData_abspath)
                time.sleep(1)
                InstLibrary.sendLlrpMsgFromFile(s_nDevHandle, configData_abspath, None)
                print u"==========开始ACPR测试=========="
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


                print u"当前阅读器参数为:前向链路调制方式:{0},编码方式:{1},数据传输速率{2}".format(ModulationName,DataEncodeName,ForwardReverseDataRate_text)
                threadlist = []
                #周期性清点
                ReaderThread = threading.Thread(target=testperoidRead,args=(GB_CODE,1,6,0))
                threadlist.append(ReaderThread)

                #ACPR测试
                getThread = threading.Thread(target=Device_Test.testACPR,args=(ModulationType_text,curr_num))
                threadlist.append(getThread)

                for thread_instance in threadlist:
                    thread_instance.start()

                time.sleep(25)

def test_AllParame_ACPR_80():
    ModulationType_GB = ModulationType_GB_paramer  #前向链路调制方式
    DataEncodeType_GB = DataEncodeType_GB_paramer  #编码方式
    ForwardReverseDataRate_GB = ForwardReverseDataRate_GB_80
    #ModulationType_GB = [1,3]  #前向链路调制方式
    #DataEncodeType_GB = [0,1,2,3]
    #ForwardReverseDataRate_GB = [(80,80),(80,128),(80,137),(80,160),(80,274),(80,320),(80,349),(80,640)]
    tree = read_xml(testData_abspath)
    curr_data = find_nodes(tree, "Data")[0].text #获取当前参数值
    power = get_power_text(curr_data) #获取当前功率值
    curr_num = 0 #定义当前执行的是第几组参数
    for ModulationType_text in ModulationType_GB:
        for DataEncodeType_text in DataEncodeType_GB:
            for ForwardReverseDataRate_text in ForwardReverseDataRate_GB:
                curr_num += 1
                new_data = change_Modulation_DataEncode_ForwardReverse_text(curr_data,ModulationType_text,DataEncodeType_text,ForwardReverseDataRate_text) #修改参数值
                #修改节点文本
                change_node_text(find_nodes(tree, "Data"), new_data) #将修改的值插入指定的节点
                #输出到结果文件
                write_xml(tree, configData_abspath)
                time.sleep(1)
                InstLibrary.sendLlrpMsgFromFile(s_nDevHandle, configData_abspath, None)
                print u"==========开始ACPR测试=========="
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


                print u"当前阅读器参数为:前向链路调制方式:{0},编码方式:{1},数据传输速率{2}".format(ModulationName,DataEncodeName,ForwardReverseDataRate_text)
                threadlist = []
                #周期性清点
                ReaderThread = threading.Thread(target=testperoidRead,args=(GB_CODE,1,6,0))
                threadlist.append(ReaderThread)

                #ACPR测试
                getThread = threading.Thread(target=Device_Test.testACPR_80,args=(ModulationType_text,curr_num))
                threadlist.append(getThread)

                for thread_instance in threadlist:
                    thread_instance.start()

                time.sleep(25)

#测试协议一致性
def test_Protocol_Conformance_80():
    Device_Test.set_protocol_conformance() #配置示波器参数
    time.sleep(3)

    ModulationType_GB = ModulationType_GB_paramer  #前向链路调制方式
    DataEncodeType_GB = DataEncodeType_GB_paramer  #编码方式
    ModulationDepth_GB = ModulationDepth_GB_paramer #调制深度
    ForwardReverseDataRate_GB = ForwardReverseDataRate_GB_80

    tree = read_xml(testData_abspath)
    curr_data = find_nodes(tree, "Data")[0].text #获取当前参数值
    power = get_power_text(curr_data) #获取当前功率值
    curr_num = 0 #定义当前执行的是第几组参数
    for ModulationDepth_text in ModulationDepth_GB:
        for ModulationType_text in ModulationType_GB:
            for DataEncodeType_text in DataEncodeType_GB:
                for ForwardReverseDataRate_text in ForwardReverseDataRate_GB:
                    curr_num += 1
                    new_data = change_Modulation_DataEncode_ForwardReverse_text(curr_data,ModulationType_text,DataEncodeType_text,ForwardReverseDataRate_text,ModulationDepth_text) #修改参数值
                    #修改节点文本
                    change_node_text(find_nodes(tree, "Data"), new_data) #将修改的值插入指定的节点
                    #输出到结果文件
                    write_xml(tree, configData_abspath)
                    time.sleep(1)
                    InstLibrary.sendLlrpMsgFromFile(s_nDevHandle, configData_abspath, None)
                    print u"==========开始测试=========="
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


                    print u"当前阅读器参数为:前向链路调制方式:{0},编码方式:{1},数据传输速率{2},调制深度{3}".format(ModulationName,DataEncodeName,ForwardReverseDataRate_text,ModulationDepth_text)
                    filename = ModulationName+DataEncodeName+ForwardReverseDataRate_text+ModulationDepth_text
                    testOneShotInv() #单次清点
                    time.sleep(3)
                    Device_Test.Save_waveform(filename)

def test_Protocol_Conformance_40():
    Device_Test.set_protocol_conformance() #配置示波器参数
    time.sleep(3)

    ModulationType_GB = ModulationType_GB_paramer  #前向链路调制方式
    DataEncodeType_GB = DataEncodeType_GB_paramer  #编码方式
    ModulationDepth_GB = ModulationDepth_GB_paramer #调制深度
    ForwardReverseDataRate_GB = ForwardReverseDataRate_GB_40

    tree = read_xml(testData_abspath)
    curr_data = find_nodes(tree, "Data")[0].text #获取当前参数值
    power = get_power_text(curr_data) #获取当前功率值
    curr_num = 0 #定义当前执行的是第几组参数
    for ModulationDepth_text in ModulationDepth_GB:
        for ModulationType_text in ModulationType_GB:
            for DataEncodeType_text in DataEncodeType_GB:
                for ForwardReverseDataRate_text in ForwardReverseDataRate_GB:
                    curr_num += 1
                    new_data = change_Modulation_DataEncode_ForwardReverse_text(curr_data,ModulationType_text,DataEncodeType_text,ForwardReverseDataRate_text,ModulationDepth_text) #修改参数值
                    #修改节点文本
                    change_node_text(find_nodes(tree, "Data"), new_data) #将修改的值插入指定的节点
                    #输出到结果文件
                    write_xml(tree, configData_abspath)
                    time.sleep(1)
                    InstLibrary.sendLlrpMsgFromFile(s_nDevHandle, configData_abspath, None)
                    print u"==========开始测试=========="
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


                    print u"当前阅读器参数为:前向链路调制方式:{0},编码方式:{1},数据传输速率{2},调制深度{3}".format(ModulationName,DataEncodeName,ForwardReverseDataRate_text,ModulationDepth_text)
                    filename = ModulationName+DataEncodeName+ForwardReverseDataRate_text+ModulationDepth_text
                    testOneShotInv() #单次清点
                    time.sleep(3)
                    Device_Test.Save_waveform(filename)

if __name__ == '__main__':
    dllfile = 'calldll/did.dll'
    InstLibrary = windll.LoadLibrary(dllfile)
    InstLibrary.initLib(1)
    s_nDevHandle = connectReader("192.168.1.203") #阅读器地址
    CB = WINFUNCTYPE(None, POINTER(ReportRes))
    #testFrequencyPower() #测试功率值
    #test_AllParame_ACPR_40() #测试ACPR
    #test_AllParame_ACPR_80()
    test_Protocol_Conformance_80() #生成波形并保存为csv文件
    WaveformData_Analyse.analyse_80_waveform() #分析保存的csv波形文件
    test_Protocol_Conformance_40()
    WaveformData_Analyse.analyse_40_waveform()
