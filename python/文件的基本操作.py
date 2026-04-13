# coding=gbk

"""
Python处理文本的25个经典操作
公众号文章：python学习杂记 2024-06-23
"""

import os

# mac: "/";  window: "\\"; ~ 是“家目录”的简写，expanduser() 是把这个简写展开成真实路径。
desktop = os.path.join(os.path.expanduser("~"), 'Desktop') + '/'
print(desktop)

# 打开文件并读取内容 [the file must exist already]
with open(file=desktop+'三字经.txt', mode='r', encoding='utf-8') as ff:
    content = ff.read()
print(content)

# 整体覆盖 [if the file exists, then replace; if not, then would create this file]
with open(file=desktop+'三字经2.txt', mode='w', encoding='utf-8') as ff:
    ff.write('[如果你看到了这行文字，说明之前的内容全部被我覆盖了]')

# 追加内容在末尾 [if the file does not exist, then it would create the file]
with open(file=desktop+'三字经3.txt', mode='a', encoding='utf-8') as ff:
    ff.write('这是一行新的内容！')

# 读取文件的特定某行，如第3行
with open(file=desktop+'三字经.txt', mode='r', encoding='utf-8') as ff:
    line = ff.readlines()[2]
print(line)

"""
read 一次性读取整个文件的内容，将其作为一个字符串返回。
每次调用 readline 方法时，它会从文件的当前指针位置开始读取一行，并返回该行的字符串。行的末尾通常包括一个换行符 \n，除非在最后一行没有换行符。
readlines 读取文件中的所有行，并将它们作为一个列表返回，其中每一行是一个列表元素，行末包含换行符。
read 更适合读取较小的文件或需要处理整个文件内容为一个字符串的情况，而 readlines 更适合需要逐行处理文件内容的情况。如果文件非常大，考虑使用文件对象的迭代操作来逐行读取文件，以减少内存使用
"""


# 复制文件内容，并写入新文件
with open(file=desktop+'三字经.txt', mode='r', encoding='utf-8') as ff, open(file=desktop+'三字经_copy.txt', mode='w', encoding='utf-8') as ff_copy:
    ff_copy.write(ff.read())


# 假设 desktop = r"C:\Users\Ben\Desktop\\"
os.makedirs(desktop+'newFolder2\\test', exist_ok=True)  
# 如果 newFolder2 or test 已经是目录，不会报错。
# 如果路径中任何层级有同名"文件"而不是目录，会报 FileExistsError。

os.rename(desktop+'三字经.txt', desktop+'newFolder2\\新三字经.txt')  
# 如果 newFolder2\新三字经.txt 已经存在（windows），会 FileExistsError。
# 如果不存在，会移动&重命名文件。

""" 
os.mkdir() 
This function is used to create a single directory level. 
It does not create nested directories; if the parent directory does not exist, it will raise a FileNotFoundError. 

os.makedirs('mydir/subdir1/subdir2')
In the example above, os.mkdir will only create mydir, and if mydir does not exist, it will raise an error. On the other hand, os.makedirs will create mydir, mydir/subdir1, and mydir/subdir1/subdir2, creating all necessary intermediate directories. If any of these directories already exist and exist_ok is not set to True, it will raise a FileExistsError. 
"""

# 删除文件
# os.remove(desktop+'三字经_copy.txt')

# 删除文件夹
# os.rmdir(desktop+'newFolder2\\test')
""" 
os.rmdir(): 
This function is used to remove a single directory. 
It can only remove empty directories. If the directory contains any files or subdirectories, os.rmdir will raise an OSError. 
It does not work on files; trying to use os.rmdir on a file will raise an error. 

os.remove(): 
This function is used to remove a file or a symbolic link. 
It cannot remove directories, even if they are empty. If you try to use os.remove on a directory, it will raise an OSError. 
It is designed to work with files and symbolic links, not directories. 
"""

# 遍历文件夹中的所有文件
# for file in os.listdir('.'):
for file in os.listdir(desktop):
    print(file)

# 获取文件大小
print(os.path.getsize(desktop + '三字经_copy.txt'))

# 检查路径是否存在
print(os.path.exists(desktop + '三字经_copy.txt'))
print(os.path.exists(desktop + 'newFolder2'))

# 确认文件行数
with open(file=desktop + '三字经.txt', mode='r', encoding='utf-8') as ff:
    line_count = sum(1 for line in ff)
print(line_count)
