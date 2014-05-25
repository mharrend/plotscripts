#include "TROOT.h"
#include "TH1F.h"
#include "TFile.h"
#include "TObject.h"

#include "fastjet/ClusterSequence.hh"

#include "ExRootAnalysis/ExRootClasses.h"

#include <iostream>
using namespace fastjet;
using namespace std;

void fastjet_antikt_clusternan() {
  //I'm not shure how the count the Number of Jets. I have to look up, if the the particles are somehow store by Events.

  //Input File
  vector<TFile*> files; 
  files.push_back(new TFile("/path/to/converted/Herwig6/Eventfile.root"));
  TFile *outputfile = new TFile("output.root","RECREATE");


  vector<PseudoJet> particles; //vector with particles
  //Step 1: Read out the px,py,pz and E of the particles and write them in some kind of vector and cluster them
  //Option 1: Find a way to read out the RootTree that is there after ExRootSTDHEPConverter
  //Option 2: Use the Treerunner from ExRootAnalysis like it is used in the MadgraphKtJet of ExRootAnalysis
  //Cut on particles
  double MaxParticleEta = 2.5;
  double MinparticlePt = 0.5;

  //Option 1:
  toS
  /*
  //Option 2:
  //Reused Code from ExRootAnalysis/modules/MadGraphKtJetFinder.cc
  fBranchParticle = UseBranch("GenParticle");
  fItParticle = fBranchParticle->MakeIterator();
  
  TRootGenParticle *particle;

  while((particle = (TRootGenParticle*) fItParticle->Next()))
  {
 	  if((particle->Status == 1) &&
	     (TMath::Abs(particle->PID) != 12) &&
	     (TMath::Abs(particle->PID) != 14) &&
	     (TMath::Abs(particle->PID) != 16) &&
	     (TMath::Abs(particle->Eta) < MaxParticleEta) && 
	     (particle->PT > MinParticlePt))
	  {
	    //Write variables of particles in a Vector. Maybe phi etc. should also be wrote in the vector
	    particles.push_back( PseudoJet(particle->PX, particle->PY, particle->PZ, particle->E));
	  }
	  }*/
  //JetAlgorithm definition: Anti-kt with 0.5 Cone Radius
  double R = 0.5;
  JetDefinition jet_def(antikt_algorithm, R);

  //Run Clustersequenz and write Jets in ne vector
  ClusterSequence cs(particles, jet_def);
  vector<PseudoJet> jets = sorted_by_pt(cs.inclusive_jets());

  //Step 2: 
  //a) Declare TH1F Histogramms for Number of Jets, Jet-pt, Jet-Energy, Jet-Phi and Jet-Theta
  //b) Loop through all Jets and fill the Histrogramms
  //c) save the Histogramms in a Root file
  TH1F∗ Hpt=new TH1F ("Hpt","Jet Pt" ,50,0,300);
  TH1F∗ Henergy=new TH1F ("Henergy","Jet Energy" ,100,0,600);
  //TH1F∗ HnJets=new TH1F ("HnJets","Nubmber of Jets" ,100,0,600);
   
  for(int i=0; i < jets.size(); i++){
    Hpt->Fill(jets[i].perp());
    Henergy->Fill(jets[i].E());
  }
  
  outputfile->WriteTObject(Hpt);
  outputfile->WriteTObject(Henergy);
  
}

# ifndef __CINT__
int main ( ) {
  fastjet_antikt_cluster.C();
  return 0;
}
# endif
