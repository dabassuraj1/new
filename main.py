from flask import Flask, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import requests
import time

app = Flask(__name__)

# ----------------------------
# VahanX scraping (faster, structured)
# ----------------------------
def get_vehicle_details_vahanx(rc_number: str) -> dict:
    rc = rc_number.strip().upper()
    url = f"https://vahanx.in/rc-search/{rc}"

    headers = {
        "Host": "vahanx.in",
        "Connection": "keep-alive",
        "sec-ch-ua": "\"Chromium\";v=\"130\", \"Google Chrome\";v=\"130\", \"Not?A_Brand\";v=\"99\"",
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": "\"Android\"",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Referer": "https://vahanx.in/rc-search",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.9"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
    except Exception as e:
        return None  # fallback to Selenium

    def get_value(label):
        try:
            div = soup.find("span", string=label).find_parent("div")
            return div.find("p").get_text(strip=True)
        except:
            return None

    data = {
        "Owner Name": get_value("Owner Name"),
        "Father's Name": get_value("Father's Name"),
        "Owner Serial No": get_value("Owner Serial No"),
        "Model Name": get_value("Model Name"),
        "Maker Model": get_value("Maker Model"),
        "Vehicle Class": get_value("Vehicle Class"),
        "Fuel Type": get_value("Fuel Type"),
        "Fuel Norms": get_value("Fuel Norms"),
        "Registration Date": get_value("Registration Date"),
        "Insurance Company": get_value("Insurance Company"),
        "Insurance No": get_value("Insurance No"),
        "Insurance Expiry": get_value("Insurance Expiry"),
        "Insurance Upto": get_value("Insurance Upto"),
        "Fitness Upto": get_value("Fitness Upto"),
        "Tax Upto": get_value("Tax Upto"),
        "PUC No": get_value("PUC No"),
        "PUC Upto": get_value("PUC Upto"),
        "Financier Name": get_value("Financier Name"),
        "Registered RTO": get_value("Registered RTO"),
        "Address": get_value("Address"),
        "City Name": get_value("City Name"),
        "Phone": get_value("Phone"),
        "NOTE": "💀Android and ☠Rahul SAY's hello 💸"
    }
    return data

# ----------------------------
# Carinfo.app scraping (JS site, fallback)
# ----------------------------
def get_vehicle_details_carinfo(rc_number: str) -> dict:
    url = f"https://www.carinfo.app/rc-details/{rc_number}"
    
    options = Options()
    options.add_argument("--headless")  
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)
    driver.get(url)
    time.sleep(5)  # wait for JS

    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    details = {}
    rows = soup.select("table tr")
    for row in rows:
        cols = row.find_all("td")
        if len(cols) == 2:
            key = cols[0].get_text(strip=True)
            val = cols[1].get_text(strip=True)
            details[key] = val

    details["NOTE"] = "✅ Scraped live from carinfo.app"
    return details if details else None

# ----------------------------
# API route
# ----------------------------
@app.route("/rc/<reg_number>")
def rc_lookup(reg_number):
    data = get_vehicle_details_vahanx(reg_number)
    if not data or all(v is None for v in data.values()):
        data = get_vehicle_details_carinfo(reg_number)
        if not data:
            return jsonify({"status": "Failed", "message": "Both sources unreachable"})
    return jsonify({"status": "Success", "details": data})

# ----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
