import time
import copy
import os
import re
import xml.dom.minidom
import subprocess

from my_xtandem_res_parser import do_parse_XTandemXmlOutput
from my_conditioning_dta import do_read_dta_n_log_n_profile_files, do_read_just_dta_file
from my_conditioning_xtandem_results import do_combine_xtandemRes_n_log_n_profile_file, do_reformat_xtandemRes
from my_updating_dta_file import do_createFixedDtaFile
from my_parent_ion_mz_fixing_module import do_fix_parent_ion_mz
from my_xml_settings_handler import getSettingsFromXML, writeSettingsToXML


class Controller:
    def __init__(self, dtaRefineryDir):

        self.dtaRefineryDir = dtaRefineryDir
        self.settingsFile = os.path.join(self.dtaRefineryDir, 'default_settings.xml')
        self.getSettings()

        self.allDimensions = ['scanNum', 'mz', 'logTrappedIonInt', 'trappedIonsTIC']

        self.logFileMissing = 'True/False'  # will hold the info if the log file missing or present

        self.dtaFileList = []  # changed from gui or command line input
        self.fastaFile = None  # changed from gui or command line input

    ##        self.currDir = os.getcwd() #current directory

    def getSettings(self):
        self.defaultSettings = getSettingsFromXML(self.settingsFile)
        self.updatedSettings = copy.deepcopy(self.defaultSettings)

    def printVersion(self):
        statusString = "DtaRefinery %s" % self.version
        print(statusString)
        self.logFh.write(statusString + '\n')
        self.logFh.flush()

    def SetXtandemPaths(self):
        #
        xtandemExe = self.updatedSettings['xtandemPars']['xtandem exe file']
        xtandemDefaultInput = self.updatedSettings['xtandemPars']['default input']
        xtandemTaxonomyList = self.updatedSettings['xtandemPars']['taxonomy list']
        self.xtandemExePath = os.path.abspath(xtandemExe)
        self.xtandemDefaultInputPath = os.path.abspath(xtandemDefaultInput)
        self.xtandemTaxonomyListPath = os.path.abspath(xtandemTaxonomyList)
        #
        # check the paths
        # switch to defaults if something was wrong with paths
        xtandemPathsValid = True
        if ((not os.path.exists(self.xtandemExePath)) or
                (not os.path.exists(self.xtandemDefaultInputPath)) or
                (not os.path.exists(self.xtandemTaxonomyListPath))):
            #
            statusString = '\n' + 'Warning! Did not find one of the X!Tandem files\n'

            if os.path.exists(self.xtandemExePath):
                statusString += '  found:        ' + self.xtandemExePath + '\n'
            else:
                statusString += '  did not find: ' + self.xtandemExePath + '\n'

            if os.path.exists(self.xtandemDefaultInputPath):
                statusString += '  found:        ' + self.xtandemDefaultInputPath + '\n'
            else:
                statusString += '  did not find: ' + self.xtandemDefaultInputPath + '\n'

            if os.path.exists(self.xtandemTaxonomyListPath):
                statusString += '  found:        ' + self.xtandemTaxonomyListPath + '\n'
            else:
                statusString += '  did not find: ' + self.xtandemTaxonomyListPath + '\n'

            xtandemDir = os.path.join(self.dtaRefineryDir, 'aux_xtandem_module')

            statusString += ('\nSwitching to the default X!Tandem location at\n  %s\n' % os.path.abspath(xtandemDir))
            print(statusString)
            self.logFh.write(statusString + '\n')
            self.logFh.flush()
            #
            self.xtandemExePath = os.path.join(xtandemDir, 'tandem_5digit_precision.exe')
            self.xtandemDefaultInputPath = os.path.join(xtandemDir, 'xtandem_default_input.xml')
            self.xtandemTaxonomyListPath = os.path.join(xtandemDir, 'xtandem_taxonomy_list.xml')

            # Check if default location is fine
            if ((not os.path.exists(self.xtandemExePath)) or
                    (not os.path.exists(self.xtandemDefaultInputPath)) or
                    (not os.path.exists(self.xtandemTaxonomyListPath))):

                statusString = "Error!\n"
                statusString += "Can not find xtandem files in their default location.\n"

                if os.path.exists(self.xtandemExePath):
                    statusString += '  found:        ' + self.xtandemExePath + '\n'
                else:
                    statusString += '  did not find: ' + self.xtandemExePath + '\n'

                if os.path.exists(self.xtandemDefaultInputPath):
                    statusString += '  found:        ' + self.xtandemDefaultInputPath + '\n'
                else:
                    statusString += '  did not find: ' + self.xtandemDefaultInputPath + '\n'

                if os.path.exists(self.xtandemTaxonomyListPath):
                    statusString += '  found:        ' + self.xtandemTaxonomyListPath + '\n'
                else:
                    statusString += '  did not find: ' + self.xtandemTaxonomyListPath + '\n'

                print(statusString)
                self.logFh.write(statusString + '\n')
                self.logFh.flush()
                self.logFh.close()
                raise Exception

            else:

                self.updatedSettings['xtandemPars']['xtandem exe file'] = str(self.xtandemExePath)
                self.updatedSettings['xtandemPars']['default input'] = str(self.xtandemDefaultInputPath)
                self.updatedSettings['xtandemPars']['taxonomy list'] = str(self.xtandemTaxonomyListPath)
        #

        statusString = '\nUsing X!Tandem at:'
        statusString += '\n  ' + os.path.abspath(self.xtandemExePath)

        statusString += '\n\nInput file paths:'
        statusString += '\n  ' + os.path.abspath(self.xtandemDefaultInputPath)
        statusString += '\n  ' + os.path.abspath(self.xtandemTaxonomyListPath)

        print(statusString)
        self.logFh.write(statusString + '\n')
        self.logFh.flush()

        dtaFileDirName = os.path.dirname(self.dtaFileList[0])
        self.xtandemCurrentTaxonomyListPath = os.path.join(dtaFileDirName, '~temp_taxonomy.xml')

    def Run(self):

        ##        originalMethod = copy.deepcopy( self.updatedSettings['refiningPars']['choices']['refining method'])
        originalMethod = self.updatedSettings['refiningPars']['choices']['refining method']
        originalSelectedDims = self.updatedSettings['refiningPars']['otherParams']['dimensions']

        for dtaFile in self.dtaFileList:

            # in case the method has been changed to simpleShift put the original back.
            self.updatedSettings['refiningPars']['choices']['refining method'] = originalMethod
            # in case dimensions were updated because _log file was not avalable. Set'em back.
            self.allDimensions = ['scanNum', 'mz', 'logTrappedIonInt', 'trappedIonsTIC']
            self.updatedSettings['refiningPars']['otherParams']['dimensions'] = originalSelectedDims

            tic = time.clock()

            dtaFileNameNoExt = os.path.splitext(dtaFile)[0]

            # set the logFile
            logFileName = dtaFileNameNoExt + '_DtaRefineryLog.txt'
            if os.path.exists(logFileName):
                os.remove(logFileName)
            self.logFh = open(logFileName, 'w')

            # actually can be checked only once for all loops
            # since I have separate log files for each dta file
            # I moved it here
            self.printVersion()
            self.SetXtandemPaths()
            self.performSomeChecks()

            # setup taxonomy file
            taxDoc = xml.dom.minidom.parse(self.xtandemTaxonomyListPath)
            elementTaxon = taxDoc.getElementsByTagName("taxon")[0]  # must be only one element
            elementTaxon.setAttribute('label', 'FASTAFILE')
            elementFile = elementTaxon.getElementsByTagName('file')[0]
            elementFile.setAttribute('URL', self.fastaFile)
            taxonomyFH = open(self.xtandemCurrentTaxonomyListPath, 'w')
            taxDoc.writexml(taxonomyFH)
            taxonomyFH.close()

            #############################################################################
            # Check for existing results
            # ---The file name is: dtaFileNameNoExt +'_OUT.xml'
            xTandemResultsFile = dtaFileNameNoExt + '_OUT.xml'

            if os.path.exists(xTandemResultsFile):
                statusString = '\nUsing existing X!Tandem results\n  ' + xTandemResultsFile
                print(statusString)
                self.logFh.write(statusString)
                self.logFh.flush()

            else:

                # setting up X!Tandem CFG file
                cfgDoc = xml.dom.minidom.parse(self.xtandemDefaultInputPath)
                nodeList = cfgDoc.getElementsByTagName("note")
                inputNodeList = [x for x in nodeList if x.getAttribute('type') == 'input']
                labelList = [x.getAttribute('label') for x in inputNodeList]
                valuesList = [x.childNodes for x in inputNodeList]
                #
                # got all the handles in default_input.xml file
                # now fill the slots
                #
                # max E value
                maxValidEvalueInd = labelList.index("output, maximum valid expectation value")
                valuesList[maxValidEvalueInd][0].data = self.updatedSettings['xtandemPars']['maximum valid E value']
                #
                # ppm tolerances
                ppmTols = self.updatedSettings['xtandemPars']['parent ion mass tolerance, ppm'].split(', ')
                ppmTolMinusInd = labelList.index("spectrum, parent monoisotopic mass error minus")
                ppmTolPlusInd = labelList.index("spectrum, parent monoisotopic mass error plus")
                valuesList[ppmTolMinusInd][0].data = ppmTols[0]
                valuesList[ppmTolPlusInd][0].data = ppmTols[1]
                #
                # static modifications
                staticModsInd = labelList.index("residue, modification mass")
                valuesList[staticModsInd][0].data = self.updatedSettings['xtandemPars']['static modifications']
                #
                # dynamic modifications
                dynamicModsInd = labelList.index("residue, potential modification mass")
                valuesList[dynamicModsInd][0].data = self.updatedSettings['xtandemPars']['dynamic modifications']
                #
                # cleavage specificity and also respectively maximum nimber of missed cleavages
                cleavageSpecificityIndex = labelList.index("protein, cleavage site")
                valuesList[cleavageSpecificityIndex][0].data = self.updatedSettings['xtandemPars'][
                    'cleavage specificity']
                misedCleavagesIndex = labelList.index("scoring, maximum missed cleavage sites")
                if self.updatedSettings['xtandemPars']['cleavage specificity'] == "[X]|[X]":
                    valuesList[misedCleavagesIndex][0].data = "50"
                else:
                    # just in case one missed cleavge
                    # for speed reasons it is better to have even 0
                    # but for safety let's have 1
                    valuesList[misedCleavagesIndex][0].data = "1"
                #
                # protein collection
                proteinTaxonInd = labelList.index("protein, taxon")
                valuesList[proteinTaxonInd][0].data = 'FASTAFILE'
                #
                # path to taxonomy file
                taxonomyPathInd = labelList.index("list path, taxonomy information")
                valuesList[taxonomyPathInd][0].data = self.xtandemCurrentTaxonomyListPath
                #
                # just handles on input and output spectra files
                specPathInd = labelList.index("spectrum, path")
                outPathInd = labelList.index("output, path")
                #
                # create xtandem input cfg xml file
                valuesList[specPathInd][0].data = dtaFile  # file in
                valuesList[outPathInd][0].data = xTandemResultsFile  # file out
                cfgFileName = dtaFileNameNoExt + '_CFG.xml'  # xtandem cfg xml file
                cfgFH = open(cfgFileName, 'w')
                cfgDoc.writexml(cfgFH)
                cfgFH.close()

                statusString = '\nCreated X!Tandem config file at ' + cfgFileName
                print(statusString)
                self.logFh.write(statusString)
                self.logFh.flush()

                #############################################################################
                # run XTandem
                try:
                    localTime = time.strftime("%m/%d/%y %H:%M:%S", time.localtime())
                    statusString = 'step 1.  starting x!tandem run. %s' % localTime
                    print('\n' + statusString)
                    self.logFh.write(statusString + '\n')
                    self.logFh.flush()
                    subprocess.call([self.xtandemExePath, cfgFileName])
                    localTime = time.strftime("%m/%d/%y %H:%M:%S", time.localtime())
                    statusString = 'step 1.  finished x!tandem run. %s' % localTime
                    print(statusString)
                    self.logFh.write(statusString + '\n')
                    self.logFh.flush()
                except:
                    localTime = time.strftime("%m/%d/%y %H:%M:%S", time.localtime())
                    statusString = 'step 1.  x!tandem run has failed! %s' % localTime
                    print('\n' + statusString)
                    self.logFh.write(statusString + '\n')
                    self.logFh.flush()
                    self.logFh.close()
                    continue
                #
                # clean up xtandem config files
                os.popen('del "%s"' % cfgFileName)
                os.popen('del "%s"' % self.xtandemCurrentTaxonomyListPath)
                #############################################################################

            ############################################################################
            # now parse the xtandem results
            xTandemRes = do_parse_XTandemXmlOutput(xTandemResultsFile)

            # now check the number of peptides from xtandem and
            # switch to something safer if there number is below threshold
            scanCharge = [i[0:2] for i in xTandemRes[1:]]
            numIds = len(dict.fromkeys(scanCharge))
            if numIds < 2:
                print('number of spectra identified less than 2!!')
                print('stop processing!!')
                self.logFh.write('number of spectra identified less than 2!!\n')
                self.logFh.write('stop processing!!\n')
                self.logFh.flush()
                break
            if ((numIds < int(self.updatedSettings['refiningPars']['otherParams'][
                                  'minimum number of peptides for regression'])) and
                    (self.updatedSettings['refiningPars']['choices']['refining method'] == 'additiveRegression')):
                self.updatedSettings['refiningPars']['choices']['refining method'] = 'simpleShift'
                self.updatedSettings['refiningPars']['choices']['simpleShift'] = 'medianShift'

            # parse and combine the dtaFile and LOG file
            dtaToLogPttrn = re.compile('(.+)_dta\.txt')
            logFile = dtaToLogPttrn.sub(r'\1_DeconMSn_log.txt', dtaFile)
            profileFile = dtaToLogPttrn.sub(r'\1_profile.txt', dtaFile)
            if (os.path.exists(logFile) and os.path.exists(profileFile)):
                statusString = '\tfound files from DeconMSn\n\t%s\n\t%s\n' % (
                    os.path.basename(logFile), os.path.basename(profileFile))
                print(statusString)
                self.logFh.write(statusString + '\n')
                self.logFh.flush()
                #
                self.logFileMissing = False
                #
                try:
                    t1 = time.clock()
                    statusString = "step 2.  parsing dta and log files"
                    print(statusString)
                    self.logFh.write(statusString + '\n')
                    self.logFh.flush()
                    dtaLogData = do_read_dta_n_log_n_profile_files(dtaFile, logFile, profileFile)
                    t2 = time.clock()
                    statusString = "step 2.  done parsing dta and log files"
                    print(statusString)
                    self.logFh.write(statusString + '\n')
                    self.logFh.flush()
                except:
                    statusString = "step 2.  failed parsing dta and/or DeconMSn_log and/or profile files\n"
                    statusString = statusString + '\tfilenames: %s \n %s \n %s' % (dtaFile, logFile, profileFile)
                    print(statusString)
                    self.logFh.write(statusString + '\n')
                    self.logFh.flush()
                    self.logFh.close()
                    os.popen('del "%s"' % (xTandemResultsFile))
                    continue
                # combine xtandem results with LOG file
                # ---to get parent MS scan, intensity and TIC
                xtLogData = do_combine_xtandemRes_n_log_n_profile_file(xTandemRes, logFile, profileFile)
                del xTandemRes  # clean up
                os.popen('del "%s"' % (xTandemResultsFile))
            else:
                statusString = '\n\tDid not find files from DeconMSn\'s output\n\t  %s\n\tor\n\t  %s' % (
                    os.path.basename(logFile), os.path.basename(profileFile))
                statusString = statusString + '\n\n' + "\tThus, the program assumes that the concatenated dta file"
                statusString = statusString + '\n' + "\tis from extract_msn and won\'t use TIC and ion intensity"
                statusString = statusString + '\n' + "\tif those parameters were selected for regression analysis\n"
                print(statusString)
                self.logFh.write(statusString + '\n')
                self.logFh.flush()
                #
                self.logFileMissing = True
                try:
                    statusString = "step 2.  parsing dta file %s" % os.path.basename(dtaFile)
                    print(statusString)
                    self.logFh.write(statusString + '\n')
                    self.logFh.flush()
                    #
                    dtaLogData = do_read_just_dta_file(dtaFile)  # VLAD. Bram Snijders parsing problem #2
                    #
                    statusString = "step 2.  done parsing dta file %s" % os.path.basename(dtaFile)
                    print(statusString)
                    self.logFh.write(statusString + '\n')
                    self.logFh.flush()
                except:
                    statusString = "step 2.  failed parsing dta file %s" % os.path.basename(dtaFile)
                    print(statusString)
                    self.logFh.write(statusString + '\n')
                    self.logFh.flush()
                    self.logFh.close()
                    os.popen('del "%s"' % (xTandemResultsFile))
                    continue

                xtLogData = do_reformat_xtandemRes(xTandemRes)  # does do_combine_xtandemRes_n_log_file without log
                # now check the settings and update if necessary
                self.allDimensions = ['scanNum', 'mz']
                selectedDims = self.updatedSettings['refiningPars']['otherParams']['dimensions']
                if selectedDims != '':
                    selectedDims = [i.strip(' ') for i in selectedDims.split(',')]
                    # --- VLAD change to not in loop
                    for d in ['logTrappedIonInt', 'trappedIonsTIC']:
                        if (d in selectedDims) and (len(selectedDims) > 0):
                            ind = selectedDims.index(d)
                            del selectedDims[ind]
                    self.updatedSettings['refiningPars']['otherParams']['dimensions'] = ', '.join(selectedDims)
            ###########################################################################

            # save the settings file
            # there will be a file per file
            # which is somewhat redundant
            if 'spectra dataset' in self.updatedSettings:
                del self.updatedSettings['spectra dataset']
            if 'spectra directory' in self.updatedSettings:
                del self.updatedSettings['spectra directory']

            # now check that if regression selected there is at least one dimension selected
            # otherwise switch to medianShift
            if (self.updatedSettings['refiningPars']['choices']['refining method'] == 'additiveRegression' and
                    self.updatedSettings['refiningPars']['otherParams']['dimensions'] == ''):
                self.updatedSettings['refiningPars']['choices']['refining method'] = 'simpleShift'
                self.updatedSettings['refiningPars']['choices']['simpleShift'] = 'medianShift'

            writeSettingsToXML(self.updatedSettings, dtaFileNameNoExt + '_SETTINGS.xml')  # VLAD to fix path

            # memorizing the directory and dataset
            ##            self.updatedSettings['spectra dataset'] = os.path.basename(dtaFile).split('_dta.txt')[0] #original
            # better to switch to regular expression later
            self.updatedSettings['spectra dataset'] = os.path.basename(dtaFile).lower().split('_dta.txt')[0]
            self.updatedSettings['spectra directory'] = os.path.dirname(dtaFile)

            # MAIN THING
            # fixing the parent mz
            try:
                localTime = time.strftime("%m/%d/%y %H:%M:%S", time.localtime())
                statusString = 'step 3.  starting refining the parent ion masses %s' % localTime
                print(statusString)
                self.logFh.write(statusString + '\n')
                self.logFh.flush()
                #
                # note the refining method
                mainApproach = self.updatedSettings['refiningPars']['choices']['refining method']
                if mainApproach == 'additiveRegression':
                    specificApproach = self.updatedSettings['refiningPars']['choices']['additiveRegression']
                    approach = mainApproach + '/' + specificApproach
                elif mainApproach == 'simpleShift':
                    specificApproach = self.updatedSettings['refiningPars']['choices']['simpleShift']
                    approach = mainApproach + '/' + specificApproach
                elif mainApproach == 'bypassRefining':
                    approach = mainApproach
                statusString = '\trefining with %s approach' % approach
                print(statusString)
                self.logFh.write(statusString + '\n')
                self.logFh.flush()
                #
                self.statPars = None
                # -------------------
                fixedDtaEntryLines = do_fix_parent_ion_mz(self, xtLogData, dtaLogData)  # ----------
                # -------------------
                #
                localTime = time.strftime("%m/%d/%y %H:%M:%S", time.localtime())
                statusString = 'step 3.  done refining the parent ion masses %s' % localTime
                print(statusString)
                self.logFh.write(statusString + '\n')
                self.logFh.flush()
            except:
                localTime = time.strftime("%m/%d/%y %H:%M:%S", time.localtime())
                statusString = 'step 3.  failed refining the parent ion masses!! %s' % localTime
                print(statusString)
                self.logFh.write(statusString + '\n')
                self.logFh.flush()
                self.logFh.close()
                raise

            # create updated file
            try:
                statusString = "step 4.  updating the dta file"
                print(statusString)
                self.logFh.write(statusString + '\n')
                self.logFh.flush()
                # --------------------
                do_createFixedDtaFile(dtaFile, fixedDtaEntryLines)  # ----------
                # --------------------
                statusString = "step 4.  done updating the dta file"
                print(statusString)
                self.logFh.write(statusString + '\n')
                self.logFh.flush()
            except:
                statusString = "step 4.  failed updating the dta file!"
                print(statusString)
                self.logFh.write(statusString + '\n')
                self.logFh.flush()
                os.popen('del "%s"' % (xTandemResultsFile))
                continue

            toc = time.clock()
            executionTime = time.strftime("%HH:%MM:%SS", time.gmtime(toc - tic))
            statusString = 'finished refining %s \nin %s' % (dtaFile, executionTime)
            statusString = '-' * 20 + '\n' + statusString
            print(statusString)
            self.logFh.write(statusString + '\n')
            self.logFh.flush()

            #
            # now tell how successful was the refining
            # mean/stdev estimates before and after
            #
            statusString = '\nEstimates of ORIGINAL parent ion mass error distribution:\n'
            statusString += '\t\t\tmean\tst.dev\n'
            temp = self.statPars['ori']['Exp.Max.']
            statusString += 'Exp. Max. estimate\t%s\t%s\n' % (round(temp['mean'], 2), round(temp['stdev'], 2))
            temp = self.statPars['ori']['Robust']
            statusString += 'Robust estimate\t\t%s\t%s\n' % (round(temp['mean'], 2), round(temp['stdev'], 2))
            print(statusString)
            self.logFh.write(statusString + '\n')
            self.logFh.flush()
            #
            statusString = 'Estimates of REFINED parent ion mass error distribution:\n'
            statusString += '\t\t\tmean\tst.dev\n'
            temp = self.statPars['new']['Exp.Max.']
            statusString += 'Exp. Max. estimate\t%s\t%s\n' % (round(temp['mean'], 2), round(temp['stdev'], 2))
            temp = self.statPars['new']['Robust']
            statusString += 'Robust estimate\t\t%s\t%s\n' % (round(temp['mean'], 2), round(temp['stdev'], 2))
            print(statusString)
            self.logFh.write(statusString + '\n')
            self.logFh.flush()

            os.popen('del "%s"' % (xTandemResultsFile))

            try:
                self.logFh.close()
            except:
                # the file has already been closed
                continue

    def performSomeChecks(self):
        # check that R(D)COM is installed if R_runmed_spline is about to run
        from win32com.client import Dispatch
        if (self.updatedSettings['refiningPars']['choices']['refining method'] == 'additiveRegression' and
                self.updatedSettings['refiningPars']['choices']['additiveRegression'] == 'R_runmed_spline'):
            try:
                sc = Dispatch("StatConnectorSrv.StatConnector")
                sc.Init("R")
            except:
                statusString = 'Can not find R(D)COM server!\nPlease install R(D)COM or use another regression approach.'
                print(statusString)
                self.logFh.write(statusString + '\n')
                self.logFh.flush()
                self.logFh.close()
