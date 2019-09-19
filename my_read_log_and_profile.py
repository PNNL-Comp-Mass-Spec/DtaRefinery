import csv
from math import log as lg

def getAuxInfo( logFileName, profileFileName):

    logFile = open(logFileName, 'r')
    csv_reader = csv.reader(logFile,delimiter='\t')
    log = [tuple(x) for x in csv_reader]
    log = log[1:]
    logFile.close()
    # MSn_Scan -- 0
    # Parent_Scan -- 2
    # Mono_Intensity -- 10
    if log[7] == ('MSn_Scan',
                  'MSn_Level',
                  'Parent_Scan',
                  'Parent_Scan_Level',
                  'Parent_Mz',
                  'Mono_Mz',
                  'Charge_State',
                  'Monoisotopic_Mass',
                  'Isotopic_Fit',
                  'Parent_Intensity',
                  'Mono_Intensity'):
        log = log[8:]
    else:
        raise Exception

    profileFile = open(profileFileName, 'r')
    csv_reader = csv.reader(profileFile,delimiter='\t')
    profile = [tuple(x) for x in csv_reader]
    profileFile.close()
    # AGC_accumulation_time -- 2
    # TIC -- 3
    if profile[0] == ('MSn_Scan',
                      'Parent_Scan',
                      'AGC_accumulation_time',
                      'TIC'):
        profile = profile[1:]
    else:
        raise Exception

    dictAuxInfo = {}
    #len(log) should be equal to len(profile) now
    for i in range(len(log)):
        dictAuxInfo[log[i][0]] = (log[i][2],
                                  lg(float(log[i][10])*float(profile[i][2])/1000, 10),
                                  float(profile[i][3])*float(profile[i][2])/1000)
    # returns key:ms2 values:(ms1, log10IntensityInTheTrap, TIC_InTheTrap)
    return dictAuxInfo



if __name__ == '__main__':
    logFileName = 'VP1P156_A-b_18Dec06_Draco_06-07-10fst2_DeconMSn_log.txt'
    profileFileName = 'VP1P156_A-b_18Dec06_Draco_06-07-10fst2_profile.txt'
    x = getAuxInfo(logFileName, profileFileName)
    print(x['3198'])
