#!/usr/bin/env python3
"""
AI Log Analyzer — fetches Kubernetes pod logs and uses Claude to diagnose issues.

Usage:
    python analyzer.py <pod-name> [--namespace <ns>] [--tail <n>]

Example:
    python analyzer.py api-reliability-monitor-abc123-xyz
    ANTHROPIC_API_KEY=sk-ant-... python analyzer.py my-pod --tail 200
"""

import argparse
import os
import subprocess
import sys

import anthropic


def fetch_pod_logs(pod_name: str, namespace: str, tail: int) -> str:
    cmd = ["kubectl", "logs", pod_name, f"--namespace={namespace}", f"--tail={tail}"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    except FileNotFoundError:
        print("Error: kubectl not found. Install it and make sure it's on your PATH.")
        sys.exit(1)
    except subprocess.TimeoutExpired:
        print("Error: kubectl logs timed out after 30 seconds.")
        sys.exit(1)

    if result.returncode != 0:
        print(f"Error fetching logs from pod '{pod_name}':")
        print(result.stderr.strip())
        sys.exit(1)

    logs = result.stdout.strip()
    if not logs:
        print(f"No logs found for pod '{pod_name}' (namespace: {namespace}).")
        sys.exit(0)

    return logs


def analyze_logs(logs: str, pod_name: str) -> None:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable is not set.")
        print("  export ANTHROPIC_API_KEY=sk-ant-...")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    prompt = f"""You are an expert SRE (Site Reliability Engineer) analyzing Kubernetes pod logs.

Pod name: {pod_name}

Here are the last {len(logs.splitlines())} lines of logs:

---
{logs}
---

Please provide:
1. **Root Cause** — What is most likely causing any errors or issues you see? If logs look healthy, say so.
2. **Severity** — Is this critical, warning, or informational?
3. **Suggested Fix** — Clear, actionable steps to resolve the issue.
4. **Preventive Measures** — How to avoid this problem in the future.

Be concise and practical. Use plain English — this output will be read by engineers who need to act fast."""

    print(f"\nAnalyzing logs for pod: {pod_name}")
    print("=" * 60)
    print("Claude is thinking...\n")

    with client.messages.stream(
        model="claude-opus-4-8",
        max_tokens=16000,
        thinking={"type": "adaptive"},
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)

    print("\n" + "=" * 60)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Analyze Kubernetes pod logs with Claude AI"
    )
    parser.add_argument("pod_name", help="Name of the Kubernetes pod to analyze")
    parser.add_argument(
        "--namespace", "-n", default="api-reliability-monitor",
        help="Kubernetes namespace (default: api-reliability-monitor)"
    )
    parser.add_argument(
        "--tail", "-t", type=int, default=100,
        help="Number of recent log lines to fetch (default: 100)"
    )
    args = parser.parse_args()

    print(f"Fetching last {args.tail} log lines from pod '{args.pod_name}'...")
    logs = fetch_pod_logs(args.pod_name, args.namespace, args.tail)
    print(f"Retrieved {len(logs.splitlines())} lines.\n")

    analyze_logs(logs, args.pod_name)


if __name__ == "__main__":
    main()
