# argParser

import config
from runparams import * 

class ArgParser(object):
    def displayInfo(self):
	    print "[useVisualization]=" + str (self.runParams.useVisualization)
	    print "[OutputFile]=" + self.runParams.outputFile
	    print "[InputFiles]"
	    for inputFile in self.runParams.inputFileList:
		    print "  " + inputFile
	 
    def __init__(self, args):

	#Read in the inputfiles for every loop, else it won't work
	self.runParams = RunParams()
	self.runParams.inputFileList = []
	self.runParams.outputFile = "output-extracted.root"
	self.runParams.useVisualization = False
	
	print "Args:"
	
	lenArgs = len(args)
	
	for i in range (0, lenArgs):
		# skip first arg as it's the script's name
		if i == 0:
			continue
				
		# provide arg and nextArg (if possible)
		arg = args[i]
		nextArg = None
		if (i < lenArgs - 1):
			nextArg = args[i+1]
			
		# parse switches
	    	if ( arg == "-v" ) or ( arg == "--visualize" )  :
		    self.runParams.useVisualization = True
		    continue
	    	if ( arg == "-o" ) or ( arg == "--output" )  :
		    if nextArg is None or nextArg[0] == '-':
			     raise Exception("'" + arg + "': Parse Error after '--output'!")
		    if nextArg [-15:] <> '-extracted.root':
			    raise Exception("'" + arg + "': Output file must end with '-extracted.root'!")
		    self.runParams.outputFile = nextArg
		    continue
		
		if (arg[0] == '-'):
			raise Exception("'" + arg + "' is not a valid switch!")
		
		# deny input files ending with '-extracted.root', as this is our signature for output files:
		if arg[-15:] == '-extracted.root':
			print "Warning: File '" + arg + "' is being skipped."
			continue
		
		# parse input files:
		if arg[-5:] == '.root':
			self.runParams.inputFileList.append(arg)
			continue
		
		raise Exception("'" + arg + "' is not a valid root file!")
					
	self.displayInfo()
			
	#elif config.mode == 2:
		#for arg in args[2:]:
			#if arg[-5:] == '.root':
				#self.runParams.inputFileList.append('root://xrootd.ba.infn.it//' + arg)
			#else:
				#print "One or more of the Arguments are no .root file. Exiting!"
				#exit()
#		
		#else:
#			print "Please change Mode!"
#			exit()
		#print self.runParams.inputFileList