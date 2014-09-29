#Script to extract histograms from the Root Tree, that is produced by Pythia8 in CMSSW
#Usage: TODO

from DataFormats.FWLite import Events, Handle
from math import pi
import sys 
from glob import glob
import os

import ROOT
from ROOT import TH1F, TFile, TTree, TString, gSystem

from sets import Set

# sibling modules
import visual
from particles import *
from runparams import *
from argparser import *
from histogram import *


IsInitialized = False

class ExtractHistos(object):

	def initialize(self):
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
		
	def getAllRelevantDaughters(self, referenceParticle, referenceJets, currentList=Set()):
		numberOfDaughters = referenceParticle.numberOfDaughters()
		
		if referenceParticle.status() < 10:
			#if runParams.useDebugOutput:
				#print " " * abs(nRecursions) + "*" + GetParticleName( referenceParticle.pdgId() ) + "[" + str(referenceParticle.status()) + "]"

			currentList.add(referenceParticle)
			return currentList
		
		for i in range (0,numberOfDaughters):
					
			cParticle = referenceParticle.daughter(i)
			
			#if runParams.useDebugOutput:
				#print " " * abs(nRecursions) + ">" + GetParticleName( cParticle.pdgId() ) + "[" + str(cParticle.status()) + "]" 
			
			self.getAllRelevantDaughters(cParticle,referenceJets, currentList)
		return currentList
		
	def WGetDecayType(self, referenceParticle):
			
		numberOfDaughters = referenceParticle.numberOfDaughters()
				
		for i in range (0,numberOfDaughters):
			
			cParticle = referenceParticle.daughter(i)
			absPdgId = abs(cParticle.pdgId())
			
			if absPdgId == 24:
				return self.WGetDecayType(cParticle)
			return 11 <= absPdgId <= 18, cParticle
			
		raise Exception("Invalid W Daughters in decay Search")

		
	def findSpecialHardParticles(self, referenceParticle, Ws = [], Bs = [], Hs = [], hasSeenT=False, hasSeenW=False, hasSeenB=False, hasSeenH=False):
		if referenceParticle is not None:
			numberOfDaughters = referenceParticle.numberOfDaughters()
			for i in range (0,numberOfDaughters):
				cParticle = referenceParticle.daughter(i)
				cStatus = cParticle.status()
				
				thisIsTop = False
				thisIsW = False
				thisIsB = False
				thisIsH = False
				
				if 21 <= cStatus <= 29:
					absPdgId = abs(cParticle.pdgId())
					if absPdgId == 6:
						thisIsTop = True
					if absPdgId == 24:
						thisIsW = True
						if hasSeenT and not hasSeenW:
							Ws.append(cParticle)
							continue
					if absPdgId == 5:
						thisIsB = True
						if hasSeenT and not hasSeenB:
							Bs.append(cParticle)
							continue
					if absPdgId == 25:
						thisIsH = True
						Hs.append(cParticle)
						continue
				self.findSpecialHardParticles(cParticle,Ws,Bs,Hs,hasSeenT or thisIsTop, hasSeenW or thisIsW , hasSeenB or thisIsB ,hasSeenH or thisIsH )
		return Ws, Bs, Hs 
		
	def createHistograms(self):
		self.events = Events (self.runParams.inputFileList)
		
		self.currentCutString = str(self.currentCut) #variable for names of histograms
		#Definition of the Histogram
		#Jet Histogram
		self.njets = Histogram (self.outputFileObject, "HnJets"+self.currentCutString, "Number of Jets "+self.currentCutString, 15, -0.5, 14.5)
		self.pt = Histogram(self.outputFileObject, "Hpt"+self.currentCutString,"Gen-Jet pt "+self.currentCutString,100,0,300)
		
		self.W_Pt = Histogram(self.outputFileObject, "HWpt"+self.currentCutString,"W-Boson pT "+self.currentCutString,100,0,300)
		self.B_Pt = Histogram(self.outputFileObject, "HBpt"+self.currentCutString,"B-Quark pT "+self.currentCutString,100,0,300)
		self.H_Pt = Histogram(self.outputFileObject, "HHpt"+self.currentCutString,"Higgs pT "+self.currentCutString,100,0,300)
		self.W_E = Histogram(self.outputFileObject, "HWE"+self.currentCutString,"W-Boson Energy "+self.currentCutString,100,0,300)
		self.B_E = Histogram(self.outputFileObject, "HBE"+self.currentCutString,"B-Quark Energy "+self.currentCutString,100,0,300)
		self.H_E = Histogram(self.outputFileObject, "HHE"+self.currentCutString,"Higgs Energy "+self.currentCutString,100,0,300)
		self.W_deltaR = Histogram(self.outputFileObject, "HWdeltaR"+self.currentCutString,"W-Boson deltaR "+self.currentCutString,100,0,300)
		self.B_deltaR = Histogram(self.outputFileObject, "HBdeltaR"+self.currentCutString,"B-Quark deltaR "+self.currentCutString,100,0,300)
		self.H_deltaR = Histogram(self.outputFileObject, "HHdeltaR"+self.currentCutString,"Higgs deltaR "+self.currentCutString,100,0,300)
		
		self.W_Hadronic_Pt = Histogram(self.outputFileObject, "HWHpT"+self.currentCutString,"W-Boson Hadronic pT "+self.currentCutString,100,0,300)
		self.W_Hadronic_E = Histogram(self.outputFileObject, "HWHE"+self.currentCutString,"W-Boson Hadronic Energy "+self.currentCutString,100,0,300)
		self.W_Leptonic_Pt = Histogram(self.outputFileObject, "HWLpT"+self.currentCutString,"W-Boson Leptonic pT "+self.currentCutString,100,0,300)
		self.W_Leptonic_E = Histogram(self.outputFileObject, "HWLE"+self.currentCutString,"W-Boson Leptonic Energy "+self.currentCutString,100,0,300)
		
		self.W_Leptonic_e_Pt = Histogram(self.outputFileObject, "HWLepT"+self.currentCutString,"W-Boson -> Electron pT "+self.currentCutString,100,0,300)
		self.W_Leptonic_e_E = Histogram(self.outputFileObject, "HWLeE"+self.currentCutString,"W-Boson -> Electron Energy "+self.currentCutString,100,0,300)
		self.W_Leptonic_nue_Pt = Histogram(self.outputFileObject, "HWLnuepT"+self.currentCutString,"W-Boson -> nu_e pT "+self.currentCutString,100,0,300)
		self.W_Leptonic_nue_E = Histogram(self.outputFileObject, "HWLnueE"+self.currentCutString,"W-Boson -> nu_e Energy "+self.currentCutString,100,0,300)
		
		self.W_Leptonic_mu_Pt = Histogram(self.outputFileObject, "HWLmupT"+self.currentCutString,"W-Boson -> Muon pT "+self.currentCutString,100,0,300)
		self.W_Leptonic_mu_E = Histogram(self.outputFileObject, "HWLmuE"+self.currentCutString,"W-Boson -> Muon Energy "+self.currentCutString,100,0,300)
		self.W_Leptonic_numu_Pt = Histogram(self.outputFileObject, "HWLnumupT"+self.currentCutString,"W-Boson -> nu_mu pT "+self.currentCutString,100,0,300)
		self.W_Leptonic_numu_E = Histogram(self.outputFileObject, "HWLnumuE"+self.currentCutString,"W-Boson -> nu_mu Energy "+self.currentCutString,100,0,300)
		
		self.W_Leptonic_t_Pt = Histogram(self.outputFileObject, "HWLtpT"+self.currentCutString,"W-Boson -> Tauon pT "+self.currentCutString,100,0,300)
		self.W_Leptonic_t_E = Histogram(self.outputFileObject, "HWLtE"+self.currentCutString,"W-Boson -> Tauon Energy "+self.currentCutString,100,0,300)
		self.W_Leptonic_nut_Pt = Histogram(self.outputFileObject, "HWLnutpT"+self.currentCutString,"W-Boson -> nu_t pT "+self.currentCutString,100,0,300)
		self.W_Leptonic_nut_E = Histogram(self.outputFileObject, "HWLnutE"+self.currentCutString,"W-Boson -> nu_t Energy "+self.currentCutString,100,0,300)
		
		self.W_n_Leptonic = Histogram (self.outputFileObject, "HnWLeptonic"+self.currentCutString, "Number of Leptonic W-Decays "+self.currentCutString, 3, -0.5, 2.5)
		self.W_n_Hadronic = Histogram (self.outputFileObject, "HnWHadronic"+self.currentCutString, "Number of Hadronic W-Decays "+self.currentCutString, 3, -0.5, 2.5)	
		
		if self.runParams.useDebugOutput:
			
			self.W_M = Histogram(self.outputFileObject, "HWM"+self.currentCutString,"W-Boson mass "+self.currentCutString,100,0,1000)
			self.B_M = Histogram(self.outputFileObject, "HBM"+self.currentCutString,"B-Quark mass "+self.currentCutString,100,0,1000)
			self.H_M = Histogram(self.outputFileObject, "HHM"+self.currentCutString,"Higgs mass "+self.currentCutString,100,0,1000)

			self.W_M_Children = Histogram(self.outputFileObject, "HWM_Children"+self.currentCutString,"W-Boson mass of children "+self.currentCutString,100,0,1000)
			self.B_M_Children = Histogram(self.outputFileObject, "HBM_Children"+self.currentCutString,"B-Quark mass of children "+self.currentCutString,100,0,1000)
			self.H_M_Children = Histogram(self.outputFileObject, "HHM_Children"+self.currentCutString,"Higgs mass of children "+self.currentCutString,100,0,1000)

			
		self.phi = Histogram(self.outputFileObject, "Hphi"+self.currentCutString,"Gen-Jet Phi "+self.currentCutString,50,-pi,pi)
		self.theta = Histogram(self.outputFileObject, "Htheta"+self.currentCutString,"Gen-Jet Theta "+self.currentCutString,50,0,pi)
		self.energy = Histogram(self.outputFileObject, "Henergy"+self.currentCutString,"Gen-Jet Energy "+self.currentCutString,100,0,600)
		self.firstjetpt = Histogram(self.outputFileObject, "HfirstJetpt"+self.currentCutString,"Pt of hardest Gen-Jet "+self.currentCutString, 100,0,300)
		self.firstjeteta = Histogram(self.outputFileObject, "H1sJeteta"+self.currentCutString,"Eta of hardest Gen-Jet "+self.currentCutString,50,-5,5)
		self.secondjetpt = Histogram(self.outputFileObject, "HsecondJetpt"+self.currentCutString,"Pt of 2nd hardest Gen-Jet "+self.currentCutString, 100,0,300)
		self.isrjetpt = Histogram(self.outputFileObject, "Hisrjetpt"+self.currentCutString, "Pt of ISR-Jets "+self.currentCutString,100,0,300)
		self.fsrjetpt = Histogram(self.outputFileObject, "Hfsrjetpt"+self.currentCutString, "Pt of FSR-Jets "+self.currentCutString,100,0,300)
		self.nIsrJets = Histogram(self.outputFileObject, "HnIsrJets"+self.currentCutString,"Number of ISR Jets per Event "+self.currentCutString, 15, -0.5, 14.5)
		self.nFsrJets = Histogram(self.outputFileObject, "HnFsrJets"+self.currentCutString,"Number of FSR Jets per Event "+self.currentCutString, 15, -0.5, 14.5)
			
		# create handle outside of loop
		# Handle and lable are pointing at the Branch you want
		self.handle  = Handle ('std::vector<reco::GenJet>')
		self.label = ("ak5GenJets")
		self.infohandle = Handle ('<GenEventInfoProduct>')
		
	def processEvent(self):
	  self.currentEvent.getByLabel (self.label, self.handle)
	  GenJets = self.handle.product()
	  self.currentEvent.getByLabel ("generator", self.infohandle)
	  Infos = self.infohandle.product()
	  nJets = 0
	  firstJetpt = 0
	  secondJetpt = 0
	  firstJeteta = 0
	  nISRJets = 0
	  nFSRJets = 0
	  eventweight = Infos.weight()
		  
	  isrJets = []
	  fsrJets = []
	  referenceParticle = None
		  
	  for currentJetIndex, currentJet in enumerate(GenJets):
		  
		  if currentJet.pt() >= self.currentCut and abs(currentJet.eta()) <= self.runParams.etaCut:
			  nJets = nJets + 1
			  self.pt.fill(eventweight,currentJet.pt())
			  self.phi.fill(eventweight,currentJet.phi())
			  self.theta.fill(eventweight,currentJet.theta())
			  self.energy.fill(eventweight,currentJet.energy())
			  
			  jetConstituents = currentJet.getJetConstituents()
			  
			  hardest = False
			  iSS = False
			  fSS = False	
			  particle = jetConstituents[0]
			  referenceParticle = particle
				  
			  while(True):
				  oldParticle = particle
				  try:
					  cs = abs(particle.status())
					  
					  if 21 <= cs <= 29:
						  hardest = True
					  if 41 <= cs <= 49:
						  iSS = True
					  if 51 <= cs <= 59:
						  fSS = True
						  
					  particle = particle.mother()
					  particle.mother() # this shall throw
					  
					  if not (particle is None):
						  referenceParticle = particle

				  except ReferenceError:
					  break
			  if not hardest:
				  isrJets.append(currentJet)
				  self.isrjetpt.fill(eventweight,currentJet.pt())
				  nISRJets = nISRJets + 1
				  if self.runParams.useDebugOutput:
					  print ( "[ISR++]" ) 
			  else:
				  fsrJets.append(currentJet)
				  self.fsrjetpt.fill(eventweight,currentJet.pt())
				  nFSRJets = nFSRJets + 1
				  if self.runParams.useDebugOutput: 
					  print ( "[FSR++]" )
								  
			  if currentJet.pt() >= firstJetpt and currentJet.pt() >= secondJetpt:
				  secondJetpt = firstJetpt
				  firstJetpt = currentJet.pt()
				  firstJeteta = currentJet.eta()
			  elif currentJet.pt() >= secondJetpt and currentJet.pt() <= firstJetpt:
				  secondJetpt = currentJet.pt()
				  self.enumber=self.enumber+1
			  self.firstjetpt.fill(eventweight,firstJetpt)
			  self.secondjetpt.fill(eventweight,secondJetpt)
			  self.firstjeteta.fill(eventweight,firstJeteta)
			  
	  Ws = []
	  Bs = []
	  Hs = []
			  
	  Ws, Bs, Hs = self.findSpecialHardParticles(referenceParticle, Ws, Bs, Hs)
	  
	  nLeptonicWDecays = 0
	  nHadronicWDecays = 0
	  
	  for idx,w in enumerate(Ws):
		  if self.runParams.useDebugOutput:
			  print "[W#" + str(idx) + "]"
			  allChildren = self.getAllRelevantDaughters( w, GenJets, Set())
			  sumP4 = ROOT.Math.LorentzVector('ROOT::Math::PxPyPzE4D<double>')()
			  
			  print "nAllChildren: " + str(len(allChildren))
							  
			  for f in allChildren:
				  sumP4 = sumP4 + f.p4()
				  
			  self.W_M.fill(eventweight,w.p4().M())
			  self.W_M_Children.fill(eventweight,sumP4.M())
				  
			  print "w p4.pt=" + str(w.p4().pt()) + ", sum allChildren pt=" + str(sumP4.pt())
			  print "w p4.M=" + str(w.p4().M()) + ", sum allChildren M=" + str(sumP4.M())
			  print "w p4.e=" + str(w.p4().energy()) + ", sum allChildren e=" + str(sumP4.energy())
		  
		  self.W_Pt.fill(eventweight,w.pt())
		  self.W_E.fill(eventweight,w.energy())
		  #W_E.fill(eventweight,w.deltaR())
		  
		  WDecay = self.WGetDecayType(w)
		  isLeptonic = WDecay[0]
		  WReferenceparticle = WDecay[1]
		  if isLeptonic:
			  nLeptonicWDecays = nLeptonicWDecays+1
			  self.W_Leptonic_Pt.fill(eventweight,WReferenceparticle.p4().pt())
			  self.W_Leptonic_E.fill(eventweight,WReferenceparticle.p4().energy())
			  
			  numDaughters = WReferenceparticle.numberOfDaughters()
			  for i in range (0, numDaughters):
				  cChild = WReferenceparticle.daughter(i)
				  pdgId = cChild.pdgId()
				  if pdgId == 11:
					  self.W_Leptonic_e_Pt.fill(eventweight,cChild.p4().pt())
					  self.W_Leptonic_e_E.fill(eventweight,cChild.p4().energy())
				  if pdgId == 12:
					  self.W_Leptonic_nue_Pt.fill(eventweight,cChild.p4().pt())
					  self.W_Leptonic_nue_E.fill(eventweight,cChild.p4().energy())
				  if pdgId == 13:
					  self.W_Leptonic_mu_Pt.fill(eventweight,cChild.p4().pt())
					  self.W_Leptonic_mu_E.fill(eventweight,cChild.p4().energy())
				  if pdgId == 14:
					  self.W_Leptonic_numu_Pt.fill(eventweight,cChild.p4().pt())
					  self.W_Leptonic_numu_E.fill(eventweight,cChild.p4().energy())
				  if pdgId == 15:
					  self.W_Leptonic_t_Pt.fill(eventweight,cChild.p4().pt())
					  self.W_Leptonic_t_E.fill(eventweight,cChild.p4().energy())
				  if pdgId == 16:
					  self.W_Leptonic_nut_Pt.fill(eventweight,cChild.p4().pt())
					  self.W_Leptonic_nut_E.fill(eventweight,cChild.p4().energy())
					  
		  else:
			  nHadronicWDecays = nHadronicWDecays+1
			  self.W_Hadronic_Pt.fill(eventweight,WReferenceparticle.p4().pt())
			  self.W_Hadronic_E.fill(eventweight,WReferenceparticle.p4().energy())
		  
	  self.W_n_Leptonic.fill(eventweight,nLeptonicWDecays)
	  self.W_n_Hadronic.fill(eventweight,nHadronicWDecays)
		  
	  for idx,b in enumerate( Bs ):
		  
		  if self.runParams.useDebugOutput:
			  print "[B#" + str(idx) + "]"
			  allChildren = self.getAllRelevantDaughters( b, GenJets, Set())
			  sumP4 = ROOT.Math.LorentzVector('ROOT::Math::PxPyPzE4D<double>')()
			  
			  print "nAllChildren: " + str(len(allChildren))
			  
			  for f in allChildren:
				  sumP4 = sumP4 + f.p4()
				  
			  self.B_M.fill(eventweight,b.p4().M())
			  self.B_M_Children.fill(eventweight,sumP4.M())
				  
			  print "b p4.pt=" + str(b.p4().pt()) + ", sum allChildren pt=" + str(sumP4.pt())
			  print "b p4.M=" + str(b.p4().M()) + ", sum allChildren M=" + str(sumP4.M())
			  print "b p4.e=" + str(b.p4().energy()) + ", sum allChildren e=" + str(sumP4.energy())
			  
		  
		  self.B_Pt.fill(eventweight,b.pt())
		  self.B_E.fill(eventweight,b.energy())
		  #B_E.fill(eventweight,b.deltaR())
	  for idx,h in enumerate( Hs):
		  
		  if self.runParams.useDebugOutput:
			  print "[H#" + str(idx) + "]"
			  allChildren = self.getAllRelevantDaughters(h, GenJets, Set())
			  sumP4 = ROOT.Math.LorentzVector('ROOT::Math::PxPyPzE4D<double>')()
			  
			  print "nAllChildren: " + str(len(allChildren))
			  
			  for f in allChildren:
				  sumP4 = sumP4 + f.p4()
				  
			  self.H_M.fill(eventweight,h.p4().M())
			  self.H_M_Children.fill(eventweight,sumP4.M())
				  
			  print "h p4.pt=" + str(h.p4().pt()) + ", sum allChildren pt=" + str(sumP4.pt())
			  print "h p4.M=" + str(h.p4().M()) + ", sum allChildren M=" + str(sumP4.M())
			  print "h p4.e=" + str(h.p4().energy()) + ", sum allChildren e=" + str(sumP4.energy())
								  
		  self.H_Pt.fill(eventweight,h.pt())
		  self.H_E.fill(eventweight,h.energy())
		  #H_E.fill(eventweight,h.deltaR())
	  
	  #print "Found: " + str(len(Ws)) + " Ws and " + str(len(Bs)) + " Bs and " + str(len(Hs)) + " Hs." 
			  
	  if self.runParams.useVisualization:
		  fileName = "cut" + self.currentCutString + "_event" + str(self.currentEventIndex);
		  visual.GraphViz(fileName, referenceParticle, isrJets, fsrJets, Ws, Bs, Hs)
			  
	  self.njets.fill(eventweight,nJets)
	  self.nIsrJets.fill(eventweight,min(15,nISRJets))
	  self.nFsrJets.fill(eventweight,min(15,nFSRJets))
		
	def finalize(self):
		self.pt.write()
		self.phi.write()
		self.theta.write()
		self.energy.write()
		self.firstjetpt.write()
		self.secondjetpt.write()
		self.firstjeteta.write()
		self.njets.write()
		self.isrjetpt.write()
		self.fsrjetpt.write()
		self.nIsrJets.write()
		self.nFsrJets.write()
		self.W_Pt.write()
		self.W_E.write()
		self.B_Pt.write()
		self.B_E.write()
		self.H_Pt.write()
		self.H_E.write()
		
		self.W_n_Leptonic.write()
		self.W_n_Hadronic.write()
		
		if self.runParams.useDebugOutput:
			self.W_M.write()
			self.W_M_Children.write()
			self.B_M.write()
			self.B_M_Children.write()
			self.H_M.write()
			self.H_M_Children.write()
		
		self.W_Leptonic_Pt.write()
		self.W_Leptonic_E.write()
		self.W_Hadronic_Pt.write()
		self.W_Hadronic_E.write()
		
		self.W_Leptonic_e_Pt.write()
		self.W_Leptonic_e_E.write()
		self.W_Leptonic_nue_Pt.write()
		self.W_Leptonic_nue_E.write()
		self.W_Leptonic_mu_Pt.write()
		self.W_Leptonic_mu_E.write()
		self.W_Leptonic_numu_Pt.write()
		self.W_Leptonic_numu_E.write()
		self.W_Leptonic_t_Pt.write()
		self.W_Leptonic_t_E.write()
		self.W_Leptonic_nut_Pt.write()
		self.W_Leptonic_nut_E.write()
		
		#delete all variables, that are used again in the next loop
		del self.handle
		del self.label
		del self.infohandle
		del self.events
		sys.stdout.write('.\n')
		sys.stdout.flush()
		
	def run(self, runParams):
		self.runParams = runParams
		global IsInitialized
		if not IsInitialized:
			self.initialize()
			IsInitialized = True
			
		self.outputFileObject = TFile(runParams.outputFile,"RECREATE")
		totalEventCount = 0
		Break = False
		
		for currentCutIndex, currentCut in enumerate(runParams.pTCuts):
			self.currentCut = currentCut
			if Break:
				break
			
			self.createHistograms()
			
			print 'Processing ' + str(self.events.size()) + ' self.events @ pTCut='+self.currentCutString+'GeV'
			self.enumber = 0
			if not runParams.useDebugOutput:
				sys.stdout.write("[                                                  ]\r[")
				sys.stdout.flush()
			percentage50 = 0 
			for self.currentEventIndex, self.currentEvent in enumerate(self.events):
			
				if len(runParams.events) > 0:
					if self.currentEventIndex not in runParams.events:
						continue
			
				totalEventCount = totalEventCount + 1
				if runParams.maxEvents > -1 and totalEventCount > runParams.maxEvents:
					Break = True
					break
			
				if runParams.useDebugOutput:
					print "Event #" + str(self.currentEventIndex)
				else:
					percentageNow = 50. * self.currentEventIndex / self.events.size()
					if percentageNow >= percentage50+1:
						percentage50 = percentage50 + 1 
						sys.stdout.write('.')
						sys.stdout.flush()
				
				self.processEvent()
			
			self.finalize()

if __name__ == '__main__':
	try:
		argParser = ArgParser(sys.argv)
		if not argParser.runParams.run:
			sys.exit()
		extractHistos = ExtractHistos()
		extractHistos.run(argParser.runParams)
	except SystemExit:
		sys.exit()
	except:
		print "Exception: ", sys.exc_info()[1]
		print "Try --info"
		exit
    
