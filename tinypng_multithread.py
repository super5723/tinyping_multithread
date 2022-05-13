#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from fileinput import filename
import os
import sys
import os.path
import click
import tinify
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED, FIRST_COMPLETED
import time

tinify.key = "834W5WL5gbC1G7HGN1wmkHC53SqFZWbV"		# API KEY
version = "1.0.1"				# 版本
totalCompressSize = 0             # 统计压缩结果

def get_file_size_str(fileSize):
    return ("%.2f KB" % (fileSize/1024))

# 压缩的核心
def compress_core(inputFile, outputFile, img_width):
    source = tinify.from_file(inputFile)
    if img_width != -1:
        resized = source.resize(method="scale", width=img_width)
        resized.to_file(outputFile)
    else:
        source.to_file(outputFile)
    inputFileSize = os.path.getsize(inputFile)
    outputFileSize = os.path.getsize(outputFile)
    global totalCompressSize
    totalCompressSize += inputFileSize-outputFileSize
    print("compress %s : %s --> %s" %(os.path.basename(inputFile),get_file_size_str(inputFileSize), get_file_size_str(outputFileSize)))


# 压缩一个文件夹下的图片
def compress_path(path, width):
    print("compress_path:%s" % path)
    global totalCompressSize
    totalCompressSize = 0
    if not os.path.isdir(path):
        print("这不是一个文件夹，请输入文件夹的正确路径!")
        return
    else:
        fromFilePath = path 			# 源路径
        toFilePath = path+"/tiny" 		# 输出路径
        print("toFilePath=%s" % toFilePath)
        executor = ThreadPoolExecutor(max_workers=3)
        startTime = time.time()
        paramList = []
        for root, dirs, files in os.walk(fromFilePath):
            # print("root = %s" % root)
            # print("dirs = %s" % dirs)
            # print("files= %s" % files)
            for name in files:
                fileName, fileSuffix = os.path.splitext(name)
                if fileSuffix == '.png' or fileSuffix == '.jpg' or fileSuffix == '.jpeg':
                    toFullPath = toFilePath + root[len(fromFilePath):]
                    toFullName = toFullPath + '/' + name
                    if os.path.isdir(toFullPath):
                        pass
                    else:
                        os.mkdir(toFullPath)
                    param = [root + '/' + name, toFullName, width]
                    paramList.append(param)
            break  # 仅遍历当前目录
        task_list = [executor.submit(
            compress_core, param[0], param[1], param[2]) for param in paramList]
        wait(task_list, return_when=ALL_COMPLETED)
        print("压缩完成，总耗时:%.3f 秒 ,总共节省了 %s ." %
              (time.time()-startTime, get_file_size_str(totalCompressSize)))

# 仅压缩指定文件
def compress_file(inputFile, width):
    print("compress_file-------------------------------------")
    if not os.path.isfile(inputFile):
        print("这不是一个文件，请输入文件的正确路径!")
        return
    print("file = %s" % inputFile)
    dirname = os.path.dirname(inputFile)
    basename = os.path.basename(inputFile)
    fileName, fileSuffix = os.path.splitext(basename)
    if fileSuffix == '.png' or fileSuffix == '.jpg' or fileSuffix == '.jpeg':
        compress_core(inputFile, dirname+"/tiny_"+basename, width)
    else:
        print("不支持该文件类型!")


@click.command()
@click.option('-f', "--file",  type=str,  default=None,  help="单个文件压缩")
@click.option('-d', "--dir",   type=str,  default=None,  help="被压缩的文件夹")
@click.option('-w', "--width", type=int,  default=-1,    help="图片宽度，默认不变")
def run(file, dir, width):
    print("GcsSloop TinyPng V%s" % (version))
    if file is not None:
        compress_file(file, width)				# 仅压缩一个文件
        pass
    elif dir is not None:
        compress_path(dir, width)				# 压缩指定目录下的文件
        pass
    else:
        compress_path(os.getcwd(), width)		# 压缩当前目录下的文件
    print("结束!")


if __name__ == "__main__":
    run()
