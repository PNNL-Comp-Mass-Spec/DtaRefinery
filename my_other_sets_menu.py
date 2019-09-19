import wx
import copy
import re


class OtherSetsMenu(wx.Menu):
    def __init__(self, parent):
        wx.Menu.__init__(self)

        self.mainFrame = parent

        # the holder for settings within the class
        self.updatedSettings = copy.deepcopy(self.mainFrame.controller.defaultSettings)

        # this is default settings just in case of RESET
        self.defaultSettings = copy.deepcopy(self.updatedSettings)

        # set the menu items
        xtandemSetsMenuItem = self.Append(-1, '&X!Tandem Settings')
        plottingSetsMenuItem = self.Append(-1, '&Plotting Settings')

        # add the bindings to the menu items
        parent.Bind(wx.EVT_MENU, self.OnXtandemSets, xtandemSetsMenuItem)

        parent.Bind(wx.EVT_MENU, self.OnPlottingSets, plottingSetsMenuItem)

    # ---HERE GOES RESPONSES---------

    # starts the dialog on X!Tandem Settings
    def OnXtandemSets(self, evt):

        dlg = XtandemSetsDialog(self.updatedSettings, self.defaultSettings)
        result = dlg.ShowModal()

        if result == wx.ID_OK:
            self.updatedSettings['xtandemPars']['maximum valid E value'] \
                = dlg.maxValidEvalue.GetValue()

            parentMassError = dlg.parentMassErrorMinus.GetValue() + ', ' + dlg.parentMassErrorPlus.GetValue()
            self.updatedSettings['xtandemPars']['parent ion mass tolerance, ppm'] \
                = parentMassError

            # --- PTM in OnXtandemSets
            # readout the PTMs
            self.updatedSettings['xtandemPars']['static modifications'] \
                = dlg.ptmHolder.staticEntry.GetValue()
            self.updatedSettings['xtandemPars']['dynamic modifications'] \
                = dlg.ptmHolder.dynamicEntry.GetValue()

            # --- Cleavage Rule in OnXtandemSets
            # readout the Cleavage Rule: Specificity, number of missed cleavages, is not-fully cleaved allowed
            self.updatedSettings['xtandemPars']['cleavage specificity'] \
                = dlg.cleavageRuleHolder.cleavageSpecificityEntry.GetValue()

            # update
            self.mainFrame.controller.updatedSettings['xtandemPars'] \
                = copy.deepcopy(self.updatedSettings['xtandemPars'])

        evt.Skip()

    # starts the dialog on plotting Settings
    def OnPlottingSets(self, evt):

        dlg = PlottingSetsDialog(self.updatedSettings, self.defaultSettings)
        result = dlg.ShowModal()

        if result == wx.ID_OK:
            # readout settings
            self.updatedSettings['plottingPars']['plot final scatterplots'] \
                = {True: 'True', False: 'False'}[dlg.plotBool.GetValue()]

            plotRange = dlg.plotRangeMin.GetValue() + ', ' + dlg.plotRangeMax.GetValue()
            self.updatedSettings['plottingPars']['plotting range, ppm'] \
                = plotRange

            self.updatedSettings['plottingPars']['histogram bin size, ppm'] \
                = dlg.histBinSize.GetValue()

            self.updatedSettings['plottingPars']['plot all iteration fits'] \
                = {True: 'True', False: 'False'}[dlg.plotAllIters.GetValue()]

            # update
            self.mainFrame.controller.updatedSettings['plottingPars'] \
                = copy.deepcopy(self.updatedSettings['plottingPars'])

        evt.Skip()

    def OnLoadNewSettings(self):
        self.updatedSettings = copy.deepcopy(self.mainFrame.controller.defaultSettings)
        self.defaultSettings = self.mainFrame.controller.defaultSettings


class XtandemSetsDialog(wx.Dialog):
    def __init__(self, updatedSettings, defaultSettings):
        '''
        updatedSettings     are current settings
        defaultSettings     are default settings
        '''

        self.updatedSettings = updatedSettings
        self.defaultSettings = defaultSettings

        wx.Dialog.__init__(self, None, -1,
                           'X!Tandem Settings')

        # get the values out of X!Tandem settings
        maxValidEvalue = self.updatedSettings['xtandemPars']['maximum valid E value']
        parentMassError = self.updatedSettings['xtandemPars']['parent ion mass tolerance, ppm']
        parentMassErrorMinus, parentMassErrorPlus = parentMassError.split(', ')
        #        staticMods         = self.updatedSettings['xtandemPars']['static modifications']
        #        dynamicMods        = self.updatedSettings['xtandemPars']['dynamic modifications']
        # cleavage rule: specificity
        #        cleavageSpecificity  = self.updatedSettings['xtandemPars']['cleavage specificity']

        # initialize all the controls
        #
        # buttons
        okButton = wx.Button(self, wx.ID_OK, "OK")
        cancelButton = wx.Button(self, wx.ID_CANCEL, "Cancel")
        resetButton = wx.Button(self, -1, "Reset Values")
        okButton.SetDefault()
        self.Bind(wx.EVT_BUTTON, self.OnReset, resetButton)
        #
        # e value
        self.maxValidEvalue = wx.TextCtrl(self, -1, maxValidEvalue, size=(40, -1))
        #
        # ppm tolerances
        self.parentMassErrorMinus = wx.TextCtrl(self, -1, parentMassErrorMinus, size=(40, -1))
        self.parentMassErrorPlus = wx.TextCtrl(self, -1, parentMassErrorPlus, size=(40, -1))

        # --- PTM in XtandemSetsDialog
        self.ptmHolder = PtmStringEntry(self)

        # --- Cleavage Rule Dialog
        self.cleavageRuleHolder = CleavageRuleEntry(self)

        # layout of the dialog
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        #
        #
        # box for entries
        box = wx.StaticBox(self, -1, 'Main Settings')
        boxSizer = wx.StaticBoxSizer(box, wx.VERTICAL)
        #
        eValSizer = wx.BoxSizer(wx.HORIZONTAL)
        eValSizer.Add(self.maxValidEvalue, 0, wx.ALL, 5)
        static = wx.StaticText(self, -1, 'Maximum Valid Expectaion Value')
        eValSizer.Add(static, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 0)
        boxSizer.Add(eValSizer)
        #
        ppmTolSizer = wx.BoxSizer(wx.HORIZONTAL)
        ppmTolSizer.Add(self.parentMassErrorMinus, 0, wx.ALL, 5)
        ppmTolSizer.Add(self.parentMassErrorPlus, 0, wx.ALL, 5)
        static = wx.StaticText(self, -1, 'Parent Monoisotopic Mass Error Tolerance (ppm). [minus, plus]')
        ppmTolSizer.Add(static, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 0)
        boxSizer.Add(ppmTolSizer)
        #

        # --- PTM SIZER
        box2 = wx.StaticBox(self, -1, 'PTM Settings')
        ptmSizer = wx.StaticBoxSizer(box2, wx.VERTICAL)
        ptmSizer.Add(self.ptmHolder.sizer, 1, wx.EXPAND)
        #
        # --- Cleavage Rule Sizer
        box3 = wx.StaticBox(self, -1, 'Cleavage Rule Settings')
        cleavageRuleSizer = wx.StaticBoxSizer(box3, wx.VERTICAL)
        cleavageRuleSizer.Add(self.cleavageRuleHolder.sizer, 1, wx.EXPAND)
        #
        #
        # buttons
        bttnSizer = wx.BoxSizer(wx.HORIZONTAL)
        bttnSizer.Add((10, 10), 1)
        bttnSizer.Add(okButton)
        bttnSizer.Add((10, 10), 1)
        bttnSizer.Add(cancelButton)
        bttnSizer.Add((10, 10), 1)
        bttnSizer.Add(resetButton)
        bttnSizer.Add((10, 10), 1)
        #
        #
        # MAIN SIZER
        mainSizer.Add(boxSizer, 0, wx.ALL | wx.EXPAND, 5)
        mainSizer.Add(ptmSizer, 0, wx.ALL | wx.EXPAND, 5)
        mainSizer.Add(cleavageRuleSizer, 0, wx.ALL | wx.EXPAND, 5)
        mainSizer.Add(bttnSizer, 0, wx.ALL | wx.EXPAND, 5)
        #
        self.SetSizer(mainSizer)
        self.Fit()

    def OnReset(self, evt):
        # get the values out of default X!Tandem settings
        maxValidEvalue = self.defaultSettings['xtandemPars']['maximum valid E value']
        parentMassError = self.defaultSettings['xtandemPars']['parent ion mass tolerance, ppm']
        parentMassErrorMinus, parentMassErrorPlus = parentMassError.split(', ')
        staticMods = self.defaultSettings['xtandemPars']['static modifications']
        dynamicMods = self.defaultSettings['xtandemPars']['dynamic modifications']
        cleavageSpecificity = self.defaultSettings['xtandemPars']['cleavage specificity']

        # set them to TextCtrl
        self.maxValidEvalue.SetValue(maxValidEvalue)
        self.parentMassErrorMinus.SetValue(parentMassErrorMinus)
        self.parentMassErrorPlus.SetValue(parentMassErrorPlus)
        self.ptmHolder.staticEntry.SetValue(staticMods)
        self.ptmHolder.dynamicEntry.SetValue(dynamicMods)
        self.cleavageRuleHolder.cleavageSpecificityEntry.SetValue(cleavageSpecificity)

        evt.Skip()


class PlottingSetsDialog(wx.Dialog):
    def __init__(self, updatedSettings, defaultSettings):
        self.updatedSettings = updatedSettings
        self.defaultSettings = defaultSettings

        wx.Dialog.__init__(self, None, -1,
                           'Plotting Settings',
                           size=(400, 500))

        ##        self.defaultPlottingSets = defaultPlottingSets

        plotBool = {'True': True, 'False': False}[self.updatedSettings['plottingPars']['plot final scatterplots']]
        plotRange = self.updatedSettings['plottingPars']['plotting range, ppm']
        plotRangeMin, plotRangeMax = plotRange.split(', ')
        histBinSize = self.updatedSettings['plottingPars']['histogram bin size, ppm']
        plotAllIters = {'True': True, 'False': False}[self.updatedSettings['plottingPars']['plot all iteration fits']]

        # initialize all the controls
        #
        # buttons
        okButton = wx.Button(self, wx.ID_OK, "OK")
        okButton.SetDefault()
        cancelButton = wx.Button(self, wx.ID_CANCEL, "Cancel")
        #
        resetButton = wx.Button(self, -1, "Reset Values")
        self.Bind(wx.EVT_BUTTON, self.OnReset, resetButton)
        #
        # do plots?
        self.plotBool = wx.CheckBox(self, -1, "Plot Final Results?")
        self.plotBool.SetValue(plotBool)
        #
        # plots range
        self.plotRangeMin = wx.TextCtrl(self, -1, plotRangeMin, size=(40, -1))
        self.plotRangeMax = wx.TextCtrl(self, -1, plotRangeMax, size=(40, -1))
        #
        # histogram bin size
        self.histBinSize = wx.TextCtrl(self, -1, histBinSize, size=(40, -1))
        #
        # plot all iterations?
        self.plotAllIters = wx.CheckBox(self, -1, "Plot All Iteration Fits")
        self.plotAllIters.SetValue(plotAllIters)

        # layout of the dialog
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        #
        # box for entries
        box = wx.StaticBox(self, -1, 'Plotting Settings')
        boxSizer = wx.StaticBoxSizer(box, wx.VERTICAL)
        #
        # do final plots chekbox
        boxSizer.Add(self.plotBool, 0, wx.ALL, 5)
        #
        # plot all iterations checkbox
        boxSizer.Add(self.plotAllIters, 0, wx.ALL, 5)
        #        
        # plot range sizer
        plotRangeSizer = wx.BoxSizer(wx.HORIZONTAL)
        plotRangeSizer.Add(self.plotRangeMin, 0, wx.ALL, 5)
        plotRangeSizer.Add(self.plotRangeMax, 0, wx.ALL, 5)
        static = wx.StaticText(self, -1, 'Plotting Range (ppm). [Min, Max]')
        plotRangeSizer.Add(static, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 0)
        boxSizer.Add(plotRangeSizer)
        #
        # hist bin size sizer
        binSizer = wx.BoxSizer(wx.HORIZONTAL)
        binSizer.Add(self.histBinSize, 0, wx.ALL, 5)
        static = wx.StaticText(self, -1, 'Histogram Bin Size')
        binSizer.Add(static, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 0)
        boxSizer.Add(binSizer)
        #
        # buttons
        bttnSizer = wx.BoxSizer(wx.HORIZONTAL)
        bttnSizer.Add((10, 10), 1)
        bttnSizer.Add(okButton)
        bttnSizer.Add((10, 10), 1)
        bttnSizer.Add(cancelButton)
        bttnSizer.Add((10, 10), 1)
        bttnSizer.Add(resetButton)
        bttnSizer.Add((10, 10), 1)
        #
        mainSizer.Add(boxSizer, 0, wx.ALL | wx.EXPAND, 5)
        mainSizer.Add(bttnSizer, 0, wx.ALL | wx.EXPAND, 5)
        #
        self.SetSizer(mainSizer)
        self.Fit()

    def OnReset(self, evt):
        plotBool = {'True': True, 'False': False}[self.defaultSettings['plottingPars']['plot final scatterplots']]
        plotRange = self.defaultSettings['plottingPars']['plotting range, ppm']
        plotRangeMin, plotRangeMax = plotRange.split(', ')
        histBinSize = self.defaultSettings['plottingPars']['histogram bin size, ppm']
        plotAllIters = {'True': True, 'False': False}[self.defaultSettings['plottingPars']['plot all iteration fits']]

        self.plotBool.SetValue(plotBool)
        self.plotRangeMin.SetValue(plotRangeMin)
        self.plotRangeMax.SetValue(plotRangeMax)
        self.histBinSize.SetValue(histBinSize)
        self.plotAllIters.SetValue(plotAllIters)

        evt.Skip()


class PtmFormatValidator(wx.PyValidator):
    def __init__(self):
        wx.PyValidator.__init__(self)
        self.setEntryPttrn()

    def Clone(self):
        return PtmFormatValidator()

    def Validate(self, win):
        textCtrl = self.GetWindow()
        text = textCtrl.GetValue()

        inRightFormat = self.checkEntry(text)

        if not inRightFormat:
            wx.MessageBox("Please check the format!", "Error")
            textCtrl.SetBackgroundColour("pink")
            textCtrl.SetFocus()
            textCtrl.Refresh()
            return False
        else:
            textCtrl.SetBackgroundColour(
                wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
            textCtrl.Refresh()
            return True

    def TransferToWindow(self):
        return True

    def TransferFromWindow(self):
        return True

    def setEntryPttrn(self):
        mass = '[+-]?\d+(\.\d+)?'
        neutralLoss = '(:' + mass + ')?'
        residue = '[ACDEFGHIKLMNPQRSTVWY\[\]]'
        self.pttrn = re.compile(mass + neutralLoss + '@' + residue + '$', re.IGNORECASE)

    def checkEntry(self, entry):
        '''
        checks if the entry was in right format
        M1@X1, M2@X2, ... Mn@Xn or M1:NL1@X1, M2:NL2@X2, ... Mn:NLn@Xn
        '''
        entries = entry.strip(' ').split(',')
        entries = [i.strip(' ') for i in entries]

        if entries == ['']:
            return True
        else:
            inRightFormat = True
            for i in entries:
                ''' now check each, that it is either M@X or M:NL@X'''
                if self.pttrn.match(i) is None:
                    inRightFormat = False
                    break

        return inRightFormat


class PtmStringEntry(XtandemSetsDialog):
    def __init__(self, parent):
        self.parent = parent

        staticMods = self.parent.updatedSettings['xtandemPars']['static modifications']
        dynamicMods = self.parent.updatedSettings['xtandemPars']['dynamic modifications']

        # set title
        # http://www.thegpm.org/TANDEM/api/refmm.html
        title = """
                Define post-translational modifications
                the format is M1@X1,M2@X2,..., Mn@Xn
                where Mi is monoisotopic mass and Xi is amino acid
                in case of N-term and C-term use [ and ], respectively
                In case of neutral loss (with monoisotopic mass NL)
                use M:NL@X format.
                For details, see http://www.thegpm.org/TANDEM/api/refmm.html

                The most common modifications are:
                57.0215@C static Cys alkylation
                14.0157@D, 14.0157@E, 14.0157@] static carboxyl group esterification
                79.9663:-97.9769@S, 79.9663:-97.9769@T dynamic Ser and Thr phosphorylation
                79.9663:-97.9769@Y dynamic tyrosine phosphorylation
                15.9949@M dynamic Met oxidation                                
                """
        titleStrings = [i.strip(' ') for i in title.split('\n')[1:-1]]
        title = '\n'.join(titleStrings)
        stringSizes = [self.parent.GetTextExtent(i) for i in titleStrings]
        stringSizes = [[j[i] for j in stringSizes] for i in range(2)]
        titleWidth = max(stringSizes[0])
        titleHeight = max(stringSizes[1]) * len(stringSizes[1])

        style = (wx.TE_MULTILINE | wx.TE_RICH2 | wx.TE_NO_VSCROLL | wx.NO_BORDER | wx.TE_READONLY)
        titleText = wx.TextCtrl(self.parent, -1, title, size=(titleWidth, titleHeight), style=style)
        bgr = self.parent.GetBackgroundColour()
        titleText.SetBackgroundColour(bgr)

        # set string for static
        self.staticEntry = wx.TextCtrl(self.parent, -1, staticMods, validator=PtmFormatValidator())
        staticTitle = wx.StaticText(self.parent, -1, 'static PTMs:', size=(80, -1), style=wx.ALIGN_RIGHT)
        staticSizer = wx.BoxSizer(wx.HORIZONTAL)
        staticSizer.Add(staticTitle, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 10)
        staticSizer.Add(self.staticEntry, 1)

        # set string for dynamic
        self.dynamicEntry = wx.TextCtrl(self.parent, -1, dynamicMods, validator=PtmFormatValidator())
        dynamicTitle = wx.StaticText(self.parent, -1, 'dynamic PTMs:', size=(80, -1), style=wx.ALIGN_RIGHT)
        dynamicSizer = wx.BoxSizer(wx.HORIZONTAL)
        dynamicSizer.Add(dynamicTitle, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 10)
        dynamicSizer.Add(self.dynamicEntry, 1)

        # layout
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(titleText, 1, wx.EXPAND | wx.ALL, 2)
        mainSizer.Add((20, 20), 0, wx.EXPAND)
        mainSizer.Add(staticSizer, 0, wx.EXPAND | wx.ALL, 2)
        mainSizer.Add(dynamicSizer, 0, wx.EXPAND | wx.ALL, 2)

        self.sizer = mainSizer


class CleavageRuleEntry(XtandemSetsDialog):
    def __init__(self, parent):
        self.parent = parent
        cleavageSpecificity = self.parent.updatedSettings['xtandemPars']['cleavage specificity']
        # set title
        # http://www.thegpm.org/TANDEM/api/refmm.html
        title = """
                Example Entries:
                \tTrypsin: [KR]|{P}
                \tGluc-C (E only): [E]|[X]
                \tNo specificity: [X]|[X]
                For details, see http://www.thegpm.org/TANDEM/api/refmm.html
                """
        titleStrings = [i.strip(' ') for i in title.split('\n')[1:-1]]
        title = '\n'.join(titleStrings)
        stringSizes = [self.parent.GetTextExtent(i) for i in titleStrings]
        stringSizes = [[j[i] for j in stringSizes] for i in range(2)]
        titleWidth = max(stringSizes[0])
        titleHeight = max(stringSizes[1]) * len(stringSizes[1])

        style = (wx.TE_MULTILINE | wx.TE_RICH2 | wx.TE_NO_VSCROLL | wx.NO_BORDER | wx.TE_READONLY)
        titleText = wx.TextCtrl(self.parent, -1, title, size=(titleWidth, titleHeight), style=style)
        bgr = self.parent.GetBackgroundColour()
        titleText.SetBackgroundColour(bgr)

        # text box
        self.cleavageSpecificityEntry = wx.TextCtrl(self.parent, -1, cleavageSpecificity,
                                                    validator=CleavageSpecificityFormatValidator())
        cleavageSpecificityTitle = wx.StaticText(self.parent, -1, 'Cleavage Specificity:', size=(100, -1),
                                                 style=wx.ALIGN_RIGHT)
        cleavageSpecificitySizer = wx.BoxSizer(wx.HORIZONTAL)
        cleavageSpecificitySizer.Add(cleavageSpecificityTitle, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 10)
        cleavageSpecificitySizer.Add(self.cleavageSpecificityEntry, 1)

        # layout
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(titleText, 1, wx.EXPAND | wx.ALL, 2)
        mainSizer.Add((20, 20), 0, wx.EXPAND)
        mainSizer.Add(cleavageSpecificitySizer, 0, wx.EXPAND | wx.ALL, 2)

        self.sizer = mainSizer


class CleavageSpecificityFormatValidator(wx.PyValidator):
    def __init__(self):
        wx.PyValidator.__init__(self)
        self.setEntryPttrn()

    def Clone(self):
        return CleavageSpecificityFormatValidator()

    def Validate(self, win):
        textCtrl = self.GetWindow()
        text = textCtrl.GetValue()

        inRightFormat = self.checkEntry(text)

        if not inRightFormat:
            wx.MessageBox("Please check the format!", "Error")
            textCtrl.SetBackgroundColour("pink")
            textCtrl.SetFocus()
            textCtrl.Refresh()
            return False
        else:
            textCtrl.SetBackgroundColour(
                wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
            textCtrl.Refresh()
            return True

    def TransferToWindow(self):
        return True

    def TransferFromWindow(self):
        return True

    def setEntryPttrn(self):
        residue = '[ACDEFGHIKLMNPQRSTVWYX]'
        str1 = "\[" + residue + "+" + "\]" + "\|" + "\[" + residue + "+" + "\]"
        str2 = "\[" + residue + "+" + "\]" + "\|" + "{" + residue + "+" + "}"
        str3 = "{" + residue + "+" + "}" + "\|" + "\[" + residue + "+" + "\]"
        self.pttrn = re.compile(str1 + "|" + str2 + "|" + str3, re.IGNORECASE)

    def checkEntry(self, entry):
        '''
        checks if the entry was in right format
        '''
        entry = entry.strip(' ')

        if entry == ['']:
            return True
        else:
            inRightFormat = True
            if self.pttrn.match(entry) is None:
                inRightFormat = False

        return inRightFormat
