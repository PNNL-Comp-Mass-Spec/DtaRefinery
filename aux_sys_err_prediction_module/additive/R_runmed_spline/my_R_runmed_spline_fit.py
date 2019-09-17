from numpy import array, ceil
from time import clock as c

def R_runmed_smooth_spline(x, y, xFit, **kwargs):

    sc =            kwargs['sc']
    spar =          float(kwargs['spar'])
    runMedSpan =    float(kwargs['runMedSpan'])
   
    NN = int(ceil(float(len(x))*runMedSpan))
    if NN%2 == 0:
        NN += 1

    sc.SetSymbol( 'x', x)
    sc.SetSymbol( 'y', y)
    sc.SetSymbol( 'xFit', xFit)    

    sc.EvaluateNoReturn( 'ord <- order( x)')
    sc.EvaluateNoReturn( 'xRmd <- x[ord]')
    sc.EvaluateNoReturn( 'yRmd <- runmed( y[ord], %s)' % NN)

##    t1 = c()
    sc.EvaluateNoReturn( 'spl.model <- smooth.spline( x[ord], yRmd, spar=%s)' % spar)
    #sc.EvaluateNoReturn( 'splData <- predict( spl.model, data.frame( x))')
    #sc.EvaluateNoReturn( 'xSpl <- splData$x[,1]')
    #sc.EvaluateNoReturn( 'ySpl <- splData$y[,1]')
    
    sc.EvaluateNoReturn( 'splData <- predict( spl.model, data.frame( xFit))')
##    t2 = c()
    sc.EvaluateNoReturn( 'yFit <- splData$y[,1]')

    xRmd = array( sc.GetSymbol( 'xRmd'))
    yRmd = array( sc.GetSymbol( 'yRmd'))
    #xSpl = array( sc.GetSymbol( 'xSpl'))
    #ySpl = array( sc.GetSymbol( 'ySpl'))
    yFit = array( sc.GetSymbol( 'yFit'))

    #sc.Close()

##    print 'R_runmed_smooth_spline done in %s seconds' % (t2-t1)

    return yFit, (xRmd, yRmd)





if __name__ == '__main__':

    from pylab import plot, show, xlim, ylim, subplot
    from pprint import pprint as p
    import csv
    from numpy import array
    from time import clock as c
    from win32com.client import Dispatch

    sc=Dispatch("StatConnectorSrv.StatConnector")
    sc.Init("R")

    
    #---READING FILES----------------------------------
    xTandemInputFH    = open('xt_log_merg.txt','r')
    csv_reader = csv.reader(xTandemInputFH, delimiter='\t')
    xTandemInput = [tuple(x) for x in csv_reader]
    xTandemInputFH.close()

    dtaEntriesFH      = open('dta_entries.txt','r')
    csv_reader = csv.reader(dtaEntriesFH, delimiter='\t')
    dtaEntries = [x for x in csv_reader]
    dtaEntriesFH.close()
    #--------------------------------------------------

    a = array([[float(y) for y in x] for x in xTandemInput[1:]])
    aColumns = xTandemInput[0]
    #('parent_scan', 'mz', 'intensity', 'ppm')

    b = array([float(x[3]) for x in dtaEntries[1:]])

    x = a[:,0]
    y = a[:,3]

    tic_1 = c()
    #spar range 0.6 .. 1.2
    yFit, runMed = R_runmed_smooth_spline(x,y,x,runMedSpan=0.1,spar=0.6,sc=sc)
    tic_2 = c()
    print 'done in %s seconds' % (tic_2-tic_1)

    sc.Close()

    plot(x,y,'bo')
    plot(runMed[0],runMed[1],'y^')
    plot(x,yFit,'r+')
    ylim((-30, +30))
    show()


