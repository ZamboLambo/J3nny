from lib2to3.pgen2 import driver
import string
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
            if(len(reply_list) <= minreplies):
                return False #not enough replies, invalid
            post_message = post.find_element(By.CLASS_NAME,'postMessage').text
            match = re.search("[Nn]ominating.*from.*[./n]",post_message)
            if match:
                if ( match.span()[1] - match.span()[0]) - (len("Nominating from ")) < 62:
                    #checking if series + character name is too big
                    #just in case someone tries giving the bot a whole copypasta
                    #upper limit is considered the verbose combo that is 'Nominating ichiro "chiro" takagi from super robot monkey team hyperforce go!'
                    return True #fits the bill, passed all tests, valid post
            else:
                return False #doesnt have the pattern or too long, invalid

def convert_to_pattern(str):
    #converts given string to valid pattern in archive links
    str_ = str.lower()
    table = str_.maketrans('','',string.punctuation)
    str_ = str_.translate(table)
    table = str_.maketrans(' ', '-')
    str_ = str_.translate(table)
    return str_

def get_posts(link): #goes to link, returns list of post webelements
    options = webdriver.FirefoxOptions()
    options.add_argument("--headless")

    driver = webdriver.Firefox(options=options)
    driver.get(link)
    sleep(5)
    post_list = driver.find_elements(By.CLASS_NAME, 'postContainer')

    #driver.close()
    return post_list

def handle_posts(posts, minreplies): #takes the original post list, converts into valid string list to archive
    valid_posts = []

    for post in posts:
        if is_post_valid(post,minreplies): #remove invalids from list
            valid_posts.append(post)

    item_list = []
    for post in valid_posts:
       postmessage = post.find_element(By.CLASS_NAME,'postMessage').text
       templist = re.split(r"[Nn]ominating|[./n!]", postmessage) #MIND THE ENDING PUNCTUATION
       postmessage = templist[1] #now postmessage holds only "x from y"
       postmessage = re.sub('from','(',postmessage)+')'#postmessage is now x( y)
       item_list.append(postmessage)
    

    return item_list






