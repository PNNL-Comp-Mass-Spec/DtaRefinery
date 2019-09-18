'''
This is memory error safe version of lowess.
Checks both, array from x!tandem and dta files
3rd ver
Jan 8, 2010
'''





from numpy import array, ceil, sort, transpose, clip, zeros, ones, median
from numpy import sum as summa
from numpy.linalg import solve
from numpy.linalg.linalg import LinAlgError
from copy import deepcopy


def lowess(x, y, X2, f=2./3., itr=3):
    # X2 are x values to estimate Y2 on
    
    x  = array(x,  'float32')
    y  = array(y,  'float32')
    X2 = array(X2, 'float32') 

    n = len(x) #total number of points
    r = int(ceil(f*n)) #the number of NN
    h = [sort(abs(x-x[i]))[r] for i in range(n)] #the bandwith in x, given NN for each point
    
    #111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111
    #figure out the chunk size safe for handling in the RAM
    chunkSize_1 = n #whole thing
    while True:
        try:
            test1 = [x[0:chunkSize_1]]-transpose([x]) #VLAD. Potential MemoryError
            test2 = [x[0:chunkSize_1]]-transpose([x]) #VLAD. Potential MemoryError
            test3 = [x[0:chunkSize_1]]-transpose([x]) #VLAD. Potential MemoryError
            test4 = [x[0:chunkSize_1]]-transpose([x]) #VLAD. Potential MemoryError
            test5 = [x[0:chunkSize_1]]-transpose([x]) #VLAD. Potential MemoryError
            test6 = [x[0:chunkSize_1]]-transpose([x]) #VLAD. Potential MemoryError
            test7 = [x[0:chunkSize_1]]-transpose([x]) #VLAD. Potential MemoryError
            test8 = [x[0:chunkSize_1]]-transpose([x]) #VLAD. Potential MemoryError
            break
        except MemoryError:
            chunkSize_1 = chunkSize_1/2 #split size into half
    try:
        del test1, test2, test3, test4, test5, test6, test7, test8
    except NameError:
        pass

    #chunk sizes, number, and left-overs
    numChunks_1     = n/chunkSize_1
    leftChunkSize_1 = n - numChunks_1*chunkSize_1

    #compute the indices
    chunkList_1 = [] #that list of tuples (start, end) how the big dataset is going to be split
    for i in range(numChunks_1):
        start = chunkSize_1 * i
        end   = chunkSize_1 * (i+1)
        chunkList_1.append(( start, end))
    if leftChunkSize_1 != 0:
        chunkList_1.append(( end, n))
    #111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111
    

    N2 = len(X2)
    H2 = [sort(abs(x-X2[i]))[r] for i in range(N2)] #the bandwith in x, given NN for each point

    #222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222
    #figure out the chunk size safe for handling in the RAM
    chunkSize = N2 #whole thing
    while True:
        try:
            test1 = [X2[0:chunkSize]]-transpose([x]) #VLAD. Potential MemoryError
            test2 = [X2[0:chunkSize]]-transpose([x]) #VLAD. Potential MemoryError
            test3 = [X2[0:chunkSize]]-transpose([x]) #VLAD. Potential MemoryError
            test4 = [X2[0:chunkSize]]-transpose([x]) #VLAD. Potential MemoryError
            test5 = [X2[0:chunkSize]]-transpose([x]) #VLAD. Potential MemoryError
            test6 = [X2[0:chunkSize]]-transpose([x]) #VLAD. Potential MemoryError
            test7 = [X2[0:chunkSize]]-transpose([x]) #VLAD. Potential MemoryError
            test8 = [X2[0:chunkSize]]-transpose([x]) #VLAD. Potential MemoryError
            break
        except (MemoryError, ValueError):
            chunkSize = chunkSize/2 #split size into half
    try:
        del test1, test2, test3, test4, test5, test6, test7, test8
    except NameError:
        pass
    
    #chunk sizes, number, and left-overs
    numChunks     = N2/chunkSize
    leftChunkSize = N2 - numChunks*chunkSize

    #compute the indices
    chunkList = [] #that list of tuples (start, end) how the big dataset is going to be split
    for i in range(numChunks):
        start = chunkSize * i
        end   = chunkSize * (i+1)
        chunkList.append(( start, end))
    if leftChunkSize != 0:
        chunkList.append(( end, N2))
    #222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222

    #---- Main Iteration Loop--------------
    yest = zeros(n,'d')
    delta = ones(n,'d') #weights characterizing how well y fits the trend
    Y2EST = zeros(N2,'d')
    Y2RETURN = deepcopy(Y2EST)

    for iteration in range(itr):
        try:      

            #1111111111111111111111111111111111111111111111111111111111111
            for chunk_1 in chunkList_1:
                d = [x[chunk_1[0]:chunk_1[1]]]-transpose([x]) 
                dh = abs(d)/h[chunk_1[0]:chunk_1[1]]
                del d
                w = clip(dh,0.0,1.0)
                del dh
                w = (1-w**3)**3

                #estimate for each point
                for i in range(n)[chunk_1[0]:chunk_1[1]]:
                    weights = delta * w[:,i-chunk_1[0]]
                    b = array([summa(weights*y), summa(weights*y*x)])
                    A = array([[summa(weights),   summa(weights*x)],
                             [summa(weights*x), summa(weights*x*x)]])
                    beta = solve(A,b) #Ax=b            
                    yest[i] = beta[0] + beta[1]*x[i]
                del weights, b, A
            #1111111111111111111111111111111111111111111111111111111111111


            #22222222222222222222222222222222222222222222222222222222222222
            # go though chunks if can not lift the entire NxM array
            for chunk in chunkList:
                D2 = [X2[chunk[0]:chunk[1]]]-transpose([x])
                DH2 = abs(D2)/H2[chunk[0]:chunk[1]]
                del D2
                W2 = clip(DH2,0.0,1.0)
                del DH2
                W2 = (1-W2**3)**3
        
                #estimate for each point
                for i in range(N2)[chunk[0]:chunk[1]]:
                    WEIGHTS2 = delta * W2[:,i-chunk[0]]
                    b = array([summa(WEIGHTS2*y), summa(WEIGHTS2*y*x)])
                    A = array([[summa(WEIGHTS2),   summa(WEIGHTS2*x)],
                             [summa(WEIGHTS2*x), summa(WEIGHTS2*x*x)]])
                    beta = solve(A,b) #Ax=b            
                    Y2EST[i] = beta[0] + beta[1]*X2[i]
                del W2, WEIGHTS2, b, A
            #22222222222222222222222222222222222222222222222222222222222222


            residuals = y-yest
            s = median(abs(residuals))
            delta = clip(residuals/(6*s),-1,1) #6*MAD
            delta = 1-delta*delta
            delta = delta*delta

        except LinAlgError:
            #print("    got the singularity problem")
            break
        else:
            #updates only if passes the loop without a problem
            Y2RETURN = deepcopy(Y2EST)
            
    return Y2RETURN







if __name__ == '__main__':

    from pprint import pprint as p
    import csv
    from pylab import plot, subplot, ylim, show
    import psyco
    from time import clock as tic
##    psyco.full()
   

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

    yEst = lowess(x, y, x, f=0.20, itr=1)

    tic_1 = tic()
    bY = lowess(x, y, b, f=0.20, itr=1)
    tic_2 = tic()
    print('done in %s seconds' % (tic_2-tic_1))

    subplot(211)
    plot(x,y,'bo')
    plot(x, yEst, 'g+')
    ylim((-30, +10))
    
    subplot(212)
    plot(x,y,'bo')
    plot(x, yEst, 'g+')
    plot(b,bY,'r,')
    ylim((-30, +10))
    show()

