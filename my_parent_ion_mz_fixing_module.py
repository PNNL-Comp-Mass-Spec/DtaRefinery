from aux_sys_err_prediction_module.my_systematic_error_prediction_module import do_predict_systematic_errors
from my_final_hist import do_plot_final_hist

import re

from numpy import log, array, median, zeros, arange, pi, exp


def do_fix_parent_ion_mz(Controller, xTandemInput, dtaEntries):
    xtPpmNew, dtaPpm = do_predict_systematic_errors(Controller, xTandemInput, dtaEntries)
    # actually xtPpmNew is used only for histogram
    # dtaPpm only for updating the dta file values
    # WARNING!! the order of ppm errors has to be the same as in INPUTS

    mzDtaIndex = list(dtaEntries[0]).index('mz')
    dtaOldMZs = array([float(x[mzDtaIndex]) for x in dtaEntries[1:]])
    dtaFixedMZs = dtaOldMZs * (1 + dtaPpm / 1e6)

    # TODO: make it positions idenpendent and depend only on name
    # dtaOldCore is dtaEntryUnqID, stringIndex, entryString
    dtaOldCore = [[y for y in x[0:3]] for x in dtaEntries[1:]]
    pttrnEntry = re.compile('(\d+.\d+)\s\d+\s+scan=(\d+)\scs=(\d+)')
    oldMH = array([float(pttrnEntry.match(i[2]).group(1)) for i in dtaOldCore])
    cs = array([int(pttrnEntry.match(i[2]).group(3)) for i in dtaOldCore])
    newMH = dtaFixedMZs * cs - (cs - 1) * 1.00727646688

    pttrnForFix = re.compile('\d+\.\d+(?P<rest>.*)')
    dtaFirstLines = [i[2] for i in dtaOldCore]
    dtaFirstLinesFixed = [pttrnForFix.sub(r'%s\g<rest>' % i[1], i[0]) \
                          for i in zip(dtaFirstLines, newMH)]

    dtaEntryUnqID = [i[0] for i in dtaOldCore]
    dtaIndexes = [i[1] for i in dtaOldCore]
    dtaNewCore = [list(i) for i in zip(dtaEntryUnqID, dtaIndexes, dtaFirstLinesFixed)]

    # compute means and stdevs before and after

    # PLOTTING FINAL HISTOGRAM AND SCATTERPLOTS
    isFinalPlots = {'True': True, 'False': False}[Controller.updatedSettings['plottingPars']['plot final scatterplots']]
    do_plot_final_hist(Controller, xTandemInput, xtPpmNew, isFinalPlots)

    return dtaNewCore
