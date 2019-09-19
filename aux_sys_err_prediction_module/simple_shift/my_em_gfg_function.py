"""
Expectation Maximization of Gaussian + Uniform Mixture model
based on em_gu_2b_as_function.py file
"""

import random as r
from numpy import random, concatenate,\
                  zeros, array, logical_not,\
                  pi, exp, log, arange
from numpy import sum as summa

def do_em_norm_n_fixed_norm(mix, numIter=30):

    def dnorm(x, m, s):
        return (1/(s*(2*pi)**0.5))*exp(-(x-m)**2/(2*s**2))

    hood = zeros(numIter,'d')

    #---Initial Guess-----------------------------------------------
    x = array([r.choice((True,False)) for i in range(len(mix))])

    mod1 = mix[x]
    mod2 = mix[logical_not(x)]

    mean1 = mod1.mean()
    stdev1 = mod1.std()
    
    portion1 = 0.5

    mean2 = mean1
    stdev2 = 50
    #---------------------------------------------------------------

    for itr in range(numIter):

        #---Expectation Step----------------------------------------
        resp = portion1*dnorm(mix,mean1,stdev1)/\
                      (portion1*dnorm(mix,mean1,stdev1)+(1-portion1)*dnorm(mix,mean2,stdev2))
        
        hood[itr] = summa(log((portion1*dnorm(mix,mean1,stdev1)+\
                            (1-portion1)*dnorm(mix,mean2,stdev2))))
        #-----------------------------------------------------------

        #---Maximization Step---------------------------------------
        mean1 = summa(resp*mix)/summa(resp)
        stdev1 = (summa(resp*((mix-mean1)**2))/summa(resp))**0.5
        portion1 = summa(resp)/len(mix)
        mean2 = mean1
        #-----------------------------------------------------------

    return mean1, stdev1, portion1, mean2, stdev2



##########################################################################
if __name__ == '__main__':

    from time import clock as c
    from pylab import hist, show, hold, ion, plot, xlim, draw, ioff, close
    
    #---make a mixed distribution------------------------------
    norm1 = random.normal(loc=0.0, scale= 1.0, size=1000)
    lim = 100
    unif2 = random.normal(loc=0.0, scale=50.0, size=3000)
    mix = concatenate((norm1,unif2))
    #----------------------------------------------------------

    t1 = c()
    mean1, stdev1, portion1 = do_em_nomr_n_unif(mix, 100)
    mean2 = mean1
    stdev2 = 50
    t2 = c()
    print('DONE in %s sec' % (t2-t1))

    #---Diagnostic Plot---------------------------------------------
    def dnorm(x, m, s):
        return (1/(s*(2*pi)**0.5))*exp(-(x-m)**2/(2*s**2))
    
    tracepoints = arange(-lim,+lim+1,1)
    dist1 = portion1*dnorm(tracepoints,mean1,stdev1)
    dist2 = (1-portion1)*dnorm(tracepoints,mean2,stdev2)
    total = len(mix)*(portion1*dnorm(tracepoints,mean1,stdev1)+\
                      (1-portion1)*dnorm(tracepoints,mean2,stdev2))

    bins = arange(-lim, +lim+1, 1)
    hist(mix, bins=bins)
    plot(tracepoints, total, 'r-', linewidth=2)
    xlim(-lim,+lim)
    show()
    #---------------------------------------------------------------

