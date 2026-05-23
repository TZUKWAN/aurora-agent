import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, r'C:\Users\lauze\.claude\skills\business-plan-writer\scripts')
from build_docx import build_batch_commands

print("Script started")

parser = argparse.ArgumentParser()
parser.add_argument("--content", required=True)
parser.add_argument("--output", required=True)
args = parser.parse_args()

print("Args parsed")
content = json.loads(Path(args.content).read_text(encoding="utf-8"))
commands = build_batch_commands(content)
print("Commands:", len(commands))

subprocess.run(["officecli", "create", args.output], check=True)
print("Created")
subprocess.run(["officecli", "open", args.output], check=True)
print("Opened")

for i in range(0, len(commands), 50):
    chunk = commands[i:i+50]
    print(f"Chunk {i//50+1} size {len(chunk)}")
    proc = subprocess.run(
        ["officecli", "batch", args.output, "--json"],
        input=json.dumps(chunk, ensure_ascii=False),
        capture_output=True, text=True, encoding="utf-8"
    )
    print(f"Chunk result {proc.returncode}")

subprocess.run(["officecli", "close", args.output], check=True)
print("Closed")
