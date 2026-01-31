# HR Cold Email Automation System (AI-Powered)

Free Python tool to send **AI-generated personalized** cold emails to HR contacts.

## Quick Start (Local)

### 1. Setup
```bash
pip install pandas openpyxl requests beautifulsoup4
```

### 2. Configure
Copy `config.example.py` to `config.py` and fill in your credentials.

### 3. Run
```bash
# Test first
python email_sender.py --test

# Send to all HRs
python email_sender.py

# Resume if interrupted
python email_sender.py --resume
```

---

## GitHub Actions Automation

### Setup Secrets
Go to your repo → **Settings → Secrets and variables → Actions** → Add these secrets:

| Secret | Value |
|--------|-------|
| `EMAIL_ADDRESS` | Your Gmail address |
| `APP_PASSWORD` | Gmail App Password (16 chars) |
| `OPENROUTER_API_KEY` | Your OpenRouter API key |
| `YOUR_NAME` | Your full name |
| `YOUR_PHONE` | Your phone number |
| `YOUR_LINKEDIN` | LinkedIn profile URL |
| `YOUR_PORTFOLIO` | Portfolio URL (optional) |
| `YOUR_SKILLS` | Your skills |
| `YOUR_EXPERIENCE` | Experience summary |
| `YOUR_EDUCATION` | Education details |
| `TARGET_ROLES` | Target job roles |
| `TEST_EMAIL` | Where to send test emails |
| `BCC_EMAIL` | BCC email (optional) |

### Schedule
Emails automatically send at **9:00 AM IST** (Monday-Friday).

### Manual Trigger
Go to **Actions → Send Cold Emails → Run workflow**

---

## Features
- ✅ **AI-Powered**: Unique email for each HR
- ✅ **Company Research**: Uses Wikipedia to personalize
- ✅ **BCC Support**: Copy someone on all emails
- ✅ **Rate Limiting**: Avoids spam filters
- ✅ **Resume Capability**: Tracks in `sent_log.csv`
- ✅ **GitHub Actions**: Automated daily sending

## Files
| File | Purpose |
|------|---------|
| `email_sender.py` | Main script |
| `config.example.py` | Config template (commit this) |
| `config.py` | Your settings (NEVER commit) |
| `.github/workflows/send-emails.yml` | Automation |
