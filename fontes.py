from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

font_list = [
    "Helvetica", "Helvetica-Bold", "Helvetica-Oblique", "Helvetica-BoldOblique",
    "Courier", "Courier-Bold", "Courier-Oblique", "Courier-BoldOblique",
    "Times-Roman", "Times-Bold", "Times-Italic", "Times-BoldItalic",
    "Symbol", "ZapfDingbats"
]

c = canvas.Canvas("exemplo_fonts.pdf", pagesize=A4)
width, height = A4
y = height - 50

for font in font_list:
    try:
        c.setFont(font, 12)
        c.drawString(50, y, f"{font}: exemplo de texto usando essa fonte.")
        y -= 20
    except:
        c.drawString(50, y, f": [Fonte não disponível]")
        y -= 20

c.save()