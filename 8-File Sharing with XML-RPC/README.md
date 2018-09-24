# 尝试使用

打开多个终端， 创建目录files1和files2，在files2下创建文件test.txt，再在一个终端执行命令：
```python
python simple_node.py http://127.0.0.1:4242 files1 123456
```
再创建一个对等体，在另一个终端执行命令：
```python
python simple_node.py http://127.0.0.1:4243 files2 456789
```
启动python交互解释器，尝试连接到其中一个对等体：
```python
>>> from xmlrpc.client import *
>>> mypeer = ServerProxy('http://127.0.0.1:4242')
>>> code, data = mypeer.query('test.txt')
>>> code
2
```
很明显失败了，我们尝试连接另一个对等体：
```python
>>> otherpeer = ServerProxy('http://127.0.0.1:4243')
>>> code, data = otherpeer.query('test.txt')
>>> code
1
```
查询成功，因为files2目录下有test.txt文件。如果test.txt文件包含文本不多，可显示变量data的内容核实传输内容正确：
```python
>>> data
'This is a test\n'
```
向第二个对等体介绍第一个对等体：
```python
>>> mypeer.hello('http://127.0.0.1:4243')
1
```
现在，第一个对等体知道第二个对等体的URL，可向其寻求帮助了。再次查询第一个对等体：
```python
>>> mypeer.query('test.txt')
[1, 'This is a test\n']
```
成功了！

现在我们测试最后一项功能----让节点一从节点二下载文件并存储它：
```python
>>> mypeer.fetch('test.txt','123456')
1
```
你会发现，文件test.txt神奇地出现在files1目录下。
