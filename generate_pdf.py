import fpdf
import os

data=[256646545434543453,986786575643,4,5,6]

pdf = fpdf.FPDF(format='letter', )
pdf.add_page()
pdf.add_font("Inter", '', 'C:/Windows/Fonts/Inter.ttf', uni=True)

# pdf.add_font("Playfair Display Regular", '', 'C:/Windows/Fonts/Playfair Display', uni=True)
pdf.set_font("Inter", size=12)
pdf.set_margins(5,5,5)
for i in data:
    pdf.write(10,str(i))
    pdf.ln()
pdf.output("testings.pdf")
os.startfile("testings.pdf")