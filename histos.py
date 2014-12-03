from math import pi

from histogram import *

## Container for all histograms written to extracted-root files
class Histos(object):
	
	## called to initialize all histograms
	def __init__(self, currentCutString, outputFileObject):
		
		self.njets = Histogram (outputFileObject, "HnJets"+currentCutString, "Number of Jets "+currentCutString, 12, -0.5, 11.5)
		self.pt = Histogram(outputFileObject, "Hpt"+currentCutString,"Gen-Jet pt "+currentCutString,50,50,300)
		
		self.W_Pt = Histogram(outputFileObject, "HWpt"+currentCutString,"W-Boson pT "+currentCutString,50,0,500)
		self.B_Pt = Histogram(outputFileObject, "HBpt"+currentCutString,"B-Quark pT "+currentCutString,50,0,500)
		self.H_Pt = Histogram(outputFileObject, "HHpt"+currentCutString,"Higgs pT "+currentCutString,50,0,300)
		self.T_Pt = Histogram(outputFileObject, "HTpt"+currentCutString,"Top pT "+currentCutString,50,0,500)
		self.W_E = Histogram(outputFileObject, "HWE"+currentCutString,"W-Boson Energy "+currentCutString,50,50,2000)
		self.B_E = Histogram(outputFileObject, "HBE"+currentCutString,"B-Quark Energy "+currentCutString,50,0,2000)
		self.H_E = Histogram(outputFileObject, "HHE"+currentCutString,"Higgs Energy "+currentCutString,50,50,300)
		self.T_E = Histogram(outputFileObject, "HTE"+currentCutString,"Top Energy "+currentCutString,50,0,2000)
		self.W_deltaPhi = Histogram(outputFileObject, "HWdeltaPhi"+currentCutString,"W-Boson deltaPhi "+currentCutString,50,-pi,pi)
		self.B_deltaPhi = Histogram(outputFileObject, "HBdeltaPhi"+currentCutString,"B-Quark deltaPhi "+currentCutString,50,-pi,pi)
		self.H_deltaPhi = Histogram(outputFileObject, "HHdeltaPhi"+currentCutString,"Higgs deltaPhi "+currentCutString,50,-pi,pi)
		self.T_deltaPhi = Histogram(outputFileObject, "HTdeltaPhi"+currentCutString,"Top deltaPhi "+currentCutString,50,-pi,pi)
		
		self.W_Hadronic_Pt = Histogram(outputFileObject, "HWHpT"+currentCutString,"W-Boson Hadronic pT "+currentCutString,50,0,100)
		self.W_Hadronic_E = Histogram(outputFileObject, "HWHE"+currentCutString,"W-Boson Hadronic Energy "+currentCutString,50,50,300)
		self.W_Leptonic_Pt = Histogram(outputFileObject, "HWLpT"+currentCutString,"W-Boson Leptonic pT "+currentCutString,50,0,100)
		self.W_Leptonic_E = Histogram(outputFileObject, "HWLE"+currentCutString,"W-Boson Leptonic Energy "+currentCutString,50,0,300)
		self.W_Leptonic_phi = Histogram(outputFileObject, "HWLphi"+currentCutString,"W-Boson Leptonic phi "+currentCutString,50,-pi,pi)
		self.W_Leptonic_theta = Histogram(outputFileObject, "HWLtheta"+currentCutString,"W-Boson Leptonic theta "+currentCutString,50,0,pi)
		
		self.W_Leptonic_e_Pt = Histogram(outputFileObject, "HWLepT"+currentCutString,"W-Boson -> Electron pT "+currentCutString,50,0,100)
		self.W_Leptonic_e_E = Histogram(outputFileObject, "HWLeE"+currentCutString,"W-Boson -> Electron Energy "+currentCutString,50,50,300)
		self.W_Leptonic_e_phi = Histogram(outputFileObject, "HWLephi"+currentCutString,"W-Boson -> Electron phi "+currentCutString,50,-pi,pi)
		self.W_Leptonic_e_theta = Histogram(outputFileObject, "HWLetheta"+currentCutString,"W-Boson -> Electron theta "+currentCutString,50,0,pi)
		self.W_Leptonic_nue_Pt = Histogram(outputFileObject, "HWLnuepT"+currentCutString,"W-Boson -> nu_e pT "+currentCutString,50,0,100)
		self.W_Leptonic_nue_E = Histogram(outputFileObject, "HWLnueE"+currentCutString,"W-Boson -> nu_e Energy "+currentCutString,50,0,300)
		self.W_Leptonic_nue_phi = Histogram(outputFileObject, "HWLnuephi"+currentCutString,"W-Boson -> nu_e phi "+currentCutString,50,-pi,pi)
		self.W_Leptonic_nue_theta = Histogram(outputFileObject, "HWLnuetheta"+currentCutString,"W-Boson -> nu_e theta "+currentCutString,50,0,pi)
		
		self.W_Leptonic_mu_Pt = Histogram(outputFileObject, "HWLmupT"+currentCutString,"W-Boson -> Muon pT "+currentCutString,50,0,100)
		self.W_Leptonic_mu_E = Histogram(outputFileObject, "HWLmuE"+currentCutString,"W-Boson -> Muon Energy "+currentCutString,50,0,300)
		self.W_Leptonic_mu_phi = Histogram(outputFileObject, "HWLmuphi"+currentCutString,"W-Boson -> Muon phi "+currentCutString,50,-pi,pi)
		self.W_Leptonic_mu_theta = Histogram(outputFileObject, "HWLmutheta"+currentCutString,"W-Boson -> Muon theta "+currentCutString,50,0,pi)
		self.W_Leptonic_numu_Pt = Histogram(outputFileObject, "HWLnumupT"+currentCutString,"W-Boson -> nu_mu pT "+currentCutString,50,0,100)
		self.W_Leptonic_numu_E = Histogram(outputFileObject, "HWLnumuE"+currentCutString,"W-Boson -> nu_mu Energy "+currentCutString,50,0,300)
		self.W_Leptonic_numu_phi = Histogram(outputFileObject, "HWLnumuphi"+currentCutString,"W-Boson -> nu_mu phi "+currentCutString,50,-pi,pi)
		self.W_Leptonic_numu_theta = Histogram(outputFileObject, "HWLnumutheta"+currentCutString,"W-Boson -> nu_mu theta "+currentCutString,50,0,pi)
		
		self.W_Leptonic_t_Pt = Histogram(outputFileObject, "HWLtpT"+currentCutString,"W-Boson -> Tauon pT "+currentCutString,50,0,100)
		self.W_Leptonic_t_E = Histogram(outputFileObject, "HWLtE"+currentCutString,"W-Boson -> Tauon Energy "+currentCutString,50,0,300)
		self.W_Leptonic_t_phi = Histogram(outputFileObject, "HWLtphi"+currentCutString,"W-Boson -> Tauon phi "+currentCutString,50,-pi,pi)
		self.W_Leptonic_t_theta = Histogram(outputFileObject, "HWLttheta"+currentCutString,"W-Boson -> Tauon theta "+currentCutString,50,0,pi)
		self.W_Leptonic_nut_Pt = Histogram(outputFileObject, "HWLnutpT"+currentCutString,"W-Boson -> nu_t pT "+currentCutString,50,0,300)
		self.W_Leptonic_nut_E = Histogram(outputFileObject, "HWLnutE"+currentCutString,"W-Boson -> nu_t Energy "+currentCutString,50,0,100)
		self.W_Leptonic_nut_phi = Histogram(outputFileObject, "HWLnutphi"+currentCutString,"W-Boson -> nu_t phi "+currentCutString,50,-pi,pi)
		self.W_Leptonic_nut_theta = Histogram(outputFileObject, "HWLnuttheta"+currentCutString,"W-Boson -> nu_t theta "+currentCutString,50,0,pi)
		
		self.W_Leptonic_WDecay_ChargedLepton_DeltaPhi = Histogram(outputFileObject, "HWLW_CL_deltaPhi"+currentCutString,"W_Leptonic_WDecay_ChargedLepton_DeltaPhi "+currentCutString,25,-pi,pi)
		self.W_Leptonic_WDecay_NeutralLepton_DeltaPhi = Histogram(outputFileObject, "HWLW_NL_deltaPhi"+currentCutString,"W_Leptonic_WDecay_NeutralLepton_DeltaPhi "+currentCutString,25,-pi,pi)
		
		self.W_n_Leptonic = Histogram (outputFileObject, "HnWLeptonic"+currentCutString, "Number of Leptonic W-Decays "+currentCutString, 6, -0.5, 5.5)
		self.W_n_Hadronic = Histogram (outputFileObject, "HnWHadronic"+currentCutString, "Number of Hadronic W-Decays "+currentCutString, 6, -0.5, 5.5)	
			
		self.W_M = Histogram(outputFileObject, "HWM"+currentCutString,"W-Boson mass "+currentCutString,50,50,100)
		self.B_M = Histogram(outputFileObject, "HBM"+currentCutString,"B-Quark mass "+currentCutString,50,0,10)
		self.H_M = Histogram(outputFileObject, "HHM"+currentCutString,"Higgs mass "+currentCutString,50,80,140)
		self.T_M = Histogram(outputFileObject, "HTM"+currentCutString,"Top mass "+currentCutString,50,150,200)

		self.phi = Histogram(outputFileObject, "Hphi"+currentCutString,"Gen-Jet Phi "+currentCutString,50,-pi,pi)
		self.theta = Histogram(outputFileObject, "Htheta"+currentCutString,"Gen-Jet Theta "+currentCutString,50,0,pi)
		self.energy = Histogram(outputFileObject, "Henergy"+currentCutString,"Gen-Jet Energy "+currentCutString,50,50,600)
		self.firstjetpt = Histogram(outputFileObject, "HfirstJetpt"+currentCutString,"Pt of hardest Gen-Jet "+currentCutString, 50,40,300)
		self.firstjeteta = Histogram(outputFileObject, "H1sJeteta"+currentCutString,"Eta of hardest Gen-Jet "+currentCutString,50,-5,5)
		self.secondjetpt = Histogram(outputFileObject, "HsecondJetpt"+currentCutString,"Pt of 2nd hardest Gen-Jet "+currentCutString, 50,40,300)
		self.isrjetenergy = Histogram(outputFileObject, "Hisrjetenergy"+currentCutString, "Energy of ISR-Jets "+currentCutString,50,0,300)
		self.isrjetpt = Histogram(outputFileObject, "Hisrjetpt"+currentCutString, "Pt of ISR-Jets "+currentCutString,50,0,100)
		self.MEREjetenergy = Histogram(outputFileObject, "HMEREjetenergy"+currentCutString, "Energy of ME add jets"+currentCutString,50,0,2000)
		self.MEREjetpt = Histogram(outputFileObject, "HMEREjetpt"+currentCutString, "Pt of ME add jets "+currentCutString,50,0,500)
		self.fsrjetenergyPS = Histogram(outputFileObject, "HfsrjetenergyPS"+currentCutString, "Energy of FSR-Jets (PS) "+currentCutString,50,0,300)
		self.fsrjetptPS = Histogram(outputFileObject, "HfsrjetptPS"+currentCutString, "Pt of FSR-Jets (PS) "+currentCutString,50,0,100)
		self.nIsrJets = Histogram(outputFileObject, "HnIsrJets"+currentCutString,"Number of ISR Jets per Event "+currentCutString, 12, -0.5, 11.5)
		self.nMEREJets = Histogram(outputFileObject, "HnMEREJets"+currentCutString,"Number of ME add jets "+currentCutString, 5, -0.5, 4.5)
		self.nFsrJetsPS = Histogram(outputFileObject, "HnFsrJetsPS"+currentCutString,"Number of FSR Jets per Event (PS) "+currentCutString, 5, -0.5, 4.5)
		
		#self.uEventPt = Histogram(outputFileObject, "HueventPt"+currentCutString, "pT of underlying Event "+currentCutString,100,0,300)
		#self.uEventE = Histogram(outputFileObject, "HueventE"+currentCutString, "Energy of underlying Event "+currentCutString,100,0,300)
		
		self.particlePt = Histogram(outputFileObject, "HparticlePt"+currentCutString, "pT of particles "+currentCutString,1000,0,100)
		self.particleE = Histogram(outputFileObject, "HparticleE"+currentCutString, "Energy of particles "+currentCutString,1000,0,300)
			
	## called to finalize all histograms and thus write them to the extracted-root file
	def finalize (self):
		self.njets.finalize()
		self.pt.finalize()
		
		self.W_Pt.finalize()
		self.W_E.finalize()
		self.B_Pt.finalize()
		self.B_E.finalize()
		self.T_Pt.finalize()
		self.T_E.finalize()
		self.H_Pt.finalize()
		self.H_E.finalize()
		self.W_deltaPhi.finalize()
		self.B_deltaPhi.finalize()
		self.H_deltaPhi.finalize()
		self.T_deltaPhi.finalize()

		self.W_Hadronic_Pt.finalize()
		self.W_Hadronic_E.finalize()
		self.W_Leptonic_Pt.finalize()
		self.W_Leptonic_E.finalize()
		self.W_Leptonic_theta.finalize()
		self.W_Leptonic_phi.finalize()

		self.W_Leptonic_e_Pt.finalize()
		self.W_Leptonic_e_E.finalize()
		self.W_Leptonic_e_theta.finalize()
		self.W_Leptonic_e_phi.finalize()
		self.W_Leptonic_nue_Pt.finalize()
		self.W_Leptonic_nue_E.finalize()
		self.W_Leptonic_nue_theta.finalize()
		self.W_Leptonic_nue_phi.finalize()
		self.W_Leptonic_mu_Pt.finalize()
		self.W_Leptonic_mu_E.finalize()
		self.W_Leptonic_mu_theta.finalize()
		self.W_Leptonic_mu_phi.finalize()
		self.W_Leptonic_numu_Pt.finalize()
		self.W_Leptonic_numu_E.finalize()
		self.W_Leptonic_numu_theta.finalize()
		self.W_Leptonic_numu_phi.finalize()
		self.W_Leptonic_t_Pt.finalize()
		self.W_Leptonic_t_E.finalize()
		self.W_Leptonic_t_theta.finalize()
		self.W_Leptonic_t_phi.finalize()
		self.W_Leptonic_nut_Pt.finalize()
		self.W_Leptonic_nut_E.finalize()
		self.W_Leptonic_nut_theta.finalize()
		self.W_Leptonic_nut_phi.finalize()
		
		self.W_Leptonic_WDecay_ChargedLepton_DeltaPhi.finalize()
		self.W_Leptonic_WDecay_NeutralLepton_DeltaPhi.finalize()
		
		self.W_n_Leptonic.finalize()
		self.W_n_Hadronic.finalize()

		self.W_M.finalize()
		self.B_M.finalize()
		self.H_M.finalize()
		self.T_M.finalize()
		
		self.phi.finalize()
		self.theta.finalize()
		self.energy.finalize()
		self.firstjetpt.finalize()
		self.secondjetpt.finalize()
		self.firstjeteta.finalize()
		
		self.isrjetenergy.finalize()
		self.isrjetpt.finalize()
		self.MEREjetenergy.finalize()
		self.MEREjetpt.finalize()
		self.fsrjetenergyPS.finalize()
		self.fsrjetptPS.finalize()
		self.nIsrJets.finalize()
		self.nMEREJets.finalize()
		self.nFsrJetsPS.finalize()
		
		#self.uEventPt.finalize()
		#self.uEventPt.finalize()
		
		self.particlePt.finalize()
		self.particleE.finalize()

		
