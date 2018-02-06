import os


class Validate(object):
    def __init__(self, config):
        self.config = config
        self.test_for_photo_dir(self.config)
        self.test_for_photo_dir_existence(self.config)
        self.test_for_output_pdf(self.config)
        self.test_photo_id_is_required(self.config)
        self.test_for_primary_sort_if_page_break_bool(self.config)

    def test_for_photo_dir(self, config):
        photo_dir = config['photo_directory']
        if photo_dir == "" or photo_dir == "<Browse to a path>":
            raise Exception("Please provide (at minimum) a photo directory\n")

    def test_for_photo_dir_existence(self, config):
        photo_dir = config['photo_directory']
        if os.path.exists(photo_dir) is False:
            raise Exception("{} not found\n".format(photo_dir))

    def test_for_output_pdf(self, config):
        output_pdf = config['output_pdf']
        if output_pdf == "<Browse to a path>":
            raise Exception("Please provide an output PDF path\n")

    def test_photo_id_is_required(self, config):
        photo_id = config['photo_id_field']
        if photo_id == u"":
            raise Exception("Photo ID field is required\n")

    def test_for_primary_sort_if_page_break_bool(self, config):
        """If user has checked "Page Break on Change to Primary Sort" checkbox,
        then Primary Sort should be populated."""
        if config['page_break_bool'] == u"True":
            if (config['primary_sort_field'] == "" or
                    config['primary_sort_field'] == "<None>"):
                raise Exception("Missing Primary Sort Field\n")

    # (u'FileGDBTextCtrl', u'file_gdb_path'),
    # (u'fc_combobox', u'featureclass_name'),
    # (u'PhotoDirTextCtrl', u'photo_directory'),
    # (u'WorkingDirTextCtrl', u'working_directory'),
    # (u'OutputPDFTextCtrl', u'output_pdf'),
    # (u'sidebarCombo1', u'sidebar_field1'),
    # (u'sidebarCombo2', u'sidebar_field2'),
    # (u'sidebarCombo3', u'sidebar_field3'),
    # (u'sidebarCombo4', u'sidebar_field4'),
    # (u'sidebarCombo5', u'sidebar_field5'),
    # (u'sidebarCombo6', u'sidebar_field6'),
    # (u'sidebarCombo7', u'sidebar_field7'),
    # (u'sidebarCombo8', u'sidebar_field8'),
    # (u'aliasTextCtrl1', u'sidebar_alias1'),
    # (u'aliasTextCtrl2', u'sidebar_alias2'),
    # (u'aliasTextCtrl3', u'sidebar_alias3'),
    # (u'aliasTextCtrl4', u'sidebar_alias4'),
    # (u'aliasTextCtrl5', u'sidebar_alias5'),
    # (u'aliasTextCtrl6', u'sidebar_alias6'),
    # (u'aliasTextCtrl7', u'sidebar_alias7'),
    # (u'aliasTextCtrl8', u'sidebar_alias8'),
    # (u'photoIDCombo', u'photo_id_field'),
    # (u'primarySortCombo', u'primary_sort_field'),
    # (u'pageBreakCheckBox', u'page_break_bool'),
    # (u'secondarySortCombo', u'secondary_sort_field'),
    # (u'filterSortCombo', u'filter_field'),
    # (u'filterValueCombo', u'filter_field_value'),
    # (u'headerTextCtrl1', u'header_text_1'),
    # (u'headerTextCtrl2', u'header_text_2'),
    # (u'pageNumberingCheckBox', u'page_numbering_bool'),
    # (u'fontFaceSelectionCtrl', u'font_face'),
    # (u'fontSizeSpinCtrl', u'font_size'),
    # (u'leadingSpinCtrl', u'leading'),
    # (u'logoTextCtrl', u'logo'),
