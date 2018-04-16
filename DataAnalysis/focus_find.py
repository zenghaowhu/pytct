import data_analysis as da
from ROOT import TCanvas,TFile,gDirectory,gStyle,TGraph
import numpy as np
from sys import argv

script,filepath = argv
def main():
    fwhm = np.array([],dtype="float")
    da.save_Tree(filepath,win_percent = 0.1)
    f = TFile(filepath + "/" + "focus.root","recreate")
    f.mkdir("distribution_of_amp")
    f.distribution.cd()
    da.hist2(filepath,1,0,1)
    h2 = f.distribution.hist2
    gDirectory.cd("..")
    f.mkfir("projection")
    f.projection.cd()
    z = h2.GetNbinsY()
    for i in range(0,z):
        da.projection(h2,'x',name = "_pz",i,i+1)
        fwhm_value = calculate_FWHM(f.projection.hist2_pz)
        np.append(fwhm,fwhm_value)
        da.projection(h2,'x',"_z" + str(i),i,i+1)

    
    f2 = TFile(filepath + "/" + "position_and_amp.root")
    z_min = f2.t1.GetMinimum("z")
    z_max = f2.t1.GetMaximum("z")
    z = np.arange(z_min,z_max+1)
    z = z.astype("float")
    tgr = TGraph(z.size,z,fwhm)
    t1 = TCanva("t1","focus")
    tgr.GetXaxis().SetTitle("z[um]")
    tgr.GetYaxis().SetTitle("FWHM[um]")
    tgr.Draw("AC*")
    tgr.Fit("pol2")
    gStyle.SetOptFit(1)
    c1.Update()
    c1.SaveAs("./result/focus.pdf")

if name == "__main__":
    main()
