# GitHub Email Scheduler

A Python application that sends scheduled emails 3 times a day. Email configuration is read from GitHub environment variables, and scheduling intervals are configured via YAML.

## Features

- **Configurable Schedule**: Define email sending times in YAML configuration
- **Environment Variables**: Email details read from GitHub environment variables
- **Background Scheduling**: Uses APScheduler for reliable background email delivery
- **Flexible Configuration**: Supports both cron-based (specific times) and interval-based scheduling
- **Logging**: Comprehensive logging for monitoring and debugging

## Prerequisites

- Python 3.7+
- Hotmail/Outlook account (or other email provider with SMTP support)

## Installation

1. **Clone/Navigate to the project directory**
   ```bash
   cd /home/syed/Documents/source/repo/GitHubScheduler
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   # Copy the example file
   cp .env.example .env
   
   # Edit .env with your actual credentials
   nano .env
   ```

## Configuration

### Environment Variables (GitHub Secrets or System Environment)

Set these environment variables:

- `GITHUB_EMAIL`: Your email address (e.g., `your_email@hotmail.com`)
- `GITHUB_EMAIL_PASSWORD`: Your Hotmail/Outlook password
- `SMTP_SERVER` (optional): SMTP server address (default: `smtp-mail.outlook.com`)
- `SMTP_PORT` (optional): SMTP port (default: `587`)

### For Hotmail/Outlook Users

If you get an authentication error "basic authentication is disabled", try these solutions in order:

**Option 1: Use an App Password (Recommended)**
1. Go to https://account.microsoft.com/security-info
2. Select **Password & security** → **App passwords**
3. Choose "Mail" and "Other (custom device)"
4. Copy the generated 16-character password
5. Set `GITHUB_EMAIL_PASSWORD` to this app password

**Option 2: Use Port 465 with SSL**
1. Update `.env`:
   ```
   SMTP_SERVER=smtp-mail.outlook.com
   SMTP_PORT=465
   ```
2. The script automatically uses SSL for port 465

**Option 3: Enable Less Secure Apps**
1. Go to https://account.microsoft.com/security-info
2. Select **Security settings** → **Less secure app access**
3. Enable the setting
4. Use your regular Hotmail password

**Default Settings:**
- SMTP Server: `smtp-mail.outlook.com`
- Port: `587` (TLS) or `465` (SSL)

### Configuration File (config.yaml)

Edit `config.yaml` to customize email content and schedule:

```yaml
email:
  subject: "Your Email Subject"
  body: "Your email body content"

scheduling:
  times:
    - "09:00"  # 9:00 AM
    - "13:00"  # 1:00 PM
    - "17:00"  # 5:00 PM
```

**Or use interval-based scheduling (every 8 hours = 28800 seconds):**

```yaml
scheduling:
  interval_seconds: 28800
```

## Usage

### Running the scheduler

```bash
# Set environment variables
export GITHUB_EMAIL="your_email@gmail.com"
export GITHUB_EMAIL_PASSWORD="your_app_password"

# Run the scheduler
python email_scheduler.py
```

### Running in the background (Linux/macOS)

```bash
nohup python email_scheduler.py > scheduler.log 2>&1 &
```

### Running as a systemd service (Linux)

Create `/etc/systemd/system/email-scheduler.service`:

```ini
[Unit]
Description=Email Scheduler Service
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/home/syed/Documents/source/repo/GitHubScheduler
Environment="GITHUB_EMAIL=your_email@gmail.com"
Environment="GITHUB_EMAIL_PASSWORD=your_app_password"
ExecStart=/usr/bin/python3 /home/syed/Documents/source/repo/GitHubScheduler/email_scheduler.py

[Install]
WantedBy=multi-user.target
```

Then enable and start:

```bash
sudo systemctl enable email-scheduler
sudo systemctl start email-scheduler
```

## Testing

### Quick SMTP Connection Test (Recommended)

Before running the full scheduler, test your SMTP connection:

```bash
# Set your credentials
export GITHUB_EMAIL="your_email@hotmail.com"
export GITHUB_EMAIL_PASSWORD="your_app_password"
export SMTP_PORT=465

# Run diagnostic test
python test_smtp.py
```

This will test each step:
- TCP connection to Hotmail
- SMTP authentication
- Sending a test email
- Connection cleanup

### Full Scheduler Test

To test the email sending functionality:

```python
import os
from email_scheduler import EmailScheduler

os.environ['GITHUB_EMAIL'] = 'your_email@hotmail.com'
os.environ['GITHUB_EMAIL_PASSWORD'] = 'your_app_password'

scheduler = EmailScheduler()
scheduler.send_email()  # Send one test email
```

## Troubleshooting

### "GITHUB_EMAIL environment variable not set"
- Ensure `GITHUB_EMAIL` is set: `echo $GITHUB_EMAIL`
- For GitHub Actions, add the secret to your repository settings

### "Failed to send email: SMTPAuthenticationError" or "basic authentication is disabled"
**For Hotmail/Outlook:**
- Try using an **App Password** instead of your regular password (see "Option 1" above)
- Or use **Port 465 with SSL** instead of port 587 (see "Option 2" above)
- Or enable **Less secure app access** in your account settings (see "Option 3" above)

**For other providers:**
- Verify your email and password/app-password are correct
- Check that 2FA is enabled if using app-specific passwords
- Verify you're using the correct SMTP server for your provider

### "Connection timed out"
- Verify SMTP server and port are correct
- Check your firewall settings
- Ensure your ISP/network allows SMTP connections
- Try using port 465 (SSL) instead of 587 (TLS)

### Script hangs at "Sending email..." or "Queued for sending"
- This usually means the SMTP server is not responding properly
- Run the diagnostic test first: `python test_smtp.py`
- Common fixes:
  1. **Try port 465 instead**: `export SMTP_PORT=465`
  2. **Check your firewall** - Some ISPs block port 587
  3. **Verify app password** - Make sure it's correct and newly generated
  4. **Increase timeout** - Edit `email_scheduler.py` and change `timeout = 15` to `timeout = 30`

### "The script sends but emails don't arrive"
- Check your Hotmail Spam/Junk folder
- Verify the recipient email address in `config.yaml`
- Check Hotmail account activity at https://account.microsoft.com/security-info for blocked attempts

## File Structure

```
GitHubScheduler/
├── email_scheduler.py      # Main scheduler script
├── test_smtp.py            # SMTP connection diagnostic test
├── example.py              # Example usage and tests
├── config.yaml             # Email and scheduling configuration
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variables template
├── .gitignore              # Git ignore file
└── README.md               # This file
```

## License

MIT License
