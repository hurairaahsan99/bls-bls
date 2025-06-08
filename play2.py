import os
import time
import requests
import logging
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('appointment_checker.log')
    ]
)

class AppointmentChecker:
    def __init__(self):
        self.api_key = os.getenv('API_KEY')
        self.email = os.getenv('EMAIL')
        self.password = os.getenv('PASSWORD')
        self.session = requests.Session()
        self.base_url = "https://blsitalypakistan.com"
        self.is_running = True

    def setup_session(self):
        """Set up session headers and cookies"""
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
        })

    def login(self):
        """Perform login"""
        try:
            # Get CSRF token
            response = self.session.get(f"{self.base_url}/en/login")
            if response.status_code != 200:
                logging.error(f"Failed to get login page: {response.status_code}")
                return False

            # Perform login
            login_data = {
                'email': self.email,
                'password': self.password,
            }

            response = self.session.post(f"{self.base_url}/en/login", data=login_data)
            if response.status_code != 200:
                logging.error(f"Login failed: {response.status_code}")
                return False

            logging.info("Login successful")
            return True

        except Exception as e:
            logging.error(f"Login error: {str(e)}")
            return False

    def check_appointment(self):
        """Check for available appointments"""
        try:
            response = self.session.get(f"{self.base_url}/en/appointment/index")

            if response.status_code != 200:
                logging.error(f"Failed to check appointments: {response.status_code}")
                return False

            # Check if specific text indicating no appointments is present
            if "No appointment slots are currently available" in response.text:
                logging.info("No appointments available")
                return False
            else:
                logging.info("APPOINTMENTS MAY BE AVAILABLE! Check the website!")
                return True

        except Exception as e:
            logging.error(f"Error checking appointments: {str(e)}")
            return False

    def run(self):
        """Main loop for checking appointments"""
        self.setup_session()

        while self.is_running:
            try:
                if not self.login():
                    logging.error("Login failed, waiting before retry...")
                    time.sleep(300)  # Wait 5 minutes before retry
                    continue

                if self.check_appointment():
                    logging.info("Found potential appointment slot!")

                # Wait 5 minutes before next check
                logging.info("Waiting 5 minutes before next check...")
                time.sleep(300)

            except Exception as e:
                logging.error(f"Error in main loop: {str(e)}")
                time.sleep(300)  # Wait 5 minutes before retry

    def stop(self):
        """Stop the appointment checker"""
        self.is_running = False

def main():
    checker = AppointmentChecker()
    checker.run()

if __name__ == "__main__":
    main()
