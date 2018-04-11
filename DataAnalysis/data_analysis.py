import numpy as np
import pandas as pd
import os
from ROOT import TH2F,TCanvas
from sys import argv

def read_filename(filepath):
    filename = np.array(os.listdir(filepath))
    print(filename.size)
    pathname = np.empty(filename.size,dtype = 'S100')
    filepath = filepath + "/"
    print(filepath)
    pathname[:] = filepath
    print(pathname)
    filename = np.core.defchararray.add(pathname,filename)
    return filename

def read_file(filename):
    df = pd.DataFrame(pd.read_csv(filename))
    return df

def extract_data(datafrm):
    pos = datafrm[datafrm.columns[2]][0:3]
    pos.name = "position"
    pos.index = ['x','y','z']

    time1 = datafrm[datafrm.columns[0]][4:]
    time1.reset_index(drop=True)
    time = time1.astype("float")
    time.name = "Time[s]"

    voltage1 = datafrm[datafrm.columns[1]][4:]
    voltage1.reset_index(drop=True)
    voltage = voltage1.astype("float")
    voltage.name = "Volt[V]"

    return pos,time,voltage

def calculate_amp(time,voltage,timewindow=0.0,window_percent=0.0):
    timenp = np.array(time)
    voltagenp = np.array(voltage)
    if window_percent != 0.0 and timewindow != 0.0:
        line_point = int(voltagenp.size * window_percent)
    if window_percent != 0.0:
        line_point = int(voltagenp.size * window_percent)
    if timewindow != 0.0:
        line_point = int(timenp.size * (timewindow /(timenp[-1] - timenp[0])))
    voltage_base = voltage[0:line_point]
    baseline = np.mean(voltage_base)
    voltage_bar = voltagenp - baseline
    amp = voltage_bar.max() - baseline
    return amp

def get_position_value(filename,time_win=0.0,win_percent=0.0):
    df = read_file(filename)
    pos,time,voltage = extract_data(df)
    Amp = calculate_amp(time,voltage,time_win,win_percent)
    amp = pd.Series([Amp],index = ['Amp'])
    pos_and_amp = pos.append(amp)
    print(pos_and_amp)

    return  pos_and_amp 

def draw_hist(filepath,time_win=0.0,win_percent=0.0):
    c1 = TCanvas('c1','Amp distribution',200,10,700,500)
    hist2 = TH2F("hist2","hist of amp",100,100,200,100,100,200)
    allname = read_filename(filepath)
    for csvfile in allname:
        pos = get_position_value(csvfile,time_win,win_percent)
        x_bin_number = int(pos.x - 100)
        y_bin_number = int(pos.y - 100)
        #print(type(x_bin_number))
        #print(x_bin_number)

        hist2.SetBinContent(x_bin_number ,y_bin_number ,pos.Amp)

    hist2.Draw()
    c1.Update()
    input()
    c1.SaveAs()
    
if __name__ == "__main__":
    script,filepath = argv 
    draw_hist(filepath,win_percent = 0.1)
   



