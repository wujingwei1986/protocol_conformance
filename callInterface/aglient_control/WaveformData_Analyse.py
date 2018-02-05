# -*- coding: GB18030 -*-
#wujingwei

import os,sys,time,csv
import numpy as np, pandas as pd
from pandas import Series, DataFrame
import matplotlib.pyplot as plt
#from CONSTANTS import *
import CONSTANTS

#��ȡ�ϼ�Ŀ¼callInterface
curr_path = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)),os.path.pardir))
air_interface40_path = os.path.join(curr_path,"result_file\\air_interface40\\") #�����겨�ν�����Ŀ¼
air_interface80_path = os.path.join(curr_path,"result_file\\air_interface80\\")
waveform40_path = os.path.join(curr_path,"result_file\waveform40\\") #���δ��Ŀ¼
waveform80_path = os.path.join(curr_path,"result_file\waveform80\\")

#��ȡȫ�������ļ�
def get_WaveformFile(waveform_path):
    for root, dirs, files in os.walk(waveform_path):
        return files #��ǰ·�������з�Ŀ¼���ļ�

#�����������д��csv
def write_toCSV(filename,data):
    with open(filename,"w") as csvfile:
        writer = csv.writer(csvfile)
        #��д��columns_name
        writer.writerow(["Encoding","Total","Max","Min","Avg"])
        #д�������writerows
        writer.writerows(data)

def analyse_40_waveform():
    filename_list = get_WaveformFile(waveform40_path)
    for filename in filename_list:
        data = pd.read_csv(filename)
        pd.set_option('precision', 12) #����С������
        media = (data["voltage"].max()+data["voltage"].min())/2
        voltage_rangeMin = media*0.99
        voltage_rangeMax = media*1.01
        #ɸѡ��������������
        CenterVoltage_times = data.loc[(data["voltage"]>voltage_rangeMin) & (data["voltage"]<voltage_rangeMax)]["time"]
        #��ɸѡ�������ת�����б�
        CenterVoltage_times_list = list(CenterVoltage_times)
        #����ɸѡ������ݿ�����ʱ���ܽ�������ֵ�����������������һ������
        data_filter = []
        for num in range(len(CenterVoltage_times_list)-1):
            if (CenterVoltage_times_list[num+1]-CenterVoltage_times_list[num])*CONSTANTS.multiple_t>1:
                data_filter.append(CenterVoltage_times_list[num])

        #print "Total length:",len(data_filter)
        #����ָ���,У׼ֵһ��ֵ
        #ÿ��һ����ȡһ��ֵ������һ������
        symbol_t = ''
        calibration_num1_list = []
        split_time_list = []
        symbol_40_00_list = []
        symbol_40_01_list = []
        symbol_40_10_list = []
        symbol_40_11_list = []

        for num in range(1,len(data_filter)-2,2):
            T = (data_filter[num+2] - data_filter[num])*CONSTANTS.multiple_t
            if T>CONSTANTS.symbol_40_00_min and T<CONSTANTS.symbol_40_00_max:
                symbol_t = "2Tc"
                symbol_40_00_list.append(T)
            elif T>CONSTANTS.symbol_40_01_min and T<CONSTANTS.symbol_40_01_max:
                symbol_t = "3Tc"
                symbol_40_01_list.append(T)
            elif T>CONSTANTS.symbol_40_11_min and T<CONSTANTS.symbol_40_11_max:
                symbol_t = "4Tc"
                symbol_40_11_list.append(T)
            elif T>CONSTANTS.symbol_40_10_min and T<CONSTANTS.symbol_40_10_max:
                symbol_t = "5Tc"
                symbol_40_10_list.append(T)
            elif T>CONSTANTS.calibration_40_num1_min and T<CONSTANTS.calibration_40_num1_max:
                calibration_num1_list.append(T)
                split_time = (data_filter[num] - data_filter[num-1])*CONSTANTS.multiple_t
                split_time_list.append(split_time)
            else:
                symbol_t = ''
            print T,symbol_t

        #������ŵ������С��ƽ��ֵ
        symbol_40_00_min = min(symbol_40_00_list)
        symbol_40_00_max = max(symbol_40_00_list)
        symbol_40_00_avg = sum(symbol_40_00_list)/len(symbol_40_00_list)

        symbol_40_01_min = min(symbol_40_01_list)
        symbol_40_01_max = max(symbol_40_01_list)
        symbol_40_01_avg = sum(symbol_40_01_list)/len(symbol_40_01_list)

        symbol_40_11_min = min(symbol_40_11_list)
        symbol_40_11_max = max(symbol_40_11_list)
        symbol_40_11_avg = sum(symbol_40_11_list)/len(symbol_40_11_list)

        symbol_40_10_min = min(symbol_40_10_list)
        symbol_40_10_max = max(symbol_40_10_list)
        symbol_40_10_avg = sum(symbol_40_10_list)/len(symbol_40_10_list)

        #�ָ���
        split_time_min = min(split_time_list)
        split_time_max = max(split_time_list)
        split_time_avg = sum(split_time_list)/len(split_time_list)

        #У׼��һ
        calibration_num1_min = min(calibration_num1_list)
        calibration_num1_max = max(calibration_num1_list)
        calibration_num1_avg = sum(calibration_num1_list)/len(calibration_num1_list)

        split_result = ["delimiter",len(split_time_list),split_time_max,split_time_min,split_time_avg]
        calibration_num1_result = ["calibration",len(calibration_num1_list),calibration_num1_max,calibration_num1_min,calibration_num1_avg]
        symbol_40_00_result = ["00",len(symbol_40_00_list),symbol_40_00_max,symbol_40_00_min,symbol_40_00_avg]
        symbol_40_01_result = ["01",len(symbol_40_01_list),symbol_40_01_max,symbol_40_01_min,symbol_40_01_avg]
        symbol_40_11_result = ["11",len(symbol_40_11_list),symbol_40_11_max,symbol_40_11_min,symbol_40_11_avg]
        symbol_40_10_result = ["10",len(symbol_40_10_list),symbol_40_10_max,symbol_40_10_min,symbol_40_10_avg]
        all_result = [split_result,calibration_num1_result,symbol_40_00_result,symbol_40_01_result,symbol_40_11_result,symbol_40_10_result]

        write_toCSV(air_interface40_path+filename,all_result)

        print u"����00���ֵ��{0}����Сֵ��{1}��ƽ��ֵ��{2}".format(symbol_40_00_max,symbol_40_00_min,symbol_40_00_avg)
        print u"����01���ֵ��{0}����Сֵ��{1}��ƽ��ֵ��{2}".format(symbol_40_01_max,symbol_40_01_min,symbol_40_01_avg)
        print u"����11���ֵ��{0}����Сֵ��{1}��ƽ��ֵ��{2}".format(symbol_40_11_max,symbol_40_11_min,symbol_40_11_avg)
        print u"����10���ֵ��{0}����Сֵ��{1}��ƽ��ֵ��{2}".format(symbol_40_10_max,symbol_40_10_min,symbol_40_10_avg)
        print u"�ָ������ֵ��{0}����Сֵ��{1}��ƽ��ֵ��{2}".format(split_time_max,split_time_min,split_time_avg)
        print u"У׼��һ���ֵ��{0}����Сֵ��{1}��ƽ��ֵ��{2}".format(calibration_num1_max,calibration_num1_min,calibration_num1_avg)


def analyse_80_waveform():
    filename_list = get_WaveformFile(waveform80_path)
    for filename in filename_list:
        data = pd.read_csv(filename)
        pd.set_option('precision', 12) #����С������
        media = (data["voltage"].max()+data["voltage"].min())/2
        voltage_rangeMin = media*0.99
        voltage_rangeMax = media*1.01
        #ɸѡ��������������
        CenterVoltage_times = data.loc[(data["voltage"]>voltage_rangeMin) & (data["voltage"]<voltage_rangeMax)]["time"]
        #��ɸѡ�������ת�����б�
        CenterVoltage_times_list = list(CenterVoltage_times)
        #����ɸѡ������ݿ�����ʱ���ܽ�������ֵ�����������������һ������
        data_filter = []
        for num in range(len(CenterVoltage_times_list)-1):
            if (CenterVoltage_times_list[num+1]-CenterVoltage_times_list[num])*CONSTANTS.multiple_t>1:
                data_filter.append(CenterVoltage_times_list[num])

        #print "Total length:",len(data_filter)
        #����ָ���,У׼ֵһ��ֵ
        #ÿ��һ����ȡһ��ֵ������һ������
        symbol_t = ''
        calibration_num1_list = []
        split_time_list = []
        symbol_80_00_list = []
        symbol_80_01_list = []
        symbol_80_10_list = []
        symbol_80_11_list = []

        for num in range(1,len(data_filter)-2,2):
            T = (data_filter[num+2] - data_filter[num])*CONSTANTS.multiple_t
            if T>CONSTANTS.symbol_80_00_min and T<CONSTANTS.symbol_80_00_max:
                symbol_t = "2Tc"
                symbol_80_00_list.append(T)
            elif T>CONSTANTS.symbol_80_01_min and T<CONSTANTS.symbol_80_01_max:
                symbol_t = "3Tc"
                symbol_80_01_list.append(T)
            elif T>CONSTANTS.symbol_80_11_min and T<CONSTANTS.symbol_80_11_max:
                symbol_t = "4Tc"
                symbol_80_11_list.append(T)
            elif T>CONSTANTS.symbol_80_10_min and T<CONSTANTS.symbol_80_10_max:
                symbol_t = "5Tc"
                symbol_80_10_list.append(T)
            elif T>CONSTANTS.calibration_80_num1_min and T<CONSTANTS.calibration_80_num1_max:
                calibration_num1_list.append(T)
                split_time = (data_filter[num] - data_filter[num-1])*CONSTANTS.multiple_t
                split_time_list.append(split_time)
            else:
                symbol_t = ''
            print T,symbol_t

        #������ŵ������С��ƽ��ֵ
        symbol_80_00_min = min(symbol_80_00_list)
        symbol_80_00_max = max(symbol_80_00_list)
        symbol_80_00_avg = sum(symbol_80_00_list)/len(symbol_80_00_list)

        symbol_80_01_min = min(symbol_80_01_list)
        symbol_80_01_max = max(symbol_80_01_list)
        symbol_80_01_avg = sum(symbol_80_01_list)/len(symbol_80_01_list)

        symbol_80_11_min = min(symbol_80_11_list)
        symbol_80_11_max = max(symbol_80_11_list)
        symbol_80_11_avg = sum(symbol_80_11_list)/len(symbol_80_11_list)

        symbol_80_10_min = min(symbol_80_10_list)
        symbol_80_10_max = max(symbol_80_10_list)
        symbol_80_10_avg = sum(symbol_80_10_list)/len(symbol_80_10_list)

        #�ָ���
        split_time_min = min(split_time_list)
        split_time_max = max(split_time_list)
        split_time_avg = sum(split_time_list)/len(split_time_list)

        #У׼��һ
        calibration_num1_min = min(calibration_num1_list)
        calibration_num1_max = max(calibration_num1_list)
        calibration_num1_avg = sum(calibration_num1_list)/len(calibration_num1_list)

        split_result = ["delimiter",len(split_time_list),split_time_max,split_time_min,split_time_avg]
        calibration_num1_result = ["calibration",len(calibration_num1_list),calibration_num1_max,calibration_num1_min,calibration_num1_avg]
        symbol_80_00_result = ["00",len(symbol_80_00_list),symbol_80_00_max,symbol_80_00_min,symbol_80_00_avg]
        symbol_80_01_result = ["01",len(symbol_80_01_list),symbol_80_01_max,symbol_80_01_min,symbol_80_01_avg]
        symbol_80_11_result = ["11",len(symbol_80_11_list),symbol_80_11_max,symbol_80_11_min,symbol_80_11_avg]
        symbol_80_10_result = ["10",len(symbol_80_10_list),symbol_80_10_max,symbol_80_10_min,symbol_80_10_avg]
        all_result = [split_result,calibration_num1_result,symbol_80_00_result,symbol_80_01_result,symbol_80_11_result,symbol_80_10_result]

        write_toCSV(air_interface80_path+filename,all_result)

        print u"����00���ֵ��{0}����Сֵ��{1}��ƽ��ֵ��{2}".format(symbol_80_00_max,symbol_80_00_min,symbol_80_00_avg)
        print u"����01���ֵ��{0}����Сֵ��{1}��ƽ��ֵ��{2}".format(symbol_80_01_max,symbol_80_01_min,symbol_80_01_avg)
        print u"����11���ֵ��{0}����Сֵ��{1}��ƽ��ֵ��{2}".format(symbol_80_11_max,symbol_80_11_min,symbol_80_11_avg)
        print u"����10���ֵ��{0}����Сֵ��{1}��ƽ��ֵ��{2}".format(symbol_80_10_max,symbol_80_10_min,symbol_80_10_avg)
        print u"�ָ������ֵ��{0}����Сֵ��{1}��ƽ��ֵ��{2}".format(split_time_max,split_time_min,split_time_avg)
        print u"У׼��һ���ֵ��{0}����Сֵ��{1}��ƽ��ֵ��{2}".format(calibration_num1_max,calibration_num1_min,calibration_num1_avg)

analyse_80_waveform()
analyse_40_waveform()