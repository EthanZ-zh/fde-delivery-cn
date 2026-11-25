"""Run the synthetic ticket-triage fixture and write one evidence record."""

import argparse
import json
from pathlib import Path
from tempfile import TemporaryDirectory


def run_ticket(ticket, scenario, decision):
    evidence = {
        "simulated": True,
        "scenario": scenario,
        "ticket_id": ticket["id"],
        "requested_decision": decision,
        "suggested_queue": None,
        "final_queue": None,
    }

    if scenario == "offline":
        return dict(evidence, status="manual_review",
                    reason_code="simulated_model_unavailable",
                    reason="建议服务模拟离线，保留原人工处理路径。",
                    events=["model_unavailable", "manual_review"])
    if ticket["category"] != "network":
        return dict(evidence, status="manual_review",
                    reason_code="unknown_category",
                    reason="样本类别没有对应队列，交由值班主管人工判断。",
                    events=["unknown_category", "manual_review"])

    evidence["suggested_queue"] = "IT 支持"
    if decision == "approve":
        return dict(evidence, final_queue=evidence["suggested_queue"], status="routed",
                    reason_code="operator_approved",
                    reason="网络故障命中固定规则，模拟主管确认后分流。",
                    events=["suggested", "approved", "routed"])
    if decision == "reject":
        return dict(evidence, status="manual_review", reason_code="operator_rejected",
                    reason="模拟主管拒绝分流建议，交由人工处理。",
                    events=["suggested", "rejected", "manual_review"])
    return dict(evidence, status="awaiting_confirmation", reason_code="decision_pending",
                reason="网络故障命中固定规则，等待值班主管确认。",
                events=["suggested", "awaiting_confirmation"])


def write_evidence(destination, evidence):
    destination.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=destination.parent) as directory:
        temporary_path = Path(directory) / "evidence.json"
        temporary_path.write_text(
            json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n"
        )
        temporary_path.replace(destination)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", choices=("normal", "offline", "unknown"), default="normal")
    parser.add_argument("--decision", choices=("pending", "approve", "reject"), default="pending")
    parser.add_argument("--out", type=Path, required=True, help="Directory for evidence.json")
    args = parser.parse_args()

    tickets = json.loads(Path(__file__).with_name("tickets.json").read_text(encoding="utf-8"))
    ticket = tickets["unknown" if args.scenario == "unknown" else "normal"]
    result = run_ticket(ticket, args.scenario, args.decision)
    write_evidence(args.out / "evidence.json", result)
    print(f"{result['ticket_id']}: {result['status']} (evidence.json)")


if __name__ == "__main__":
    main()
