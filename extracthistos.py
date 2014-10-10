#!/usr/bin/env python
#Script to extract histograms from the Root Tree, that is produced by Pythia8 in CMSSW
#Can be used to visualize events

from DataFormats.FWLite import Events, Handle
import sys 
from glob import glob
import os
from collections import namedtuple
import time

import ROOT
from sets import Set

import cProfile
import re

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

## write root plots and trigger event visualization
#
#In executable mode, this class is called by the main function.
#In package mode, use can create your own instance of this class.
#Use the run() method.
class ExtractHistos(object):

	## determines the type of the W decay
	#
	#@param referenceParticle	(Reco Gen Particle) the W particle to be examined
	#@return tuple ( (BOOL) TRUE if the decay is leptonic / FALSE otherwise, (Reco Gen Particle) last examined particle )
	def WGetDecayType(self, referenceParticle):
		for cParticle in referenceParticle:
			absPdgId = abs(cParticle.pdgId())
			
			if absPdgId == 24:
				return self.WGetDecayType(cParticle)
			return 11 <= absPdgId <= 18, cParticle
			
		raise Exception("Invalid W Daughters in decay Search")
		
	## writes genGenInformation to extracted-root file
	#
	#@param histos		(object) Histogramm container
	#@param currentCut	(int) currently examined pT-Cut
	#@param eventweight	(double) weight of currently examined event
	#@param genJetsProduct	(object) root container of Gen Jets
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
		
		
	## finds the products of the hardest process
	#
	# Particles can be { Higgs (H), W-Boson (W), B-Quark (B) }
	# This function is used recursively
	#@param firstHardParticle	(Reco Gen Particle) The reactants of the hardest process 
	#@param Ws			[OUT] (list[Reco Gen Particle]) found W particles
	#@param Bs			[OUT] (list[Reco Gen Particle]) found B particles
	#@param Hs			[OUT] (list[Reco Gen Particle]) found H particles
	#@param hasSeenT		(bool) TRUE if this branch is child of a T, FALSE otherwise
	#@param hasSeenW		(bool) TRUE if this branch is child of a W, FALSE otherwise
	#@param hasSeenB		(bool) TRUE if this branch is child of a B, FALSE otherwise
	#@param hasSeenH		(bool) TRUE if this branch is child of a H, FALSE otherwise
	def findSpecialHardParticles(self, firstHardParticle, Ws = [], Bs = [], Hs = [], hasSeenT=False, hasSeenW=False, hasSeenB=False, hasSeenH=False):
		for cParticle in firstHardParticle:
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
			self.findSpecialHardParticles(firstHardParticle,Ws,Bs,Hs,hasSeenT or thisIsTop, hasSeenW or thisIsW , hasSeenB or thisIsB ,hasSeenH or thisIsH )
		return Ws, Bs, Hs 
		
		
	## finds the products of the hardest process and write the result to the extracted-root files
	#
	#@param histos			(object) Histogramm container
	#@param eventweight		(double) weight of currently examined event
	#@param currentCut		(int) currently examined pT-Cut
	#@param firstHardParticles	(list[Reco Gen Particle]) The reactants of the hardest process
	#
	#@return  specialParticles	(tuple (Ws,Bs,Hs)) lists of Reco Gen Particles
	def findAndPlotSpecialHardParticles(self,histos, eventweight, firstHardParticles):
		Ws = []
		Bs = []
		Hs = []
		for firstHard in firstHardParticles:
			Ws, Bs, Hs = self.findSpecialHardParticles(firstHard, Ws, Bs, Hs)
			break
		
		nLeptonicWDecays = 0
		nHadronicWDecays = 0
		
		for idx,w in enumerate(Ws):
			histos.W_Pt.fill(eventweight,w.pt())
			histos.W_M.fill(eventweight,w.p4().M())
			histos.W_E.fill(eventweight,w.energy())
			WDecay = self.WGetDecayType(w)
			isLeptonic = WDecay[0]
			WReferenceparticle = WDecay[1]
			if isLeptonic:
				nLeptonicWDecays = nLeptonicWDecays+1
				histos.W_Leptonic_Pt.fill(eventweight,WReferenceparticle.p4().pt())
				histos.W_Leptonic_E.fill(eventweight,WReferenceparticle.p4().energy())
				
				for cChild in WReferenceparticle:
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
		
		
	## from genParticlesProduct, finds the two mother protons
	#
	#@param genParticlesProduct	(list[Reco Gen Particle]) the event's particles
	#
	#@return  (tuple (p0,p1))	(Reco Gen Particle) the two mother protons
	def getMotherParticles(self, genParticlesProduct):
		return genParticlesProduct[0], genParticlesProduct[1]

	## finds reactants of hardest subprocess
	#
	#@param p	(Reco Gen Particle) starting particle (search is downwards)
	#
	#@return  (tuple (p0,p1))	(Reco Gen Particle) the two reactants of hardest subprocess
	def findFirstHardParticles(self,p, currentList):
		
		cs = p.status()
		
		if 20 <= cs <= 29:
			for d in p:
				nMothers = d.numberOfMothers()
				for i in range(0,nMothers):
					currentList.add(d.mother(i))
			return True
				
		# discard outgoing iss
		if cs == 43 or cs == 44:
			return False
		
		# discard outgoing fss
		if cs == 51 or cs == 52:
			return False
		
		# discard outgoing beam remnant
		if cs == 62 or cs == 63:
			return False
		
		# discard hadronization process particles
		if 70 <= cs <= 79:
			return False
				
		for d in p:
			if self.findFirstHardParticles(d, currentList):
				return True
		return False
		
	## finds all particles between the hardest sub process and the mothers
	#
	# This is later used to search for initial state radiation (ISR).
	#@param particles			(list[Reco Gen Particle]) starting particles
	#@param mainInteractionChainParticles	[OUT] (list[Reco Gen Particle]) result is written to this list
	#@param rec				(int) level of recursion
	def findMainInteractionChainParticles(self,particles, mainInteractionChainParticles, rec = 0):
		for p in particles:
			if rec > 0:
				mainInteractionChainParticles.add(p)
			mothers = []
			nMothers = p.numberOfMothers()
			for i in range (0,nMothers):
				mothers.append(p.mother(i))
			self.findMainInteractionChainParticles(mothers,mainInteractionChainParticles, rec + 1)
		
		
	## finds all initial state radiation (ISR) jet mother particles
	#
	#@param mainInteractionChainParticles	(list[Reco Gen Particle]) all particles between the hardest sub process and the mothers
	#@param firstHardParticles		(list[Reco Gen Particle]) The reactants of the hardest process
	#@param motherParticles			(list[Reco Gen Particle]) The two protons
	#@param isrJetParticles 		[OUT] (list[Reco Gen Particle]) all initial state radiation (ISR) jet mother particles
	def findIsrJetParticles(self,mainInteractionChainParticles,firstHardParticles,motherParticles,isrJetParticles):
		for mic in mainInteractionChainParticles:
			
			if mic == motherParticles[0] or mic == motherParticles[1] or mic in firstHardParticles:
				continue
				
			for dMic in mic:
				found = False
				if dMic in firstHardParticles or dMic in mainInteractionChainParticles:
					continue
				isrJetParticles.add(dMic)
				
	## finds all final state radiation (FSR) jet mother particles coming from the matrix element (ME)
	#
	#@param genParticlesProduct	(list[Reco Gen Particle]) all event particles
	#@param fsrJetParticlesME 	[OUT] (list[Reco Gen Particle]) all final state radiation (FSR) jet mother particles coming from the matrix element (ME)
	def findFsrJetParticlesME(self,genParticlesProduct,fsrJetParticlesME):
		for p in genParticlesProduct:
			if p.status() == 23:
				found = False
				
				nMothers = p.numberOfMothers()
				for i in range (0,nMothers):
					if p.mother(i).status() == 21: 
						found = True
						break
				if found:
					fsrJetParticlesME.add(p)
				
	## finds all particles with status id 21
	#
	#@param genParticlesProduct	(list[Reco Gen Particle]) all event particles
	#@param incomingHardParticles 	[OUT] (list[Reco Gen Particle]) all particles with status id 21
	def findIncomingHardParticles(self,genParticlesProduct, incomingHardParticles):
		for p in genParticlesPall event particlesroduct:
			if p.status() == 21:
				incomingHardParticles.add(p)
				
	## finds all hard matrix element mass particles
	#
	#@param incomingHardParticles		(list[Reco Gen Particle]) all particles with status id 21
	#@param hardMEMassParticles 		[OUT] (lReco Gen Particle])))ist[Reco Gen Particle]) all hard matrix element mass particles
	def findhardMEMassParticles(self,incomingHardParticles, hardMEMassParticles):
		for p in incomingHardParticles:
			for d in p:
				if 22 <= d.status() <= 23 and d.pdgId() <> 21:
					hardMEMassParticles.add(d)
				
	## finds all particles between hard matrix element massParticles downwards until the next particle decay
	#
	#@param hardMassParticle			(list[Reco Gen Particle]) hard matrix element massParticles
	#@param fsrJetParticlesME 			(list[Reco Gen Particle]) FSR Jet Particles from matrix element
	#@param hardMEMassParticleChainParticles 	[OUT] (list[Reco Gen Particle]) all particles between hard matrix element mass particles downwards until the next particle decay
	def findhardMEMassParticleChainParticlesFromMassParticle(self, hardMassParticle, fsrJetParticlesME, hardMEMassParticleChainParticles):
		hardMassParticleStatus = hardMassParticle.status()
		hardMassParticlePdgId = hardMassParticle.pdgId()
		for d in hardMassParticle:
			if d.pdgId() <> hardMassParticlePdgId or hardMassParticle in fsrJetParticlesME:
				continue

			hardMEMassParticleChainParticles.add(hardMassParticle)
			self.findhardMEMassParticleChainParticlesFromMassParticle(d,fsrJetParticlesME,hardMEMassParticleChainParticles)
			return
	
	## finds all particles between hard matrix element massParticles downwards until the next particle decay
	#
	#@param hardMEMassParticles			(list[Reco Gen Particle]) hard matrix element massParticles
	#@param fsrJetParticlesME 			(list[Reco Gen Particle]) all final state radiation (FSR) jet mother particles coming from the matrix element (ME)
	#@param hardMEMassParticleChainParticles 	[OUT] (list[Reco Gen Particle]) all particles between hard matrix element mass particles downwards until the next particle decay
	def findhardMEMassParticleChainParticles(self, hardMEMassParticles, fsrJetParticlesME, hardMEMassParticleChainParticles):
		for hf in hardMEMassParticles:
			self.findhardMEMassParticleChainParticlesFromMassParticle(hf,fsrJetParticlesME,hardMEMassParticleChainParticles)

	## finds all final state radiation (FSR) jet mother particles coming from parton showers (PS)
	#
	#@param hardMEMassParticleChainParticles	(list[Reco Gen Particle]) all particles between hard matrix element mass particles downwards until the next particle decay
	#@param fsrJetParticlesPS 			[OUT] (list[Reco Gen Particle]) all final state radiation (FSR) jet mother particles coming from parton showers (PS)
	def findFsrJetParticlesPS(self,hardMEMassParticleChainParticles,fsrJetParticlesPS):
		for hic in hardMEMassParticleChainParticles:
			hicPdgId = hic.pdgId()
			for d in hic:
				if hicPdgId == d.pdgId():
					continue
				if d in hardMEMassParticleChainParticles:
					continue
				fsrJetParticlesPS.add(d)

	## finds all FSR/ISR jet mother particles and writes them to the root-extracted file
	#
	#@param histos			(object) Histogram container
	#@param eventweight		(double) weight of the current event
	#@param genParticlesProduct	(list[Reco Gen Particle]) all event particles
	#@param motherParticles		(list[Reco Gen Particle]) the two protons
	#@param firstHardParticles	(list[Reco Gen Particle]) The reactants of the hardest process
	#@param fsrIsrParticles 	[OUT] (tupel(list[Reco Gen Particle]),tupel(list[Reco Gen Particle],list[Reco Gen Particle]))) (ISR,(FSRME,FSRPS)) all FSR/ISR jet mother particles
	def findAndPlotFsrIsr(self,histos,eventweight,genParticlesProduct,motherParticles,firstHardParticles,fsrIsrParticles):
		firstHardParticles = Set()
		self.findFirstHardParticles(motherParticles[0],firstHardParticles)
		#self.findFirstHardParticles(motherParticles[1],firstHardParticles)
		mainInteractionChainParticles = Set()
		self.findMainInteractionChainParticles(firstHardParticles,mainInteractionChainParticles)
		isrJetParticles = Set()
		self.findIsrJetParticles(mainInteractionChainParticles,firstHardParticles,motherParticles,isrJetParticles)
		fsrJetParticlesME = Set()
		self.findFsrJetParticlesME(genParticlesProduct,fsrJetParticlesME)
		incomingHardParticles = Set()
		self.findIncomingHardParticles(genParticlesProduct,incomingHardParticles)
		hardMEMassParticles = Set()
		self.findhardMEMassParticles(incomingHardParticles,hardMEMassParticles)
		hardMEMassParticleChainParticles = Set()
		self.findhardMEMassParticleChainParticles(hardMEMassParticles, fsrJetParticlesME, hardMEMassParticleChainParticles)
		fsrJetParticlesPS = Set()
		self.findFsrJetParticlesPS(hardMEMassParticleChainParticles,fsrJetParticlesPS)
		
		for p in isrJetParticles:
			histos.isrjetenergy.fill(eventweight,p.energy())
			histos.isrjetpt.fill(eventweight,p.pt())
		histos.nIsrJets.fill(eventweight,len(isrJetParticles))
			
		for p in fsrJetParticlesME:
			histos.fsrjetenergyME.fill(eventweight,p.energy())
			histos.fsrjetptME.fill(eventweight,p.pt())
			histos.fsrjetenergy.fill(eventweight,p.energy())
			histos.fsrjetpt.fill(eventweight,p.pt())
		histos.nFsrJetsME.fill(eventweight,len(fsrJetParticlesME))
			
		for p in fsrJetParticlesPS:
			histos.fsrjetenergyPS.fill(eventweight,p.energy())
			histos.fsrjetptPS.fill(eventweight,p.pt())
			histos.fsrjetenergy.fill(eventweight,p.energy())
			histos.fsrjetpt.fill(eventweight,p.pt())
		histos.nFsrJetsPS.fill(eventweight,len(fsrJetParticlesPS))
		
		histos.nFsrJets.fill(eventweight,len(fsrJetParticlesPS)+len(fsrJetParticlesME))
		
		# particle Energy
		for p in genParticlesProduct:
			histos.particlePt.fill(eventweight,p.pt())
			histos.particleE.fill(eventweight,p.energy())	
				
		fsrIsrParticles.append(isrJetParticles)
		fsrIsrParticles.append( (fsrJetParticlesME,fsrJetParticlesPS) )

	def processEvent(self,infoObj, genJetsObj, genParticlesObj, currentCut, currentCutIndex, currentEventIndex, currentEvent, histos):
		
		currentEvent.getByLabel (genJetsObj.label, genJetsObj.handle)
		genJetsProduct = genJetsObj.handle.product()
		currentEvent.getByLabel (infoObj.label, infoObj.handle)
		eventweight = infoObj.handle.product().weight()
		currentEvent.getByLabel (genParticlesObj.label, genParticlesObj.handle)
		genParticlesProduct = genParticlesObj.handle.product()
			
		motherParticles = self.getMotherParticles(genParticlesProduct)
		self.plotGenJets(histos,currentCut,eventweight,genJetsProduct)

		fsrIsrParticles = []
		firstHardParticles = Set()
		self.findAndPlotFsrIsr(histos,eventweight,genParticlesProduct,motherParticles,firstHardParticles,fsrIsrParticles)
		
		specialParticles = self.findAndPlotSpecialHardParticles(histos,eventweight,firstHardParticles)

		
		plotSlot = []
	
		# example of how to use the additional plot slot:
		#plotSlot.append( (motherParticles[1],"A0A0A0") )
		
		#print "incomingHardParticles=" + str(len(incomingHardParticles))
		#for p in incomingHardParticles:
			#print ParticleGetName(p.pdgId()) + " [" + str(p.status()) + "]"
			#plotSlot.append( (p,"404080") )
					
		if self.runParams.useVisualization and currentCutIndex == 0:
			fileName = "event" + str(currentEventIndex);
			visual.GraphViz(fileName, motherParticles, self.runParams, fsrIsrParticles, specialParticles, plotSlot)
	
	def run(self, runParams):
		self.runParams = runParams
		InitializeFWLite()
		outputFileObject = TFile(runParams.outputFile,"RECREATE")
		totalEventCount = 0
		Break = False
		
		startTime = time.time()
		
		genJetsObj = namedtuple('Obj', ['handle', 'label'])
		genJetsObj.handle = Handle ('std::vector<reco::GenJet>')
		genJetsObj.label="ak5GenJets"
		
		infoObj = namedtuple('Obj', ['handle', 'label'])
		infoObj.handle = Handle ('<GenEventInfoProduct>')
		infoObj.label="generator"
		
		genParticlesObj = namedtuple('Obj', ['handle', 'label'])
		genParticlesObj.handle = Handle ('std::vector<reco::GenParticle>')
		genParticlesObj.label="genParticles"
		
		for currentCutIndex, currentCut in enumerate(runParams.pTCuts):
			if Break:
				break
			
			events = Events (self.runParams.inputFileList)
			histos = Histos(str(currentCut),outputFileObject)
			
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
			del histos
			
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
    
