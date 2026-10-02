"""UI-state isolation checks; no Streamlit runtime or S8 dataset required."""

import ast
import unittest
from pathlib import Path

from app.session_keys import case_key


class CaseSessionKeyTests(unittest.TestCase):
    def test_key_is_stable_for_the_same_operator_case_and_field(self):
        self.assertEqual(
            case_key("caseworker-01", "sentinel-001", "opened"),
            case_key("caseworker-01", "sentinel-001", "opened"),
        )

    def test_shared_sentinel_has_independent_state_for_each_operator(self):
        session = {
            case_key("caseworker-01", "sentinel-001", "opened"): "09:00",
            case_key("caseworker-01", "sentinel-001", "revealed"): True,
            case_key("caseworker-01", "sentinel-001", "own"): "High",
        }
        for field in ("opened", "revealed", "own"):
            self.assertNotIn(case_key("caseworker-02", "sentinel-001", field), session)
        session[case_key("caseworker-02", "sentinel-001", "opened")] = "10:00"
        self.assertEqual(
            session[case_key("caseworker-01", "sentinel-001", "opened")], "09:00"
        )

    def test_widget_answers_do_not_cross_operators(self):
        for field in ("reasoning", "answer", "decision", "justification"):
            self.assertNotEqual(
                case_key("caseworker-01", "sentinel-001", field),
                case_key("caseworker-02", "sentinel-001", field),
            )

    def test_preliminary_category_does_not_cross_cases(self):
        self.assertNotEqual(
            case_key("caseworker-01", "case-001", "preliminary_category"),
            case_key("caseworker-01", "case-002", "preliminary_category"),
        )

    def test_fields_are_distinct(self):
        fields = ("opened", "revealed", "own", "preliminary_category", "justification")
        keys = {case_key("caseworker-01", "case-001", field) for field in fields}
        self.assertEqual(len(keys), len(fields))

    def test_component_boundaries_cannot_collide(self):
        self.assertNotEqual(
            case_key("a-b", "c", "opened"), case_key("a", "b-c", "opened")
        )
        self.assertNotEqual(
            case_key("a:b", "c", "opened"), case_key("a", "b:c", "opened")
        )

    def test_caseworker_page_scopes_all_case_state_fields(self):
        source = Path(__file__).resolve().parents[1] / "app" / "caseworker.py"
        calls = [
            node
            for node in ast.walk(ast.parse(source.read_text(encoding="utf-8")))
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "case_key"
        ]
        self.assertEqual(
            {call.args[2].value for call in calls},
            {
                "opened",
                "revealed",
                "initial_decision",
                "initial_justification",
                "reasoning",
                "answer",
                "decision",
                "justification",
            },
        )
        for call in calls:
            self.assertEqual(call.args[0].id, "caseworker")
            self.assertEqual(call.args[1].id, "case_id")


if __name__ == "__main__":
    unittest.main()
