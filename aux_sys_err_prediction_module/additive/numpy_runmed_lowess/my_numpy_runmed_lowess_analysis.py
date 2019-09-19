from aux_sys_err_prediction_module.additive.numpy_runmed_lowess.my_runmed_lowess import runmed_lowess_model
from numpy import random, array, median, where, zeros, average, hstack
from scipy.interpolate import splev
import time
import math

from pylab import plot, show, subplot, savefig, clf, ylim

myName = 'numpy_runmed_lowess'
useMAD = True #use median absolute deviation instead for sum of squared residuals for prediction error estimation

#-----------------------------------------------------------------------
def runmed_lowess_MAIN(ARG3, Controller):

    params = Controller.updatedSettings['refiningPars']['regressionSettings'][myName]

    #ARG3
    x = ARG3[0][0]
    y = ARG3[0][1]

    #get the prediction error
    predErr = runmed_lowess_KCV_predErr(x, y, **params)
    
    #compare with original SSE
    #is fit successful?
    #return isSuccessfulFit, yFit, yEval, runMedData
    SSE = sum(y**2)
    MAD = 1.4826 * median(abs(y))
    #just substituted sum of squared errors with median absolute error
    if useMAD:
        SSE = MAD #VLAD. band-aid fix
    if predErr < SSE: #VLAD. may be no need to check that two times???
        isSuccessfulFit = True
        #
        ppmArrs = [[] for i in range(len(ARG3))]
        for ind in range(len(ARG3)):
            x     = ARG3[ind][0]
            y     = ARG3[ind][1]
            xEval = ARG3[ind][2]
            #
            yFit,  runMedData = runmed_lowess_model(x, y, x,     **params)
            yEval, runMedData = runmed_lowess_model(x, y, xEval, **params)
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

    return isSuccessfulFit, predErr, ppmArrs
#-----------------------------------------------------------------------



#-----------------------------------------------------------------------
def runmed_lowess_KCV_predErr(x, y, **params):
    """
    just returns the prediction error
    """
    K = int(params['K'])
    #--Related to K-fold CV---------------------------
    L = len(x)
    N = L/K ##min length of pieces
    W = [i for i in range(L)]
        
    Z = range(1,K+1)
    Z = [N for j in Z]
    R = L%K
    Z[0:R] = [j+1 for j in Z[0:R]] # length of the pieces
    random.shuffle(W)
    ind = 0
    predErr = 0
    allResiduals = array([])
    SSE = sum(y**2)
    MAD = median(abs(y))
    SSE = MAD #same fix as above. VLAD
    #---running through K training/testings-------------
    for j in Z:
        
        jInt = math.floor(j)
        
        #---making training/testing subsets-------------
        test = W[ind:ind+jInt]
        test.sort()
        train = W[0:ind] + W[ind+jInt:]
        train.sort()
        ind += jInt
        #-----------------------------------------------

        #---fit runmed_spline here----------------------
        yFit, runMed = runmed_lowess_model(x[train], y[train], x[test], **params)
        residualsTest = y[test] - yFit
        predErr += sum(residualsTest**2)
        allResiduals = hstack( ( allResiduals, residualsTest))
        #-----------------------------------------------

    if useMAD:
        predErr = 1.4826 * median(abs(allResiduals)) # just overwrites the one based on sum of squared residuals

    return predErr
#-----------------------------------------------------------------------










if __name__ == '__main__':
    from numpy import linspace, cos, lexsort, zeros, sin
    from pylab import plot, show, subplot, savefig, clf, ylim
    from pprint import pprint as p
    
    x1 = linspace(0,30,300)
    y1 = cos(x1)
##    y1 = zeros(len(x1),'d') #nice test
##    y1 = x1*0.03
    
    y1 += random.normal(scale=0.2, size=y1.shape)
    ind = lexsort(keys=(y1,x1))
    x1 = x1[ind]
    y1 = y1[ind]

    isSuccessfulFit, yFit, yEval, runMedData, predErr = \
                     runmed_lowess_MAIN(x1,y1,x1, K=10, runMedSpan=0.01,  f=0.1, itr=3)


    subplot(211)
    plot(x1,y1,'bo')
    plot(runMedData[0], runMedData[1], 'y^')
    plot(x1,yEval,'r+-')
    ylim([-1.5, +1.5])
    subplot(212)
    plot(x1,y1-yEval,'go')
    ylim([-1.5, +1.5])
    show()

