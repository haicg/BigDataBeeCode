# -*- coding:utf-8 -*-
import re
import json
import codecs
import urllib
import requests
from bs4 import BeautifulSoup


def parseLessonsMainPage(hostUrl):
    mLessonDict = {}
    response = requests.get(hostUrl)
    response.encoding = response.apparent_encoding
    soup = BeautifulSoup(response.text, "html.parser")
    pattrn = re.compile('\s*' + u'走遍美国第')
    res = soup.find_all('a', title=pattrn)
    for lesson in res:
        if ('title' in lesson.attrs) and ('href' in lesson.attrs):
            title_str = lesson['title']
            mLessonDict[title_str] = lesson['href']
    print mLessonDict
    return mLessonDict


def parseSingleLessonPage(urlStr):
    try:
        response = requests.get(urlStr)
        response.encoding = response.apparent_encoding
        str = response.text
        soup = BeautifulSoup(response.text, "html.parser")
        for script_str_obj in soup.find_all("script"):
            script_str = script_str_obj.text
            if script_str.find("jp-download") != -1:
                pattern = re.compile('(?<=jp-download)(.+?)open\s?'
                                     '\(\s?\'(.+?)\s?\'\)(.+?)(?<=;)', re.S)
                res = re.search(pattern, script_str)
                if (res.lastindex >= 2):
                    return res.group(2)
    except Exception, ex:
        print Exception, ":", ex
        return None


def getOneLessonDloadUrl(url):
    print url
    try:
        dowloadUrls = {}
        response = requests.get(url)
        response.encoding = response.apparent_encoding
        print response.text
        soup = BeautifulSoup(response.text, "html.parser")
        res = soup.find('a', id="dload")
        if 'href'in res.attrs:
            dowloadUrls["mp3"] = res.attrs['href']
        res = soup.find('a', id="dloadword")
        if 'href' in res.attrs:
            dowloadUrls["lrc"] = res.attrs['href']
            return dowloadUrls
    except Exception, ex:
        print Exception, ":", ex
        return None


def getLessonFilesDownloadUrls():
    try:
        lessonsUrlList = []
        website_host = "http://www.en8848.com.cn"
        lessonShowPageUrls = parseLessonsMainPage(
            website_host + "/tingli/brand/USA/")
        print lessonShowPageUrls
        for (title, urlStr) in lessonShowPageUrls.items():
            dlPageUrl = parseSingleLessonPage(website_host + urlStr)
            if dlPageUrl is None:
                continue
            print "dl page url : " + dlPageUrl
            fileUrls = getOneLessonDloadUrl(website_host + dlPageUrl)
            if fileUrls is None:
                continue
            print fileUrls
            lessonUrl = {}
            lessonUrl["title"] = title
            lessonUrl["urls"] = fileUrls
            lessonsUrlList.append(lessonUrl)
        return lessonsUrlList
    except Exception, ex:
        print Exception, ":", ex
        return None


def saveFileUtf8(filename, strText):
    with codecs.open(filename, 'w', encoding="utf-8") as fp:
        fp.write(strText)


def loadFile(filename):
    with codecs.open(filename, 'r', encoding="utf-8") as fp:
        return fp.read()


def downloadFile(url, filename):
    urllib.urlretrieve(url, filename)


def saveAllLessonsDloadUrls(filename="lessonMp3Urls.json"):
    lessonDloadUrlList = getLessonFilesDownloadUrls()
    print lessonDloadUrlList
    jsonLessonUrls = json.dumps(lessonDloadUrlList, sort_keys=True, indent=4)
    saveFileUtf8(filename, jsonLessonUrls)
    return lessonDloadUrlList


def downloadAllLessonsFile(lessonDloadUrlList):
    for lesson in lessonDloadUrlList:
        print lesson
        urls = None
        if "title" in lesson and "urls" in lesson:
            print lesson["title"]
            urls = lesson["urls"]
        if urls and "lrc" in urls and "mp3" in urls:
            print urls['lrc']
            downloadFile(urls['lrc'], 'download/'+lesson["title"]+".lrc")
            print urls['mp3']
            downloadFile(urls['mp3'], 'download/' + lesson["title"] + ".mp3")


def downloadLessonsWithFile(filename="lessonMp3Urls.json"):
    str = loadFile(filename)
    lessonList = json.loads(str)
    downloadAllLessonsFile(lessonList)


def test_getDloadUrl():
    website_host = "http://www.en8848.com.cn"
    lessonUrls = parseLessonsMainPage(website_host + "/tingli/brand/USA/")
    download_link = parseSingleLessonPage(website_host, lessonUrls)
    getOneLessonDloadUrl(website_host + download_link)


def main():
    lessonDloadUrlList = saveAllLessonsDloadUrls("lessonMp3Urls.json")
    downloadAllLessonsFile(lessonDloadUrlList)


if __name__ == "__main__":
    main()
