"""Command-line interface: supportsage triage <tickets.jsonl> --out <out.jsonl>."""

import argparse
import json
import sys
from collections import Counter

from .triage import triage_ticket


def build_parser():
    parser = argparse.ArgumentParser(
        prog="supportsage",
        description="Rule-based customer support ticket triage (mock, no LLM calls).",
    )
    sub = parser.add_subparsers(dest="command", required=True)
    triage = sub.add_parser("triage", help="triage tickets from a JSONL file")
    triage.add_argument("input", help="input JSONL file, one ticket per line")
    triage.add_argument("--out", required=True, help="output JSONL file")
    return parser


def run_triage(input_path, output_path):
    try:
        infile = open(input_path, encoding="utf-8")
    except FileNotFoundError:
        print(f"error: input file not found: {input_path}", file=sys.stderr)
        return 2

    categories = Counter()
    priorities = Counter()
    total = 0
    with infile, open(output_path, "w", encoding="utf-8") as outfile:
        for line in infile:
            line = line.strip()
            if not line:
                continue
            ticket = json.loads(line)
            triaged = triage_ticket(ticket)
            categories[triaged["category"]] += 1
            priorities[triaged["priority"]] += 1
            total += 1
            outfile.write(json.dumps(triaged) + "\n")

    cat_summary = ", ".join(f"{c}={n}" for c, n in sorted(categories.items()))
    pri_summary = ", ".join(f"{p}={n}" for p, n in sorted(priorities.items()))
    print(f"triaged {total} tickets | categories: {cat_summary} | priorities: {pri_summary}")
    return 0


def main(argv=None):
    args = build_parser().parse_args(argv)
    if args.command == "triage":
        return run_triage(args.input, args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
