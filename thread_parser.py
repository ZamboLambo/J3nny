import string
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import re

def find_nomination(post): #tries to find a way to convert message to "character (series)"
                     #returns message unaltered if failed to 
                    #delete multispaces leftover from deleting replies+newlines
    if(re.search("(   )",post)):
        temp = re.split("   ",post,1)
        post = temp[0]


    nomination = re.search("(Nominating|nominating|NOMINATING|nominate).*(from|FROM).*(.|/n)",post)
    if nomination:
        x = nomination.group()
        x = re.sub("(Nominating|nominating|NOMINATING|nominate)",'',x)
        x = re.sub("(from |FROM )",'(',x)
        x = x + ')'
        return x
    from_ = re.search("(from|FROM)",post)
    if from_:
        x = re.sub("(from |FROM )",'(' ,post)
        x = x + ')'
        return x
    return post #no pattern, shove in sheet as is





def remove_replies(postmessage):
    replies = re.findall(">.*\d",postmessage)
    if(replies):
       x = re.sub(">.*\d",'',postmessage)
       if(re.search("'('OP')'",x)):
            x = re.sub("('('OP')'\n)",'',x)
       return x
    return postmessage

def remove_newlines(postmessage):
    newlines = re.findall("\n",postmessage)
    if(newlines):
        x = re.sub("\n", " ", postmessage)
        return x
    return postmessage
    

def is_post_valid(post,minreplies):
    try:
        post.find_element(By.TAG_NAME,"img")
    except NoSuchElementException:
        return False #no image attached, invalid
    else:
        try:
            post.find_element(By.CLASS_NAME,'backlink')
        except NoSuchElementException:
            return False #no replies, invalid
        else:
            replies = post.find_element(By.CLASS_NAME,'backlink').text
            reply_list = replies.split()
            if(len(reply_list) < minreplies):
                return False #not enough replies, invalid
            return True

def convert_to_pattern(str):
    #converts given string to valid pattern in archive links
    str_ = str.lower()
    table = str_.maketrans('','',string.punctuation)
    str_ = str_.translate(table)
    table = str_.maketrans(' ', '-')
    str_ = str_.translate(table)
    return str_


def handle_posts(posts, minreplies): #takes the original post list, converts into valid string list to archive
    valid_posts = []

    for post in posts:
        if is_post_valid(post,minreplies) and (post != posts[0]): #remove invalids and OP from list
            valid_posts.append(post)

    item_list = []
    for post in valid_posts:
       postmessage = post.find_element(By.CLASS_NAME,'postMessage').text
       postmessage = remove_replies(postmessage)
       postmessage = remove_newlines(postmessage)
       postmessage = find_nomination(postmessage)


       item_list.append(postmessage)
    

    return item_list






