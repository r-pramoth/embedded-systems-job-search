"""Offline regression tests using fictional fixtures, never live vacancies."""

import contextlib
import io
import unittest
from unittest.mock import patch

from scripts import job_search


def setUpModule():
    # Fail closed if a test accidentally tries to contact any external service.
    global network_guard
    network_guard = patch.object(
        job_search,
        "urlopen",
        side_effect=AssertionError("Tests must not make network requests"),
    )
    network_guard.start()


def tearDownModule():
    network_guard.stop()


def candidate(title, description, slug):
    return {
        "title": title,
        "description": description,
        "url": f"https://example.invalid/{slug}",
        "source": "Fictional Careers Bulletin",
        "published": "Mon, 05 Jan 2026 10:00:00 +0000",
        "query": "fictional regression fixture",
    }


class ExperienceRegressionTests(unittest.TestCase):
    def test_ranges_starting_at_zero_are_not_senior(self):
        for experience in (
            "0-1 years",
            "0-2 years",
            "0–3 years",
            "0—4 years",
            "0 to 2 years",
            "0 - 2 yrs",
        ):
            with self.subTest(experience=experience):
                self.assertFalse(
                    job_search.is_clearly_senior(
                        f"Firmware trainee: {experience} of experience"
                    )
                )

    def test_range_uses_minimum_experience(self):
        self.assertFalse(job_search.is_clearly_senior("1–3 years"))
        self.assertTrue(job_search.is_clearly_senior("2–3 years"))

    def test_explicit_experienced_requirements_are_senior(self):
        for experience in (
            "2 years",
            "3+ years",
            "5–8 years",
            "20 years",
            "2.5 years",
            "2 yrs",
        ):
            with self.subTest(experience=experience):
                self.assertTrue(job_search.is_clearly_senior(experience))

    def test_architecture_does_not_mean_architect(self):
        self.assertFalse(
            job_search.is_clearly_senior(
                "Graduate firmware engineer studying ARM architecture"
            )
        )

    def test_senior_job_labels_still_match(self):
        for title in ("Senior Engineer", "Principal Engineer", "System Architect"):
            with self.subTest(title=title):
                self.assertTrue(job_search.is_clearly_senior(title))


class KeywordRegressionTests(unittest.TestCase):
    def test_unrelated_words_do_not_match_embedded_keywords(self):
        self.assertEqual(
            job_search.technical_matches(
                "Hospital topics and inspiration for an editorial article"
            ),
            [],
        )

    def test_real_embedded_terms_still_match(self):
        matches = job_search.technical_matches(
            "Embedded C++, UART, SPI/I2C and ARM Cortex"
        )
        self.assertTrue(
            {"embedded c++", "uart", "spi", "i2c", "arm cortex"}.issubset(matches)
        )

    def test_target_does_not_match_get_trainee_abbreviation(self):
        self.assertFalse(
            job_search.is_fresher_relevant("Firmware target platform development")
        )

    def test_fresher_terms_still_match(self):
        for title in ("Graduate engineer trainee", "GET hiring", "Entry-level role"):
            with self.subTest(title=title):
                self.assertTrue(job_search.is_fresher_relevant(title))

    def test_company_names_do_not_match_unrelated_words(self):
        self.assertEqual(
            job_search.extract_company(
                "Intelligent monitoring", "Knowledge management", ""
            ),
            "Company not identified",
        )

    def test_source_publisher_is_not_assumed_to_be_the_employer(self):
        self.assertEqual(
            job_search.extract_company(
                "Firmware trainee", "Embedded role", "Fictional Careers Bulletin"
            ),
            "Company not identified",
        )

    def test_known_company_names_still_match(self):
        for company in ("Intel", "GE", "NXP", "Texas Instruments"):
            with self.subTest(company=company):
                self.assertEqual(
                    job_search.extract_company(
                        f"{company}: Firmware trainee", "", ""
                    ),
                    company,
                )

    def test_country_abbreviation_does_not_match_inside_a_name(self):
        self.assertEqual(
            job_search.extract_location("Sukumar announced a firmware opening"),
            "Location not verified",
        )

    def test_real_locations_still_match(self):
        self.assertEqual(
            job_search.extract_location("Graduate firmware engineer, Bengaluru"),
            "Bengaluru, India",
        )
        self.assertEqual(
            job_search.extract_location("Firmware graduate in the UK"),
            "Uk",
        )


class PipelineRegressionTests(unittest.TestCase):
    def test_pipeline_keeps_zero_experience_range_and_rejects_other_roles(self):
        fixtures = [
            candidate(
                "Firmware trainee",
                "0–2 years; ARM Cortex, UART and SPI.",
                "trainee",
            ),
            candidate(
                "Firmware engineer",
                "3–5 years of embedded experience.",
                "experienced",
            ),
            candidate(
                "Editorial assistant",
                "0–1 years; topics for hospital management.",
                "unrelated",
            ),
        ]
        with patch.object(job_search, "fetch_url", return_value=""):
            with contextlib.redirect_stdout(io.StringIO()):
                results = job_search.prepare_results(fixtures)

        self.assertEqual(
            [result["url"] for result in results],
            ["https://example.invalid/trainee"],
        )
        self.assertTrue(results[0]["fresher_relevant"])
        self.assertEqual(results[0]["experience"], "0–2 years")
        self.assertEqual(results[0]["company"], "Company not identified")
        self.assertEqual(results[0]["source"], "Fictional Careers Bulletin")

        report = job_search.create_report(results)
        self.assertIn("https://example.invalid/trainee", report)
        self.assertNotIn("https://example.invalid/experienced", report)
        self.assertNotIn("https://example.invalid/unrelated", report)

    def test_rss_parsing_uses_mocked_response(self):
        rss = """<rss><channel><item>
        <title>Firmware trainee &amp; graduate role</title>
        <link>https://example.invalid/fixture</link>
        <description>&lt;p&gt;Embedded C &amp; UART&lt;/p&gt;</description>
        <source>Fictional Careers Bulletin</source>
        <pubDate>Mon, 05 Jan 2026 10:00:00 +0000</pubDate>
        </item></channel></rss>"""

        with patch.object(job_search, "fetch_url", return_value=rss) as fetch:
            results = job_search.google_news_search("fictional fixture")

        fetch.assert_called_once()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "Firmware trainee & graduate role")
        self.assertEqual(results[0]["description"], "Embedded C & UART")
        self.assertEqual(results[0]["url"], "https://example.invalid/fixture")


if __name__ == "__main__":
    unittest.main()
