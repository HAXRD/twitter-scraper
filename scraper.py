from __future__ import print_function

import credential as cdt 
import shutil
import tweepy
import pandas as pd 
import xlwt
import os
import wget

class Scraper:
    def __init__(self, api, user_id, filename, folder):
        self.api = api
        self.user_id = user_id
        self.filename = filename
        self.folder = folder
        self.data = {
            # 'ori_text': [],
            'text': [],
            'img_urls': []
        }
        self.df = None

    def process_item(self, i, item):
        # process img_url
        img_url = ""
        media = item.entities.get('media', [])
        if (len(media) > 0):
            img_url = media[0]['media_url']
            self.data['img_urls'].append(img_url)
            # process text
        
            urlIndex = item.text.find('http')
            print(i, urlIndex)
            # self.data['ori_text'].append(item.text)
            self.data['text'].append(' '.join(item.text[:urlIndex].split()))

            

    def write_xlsx(self):
        self.df = pd.DataFrame(self.data)
        writer = pd.ExcelWriter(self.filename, engine='xlsxwriter')
        self.df.to_excel(writer)
        writer.save()

    def process(self, limit):
        for i, item in enumerate(tweepy.Cursor(self.api.user_timeline, id=self.user_id).items()):
            if limit != -1:
                if i >= limit:
                    break
            self.process_item(i, item)

        # write to excel
        self.write_xlsx()
    
    def download_imgs(self):
        if os.path.exists(self.folder):
            shutil.rmtree(self.folder)
            os.mkdir(self.folder)
        else:
            os.mkdir(self.folder)
        # download files
        print("Downloading Images:")
        for i, url in enumerate(self.data['img_urls']):
            print(i, "==>")
            wget.download(url, os.path.join(self.folder, str(i) + '.jpg'))
            print("")

if __name__ == '__main__':
    ipt = input('Input feed limit (enter -1 to choose all): ')

    print(ipt)
    # authentication
    auth = tweepy.OAuthHandler(
        cdt.consumer_key,
        cdt.consumer_secret
    )
    auth.set_access_token(
        cdt.access_token,
        cdt.access_token_secret
    )
    api = tweepy.API(auth)

    scper = Scraper(api, 'FacesPics', 'output.xlsx', 'imgs')
    scper.process(ipt)
    scper.download_imgs()