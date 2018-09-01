def lines(file):
	for line in file:
		yield line
	yield '\n'
	
def blocks(file):
	block = []
	for line in lines(file):
		if line.strip():
			block.append(line)
		elif block:			#段落结束整合
			yield ''.join(block).strip()
			block = []		#每一段获取完后清零