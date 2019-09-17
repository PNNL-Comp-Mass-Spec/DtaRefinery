import xml.dom.minidom
import copy



def extendDict(path, d):
    key = path[0]
    if not d.has_key(key):
        d[str(key)] = {}
    path = path[1:]
    if len(path) > 0:
        return extendDict(path, d[key])


def addToDict(path, finalDict, (label, data)):
    key = path[0]
    path = path[1:]
    if path != []:
        return addToDict(path, finalDict[key], (label, data))
    else:
        finalDict[str(key)][str(label)] = data
        return finalDict


def getPaths(paths, finalDict, mainNode):
    for path in paths:
        node = copy.deepcopy(mainNode)
        for step in path:
            #get the final node. for each step there shold be only one
            node = [i for i in node.childNodes if i.localName == step][0]
        childrenAll = [i for i in node.childNodes if i.nodeType == i.ELEMENT_NODE]
        if childrenAll != []:
            children = [i for i in childrenAll if
                            (i.localName != 'choice' and i.localName != 'par')]        
            if children != []:
                del paths[paths.index(path)]
                for child in children:
                    newPath = path + [child.localName]
                    paths.append(newPath)
                    extendDict(newPath, finalDict)
                getPaths(paths, finalDict, mainNode)
            else:
                for child in childrenAll:
                    label = child.getAttribute('label')
                    if child.childNodes != []:
                        data = child.childNodes[0].data.strip('\t\n')
                    else:
                        data = ''
                    #get to that node in dictionay
                    finaDict = addToDict(path, finalDict, (label, data))
                        


def getSettingsFromXML(xmlFileName):
    xmlDoc = xml.dom.minidom.parse(xmlFileName)
    paths = [[]]
    finalDict = {}
    getPaths(paths, finalDict, xmlDoc)
    #removes the first layer of allPars
    return finalDict[finalDict.keys()[0]]





def dict2xml(doc, mainElement, finalDict):
    currElem = mainElement    
    for k in finalDict.keys():
        if type(finalDict[k]) == dict:
            '''create it'''
            element = doc.createElement(k)
            mainElement.appendChild(element)
            dict2xml(doc, element, finalDict[k])        
        else:
            name = 'par'
            if mainElement.localName in ['choices']:
                name = 'choice'
            element = doc.createElement(name)
            element.setAttribute('label', k)
            text = doc.createTextNode(str(finalDict[k]))
            element.appendChild(text)
            mainElement.appendChild(element)




def writeSettingsToXML( settings, fileName):
    doc = xml.dom.minidom.Document()
    mainElement = doc.createElement('allPars')
    doc.appendChild(mainElement)
    dict2xml(doc, mainElement, settings)
    fh = open(fileName,'w')
    doc.writexml(fh, indent='\t', addindent='\t', newl='\n')
    fh.close()    

    


























