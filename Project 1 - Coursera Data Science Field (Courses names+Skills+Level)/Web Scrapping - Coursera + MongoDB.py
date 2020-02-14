#!/usr/bin/env python
# coding: utf-8




## The aim of this file is to scrape the coursera website specifically (data-science) courses.
## And get the corresponding required skills and level of difficulty of each course.
## Not only this! But also save this information into MongoDB. (DataBase)
## All of these will be done by google chrome driver & pymongo





#Import the needed libraries
from selenium import webdriver
import time
from bs4 import BeautifulSoup
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import pymongo





#Open google chrome driver
chromeBrowser = webdriver.Chrome(executable_path=r"C:\Users\Owner\Desktop\iNetworks - Internship\1\chromedriver.exe")
chromeBrowser.implicitly_wait(2) # seconds





#Go to the base URL of data-science
URL = 'https://www.coursera.org/browse/data-science'
chromeBrowser.get(URL)
time.sleep(5) 





#Function: Skill dropdown button (Click on it)

def skill_drop_down_click():
    skills = chromeBrowser.find_elements_by_class_name('Button_1w8tm98-o_O-icon_1rbfoc-o_O-sm_pd780u')[0]
    skills.click()
    time.sleep(0.25) 
    
##EOF





#Function: Level dropdown button (Click on it)

def Level_drop_down_click():
    levels = chromeBrowser.find_elements_by_class_name('Button_1w8tm98-o_O-icon_1rbfoc-o_O-sm_pd780u')[2]
    levels.click()
    time.sleep(0.25) 
    
##EOF





##Function: Click on apply button

def click_apply():
    apply_button = chromeBrowser.find_elements_by_class_name('Button_1w8tm98-o_O-primary_cv02ee-o_O-md_1jvotax')[0]
    apply_button.click()
    
    delay = 10
    try:
        WebDriverWait(chromeBrowser, delay).until(EC.presence_of_element_located((By.CLASS_NAME, 'ReactVirtualized__Grid__innerScrollContainer')))
    except TimeoutException:
        print("Loading took too much time!")
        
    html = chromeBrowser.page_source #Get the html code of the new page with the selected filters.
    soup = BeautifulSoup(html, 'html.parser')
    return soup
##EOF





##Function: Return the name of the courses with the selected filters
Courses_names = []
def courses_names(soup):
    time.sleep(0.5) 
    Courses_div = soup.find("div",{"class":"ReactVirtualized__Grid__innerScrollContainer"})
    if(Courses_div is None):
        time.sleep(2)
        Courses_div = soup.find("div",{"class":"ReactVirtualized__Grid__innerScrollContainer"})
        
    Courses = Courses_div.find_all("a", {"data-click-key":"browse.browse.click.offering_card"})
    
    ##For loop to get all the courses names
    for course_num in range(len(Courses)):
        Courses_names.append(Courses[course_num]['aria-label'])
    ##End of for
    return courses_names





##Function: Click on clear all filter

def clear_all_filter():
    clear_filter = chromeBrowser.find_elements_by_class_name("divider_1mxyv2r-o_O-Box_120drhm-o_O-centerAlign_19zvu2s-o_O-displayflex_poyjc")[0]
    clear_filter.click()
    time.sleep(0.25) 





##Function: Click on Type and then select courses only.

def type_courses():
    type_ = chromeBrowser.find_elements_by_class_name("Button_1w8tm98-o_O-icon_1rbfoc-o_O-sm_pd780u")[4]
    type_.click()
    time.sleep(0.25)
    select_courses = chromeBrowser.find_elements_by_class_name("input_3xha1c-o_O-active_ro0g1e")[0]
    select_courses.click()





##Function: To clear the skills only.

def clear_skills_only():
    clear_skills = chromeBrowser.find_element_by_class_name("Button_1w8tm98-o_O-link_wjki9h-o_O-md_1jvotax.filter-clear-button")
    clear_skills.click()
    time.sleep(0.25)
    apply_button = chromeBrowser.find_elements_by_class_name('Button_1w8tm98-o_O-primary_cv02ee-o_O-md_1jvotax')[0]
    apply_button.click()
    time.sleep(0.25)





#Helper function
#To check if the course already exist in my dict. then append the new skill
#If the course doesn't exist then create a new course.
def Course_exist(name):
    all_keys = list(data_struct.keys())
    for i in range (0, len(all_keys)):
        if(all_keys[i] == name):
            return True
    return False





#Illustration
#Shape of data structure
test = {"Course1": ["Linear Algebra", "Machine Learning", "Problem Solving"]}
test["Course1"].append("New Skill")
test





data_struct = {}





#Function to save the acquired data into mongo database.
def saveToDB(collection, course_name_l, skill_l):
    course_name_l = course_name_l.replace(".", " ").replace("%", "").replace("&", "")
    result = collection.count_documents({"Course": course_name_l})
    if result <= 0:
        collection.insert_one({"Course" : course_name_l, "Skills" : [skill_l]})
    elif result > 0:
        x = collection.find_one({"Course": course_name_l})
        temp = x["Skills"]
        temp.append(skill_l)
        collection.find_one_and_replace({'Course': course_name_l}, {"Course" : course_name_l, "Skills" : temp})





#Connect to localhost mongodb.
client = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = client["iNetworks"]
mycol = mydb["Skills_Levels_Courses"]
mycol.delete_many({}) #To initialize the collection.





## Main program number 1 to loop on all the skills
skill_name = ""
Courses_names = []
data_struct = {}

type_courses() ##To select courses only.
skill_drop_down_click()
skills_f = chromeBrowser.find_elements_by_class_name('input_3xha1c-o_O-active_ro0g1e')
length = len(skills_f)

for index in range (0,length):
    
    #The following line to fix the session bug.
    skill_drop_down_click() #Call function
    skills_f = chromeBrowser.find_elements_by_class_name('input_3xha1c-o_O-active_ro0g1e')
    
    # Choose specific skill
    skill_name = skills_f[index].get_attribute('value')
    skills_f[index].click()
    time.sleep(0.5)
    # End of choose specific skill
    
    soup = click_apply() #Call function
    time.sleep(0.25)
    courses_names(soup) #Call function
    
    for course in range(0,len(Courses_names)):
        saveToDB(mycol, Courses_names[course], skill_name) #This line will save into mongodb.
        EXIST = Course_exist(Courses_names[course]) #The following lines will save into our ordinary dict.
        if (not EXIST):
            data_struct.update({Courses_names[course]: [skill_name]})
        elif (EXIST):
            data_struct[Courses_names[course]].append(skill_name)
            
    skill_drop_down_click() #Call function
    clear_skills_only() #Call function
    
    Courses_names = []
    skill_name = []
    time.sleep(0.25)
       





#To export the dict to a csv file.
import csv





#Write the dictonary(Course & Skills) to a csv file
with open('JobReq2.csv', 'w', newline='',encoding="utf-8") as file:
    fieldnames = ['Course', 'Skills']
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    
    KEYS = list(data_struct.keys())
    writer.writeheader()
    for i in range (0, len(data_struct)):
        writer.writerow({'Course': KEYS[i], 'Skills': data_struct.get(KEYS[i])})
    





## Now get the level of each course
import pandas as pd





#Get the saved dataset(Course and skill only), we will add the level of each course now.
df = pd.read_csv(r'C:\Users\Owner\Desktop\iNetworks - Internship\JobReq.csv')  





#Glimpse
df.head()





#New column corresponding to the level
df["Level"] = ""





#To know the number of rows.
df.info()





#To avoid the repetition of the courses when getting the html files of the levels (Because I scroll down to their might be
#duplicates)
def Course_exist2(name):
    for i in range (0, len(Courses_names_2)):
        if(Courses_names_2[i] == name):
            return True
    return False





#To get a list of the course and the corresponding level
Courses_names_2 = []
def Choose_all_courses():    
    for i in range (0,35):
        html = chromeBrowser.page_source #Get the html code of the new page with the selected filters.
        soup = BeautifulSoup(html, 'html.parser')
        Courses_div = soup.find("div",{"class":"ReactVirtualized__Grid__innerScrollContainer"})
        Courses = Courses_div.find_all("a", {"data-click-key":"browse.browse.click.offering_card"})

        ##For loop to get all the courses names
        for course_num in range(len(Courses)):
            EXIST = Course_exist2(Courses[course_num]['aria-label'])
            if (not EXIST):
                Courses_names_2.append(Courses[course_num]['aria-label'])
        
        ##End of for
    
        time.sleep(0.25)
        chromeBrowser.execute_script("window.scrollTo(0, window.scrollY + 1500)")
        time.sleep(0.25)
    





#To select the beginner level
def Beginner_click():   
    Beginner = chromeBrowser.find_elements_by_class_name('input_3xha1c-o_O-active_ro0g1e')[1]
    Beginner.click()
    time.sleep(0.25) 





#To select the intermediate level
def Intermediate_click():  
    Intermediate = chromeBrowser.find_elements_by_class_name('input_3xha1c-o_O-active_ro0g1e')[2]
    Intermediate.click()
    time.sleep(0.25) 





#To select the advanced level
def Advanced_click():
    Advanced = chromeBrowser.find_elements_by_class_name('input_3xha1c-o_O-active_ro0g1e')[3]
    Advanced.click()
    time.sleep(0.25) 





#To write the beginner level
def write_beginner():
    for i in range (0,372):
        for j in range (0,len(Courses_names_2)):
            if (df['Course'][i] == Courses_names_2[j]):
                df["Level"][i] = df["Level"][i] + "Beginner "





#To write the intermediate level
def write_intermediate():
    for i in range (0,372):
        for j in range (0,len(Courses_names_2)):
            if (df['Course'][i] == Courses_names_2[j]):
                df["Level"][i] = df["Level"][i] + "Intermediate "





#To write the advanced level
def write_advanced():
    for i in range (0,372):
        for j in range (0,len(Courses_names_2)):
            if (df['Course'][i] == Courses_names_2[j]):
                df["Level"][i] = df["Level"][i] + "Advanced "





## Main program number 2 to loop on all the levels

for i in range(0,3):
    type_courses() ##To select courses only.
    Level_drop_down_click()
    if (i == 0):
        Beginner_click()
    elif(i == 1):
        Intermediate_click()
    elif(i == 2):
        Advanced_click()   
    apply_button = chromeBrowser.find_elements_by_class_name('Button_1w8tm98-o_O-primary_cv02ee-o_O-md_1jvotax')[0]
    apply_button.click()
    time.sleep(5)
    Choose_all_courses()
    if (i == 0):
        write_beginner()
    elif(i == 1):
        write_intermediate()
    elif(i == 2):
        write_advanced()
    chromeBrowser.execute_script("window.scrollTo(0, -10000)")
    clear_all_filter()
    time.sleep(1)





#Final data frame
df.head()





#Write the data frame to a csv file
## FINAL DATASET (Course with the corresponding skill and level)
df.to_csv('Final.csv',index=False)













