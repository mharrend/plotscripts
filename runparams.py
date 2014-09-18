# runparams
class RunParams(object):
	def __init__(self):
		self.inputFileList = []
		self.outputFile = "output-extracted.root"
		self.useVisualization = False
		self.maxEvents = -1
		self.useDebugOutput = False
		self.etaCut = 2.5
		self.pTCuts = [25., 30., 50., 100.]
		self.run = True
		self.zeroAdditionalJets = False