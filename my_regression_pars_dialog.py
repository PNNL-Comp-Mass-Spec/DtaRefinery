import wx


class RegressionParsDialog(wx.Dialog):
    def __init__(self, pars):
        wx.Dialog.__init__(self, None, -1,
                           'Regression Parsmeters',
                           size=(400,400))
        self.pars = pars

        # buttons
        acceptBttn  = wx.Button( self, wx.ID_APPLY,  'ACCEPT')
        rejectBttn  = wx.Button( self, wx.ID_CANCEL, 'REJECT')
        defaultBttn = wx.Button( self, wx.ID_RESET,  'RESET')
        defaultBttn.SetDefault()

        # main radio buttons
        
        


        # setting sizers
        additiveRegBoxSizer = self.createAdditiveRegBox()
        
        simpleShiftBoxSizer = self.createSimpleShiftBox()

        bypassRefiningBoxSizer   = self.createBypassRefiningBox()


        bttnSizer = wx.BoxSizer( wx.HORIZONTAL)
        bttnSizer.Add((10,10), 1)        
        bttnSizer.Add( acceptBttn)
        bttnSizer.Add((10,10), 1)
        bttnSizer.Add( rejectBttn)
        bttnSizer.Add((10,10), 1)        
        bttnSizer.Add( defaultBttn)
        bttnSizer.Add((10,10), 1)
        
        sizer = wx.BoxSizer( wx.VERTICAL)
        sizer.Add( additiveRegBoxSizer, 1, wx.EXPAND|wx.ALL, 2)
        sizer.Add( simpleShiftBoxSizer, 1, wx.EXPAND|wx.ALL, 2)
        sizer.Add( bypassRefiningBoxSizer,   1, wx.EXPAND|wx.ALL, 2)
        sizer.Add( bttnSizer,      0, wx.EXPAND|wx.ALL, 10)

        self.SetSizer( sizer)
##        sizer.Fit( self)
        # end sizer

    def createAdditiveRegBox(self):
        additiveRegBox = wx.StaticBox( self, -1, 'additive regression')
        sizer = wx.StaticBoxSizer(additiveRegBox, wx.VERTICAL)
        sizer.Add((10,10))
        return sizer

    def createSimpleShiftBox(self):
        simpleShiftBox = wx.StaticBox( self, -1, 'simple shift')
        sizer = wx.StaticBoxSizer( simpleShiftBox, wx.VERTICAL)
        sizer.Add((10,10), 1, wx.EXPAND)
        return sizer

    def createBypassRefiningBox(self):
        bypassRefiningBox = wx.StaticBox( self, -1, 'bypass refining')
        sizer = wx.StaticBoxSizer( bypassRefiningBox, wx.VERTICAL)
        sizer.Add((10,10))
        return sizer


if __name__ == '__main__':
    app = wx.PySimpleApp()
    dlg = RegressionParsDialog('some pars')
    result = dlg.ShowModal()
    if result == wx.ID_OK:
        print 'OK'
    else:
        print 'Cancel'
        print dlg.pars 
    dlg.Destroy()
