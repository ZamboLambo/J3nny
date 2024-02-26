import re


def removeReplies(postmessage):
        sub = re.sub(">>[0-9]+",'',postmessage)
        return sub

class Post:
    #just pass its individual postreply postcontainer and it ought to handle setting itself
    def __init__(self, htmlSoup):
        self.id = htmlSoup['id'].lstrip('pc')
        self.replies = [x.lstrip('>>') for x in re.findall(">>[0-9]+" , htmlSoup.find_next(name="blockquote").text)]
        self.text = removeReplies(htmlSoup.find_next(name="blockquote").text)
        self.yous = 0
        self.hasImage = True if htmlSoup.find(class_="file") else False

