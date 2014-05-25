#include <iostream>
#include <sstream>

#include <stdlib.h>

#include "stdhep_mcfio.h"
#include "stdhep_declarations.h"

#include "TROOT.h"
#include "TApplication.h"

#include "TFile.h"
#include "TChain.h"
#include "TString.h"

#include "TH2.h"
#include "THStack.h"
#include "TLegend.h"
#include "TPaveText.h"
#include "TLorentzVector.h"

#include "LHEF.h"

#include "ExRootAnalysis/ExRootClasses.h"

#include "ExRootAnalysis/ExRootTreeWriter.h"
#include "ExRootAnalysis/ExRootTreeBranch.h"

#include "ExRootAnalysis/ExRootUtilities.h"
#include "ExRootAnalysis/ExRootProgressBar.h"

using namespace std;


//---------------------------------------------------------------------------

static void AnalyseEvent(ExRootTreeBranch *branch, Long64_t eventNumber)
{
  TRootLHEFEvent *element;

  element = static_cast<TRootLHEFEvent*>(branch->NewEntry());

  element->Number = eventNumber;
  
  element->ProcessID = 0;
  element->Nparticles = myhepevt.nhep;
  element->Weight = hepev4_.eventweightlh;
  element->ScalePDF = hepev4_.scalelh[0];
  element->CouplingQED = hepev4_.alphaqedlh;
  element->CouplingQCD = hepev4_.alphaqcdlh;
}

//---------------------------------------------------------------------------

static void AnalyseParticles(ExRootTreeBranch *branch)
{
  TRootGenParticle *element;

  Double_t signPz, cosTheta;
  TLorentzVector momentum;
  Int_t number;

  for(number = 0; number < myhepevt.nhep; ++number)
  {

    element = static_cast<TRootGenParticle*>(branch->NewEntry());

    element->PID = myhepevt.idhep[number];
    element->Status = myhepevt.isthep[number];
    element->M1 = myhepevt.jmohep[number][0] - 1;
    element->M2 = myhepevt.jmohep[number][1] - 1;
    element->D1 = myhepevt.jdahep[number][0] - 1;
    element->D2 = myhepevt.jdahep[number][1] - 1;

    element->E = myhepevt.phep[number][3];
    element->Px = myhepevt.phep[number][0];
    element->Py = myhepevt.phep[number][1];
    element->Pz = myhepevt.phep[number][2];

    momentum.SetPxPyPzE(element->Px, element->Py, element->Pz, element->E);
    
    cosTheta = TMath::Abs(momentum.CosTheta());
    signPz = (momentum.Pz() >= 0.0) ? 1.0 : -1.0;

    element->PT = momentum.Perp();
    element->Phi = momentum.Phi();
    element->Eta = (cosTheta == 1.0 ? signPz*999.9 : momentum.Eta());
    element->Rapidity = (cosTheta == 1.0 ? signPz*999.9 : momentum.Rapidity());


    element->T = myhepevt.vhep[number][3];
    element->X = myhepevt.vhep[number][0];
    element->Y = myhepevt.vhep[number][1];
    element->Z = myhepevt.vhep[number][2];
    
   
  }
}

//---------------------------------------------------------------------------

string convertInt(int number)
{
   stringstream s;// string Stream erzeugen
   s<< number;// Zahl hinzufügen
   return s.str();// string zurückgeben
}

int main(int argc, char *argv[])
{
  int ierr, entryType;
  int istr = 0;
  int nevt = 0;
  char appName[] = "ExRootSTDHEPConverter";

  if(argc != 3)
  {
    cout << " Usage: " << appName << " input_file" << " output_file" << endl;
    cout << " input_file - input file in STDHEP format," << endl;
    cout << " output_file - output file in ROOT format." << endl;
    return 1;
  }

  gROOT->SetBatch();

  int appargc = 1;
  char *appargv[] = {appName};
  TApplication app(appName, &appargc, appargv);

  // Open a stream connected to an event file:
  char inputFileName[80];
  strcpy(inputFileName, argv[1]);
  ierr = StdHepXdrReadInit(inputFileName, &nevt, istr);

  if(ierr != 0)
  {
    cerr << "** ERROR: Can't open '" << argv[1] << "' for input" << endl;
    return 1;
  }
  Long64_t allEntries = nevt;
  cout << "** Input file contains " << allEntries << " entries" << endl;

  TFile *outputFile = TFile::Open(argv[2], "RECREATE");
  ExRootTreeWriter *treeWriter = new ExRootTreeWriter(outputFile, "STDHEP");

  // information about generated event
  ExRootTreeBranch *branchGenEvent = treeWriter->NewBranch("Event", TRootLHEFEvent::Class());
  // generated particles from HEPEVT
  //ExRootTreeBranch *branchGenParticle = treeWriter->NewBranch("GenParticle", TRootGenParticle::Class());

  if(allEntries > 0)
  {
    ExRootProgressBar progressBar(allEntries);

    // Loop over all objects
    Long64_t entry = 0;
    Long64_t recordNumber = 1;
    int branchnumber = 0;
    for(entry = 0; entry < allEntries; ++entry)
    {
      string branchname = "GenParticle"+"_event_"+convertInt(branchnumber);
      branchnumber = branchnumber + 1;
      ExRootTreeBranch *branchGenParticle = treeWriter->NewBranch(branchname, TRootGenParticle::Class());
      
      ierr = StdHepXdrRead(&entryType, istr);

      if(ierr != 0)
      {
        cerr << "** ERROR: Unexpected end of file after " << entry << " entries" << endl;
        break;
      }

      // analyse only entries with standard HEPEVT common block
      if(entryType == 1 || entryType == 4)
      {
        // add empty events for missing event numbers
        while(recordNumber < myhepevt.nevhep)
        {
          treeWriter->Clear();
          AnalyseEvent(branchGenEvent, recordNumber);
          treeWriter->Fill();
          ++recordNumber;
        }

        treeWriter->Clear();
 
        AnalyseEvent(branchGenEvent, myhepevt.nevhep);
        AnalyseParticles(branchGenParticle);
        treeWriter->Fill();

        ++recordNumber;
    
      }

      progressBar.Update(entry);
    }
    

    progressBar.Finish();
  }

  treeWriter->Write();

  cout << "** Exiting..." << endl;

  delete treeWriter;
  StdHepXdrEnd(istr);
}

