#Script to extract histograms from the Root Tree, that is produced by Pythia8 in CMSSW
#Usage: TODO

from DataFormats.FWLite import Events, Handle
from math import pi
import sys 
from glob import glob
import os

import ROOT
from ROOT import TH1F, TFile, TTree, TString, gSystem

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
		
	def getAllDaughters(self, referenceParticle, currentList=[], nRecursions=-1, onlyFinal=False):
		numberOfDaughters = referenceParticle.numberOfDaughters()
		for i in range (0,numberOfDaughters):
			cParticle = referenceParticle.daughter(i)
			if not onlyFinal:
				currentList.append(cParticle)
			if nRecursions <> 0:
				self.getAllDaughters(cParticle,currentList,nRecursions-1, onlyFinal)
		if onlyFinal and numberOfDaughters == 0 and nRecursions <> -1:
			currentList.append(referenceParticle)
		return currentList
		
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
				
				
				for w in Ws:
					if runParams.useDebugOutput:
						allFinalDaughters = self.getAllDaughters(w, [], -1, True)
						sum = w.p4() - w.p4()
						#print "First.M()=" + str(sum.M())
						for f in allFinalDaughters:
							if f.status() <> 1:
								print GetParticleName(f.pdgId()) + " [" + str(f.status()) + "] M=" + str(f.p4().M())
							sum = sum + f.p4()
						print "w M=" + str(w.p4().M()) + ", sum final Daughters M=" + str(sum.M())
					W_Pt.fill(eventweight,w.pt())
					W_E.fill(eventweight,w.energy())
					#W_E.fill(eventweight,w.deltaR())
				for b in Bs:
					B_Pt.fill(eventweight,b.pt())
					B_E.fill(eventweight,b.energy())
					#B_E.fill(eventweight,b.deltaR())
				for h in Hs:
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
    
