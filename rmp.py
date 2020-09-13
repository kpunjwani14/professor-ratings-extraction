#!/usr/bin/env python
from fuzzywuzzy import fuzz 
import copy
from fuzzywuzzy import process 
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import ActionChains
import time
import sys
import csv
import mysql.connector
from mysql.connector import errorcode
from mysql.connector import MySQLConnection, Error
import sys
import re
import sys

try:
  cnx = mysql.connector.connect(user='root',password='',
                                 host='', database='test')
except mysql.connector.Error as err:
  if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
    print("Something is wrong with your user name or password")
  elif err.errno == errorcode.ER_BAD_DB_ERROR:
    print("Database does not exist")
  else:
    print(err)
  sys.exit(0)


def waitForElement(e,time):
    try:
        WebDriverWait(driver, time).until(EC.presence_of_element_located((By.CSS_SELECTOR, e)))
    except(TimeoutException):
        return False
    return True



def match(rmp):
    
    for x in dic:
        if(fuzz.token_set_ratio(x.lower(),rmp)==100):
            return x
    return ''

 


rows=[]
fields=[]

links={}

dic={}
month = {'Jan':1, 'Feb':2, 'Mar':3, 'Apr':4, 'May':5, 'Jun':6, 'Jul':7, 'Aug':8, 'Sep':9, 'Oct':10, 'Nov':11, 'Dec':10}
mycursor=cnx.cursor()
fName='Cougargrades/'
filename=[fName+'Fall2019.csv',fName+'PICK-A-PROF-UH_Fall 2018.xls.csv',fName+'Grade Distribution_Spring 2019.csv',fName+'Spring20.csv']

mycursor.execute('select * from proftest;')
for f in mycursor:
    dic[f[1]]=f[0]
backup=copy.deepcopy(dic)
print(len(dic))
def buttonExists(elem):
    try:
       driver.find_element_by_css_selector(elem)
    except (NoSuchElementException):
        return False
    return True
def checkLen():
    driver.refresh()
    WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".progressbtnwrap[style='display: block;'] > .content")))
    element= driver.find_element_by_css_selector(".progressbtnwrap[style='display: block;'] > .content")
    while buttonExists(".progressbtnwrap[style='display: block;'] > .content"):
        driver.execute_script("arguments[0].click();", element)
    
def load_but(ratings,load_ratings):

    while ( len(ratings)<100 and buttonExists(load_ratings)):
         try:
            but=driver.find_element_by_css_selector(load_ratings)
         except (NoSuchElementException):
             break
         try:
             WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, load_ratings))) 
         except (TimeoutException):
            if(buttonExists(load_ratings)):
                return False
            break
         #try:
        
          #except:
             #pass
       
         but.click()
         time.sleep(.5)
         ratings=driver.find_elements_by_css_selector(".Rating__StyledRating-sc-1rhvpxz-1.jcIQzP")
         print (len(ratings))
    return True
chrome_options = Options()
# chrome_options.add_argument("--headless")
# chrome_options.add_argument("--window-size=1920x1080")

driver = webdriver.Chrome(chrome_options=chrome_options,executable_path='/mnt/c/Program Files (x86)/chromedriver.exe')

driver.get('https://www.ratemyprofessors.com/search.jsp?queryBy=schoolId&schoolName=University+of+Houston&schoolID=1109&queryoption=TEACHER')

WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.CLASS_NAME, "ccpa-close")))
driver.find_element_by_class_name("ccpa-close").click()
elem= driver.find_element_by_css_selector(".side-panel > .result-list ul")
prof=elem.find_elements_by_tag_name("li")   

# elem= driver.find_element_by_css_selector(".side-panel > .result-list ul")
# prof=elem.find_elements_by_tag_name("li")
profCount=0
errorCount=0
notFound=0
bsError=0
while len(links)<1200:
    checkLen()
    links.clear()
    front_page=BeautifulSoup(driver.page_source,features="html.parser")
    prof=front_page.find('div',class_="side-panel").find('div',class_='result-list').find_all('li')
    url='https://www.ratemyprofessors.com' 
    dic=copy.deepcopy(backup)
    for p in prof:
        rmp=p.find('span',class_='name').contents[0].strip().split(',')
        prof_match=match(rmp[0].lower()+' '+rmp[1].lower())
        if(prof_match!='' and int(p.find('span',class_='info').text.split(' ',1)[0])!=0):
            print(prof_match,int(p.find('span',class_='info').text.split(' ',1)[0]) )
            links[url+p.find('a').get('href')]=dic[prof_match]
            print(links[url+p.find('a').get('href')])
            del dic[prof_match]
            
    print(len(links)) 
del dic
del backup

for l in links:
    finished=False
    while not finished:
        driver.get(l)
    
        if(buttonExists("div.header.error")):   
            notFound+=1
            continue
        if not waitForElement('div.NameTitle__Name-dowf0z-0.jeLOXk',10):
                errorCount+=1
                continue
        if not waitForElement('.Rating__StyledRating-sc-1rhvpxz-1.jcIQzP',10):
                errorCount+=1
                continue
                
                
        ratings=driver.find_elements_by_css_selector(".Rating__StyledRating-sc-1rhvpxz-1.jcIQzP")
        load_ratings="button.Buttons__BlackButton-sc-19xdot-1.PaginationButton__StyledPaginationButton-txi1dr-1.fwhQq"
        
        if(not load_but(ratings,load_ratings)):
            
            print ('driver did not work')
            errorCount+=1
            continue

        teacher_page=BeautifulSoup(driver.page_source,features="html.parser")
        if(teacher_page.find('div',class_='header error')):   
            bsError+=1
            continue
        prof_name=teacher_page.find('div',class_="NameTitle__Name-dowf0z-0 jeLOXk").text
        rating=teacher_page.find('div',class_="RatingValue__Numerator-qw8sqy-2 gxuTRq").text
        rev=teacher_page.find_all('div',class_="Rating__StyledRating-sc-1rhvpxz-1 jcIQzP")
        print ('Professor Name: ',prof_name)
        print('Rating: ',rating)
        mycursor.execute("UPDATE proftest SET prof_rating = %s WHERE id = %s;" % (rating,links[l]))
        i=0
        
        while i<len(rev) and i<100:
                r=rev[i]
                class_name=r.find('div',class_="RatingHeader__StyledClass-sc-1dlkqw1-2 eOgHRd").text.replace("\'","\'\'")
                qd=r.find_all('div',class_="RatingValues__RatingValue-sc-6dc747-3")
                quality=qd[0].text
                difficulty=qd[1].text
                description=r.find('div',class_="Comments__StyledComments-dzzyvm-0 dvnRbr").text
                description=description.replace("\'","\'\'")
                date=r.find('div',class_="TimeStamp__StyledTimeStamp-sc-9q2r30-0 bXQmMr RatingHeader__RatingTimeStamp-sc-1dlkqw1-3 BlaCV").text
                mod_date=date.split(' ')
           
                
                date=mod_date[2]+'-'+str(month[mod_date[0]])+'-'+mod_date[1]
                ld=r.find_all('div',class_="RatingFooter__HelpTotal-ciwspm-2 kAVFzA")
                likes=ld[0].text
                dislikes=ld[1].text
                print ('Class Name: ',class_name )
                print ('Quality: ',quality)
                print ('Difficulty: ',difficulty)
                print ('Description: ',description)
                query_extra=''
                vals=''
                recs=r.find_all('div',class_="MetaItem__StyledMetaItem-y0ixml-0 ezVUqy")
                
                    
                for re in recs:
                    sp=re.text.split(':')
                    query_extra+=(sp[0].replace(" ","_")+",")
                    vals+=("\""+sp[1][1:]+"\""+",")
                    print (re.text)

                print ('Date: ',date )
                
                
                print ('Likes: ',likes)
                print ('Dislikes', dislikes)
                i+=1
                mycursor.execute("insert into ratings(%s prof_id,description,quality,difficulty,likes,dislikes,date) values(%s \"%s\",\'%s\',\"%s\",\"%s\",\"%s\",\"%s\",\"%s\");" % (query_extra,vals,links[l],description,quality,difficulty,likes,dislikes,date))
               
        cnx.commit()
        if (i!=100 and i!=len(rev)) or i==0:
                sys.exit(0)
        finished=True     


          
   






