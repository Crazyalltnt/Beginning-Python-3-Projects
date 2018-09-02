from urllib.request import urlopen
from reportlab.graphics.shapes import*
from reportlab.graphics.charts.lineplots import LinePlot
from reportlab.graphics.charts.textlabels import Label
from reportlab.graphics import renderPDF

URL = 'ftp://ftp.swpc.noaa.gov/pub/weekly/Predict.txt'
COMMENT_CHARS = '#:'

drawing = Drawing(400, 200)
data = []
for line in urlopen(URL).readlines():
	line = line.decode()
	if not line.isspace() and line[0] not in COMMENT_CHARS:
		data.append([float(n) for n in line.split()])	#每行数据作为列表添加到数据列表中
	
pred = [row[2] for row in data]	#数据列
high = [row[3] for row in data]
low = [row[4] for row in data]
times = [row[0] + row[1]/12.0 for row in data]

lp = LinePlot()
lp.x = 50
lp.y = 50
lp.height = 125
lp.width = 300
lp.data = [list(zip(times, pred)),
           list(zip(times, high)),
		   list(zip(times, low))]
lp.lines[0].strokeColor = colors.blue
lp.lines[1].strokeColor = colors.red
lp.lines[2].strokeColor = colors.green

drawing.add(lp)

drawing.add(String(180, 10, 'Sunspots', fontSize=16, fillColor=colors.black))
drawing.add(String(120, 115, 'Predicted', fontSize=12, fillColor=colors.blue))
drawing.add(String(120, 160, 'High', fontSize=12, fillColor=colors.red))
drawing.add(String(120, 75, 'Low', fontSize=12, fillColor=colors.green))
			
renderPDF.drawToFile(drawing, 'report2.pdf', 'Sunsports')