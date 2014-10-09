import ROOT

#ROOT.Math.LorentzVector('ROOT::Math::PxPyPzE4D<double>')()



def Hash(self):
	return 0

ROOT.reco.GenParticle.__hash__ = Hash

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

# Get human readable particle name by PdgId
def ParticleGetName(pdgId):
	try:
		if pdgId < 0:
			return "-" + PARTICLE[-pdgId]
		else:
			return PARTICLE[pdgId]
	except KeyError:
		return str(pdgId)
	
def ParticleGetPointer(p):
	strP = str(p)
	indexF = strP.find('0x')+2
	particleIdentifier = strP[indexF:]
	indexL = particleIdentifier.find('>')
	return particleIdentifier[:indexL]

def ParticleGetLabel(p):
	return ParticleGetName(p.pdgId()) + " [" + str(p.status()) + "]"

def ParticleGetInfo(p):
	return ParticleGetLabel(p) + " (0x" + ParticleGetPointer(p) + ")"
