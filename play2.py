import time
import requests
from io import BytesIO
from PIL import Image
from playwright.sync_api import sync_playwright, TimeoutError
from datetime import datetime
from config import *
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('appointment_checker.log'),
        logging.StreamHandler()
    ]
)

def check_site_availability():
    try:
        response = requests.get(LOGOUT_URL, timeout=30)
        if response.status_code == 200:
            logging.info("Site is reachable")
            return True
        else:
            logging.warning(f"Site is not responding properly (Status code: {response.status_code})")
            return False
    except requests.RequestException as e:
        logging.error(f"Error accessing the site: {str(e)}")
        return False

def safe_close(browser=None, context=None, page=None):
    try:
        if page:
            page.close()
        if context:
            context.close()
        if browser:
            browser.close()
    except Exception as e:
        logging.warning(f"Error closing browser resources: {e}")

def solve_captcha(captcha_image_url):
    if not API_KEY:
        logging.error("CAPTCHA API key not found in environment variables")
        raise ValueError("CAPTCHA API key not configured")

    response = requests.get(captcha_image_url)
    img = Image.open(BytesIO(response.content))
    img.save("captcha.png")

    with open("captcha.png", "rb") as captcha_file:
        response = requests.post(
            "http://2captcha.com/in.php",
            files={"file": captcha_file},
            data={"key": API_KEY, "method": "post"}
        )

    if not response.text.startswith('OK|'):
        logging.error(f"Error submitting CAPTCHA: {response.text}")
        raise Exception(f"Error submitting CAPTCHA: {response.text}")

    captcha_id = response.text.split('|')[1]
    for _ in range(20):
        response = requests.get(f"http://2captcha.com/res.php?key={API_KEY}&action=get&id={captcha_id}")
        if response.text == 'CAPCHA_NOT_READY':
            time.sleep(5)
            continue
        elif 'OK' in response.text:
            captcha_solution = response.text.split('|')[1]
            return captcha_solution.strip()
        else:
            logging.error(f"Error solving CAPTCHA: {response.text}")
            raise Exception(f"Error solving CAPTCHA: {response.text}")

def solve_recaptcha_v2():
    if not API_KEY:
        logging.error("CAPTCHA API key not found in environment variables")
        raise ValueError("CAPTCHA API key not configured")

    captcha_response = requests.post(
        "http://2captcha.com/in.php",
        data={
            "key": API_KEY,
            "method": "userrecaptcha",
            "googlekey": SITE_KEY,
            "pageurl": APPOINTMENT_URL
        }
    )

    if captcha_response.text.startswith('OK|'):
        captcha_id = captcha_response.text.split('|')[1]
    else:
        logging.error(f"Error sending reCAPTCHA solving request: {captcha_response.text}")
        raise Exception(f"Error sending reCAPTCHA solving request: {captcha_response.text}")

    result_url = f"http://2captcha.com/res.php?key={API_KEY}&action=get&id={captcha_id}"

    for _ in range(20):
        result_response = requests.get(result_url)
        if result_response.text == 'CAPCHA_NOT_READY':
            time.sleep(5)
            continue
        elif result_response.text.startswith('OK|'):
            return result_response.text.split('|')[1]
        else:
            logging.error(f"Error getting reCAPTCHA solution: {result_response.text}")
            raise Exception(f"Error getting reCAPTCHA solution: {result_response.text}")

def check_appointment_date(page):
    calendar = page.query_selector('table.table-condensed')
    if calendar:
        day_11 = calendar.query_selector('td[data-date="1726012800000"]')
        if day_11 and "disabled" not in day_11.get_attribute("class"):
            return True
    return False

def login(page):
    if not all([EMAIL, PASSWORD]):
        logging.error("Email or password not found in environment variables")
        raise ValueError("Email or password not configured")

    try:
        page.goto(LOGIN_URL)
        page.fill('input[placeholder="Enter Email"]', EMAIL)
        page.fill('input[placeholder="Enter Password"]', PASSWORD)

        recaptcha_solution = solve_recaptcha_v2()
        page.evaluate(f'document.getElementById("g-recaptcha-response").value = "{recaptcha_solution}"')
        page.click('button[name="submitLogin"]')
        logging.info("Logged in successfully")
    except Exception as e:
        logging.error(f"Login failed: {e}")
        page.reload()

def main():
    if not all([API_KEY, EMAIL, PASSWORD]):
        logging.error("Required environment variables are missing")
        raise ValueError("Please configure API_KEY, EMAIL, and PASSWORD in .env file")

    browser = None
    context = None
    page = None

    while True:
        try:
            if not check_site_availability():
                logging.info(f"Site not reachable. Waiting {CHECK_INTERVAL/60} minutes before next check...")
                time.sleep(CHECK_INTERVAL)
                continue

            with sync_playwright() as p:
                try:
                    browser = p.firefox.launch(headless=False)
                    context = browser.new_context()
                    page = context.new_page()
                    login(page)

                    time.sleep(1)
                    while True:
                        if not check_site_availability():
                            logging.warning("Site became unreachable. Restarting process...")
                            break

                        try:
                            page.goto(APPOINTMENT_URL)
                        except TimeoutError as e:
                            logging.warning(f"Page load timeout: {e}, retrying...")
                            if not check_site_availability():
                                break
                            page.reload()
                            continue
                        except Exception as e:
                            logging.error(f"Error navigating to appointment page: {e}")
                            if not check_site_availability():
                                break
                            page.reload()
                            continue

                        if page.url == LOGOUT_URL:
                            logging.info("Logged out, logging in again.")
                            if not check_site_availability():
                                break
                            login(page)
                            continue

                        try:
                            popup = page.query_selector('a.cl')
                            if popup:
                                popup.click()
                                logging.info("Popup closed successfully")
                        except Exception as e:
                            logging.warning(f"Popup closure failed: {e}, continuing...")

                        try:
                            page.select_option('select#valCenterLocationId', label="Islamabad (Pakistan)")
                            time.sleep(2)

                            page.select_option("select#valCenterLocationTypeId", label="National - Work")
                            selected_value = page.evaluate("() => document.getElementById('valCenterLocationTypeId').value")
                            logging.info(f"Selected value: {selected_value}")
                            time.sleep(2)

                            page.select_option('select#valAppointmentForMembers', label="Individual")
                            time.sleep(2)
                        except Exception as e:
                            logging.error(f"Form selection error: {e}, retrying...")
                            if not check_site_availability():
                                break
                            page.reload()
                            continue

                        while True:
                            if not check_site_availability():
                                logging.warning("Site became unreachable during appointment check. Restarting process...")
                                break

                            if page.url == LOGOUT_URL:
                                logging.info("Logged out, logging in again.")
                                break

                            try:
                                if check_appointment_date(page):
                                    logging.info("Appointment for 11 September is available.")
                                    captcha_image_url = page.get_attribute('#Imageid', 'src')
                                    second_captcha_solution = solve_captcha(captcha_image_url)
                                    page.fill('#captcha_code_reg', second_captcha_solution)
                                    logging.info("Second captcha filled.")

                                    page.check('#agree')
                                    page.click('#valBookNow')
                                    logging.info("Appointment booked for 11 September.")
                                    return

                                else:
                                    logging.info(f"Appointment for 11 September is not available. Waiting {CHECK_INTERVAL/60} minutes...")
                                    time.sleep(CHECK_INTERVAL)
                                    page.reload()
                            except Exception as e:
                                logging.error(f"Error checking appointment: {e}, retrying...")
                                if not check_site_availability():
                                    break
                                page.reload()

                        if not check_site_availability():
                            break
                        time.sleep(1)
                        page.reload()

                except Exception as e:
                    logging.error(f"An unexpected error occurred: {e}")

                finally:
                    safe_close(browser, context, page)
                    logging.info("Session ended, checking site availability before restart...")

        except Exception as e:
            logging.error(f"Main loop error: {e}")
            safe_close(browser, context, page)

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("Script stopped by user")
    except Exception as e:
        logging.error(f"Fatal error: {e}")
