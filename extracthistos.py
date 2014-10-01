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
import time

from collections import namedtuple

# sibling modules
import visual
from particles import *
from runparams import *
from argparser import *
from histogram import *


IsInitialized = False

def InitializeFWLite():
	
	global IsInitialized
	
	if IsInitialized:
		return
	
	cmsswbase = TString.getenv("CMSSW_BASE")	
	print 'Loading FW Lite setup.\n'
	gSystem.Load("libFWCoreFWLite.so")
	ROOT.AutoLibraryLoader.enable()
	gSystem.Load("libDataFormatsFWLite.so")
	gSystem.Load("libDataFormatsPatCandidates.so")
	
	IsInitialized = True

class ExtractHistos(object):
		
	def getAllRelevantDaughters(self, referenceParticle, referenceJets, currentList):
		numberOfDaughters = referenceParticle.numberOfDaughters()
		
		if referenceParticle.status() < 10:
			#if runParams.useDebugOutput:
				#print " " * abs(nRecursions) + "*" + GetParticleName( referenceParticle.pdgId() ) + "[" + str(referenceParticle.status()) + "]"

			currentList.add(referenceParticle)
			return
		
		for i in range (0,numberOfDaughters):
					
			cParticle = referenceParticle.daughter(i)
			
			#if runParams.useDebugOutput:
				#print " " * abs(nRecursions) + ">" + GetParticleName( cParticle.pdgId() ) + "[" + str(cParticle.status()) + "]" 
			
			self.getAllRelevantDaughters(cParticle,referenceJets, currentList)
		return
		
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
		
	def createHistograms(self, currentCutString):
		self.njets = Histogram (self.outputFileObject, "HnJets"+currentCutString, "Number of Jets "+currentCutString, 15, -0.5, 14.5)
		self.pt = Histogram(self.outputFileObject, "Hpt"+currentCutString,"Gen-Jet pt "+currentCutString,100,0,300)
		
		self.W_Pt = Histogram(self.outputFileObject, "HWpt"+currentCutString,"W-Boson pT "+currentCutString,100,0,300)
		self.B_Pt = Histogram(self.outputFileObject, "HBpt"+currentCutString,"B-Quark pT "+currentCutString,100,0,300)
		self.H_Pt = Histogram(self.outputFileObject, "HHpt"+currentCutString,"Higgs pT "+currentCutString,100,0,300)
		self.W_E = Histogram(self.outputFileObject, "HWE"+currentCutString,"W-Boson Energy "+currentCutString,100,0,300)
		self.B_E = Histogram(self.outputFileObject, "HBE"+currentCutString,"B-Quark Energy "+currentCutString,100,0,300)
		self.H_E = Histogram(self.outputFileObject, "HHE"+currentCutString,"Higgs Energy "+currentCutString,100,0,300)
		self.W_deltaR = Histogram(self.outputFileObject, "HWdeltaR"+currentCutString,"W-Boson deltaR "+currentCutString,100,0,300)
		self.B_deltaR = Histogram(self.outputFileObject, "HBdeltaR"+currentCutString,"B-Quark deltaR "+currentCutString,100,0,300)
		self.H_deltaR = Histogram(self.outputFileObject, "HHdeltaR"+currentCutString,"Higgs deltaR "+currentCutString,100,0,300)
		
		self.W_Hadronic_Pt = Histogram(self.outputFileObject, "HWHpT"+currentCutString,"W-Boson Hadronic pT "+currentCutString,100,0,300)
		self.W_Hadronic_E = Histogram(self.outputFileObject, "HWHE"+currentCutString,"W-Boson Hadronic Energy "+currentCutString,100,0,300)
		self.W_Leptonic_Pt = Histogram(self.outputFileObject, "HWLpT"+currentCutString,"W-Boson Leptonic pT "+currentCutString,100,0,300)
		self.W_Leptonic_E = Histogram(self.outputFileObject, "HWLE"+currentCutString,"W-Boson Leptonic Energy "+currentCutString,100,0,300)
		
		self.W_Leptonic_e_Pt = Histogram(self.outputFileObject, "HWLepT"+currentCutString,"W-Boson -> Electron pT "+currentCutString,100,0,300)
		self.W_Leptonic_e_E = Histogram(self.outputFileObject, "HWLeE"+currentCutString,"W-Boson -> Electron Energy "+currentCutString,100,0,300)
		self.W_Leptonic_nue_Pt = Histogram(self.outputFileObject, "HWLnuepT"+currentCutString,"W-Boson -> nu_e pT "+currentCutString,100,0,300)
		self.W_Leptonic_nue_E = Histogram(self.outputFileObject, "HWLnueE"+currentCutString,"W-Boson -> nu_e Energy "+currentCutString,100,0,300)
		
		self.W_Leptonic_mu_Pt = Histogram(self.outputFileObject, "HWLmupT"+currentCutString,"W-Boson -> Muon pT "+currentCutString,100,0,300)
		self.W_Leptonic_mu_E = Histogram(self.outputFileObject, "HWLmuE"+currentCutString,"W-Boson -> Muon Energy "+currentCutString,100,0,300)
		self.W_Leptonic_numu_Pt = Histogram(self.outputFileObject, "HWLnumupT"+currentCutString,"W-Boson -> nu_mu pT "+currentCutString,100,0,300)
		self.W_Leptonic_numu_E = Histogram(self.outputFileObject, "HWLnumuE"+currentCutString,"W-Boson -> nu_mu Energy "+currentCutString,100,0,300)
		
		self.W_Leptonic_t_Pt = Histogram(self.outputFileObject, "HWLtpT"+currentCutString,"W-Boson -> Tauon pT "+currentCutString,100,0,300)
		self.W_Leptonic_t_E = Histogram(self.outputFileObject, "HWLtE"+currentCutString,"W-Boson -> Tauon Energy "+currentCutString,100,0,300)
		self.W_Leptonic_nut_Pt = Histogram(self.outputFileObject, "HWLnutpT"+currentCutString,"W-Boson -> nu_t pT "+currentCutString,100,0,300)
		self.W_Leptonic_nut_E = Histogram(self.outputFileObject, "HWLnutE"+currentCutString,"W-Boson -> nu_t Energy "+currentCutString,100,0,300)
		
		self.W_n_Leptonic = Histogram (self.outputFileObject, "HnWLeptonic"+currentCutString, "Number of Leptonic W-Decays "+currentCutString, 3, -0.5, 2.5)
		self.W_n_Hadronic = Histogram (self.outputFileObject, "HnWHadronic"+currentCutString, "Number of Hadronic W-Decays "+currentCutString, 3, -0.5, 2.5)	
			
		self.W_M = Histogram(self.outputFileObject, "HWM"+currentCutString,"W-Boson mass "+currentCutString,100,0,1000)
		self.B_M = Histogram(self.outputFileObject, "HBM"+currentCutString,"B-Quark mass "+currentCutString,100,0,1000)
		self.H_M = Histogram(self.outputFileObject, "HHM"+currentCutString,"Higgs mass "+currentCutString,100,0,1000)

		self.phi = Histogram(self.outputFileObject, "Hphi"+currentCutString,"Gen-Jet Phi "+currentCutString,50,-pi,pi)
		self.theta = Histogram(self.outputFileObject, "Htheta"+currentCutString,"Gen-Jet Theta "+currentCutString,50,0,pi)
		self.energy = Histogram(self.outputFileObject, "Henergy"+currentCutString,"Gen-Jet Energy "+currentCutString,100,0,600)
		self.firstjetpt = Histogram(self.outputFileObject, "HfirstJetpt"+currentCutString,"Pt of hardest Gen-Jet "+currentCutString, 100,0,300)
		self.firstjeteta = Histogram(self.outputFileObject, "H1sJeteta"+currentCutString,"Eta of hardest Gen-Jet "+currentCutString,50,-5,5)
		self.secondjetpt = Histogram(self.outputFileObject, "HsecondJetpt"+currentCutString,"Pt of 2nd hardest Gen-Jet "+currentCutString, 100,0,300)
		self.isrjetpt = Histogram(self.outputFileObject, "Hisrjetpt"+currentCutString, "Pt of ISR-Jets "+currentCutString,100,0,300)
		self.fsrjetpt = Histogram(self.outputFileObject, "Hfsrjetpt"+currentCutString, "Pt of FSR-Jets "+currentCutString,100,0,300)
		self.nIsrJets = Histogram(self.outputFileObject, "HnIsrJets"+currentCutString,"Number of ISR Jets per Event "+currentCutString, 15, -0.5, 14.5)
		self.nFsrJets = Histogram(self.outputFileObject, "HnFsrJets"+currentCutString,"Number of FSR Jets per Event "+currentCutString, 15, -0.5, 14.5)
			
	def processEvent(self,genJets, currentCut, currentEventIndex, currentEvent):
	  currentEventHandle = None
	  currentEvent.getByLabel (genJets.label, currentEventHandle)
	  genJetsProduct = currentEventHandle.product()
	  currentEvent.getByLabel ("generator", infoHandle)
	  eventweight = infoHandle.product().weight()
	  nJets = 0
	  firstJetpt = 0
	  secondJetpt = 0
	  firstJeteta = 0
	  nISRJets = 0
	  nFSRJets = 0
		  
	  isrJets = []
	  fsrJets = []
	  referenceParticle = None
		  
	  for currentJetIndex, currentJet in enumerate(genJetsProduct):
		  
		  if currentJet.pt() >= currentCut and abs(currentJet.eta()) <= self.runParams.etaCut:
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
		  
		  self.W_Pt.fill(eventweight,w.pt())
		  self.W_M.fill(eventweight,w.p4().M())
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
		  self.B_Pt.fill(eventweight,b.pt())
		  self.B_M.fill(eventweight,b.p4().M())
		  self.B_E.fill(eventweight,b.energy())
		  #B_E.fill(eventweight,b.deltaR())
	  for idx,h in enumerate( Hs):
		  self.H_Pt.fill(eventweight,h.pt())
		  self.H_M.fill(eventweight,h.p4().M())
		  self.H_E.fill(eventweight,h.energy())
		  #H_E.fill(eventweight,h.deltaR())
	  
	  #print "Found: " + str(len(Ws)) + " Ws and " + str(len(Bs)) + " Bs and " + str(len(Hs)) + " Hs." 
			  
	  if self.runParams.useVisualization:
		  fileName = "cut" + currentCutString + "_event" + str(currentEventIndex);
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
		self.W_M.write()
		self.B_M.write()
		self.H_M.write()
				
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
		
	def run(self, runParams):
		self.runParams = runParams
		InitializeFWLite()			
		self.outputFileObject = TFile(runParams.outputFile,"RECREATE")
		totalEventCount = 0
		Break = False
		
		startTime = time.time()
		
		events = Events (self.runParams.inputFileList)
		
		genJets = namedtuple('Handle', ['handle', 'label'])
		genJets.handle = Handle ('std::vector<reco::GenJet>')
		genJets.label="ak5GenJets"
		
		for currentCutIndex, currentCut in enumerate(runParams.pTCuts):
			if Break:
				break
			
			self.createHistograms(str(currentCut))
			
			print 'Processing ' + str(events.size()) + ' events @ pTCut='+str(currentCut)+'GeV'
			if not runParams.useDebugOutput:
				sys.stdout.write("[                                                  ]\r[")
				sys.stdout.flush()
			percentage50 = 0 
			for currentEventIndex, currentEvent in enumerate(events):
			
				if len(runParams.events) > 0:
					if currentEventIndex not in runParams.events:
						continue
			
				totalEventCount = totalEventCount + 1
				if runParams.maxEvents > -1 and totalEventCount > runParams.maxEvents:
					Break = True
					break
			
				if runParams.useDebugOutput:
					print "Event #" + str(currentEventIndex)
				else:
					percentageNow = 50. * currentEventIndex / events.size()
					if percentageNow >= percentage50+1:
						percentage50 = percentage50 + 1 
						sys.stdout.write('.')
						sys.stdout.flush()
							
				self.processEvent( genJets, currentCut, currentEventIndex, currentEvent )
				
			endTime = time.time()
			totalTime = endTime - startTime
			self.finalize()
		
		print "%i events in %.2fs (%.2f events/sec)" % (totalEventCount, totalTime, totalEventCount/totalTime)
			

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
    
