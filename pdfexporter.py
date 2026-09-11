from reportlab.pdfgen import canvas
import markdown
from bs4 import BeautifulSoup

def md_para_texto(md):
    html = markdown.markdown(md)
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text()

def exportar_pdf_simples(texto, caminho_pdf):
    c = canvas.Canvas(caminho_pdf)
    y = 800

    for linha in texto.split("\n"):
        c.drawString(50, y, linha)
        y -= 15
        if y < 50:
            c.showPage()
            y = 800

    c.save()
