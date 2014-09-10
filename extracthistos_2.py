#Script to extract histograms from the Root Tree, that is produced by Pythia8 in CMSSW
#Usage: python extracthistos_2.py output.root
#The script, if mode 0 is set searches for .root files in the dir the script is running and uses them as inputs.
#This script allows also to get root files directly from the dCache if mode 2 is set.
#Currently the only execption to this is, are root-File that are ending with *-extracted.root
from DataFormats.FWLite import Events, Handle
import ROOT
from math import pi
from ROOT import TH1F, TFile, TTree, TString, gSystem
import sys 
from glob import glob
import os

def getmother(particle):
    #for constituent in constituents:
    #print particle.mother().status()
    getmother(particle)

#Mode 0: Searches for root files in dir
#Mode 1: input files als arguments
#Mode 2: Takes files from dCache, please give full path, e.g.
# /store/user/mharrend/FxFx_4FS_tt_0Jet_max1Jet_8TeV_CTEQ6M_0/FxFx_4FS_tt_0Jet_max1Jet_8TeV_CTEQ6M_0/f5ba0ca3f4cd3e3e394789a8eae55065/tt0JetFxFx8TeVCTEQ6M_1_1_fgZ.root
mode = 1

#----------- Class for Histograms ----------------#
# initialize histograms the same way like when using TH1F only with Histograms
# the constuctor initializes 3 TH1F objects.
class Histograms(object):
    def __init__(self, inhalt, title, nbins, minbin, maxbin):
        self.pos = TH1F(inhalt+"pos",title+" with pos. weights",nbins,minbin,maxbin)
        self.neg = TH1F(inhalt+"neg",title+" with neg. weights",nbins,minbin,maxbin)
        self.combined = TH1F(inhalt,title,nbins,minbin,maxbin)
    def fill(self,weight,value):
        if weight >0:
            self.pos.Fill(value,1.)
            self.combined.Fill(value,1.)
        elif weight < 0:
            self.neg.Fill(value,-1.)
            self.combined.Fill(value,-1.)
    def write(self):
        outputfile.WriteTObject(self.pos)
        outputfile.WriteTObject(self.neg)
        outputfile.WriteTObject(self.combined)
        del self

#-------------------------------------------------#
#---------------- Cut definitions ----------------#
# ptcuts is a list of different cut values
ptcuts = [25., 30., 50., 100.] 
etacut = 2.5
#-------------------------------------------------#
#First use FW Lite from CMSSW
#-------------------- FW Lite --------------------#
cmsswbase = TString.getenv("CMSSW_BASE")

print 'Loading FW Lite setup.\n'
gSystem.Load("libFWCoreFWLite.so") 
ROOT.AutoLibraryLoader.enable()
gSystem.Load("libDataFormatsFWLite.so")
gSystem.Load("libDataFormatsPatCandidates.so")
#-------------------------------------------------#
#Create output file bevor loop
outputfile = TFile(sys.argv[1],"RECREATE")

#Read in the inputfiles for every loop, else it won't work
inputlist = []
if mode == 0:
    if len(sys.argv) > 2:
        dirs = sys.argv[2:]
    else:
        dirs = [""]
    for d in dirs:
        for f in glob(os.path.join(d, '*.root')):
            if f[-15:] != '-extracted.root' and f != sys.argv[1]:
                inputlist.append(f)
elif mode == 1:
    for arg in sys.argv[2:]:
        if arg[-5:] == '.root':
            inputlist.append(arg)
        else:
            print "One or more of the Arguments are no .root file. Exiting!"
            exit()

elif mode == 2:
    for arg in sys.argv[2:]:
        if arg[-5:] == '.root':
            inputlist.append('root://xrootd.ba.infn.it//' + arg)
        else:
            print "One or more of the Arguments are no .root file. Exiting!"
            exit()

else:
    print "Please change Mode!"
    exit()
print inputlist

for cut in ptcuts:

    events = Events (inputlist)

    cutn = str(cut) #variable for names of histograms
    #Definition of the Histograms
    #Jet Histograms
    njets = Histograms ("HnJets"+cutn, "Number of Jets "+cutn, 15, -0.5, 14.5)
    pt = Histograms("Hpt"+cutn,"Gen-Jet pt "+cutn,100,0,300)
    phi = Histograms("Hphi"+cutn,"Gen-Jet Phi "+cutn,50,-pi,pi)
    theta = Histograms("Htheta"+cutn,"Gen-Jet Theta "+cutn,50,0,pi)
    energy = Histograms("Henergy"+cutn,"Gen-Jet Energy "+cutn,100,0,600)
    firstjetpt = Histograms("HfirstJetpt"+cutn,"Pt of hardest Gen-Jet "+cutn, 100,0,300)
    firstjeteta = Histograms("H1sJeteta"+cutn,"Eta of hardest Gen-Jet "+cutn,50,-5,5)
    secoundjetpt = Histograms("HsecoundJetpt"+cutn,"Pt of 2nd hardest Gen-Jet "+cutn, 100,0,300)
    isrjetpt = Histograms("Hisrjetpt"+cutn, "Pt of ISR-Jets "+cutn,100,0,300)
    fsrjetpt = Histograms("Hfsrjetpt"+cutn, "Pt of FSR-Jets "+cutn,100,0,300)
    nIsrJets = Histograms("HnIsrJets"+cutn,"Number of ISR Jets per Event "+cutn, 15, -0.5, 14.5)
    nFsrJets = Histograms("HnFsrJets"+cutn,"Number of FSR Jets per Event "+cutn, 15, -0.5, 14.5)

    # create handle outside of loop
    # Handle and lable are pointing at the Branch you want
    handle  = Handle ('std::vector<reco::GenJet>')
    label = ("ak5GenJets")
    infohandle = Handle ('<GenEventInfoProduct>')

    #ROOT.gROOT.SetStyle('Plain') # white background
    #Loop through all Events and Fill the Histograms
    print 'Filling new jet histograms with ptcut: '+cutn+'GeV'
    enumber = 0
    print "handle_label",handle, label
    for event in events:
        event.getByLabel (label, handle)
        GenJets = handle.product()
        ievent = event
        ievent.getByLabel ("generator", infohandle)
        Infos = infohandle.product()
        nJets = 0
        firstJetpt = 0
        secoundJetpt = 0
        firstJeteta = 0
	nISRJets = 0
	nFSRJets = 0
        eventweight = Infos.weight()
        for Jet in GenJets:
            if Jet.pt() >= cut and abs(Jet.eta()) <= etacut:
                #for JetConstituent in Jet.getJetConstituents():
                #        print JetConstituent.pdgId(), " no of mothers ", JetConstituent.numberOfMothers()
                nJets = nJets + 1
                pt.fill(eventweight,Jet.pt())
                phi.fill(eventweight,Jet.phi())
                theta.fill(eventweight,Jet.theta())
                energy.fill(eventweight,Jet.energy())
		
		# ISR/FSR implementation
		for constituent in Jet.getJetConstituents():
                    childOfHard = False
		    childOfISS = False
		    childOfFSS = False
                    while(True):
			try:
				constituent = constituent.mother()
				cs = constituent.status()

				if 21 <= cs <= 29:
					childOfHard = True
				if 41 <= cs <= 49:
					childOfISS = True
				if 51 <= cs <= 59:
					childOfFSS = True
                        except ReferenceError:
                            break
		if ( not childOfHard ) and childOfISS:
			isrjetpt.fill(eventweight,Jet.pt())
			nISRJets = nISRJets + 1 
		if childOfHard and childOfFSS:
			fsrjetpt.fill(eventweight,Jet.pt())
			nFSRJets = nFSRJets + 1 

                if Jet.pt() >= firstJetpt and Jet.pt() >= secoundJetpt:
                    secoundJetpt = firstJetpt
                    firstJetpt = Jet.pt()
                    firstJeteta = Jet.eta()
                elif Jet.pt() >= secoundJetpt and Jet.pt() <= firstJetpt:
                    secoundJetpt = Jet.pt()
                    enumber=enumber+1
                    firstjetpt.fill(eventweight,firstJetpt)
                    secoundjetpt.fill(eventweight,secoundJetpt)
                    firstjeteta.fill(eventweight,firstJeteta)
        njets.fill(eventweight,nJets)
	nIsrJets.fill(eventweight,min(15,nISRJets))
	nFsrJets.fill(eventweight,min(15,nFSRJets))
	

    #wirte all histograms in the output file. After they are wrote, they are getting deleted (s. write() method)
    pt.write()
    phi.write()
    theta.write()
    energy.write()
    firstjetpt.write()
    secoundjetpt.write()
    firstjeteta.write()
    njets.write()
    isrjetpt.write()
    fsrjetpt.write()
    nIsrJets.write()
    nFsrJets.write()
    #delete all variables, that are used again in the next loop
    del handle
    del label
    del infohandle
    del events
