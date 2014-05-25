#include "fastjet/ClusterSequence.hh"
#include "
#include <iostream>
using namespace fastjet;
using namespace std;

void fastjet_antikt_cluster.C() {

  vector<PseudoJet> particles; //vector with particles
  //Step 1: Read out the px,py,pz and E of the particles and write them in some kind of vector and cluster them
  //Option 1: Find a way to read out the RootTree that is there after ExRootSTDHEPConverter
  //Option 2: Use the Treerunner from ExRootAnalysis like it is used in the MadgraphKtJet of ExRootAnalysis

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
}
