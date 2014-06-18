#include <vector>
#include <iomanip>
#include <string>

/***********************************
compares plots of same name in different root files and stores result in pdf
************************************/

void compareplots_noRatio(){
  vector<TFile*> files; 
  files.push_back(new TFile("/storage/9/schweiger/analyseFxFx/pythia8/100kEvents/ttbarMergedFxFx8TeVCTEQ6M-extracted.root"));
  files.push_back(new TFile("/storage/9/schweiger/analyseFxFx/pythia8/100kEvents/mergingscale_30/ttbarMergedFxFxMS30GeVMECut10GeV8TeVCTEQ6M-extracted.root"));   
  files.push_back(new TFile("/storage/9/schweiger/analyseFxFx/pythia8/100kEvents/mergingscale_100/ttbarMergedMS100GeV8TeVCTEQ6M-extracted.root"));   
  files.push_back(new TFile("/storage/9/schweiger/analyseFxFx/pythia8/100kEvents/mergingscale_100/ttbarMergedMS100GeVMCCut50GeV8TeVCTEQ6M-extracted.root"));   
  


  
  vector<TString> names;
  names.push_back("ttbar +0/1 Jet, #mu_{Q}=10 GeV #mu_{ME} = 10 GeV");
  names.push_back("ttbar +0/1 Jet, #mu_{Q}=30 GeV #mu_{ME} = 10 GeV");
  names.push_back("ttbar +0/1 Jet, #mu_{Q}=100 GeV #mu_{ME} = 10 GeV");
  names.push_back("ttbar +0/1 Jet, #mu_{Q}=100 GeV #mu_{ME} = 50 GeV");
  
  
  vector<TString> titles;
 titles.push_back("Gen-Jet p_{T}  with pos weights (GeV)");
  titles.push_back("Gen-Jet p_{T} with neg weights (GeV)");
  titles.push_back("Gen-Jet p_{T} (GeV)");
  titles.push_back("Gen_Jet #phi with pos. weights");
  titles.push_back("Gen_Jet #phi with neg. weights");
  titles.push_back("Gen_Jet #phi");
  titles.push_back("Gen Jet #theta with pos weights");
  titles.push_back("Gen Jet #theta with neg weights");
  titles.push_back("Gen Jet #theta");
  titles.push_back("Gen Jet Energy with pos weights (GeV) ");
  titles.push_back("Gen Jet Energy with neg weights (GeV)");
  titles.push_back("Gen Jet Energy (GeV)");
  titles.push_back("p_{T} of hardest Gen-Jet with pos weights (GeV)");
  titles.push_back("p_{T} of hardest Gen-Jet with neg weights (GeV)");
  titles.push_back("p_{T} of hardest Gen-Jet (GeV)");
  titles.push_back("p_{T} of 2nd hardest Gen-Jet with pos weights (GeV)");
  titles.push_back("p_{T} of 2nd hardest Gen-Jet with neg weights (GeV)");
  titles.push_back("p_{T} of 2nd hardest Gen-Jet (GeV)");
  titles.push_back("#eta of hardest Gen-Jets with pos weights");
  titles.push_back("#eta of hardest Gen-Jets with neg weights");
  titles.push_back("#eta of hardest Gen-Jets");
  titles.push_back("Number of Gen-Jets with pos. weights");
  titles.push_back("Number of Gen-Jets with neg. weights");
  titles.push_back("Number of Gen-Jets");

  TFile *vergleich = new TFile("vergleich_ttbar_0Jet.root","RECREATE");

// Show no statistics box
gStyle->SetOptStat(0);

TH1::SetDefaultSumw2();

// Main program part
  TIter nextkey(files.at(0)->GetListOfKeys());
  TKey *key;
  bool first=true;
  TCanvas* c = new TCanvas();
  c->Print("plots.pdf[");

  // Save also as pictures
  int pictureNumber = 0;

  int run = 0;
  while (key = (TKey*)nextkey()) {
    pictureNumber++;
    TString pictureName = TString::Format("%d.png",pictureNumber);


    vector<TH1F*> histos;
    histos.push_back((TH1F*)key->ReadObj());
    for(size_t i=1;i<files.size();i++){
      histos.push_back((TH1F*)files.at(i)->Get(histos.at(0)->GetName()));
    }
		       
    for(size_t i=0;i<histos.size();i++){
      if(i == 0){
	histos.at(i)->SetLineColor(kBlack);
      }
      if(i == 1){
	histos.at(i)->SetLineColor(kRed);
      }
      if(i == 2){
	histos.at(i)->SetLineColor(kBlue);
      }
      if(i == 3){
	histos.at(i)->SetLineColor(kGreen+2);
      }
    }
   
    for(size_t i=0;i<histos.size();i++){
      histos.at(i)->Sumw2();
      histos.at(i)->Scale(1./histos.at(i)->Integral(),"width");
    }

// Set axis title
histos.at(0)->GetYaxis()->SetTitle("Normalized units"); 
std::string const histogramName = histos.at(1)->GetName();
histos.at(0)->GetXaxis()->SetLabelSize(0.05);
histos.at(0)->GetXaxis()->SetLabelOffset(0.006);
histos.at(0)->GetYaxis()->SetLabelSize(0.05);
histos.at(0)->GetYaxis()->SetLabelOffset(0.006);
histos.at(0)->GetXaxis()->SetTitleSize(0.06);
histos.at(0)->GetXaxis()->SetTitleOffset(1.1);
histos.at(0)->GetYaxis()->SetTitleSize(0.06);
histos.at(0)->GetYaxis()->SetTitleOffset(1.15);
	

 histos.at(0)->GetXaxis()->SetTitle(titles.at(run));
 run = run+1;

// If only two histograms per plot make a ratio plot
if(histos.size() == 2)
{

//create main pad  
                                                                                                                                                          
           TPad *mainPad = new TPad("","",0.0,0.0,1.0,1.0);
           mainPad->SetNumber(1);
           mainPad->SetBottomMargin(0.15);
           mainPad->SetRightMargin(0.04);
	   mainPad->SetLeftMargin(0.13);
           mainPad->Draw();
	   gStyle->SetOptTitle(0);
           //create ratio pad                                                                                                                                                           
           /*TPad *ratioPad = new TPad("","",0.0,0.0,1.0,0.3);
           ratioPad->SetTopMargin(0.0);
           ratioPad->SetBottomMargin(0.4);
           ratioPad->SetLeftMargin(0.13);                                                                                                                                             
           ratioPad->SetRightMargin(0.04);
           gStyle->SetOptTitle(0);
           ratioPad->SetFillColor(0);
           ratioPad->SetNumber(2);
           ratioPad->SetGridy();                                                                                                                                                      
           ratioPad->Draw();*/

// Draw both histograms first
c->cd(1);

histos.at(0)->Draw("histo E");
histos.at(1)->Draw("histo same E");

// Show legend and statistical tests in first pad
    for(size_t i=0;i<histos.size()-1;i=i+2){

      double ksresult = histos.at(i)->KolmogorovTest(histos.at(i+1));
      ksresult=floor(ksresult*1000+0.5)/1000;
      double chi2result =histos.at(i)->Chi2Test(histos.at(i+1),"WW");
      chi2result=floor(chi2result*1000+0.5)/1000;

      stringstream ss;
      //ss << "     KS: " <<std::setprecision(3) << ksresult << " chi2: " <<std::setprecision(3) << chi2result << " Private Work"; 
      ss << "            Private Work";
      const char * ch = & ss.str().c_str();;
      TLatex * ks = new TLatex(0.1, 0.9-0.03*i, ch );
      ks->SetTextColor(histos.at(i)->GetLineColor());
      ks->SetNDC();
      ks->Draw("");      

    }

    TLegend* l = new TLegend(0.40,0.9,0.69,0.99);
    // Options for legend
    l->SetBorderSize(0);
    l->SetLineStyle(0);
    l->SetTextSize(0.049);
    l->SetFillStyle(0);
    for(size_t i=0;i<names.size();i++){
      l->AddEntry(histos.at(i),names.at(i),"L");
    }
    l->Draw("same");

/*
// Clone histograms and draw ratio plot
c->cd(2);
 TH1F* ratioHisto = (TH1F*)histos.at(0)->Clone();
ratioHisto->Divide(histos.at(1));
ratioHisto->SetLineColor(kBlue);
ratioHisto->SetStats(false);
ratioHisto->GetYaxis()->SetTitle("Ratio #frac{noFxFx}{FxFx}");
// Same Size like in histogram
ratioHisto->SetLabelSize(histos.at(0)->GetLabelSize() * 0.7 / 0.3);
ratioHisto->SetTitleOffset((histos.at(0)->GetTitleOffset("Y") * 0.3 / 0.7), "Y");
ratioHisto->SetTitleSize((histos.at(0)->GetTitleSize("Y") * 0.7 / 0.3), "Y");
ratioHisto->SetTitleOffset((histos.at(0)->GetTitleOffset("X")), "X");
ratioHisto->SetTitleSize((histos.at(0)->GetTitleSize("X") * 0.7 / 0.3), "X");
// Use nicer range
ratioHisto->GetYaxis()->SetRangeUser(0, 2.2);
ratioHisto->GetYaxis()->SetNdivisions(503);
ratioHisto->GetYaxis()->SetLabelSize(0.06 * 0.7 / 0.3);
ratioHisto->Draw();*/
}
else
{
        TPad *mainPad = new TPad("","",0.0,0.0,1.0,1.0);
        mainPad->SetNumber(1);
        mainPad->SetBottomMargin(0.15);
        mainPad->SetRightMargin(0.04);
        mainPad->SetLeftMargin(0.13);
        mainPad->Draw();
        gStyle->SetOptTitle(0);
        //mainPad->SetLogx(1);
	c->cd(1);

    histos.at(0)->Draw("histo E");
    for(size_t i=0;i<histos.size();i++){
      histos.at(i)->Draw("histo same E");
    }


    for(size_t i=0;i<histos.size()-1;i=i+2){
      /*
      double ksresult = histos.at(i)->KolmogorovTest(histos.at(i+1));
      ksresult=floor(ksresult*1000+0.5)/1000;
      double chi2result =histos.at(i)->Chi2Test(histos.at(i+1),"WW");
      chi2result=floor(chi2result*1000+0.5)/1000;

      stringstream ss;
      ss << "KS: " <<std::setprecision(3) << ksresult << " chi2: " <<std::setprecision(3) << chi2result; 
      const char * ch = & ss.str().c_str();;
      TText * ks = new TText(0.1, 0.9-0.03*i, ch );
      ks->SetTextColor(histos.at(i)->GetLineColor());
      ks->SetNDC();
      ks->Draw("");      
      */
    }

    TLegend* l = new TLegend(0.65,0.5,0.9,0.7);
    l->SetBorderSize(0);
    l->SetLineStyle(0);
    //    l->SetTextSize(0.039);
    l->SetFillStyle(0);
    for(size_t i=0;i<names.size();i++){
      l->AddEntry(histos.at(i),names.at(i),"L");
    }
    l->Draw("same");
}

    c->Print("plots.pdf");
    c->SaveAs(pictureName);
    vergleich->WriteTObject(c);

}
  c->Print("plots.pdf]");


}
