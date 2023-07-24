import time
import json
import pandas as pd
from flask import Flask, jsonify
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc

def get_undetected_chrome_driver():
    chrome_options = uc.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--window-size=1920,1080')
    driver = uc.Chrome(options=chrome_options)
    return driver

def is_element_exists(driver, by, element):
    try:
        driver.find_element(
            by, element)
        return True
    except:
        return False


def custom_call(user_input):
    driver = get_undetected_chrome_driver()
    vehicle_urls = []
    final_payload = []
    base_url = "https://www.rbauction.com/cars?keywords=&category=22638792844"
    driver.get(base_url)

    if is_element_exists(driver, By.CSS_SELECTOR,"#simple-keyword-search"):
        driver.find_element(By.CSS_SELECTOR,"#simple-keyword-search").send_keys(user_input)
    if is_element_exists(driver,By.CSS_SELECTOR,"#keyword-submit"):
        driver.execute_script("arguments[0].click();", WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "#keyword-submit"))))
    time.sleep(5)

    if is_element_exists(driver, By.XPATH, "(//div[@class='sc-cHGsZl cCRZtc']//h3//a)"):
        vehicle_links = driver.find_elements(By.XPATH, "(//div[@class='sc-cHGsZl cCRZtc']//h3//a)")
        for span in vehicle_links:
            href = span.get_attribute("href")
            if href not in vehicle_urls:
                vehicle_urls.append(href)

    vehicle_urls = vehicle_urls[0:5]
    for url in vehicle_urls:
        try:
            print("\nLink: ", url)
            driver.get(url)
            time.sleep(5)
            title = vin_number = document_link = odometer = high_value = year = make =  model = vehicle_type = ""
            image_urls = []

            #Title of vehicle
            if is_element_exists(driver, By.CSS_SELECTOR, ".sc-pVTFL.iCBAUx"):
                title = driver.find_element(By.CSS_SELECTOR, ".sc-pVTFL.iCBAUx").text

            #high bid value of the vehicle
            if is_element_exists(driver, By.XPATH,"//div[@class='sc-iCfMLu cPosbz']//div[@class='sc-bdvvtL AqMUJ']//div//p"):
                high_value = driver.find_element(By.XPATH, "//div[@class='sc-iCfMLu cPosbz']//div[@class='sc-bdvvtL AqMUJ']//div//p").text
            
            #year + make + model + type + vin + odometer
            if is_element_exists(driver,By.XPATH,"(//p[@class='sc-pVTFL ca-ddJj'])"):
                features = driver.find_elements(By.XPATH,"(//p[@class='sc-pVTFL ca-ddJj'])")
                if len(features) >= 7:
                    year = features[1].text
                    make = features[2].text
                    model = features[3].text
                    vehicle_type = features[4].text
                    vin_number = features[5].text
                    odometer = features[6].text

            #document
            if is_element_exists(driver,By.CSS_SELECTOR,".sc-pVTFL.vvHQt"):
                document_link = driver.find_element(By.CSS_SELECTOR,".sc-pVTFL.vvHQt").get_attribute("href")

            #Images of vehicle
            if is_element_exists(driver,By.XPATH,"(//object[@class='sc-jrQzAO dwJlJU'])"):
                images = driver.find_elements(By.XPATH, "(//object[@class='sc-jrQzAO dwJlJU'])")
                for image in images:
                    scr_of_image = image.get_attribute("data")
                    if scr_of_image not in image_urls:
                        image_urls.append(scr_of_image)

            payload = []
            payload.append(url.replace("'",""))
            payload.append(title)
            payload.append(year)
            payload.append(make)
            payload.append(model)
            payload.append(vin_number)
            payload.append(odometer)
            payload.append(vehicle_type)
            payload.append(high_value)
            payload.append(document_link)
            payload.append(json.dumps(image_urls))
            
            if len(features) != 6:
                final_payload.append(payload)
                print("Data inserted into the final_payload file successfully.")
        except Exception as e:
            print(type(e))
            pass

    driver.close()
    return final_payload


app = Flask(__name__)
df = pd.read_csv('rbauction.csv')

@app.route('/<title>', methods=['GET'])

def get_vehicle_data(title):
    filtered_df = df[df['Title'].str.contains(title, case=False, na=False)]
    if filtered_df.empty:
        custom_data = custom_call(title)
        return jsonify(custom_data)
    data = filtered_df.to_dict(orient='records')
    return jsonify(data)
if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5000,debug=True)
