from pprint import pprint as p
import csv
import re

def do_createFixedDtaFile_OLD( dtaFileName, fixedDtaEntryLines):

    dtaFH = open(dtaFileName, 'r')
    dtaLines = dtaFH.readlines()
    dtaFH.close()

    #update the lines
    for i in fixedDtaEntryLines:
        dtaLines[i[1]] = i[2] + '\n'

    #create the fixed file name
    pttrn = re.compile('(.+)_dta\.txt')
    fixedFileName = pttrn.sub(r'\1_FIXED_dta.txt', dtaFileName)

    #write the data
    fixedFH = open(fixedFileName, 'w')
    fixedFH.writelines(dtaLines)
    fixedFH.close()

def do_createFixedDtaFile( dtaFileName, fixedDtaEntryLines):

    pttrn = re.compile('(.+)_dta\.txt')

    dtaFH = open(dtaFileName, 'r')
    #create the fixed file name
    fixedFileName = pttrn.sub(r'\1_FIXED_dta.txt', dtaFileName)
    fixedFH = open(fixedFileName, 'w')

    entryIndex = -1
    index = -1
    while True:
        line = dtaFH.readline()
        index += 1
        if not line:
            break
        fixedFH.write( line)            
        if line[0:10] == '='*10:
            #substitute next with updated one
            targetLine = dtaFH.readline() #reading the line that to be replaced
            index += 1
            entryIndex += 1
            #just to make sure that they are from the same place
            if index == fixedDtaEntryLines[ entryIndex][1]:
                fixedFH.write( fixedDtaEntryLines[ entryIndex][2] + '\n')

    fixedFH.close()
    dtaFH.close()










if __name__ == '__main__':

    #read new entries file
    fileName = 'TEMP.txt'
    f = open(fileName, 'r')
    yo = csv.reader(f,delimiter='\t')
    L = [tuple(x) for x in yo]
    f.close()


    L2 = [[int(i[0]),i[1]] for i in L]
    p(L2[0:4])

    #read original dta file
    fileName = 'VP2P47_B_unf_5xDil_rn1_11Oct07_Raptor_Fst-75-1_dta.txt'
    f = open(fileName, 'r')
    lines = f.readlines()
    f.close()


    #update the entries
    for i in L2:
        lines[i[0]] = i[1]+'\n'

    #output
    pttrn = re.compile('(.+)_dta\.txt')
    logFile = pttrn.sub(r'\1_FIXED_dta.txt',fileName)
    f = open(logFile, 'w')
    f.writelines(lines)
    f.close()

