import numpy as np
import pandas as pd
import os
from ROOT import TH2F,TCanvas,TFile,TTree,TH1F,TGraph
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

def baseline_calculate_amp(time,voltage,timewindow=0.0,window_percent=0.0):
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
    Amp = baseline_calculate_amp(time,voltage,time_win,win_percent)
    amp = pd.Series([Amp],index = ['Amp'])
    pos_and_amp = pos.append(amp)
    print(pos_and_amp)

    return  pos_and_amp

def save_Tree(filepath,time_win=0.0,win_percent=0.0):
    allfiles = read_filename(filepath)
    rootfile = TFile(filepath + "/" + 'position_and_amp.root',"recreate")
    t1 = TTree("t1","include position and amp info")
    x = np.array([0],dtype = "int")
    y = np.array([0],dtype = "int")
    z = np.array([0],dtype = "int")
    Amp = np.array([0.0],dtype = "float")
    t1.Branch("x",x,"x/I")
    t1.Branch("y",y,"y/I")
    t1.Branch("z",z,"z/I")
    t1.Branch("Amp",Amp,"Amp/D")
    for csvfile in allfiles:
        position = get_position_value(csvfile,time_win,win_percent)
        x[0] = int(position.x)
        y[0] = int(position.y)
        z[0] = int(position.z)
        Amp[0] = position.Amp
        t1.Fill()

    t1.Write()
    rootfile.Close()

def hist2(filepath,x_axis=1,y_axis=1,z_axis=0):
    c1 = TCanvas("c1","Distribution of Amp")
    f1 = TFile(filepath + "/" + "position_and_amp.root")
    t1 = f1.Get("t1")
    x = np.array([0],dtype="int")
    y = np.array([0],dtype="int")
    z = np.array([0],dtype="int")
    amp = np.array([0.0],dtype="float")
    t1.SetBranchAddress("x",x)
    t1.SetBranchAddress("y",y)
    t1.SetBranchAddress("z",z)
    t1.SetBranchAddress("Amp",amp)
    if x_axis and y_axis and z_axis:
        print("Please choice right histgram!!!\nThis is TH2F!\n")
        exit()

    elif x_axis and y_axis:
        low1 = int(t1.GetMinimum("x"))
        high1 = int(t1.GetMaximum("x"))
        bin_number1 = high1 - low1 + 1
        low2 = int(t1.GetMinimum("y"))
        high2 = int(t1.GetMaximum("y"))
        bin_number2 = high2 - low2 + 1
        hist2 = TH2F("hist2","hist of Amp",bin_number1,low1,high1,bin_number2,low2,high2)
        hist2.GetXaxis().SetTitle('x')
        hist2.GetYaxis().SetTitle('y')
        nentries = t1.GetEntries()
        for i in range(0,nentries):
            t1.GetEntry(i)
            hist2.SetBinContent(x[0] - low1, y[0] - low2, amp[0])

    elif x_axis and z_axis:
        low1 = int(t1.GetMinimum("x"))
        high1 = int(t1.GetMaximum("x"))
        bin_number1 = high1 - low1 + 1
        low2 = int(t1.GetMinimum("z"))
        high2 = int(t1.GetMaximum("z"))
        bin_number2 = high2 - low2 + 1
        hist2 = TH2F("hist2","hist of Amp",bin_number1,low1,high1,bin_number2,low2,high2)
        hist2.GetXaxis().SetTitle('x')
        hist2.GetYaxis().SetTitle('z')
        nentries = t1.GetEntries()
        for i in range(0,nentries):
            t1.GetEntry(i)
            hist2.SetBinContent(x[0] - low1, z[0] - low2, amp[0])

    elif y_axis and z_axis:
        low1 = int(t1.GetMinimum("y"))
        high1 = int(t1.GetMaximum("y"))
        bin_number1 = high1 - low1 + 1
        low2 = int(t1.GetMinimum("z"))
        high2 = int(t1.GetMaximum("z"))
        bin_number2 = high2 - low2 + 1
        hist2 = TH2F("hist2","hist of Amp",bin_number1,low1,high1,bin_number2,low2,high2)
        hist2.GetXaxis().SetTitle('y')
        hist2.GetYaxis().SetTitle('z')
        nentries = t1.GetEntries()
        for i in range(0,nentries):
            t1.GetEntry(i)
            hist2.SetBinContent(y[0] - low1, z[0] - low2, amp[0])

    else:
        print("Please choice correct histgram!\nMaybe you should choice TH1F(hist1)\n")
        exit()
    hist2.Draw("Colz")
    #f = TFile("distribution_of_amp.root","recreate")
    hist2.Write()
    #f.Close()
    c1.Update()
    c1.SaveAs("./result/distribution_of_amp.pdf")

def projection(hist2,project_axis='x',name="_px",first_bin=0,last_bin=-1):
    if project_axis == 'x':
        h1 = hist2.ProjectionX(name,first_bin,last_bin)
        h1.Write()
    elif project_axis == 'y':
        h1 = hist2.ProjectionY(name,first_bin,last_bin)
        h1.Write()
    else:
        print("projection axis error!\n")

def calculate_FWHM(hist1):
    amp_max = hist1.GetMaximum()
    amp_min = hist1.GetMinimum()
    half_maximum = (amp_max - amp_min)/2
    total_bins = hist1.GetNbinsX()
    for i in range(1,total_bins):
        if half_maximum < hist1.GetBinContent(i) and half_maximum >= hist1.GetBinContent(i+1):
            left = hist1.GetBinContent(i+1)
            break
    for j in range(total_bins,1):
        if half_maximum < hist1.GetBinContent(j) and half_maximum >= hist1.GetBinContent(j+1):
            right = hist1.GetBinContent(j+1)
            break
    return right - left

def focus_fit(z,fwhm):
    tgr = TGraph(z.size,z,fwhm)
    tgr.Draw("AC*")
    tgr.Fit("pol2")
    tgr.Write()

if __name__ == "__main__":
    hist2("/home/zenghao/TCT/pytct/DataAnalysis")
    f = TFile("distribution_of_amp.root","UPDATE")
    f.mkdir("projectionX")
    f.projectionX.cd()
    projection(f.hist2,'x','_px',50,60)

