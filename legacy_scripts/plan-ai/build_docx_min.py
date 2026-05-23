import argparse
import json
import subprocess
from pathlib import Path

print("Script started")

parser = argparse.ArgumentParser()
parser.add_argument("--content", required=True)
parser.add_argument("--output", required=True)
args = parser.parse_args()

print("Args parsed:", args.content, args.output)

content = json.loads(Path(args.content).read_text(encoding="utf-8"))
print("Content loaded, sections:", len(content.get("sections", [])))

subprocess.run(["officecli", "create", args.output], check=True)
print("Created")
subprocess.run(["officecli", "open", args.output], check=True)
print("Opened")
subprocess.run(["officecli", "close", args.output], check=True)
print("Closed")
