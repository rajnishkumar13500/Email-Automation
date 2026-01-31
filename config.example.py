"""
Email Automation Configuration Template
========================================
Copy this file to config.py and fill in your details.
NEVER commit config.py to GitHub - it contains secrets!
"""

# Your Gmail credentials
EMAIL_ADDRESS = "your.email@gmail.com"  # Your Gmail address
APP_PASSWORD = "xxxx xxxx xxxx xxxx"     # Your Gmail App Password (16 chars with spaces)

# OpenRouter API for AI-generated emails (free)
OPENROUTER_API_KEY = "sk-or-v1-your-api-key-here"


# Your personal information (used in email template)
YOUR_NAME = "Your Name"
YOUR_PHONE = "+91-XXXXXXXXXX"
YOUR_LINKEDIN = "https://www.linkedin.com/in/your-profile/"
YOUR_PORTFOLIO = ""  # Optional, leave empty if none

# Your skills and experience (customize based on your background)
YOUR_SKILLS = "Your skills here"
YOUR_EXPERIENCE = "Your experience summary"
YOUR_EDUCATION = "Your education details"

# Target roles you're interested in (AI will subtly mention these)
# Example for security roles: "Software Engineer, IAM Developer, Information Security, Security Analyst"
# Example for dev roles: "Software Developer, Full Stack Developer, Mainframe Developer, COBOL"
TARGET_ROLES = "Your target roles here"

# Email settings
# Note: Delay between emails is RANDOM (2-8 minutes) to appear more human-like
DAILY_LIMIT = 10           # Emails per run (GitHub Actions runs daily at 9 AM IST)
TEST_EMAIL = "your.test.email@gmail.com"  # Where to send test emails
BCC_EMAIL = ""  # Optional: BCC someone on all emails (leave empty to disable)
