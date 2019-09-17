from my_R_runmed_spline_fit import R_runmed_smooth_spline
from numpy import random, array, median, where, zeros, average, arange, hstack
from scipy.interpolate import splev
from pylab import plot, show, subplot, savefig, clf, ylim
from pprint import pprint as p

from win32com.client import Dispatch


myName = 'R_runmed_spline'
useMAD = True #use median absolute deviations instead of sum of squared residues

#-----------------------------------------------------------------------
def R_runmed_spline_MAIN( ARG3, Controller):

    pars = Controller.updatedSettings['refiningPars']['regressionSettings'][myName]

    #ARG3
    x = ARG3[0][0]
    y = ARG3[0][1]

    sc=Dispatch("StatConnectorSrv.StatConnector")
    sc.Init("R")

    #get the best smoothing parameter
    bestSpar = R_runmed_spline_KCV_OPTIMIZATION(x, y, sc=sc, **pars)

    #get the prediction error for this smoothing parameter
    bestPredErr = R_runmed_spline_KCV_predErr(x, y, spar=bestSpar, sc=sc, **pars)
    
    #compare with original SSE
    #is fit successful?
    #return isSuccessfulFit, yFit, yEval, runMedData
    SSE = sum(y**2)
    MAD = 1.4826 * median(abs(y))
    if useMAD:
        SSE = MAD
    if bestPredErr < SSE:
        isSuccessfulFit = True
        #
        ppmArrs = [[] for i in range(len(ARG3))]
        for ind in range(len(ARG3)):
            x     = ARG3[ind][0]
            y     = ARG3[ind][1]
            xEval = ARG3[ind][2]
            #
            yFit, runMedData = R_runmed_smooth_spline(x, y, x, spar=bestSpar, sc=sc, **pars)
            yEval, runMedData = R_runmed_smooth_spline(x, y, xEval, spar=bestSpar, sc=sc, **pars)
            #
            ppmArrs[ind] = [yFit, yEval]
    else:
        isSuccessfulFit = False
        #
        ppmArrs = [[] for i in range(len(ARG3))]
        for ind in range(len(ARG3)):
            x     = ARG3[ind][0]
            y     = ARG3[ind][1]
            xEval = ARG3[ind][2]
            #
            yFit  = zeros(len(x),'d')
            yEval = zeros(len(xEval),'d')
            #
            ppmArrs[ind] = [yFit, yEval]

    sc.Close()

    return isSuccessfulFit, bestPredErr, ppmArrs
#-----------------------------------------------------------------------



#-----------------------------------------------------------------------
def R_runmed_spline_KCV_OPTIMIZATION(x, y, sc, **pars):

    sparRange     = array([float(i) for i in pars['spar range'].split(',')])
    sparStepsNum  = int(pars['spar steps number'])
    sparStep      = round((sparRange[1] - sparRange[0]) / sparStepsNum, 5)
    sparSet       = arange(sparRange[0],sparRange[1],sparStep)
    
    predErrSet = zeros(len(sparSet),'d')
    for i in range(len(sparSet)):
        predErr = R_runmed_spline_KCV_predErr( x, y, spar = sparSet[i], sc=sc, **pars)
        predErrSet[i] = predErr

##    p(zip(sparSet, predErrSet))
    spar = sparSet[predErrSet == min(predErrSet)][-1] #take the last one (smoothest) if there are few
##    print 'spar ', spar

    return spar
#-----------------------------------------------------------------------            

            
#-----------------------------------------------------------------------
def R_runmed_spline_KCV_predErr(x, y, **kwargs):
    """
    just returns the prediction error
    """
    K = int(kwargs['K'])
    #--Related to K-fold CV---------------------------
    L = len(x)
    N = L/K ##min length of pieces
    W = range(L)
    Z = range(1,K+1)
    Z = [N for j in Z]
    R = L%K
    Z[0:R] = [j+1 for j in Z[0:R]] # length of the pieces
    random.shuffle(W)
    ind = 0
    predErr = 0
    allResiduals = array([])
    SSE = sum(y**2) #VLAD. Why do I need this???
    #---running through K training/testings-------------
    for j in Z:
        
        #---making training/testing subsets-------------
        test = W[ind:ind+j]
        test.sort()
        train = W[0:ind] + W[ind+j:]
        train.sort()
        ind += j
        #-----------------------------------------------

        #---fit runmed_spline here----------------------
        yFit, runMed = R_runmed_smooth_spline(x[train], y[train], x[test], **kwargs)
        residualsTest = y[test] - yFit
        predErr += sum(residualsTest**2)
        allResiduals = hstack( ( allResiduals,residualsTest))
        #-----------------------------------------------

    if useMAD:
        predErr = 1.4826 * median(abs( allResiduals))

    return predErr
#-----------------------------------------------------------------------










if __name__ == '__main__':
    from numpy import linspace, cos, lexsort, zeros, sin
    from pylab import plot, show, subplot, savefig, clf, ylim
    from pprint import pprint as p
    from time import clock as c
    
    x1 = linspace(0,30,300)
##    y1 = cos(x1)
##    y1 = zeros(len(x1),'d') #nice test
    y1 = x1*0.03
    
    y1 += random.normal(scale=0.2, size=y1.shape)
    ind = lexsort(keys=(y1,x1))
    x1 = x1[ind]
    y1 = y1[ind]

    t1 = c()
    isSuccessfulFit, yFit, yEval, runMedData, predErr = \
                     R_runmed_spline_MAIN(x1,y1,x1, runMedSpan=0.01, K=10, sparRange=[0.6,1.1,0.1])
    t2 = c()
    print 'done in %s seconds' % (t2-t1)


    subplot(211)
    plot(x1,y1,'bo')
    plot(runMedData[0], runMedData[1], 'y^')
    plot(x1,yEval,'r+-')
    ylim([-1.5, +1.5])
    subplot(212)
    plot(x1,y1-yEval,'go')
    ylim([-1.5, +1.5])
    show()

