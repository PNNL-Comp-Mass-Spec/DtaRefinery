"""
This is memory error safe version of lowess.
Checks both, array from x!tandem and dta files
3rd ver
Jan 8, 2010
"""

from numpy import array, ceil, sort, transpose, clip, zeros, ones, median
from numpy import sum as summa
from numpy.linalg import solve
from numpy.linalg.linalg import LinAlgError
from copy import deepcopy
import math


def lowess(x, y, X2, f=2. / 3., itr=3):
    # X2 are x values to estimate Y2 on

    # Uncomment to show the first 101 values of x, y, and X2
    '''   
    print('\n\n\n Debugging lowess')
    print('Values for x')
    
    for i in list(x)[:101]:
        print(i,end=',',flush=True)

    print('\n\nValues for y')
    for i in list(y)[:101]:
        print(i,end=',',flush=True)

    print('\n\nValues for X2')
    for i in list(X2)[:101]:
        print(i,end=',',flush=True)
    
    print ('\n')
    '''

    x = array(x, 'float32')
    y = array(y, 'float32')
    X2 = array(X2, 'float32')

    n = len(x)  # total number of points
    r = int(ceil(f * n))  # the number of NN
    h = [sort(abs(x - x[i]))[r] for i in range(n)]  # the bandwith in x, given NN for each point

    # 111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111
    # figure out the chunk size safe for handling in the RAM
    chunkSize_1 = n  # whole thing
    attempt = 0
    while True:
        if attempt >= 8:
            break

        try:
            test1 = [x[0:chunkSize_1]] - transpose([x])  # VLAD. Potential MemoryError
            test2 = [x[0:chunkSize_1]] - transpose([x])  # VLAD. Potential MemoryError
            test3 = [x[0:chunkSize_1]] - transpose([x])  # VLAD. Potential MemoryError
            test4 = [x[0:chunkSize_1]] - transpose([x])  # VLAD. Potential MemoryError
            test5 = [x[0:chunkSize_1]] - transpose([x])  # VLAD. Potential MemoryError
            test6 = [x[0:chunkSize_1]] - transpose([x])  # VLAD. Potential MemoryError
            test7 = [x[0:chunkSize_1]] - transpose([x])  # VLAD. Potential MemoryError
            test8 = [x[0:chunkSize_1]] - transpose([x])  # VLAD. Potential MemoryError
            break
        except MemoryError:
            chunkSize_1 = int(chunkSize_1 / 2)  # split size into half
            attempt += 1
    try:
        del test1, test2, test3, test4, test5, test6, test7, test8
    except NameError:
        pass

    # chunk sizes, number, and left-overs
    numChunks_1 = math.floor(n / chunkSize_1)
    leftChunkSize_1 = n - numChunks_1 * chunkSize_1

    # compute the indices
    chunkList_1 = []  # that list of tuples (start, end) how the big dataset is going to be split
    for i in range(numChunks_1):
        start = chunkSize_1 * i
        end = chunkSize_1 * (i + 1)
        chunkList_1.append((start, end))
    if leftChunkSize_1 != 0:
        chunkList_1.append((end, n))
    # 111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111

    N2 = len(X2)
    H2 = [sort(abs(x - X2[i]))[r] for i in range(N2)]  # the bandwith in x, given NN for each point

    # 222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222
    # figure out the chunk size safe for handling in the RAM
    chunkSize = N2  # whole thing
    while True:
        try:
            test1 = [X2[0:chunkSize]] - transpose([x])  # VLAD. Potential MemoryError
            test2 = [X2[0:chunkSize]] - transpose([x])  # VLAD. Potential MemoryError
            test3 = [X2[0:chunkSize]] - transpose([x])  # VLAD. Potential MemoryError
            test4 = [X2[0:chunkSize]] - transpose([x])  # VLAD. Potential MemoryError
            test5 = [X2[0:chunkSize]] - transpose([x])  # VLAD. Potential MemoryError
            test6 = [X2[0:chunkSize]] - transpose([x])  # VLAD. Potential MemoryError
            test7 = [X2[0:chunkSize]] - transpose([x])  # VLAD. Potential MemoryError
            test8 = [X2[0:chunkSize]] - transpose([x])  # VLAD. Potential MemoryError
            break
        except (MemoryError, ValueError):
            chunkSize = chunkSize / 2  # split size into half
    try:
        del test1, test2, test3, test4, test5, test6, test7, test8
    except NameError:
        pass

    # chunk sizes, number, and left-overs
    numChunks = math.floor(N2 / chunkSize)
    leftChunkSize = N2 - numChunks * chunkSize

    # compute the indices
    chunkList = []  # that list of tuples (start, end) how the big dataset is going to be split
    for i in range(numChunks):
        start = chunkSize * i
        end = chunkSize * (i + 1)
        chunkList.append((start, end))
    if leftChunkSize != 0:
        chunkList.append((end, N2))
    # 222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222

    # ---- Main Iteration Loop--------------
    yest = zeros(n, 'd')
    delta = ones(n, 'd')  # weights characterizing how well y fits the trend
    Y2EST = zeros(N2, 'd')
    Y2RETURN = deepcopy(Y2EST)

    for iteration in range(itr):
        try:

            # 1111111111111111111111111111111111111111111111111111111111111
            for chunk_1 in chunkList_1:
                d = [x[chunk_1[0]:chunk_1[1]]] - transpose([x])
                dh = abs(d) / h[chunk_1[0]:chunk_1[1]]
                del d
                w = clip(dh, 0.0, 1.0)
                del dh
                w = (1 - w ** 3) ** 3

                # estimate for each point
                for i in range(n)[chunk_1[0]:chunk_1[1]]:
                    weights = delta * w[:, i - chunk_1[0]]
                    b = array([summa(weights * y), summa(weights * y * x)])
                    A = array([[summa(weights), summa(weights * x)],
                               [summa(weights * x), summa(weights * x * x)]])
                    beta = solve(A, b)  # Ax=b
                    yest[i] = beta[0] + beta[1] * x[i]
                del weights, b, A
            # 1111111111111111111111111111111111111111111111111111111111111

            # 22222222222222222222222222222222222222222222222222222222222222
            # go though chunks if can not lift the entire NxM array
            for chunk in chunkList:
                D2 = [X2[chunk[0]:chunk[1]]] - transpose([x])
                DH2 = abs(D2) / H2[chunk[0]:chunk[1]]
                del D2
                W2 = clip(DH2, 0.0, 1.0)
                del DH2
                W2 = (1 - W2 ** 3) ** 3

                # estimate for each point
                for i in range(N2)[chunk[0]:chunk[1]]:
                    WEIGHTS2 = delta * W2[:, i - chunk[0]]
                    b = array([summa(WEIGHTS2 * y), summa(WEIGHTS2 * y * x)])
                    A = array([[summa(WEIGHTS2), summa(WEIGHTS2 * x)],
                               [summa(WEIGHTS2 * x), summa(WEIGHTS2 * x * x)]])
                    beta = solve(A, b)  # Ax=b
                    Y2EST[i] = beta[0] + beta[1] * X2[i]
                del W2, WEIGHTS2, b, A
            # 22222222222222222222222222222222222222222222222222222222222222

            residuals = y - yest
            s = median(abs(residuals))
            delta = clip(residuals / (6 * s), -1, 1)  # 6*MAD
            delta = 1 - delta * delta
            delta = delta * delta

        except LinAlgError:
            # print("    got the singularity problem")
            break
        else:
            # updates only if passes the loop without a problem
            Y2RETURN = deepcopy(Y2EST)

    return Y2RETURN


if __name__ == '__main__':
    from pprint import pprint as p
    import csv
    from pylab import plot, subplot, ylim, show
    from time import clock as tic

    x = [215.0, 530.0, 531.0, 577.0, 582.0, 591.0, 592.0, 594.0, 669.0, 687.0, 734.0, 794.0, 801.0, 887.0, 982.0,
         1003.0, 1017.0, 1091.0, 1140.0, 1143.0, 1205.0, 1211.0, 1220.0, 1221.0, 1222.0, 1229.0, 1262.0, 1332.0, 1392.0,
         1428.0, 1435.0, 1479.0, 1481.0, 1503.0, 1504.0, 1507.0, 1522.0, 1540.0, 1547.0, 1555.0, 1556.0, 1564.0, 1588.0,
         1617.0, 1659.0, 1680.0, 1686.0, 1689.0, 1696.0, 1727.0, 1729.0, 1759.0, 1766.0, 1771.0, 1777.0, 1780.0, 1783.0,
         1820.0, 1827.0, 1852.0, 1869.0, 1886.0, 1894.0, 1901.0, 1918.0, 1920.0, 1931.0, 1938.0, 1996.0, 2020.0, 2021.0,
         2024.0, 2051.0, 2054.0, 2058.0, 2074.0, 2085.0, 2087.0, 2149.0, 2166.0, 2171.0, 2174.0, 2195.0, 2206.0, 2217.0,
         2228.0, 2238.0, 2250.0, 2255.0, 2265.0, 2289.0, 2291.0, 2309.0, 2367.0, 2381.0, 2402.0, 2421.0, 2441.0, 2446.0,
         2448.0, 2497.0]
    y = [0.5497521895637796, 0.5497521895637796, 0.713149232380396, 1.4423295778699594, 1.4423295778699594,
         1.4423295778699594, 0.713149232380396, 0.713149232380396, 0.877591085299529, 0.9789298579447958,
         0.9789298579447958, 0.9730243568437902, 0.9730243568437902, 0.9730243568437902, 0.9730243568437902,
         0.9730243568437902, 0.877591085299529, 0.877591085299529, 0.802007619794093, 0.7266473524205377,
         0.7190606204711997, 0.713149232380396, 0.713149232380396, 0.713149232380396, 0.6657905033816989,
         0.5589167001415871, 0.5589167001415871, 0.5899141882652706, 0.5589167001415871, 0.5589167001415871,
         0.5589167001415871, 0.5589167001415871, 0.5497521895637796, 0.5497521895637796, 0.5589167001415871,
         0.5497521895637796, 0.5497521895637796, 0.5497521895637796, 0.5589167001415871, 0.5696596444630995,
         0.5899141882652706, 0.5899141882652706, 0.5696596444630995, 0.5899141882652706, 0.6515522409162253,
         0.6515522409162253, 0.5899141882652706, 0.5696596444630995, 0.5589167001415871, 0.5497521895637796,
         0.5425228086755984, 0.5425228086755984, 0.5131636214873316, 0.5092370850176545, 0.5063845278306338,
         0.48880046613695494, 0.37478117258672683, 0.37478117258672683, 0.35699212257247714, 0.2882512857296859,
         0.27122430700459943, 0.27122430700459943, 0.269336827792158, 0.2087886830974931, 0.1651408702088103,
         0.11629056233673879, 0.11629056233673879, 0.11629056233673879, 0.11629056233673879, 0.10820183067892264,
         0.10071458827357527, 0.07982311035357581, 0.07982311035357581, 0.07150765549813476, 0.07150765549813476,
         0.0518160789730292, 0.050529251087801486, 0.04835630407698066, 0.04835630407698066, 0.050529251087801486,
         0.04835630407698066, 0.036457495885759195, 0.032888515016973985, 0.032888515016973985, 0.032888515016973985,
         0.032888515016973985, 0.032888515016973985, 0.026680773242979572, 0.026680773242979572, 0.032888515016973985,
         0.026680773242979572, 0.026680773242979572, -0.025916723670095565, 0.026680773242979572, -0.025916723670095565,
         0.026680773242979572, -0.025916723670095565, -0.025916723670095565, -0.06244783799579745, -0.06244783799579745,
         -0.06244783799579745]
    X2 = [2455.0, 3613.0, 8993.0, 4070.0, 10098.0, 6233.0, 3051.0, 5534.0, 5651.0, 8067.0, 10715.0, 4483.0, 9809.0,
          9969.0, 10181.0, 10449.0, 8829.0, 8877.0, 6992.0, 589.0, 5717.0, 7382.0, 10479.0, 1724.0, 9768.0, 3691.0,
          4564.0, 8765.0, 6069.0, 6970.0, 7476.0, 3886.0, 3185.0, 10733.0, 8369.0, 8766.0, 9318.0, 8694.0, 5657.0,
          5489.0, 3481.0, 7441.0, 9754.0, 8934.0, 2731.0, 9684.0, 9761.0, 5114.0, 4461.0, 3364.0, 6386.0, 6310.0,
          5928.0, 10411.0, 1210.0, 5264.0, 5691.0, 4606.0, 3880.0, 1541.0, 5679.0, 2337.0, 7588.0, 3340.0, 6932.0,
          5509.0, 8585.0, 10819.0, 8604.0, 7189.0, 7197.0, 6306.0, 5158.0, 9923.0, 5163.0, 5225.0, 2910.0, 2528.0,
          3865.0, 4756.0, 7710.0, 2539.0, 7429.0, 6318.0, 3135.0, 3832.0, 7805.0, 10638.0, 10621.0, 3916.0, 3787.0,
          7580.0, 5786.0, 3013.0, 10442.0, 2335.0, 8672.0, 10609.0, 5324.0, 8648.0, 9311.0]

    yEst = lowess(x, y, X2, f=0.20, itr=1)

    subplot(211)
    plot(x, y, 'bo')
    plot(x, yEst, 'g+')
    ylim((-30, +10))

    show()

    '''
    # Test using X!Tandem results
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
    '''
