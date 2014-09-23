# ExtractHistos Module Tester

from extracthistos import *

print "Module Tester"

runParams = RunParams()
runParams.inputFileList = ["ttH0JetFxFx8TeVCTEQ6M.root"]
		#outputFile = "output-extracted.root"
		#useVisualization = False
		#maxEvents = -1
		#useDebugOutput = False
		#etaCut = 2.5
		#pTCuts = [25., 30., 50., 100.]

extractHistos = ExtractHistos()
extractHistos.run(runParams)

