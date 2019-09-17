DtaRefinery
Version: 1.2

== Changes in ver 1.2 (2010.02.16) ==
1) Fixed problem in parsing dta file when MH value of parent
ion was an number without decimal positions.
2) Display and print out version number in the log file
3) Switch to simple shift from additive regression only
if additive regression was selected as the method of choice.
4) (2010.04.26) Flush the buffer after each log into the log file.
This updates the programs running status more frequently.

== Changes in ver 1.1 (2010.01.11) ==
1) Fixed ValueError problem with very large dataset refinement
2) Added option for analysis of non-trytic digests
3) Added widget for showing the refinement method
4) Fixed the "bypass refinement" method
5) Allowed 1 missed clevage event in case the cleavage specificity.
In the case of no enzyme rule digest, the number of missed cleavages
goes up to 50.
6) The default settings now includes static alkylation of cystein and 
trypsin cleavage specificity.




== Overview ==
The DtaRefinery is a software application that can eliminate parent ion 
systematic mass measurement errors for MS/MS data acquired on hybrid 
instrumentation capable of switching between a high accuracy MS scan acquisition 
mode and MS/MS fragmentation (for example the LTQ-FT and LTQ-Orbitrap). The 
software improves mass measurement errors for parent ions of tandem MS/MS data 
by modeling systematic errors based on putative peptide identifications.  This 
information is used to subtract out errors from parent ion protonated masses.  

== Details ==
The DtaRefinery program reads the concatenated dta files, which can be obtained 
either by concatenating individual dta files from extract_msn output or by 
running DeconMSn with the -XCDTA option. It is recomended to use DeconMSn as a 
preprocessing tool since it not only picks the right monoisotopic mass for 
parent ions, but also provides additional information that can be used for 
statistical analysis (specifically, ion intensity, total ion current, and AGC 
accumulation times).

As an output, DtaRefinery produces a concatenated dta file, but with corrected 
protonated parent ion mass values. Optionally it can output a mass error 
distribution histogram with the estimates of mean and standard deviation of 
parent ion mass measurements, along with scatterplots showing original and 
final dependencies of mass measurement errors on parameters like scan number, 
m/z, ion intensity and total ion current.  Modeling of the systematic mass 
measurement error is based on robust non-parametric regression analysis of 
dependecy of error residuals on multiple parameters, including scan number, 
m/z, ion intensity, and total ion current.


== Example Data included with the Installer ==
Included with the DTARefinery is a test dataset based on a typical mouse brain 
LC-MS/MS dataset obtained on an LTQ-Obritrap intrument. The ".raw" file was 
processed with DeconMSn.  The following example files (installed at C:\Program 
Files\DtaRefinery\examples) are included for you to explore the DtaRefinery's 
functionality:
1) test_dta.txt
	A concatenated dta file from DeconMSn
2) test_DeconMSn_log.txt
	The DeconMSn log file
3) test_profile.txt
	The DeconMSn profile file
4) ipiMOUSEv328.fasta
	The mouse IPI v3.28 FASTA (from 
ftp://ftp.ebi.ac.uk/pub/databases/IPI/old/HUMAN)
5) *.bat
	Command line batch files demonstrating various methods for improving mass 
	measurement error (each invokes the application from the command line)
6) *.xml
	Corresponding XML settings files for the batch files


== Using DtaRefinery ==
The program can be run either in an interactive (GUI) mode or via the command 
line.  To use the GUI, simply run the application from the start menu or by 
double clicking dta_refinery.exe.  Simple steps to get started:
1) Choose "File -> dta Files..."  to load concatenated dta files
2) Choose "File -> FASTA File..." to load FASTA file
3) The settings can be loaded with "File -> Load Settings File...", or by 
choosing the "Error Correction Params" and "Misc Settings" menus.
4) Click Run

== Command line Syntax ==
dta_refinery [setting file (xml)] [concatenated dta file (_dta.txt)] [FASTA file]


== DtaRefinery Output files ==

* _dta_DtaRefineryLog.txt 
	* the processing log file
* _dta_SETTINGS.xml
	* the settings that were used to refine a particular dataset
* _FIXED_dta.txt
	* the concatenated dta file with corrected parent ion masses
* _HIST.png
	* mass measurement error histograms before and after procedure
* _HIST.txt
	* histogram data as in *_HIST.png file, but in text format

Scatterplots showing mass measurement error residuals dependencies on:
 * scan number: _scanNum.png
 * m/z: _mz.png
 * log10 of ion intensity in the ICR/Orbitrap cell: _logTrappedIonInt.png
 * total ion current in the ICR/Orbitrap cell: _trappedIonsTIC.png

-------------------------------------------------------------------------------
Written by Vlad Petyuk
for the Department of Energy (PNNL, Richland, WA)
Copyright 2008, Battelle Memorial Institute.  All Rights Reserved.

E-mail: vladislav.petyuk@pnl.gov
General proteomics contact e-mail: proteomics@pnl.gov
Website: http://ncrr.pnl.gov/ or http://omics.pnl.gov/
-------------------------------------------------------------------------------

All publications that result from the use of this software should include 
the following acknowledgment statement:
 Portions of this research were supported by the W.R. Wiley Environmental 
 Molecular Science Laboratory, a national scientific user facility sponsored 
 by the U.S. Department of Energy's Office of Biological and Environmental 
 Research and located at PNNL.  PNNL is operated by Battelle Memorial Institute 
 for the U.S. Department of Energy under contract DE-AC05-76RL0 1830.

Notice: This computer software was prepared by Battelle Memorial Institute, 
hereinafter the Contractor, under Contract No. DE-AC05-76RL0 1830 with the 
Department of Energy (DOE).  All rights in the computer software are reserved 
by DOE on behalf of the United States Government and the Contractor as 
provided in the Contract.  NEITHER THE GOVERNMENT NOR THE CONTRACTOR MAKES ANY 
WARRANTY, EXPRESS OR IMPLIED, OR ASSUMES ANY LIABILITY FOR THE USE OF THIS 
SOFTWARE.  This notice including this sentence must appear on any copies of 
this computer software.
