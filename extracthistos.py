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
		
	def getAllRelevantDaughters(self, runParams, referenceParticle, referenceJets, currentList=Set()):
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
			
			self.getAllRelevantDaughters(runParams, cParticle,referenceJets, currentList)
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
		
	def run(self, runParams):
		global IsInitialized
		if not IsInitialized:
			self.initialize()
			IsInitialized = True
			
		outputFileObject = TFile(runParams.outputFile,"RECREATE")
		totalEventCount = 0
		Break = False
		
		for currentCutIndex, currentCut in enumerate(runParams.pTCuts):
			if Break:
				break
			events = Events (runParams.inputFileList)
			
			currentCutString = str(currentCut) #variable for names of histograms
			#Definition of the Histogram
			#Jet Histogram
			njets = Histogram (outputFileObject, "HnJets"+currentCutString, "Number of Jets "+currentCutString, 15, -0.5, 14.5)
			pt = Histogram(outputFileObject, "Hpt"+currentCutString,"Gen-Jet pt "+currentCutString,100,0,300)
			
			W_Pt = Histogram(outputFileObject, "HWpt"+currentCutString,"W-Boson pT "+currentCutString,100,0,300)
			B_Pt = Histogram(outputFileObject, "HBpt"+currentCutString,"B-Quark pT "+currentCutString,100,0,300)
			H_Pt = Histogram(outputFileObject, "HHpt"+currentCutString,"Higgs pT "+currentCutString,100,0,300)
			W_E = Histogram(outputFileObject, "HWE"+currentCutString,"W-Boson Energy "+currentCutString,100,0,300)
			B_E = Histogram(outputFileObject, "HBE"+currentCutString,"B-Quark Energy "+currentCutString,100,0,300)
			H_E = Histogram(outputFileObject, "HHE"+currentCutString,"Higgs Energy "+currentCutString,100,0,300)
			W_deltaR = Histogram(outputFileObject, "HWdeltaR"+currentCutString,"W-Boson deltaR "+currentCutString,100,0,300)
			B_deltaR = Histogram(outputFileObject, "HBdeltaR"+currentCutString,"B-Quark deltaR "+currentCutString,100,0,300)
			H_deltaR = Histogram(outputFileObject, "HHdeltaR"+currentCutString,"Higgs deltaR "+currentCutString,100,0,300)
			
			W_Hadronic_Pt = Histogram(outputFileObject, "HWHpT"+currentCutString,"W-Boson Hadronic pT "+currentCutString,100,0,300)
			W_Hadronic_E = Histogram(outputFileObject, "HWHE"+currentCutString,"W-Boson Hadronic Energy "+currentCutString,100,0,300)
			W_Leptonic_Pt = Histogram(outputFileObject, "HWLpT"+currentCutString,"W-Boson Leptonic pT "+currentCutString,100,0,300)
			W_Leptonic_E = Histogram(outputFileObject, "HWLE"+currentCutString,"W-Boson Leptonic Energy "+currentCutString,100,0,300)
			
			W_Leptonic_e_Pt = Histogram(outputFileObject, "HWLepT"+currentCutString,"W-Boson -> Electron pT "+currentCutString,100,0,300)
			W_Leptonic_e_E = Histogram(outputFileObject, "HWLeE"+currentCutString,"W-Boson -> Electron Energy "+currentCutString,100,0,300)
			W_Leptonic_nue_Pt = Histogram(outputFileObject, "HWLnuepT"+currentCutString,"W-Boson -> nu_e pT "+currentCutString,100,0,300)
			W_Leptonic_nue_E = Histogram(outputFileObject, "HWLnueE"+currentCutString,"W-Boson -> nu_e Energy "+currentCutString,100,0,300)
			
			W_Leptonic_mu_Pt = Histogram(outputFileObject, "HWLmupT"+currentCutString,"W-Boson -> Muon pT "+currentCutString,100,0,300)
			W_Leptonic_mu_E = Histogram(outputFileObject, "HWLmuE"+currentCutString,"W-Boson -> Muon Energy "+currentCutString,100,0,300)
			W_Leptonic_numu_Pt = Histogram(outputFileObject, "HWLnumupT"+currentCutString,"W-Boson -> nu_mu pT "+currentCutString,100,0,300)
			W_Leptonic_numu_E = Histogram(outputFileObject, "HWLnumuE"+currentCutString,"W-Boson -> nu_mu Energy "+currentCutString,100,0,300)
			
			W_Leptonic_t_Pt = Histogram(outputFileObject, "HWLtpT"+currentCutString,"W-Boson -> Tauon pT "+currentCutString,100,0,300)
			W_Leptonic_t_E = Histogram(outputFileObject, "HWLtE"+currentCutString,"W-Boson -> Tauon Energy "+currentCutString,100,0,300)
			W_Leptonic_nut_Pt = Histogram(outputFileObject, "HWLnutpT"+currentCutString,"W-Boson -> nu_t pT "+currentCutString,100,0,300)
			W_Leptonic_nut_E = Histogram(outputFileObject, "HWLnutE"+currentCutString,"W-Boson -> nu_t Energy "+currentCutString,100,0,300)
			
			W_n_Leptonic = Histogram (outputFileObject, "HnWLeptonic"+currentCutString, "Number of Leptonic W-Decays "+currentCutString, 3, -0.5, 2.5)
			W_n_Hadronic = Histogram (outputFileObject, "HnWHadronic"+currentCutString, "Number of Hadronic W-Decays "+currentCutString, 3, -0.5, 2.5)
			
			
			
			if runParams.useDebugOutput:
			
				W_M = Histogram(outputFileObject, "HWM"+currentCutString,"W-Boson mass "+currentCutString,100,0,1000)
				B_M = Histogram(outputFileObject, "HBM"+currentCutString,"B-Quark mass "+currentCutString,100,0,1000)
				H_M = Histogram(outputFileObject, "HHM"+currentCutString,"Higgs mass "+currentCutString,100,0,1000)
	
				W_M_Children = Histogram(outputFileObject, "HWM_Children"+currentCutString,"W-Boson mass of children "+currentCutString,100,0,1000)
				B_M_Children = Histogram(outputFileObject, "HBM_Children"+currentCutString,"B-Quark mass of children "+currentCutString,100,0,1000)
				H_M_Children = Histogram(outputFileObject, "HHM_Children"+currentCutString,"Higgs mass of children "+currentCutString,100,0,1000)

			
			phi = Histogram(outputFileObject, "Hphi"+currentCutString,"Gen-Jet Phi "+currentCutString,50,-pi,pi)
			theta = Histogram(outputFileObject, "Htheta"+currentCutString,"Gen-Jet Theta "+currentCutString,50,0,pi)
			energy = Histogram(outputFileObject, "Henergy"+currentCutString,"Gen-Jet Energy "+currentCutString,100,0,600)
			firstjetpt = Histogram(outputFileObject, "HfirstJetpt"+currentCutString,"Pt of hardest Gen-Jet "+currentCutString, 100,0,300)
			firstjeteta = Histogram(outputFileObject, "H1sJeteta"+currentCutString,"Eta of hardest Gen-Jet "+currentCutString,50,-5,5)
			secondjetpt = Histogram(outputFileObject, "HsecondJetpt"+currentCutString,"Pt of 2nd hardest Gen-Jet "+currentCutString, 100,0,300)
			isrjetpt = Histogram(outputFileObject, "Hisrjetpt"+currentCutString, "Pt of ISR-Jets "+currentCutString,100,0,300)
			fsrjetpt = Histogram(outputFileObject, "Hfsrjetpt"+currentCutString, "Pt of FSR-Jets "+currentCutString,100,0,300)
			nIsrJets = Histogram(outputFileObject, "HnIsrJets"+currentCutString,"Number of ISR Jets per Event "+currentCutString, 15, -0.5, 14.5)
			nFsrJets = Histogram(outputFileObject, "HnFsrJets"+currentCutString,"Number of FSR Jets per Event "+currentCutString, 15, -0.5, 14.5)
			
			# create handle outside of loop
			# Handle and lable are pointing at the Branch you want
			handle  = Handle ('std::vector<reco::GenJet>')
			label = ("ak5GenJets")
			infohandle = Handle ('<GenEventInfoProduct>')
			
			#ROOT.gROOT.SetStyle('Plain') # white background
			#Loop through all Events and Fill the Histogram
			print 'Processing ' + str(events.size()) + ' events @ pTCut='+currentCutString+'GeV'
			enumber = 0
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
				currentEvent.getByLabel (label, handle)
				GenJets = handle.product()
				currentEvent.getByLabel ("generator", infohandle)
				Infos = infohandle.product()
				nJets = 0
				firstJetpt = 0
				secondJetpt = 0
				firstJeteta = 0
				nISRJets = 0
				nFSRJets = 0
				eventweight = Infos.weight()
				
#				thisEventHasBeenDiGraphed = False
					
				isrJets = []
				fsrJets = []
				referenceParticle = None
					
				for currentJetIndex, currentJet in enumerate(GenJets):
					
					#print '\n* Methods *'
					#for names in dir(currentJet):
						#attr = getattr(currentJet,names)
						#if callable(attr):
							#print names,':',attr.__doc__
					
					if currentJet.pt() >= currentCut and abs(currentJet.eta()) <= runParams.etaCut:
						nJets = nJets + 1
						pt.fill(eventweight,currentJet.pt())
						phi.fill(eventweight,currentJet.phi())
						theta.fill(eventweight,currentJet.theta())
						energy.fill(eventweight,currentJet.energy())
						
						# ISR/FSR implementation	
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
								#if runParams.useDebugOutput:
									#print ( GetParticleName( particle.pdgId() ) ),
									#print cs,
								
								if 21 <= cs <= 29:
									hardest = True
									#if runParams.useDebugOutput:
										#print ( "[H]" ),
								if 41 <= cs <= 49:
									iSS = True
									#if runParams.useDebugOutput:
										#print ( "[IS]" ),
								if 51 <= cs <= 59:
									fSS = True
									#if runParams.useDebugOutput:
										#print ( "[FS]" ),
								#if runParams.useDebugOutput:
									#print (" <- "),
									
								particle = particle.mother()
								particle.mother() # this shall throw
								
								if not (particle is None):
									referenceParticle = particle

							except ReferenceError:
								#if runParams.useDebugOutput:
									#print "."
								break
							#break
							
						if iSS:
							isrJets.append(currentJet)
							isrjetpt.fill(eventweight,currentJet.pt())
							nISRJets = nISRJets + 1
							if runParams.useDebugOutput:
								print ( "[ISR++]" ) 
						#if hardest:
						#	fsrJets.append(currentJet)
						#	fsrjetpt.fill(eventweight,currentJet.pt())
						#	nFSRJets = nFSRJets + 1
						#	if runParams.useDebugOutput: 
						#		print ( "[FSR++]" )
											
						if currentJet.pt() >= firstJetpt and currentJet.pt() >= secondJetpt:
							secondJetpt = firstJetpt
							firstJetpt = currentJet.pt()
							firstJeteta = currentJet.eta()
						elif currentJet.pt() >= secondJetpt and currentJet.pt() <= firstJetpt:
							secondJetpt = currentJet.pt()
							enumber=enumber+1
						firstjetpt.fill(eventweight,firstJetpt)
						secondjetpt.fill(eventweight,secondJetpt)
						firstjeteta.fill(eventweight,firstJeteta)
						
				Ws = []
				Bs = []
				Hs = []
						
				Ws, Bs, Hs = self.findSpecialHardParticles(referenceParticle, Ws, Bs, Hs)
				
				nLeptonicWDecays = 0
				nHadronicWDecays = 0
				
				for idx,w in enumerate(Ws):
					if runParams.useDebugOutput:
						print "[W#" + str(idx) + "]"
						allChildren = self.getAllRelevantDaughters(runParams, w, GenJets, Set())
						sumP4 = ROOT.Math.LorentzVector('ROOT::Math::PxPyPzE4D<double>')()
						
						print "nAllChildren: " + str(len(allChildren))
										
						for f in allChildren:
							sumP4 = sumP4 + f.p4()
							
						W_M.fill(eventweight,w.p4().M())
						W_M_Children.fill(eventweight,sumP4.M())
							
						print "w p4.pt=" + str(w.p4().pt()) + ", sum allChildren pt=" + str(sumP4.pt())
						print "w p4.M=" + str(w.p4().M()) + ", sum allChildren M=" + str(sumP4.M())
						print "w p4.e=" + str(w.p4().energy()) + ", sum allChildren e=" + str(sumP4.energy())
					
					W_Pt.fill(eventweight,w.pt())
					W_E.fill(eventweight,w.energy())
					#W_E.fill(eventweight,w.deltaR())
					
					WDecay = self.WGetDecayType(w)
					isLeptonic = WDecay[0]
					WReferenceparticle = WDecay[1]
					if isLeptonic:
						nLeptonicWDecays = nLeptonicWDecays+1
						W_Leptonic_Pt.fill(eventweight,WReferenceparticle.p4().pt())
						W_Leptonic_E.fill(eventweight,WReferenceparticle.p4().energy())
						
						numDaughters = WReferenceparticle.numberOfDaughters()
						for i in range (0, numDaughters):
							cChild = WReferenceparticle.daughter(i)
							pdgId = cChild.pdgId()
							if pdgId == 11:
								W_Leptonic_e_Pt.fill(eventweight,cChild.p4().pt())
								W_Leptonic_e_E.fill(eventweight,cChild.p4().energy())
							if pdgId == 12:
								W_Leptonic_nue_Pt.fill(eventweight,cChild.p4().pt())
								W_Leptonic_nue_E.fill(eventweight,cChild.p4().energy())
							if pdgId == 13:
								W_Leptonic_mu_Pt.fill(eventweight,cChild.p4().pt())
								W_Leptonic_mu_E.fill(eventweight,cChild.p4().energy())
							if pdgId == 14:
								W_Leptonic_numu_Pt.fill(eventweight,cChild.p4().pt())
								W_Leptonic_numu_E.fill(eventweight,cChild.p4().energy())
							if pdgId == 15:
								W_Leptonic_t_Pt.fill(eventweight,cChild.p4().pt())
								W_Leptonic_t_E.fill(eventweight,cChild.p4().energy())
							if pdgId == 16:
								W_Leptonic_nut_Pt.fill(eventweight,cChild.p4().pt())
								W_Leptonic_nut_E.fill(eventweight,cChild.p4().energy())
								
					else:
						nHadronicWDecays = nHadronicWDecays+1
						W_Hadronic_Pt.fill(eventweight,WReferenceparticle.p4().pt())
						W_Hadronic_E.fill(eventweight,WReferenceparticle.p4().energy())
					
				W_n_Leptonic.fill(eventweight,nLeptonicWDecays)
				W_n_Hadronic.fill(eventweight,nHadronicWDecays)
					
				for idx,b in enumerate( Bs ):
					
					if runParams.useDebugOutput:
						print "[B#" + str(idx) + "]"
						allChildren = self.getAllRelevantDaughters(runParams, b, GenJets, Set())
						sumP4 = ROOT.Math.LorentzVector('ROOT::Math::PxPyPzE4D<double>')()
						
						print "nAllChildren: " + str(len(allChildren))
						
						for f in allChildren:
							sumP4 = sumP4 + f.p4()
							
						B_M.fill(eventweight,b.p4().M())
						B_M_Children.fill(eventweight,sumP4.M())
							
						print "b p4.pt=" + str(b.p4().pt()) + ", sum allChildren pt=" + str(sumP4.pt())
						print "b p4.M=" + str(b.p4().M()) + ", sum allChildren M=" + str(sumP4.M())
						print "b p4.e=" + str(b.p4().energy()) + ", sum allChildren e=" + str(sumP4.energy())
						
					
					B_Pt.fill(eventweight,b.pt())
					B_E.fill(eventweight,b.energy())
					#B_E.fill(eventweight,b.deltaR())
				for idx,h in enumerate( Hs):
					
					if runParams.useDebugOutput:
						print "[H#" + str(idx) + "]"
						allChildren = self.getAllRelevantDaughters(runParams, h, GenJets, Set())
						sumP4 = ROOT.Math.LorentzVector('ROOT::Math::PxPyPzE4D<double>')()
						
						print "nAllChildren: " + str(len(allChildren))
						
						for f in allChildren:
							sumP4 = sumP4 + f.p4()
							
						H_M.fill(eventweight,h.p4().M())
						H_M_Children.fill(eventweight,sumP4.M())
							
						print "h p4.pt=" + str(h.p4().pt()) + ", sum allChildren pt=" + str(sumP4.pt())
						print "h p4.M=" + str(h.p4().M()) + ", sum allChildren M=" + str(sumP4.M())
						print "h p4.e=" + str(h.p4().energy()) + ", sum allChildren e=" + str(sumP4.energy())
											
					H_Pt.fill(eventweight,h.pt())
					H_E.fill(eventweight,h.energy())
					#H_E.fill(eventweight,h.deltaR())
				
				#print "Found: " + str(len(Ws)) + " Ws and " + str(len(Bs)) + " Bs and " + str(len(Hs)) + " Hs." 
						
				if runParams.useVisualization:
					fileName = "cut" + currentCutString + "_event" + str(currentEventIndex);
					visual.GraphViz(fileName, referenceParticle, isrJets, fsrJets, Ws, Bs, Hs)
						
				njets.fill(eventweight,nJets)
				nIsrJets.fill(eventweight,min(15,nISRJets))
				nFsrJets.fill(eventweight,min(15,nFSRJets))
				
			#write all histograms in the output file. After they are wrote, they are getting deleted (s. write() method)
			pt.write()
			phi.write()
			theta.write()
			energy.write()
			firstjetpt.write()
			secondjetpt.write()
			firstjeteta.write()
			njets.write()
			isrjetpt.write()
			fsrjetpt.write()
			nIsrJets.write()
			nFsrJets.write()
			W_Pt.write()
			W_E.write()
			B_Pt.write()
			B_E.write()
			H_Pt.write()
			H_E.write()
			
			W_n_Leptonic.write()
			W_n_Hadronic.write()
			
			if runParams.useDebugOutput:
				W_M.write()
				W_M_Children.write()
				B_M.write()
				B_M_Children.write()
				H_M.write()
				H_M_Children.write()
			
			W_Leptonic_Pt.write()
			W_Leptonic_E.write()
			W_Hadronic_Pt.write()
			W_Hadronic_E.write()
			
			W_Leptonic_e_Pt.write()
			W_Leptonic_e_E.write()
			W_Leptonic_nue_Pt.write()
			W_Leptonic_nue_E.write()
			W_Leptonic_mu_Pt.write()
			W_Leptonic_mu_E.write()
			W_Leptonic_numu_Pt.write()
			W_Leptonic_numu_E.write()
			W_Leptonic_t_Pt.write()
			W_Leptonic_t_E.write()
			W_Leptonic_nut_Pt.write()
			W_Leptonic_nut_E.write()
			
			#delete all variables, that are used again in the next loop
			del handle
			del label
			del infohandle
			del events
			sys.stdout.write('.\n')
			sys.stdout.flush()
		#if runParams.useVisualization:
			#visual.GraphViz_WaitForThreads()

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
    
