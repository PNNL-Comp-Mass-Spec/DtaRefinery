from aux_sys_err_prediction_module.my_systematic_error_prediction_module\
     import do_predict_systematic_errors

from aux_sys_err_prediction_module.simple_shift.my_em_gfg_function import do_em_norm_n_fixed_norm
from pprint import pprint as p

import os.path
import re

from numpy import log, array, median, zeros, arange, pi, exp, vstack, savetxt, around, append
from pylab import plot, grid, axhline,\
                 ylim, show, subplot, clf,\
                 savefig, hist, xlabel, ylabel,\
                 title, text, xlim, subplots_adjust,\
                 savefig, gcf, figure

from matplotlib.font_manager import FontProperties



def dnorm(x, m, s):
    return (1/(s*(2*pi)**0.5))*exp(-(x-m)**2/(2*s**2))



def bothScatterPlots( par, xtPpmOld, xtPpmNew, lims, dim):

    # plot the OLD ones

    figure(num = None, figsize=(10, 5))#, dpi=80, facecolor='w', edgecolor='k')

    subplots_adjust(top=0.875, bottom=0.175, left = 0.1, right = 0.925, wspace = 0.1) 
    
    sbPlt = subplot(121)
    sbPlt.xaxis.major.formatter.set_powerlimits((-3,+3))
    plot( par, xtPpmOld, 'b.')
    sbPlt.set_title('original')
    grid()
    xlabel(dim)
    ylabel('mass error (ppm)')
    ylim(lims)
    
    # plot the NEW ones
    sbPlt = subplot(122)
    sbPlt.xaxis.major.formatter.set_powerlimits((-3,+3))
    plot( par, xtPpmNew, 'g.')
    sbPlt.set_title('refined')
    grid()
    xlabel(dim)
    sbPlt.set_yticklabels([])    
    ylim(lims)






def subHist(*args):

    subPlotInd, expDist, bins, lims, theorDist, mean, stdev, totalMAD, meanMAD, stdevMAD, title, yLim = args

    if title == 'original':
        fc = 'b'
    else:
        fc = 'g'
        
    sbPlt = subplot(subPlotInd)
    sbPlt.set_title(title)
    result = hist( expDist, fc=fc, bins=bins)
    xlabel('mass error (ppm)')
    plot(bins, theorDist, 'r--', linewidth=1.5)
    plot(bins, totalMAD,  'c--', linewidth=1.5)    
    grid()
    xlim(lims)
    pars = '      EM est.\nmean = %s\nstdev = %s' % (round(mean,2), round(stdev,2))
    text(0.66, 0.9, pars,\
         fontsize=10,\
         horizontalalignment='left',\
         verticalalignment='center',\
         transform = sbPlt.transAxes,\
         bbox = dict(facecolor='#EEEEEE',\
                     edgecolor='#EEEEEE',\
#                     width = 130,\
                     pad = 5,\
                     alpha=0.85))

    pars = '      Robust est.\nmean = %s\nstdev = %s' % (round(meanMAD,2), round(stdevMAD,2))
    text(0.66, 0.74, pars,\
         fontsize=10,\
         horizontalalignment='left',\
         verticalalignment='center',\
         transform = sbPlt.transAxes,\
         bbox = dict(facecolor='#EEEEEE',\
                     edgecolor='#EEEEEE',\
#                     width = 130,\
                     pad = 5,\
                     alpha=0.85))

    text(0.66, 0.945, '---',\
         color = 'red',\
         fontsize=16,\
         horizontalalignment='left',\
         verticalalignment='center',\
         transform = sbPlt.transAxes,\
         bbox = dict(facecolor='#EEEEEE',\
                     edgecolor='#EEEEEE',\
#                     width = 130,\
                     pad = 5,\
                     alpha=0.0))

    text(0.66, 0.785, '---',\
         color = 'cyan',\
         fontsize=16,\
         horizontalalignment='left',\
         verticalalignment='center',\
         transform = sbPlt.transAxes,\
         bbox = dict(facecolor='#EEEEEE',\
                     edgecolor='#EEEEEE',\
#                     width = 130,\
                     pad = 5,\
                     alpha=0.0))

    if title == 'refined':
        sbPlt.set_yticklabels([])
    else:
        ylabel('counts')

    if yLim is not None:
        sbPlt.set_ylim(yLim)

    # that adjusting the y axis of the histograms to the same scale
    # is backward
    # result[0] is bin count data 
    return sbPlt.get_ylim(), result[0]




def do_plot_final_hist( Controller, xTandemInput, xtPpmNew, isFinalPlots):

    lims     = Controller.updatedSettings['plottingPars']['plotting range, ppm']
    lims     = tuple([float(i) for i in lims.split(',')])
    binSize  = float(Controller.updatedSettings['plottingPars']['histogram bin size, ppm'])
    
    dSetName =  Controller.updatedSettings['spectra dataset']
    dirName  =  Controller.updatedSettings['spectra directory']
    pathName = os.path.join(dirName, dSetName)+'_HIST.png'


    ppmInd = list(xTandemInput[0]).index('massErrorPpm')
    xtPpmOld = array([float(i[ppmInd]) for i in xTandemInput[1:]])


    bins = arange(lims[0], lims[1]+binSize, binSize)

    if isFinalPlots:
        figure(num = None, figsize=(10, 5))
        subplots_adjust(top=0.875, bottom=0.175, left = 0.1, right = 0.925, wspace = 0.1)


    # some info in the bottom left corner
    fineprint = 'dataset: %s\ntotal number of identifications: %s\nbin size: %s ppm'\
                % (dSetName, len(xTandemInput), binSize)
    t = gcf().text(0.05, 0.075, fineprint,
                   horizontalalignment='left',
                   verticalalignment='top',
                   fontproperties=FontProperties(size=6))

    # go through NEW ppm error
    mean1, stdev1, portion1, mean2, stdev2 = do_em_norm_n_fixed_norm( xtPpmNew)
    dist1 = portion1*dnorm(bins,mean1,stdev1)
    dist2 = (1-portion1)*dnorm(bins,mean2,stdev2)
    total = binSize*len( xtPpmNew)*(dist1 + dist2)
    #
    meanMAD = median( xtPpmNew)
    stdevMAD = 1.4826 * median(abs( xtPpmNew - meanMAD))
    totalMAD = binSize*len( xtPpmNew) * dnorm( bins, meanMAD, stdevMAD)
    # plot histogram with NEW
    yLim = None
    statParsNew = dict( zip( [ 'Exp.Max.','Robust'],
                             [dict( zip( ['mean','stdev'],[mean1, stdev1])),
                               dict( zip( ['mean','stdev'],[meanMAD, stdevMAD]))]
                             )
                       )
    totalEMNew, totalMADNew = total, totalMAD
    if isFinalPlots:
        yLim, binCountNew = subHist(122, xtPpmNew, bins, lims, total, mean1, stdev1, totalMAD, meanMAD, stdevMAD, 'refined', yLim)

    # go through OLD ppm error
    mean1, stdev1, portion1, mean2, stdev2 = do_em_norm_n_fixed_norm( xtPpmOld)
    dist1 = portion1*dnorm(bins,mean1,stdev1)
    dist2 = (1-portion1)*dnorm(bins,mean2,stdev2)
    total = binSize*len( xtPpmOld)*(dist1 + dist2)
    #
    meanMAD = median( xtPpmOld)
    stdevMAD = 1.4826 * median(abs( xtPpmOld - meanMAD))
    totalMAD = binSize*len( xtPpmOld) * dnorm( bins, meanMAD, stdevMAD)
    # plot histogram with OLD
    statParsOri = dict( zip( [ 'Exp.Max.','Robust'],
                             [dict( zip( ['mean','stdev'],[mean1, stdev1])),
                               dict( zip( ['mean','stdev'],[meanMAD, stdevMAD]))]
                             )
                       )
    if isFinalPlots:
        totalEMOri, totalMADOri = total, totalMAD
        yLim, binCountOri = subHist(121, xtPpmOld, bins, lims, total, mean1, stdev1, totalMAD, meanMAD, stdevMAD,  'original', yLim)

    if isFinalPlots:
        savefig(str(pathName))
        clf()


    # KEEP GOING AND MAKE RESIDUAL ERROR
    # SCATTER PLOTS
    if isFinalPlots:
        dimensions = Controller.allDimensions
        for dim in dimensions:
            ind = list(xTandemInput[0]).index(dim)
            par = array([float(i[ind]) for i in xTandemInput[1:]])
            #
            # some info in the bottom left corner
            fineprint = 'dataset: %s'\
                        % (dSetName)
            t = gcf().text(0.05, 0.075, fineprint,
                           horizontalalignment='left',
                           verticalalignment='top',
                           fontproperties=FontProperties(size=6))
            #
            bothScatterPlots( par, xtPpmOld, xtPpmNew, lims, dim)
            #
            pathName = os.path.join(dirName, dSetName)+'_%s.png' % dim
            savefig(str(pathName))
            clf()
    
    # pass the statistics
    statPars = {}
    statPars['new'] = statParsNew
    statPars['ori'] = statParsOri
    Controller.statPars = statPars
    
    # save the histograms as text
    # bins - array
    # binCountNew - array
    # binCountOri - array
    # totalEMNew, totalMADNew 
    # totalEMOri, totalMADOri
    if isFinalPlots:
       # The binCountOri and binCountNew arrays are likely 1 item shorter than bins
       # The while loops correct for this
       
        while len(binCountOri) < len(bins):
            binCountOri = append(binCountOri, [0])

        while len(binCountNew) < len(bins):
            binCountNew = append(binCountNew, [0])
      
        data = vstack((bins, binCountOri, totalEMOri, totalMADOri, binCountNew, totalEMNew, totalMADNew)).T
        data = around(data,1)
        titles = ['MassErrorBin (ppm)', 'Original', 'OriginalFitEM', 'OriginalFitRobust', 
                                        'Refined',  'RefinedFitEM',  'RefinedFitRobust']
        data = vstack((titles, data))
        histTxtPath = os.path.join(dirName, dSetName)+'_HIST.txt'
        savetxt(histTxtPath, data, fmt='%s', delimiter='\t')
