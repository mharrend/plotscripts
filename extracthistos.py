#Script to extract histograms from the Root Tree, that is produced by Pythia8 in CMSSW
#Usage: python extracthistos.py input1.root (input2.root) output.root
#the secound inputfile is only needed, if you want to fill the showerd events from two events on partonlevel into the same output histogram
from DataFormats.FWLite import Events, Handle
import ROOT
from math import pi
from ROOT import TH1F, TFile, TTree, TString, gSystem
import sys 
#---------------- Cut definitions -----------------#
ptcut = 25 
etacut = 2.5
#--------------------------------------------------#
#First use ROOT Lite in CMSSW
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
	events = Events ([sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5],sys.argv[6],sys.argv[7],sys.argv[8],sys.argv[9],sys.argv[10],sys.argv[11]])
	outputfile = TFile(sys.argv[1],"RECREATE")
elif len(sys.argv) == 22:
	events = Events ([sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5],sys.argv[6],sys.argv[7],sys.argv[8],sys.argv[9],sys.argv[10],sys.argv[11],sys.argv[12],sys.argv[13],sys.argv[14],sys.argv[15],sys.argv[16],sys.argv[17],sys.argv[18],sys.argv[19],sys.argv[20],sys.argv[21]])
	outputfile = TFile(sys.argv[1],"RECREATE")
else:
	print "Something is wrong with the number of arguments!"
	print "Use: python extracthistos.py input.root output.root, if you just want to extract the Histograms from a single root file"
	print "Or use: python extracthistos.py input1.root input2.root output.root, if you want also to add the input Histograms"
	exit()

#Definition of the Histograms
#Jet Histograms
HnJets = TH1F ("HnJets", "Number of Jets", 15, -0.5, 14.5)
Hpt = TH1F("Hpt","Gen-Jet pt",100,0,300)
Hphi = TH1F("Hphi","Gen-Jet Phi",50,-pi,pi)
Htheta = TH1F("Htheta","Gen-Jet Theta",50,0,pi)
Henergy = TH1F("Henergy","Gen-Jet Energy",100,0,600)
H1stJetpt = TH1F("H1stJetpt","Pt of hardest Gen-Jet", 100,0,300)
H1stJeteta = TH1F("H1sJeteta","Eta of hardest Gen-Jet",50,-5,5)
H2ndJetpt = TH1F("H2ndJetpt","Pt of 2nd hardest Gen-Jet", 100,0,300)
#Particle Histograms
Htpt = TH1F ("Htpt","pt of Top-Quarks", 100,0,300)
Htbarpt = TH1F ("Htbarpt","pt of Top-Anti-Quark", 100, 0, 300)
Httbarpt = TH1F ("Httbarpt", "pt of t tbar pair", 100, 0 ,300)

# create handle outside of loop
# Handle and lable are pointing at the Branch you want
handle  = Handle ('std::vector<reco::GenJet>')
label = ("ak5GenJets")
particlehandle = Handle ('std::vector<reco::GenParticles>')
particlelabel = ("genParticles")


#ROOT.gROOT.SetStyle('Plain') # white background
#Loop through all Events and Fill the Histograms
print 'Filling new jet histograms'
for event in events:
	event.getByLabel (label, handle)
	GenJets = handle.product()
	nJets = 0
	1stJetpt = 0
	2ndJetpt = 0
	1stJeteta = 0
	for Jet in GenJets:
		if Jet.pt() >= ptcut and abs(Jet.eta()) <= etacut:
			nJets = nJets + 1
			Hpt.Fill(Jet.pt())
			Hphi.Fill(Jet.phi())
			Htheta.Fill(Jet.theta())
			Henergy.Fill(Jet.energy())
			if Jet.pt() >= 1stJetpt:
				2ndJetpt = 1stJetpt
				1stJetpt = Jet.pt()
				1stJeteta = Jet.eta()
	H1stJetpt.Fill(1stJetpt)
	H2ndJetpt.Fill(2ndJetpt)
	H1stJeteta.Fill(1stJeteta)
	HnJets.Fill(nJets)
print 'Filling new particle histograms'
for pevent in events:
	toppt = 0
	tbarpt = 0
	pevent.getByLabel (particlelabel, particlehandle)
	GenParticle = particlehandle.product()
	for particle in GenParticles:
		if particle.pdgId() == 6:
			toppt = particle.pt()
		if particle.pdgId() == -6:
			tbarpt = particle.pt
		Htpt.Fill(toppt)
		Htbarpt.Fill(tbarpt)
		if toppt != 0 and tbarpt != 0:
			Httbarpt.Fill(toppt + tbarpt)

#Write Root File with Histogramms
outputfile.WriteTObject(Hpt)
outputfile.WriteTObject(Hphi)
outputfile.WriteTObject(Htheta)
outputfile.WriteTObject(Henergy)
outputfile.WriteTObject(HnJets)
outputfile.WriteTObject(H1stJetpt)
outputfile.WriteTObject(H2ndJetpt)
outputfile.WriteTObject(H1stJeteta)
outputfile.WriteTObject(Htpt)
outputfile.WriteTObject(Htbarpt)
outputfile.WriteTObject(Httbarpt)
