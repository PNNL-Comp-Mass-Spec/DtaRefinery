from my_read_log_and_profile import getAuxInfo


def do_combine_xtandemRes_n_log_n_profile_file(xTandemRes, logFileName, profileFileName):
    ##    #read log file
    ##    logFile = open(logFileName, 'r')
    ##    csv_reader = csv.reader(logFile,delimiter='\t')
    ##    log = [tuple(x) for x in csv_reader]
    ##    log = log[1:]
    ##    logFile.close()
    ##
    ##
    ##    #flipping the structure of log entries
    ##    flog = [[y[x] for y in log] for x in range(len(log[0]))]
    ##
    ##
    ##    #for (dta scan, charge)
    ##    #---returns (parent ion MS scan, mz, parent ion intensity, ppm)
    ##    def get_extra_info(x):
    ##
    ##        scan = str(x[0])
    ##        charge = str(x[1])
    ##
    ##        #looking for indeces within the flog structure for the given MS/MS scan number
    ##        flog_scan_indeces = [i for i in range(len(flog[0])) if flog[0][i] == scan]
    ##
    ##        #looking for index within found indeces given the charge state
    ##        index = [i for i in flog_scan_indeces if flog[3][i] == charge]
    ##
    ##        if len(index) != 1:
    ##            raise Exception("Some error in indexing scans and charges")
    ##
    ##        index = index[0] #de-listing
    ##
    ##        #returns
    ##        #---parent MS scan number,
    ##        #---log of normalized parent ion intensity
    ##        #---and normalized TIC
    ##        #---
    ##        #---flog[1] Parent_Scan column
    ##        #---flog[6] Intensity column
    ##        #---flog[7] AGC accumulation time
    ##        #---flog[8] TIC
    ##
    ##        extra_info = (float(flog[1][index]),
    ##                      lg(float(flog[6][index])*float(flog[7][index])/1000, 10),
    ##                      float(flog[8][index])*float(flog[7][index])/1000)
    ##        return extra_info

    dictAuxInfo = getAuxInfo(logFileName, profileFileName)

    mzObs = [x[2] for x in xTandemRes[1:]]
    massErrorPpm = [x[3] for x in xTandemRes[1:]]
    dtaEntryUnqID = ['scan=%s cs=%s' % x[0:2] for x in xTandemRes[1:]]

    ms1ScanNum = [dictAuxInfo[str(i[0])][0] for i in xTandemRes[1:]]
    logTrappedIonInt = [dictAuxInfo[str(i[0])][1] for i in xTandemRes[1:]]
    trappedIonsTIC = [dictAuxInfo[str(i[0])][2] for i in xTandemRes[1:]]

    dataOut = zip(dtaEntryUnqID,
                  ms1ScanNum,
                  mzObs,
                  logTrappedIonInt,
                  trappedIonsTIC,
                  massErrorPpm)

    header = [['dtaEntryUnqID',
               'scanNum',
               'mz',
               'logTrappedIonInt',
               'trappedIonsTIC',
               'massErrorPpm']]

    dataWithHeader = header + list(dataOut)
    return dataWithHeader


def do_reformat_xtandemRes(xTandemRes):
    scanNum = [x[0] for x in xTandemRes[1:]]
    mzObs = [x[2] for x in xTandemRes[1:]]
    massErrorPpm = [x[3] for x in xTandemRes[1:]]
    dtaEntryUnqID = ['scan=%s cs=%s' % x[0:2] for x in xTandemRes[1:]]

    dataOut = zip(dtaEntryUnqID,
                  scanNum,
                  mzObs,
                  massErrorPpm)

    header = [['dtaEntryUnqID',
               'scanNum',
               'mz',
               'massErrorPpm']]

    dataWithHeader = header + list(dataOut)
    return dataWithHeader


####################################################################
if __name__ == '__main__':
    import shelve

    arc = shelve.open('xTandemRes.shlv')
    xTandemRes = arc['xTandemRes']
