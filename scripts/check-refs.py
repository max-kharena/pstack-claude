#!/usr/bin/env python3
"""Prove pstack's cross-references survived the port.

Checks every shipped markdown file for:
  - relative links whose target file is missing
  - skills named as **name** skill, `/name`, `/pstack:name`, or principle-* that do not exist
  - subagent_type values that name no agent
Prints the skill -> skill dependency graph with --graph.

Usage: scripts/check-refs.py [--graph]   (exit 1 on any broken reference)
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SHIPPED = ["skills", "agents", "docs", "automations", "output-styles"]
SKILLS = {p.name for p in (ROOT / "skills").iterdir() if (p / "SKILL.md").exists()}
AGENTS = {"pstack:" + p.stem for p in (ROOT / "agents").glob("*.md")}
BUILTIN_AGENTS = {"general-purpose", "Explore", "Plan"}
# Slash commands and skills that live outside pstack on purpose.
EXTERNAL = {
    "loop", "schedule", "routines", "output-style", "plugin", "effort", "config", "clear", "resume",
    "skill-creator", "web-setup", "agents", "add-dir", "help", "model", "verify",
    "reload-plugins", "plugins",
}
# Backticked tokens that look like slash commands but are paths, endpoints, or
# a deliberate "this is not a skill" note (poteto-help on /orchestrate).
NOT_SKILLS = {"tmp", "fire", "orchestrate"}
# Benny's operational files are read by path, not registered as skills.
BENNY = {"setup-benny", "triage-issue-reports", "reproduce-and-fix-issues"}

LINK = re.compile(r"\]\(([^)#\s]+)(?:#[^)]*)?\)")
BOLD_SKILL = re.compile(r"\*\*([a-z][a-z0-9-]+)\*\*(?= (?:principle )?skill)")
SLASH = re.compile(r"`/(?:pstack:)?([a-z][a-z0-9-]+)(?=[`\s])")
PRINCIPLE = re.compile(r"\bprinciple-[a-z0-9-]+[a-z0-9]")
SUBAGENT = re.compile(r"subagent_type`?:\s*`?\"?([A-Za-z][\w:-]*)")


def owner(path):
    rel = path.relative_to(ROOT).parts
    return rel[1] if rel[0] == "skills" else "/".join(rel[:2])


def main():
    errors, graph = [], {}
    for base in SHIPPED:
        for path in sorted((ROOT / base).rglob("*.md")):
            text = path.read_text()
            rel = path.relative_to(ROOT)
            src = owner(path)
            for target in LINK.findall(text):
                if re.match(r"[a-z]+:", target) or target.startswith("${") or target in {"url", "URL"}:
                    continue
                if not (path.parent / target).exists():
                    errors.append(f"{rel}: broken link {target}")
            named = set(BOLD_SKILL.findall(text)) | set(SLASH.findall(text)) | set(PRINCIPLE.findall(text))
            for name in named:
                # Upstream names principles by their short form: "the **prove-it-works** principle skill".
                if name not in SKILLS and "principle-" + name in SKILLS:
                    name = "principle-" + name
                if name in SKILLS:
                    if name != src:
                        graph.setdefault(src, set()).add(name)
                elif name not in EXTERNAL | NOT_SKILLS | BENNY and not name.startswith("principle-name"):
                    errors.append(f"{rel}: names missing skill '{name}'")
            for agent in SUBAGENT.findall(text):
                if agent not in AGENTS and agent not in BUILTIN_AGENTS:
                    errors.append(f"{rel}: subagent_type '{agent}' is not a pstack or built-in agent")
    if "--graph" in sys.argv:
        for src in sorted(graph):
            print(f"{src} -> {', '.join(sorted(graph[src]))}")
    for e in errors:
        print("ERROR", e)
    print(f"check-refs: {len(SKILLS)} skills, {len(AGENTS)} agents, {sum(len(v) for v in graph.values())} skill edges, {len(errors)} broken")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
