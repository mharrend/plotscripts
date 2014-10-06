#Script to extract histograms from the Root Tree, that is produced by Pythia8 in CMSSW
#Usage: TODO

from DataFormats.FWLite import Events, Handle
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
from histos import *

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
		
	def plotGenJets(self, histos, currentCut, eventweight, genJetsProduct):
		nJets = 0
		firstJetpt = 0
		secondJetpt = 0
		firstJeteta = 0
		nISRJets = 0
		nFSRJets = 0
			
		for currentJetIndex, currentJet in enumerate(genJetsProduct):
			
			if currentJet.pt() >= currentCut and abs(currentJet.eta()) <= self.runParams.etaCut:
				nJets = nJets + 1
				histos.pt.fill(eventweight,currentJet.pt())
				histos.phi.fill(eventweight,currentJet.phi())
				histos.theta.fill(eventweight,currentJet.theta())
				histos.energy.fill(eventweight,currentJet.energy())
				if currentJet.pt() >= firstJetpt and currentJet.pt() >= secondJetpt:
					secondJetpt = firstJetpt
					firstJetpt = currentJet.pt()
					firstJeteta = currentJet.eta()
				elif currentJet.pt() >= secondJetpt and currentJet.pt() <= firstJetpt:
					secondJetpt = currentJet.pt()
				histos.firstjetpt.fill(eventweight,firstJetpt)
				histos.secondjetpt.fill(eventweight,secondJetpt)
				histos.firstjeteta.fill(eventweight,firstJeteta)
			  
		histos.njets.fill(eventweight,nJets)
		histos.nIsrJets.fill(eventweight,min(15,nISRJets))
		histos.nFsrJets.fill(eventweight,min(15,nFSRJets))
		
		
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
		
	def findAndPlotSpecialHardParticles(self,histos, eventweight, referenceParticle):
		Ws = []
		Bs = []
		Hs = []
		Ws, Bs, Hs = self.findSpecialHardParticles(referenceParticle, Ws, Bs, Hs)
		nLeptonicWDecays = 0
		nHadronicWDecays = 0
		
		for idx,w in enumerate(Ws):
			
			histos.W_Pt.fill(eventweight,w.pt())
			histos.W_M.fill(eventweight,w.p4().M())
			histos.W_E.fill(eventweight,w.energy())
			#W_E.fill(eventweight,w.deltaR())
			
			WDecay = self.WGetDecayType(w)
			isLeptonic = WDecay[0]
			WReferenceparticle = WDecay[1]
			if isLeptonic:
				nLeptonicWDecays = nLeptonicWDecays+1
				histos.W_Leptonic_Pt.fill(eventweight,WReferenceparticle.p4().pt())
				histos.W_Leptonic_E.fill(eventweight,WReferenceparticle.p4().energy())
				
				numDaughters = WReferenceparticle.numberOfDaughters()
				for i in range (0, numDaughters):
					cChild = WReferenceparticle.daughter(i)
					pdgId = cChild.pdgId()
					if pdgId == 11:
						histos.W_Leptonic_e_Pt.fill(eventweight,cChild.p4().pt())
						histos.W_Leptonic_e_E.fill(eventweight,cChild.p4().energy())
					if pdgId == 12:
						histos.W_Leptonic_nue_Pt.fill(eventweight,cChild.p4().pt())
						histos.W_Leptonic_nue_E.fill(eventweight,cChild.p4().energy())
					if pdgId == 13:
						histos.W_Leptonic_mu_Pt.fill(eventweight,cChild.p4().pt())
						histos.W_Leptonic_mu_E.fill(eventweight,cChild.p4().energy())
					if pdgId == 14:
						histos.W_Leptonic_numu_Pt.fill(eventweight,cChild.p4().pt())
						histos.W_Leptonic_numu_E.fill(eventweight,cChild.p4().energy())
					if pdgId == 15:
						histos.W_Leptonic_t_Pt.fill(eventweight,cChild.p4().pt())
						histos.W_Leptonic_t_E.fill(eventweight,cChild.p4().energy())
					if pdgId == 16:
						histos.W_Leptonic_nut_Pt.fill(eventweight,cChild.p4().pt())
						histos.W_Leptonic_nut_E.fill(eventweight,cChild.p4().energy())
						
			else:
				nHadronicWDecays = nHadronicWDecays+1
				histos.W_Hadronic_Pt.fill(eventweight,WReferenceparticle.p4().pt())
				histos.W_Hadronic_E.fill(eventweight,WReferenceparticle.p4().energy())
			
		histos.W_n_Leptonic.fill(eventweight,nLeptonicWDecays)
		histos.W_n_Hadronic.fill(eventweight,nHadronicWDecays)
		
			
		for idx,b in enumerate( Bs ):
			histos.B_Pt.fill(eventweight,b.pt())
			histos.B_M.fill(eventweight,b.p4().M())
			histos.B_E.fill(eventweight,b.energy())
			#B_E.fill(eventweight,b.deltaR())
		for idx,h in enumerate( Hs):
			histos.H_Pt.fill(eventweight,h.pt())
			histos.H_M.fill(eventweight,h.p4().M())
			histos.H_E.fill(eventweight,h.energy())
			#H_E.fill(eventweight,h.deltaR())
			
		specialParticles = namedtuple('specialParticles','Ws Bs Hs')
		specialParticles.Ws = Ws
		specialParticles.Bs = Bs
		specialParticles.Hs = Hs
		return specialParticles
		
	def findMotherParticles(self, genParticlesProduct):
		
		return genParticlesProduct[0], genParticlesProduct[1]
		
		#print "total Particles: " + str(genParticlesProduct.size())
		
		#particleMap = Map()
		
		#for currentParticleIndex, currentParticle in enumerate(genParticlesProduct):
			#pdgId = currentParticle.pdgId()
			#status = currentParticle.status()
			#print "particle #" + str(currentParticleIndex) + ": " + GetParticleName(pdgId) + "[" + str(status) + "]"

	def processEvent(self,infoObj, genJetsObj, genParticlesObj, currentCut, currentCutIndex, currentEventIndex, currentEvent, histos):
		currentEvent.getByLabel (genJetsObj.label, genJetsObj.handle)
		genJetsProduct = genJetsObj.handle.product()
		currentEvent.getByLabel (infoObj.label, infoObj.handle)
		eventweight = infoObj.handle.product().weight()
		currentEvent.getByLabel (genParticlesObj.label, genParticlesObj.handle)
		genParticlesProduct = genParticlesObj.handle.product()
		
		motherParticles = self.findMotherParticles(genParticlesProduct)
		
		self.plotGenJets(histos,currentCut,eventweight,genJetsProduct)
		specialParticles = self.findAndPlotSpecialHardParticles(histos,eventweight,motherParticles[0])
		
		if self.runParams.useVisualization and currentCutIndex == 0:
			fileName = "event" + str(currentEventIndex);
			visual.GraphViz(fileName, motherParticles, self.runParams, ([], []), specialParticles)
	
	def run(self, runParams):
		self.runParams = runParams
		InitializeFWLite()
		outputFileObject = TFile(runParams.outputFile,"RECREATE")
		totalEventCount = 0
		Break = False
		
		startTime = time.time()
		
		for currentCutIndex, currentCut in enumerate(runParams.pTCuts):
			if Break:
				break
			
			events = Events (self.runParams.inputFileList)
			
			histos = Histos(str(currentCut),outputFileObject)
			
			genJetsObj = namedtuple('Obj', ['handle', 'label'])
			genJetsObj.handle = Handle ('std::vector<reco::GenJet>')
			genJetsObj.label="ak5GenJets"
			
			infoObj = namedtuple('Obj', ['handle', 'label'])
			infoObj.handle = Handle ('<GenEventInfoProduct>')
			infoObj.label="generator"
			
			genParticlesObj = namedtuple('Obj', ['handle', 'label'])
			genParticlesObj.handle = Handle ('std::vector<reco::GenParticle>')
			genParticlesObj.label="genParticles"
			
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
							
				self.processEvent( infoObj, genJetsObj, genParticlesObj, currentCut, currentCutIndex, currentEventIndex, currentEvent, histos )
				
			endTime = time.time()
			totalTime = endTime - startTime
			histos.finalize()
			
			if not runParams.useDebugOutput:
				print(".\n")
		
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
    
