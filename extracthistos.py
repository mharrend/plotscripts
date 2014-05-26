#Script to extract histograms from the Root Tree, that is produced by Pythia8 in CMSSW
#Usage: python extracthistos.py input1.root (input2.root) output.root
#the secound inputfile is only needed, if you want to fill the showerd events from two events on partonlevel into the same output histogram
from DataFormats.FWLite import Events, Handle
import ROOT
from math import pi
from ROOT import TH1F, TFile, TTree, TString, gSystem
import sys 
#First use ROOT Lite in CMSSW
#--------------------------------------------------#
#-------------------- ROOT Lite -------------------#
cmsswbase = TString.getenv("CMSSW_BASE")

print 'Loading FW Lite setup.\n'
gSystem.Load("libFWCoreFWLite.so") 
ROOT.AutoLibraryLoader.enable()
gSystem.Load("libDataFormatsFWLite.so")
gSystem.Load("libDataFormatsPatCandidates.so")
#-------------------------------------------------#
#Check number of system arguments
if len(sys.argv) == 3:
	events = Events (sys.argv[1])
	outputfile = TFile(sys.argv[2],"RECREATE")
elif len(sys.argv) == 4:
	events = Events ([sys.argv[1],sys.argv[2]])
	outputfile = TFile(sys.argv[3],"RECREATE")
elif len(sys.argv) == 12:
	events = Events ([sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5],sys.argv[6],sys.argv[7],sys.argv[8],sys.argv[9],sys.argv[10]])
	outputfile = TFile(sys.argv[11],"RECREATE")
else:
	print "Something is wrong with the number of arguments!"
	print "Use: python extracthistos.py input.root output.root, if you just want to extract the Histograms from a single root file"
	print "Or use: python extracthistos.py input1.root input2.root output.root, if you want also to add the input Histograms"
	exit()

#Stuff with loop for getting a Histogramm with number of Jets
#events = Events (['ttH1JetFxFx8TeVCTEQ6M.root','ttH1JetFxFx8TeVCTEQ6M.root'])
#events = Events (['ttH1JetFxFx8TeVCTEQ6M.root','ttH0JetFxFx8TeVCTEQ6M.root'])
HnJets = TH1F ("HnJets", "Number of Jets", 15, -0.5, 14.5)
Hpt = TH1F("Hpt","Gen-Jet pt",50,0,300)
Hphi = TH1F("Hphi","Gen-Jet Phi",50,-pi,pi)
Htheta = TH1F("Htheta","Gen-Jet Theta",50,0,pi)
Henergy = TH1F("Henergy","Gen-Jet Energy",100,0,800)

# create handle outside of loop
# Handle and lable are pointing at the Branch you want
handle  = Handle ('std::vector<reco::GenJet>')
label = ("ak5GenJets")

#ROOT.gROOT.SetStyle('Plain') # white background
#Loop through all Events and Fill the Histogramms
for event in events:
	event.getByLabel (label, handle)
	GenJets = handle.product()
	nJets = 0
	for Jet in GenJets:
		if Jet.pt() >= 10 and Jet.eta() <= 2.5 and Jet.eta() >= -2.5:
			nJets = nJets + 1
		Hpt.Fill(Jet.pt())
		Hphi.Fill(Jet.phi())
		Htheta.Fill(Jet.theta())
		Henergy.Fill(Jet.energy())

	HnJets.Fill(nJets)

#Write Root File with Histogramms
#outputfile = TFile("ttHFxFx8TeVCTEQ6M-extracted.root","RECREATE")
outputfile.WriteTObject(Hpt)
outputfile.WriteTObject(Hphi)
outputfile.WriteTObject(Htheta)
outputfile.WriteTObject(Henergy)
outputfile.WriteTObject(HnJets)

