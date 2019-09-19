import sys
import wx
import os
from my_controller             import Controller
from my_correction_pars_menu   import CorrectionParsMenu
from my_other_sets_menu        import OtherSetsMenu
from my_xml_settings_handler   import  writeSettingsToXML

__VERSION__ = '1.3'

class MainFrame(wx.Frame):
    def __init__(self, dtaRefineryDir):
        self.dtaRefineryDir = dtaRefineryDir
        wx.Frame.__init__(self, None,
                          title = 'dta refinery',
                          size = (300, 200))
        self.panel = wx.Panel(self)
        self.controller = Controller( self.dtaRefineryDir)
        self.controller.version = __VERSION__
        self.CreateMenuBar()
        self.CreateLabels()
        self.CreateRunBttn()

        #--- Layout
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add((10,10), 1, wx.ALIGN_CENTER)
        self.sizer.Add(self.labelSizer, 0, wx.ALIGN_CENTER|wx.EXPAND|wx.LEFT|wx.RIGHT, border = 5)
        self.sizer.Add((5,5), 0, wx.ALIGN_CENTER)
        self.sizer.Add(self.refiningMethodSizer, 0, wx.ALIGN_CENTER|wx.EXPAND|wx.LEFT|wx.RIGHT, border = 5)
        self.sizer.Add((5,5), 0, wx.ALIGN_CENTER)
        self.sizer.Add(self.runBttn, 0, wx.ALIGN_CENTER)
        self.sizer.Add((10,10), 1, wx.ALIGN_CENTER)        
        self.panel.SetSizer(self.sizer)
        self.panel.Fit()
        
        

    def CreateMenuBar(self):
        menuBar = wx.MenuBar()

        fileMenu = wx.Menu()
        fileMenuDtaItem = fileMenu.Append(-1, "&dta Files...", "Select dta Files")
        fileMenuFastaItem = fileMenu.Append(-1, "&FASTA File...", "Select FASTA File")
        fileMenu.AppendSeparator()
        loadSettingsItem = fileMenu.Append(-1, "&Load Settings File...",    "Load Settings File")
        saveSettingsItem = fileMenu.Append(-1, "&Save Settings File As...", "Save Settings File")
        fileMenu.AppendSeparator()
        exitProgramItem = fileMenu.Append(-1, "E&xit", "Exit")
        #
        self.Bind(wx.EVT_MENU, self.OnSelectDtaFiles,  fileMenuDtaItem)
        self.Bind(wx.EVT_MENU, self.OnSelectFastaFile, fileMenuFastaItem)
        self.Bind(wx.EVT_MENU, self.OnLoadSettings, loadSettingsItem)
        self.Bind(wx.EVT_MENU, self.OnSaveSettings, saveSettingsItem)
        self.Bind(wx.EVT_MENU, self.OnExitProgramItem, exitProgramItem)
        #
        menuBar.Append(fileMenu,"&File")
        
        # correction pars menu
        menuCorrPars = CorrectionParsMenu(self)
        menuBar.Append( menuCorrPars, '&Error Correction Params')
        self.menuCorrPars = menuCorrPars

        # other setting menu
        menuOtherSets = OtherSetsMenu(self)
        menuBar.Append( menuOtherSets, '&Misc Settings')
        self.menuOtherSets = menuOtherSets
       
        # about menu
        helpMenu = wx.Menu()
        helpMenuHelpItem = helpMenu.Append(-1, "&About", "About")
        self.Bind(wx.EVT_MENU, self.OnHelp, helpMenuHelpItem)		
        menuBar.Append( helpMenu, "&About")

        self.SetMenuBar(menuBar)



    def CreateLabels(self):
        
        self.dtaFilesEntryText   = 'not selected'
        self.fastaFilesEntryText = 'not selected'

        dtaFileSizer = wx.BoxSizer(wx.HORIZONTAL)
        dtaFilesTitle = wx.StaticText( self.panel, -1, 'dta file dir:', size=(80,-1))#, style=wx.BORDER_SUNKEN)
        font = dtaFilesTitle.GetFont()
        font.SetWeight( wx.BOLD)
        dtaFilesTitle.SetFont( font)        
        dtaFilesEntry = wx.StaticText( self.panel, -1, self.dtaFilesEntryText)#, style=wx.BORDER_SUNKEN)
        dtaFileSizer.Add((2,2), 0)
        dtaFileSizer.Add(dtaFilesTitle, 0)
        dtaFileSizer.Add((2,2), 0)
        dtaFileSizer.Add(dtaFilesEntry, 1)
        dtaFileSizer.Add((2,2), 0)

        fastaFileSizer = wx.BoxSizer(wx.HORIZONTAL)
        fastaFilesTitle = wx.StaticText( self.panel, -1, 'FASTA file:', size=(80,-1))#, style=wx.BORDER_SUNKEN)
        fastaFilesTitle.SetFont( font)
        fastaFilesEntry = wx.StaticText( self.panel, -1, self.fastaFilesEntryText)#, style=wx.BORDER_SUNKEN)
        fastaFileSizer.Add((2,2), 0)        
        fastaFileSizer.Add(fastaFilesTitle, 0)
        fastaFileSizer.Add((2,2), 0)        
        fastaFileSizer.Add(fastaFilesEntry, 1)
        fastaFileSizer.Add((2,2), 0)        
        
        box = wx.StaticBox( self.panel, -1, 'File Selections')
        sizer = wx.StaticBoxSizer( box, wx.VERTICAL)        
        sizer.Add(dtaFileSizer, 0, wx.EXPAND)
        sizer.Add((2,2), 0)
        sizer.Add(fastaFileSizer, 0, wx.EXPAND)
        
        box2 = wx.StaticBox( self.panel, -1, 'Refining Method')
        sizer2 = wx.StaticBoxSizer( box2, wx.VERTICAL)
        defaultMethod = self.controller.updatedSettings['refiningPars']['choices']['refining method']
        self.refiningMethodEntry = wx.StaticText( self.panel, -1, defaultMethod)        
        sizer2.Add( self.refiningMethodEntry, 0, wx.EXPAND)
        sizer2.Add((20,20), 0, wx.EXPAND)
        
        self.labelSizer = sizer
        self.refiningMethodSizer = sizer2
        self.dtaFilesEntry = dtaFilesEntry
        self.fastaFilesEntry = fastaFilesEntry



    def CreateRunBttn(self):
        self.runBttn = wx.Button(self.panel, -1, label = 'Run')
        self.runBttn.Bind(wx.EVT_BUTTON, self.OnRunBttn, self.runBttn)



#---RESPONCES-----------------------------------------
    def OnSelectDtaFiles(self, evt):
        wildcard = "_dta text files (*_dta.txt)|*_dta.txt|dta files (*.dta)|*.dta*|All files (*.*)|*.*"
        dlg = wx.FileDialog(self, "Open dta file...", os.getcwd(),
                                        style=wx.OPEN|wx.FD_MULTIPLE, wildcard=wildcard)
        if dlg.ShowModal() == wx.ID_OK:
            self.controller.dtaFileList = dlg.GetPaths()
            self.dtaFilesEntryText = os.path.dirname( self.controller.dtaFileList[0])+'\\'
            self.updateLabels()
            dlg.Destroy()
        evt.Skip()


    def OnSelectFastaFile(self, evt):
        wildcard = "FASTA files (*.fasta)|*.fasta|text files (*.txt)|*.txt|All files (*.*)|*.*"
        dlg = wx.FileDialog(self, "Open FASTA file...", os.getcwd(),
                                        style=wx.OPEN, wildcard=wildcard)
        if dlg.ShowModal() == wx.ID_OK:
            self.controller.fastaFile = dlg.GetPath()
            self.fastaFilesEntryText = str( self.controller.fastaFile)
            self.updateLabels() 
            dlg.Destroy()
        evt.Skip()
        

    def OnLoadSettings(self, evt):
        wildcard = "xml files (*.xml)|*.xml|All files (*.*)|*.*"
        dlg = wx.FileDialog(self, "Open settings file...", os.getcwd(),
                                        style=wx.OPEN, wildcard=wildcard)
        if dlg.ShowModal() == wx.ID_OK:
            self.controller.settingsFile = dlg.GetPath()
            self.controller.getSettings()
            self.OnLoadNewSettingsToMenues() # here update the settings that dialogs load when start
            dlg.Destroy()
        evt.Skip()


        
    def OnSaveSettings(self, evt):
        wildcard = "xml files (*.xml)|*.xml|All files (*.*)|*.*"
        dlg = wx.FileDialog(self, "Save settings file...", os.getcwd(),
                                        style=wx.SAVE, wildcard=wildcard)
        if dlg.ShowModal() == wx.ID_OK:
            writeSettingsToXML( self.controller.updatedSettings, dlg.GetPath()) #VLAD to fix path
            dlg.Destroy()
        evt.Skip()
        


    def OnExitProgramItem(self, evt):
        self.Close(True)


    def updateLabels(self):
        self.dtaFilesEntry.SetLabel( self.dtaFilesEntryText)
        self.fastaFilesEntry.SetLabel( self.fastaFilesEntryText)
        self.sizer.Fit(self)

    def updateRefiningMethod(self):
        self.refiningMethodEntry.SetLabel( self.controller.updatedSettings['refiningPars']['choices']['refining method'])
        # it is not necessary since the names are short anyway
#        self.sizer.Fit(self)

    def OnHelp(self, evt):
        aboutText  = 'DtaRefinery\n'
        aboutText += 'Version %s\n' % self.controller.version
        aboutText += 'Pacific Northwest National Laboratory, 2019\n'
        aboutText += 'Developed by Vlad Petyuk'
        wx.MessageBox( aboutText, "About")
        evt.Skip()


    def checkFileEntries( self):
        if ((self.controller.fastaFile == None) and
            (self.controller.dtaFileList == [])):
            wx.MessageBox('Please select dta and FASTA files!')
            return False
        elif self.controller.fastaFile == None:
            wx.MessageBox('Please select FASTA file!')
            return False
        elif self.controller.dtaFileList == []:
            wx.MessageBox('Please select dta file(s)!')
            return False
        else:
            return True

    def OnRunBttn(self, evt):
        if self.checkFileEntries():
            self.runBttn.Disable()
            self.controller.Run()
            self.runBttn.Enable()
        evt.Skip()

    def OnLoadNewSettingsToMenues( self):
        self.menuOtherSets.OnLoadNewSettings()
        self.menuCorrPars.OnLoadNewSettings()





class App(wx.App):
    def __init__(self, dtaRefineryDir):
        self.dtaRefineryDir = dtaRefineryDir        
        wx.App.__init__(self, 0)
    def OnInit(self):
        frame = MainFrame( self.dtaRefineryDir)
        frame.Show(True)
        return True




    


def mainFromGUI( dtaRefineryDir):
    defaultSettingsFile = os.path.join( dtaRefineryDir, 'default_settings.xml')
    if not os.path.exists(defaultSettingsFile):
        print('\n')
        print('INPUT ERROR!')
        print('the default settings file %s' % defaultSettingsFile)
        print('does not exists!\n')
        raise Exception
    app = App( dtaRefineryDir)
    app.MainLoop()


def mainFromCommandLine( dtaRefineryDir, settingFile, cdtaFile, fastaFile):

    if not os.path.exists(settingFile):
        print('\n')
        print('INPUT ERROR!')
        print('the specified settings file %s' % settingFile)
        print('does not exists!\n')
        raise Exception
    if not os.path.exists(cdtaFile):
        print('\n')
        print('INPUT ERROR!'        )
        print('the specified cdta file %s' % cdtaFile)
        print('does not exists!\n')
        raise Exception
    if not os.path.exists(fastaFile):
        print('\n')
        print('INPUT ERROR!'        )
        print('the specified fasta file %s' % fastaFile)
        print('does not exists!\n')
        raise Exception
       
    controller = Controller( dtaRefineryDir)
    controller.version = __VERSION__    
    controller.fastaFile    = fastaFile
    controller.dtaFileList  = [cdtaFile]
    controller.settingsFile = settingFile
    controller.getSettings()    
    controller.Run()


if __name__ == "__main__":
    if len(sys.argv) == 4:
        dtaRefineryDir = os.path.dirname(sys.argv[0])
        settingFile, cdtaFile, fastaFile = sys.argv[1:]
        mainFromCommandLine( dtaRefineryDir, settingFile, cdtaFile, fastaFile)
    elif len(sys.argv) == 1:
        dtaRefineryDir = os.path.dirname(sys.argv[0])
        mainFromGUI( dtaRefineryDir)
    else:
        print('wrong number of arguments')
    
	
