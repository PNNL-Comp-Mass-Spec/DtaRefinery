from numpy import array, median


def runmed(x, NN):
    """
    x = array,
    k = extra number of NN from one side
    """
    if NN % 2 == 0:
        raise Exception("Error in runmed. Use odd NN")

    k = (NN + 1) / 2
    sm = x.copy()
    n = len(x)
    # first look, filling middle
    nachalo = k
    konec = n - k
    nabor = range(nachalo, konec)
    smMid = [median(x[(i - k):(i + k + 1)]) for i in nabor]
    sm[nabor] = array(smMid)
    # second loop to fill k-flanks, except 1 & n
    flangBegIndx = range(1, nachalo)
    smBeg = [median(x[0:i * 2 + 1]) for i in flangBegIndx]
    sm[flangBegIndx] = smBeg
    flangEndIndx = range(konec, n - 1)
    smEnd = [median(x[2 * i - n + 1:n]) for i in flangEndIndx]
    sm[flangEndIndx] = smEnd
    # filling 1 & n elements
    sm[0] = median([sm[0], sm[1], 3 * sm[1] - 2 * sm[2]])
    sm[n - 1] = median([sm[n - 1], sm[n - 2], 3 * sm[n - 2] - 2 * sm[n - 3]])
    return sm


if __name__ == '__main__':
    # ---TESTING---
    from random import uniform
    from pylab import plot, show, xlim, ylim
    from numpy import cos, arange

    RANGE = 100

    x = arange(0, RANGE / 10, 0.1)
    co = cos(x)
    no = array([uniform(0, 0.1) for i in range(RANGE)])
    cono = co + no

    res = runmed(cono, 1)

    plot(range(int(RANGE * 0.1 + 1), int(RANGE * 1.1 + 1)), cono, 'bo')
    xlim(0, RANGE * 1.2)
    ylim(-1.2, +2.2)
    plot(range(int(RANGE * 0.1 + 1), int(RANGE * 1.1 + 1)), res, 'rd')
    show()
