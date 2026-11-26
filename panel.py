import argparse
import csv
import json
from collections import Counter
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("command", choices=["init", "report"])
parser.add_argument("directory", type=Path)
args = parser.parse_args()
root = args.directory
if args.command == "init":
    root.mkdir(parents=True, exist_ok=True)
    with (root / "panel.csv").open("x", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(["id", "viewport", "experience", "priority", "goal_slot"])
        for i in range(100):
            writer.writerow([i + 1, ["390x844", "1440x900"][i // 50],
                             ["new", "experienced"][i // 25 % 2],
                             ["clarity", "speed", "readability", "keyboard", "error prevention"][i // 5 % 5],
                             i % 5 + 1])
else:
    statuses = ["success", "partial", "blocked", "untested"]
    fields = ["page", "action", "evidence", "interface", "friction", "improvement"]
    cases = {}
    for line in (root / "reviews.jsonl").read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        index = row["id"]
        if type(index) is not int or index in cases or not 1 <= index <= 100:
            raise SystemExit(f"Invalid or repeated ID {index}")
        if row["status"] not in statuses or any(not isinstance(row.get(k), str) or not row[k].strip() for k in fields):
            raise SystemExit(f"Incomplete review {index}")
        cases[index] = row
    if len(cases) != 100:
        raise SystemExit(f"Missing IDs {sorted(set(range(1, 101)) - cases.keys())}")
    counts = Counter(r["status"] for r in cases.values())
    lines = ["# Đánh giá của 100 khách hàng mô phỏng", ""]
    lines.extend(f"- {s}: {counts[s]}" for s in statuses)
    labels = ["Trang", "Thao tác", "Quan sát", "Giao diện", "Bất cập", "Đề xuất"]
    for index, row in sorted(cases.items()):
        lines.extend(["", f"## #{index} · {row['status']}", ""])
        lines.extend(f"- {label}: {row[k]}" for label, k in zip(labels, fields))
    (root / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
