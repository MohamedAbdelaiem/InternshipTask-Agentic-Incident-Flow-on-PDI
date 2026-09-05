import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config.constants import SN_CLOSE_CODE_SOLVED_PERMANENTLY, SN_STATE_RESOLVED
from app.llm.gemeni import get_agent_decision
from app.servicenow.service_now import build_update_payload


def run_tests():
    test_file = Path(__file__).resolve().parent / "test_incidents.json"
    with open(test_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    print("\nTesting Official Incidents (Decision + ServiceNow Payload):\n")
    all_passed = True

    for i, inc in enumerate(data.get("incidents", []), start=1):
        decision = get_agent_decision(inc["short_description"], inc["description"])
        expected = inc["expected_decision"]
        payload = build_update_payload(decision)

        # Validate decision matches expected
        decision_ok = decision.decision == expected

        # Validate ServiceNow payload matches rules
        if expected == "respond":
            payload_ok = (
                payload.get("state") == SN_STATE_RESOLVED
                and payload.get("close_code") == SN_CLOSE_CODE_SOLVED_PERMANENTLY
            )
        elif expected == "ask":
            payload_ok = "comments" in payload
        elif expected == "escalate":
            payload_ok = "work_notes" in payload
        else:
            payload_ok = False

        passed = decision_ok and payload_ok
        if not passed:
            all_passed = False

        status = "PASS" if passed else "FAIL"
        print(f"[{status}] Ticket {i}: {inc['short_description']}")
        print(f"       Decision : {decision.decision} (Expected: {expected})")
        print(f"       Message  : {decision.message}")
        print(f"       Payload  : {payload}\n")

    if all_passed:
        print("All 3 tests and ServiceNow payloads verified!\n")
    else:
        print("Some tests failed.\n")

    return all_passed


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
