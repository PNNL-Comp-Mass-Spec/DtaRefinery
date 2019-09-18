from aux_sys_err_prediction_module.additive.R_runmed_spline.my_R_runmed_spline_analysis import R_runmed_spline_MAIN
from aux_sys_err_prediction_module.additive.numpy_runmed_lowess.my_numpy_runmed_lowess_analysis import runmed_lowess_MAIN
from aux_sys_err_prediction_module.additive.numpy_runmed_spline.my_numpy_runmed_spline_analysis import runmed_spline_MAIN


from pprint import pprint as p



def do_1D_regression_analysis(ARG3, Controller):
    '''
    just picks the right regression approach and passes to it all the arguments
    '''

    #get the regression name        
    regressionToUseName = Controller.updatedSettings['refiningPars']['choices']['additiveRegression']

    #get the approach function
    # it is a little bit wierd, that function names are different
    # from approach names.
    # would be more convinient if they are the same
    # would get it by func.__name__
    regressionToUse = {'numpy_runmed_spline':   runmed_spline_MAIN,
                       'numpy_runmed_lowess':   runmed_lowess_MAIN,
                       'R_runmed_spline':       R_runmed_spline_MAIN}[regressionToUseName]


    res = regressionToUse(ARG3, Controller)
    return res
    
