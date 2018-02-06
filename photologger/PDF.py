# ------------------------------------------------------------------------------
# Name:        PDF.py
# Purpose:     Handles all aspects of photo log PDF creation
# Author:      gdmf
# Created:     05/19/2016
# ------------------------------------------------------------------------------
from __future__ import unicode_literals
try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO
from PIL import Image
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, Frame
from reportlab.platypus.flowables import Spacer
from reportlab.lib.utils import ImageReader

from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.styles import ParagraphStyle
# from reportlab.pdfbase import pdfmetrics
# from reportlab.pdfbase.ttfonts import TTFont
# from reportlab.pdfbase import ttfonts
# import Formatter


class Doc(object):
    """Represents a PDF document."""
    # top = 0
    # page_number = 1

    def __init__(self, config, pagesize=letter):
        """Initialize a new PDF document. Page size defaults to letter."""
        self.path = config['output_pdf']
        self.pagesize = pagesize
        self.doc = Canvas(self.path, self.pagesize)
        self.top = 0
        self.page_number = 1


        # register TrueType font
        # http://stackoverflow.com/questions/4899885/how-to-set-any-font-in-reportlab-canvas-in-python
        # http://stackoverflow.com/questions/14370630/reportlab-pdfgen-support-for-bold-truetype-fonts
        # font_ttf = "{}.ttf".format(config['font_face'])
        # pdfmetrics.registerFont(TTFont(config['font_face'], font_ttf))

        self.doc.setFont(config['font_face'], config['font_size'])
        self.style = getSampleStyleSheet()['Normal']
        self.style.fontName = config['font_face']
        self.style.fontSize = config['font_size']
        self.style.leading = config['leading']
        r, g, b = (0.5, 0.5, 0.5)
        self.doc.setStrokeColorRGB(r, g, b)  # color for lines and rectangles
        self.logo = config['logo']



        # Header dimensions
        self.dim_header_rect1 = (.5 * inch, 10 * inch,
                                 7.6 * inch, 0.25 * inch)
        self.dim_header_rect2 = (.5 * inch, 10.25 * inch,
                                 7.6 * inch, 0.25 * inch)
        self.dim_header_string1 = (4.25 * inch, 10.325 * inch)
        self.dim_header_string2 = (4.25 * inch, 10.075 * inch)

        # Footer dimensions
        self.dim_footer_line = (2.5 * inch, 0.75 * inch,
                                8.1 * inch, 0.75 * inch)
        self.dim_footer_logo = (.5 * inch, .4 * inch, 1 * inch, .45 * inch)
        self.dim_page_number = (8.15 * inch, .4 * inch)

        # Photo frame dimensions
        self.dim_top_frame = (2.5 * inch, 5.5 * inch,
                              5.6 * inch, 4.25 * inch)
        self.dim_bottom_frame = (2.5 * inch, 1.25 * inch,
                                 5.6 * inch, 4.25 * inch)

        # Sidebar dimensions
        self.dim_top_sidebar = (.5 * inch, 5.5 * inch, 2 * inch, 4.25 * inch)
        self.dim_bottom_sidebar = (.5 * inch, 1.25 * inch,
                                   2 * inch, 4.25 * inch)

        # Photo dimensions
        self.dim_top_photo = (2.6 * inch, 5.6 * inch, 5.4 * inch, 4.05 * inch)
        self.dim_bottom_photo = (2.6 * inch, 1.35 * inch,
                                 5.4 * inch, 4.05 * inch)

    def add_header(self, config):
        """Add two header rectangles with text."""
        # HEADER RECTANGLES
        # http://stackoverflow.com/questions/29703579/reportlab-rounded-rect
        self.doc.roundRect(*self.dim_header_rect1, radius=4, stroke=1, fill=0)
        self.doc.roundRect(*self.dim_header_rect2, radius=4, stroke=1, fill=0)

        # HEADER TEXT
        self.headerStyle = getSampleStyleSheet()['Normal']
        self.headerStyle.name = 'header'
        self.headerStyle.fontName = config['font_face']
        # self.headerStyle.fontSize = config['font_size']
        self.headerStyle.fontSize = 12
        self.headerStyle.alignment = TA_CENTER

        self.header_text_01 = []
        self.header_text_01.append(Paragraph(
            config['header_text_1'], self.headerStyle))
        self.headerFrame_01 = Frame(
            .5 * inch, 10.075 * inch, 7.6 * inch, 0.5 * inch)
        self.headerFrame_01.addFromList(self.header_text_01, self.doc)

        self.header_text_02 = []
        self.header_text_02.append(Paragraph(
            config['header_text_2'], self.headerStyle))
        self.headerFrame_02 = Frame(
            .5 * inch, 9.825 * inch, 7.6 * inch, 0.5 * inch)
        self.headerFrame_02.addFromList(self.header_text_02, self.doc)
        # self.doc.drawCentredString(*self.dim_header_string1,
        #                            text=config['header_text_1'])
        # self.doc.drawCentredString(*self.dim_header_string2,
        #                            text=config['header_text_2'])

    def add_footer(self, config):
        """Add footer line, logo and page number."""
        # FOOTER LINE
        self.doc.line(*self.dim_footer_line)

        # LOGO
        self.doc.drawImage(self.logo, *self.dim_footer_logo,
                           preserveAspectRatio=True)

        # PAGE NUMBER
        if config['page_numbering_bool']:

            self.pageNumStyle = getSampleStyleSheet()['Normal']
            self.pageNumStyle.name = 'pageNum'
            self.pageNumStyle.fontName = config['font_face']
            self.pageNumStyle.fontSize = 12
            self.pageNumStyle.alignment = TA_RIGHT

            self.pageNumText = []
            self.pageNumText.append(Paragraph(
                str(self.page_number), self.pageNumStyle))
            self.pageNumFrame = Frame(
                7.8 * inch, .2 * inch, 0.4 * inch, 0.4 * inch)
            self.pageNumFrame.addFromList(self.pageNumText, self.doc)
            # self.doc.drawAlignedString(*self.dim_page_number,
            #                            text=str(self.page_number))

    def add_page(self):
        """Add a new page to the PDF document."""
        self.page_number += 1
        self.doc.showPage()

    def add_page_item(self, photo_path, config, page_break_flag=False):
        """Add a page item, consisting of a photo, photo frame
        and sidebar frame. Add header if top page item or footer if bottom page
        item."""

        if page_break_flag is True:
            if self.top % 2 == 1:  # if top
                self.add_page()
            self.top = 0

        self.top += 1
        if self.top % 2 == 1:    # = top
            self.add_header(config)
            # add footer when page added; otherwise it will get left off with
            # odd numbers of photos
            self.add_footer(config)
            self.doc.rect(*self.dim_top_frame, stroke=1, fill=0)
            self.doc.rect(*self.dim_top_sidebar, stroke=1, fill=0)
            # resize on fly
            im = Image.open(photo_path)
            im.thumbnail((600, 600), Image.ANTIALIAS)
            # use StringIO for buffer
            f = StringIO()
            im.save(f, 'JPEG')
            self.doc.drawImage(ImageReader(f),
                               *self.dim_top_photo,
                               preserveAspectRatio=True)

        else:                   # = bottom
            self.doc.rect(*self.dim_bottom_frame, stroke=1, fill=0)
            self.doc.rect(*self.dim_bottom_sidebar, stroke=1, fill=0)
            # resize on fly
            im = Image.open(photo_path)
            im.thumbnail((600, 600), Image.ANTIALIAS)
            # use StringIO for buffer
            f = StringIO()
            im.save(f, 'JPEG')
            self.doc.drawImage(ImageReader(f),
                               *self.dim_bottom_photo,
                               preserveAspectRatio=True)

    def add_sidebar_text(self, data, config, page_break_flag):
        """Add text to sidebar."""
        sidebar_text = []

        for k, v in data.items():

            field_alias = "<b>%s:</b>" % k
            sidebar_text.append(Paragraph(field_alias, self.style))

            field_value = str(v)
            sidebar_text.append(Paragraph(field_value, self.style))

            s = Spacer(width=0.1 * inch, height=0.1 * inch)
            sidebar_text.append(s)

        if self.top % 2 == 1:
            f = Frame(*self.dim_top_sidebar)
        else:
            f = Frame(*self.dim_bottom_sidebar)

        f.addFromList(sidebar_text, self.doc)

        if self.top % 2 == 0:
            self.add_page()

    def save(self):
        """Save the PDF document to a file."""
        self.doc.save()
