plotscripts
===========

Plotting scripts for FxFx-Merging

Content
===========

* comparePlots.C: ROOT macro; Reads in two or more ROOT files and plots histograms with the same object name from different ROOT files in one plot. If exactly two ROOT files are choosen inside the macro additionally a ratio plot is drawn.
* comparePlots_noRatio.C: ROOT macro; Similar functionality as comparePlots.c, but does not draw a ratio plot.
* extracthistos.py: pyROOT module


extracthistos.py in more detail
===========

The extracthistos.py module consists of the following files:
* argparser.py: This class reads in parameter and settings from the command line and passes them to the main program.
* extracthistos.py: Main program
* extracthistos_moduletester.py: Allows to do a module test after refactoring and changing the classes.
* histogram.py: Creates three TH1F histograms at once. One histogram for the events with positive weight, one histogram for the events with negative weight and one for all events.
* histos.py: Container class for all histograms. Used to write out the variables to the output root files.
* particles.py: Maps PdgID to particle names.
* runparams.py: Class sets the default run parameters used by the main program.
* visuals.py: Contains the parameters and routines for the event visualization.

example usage of extracthistos.py
==========
* Note: ROOT files name *-extracted.root are not used during the read in phase. Thus it is possible to read all ROOT files in a directory except the final output ROOT file output-extracted.root
* "extracthistos.py --info" : Shows all available options
* "extracthistos inputFile.root" : Reads in an input ROOT file and uses the default run parameters, defined in runparams.py, to create an outputfile named inputFile-extracted.root 
* "extracthistos inputFile.root /intputDir/*.root --visualize --output outputfile-extracted.root --ptcuts 20,30,50,100 --etacut 2.5 --limit 100" : Reads in inputFile.root and all ROOT files in inputDir; Visualizes the single events with GraphViz; Creates an output ROOT file named outputfile-extraced.root, in which all histograms will be stored; Applies same pT cuts on the events, Note: For every pT cut the main program will be invoked a further time; Apply an eta cut on the events; Limit the number of processed events.
* "extracthistos inputFile.root /intputDir/*.root -v -o outputfile-extracted.root -p 20,30,50,100 -e 2.5 -l 100": Short version of above example
* Program switches:
** " -d | --debug: Show debug information"
** " -e | --etacut: Set etaCut (double)"
** " -f | --force: Force overwriting of output file"
** " -i | --info: Shows this info"
** " -l | --limit: Limit maximum # of events processed"
** " -o | --output: Set output file (string)"
** " -od | --output-outputdirectory: Set output directory (string)"
** " -p | --ptcuts: Set pTcuts (list of doubles seperated by ',')"
** " -# | --events: Specify events to processed (list of ints seperated by ',')"
** " -m | --multi-processing: create n (int) subprocesses"
** " -% | --modulo: process only every nth event (int)"
** " -%r | --modulo-rest: process only every nth + r event (int)"
** " -v | --visualize: Create visualization(s)"
** " -vs | --visualize-skip-copies: Do not render non-physical particle copies"
** " -vnu | --visualize-no-underlying-event: Do not visualize the underlying event"
** " -vni | --visualize-no-main-interaction: Do not visualize the main interaction"
** " -vsj | --visualize-color-special-jets: Color special particle jets"
** " -vce | --visualize-cutoff-energy: Specify Visualization energy cutoff (double)"
** " -vcs | --visualize-cutoff-special-jets: Cutoff Special Jets"
** " -vcr | --visualize-cutoff-radiation: Cutoff ISR/FSR Jets"
** " -vme | --visualize-mode-energy: Color particles by their energy"
** " -vmp | --visualize-mode-pt: Color particles by their pT"
** " -vr | --visualize-renderer: Specify GraphViz renderer (string), defaults to 'dot'"
