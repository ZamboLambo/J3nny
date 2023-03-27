import string
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import re
from selenium import webdriver
from urllib.request import urlopen
from urllib.error import HTTPError
from bs4 import BeautifulSoup

def get_threadarchived(pattern,board): 
    #Gets first thread link from archive based on pattern
    #Pattern is thread title or if theres none, body of text
    #4chan archives automatically remove special characters, make it lowercase and replace spaces with -
    #return value is string or 0 if failed to find
    html = urlopen("https://boards.4channel.org/" + board + "/archive")
    bsobj = BeautifulSoup(html, 'html.parser')
    match = str(bsobj.find(href = re.compile(pattern)))
    cut1 = re.split(pattern,match)
    cut2 = re.split("href=\"",cut1[0])
    if len(cut2) > 1:
        thread = "https://boards.4channel.org" + cut2[1]
        return thread
    return 0

def is404(thread):
    #give a link, returns if its a 404 page
    try:
        x = urlopen(thread)
    except HTTPError as e:
        if e.code == 404:
            return True
    else:
        return False

def isarchived(thread):
    #give link, returns if its an archived thread
    html = urlopen(thread)
    soup = BeautifulSoup(html, 'html.parser')
    if soup.find("div",class_="closed"):
        return True
    return False

def get_threadcatalog(pattern,board):
    #goes through catalog, returns thread link or 0 if failed to find
    html = urlopen("https://boards.4channel.org/" + board + "/catalog")
    bsobj = BeautifulSoup(html, 'html.parser')
    script = bsobj.find_all("script")
    t = str(script[4])
    results = (re.search("(var catalog = {\"threads\":)(.*)(}})",t).group(2))
    old = results
    results = results.split(pattern)[0]
    if old == results:
        #pattern not found
        return 0
    matches = re.findall("\"(\d+)\"", results)
    matches.reverse()
    thread = "https://boards.4channel.org/" + board + "/thread/" + matches[1]
    return thread

def find_nomination(post): 
    #tries to find a way to convert message to "character (series)"
    #returns message unaltered if failed to 
    #delete multispaces leftover from deleting replies+newlines
    if(re.search("( {3})",post)):
        temp = re.split(" {3}",post,1)
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

def convert_to_archivepattern(str):
    #converts given string to valid pattern in archive links
    str_ = str.lower()
    table = str_.maketrans('','',string.punctuation)
    str_ = str_.translate(table)
    table = str_.maketrans(' ', '-')
    str_ = str_.translate(table)
    return str_

def handle_posts(posts, minreplies): 
    #takes the original post list, converts into valid string list to archive
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

def scrape_thread(thread,results,minreplies):
    #scrapes and archive, return is only the thread's page
    print("Beginning scrape routine of " + thread)

    options = webdriver.FirefoxOptions()
    options.add_argument("--headless")

    driver = webdriver.Firefox(options=options)
    driver.get(thread)
    post_list = driver.find_elements(By.CLASS_NAME, 'postContainer')
    character_list = handle_posts(post_list,minreplies)
    threadnumber = driver.find_element(By.CLASS_NAME, 'ts-page').text
                
    driver.close()
    try:
        open(results)
    except FileNotFoundError:
        open(results,'x')
    finally:
        a = open(results,"a", encoding="utf-8")
        for item in character_list:
            if (item != "" and item != " " and len(item) < 100):
                a.write(item + "\n")
        a.close()

        print(str(len(character_list)) + " nominations added to nomination file.")
    return int(threadnumber)

def scrape_archived_thread(pattern,board,scraped,results,minreplies):
        
    try:
        open(scraped)
    except FileNotFoundError:
        open(scraped,'x')
    finally:
        f = open(scraped,"r+", encoding="utf-8")
        fields = []
        for line in f:
            fields = line.split()

        curr_thread = get_threadarchived(pattern,board)

        if curr_thread and curr_thread not in fields: 
            scrape_thread(curr_thread,results,minreplies)


        else:
            f.close() #scraped already, close file and do nothing
