import datetime
import collections
import json
import os
import sys
import wx

print "\nPlease wait while the application loads modules..."

from wx.html import HtmlWindow
from photologger.data import Data
from photologger import images


COLOR_INCOMPLETE = "PINK"
COLOR_COMPLETE = (150, 255, 140)  # alt: "SPRING GREEN"


class TestFrame(wx.Frame):
    def __init__(self):
        self.frame_size = (1060, 620)
        self.x = wx.SystemSettings.GetMetric(wx.SYS_SCREEN_X)
        self.y = wx.SystemSettings.GetMetric(wx.SYS_SCREEN_Y)
        posx = (self.x / 2) - (self.frame_size[0] / 2)
        posy = (self.y / 2) - (self.frame_size[1] / 2)

        wx.Frame.__init__(self, None, -1, "Photo Logger  |  Untitled",
                          pos=(posx, posy),
                          # style uses default style but disables resizability
                          style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER)

        # Icon
        cam = images.camera
        icon = cam.GetIcon()
        self.SetIcon(icon)

        self.InitUI()

    def InitUI(self):
        wx.CallAfter(self.loadDelay)

        self.panel = wx.Panel(self, -1)

        # create the labels/dropdowns for field choices
        self.choice_list = ["Photo File Name",
                            "EXIF Latitude",
                            "EXIF Longitude",
                            "EXIF Bearing",
                            "EXIF TimeStamp",
                            "<None>"]
        self.fc_choices = []
        self.filter_value_list = []

        self.font_choices = ["Courier", "Helvetica", "Times-Roman"]
        # future font implementation "Arial", "Calibri",
        #                            "Georgia", "Vera", "Verdana"
        self.createMenuBar()
        self.createChoosers()
        self.createSidebar()
        self.createRemainingConfig()
        self.addSizers()

        # text controls for new/open/save config
        self.all_ctrls = [
            # file path choosers
            "FileGDBTextCtrl", "fc_combobox",
            "PhotoDirTextCtrl", "OutputPDFTextCtrl",

            # sidebar
            "sidebarCombo1", "aliasTextCtrl1",
            "sidebarCombo2", "aliasTextCtrl2",
            "sidebarCombo3", "aliasTextCtrl3",
            "sidebarCombo4", "aliasTextCtrl4",
            "sidebarCombo5", "aliasTextCtrl5",
            "sidebarCombo6", "aliasTextCtrl6",
            "sidebarCombo7", "aliasTextCtrl7",
            "sidebarCombo8", "aliasTextCtrl8",

            # other config
            "photoIDCombo",
            "primarySortCombo",
            "pageBreakCheckBox",
            "secondarySortCombo",
            "filterSortCombo", "filterValueCombo",
            "headerTextCtrl1", "headerTextCtrl2",
            "pageNumberingCheckBox",
            "fontFaceSelectionCtrl", "fontSizeSpinCtrl", "leadingSpinCtrl",
            "logoTextCtrl",
        ]

        self.chooser_ctrls = ["FileGDBTextCtrl", "PhotoDirTextCtrl",
                              "OutputPDFTextCtrl"]
        # does not include font face combo
        self.combo_ctrls = [ctrl for ctrl in self.all_ctrls if "Combo" in ctrl]

        # for new/open/save config
        self.config_file_path = None
        self.data = self.InitData(self.all_ctrls)
        # bind wx.Frame to OnCloseWindow
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
        print "Modules loaded; application is running...\n"

    def InitData(self, ctrls):
        data = collections.OrderedDict()
        for item in ctrls:
            data[item] = ""

        # defaults
        data["primarySortCombo"] = "Photo File Name"
        data["pageBreakCheckBox"] = False
        data["pageNumberingCheckBox"] = False
        data["fontFaceSelectionCtrl"] = "Helvetica"
        data["fontSizeSpinCtrl"] = 10
        data["leadingSpinCtrl"] = 12
        data["logoTextCtrl"] = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "logo\logo-gsi.png")
        return data

# Menu Creation ###############################################################

    def menuData(self):
        return [("&File", (
                ("&New Config File\tCtrl-N", "", self.OnNew),
                ("&Open Existing Config\tCtrl-O", "", self.OnLoad),
                ("", "", ""),
                ("&Save\tCtrl-S", "", self.OnSave),
                ("&Save As...\tCtrl-Shift-S", "", self.OnSaveAs),
                ("", "", ""),
                ("&Quit\tCtrl-Q", "", self.OnCloseWindow)
                )),
                ("&Run", (("&Run\tCtrl-R", "", self.OnRun),)),
                ("&Help", (("&About", "", self.OnAbout),)),
                ]

    def createMenuBar(self):
        menuBar = wx.MenuBar()

        for eachMenuData in self.menuData():
            menuLabel = eachMenuData[0]
            menuItems = eachMenuData[1]
            menuBar.Append(self.createMenu(menuItems), menuLabel)
        self.SetMenuBar(menuBar)

    def createMenu(self, menuData):
        menu = wx.Menu()
        for eachItem in menuData:
            if len(eachItem) == 2:
                label = eachItem[0]
                subMenu = self.createMenu(eachItem[1])
                menu.AppendMenu(wx.NewId(), label, subMenu)
            else:
                self.createMenuItem(menu, *eachItem)
        return menu

    def createMenuItem(self, menu, label, status, handler,
                       kind=wx.ITEM_NORMAL):
        if not label:
            menu.AppendSeparator()
            return
        menuItem = menu.Append(-1, label, status, kind)
        self.Bind(wx.EVT_MENU, handler, menuItem)

# Data Entry Controls #########################################################

    def createChoosers(self):
        # create the label/text/dialogs for files and directories
        def make_choosers(label, button_handler, textCtrlName):
            label_text = wx.StaticText(self.panel, -1, label, size=(135, -1),
                                       style=wx.ALIGN_RIGHT)
            text = wx.TextCtrl(self.panel, -1, "", size=(588, -1),
                               name=textCtrlName)
            text.SetValue("<Browse to a path>")
            text.Bind(wx.EVT_TEXT, self.OnDataEntry)
            text.SetEditable(False)
            text.SetBackgroundColour(COLOR_INCOMPLETE)
            button = wx.Button(self.panel, label="Browse")
            button.Bind(wx.EVT_BUTTON, button_handler)
            if textCtrlName == "FileGDBTextCtrl":
                text.Bind(wx.EVT_TEXT, self.OnGDBSelectionHandler)
                self.chooserComboBox = wx.ComboBox(
                    self.panel, -1, size=(200, -1), choices=[],
                    value="<Choose a Featureclass>", name="fc_combobox")
                self.chooserComboBox.SetBackgroundColour(COLOR_INCOMPLETE)
                self.chooserComboBox.SetEditable(False)
                self.chooserComboBox.Bind(wx.EVT_COMBOBOX,
                                          self.OnFCSelectionHandler)
                # use EVT_TEXT instead of EVT_COMBOBOX because EVT_TEXT will
                # be fired if loading from config
                self.chooserComboBox.Bind(wx.EVT_TEXT,
                                          self.OnFCSelectionHandler)
                self.chooserComboBox.Bind(wx.EVT_TEXT, self.OnDataEntry)

            sizer = wx.BoxSizer(wx.HORIZONTAL)
            sizer.Add(label_text, flag=wx.ALIGN_CENTER_VERTICAL)
            sizer.Add(text, 1, flag=wx.ALIGN_CENTER_VERTICAL)
            sizer.Add(button, flag=wx.EXPAND)
            if textCtrlName == "FileGDBTextCtrl":
                sizer.Add(self.chooserComboBox, flag=wx.ALIGN_CENTER_VERTICAL)
            return sizer

        self.chooser_info = (
            ("File GDB  ", self.OnGDBDlgButton, "FileGDBTextCtrl"),
            ("Photo Directory  ",
                self.OnPhotoDirDlgButton, "PhotoDirTextCtrl"),
            # ("Working Directory  ",
            #     self.OnWorkingDirDlgButton, "WorkingDirTextCtrl"),
            ("Output PDF  ", self.OnOutputPDFDlgButton, "OutputPDFTextCtrl"))

        chooser_sizers = [make_choosers(label, button_handler, textCtrlName)
                          for (label, button_handler, textCtrlName)
                          in self.chooser_info]

        self.pathSizer = wx.BoxSizer(wx.VERTICAL)

        for sizer in chooser_sizers:
            self.pathSizer.Add(sizer, flag=wx.EXPAND)

        self.box = wx.StaticBox(self.panel, -1, "File / Directory Locations")
        self.staticSizer = wx.StaticBoxSizer(self.box, wx.VERTICAL)
        self.staticSizer.Add(self.pathSizer, 0, wx.ALL, 5)

    def createSidebar(self):
        def make_sidebar_config(i):
            field_label = wx.StaticText(
                self.panel, -1, "Field " + str(i + 1) + "  ",
                style=wx.ALIGN_RIGHT)
            self.sidebar_combo_box = wx.ComboBox(
                self.panel, -1, size=(200, -1), choices=self.choice_list,
                value="<None>", name="sidebarCombo" + str(i + 1))
            self.sidebar_combo_box.SetEditable(False)
            self.sidebar_combo_box.SetBackgroundColour("WHITE")
            self.sidebar_combo_box.Bind(wx.EVT_TEXT, self.OnDataEntry)
            field_alias_label = wx.StaticText(self.panel, -1,
                                              "  Alias ", style=wx.ALIGN_RIGHT)
            field_alias_text = wx.TextCtrl(self.panel, -1, "", size=(200, -1),
                                           name="aliasTextCtrl" + str(i + 1))
            field_alias_text.Bind(wx.EVT_TEXT, self.OnDataEntry)
            field_sizer = wx.BoxSizer(wx.HORIZONTAL)
            field_sizer.Add(field_label, flag=wx.ALIGN_CENTER_VERTICAL)
            field_sizer.Add(self.sidebar_combo_box)
            field_sizer.Add(field_alias_label, flag=wx.ALIGN_CENTER_VERTICAL)
            field_sizer.Add(field_alias_text)
            return field_sizer

        sidebar_sizers = [make_sidebar_config(i) for i in range(8)]

        self.box2 = wx.StaticBox(self.panel, -1, "Sidebar Config")
        self.staticSizer2 = wx.StaticBoxSizer(self.box2, wx.VERTICAL)
        for sizer in sidebar_sizers:
            self.staticSizer2.Add(sizer, 0, wx.ALL, 5)

        # Decorative image

        self.image_box = wx.StaticBox(self.panel, -1)
        self.image_box_sizer = wx.StaticBoxSizer(self.image_box, wx.HORIZONTAL)

        image = images.camera_to_pdf_blue.GetImage()
        w = image.GetWidth()
        h = image.GetHeight()
        image2 = image.Scale(w / 1.6, h / 1.6)

        img = wx.StaticBitmap(self.panel, -1, wx.BitmapFromImage(image2))

        self.image_box_sizer.Add(img, 0, wx.ALL, 10)
        self.horizontal_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.horizontal_sizer.Add((156, -1))
        self.horizontal_sizer.Add(self.image_box_sizer, 0, wx.ALL, 5)
        self.staticSizer2.Add(self.horizontal_sizer, 0, wx.ALL, 0)

    def createRemainingConfig(self):
        # create the labels, etc. for other config options
        # Photo ID
        self.PhotoIDLbl = wx.StaticText(self.panel, -1, "Photo ID Field  ",
                                        style=wx.ALIGN_RIGHT)
        self.PhotoIDCombo = wx.ComboBox(self.panel, -1, size=(200, -1),
                                        choices=self.choice_list,
                                        value="<None>", name="photoIDCombo")
        self.PhotoIDCombo.SetEditable(False)
        self.PhotoIDCombo.SetBackgroundColour("WHITE")
        self.PhotoIDCombo.Bind(wx.EVT_TEXT, self.OnDataEntry)
        self.PhotoIDsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.PhotoIDsizer.Add(self.PhotoIDLbl, flag=wx.ALIGN_CENTER_VERTICAL)
        self.PhotoIDsizer.Add(self.PhotoIDCombo)

        # Primary Sort Field
        self.Sort1Lbl = wx.StaticText(self.panel, -1, "Primary Sort Field  ",
                                      style=wx.ALIGN_RIGHT)
        # remove <None>
        self.Sort1Combo = wx.ComboBox(self.panel, -1, size=(200, -1),
                                      choices=self.choice_list,
                                      value="Photo File Name",
                                      name="primarySortCombo")
        self.Sort1Combo.SetEditable(False)
        self.Sort1Combo.SetBackgroundColour("WHITE")
        self.Sort1Combo.Bind(wx.EVT_TEXT, self.OnDataEntry)
        self.Sort1sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.Sort1sizer.Add(self.Sort1Lbl, flag=wx.ALIGN_CENTER_VERTICAL)
        self.Sort1sizer.Add(self.Sort1Combo)

        # Group/Page Break on Primary Sort?
        self.GroupCheckbox = wx.CheckBox(self.panel, -1,
                                         " Page Break on Change to Primary Sort\
                                          Value?", size=(330, 20),
                                         name="pageBreakCheckBox")
        self.GroupCheckbox.Bind(wx.EVT_CHECKBOX, self.OnDataEntry)
        self.GroupCheckboxSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.GroupCheckboxSizer.Add(self.GroupCheckbox)

        # Secondary Sort Field
        self.Sort2Lbl = wx.StaticText(self.panel, -1, "Secondary Sort Field  ",
                                      style=wx.ALIGN_RIGHT)
        self.Sort2Combo = wx.ComboBox(self.panel, -1, size=(200, -1),
                                      choices=self.choice_list, value="<None>",
                                      name="secondarySortCombo")
        self.Sort2Combo.SetEditable(False)
        self.Sort2Combo.SetBackgroundColour("WHITE")
        self.Sort2Combo.Bind(wx.EVT_TEXT, self.OnDataEntry)
        self.Sort2sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.Sort2sizer.Add(self.Sort2Lbl, flag=wx.ALIGN_CENTER_VERTICAL)
        self.Sort2sizer.Add(self.Sort2Combo)

        # Filter
        self.FilterLbl = wx.StaticText(self.panel, -1, "Filter Field  ",
                                       style=wx.ALIGN_RIGHT)
        self.FilterCombo = wx.ComboBox(self.panel, -1, size=(200, -1),
                                       choices=self.choice_list,
                                       value="<None>", name="filterSortCombo")
        self.FilterCombo.SetEditable(False)
        self.FilterCombo.SetBackgroundColour("WHITE")
        self.FilterCombo.Bind(wx.EVT_COMBOBOX, self.OnFilterSelectHandler)
        self.FilterCombo.Bind(wx.EVT_TEXT, self.OnDataEntry)

        self.FilterValueLbl = wx.StaticText(self.panel, -1,
                                            "    Filter Value  ",
                                            style=wx.ALIGN_RIGHT)
        self.FilterValueCombo = wx.ComboBox(self.panel, -1, size=(100, -1),
                                            choices=self.filter_value_list,
                                            value="<None>",
                                            name="filterValueCombo")
        self.FilterValueCombo.SetEditable(False)
        self.FilterValueCombo.SetBackgroundColour("WHITE")
        self.FilterValueCombo.Bind(wx.EVT_TEXT, self.OnDataEntry)

        self.FilterSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.FilterSizer.Add(self.FilterLbl, flag=wx.ALIGN_CENTER_VERTICAL)
        self.FilterSizer.Add(self.FilterCombo)
        self.FilterSizer.Add(self.FilterValueLbl,
                             flag=wx.ALIGN_CENTER_VERTICAL)
        self.FilterSizer.Add(self.FilterValueCombo)

        # Header Text 1
        self.Header1Lbl = wx.StaticText(self.panel, -1, "Header Text 1  ",
                                        style=wx.ALIGN_RIGHT)
        self.Header1Text = wx.TextCtrl(self.panel, -1, "", size=(200, -1),
                                       name="headerTextCtrl1")
        self.Header1Text.Bind(wx.EVT_TEXT, self.OnDataEntry)
        self.Header1sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.Header1sizer.Add(self.Header1Lbl, flag=wx.ALIGN_CENTER_VERTICAL)
        self.Header1sizer.Add(self.Header1Text)

        # Header Text 2
        self.Header2Lbl = wx.StaticText(self.panel, -1, "Header Text 2  ",
                                        style=wx.ALIGN_RIGHT)
        self.Header2Text = wx.TextCtrl(self.panel, -1, "", size=(200, -1),
                                       name="headerTextCtrl2")
        self.Header2Text.Bind(wx.EVT_TEXT, self.OnDataEntry)
        self.Header2sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.Header2sizer.Add(self.Header2Lbl, flag=wx.ALIGN_CENTER_VERTICAL)
        self.Header2sizer.Add(self.Header2Text)

        # Page Numbering
        self.PageNumberingCheckbox = wx.CheckBox(self.panel, -1,
                                                 " Enable Page Numbering?",
                                                 size=(200, 20),
                                                 name="pageNumberingCheckBox")
        self.PageNumberingCheckbox.Bind(wx.EVT_CHECKBOX, self.OnDataEntry)
        self.PageNumberingSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.PageNumberingSizer.Add(self.PageNumberingCheckbox)

        # Font and Font size
        self.FontFaceLbl = wx.StaticText(self.panel, -1, "Font  ",
                                         style=wx.ALIGN_RIGHT)
        self.FontFaceSelectionCtrl = wx.ComboBox(self.panel, -1,
                                                 size=(200, -1),
                                                 choices=self.font_choices,
                                                 value="Helvetica",
                                                 name="fontFaceSelectionCtrl")
        self.FontFaceSelectionCtrl.Bind(wx.EVT_COMBOBOX, self.OnFontSelect)
        self.FontSizeLbl = wx.StaticText(self.panel, -1, "    Font Size  ",
                                         style=wx.ALIGN_RIGHT)
        self.FontSizeSpinCtrl = wx.SpinCtrl(self.panel, -1, "", size=(100, -1),
                                            style=wx.SP_ARROW_KEYS,
                                            min=4, max=30, initial=10,
                                            name="fontSizeSpinCtrl")
        self.FontSizeSpinCtrl.Bind(wx.EVT_TEXT, self.OnDataEntry)
        self.Fontsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.Fontsizer.Add(self.FontFaceLbl, flag=wx.ALIGN_CENTER_VERTICAL)
        self.Fontsizer.Add(self.FontFaceSelectionCtrl)
        self.Fontsizer.Add(self.FontSizeLbl, flag=wx.ALIGN_CENTER_VERTICAL)
        self.Fontsizer.Add(self.FontSizeSpinCtrl)

        # Leading
        self.LeadingLbl = wx.StaticText(self.panel, -1, "Font Leading  ",
                                        style=wx.ALIGN_RIGHT)
        self.LeadingSpinCtrl = wx.SpinCtrl(self.panel, -1, "", size=(100, -1),
                                           style=wx.SP_ARROW_KEYS,
                                           min=0, max=30, initial=12,
                                           name="leadingSpinCtrl")
        self.LeadingSpinCtrl.Bind(wx.EVT_TEXT, self.OnDataEntry)
        self.Leadingsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.Leadingsizer.Add(self.LeadingLbl, flag=wx.ALIGN_CENTER_VERTICAL)
        self.Leadingsizer.Add(self.LeadingSpinCtrl)

        # Logo
        self.LogoLbl = wx.StaticText(self.panel, -1, "Logo  ",
                                     style=wx.ALIGN_RIGHT)
        self.LogoTextCtrl = wx.TextCtrl(self.panel, -1, "", size=(320, -1),
                                        name="logoTextCtrl")
        default_logo_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "logo\logo-gsi.png")
        self.LogoTextCtrl.SetValue(default_logo_path)
        self.LogoTextCtrl.SetEditable(False)
        self.LogoTextCtrl.Bind(wx.EVT_TEXT, self.OnDataEntry)
        self.LogoBtn = wx.Button(self.panel, label="Browse")
        self.LogoBtn.Bind(wx.EVT_BUTTON, self.OnLogoDlgButton)
        self.LogoSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.LogoSizer.Add(self.LogoLbl, flag=wx.ALIGN_CENTER_VERTICAL)
        self.LogoSizer.Add(self.LogoTextCtrl, 1, flag=wx.ALIGN_CENTER_VERTICAL)
        self.LogoSizer.Add(self.LogoBtn, flag=wx.EXPAND)

        # static box sizers
        self.box3 = wx.StaticBox(self.panel, -1, "Other Config Options")
        self.staticSizer3 = wx.StaticBoxSizer(self.box3, wx.VERTICAL)
        sizers = [self.PhotoIDsizer, self.Sort1sizer, self.GroupCheckboxSizer,
                  self.Sort2sizer, self.FilterSizer, self.Header1sizer,
                  self.Header2sizer, self.PageNumberingSizer, self.Fontsizer,
                  self.Leadingsizer, self.LogoSizer]
        for sizer in sizers:
            self.staticSizer3.Add(sizer, 0, wx.ALL | wx.ALIGN_RIGHT, 5)

    def addSizers(self):
        self.hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox.Add(self.staticSizer2, wx.ALL | wx.LEFT, 5)
        self.hbox.Add(self.staticSizer3, wx.ALL | wx.LEFT, 5)

        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.vbox.Add(self.staticSizer, 0, wx.ALL | wx.LEFT, 5)
        self.vbox.Add(self.hbox, 0, wx.ALL | wx.LEFT, 5)

        self.panel.SetSizer(self.vbox)
        self.Show()
        self.vbox.SetSizeHints(self)

    def createLogger(self):
        """
        http://www.blog.pythonlibrary.org/2009/01/01/wxpython-redirecting-stdout-stderr/
        """
        # prevent open logger windows on consecutive runs
        try:
            self.logging_window.Destroy()
        except:
            pass
        # set position and size
        logging_frame_size = self.GetSize()[0] - 150, self.GetSize()[1] - 150
        logging_frame_pos = (self.GetPosition()[0] + 75,
                             self.GetPosition()[1] + 75)
        self.logging_window = wx.Frame(None, -1, size=logging_frame_size,
                                       pos=logging_frame_pos)

        # create panel with text Ctrl
        log_panel = wx.Panel(self.logging_window, -1)
        style = wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL
        self.log = wx.TextCtrl(log_panel, -1, size=(300, 100), style=style)
        self.log_btn = wx.Button(log_panel, -1, "Close Log")
        self.log_btn.Bind(wx.EVT_BUTTON, self.onLogDismiss)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.log, 1, wx.ALL | wx.EXPAND, 5)
        sizer.Add(self.log_btn, 0, wx.ALL | wx.CENTER, 0)
        log_panel.SetSizer(sizer)

        # redirect text here
        sys.stdout = self.log
        sys.stderr = self.log
        self.logging_window.Show()

# Event Handelers for  New / Load / Save / SaveAs / Quit / About / Run ########

    # For each menu item:
    #   manage config_file_path
    #   manage data
    #   manage title
    #   manage state of controls

    def OnLoad(self, event):
        """Handler for Open Existing Config menu item: load an existing
        configuration (json) file and populate the relevantcontrols."""

        # dialog to get file
        self.configOpenDlg = wx.FileDialog(None, message="Choose a File",
                                           defaultDir="", defaultFile="",
                                           wildcard="*.cfg", style=wx.OPEN,
                                           pos=wx.DefaultPosition)

        if self.configOpenDlg.ShowModal() == wx.ID_OK:
            self.clearCtrls()
            self.config_file_path = self.configOpenDlg.GetPath()
            self.readConfig(self.config_file_path, self.all_ctrls)

            self.SetTitle("Photo Logger  |  " +
                          os.path.basename(self.config_file_path))
        self.configOpenDlg.Destroy()

    def OnNew(self, event):
        """Handler for New menu item: prompt to save; clear all controls."""

        # prompt to save
        retCode = wx.MessageBox(
            "Do you want to save what you've entered\nto a configuration file (.cfg)?",
            "Save?", wx.YES_NO | wx.CANCEL | wx.ICON_QUESTION)
        if retCode == wx.YES:
            self.saveConfig()

        elif retCode == wx.NO:
            self.clearCtrls()
            self.config_file_path = None
            self.SetTitle("Photo Logger  |  Untitled")
            # print json.dumps(self.data, indent=4)

    def clearCtrls(self):
        """Helper method: reset controls."""
        # print "clearCtrls"
        self.data = self.InitData(self.all_ctrls)
        for k, v in self.data.iteritems():
            if k == 'pageBreakCheckBox' or k == 'pageNumberingCheckBox':
                self.FindWindowByName(k).SetValue(False)
            elif k in self.combo_ctrls:
                combo = self.FindWindowByName(k)
                combo.Clear()
                if k in ["filterSortCombo", "filterValueCombo"]:
                    combo.SetValue("<None>")
                elif k == "primarySortCombo":
                    combo.AppendItems(self.choice_list)
                    combo.SetValue("Photo File Name")
                else:
                    combo.AppendItems(self.choice_list)
                    combo.SetValue("<None>")
            elif k == "fc_combobox":
                combo = self.FindWindowByName(k)
                combo.Clear()
                combo.SetValue("<Choose a Featureclass>")
                combo.SetBackgroundColour(COLOR_INCOMPLETE)
            elif k in self.chooser_ctrls:
                chooser = self.FindWindowByName(k)
                chooser.SetValue("<Browse to a path>")
                chooser.SetBackgroundColour(COLOR_INCOMPLETE)
            else:
                self.FindWindowByName(k).SetValue(v)

    def OnSave(self, event):
        """Handler for Save menu item."""
        if self.config_file_path:
            self.writeConfig(self.config_file_path)
        else:
            self.saveConfig()

    def OnSaveAs(self, event):
        """Handler for Save As menu item."""
        self.saveConfig()

    def readConfig(self, path, controls):
        """Helper method: read a config file and populate all controls."""
        # print "readConfig"
        with open(path, 'r') as src:
            self.data = json.load(src,
                                  object_pairs_hook=collections.OrderedDict)
            # print json.dumps(self.data, indent=4)
            if self.data["FileGDBTextCtrl"] != "" and \
               self.data["fc_combobox"] != "":
                self.FindWindowByName("FileGDBTextCtrl").SetValue(
                    self.data["FileGDBTextCtrl"])
                self.OnGDBSelection()

                self.FindWindowByName("fc_combobox").SetValue(
                    self.data["fc_combobox"])
                self.OnFCSelection()

                if self.data["filterSortCombo"] != "":
                    self.FindWindowByName("filterSortCombo").SetValue(
                        self.data["filterSortCombo"])
                    self.OnFilterSelect()

            # populate remaining controls
            for k, v in self.data.iteritems():
                # print k, v
                if k not in ["FileGDBTextCtrl", "fc_combobox",
                             "filterSortCombo"]:
                    self.FindWindowByName(k).SetValue(v)

            # set colors
            for control in self.chooser_ctrls:
                if self.data[control] not in ["<Browse to a path>", ""]:
                    self.FindWindowByName(control).SetBackgroundColour(
                        COLOR_COMPLETE)

    def writeConfig(self, path):
        """Helper method: write data to file."""
        with open(path, 'w') as dest:
            json.dump(self.data, dest, indent=4)
        # print json.dumps(self.data, indent=4)

    def saveConfig(self, ):
        """Helper method: prompt for Save As file, then call writeConfig."""
        self.configSaveDlg = wx.FileDialog(None, message="Save As",
                                           defaultDir="", defaultFile="",
                                           wildcard="*.cfg",
                                           style=wx.SAVE | wx.OVERWRITE_PROMPT,
                                           pos=wx.DefaultPosition)
        if self.configSaveDlg.ShowModal() == wx.ID_OK:
            self.config_file_path = self.configSaveDlg.GetPath()
            # use path to write a file
            self.writeConfig(self.config_file_path)
            self.SetTitle("Photo Logger  |  " +
                          os.path.basename(self.config_file_path))

        self.configSaveDlg.Destroy()
        # print json.dumps(self.data, indent=4)

    def OnCloseWindow(self, event):
        print "Application is closing"
        self.Destroy()
        sys.exit(0)

    def OnRun(self, event):
        self.createLogger()
        print "Start: {}\n".format(datetime.datetime.now())

        # print json.dumps(self.data, indent=4)

        config = self.data
        d = Data(config)
        d.process()
        print "\nEnd: {}\n".format(datetime.datetime.now())

    def OnAbout(self, event):
        dlg = PhotoLoggerAbout(self)
        dlg.ShowModal()
        dlg.Destroy()

# Handlers and misc methods ###################################################

    def OnDataEntry(self, event):
        """Callback for data entry"""
        calling_widget = self.FindWindowById(event.Id)
        name = calling_widget.GetName()
        value = calling_widget.GetValue()
        self.data[name] = value

    def onLogDismiss(self, event):
        self.logging_window.Hide()

    def loadDelay(self):
        wx.FutureCall(1000, self.loadArcpy)

    def loadArcpy(self):
        msg = "Please wait while arcpy imports..."
        busyDlg = wx.BusyInfo(msg, parent=self.panel)
        import arcpy
        busyDlg = None

    def OnGDBSelectionHandler(self, event):
        self.OnGDBSelection()

    def OnGDBSelection(self):
        tc = self.FindWindowByName("FileGDBTextCtrl")
        tc.SetBackgroundColour(COLOR_COMPLETE)
        gdb = tc.GetValue()
        if gdb == "<Browse to a path>":
            pass
        else:
            arcpy.env.workspace = gdb
            fcs = sorted(arcpy.ListFeatureClasses())

            if fcs:
                self.featureclass_dropdown = self.FindWindowByName("fc_combobox")
                self.featureclass_dropdown.Clear()
                self.featureclass_dropdown.AppendItems(fcs)

    def ResetComboControls(self):
        """Helper method: reset all combo controls"""
        fc_combo = self.FindWindowByName("fc_combobox")
        fc_combo.SetBackgroundColour(COLOR_INCOMPLETE)
        fc_combo.Clear()
        fc_combo.SetValue("<Choose a Featureclass>")

        for combo_name in self.combo_ctrls:
            combo = wx.FindWindowByName(combo_name)
            fc_combo.SetBackgroundColour(COLOR_INCOMPLETE)
            combo.Clear()
            combo.SetValue("<None>")

    def OnGDBDlgButton(self, event):
        """Event handler for GDB browse button."""
        self.GDBDlg = wx.DirDialog(None, message="Choose a gdb",
                                   defaultPath="", style=0,
                                   pos=wx.DefaultPosition, size=wx.DefaultSize,
                                   name="wxGDBDirCtrl")
        if self.GDBDlg.ShowModal() == wx.ID_OK:
            control = self.FindWindowByName("FileGDBTextCtrl")
            control.SetBackgroundColour(COLOR_INCOMPLETE)

            self.ResetComboControls()

            gdb_path = self.GDBDlg.GetPath()
            arcpy.env.workspace = gdb_path
            fcs = sorted(arcpy.ListFeatureClasses())
            
            if fcs > 0:
                # unbind EVT_TEXT so that OnGDBSelectionHandler does not fire
                control.Unbind(wx.EVT_TEXT)
                control.SetValue(self.GDBDlg.GetPath())
                # rebind
                control.Bind(wx.EVT_TEXT, self.OnGDBSelectionHandler)
                control.SetBackgroundColour(COLOR_COMPLETE)

                # set choices for featureclass dropdown
                featureclass_dropdown = wx.FindWindowByName("fc_combobox")
                featureclass_dropdown.AppendItems(fcs)

        self.GDBDlg.Destroy()

    def OnFCSelectionHandler(self, event):
        self.OnFCSelection(manually=True)

    def OnFCSelection(self, manually=False):
        """Event handler for featureclass combobox selection."""
        gdb_textctrl = self.FindWindowByName("FileGDBTextCtrl")
        gdb_path = gdb_textctrl.GetValue()
        fc_combobox = self.FindWindowByName("fc_combobox")
        fc_name = fc_combobox.GetValue()
        self.fc_path = os.path.join(gdb_path, fc_name)
        fields = arcpy.Describe(self.fc_path).fields
        shapefield = arcpy.Describe(self.fc_path).shapeFieldName
        fieldnames = [field.name for field in fields]
        if fieldnames > 0:
            fieldnames.remove(shapefield)
            self.choice_list = fieldnames
            self.choice_list.extend(["EXIF Latitude", "EXIF Longitude",
                                     "EXIF Bearing", "EXIF TimeStamp",
                                     "<None>"])
            fc_combobox.SetBackgroundColour(COLOR_COMPLETE)

            # update Sidebar Config combos

            for i in range(8):      # TODO make a flexible number of dropdowns
                sidebarCombo = self.FindWindowByName("sidebarCombo" +
                                                     str(i + 1))
                sidebarCombo.Clear()
                sidebarCombo.AppendItems(self.choice_list)
                if self.data['sidebarCombo' + str(i + 1)] == "":
                    sidebarCombo.SetValue(self.choice_list[-1])
                else:
                    sidebarCombo.SetValue(self.data['sidebarCombo' +
                                          str(i + 1)])

            # update Other Config Options combos

            for combo in ["photoIDCombo", "primarySortCombo",
                          "secondarySortCombo", "filterSortCombo"]:
                otherCombo = self.FindWindowByName(combo)
                otherCombo.Clear()

                if combo in ["photoIDCombo", "filterSortCombo"]:
                    truncated_list = self.choice_list[:]
                    for item in ["EXIF Latitude", "EXIF Longitude",
                                 "EXIF Bearing", "EXIF TimeStamp"]:
                        truncated_list.remove(item)
                    otherCombo.AppendItems(truncated_list)
                else:
                    otherCombo.AppendItems(self.choice_list)

                if combo == "filterSortCombo" and manually is False:
                    otherCombo.SetValue(self.data[combo])
                else:
                    if self.data[combo] != "" and self.data[combo] != "<None>":
                        otherCombo.SetValue(self.data[combo])
                    else:
                        otherCombo.SetValue(self.choice_list[-1])

    def OnFilterSelectHandler(self, event):
        self.OnFilterSelect(manually=True)

    def OnFilterSelect(self, manually=False):
        possible_values = []
        if manually is False:
            self.filterField = self.data['filterSortCombo']
        else:
            self.filterField = self.FilterCombo.GetValue()
        if self.filterField != "<None>":
            with arcpy.da.SearchCursor(self.fc_path,
                                       [self.filterField]) as cursor:
                for row in cursor:
                    possible_values.append(str(row[0]))
            self.filter_value_list = list(set(possible_values))
            self.filter_value_list.append("<None>")
            self.FilterValueCombo.Clear()
            self.FilterValueCombo.AppendItems(self.filter_value_list)
            if manually:
                self.FilterValueCombo.SetValue(self.choice_list[-1])
            else:
                self.FilterValueCombo.SetValue(self.data["filterValueCombo"])
        elif self.filterField == "<None>":
            self.FilterValueCombo.Clear()
            self.filter_value_list = ["<None>"]
            self.FilterValueCombo.AppendItems(self.filter_value_list)
            self.FilterValueCombo.SetValue(self.filter_value_list[-1])

    def OnFontSelect(self, event):
        control = wx.FindWindowByName("fontFaceSelectionCtrl")
        self.data["fontFaceSelectionCtrl"] = control.GetValue()

    def OnPhotoDirDlgButton(self, event):
        """Event handler for Photo Directory dialog."""
        PhotoDirDlg = wx.DirDialog(None, message="Choose a photo directory",
                                   defaultPath="", style=0,
                                   pos=wx.DefaultPosition, size=wx.DefaultSize,
                                   name="wxPhotoDirCtrl")
        if PhotoDirDlg.ShowModal() == wx.ID_OK:
            tc = self.FindWindowByName("PhotoDirTextCtrl")
            tc.SetValue(PhotoDirDlg.GetPath())
            tc.SetBackgroundColour(COLOR_COMPLETE)
        PhotoDirDlg.Destroy()

    def OnOutputPDFDlgButton(self, event):
        """Event handler for Output PDF dialog."""
        PDFDlg = wx.FileDialog(None, message="Choose a file", defaultDir="",
                               defaultFile="", wildcard="*.pdf",
                               style=wx.SAVE | wx.OVERWRITE_PROMPT,
                               pos=wx.DefaultPosition)
        if PDFDlg.ShowModal() == wx.ID_OK:
            tc = self.FindWindowByName("OutputPDFTextCtrl")
            tc.SetValue(PDFDlg.GetPath())
            tc.SetBackgroundColour(COLOR_COMPLETE)
        PDFDlg.Destroy()

    def OnLogoDlgButton(self, event):
        """Event handler for Logo dialog."""
        wildcard = "images (*.png, *.jpg,*.jpeg)|*.png;*.jpg;*.jpeg"
        LogoDlg = wx.FileDialog(None, message="Choose a logo", defaultDir="",
                                defaultFile="", wildcard=wildcard, style=0)
        if LogoDlg.ShowModal() == wx.ID_OK:
            tc = self.FindWindowByName("logoTextCtrl")
            tc.SetValue(LogoDlg.GetPath())
        LogoDlg.Destroy()


class PhotoLoggerAbout(wx.Dialog):
    py_version = "{} {} {}".format(sys.platform, "Python",
                                   sys.version.split()[0])
    platform = list(wx.PlatformInfo[1:])
    platform[0] += (" " + wx.VERSION_STRING)
    wx_info = ", ".join(platform)
    text = """
            <html>
            <body bgcolor="#D0E2F5">
            <center><table bgcolor="#B6D3F1" width="100%" cellspacing="0"
            cellpadding="0" border="1">
            <tr>
            <td align="center"><h1>Photo Logger</h1></td>
            </tr>
            </table>
            </center>
            <p><b>Photo Logger</b> is a Python application written in
            <b>wxPython</b> <br />
            Version 1.0
            <hr />
            Dependencies: <br />
            <ul>
            <li>ArcPy (for reading spatial data)</li>
            <li>piexif (Jpeg exif header info)</li>
            <li>PIL/Pillow (image resizing)</li>
            <li>ReportLab (PDF creation)</li>
            </ul>
            <hr />
            </p>
            Copyright &copy; 2016 Grant Miller-Francisco</p>
            <hr />
            Platform Info: <br />
            {}<br />
            {}
            </body>
            </html>
        """.format(py_version, wx_info)

    def __init__(self, parent):
        about_widget_size = (520, 580)
        self.x = wx.SystemSettings.GetMetric(wx.SYS_SCREEN_X)
        self.y = wx.SystemSettings.GetMetric(wx.SYS_SCREEN_Y)
        posx = (self.x / 2) - (about_widget_size[0] / 2)
        posy = (self.y / 2) - (about_widget_size[1] / 2)
        wx.Dialog.__init__(self, parent, -1, 'About Photo Logger',
                           pos=(posx, posy), size=about_widget_size)
        html = wx.html.HtmlWindow(self)
        html.SetPage(self.text)
        button = wx.Button(self, wx.ID_OK, "Close")
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(html, 1, wx.EXPAND | wx.ALL, 5)
        sizer.Add(button, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        self.SetSizer(sizer)
        self.Layout()


class App(wx.App):

    def OnInit(self):
        self.locale = wx.Locale(wx.LANGUAGE_ENGLISH)
        self.frame = TestFrame()
        self.SetTopWindow(self.frame)
        return True

if __name__ == '__main__':
    app = App()
    app.MainLoop()
