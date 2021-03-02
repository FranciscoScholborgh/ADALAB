from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt

alingment_types = {
    'left' : WD_ALIGN_PARAGRAPH.LEFT,
    'center' : WD_ALIGN_PARAGRAPH.CENTER,
    'justify' : WD_ALIGN_PARAGRAPH.JUSTIFY
}

class StyleDocument():

    def create_style(document, style_name, font='Times New Roman', size=12, is_bold=False, alignment="left"):
        styles = document.styles
        style_header = styles.add_style(style_name, WD_STYLE_TYPE.PARAGRAPH)
        style_header.font.name = font
        style_header.font.size = Pt(size)
        style_header.font.bold = is_bold
        style_header.paragraph_format.alignment = alingment_types[alignment]
        return style_header

    def editParagraph_style(paragraph, font='Times New Roman', size=12, is_bold=False, alignment="left"):
        style = paragraph.style
        style.font.name = font
        style.font.size = Pt(size)
        style.font.bold = is_bold
        style_alignment = alingment_types[alignment]
        style.paragraph_format.alignment = style_alignment
