import copy
from collections import namedtuple
from subprocess import call
from sets import Set

import math
import thread
import threading
import runparams
from particles import *

## determines branch's origin
#
# @return (bool) TRUE if branch is main event, FALSE otherwise
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


## specifies branches
#
# @param referenceParticles 	(list[RecoGenParticle]) motherParticles
# @return  tuple(list[RecoGenParticle],list[RecoGenParticle]) (mainInteractionBranches, underlyingEventBranches)
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

## visualization function
#
# @param fileName 		(string) output file name
# @param referenceParticles 	list[RecoGenParticle] mother particles
# @param runParams 		(object) run args
# @param isrFsr 		(tuple(list[RecoGenParticle],tuple(list[RecoGenParticle],list[RecoGenParticle])))   (ISR,(FSRME,FSRPS)) lists of radiation mother particles
# @param specialParticles 	(tuple(list[RecoGenParticle],list[RecoGenParticle],list[RecoGenParticle])) {Ws,Bs,Hs}
# @param plotSlot 		(list[list[RecoGenParticle],string)]) tuplize particles lists and colors for additional particle colors
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

## creates the call to the GraphVizrenderer
#
# @param runParams 		(object) run args
# @param diFileName 		(string) output di file name
# @param pngFileName 		(string) output png file name
def GraphVizCreate(runParams, diFileName, pngFileName):
	call([runParams.visualizationRenderer, diFileName ,"-Tpng","-o",pngFileName ])	
	
## creates a 2 character color hex string from an integer
#
# @param index 		(int) an arbitrary value
# @param parity 	(int) parity
# @return 	(string) 2 character color hex string from an integer
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
	
## creates a 2 character color hex string from a jet type
#
# @param jetType	(string) jet type { "ISR", "FSR" }
# @param numJet 	(int) numJet
# @return 	(string) 2 character color hex string from a jet type
def CreateColorFromParams(jetType,numJet):
	if jetType == "FSR":
		return "00" + CreateColorChannelFromIndex(numJet) + CreateColorChannelFromIndex(numJet,-1)
	elif jetType == "ISR":
		return "FF" + CreateColorChannelFromIndex(numJet) + "00"
	else:
		raise Exception("unknown jet type: '" + jetType + "'")
	
## clamps energy to scale
#
# @param energy		(double) input energy
# @param scaleMax 	(double) maximum
# @param factor 	(double) factor (multiplier)
# @return 	(double) clamped energy
def ScaleEnergy(energy,scaleMax,factor):
	return min(scaleMax,factor*energy)
	
## creates RBG value from scale (double) value
#
# @param energy		(double) input energy
# @param scaleMax 	(double) maximum
# @param factor 	(double) factor (multiplier)
# @return 		(r,g,b) (double)
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
	
## converts double val to 2 character hex string
#
# @param ratio		(double) input
# @return 		(string) to 2 character hex string
def ratioToHexChannel(ratio):
	color = int(ratio * (255))
	colorString = hex(color)
	result = colorString[2:]
	if len(result) == 1:
		result = "0" + result
	return result	
	
## converts (r,g,b) (double) to 6 character ascii hex color string
#
# @param rgb		(r,g,b) (double)
# @return 		(string) 6 character ascii hex color string
def RgbToString(rgb):
	return ratioToHexChannel(rgb[0]) + ratioToHexChannel(rgb[1]) +ratioToHexChannel(rgb[2])
	
## converts (double) energy to 6 character ascii hex color string
#
# @param energy		(double)
# @return 		(string) 6 character ascii hex color string
def CreateColorFromEnergy(energy):
	if energy > 0:
		scale = ScaleEnergy(math.log(energy),5,0.55)
	else:
		scale = 0
	rgb = scaleToRgb(scale)
	return RgbToString(rgb)
	
## recurses through particle tree to create GraphViz plot
#
# @param diFile			(string) path to difile
# @param p			(RecoGenParticle) current particle
# @param rec			(int) level of recursion
# @param lastParticleIdentifier	(string) this particles mother's identifier from which the link will be created
# @param particleSet		(list[RecoGenParticle])
# @param particleConnectionSet	(list[RecoGenParticle])
# @param runParams		(object) handles args passed to the program
# @param mainInteractionInfo	(object) {mainInteractionBranches,underlyingEventBranches}, both list[RecoGenParticle]
# @param isrFsr			(ISR,(FSRME,FSRPS))
# @param specialParticles	(list[RecoGenParticle])
# @param plotSlot		(object) additional plotting info
# @param isWDaughter		(bool) TRUE is this particle is daughter of a W, FALSE otherwise
# @param isBDaughter		(bool) TRUE is this particle is daughter of a B, FALSE otherwise
# @param isHDaughter		(bool) TRUE is this particle is daughter of a H, FALSE otherwise
def GraphVizRecurseParticle(diFile, p, rec, lastParticleIdentifier, particleSet, particleConnectionSet, runParams, mainInteractionInfo, isrFsr, specialParticles, plotSlot, isWDaughter=False,  isBDaughter=False,  isHDaughter=False):

	cutThis = False
	
	if p.p4().energy() < runParams.visualizationEnergyCutoff:
		cutThis = True

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
		if p.numberOfDaughters() == 1 and p.numberOfMothers() == 1:
			if p.pdgId() == p.daughter(0).pdgId() and p.pdgId() == p.mother(0).pdgId():
				if p.mother(0).numberOfDaughters() == 1:
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
				cutThis = runParams.visualizationCutSpecialJets
				
		for b in specialParticles.Bs:
			if ParticleGetPointer(p) == ParticleGetPointer(b):
				isBDaughter = True
				cutThis = runParams.visualizationCutSpecialJets
			
		for h in specialParticles.Hs:
			if ParticleGetPointer(p) == ParticleGetPointer(h):
				isHDaughter = True
				cutThis = runParams.visualizationCutSpecialJets

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

