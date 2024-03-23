from bs4 import BeautifulSoup
import requests
import re
import pandas as pd



def removeReplies(postmessage):
        sub = re.sub(">>[0-9]+",' ',postmessage)
        return sub

def htmlToPd(htmlSoup):
    htmlPosts = [x for x in htmlSoup.findAll(name='div', attrs={'class': 'postContainer replyContainer'})]
    ids = []
    replies = []
    texts = []
    yous = []
    hasImage = []
    for item in htmlPosts:
        ids.append(item['id'].lstrip('pc'))
        replies.append([x.lstrip('>>') for x in re.findall(">>[0-9]+" , item.find_next(name="blockquote").text)])
        texts.append(removeReplies(item.find_next(name="blockquote").text))
        hasImage.append((True if item.find(class_="file") else False))
        yous.append(0)
    df = pd.DataFrame(
        {
            'id' : ids,
            'replies' : replies,
            'text' : texts,
            'youCount' : yous,
            'hasFile' : hasImage
        }
    )
    return df


class chanThread:
    def __init__(self, link: str = "", dataFrame: pd.DataFrame = None ):
        if link != "":
            self.link = link
            self.soup = BeautifulSoup(requests.get(link).content, 'html.parser')
            self.posts = htmlToPd(self.soup)
            self.setYous()
        else:
            self.link = None
            self.posts = dataFrame
            self.soup = None

    def refreshSoup(self):
        self.soup = BeautifulSoup(requests.get(self.link), 'html.parser')

    def isAlive(self):
        response = requests.get(self.link)
        if (response.status_code >= 400 or response.status_code < 200):
            False
        html = BeautifulSoup(response.raw, features='lxml')
        if html.find("div",class_="closed"):
            return False
        return True

    def setYous(self):
        for item in self.posts.index:
            for n in range(item, self.posts.last_valid_index()):
                if self.posts.iloc[item]['id'] in self.posts.iloc[n]['replies']:
                    self.posts.at[item,'youCount'] += 1

    def refreshSelf(self):
        self.refreshSoup()
        self.posts = htmlToPd(self.soup)
        self.setYous()

        