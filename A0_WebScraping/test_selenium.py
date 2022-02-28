from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time

PATH = "C:\Program Files (x86)\chromedriver.exe"
driver = webdriver.Chrome(PATH)

def web_scraper():
    #print(driver.title)
    place = ['Toronto','Roma','Berlin']
    my_list = []

    for _ in place:
        driver.get("https://www.latlong.net/")
        search = driver.find_element_by_id("place")
        search.send_keys(f"{_}")
        search.send_keys(Keys.RETURN)

        lat = driver.find_element_by_name("lat").get_property('value')
        print(lat)
        lng = driver.find_element_by_id("lng").get_property('value')
        print(lng)


        time.sleep(2)

        my_list += ['{},{},{}'.format(place, lat, lng)]

    time.sleep(5)

    
    print(my_list)

    driver.quit()

if __name__ == '__main__':
    web_scraper()