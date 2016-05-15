﻿#coding:utf-8
import urllib
import urllib2
import re


#处理页面标签
class Tool:
    #去除img标签，7位长空格
    removeImg = re.compile('<img.*?>| {7}|')
    #去除超链接标签
    removeAddr =  re.compile('<a.*?>|</a>')
    #把换行的标签替换为\n
    replaceLine = re.compile('<tr>|<div>|</div>|<p>')
    #把表格制表<td>替换为\t
    replaceTD = re.compile('<td>')
    #把段落开头换为\n并加两个空格
    replacePara = re.compile('<p.*?>')
    #将换行符或者双换行符替换为\n
    replaceBR = re.compile('<br><br>|<br>')
    #把其余标签去掉
    removeExtraTag = re.compile('<.*?>')

    def replace(self, x):
        x = re.sub(self.removeImg, "", x)
        x = re.sub(self.removeAddr, "", x)
        x = re.sub(self.replaceLine, "\n", x)
        x = re.sub(self.replaceTD, "\t", x)
        x = re.sub(self.replacePara, "\n       ", x)
        x = re.sub(self.replaceBR, "\n", x)
        x = re.sub(self.removeExtraTag, "", x)
        #strip()将前后多余的内容删除
        return x.strip()

class BDTB:

    #初始化， 传入基地址， 是否楼主参数
    def __init__(self, baseUrl, seeLZ, floorTag):
        #base链接地址
        self.baseURL = baseUrl
        #是否只看楼主
        self.seeLZ = '?see_lz=' + str(seeLZ)
        #html标签剔除工具类对象
        self.tool = Tool()
        #全局file变量， 文件写入操作对象
        self.file = None
        #楼层标号, 初始为1
        self.floor = 1
        #默认的标题, 如果没有成活获取标题的话会使用这个标题
        self.defaultTitle = u"百度贴吧"
        #是否写入楼层分隔符的标记
        self.floorTag = floorTag

    def getPage(self, pageNum):
        try:
            #构建URL
            url = self.baseURL + self.seeLZ + '&pn=' + str(pageNum)
            request = urllib2.Request(url)
            response = urllib2.urlopen(request)
            #返回UTF-8格式编码错误
            return response.read().decode('utf-8')
        except urllib2.URLError, e:
            if hasattr(e, "reason"):
                print u"链接百度贴吧失败，错误原因是：", e.reason
                return None

    def  getTitle(self, page):
        #得到标题的正则表达式
        pattern  = re.compile('<h3 class="core_title_txt.*?>(.*?)</h3>', re.S)
        result = re.search(pattern, page )
        if result:
            #如果标题是存在的，那么返回标题
            return result.group(1).strip()
        else:
            return None

    #获取帖子一共有多少页
    def getPageNum(self, page):
        #得到帖子页数的正则表达式
        pattern = re.compile('<li class="l_reply_num.*?</span>.*?<span.*?>(.*?)</span>',re.S)
        result = re.search(pattern,page)
        if result:
            #如果结果存在的话
                return result.group(1).strip()
        else:
            return None

    def getContent(self, page):
        pattern = re.compile('<div id="post_content_.*?>(.*?)</div>',re.S)
        items = re.findall(pattern, page)
        contents = []
        for item in items:
            #将文本进行去除标签处理， 同时在前后加入换行符
            content = "\n" + self.tool.replace(item) + "\n"
            contents.append(content.encode("utf-8"))
        return contents

    def setFileTitle(self, title):
        #如果标题不是None，继成功获取到标题
        if title is not None:
            self.file = open(title + ".txt", "w+")
        else:
            self.file = open (self.defaultTitle + ".txt", "w+")

    def writeData(self, contents):
        #向文件写入每一楼的信息
        for item in contents:
            if self.floorTag == "1":
                #楼之间的分隔符
                floorLine = "\n" + str(self.floor) + u"-----------------------------------------------------------------------------------------\n"
                self.file.write(floorLine)
            self.file.write(item)
            self.floor += 1

    def start(self):
        indexPage = self.getPage(1)
        pageNum = self.getPageNum(indexPage)
        title = self.getTitle(indexPage)
        self.setFileTitle(title)
        if pageNum == None:
            print u"这个网址已经失效了哦，请更换个网址~"
            return
        try:
            print u"该帖子一共有" + str(pageNum) + u"页哦"
            for i in range(1, int(pageNum) + 1):
                print u"正在写入第" + str(i) + u"哦，请稍安勿躁~"
                page = self.getPage(i)
                contents = self.getContent(page)
                self.writeData(contents)
        #出现写入异常
        except IOError, e:
            print u"出现写入错误了哦，原因是：" + e.message
        finally:
            print u"任务完成了哦，请享受它吧~"


if __name__ == "__main__":
    print u"请输入帖子代号"
    baseURL = 'http://tieba.baidu.com/p/' + str(raw_input())
    seeLZ = raw_input("是否只获取楼主发言，是输入1，否输入0\n")
    floorTag = raw_input("是否写入楼层信息，是输入1，否输入0\n")
    bdtb = BDTB(baseURL, seeLZ, floorTag)
    bdtb.start()













