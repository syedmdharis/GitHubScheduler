import os
import smtplib
import yaml
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import logging
import ssl

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EmailScheduler:
    def __init__(self, config_file='config.yaml'):
        """Initialize the email scheduler with configuration from YAML file."""
        self.config = self.load_config(config_file)
        self.email = self.get_email_from_env()
        self.password = self.get_password_from_env()
        self.scheduler = BackgroundScheduler()
        
    def load_config(self, config_file):
        """Load configuration from YAML file."""
        try:
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
            logger.info(f"Configuration loaded from {config_file}")
            return config
        except FileNotFoundError:
            logger.error(f"Configuration file {config_file} not found!")
            raise
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML file: {e}")
            raise
    
    def get_email_from_env(self):
        """Read email from GitHub environment variable."""
        email = os.getenv('GITHUB_EMAIL')
        if not email:
            raise ValueError("GITHUB_EMAIL environment variable not set!")
        logger.info(f"Email loaded from environment: {email}")
        return email
    
    def get_password_from_env(self):
        """Read email password/token from GitHub environment variable."""
        password = os.getenv('GITHUB_EMAIL_PASSWORD')
        if not password:
            raise ValueError("GITHUB_EMAIL_PASSWORD environment variable not set!")
        logger.info("Email password/token loaded from environment")
        return password
    
    def send_email(self, recipient=None):
        """Send email to recipient."""
        try:
            recipient = recipient or self.email
            subject = self.config.get('email', {}).get('subject', 'Notification')
            body = self.config.get('email', {}).get('body', 'This is a notification.')
            
            # Create email message
            msg = MIMEMultipart()
            msg['From'] = self.email
            msg['To'] = recipient
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email via SMTP (Hotmail/Outlook)
            # For Hotmail: use smtp-mail.outlook.com
            # Port 465 (SSL) is recommended and more secure
            smtp_server = os.getenv('SMTP_SERVER', 'smtp-mail.outlook.com')
            smtp_port = int(os.getenv('SMTP_PORT', '465'))
            timeout = 15  # 15 second timeout
            
            # Create SSL context
            context = ssl.create_default_context()
            
            logger.info(f"[STEP 1] Connecting to {smtp_server}:{smtp_port}...")
            
            # Use SSL for port 465, TLS for port 587
            if smtp_port == 465:
                logger.info(f"[STEP 2] Using SSL connection with {timeout}s timeout...")
                server = smtplib.SMTP_SSL(smtp_server, smtp_port, context=context, timeout=timeout)
            else:
                logger.info(f"[STEP 2] Using TLS connection with {timeout}s timeout...")
                server = smtplib.SMTP(smtp_server, smtp_port, timeout=timeout)
                server.starttls(context=context)
            
            logger.info(f"[STEP 3] Connected! Logging in as {self.email}...")
            server.login(self.email, self.password)
            
            logger.info(f"[STEP 4] Sending email to {recipient}...")
            # Use sendmail instead of send_message for better control
            server.sendmail(self.email, recipient, msg.as_string())
            
            logger.info(f"[STEP 5] Message queued for sending...")
            server.quit()
            
            logger.info(f"✓ Email sent successfully to {recipient} at {datetime.now()}")
            
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"✗ Authentication failed: {e}")
            logger.error("Make sure you're using an App Password, not your regular password!")
            logger.error("Generate one at: https://account.microsoft.com/security-info -> App passwords")
            raise
        except smtplib.SMTPException as e:
            logger.error(f"✗ SMTP Error: {e}")
            raise
        except TimeoutError as e:
            logger.error(f"✗ Connection timeout after 15 seconds: {e}")
            logger.error("The Hotmail server is not responding. Check your internet connection.")
            raise
        except Exception as e:
            logger.error(f"✗ Failed to send email: {e}")
            logger.error(f"Exception type: {type(e).__name__}")
            raise
            
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"Authentication failed: {e}")
            logger.error("Make sure you're using an App Password, not your regular password!")
            logger.error("Generate one at: https://account.microsoft.com/security-info -> App passwords")
            raise
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            raise
    
    def schedule_jobs(self):
        """Schedule email jobs based on configuration."""
        try:
            # Check if using cron times or interval
            if 'times' in self.config.get('scheduling', {}):
                # Schedule using specific times (cron format)
                times = self.config['scheduling']['times']
                for time_str in times:
                    hour, minute = map(int, time_str.split(':'))
                    trigger = CronTrigger(hour=hour, minute=minute)
                    job_id = f"email_job_{hour}_{minute}"
                    self.scheduler.add_job(
                        self.send_email,
                        trigger=trigger,
                        id=job_id,
                        name=f"Send email at {time_str}"
                    )
                    logger.info(f"Scheduled job: Send email at {time_str}")
            
            elif 'interval_seconds' in self.config.get('scheduling', {}):
                # Schedule using intervals
                interval = self.config['scheduling']['interval_seconds']
                self.scheduler.add_job(
                    self.send_email,
                    'interval',
                    seconds=interval,
                    id='email_job_interval',
                    name=f"Send email every {interval} seconds"
                )
                logger.info(f"Scheduled job: Send email every {interval} seconds")
            
        except Exception as e:
            logger.error(f"Failed to schedule jobs: {e}")
            raise
    
    def start(self):
        """Start the scheduler."""
        try:
            self.schedule_jobs()
            self.scheduler.start()
            logger.info("Email scheduler started!")
            
            # Keep the scheduler running
            try:
                while True:
                    pass
            except KeyboardInterrupt:
                logger.info("Scheduler interrupted by user")
                self.stop()
        
        except Exception as e:
            logger.error(f"Failed to start scheduler: {e}")
            raise
    
    def stop(self):
        """Stop the scheduler."""
        self.scheduler.shutdown()
        logger.info("Email scheduler stopped!")


if __name__ == "__main__":
    try:
        scheduler = EmailScheduler('config.yaml')
        scheduler.start()
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
