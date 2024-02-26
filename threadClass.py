from bs4 import BeautifulSoup
import requests
import re
from postClass import Post

class chanThread:
    def __init__(self, link: str):
        self.link = link
        self.soup = BeautifulSoup(requests.get(link).content, 'html.parser')
        self.posts = [Post(x) for x in self.soup.findAll(name='div', attrs={'class': 'postContainer replyContainer'})]
        self.setYous()

    def refreshSoup(self):
        self.soup = BeautifulSoup(requests.get(self.link), 'html.parser')

    def isAlive(self):
        response = requests.get(self.link)
        if (response.status_code == 404):
            False
        html = BeautifulSoup(response.raw, features='lxml')
        if html.find("div",class_="closed"):
            return False
        return True

    def is404(self):
        response = requests.get(self.link)

        if (response.status_code == 404):
            return True
        return False

    def isarchived(self):
        self.refreshSoup()
        if self.soup.find("div",class_="closed"):
            return True
        return False

    def setYous(self):
        for x in range(len(self.posts)):
            youCount = 0
            id = self.posts[x].id
            for n in range(x, len(self.posts)):
                if id in self.posts[n].replies:
                    youCount += 1
            self.posts[x].yous = youCount

    def refreshSelf(self):
        self.refreshSoup()
        self.posts = [Post(x) for x in self.soup.findAll(name='div', attrs={'class': 'postContainer replyContainer'})]
        self.setYous()

            




test_link = "https://boards.4chan.org/int/thread/194152481"

thread = chanThread(test_link)
print(thread.isAlive())
print(thread.posts[0].hasImage)
print(thread.posts[0].text)
