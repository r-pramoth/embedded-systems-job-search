#!/usr/bin/env python3
"""
Daily Embedded Systems Fresher Job Search Script
Runs via GitHub Actions every day at 7:30 AM IST
"""

import os
import json
from datetime import datetime
from anthropic import Anthropic

def create_search_prompt():
    """Generate the comprehensive job search prompt"""
    return """
Every day at 7:30 AM IST, search the web for newly posted job openings suitable for freshers in Embedded Systems.

PRIMARY OBJECTIVE

Find genuine and relevant Embedded Systems opportunities in India and internationally, with the newest postings receiving the highest priority.

The purpose of this task is to discover opportunities as early as possible so I can personally decide which jobs to apply for.

IMPORTANT — DO NOT MAKE THE FINAL DECISION FOR ME

Do not silently reject or remove a potentially relevant job based on your own assumptions.

If a job is reasonably related to Embedded Systems and could potentially be relevant to a fresher:

- Include it in the results.
- Show the employer's stated requirements.
- Show the exact experience requirement when available.
- Clearly identify uncertainty.
- Let me make the final decision about whether to apply.

Do not reject a job merely because:
- The job description is ambiguous.
- The employer does not explicitly use the word "fresher."
- The experience requirement is unclear.
- The job asks for skills I may not currently have.
- The job contains multiple technical requirements.
- You think my chances of getting selected are low.
- The position is international.
- Visa sponsorship information is unavailable.
- Relocation may be required.
- The salary is below my preferred amount.
- You personally consider the job a weaker match.

However, exclude positions that explicitly require 2+ years of professional experience when freshers are clearly ineligible, and clearly senior, lead, principal, architect, manager, or experienced-only positions.

When uncertain, INCLUDE THE JOB and explain the uncertainty.

The final decision about whether I should apply belongs to me.

SALARY PREFERENCE — IMPORTANT

My preferred target is approximately:

₹1,00,000 per month or approximately ₹12 LPA.

This is ONLY an additional preference, NOT a minimum requirement.

NEVER reject or exclude a job merely because:
- Salary is below ₹1,00,000/month.
- Salary is not disclosed.
- Salary information cannot be verified.

Always report the actual salary when available.

If salary is available, classify it as:

- ₹1,00,000+/month — Meets/exceeds my preferred target
- ₹75,000–₹99,999/month — Close to preferred target
- ₹50,000–₹74,999/month — Below preferred target
- Below ₹50,000/month — Significantly below preferred target
- Not disclosed — Salary not mentioned

For annual compensation, convert it approximately to monthly compensation for easier comparison, while preserving the original CTC/package figure.

Example:

₹12 LPA CTC → approximately ₹1,00,000/month CTC equivalent.

Clearly distinguish:
- CTC
- Base salary
- Bonus
- Stock/equity
- Stipend
- Estimated/inferred compensation

Do not treat CTC as take-home salary.

SALARY PRIORITY

Use salary as an additional ranking factor only.

A lower-paying job can still be a high-priority result if:
- The company is highly reputable.
- The role provides strong Embedded Systems experience.
- The technology stack is valuable.
- The company offers strong learning opportunities.
- The role is directly relevant to firmware/embedded development.
- The opportunity has strong long-term career value.

Do not sacrifice job relevance merely to reach the ₹1 lakh/month preference.

TIMING STRATEGY

- Run the search every day at 7:30 AM IST.
- Prioritize jobs posted within the previous 24 hours.
- Give the newest verified jobs the highest priority.
- If fewer than 5 strong matches are found within 24 hours, expand the search to jobs posted within the previous 7 days.
- Search international jobs according to the employer's local time zone as well.
- Give additional priority to fresh postings from Monday through Thursday, especially Tuesday and Wednesday.
- Do not exclude jobs simply because they were posted outside normal business hours.

SEARCH SCOPE

INDIA:

Search across all cities and states in India.

Include:
- Onsite
- Hybrid
- Remote

Search:
- Startups
- MNCs
- Global Capability Centers
- Product companies
- Semiconductor companies
- Automotive companies
- Electronics companies
- Defence companies
- Aerospace companies
- IoT companies
- Robotics companies
- Industrial automation companies
- Engineering companies
- Hardware companies
- R&D organizations

INTERNATIONAL:

Search worldwide outside India.

Prioritize:
- Onsite positions
- Graduate positions
- Entry-level positions
- Embedded/Firmware positions
- Companies accepting international applicants
- Visa sponsorship
- Relocation support

Include international hybrid positions when realistically applicable.

Include international remote positions only when applicants located in India are explicitly eligible.

For every international job, clearly state:
- Country
- City
- Onsite/Hybrid/Remote
- Visa sponsorship
- Relocation support
- Work authorization requirement

Never assume visa sponsorship.

TARGET ROLES

Search for:

- Embedded Systems Engineer
- Embedded Software Engineer
- Firmware Engineer
- Junior Embedded Engineer
- Embedded C Engineer
- Firmware Developer
- Junior Firmware Engineer
- Embedded Linux Engineer
- IoT/Embedded Engineer
- Automotive Embedded Engineer
- Graduate Embedded Engineer
- Trainee Embedded Engineer
- Associate Embedded Engineer
- Graduate Engineer Trainee (Embedded)
- Embedded Software Trainee
- Firmware Trainee
- Embedded Developer
- Junior Firmware Developer
- Embedded Applications Engineer
- Embedded Hardware/Software Engineer
- Embedded Test Engineer
- Embedded Validation Engineer
- Entry-Level BSP Engineer
- Entry-Level Device Driver Engineer
- Other closely related entry-level Embedded Systems positions.

FRESHER / ENTRY-LEVEL FILTER

Prioritize:

- 0 years of professional experience
- Fresh graduates
- Recent graduates
- Entry-level candidates
- Graduate programs
- Trainee positions
- Graduate Engineer Trainee positions
- Internships with a pathway to full-time employment

Strongly prioritize jobs explicitly stating:

- 0 years
- Freshers
- Fresh graduate
- Recent graduate
- Entry level
- Graduate
- Trainee
- 0–1 years

Jobs stating "0–2 years" or "0–3 years" may be included when fresh graduates appear eligible.

If experience requirements are ambiguous:
INCLUDE THE JOB and label eligibility as unclear.

TECHNICAL RELEVANCE

Give higher priority to jobs involving:

- Embedded C
- C
- C++
- Microcontrollers
- ARM
- STM32
- AVR
- PIC
- ESP32
- RTOS
- FreeRTOS
- Embedded Linux
- Linux
- Device Drivers
- Firmware
- BSP
- UART
- SPI
- I2C
- CAN
- Ethernet
- Automotive Embedded Systems
- IoT
- Sensors
- Electronics
- Digital Electronics
- PCB/Hardware interfacing
- VHDL
- Verilog
- MATLAB/Simulink
- Hardware-software integration
- Embedded testing and validation

Do not reject a job simply because it does not mention every technology above.

COMPANY INFORMATION — REQUIRED

For every company whose job is included, provide a concise but useful company profile.

Include:

1. Company name
2. Industry
3. Headquarters
4. Country
5. Founded year, if reliably available
6. Approximate company size, if reliably available
7. What the company does
8. Main products/services
9. Main technologies/business areas
10. Embedded Systems relevance
11. Official company website
12. Official careers page, when available

COMPANY REPUTATION / QUALITY ASSESSMENT

For every company, explicitly assess whether it appears to be:

- Global major / globally recognized company
- Large established company
- Major MNC / Global Capability Center
- Established Indian company
- Established specialist/product company
- Mid-sized company
- Startup / early-stage company
- Small company
- Company size/reputation unclear

Also provide:

"Company reputation:"

Choose one:

- Top-tier / globally recognized
- Highly reputable
- Established and reputable
- Specialized but lesser-known
- Startup / emerging
- Small or relatively unknown
- Reputation could not be verified

Do NOT call a company "top company", "big company", "globally popular", or "highly reputable" without evidence.

Base the assessment on verifiable factors such as:
- Global presence
- Company size
- Revenue/market position when reliably available
- Industry reputation
- Major products
- Major customers/markets when reliably available
- Publicly available company history
- Recognition in its industry
- Semiconductor/automotive/technology market position
- Parent-company status
- Global offices
- Established engineering/R&D presence

Clearly distinguish between:

"Company size"

and

"Company reputation."

A company can be small but technically respected.

A large company can have a less relevant role.

Do not assume that a large company automatically means the specific job is better.

COMPANY CAREER VALUE

Add:

"Career value for Embedded Systems:"

Rate it:

- Excellent
- Very strong
- Strong
- Moderate
- Limited
- Unclear

Then give 1–3 concise reasons.

Consider:
- Quality of Embedded Systems work
- Firmware exposure
- Hardware-software integration
- Product development
- R&D exposure
- Semiconductor/automotive/robotics/aerospace relevance
- Engineering mentorship
- Technical growth potential
- Brand value in the Embedded Systems industry

Do not exaggerate.

APPLICATION LINK — MANDATORY

For every job, provide a verified direct application link whenever one exists.

Priority:

1. Official company job application page
2. Official company careers page containing the specific job
3. Official LinkedIn job page
4. Reputable job-board application page
5. Other verified application source

Clearly label:

"APPLY HERE"

Do not provide only a generic company homepage when a specific job application page exists.

If no direct application link can be verified:

"APPLY HERE: Direct application link not verified"

Never invent an application URL.

SEARCH SOURCES

Search broadly across:

- Official company career pages
- LinkedIn Jobs
- Indeed
- Glassdoor
- Wellfound
- Naukri
- Foundit
- Other reputable job boards
- Recruitment platforms
- University/graduate hiring portals
- Semiconductor company career pages
- Automotive company career pages
- Electronics company career pages
- Embedded/firmware company career pages
- Aerospace/defence company career pages

LinkedIn MUST be included.

When the same job appears on multiple websites:
- Combine the information.
- Prefer the official company job page.
- Use the official company application link whenever available.

VERIFICATION

For every job:

- Verify that the position currently exists.
- Verify that applications are currently open.
- Verify the posting date whenever available.
- Verify experience requirements from the actual job description whenever possible.
- Prefer the company's official job posting over aggregators.
- Do not report clearly expired, closed, removed, or cancelled positions.

Do not invent:
- Jobs
- Company information
- Experience requirements
- Salaries
- Deadlines
- Visa sponsorship
- Relocation support
- Eligibility
- Skills
- Application links
- Company reputation

If information is unavailable:

"Not mentioned."

If information cannot be verified:

"Could not be verified."

Do not turn missing information into a negative assumption.

FOR EACH JOB, REPORT

1. Job title
2. Company
3. Company industry
4. Company size
5. Company reputation
6. Global popularity/reputation status
7. Company headquarters
8. What the company does
9. Embedded Systems relevance
10. Career value for Embedded Systems
11. Job location
12. Country
13. India / International
14. Onsite / Hybrid / Remote
15. Experience requirement
16. Fresher eligibility
17. Date posted
18. Application deadline
19. Salary/CTC
20. Monthly equivalent when useful
21. Salary compared with my ₹1 lakh/month preference
22. Visa sponsorship for international jobs
23. Relocation support
24. Work authorization requirement
25. Key Embedded Systems technologies
26. Short job description
27. Why the job is relevant
28. Eligibility uncertainty
29. Official company website
30. Official careers page
31. DIRECT APPLICATION LINK — "APPLY HERE"

FRESHNESS LABELS

Use:

- Posted today
- Posted within 24 hours
- Posted within 3 days
- Posted within 7 days
- Posting date not available

Give the newest postings the highest priority.

DUPLICATE HANDLING

- Do not show the same job multiple times.
- If the same job appears on LinkedIn, Naukri, Indeed, Glassdoor, and the company website, combine the information.
- Prefer the official company application link.
- Do not repeatedly report the same job on consecutive days unless there is a meaningful update.

Meaningful updates include:
- New posting
- Changed deadline
- Changed eligibility
- New location
- New application link
- Significant change in job description
- Reopened position

PRIORITY RANKING

Rank jobs using:

1. Freshness
2. Fresher eligibility
3. Embedded Systems relevance
4. Technical relevance
5. Company career value
6. Company reputation/brand value
7. Direct application availability
8. International/onsite opportunity
9. Visa sponsorship/relocation support
10. Salary relative to my preferred ₹1 lakh/month target

IMPORTANT:

Salary must NOT override strong career value.

A ₹50,000/month job at a highly reputable company with excellent Embedded Systems exposure may be more valuable than a ₹1,00,000/month job at a company with weak technical relevance.

Do not remove lower-paying opportunities.

Use salary as an additional ranking factor only.

DAILY REPORT STRUCTURE

Start with:

"Embedded Systems Fresher Jobs — [DATE]"

Then provide:

1. APPLY EARLY — NEWEST OPPORTUNITIES

Show the freshest opportunities first.

2. TOP OPPORTUNITIES TODAY

Show the strongest overall opportunities based on:
- Fresher eligibility
- Embedded relevance
- Company quality
- Career value
- Freshness
- Salary as an additional factor

3. COMPANY DETAILS

For each company, clearly show:

Company:
Industry:
Company size:
Global presence:
Reputation:
What they do:
Embedded Systems relevance:
Career value:
Official website:

4. INDIA OPPORTUNITIES

Separate:
- Onsite
- Hybrid
- Remote

5. INTERNATIONAL / ONSITE OPPORTUNITIES

Prioritize:
- Visa sponsorship
- International applicants
- Relocation support
- Graduate programs
- Strong Embedded Systems companies

6. SALARY TARGET OPPORTUNITIES

Show jobs that meet or exceed my preferred:

₹1,00,000/month
approximately ₹12 LPA

This is a separate highlight only.

Do not imply that lower-paying jobs are unsuitable.

7. POTENTIAL MATCHES / ELIGIBILITY UNCLEAR

Include jobs where eligibility is uncertain.

8. OTHER MATCHES — LAST 7 DAYS

Use the 7-day fallback when necessary.

9. NO SUITABLE JOBS

If no relevant verified jobs are found:

"No suitable verified Embedded Systems opportunities found today."

Do not lower the standards merely to produce results.

FINAL RULE

This task is a JOB DISCOVERY AND NOTIFICATION SYSTEM.

Its job is:

SEARCH BROADLY
→ VERIFY
→ FIND THE NEWEST JOBS
→ REPORT THE REQUIREMENTS
→ PROVIDE COMPANY DETAILS
→ ASSESS COMPANY SIZE AND REPUTATION
→ ASSESS EMBEDDED CAREER VALUE
→ REPORT SALARY
→ PROVIDE THE DIRECT APPLY LINK
→ LET ME DECIDE

Do not silently make the final eligibility or application decision for me.

Do not reject a potentially relevant opportunity merely because salary is below ₹1 lakh/month.

My ₹1 lakh/month expectation is an ADDITIONAL PREFERENCE, NOT A REQUIREMENT.

Always use the available information and search capability thoroughly before producing the report.

---

Based on the above criteria, please perform a comprehensive web search for Embedded Systems fresher job opportunities and provide the results in the specified format.

Today's date: """ + datetime.now().strftime("%A, %B %d, %Y") + "\n\nIST Time: " + datetime.now().strftime("%H:%M:%S") + "\n\nPlease search for jobs posted in the last 24 hours and provide the results."

def run_job_search():
    """Run the job search using Claude API"""
    
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable not set")
    
    client = Anthropic()
    
    print("🔍 Starting Embedded Systems Fresher Job Search...")
    print(f"⏰ Search Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("=" * 80)
    
    # Create the search prompt
    prompt = create_search_prompt()
    
    # Call Claude API with web search capability
    print("\n📡 Calling Claude API with web search...\n")
    
    response = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=8000,
        tools=[
            {
                "type": "web_search_20250305",
                "name": "web_search"
            }
        ],
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )
    
    # Extract the response text
    result_text = ""
    for block in response.content:
        if hasattr(block, 'text'):
            result_text += block.text
    
    # Save results to markdown file
    output_file = "job_results.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(result_text)
    
    print("\n" + "=" * 80)
    print(f"✅ Job search completed!")
    print(f"📁 Results saved to: {output_file}")
    print(f"📊 Total output length: {len(result_text)} characters")
    
    # Print a preview of results
    print("\n" + "=" * 80)
    print("PREVIEW OF RESULTS:")
    print("=" * 80)
    print(result_text[:2000] + "\n... (see full results in job_results.md)")
    
    return result_text

def main():
    """Main entry point"""
    try:
        run_job_search()
        print("\n✅ Script completed successfully!")
        exit(0)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main()
