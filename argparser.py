# argParser

from runparams import * 
import os.path
import string

class ArgParser(object):
    #def displayInfo(self):
	#    print "[useVisualization]=" + str (self.runParams.useVisualization)
	 #   print "[maxEvents]=" + str (self.runParams.maxEvents)
	  #  print "[useDebugOutput]=" + str (self.runParams.useDebugOutput)
	   # print "[OutputFile]=" + self.runParams.outputFile
	    #print "[InputFiles]"
	    #for inputFile in self.runParams.inputFileList:
		#    print "  " + inputFile
	 
    def parsePtCutString(self, ptCutString):
	return map(float, string.split(ptCutString,',') )
    
    def parseEventsString(self, eventsString):
	return map(int, string.split(eventsString,',') )
	 
	 
    def displayUserInfo(self):
	    print ""
	    print "o------------------o"
	    print "|Extracthistos Info|"
	    print "o------------------o"
	    print ""
	    print "[example usage]"
	    print ""
	    print "extracthistos inputFile.root"
	    print ""
	    print "extracthistos inputFile.root /intputDir/*.root --visualize --output outputfile-extracted.root --ptcuts 20,30,50,100 --etacut 2.5 --limit 100"
	    print ""
	    print "extracthistos inputFile.root /intputDir/*.root -v -o outputfile-extracted.root -p 20,30,50,100 -e 2.5 -l 100"
	    print ""
	    print "[switches]"
	    print " -d   | --debug:                          Show debug information"
	    print " -e   | --etacut:                         Set etaCut (double)"
	    print " -f   | --force:                          Force overwriting of output file"
	    print " -i   | --info:                           Shows this info"
	    print " -l   | --limit:                          Limit maximum # of events processed"
	    print " -o   | --output:                         Set output file (string)"
	    print " -p   | --ptcuts:                         Set pTcuts (list of doubles seperated by ',')"
	    print " -v   | --visualize:                      Create visualization(s)"
	    print " -vnu | --visualize-no-underlying-event:  Do not visualize the underlying event"
	    print " -vni | --visualize-no-main-interaction:  Do not visualize the main interaction"
	    print " -vsj | --visualize-color-special-jets:   Color special particle jets"
	    print " -ve  | --visualize-energy-cutoff:        Specify Visualization energy cutoff (double)"
	    print " -vr  | --visualize-renderer:             Specify GraphViz renderer (string), defaults to 'dot'"
	    print " -#   | --events:                         Specify events to processed (list of ints seperated by ',')"
	    print ""
	    
    def __init__(self, args):

	self.runParams = RunParams()
	
	lenArgs = len(args)
	
	skip = False
	forceOutputOverride = False
	
	for i in range (0, lenArgs):
		# skip first arg as it's the script's name
		if i == 0 or skip:
			skip = False
			continue
				
		# provide arg and nextArg (if possible)
		arg = args[i]
		nextArg = None
		if (i < lenArgs - 1):
			nextArg = args[i+1]
			
		# parse switches
	    	if ( arg == "-d" ) or ( arg == "--debug" )  :
		    self.runParams.useDebugOutput = True
		    continue
		if ( arg == "-e" ) or ( arg == "--etacut" )  :
		    if nextArg is None or nextArg[0] == '-':
			     raise Exception("'" + arg + "': Parse Error after '"+arg+"'!")
		    self.runParams.eta = int(nextArg)
		    skip = True
		    continue
		if ( arg == "-f" ) or ( arg == "--force" )  :
		    forceOutputOverride = True
		    continue
		if ( arg == "-i" ) or ( arg == "--info" )  :
		    self.displayUserInfo()
		    self.runParams.run = False
		    break

		if ( arg == "-l" ) or ( arg == "--limit" )  :
		    if nextArg is None or nextArg[0] == '-':
			     raise Exception("'" + arg + "': Parse Error after '"+arg+"'!")
		    self.runParams.maxEvents = int(nextArg)
		    skip = True
		    continue
	    	if ( arg == "-o" ) or ( arg == "--output" )  :
		    if nextArg is None or nextArg[0] == '-':
			     raise Exception("'" + arg + "': Parse Error after '"+arg+"'!")
		    if nextArg [-15:] <> '-extracted.root':
			    raise Exception("'" + arg + "': Output file must end with '-extracted.root'!")
		    self.runParams.outputFile = nextArg
		    skip = True
		    continue
		if ( arg == "-p" ) or ( arg == "--ptcuts" )  :
		    if nextArg is None or nextArg[0] == '-':
			     raise Exception("'" + arg + "': Parse Error after '"+arg+"'!")
		    ptCutString = nextArg
		    self.runParams.pTCuts = self.parsePtCutString(ptCutString)
		    skip = True
		    continue
		if ( arg == "-v" ) or ( arg == "--visualize" )  :
		    self.runParams.useVisualization = True
		    continue
		
		if ( arg == "-vnu" ) or ( arg == "--visualize-no-underlying-event" )  :
		    self.runParams.visualizationShowUnderlyingEvent = False
		    continue
		
		if ( arg == "-vni" ) or ( arg == "--visualize-no-main-interaction" )  :
		    self.runParams.visualizationShowMainInteraction = False
		    continue
		
		if ( arg == "-vsj" ) or ( arg == "--visualize-color-special-jets" )  :
		    self.runParams.visualizationColorSpecialJets = True
		    continue
		
		if ( arg == "-ve" ) or ( arg == "--visualize-energy-cutoff" )  :
		    if nextArg is None or nextArg[0] == '-':
			     raise Exception("'" + arg + "': Parse Error after '"+arg+"'!")
		    self.runParams.visualizationEnergyCutoff = int(nextArg)
		    skip = True
		    continue
		
		if ( arg == "-vr" ) or ( arg == "--visualize-renderer:" )  :
		    if nextArg is None or nextArg[0] == '-':
			     raise Exception("'" + arg + "': Parse Error after '"+arg+"'!")
		    self.runParams.visualizationRenderer = nextArg
		    skip = True
		    continue
		
		#if ( arg == "-z" ) or ( arg == "--zero-jets" )  :
		    #self.runParams.zeroAdditionalJets = True
		    #continue
		if ( arg == "-#" ) or ( arg == "--events" )  :
		    if nextArg is None or nextArg[0] == '-':
			     raise Exception("'" + arg + "': Parse Error after '"+arg+"'!")
		    eventsString = nextArg
		    self.runParams.events = self.parseEventsString(eventsString)
		    skip = True
		    continue
		
		if (arg[0] == '-'):
			raise Exception("'" + arg + "' is not a valid switch!")
		
		# deny input files ending with '-extracted.root', as this is our signature for output files:
		if arg[-15:] == '-extracted.root':
			print "Warning: File '" + arg + "' is being skipped."
			continue
		
		# parse input files:
		if arg[-5:] == '.root':
			thisFile = arg
			if thisFile[:7] == "/store/":
				if not os.path.isfile(thisFile):
					thisFile = "root://xrootd.ba.infn.it/" + thisFile
			else:
				if not os.path.isfile(thisFile):
					raise Exception("File '" + thisFile + "' does not exist!")
			self.runParams.inputFileList.append(thisFile)
			continue
		
		raise Exception("'" + arg + "' is not a valid root file!")
	
	if self.runParams.useVisualization and len(self.runParams.inputFileList) > 1:
		raise Exception("Visualization is allowed only for exactly one input file.")
		
	
	if self.runParams.run:
		if os.path.isfile(self.runParams.outputFile) and not forceOutputOverride:
			raise Exception("'" + self.runParams.outputFile + "' exists. Use the --force switch to force overriding.")
					
	#self.displayInfo()
