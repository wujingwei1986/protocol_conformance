# -*- coding: GB18030 -*-
#wujingwei

import os,sys,time,csv
import numpy as np, pandas as pd
from pandas import Series, DataFrame
import matplotlib.pyplot as plt
#from CONSTANTS import *
import CONSTANTS

#获取上级目录callInterface
curr_path = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)),os.path.pardir))
air_interface40_path = os.path.join(curr_path,"result_file\\air_interface40\\") #分析完波形结果存放目录
air_interface80_path = os.path.join(curr_path,"result_file\\air_interface80\\")
waveform40_path = os.path.join(curr_path,"result_file\waveform40\\") #波形存放目录
waveform80_path = os.path.join(curr_path,"result_file\waveform80\\")

#获取全部波形文件
def get_WaveformFile(waveform_path):
    for root, dirs, files in os.walk(waveform_path):
        return files #当前路径下所有非目录子文件

#分析完的数据写入csv
def write_toCSV(filename,data):
    with open(filename,"w") as csvfile:
        writer = csv.writer(csvfile)
        #先写入columns_name
        writer.writerow(["Encoding","Total","Max","Min","Avg"])
        #写入多行用writerows
        writer.writerows(data)

def analyse_40_waveform():
    filename_list = get_WaveformFile(waveform40_path)
    for filename in filename_list:
        data = pd.read_csv(filename)
        pd.set_option('precision', 12) #设置小数精度
        media = (data["voltage"].max()+data["voltage"].min())/2
        voltage_rangeMin = media*0.99
        voltage_rangeMax = media*1.01
        #筛选符合条件的数据
        CenterVoltage_times = data.loc[(data["voltage"]>voltage_rangeMin) & (data["voltage"]<voltage_rangeMax)]["time"]
        #将筛选后的数据转换成列表
        CenterVoltage_times_list = list(CenterVoltage_times)
        #初步筛选后的数据可能有时间点很近的两个值都符合条件，还需进一步过滤
        data_filter = []
        for num in range(len(CenterVoltage_times_list)-1):
            if (CenterVoltage_times_list[num+1]-CenterVoltage_times_list[num])*CONSTANTS.multiple_t>1:
                data_filter.append(CenterVoltage_times_list[num])

        #print "Total length:",len(data_filter)
        #计算分隔符,校准值一的值
        #每隔一个点取一次值，代表一个周期
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

        #计算符号的最大最小和平均值
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

        #分隔符
        split_time_min = min(split_time_list)
        split_time_max = max(split_time_list)
        split_time_avg = sum(split_time_list)/len(split_time_list)

        #校准符一
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

        print u"符号00最大值：{0}，最小值：{1}，平均值：{2}".format(symbol_40_00_max,symbol_40_00_min,symbol_40_00_avg)
        print u"符号01最大值：{0}，最小值：{1}，平均值：{2}".format(symbol_40_01_max,symbol_40_01_min,symbol_40_01_avg)
        print u"符号11最大值：{0}，最小值：{1}，平均值：{2}".format(symbol_40_11_max,symbol_40_11_min,symbol_40_11_avg)
        print u"符号10最大值：{0}，最小值：{1}，平均值：{2}".format(symbol_40_10_max,symbol_40_10_min,symbol_40_10_avg)
        print u"分隔符最大值：{0}，最小值：{1}，平均值：{2}".format(split_time_max,split_time_min,split_time_avg)
        print u"校准符一最大值：{0}，最小值：{1}，平均值：{2}".format(calibration_num1_max,calibration_num1_min,calibration_num1_avg)


def analyse_80_waveform():
    filename_list = get_WaveformFile(waveform80_path)
    for filename in filename_list:
        data = pd.read_csv(filename)
        pd.set_option('precision', 12) #设置小数精度
        media = (data["voltage"].max()+data["voltage"].min())/2
        voltage_rangeMin = media*0.99
        voltage_rangeMax = media*1.01
        #筛选符合条件的数据
        CenterVoltage_times = data.loc[(data["voltage"]>voltage_rangeMin) & (data["voltage"]<voltage_rangeMax)]["time"]
        #将筛选后的数据转换成列表
        CenterVoltage_times_list = list(CenterVoltage_times)
        #初步筛选后的数据可能有时间点很近的两个值都符合条件，还需进一步过滤
        data_filter = []
        for num in range(len(CenterVoltage_times_list)-1):
            if (CenterVoltage_times_list[num+1]-CenterVoltage_times_list[num])*CONSTANTS.multiple_t>1:
                data_filter.append(CenterVoltage_times_list[num])

        #print "Total length:",len(data_filter)
        #计算分隔符,校准值一的值
        #每隔一个点取一次值，代表一个周期
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

        #计算符号的最大最小和平均值
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

        #分隔符
        split_time_min = min(split_time_list)
        split_time_max = max(split_time_list)
        split_time_avg = sum(split_time_list)/len(split_time_list)

        #校准符一
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

        print u"符号00最大值：{0}，最小值：{1}，平均值：{2}".format(symbol_80_00_max,symbol_80_00_min,symbol_80_00_avg)
        print u"符号01最大值：{0}，最小值：{1}，平均值：{2}".format(symbol_80_01_max,symbol_80_01_min,symbol_80_01_avg)
        print u"符号11最大值：{0}，最小值：{1}，平均值：{2}".format(symbol_80_11_max,symbol_80_11_min,symbol_80_11_avg)
        print u"符号10最大值：{0}，最小值：{1}，平均值：{2}".format(symbol_80_10_max,symbol_80_10_min,symbol_80_10_avg)
        print u"分隔符最大值：{0}，最小值：{1}，平均值：{2}".format(split_time_max,split_time_min,split_time_avg)
        print u"校准符一最大值：{0}，最小值：{1}，平均值：{2}".format(calibration_num1_max,calibration_num1_min,calibration_num1_avg)

analyse_80_waveform()
analyse_40_waveform()