from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import mysql.connector
import time

#Connecting to MySQL
def connect_to_mysql():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="redbus_project"  
    )

#Inserting bus details into the database
def insert_bus_details(bus_details, connection):
    cursor = connection.cursor()
    
    for bus in bus_details:
        try:
            cursor.execute("""
                SELECT COUNT(*) 
                FROM bus_routes 
                WHERE route_name = %s AND busname = %s AND bustype = %s AND departing_time = %s AND duration = %s AND reaching_time = %s
            """, (
                bus['RouteName'],        
                bus['Name'],             
                bus['Type'],             
                bus['Departure Time'],   
                bus['Duration'],         
                bus['Reaching Time']     
            ))
            if cursor.fetchone()[0] > 0:
                print(f"Bus with route name '{bus['RouteName']}' and other details already exists. Skipping...")
                continue
            
            #Inserting bus details into the table
            
            cursor.execute("""
                INSERT INTO bus_routes (route_name, busname, bustype, departing_time, duration, reaching_time, star_rating, price, seats_available)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                bus['RouteName'],      
                bus['Name'],       
                bus['Type'],       
                bus['Departure Time'],  
                bus['Duration'],  
                bus['Reaching Time'],   
                bus['Rating'],     
                bus['Price'],      
                bus['Seats Available']   
            ))

            #Commit the transaction
            connection.commit()
            print(f"Inserted bus: {bus['Name']}")
        except Exception as e:
            print(f"Error inserting bus: {e}")
            connection.rollback()


#Setting up the WebDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

#Opening Redbus website
driver.get("https://www.redbus.in/")

# Maximizing the browser window
driver.maximize_window()

# Giving some time to load the homepage
time.sleep(3)

#Searching for buses from 'Bangalore' to 'Chennai'
from_str="Bangalore"
#Input "From" city
from_city = driver.find_element(By.ID, "src")
from_city.clear()
from_city.send_keys(from_str)
time.sleep(1)
from_city.send_keys(Keys.ENTER)

#Input "To" city
to_str="Chennai"
to_city = driver.find_element(By.ID, "dest")
to_city.clear()
to_city.send_keys(to_str)
time.sleep(1)
to_city.send_keys(Keys.ENTER)

#Setting up the Date
date_element = driver.find_element(By.ID, "onwardCal")
date_element.click()

#Selecting the next available date
next_date = driver.find_element(By.XPATH, "//div[@id='onwardCal']/div/div[2]/div/div/div[3]/div[6]/span/div[3]/span")
next_date.click()

#Clicking search button
search_button = driver.find_element(By.ID, "search_button")
search_button.click()

#Wait for the search results to load
wait = WebDriverWait(driver, 10)
wait.until(EC.presence_of_element_located((By.CLASS_NAME, "bus-item")))


last_height = driver.execute_script("return document.body.scrollHeight")
while True:
    #Scroll down to the bottom
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)  # Wait for content to load

    #Calculate new scroll height and compare with last scroll height
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        #Break the loop
        break
    last_height = new_height

time.sleep(5)

bus_containers = driver.find_elements(By.CLASS_NAME, "bus-item")

#Extract details row by row
bus_details = []

for bus in bus_containers:
    try:
        name = bus.find_element(By.CLASS_NAME, "travels").text
    except:
        name = "N/A"

    try:
        price = bus.find_element(By.XPATH, ".//div[contains(@class, 'fare')]/span").text
    except:
        price = "0"

    try:
        bus_type = bus.find_element(By.CLASS_NAME, "bus-type").text
    except:
        bus_type = "N/A"

    try:
        departure_time = bus.find_element(By.CLASS_NAME, "dp-time").text
    except:
        departure_time = "N/A"

    try:
        duration = bus.find_element(By.CLASS_NAME, "dur").text
    except:
        duration = "N/A"

    try:
        reaching_time = bus.find_element(By.CLASS_NAME, "bp-time").text
    except:
        reaching_time = "N/A"

    try:
        rating = bus.find_element(By.CLASS_NAME, "rating").text
        rating = float(rating)
    except:
        rating = None

    try:
        full_text = bus.find_element(By.CLASS_NAME, "seat-left").text
        seats = full_text.split()[0] 
    except:
        seats = "N/A"

    #Add extracted details to the list
    bus_details.append({
        "RouteName":f"{from_str}-{to_str}",
        "Name": name,
        "Price": price,
        "Type": bus_type,
        "Departure Time": departure_time,
        "Duration": duration,
        "Reaching Time": reaching_time,
        "Rating": rating,
        "Seats Available": seats,
    })

#Print extracted data
print("Available Buses and their Details count: ",len(bus_details))
for i, bus in enumerate(bus_details, 1):
    print(f"Bus {i}:")
    for key, value in bus.items():
        print(f"  {key}: {value}")
    print("-" * 50)

#Connecting to MySQL and insert data
connection = connect_to_mysql()
insert_bus_details(bus_details, connection)
connection.close()    

# Finally, close the browser
driver.quit()