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


def waitForElement(e,time):
    try:
        WebDriverWait(driver, time).until(EC.presence_of_element_located((By.CSS_SELECTOR, e)))
    except(TimeoutException):
        return False
    return True



def buttonExists(elem):
    try:
       driver.find_element_by_css_selector(elem)
    except (NoSuchElementException):
        return False
    return True

def load_but(ratings,load_ratings):
    
    while ( len(ratings)<100 and buttonExists(load_ratings)):
         if not buttonExists(load_ratings):
            break
         else:
             but=driver.find_element_by_css_selector(load_ratings)
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
WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".progressbtnwrap[style='display: block;'] > .content")))
element= driver.find_element_by_css_selector(".progressbtnwrap[style='display: block;'] > .content")

while buttonExists(".progressbtnwrap[style='display: block;'] > .content"):
    driver.execute_script("arguments[0].click();", element)

# elem= driver.find_element_by_css_selector(".side-panel > .result-list ul")
# prof=elem.find_elements_by_tag_name("li")
front_page=BeautifulSoup(driver.page_source,features="html.parser")
prof=front_page.find('div',class_="side-panel").find('div',class_='result-list').find_all('li')
url='https://www.ratemyprofessors.com' 


profCount=0
errorCount=0
pr=0
notFound=0
while pr<len(prof) and not prof[pr].find('span',class_='zero-icon'):
   p=prof[pr]
   link= p.find('a').get('href')
   print (url+link)
   driver.get(url+link)
  
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
   
   rev=teacher_page.find_all('div',class_="Rating__StyledRating-sc-1rhvpxz-1 jcIQzP")
   print ('Professor Name: ',teacher_page.find('div',class_="NameTitle__Name-dowf0z-0 jeLOXk").text)
   i=0
   
   while i<len(rev) and i<100:
         r=rev[i]
         print ('Class Name: ', r.find('div',class_="RatingHeader__StyledClass-sc-1dlkqw1-2 eOgHRd").text)
         qd=r.find_all('div',class_="RatingValues__RatingValue-sc-6dc747-3")
         print ('Quality: ',qd[0].text)
         print ('Difficulty: ',qd[1].text)
         print ('Description: ',r.find('div',class_="Comments__StyledComments-dzzyvm-0 dvnRbr").text)
         recs=r.find_all('div',class_="MetaItem__StyledMetaItem-y0ixml-0 ezVUqy")
         for re in recs:
             print (re.text)
         print ('Date: ', r.find('div',class_="TimeStamp__StyledTimeStamp-sc-9q2r30-0 bXQmMr RatingHeader__RatingTimeStamp-sc-1dlkqw1-3 BlaCV").text)
         ld=r.find_all('div',class_="RatingFooter__HelpTotal-ciwspm-2 kAVFzA")
         print ('Likes: ',ld[0].text)
         print ('Dislikes', ld[1].text)
         i+=1
   if i!=100 and i!=len(rev):
        sys.exit(0)
   profCount+=1
   print ('ErrorCount= ',errorCount)
   print ('Not Found ErrorCount= ',errorCount)
   print ('ProfCount= ',profCount)
   pr+=1


