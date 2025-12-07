import os
import time
import requests
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

BASE_URL = "https://coloradosprings.legistar.com/"
CALENDAR_URL = urljoin(BASE_URL, "Calendar.aspx")
DOWNLOAD_DIR = os.path.join(os.path.expanduser("~"), "Downloads", "legistar_agendas")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def get_unique_filepath(directory, filename):
    """
    If filename exists, returns a new name like 'filename_1.pdf'.
    """
    name, ext = os.path.splitext(filename)
    counter = 1
    new_filename = filename
    full_path = os.path.join(directory, new_filename)
    
    while os.path.exists(full_path):
        new_filename = f"{name}_{counter}{ext}"
        full_path = os.path.join(directory, new_filename)
        counter += 1
        
    return full_path

def download_pdf(url):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        # Check if content is actually a PDF
        content_type = response.headers.get("Content-Type", "").lower()
        if "pdf" not in content_type and "application/octet-stream" not in content_type:
            return

        # 1. Determine Filename
        filename = "Agenda.pdf" # Default fallback
        
        # Try to get filename from URL
        url_name = url.split("/")[-1].split("?")[0]
        if url_name: 
            filename = url_name
            
        # Try to get filename from Content-Disposition (Higher Priority)
        cd = response.headers.get("Content-Disposition")
        if cd and "filename=" in cd:
            filename = cd.split("filename=")[-1].strip('"')

        # Ensure .pdf extension
        if not filename.lower().endswith(".pdf"):
            filename += ".pdf"

        # 2. Handle Duplicate Names (The Fix)
        # Instead of skipping, we generate a unique path (Agenda_1.pdf, Agenda_2.pdf...)
        path = get_unique_filepath(DOWNLOAD_DIR, filename)

        print(f"Downloading to {os.path.basename(path)}...")
        with open(path, "wb") as f:
            for chunk in response.iter_content(8192):
                f.write(chunk)
                
    except Exception as e:
        print(f"Failed to download {url}: {e}")

def scrape_agendas():
    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    wait = WebDriverWait(driver, 10)

    try:
        driver.get(CALENDAR_URL)
        time.sleep(3) 

        while True:
            # 1. Grab all URL strings first to avoid Stale Elements
            meeting_elements = driver.find_elements(By.XPATH, "//a[contains(@id,'hypMeetingDetail') and not(contains(@class,'NotViewable'))]")
            detail_urls = [link.get_attribute("href") for link in meeting_elements if link.get_attribute("href")]
            
            print(f"Processing {len(detail_urls)} meetings on this page...")

            # 2. Iterate through the URL strings
            for detail_url in detail_urls:
                try:
                    driver.execute_script("window.open(arguments[0]);", detail_url)
                    driver.switch_to.window(driver.window_handles[-1])
                    
                    try:
                        # Wait for Agenda link
                        agenda_link = wait.until(EC.presence_of_element_located((By.XPATH, "//a[text()='Agenda']")))
                        pdf_href = agenda_link.get_attribute("href")
                        if pdf_href:
                            download_pdf(pdf_href)
                    except Exception:
                        # No Agenda found for this meeting
                        pass
                    
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                    
                except Exception as e:
                    print(f"Error on meeting page: {e}")
                    if len(driver.window_handles) > 1:
                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])

            # 3. Pagination Logic
            try:
                next_button = driver.find_element(By.XPATH, "//a[contains(@class, 'rgPageNext')]")
                if "rgPageNextDisabled" in next_button.get_attribute("class"):
                    print("Finished all pages.")
                    break
                
                print(">>> Next Page")
                next_button.click()
                time.sleep(5) # Wait for grid reload
            except:
                break

    finally:
        driver.quit()

if __name__ == "__main__":
    scrape_agendas()