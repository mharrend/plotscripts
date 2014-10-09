# runparams
class RunParams(object):
	def __init__(self):
		self.inputFileList = []
		self.outputFile = "output-extracted.root"
		self.useVisualization = False
		self.visualizationEnergyCutoff = -1
		self.visualizationCutoffRadiation = False
		#self.visualizationPtCutoff = -1
		self.visualizationShowUnderlyingEvent = True
		self.visualizationShowMainInteraction = True
		self.visualizationColorSpecialJets = False
		self.visualizationRenderer = "dot"
		self.visualizationEnergyMode = False
		self.visualizationPtMode = False
		self.visualizationSkipCopies = False
		self.visualizationCutSpecialJets = False
		self.maxEvents = -1
		self.useDebugOutput = False
		self.etaCut = 2.5
		self.pTCuts = [25., 30., 50., 100.]
		self.events = []
		self.run = True
		self.zeroAdditionalJets = False