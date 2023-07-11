import io
import os
from functools import partial
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

from pdf_table_builder.helpers import calculate_image_dimensions_and_keep_aspect_ratio

styles = getSampleStyleSheet()
styleN = styles['Normal']
styleH = styles['Heading1']

DESIRED_PHOTO_WIDTH = A4[0] - 160
DESIRED_PHOTO_HEIGHT = A4[1] / 2 - 170

BASIC_MARGIN = 30
BODY_FONT_SIZE = 8
PAGE_WIDTH = A4[0]
PAGE_HEIGHT = A4[1]
LINE_Y = 730

FRAME_X1 = 30
FRAME_Y1 = 30

WATERMARK = None
LOGO_PATH = None
LOGO_BASE_WIDTH = 180
PDF_TAB_TITLE = 'PDF Tab Title'
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))


class ReportLabPDFBuilder:

    def __init__(self, logo_path=None, watermark=None, pdf_tab_title=PDF_TAB_TITLE, logo_base_width=LOGO_BASE_WIDTH,
                 logo_canvas_x=0, logo_canvas_y=0, frame_left_padding=30, frame_right_padding=30, frame_top_padding=30,
                 frame_bottom_padding=30, have_header_bottom_line=True, company_info=None, footer_text=None, ):
        global WATERMARK
        global LOGO_PATH
        global BODY_STYLE
        global PDF_TAB_TITLE
        global LOGO_BASE_WIDTH

        LOGO_PATH = logo_path
        WATERMARK = watermark
        BODY_STYLE = get_body_style()
        PDF_TAB_TITLE = pdf_tab_title
        LOGO_BASE_WIDTH = logo_base_width

        self.pdf_buffer = BytesIO()
        self.pdf = BaseDocTemplate(self.pdf_buffer, pagesize=A4)

        logo_print_width = 0
        logo_print_height = 0
        if LOGO_PATH:
            im = pilim.open(LOGO_PATH)
            logo_print_width, logo_print_height = calculate_image_dimensions_and_keep_aspect_ratio(
                img_width=im.size[0],
                img_height=im.size[1],
                img_desired_width=LOGO_BASE_WIDTH
            )

        top_y = PAGE_HEIGHT - logo_print_height - 30
        if company_info:
            i = 0
            for value in company_info:
                if value:
                    if i > 0:
                        top_y -= 12
                    i += 1

        if have_header_bottom_line:
            top_y -= 12

        frame = Frame(
            0,
            0 - (PAGE_HEIGHT - top_y) + 20,
            width=PAGE_WIDTH,
            height=PAGE_HEIGHT,
            leftPadding=frame_left_padding,
            bottomPadding=frame_bottom_padding,
            rightPadding=frame_right_padding,
            topPadding=frame_top_padding
        )
        header_and_footer_partial = partial(
            header_and_footer,
            logo_canvas_x,
            logo_canvas_y,
            have_header_bottom_line,
            top_y,
            logo_print_width,
            logo_print_height,
            company_info,
            footer_text
        )
        template = PageTemplate(id='all_pages', frames=frame, onPage=header_and_footer_partial)
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

    def get_pdf_buffer(self):
        self.pdf.build(self.story)
        self.pdf_buffer.close()
        return self.pdf_buffer

    def save_pdf_file(self, file_name):
        self.pdf.build(self.story)
        with open(file_name, "wb") as f:
            self.pdf_buffer.seek(io.SEEK_SET)
            f.writelines(self.pdf_buffer)


class Row:
    def __init__(self, columns, line=None, grid=None, background_color=None, text_color=None, full_width=False,
                 align=TA_LEFT, valign=None):
        self.columns = columns
        self.line = line
        self.grid = grid
        self.background_color = background_color
        self.text_color = text_color
        self.align = align
        self.full_width = full_width
        self.valign = valign  # TOP, MIDDLE, BOTTOM

    def get_number_of_columns(self):
        return len(self.columns)


class Column:

    def __init__(self, content='', line=None, grid=None, background_color=None, text_color=None, image_width=50,
                 image_height=50, align=TA_LEFT, valign=None):
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
        self.valign = valign  # TOP, MIDDLE, BOTTOM


class Grid:
    def __init__(self, line_width=0.5, line_color=colors.gray):
        self.line_width = line_width
        self.line_color = line_color


class Line:
    def __init__(self, line_position='LINEBELOW', line_width=0.5, line_color=colors.gray):
        """
        :param line_position: Can be LINEBELOW, LINEABOVE, LINEBEFORE, LINEAFTER
        :param line_width: Can be 0.5, 1, 2 etc.
        :param line_color: Can be colors.gray, colors.black etc. or HEX color like '#000000'.
        """
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
                    _col = col.content

                column_final.append(_col)

            table_data.append(column_final)
        else:
            print("SOMETHING ELSE")
            print(row_obj)

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
                # VALIGN
                apply_style = False
                valign = None
                if col_obj.valign:
                    apply_style = True
                    valign = col_obj.valign
                elif row_obj.valign:
                    apply_style = True
                    valign = row_obj.valign
                if apply_style:
                    table_styles.add('VALIGN', (col_ctr, row_ctr), (col_ctr, row_ctr), valign)
    t = Table(table_data)
    t.setStyle(table_styles)
    return t


def header_and_footer(logo_canvas_x, logo_canvas_y, have_header_bottom_line, top_y, logo_print_width, logo_print_height,
                      company_info, footer_text, canvas, pdf):
    canvas.setTitle(PDF_TAB_TITLE)

    # LOGO
    if LOGO_PATH:
        im = pilim.open(LOGO_PATH)
        pil_img = ImageReader(im)
        canvas.drawImage(
            pil_img,
            logo_canvas_x,
            logo_canvas_y,
            width=logo_print_width,
            height=logo_print_height,
            mask='auto'
        )

    # COMPANY'S INFO
    top_y = PAGE_HEIGHT - logo_print_height - 30
    if company_info:
        canvas.setFont('NotoSans', 9)
        i = 0
        for value in company_info:
            if value:
                if i == 0:
                    canvas.drawString(BASIC_MARGIN, top_y, value.strip())
                else:
                    top_y -= 12
                    canvas.drawString(BASIC_MARGIN, top_y, value.strip())
                i += 1

    if have_header_bottom_line:
        top_y -= 12
        canvas.line(BASIC_MARGIN, top_y, PAGE_WIDTH - BASIC_MARGIN, top_y)

    # ----------------------- FOOTER ----------------------- #
    bottom_y = 8
    # Page number.
    page_number_text = "%d" % pdf.page
    canvas.drawCentredString(295, bottom_y, '-' + page_number_text + '-')

    # Footer text.
    if footer_text:
        canvas.setFont('NotoSans', 8)
        bottom_y += 5 + (len(footer_text) * 12)
        i = 0
        for value in footer_text:
            if value:
                if i == 0:
                    canvas.drawString(BASIC_MARGIN, bottom_y, value.strip())
                else:
                    bottom_y -= 12
                    canvas.drawString(BASIC_MARGIN, bottom_y, value.strip())
                i += 1

    # Watermark.
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
