# argParser

import config
from runparams import * 

class ArgParser(object):
    def __init__(self, args):

	#Read in the inputfiles for every loop, else it won't work
	self.runParams = RunParams()
	self.runParams.inputFileList = []
	self.runParams.outputFile = "output.root"
	self.runParams.useVisualization = False
	if config.mode == 0:
		if len(args) > 2:
			dirs = args[2:]
		else:
			dirs = [""]
		for d in dirs:
			for f in glob(os.path.join(d, '*.root')):
				if f[-15:] != '-extracted.root' and f != args[1]:
					self.runParams.inputFileList.append(f)
	elif config.mode == 1:
		for arg in args[2:]:
			if arg[-5:] == '.root':
				self.runParams.inputFileList.append(arg)
			else:
				print "One or more of the Arguments are no .root file. Exiting!"
				exit()
		
	elif config.mode == 2:
		for arg in args[2:]:
			if arg[-5:] == '.root':
				self.runParams.inputFileList.append('root://xrootd.ba.infn.it//' + arg)
			else:
				print "One or more of the Arguments are no .root file. Exiting!"
				exit()
		
		else:
			print "Please change Mode!"
			exit()
		print self.runParams.inputFileList