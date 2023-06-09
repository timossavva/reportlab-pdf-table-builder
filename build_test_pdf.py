import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT
from reportlab.platypus import Spacer

from pdf_table_builder.builder import Row, Column, Grid, pfd_table_builder, ReportLabPDFBuilder

data = [
    Row(columns=[Column(content='<font size=10>{}</font>'.format(datetime.date.today().strftime("%d/%m/%Y")))]),
    Spacer(1, 1),
    Row(columns=[Column(content='Title')]),
    Spacer(1, 1),
    # Image(buff1, width=150, height=300),
    Row(
        columns=[
            Column(content='Panel color outside:'),
            Column(content='7012 Matt'),
            Column(content='$100', align=TA_RIGHT),
            Column(content='test'),
            Column(content='test2', grid=Grid(line_color=colors.yellow, line_width=2)),
        ],
        grid=Grid(line_color=colors.blue, line_width=1),
        # text_color=colors.red
        valign='MIDDLE'
    ),
    Row(
        columns=[
            Column(content='test2', align=TA_CENTER, background_color=colors.red, text_color=colors.blue),
            Column(content='Panel color outside:'),
            Column(content='7012 Matt', valign='BOTTOM'),
            Column(content='$100', align=TA_RIGHT, grid=Grid(line_color=colors.yellow, line_width=2)),
            Column(content='test', align=TA_CENTER, background_color=colors.aqua),
            Column(content='test2', align=TA_CENTER, background_color=colors.red, text_color=colors.white),
            Column(content='test2', align=TA_CENTER, background_color=colors.purple, text_color=colors.red),

        ],
        background_color=colors.green,
        text_color=colors.red,
        valign='MIDDLE'
    ),
    Row(
        columns=[
            Column(content='test2', align=TA_CENTER, background_color=colors.red, text_color=colors.blue),
            Column(content='Panel color outside:'),
            Column(content='7012 Matt'),
            Column(content='$100', align=TA_RIGHT),
            Column(content='test1', background_color=colors.purple),
            Column(content='test', align=TA_CENTER, background_color=colors.aqua, text_color=colors.yellow),
            Column(content='test2', align=TA_CENTER, background_color=colors.red, text_color=colors.white),
        ],
        background_color=colors.green,
        text_color=colors.blue,
        grid=Grid(),
    ),
]

table = pfd_table_builder(data)

pdfbuilder = ReportLabPDFBuilder(logo_path='logo.png')
pdfbuilder.add_to_story(table)
pdfbuilder.save_pdf_file('test_pdf.pdf')
