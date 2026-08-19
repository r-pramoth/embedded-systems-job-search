#!/usr/bin/env python3

import html
import json
import os
import re
import sys
import time
import traceback

from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from urllib.parse import quote, urlparse
from urllib.request import Request, urlopen
from xml.etree import ElementTree


IST = timezone(timedelta(hours=5, minutes=30))

OUTPUT_FILE = "job_results.md"

PRIORITY_COMPANIES = [
    "HARMAN",
    "Samsung",
    "Bosch",
    "Continental",
    "NXP",
    "Texas Instruments",
    "Qualcomm",
    "Intel",
    "AMD",
    "NVIDIA",
    "Microchip",
    "STMicroelectronics",
    "Infineon",
    "Renesas",
    "MediaTek",
    "Siemens",
    "ABB",
    "Schneider Electric",
    "Honeywell",
    "GE",
    "Eaton",
    "Valeo",
    "Aptiv",
    "ZF",
    "Visteon",
    "Tata Elxsi",
    "LTTS",
    "KPIT",
    "Wipro",
]

SEARCH_QUERIES = [
    '"embedded software engineer" fresher India',
    '"embedded systems engineer" fresher India',
    '"embedded engineer" fresher India',
    '"firmware engineer" fresher India',
    '"embedded C" fresher India',
    '"firmware developer" fresher India',
    '"embedded linux" fresher India',
    '"embedded software" "0-2 years" India',
    '"embedded" "graduate engineer trainee" India',
    '"embedded" "trainee engineer" India',
    '"embedded" "entry level" India',
    '"embedded" "0 years" India',

    '"embedded software engineer" fresher Bangalore',
    '"embedded systems engineer" fresher Bangalore',
    '"firmware engineer" fresher Bangalore',
    '"embedded C" fresher Bangalore',
    '"embedded linux" fresher Bangalore',
    '"firmware" "graduate engineer trainee" Bangalore',

    '"embedded software engineer" fresher Chennai',
    '"embedded systems engineer" fresher Chennai',
    '"firmware engineer" fresher Chennai',

    '"embedded software engineer" fresher Hyderabad',
    '"embedded systems engineer" fresher Hyderabad',
    '"firmware engineer" fresher Hyderabad',

    '"embedded software engineer" fresher Pune',
    '"embedded systems engineer" fresher Pune',
    '"firmware engineer" fresher Pune',

    '"automotive embedded" fresher India',
    '"automotive firmware" fresher India',
    '"AUTOSAR" fresher India',
    '"CAN" embedded fresher India',
    '"FreeRTOS" fresher India',
    '"RTOS" embedded fresher India',
    '"embedded Linux" graduate India',
    '"device driver" fresher India',
    '"BSP" embedded fresher India',

    '"embedded software engineer" graduate jobs',
    '"embedded systems engineer" graduate jobs',
    '"firmware engineer" graduate jobs',
    '"embedded engineer" entry level jobs',
]


for company in PRIORITY_COMPANIES:
    SEARCH_QUERIES.extend(
        [
            f'"{company}" embedded fresher',
            f'"{company}" embedded engineer graduate',
            f'"{company}" firmware fresher',
            f'"{company}" embedded software engineer entry level',
        ]
    )


EMBEDDED_KEYWORDS = [
    "embedded",
    "firmware",
    "microcontroller",
    "mcu",
    "embedded software",
    "embedded systems",
    "embedded c",
    "embedded c++",
    "rtos",
    "freertos",
    "embedded linux",
    "device driver",
    "bsp",
    "bootloader",
    "arm cortex",
    "stm32",
    "esp32",
    "avr",
    "pic",
    "uart",
    "spi",
    "i2c",
    "can bus",
    "can fd",
    "autosar",
    "iot",
    "firmware development",
    "board bring-up",
]

FRESHER_KEYWORDS = [
    "fresher",
    "fresh graduate",
    "recent graduate",
    "graduate",
    "entry level",
    "entry-level",
    "trainee",
    "graduate engineer trainee",
    "get",
    "0 years",
    "0-1 years",
    "0–1 years",
    "0-2 years",
    "0–2 years",
    "0-3 years",
    "0–3 years",
    "junior",
    "associate",
    "intern",
]

SENIOR_KEYWORDS = [
    "senior engineer",
    "senior software engineer",
    "lead engineer",
    "principal engineer",
    "staff engineer",
    "architect",
    "engineering manager",
    "technical manager",
    "director",
]

INDIA_LOCATIONS = [
    "bangalore",
    "bengaluru",
    "chennai",
    "hyderabad",
    "pune",
    "mumbai",
    "noida",
    "gurgaon",
    "gurugram",
    "delhi",
    "ahmedabad",
    "coimbatore",
    "mysore",
    "mysuru",
    "kochi",
    "trivandrum",
    "thiruvananthapuram",
    "kolkata",
]


def clean_text(value):
    value = html.unescape(value or "")
    value = re.sub(r"<[^>]+>", " ", value)
    value = re.sub(r"\s+", " ", value)

    return value.strip()


def fetch_url(url, timeout=20):
    request = Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 "
                "(compatible; EmbeddedJobSearch/1.0)"
            )
        },
    )

    with urlopen(request, timeout=timeout) as response:
        content_type = response.headers.get(
            "Content-Type",
            "",
        )

        data = response.read()

        charset = "utf-8"

        match = re.search(
            r"charset=([A-Za-z0-9._-]+)",
            content_type,
            re.IGNORECASE,
        )

        if match:
            charset = match.group(1)

        return data.decode(
            charset,
            errors="replace",
        )


def google_news_search(query):
    encoded_query = quote(query)

    url = (
        "https://news.google.com/rss/search?"
        f"q={encoded_query}"
        "&hl=en-IN"
        "&gl=IN"
        "&ceid=IN:en"
    )

    try:
        xml_data = fetch_url(url)

        root = ElementTree.fromstring(xml_data)

        results = []

        for item in root.findall(".//item"):
            title = item.findtext("title") or ""
            link = item.findtext("link") or ""
            description = item.findtext("description") or ""
            pub_date = item.findtext("pubDate") or ""
            source = item.findtext("source") or ""

            results.append(
                {
                    "title": clean_text(title),
                    "url": link.strip(),
                    "description": clean_text(description),
                    "published": pub_date,
                    "source": clean_text(source),
                    "query": query,
                }
            )

        return results

    except Exception as exc:
        print(
            f"Search failed for '{query}': {exc}",
            file=sys.stderr,
        )

        return []


def parse_date(date_string):
    if not date_string:
        return None

    try:
        return parsedate_to_datetime(
            date_string
        ).astimezone(IST)

    except Exception:
        return None


def freshness_label(published):
    if not published:
        return "Posting date not available"

    age = datetime.now(IST) - published

    if age <= timedelta(hours=24):
        return "Posted within 24 hours"

    if age <= timedelta(days=3):
        return "Posted within 3 days"

    if age <= timedelta(days=7):
        return "Posted within 7 days"

    return "Older than 7 days"


def extract_company(title, description, source):
    text = f"{title} {description} {source}"
    lowered = text.lower()

    for company in PRIORITY_COMPANIES:
        if company.lower() in lowered:
            return company

    if source:
        return source

    return "Company not identified"


def extract_location(text):
    lowered = text.lower()

    for location in INDIA_LOCATIONS:
        if location in lowered:

            if location in ("bangalore", "bengaluru"):
                return "Bengaluru, India"

            return location.title() + ", India"

    international_locations = [
        "germany",
        "united states",
        "usa",
        "canada",
        "uk",
        "united kingdom",
        "ireland",
        "netherlands",
        "france",
        "sweden",
        "singapore",
        "japan",
        "australia",
    ]

    for location in international_locations:
        if location in lowered:
            return location.title()

    return "Location not verified"


def extract_salary(text):
    patterns = [
        r"₹\s?[\d,]+\s?(?:lpa|lakh|lakhs)",
        r"₹\s?[\d,]+\s?(?:per month|/month)",
        r"\b\d+(?:\.\d+)?\s?LPA\b",
        r"\b\d+(?:\.\d+)?\s?lakhs?\b",
        r"\$\s?[\d,]+",
    ]

    for pattern in patterns:
        match = re.search(
            pattern,
            text,
            re.IGNORECASE,
        )

        if match:
            return match.group(0)

    return "Not disclosed"


def find_experience(text):
    patterns = [
        r"\b0\s*[-–]\s*1\s*years?\b",
        r"\b0\s*[-–]\s*2\s*years?\b",
        r"\b0\s*[-–]\s*3\s*years?\b",
        r"\b0\s*[-–]\s*4\s*years?\b",
        r"\b1\s*[-–]\s*2\s*years?\b",
        r"\b1\s*[-–]\s*3\s*years?\b",
        r"\b\d+\+?\s*years?\b",
        r"\bfreshers?\b",
        r"\bentry[- ]level\b",
        r"\bgraduate\b",
        r"\btrainee\b",
    ]

    for pattern in patterns:
        match = re.search(
            pattern,
            text,
            re.IGNORECASE,
        )

        if match:
            return match.group(0)

    return "Not mentioned"


def technical_matches(text):
    lowered = text.lower()

    matches = []

    for keyword in EMBEDDED_KEYWORDS:
        if keyword in lowered:
            matches.append(keyword)

    return list(dict.fromkeys(matches))


def is_embedded_related(text):
    lowered = text.lower()

    return any(
        keyword in lowered
        for keyword in EMBEDDED_KEYWORDS
    )


def is_fresher_relevant(text):
    lowered = text.lower()

    return any(
        keyword in lowered
        for keyword in FRESHER_KEYWORDS
    )


def is_clearly_senior(text):
    lowered = text.lower()

    for keyword in SENIOR_KEYWORDS:
        if keyword in lowered:
            return True

    experience_matches = re.findall(
        r"\b([2-9]|1[0-9])\+?\s*years?\b",
        lowered,
    )

    for value in experience_matches:
        if int(value) >= 2:
            return True

    return False


def company_quality(company):
    if company in PRIORITY_COMPANIES:
        return 25

    return 0


def score_result(result):
    text = (
        f"{result['title']} "
        f"{result['description']}"
    ).lower()

    score = 0

    embedded = technical_matches(text)

    score += min(
        len(embedded) * 3,
        30,
    )

    if is_fresher_relevant(text):
        score += 25

    if (
        "bengaluru" in text
        or "bangalore" in text
    ):
        score += 15

    score += company_quality(
        result["company"]
    )

    if "firmware" in text:
        score += 5

    if "embedded c" in text:
        score += 5

    if "rtos" in text:
        score += 5

    if "embedded linux" in text:
        score += 5

    if "graduate engineer trainee" in text:
        score += 10

    if "internship" in text:
        score += 5

    if is_clearly_senior(text):
        score -= 40

    published = result.get(
        "published_datetime"
    )

    if published:
        age = (
            datetime.now(IST)
            - published
        )

        if age <= timedelta(hours=24):
            score += 20

        elif age <= timedelta(days=3):
            score += 10

        elif age <= timedelta(days=7):
            score += 5

    return score


def normalize_url(url):
    if not url:
        return ""

    parsed = urlparse(url)

    return (
        parsed.scheme.lower(),
        parsed.netloc.lower(),
        parsed.path.rstrip("/"),
    )


def deduplicate(results):
    unique = {}

    for result in results:
        key = normalize_url(
            result["url"]
        )

        if not key:
            key = (
                result["title"].lower(),
                result["company"].lower(),
            )

        if key not in unique:
            unique[key] = result

    return list(unique.values())


def enrich_result(result):
    page_text = ""

    try:
        page_text = clean_text(
            fetch_url(result["url"])
        )

        page_text = page_text[:30000]

    except Exception as exc:
        print(
            f"Could not fetch "
            f"{result['url']}: {exc}",
            file=sys.stderr,
        )

    combined = (
        result["title"]
        + " "
        + result["description"]
        + " "
        + page_text
    )

    result["page_text"] = page_text

    result["location"] = extract_location(
        combined
    )

    result["salary"] = extract_salary(
        combined
    )

    result["experience"] = find_experience(
        combined
    )

    result["technical_matches"] = (
        technical_matches(combined)
    )

    result["embedded_relevant"] = (
        is_embedded_related(combined)
    )

    result["fresher_relevant"] = (
        is_fresher_relevant(combined)
    )

    result["senior"] = is_clearly_senior(
        combined
    )

    result["freshness"] = freshness_label(
        result["published_datetime"]
    )

    result["score"] = score_result(
        result
    )

    return result


def search_all():
    print("=" * 80)
    print("Embedded Systems Fresher Job Search")
    print("=" * 80)

    print(
        "Search time:",
        datetime.now(IST).strftime(
            "%Y-%m-%d %H:%M:%S IST"
        ),
    )

    all_results = []

    for index, query in enumerate(
        SEARCH_QUERIES,
        start=1,
    ):
        print(
            f"[{index}/{len(SEARCH_QUERIES)}] "
            f"{query}"
        )

        all_results.extend(
            google_news_search(query)
        )

        time.sleep(0.3)

    print(
        f"Raw results: {len(all_results)}"
    )

    return all_results


def prepare_results(results):
    prepared = []

    for result in results:

        if not result.get("url"):
            continue

        result["published_datetime"] = (
            parse_date(
                result.get(
                    "published",
                    "",
                )
            )
        )

        result["company"] = (
            extract_company(
                result["title"],
                result["description"],
                result["source"],
            )
        )

        prepared.append(result)

    prepared = deduplicate(prepared)

    print(
        f"Unique results: {len(prepared)}"
    )

    enriched = []

    for index, result in enumerate(
        prepared,
        start=1,
    ):
        print(
            f"Checking result "
            f"{index}/{len(prepared)}: "
            f"{result['title'][:80]}"
        )

        try:
            result = enrich_result(result)

            if not result["embedded_relevant"]:
                continue

            if result["senior"]:
                continue

            enriched.append(result)

        except Exception as exc:
            print(
                f"Enrichment failed: {exc}",
                file=sys.stderr,
            )

    enriched.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    return enriched


def company_reputation(company):
    if company in PRIORITY_COMPANIES:
        return (
            "Major / established company; "
            "priority company in this search"
        )

    return (
        "Company reputation requires "
        "individual verification"
    )


def career_value(result):
    count = len(
        result["technical_matches"]
    )

    if count >= 6:
        return "Very strong"

    if count >= 3:
        return "Strong"

    if count >= 1:
        return "Moderate"

    return "Unclear"


def job_markdown(result, number):
    published = result.get(
        "published_datetime"
    )

    if published:
        posted = published.strftime(
            "%Y-%m-%d %H:%M IST"
        )
    else:
        posted = "Not available"

    technical = ", ".join(
        result["technical_matches"][:15]
    )

    if not technical:
        technical = "Not identified"

    description = result["description"]

    if not description:
        description = (
            "Job description could not "
            "be fully extracted."
        )

    return (
        f"### {number}. {result['title']}\n\n"
        f"**Company:** {result['company']}\n\n"
        f"**Company size/reputation:** "
        f"{company_reputation(result['company'])}\n\n"
        f"**Location:** {result['location']}\n\n"
        f"**Experience requirement:** "
        f"{result['experience']}\n\n"
        f"**Fresher relevance:** "
        f"{'Potentially suitable' if result['fresher_relevant'] else 'Eligibility unclear'}\n\n"
        f"**Posted:** {posted}\n\n"
        f"**Freshness:** {result['freshness']}\n\n"
        f"**Salary:** {result['salary']}\n\n"
        f"**Embedded Systems relevance:** "
        f"{'Yes' if result['embedded_relevant'] else 'Unclear'}\n\n"
        f"**Career value:** "
        f"{career_value(result)}\n\n"
        f"**Key technologies:** {technical}\n\n"
        f"**Source:** {result['source']}\n\n"
        f"**APPLY HERE:** {result['url']}\n\n"
        f"**Job description/source summary:**\n\n"
        f"{description[:1500]}\n"
    )


def create_report(results):
    now = datetime.now(IST)

    report = []

    report.append(
        "# Embedded Systems Fresher Jobs — "
        + now.strftime("%B %d, %Y")
    )

    report.append("")

    report.append(
        f"Search time: "
        f"{now.strftime('%Y-%m-%d %H:%M:%S IST')}"
    )

    report.append("")

    report.append(
        "> Automated Embedded Systems job discovery."
    )

    report.append("")

    report.append(
        "## Priority Companies"
    )

    report.append("")

    for company in PRIORITY_COMPANIES:
        found = sum(
            1
            for result in results
            if result["company"] == company
        )

        report.append(
            f"- **{company}** — "
            f"{found} result(s)"
        )

    report.append("")

    report.append(
        "## Top Opportunities"
    )

    report.append("")

    if not results:
        report.append(
            "No suitable Embedded Systems "
            "fresher opportunities were found."
        )

    else:
        for index, result in enumerate(
            results[:30],
            start=1,
        ):
            report.append(
                job_markdown(
                    result,
                    index,
                )
            )

    report.append("")

    report.append(
        "## Verification Note"
    )

    report.append("")

    report.append(
        "Open the application link and verify "
        "the current job description, eligibility, "
        "location, salary, and application status "
        "before applying."
    )

    return "\n".join(report)


def telegram_escape(text):
    """
    Convert normal text to safe Telegram HTML.
    """

    return html.escape(
        text,
        quote=False,
    )


def markdown_to_telegram_html(markdown):
    """
    Convert the report's basic Markdown formatting
    into Telegram HTML.

    This prevents literal * characters from appearing
    in Telegram messages.
    """

    text = markdown

    # Escape HTML first.
    text = telegram_escape(text)

    # Headings.
    text = re.sub(
        r"^### (.+)$",
        r"<b>\1</b>",
        text,
        flags=re.MULTILINE,
    )

    text = re.sub(
        r"^## (.+)$",
        r"<b>\1</b>",
        text,
        flags=re.MULTILINE,
    )

    text = re.sub(
        r"^# (.+)$",
        r"<b>\1</b>",
        text,
        flags=re.MULTILINE,
    )

    # Bold Markdown.
    text = re.sub(
        r"\*\*(.+?)\*\*",
        r"<b>\1</b>",
        text,
    )

    # Markdown blockquote.
    text = re.sub(
        r"^&gt; (.+)$",
        r"<i>\1</i>",
        text,
        flags=re.MULTILINE,
    )

    # Remove remaining Markdown emphasis characters.
    text = text.replace(
        "**",
        "",
    )

    return text.strip()


def split_telegram_message(text, max_length=3800):
    """
    Split long Telegram messages while keeping
    each message below Telegram's size limit.
    """

    chunks = []

    while len(text) > max_length:

        split_at = text.rfind(
            "\n",
            0,
            max_length,
        )

        if split_at <= 0:
            split_at = max_length

        chunks.append(
            text[:split_at]
        )

        text = text[split_at:].lstrip()

    if text:
        chunks.append(text)

    return chunks


def send_telegram_message(message):
    bot_token = os.environ.get(
        "TELEGRAM_BOT_TOKEN"
    )

    chat_id = os.environ.get(
        "TELEGRAM_CHAT_ID"
    )

    if not bot_token:
        print(
            "TELEGRAM_BOT_TOKEN is not configured.",
            file=sys.stderr,
        )
        return

    if not chat_id:
        print(
            "TELEGRAM_CHAT_ID is not configured.",
            file=sys.stderr,
        )
        return

    telegram_message = (
        markdown_to_telegram_html(message)
    )

    chunks = split_telegram_message(
        telegram_message
    )

    url = (
        "https://api.telegram.org/bot"
        f"{bot_token}/sendMessage"
    )

    for index, chunk in enumerate(
        chunks,
        start=1,
    ):
        payload = json.dumps(
            {
                "chat_id": chat_id,
                "text": chunk,
                "parse_mode": "HTML",
                "disable_web_page_preview": True,
            }
        ).encode("utf-8")

        request = Request(
            url,
            data=payload,
            headers={
                "Content-Type": "application/json"
            },
            method="POST",
        )

        try:
            with urlopen(
                request,
                timeout=30,
            ) as response:

                response_data = response.read().decode(
                    "utf-8",
                    errors="replace",
                )

                telegram_result = json.loads(
                    response_data
                )

                if not telegram_result.get("ok"):
                    raise RuntimeError(
                        "Telegram API error: "
                        + response_data
                    )

        except Exception as exc:
            print(
                f"Telegram message {index} failed: {exc}",
                file=sys.stderr,
            )
            raise

        print(
            f"Telegram message "
            f"{index}/{len(chunks)} sent."
        )


def write_failure(error):
    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8",
    ) as file:

        file.write(
            "# Embedded Systems "
            "Job Search — FAILED\n\n"
        )

        file.write(
            f"Error: {error}\n\n"
        )

        file.write(
            "## Traceback\n\n"
        )

        file.write(
            "```text\n"
        )

        file.write(
            traceback.format_exc()
        )

        file.write(
            "\n```\n"
        )


def main():
    try:
        print(
            "Starting Embedded Systems "
            "job search..."
        )

        raw_results = search_all()

        results = prepare_results(
            raw_results
        )

        report = create_report(
            results
        )

        with open(
            OUTPUT_FILE,
            "w",
            encoding="utf-8",
        ) as file:

            file.write(report)

        send_telegram_message(
            report
        )

        print(
            f"Job search completed. "
            f"Results: {len(results)}"
        )

        return 0

    except Exception as exc:

        print(
            f"Job search failed: {exc}",
            file=sys.stderr,
        )

        write_failure(
            str(exc)
        )

        return 1


if __name__ == "__main__":
    sys.exit(main())
