import ROOT
from ROOT import TH1F, TFile, TTree, TString, gSystem

#----------- Class for Histograms ----------------#
# initialize histograms the same way like when using TH1F only with Histograms
# the constuctor initializes 3 TH1F objects.
class Histogram(object):
	def __init__(self, outputFile, inhalt, title, nbins, minbin, maxbin):
		#print str(self) + ": __init__"
		self.pos = TH1F(inhalt+"pos",title+" with pos. weights",nbins,minbin,maxbin)
		self.neg = TH1F(inhalt+"neg",title+" with neg. weights",nbins,minbin,maxbin)
		self.combined = TH1F(inhalt,title,nbins,minbin,maxbin)
		self.outputFile = outputFile
	
	def check(self, caller):
		if (self.pos is None) or (self.neg is None) or (self.combined is None):
			print caller + ": Warning: histogram->check() failed. (None)"
			raise Exception("stop.")
			return False
	
		if (str(self.pos) == 'None') or (str(self.neg) == 'None') or (str(self.combined) == 'None'):
			print caller + ": Warning: histogram->check() failed. ('None')"
			raise Exception("stop.")
			return False
		return True
	
	def fill(self,weight,value):
		#print str(self) + ": fill"
		#print str(self.pos)
		#print str(self.neg)
		#print str(self.combined)
		if not self.check("fill"):
			return
		
		if weight >0:
			self.pos.Fill(value,1.)
			self.combined.Fill(value,1.)
		elif weight < 0:
			self.neg.Fill(value,-1.)
			self.combined.Fill(value,-1.)
	def finalize(self):
		
		if not self.check("finalize"):
			return
		
		#print str(self) + ": finalize"
		self.outputFile.WriteTObject(self.pos)
		self.outputFile.WriteTObject(self.neg)
		self.outputFile.WriteTObject(self.combined)
        #del self
	#def __del__(self):
		#print str(self) + ": __del__"
