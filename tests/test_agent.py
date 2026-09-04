import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.llm.gemeni import get_agent_decision
from app.servicenow.service_now import build_update_payload


def run_tests():
    test_file = Path(__file__).resolve().parent / "test_incidents.json"
    with open(test_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    print("\nTesting 3 Official Incidents against Gemini Agent:\n")

    all_passed = True

    for i, inc in enumerate(data.get("incidents", []), start=1):
        decision = get_agent_decision(inc["short_description"], inc["description"])
        expected = inc["expected_decision"]
        passed = decision.decision == expected

        if not passed:
            all_passed = False

        status = "PASS" if passed else "FAIL"
        print(f"[{status}] Ticket {i}: {inc['short_description']}")
        print(f"       Decision : {decision.decision} (Expected: {expected})")
        print(f"       Response : {decision.message}\n")

    if all_passed:
        print("All 3 tests passed successfully!\n")
    else:
        print("Some tests failed.\n")

    return all_passed


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
