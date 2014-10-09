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
			#print "appended " + ParticleGetName(branch.pdgId()) + "[" + str(branch.status()) +"] to main"
			mainInteractionBranches.append(branch)
		else:
			#print "appended " + ParticleGetName(branch.pdgId()) + "[" + str(branch.status()) +"] to underl"
			underlyingEventBranches.append(branch)
			
	return mainInteractionBranches, underlyingEventBranches

def GraphViz(fileName, referenceParticles,  runParams, isrFsr, specialParticles, plotSlot):
	diFileName = fileName + ".di"
	pngFileName = fileName + ".png"
	
	diFile = open(diFileName , 'w')
	diFile.write("digraph G {\n")
	diFile.write("graph [nodesep=0.01]\n") 
	
	mainInteractionInfo = namedtuple('mainInteractionInfo', 'useMainInteractionInfo referenceParticles mainInteractionBranches underlyingEventBranches')
	mainInteractionInfo.useMainInteractionInfo = not runParams.visualizationShowUnderlyingEvent or not runParams.visualizationShowMainInteraction
	mainInteractionInfo.referenceParticles = referenceParticles
		
	if mainInteractionInfo.useMainInteractionInfo:
		mainInteractionInfo.mainInteractionBranches, mainInteractionInfo.underlyingEventBranches = GetSpecialBranches(referenceParticles)
		
	particleSet = Set()
	particleConnectionSet = Set()
	
	lastParticleIdentifier = ""
	startingRecursionLevel = 0
		
	GraphVizRecurseParticle(diFile, referenceParticles[0], startingRecursionLevel, lastParticleIdentifier, particleSet, particleConnectionSet, runParams, mainInteractionInfo, isrFsr, specialParticles, plotSlot)
	GraphVizRecurseParticle(diFile, referenceParticles[1], startingRecursionLevel, lastParticleIdentifier, particleSet, particleConnectionSet, runParams, mainInteractionInfo, isrFsr, specialParticles, plotSlot)
	
	diFile.write("}\n")
	diFile.close()
	
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
	#print scale
	if scale <= 1:
		c = max(0,scale)
		return 0,0,0.5+c/2
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
	if energy > 0:
		scale = ScaleEnergy(math.log(energy),5,0.55)
	else:
		scale = 0
	rgb = scaleToRgb(scale)
	return RgbToString(rgb)
	
def GraphVizRecurseParticle(diFile, p, rec, lastParticleIdentifier, particleSet, particleConnectionSet, runParams, mainInteractionInfo, isrFsr, specialParticles, plotSlot, isWDaughter=False,  isBDaughter=False,  isHDaughter=False):

	cutThis = False
	
	if p.p4().energy() < runParams.visualizationEnergyCutoff:
		cutThis = True
		#return
	
	#if p.pt() < runParams.visualizationPtCutoff:
		#cutThis = True
		##return
	
	pPtr = ParticleGetPointer(p)
	duplicateParticle = pPtr in particleSet
	particleSet.add(pPtr)
	
	if mainInteractionInfo.useMainInteractionInfo:
		if not runParams.visualizationShowUnderlyingEvent:
			if p in mainInteractionInfo.underlyingEventBranches:
				return
		if not runParams.visualizationShowMainInteraction:
			if p in mainInteractionInfo.mainInteractionBranches:
				return
	
	skipThis = False
	
	if runParams.visualizationSkipCopies:
		if p.numberOfDaughters() == 1:
			skipThis = True

	
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
		skipThis = False
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
	
	particleIdentifier = "P" + pPtr
	particleLabelFinal = ParticleGetLabel(p)

	promimentColorMode = False

	usedPlotSlot = False
	for ps in plotSlot:
		if pPtr == ParticleGetPointer(ps[0]):
			colorString = "black"
			textColorString = "black"
			fillColorString='"#'+ps[1]+'"'
			styleString = ", style=filled"
			usedPlotSlot = True
			break

	if usedPlotSlot:
		pass
	elif runParams.visualizationEnergyMode:
		colorString = "black"
		textColorString = "black"
		fillColorString='"#'+CreateColorFromEnergy(p.energy())+'"'
		styleString = ", style=filled"
		promimentColorMode = True
	elif runParams.visualizationPtMode:
		colorString = "black"
		textColorString = "black"
		fillColorString='"#'+CreateColorFromEnergy(p.pt()*5)+'"'
		styleString = ", style=filled"
		promimentColorMode = True
			
	isrFsrJetColored = False

	for numJet, jet in enumerate(isrFsr[0]):
		currentCandidate = ParticleGetPointer(jet)
		if currentCandidate == pPtr:
			if not promimentColorMode:
				textColorString = "black"
				fillColorString='"#00FF00"'
				styleString = ", style=filled"
			isrFsrJetColored = True
				
	for numJet, jet in enumerate(isrFsr[1][0]):
		currentCandidate = ParticleGetPointer(jet)
		if currentCandidate == pPtr:
			if not promimentColorMode:
				textColorString = "black"
				fillColorString='"#0000FF"'
				styleString = ", style=filled"
			isrFsrJetColored = True
			
	for numJet, jet in enumerate(isrFsr[1][1]):
		currentCandidate = ParticleGetPointer(jet)
		if currentCandidate == pPtr:
			if not promimentColorMode:
				textColorString = "black"
				fillColorString='"#00FFFF"'
				styleString = ", style=filled"
			isrFsrJetColored = True
			
	if runParams.visualizationCutoffRadiation and isrFsrJetColored:
		cutThis = True

	if not isrFsrJetColored and runParams.visualizationColorSpecialJets and (isWDaughter or isBDaughter or isHDaughter) :
		if not promimentColorMode:
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
			if ParticleGetPointer(p) == ParticleGetPointer(w):
				isWDaughter = True
				
		for b in specialParticles.Bs:
			if ParticleGetPointer(p) == ParticleGetPointer(b):
				isBDaughter = True
			
		for h in specialParticles.Hs:
			if ParticleGetPointer(p) == ParticleGetPointer(h):
				isHDaughter = True

	attrib = styleString + ", color=" + colorString + ", fillcolor=" + fillColorString + ", fontcolor=" + textColorString
		
	if not skipThis:
		
		diFile.write(particleIdentifier + "[label=\"" + particleLabelFinal + "\"" + attrib + "];\n")
		
		if lastParticleIdentifier <> "":
			particleConnection = lastParticleIdentifier + " -> " + particleIdentifier + ";\n"
			if particleConnection not in particleConnectionSet:
				diFile.write(particleConnection)
				particleConnectionSet.add(particleConnection)
		
	if cutThis:
		return
		
	n = p.numberOfDaughters();
	for i in range(0,n):
		if not skipThis:
			GraphVizRecurseParticle(diFile, p.daughter(i), rec + 1, particleIdentifier, particleSet, particleConnectionSet, runParams, mainInteractionInfo, isrFsr, specialParticles, plotSlot, isWDaughter, isBDaughter, isHDaughter)
		else:
			GraphVizRecurseParticle(diFile, p.daughter(i), rec + 1, lastParticleIdentifier, particleSet, particleConnectionSet, runParams, mainInteractionInfo, isrFsr, specialParticles, plotSlot, isWDaughter, isBDaughter, isHDaughter)

