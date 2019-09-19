import xml.dom.minidom
import re
import numpy

def do_parse_XTandemXmlOutput(fileName):

    #---parsing the XML file---
    doc = xml.dom.minidom.parse(fileName)
    biomlElement = doc.getElementsByTagName('bioml')[0] #the root

    #getting
    #<group type='model'>
    #</group>
    try:
        groupModelElements = [x for x in biomlElement.childNodes if\
                              (x.nodeName == 'group' and x.getAttribute('type') == 'model')]
    except:
        print('Error! Something wrong with XML file format (1)')

    #getting
    #<group type='support'>
    #    <note label='Description'> scan=XXX z=X</note>
    #</group>
    groupSupportElements = [x.getElementsByTagName('group')[0]\
                            for x in groupModelElements if\
                                x.getAttribute('type') != 'support']
    noteDescriptionElements = [[y for y in x.getElementsByTagName('note') \
                                if y.getAttribute('label') == 'Description'][0] \
                                for x in groupSupportElements]
    noteDescriptionData = [x.childNodes[0].data for x in noteDescriptionElements]

    #getting <domain></domain>
    #this is bypassing extraction "protein" and "peptide" elements
    #Thus I'm just loosing information on matching protein
    #and postion and number of hits within protein
    domainElements = [x.getElementsByTagName('domain') for x in groupModelElements]

    #organizing into
    #[groupModelElements, noteDescriptionData, [domainElements,...]]
    data = zip(groupModelElements, noteDescriptionData, domainElements)
    #   groupModelElements mhObs
    #   groupModelElements z
    #   noteDescriptionData scan
    #   domainElements delta
    #   domainElements mhTheor
    #   domainElements expect


    mhObsList = [x.getAttribute('mh') for x in groupModelElements]
    zList = [x.getAttribute('z') for x in groupModelElements]
    pttrn = re.compile('.*scan=(\d+)\s.*')
    scanList = [pttrn.match(x).group(1) for x in noteDescriptionData]



    #sequenceList = [x.getAttribute('seq') for x in domainElements]
    #mhTheorList = [x.getAttribute('mh') for x in domainElements]
    #dMList = [x.getAttribute('delta') for x in domainElements]
    #eValueList = [x.getAttribute('expect') for x in domainElements]



    domainData = [[[y.getAttribute('seq'),
                    y.getAttribute('mh'),
                    y.getAttribute('delta'),
                    y.getAttribute('expect')
                    ] for y in x] for x in domainElements]


    data = zip(mhObsList, zList, scanList, domainData)

    dataFlat = []
    for i1 in data:
        for i2 in i1[3]:
            dataFlat.append(tuple(list(i1[0:3]) + i2))

    dataFlatUnq = dict.fromkeys(dataFlat).keys()
    headers = [('mhObs','z','scan','peptide','mhTheor','deltaM','eValue')]

    #mzTheor = (mhTheor + (z-1)*1.00727646688)/z
    mzTheor = [(float(x[4])+(float(x[1])-1)*1.00727646688)/float(x[1]) for x in dataFlatUnq]
    mzObs = [(float(x[0])+(float(x[1])-1)*1.00727646688)/float(x[1]) for x in dataFlatUnq]
    mzs = zip(mzObs, mzTheor)
    ppm = [1e6*(x[0]-x[1])/x[1] for x in mzs]
    scan = [int(x[2]) for x in dataFlatUnq]
    charge = [int(x[1]) for x in dataFlatUnq]    

    data = zip(scan, charge, mzTheor, ppm) 
    headersAndData = [('scan', 'charge', 'mz', 'ppm')] + list(data)

    ##dataGroupModels = numpy.array(headersAndData)
    return headersAndData

if __name__ == '__main__':
##    rez = do_parse_XTandemXmlOutput('out_test.xml')
    rez = do_parse_XTandemXmlOutput('VP2P47_B_unf_5xDil_rn1_11Oct07_Raptor_Fst-75-1_dta_OUT.xml')
    rez = numpy.array(rez)    
    numpy.savetxt('dataRez.txt', rez, fmt='%s', delimiter='\t')
