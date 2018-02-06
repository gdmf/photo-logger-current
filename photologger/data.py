import collections
import csv
import datetime
import glob
import os
import sys
from . import exif_reader
from . import formatter
from . import PDF
from . import reader
from . import validator


class Data(object):

    def __init__(self, config):

        self.config = config

        self.key_map = collections.OrderedDict([
            (u'FileGDBTextCtrl', u'file_gdb_path'),
            (u'fc_combobox', u'featureclass_name'),
            (u'PhotoDirTextCtrl', u'photo_directory'),
            (u'OutputPDFTextCtrl', u'output_pdf'),
            (u'sidebarCombo1', u'sidebar_field1'),
            (u'sidebarCombo2', u'sidebar_field2'),
            (u'sidebarCombo3', u'sidebar_field3'),
            (u'sidebarCombo4', u'sidebar_field4'),
            (u'sidebarCombo5', u'sidebar_field5'),
            (u'sidebarCombo6', u'sidebar_field6'),
            (u'sidebarCombo7', u'sidebar_field7'),
            (u'sidebarCombo8', u'sidebar_field8'),
            (u'aliasTextCtrl1', u'sidebar_alias1'),
            (u'aliasTextCtrl2', u'sidebar_alias2'),
            (u'aliasTextCtrl3', u'sidebar_alias3'),
            (u'aliasTextCtrl4', u'sidebar_alias4'),
            (u'aliasTextCtrl5', u'sidebar_alias5'),
            (u'aliasTextCtrl6', u'sidebar_alias6'),
            (u'aliasTextCtrl7', u'sidebar_alias7'),
            (u'aliasTextCtrl8', u'sidebar_alias8'),
            (u'photoIDCombo', u'photo_id_field'),
            (u'primarySortCombo', u'primary_sort_field'),
            (u'pageBreakCheckBox', u'page_break_bool'),
            (u'secondarySortCombo', u'secondary_sort_field'),
            (u'filterSortCombo', u'filter_field'),
            (u'filterValueCombo', u'filter_field_value'),
            (u'headerTextCtrl1', u'header_text_1'),
            (u'headerTextCtrl2', u'header_text_2'),
            (u'pageNumberingCheckBox', u'page_numbering_bool'),
            (u'fontFaceSelectionCtrl', u'font_face'),
            (u'fontSizeSpinCtrl', u'font_size'),
            (u'leadingSpinCtrl', u'leading'),
            (u'logoTextCtrl', u'logo'),
        ])

    def process(self):
        """Calls all processing functions -- path normalization, key mapping,
        data loading, photo path creation, filtering and sorting, and PDF
        creation."""
        self.config = self.remap_keys(self.config, self.key_map)
        self.config = self.normalize_paths(self.config)

        # Conditionals testing for gdb-less mode
        if self.config['featureclass_name'] == "<Choose a Featureclass>":
            if (self.config['photo_directory'] != "" and
                    self.config['photo_directory'] != "<Browse to a path>" and
                    self.config['output_pdf'] != "" and
                    self.config['output_pdf'] != "<Browse to a path>"):
                self.config['photo_id_field'] = 'Photo File Name'

        try:
            validator.Validate(self.config)
        except Exception, e:
            print e
            return

        # Test if in gdb-less mode:
        if self.config['featureclass_name'] == "<Choose a Featureclass>":
            if (self.config['photo_directory'] != "" and
                    self.config['output_pdf'] != ""):

                self.photo_paths, self.photo_path_dict = self.get_photo_paths(
                    self.config)
                self.data = self.get_exif_data(
                    self.config['photo_directory'])

                # skip photo id match, they will all just match

                # skip self.filter_records_by_filter_field
                if (self.config['primary_sort_field'] != '' and
                        self.config['primary_sort_field'] != '<None>'):
                    self.sorted_records = self.sort_records_by_sort_fields(
                        self.data, self.config)
                else:
                    self.sorted_records = self.data

                self.formatted_data = self.format_data_by_sidebar_fields(
                    self.sorted_records, self.config)

                self.generate_pdf(self.formatted_data,
                                  self.config,
                                  self.photo_path_dict)

        else:
            # sometimes there will be fieldnames, sometimes there won't
            self.fieldnames, self.data = self.load_data(self.config)

            self.photo_paths, self.photo_path_dict = self.get_photo_paths(
                self.config)

            self.filtered_by_filter_field = self.filter_records_by_filter_field(
                self.data, self.config)

            self.filtered_by_photo_id_match = self.filter_records_by_photo_id_match(
                self.fieldnames, self.filtered_by_filter_field, self.config, self.photo_paths)

            self.sorted_records = self.sort_records_by_sort_fields(
                self.filtered_by_photo_id_match, self.config)

            self.formatted_data = self.format_data_by_sidebar_fields(
                self.sorted_records, self.config)

            self.generate_pdf(
                self.formatted_data, self.config, self.photo_path_dict)

    def remap_keys(self, config, key_map):
        # remap config keys from gui to more funcional names
        remapped_config = collections.OrderedDict()
        for k, v in config.items():
            remapped_config[key_map[k]] = v
        return remapped_config

    def normalize_paths(self, config):
        path_keys = [u"file_gdb_path", u"photo_directory",
                     u"output_pdf", u"logo"]
        for key in path_keys:
            # os.path.normpath("") ==> '.' -- thus the need for if-statement
            if config[key] != "":
                str_path = str(config[key])
                encoded_path = str_path.encode('string-escape')
                normalized_path = os.path.normpath(encoded_path)
                config[key] = os.path.normpath(normalized_path)
        return config

    def get_fc_data(self, config):
        featureclass_path = os.path.join(config['file_gdb_path'],
                                         config['featureclass_name'])
        fieldnames, data = reader.read_fc(featureclass_path)
        return fieldnames, data

    def get_exif_data(self, photo_dir):     # ##### config
        d = exif_reader.read(photo_dir)     # ####### config['photo_directory']
        data = []

        for record in d:
            record_dict = {
                'Photo File Name': record['Photo File Name'],
                'EXIF TimeStamp': formatter.datetime_from_exif_header(
                    record['datetime']),
                'EXIF Latitude': formatter.dd_from_exif_coord(
                    record['latitude'], record['latitude_ref']),
                'EXIF Longitude': formatter.dd_from_exif_coord(
                    record['longitude'], record['longitude_ref']),
                'EXIF Bearing': formatter.bearing_from_exif_image_direction(
                    record['image_direction'], record['image_direction_ref']),
            }
            data.append(record_dict)
        return data

    def load_data(self, config):

        # find out which controls have EXIF values
        combo_controls = [u'sidebar_field1', u'sidebar_field2',
                          u'sidebar_field3', u'sidebar_field4',
                          u'sidebar_field5', u'sidebar_field6',
                          u'sidebar_field7', u'sidebar_field8',
                          u'photo_id_field', u'primary_sort_field',
                          u'secondary_sort_field', u'filter_field']

        combo_values = [config[control] for control in combo_controls]

        exif_fieldnames = [u"EXIF Latitude", u"EXIF Longitude",
                           u"EXIF Bearing", u"EXIF TimeStamp"]

        # False means there is at least one EXIF field
        if set(combo_values).isdisjoint(exif_fieldnames):
            # CASE: no exif
            fieldnames, data = self.get_fc_data(self.config)
            return fieldnames, data

        elif config['file_gdb_path'] == u"<Browse to a path>":      #
            # CASE: all Exif
            data = self.get_exif_data(config['photo_directory'])
            fieldnames = []
            return fieldnames, data

        else:
            # CASE: mix
            fieldnames, fc_data = self.get_fc_data(self.config)
            exif_data = self.get_exif_data(config['photo_directory'])
            data = []

            # update based on photo_id match
            for d in fc_data:
                photo_id_key = d[self.config['photo_id_field']]
                # more keys at this point than exif data
                for item in exif_data:
                    if photo_id_key in item.values():
                        d.update(item)
                        del d['Photo File Name']
                data.append(d)
            fieldnames.extend(['EXIF Longitude',
                               'EXIF TimeStamp',
                               'EXIF Latitude',
                               'EXIF Bearing'])
            return fieldnames, data

    def get_photo_paths(self, config):
        """
        Return a list of photo file names (with extensions stripped)
        and a dict with keys = photo name and values = photo path
        """
        photo_directory = config['photo_directory']

        # create a dict mapping photo_id to photo path
        photo_path_dict = {}

        # grab all files with jpg extension
        os.chdir(photo_directory)
        extensions = ('*.jpg', '*.JPG', '*.jpeg', '*.JPEG')
        photos = []
        for extension in extensions:
            photos.extend(glob.glob(extension))

        for photo in photos:
            photo_base = os.path.splitext(photo)[0]
            photo_path = os.path.join(photo_directory, photo)
            photo_path_dict[photo_base] = photo_path

        # get list of processed photo file names with extensions stripped
        processed_photos_list = [os.path.splitext(photo)[0]
                                 for photo in os.listdir(photo_directory)]
        return processed_photos_list, photo_path_dict

    # SORTING AND FILTERING
    # only get rid of fields (filter by sidebar fields) as a last step.
    # you may need fields that are not in sidebar fields in order to sort
    # or filter

    def filter_records_by_filter_field(self, data, config):
        """Return only those records in the data where the value matches the
        'filter_field_value'."""
        filter_value = config['filter_field_value']
        if filter_value != '' and filter_value != u'<None>':
            # print filter_value
            return [record for record in data
                    if record[config['filter_field']] == filter_value]
        else:
            return data

    def filter_records_by_photo_id_match(self, fieldnames, data, config, photo_paths):
        """Return only those records in the data with a match in the list
        of photos."""
        # records loaded from featureclass will have config['photo_id_field']
        # records loaded from exif will have record['photo_id']

        # return [record for record in data
        #         if record[config['photo_id_field']] in photo_paths]

        # This seems like the logical place to log photos not matched

        pdf_path = config['output_pdf']
        now = "{:%Y%m%d-%H%M%S}".format(datetime.datetime.now())
        log_path = os.path.splitext(pdf_path)[0] + '_{}_log.csv'.format(now)
        with open(log_path, 'wb') as log:

            filtered_data = []

            fieldnames.append("LOCATED")
            dw = csv.DictWriter(log, fieldnames=fieldnames)
            dw.writeheader()

            for record in data:
                if config['photo_id_field'] != u'<None>':
                    photo_id = record[config['photo_id_field']]
                elif record['photo_id']:
                    photo_id = record['photo_id']
                else:
                    print "No photo ID"
                    sys.exit()

                if photo_id in photo_paths:
                    record["LOCATED"] = "YES"
                    dw.writerow(record)
                    filtered_data.append(record)
                else:
                    record["LOCATED"] = "NO"
                    dw.writerow(record)

            return filtered_data

    def sort_records_by_sort_fields(self, data, config):
        """Sort records by optional primary and secondary sort fields."""
        sort_fields = []
        sort_fields.append(config['primary_sort_field'])
        sort_fields.append(config['secondary_sort_field'])
        return sorted(data, key=lambda s: [s[key] for key in sort_fields
                                           if key != "" and key != "<None>"])

    def make_sidebar_field_keys(self, data, config):
        """Return a list of (sidebar_field, alias) tuples."""
        fields = [k for k, v in config.items()
                  if k.startswith("sidebar_field")]
        aliases = [k for k, v in config.items()
                   if k.startswith("sidebar_alias")]
        return zip(fields, aliases)

    def format_data_by_sidebar_fields(self, data, config):
        """Returns a list of ordered dicts, ordered by the sidebar fields.
        Call this function last before handing off to the PDF loop."""

        """
            record = {
                'photo_id': 'DSCN0014.JPG',
                'data': collections.OrderedDict([
                        # Alias: value
                        ('Short Name', u'DSCN004'),
                        ('DateTime', u'2015:12:21 11:03:13'),
                        ('POINT_X', 743006.7721)
                    ])
            }
        """
        sidebar = self.make_sidebar_field_keys(data, config)

        # # create a list of fields
        populated_sidebar = [item for item in sidebar
                             if config[item[0]] not in ["<None>", ""]]

        # print populated_sidebar
        ordered_data = []
        for record in data:
            # {'Photo File Name': 'A0290', 'EXIF TimeStamp': '10/19/2010 10:17:40', 'EXIF Latitude': 'No GPS info', 'EXIF Longitude': 'No GPS info', 'EXIF Bearing': 'No GPS info'}
            #print config['photo_id_field']
            # 'Photo File Name'
            new_record = {}
            if config['photo_id_field'] != u'<None>':
                new_record['photo_id'] = record[config['photo_id_field']]
            elif record['photo_id']:
                new_record['photo_id'] = record['photo_id']
            # new_record['photo_id'] = record[config['photo_id_field']]
            new_record['primary_sort_field'] = record[
                config['primary_sort_field']]
            new_record['data'] = collections.OrderedDict()

            #print populated_sidebar

            for field_key, alias_key in populated_sidebar:
                # if the alias is "", use the field name instead
                if config[alias_key] == "":
                    alias = config[field_key]
                else:
                    alias = config[alias_key]
                new_record['data'][alias] = record[config[field_key]]
            ordered_data.append(new_record)

        return ordered_data

    def generate_pdf(self, data, config, photo_path_dict):

        pdf = PDF.Doc(config=config)

        i = 1

        if config['page_break_bool']:
            prev_sort_field = data[0]['primary_sort_field']

        for record in data:
            photo_path = record['photo_id']

            print "Inserting {} into PDF".format(photo_path)

            sort_field = record['primary_sort_field']

            # set page break flag
            if config['page_break_bool'] and sort_field != prev_sort_field:
                page_break_flag = True
            else:
                page_break_flag = False

            pdf.add_page_item(photo_path_dict[photo_path],
                              config,
                              page_break_flag)
            pdf.add_sidebar_text(record['data'], config, page_break_flag)

            # reset flags
            page_break_flag = False
            prev_sort_field = sort_field

            i += 1
        pdf.save()
