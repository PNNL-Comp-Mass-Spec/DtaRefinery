import wx
import copy


# this one called first
class CorrectionParsMenu(wx.Menu):
    def __init__(self, parent):
        wx.Menu.__init__(self)

        self.mainFrame = parent

        # the class holds the dictionary with params in
        self.updatedSettings = copy.deepcopy( self.mainFrame.controller.defaultSettings)

        # set the menu
        addRegSubmenu = wx.Menu()
        self.addRegSubmenu_SseSplineItem        = addRegSubmenu.AppendCheckItem(-1, '&MSE restricted spline')
        self.addRegSubmenu_PenSecDerSplineItem  = addRegSubmenu.AppendCheckItem(-1, '&spline with penalized second derivative')
        self.addRegSubmenu_LowessItem           = addRegSubmenu.AppendCheckItem(-1, '&lowess')
        self.AppendMenu(-1, '&Additive Regressions', addRegSubmenu)

        simpleShiftSubmenu = wx.Menu()
        self.simpleShiftSubmenu_MedianItem   = simpleShiftSubmenu.AppendCheckItem(-1, 'shift by mean est. as &median')
        self.simpleShiftSubmenu_EmItem       = simpleShiftSubmenu.AppendCheckItem(-1, 'shift by mean est. using &EM')
        self.AppendMenu(-1, '&Simple Shift', simpleShiftSubmenu)

        bypassRefiningSubmenu = wx.Menu()
        self.bypassRefiningSubmenu_Item = bypassRefiningSubmenu.AppendCheckItem(-1, '&bypass refining')
        self.AppendMenu(-1, '&Bypass Refining', bypassRefiningSubmenu)

        self.AppendSeparator()

        restoreDefaultsItem = self.Append(-1, '&Resore Defaults',
                                          'Restore Default Settings')

        # add the bindings to the menu items
        parent.Bind(wx.EVT_MENU, self.OnAddRegSubmenu_SseSpline,
                    self.addRegSubmenu_SseSplineItem)
        
        parent.Bind(wx.EVT_MENU, self.OnAddRegSubmenu_PenSecDerSpline,
                    self.addRegSubmenu_PenSecDerSplineItem)
        
        parent.Bind(wx.EVT_MENU, self.OnAddRegSubmenu_Lowess,
                    self.addRegSubmenu_LowessItem)
        #
        parent.Bind(wx.EVT_MENU, self.OnSimpleShiftSubmenu_Median,
                    self.simpleShiftSubmenu_MedianItem)

        parent.Bind(wx.EVT_MENU, self.OnSimpleShiftSubmenu_EM,
                    self.simpleShiftSubmenu_EmItem)
        #
        parent.Bind(wx.EVT_MENU, self.OnBypassRefiningSubmenu,
                    self.bypassRefiningSubmenu_Item)
        #
        parent.Bind(wx.EVT_MENU, self.OnRestoreDefaults,
                    restoreDefaultsItem)
        #
        # self explanatory
        self.refreshTheCheckPoints()
        
        
    def refreshTheCheckPoints(self):
        # clean all the settings
        self.addRegSubmenu_SseSplineItem.Check(False)
        self.addRegSubmenu_PenSecDerSplineItem.Check(False)
        self.addRegSubmenu_LowessItem.Check(False)
        self.simpleShiftSubmenu_MedianItem.Check(False)
        self.simpleShiftSubmenu_EmItem.Check(False)
        self.bypassRefiningSubmenu_Item.Check(False)
        #
        # get names of approaches
        refiningMethod       = self.updatedSettings['refiningPars']['choices']['refining method']
        addRegSubMethod      = self.updatedSettings['refiningPars']['choices']['additiveRegression']
        simpleShiftSubMethod = self.updatedSettings['refiningPars']['choices']['simpleShift']
        #
        if refiningMethod == 'additiveRegression':
            subMenu = {'numpy_runmed_spline':    self.addRegSubmenu_SseSplineItem,
                       'R_runmed_spline':        self.addRegSubmenu_PenSecDerSplineItem,
                       'numpy_runmed_lowess':    self.addRegSubmenu_LowessItem
                       }[str(addRegSubMethod)]
            subMenu.Check(True)
        elif refiningMethod == 'simpleShift':
            subMenu = {'medianShift':                self.simpleShiftSubmenu_MedianItem,
                       'ExpMax_Norm_n_FixedNorm':    self.simpleShiftSubmenu_EmItem,
                       }[str(simpleShiftSubMethod)]
            subMenu.Check(True)
        elif refiningMethod == 'bypassRefining':
            self.bypassRefiningSubmenu_Item.Check(True)
        else:
            raise Exception, 'can not recognize method name'




    # here goes the responces
    def OnAddRegSubmenu_SseSpline(self, evt):
        # TUNE THE PARAMS OF numpy_runmed_spline
        # is overfit proof?
        # 'number of splitted pieces for overfit proof mode'
        # running median span
        # spar optimization range
        # spar optimization linear steps number
        # K for predError estimates
        # dimensions to use
        # plot all fits        
        dlg = SseSplineDialog( self.updatedSettings)
        result = dlg.ShowModal()
        
        if result == wx.ID_OK:
            #
            self.updatedSettings['refiningPars']['choices']['refining method'] = 'additiveRegression'
            self.updatedSettings['refiningPars']['choices']['additiveRegression'] = 'numpy_runmed_spline'        
            #
            # readout the exposed parameters
            self.updatedSettings['refiningPars']['otherParams']['use overfit proof mode']\
                            = {True:'True', False:'False'}[dlg.isOverfitProof.GetValue()]

            self.updatedSettings['refiningPars']['otherParams']['number of splits for overfit proof mode']\
                            = dlg.numPartForOverfitProofMode.GetValue()

            self.updatedSettings['refiningPars']['regressionSettings']['numpy_runmed_spline']['runMedSpan']\
                            = dlg.runMedSpan.GetValue()

            sseSmoothLog10Range = dlg.sseLog10MultMin.GetValue() +', '+ dlg.sseLog10MultMax.GetValue()
            self.updatedSettings['refiningPars']['regressionSettings']['numpy_runmed_spline']['sse smooth log10 range']\
                            = sseSmoothLog10Range

            self.updatedSettings['refiningPars']['regressionSettings']['numpy_runmed_spline']['bisections']\
                            = dlg.numBisections.GetValue()

            self.updatedSettings['refiningPars']['regressionSettings']['numpy_runmed_spline']['K']\
                            = dlg.kValue.GetValue()

            dimToUse = []
            if dlg.useScan.GetValue():
                dimToUse.append('scanNum')
            if dlg.useMZ.GetValue():
                dimToUse.append('mz')
            if dlg.useInt.GetValue():
                dimToUse.append('logTrappedIonInt')
            if dlg.useTIC.GetValue():
                dimToUse.append('trappedIonsTIC')

            self.updatedSettings['refiningPars']['otherParams']['dimensions']\
                            = ', '.join(dimToUse)

            self.updatePars()
            
        self.refreshTheCheckPoints()
        evt.Skip()





    def OnAddRegSubmenu_PenSecDerSpline(self, evt):
        # TUNE THE PARAMS OF R_runmed_spline
        # is overfit proof?
        # 'number of splitted pieces for overfit proof mode'
        # running median span
        # spar optimization range
        # spar optimization linear steps number
        # K for predError estimates
        # dimensions to use
        dlg = RSplineDialog( self.updatedSettings)
        result = dlg.ShowModal()
        
        if result == wx.ID_OK:
            #
            self.updatedSettings['refiningPars']['choices']['refining method'] = 'additiveRegression'
            self.updatedSettings['refiningPars']['choices']['additiveRegression'] = 'R_runmed_spline'        
            #
            # readout the exposed parameters
            self.updatedSettings['refiningPars']['otherParams']['use overfit proof mode']\
                            = {True:'True', False:'False'}[dlg.isOverfitProof.GetValue()]            

            self.updatedSettings['refiningPars']['otherParams']['number of splits for overfit proof mode']\
                            = dlg.numPartForOverfitProofMode.GetValue()

            self.updatedSettings['refiningPars']['regressionSettings']['R_runmed_spline']['K']\
                            = dlg.kValue.GetValue()

            self.updatedSettings['refiningPars']['regressionSettings']['R_runmed_spline']['runMedSpan']\
                            = dlg.runMedSpan.GetValue()
            
            sparRange = dlg.sparRangeMin.GetValue() +', '+ dlg.sparRangeMax.GetValue()
            self.updatedSettings['refiningPars']['regressionSettings']['R_runmed_spline']['spar range']\
                            = sparRange

            self.updatedSettings['refiningPars']['regressionSettings']['R_runmed_spline']['spar steps number']\
                            = dlg.numSparOptimSteps.GetValue()

            dimToUse = []
            if dlg.useScan.GetValue():
                dimToUse.append('scanNum')
            if dlg.useMZ.GetValue():
                dimToUse.append('mz')
            if dlg.useInt.GetValue():
                dimToUse.append('logTrappedIonInt')
            if dlg.useTIC.GetValue():
                dimToUse.append('trappedIonsTIC')

            self.updatedSettings['refiningPars']['otherParams']['dimensions']\
                            = ', '.join(dimToUse)

            self.updatePars()
            
        self.refreshTheCheckPoints()

        evt.Skip()
        



    def OnAddRegSubmenu_Lowess(self, evt):
        # TUNE THE PARAMS OF LOWESS
        # is overfit proof?
        # K for predError estimates
        # running median span
        # lowess span
        # lowess robust iters
        # plot all fits
        # dimensions to use
        dlg = LowessDialog( self.updatedSettings)
        result = dlg.ShowModal()
        
        if result == wx.ID_OK:
            #
            self.updatedSettings['refiningPars']['choices']['refining method'] = 'additiveRegression'
            self.updatedSettings['refiningPars']['choices']['additiveRegression'] = 'numpy_runmed_lowess'        
            #
            # readout the exposed parameters
            self.updatedSettings['refiningPars']['otherParams']['use overfit proof mode']\
                            = {True:'True', False:'False'}[dlg.isOverfitProof.GetValue()]            

            self.updatedSettings['refiningPars']['otherParams']['number of splits for overfit proof mode']\
                            = dlg.numPartForOverfitProofMode.GetValue()

            self.updatedSettings['refiningPars']['regressionSettings']['numpy_runmed_lowess']['K']\
                            = dlg.kValue.GetValue()

            self.updatedSettings['refiningPars']['regressionSettings']['numpy_runmed_lowess']['runMedSpan']\
                            = dlg.runMedSpan.GetValue()

            self.updatedSettings['refiningPars']['regressionSettings']['numpy_runmed_lowess']['lowess span']\
                            = dlg.lowessSpan.GetValue()

            self.updatedSettings['refiningPars']['regressionSettings']['numpy_runmed_lowess']['lowess robust iters']\
                            = dlg.numRobIter.GetValue()

            dimToUse = []
            if dlg.useScan.GetValue():
                dimToUse.append('scanNum')
            if dlg.useMZ.GetValue():
                dimToUse.append('mz')
            if dlg.useInt.GetValue():
                dimToUse.append('logTrappedIonInt')
            if dlg.useTIC.GetValue():
                dimToUse.append('trappedIonsTIC')
            self.updatedSettings['refiningPars']['otherParams']['dimensions']\
                            = ', '.join(dimToUse)         
            self.updatePars()
        self.refreshTheCheckPoints()
        evt.Skip()        




    def OnSimpleShiftSubmenu_Median(self, evt):

        dlg = MedianShiftDialog( self.updatedSettings)
        result = dlg.ShowModal()
        
        if result == wx.ID_OK:
            self.updatedSettings['refiningPars']['choices']['refining method'] = 'simpleShift'
            self.updatedSettings['refiningPars']['choices']['simpleShift'] = 'medianShift'
            self.updatePars()
        self.refreshTheCheckPoints()
        evt.Skip()        



    def OnSimpleShiftSubmenu_EM(self, evt):

        dlg = EmShiftDialog( self.updatedSettings)
        result = dlg.ShowModal()
        if result == wx.ID_OK:
            self.updatedSettings['refiningPars']['choices']['refining method'] = 'simpleShift'
            self.updatedSettings['refiningPars']['choices']['simpleShift'] = 'ExpMax_Norm_n_FixedNorm'
            self.updatePars()
        self.refreshTheCheckPoints()
        evt.Skip()  





    def OnBypassRefiningSubmenu(self, evt):
        dlg = BypassRefiningDialog( self.updatedSettings)
        result = dlg.ShowModal()
        if result == wx.ID_OK:
            self.updatedSettings['refiningPars']['choices']['refining method'] = 'bypassRefining'
            self.updatePars()            
        self.refreshTheCheckPoints()
        evt.Skip()        





    def OnRestoreDefaults(self, evt):
        self.updatedSettings['refiningPars']\
             = copy.deepcopy(self.mainFrame.controller.defaultSettings['refiningPars'])
        # 
        # update the checks of the subMenuItems
        self.refreshTheCheckPoints()
        #
        wx.MessageBox('Default Error Correction and Plotting Settings Restored')
        evt.Skip()        





    def updatePars( self):
        self.mainFrame.controller.updatedSettings['refiningPars']\
             = copy.deepcopy( self.updatedSettings['refiningPars'])
        # also update label on the main panel
        self.mainFrame.updateRefiningMethod()
        


    def OnLoadNewSettings(self):
        self.updatedSettings = copy.deepcopy( self.mainFrame.controller.defaultSettings)
        self.defaultSettings = self.mainFrame.controller.defaultSettings
        self.refreshTheCheckPoints()







class LowessDialog(wx.Dialog):
    def __init__(self, updatedSettings):
        wx.Dialog.__init__( self, None, -1,
                            'Running Median and Lowess Settings',
                            size=(400,500))


        # get the settings
        isOverfitProof      = {'True':True, 'False':False}[updatedSettings['refiningPars']['otherParams']['use overfit proof mode']]
        numPartForOverfitProofMode = updatedSettings['refiningPars']['otherParams']['number of splits for overfit proof mode']
        runMedSpan          = updatedSettings['refiningPars']['regressionSettings']['numpy_runmed_lowess']['runMedSpan']
        lowessSpan          = updatedSettings['refiningPars']['regressionSettings']['numpy_runmed_lowess']['lowess span']
        numRobIter          = updatedSettings['refiningPars']['regressionSettings']['numpy_runmed_lowess']['lowess robust iters']
        kValue              = updatedSettings['refiningPars']['regressionSettings']['numpy_runmed_lowess']['K']        
        useDims             = updatedSettings['refiningPars']['otherParams']['dimensions'].split(',')
        useDims             = [i.strip(' ') for i in useDims]

        useScan = 'scanNum'          in useDims
        useMZ   = 'mz'               in useDims
        useInt  = 'logTrappedIonInt'    in useDims
        useTIC  = 'trappedIonsTIC'      in useDims        


        # initialize all the controls
        okButton = wx.Button(self, wx.ID_OK, "OK")
        okButton.SetDefault()
        cancelButton = wx.Button(self, wx.ID_CANCEL, "Cancel")

        self.isOverfitProof = wx.CheckBox(self, -1, "Use Overfit Proof Mode")
        self.isOverfitProof.SetValue( isOverfitProof)
        self.numPartForOverfitProofMode = wx.TextCtrl(self, -1, numPartForOverfitProofMode, size = (40,-1))
        #
        self.runMedSpan     = wx.TextCtrl(self, -1, runMedSpan,     size = (40,-1))
        self.lowessSpan     = wx.TextCtrl(self, -1, lowessSpan,     size = (40,-1))
        self.numRobIter     = wx.TextCtrl(self, -1, numRobIter,     size = (40,-1))
        self.kValue         = wx.TextCtrl(self, -1, kValue,         size = (40,-1))
        #
        self.useScan        = wx.CheckBox(self, -1, "Use MS Scan Number")
        self.useScan.SetValue( useScan)
        self.useMZ          = wx.CheckBox(self, -1, "Use m/z")
        self.useMZ.SetValue( useMZ)
        self.useInt         = wx.CheckBox(self, -1, "Use Parent Ion Intensity")
        self.useInt.SetValue( useInt)        
        self.useTIC         = wx.CheckBox(self, -1, "Use TIC of the MS Scan")
        self.useTIC.SetValue( useTIC)



        # LAYOUT
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        
        # Overfit Proof Mode
        overfitBox       = wx.StaticBox( self, -1, 'Overfit Proof Mode')
        overfitSizer     = wx.StaticBoxSizer( overfitBox, wx.VERTICAL)
        overfitSizer.Add( self.isOverfitProof, 0, wx.ALL, 5)
        numPartSizer     = wx.BoxSizer( wx.HORIZONTAL)
        numPartSizer.Add( self.numPartForOverfitProofMode, 0, wx.ALL, 5)
        static           = wx.StaticText(self, -1, "Number of Pieces to Split Data")        
        numPartSizer.Add( static, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 0)
        overfitSizer.Add( numPartSizer)
        mainSizer.Add( overfitSizer, 0, wx.ALL|wx.EXPAND, 5)
        
        
        # Regression Fitting Pars
        regressBox = wx.StaticBox( self, -1, 'Regression Fitting Parameters')
        regressSizer = wx.StaticBoxSizer( regressBox, wx.VERTICAL)
        #
        runMedSizer = wx.BoxSizer( wx.HORIZONTAL)
        runMedSizer.Add( self.runMedSpan, 0, wx.ALL, 5)
        static = wx.StaticText(self, -1, "Running Median Span (from 0 to 1)")
        runMedSizer.Add( static, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 0)
        runMedSizer.Add( (10,10), 1, wx.ALL, 5)
        regressSizer.Add( runMedSizer)
        #
        lowessSpanSizer = wx.BoxSizer( wx.HORIZONTAL)
        lowessSpanSizer.Add( self.lowessSpan, 0, wx.ALL, 5)
        static = wx.StaticText(self, -1, "Lowess Span (from 0 to 1)")
        lowessSpanSizer.Add( static, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 0)
        lowessSpanSizer.Add( (10,10), 1, wx.ALL, 5)
        regressSizer.Add( lowessSpanSizer)
        #
        numRobIterSizer = wx.BoxSizer( wx.HORIZONTAL)
        numRobIterSizer.Add( self.numRobIter, 0, wx.ALL, 5)
        static = wx.StaticText( self, -1, "Number of Robustifying Iterations")
        numRobIterSizer.Add( static, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 0)
        numRobIterSizer.Add( (10,10), 1, wx.ALL, 5)
        regressSizer.Add( numRobIterSizer)
        #
        kValSizer = wx.BoxSizer( wx.HORIZONTAL)
        kValSizer.Add( self.kValue, 0, wx.ALL, 5)
        static = wx.StaticText(self, -1, "K Value for Prediction Error Estimation Using K-fold CV")
        kValSizer.Add( static, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 0)
        kValSizer.Add( (10,10), 1, wx.ALL, 5)
        regressSizer.Add( kValSizer)
        #
        mainSizer.Add( regressSizer, 0, wx.ALL|wx.EXPAND, 5)

        # dimensions to use
        dimensionsBox = wx.StaticBox( self, -1, 'Dimenstions to Use')
        dimensionsSizer = wx.StaticBoxSizer( dimensionsBox, wx.VERTICAL)
        dimensionsSizer.Add( self.useScan, 0, wx.ALL, 5)
        dimensionsSizer.Add( self.useMZ, 0, wx.ALL, 5)
        dimensionsSizer.Add( self.useInt, 0, wx.ALL, 5)
        dimensionsSizer.Add( self.useTIC, 0, wx.ALL, 5)        
        mainSizer.Add( dimensionsSizer, 0, wx.ALL|wx.EXPAND, 5)

        # buttons
        bttnSizer = wx.BoxSizer(wx.HORIZONTAL)
        bttnSizer.Add((10,10), 1)
        bttnSizer.Add(okButton)
        bttnSizer.Add((10,10), 1)
        bttnSizer.Add(cancelButton)        
        bttnSizer.Add((10,10), 1)
        
        mainSizer.Add(bttnSizer, 0, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(mainSizer)
        self.Fit()








class RSplineDialog( wx.Dialog):
    def __init__(self, updatedSettings):
        wx.Dialog.__init__( self, None, -1,
                            'Running Median and Spline Settings',
                            size=(400,500))


        # get the settings
        isOverfitProof      = {'True':True, 'False':False}[updatedSettings['refiningPars']['otherParams']['use overfit proof mode']]
        numPartForOverfitProofMode = updatedSettings['refiningPars']['otherParams']['number of splits for overfit proof mode']
        runMedSpan          = updatedSettings['refiningPars']['regressionSettings']['R_runmed_spline']['runMedSpan']
        sparRangeStr        = updatedSettings['refiningPars']['regressionSettings']['R_runmed_spline']['spar range']
        sparRangeMin        = sparRangeStr.split(',')[0]
        sparRangeMax        = sparRangeStr.split(',')[1]
        numSparOptimSteps   = updatedSettings['refiningPars']['regressionSettings']['R_runmed_spline']['spar steps number']
        kValue              = updatedSettings['refiningPars']['regressionSettings']['R_runmed_spline']['K']        
        useDims             = updatedSettings['refiningPars']['otherParams']['dimensions'].split(',')
        useDims             = [i.strip(' ') for i in useDims]
        
        useScan = 'scanNum'          in useDims
        useMZ   = 'mz'               in useDims
        useInt  = 'logTrappedIonInt'    in useDims
        useTIC  = 'trappedIonsTIC'      in useDims        


        # initialize all the controls
        okButton = wx.Button(self, wx.ID_OK, "OK")
        okButton.SetDefault()
        cancelButton = wx.Button(self, wx.ID_CANCEL, "Cancel")

        self.isOverfitProof = wx.CheckBox(self, -1, "Use Overfit Proof Mode")
        self.isOverfitProof.SetValue( isOverfitProof)
        self.numPartForOverfitProofMode = wx.TextCtrl(self, -1, numPartForOverfitProofMode, size = (40,-1))
        #
        self.runMedSpan         = wx.TextCtrl(self, -1, runMedSpan,         size = (40,-1))
        self.sparRangeMin       = wx.TextCtrl(self, -1, sparRangeMin,       size = (40,-1))
        self.sparRangeMax       = wx.TextCtrl(self, -1, sparRangeMax,       size = (40,-1))
        self.numSparOptimSteps  = wx.TextCtrl(self, -1, numSparOptimSteps,  size = (40,-1))
        self.kValue             = wx.TextCtrl(self, -1, kValue,             size = (40,-1))
        #
        self.useScan = wx.CheckBox(self, -1, "Use MS Scan Number")
        self.useScan.SetValue( useScan)
        self.useMZ   = wx.CheckBox(self, -1, "Use m/z")
        self.useMZ.SetValue( useMZ)
        self.useInt  = wx.CheckBox(self, -1, "Use Parent Ion Intensity")
        self.useInt.SetValue( useInt)        
        self.useTIC  = wx.CheckBox(self, -1, "Use TIC of the MS Scan")
        self.useTIC.SetValue( useTIC)

        # LAYOUT
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        
        # Overfit Proof Mode
        overfitBox = wx.StaticBox( self, -1, 'Overfit Proof Mode')
        overfitSizer = wx.StaticBoxSizer( overfitBox, wx.VERTICAL)
        overfitSizer.Add( self.isOverfitProof, 0, wx.ALL, 5)
        numPartSizer = wx.BoxSizer( wx.HORIZONTAL)
        numPartSizer.Add( self.numPartForOverfitProofMode, 0, wx.ALL, 5)
        static = wx.StaticText(self, -1, "Number of Pieces to Split Data")        
        numPartSizer.Add( static, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 0)
        overfitSizer.Add( numPartSizer)
        mainSizer.Add( overfitSizer, 0, wx.ALL|wx.EXPAND, 5)
        
        
        # Regression Fitting Pars
        regressBox = wx.StaticBox( self, -1, 'Regression Fitting Parameters')
        regressSizer = wx.StaticBoxSizer( regressBox, wx.VERTICAL)
        #
        runMedSizer = wx.BoxSizer( wx.HORIZONTAL)
        runMedSizer.Add( self.runMedSpan, 0, wx.ALL, 5)
        static = wx.StaticText(self, -1, "Running Median Span (from 0 to 1)")
        runMedSizer.Add( static, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 0)
        runMedSizer.Add( (10,10), 1, wx.ALL, 5)
        regressSizer.Add( runMedSizer)
        #
        sparRangeSizer = wx.BoxSizer( wx.HORIZONTAL)
        sparRangeSizer.Add( self.sparRangeMin, 0, wx.ALL, 5)
        sparRangeSizer.Add( self.sparRangeMax, 0, wx.ALL, 5)        
        static = wx.StaticText(self, -1, "Smoothing Parameter Range [Min, Max]")
        sparRangeSizer.Add( static, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 0)
        sparRangeSizer.Add( (10,10), 1, wx.ALL, 5)
        regressSizer.Add( sparRangeSizer)
        #
        numSparStepsSizer = wx.BoxSizer( wx.HORIZONTAL)
        numSparStepsSizer.Add( self.numSparOptimSteps, 0, wx.ALL, 5)
        static = wx.StaticText( self, -1, "Number of Steps for Linear Optimization")
        numSparStepsSizer.Add( static, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 0)
        numSparStepsSizer.Add( (10,10), 1, wx.ALL, 5)
        regressSizer.Add( numSparStepsSizer)
        #
        kValSizer = wx.BoxSizer( wx.HORIZONTAL)
        kValSizer.Add( self.kValue, 0, wx.ALL, 5)
        static = wx.StaticText(self, -1, "K Value for Prediction Error Estimation Using K-fold CV")
        kValSizer.Add( static, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 0)
        kValSizer.Add( (10,10), 1, wx.ALL, 5)
        regressSizer.Add( kValSizer)
        #
        mainSizer.Add( regressSizer, 0, wx.ALL|wx.EXPAND, 5)

        # dimensions to use
        dimensionsBox = wx.StaticBox( self, -1, 'Dimenstions to Use')
        dimensionsSizer = wx.StaticBoxSizer( dimensionsBox, wx.VERTICAL)
        dimensionsSizer.Add( self.useScan, 0, wx.ALL, 5)
        dimensionsSizer.Add( self.useMZ, 0, wx.ALL, 5)
        dimensionsSizer.Add( self.useInt, 0, wx.ALL, 5)
        dimensionsSizer.Add( self.useTIC, 0, wx.ALL, 5)        
        mainSizer.Add( dimensionsSizer, 0, wx.ALL|wx.EXPAND, 5)

        # buttons
        bttnSizer = wx.BoxSizer(wx.HORIZONTAL)
        bttnSizer.Add((10,10), 1)
        bttnSizer.Add(okButton)
        bttnSizer.Add((10,10), 1)
        bttnSizer.Add(cancelButton)        
        bttnSizer.Add((10,10), 1)
        
        mainSizer.Add(bttnSizer, 0, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(mainSizer)
        self.Fit()






class SseSplineDialog( wx.Dialog):
    def __init__(self, updatedSettings):
        wx.Dialog.__init__( self, None, -1,
                            'Running Median and Spline Settings',
                            size=(400,500))


        # get the settings
        isOverfitProof      = {'True':True, 'False':False}[updatedSettings['refiningPars']['otherParams']['use overfit proof mode']]
        numPartForOverfitProofMode = updatedSettings['refiningPars']['otherParams']['number of splits for overfit proof mode']
        runMedSpan          = updatedSettings['refiningPars']['regressionSettings']['numpy_runmed_spline']['runMedSpan']
        sseLog10MultStr     = updatedSettings['refiningPars']['regressionSettings']['numpy_runmed_spline']['sse smooth log10 range']
        sseLog10MultMin     = sseLog10MultStr.split(',')[0]
        sseLog10MultMax     = sseLog10MultStr.split(',')[1]
        numBisections       = updatedSettings['refiningPars']['regressionSettings']['numpy_runmed_spline']['bisections']
        kValue              = updatedSettings['refiningPars']['regressionSettings']['numpy_runmed_spline']['K']        
        useDims             = updatedSettings['refiningPars']['otherParams']['dimensions'].split(',')
        useDims             = [i.strip(' ') for i in useDims]
        
        useScan = 'scanNum'          in useDims
        useMZ   = 'mz'               in useDims
        useInt  = 'logTrappedIonInt'    in useDims
        useTIC  = 'trappedIonsTIC'      in useDims        


        # initialize all the controls
        okButton        = wx.Button(self, wx.ID_OK, "OK")
        okButton.SetDefault()
        cancelButton    = wx.Button(self, wx.ID_CANCEL, "Cancel")

        self.isOverfitProof = wx.CheckBox(self, -1, "Use Overfit Proof Mode")
        self.isOverfitProof.SetValue( isOverfitProof)
        self.numPartForOverfitProofMode = wx.TextCtrl(self, -1, numPartForOverfitProofMode, size = (40,-1))
        #
        self.runMedSpan         = wx.TextCtrl(self, -1, runMedSpan,         size = (40,-1))
        self.sseLog10MultMin    = wx.TextCtrl(self, -1, sseLog10MultMin,    size = (40,-1))
        self.sseLog10MultMax    = wx.TextCtrl(self, -1, sseLog10MultMax,    size = (40,-1))
        self.numBisections      = wx.TextCtrl(self, -1, numBisections,      size = (40,-1))
        self.kValue             = wx.TextCtrl(self, -1, kValue,             size = (40,-1))
        #
        self.useScan    = wx.CheckBox(self, -1, "Use MS Scan Number")
        self.useScan.SetValue( useScan)
        self.useMZ      = wx.CheckBox(self, -1, "Use m/z")
        self.useMZ.SetValue( useMZ)
        self.useInt     = wx.CheckBox(self, -1, "Use Parent Ion Intensity")
        self.useInt.SetValue( useInt)        
        self.useTIC     = wx.CheckBox(self, -1, "Use TIC of the MS Scan")
        self.useTIC.SetValue( useTIC)

        # LAYOUT
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        
        # Overfit Proof Mode
        overfitBox      = wx.StaticBox( self, -1, 'Overfit Proof Mode')
        overfitSizer    = wx.StaticBoxSizer( overfitBox, wx.VERTICAL)
        overfitSizer.Add( self.isOverfitProof, 0, wx.ALL, 5)
        numPartSizer    = wx.BoxSizer( wx.HORIZONTAL)
        numPartSizer.Add( self.numPartForOverfitProofMode, 0, wx.ALL, 5)
        static          = wx.StaticText(self, -1, "Number of Pieces to Split Data")        
        numPartSizer.Add( static, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 0)
        overfitSizer.Add( numPartSizer)
        mainSizer.Add( overfitSizer, 0, wx.ALL|wx.EXPAND, 5)
        
        
        # Regression Fitting Pars
        regressBox      = wx.StaticBox( self, -1, 'Regression Fitting Parameters')
        regressSizer    = wx.StaticBoxSizer( regressBox, wx.VERTICAL)
        #
        runMedSizer     = wx.BoxSizer( wx.HORIZONTAL)
        runMedSizer.Add( self.runMedSpan, 0, wx.ALL, 5)
        static          = wx.StaticText(self, -1, "Running Median Span (from 0 to 1)")
        runMedSizer.Add( static, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 0)
        runMedSizer.Add( (10,10), 1, wx.ALL, 5)
        regressSizer.Add( runMedSizer)
        #
        sseMultRangeSizer = wx.BoxSizer( wx.HORIZONTAL)
        sseMultRangeSizer.Add( self.sseLog10MultMin, 0, wx.ALL, 5)
        sseMultRangeSizer.Add( self.sseLog10MultMax, 0, wx.ALL, 5)        
        static = wx.StaticText(self, -1, "SSE Multiplier Log10 Range [Min, Max]")
        sseMultRangeSizer.Add( static, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 0)
        sseMultRangeSizer.Add( (10,10), 1, wx.ALL, 5)
        regressSizer.Add( sseMultRangeSizer)
        #
        numBisectionsSizer = wx.BoxSizer( wx.HORIZONTAL)
        numBisectionsSizer.Add( self.numBisections, 0, wx.ALL, 5)
        static = wx.StaticText( self, -1, "Number of Bisections for Multiplier Optimization")
        numBisectionsSizer.Add( static, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 0)
        numBisectionsSizer.Add( (10,10), 1, wx.ALL, 5)
        regressSizer.Add( numBisectionsSizer)
        #
        kValSizer = wx.BoxSizer( wx.HORIZONTAL)
        kValSizer.Add( self.kValue, 0, wx.ALL, 5)
        static = wx.StaticText(self, -1, "K Value for Prediction Error Estimation Using K-fold CV")
        kValSizer.Add( static, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 0)
        kValSizer.Add( (10,10), 1, wx.ALL, 5)
        regressSizer.Add( kValSizer)
        #
        mainSizer.Add( regressSizer, 0, wx.ALL|wx.EXPAND, 5)

        # dimensions to use
        dimensionsBox = wx.StaticBox( self, -1, 'Dimenstions to Use')
        dimensionsSizer = wx.StaticBoxSizer( dimensionsBox, wx.VERTICAL)
        dimensionsSizer.Add( self.useScan, 0, wx.ALL, 5)
        dimensionsSizer.Add( self.useMZ, 0, wx.ALL, 5)
        dimensionsSizer.Add( self.useInt, 0, wx.ALL, 5)
        dimensionsSizer.Add( self.useTIC, 0, wx.ALL, 5)        
        mainSizer.Add( dimensionsSizer, 0, wx.ALL|wx.EXPAND, 5)

        # buttons
        bttnSizer = wx.BoxSizer(wx.HORIZONTAL)
        bttnSizer.Add((10,10), 1)
        bttnSizer.Add(okButton)
        bttnSizer.Add((10,10), 1)
        bttnSizer.Add(cancelButton)        
        bttnSizer.Add((10,10), 1)
        
        mainSizer.Add(bttnSizer, 0, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(mainSizer)
        self.Fit()








class MedianShiftDialog( wx.Dialog):
    def __init__(self, updatedSettings):
        wx.Dialog.__init__( self, None, -1,
                            'Shift by Median',
                            size=(400,500))


        # initialize all the controls
        static = wx.StaticText( self, -1,
                                'The distribution of mass measurement errors is going to be zero-centered.\n'
                                '\n'
                                'The mean of the distribution is going to be estimated as median, followed by\n'
                                'subtraction of the estimated mean from all the error residual values.')
        
        okButton = wx.Button(self, wx.ID_OK, "OK")
        okButton.SetDefault()
        cancelButton = wx.Button(self, wx.ID_CANCEL, "Cancel")


        # LAYOUT
        mainSizer = wx.BoxSizer(wx.VERTICAL)

        #caption
        mainSizer.Add( static, 1, wx.EXPAND|wx.ALL, 10)
        
        # buttons
        bttnSizer = wx.BoxSizer(wx.HORIZONTAL)
        bttnSizer.Add((10,10), 1)
        bttnSizer.Add(okButton)
        bttnSizer.Add((10,10), 1)
        bttnSizer.Add(cancelButton)        
        bttnSizer.Add((10,10), 1)
        
        mainSizer.Add(bttnSizer, 0, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(mainSizer)
        self.Fit()






class EmShiftDialog( wx.Dialog):
    def __init__(self, updatedSettings):
        wx.Dialog.__init__( self, None, -1,
                            'Shift by Mean Estimated by EM',
                            size=(400,500))


        # initialize all the controls
        static = wx.StaticText( self, -1,
                                'The distribution of mass measurement errors is going to be zero-centered.\n'
                                '\n'
                                'The mean of the distribution is going to be estimated using Expectation\n'
                                'Maximization algorithm, followed by subtraction of the estimated mean from\n'
                                'all the error residual values.')
        
        okButton = wx.Button(self, wx.ID_OK, "OK")
        okButton.SetDefault()
        cancelButton = wx.Button(self, wx.ID_CANCEL, "Cancel")


        # LAYOUT
        mainSizer = wx.BoxSizer(wx.VERTICAL)

        #caption
        mainSizer.Add( static, 1, wx.EXPAND|wx.ALL, 10)
        
        # buttons
        bttnSizer = wx.BoxSizer(wx.HORIZONTAL)
        bttnSizer.Add((10,10), 1)
        bttnSizer.Add(okButton)
        bttnSizer.Add((10,10), 1)
        bttnSizer.Add(cancelButton)        
        bttnSizer.Add((10,10), 1)
        
        mainSizer.Add(bttnSizer, 0, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(mainSizer)
        self.Fit()






class BypassRefiningDialog( wx.Dialog):
    def __init__(self, updatedSettings):
        wx.Dialog.__init__( self, None, -1,
                            'Bypass Refining',
                            size=(400,500))


        # initialize all the controls
        static = wx.StaticText( self, -1,
                                'No error correction procedure is going to be applied.\n'
                                'All the parent ion masses are going to be left as is.')
        
        okButton = wx.Button(self, wx.ID_OK, "OK")
        okButton.SetDefault()
        cancelButton = wx.Button(self, wx.ID_CANCEL, "Cancel")


        # LAYOUT
        mainSizer = wx.BoxSizer(wx.VERTICAL)

        #caption
        mainSizer.Add( static, 1, wx.EXPAND|wx.ALL, 10)
        
        # buttons
        bttnSizer = wx.BoxSizer(wx.HORIZONTAL)
        bttnSizer.Add((10,10), 1)
        bttnSizer.Add(okButton)
        bttnSizer.Add((10,10), 1)
        bttnSizer.Add(cancelButton)        
        bttnSizer.Add((10,10), 1)
        
        mainSizer.Add(bttnSizer, 0, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(mainSizer)
        self.Fit()





if __name__ == '__main__':
    app = wx.PySimpleApp()
    frm = wx.Frame(None)
    menuBar = wx.MenuBar()
    MyMenu = CorrectionParsMenu(frm)
    menuBar.Append(MyMenu, 'Corr Pars')
    frm.SetMenuBar(menuBar)
    frm.Show(True)
    app.MainLoop()
