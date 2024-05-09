from bs4 import BeautifulSoup, SoupStrainer
import requests
import re
import pandas as pd
import numpy as np
import lxml
import time

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

def flatten(xss):
    return [x for xs in xss for x in xs]

def crossCompare(listA, listB):
    #given A and B 1d lists return a list with count of 
    #A shape with count of how many A[i] items are in B
    x = np.array(listA)
    comparator = np.array(listB)
    comparator = np.broadcast_to(comparator,(x.shape[0],comparator.shape[0]))
    
    return  np.sum(x == np.rollaxis(comparator,1), axis=0).tolist()

class chanThread:
    def __init__(self, link: str = "", dataFrame: pd.DataFrame = None ):
        if link != "":
            self.link = link
            relevantInfo = SoupStrainer("div",{"class": "board"})
            self.soup = BeautifulSoup(requests.get(link).content, 'lxml', parse_only=relevantInfo)



            self.posts = htmlToPd(self.soup)
            self.setYous()
        else:
            self.link = None
            self.posts = dataFrame
            self.soup = None

    def isAlive(self):
        response = requests.get(self.link)
        if (response.status_code >= 400 or response.status_code < 200):
            return False
        html = BeautifulSoup(response.raw, features='lxml')
        if html.find("div",class_="closed"):
            return False
        return True

    def setYous(self): 
        replyList = self.posts["replies"].to_list()
        replyList = flatten(replyList)
        self.posts["youCount"] = crossCompare(self.posts["id"], replyList)

        