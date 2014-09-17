import ROOT
from ROOT import TH1F, TFile, TTree, TString, gSystem


#----------- Class for Histograms ----------------#
# initialize histograms the same way like when using TH1F only with Histograms
# the constuctor initializes 3 TH1F objects.
class Histogram(object):
    def __init__(self, outputFile, inhalt, title, nbins, minbin, maxbin):
        self.pos = TH1F(inhalt+"pos",title+" with pos. weights",nbins,minbin,maxbin)
        self.neg = TH1F(inhalt+"neg",title+" with neg. weights",nbins,minbin,maxbin)
        self.combined = TH1F(inhalt,title,nbins,minbin,maxbin)
	self.outputFile = outputFile
    def fill(self,weight,value):
        if weight >0:
            self.pos.Fill(value,1.)
            self.combined.Fill(value,1.)
        elif weight < 0:
            self.neg.Fill(value,-1.)
            self.combined.Fill(value,-1.)
    def write(self):
        self.outputFile.WriteTObject(self.pos)
        self.outputFile.WriteTObject(self.neg)
        self.outputFile.WriteTObject(self.combined)
        del self
