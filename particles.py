import ROOT

# Use human readable particle names for pdgIds according to 
# http://pdg.lbl.gov/2014/reviews/rpp2014-rev-monte-carlo-numbering.pdf
PARTICLE = { 1 : "d",
	2 : "u",
	3 : "s",
	4 : "c",
	5 : "b",
	6 : "t",
	7 : "b'",
	8 : "t'",
	11 : "e",
	12 : "nu_e",
	13 : "mu",
	14 : "nu_mu",
	15 : "tau",
	16 : "nu_tau",
	17 : "tau'",
	18 : "nu_tau'",
	21 : "g",
	22 : "y",
	23 : "Z",
	24 : "W",
	25 : "H",
	2112 : "n",
	2212 : "p"
	}

## Get human readable particle name by PdgId
def ParticleGetName(pdgId):
	try:
		if pdgId < 0:
			return "-" + PARTICLE[-pdgId]
		else:
			return PARTICLE[pdgId]
	except KeyError:
		return str(pdgId)
	
## Get Pointer adress as hash
def ParticleGetPointer(p):
	strP = str(p)
	indexF = strP.find('0x')+2
	particleIdentifier = strP[indexF:]
	indexL = particleIdentifier.find('>')
	return particleIdentifier[:indexL]

## Create human readable label
def ParticleGetLabel(p):
	return ParticleGetName(p.pdgId()) + " [" + str(p.status()) + "]"

## Create human readable label and more info
def ParticleGetInfo(p):
	return ParticleGetLabel(p) + " (0x" + ParticleGetPointer(p) + ")"

## Override RecoGenObject __hash__() function
def Particle__hash__(self):
	try:
		return self.___hash
		
	except:
		self.___hash = int(ParticleGetPointer(self),16)
	return self.___hash

## Override RecoGenObject __eq__() function
def Particle__eq__(self,other):
	return self.__hash__() == other.__hash__()


ROOT.reco.GenParticle.__hash__ = Particle__hash__
ROOT.reco.GenParticle.__eq__ = Particle__eq__
