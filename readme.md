# BLS Italy Appointment Checker

This application automatically checks for available appointments on the BLS Italy visa website and provides a web interface to monitor the process.

## Features

- Web interface to start/stop the appointment checker
- Real-time log viewing through the browser
- Automatic appointment checking in the background
- Easy deployment to free hosting platforms

## Local Setup

1. Install dependencies:
```bash
python3 -m pip install -r requirements.txt
```

2. Install Playwright browsers:
```bash
playwright install
```

3. Create a `.env` file with your credentials:
```
API_KEY=your_api_key
EMAIL=your_email
PASSWORD=your_password
```

4. Run the web application:
```bash
python app.py
```

5. Open http://localhost:5000 in your browser

## Deployment to PythonAnywhere

1. Sign up for a free account at [PythonAnywhere](https://www.pythonanywhere.com)

2. Open a Bash console in PythonAnywhere

3. Clone your repository:
```bash
git clone https://github.com/yourusername/your-repo-name.git
```

4. Create a virtual environment and install dependencies:
```bash
cd your-repo-name
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install
```

5. Set up your environment variables in the PythonAnywhere dashboard

6. Configure a new web app:
   - Choose Manual Configuration
   - Select Python 3.8 or later
   - Set the source code directory to your project folder
   - Set the working directory to your project folder
   - Update the WSGI file to point to your app.py

7. Reload your web app

Your application will now be available at yourusername.pythonanywhere.com

## Usage

1. Visit the web interface
2. Click "Start Checker" to begin monitoring appointments
3. View real-time logs in the browser
4. Click "Stop Checker" to stop the monitoring process

## Important Notes

- The free tier of PythonAnywhere has some limitations on CPU usage and running time
- Make sure to comply with BLS Italy's terms of service
- Keep your credentials secure and never share them publicly

## Setup Instructions

1. Clone the repository:
```bash
git clone <your-repo-url>
cd <repo-directory>
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
playwright install
```

4. Create a `.env` file in the root directory with your credentials:
```env
CAPTCHA_API_KEY=your_2captcha_api_key
BLS_EMAIL=your_bls_email
BLS_PASSWORD=your_bls_password
```

## Running the Script

1. Make sure your virtual environment is activated
2. Run the script:
```bash
python play2.py
```

The script will:
- Check site availability every 5 minutes
- Log all activities to `appointment_checker.log`
- Automatically handle login and CAPTCHA solving
- Book an appointment when available

## Hosting Instructions

### Option 1: Running on a VPS (Recommended)

1. Set up a VPS (e.g., DigitalOcean, AWS EC2, etc.)
2. Install required packages:
```bash
sudo apt update
sudo apt install python3-pip python3-venv xvfb
```

3. Set up a screen session to keep the script running:
```bash
screen -S appointment_checker
```

4. Follow the setup instructions above
5. Start the script:
```bash
python play2.py
```

6. Detach from screen (Ctrl+A, D)

### Option 2: Running as a Systemd Service

1. Create a systemd service file:
```bash
sudo nano /etc/systemd/system/appointment-checker.service
```

2. Add the following content:
```ini
[Unit]
Description=BLS Italy Appointment Checker
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/script
Environment=DISPLAY=:99
ExecStartPre=/usr/bin/Xvfb :99 -screen 0 1024x768x24 -ac
ExecStart=/path/to/venv/bin/python play2.py
Restart=always
RestartSec=300

[Install]
WantedBy=multi-user.target
```

3. Enable and start the service:
```bash
sudo systemctl enable appointment-checker
sudo systemctl start appointment-checker
```

## Monitoring

- Check the logs in `appointment_checker.log`
- Monitor the service status:
```bash
sudo systemctl status appointment-checker  # If running as a service
```

## Security Notes

- Never commit the `.env` file
- Keep your API keys and credentials secure
- Regularly update dependencies
- Monitor the logs for any suspicious activity

## Troubleshooting

1. If the script crashes:
   - Check the logs in `appointment_checker.log`
   - Ensure all environment variables are set correctly
   - Verify your internet connection

2. If CAPTCHA solving fails:
   - Check your 2captcha API key balance
   - Verify the API key is correct in `.env`

3. If the browser doesn't start:
   - Ensure Playwright is installed correctly
   - Try reinstalling Playwright: `playwright install`
