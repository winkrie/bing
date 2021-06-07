# -*- coding: utf-8 *-*

import time
import os
import urllib2
import json
import contextlib
import shutil


class Bing:
    host = 'http://cn.bing.com'
    url_tpl = '%s/HPImageArchive.aspx?format=js&uhd=1&uhdwidth=%d&uhdheight=%d&idx=%d&n=%d&nc=%d'
    uhdwidth = 3840
    uhdheight = 2160
    fetch_size = 8
    server_url = ''
    ensearch = [0, 1]

    def __init__(self, index=0):
        self.server_url = self.url_tpl % (self.host, self.uhdwidth, self.uhdheight, index, self.fetch_size, int(time.time()))
        '''
        self.server_url = 'http://cn.bing.com/HPImageArchive.aspx?format=js&uhd=1&uhdwidth=3840&uhdheight=2160&idx=0&n=8'
        '''

    @staticmethod
    def __get_image_name(img):
        name = os.path.basename(img)
        pos = name.find('_')
        if not pos:
            return None
        point_pos = name.find('.')
        if pos > point_pos > 0:
            return name[point_pos + 1:pos]
        return name[:pos]

    @staticmethod
    def __download(url, filename, datetime=0):
        print url, '=>', filename
        try:
            with contextlib.closing(urllib2.urlopen(url)) as res, open(filename, 'wb') as f:
                shutil.copyfileobj(res, f)
            if datetime:
                datetime = int(time.mktime(time.strptime(str(datetime), '%Y%m%d')))
                os.utime(filename, (datetime, datetime))
            return True
        except urllib2.URLError, e:
            print e.reason
            return False

    def save(self, path):
        if not os.path.exists(path):
            os.mkdir(path)
        for en in self.ensearch:
            url = self.server_url + '&ensearch=' + str(en)
            try:
                with contextlib.closing(urllib2.urlopen(url)) as res:
                    content = res.read()
                if not content:
                    continue
                content_json = json.loads(content)
                if not content_json:
                    continue
                for item in content_json['images']:
                    img_name = self.__get_image_name(item['url'])
                    if not img_name:
                        continue
                    filename = os.path.join(path, img_name + '.jpg')
                    try:
                        mtime = os.path.getmtime(filename)
                        time_local = time.localtime(mtime)
                        if time.strftime('%H:%M:%S', time_local) == '00:00:00':
                            continue
                    except os.error:
                        pass
                    img_url = item['url'] if item['url'].find('http') == 0 else (self.host + item['url'])
                    self.__download(img_url, filename, item['startdate'])
            except urllib2.URLError, e:
                print e.reason
