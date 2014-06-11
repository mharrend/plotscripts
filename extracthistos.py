#Script to extract histograms from the Root Tree, that is produced by Pythia8 in CMSSW
#Usage: python extracthistos.py input1.root (input2.root) output.root
#the secound inputfile is only needed, if you want to fill the showerd events from two events on partonlevel into the same output histogram
from DataFormats.FWLite import Events, Handle
import ROOT
from math import pi
from ROOT import TH1F, TFile, TTree, TString, gSystem
import sys 

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
            self.pos.Fill(value,weight)
        elif weight < 0:
            self.neg.Fill(value,weight*(-1.))
        self.combined.Fill(value,weight)
    def write(self):
        outputfile.WriteTObject(self.pos)
        outputfile.WriteTObject(self.neg)
        outputfile.WriteTObject(self.combined)
#-------------------------------------------------#
#---------------- Cut definitions ----------------#
ptcut = 25 
etacut = 2.5
#-------------------------------------------------#
#First use ROOT Lite in CMSSW
#-------------------- ROOT Lite ------------------#
cmsswbase = TString.getenv("CMSSW_BASE")

print 'Loading FW Lite setup.\n'
gSystem.Load("libFWCoreFWLite.so") 
ROOT.AutoLibraryLoader.enable()
gSystem.Load("libDataFormatsFWLite.so")
gSystem.Load("libDataFormatsPatCandidates.so")
#-------------------------------------------------#
#Check number of system arguments
if len(sys.argv) == 3:
	events = Events (sys.argv[2])
	outputfile = TFile(sys.argv[1],"RECREATE")
elif len(sys.argv) == 4:
	events = Events ([sys.argv[2],sys.argv[3]])
	outputfile = TFile(sys.argv[1],"RECREATE")
elif len(sys.argv) == 12:
	events = Events ([sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5],sys.argv[6],sys.argv[7],sys.argv[8],sys.argv[9],sys.argv[10],sys.argv[11]])
	outputfile = TFile(sys.argv[1],"RECREATE")
elif len(sys.argv) == 22:
	events = Events ([sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5],sys.argv[6],sys.argv[7],sys.argv[8],sys.argv[9],sys.argv[10],sys.argv[11],sys.argv[12],sys.argv[13],sys.argv[14],sys.argv[15],sys.argv[16],sys.argv[17],sys.argv[18],sys.argv[19],sys.argv[20],sys.argv[21]])
	outputfile = TFile(sys.argv[1],"RECREATE")
else:
	print "Something is wrong with the number of arguments!"
	print "Use: python extracthistos.py output.root input.root, if you just want to extract the Histograms from a single root file"
	print "Or use: python extracthistos.py output.root input1.root input2.root, if you want also to add the input Histograms"
	print "currently inplemented: 10 inputs and 20 inputs"
	exit()

#Definition of the Histograms
#Jet Histograms
njets= Histograms ("HnJets", "Number of Jets", 15, -0.5, 14.5)
pt = Histograms("Hpt","Gen-Jet pt",100,0,300)
phi = Histograms("Hphi","Gen-Jet Phi",50,-pi,pi)
theta = Histograms("Htheta","Gen-Jet Theta",50,0,pi)
energy = Histograms("Henergy","Gen-Jet Energy",100,0,600)
firstjetpt = Histograms("HfirstJetpt","Pt of hardest Gen-Jet", 100,0,300)
firstjeteta = Histograms("H1sJeteta","Eta of hardest Gen-Jet",50,-5,5)
secoundjetpt = Histograms("HsecoundJetpt","Pt of 2nd hardest Gen-Jet", 100,0,300)
"""
#Particle Histograms
Htpt = TH1F ("Htpt","pt of Top-Quarks", 100,0,300)
Htbarpt = TH1F ("Htbarpt","pt of Top-Anti-Quark", 100, 0, 300)
Httbarpt = TH1F ("Httbarpt", "pt of t tbar pair", 100, 0 ,300)
"""
# create handle outside of loop
# Handle and lable are pointing at the Branch you want
handle  = Handle ('std::vector<reco::GenJet>')
label = ("ak5GenJets")
particlehandle = Handle ('std::vector<reco::GenParticle>')
particlelabel = ("genParticles")
infohandle = Handle ('<GenEventInfoProduct>')


#ROOT.gROOT.SetStyle('Plain') # white background
#Loop through all Events and Fill the Histograms
print 'Filling new jet histograms'
enumber = 0
for event in events:
        #print "In event ", event
	event.getByLabel (label, handle)
	GenJets = handle.product()
	ievent = event
	ievent.getByLabel ("generator", infohandle)
	Infos = infohandle.product()
	nJets = 0
	firstJetpt = 0
	secoundJetpt = 0
	firstJeteta = 0
	eventweight = Infos.weight()
	print eventweight, enumber
	for Jet in GenJets:
		if Jet.pt() >= ptcut and abs(Jet.eta()) <= etacut:
                        #for JetConstituent in Jet.getJetConstituents():
                        #        print JetConstituent.pdgId(), " no of mothers ", JetConstituent.numberOfMothers()
			nJets = nJets + 1
                        pt.fill(eventweight,Jet.pt())
			phi.fill(eventweight,Jet.phi())
			theta.fill(eventweight,Jet.theta())
			energy.fill(eventweight,Jet.energy())
			if Jet.pt() >= firstJetpt and Jet.pt() >= secoundJetpt:
				secoundJetpt = firstJetpt
				firstJetpt = Jet.pt()
				firstJeteta = Jet.eta()
			elif Jet.pt() >= secoundJetpt and Jet.pt() <= firstJetpt:
				secoundJetpt = Jet.pt()
	enumber=enumber+1
	print firstJetpt
	firstjetpt.fill(eventweight,firstJetpt)
	secoundjetpt.fill(eventweight,secoundJetpt)
	firstjeteta.fill(eventweight,firstJeteta)
	njets.fill(eventweight,nJets)

pt.write()
phi.write()
theta.write()
energy.write()
firstjetpt.write()
secoundjetpt.write()
firstjeteta.write()
njets.write()
"""
        print 'Filling new particle histograms'
#for pevent in events:
        print "In pevent"
        pevent = event
	toppt = 0
	tbarpt = 0
	pevent.getByLabel (particlelabel, particlehandle)
        print "event nr ", pevent
	GenParticles = particlehandle.product()
	for particle in GenParticles:
                if abs(particle.pdgId())<= 6 or particle.pdgId() == 21:
                #if particle.numberOfDaughters() == 0:
                        print "particle nr ", particle
                        print particle.pdgId()
#		if particle.pdgId() == 6:
#			toppt = particle.pt()
#		if particle.pdgId() == -6:
#			tbarpt = particle.pt
		#Htpt.Fill(toppt)
		#Htbarpt.Fill(tbarpt)
		#if toppt != 0 and tbarpt != 0:
			#Httbarpt.Fill(toppt + tbarpt)
"""
