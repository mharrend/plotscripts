import copy
from collections import namedtuple
from subprocess import call
from sets import Set

import math
import thread
import threading
import runparams
from particles import *

#
# Visualization
# 

def BranchIsMainEvent(particle):
	if 21 <= particle.status() <= 29:
		return True
	numberOfDaughters = particle.numberOfDaughters()
	for i in range (0,numberOfDaughters):
		cParticle = particle.daughter(i)
		isMainEvent = 	BranchIsMainEvent(cParticle)
		if isMainEvent:
			return True
	return False

def GetSpecialBranches(referenceParticles):
	
	underlyingEventBranches = []
	mainInteractionBranches = []
	branches = []
	
	for j in range (0,2):
		numberOfDaughters = referenceParticles[j].numberOfDaughters()
		for i in range (0,numberOfDaughters):
			cParticle = referenceParticles[j].daughter(i)
			branches.append(cParticle)
			
	for branch in branches:
		if BranchIsMainEvent(branch):
			#print "appended " + GetParticleName(branch.pdgId()) + "[" + str(branch.status()) +"] to main"
			mainInteractionBranches.append(branch)
		else:
			#print "appended " + GetParticleName(branch.pdgId()) + "[" + str(branch.status()) +"] to underl"
			underlyingEventBranches.append(branch)
			
	return mainInteractionBranches, underlyingEventBranches

def GraphViz(fileName, referenceParticles,  runParams, isrFsr, specialParticles, plotSlot):
	diFileName = fileName + ".di"
	pngFileName = fileName + ".png"
	
	f = open(diFileName , 'w')
	f.write("digraph G {\n")
	f.write("graph [nodesep=0.01]\n") 
	
	mainInteractionInfo = namedtuple('mainInteractionInfo', 'useMainInteractionInfo referenceParticles mainInteractionBranches underlyingEventBranches')
	mainInteractionInfo.useMainInteractionInfo = not runParams.visualizationShowUnderlyingEvent or not runParams.visualizationShowMainInteraction
	mainInteractionInfo.referenceParticles = referenceParticles
		
	if mainInteractionInfo.useMainInteractionInfo:
		mainInteractionInfo.mainInteractionBranches, mainInteractionInfo.underlyingEventBranches = GetSpecialBranches(referenceParticles)
		
	particleSet = Set()
	particleConnectionSet = Set()
		
	RecurseParticle(f, referenceParticles[0], 0, "", 0,  particleSet, particleConnectionSet, runParams, mainInteractionInfo, isrFsr, specialParticles, plotSlot)
	RecurseParticle(f, referenceParticles[1], 0, "", 0,  particleSet, particleConnectionSet, runParams, mainInteractionInfo, isrFsr, specialParticles, plotSlot)
	
	f.write("}\n")
	f.close()
	
	GraphVizCreate (runParams, diFileName, pngFileName )

def GraphVizCreate(runParams, diFileName, pngFileName):
	call([runParams.visualizationRenderer, diFileName ,"-Tpng","-o",pngFileName ])	
	
def CreateColorChannelFromIndex(index,parity=1):
	color = index * (256-25)
	color = color % 256
	if parity == -1:
		color = 255 - color
	colorString = hex(color)
	result = colorString[2:]
	if len(result) == 1:
		result = "0" + result

	return result
	
def CreateColorFromParams(jetType,numJet):
	if jetType == "FSR":
		return "00" + CreateColorChannelFromIndex(numJet) + CreateColorChannelFromIndex(numJet,-1)
	elif jetType == "ISR":
		return "FF" + CreateColorChannelFromIndex(numJet) + "00"
	else:
		raise Exception("unknown jet type: '" + jetType + "'")
	
def ScaleEnergy(energy,scaleMax,factor):
	return min(scaleMax,factor*energy)
	
def scaleToRgb(scale):
	if scale <= 1:
		c = scale
		return 0,0,c
	if scale <= 2: 
		c = scale-1
		return 0,c,(1-c)
	if scale <= 3: 
		c = scale-2
		return c,1,0
	if scale <= 4: 
		c = scale-3
		return 1,1-c,0
	if scale <= 5: 
		c = scale-4
		return 1,0,c

	return 1,0,1
	
def ratioToHexChannel(ratio):
	color = int(ratio * (255))
	colorString = hex(color)
	result = colorString[2:]
	if len(result) == 1:
		result = "0" + result
	return result	
	
def RgbToString(rgb):
	return ratioToHexChannel(rgb[0]) + ratioToHexChannel(rgb[1]) +ratioToHexChannel(rgb[2])
	
def CreateColorFromEnergy(energy):
	scale = ScaleEnergy(math.log(energy),5,0.55)
	rgb = scaleToRgb(scale)
	return RgbToString(rgb)
	
def GetPointer(p):
	strP = str(p)
	indexF = strP.find('0x')+2
	particleIdentifier = "P" + strP[indexF:]
	indexL = particleIdentifier.find('>')
	return particleIdentifier[:indexL]

	
def RecurseParticle(f, p, rec, last, index, particleSet, particleConnectionSet, runParams, mainInteractionInfo, isrFsr, specialParticles, plotSlot, isWDaughter=False,  isBDaughter=False,  isHDaughter=False):

	if p.p4().energy() < runParams.visualizationEnergyCutoff:
		return
	
	pPtr = GetPointer(p)
	duplicateParticle = pPtr in particleSet
	particleSet.add(pPtr)
	
	if mainInteractionInfo.useMainInteractionInfo:
		if not runParams.visualizationShowUnderlyingEvent:
			if p in mainInteractionInfo.underlyingEventBranches:
				return
		if not runParams.visualizationShowMainInteraction:
			if p in mainInteractionInfo.mainInteractionBranches:
				return
	
	particleName = GetParticleName( p.pdgId() )
	cs = abs(p.status())
	
	typeString = str(cs)
	colorString = "black"
	textColorString = "black"
	fillColorString = "white"
	styleString = ""
	
	if cs == 4:
		styleString = ", style=filled"
		fillColorString="deeppink"
	elif 21 <= cs <= 29:
		#hardest = True
		fillColorString="yellow"
		styleString = ", style=filled"
	#elif 31 <= cs <= 39:
		#fillColorString="green"
		#styleString = ", style=filled"
	#elif 41 <= cs <= 49:
		#iSS = True
		#fillColorString="red"
		#styleString = ", style=filled"
	#elif 51 <= cs <= 59:
		#fSS = True
		#fillColorString="lightblue"
		#styleString = ", style=filled"
	#elif 61 <= cs <= 69:
		#fillColorString="brown"
		#styleString = ", style=filled"
	#elif 71 <= cs <= 79:
		#fillColorString="gray"
		#styleString = ", style=filled"
	
	particleIdentifier = pPtr
	particleLabel = particleName
	particleLabelFinal = particleLabel + "[" + typeString + "]"

	usedPlotSlot = False
	for ps in plotSlot:
		if pPtr == GetPointer(ps[0]):
			colorString = "black"
			textColorString = "black"
			fillColorString='"#'+ps[1]+'"'
			styleString = ", style=filled"
			usedPlotSlot = True
			break

	if usedPlotSlot:
		usedPlotSlot = True # nops in python?!
	elif runParams.visualizationEnergyMode:
		
		colorString = "black"
		textColorString = "black"
		fillColorString='"#'+CreateColorFromEnergy(p.energy())+'"'
		styleString = ", style=filled"
		
	else:

		isrFsrJetColored = False

		for numJet, jet in enumerate(isrFsr[0]):
			currentCandidate = GetPointer(jet)
			if currentCandidate == pPtr:
				#colorString = "green"
				textColorString = "black"
				fillColorString='"#00FF00"'
				styleString = ", style=filled"
				isrFsrJetColored = True
					
		for numJet, jet in enumerate(isrFsr[1][0]):
			currentCandidate = GetPointer(jet)
			if currentCandidate == pPtr:
				#colorString = "blue"
				textColorString = "black"
				fillColorString='"#0000FF"'
				styleString = ", style=filled"
				isrFsrJetColored = True
				
		for numJet, jet in enumerate(isrFsr[1][1]):
			currentCandidate = GetPointer(jet)
			if currentCandidate == pPtr:
				#colorString = "blue"
				textColorString = "black"
				fillColorString='"#00FFFF"'
				styleString = ", style=filled"
				isrFsrJetColored = True

		if not isrFsrJetColored and runParams.visualizationColorSpecialJets and (isWDaughter or isBDaughter or isHDaughter) :
			colorString = "black"
			textColorString = "black"
			if isWDaughter:
				fillColorString = "red"
			if isBDaughter:
				fillColorString = "orange"
			if isHDaughter:
				fillColorString = "deeppink"
			styleString = ", style=filled"
		
		if runParams.visualizationColorSpecialJets:
			for w in specialParticles.Ws:
				if GetPointer(p) == GetPointer(w):
					isWDaughter = True
					
			for b in specialParticles.Bs:
				if GetPointer(p) == GetPointer(b):
					isBDaughter = True
				
			for h in specialParticles.Hs:
				if GetPointer(p) == GetPointer(h):
					isHDaughter = True
	

	
	attrib = styleString + ", color=" + colorString + ", fillcolor=" + fillColorString + ", fontcolor=" + textColorString
		
	f.write(particleIdentifier + "[label=\"" + particleLabelFinal + "\"" + attrib + "];\n")
	
	
	if last <> "":
		particleConnection = last + " -> " + particleIdentifier + ";\n"
		if particleConnection not in particleConnectionSet:
			f.write(particleConnection)
			particleConnectionSet.add(particleConnection)
		
	n = p.numberOfDaughters();
	for i in range(0,n):
		RecurseParticle(f, p.daughter(i), rec + 1, particleIdentifier, i, particleSet, particleConnectionSet, runParams, mainInteractionInfo, isrFsr, specialParticles, plotSlot, isWDaughter, isBDaughter, isHDaughter)
