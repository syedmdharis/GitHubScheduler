"""
Example script demonstrating how to use the EmailScheduler class.
This shows how to send test emails and integrate the scheduler into your project.
"""

import os
from email_scheduler import EmailScheduler
import logging

# Configure logging to see detailed output
logging.basicConfig(level=logging.INFO)

# Example 1: Send a single test email
def send_test_email():
    """Send a single test email to verify configuration."""
    print("=" * 50)
    print("Example 1: Sending a test email")
    print("=" * 50)
    
    try:
        scheduler = EmailScheduler('config.yaml')
        scheduler.send_email()
        print("✓ Test email sent successfully!")
    except Exception as e:
        print(f"✗ Failed to send test email: {e}")


# Example 2: Start the scheduler with all configured jobs
def start_scheduler():
    """Start the scheduler with all configured jobs."""
    print("=" * 50)
    print("Example 2: Starting the scheduler")
    print("=" * 50)
    print("This will schedule emails according to config.yaml")
    print("Press Ctrl+C to stop the scheduler\n")
    
    try:
        scheduler = EmailScheduler('config.yaml')
        scheduler.start()
    except Exception as e:
        print(f"✗ Failed to start scheduler: {e}")


# Example 3: Custom email configuration
def custom_email_example():
    """Example of how to extend EmailScheduler for custom functionality."""
    print("=" * 50)
    print("Example 3: Custom email functionality")
    print("=" * 50)
    
    try:
        scheduler = EmailScheduler('config.yaml')
        
        # You can extend this to send custom emails
        # For example, send with custom body
        original_body = scheduler.config['email']['body']
        scheduler.config['email']['body'] = f"Custom message: {original_body}\nSent at custom time."
        
        scheduler.send_email()
        print("✓ Custom email sent successfully!")
    except Exception as e:
        print(f"✗ Failed to send custom email: {e}")


# Example 4: Verify environment variables
def verify_environment():
    """Verify that all required environment variables are set."""
    print("=" * 50)
    print("Example 4: Verifying environment variables")
    print("=" * 50)
    
    required_vars = ['EMAIL', 'PWD']
    missing_vars = []
    
    for var in required_vars:
        if var in os.environ:
            value = os.environ[var]
            # Mask the password for security
            if 'PWD' in var:
                display_value = '*' * len(value)
            else:
                display_value = value
            print(f"✓ {var}: {display_value}")
        else:
            print(f"✗ {var}: NOT SET")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\nMissing variables: {', '.join(missing_vars)}")
        print("Please set these environment variables before running the scheduler.")
        return False
    else:
        print("\n✓ All required environment variables are set!")
        return True


if __name__ == "__main__":
    import sys
    
    print("\nEmail Scheduler - Examples and Tests\n")
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'test':
            send_test_email()
        elif command == 'start':
            start_scheduler()
        elif command == 'custom':
            custom_email_example()
        elif command == 'verify':
            verify_environment()
        else:
            print(f"Unknown command: {command}")
            print("\nAvailable commands:")
            print("  python example.py test     - Send a test email")
            print("  python example.py start    - Start the scheduler")
            print("  python example.py custom   - Send a custom email")
            print("  python example.py verify   - Verify environment variables")
    else:
        # Run all examples
        print("Running all examples...\n")
        
        # First verify environment
        if verify_environment():
            print("\n")
            send_test_email()
            print("\n")
            custom_email_example()
            print("\n")
            print("=" * 50)
            print("To start the scheduler, run:")
            print("  python example.py start")
            print("=" * 50)
        else:
            print("\nPlease set the required environment variables first.")
