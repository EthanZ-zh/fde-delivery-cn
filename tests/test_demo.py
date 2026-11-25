import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


DEMO = Path(__file__).resolve().parents[1] / "examples" / "ticket-triage" / "demo.py"


class TicketTriageDemoTests(unittest.TestCase):
    def run_demo(self, scenario, decision=None):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "run"
            args = [sys.executable, "-X", "utf8", str(DEMO), "--scenario", scenario, "--out", str(output)]
            if decision is not None:
                args.extend(["--decision", decision])
            run = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", timeout=10)
            self.assertEqual(run.returncode, 0, run.stderr)
            return json.loads((output / "evidence.json").read_text(encoding="utf-8"))

    def test_default_waits_for_confirmation_without_routing(self):
        evidence = self.run_demo("normal")
        self.assertEqual(evidence["ticket_id"], "DEMO-1042")
        self.assertEqual(evidence["suggested_queue"], "IT 支持")
        self.assertEqual(evidence["requested_decision"], "pending")
        self.assertEqual(evidence["status"], "awaiting_confirmation")
        self.assertIsNone(evidence["final_queue"])
        self.assertEqual(evidence["events"], ["suggested", "awaiting_confirmation"])

    def test_approval_records_decision_before_simulated_routing(self):
        evidence = self.run_demo("normal", "approve")
        self.assertIs(evidence["simulated"], True)
        self.assertEqual(evidence["final_queue"], "IT 支持")
        self.assertEqual(evidence["requested_decision"], "approve")
        self.assertTrue(evidence["reason"])
        self.assertEqual(evidence["status"], "routed")
        self.assertEqual(evidence["events"], ["suggested", "approved", "routed"])

    def test_rejection_preserves_manual_handling(self):
        evidence = self.run_demo("normal", "reject")
        self.assertEqual(evidence["suggested_queue"], "IT 支持")
        self.assertIsNone(evidence["final_queue"])
        self.assertEqual(evidence["status"], "manual_review")
        self.assertEqual(evidence["reason_code"], "operator_rejected")
        self.assertEqual(evidence["events"], ["suggested", "rejected", "manual_review"])

    def test_offline_falls_back_even_if_approval_is_requested(self):
        evidence = self.run_demo("offline", "approve")
        self.assertIsNone(evidence["suggested_queue"])
        self.assertIsNone(evidence["final_queue"])
        self.assertEqual(evidence["status"], "manual_review")
        self.assertEqual(evidence["reason_code"], "simulated_model_unavailable")
        self.assertEqual(evidence["events"], ["model_unavailable", "manual_review"])

    def test_unknown_category_falls_back_even_if_approval_is_requested(self):
        evidence = self.run_demo("unknown", "approve")
        self.assertIsNone(evidence["suggested_queue"])
        self.assertIsNone(evidence["final_queue"])
        self.assertEqual(evidence["status"], "manual_review")
        self.assertEqual(evidence["reason_code"], "unknown_category")
        self.assertEqual(evidence["events"], ["unknown_category", "manual_review"])


if __name__ == "__main__":
    unittest.main()
