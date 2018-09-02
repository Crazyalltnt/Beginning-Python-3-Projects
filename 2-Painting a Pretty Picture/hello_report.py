#@author: Neil
#2018-09-02

from reportlab.graphics.shapes import Drawing, String
from reportlab.graphics import renderPDF

d = Drawing(100, 100)	#图片规格100*100
s = String(50, 50, 'Hello, world!', textAnchor = 'middle')

d.add(s)

renderPDF.drawToFile(d, 'hello.pdf', 'A simple PDF file')