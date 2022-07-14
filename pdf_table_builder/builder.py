import io
import os
from io import BytesIO

from PIL import Image as pilim
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import BaseDocTemplate, Image
from reportlab.platypus import Frame, PageTemplate
from reportlab.platypus import Paragraph, Table, TableStyle

styles = getSampleStyleSheet()
styleN = styles['Normal']
styleH = styles['Heading1']

DESIRED_PHOTO_WIDTH = A4[0] - 100
DESIRED_PHOTO_HEIGHT = A4[1] / 2 - 170

BASIC_MARGIN = 30
LEFT_MARGIN = BASIC_MARGIN
RIGHT_MARGIN = BASIC_MARGIN
TOP_MARGIN = BASIC_MARGIN
BOTTOM_MARGIN = BASIC_MARGIN
BODY_FONT_SIZE = 8
PAGE_WIDTH = 530
PAGE_HEIGHT = 750
LINE_Y = 730
BODY_STYLE = None
USER_CAN_VIEW_PRICES = None

WATERMARK = None
LOGO_PATH = None
PDF_TAB_TITLE = 'PDF Tab Title'
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))


class ReportLabPDFBuilder:

    def __init__(self, logo_path=None, watermark=None, pdf_tab_title=PDF_TAB_TITLE):
        global WATERMARK
        global LOGO_PATH
        global BODY_STYLE
        global PDF_TAB_TITLE

        LOGO_PATH = logo_path
        WATERMARK = watermark
        BODY_STYLE = get_body_style()
        PDF_TAB_TITLE = pdf_tab_title

        self.pdf_buffer = BytesIO()
        self.pdf = BaseDocTemplate(self.pdf_buffer, pagesize=A4)
        frame = Frame(LEFT_MARGIN, BOTTOM_MARGIN, PAGE_WIDTH, 687, showBoundary=1)
        template = PageTemplate(id='all_pages', frames=frame, onPage=header_and_footer)
        self.pdf.addPageTemplates([template])
        self.story = []

    def add_to_story(self, obj):
        if isinstance(obj, list):
            for x in obj:
                self.story.append(x)
        else:
            self.story.append(obj)

    def get_pdf_value(self):
        self.pdf.build(self.story)
        pdf_value = self.pdf_buffer.getvalue()
        self.pdf_buffer.close()
        return pdf_value

    def save_pdf_file(self, file_name):
        self.pdf.build(self.story)
        with open(file_name, "wb") as f:
            self.pdf_buffer.seek(io.SEEK_SET)
            f.writelines(self.pdf_buffer)


class Row:
    def __init__(self, columns, line=None, grid=None, background_color=None, text_color=None, full_width=False,
                 align=TA_LEFT):
        self.columns = columns
        self.line = line
        self.grid = grid
        self.background_color = background_color
        self.text_color = text_color
        self.align = align
        self.full_width = full_width

    def get_number_of_columns(self):
        return len(self.columns)


class Column:

    def __init__(self, content, line=None, grid=None, background_color=None, text_color=None, image_width=50,
                 image_height=50, align=TA_LEFT):
        """

        :param content: This variable's data will be passed into the Reportlab's Paragraph Class, or if its BytesIO
                        object will be passed in a Reportlab's Image Class object and appended in the table.
        :param grid:
        :param background_color:
        :param text_color:
        :param image_width:
        :param image_height:
        :param align: Align options (from ReportLab) -> TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
        """
        self.content = content
        self.line = line
        self.grid = grid
        self.background_color = background_color
        self.text_color = text_color
        self.image_width = image_width
        self.image_height = image_height
        self.align = align


class Grid:
    def __init__(self, line_width=0.5, line_color=colors.gray):
        self.line_width = line_width
        self.line_color = line_color


class Line:
    def __init__(self, line_position='LINEBELOW', line_width=0.5, line_color=colors.gray):
        self.line_position = line_position
        self.line_width = line_width
        self.line_color = line_color


def get_img(img_path):
    # buff1 = BytesIO()
    # img = pilim.open(img_path)
    # print('img_path:', img_path, img.size[0], img.size[1])
    # door_out_img = Image(img_path, width=2 * inch, height=2 * inch)

    return '''<para autoLeading="off" fontSize=12>This &lt;img/&gt; <img
src="{0}" valign="top" width="{1}" height="{2}"/> </para>'''.format(img_path, 100, 100)


def pfd_table_builder(data, fonts=None):
    if fonts is None:
        fonts = []
    for font in fonts:
        pdfmetrics.registerFont(font)

    table_data = []
    for row_ctr, row_obj in enumerate(data):
        if isinstance(row_obj, Row):
            column_final = []
            for col_ctr, col in enumerate(row_obj.columns):
                style = get_body_style()
                # print('{}, {}'.format(row_ctr, col_ctr))
                # Loop through all the cells and apply the styles on cell level if declared
                # specifically for the particular cell or else apply the style of the row on the cell (if any).
                # Align
                if col.align:
                    style.alignment = col.align
                elif row_obj.align:
                    style.alignment = row_obj.align
                # Text Colour
                if col.text_color:
                    style.textColor = col.text_color
                elif row_obj.text_color:
                    style.textColor = row_obj.text_color

                # print("type:", type(col.content))
                if isinstance(col.content, BytesIO):
                    _col = Image(col.content, width=col.image_width, height=col.image_height)
                elif isinstance(col.content, str):
                    _col = Paragraph('{}'.format(col.content, 'N/A'), style)
                else:
                    # print("SOMETHING ELSE")
                    _col = col.content

                column_final.append(_col)

            table_data.append(column_final)
        else:
            table_data.append([row_obj])

    # ------------------ STYLE
    table_styles = TableStyle()
    for row_ctr, row_obj in enumerate(data):
        if isinstance(row_obj, Row):
            # Loop through all the cells and apply the styles on cell level if declared
            # specifically for the particular cell or else apply the style of the row on the cell
            # (so every cell on this row will have this style, if any).
            for col_ctr, col_obj in enumerate(row_obj.columns):
                apply_style = False
                # Background Colour
                background_color = None
                if col_obj.background_color:
                    apply_style = True
                    background_color = col_obj.background_color
                elif row_obj.background_color:
                    apply_style = True
                    background_color = row_obj.background_color
                if apply_style:
                    table_styles.add('BACKGROUND', (col_ctr, row_ctr), (col_ctr, row_ctr), background_color)
                # Grid
                apply_style = False
                grid_line_color = None
                grid_line_width = None
                if col_obj.grid:
                    apply_style = True
                    grid_line_color = col_obj.grid.line_color
                    grid_line_width = col_obj.grid.line_width
                elif row_obj.grid:
                    apply_style = True
                    grid_line_color = row_obj.grid.line_color
                    grid_line_width = row_obj.grid.line_width
                if apply_style:
                    table_styles.add('GRID', (col_ctr, row_ctr), (col_ctr, row_ctr), grid_line_width, grid_line_color)
                # Line
                apply_style = False
                line_color = None
                line_width = None
                line_position = None
                if col_obj.line:
                    apply_style = True
                    line_color = col_obj.line.line_color
                    line_width = col_obj.line.line_width
                    line_position = col_obj.line.line_position
                elif row_obj.line:
                    apply_style = True
                    line_color = row_obj.line.line_color
                    line_width = row_obj.line.line_width
                    line_position = row_obj.line.line_position
                if apply_style:
                    table_styles.add(line_position, (col_ctr, row_ctr), (col_ctr, row_ctr), line_width, line_color)
                # SPAN
                if row_obj.full_width:
                    table_styles.add('SPAN', (col_ctr, row_ctr), (-1, row_ctr))

    t = Table(table_data)
    t.setStyle(table_styles)
    return t


def header_and_footer(canvas, pdf):
    canvas.setTitle(PDF_TAB_TITLE)
    # LOGO
    # print('LOGO_PATH', LOGO_PATH)
    if LOGO_PATH:
        im = pilim.open(LOGO_PATH)
        pil_img = ImageReader(im)
        canvas.drawImage(pil_img, 350, PAGE_HEIGHT, width=210, height=70, mask='auto')

    canvas.line(BASIC_MARGIN, LINE_Y, PAGE_WIDTH + BASIC_MARGIN, LINE_Y)

    # ----------------------- FOOTER ----------------------- #
    canvas.setFont('Helvetica-Bold', 8)
    # page number
    page_number_text = "%d" % pdf.page
    canvas.drawCentredString(295, 8, '-' + page_number_text + '-')
    # watermark
    if WATERMARK:
        canvas.drawCentredString(507, 8, WATERMARK)

    canvas.line(BASIC_MARGIN, 20, PAGE_WIDTH + BASIC_MARGIN, 20)


def get_body_style():
    sample_style_sheet = getSampleStyleSheet()
    body_style = sample_style_sheet['BodyText']
    body_style.fontSize = BODY_FONT_SIZE
    pdfmetrics.registerFont(TTFont('NotoSans', os.path.join(__location__, 'fonts/NotoSans-Regular.ttf')))
    pdfmetrics.registerFont(TTFont('NotoSansBold', os.path.join(__location__, 'fonts/NotoSans-Bold.ttf')))
    body_style.fontName = 'NotoSans'
    return body_style


def find_max_num_of_columns(data):
    max_num_of_cols = 0
    for row_counter, row in enumerate(data):
        num_of_cols = len(row.columns) if isinstance(row, Row) else 1
        if num_of_cols > max_num_of_cols:
            max_num_of_cols = num_of_cols
    return max_num_of_cols


def append_colon(param):
    return '{}:'.format(param)
