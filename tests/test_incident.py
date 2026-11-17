import sqlite3
import unittest
from pathlib import Path

from app.incident import COHORT_SQL, validate_brief

ROOT = Path(__file__).resolve().parents[1]


class IncidentTest(unittest.TestCase):
    def test_seed_reproduces_incident(self):
        setup = (ROOT / "sql/01_setup.sql").read_text()
        seed = (ROOT / "sql/02_seed.sql").read_text()
        with sqlite3.connect(":memory:") as connection:
            connection.executescript(setup[setup.index("CREATE TABLE"):])
            connection.executescript(seed[seed.index("BEGIN;"):])
            query = COHORT_SQL.replace("LAUNCH_MYSTERY.DEMO.", "")
            connection.row_factory = sqlite3.Row
            rows = connection.execute(query).fetchall()

        self.assertEqual(len(rows), 8)
        totals = {
            phase: sum(row["ORDERS"] for row in rows if row["RELEASE_PHASE"] == phase)
            for phase in ("Before", "After")
        }
        self.assertEqual(totals, {"Before": 1000, "After": 820})
        sessions = [
            sum(row["SESSIONS"] for row in rows if row["RELEASE_PHASE"] == phase)
            for phase in ("Before", "After")
        ]
        self.assertEqual(sessions, [7000, 7000])
        self.assertEqual([row["COMPLETION_PCT"] for row in rows if row["COHORT"] == "Rollout"], [60, 24])
        self.assertEqual([row["COMPLETION_PCT"] for row in rows if row["COHORT"] == "Holdout"], [60.6, 60.6])

    def test_quote_must_exist_under_cited_document_id(self):
        notes = [{"DOC_ID": "PAY-017", "BODY": "First affected at 11:20 UTC."}]
        output = {
            "assessment": "The provider alert came later.",
            "next_check": "Review the rollout.",
            "citations": [{"doc_id": "PAY-017", "quote": "11:20 UTC"}],
        }
        self.assertEqual(validate_brief(output, notes, requires_citation=True), output)
        output["citations"][0]["quote"] = "10:20 UTC"
        with self.assertRaisesRegex(ValueError, "could not be verified"):
            validate_brief(output, notes)

    def test_abstention_can_have_no_citation(self):
        output = {"assessment": "The commit is unknown.", "next_check": "Check Git.", "citations": []}
        self.assertEqual(validate_brief(output, []), output)
        with self.assertRaisesRegex(ValueError, "required source quotes"):
            validate_brief(output, [], requires_citation=True)
