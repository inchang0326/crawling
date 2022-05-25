from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import time

def launchBrowser(url, headless):
    # headless setting : no popup the browser
    options = webdriver.ChromeOptions()
    options.headless = headless
    options.add_argument("window-size=1440x900")
    #
    browser = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    browser.get(url)
    return browser

def paging() :
    # paging
    prevLocation = browser.execute_script("return document.body.scrollHeight")

    while(True) :
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight)")
    
        time.sleep(0.5)

        currLocation = browser.execute_script("return document.body.scrollHeight")

        if prevLocation == currLocation :
            break
        else :
            prevLocation = currLocation

def career_to_skt(jobTitle) :
    # filtering
    # job search click
    search = browser.find_element_by_class_name("recruit-search-box")
    jobSearch = search.find_element_by_id("JobRole")
    action = ActionChains(browser)
    action.move_to_element(jobSearch).click(jobSearch).perform()

    # job item click
    jobItems = search.find_elements_by_tag_name("li")
    for jobItem in jobItems :
        if jobTitle in jobItem.text :
            jobItem.click()
            break

    time.sleep(0.5)

    # skt
    skt = browser.find_element_by_id("Corp5")
    browser.execute_script("arguments[0].click();", skt)

    time.sleep(0.5)

    # paging
    paging()
    
    # get job-list size
    jobsLength = int(len(browser.find_elements_by_class_name("recruit-list-item")))

    # job desc parsing and write on html
    filePath = "sktjobs.html"
    with open(filePath, "w") as sktjobs:
        for i in range(0, jobsLength):
            jobs = browser.find_elements_by_class_name("recruit-list-item")
            jobDetail = jobs[i].find_element_by_tag_name("a")
            link = jobDetail.get_attribute("href")

            action = ActionChains(browser)
            action.move_to_element(jobDetail).click(jobDetail).perform()
    
            browser.switch_to.window( browser.window_handles[ i + 1 ] )

            soup = BeautifulSoup(browser.page_source, "lxml")
            sktjobs.write("<h2><a href='" + link + "' style='color:black; text-decoration:none;'/>" + str(soup.find("div", attrs={"class", "job-title"})) + "</h2>")
        
            contents = soup.find_all("div", attrs={"class", "guide-content"})
            sktjobs.write(str(contents[1]))
            sktjobs.write("<hr></br>")
            browser.switch_to.window( browser.window_handles[ 0 ] )

def career_to_woowahan(jobTitle) :
    # filtering
    # development click
    keywords = browser.find_elements_by_class_name("keyword-list")
    for keyword in keywords:
        button = keyword.find_element_by_tag_name("button")
        if "개발" in button.text :
            action = ActionChains(browser)
            action.move_to_element(button).click(button).perform()            
            break

    time.sleep(0.5)
    
    # server/backed click
    checkbox = browser.find_element_by_xpath("//*[@id='PCAppMain']/div[3]/section/aside/div/div[2]/ul")
    jobItems = checkbox.find_elements_by_tag_name("li")
    for jobItem in jobItems :
        if jobTitle in jobItem.text :
            jobItem.click()
            break    

    time.sleep(0.5)

    # paging
    paging()
    
    # get job-list size
    jobsLength = int(len(browser.find_element_by_class_name("recruit-type-list").find_elements_by_tag_name("li")))

    # job desc parsing and write on html
    filePath = "woowahanjobs.html"
    with open(filePath, "w") as woowahanjobs:
        for i in range(0, jobsLength):
            time.sleep(2)
            jobs = browser.find_element_by_class_name("recruit-type-list").find_elements_by_tag_name("li")
            jobDetail = jobs[i].find_element_by_tag_name("a")
            link = jobDetail.get_attribute("href")

            action = ActionChains(browser)
            action.move_to_element(jobDetail).key_down(Keys.COMMAND).click(jobDetail).key_up(Keys.COMMAND).perform()
            
            browser.switch_to.window( browser.window_handles[ i + 1 ] )

            time.sleep(3)
            # soup = BeautifulSoup(browser.page_source, "html.parser")
            # print(soup.prettify())
            woowahanjobs.write("<h2><a href='" + link + "' style='color:black; text-decoration:none;'/>" + "우아한형제들 " + browser.find_element_by_class_name("title").text + "</h2>")

            stringList = browser.find_elements_by_tag_name("strong")
            for string in stringList :
                if "[지원자격]" in string.text :
                    woowahanjobs.write(string.find_element_by_xpath("..").text)
                    woowahanjobs.write("</br>")
                elif "[개발환경]" in string.text :
                    woowahanjobs.write(string.find_element_by_xpath("..").text)                
            woowahanjobs.write("<hr></br>")
            browser.switch_to.window( browser.window_handles[ 0 ] )       

def career_to(i) :
    if i == 0 :
        career_to_skt("Backend")
    else :
        career_to_woowahan("백엔드")

url = ["https://thecareers.sktelecom.com/Recruit", "https://career.woowahan.com/"]
urlLength = len(url)

for i in range(0, urlLength):
    # browser launch
    browser = launchBrowser(url[i], True)
    # dynamic scraping
    career_to(i)


# browser = launchBrowser(url[1], True)
# career_to(1)
