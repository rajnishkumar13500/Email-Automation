#!/usr/bin/env python3
"""
HR Cold Email Automation System with AI Personalization & Company Research
============================================================================
Sends AI-generated personalized cold emails to HR contacts from an Excel file.
Uses OpenRouter AI (free) + Gmail SMTP (free, 500 emails/day limit).
Researches each company via web search for authentic personalization.

Usage:
    python email_sender.py --test    # Send test email to yourself
    python email_sender.py           # Send to all HR contacts
    python email_sender.py --resume  # Resume from where you left off
"""

import smtplib
import pandas as pd
import time
import csv
import argparse
import sys
import requests
import json
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup

# Import configuration
try:
    import config
except ImportError:
    print("ERROR: config.py not found. Please create it from config.py.example")
    sys.exit(1)


class CompanyResearcher:
    """Research company information via web search."""
    
    def __init__(self):
        self.cache = {}  # Cache company info to avoid repeated searches
    
    def search_company(self, company_name: str) -> dict:
        """
        Search for company information using multiple sources.
        
        Returns:
            dict with keys: description, heading, related_info, found
        """
        if not company_name or company_name.lower() in ['nan', 'your company', '']:
            return self._empty_result()
        
        # Check cache first
        cache_key = company_name.lower().strip()
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Try Wikipedia first (most reliable)
        result = self._search_wikipedia(company_name)
        
        # If Wikipedia fails, try DuckDuckGo
        if not result['found']:
            result = self._search_duckduckgo(company_name)
        
        # If both fail, try web scraping
        if not result['found']:
            result = self._scrape_search(company_name)
        
        self.cache[cache_key] = result
        return result
    
    def _search_wikipedia(self, company_name: str) -> dict:
        """Search Wikipedia for company info."""
        try:
            # Wikipedia API search
            search_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{requests.utils.quote(company_name)}"
            
            response = requests.get(search_url, timeout=10, headers={
                'User-Agent': 'EmailAutomation/1.0 (Student Project)'
            })
            
            if response.status_code == 200:
                data = response.json()
                extract = data.get('extract', '')
                title = data.get('title', '')
                
                if extract and len(extract) > 50:
                    return {
                        'description': extract[:500],
                        'heading': title,
                        'related_info': '',
                        'found': True
                    }
            
            # Try with "(company)" suffix for disambiguation
            search_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{requests.utils.quote(company_name + ' (company)')}"
            response = requests.get(search_url, timeout=10, headers={
                'User-Agent': 'EmailAutomation/1.0 (Student Project)'
            })
            
            if response.status_code == 200:
                data = response.json()
                extract = data.get('extract', '')
                title = data.get('title', '')
                
                if extract and len(extract) > 50:
                    return {
                        'description': extract[:500],
                        'heading': title,
                        'related_info': '',
                        'found': True
                    }
                    
        except Exception as e:
            pass
        
        return self._empty_result()
    
    def _search_duckduckgo(self, company_name: str) -> dict:
        """Search DuckDuckGo for company info."""
        try:
            query = f"{company_name} company"
            url = f"https://api.duckduckgo.com/?q={requests.utils.quote(query)}&format=json&no_html=1"
            
            response = requests.get(url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            
            if response.status_code == 200:
                data = response.json()
                abstract = data.get('Abstract', '')
                heading = data.get('Heading', '')
                
                # Check related topics
                related = []
                for topic in data.get('RelatedTopics', [])[:3]:
                    if isinstance(topic, dict) and 'Text' in topic:
                        related.append(topic['Text'])
                
                if abstract or related:
                    return {
                        'description': abstract if abstract else related[0] if related else '',
                        'heading': heading,
                        'related_info': ' '.join(related)[:300],
                        'found': bool(abstract or related)
                    }
                    
        except Exception as e:
            pass
        
        return self._empty_result()
    
    def _scrape_search(self, company_name: str) -> dict:
        """Fallback: scrape Bing search results (more reliable than Google)."""
        try:
            query = f"{company_name} company about us"
            url = f"https://www.bing.com/search?q={requests.utils.quote(query)}"
            
            response = requests.get(url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            })
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find snippets from Bing results
                snippets = []
                for p in soup.find_all(['p', 'span', 'li']):
                    text = p.get_text().strip()
                    if len(text) > 80 and company_name.lower() in text.lower():
                        # Clean up the text
                        text = re.sub(r'\s+', ' ', text)
                        if not any(skip in text.lower() for skip in ['cookie', 'privacy', 'sign in', 'log in']):
                            snippets.append(text)
                            if len(snippets) >= 2:
                                break
                
                if snippets:
                    return {
                        'description': snippets[0][:400],
                        'heading': company_name,
                        'related_info': snippets[1][:200] if len(snippets) > 1 else '',
                        'found': True
                    }
        except Exception as e:
            pass
        
        return self._empty_result()
    
    def _empty_result(self) -> dict:
        return {
            'description': '',
            'heading': '',
            'related_info': '',
            'found': False
        }
    
    def get_company_summary(self, company_name: str) -> str:
        """Get a brief summary about the company for email personalization."""
        info = self.search_company(company_name)
        
        if info['found']:
            summary = info['description']
            if info['related_info']:
                summary += f" {info['related_info']}"
            # Clean up and limit length
            summary = re.sub(r'\s+', ' ', summary).strip()
            return summary[:500]
        
        return f"{company_name} (no additional information found)"


class AIEmailGenerator:
    """Generate personalized emails using OpenRouter AI with company research."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "arcee-ai/trinity-large-preview:free"
        self.researcher = CompanyResearcher()
    
    def generate_email(self, hr_name: str, company: str, title: str, 
                       candidate_name: str, skills: str, experience: str, 
                       education: str, linkedin: str, phone: str,
                       target_roles: str = "") -> tuple:
        """
        Generate a unique personalized cold email using AI with real company research.
        
        Returns:
            tuple: (subject, body)
        """
        # Clean up HR name
        clean_name = hr_name.strip()
        for prefix in ['Mr.', 'Ms.', 'Mrs.', 'Dr.', 'Mr', 'Ms', 'Mrs', 'Dr']:
            if clean_name.startswith(prefix):
                clean_name = clean_name[len(prefix):].strip()
        first_name = clean_name.split()[0] if clean_name else "Hiring Manager"
        
        company_clean = company.strip() if pd.notna(company) and company else "your company"
        title_clean = title.strip() if pd.notna(title) and title else "HR Professional"
        
        # Research the company
        print(f"   🔍 Researching {company_clean}...")
        company_info = self.researcher.get_company_summary(company_clean)
        print(f"   📊 Company Info: {company_info[:200]}..." if len(company_info) > 200 else f"   📊 Company Info: {company_info}")
        
        prompt = f"""You are an expert career coach and persuasive copywriter. Write a cold email that will COMPEL the HR to respond and shortlist this candidate.

RECIPIENT DETAILS:
- HR Name: {first_name}
- Company: {company_clean}
- HR Title: {title_clean}

REAL COMPANY INFORMATION (use this to personalize):
{company_info}

CANDIDATE DETAILS:
- Name: {candidate_name}
- Skills: {skills}
- Experience: {experience}
- Education: {education}
- LinkedIn: {linkedin}

CANDIDATE'S AREA OF INTEREST/EXPERTISE:
{target_roles}

CRITICAL REQUIREMENTS FOR A HIGH-RESPONSE EMAIL:
1. SUBJECT LINE (MOST IMPORTANT - HR decides to open or delete based on this!):
   - Make it IRRESISTIBLE, eye-catching, and impossible to ignore
   - Create curiosity or intrigue that FORCES them to click
   - Mention the company name + something unique about you
   - Use power words: "Transforming", "Driving", "Elevating", "Passionate about"
   - Examples of GREAT subjects:
     * "A Data Scientist Who Thinks Like {company}'s Product Team"
     * "What {company}'s AI Strategy Taught Me About Innovation"
     * "From Solving {company}-Sized Problems to Joining Your Team"
     * "The Intersection of Security & AI - My Pitch for {company}"
   - AVOID boring subjects like "Application for Position" or "Job Inquiry"
2. OPENING HOOK: Reference something REAL about the company from the information provided above
3. SUBTLE ROLE INDICATION: DO NOT directly say "I'm looking for a Software Engineer role". Instead:
   - Frame your skills and projects around the target areas naturally
   - Mention relevant projects or interests that align with those roles
   - Let your expertise speak for itself
   - Example: Instead of "seeking IAM Developer role", say "my work in building secure authentication systems..."
   - Example: Instead of "looking for Full Stack position", say "my experience building end-to-end web applications..."
4. VALUE PROPOSITION: Connect your skills to what the company does + your area of interest
5. CLEAR CTA: End with a low-pressure call to action
6. WRITING STYLE (CRITICAL):
   - Write like a HUMAN, not a robot or corporate machine
   - Use SIMPLE, everyday words - no fancy vocabulary or corporate buzzwords
   - NO words like: "leverage", "synergy", "spearhead", "utilize", "endeavor", "paramount"
   - YES words like: "help", "work", "build", "create", "improve", "grow"
   - Write like you're talking to a friend who happens to be a professional
   - Be genuine and authentic - HRs can smell fake emails instantly
   - Sound confident but humble, not arrogant or desperate
7. FORMATTING:
   - Use **bold** (double asterisks) for 1-2 KEY points you want HR to notice
   - Example: "I've worked with **SailPoint** and **Okta**" or "built **secure authentication systems**"
   - Do NOT overuse bold - only the most important 1-2 things
8. AVOID AI PATTERNS (very important):
   - NO em-dashes (—) or unusual punctuation
   - NO phrases like "I hope this email finds you well"
   - NO "I am writing to express my interest"
   - NO "I believe I would be a great fit"
   - These scream "AI-generated template" - avoid them!
9. LENGTH: 80-120 words MAXIMUM
10. NO PLACEHOLDERS: Never use [brackets] or placeholder text

WHAT MAKES HRs RESPOND:
- Emails that feel REAL and human, not template-generated
- Simple, clear language that's easy to read
- Genuine interest in the company (not just "give me a job")
- Confidence without arrogance

FORMAT YOUR RESPONSE EXACTLY LIKE THIS:
SUBJECT: [Your compelling subject line]

[Email body - SHORT, IMPACTFUL, with subtle role hints]

Best regards,
{candidate_name}
LinkedIn: {linkedin}"""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost",
            "X-Title": "Email Automation",
        }
        
        data = json.dumps({
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        })
        
        try:
            response = requests.post(self.url, headers=headers, data=data, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                return self._parse_email(content, first_name, company_clean, candidate_name, phone, linkedin)
            else:
                print(f"⚠️  AI API Error: {response.status_code}")
                return self._fallback_email(first_name, company_clean, candidate_name, skills, experience, phone, linkedin, company_info)
                
        except Exception as e:
            print(f"⚠️  AI generation failed: {e}")
            return self._fallback_email(first_name, company_clean, candidate_name, skills, experience, phone, linkedin, company_info)
    
    def _parse_email(self, content: str, hr_name: str, company: str, 
                     candidate_name: str, phone: str, linkedin: str) -> tuple:
        """Parse AI response to extract subject and body."""
        lines = content.strip().split('\n')
        subject = ""
        body_lines = []
        body_start = False
        
        for line in lines:
            if line.upper().startswith('SUBJECT:'):
                subject = line.split(':', 1)[1].strip()
                body_start = True
            elif body_start:
                body_lines.append(line)
        
        body = '\n'.join(body_lines).strip()
        
        # Fallback if parsing failed
        if not subject:
            subject = f"Exploring Opportunities at {company}"
        if not body:
            body = content
        
        return subject, body
    
    def _fallback_email(self, hr_name: str, company: str, candidate_name: str, 
                        skills: str, experience: str, phone: str, linkedin: str,
                        company_info: str = "") -> tuple:
        """Fallback template when AI fails."""
        subject = f"Application for Entry-Level Opportunity at {company}"
        
        # Use company info if available
        company_hook = ""
        if company_info and "no additional information" not in company_info:
            company_hook = f"I've been following {company}'s work and am impressed by your impact in the industry. "
        
        body = f"""Dear {hr_name},

{company_hook}I am {candidate_name}, {experience}. My skills in {skills} align well with the innovative work at {company}.

I would love the opportunity to discuss how I could contribute to your team.

Best regards,
{candidate_name}
{linkedin}"""
        return subject, body


class EmailAutomation:
    def __init__(self):
        self.excel_path = Path(__file__).parent / "HR_Contact_List.xlsx"
        self.log_path = Path(__file__).parent / "sent_log.csv"
        self.templates_path = Path(__file__).parent / "templates"
        
        # Auto-find resume PDF in templates folder
        pdf_files = list(self.templates_path.glob("*.pdf"))
        self.resume_path = pdf_files[0] if pdf_files else None
        
        # Initialize AI generator
        self.ai_generator = AIEmailGenerator(config.OPENROUTER_API_KEY)
        
        self.sent_emails = set()
        self.load_sent_log()
    
    def load_sent_log(self):
        """Load previously sent emails to enable resume functionality."""
        if self.log_path.exists():
            try:
                with open(self.log_path, 'r', newline='', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if row.get('status') == 'sent':
                            self.sent_emails.add(row['email'].lower())
                print(f"📋 Loaded {len(self.sent_emails)} previously sent emails")
            except Exception as e:
                print(f"⚠️  Could not load sent log: {e}")
    
    def log_email(self, email: str, status: str, error: str = ""):
        """Log email sending status to CSV."""
        file_exists = self.log_path.exists()
        with open(self.log_path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(['email', 'status', 'timestamp', 'error'])
            writer.writerow([email, status, datetime.now().isoformat(), error])
    
    def _convert_to_html(self, text: str) -> str:
        """Convert plain text to HTML with clickable links."""
        import re
        
        # First, extract and replace LinkedIn URL with a placeholder
        linkedin_placeholder = "___LINKEDIN_LINK___"
        linkedin_match = re.search(r'LinkedIn:\s*(https?://(?:www\.)?linkedin\.com/[^\s]+)', text)
        linkedin_url = ""
        if linkedin_match:
            linkedin_url = linkedin_match.group(1)
            text = re.sub(r'LinkedIn:\s*https?://(?:www\.)?linkedin\.com/[^\s]+', linkedin_placeholder, text)
        
        # Escape HTML special characters
        text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        
        # Replace placeholder with actual HTML link
        if linkedin_url:
            text = text.replace(linkedin_placeholder, f'<a href="{linkedin_url}" style="color: #0077B5; text-decoration: none;">LinkedIn</a>')
        
        # Convert markdown bold **text** to HTML <strong>
        text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
        
        # Convert newlines to HTML breaks
        text = text.replace('\n', '<br>\n')
        
        # Wrap in basic HTML structure with professional styling
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; font-size: 14px; line-height: 1.6; color: #333;">
        {text}
        </body>
        </html>
        """
        return html
    
    def send_email(self, to_email: str, subject: str, body: str, attach_resume: bool = True) -> bool:
        """Send email via Gmail SMTP with HTML formatting."""
        try:
            msg = MIMEMultipart()
            msg['From'] = config.EMAIL_ADDRESS
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add BCC if configured
            bcc_email = getattr(config, 'BCC_EMAIL', '')
            if bcc_email:
                msg['Bcc'] = bcc_email
            # Convert plain text body to HTML with clickable links
            html_body = self._convert_to_html(body)
            msg.attach(MIMEText(html_body, 'html'))
            
            # Attach resume if exists
            if attach_resume and self.resume_path and self.resume_path.exists():
                try:
                    with open(self.resume_path, 'rb') as f:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(f.read())
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition', 
                                   f'attachment; filename="{config.YOUR_NAME.replace(" ", "_")}_Resume.pdf"')
                    msg.attach(part)
                except Exception as e:
                    print(f"⚠️  Could not attach resume: {e}")
            
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(config.EMAIL_ADDRESS, config.APP_PASSWORD.replace(" ", ""))
                server.send_message(msg)
            
            return True
            
        except smtplib.SMTPAuthenticationError:
            print("\n❌ AUTHENTICATION FAILED!")
            print("Please check your EMAIL_ADDRESS and APP_PASSWORD in config.py")
            return False
            
        except Exception as e:
            print(f"❌ Failed to send: {e}")
            return False
    
    def load_contacts(self) -> pd.DataFrame:
        """Load HR contacts from Excel file."""
        if not self.excel_path.exists():
            print(f"ERROR: Excel file not found at {self.excel_path}")
            sys.exit(1)
        
        df = pd.read_excel(self.excel_path)
        print(f"📊 Loaded {len(df)} contacts from Excel")
        return df
    
    def run_test(self):
        """Send a test email to yourself with AI-generated content."""
        print("\n🧪 TEST MODE (AI-Powered with Company Research)")
        print("=" * 50)
        
        print("🤖 Generating personalized email with AI...")
        subject, body = self.ai_generator.generate_email(
            hr_name="Test HR",
            company="Google",  # Use a real company for testing
            title="HR Manager",
            candidate_name=config.YOUR_NAME,
            skills=config.YOUR_SKILLS,
            experience=config.YOUR_EXPERIENCE,
            education=config.YOUR_EDUCATION,
            linkedin=config.YOUR_LINKEDIN,
            phone=config.YOUR_PHONE,
            target_roles=config.TARGET_ROLES
        )
        
        print(f"\n📧 Sending test email to: {config.TEST_EMAIL}")
        print(f"📝 Subject: {subject}")
        print("\n--- AI-Generated Email Preview ---")
        print(body)
        print("--- End Preview ---\n")
        
        if self.send_email(config.TEST_EMAIL, subject, body):
            print("✅ Test email sent successfully!")
            print(f"📬 Check your inbox at {config.TEST_EMAIL}")
        else:
            print("❌ Test failed. Please check your config.py settings.")
    
    def run_production(self, resume_mode: bool = False, auto_mode: bool = False):
        """Send AI-generated emails to all HR contacts."""
        print("\n🚀 PRODUCTION MODE (AI-Powered with Company Research)")
        print("=" * 50)
        
        if resume_mode:
            print("📋 Resume mode: Skipping previously sent emails")
        
        df = self.load_contacts()
        
        if resume_mode:
            df = df[~df['Email'].str.lower().isin(self.sent_emails)]
            print(f"📧 {len(df)} emails remaining to send")
        
        if len(df) == 0:
            print("✅ All emails have already been sent!")
            return
        
        df = df.head(config.DAILY_LIMIT)
        print(f"📊 Will send {len(df)} AI-generated emails today (limit: {config.DAILY_LIMIT})")
        print("🔍 Each email will include real company research for personalization")
        
        # Skip confirmation in auto mode (for GitHub Actions)
        if not auto_mode:
            print(f"\n⚠️  About to send {len(df)} emails with {config.DELAY_BETWEEN_EMAILS}s delay between each")
            confirm = input("Type 'YES' to continue: ")
            if confirm != 'YES':
                print("❌ Cancelled by user")
                return
        else:
            print(f"\n🤖 Auto mode: Sending {len(df)} emails...")
        
        sent_count = 0
        failed_count = 0
        
        for idx, row in df.iterrows():
            email = str(row['Email']).strip()
            name = str(row['Name']) if pd.notna(row['Name']) else "Hiring Manager"
            company = str(row['Company']) if pd.notna(row['Company']) else ""
            title = str(row['Title']) if pd.notna(row['Title']) else ""
            
            if not email or '@' not in email or email.lower() == 'nan':
                print(f"⏭️  Skipping invalid email: {email}")
                continue
            
            if email.lower() in self.sent_emails:
                print(f"⏭️  Already sent: {email}")
                continue
            
            print(f"\n📧 [{sent_count + failed_count + 1}/{len(df)}] Processing {name} at {company}...")
            
            # Generate unique AI email with company research
            subject, body = self.ai_generator.generate_email(
                hr_name=name,
                company=company,
                title=title,
                candidate_name=config.YOUR_NAME,
                skills=config.YOUR_SKILLS,
                experience=config.YOUR_EXPERIENCE,
                education=config.YOUR_EDUCATION,
                linkedin=config.YOUR_LINKEDIN,
                phone=config.YOUR_PHONE,
                target_roles=config.TARGET_ROLES
            )
            
            print(f"   📝 Subject: {subject[:60]}...")
            print(f"   📨 Sending to: {email}")
            
            if self.send_email(email, subject, body):
                sent_count += 1
                self.sent_emails.add(email.lower())
                self.log_email(email, 'sent')
                print(f"   ✅ Sent! (Total: {sent_count})")
            else:
                failed_count += 1
                self.log_email(email, 'failed')
                print(f"   ❌ Failed!")
            
            if sent_count + failed_count < len(df):
                # Random delay between 2-8 minutes to appear more human
                import random
                delay = random.randint(120, 480)  # 2-8 minutes in seconds
                print(f"   ⏳ Waiting {delay // 60} min {delay % 60}s before next email...")
                time.sleep(delay)
        
        print("\n" + "=" * 50)
        print("📊 SUMMARY")
        print(f"   ✅ Sent: {sent_count}")
        print(f"   ❌ Failed: {failed_count}")
        print(f"   📋 Log saved to: {self.log_path}")


def main():
    parser = argparse.ArgumentParser(description='HR Cold Email Automation with AI & Research')
    parser.add_argument('--test', action='store_true', help='Send test email to yourself')
    parser.add_argument('--resume', action='store_true', help='Resume from where you left off')
    parser.add_argument('--auto', action='store_true', help='Auto mode - skip confirmation (for GitHub Actions)')
    args = parser.parse_args()
    
    print("\n" + "=" * 50)
    print("  📧 HR Cold Email Automation (AI + Research)")
    print("=" * 50)
    
    automation = EmailAutomation()
    
    if args.test:
        automation.run_test()
    else:
        automation.run_production(resume_mode=args.resume, auto_mode=args.auto)


if __name__ == "__main__":
    main()
