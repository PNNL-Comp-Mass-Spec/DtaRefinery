# this is a speed up version of dta paser
# see the earlier versions for other parser
# from ver 1.05

# 2010/02/16 bugfix
# fixes the problem in parsing when the parent MH is
# an integer, but not a floating point value


from my_read_log_and_profile import getAuxInfo
from math import log as lg
import csv
import re



def do_read_just_dta_file( dtaFileName):

    dataOut = [('dtaEntryUnqID','stringIndex','entryString','scanNum','mz')]
##    pttrn = re.compile('(\d+\.\d+)\s\d+\s+scan=(\d+)\scs=(\d+)')# this is the string just below the headers
    pttrn = re.compile('(\S+)\s\d+\s+scan=(\d+)\scs=(\d+)')# this is the string just below the headers    
    
    #read dta file
    dtaFile = open(dtaFileName,'r')
    
    index = -1
    while True:
        line = dtaFile.readline()
        index += 1
        if not line:
            break
        if line[0:10] == '='*10:
            selectedString = dtaFile.readline().strip('\n')
            index += 1
            mh   = float(pttrn.match(selectedString).group(1))
            scan = pttrn.match(selectedString).group(2)
            z    = pttrn.match(selectedString).group(3)
            dtaEntryUnqID = 'scan=%s cs=%s' % (scan, z)
            mzObs = (float(mh)+(int(z)-1)*1.00727646688)/int(z)
            entryOut = ( dtaEntryUnqID, index, selectedString, scan, mzObs)
            dataOut.append( entryOut)
        
    dtaFile.close()

    return dataOut





def do_read_dta_n_log_n_profile_files( dtaFileName, logFileName, profileFileName):

    dictAuxInfo = getAuxInfo( logFileName, profileFileName)

    dataOut = [('dtaEntryUnqID','stringIndex','entryString','scanNum','mz','logTrappedIonInt', 'trappedIonsTIC')]
##    pttrn = re.compile('(\d+\.\d+)\s\d+\s+scan=(\d+)\scs=(\d+)')# this is the string just below the headers
    pttrn = re.compile('(\S+)\s\d+\s+scan=(\d+)\scs=(\d+)')# this is the string just below the headers    
    
    #read dta file
    dtaFile = open(dtaFileName,'r')
    
    index = -1
    while True:
        line = dtaFile.readline()
        index += 1
        if not line:
            break
        if line[0:10] == '='*10:
            selectedString = dtaFile.readline().strip('\n')
            index += 1
            mh   = float(pttrn.match(selectedString).group(1))
            scan = pttrn.match(selectedString).group(2)
            z    = pttrn.match(selectedString).group(3)
            dtaEntryUnqID = 'scan=%s cs=%s' % (scan, z)
            mzObs = (float(mh)+(int(z)-1)*1.00727646688)/int(z)
            #extra
            ms1ScanNum =        dictAuxInfo[scan][0]
            logTrappedIonInt =  dictAuxInfo[scan][1]
            trappedIonsTIC =    dictAuxInfo[scan][2]
            #extra
            entryOut = ( dtaEntryUnqID, index, selectedString, ms1ScanNum, mzObs, logTrappedIonInt, trappedIonsTIC)
            dataOut.append( entryOut)
        
    dtaFile.close()
    return dataOut


if __name__ == '__main__':
    do_read_just_dta_file("testsulfo_dta2.txt")


