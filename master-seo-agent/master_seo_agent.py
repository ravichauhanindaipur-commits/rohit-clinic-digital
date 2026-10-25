
from pathlib import Path
import subprocess
import sys

ROOT = Path.home() / "rohit-clinic-digital"
AGENT_DIR = ROOT / "seo-audit-agent"

print("\n=== ROHIT CLINIC MASTER SEO AGENT ===\n")

if not AGENT_DIR.is_dir():
    print("SEO agent folder nahi mila:", AGENT_DIR)
    sys.exit(1)

agents = sorted(AGENT_DIR.glob("*.py"))

if not agents:
    print("Koi Python agent file nahi mili.")
    print("Folder:", AGENT_DIR)
    print("Available files:")
    for p in sorted(AGENT_DIR.iterdir()):
        print("-", p.name)
    sys.exit(1)

for agent in agents:
    if agent.name.startswith("__"):
        continue

    print(f"\n--- Running: {agent.name} ---")
    result = subprocess.run(
        [sys.executable, str(agent)],
        cwd=str(AGENT_DIR)
    )
    print("Exit code:", result.returncode)

print("\n=== MASTER SEO AGENT FINISHED ===")


