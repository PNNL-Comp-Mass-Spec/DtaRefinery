from aux_sys_err_prediction_module.additive.numpy_runmed_spline.my_runmed_spline import runmed_spline_model
from numpy import random, array, median, zeros, average, hstack
import math

myName = 'numpy_runmed_spline'
useMAD = True  # Use median absolute deviation instead of sum of squared residuals


# def runmed_spline_MAIN(x, y, xEval, **params):
def runmed_spline_MAIN(ARG3, Controller):
    params = Controller.updatedSettings['refiningPars']['regressionSettings'][myName]

    # ARG3
    x = ARG3[0][0]
    y = ARG3[0][1]

    # get the best multiplier
    bestMultiplier = runmed_spline_KCV_BISEC(x, y, **params)
    # get the prediction error for this multiplier
    bestPredErr = runmed_spline_KCV_predErr(x, y, multiplier=bestMultiplier, **params)

    # compare with original SSE
    # is fit successful?
    # return isSuccessfulFit, yFit, yEval, runMedData
    SSE = sum(y ** 2)
    MAD = 1.4826 * median(abs(y))
    if useMAD:
        SSE = MAD
    if bestPredErr < SSE:
        isSuccessfulFit = True
        #
        ppmArrs = [[] for i in range(len(ARG3))]
        for ind in range(len(ARG3)):
            x = ARG3[ind][0]
            y = ARG3[ind][1]
            xEval = ARG3[ind][2]
            #
            yFit, runMedData = runmed_spline_model(x, y, x, multiplier=bestMultiplier, **params)
            yEval, runMedData = runmed_spline_model(x, y, xEval, multiplier=bestMultiplier, **params)
            #
            if yFit[0] < 100:
                ppmArrs[ind] = [yFit, yEval]

    else:
        isSuccessfulFit = False
        #
        ppmArrs = [[] for i in range(len(ARG3))]
        for ind in range(len(ARG3)):
            x = ARG3[ind][0]
            y = ARG3[ind][1]
            xEval = ARG3[ind][2]
            #
            yFit = zeros(len(x), 'd')
            yEval = zeros(len(xEval), 'd')
            #
            ppmArrs[ind] = [yFit, yEval]

    return isSuccessfulFit, bestPredErr, ppmArrs


# -----------------------------------------------------------------------


# -----------------------------------------------------------------------
def runmed_spline_KCV_BISEC(x, y, **params):
    intvl = array([float(i) for i in params['sse smooth log10 range'].split(',')])
    for step in range(int(params['bisections'])):

        # split the intervals
        midPoint = average(intvl)
        point_lo = 10 ** average([intvl[0], midPoint])
        point_up = 10 ** average([intvl[1], midPoint])

        # do fit for both inteval midpoints
        predErr_lo = runmed_spline_KCV_predErr(x, y, multiplier=point_lo, **params)
        predErr_up = runmed_spline_KCV_predErr(x, y, multiplier=point_up, **params)

        if predErr_lo > predErr_up:
            intvl[0] = average(intvl)
        else:
            intvl[1] = average(intvl)

    multiplier = 10 ** average(intvl)
    ##    multiplier = 10**intvl[1] #conserved option

    return multiplier


# -----------------------------------------------------------------------


# -----------------------------------------------------------------------
def runmed_spline_KCV_predErr(x, y, **kwargs):
    """
    just returns the prediction error
    """
    K = int(kwargs['K'])
    # --Related to K-fold CV---------------------------
    L = len(x)
    N = L / K  ##min length of pieces
    W = list(range(L))
    Z = list(range(1, K + 1))
    Z = [N for j in Z]
    R = L % K
    Z[0:R] = [j + 1 for j in Z[0:R]]  # length of the pieces
    random.shuffle(W)
    ind = 0
    predErr = 0
    allResiduals = array([])
    SSE = sum(y ** 2)  # VLAD. Why do I need this???
    # ---running through K training/testings-------------
    for val in Z:
        j = math.floor(val)

        # ---making training/testing subsets-------------
        test = W[ind:ind + j]
        test.sort()
        train = W[0:ind] + W[ind + j:]
        train.sort()
        ind += j
        # -----------------------------------------------

        # ---fit runmed_spline here----------------------
        yFit, runMed = runmed_spline_model(x[train], y[train], x[test], **kwargs)
        if yFit[0] < 100:
            residualsTest = y[test] - yFit
            predErr += sum(residualsTest ** 2)
            allResiduals = hstack((allResiduals, residualsTest))

        # -----------------------------------------------

    if useMAD:
        predErr = 1.4826 * median(abs(allResiduals))

    return predErr


# -----------------------------------------------------------------------


if __name__ == '__main__':
    from numpy import linspace, cos, lexsort, zeros, sin
    from pylab import plot, show, subplot, savefig, clf, ylim
    from pprint import pprint as p
    from time import clock as c

    x1 = linspace(0, 30, 300)
    y1 = cos(x1)
    ##    y1 = zeros(len(x1),'d') #nice test
    ##    y1 = x1*0.03

    y1 += random.normal(scale=0.2, size=y1.shape)
    ind = lexsort(keys=(y1, x1))
    x1 = x1[ind]
    y1 = y1[ind]

    t1 = c()
    isSuccessfulFit, yFit, yEval, runMedData, predErr = \
        runmed_spline_MAIN(x1, y1, x1, runMedSpan=0.01, K=10, bisections=10, adj=0)
    t2 = c()
    print('done ins %s seconds' % (t2 - t1))

    subplot(211)
    plot(x1, y1, 'bo')
    plot(runMedData[0], runMedData[1], 'y^')
    plot(x1, yEval, 'r+-')
    ylim([-1.5, +1.5])
    subplot(212)
    plot(x1, y1 - yEval, 'go')
    ylim([-1.5, +1.5])
    show()
