# python version: 3.11.5
# selenium version: 4.12.0
##Installing pip advised
#OS: windows 10

#Imported libraries to support code
import csv
from datetime import date
import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
import json

# set up the webdriver
#There are many webdriver manager options and they could be different for different browsers of choice. I used a webdriver manager. From my understanding, a webdriver manager automates some of the environment variables instead of having to do them manualy.

#“WebDriverManager automates the management of WebDriver binaries, thereby avoiding installing any device binaries manually.
#WebDriverManager checks the version of the browser installed on your machine and downloads the proper driver binaries into the local cache (~/.cache/selenium by default) if not already present.

driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
#I put in class format so that it is possible to create objects or call certain methods from other classes. For example, In a separate function, I would be able to call multiple classes’ main methods to run all of them at once.
class SpaceScrape():

#returns the name of the file with the current date
    def file_name(self):
        x = date.today()
        return ("SpaceX " + str(x) + ".csv")
    

     #Find the last element on the page by scrolling down
    #This is necessary to load more jobs on the page. Some pages only load some jobs and load more when you scroll to the bottom
   #method mainly comprises of javascript code scrolls to end of page and returns height of page
# How it works:
            #sets lastCount as lenOfPage
            #waits a second to load more postings
            # runs the script:
            # if there are more jobs then 
                #   lenOfPage will be more than last count
            #else
                # if there are no more jobs loaded lenOfPage will have not changed
                #  and will be equal to lastCount
                #in which case while loop will terminate

    def scroll(self):    
        
        script = ("window.scrollTo(0, document.body.scrollHeight);"
                  "var lenOfPage=document.body.scrollHeight;"
                  "return lenOfPage;")
        
        lenOfPage = driver.execute_script(script)
        match=False
        while(match==False):
            lastCount = lenOfPage
            time.sleep(1)
            lenOfPage = driver.execute_script(script)

            if lastCount==lenOfPage:
                match=True


#This method is meant to find certain fields on the webpage. This is invoked after the webpage for specific job postings is opened
    def heads(self):
#It is more organized to use dictionaries rather than discrete lines and also is compatible with DictWriter method (in main()) that can write a whole dictionary at once instead of separate lines and organizes the fields and field names.
#Each “Key” is given a default “Value” so that if the element is not found on a page, the default value would be output
        titles = {
            'jobTitle'    : "Title_Unavailable",
            'jobLocation' : "Location_Unavailable",
            'date_posted' : "Date_Posted_Unavailable"
        }
#Try-except blocks are used for exception handling and so that the code keeps running if element is not found
        try:
# 'jobTitle' is found using XPath as it has an <h1> tag and a class name of ‘app-title’
# .text is used to return the text attribute of the element rather than a web element or a web element address
# .replace("\n","") is used to remove all ‘\n’ from the string returned. Otherwise, it is processed by the output file and could induce incosistencies
            titles['jobTitle'] = driver.find_element(By.XPATH, "//h1[@class='app-title']").text.replace("\n","")
        except Exception:
            pass # if element is not found…skip it and keep going instead of breaking. the default is the string "...unavailable" above is returned if element is not available    
        
        try:
            titles['jobLocation'] = driver.find_element(By.XPATH, "//div[@class='location']").text.replace("\n","")
        except Exception:
            pass

        
        #The date posted was not available on the page under a unique tag. However, it could be found in a very large script. I had to use an online JSON parser to find its placement or the layer at which it exists to extract accordingly
 
 
#elem finds the specific script that contains the date posted
#often times the script tag does not have any unique identifiers like ‘type’ in this case. In the case that it does not you would have to find another way to locate…possibly its order or some unique substring
        elem = driver.find_element(By.XPATH, "//script[@type='application/ld+json']")
        jsontext = json.loads(elem.get_attribute('innerHTML'))

        try:
	#luckily it was just in the outermost loop without much nesting
            titles['date_posted'] = jsontext['datePosted']
        except Exception:
            pass

#return the whole dictionary after finding the different elements
        return titles
        
    
# description method finds another set of fields or elements on the specific pages. It is built in a similar fashion to the headings() function above. 
    def descriptions(self):

        desc = {
            'Overview'  : "Overview not available",
            'Responsibilities' : "Responsibilities is not availvble",
            'Qualifications'    : "Description not available",
            #'preferred_Qualifications' :  "preferred_Qualifications unavailable"
        }
        
        
        
        # To find expect & do there are two divs with attribute //div[contains(@class,'style_descriptionItem')]
        try:
# This Xpath returns the list or <ul> elements that follow the <div> with ‘content’ id. The list of responsibilities happens to always be the first list. Hence the [0]
           desc["Responsibilities"]  = driver.find_elements(By.XPATH, ("//div[@id='content']//ul"))[0].text.replace("\n","")
        except Exception:
            pass

# This block is not yet functioning 
        try:
            desc["Overview"]    = driver.find_elements(By.XPATH, "//*[@id='content']/descendant::text()")[2].text
        except:
            pass

# For the Qualifications block, finding the second list <ul> used to not work for a few pages. So I decided to find the list right under the “Qualifications” line. However, it used to be sometimes in a <strong> and other times in a <b> so I had to try both by using a nested try-except block.

#I also could not just use //*[contains(text()... in the Xpath because there was a similar text in the JSON <script> tag described earlier. Some of them elements in the JSON Script also have a <strong> so the Xpath had to be what is seen below.
# The parent tags of the <strong> or the <b> were not consistent either so I had to use *
        try:
            desc["Qualifications"]    = driver.find_elements(By.XPATH, "//*/strong[contains(text(), 'BASIC QUALIFICATIONS')]//following::ul")[0].text
            print(desc["Qualifications"])
        except:
            try:
                desc["Qualifications"]    = driver.find_elements(By.XPATH, "//*/b[contains(text(), 'BASIC QUALIFICATIONS')]//following::ul")[0].text
            except:
                pass
        
        return desc
    
#This method is invoked by the main() method for every job posting 
    def get_Job_Details(self, job):

#It gets the link (‘href’) attribute from every job webelement
        posting = job.get_attribute("href")

#Opens a new window and switches to it
        driver.execute_script("window.open('');")
        window_after = driver.window_handles[1]
        driver.switch_to.window(window_after)

#Opens job posting in new window
        driver.get(posting)

#finds heading and descriptions from that page using heads() and descriptions() method above
#assigns dictionaries returned to variables ‘headings’ and ‘description’
        headings = self.heads()
        description = self.descriptions()

        #defining a new dictionary that merges both dictionaries: headings & descriptions
# When writing to the CSV file, the writerow() method of the DictWriter writes a dictionary per row…so I had to combine to write all headings and descriptions on the same row
        temp = headings
        headings.update(description)
        myDictionary = headings
        headings  = temp
#also added the link to job posting page to dictionary
        myDictionary['url_link'] = str(posting)
#returns dictionary with all required fields 
        return myDictionary


#Main method that does the magic  
    def main(self):
        
        #Opens the SpaceX careers webiste
        driver.get("https://www.spacex.com/careers/jobs/")
        #gives it a second to load
        time.sleep(1)

        #setting implicit wait time to 4 seconds...in case something is not working, it will give it 4 seconds before breaking or moving on
        driver.implicitly_wait(4)
        #maximise window to full screen
        driver.maximize_window()
        #invokes scroll method to scroll to the bottom of the screen. I didn't tested it without. But it is good to be safe. Tesla website requires to load more jobs
        self.scroll()
        
        #The XPath with the link to the job postings
        firstPath = "//div[@id='jobs-list']//td/a"
        #returns a list of web elements of all the job postings
        elements = driver.find_elements(By.XPATH, firstPath) #creates a list of job postings on the landing page

        file_name = self.file_name()
        rowNames = ['jobTitle','jobLocation','date_posted', 'Overview','Responsibilities','Qualifications','url_link']
        with open(file_name, mode='w+', encoding='utf-8', newline='') as file:
            #creating a DictWriter object 'writer' to write dictionaries to CSV
            #It writes the field names as decribed in 'rowNames' above and also aligns input 'Keys' to field names
            #Be advised that DictWriter requires that number of inputs is equal to the number of field names.
                #So if you wanted to remove 'Overview from CSV' for example, you have to remove it from input in desc() method and also from rowNames list
            writer = csv.DictWriter(file, fieldnames=rowNames)   
            writer.writeheader()
            #repeats for every job posting in elements list
            for job in elements:
                #getting dictionary with all the desired values by invoking the get_Job_Details() method and passing the 'job' web element as parameter
                myDict = self.get_Job_Details(job)   
                #writes values of dictionary to CSV file     
                writer.writerow(myDict)
                #closes the window with the current job posting
                driver.close()
                #go back to main SpaceX careers landing page
                driver.switch_to.window(driver.window_handles[0])
            #when the loop is finished with all the job postings, close the webdriver and terminate browser testing
            driver.quit()

#calling upon main method to start running
if __name__=="__main__": 
    SpaceScrape().main()

