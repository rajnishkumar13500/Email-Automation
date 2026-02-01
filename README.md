# HR Cold Email Automation System (AI-Powered)

Free Python tool to send **AI-generated personalized** cold emails to HR contacts with company research, HTML formatting, and automatic progress tracking.

## 🚀 Features

| Feature | Description |
|---------|-------------|
| 🤖 **AI-Powered Emails** | Each email uniquely generated using OpenRouter AI |
| 🔍 **Company Research** | Auto-researches companies via Wikipedia for personalization |
| 🔄 **AI Retry Logic** | Tries AI twice before using fallback template |
| ⏰ **Random Delays** | 2-8 minute random delays between emails (appears human) |
| 📧 **HTML Formatting** | Bold keywords, clickable LinkedIn links |
| 📋 **Progress Tracking** | Remembers sent emails via `sent_log.csv` |
| 📎 **Resume Attachment** | Auto-attaches PDF resume from `templates/` folder |
| 👥 **BCC Support** | Option to BCC someone on all emails |
| ⚡ **GitHub Actions** | Automated daily sending with persistent progress |

---

## 📋 Quick Start (Local)

### 1. Install Dependencies
```bash
pip install pandas openpyxl requests beautifulsoup4
```

### 2. Configure
Copy `config.example.py` to `config.py` and fill in your credentials:
- Gmail address and App Password
- OpenRouter API key (free at openrouter.ai)
- Your personal info, skills, experience

### 3. Prepare Files
- Place your HR contacts in `HR_Contact_List.xlsx` (columns: Name, Email, Company, Title)
- Place your resume PDF in `templates/` folder

### 4. Run
```bash
# Test first (sends to your TEST_EMAIL)
python email_sender.py --test

# Send to all HRs (asks for confirmation)
python email_sender.py

# Resume from where you left off
python email_sender.py --resume
```

---

## ⚙️ GitHub Actions Automation

### Setup Secrets
Go to **Settings → Secrets and variables → Actions** → Add:

| Secret | Description |
|--------|-------------|
| `EMAIL_ADDRESS` | Your Gmail address |
| `APP_PASSWORD` | Gmail App Password (16 chars) |
| `OPENROUTER_API_KEY` | OpenRouter API key |
| `YOUR_NAME` | Your full name |
| `YOUR_PHONE` | Phone number |
| `YOUR_LINKEDIN` | LinkedIn profile URL |
| `YOUR_PORTFOLIO` | Portfolio URL (optional) |
| `YOUR_SKILLS` | Your skills (comma-separated) |
| `YOUR_EXPERIENCE` | Experience summary |
| `YOUR_EDUCATION` | Education details |
| `TARGET_ROLES` | Target job roles (comma-separated) |
| `TEST_EMAIL` | Where to send test emails |
| `BCC_EMAIL` | BCC email (optional) |

### Schedule
- **Automatic**: Runs at **9:00 AM IST** (Monday-Friday)
- **Manual**: Go to Actions → Send Cold Emails → Run workflow

### Progress Persistence
GitHub Actions automatically commits `sent_log.csv` after each run, so it remembers which emails were sent across runs.

---

## 📁 Project Structure

| File | Purpose |
|------|---------|
| `email_sender.py` | Main script with AI generation |
| `config.py` | Your settings (**NEVER commit**) |
| `config.example.py` | Config template (safe to commit) |
| `HR_Contact_List.xlsx` | HR contacts to email |
| `sent_log.csv` | Tracks sent emails |
| `templates/*.pdf` | Your resume (auto-attached) |
| `.github/workflows/send-emails.yml` | GitHub Actions workflow |

---

## 📧 Email Format

Each email includes:
- **Personalized greeting** with HR name
- **Company-specific hook** from research
- **Your skills highlighted in bold**
- **Call to action**
- **Signature** with name and clickable LinkedIn

Example:
```
Dear [HR Name],

I came across [Company] and was impressed...

With hands-on experience in **IAM**, **SailPoint**, **Okta**...

Would you be open to a quick chat?

Best regards,
[Your Name]
LinkedIn  ← clickable link
```

---

## 🔧 Configuration Options

In `config.py`:
- `DAILY_LIMIT` - Max emails per run (default: 10)
- `BCC_EMAIL` - Optional BCC recipient
- `TARGET_ROLES` - AI subtly mentions these roles

---

## 📝 License

MIT License - Free to use and modify.
