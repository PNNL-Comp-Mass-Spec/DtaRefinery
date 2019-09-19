import os.path
import random
import math

#
from aux_sys_err_prediction_module.additive.my_1D_regression_analysis import do_1D_regression_analysis
#

from numpy import log, array, median, zeros
from pylab import plot, grid, axhline,\
                  ylim, show, subplot, clf,\
                  savefig, hist, xlabel, ylabel,\
                  title, text, xlim, subplots_adjust


# the name of the approach encoded in the module
myName = 'additiveRegression'



def do_plot_iteration_fit( *args):

    Controller, xtPar, xtPpmOld, xtPpmPred, isSuccessfulFit, predErr, key, count = args

    dirName =  Controller.updatedSettings['spectra directory']
    dSetName = Controller.updatedSettings['spectra dataset']
    
    ax = subplot(111)
    ax.xaxis.major.formatter.set_powerlimits((-4,+4))
    subplots_adjust(top=0.8)
    plot( xtPar, xtPpmOld,'bo')
    plot( xtPar, xtPpmPred,'r+')
    xlabel(key)
    ylabel('ppm')
    t = ax.set_title('dataset:      %s   \n' % dSetName +
                     'parameter:    %s   \n' % key +
                     'iteration:    %s   \n' % count +
                     'isSuccessfulFit:  %s   \n' % isSuccessfulFit +
                     'prediction error: %s   ' % predErr,
                     {'horizontalalignment': 'left',
                      'fontsize': 10})
    t.set_x(0)
    grid()
    axhline(0,color='g')

    lims     = Controller.updatedSettings['plottingPars']['plotting range, ppm']
    lims     = tuple([float(i) for i in lims.split(',')])    
    ylim( lims)
    filePath = os.path.join(dirName, dSetName)
    suffix = '_iter-%s__%s.png' % (count, key)
    filePath += suffix
    savefig(str(filePath))
    clf()





def do_split_inputs( xTandemInput, dtaInput, K):

    # initialize the holder
    holder = [[[],[]] for x in range(K+1)]

    # dtaEntryUnqID
    # just takes the first columns of IDs
    idsXt   = [x[0] for x in xTandemInput[1:]]
    uidsXt  = dict.fromkeys(idsXt).keys()
    idsDta  = [x[0] for x in dtaInput[1:]]

    # fill the first slot with dtaEntryUnqID
    # holder[0][0] unique IDs from x!tandem results: list of values like 'scan=14630 cs=2', 'scan=14631 cs=3'
    # holder[0][1] whatever left in dta file: list of values like 'scan=14 cs=2', scan=15 cs=3'
    idsDtaOnly = idsDta[:]
    for x in uidsXt:
        idsDtaOnly.remove(x)
        
    holder[0][0] = list(uidsXt)
    holder[0][1] = idsDtaOnly
    
    # fill the rest K slots
    L = len(uidsXt)
    # it may be a problem here if L < K !!
    N = L/K #min length of pieces
    R = L%K #how much left
    Z = [N for j in range(K)] #get K numbers N      ??same as [N]*K??
            
    Z[0:R] = [j+1 for j in Z[0:R]] # distribute the leftovers each into one interval

    shuffledXtUids = list(uidsXt)
    random.shuffle(shuffledXtUids) #randomize the entry IDs

    ind = 0
    for i in range(K):
        j = math.floor(Z[i])
 
        learn = shuffledXtUids[0:ind] + shuffledXtUids[ind+j:] # exclude ind:ind+j interval
        fit = shuffledXtUids[ind:ind+j]                # include ind:ind+j interval
        holder[i+1][0] = learn[:]
        holder[i+1][1] = fit[:]
        ind += j

    #-------------------------------------------------------------------
    # !! now holder is ready for switching to full data from indices
    # function takes IDs returns the full data
    def fetch_full_data(ids, fullInput):
        
        header    = fullInput[0]
        fullInput = fullInput[1:]
        
        # flip the input structure
        flipInput = [[y[x] for y in fullInput] for x in range(len(fullInput[0]))]

        # get the indices corresponding to ids
        indices = []
        for idi in ids:
            x = [i for i in range(len(flipInput[0])) if flipInput[0][i] == idi]
            indices.extend(x)

        # subset the input
        subInput = [fullInput[i] for i in indices]

        return [header,] + subInput
    #--------------------------------------------------------------------
    

    for x in range(len(holder)):
        holder[x][0] = fetch_full_data( holder[x][0], xTandemInput)
        holder[x][1] = fetch_full_data( holder[x][1], dtaInput)

##    print('done splitting the dataset for overfitting proof mode')
    return holder
            

    




def do_additive_regression_analysis( Controller, xTandemInput, dtaInput):

    updatedSettings = Controller.updatedSettings
    logFh = Controller.logFh

##    params = correctionPars[myName]['params']
##    params['other params'] = correctionPars['other params']

    # make plots of all iterations??
    plotIters = {'True':True, 'False':False}[updatedSettings['plottingPars']['plot all iteration fits']]

    # Sort out which column is which parameter
    xtColumns   = list(xTandemInput[0][1:])
    dtaColumns  = list(dtaInput[0][3:])
##    allPars     = ['scanNum', 'mz', 'logTrappedIonInt', 'trappedIonsTIC']
    allPars     = Controller.allDimensions 
    xtIndeces   = [xtColumns.index(i) for i in allPars]
    dtaIndeces  = [dtaColumns.index(i) for i in allPars]
    par2col     = dict(zip(allPars, zip(xtIndeces,dtaIndeces)))


    # isOverfitProofMode??
    isOverfitProofMode = {'True':True, 'False':False}[updatedSettings['refiningPars']['otherParams']['use overfit proof mode']]
    # ---if True then split the inputs
    if isOverfitProofMode:
        numPieces = int(updatedSettings['refiningPars']['otherParams']['number of splits for overfit proof mode'])
        ARG = do_split_inputs( xTandemInput, dtaInput, numPieces)
    # ---else roll the original inputs
    else:
        ARG = [[xTandemInput, dtaInput]]
    # ARG structure
    #[[xTandemInput    , dtaInput    ],
    # [xTandemInput'   , dtaInput'   ],
    #           ...
    # [xTandemInput'''', dtaInput'''']]


    # convert ARG into ARG2
    # from lists to arrays
    ARG2 = [[] for x in range(len(ARG))]
    for ind in range(len(ARG)):
        xt  = array([[float(y) for y in x[1:]] for x in ARG[ind][0][1:]])
        dta = array([[float(y) for y in x[3:]] for x in ARG[ind][1][1:]])
      
        # extracting and setting errors
        xtPpm = xt[:,xtColumns.index('massErrorPpm')].copy()
        dtaPpm = zeros(dta.shape[0],'d')

        # zero center the errors by shifting by the median
        shift = median(xtPpm)
        xtPpm = xtPpm - shift
        dtaPpm = dtaPpm - shift

        # filling the list
        # [xt, xtPpm, dta, dtaPpm]
        ARG2[ind].append(xt)
        ARG2[ind].append(xtPpm)
        ARG2[ind].append(dta)
        ARG2[ind].append(dtaPpm)        




    # output format
    resultNames = ['isSuccessfulFit', 'predErr', 'ppmArrs']
    entry = dict.fromkeys(resultNames)

    # actual dimensions to use
    dimensions = updatedSettings['refiningPars']['otherParams']['dimensions'].split(',')
    dimensions = [i.strip(' ') for i in dimensions]

    # for each dimention create a result holder
    parSet = dict([(i,{'cols':par2col[i], 'entry':entry}) for i in dimensions])

    # main iterative fitting loop
    count = 1
    while True:

        # try each parameter. see if it provides good explanation
        for key in parSet.keys():

            # pull out right column indices
            xtInd, dtaInd  = parSet[key]['cols']

            # make an complex argument ARG3 from ARG2
            # ARG3 is needed just to feed into do_1D_regression_analysis
            # xt[:,xtInd], xtPpm, dta[:,dtaInd] == x, y, xEval
            ARG3 = [[] for x in range(len(ARG2))]
            for ind in range(len(ARG2)):
                # equivalent to 
                # xt[:,xtInd], xtPpm, dta[:,dtaInd] = ARG2[ind][0][:,xtInd], ARG2[ind][1], ARG2[ind][2][:,dtaInd]
                # I guess it is taking x0, y0, x1 to predict y1
                complArg = [ARG2[ind][0][:,xtInd], ARG2[ind][1], ARG2[ind][2][:,dtaInd]]
                ARG3[ind] = complArg

            # 1D REGRESSION IS HERE
            statusString = '\tstarting regression. %s pass, %s parameter...' % (count, key)
            print(statusString)
            logFh.write(statusString+'\n')
            logFh.flush()
            resultVals = do_1D_regression_analysis( ARG3, Controller) # ARG3 is split into K pieces if overfit proof mode is enabled
##            print(' got through 1D regression')
            # resultVals is a list with the order
            # 'isSuccessfulFit', 'predErr' prediction error MSE?, 'ppmArrs'


            results = dict(zip(resultNames, resultVals))
            parSet[key]['entry'] = results

            if plotIters:
                # xt the whole dataset
                # xtInd the column index where parameter values are
                # xtPpm the submitted ppm values
                # resultVals the result 1D regression output
                # key the parameter name
                # count the iteration count
                xtPar       = ARG3[0][0]
                xtPpmOld    = ARG2[0][1]
                xtPpmPred   = resultVals[2][0][0]
                isSuccessfulFit = resultVals[0]
                predErr = resultVals[1]
                do_plot_iteration_fit( Controller, xtPar, xtPpmOld, xtPpmPred, isSuccessfulFit, predErr, key, count)                


        # now parSet is filled with the results
        # we have to check which parameter is the best
        # and substract the results of corresponding
        # regression

        # TODO: check if the isSuccessfulFit first
        parToPredErrAndIfSuccess = [( i,
                                      parSet[i]['entry']['predErr'],
                                      parSet[i]['entry']['isSuccessfulFit']) for i in dimensions]
        parToPredErrAndSuccessOnly = [i for i in parToPredErrAndIfSuccess if i[2] == True]

        if parToPredErrAndSuccessOnly != []:
            parToPredErr = [[j[i] for j in parToPredErrAndSuccessOnly] for i in (0,1)]
            bestPar = parToPredErr[0][parToPredErr[1].index(min(parToPredErr[1]))]
            # now we know the best parameter of (mz, scan, int, TIC, ...)
            # whatever was used
            # correct the error residuals
            # iteration counter
            count += 1
            # subtract predicted (systematic) errors
            for ind in range(len(ARG2)):
                xtPpmPred  = parSet[bestPar]['entry']['ppmArrs'][ind][0]
                dtaPpmPred = parSet[bestPar]['entry']['ppmArrs'][ind][1]
                ARG2[ind][1] = ARG2[ind][1] - xtPpmPred 
                ARG2[ind][3] = ARG2[ind][3] - dtaPpmPred
        else:
            break


    # CONVERSION BACK-----------------------------------------------
    # now we have to return
    # xtPpm and dtaPpm
    # for xTandemInput and dtaInput
    # we have ARG2 with structure:
    # [[xt0, xtPpm0, dta0, dtaPpm0],
    #  [xt1, xtPpm1, dta1, dtaPpm1],
    #          ...
    #  [xtN, xtPpmN, dtaN, dtaPpmN]]
    dtaIDs    = []
    sysErrPpm =  []
    for i in range(len(ARG)):

        # get the dtaEntryUnqID
        dtaPart       = ARG[i][1]
        dtaPartHeader = dtaPart[0]
        dtaPartBody   = dtaPart[1:]
        dtaEntryUnqID = [x[0] for x in dtaPart]
        if dtaEntryUnqID[0] != 'dtaEntryUnqID':
            raise 'Something wrong with format of dtaInput'
        dtaEntryUnqID = dtaEntryUnqID[1:]
        dtaIDs.extend(dtaEntryUnqID)

        # get the ppms
        dtaPpm = ARG2[i][3]
        sysErrPpm.extend(dtaPpm)

    '''
    print('\nFirst 10 items of dtaIDs; size: ', len(dtaIDs))
    print(type(dtaIDs))
        
    for i in dtaIDs[0:10]:
        print(i)

    print('\nFirst 10 items of sysErrPpm; size: ', len(sysErrPpm))
    print(type(sysErrPpm))
        
    for i in sysErrPpm[0:10]:
        print(i)
     '''   
                
    # now obtain got IDs with corresponding systematic error
    # idToPpm is a list of (dtaEntryUnqID, ppm)
    idToPpm = [[y[x] for y in list(zip(dtaIDs, sysErrPpm))] for x in (0,1)]
        
    # now go through inputs like xTandemInput
    # and report fixed errors given the dtaEntryUnqID
    idCol      = list(xTandemInput[0]).index('dtaEntryUnqID')
    ppmCol     = list(xTandemInput[0]).index('massErrorPpm')
    dtaIDs     = [i[idCol] for i in xTandemInput[1:]]
    xtFullPpms = array([float(i[ppmCol]) for i in xTandemInput[1:]])
    indices    = [idToPpm[0].index(i) for i in dtaIDs]
    
    xtSysPpms  = array([idToPpm[1][i] for i in indices])
    xtResPpms  = xtFullPpms + xtSysPpms # yes. it is negative systematic error

    # now go through inputs like dtaInput
    # and report systematic errors given the IDs
    idCol      = list(dtaInput[0]).index('dtaEntryUnqID')
    dtaIDs     = [i[idCol] for i in dtaInput[1:]]
    indices    = [idToPpm[0].index(i) for i in dtaIDs]    
    dtaSysPpms = array([idToPpm[1][i] for i in indices])
    # -----------------------------------------------------------------

    # xtResPpms <- overfit proof if corresponding option was enabled
    return xtResPpms, dtaSysPpms
