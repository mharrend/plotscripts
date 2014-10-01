from math import pi

from histogram import *

# histos
class Histos(object):
	def __init__(self, currentCutString, outputFileObject):
		
		self.njets = Histogram (outputFileObject, "HnJets"+currentCutString, "Number of Jets "+currentCutString, 15, -0.5, 14.5)
		self.pt = Histogram(outputFileObject, "Hpt"+currentCutString,"Gen-Jet pt "+currentCutString,100,0,300)
		
		self.W_Pt = Histogram(outputFileObject, "HWpt"+currentCutString,"W-Boson pT "+currentCutString,100,0,300)
		self.B_Pt = Histogram(outputFileObject, "HBpt"+currentCutString,"B-Quark pT "+currentCutString,100,0,300)
		self.H_Pt = Histogram(outputFileObject, "HHpt"+currentCutString,"Higgs pT "+currentCutString,100,0,300)
		self.W_E = Histogram(outputFileObject, "HWE"+currentCutString,"W-Boson Energy "+currentCutString,100,0,300)
		self.B_E = Histogram(outputFileObject, "HBE"+currentCutString,"B-Quark Energy "+currentCutString,100,0,300)
		self.H_E = Histogram(outputFileObject, "HHE"+currentCutString,"Higgs Energy "+currentCutString,100,0,300)
		self.W_deltaR = Histogram(outputFileObject, "HWdeltaR"+currentCutString,"W-Boson deltaR "+currentCutString,100,0,300)
		self.B_deltaR = Histogram(outputFileObject, "HBdeltaR"+currentCutString,"B-Quark deltaR "+currentCutString,100,0,300)
		self.H_deltaR = Histogram(outputFileObject, "HHdeltaR"+currentCutString,"Higgs deltaR "+currentCutString,100,0,300)
		
		self.W_Hadronic_Pt = Histogram(outputFileObject, "HWHpT"+currentCutString,"W-Boson Hadronic pT "+currentCutString,100,0,300)
		self.W_Hadronic_E = Histogram(outputFileObject, "HWHE"+currentCutString,"W-Boson Hadronic Energy "+currentCutString,100,0,300)
		self.W_Leptonic_Pt = Histogram(outputFileObject, "HWLpT"+currentCutString,"W-Boson Leptonic pT "+currentCutString,100,0,300)
		self.W_Leptonic_E = Histogram(outputFileObject, "HWLE"+currentCutString,"W-Boson Leptonic Energy "+currentCutString,100,0,300)
		
		self.W_Leptonic_e_Pt = Histogram(outputFileObject, "HWLepT"+currentCutString,"W-Boson -> Electron pT "+currentCutString,100,0,300)
		self.W_Leptonic_e_E = Histogram(outputFileObject, "HWLeE"+currentCutString,"W-Boson -> Electron Energy "+currentCutString,100,0,300)
		self.W_Leptonic_nue_Pt = Histogram(outputFileObject, "HWLnuepT"+currentCutString,"W-Boson -> nu_e pT "+currentCutString,100,0,300)
		self.W_Leptonic_nue_E = Histogram(outputFileObject, "HWLnueE"+currentCutString,"W-Boson -> nu_e Energy "+currentCutString,100,0,300)
		
		self.W_Leptonic_mu_Pt = Histogram(outputFileObject, "HWLmupT"+currentCutString,"W-Boson -> Muon pT "+currentCutString,100,0,300)
		self.W_Leptonic_mu_E = Histogram(outputFileObject, "HWLmuE"+currentCutString,"W-Boson -> Muon Energy "+currentCutString,100,0,300)
		self.W_Leptonic_numu_Pt = Histogram(outputFileObject, "HWLnumupT"+currentCutString,"W-Boson -> nu_mu pT "+currentCutString,100,0,300)
		self.W_Leptonic_numu_E = Histogram(outputFileObject, "HWLnumuE"+currentCutString,"W-Boson -> nu_mu Energy "+currentCutString,100,0,300)
		
		self.W_Leptonic_t_Pt = Histogram(outputFileObject, "HWLtpT"+currentCutString,"W-Boson -> Tauon pT "+currentCutString,100,0,300)
		self.W_Leptonic_t_E = Histogram(outputFileObject, "HWLtE"+currentCutString,"W-Boson -> Tauon Energy "+currentCutString,100,0,300)
		self.W_Leptonic_nut_Pt = Histogram(outputFileObject, "HWLnutpT"+currentCutString,"W-Boson -> nu_t pT "+currentCutString,100,0,300)
		self.W_Leptonic_nut_E = Histogram(outputFileObject, "HWLnutE"+currentCutString,"W-Boson -> nu_t Energy "+currentCutString,100,0,300)
		
		self.W_n_Leptonic = Histogram (outputFileObject, "HnWLeptonic"+currentCutString, "Number of Leptonic W-Decays "+currentCutString, 3, -0.5, 2.5)
		self.W_n_Hadronic = Histogram (outputFileObject, "HnWHadronic"+currentCutString, "Number of Hadronic W-Decays "+currentCutString, 3, -0.5, 2.5)	
			
		self.W_M = Histogram(outputFileObject, "HWM"+currentCutString,"W-Boson mass "+currentCutString,100,0,1000)
		self.B_M = Histogram(outputFileObject, "HBM"+currentCutString,"B-Quark mass "+currentCutString,100,0,1000)
		self.H_M = Histogram(outputFileObject, "HHM"+currentCutString,"Higgs mass "+currentCutString,100,0,1000)

		self.phi = Histogram(outputFileObject, "Hphi"+currentCutString,"Gen-Jet Phi "+currentCutString,50,-pi,pi)
		self.theta = Histogram(outputFileObject, "Htheta"+currentCutString,"Gen-Jet Theta "+currentCutString,50,0,pi)
		self.energy = Histogram(outputFileObject, "Henergy"+currentCutString,"Gen-Jet Energy "+currentCutString,100,0,600)
		self.firstjetpt = Histogram(outputFileObject, "HfirstJetpt"+currentCutString,"Pt of hardest Gen-Jet "+currentCutString, 100,0,300)
		self.firstjeteta = Histogram(outputFileObject, "H1sJeteta"+currentCutString,"Eta of hardest Gen-Jet "+currentCutString,50,-5,5)
		self.secondjetpt = Histogram(outputFileObject, "HsecondJetpt"+currentCutString,"Pt of 2nd hardest Gen-Jet "+currentCutString, 100,0,300)
		self.isrjetpt = Histogram(outputFileObject, "Hisrjetpt"+currentCutString, "Pt of ISR-Jets "+currentCutString,100,0,300)
		self.fsrjetpt = Histogram(outputFileObject, "Hfsrjetpt"+currentCutString, "Pt of FSR-Jets "+currentCutString,100,0,300)
		self.nIsrJets = Histogram(outputFileObject, "HnIsrJets"+currentCutString,"Number of ISR Jets per Event "+currentCutString, 15, -0.5, 14.5)
		self.nFsrJets = Histogram(outputFileObject, "HnFsrJets"+currentCutString,"Number of FSR Jets per Event "+currentCutString, 15, -0.5, 14.5)
			
	def finalize (self):
		self.pt.finalize()
		self.phi.finalize()
		self.theta.finalize()
		self.energy.finalize()
		self.firstjetpt.finalize()
		self.secondjetpt.finalize()
		self.firstjeteta.finalize()
		self.njets.finalize()
		self.isrjetpt.finalize()
		self.fsrjetpt.finalize()
		self.nIsrJets.finalize()
		self.nFsrJets.finalize()
		self.W_Pt.finalize()
		self.W_E.finalize()
		self.B_Pt.finalize()
		self.B_E.finalize()
		self.H_Pt.finalize()
		self.H_E.finalize()
		
		self.W_n_Leptonic.finalize()
		self.W_n_Hadronic.finalize()
		self.W_M.finalize()
		self.B_M.finalize()
		self.H_M.finalize()
				
		self.W_Leptonic_Pt.finalize()
		self.W_Leptonic_E.finalize()
		self.W_Hadronic_Pt.finalize()
		self.W_Hadronic_E.finalize()
		
		self.W_Leptonic_e_Pt.finalize()
		self.W_Leptonic_e_E.finalize()
		self.W_Leptonic_nue_Pt.finalize()
		self.W_Leptonic_nue_E.finalize()
		self.W_Leptonic_mu_Pt.finalize()
		self.W_Leptonic_mu_E.finalize()
		self.W_Leptonic_numu_Pt.finalize()
		self.W_Leptonic_numu_E.finalize()
		self.W_Leptonic_t_Pt.finalize()
		self.W_Leptonic_t_E.finalize()
		self.W_Leptonic_nut_Pt.finalize()
		self.W_Leptonic_nut_E.finalize()
		
		del self