from lib2to3.pgen2 import driver
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import re

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
            if(len(reply_list) => minreplies):
                return False #not enough replies, invalid
            post_message = post.find_element(By.CLASS_NAME,'postMessage').text
            match = re.search("[Nn]ominating.*from.*[.]",post_message)
            if match:
                return True #fits the bill, passed all tests, valid post
            else:
                return False #doesnt fit the pattern, invalid


def get_posts(link): #goes to link, returns list of post webelements
    options = webdriver.FirefoxOptions()
    options.add_argument("--headless")

    driver = webdriver.Firefox(options=options)
    driver.get(link)
    sleep(5)
    post_list = driver.find_elements(By.CLASS_NAME, 'postContainer')

    #driver.close()
    return post_list

#
def handle_posts(posts, minreplies): #takes the original post list, converts into valid string list to archive
    valid_posts = []

    for post in posts:
        if is_post_valid(post,minreplies): #remove invalids from list
            valid_posts.append(post)

    item_list = []
    for post in valid_posts:
       postmessage = post.find_element(By.CLASS_NAME,'postMessage').text
       templist = re.split(r"[Nn]ominating|[.]", postmessage) #MIND THE ENDING DOT
       postmessage = templist[1] #now postmessage holds only "x from y"
       postmessage = re.sub('from','(',postmessage)+')'#postmessage is now x( y)
       item_list.append(postmessage)
    

    return item_list






