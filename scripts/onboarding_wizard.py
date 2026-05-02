#!/usr/bin/env python3
"""CertainLogic Onboarding Wizard v2.0.0

Automated environment scan + personalized recommendations.
Generates install commands. User runs them manually.

Usage:
    python3 scripts/onboarding_wizard.py [goal]
    python3 scripts/onboarding_wizard.py --scan-only
"""
import sys
import json
import os
import platform
import subprocess
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional, Set

import datetime


# ------------------------------------------------------------------
# Skill registry — our products + verified community skills
# ------------------------------------------------------------------
CERTAINLOGIC_SKILLS = {
    "skill-vetter-plus": {
        "name": "Skill Vetter Plus",
        "category": "security",
        "priority": 1,
        "description": "Security scanner — always install first",
        "clawhub_id": "skill-vetter-plus"
    },
    "certainlogic-smart-router": {
        "name": "CertainLogic Smart Router",
        "category": "routing",
        "priority": 2,
        "description": "Route queries to cheapest model tier",
        "clawhub_id": "certainlogic-smart-router"
    },
    "token-reduction-engine-v2": {
        "name": "Token Reduction Engine",
        "category": "optimization",
        "priority": 3,
        "description": "Keep sessions lean",
        "clawhub_id": "token-reduction-engine-v2"
    },
    "pa-pack": {
        "name": "Personal Assistant Pack",
        "category": "productivity",
        "priority": 4,
        "description": "Curated daily workflow (macOS-centric)",
        "clawhub_id": "pa-pack"
    },
    "skill-oracle": {
        "name": "Skill Oracle",
        "category": "discovery",
        "priority": 5,
        "description": "Curated skill directory",
        "clawhub_id": "skill-oracle"
    },
    "agentpathfinder": {
        "name": "AgentPathfinder",
        "category": "tracking",
        "priority": 6,
        "description": "Verifiable task tracking",
        "clawhub_id": "agentpathfinder"
    },
}

COMMUNITY_SKILLS = {
    "gog": {
        "name": "Google Workspace CLI (gog)",
        "creator": "steipete",
        "category": "productivity",
        "description": "Gmail, Calendar, Drive, Contacts, Sheets, Docs",
        "platforms": ["linux", "macos"],
        "clawhub_id": "gog"
    },
    "things-mac": {
        "name": "Things 3 for macOS",
        "creator": "",
        "category": "productivity",
        "description": "macOS task manager integration",
        "platforms": ["macos"],
        "clawhub_id": "things-mac"
    },
    "himalaya": {
        "name": "Himalaya Email",
        "creator": "pimalaya",
        "category": "communication",
        "description": "Terminal email client (IMAP)",
        "platforms": ["linux", "macos"],
        "clawhub_id": "himalaya"
    },
    "notion": {
        "name": "Notion Integration",
        "creator": "",
        "category": "productivity",
        "description": "Knowledge base integration",
        "platforms": ["linux", "macos"],
        "clawhub_id": "notion"
    },
    "skill-creator": {
        "name": "Skill Creator",
        "creator": "",
        "category": "development",
        "description": "Build your own skills",
        "platforms": ["linux", "macos"],
        "clawhub_id": "skill-creator"
    },
    "taskflow": {
        "name": "TaskFlow",
        "creator": "",
        "category": "automation",
        "description": "Durable task management",
        "platforms": ["linux", "macos"],
        "clawhub_id": "taskflow"
    },
    "github": {
        "name": "GitHub Integration",
        "creator": "",
        "category": "development",
        "description": "Repository access",
        "platforms": ["linux", "macos"],
        "clawhub_id": "github"
    },
}

GOAL_PROFILES = {
    "developer": {
        "title": "Coding / Development",
        "certainlogic_skills": ["skill-vetter-plus", "certainlogic-smart-router", "token-reduction-engine-v2"],
        "community_skills": ["github", "skill-creator"],
    },
    "business": {
        "title": "Small Business",
        "certainlogic_skills": ["skill-vetter-plus", "pa-pack", "certainlogic-smart-router"],
        "community_skills": ["gog", "notion", "himalaya"],
    },
    "research": {
        "title": "Research & Analysis",
        "certainlogic_skills": ["skill-vetter-plus", "skill-oracle", "certainlogic-smart-router"],
        "community_skills": ["taskflow"],
    },
    "productivity": {
        "title": "Personal Productivity",
        "certainlogic_skills": ["skill-vetter-plus", "pa-pack", "certainlogic-smart-router"],
        "community_skills": ["things-mac", "gog", "notion"],
    },
    "beginner": {
        "title": "Just Starting",
        "certainlogic_skills": ["skill-vetter-plus", "skill-oracle", "certainlogic-smart-router", "token-reduction-engine-v2"],
        "community_skills": ["skill-creator"],
    },
}


class EnvironmentScanner:
    """Scan the user's OpenClaw environment."""

    @staticmethod
    def detect_os() -> str:
        system = platform.system().lower()
        return "macos" if system == "darwin" else system

    @staticmethod
    def find_skills_dir() -> Optional[Path]:
        paths = [
            Path.home() / ".openclaw" / "skills",
            Path.home() / ".openclaw" / "workspace" / "skills",
        ]
        for p in paths:
            if p.exists():
                return p
        return None

    @staticmethod
    def scan_installed_skills(skills_dir: Optional[Path]) -> Set[str]:
        """Return set of installed skill slugs."""
        if not skills_dir:
            return set()
        # Look for SKILL.md or directories in skills folder
        installed = set()
        for item in skills_dir.iterdir():
            if item.is_dir() and not item.name.startswith("."):
                installed.add(item.name)
        return installed

    @staticmethod
    def detect_openclaw_version() -> str:
        """Try to detect OpenClaw version."""
        try:
            result = subprocess.run(
                ["openclaw", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        return "Unknown"


class OnboardingWizard:
    """Main wizard class."""

    def __init__(self, output_dir: Optional[Path] = None):
        if output_dir is None:
            output_dir = Path.home() / ".openclaw" / "workspace" / "onboarding-guides"
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.scanner = EnvironmentScanner()

    def detect_goal(self, raw_input: str) -> Optional[str]:
        """Map free-form input to a known goal profile."""
        raw = raw_input.lower().strip()
        if raw in GOAL_PROFILES:
            return raw
        keywords = {
            "developer": ["code", "coding", "programmer", "dev", "software", "engineer", "github"],
            "business": ["business", "company", "startup", "entrepreneur", "solopreneur", "consulting"],
            "research": ["research", "analyst", "analysis", "investigate", "study", "academic"],
            "productivity": ["productivity", "personal", "assistant", "workflow", "tasks", "todo"],
            "beginner": ["new", "start", "beginner", "first time", "help me set up"],
        }
        for goal, words in keywords.items():
            if any(w in raw for w in words):
                return goal
        return None

    def generate_report(self, goal: str, env_info: Dict[str, Any]) -> str:
        """Generate comprehensive markdown onboarding report."""
        profile = GOAL_PROFILES[goal]
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        os_name = env_info.get("os", "unknown")
        installed = env_info.get("installed_skills", set())

        report = f"""# Your OpenClaw Onboarding Report
Generated: {timestamp} | Profile: {profile['title']}

> ⚠️ Recommendations based on our testing. Verify before trusting.

## Environment Detected
- **OS:** {os_name}
- **OpenClaw:** {env_info.get('openclaw_version', 'Unknown')}
- **Skills directory:** {env_info.get('skills_dir', 'Not found')}
- **Existing skills:** {len(installed)} installed

"""

        # CertainLogic skills section
        report += "## CertainLogic Skills\n\n"
        for skill_slug in profile["certainlogic_skills"]:
            skill = CERTAINLOGIC_SKILLS[skill_slug]
            status = "✅ Installed" if skill_slug in installed else "⬜ Not installed"
            report += f"### {skill['name']}\n"
            report += f"- **Status:** {status}\n"
            report += f"- **Why:** {skill['description']}\n"
            if skill_slug not in installed:
                report += f"- **Install:** `clawhub install {skill['clawhub_id']}`\n"
            report += "\n"

        # Community skills section (filtered by OS)
        report += "## Community Skills (Verified)\n\n"
        for skill_slug in profile.get("community_skills", []):
            if skill_slug not in COMMUNITY_SKILLS:
                continue
            skill = COMMUNITY_SKILLS[skill_slug]
            # Filter by platform
            if os_name not in skill.get("platforms", ["linux", "macos"]):
                report += f"### {skill['name']}\n"
                report += f"- **Status:** ⏭️ Skipped ({os_name} not supported)\n"
                report += f"- **Why:** {skill['description']}\n\n"
                continue

            status = "✅ Installed" if skill_slug in installed else "⬜ Not installed"
            report += f"### {skill['name']}\n"
            report += f"- **Status:** {status}\n"
            report += f"- **Creator:** {skill.get('creator', 'Community')}\n"
            report += f"- **Why:** {skill['description']}\n"
            if skill_slug not in installed:
                report += f"- **Install:** `clawhub install {skill['clawhub_id']}`\n"
            report += "\n"

        # Install checklist
        report += """## Your Install Checklist

"""
        all_skills = profile["certainlogic_skills"] + profile.get("community_skills", [])
        for i, skill_slug in enumerate(all_skills, 1):
            if skill_slug in CERTAINLOGIC_SKILLS:
                name = CERTAINLOGIC_SKILLS[skill_slug]["name"]
                cmd = f"clawhub install {CERTAINLOGIC_SKILLS[skill_slug]['clawhub_id']}"
            elif skill_slug in COMMUNITY_SKILLS:
                name = COMMUNITY_SKILLS[skill_slug]["name"]
                cmd = f"clawhub install {COMMUNITY_SKILLS[skill_slug]['clawhub_id']}"
            else:
                continue

            if skill_slug in installed:
                report += f"{i}. ✅ ~~{name}~~ (already installed)\n"
            else:
                report += f"{i}. ⬜ **{name}**\n   `{cmd}`\n"

        report += """
## Important Notes

1. **Install Vetter Plus FIRST** — Scan every new skill before trusting it
2. **Read SKILL.md files** — Every skill has limitations
3. **Test before trusting** — What worked for us may not work for you
4. **macOS users:** PA Pack requires Things 3 (paid app)
5. **Linux users:** Some macOS-specific skills are skipped automatically

## Honest Limitations

- Recommendations are based on our testing, not universal truth
- Auto-detection checks common paths — may miss custom setups
- Platform filtering is best-effort
- We can't verify skill quality post-install — test everything
- API costs are your responsibility

## Next Steps

1. Work through the install checklist above
2. Run `python3 scripts/vetter.py <skill-dir>` on each new skill
3. Test each skill with simple tasks before using for real work
4. Join the OpenClaw community for help

---

*Built by CertainLogicAI. We want every new OpenClaw user to start strong.*
*This report was auto-generated. Review all recommendations before acting.*
"""
        return report

    def run(self, goal_input: Optional[str] = None) -> Path:
        """Run full onboarding flow with auto-detection."""
        print("=" * 70)
        print("CertainLogic Onboarding Wizard v2.0.0")
        print("=" * 70)
        print()

        # Environment scan
        print("🔍 Scanning your environment...")
        os_name = self.scanner.detect_os()
        skills_dir = self.scanner.find_skills_dir()
        installed = self.scanner.scan_installed_skills(skills_dir)
        version = self.scanner.detect_openclaw_version()

        env_info = {
            "os": os_name,
            "skills_dir": str(skills_dir) if skills_dir else None,
            "installed_skills": installed,
            "openclaw_version": version,
        }

        print(f"   OS: {os_name}")
        print(f"   Skills directory: {skills_dir or 'Not found'}")
        print(f"   Installed skills: {len(installed)}")
        print(f"   OpenClaw version: {version}")
        print()

        # Goal detection
        if goal_input:
            goal = self.detect_goal(goal_input)
        else:
            print("What brings you to OpenClaw?")
            print("  developer | business | research | productivity | beginner")
            goal = self.detect_goal(input("> ").strip())

        if not goal or goal not in GOAL_PROFILES:
            print("Unknown goal. Defaulting to 'beginner'.")
            goal = "beginner"

        print(f"\n🎯 Profile: {GOAL_PROFILES[goal]['title']}")
        print()

        # Generate report
        print("📋 Generating your personalized onboarding report...")
        report = self.generate_report(goal, env_info)

        # Save
        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        path = self.output_dir / f"onboarding-report-{timestamp}.md"
        path.write_text(report, encoding="utf-8")

        print(f"\n✅ Report saved: {path}")
        print(f"\n📌 Next: Open the report and work through your install checklist.")
        print("   Remember: Install Vetter Plus first, scan everything, read SKILL.md files.")

        return path

    def scan_only(self):
        """Just show environment scan, no recommendations."""
        print("=" * 70)
        print("Environment Scan Only")
        print("=" * 70)
        os_name = self.scanner.detect_os()
        skills_dir = self.scanner.find_skills_dir()
        installed = self.scanner.scan_installed_skills(skills_dir)

        print(f"\nOS: {os_name}")
        print(f"Skills directory: {skills_dir or 'Not found'}")
        print(f"Installed skills ({len(installed)}):")
        for s in sorted(installed):
            print(f"  • {s}")


def main():
    parser = argparse.ArgumentParser(description="CertainLogic Onboarding Wizard v2.0")
    parser.add_argument("goal", nargs="?", help="Your goal")
    parser.add_argument("--scan-only", action="store_true", help="Just scan environment")
    parser.add_argument("--output-dir", type=str, help="Custom output directory")
    args = parser.parse_args()

    wizard = OnboardingWizard(output_dir=args.output_dir)

    if args.scan_only:
        wizard.scan_only()
        return

    wizard.run(goal_input=args.goal)


if __name__ == "__main__":
    main()
