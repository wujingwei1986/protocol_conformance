# -*- coding: GB18030 -*-
import visa,time
from pyvisa.resources.usb import USBInstrument
from pyvisa.constants import  *
from CONSTANTS import *

class Agilent(object):

    def OpenInstrument(self):
        rm = visa.ResourceManager()
        self.my_instrument = rm.open_resource('TCPIP0::192.168.1.137::inst0::INSTR')
        self.my_instrument.timeout = 5000
        print self.my_instrument.query('*IDN?')  #get device info
        return self.my_instrument

    def Initialize(self):
        self.my_instrument.write('*CLS')
        self.my_instrument.write('*RST')# clear device

    # set device mode
    def SA_SetMode(self,nMode):
        if nMode==1:
            self.my_instrument.write(':INST:SEL SA')
        elif nMode==2:
            self.my_instrument.write(':INST:SEL VSA89601')
        else:
            print "set device mode error!"

    #设置功率补偿
    def SA_SetOffset(self,fOffset):
        '''
        :param fOffset:为频谱分析仪对输入信号的功率补偿，单位是dbm
        :return:None
        '''
        offset = ':DISP:WIND:TRAC:Y:RLEV:OFFS ' + str(fOffset)
        self.my_instrument.write(offset)

    def SA_SetRFAtten(self):
        #内部衰减设置为自动
        self.my_instrument.write(':SENS:POW:ATT 10')

    def SA_SetDetector(self,nType):
        '''
        :param nType: Type表示检波方式，1表示峰值检波（正峰值检波），2表示有效值检波（RMS）。
        :return:None
        '''
        if nType==1:
            self.my_instrument.write(':SENS:DET:AUTO OFF')
            self.my_instrument.write(':SENS:DET POS')
        elif nType==2:
            self.my_instrument.write(':SENS:DET:AUTO OFF')
            self.my_instrument.write(':SENS:DET AVE')
        else:
            print u"检波方式错误！"

    #初始化仪器
    def SAInit(self):
        self.SA_Reset()
        self.SA_SetMode(1)
        self.SA_SetOffset(fOffset)
        #self.SA_SetRFAtten()
        self.SA_SetDetector(1)

    #发射频率范围和发射信号平坦度测试
    #选择频谱仪的测量模式为连续扫频模式
    def SA_SetMeas(self,nMode):
        '''
        :param nMode:表示频谱分析仪的模式，1表示扫频模式，2表示OBW模式，3表示ACP模式
        :return:None
        '''
        if nMode==1:
            self.my_instrument.write('CONF:SAN:NDEF')
        elif nMode==2:
            self.my_instrument.write('CONF:OBW:NDEF')
        elif nMode==3:
            self.my_instrument.write('CONF:ACP:NDEF')

    #设置ACPR测量参数
    def SA_SetACPR(self):
        #关闭平均值
        self.my_instrument.write(':SENS:ACP:AVER:STAT OFF')
        time.sleep(0.5)
        self.SA_SetTraceMode(1)
        time.sleep(0.5)
        #扫频时间和扫频点数
        self.my_instrument.write(':SENS:ACP:SWE:TIME 500ms')
        time.sleep(0.5)
        self.my_instrument.write(':SENS:OBW:SWE:POIN 1001')
        time.sleep(0.5)
        #主信道和邻接信道
        self.my_instrument.write(':SENS:ACP:BAND:INT 250Khz')
        time.sleep(0.5)
        self.my_instrument.write(':SENS:ACP:OFFS:LIST:STAT ON,ON,OFF,OFF,OFF,OFF')
        time.sleep(0.5)
        self.my_instrument.write(':SENS:ACP:OFFS:LIST:BAND 250KHz,250KHz,0,0,0,0')
        time.sleep(0.5)
        #250KHz,250KHz,0,0,0,0
        self.my_instrument.write(':SENS:ACP:OFFS:LIST:FREQ 250KHz,500KHz,0,0,0,0')
        time.sleep(1)
        #250KHz,500KHz,0,0,0,0
        #前面配置完成后才能执行下面指令
        #设置扫频带宽和测量带宽
        self.my_instrument.write(':SENS:ACP:FREQ:SPAN 1.5MHz')
        time.sleep(0.5)
        self.my_instrument.write(':SENS:ACP:BAND 10KHz')
        time.sleep(0.5)
        self.SA_SetRFAtten()
        time.sleep(0.5)
        self.SA_SetCenterFrequency(ACPR_fCenterFrequency) #设置ACPR中心频点，一般为10，对应值为842.625
        self.SA_SetOffset(fOffset)


    #设置中心频点
    def SA_SetCenterFrequency(self,fCenterFrequency):
        '''
        :param fCenterFrequency:为频谱的中心频率，单位是MHz
        :return:None
        '''
        CenterFrequency = ':SENS:FREQ:CENT ' + str(fCenterFrequency) + 'MHz'
        self.my_instrument.write(CenterFrequency)

    #设置频谱带宽
    def SA_SetSpan(self,fSpan):
        '''
        :param fSpan:为频谱的带宽，单位是MHz
        :return:None
        '''
        span = ':SENS:FREQ:SPAN ' + str(fSpan) + 'MHz'
        self.my_instrument.write(span)

    #设置分辨率带宽
    def SA_SetRBW(self,fRBW):
        '''
        :param fRBW:为频谱分析仪的分辨率带宽即测量带宽，单位是KHz。
                最小值一般是1KHz，输入值小于等于0表示测量带宽为自动
        :return:
        '''
        if fRBW<=0:
            self.my_instrument.write('BAND:AUTO ON')
        else:
            rbw = 'BAND ' + str(fRBW) + 'KHz'
            self.my_instrument.write('BAND:AUTO OFF')
            self.my_instrument.write(rbw)

    #设置频谱仪为最大值保持模式
    def SA_SetTraceMode(self,nMode):
        '''
        :param nMode: 表示Trace方式，0表示ClearWrite，1表示最大值保持
        :return:None
        '''
        if nMode==0:
            self.my_instrument.write(':TRAC:MODE WRIT')
        elif nMode==1:
            self.my_instrument.write(':TRAC:MODE MAXH')


    #设置频谱仪为连续扫频模式
    def SA_SetCont(self,nMode):
        '''
        :param nMode:表示扫频方式，0表示单扫，1表示连续扫
        :return:None
        '''
        if nMode==0:
            self.my_instrument.write('INIT:CONT OFF')
        elif nMode==1:
            self.my_instrument.write('INIT:CONT ON')
            self.my_instrument.write('INIT;*WAI')

    #设置频域的起点
    def SA_SetStart(self,fStart):
        '''
        :param fStart:为频谱上频域的起点，单位是MHz
        :return:None
        '''
        start = ':SENS:FREQ:STAR ' + fStart +'MHz'
        self.my_instrument.write(start)

    #设置频域的终点
    def SA_SetStop(self,fStop):
        '''
        :param fStop:为频谱上频域的终点，单位是MHz
        :return:
        '''
        stop = ':SENS:FREQ:STOP ' + fStop +'MHz'
        self.my_instrument.write(stop)

    #设置功率参考值
    def SA_SetReferenceLevel(self,fRefer):
        '''
        :param fRefer: 为功率参考上限值，单位是dbm
        :return:
        '''
        refer = ':DISP:WIND:TRAC:Y:RLEV ' + str(fRefer)
        self.my_instrument.write(refer)

    #设置视频带宽
    def SA_SetVBW(self,fVBW):
        '''
        :param fVBW:为频谱分析仪的视频带宽，单位是KHz。
                输入值小于等于0表示视频带宽为自动
        :return:
        '''
        if fVBW<=0:
            self.my_instrument.write('BAND:VID:AUTO ON')
        else:
            vbw = 'BAND:VID ' + fVBW + 'KHz'
            self.my_instrument.write('BAND:VID:AUTO OFF')
            self.my_instrument.write(vbw)

    #配置OBW测量参数
    def SA_SetOBW(self,nSpan,nRBW):
        '''
        :param nSpan: 表示测量OBW时频域的宽度
        :param nRBW:表示测量OBW时使用的测量带宽，单位KHz
        :return:None
        '''
        #打开最大值保持
        self.my_instrument.write(':OBW:MAXH ON')
        #关闭平均值
        self.my_instrument.write(':SENS:OBW:AVER:STAT OFF')
        #扫频时间和扫频点数
        self.my_instrument.write(':SENS:ACP:SWE:TIME 500ms')
        self.my_instrument.write(':SENS:OBW:SWE:POIN 1001')
        #设置扫频带宽 :SENS:OBW:FREQ:SPAN 2MHz
        span = ':SENS:OBW:FREQ:SPAN '+ str(nSpan) + 'MHz'
        self.my_instrument.write(span)
        #能量百分比
        self.my_instrument.write(':OBW:PERC 99')
        #设置OBW分辨率带宽 :SENS:OBW:BAND 10KHz
        rbw = ':SENS:OBW:BAND ' +  str(nRBW) + 'KHz'
        self.my_instrument.write(rbw)

    #读取频谱中Mark点的频率值和功率值
    #def SA_GetMark(fFreq, fAmpt):
        '''
        :param fFreq: fFreq是频谱中峰值点的频率，单位是MHz
        :param fAmpt: fAmpt是频谱中峰值点的功率值，单位是dbm
        :return:
        '''

        #self.my_instrument.query('CALC:MARK:X?;*WAI')
        #self.my_instrument.query('CALC:MARK:Y?;*WAI')

    #获得当前频谱上所有峰值点的频率和功率
    def SA_PeakSearch(self):
        self.my_instrument.write('CALC:MARK:PEAK:EXC:STAT ON')
        time.sleep(0.5)
        self.my_instrument.write('CALC:MARK:PEAK:EXC 6')
        time.sleep(0.5)
        self.my_instrument.write('CALC:MARK:PEAK:THR:STAT OFF')
        time.sleep(0.5)
        self.my_instrument.write('CALC:MARK:STAT ON')
        time.sleep(0.5)
        self.my_instrument.write('CALC:MARK:TRAC 1')
        time.sleep(0.5)
        self.my_instrument.write('CALC:MARK:MAX')
        time.sleep(0.5)
        self.my_instrument.write('CALC:MARK:MAX:LEFT')
        time.sleep(0.5)
        self.my_instrument.write('CALC:MARK:MAX:RIGH')
        time.sleep(0.5)

    def SA_GetMark(self):
        x = self.my_instrument.query('CALC:MARK:X?;*WAI')
        y = self.my_instrument.query('CALC:MARK:Y?;*WAI')
        return x,y

    #读取邻道功率泄漏比ACPR的值
    def SA_GetACPRPower(self):
        return self.my_instrument.query('FETC:ACP?')


    #读取占用带宽OBW
    def SA_GetOBW(self):
        return self.my_instrument.query('FETC:OBW?')

    #示波器配置
    def Set_Analyze(self):
        #config f1
        #self.my_instrument.write(":FUNCTION1:ADD CHANNEL1,CHANNEL2")
        self.my_instrument.write(":FUNCtion1:ABSolute CHANnel4") #operator为Absolute Value，Source channel4
        #print self.my_instrument.query(":FUNCtion1?")
        time.sleep(0.5)
        #config f2 parameters
        self.my_instrument.write("FUNCtion2:DISPlay ON")
        time.sleep(0.5)
        self.my_instrument.write(":FUNCtion2:LOWPass FUNCtion1,2E6") #低通，source为Function1，bandwidth 2MHZ
        time.sleep(0.5)
        self.my_instrument.write("FUNCtion2:VERTical MANual") #vertical手动模式
        time.sleep(0.5)
        self.my_instrument.write(":FUNCtion2:VERTical:RANGe 4000E-3") #与scale是8倍的关系：scale*8=Range
        time.sleep(0.5)
        self.my_instrument.write(":FUNCtion2:VERTical:OFFSet 300E-3")
        time.sleep(0.5)
        scale = self.my_instrument.query(":FUNCtion2:VERTical:RANGe?")
        while float(scale) != 4.0:
            self.my_instrument.write(":FUNCtion2:VERTical:RANGe 4000E-3")
            time.sleep(0.5)

        offset = self.my_instrument.query(":FUNCtion2:VERTical:OFFSet?")
        while float(offset)*1000 != 300:
            self.my_instrument.write(":FUNCtion2:VERTical:OFFSet 300E-3")

    def Set_trigger(self):
        self.my_instrument.write(":TRIGger:MODE EDGE")
        time.sleep(0.5)
        self.my_instrument.write(":TRIGger:EDGE:SOURce CHANnel4")
        time.sleep(0.5)
        self.my_instrument.write(":TRIGger:LEVel CHANnel4,480E-3")
        time.sleep(0.5)
        self.my_instrument.write(":TRIGger:EDGE:SLOPe POSitive")
        time.sleep(0.5)

    def scale_position(self):
        self.my_instrument.write(":TIMebase:SCALe 2E-3")
        time.sleep(0.5)
        self.my_instrument.write(":TIMebase:POSition 6.5E-3")
        time.sleep(0.5)
        self.my_instrument.write(":TRIGger:SWEep TRIGgered")
        time.sleep(0.5)

    def WAVeform_PREamble(self):
        self.my_instrument.query(":WAVeform:PREamble?")

    def Set_marker(self):
        self.my_instrument.write(":MARKer:MODE MANual")
        time.sleep(0.5)
        self.my_instrument.write(":MARKer:X1Y1source FUNCtion2")
        time.sleep(0.5)
        self.my_instrument.write(":MARKer:X2Y2source FUNCtion2")
        time.sleep(0.5)
        self.my_instrument.write(":MARKer:X1Position -1E-3")
        time.sleep(0.5)
        self.my_instrument.write(":MARKer:X2Position 1E-3")
        time.sleep(0.5)
        self.my_instrument.write(":MARKer:Y1Position -700E-3")
        time.sleep(0.5)
        self.my_instrument.write(":MARKer:Y2Position 300E-3")
        time.sleep(0.5)

    def Save_waveformtoDisk(self,filename):
        self.my_instrument.write(":DISK:SAVE:WAVeform FUNCtion2,"+filename+",CSV,ON")