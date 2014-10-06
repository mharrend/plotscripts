from particles import *

from subprocess import call

import thread
import threading
import runparams

#
# Visualization
# 

def GraphViz(fileName, referenceParticles,  runParams, isr_jets, fsr_jets, specialParticles):
	if referenceParticles is None:
		print "Warning in " + fileName + ": MainConstituent is None."
		return 
	diFileName = fileName + ".di"
	pngFileName = fileName + ".png"
	
	f = open(diFileName , 'w')
	f.write("digraph G {\n")
	f.write("graph [nodesep=0.01]\n") 
	
	RecurseParticle(f, referenceParticles[0], 0, "", 0,  runParams, isr_jets, fsr_jets, specialParticles)
	RecurseParticle(f, referenceParticles[1], 0, "", 0,  runParams, isr_jets, fsr_jets, specialParticles)
	
	f.write("}\n")
	f.close()
	
	GraphVizCreate (diFileName, pngFileName )

def GraphVizCreate(diFileName, pngFileName):
	call(["twopi", diFileName ,"-Tpng","-o",pngFileName ])	
	
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
	
def RecurseParticle(f, p, rec, last, index, runParams, isr_jets, fsr_jets, specialParticles, isWDaughter=False, isBDaughter=False, isHDaughter=False):
	
	if p.p4().energy() < runParams.visualizationEnergyCutoff:
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
	#Ws, Bs, Hs
	index = str(p).find('0x')
	particleIdentifier = "P" + (str(p)[index+2:][:8])
	particleLabel = particleName
	particleLabelFinal = particleLabel + "[" + typeString + "]"

	if True:#isWDaughter or isBDaughter or isHDaughter :
		#colorString = "black"
		#textColorString = "black"
		#if isWDaughter:
			#fillColorString = "red"
			##particleLabelFinal = "<W>"
		#if isBDaughter:
			#fillColorString = "orange"
			##particleLabelFinal = "<B>"
		#if isHDaughter:
			#fillColorString = "deeppink"
			##particleLabelFinal = "<H>"
		#styleString = ", style=filled"
	
	#else:
		
		#for w in Ws:
			#if p == w:
				#isWDaughter = True
				
		#for b in Bs:
			#if p == b:
				#isBDaughter = True
			
		#for h in Hs:
			#if p == h:
				#isHDaughter = True
				
		if not (isWDaughter or isBDaughter or isHDaughter):

			for numJet, jet in enumerate(isr_jets):

				nDaughters = jet.numberOfDaughters()
				for i in range(0,nDaughters):
					currentCandidate = jet.daughter(i)
					if currentCandidate == p:
						#particleLabelFinal = str(numJet)
						colorString = "red"
						textColorString = "black"
						fillColorString='"#'+CreateColorFromParams("ISR",numJet)+'"'
						styleString = ", style=filled"
						
			for numJet, jet in enumerate(fsr_jets):
				nDaughters = jet.numberOfDaughters()
				for i in range(0,nDaughters):
					currentCandidate = jet.daughter(i)
					if currentCandidate == p:
						#particleLabelFinal = str(numJet)
						colorString = "blue"
						textColorString = "black"
						fillColorString='"#'+CreateColorFromParams("FSR",numJet)+'"'
						styleString = ", style=filled"
	
	attrib = styleString + ", color=" + colorString + ", fillcolor=" + fillColorString + ", fontcolor=" + textColorString
		
	f.write(particleIdentifier + "[label=\"" + particleLabelFinal + "\"" + attrib + "];\n")
	if last <> "":
		f.write(last + " -> " + particleIdentifier + ";\n")
		
	n = p.numberOfMothers();
	if n>1:
		print GetParticleName(p.pdgId()) + "[" + str(p.status()) + "] has " + str(n) + " mothers."
		for i in range(0,n):
			print GetParticleName(p.mother(i).pdgId()) + " [" + str(p.mother(i).status()) + "]"
			
	n = p.numberOfDaughters();
	for i in range(0,n):
		RecurseParticle(f, p.daughter(i), rec + 1, particleIdentifier, i, runParams, isr_jets, fsr_jets, specialParticles, isWDaughter, isBDaughter, isHDaughter)
