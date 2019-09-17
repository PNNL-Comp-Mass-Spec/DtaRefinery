# DtaRefinery

The DtaRefinery is a software application that can eliminate parent ion 
systematic mass measurement errors for MS/MS data acquired on hybrid 
instrumentation capable of switching between a high accuracy MS scan acquisition 
mode and MS/MS fragmentation (for example the LTQ-FT and LTQ-Orbitrap). The 
software improves mass measurement errors for parent ions of tandem MS/MS data 
by modeling systematic errors based on putative peptide identifications. This 
information is used to subtract out errors from parent ion protonated masses.

## Details

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
m/z, ion intensity and total ion current. Modeling of the systematic mass 
measurement error is based on robust non-parametric regression analysis of 
dependecy of error residuals on multiple parameters, including scan number, 
m/z, ion intensity, and total ion current.

## Example Data included with the Installer

Included with the DTARefinery is a test dataset based on a typical mouse brain 
LC-MS/MS dataset obtained on an LTQ-Obritrap intrument. The ".raw" file was 
processed with DeconMSn. The following example files (installed at C:\Program 
Files\DtaRefinery\examples) are included for you to explore the DtaRefinery's 
functionality:

1) test_dta.txt
  * A concatenated dta file from DeconMSn
2) test_DeconMSn_log.txt
  * The DeconMSn log file
3) test_profile.txt
  * The DeconMSn profile file
4) ipiMOUSEv328.fasta
  * The mouse IPI v3.28 FASTA (from 
ftp://ftp.ebi.ac.uk/pub/databases/IPI/old/HUMAN)
5) *.bat
  * Command line batch files demonstrating various methods for improving mass measurement error (each invokes the application from the command line)
6) *.xml
  * Corresponding XML settings files for the batch files

## Using DtaRefinery

The program can be run either in an interactive (GUI) mode or via the command 
line. To use the GUI, simply run the application from the start menu or by 
double clicking dta_refinery.exe. Simple steps to get started:

1) Choose "File -> dta Files..."  to load concatenated dta files
2) Choose "File -> FASTA File..." to load FASTA file
3) The settings can be loaded with "File -> Load Settings File...", or by 
choosing the "Error Correction Params" and "Misc Settings" menus.
4) Click Run

## Command line Syntax

### Compiled Executable

dta_refinery.exe [setting file (xml)] [concatenated dta file (_dta.txt)] [FASTA file]


### Running via Python 3.x

Install the wx package:
```pip install wxPython```

Call python.exe with the dta_refinery.py followed by options
```python.exe dta_refinery.py```


## DtaRefinery Output files

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
 
## Revision History

### Changes in version 1.3 (2010.04.26)

1) Now reads the _DeconMSn_log.txt and profile.txt files created by DeconMSn


### Changes in version 1.2 (2010.02.16)

1) Fixed problem in parsing dta file when MH value of parent
ion was an number without decimal positions.
2) Display and print out version number in the log file
3) Switch to simple shift from additive regression only
if additive regression was selected as the method of choice.
4) (2010.04.26) Flush the buffer after each log into the log file.
This updates the programs running status more frequently.

### Changes in version 1.1 (2010.01.11)

1) Fixed ValueError problem with very large dataset refinement
2) Added option for analysis of non-trytic digests
3) Added widget for showing the refinement method
4) Fixed the "bypass refinement" method
5) Allowed 1 missed clevage event in case the cleavage specificity.
In the case of no enzyme rule digest, the number of missed cleavages
goes up to 50.
6) The default settings now includes static alkylation of cystein and 
trypsin cleavage specificity.

## Contacts

Written by Vlad Petyuk for the Department of Energy (PNNL, Richland, WA) \
Copyright 2008, Battelle Memorial Institute. All Rights Reserved. \
E-mail: vladislav.petyuk@pnnl.gov or proteomics@pnnl.gov \
Website: https://omics.pnl.gov/ or https://panomics.pnnl.gov/

## License

DTARefinery is licensed under the 2-Clause BSD License; you may not use 
this file except in compliance with the License. You may obtain 
a copy of the License at https://opensource.org/licenses/BSD-2-Clause
