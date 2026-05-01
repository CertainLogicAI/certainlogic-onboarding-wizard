#!/usr/bin/env python3
"""CertainLogic Onboarding Wizard v1.0.0

Conversational onboarding tool for OpenClaw. Generates personalized markdown starter guides.
NOT an installer — produces guides only. User executes steps manually.

Usage:
    python3 scripts/onboarding_wizard.py [goal]

Goals: developer, business, research, productivity, beginner
"""
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional

import datetime

# ------------------------------------------------------------------
# Goal profiles — curated recommendations (our testing, user verifies)
# ------------------------------------------------------------------
GOAL_PROFILES = {
    "developer": {
        "title": "Coding / Development",
        "follow_up_questions": [
            "What languages do you primarily code in?",
            "Do you need GitHub/GitLab integration?",
            "Are you working solo or with a team?",
            "What's your monthly API budget? (rough estimate)",
        ],
        "recommended_skills": [
            {
                "name": "Context TokenReducer",
                "clawhub_id": "token-reduction-engine-v2",
                "reason": "Helps manage session size during long coding sessions",
                "caveat": "Manages sessions but doesn't directly reduce API costs",
                "cost": "Free"
            },
            {
                "name": "GitHub Skill",
                "clawhub_id": "github",
                "reason": "Repository access and code review workflows",
                "caveat": "Requires GitHub token setup — you handle credentials",
                "cost": "Free"
            },
            {
                "name": "Skill Vetter Plus",
                "clawhub_id": "skill-vetter-plus",
                "reason": "Security pre-check before installing any new skill",
                "caveat": "Catches obvious issues, not all security problems",
                "cost": "Free"
            },

         ],
   "setup_steps": [
            "Install Vetter Plus: `clawhub install skill-vetter-plus`",
            "Scan every skill before installing it",
            "Install TokenReducer: `clawhub install token-reduction-engine-v2`",
            "Set up GitHub token in your environment",
            "Install GitHub skill: `clawhub install github`",
        ],
        "estimated_monthly_cost": "Variable — depends on coding frequency and model choice",
    },
    "business": {
        "title": "Small Business Assistant",
        "follow_up_questions": [
            "What type of business? (e.g., consulting, e-commerce, service)",
            "Do you have a personal assistant or are you solo?",
            "What tasks take up most of your time?",
            "Do you use Google Workspace or Microsoft 365?",
        ],
        "recommended_skills": [
            {
                "name": "Skill Vetter Plus",
                "clawhub_id": "skill-vetter-plus",
                "reason": "Security baseline — scan before installing anything",
                "caveat": "First-line check only, not a full security audit",
                "cost": "Free"
            },
            {
                "name": "Personal Assistant Pack",
                "clawhub_id": "pa-pack",
                "reason": "Curated daily workflow tools (things-mac, notion, etc.)",
                "caveat": "Requires macOS for Things 3; OAuth setup for Google Workspace",
                "cost": "Free"
            },
            {
                "name": "Context TokenReducer",
                "clawhub_id": "token-reduction-engine-v2",
                "reason": "Prevents context bloat during long business sessions",
                "caveat": "Benefits vary by usage pattern",
                "cost": "Free"
            },
        ],
        "setup_steps": [
            "Install Vetter Plus: `clawhub install skill-vetter-plus`",
            "Run security scan on PA Pack before installing",
            "Install PA Pack: `clawhub install pa-pack`",
            "Review PA_GUIDE.md for your daily workflow",
            "Set up Google Workspace OAuth if using gog skill",
            "Install TokenReducer: `clawhub install token-reduction-engine-v2`",
        ],
        "estimated_monthly_cost": "Variable — PA Pack skills are free; API costs depend on usage",
    },
    "research": {
        "title": "Research & Analysis",
        "follow_up_questions": [
            "What field are you researching?",
            "Do you need web search or database access?",
            "How do you want to organize findings?",
            "Do you share research with a team?",
        ],
        "recommended_skills": [
            {
                "name": "Skill Oracle",
                "clawhub_id": "skill-oracle",
                "reason": "Curated directory of quality ClawHub skills",
                "caveat": "Our opinions. Verify before trusting any recommendation",
                "cost": "Free"
            },
            {
                "name": "Context TokenReducer",
                "clawhub_id": "token-reduction-engine-v2",
                "reason": "Critical for long research sessions with large contexts",
                "caveat": "Session management only — doesn't fact-check",
                "cost": "Free"
            },
            {
                "name": "Search Skills",
                "clawhub_id": "various",
                "reason": "Web search, Perplexity, or Exa integration",
                "caveat": "Search results are only as good as the query — verify sources",
                "cost": "Free (some search APIs may require paid keys)"
            },
        ],
        "setup_steps": [
            "Install Skill Oracle: `clawhub install skill-oracle`",
            "Browse Oracle catalog for research-relevant skills",
            "Install TokenReducer: `clawhub install token-reduction-engine-v2`",
            "Set up search API keys if using external search",
            "Install chosen search skill: `clawhub install <skill-name>`",
        ],
        "estimated_monthly_cost": "Variable — search APIs may add cost; OpenClaw skills are free",
    },
    "productivity": {
        "title": "Personal Productivity",
        "follow_up_questions": [
            "What platform? (macOS strongly recommended for PA Pack)",
            "What apps do you already use? (Notion, Things 3, Calendar?)",
            "What's your biggest productivity bottleneck?",
            "Do you want automation or just better organization?",
        ],
        "recommended_skills": [
            {
                "name": "Personal Assistant Pack",
                "clawhub_id": "pa-pack",
                "reason": "Complete daily workflow automation stack",
                "caveat": "macOS + Things 3 required for full experience; Google Workspace requires OAuth",
                "cost": "Free"
            },
            {
                "name": "Skill Oracle",
                "clawhub_id": "skill-oracle",
                "reason": "Find additional productivity tools beyond PA Pack",
                "caveat": "Curated, not exhaustive",
                "cost": "Free"
            },
            {
                "name": "Context TokenReducer",
                "clawhub_id": "token-reduction-engine-v2",
                "reason": "Keeps long productivity sessions from hitting context limits",
                "caveat": "Session management, not cost reduction",
                "cost": "Free"
            },
        ],
        "setup_steps": [
            "Install PA Pack: `clawhub install pa-pack`",
            "Read PA_GUIDE.md for morning workflow",
            "Set up Things 3 (macOS) or alternative task manager",
            "Configure Google Workspace OAuth if using gog",
            "Install Skill Oracle: `clawhub install skill-oracle`",
            "Browse Oracle for additional productivity skills",
        ],
        "estimated_monthly_cost": "Free skills + your API usage",
    },
    "beginner": {
        "title": "Just Starting",
        "follow_up_questions": [
            "What's your technical background? (none, some coding, developer?)",
            "What do you want to accomplish with your AI agent?",
            "Do you have API keys (OpenAI, Anthropic) already?",
            "What's your monthly budget for AI tools?",
        ],
        "recommended_skills": [
            {
                "name": "Skill Vetter Plus",
                "clawhub_id": "skill-vetter-plus",
                "reason": "Safety first — learn to vet skills before installing",
                "caveat": "Catches obvious problems. Always read SKILL.md files too",
                "cost": "Free"
            },
            {
                "name": "Skill Oracle",
                "clawhub_id": "skill-oracle",
                "reason": "Curated directory so you don't waste time on broken skills",
                "caveat": "Our testing + community feedback. Verify for yourself",
                "cost": "Free"
            },
            {
                "name": "Context TokenReducer",
                "clawhub_id": "token-reduction-engine-v2",
                "reason": "Helps prevent expensive context bloat mistakes",
                "caveat": "Manages sessions. Doesn't reduce costs directly",
                "cost": "Free"
            },
        ],
        "setup_steps": [
            "Install Vetter Plus: `clawhub install skill-vetter-plus`",
            "Learn to scan: `python3 scripts/vetter.py <skill-dir>`",
            "Install Skill Oracle: `clawhub install skill-oracle`",
            "Browse Oracle catalog, read SKILL.md files before installing",
            "Install TokenReducer: `clawhub install token-reduction-engine-v2`",
            "Start with simple tasks, build complexity slowly",
        ],
        "estimated_monthly_cost": "Skills are free. API costs: $10-50/mo for light usage, $100+/mo for heavy",
    },
}

# ------------------------------------------------------------------
# Pro templates (future expansion)
# ------------------------------------------------------------------
PRO_TEMPLATES = {
    "real-estate": {"available_in": "Pro", "description": "Lead tracking, property research, client communication"},
    "restaurant": {"available_in": "Pro", "description": "Inventory, staff scheduling, supplier management"},
    "ecommerce": {"available_in": "Pro", "description": "Product research, listing optimization, competitor tracking"},
    "consulting": {"available_in": "Pro", "description": "Client onboarding, project tracking, deliverable templates"},
    "content-creator": {"available_in": "Pro", "description": "Content calendar, multi-platform posting, analytics"},
}


class OnboardingWizard:
    """Main wizard class — handles questionnaire and guide generation."""

    def __init__(self, output_dir: Optional[Path] = None):
        if output_dir is None:
            output_dir = Path.home() / ".openclaw" / "workspace" / "onboarding-guides"
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def detect_goal(self, raw_input: str) -> Optional[str]:
        """Map free-form input to a known goal profile."""
        raw = raw_input.lower().strip()

        # Direct matches
        if raw in GOAL_PROFILES:
            return raw

        # Keyword matching
        keywords = {
            "developer": ["code", "coding", "programmer", "programming", "dev", "software", "engineer", "github", "git"],
            "business": ["business", "company", "startup", "entrepreneur", "solopreneur", "small biz", "smb", "consulting"],
            "research": ["research", "analyst", "analysis", "investigate", "study", "academic", "market research"],
            "productivity": ["productivity", "personal", "assistant", " organize", "workflow", "pa", "tasks", "todo"],
            "beginner": ["new", "start", "beginner", "just started", "first time", "noob", "help me set up"],
        }

        for goal, words in keywords.items():
            if any(w in raw for w in words):
                return goal

        return None

    def ask_question(self, question: str) -> str:
        """Ask a follow-up question. In agent context, the agent asks. In CLI, we prompt."""
        # When running standalone, prompt user
        # When agent-guided, the agent presents the question
        try:
            return input(f"  {question} ")
        except EOFError:
            # Non-interactive mode (agent or piped input)
            return ""

    def generate_guide(self, goal: str, answers: List[str]) -> str:
        """Generate personalized markdown guide."""
        profile = GOAL_PROFILES[goal]
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

        guide = f"""# Your OpenClaw Starter Guide ({profile['title']})

> Generated by CertainLogic Onboarding Wizard v1.0.0 on {timestamp}
> ⚠️ This is a recommendation only. Verify everything before trusting.

## Your Goals

Based on your input, we've curated a starter stack for: **{profile['title']}**

### Your Answers
"""
        for i, (q, a) in enumerate(zip(profile['follow_up_questions'], answers), 1):
            guide += f"\n{i}. **Q:** {q}\n   **A:** {a or '(no answer)'}\n"

        guide += f"\n## Recommended Skills\n\n"
        for skill in profile['recommended_skills']:
            guide += f"""### {skill['name']}
- **Why:** {skill['reason']}
- **Cost:** {skill['cost']}
- **Caveat:** {skill['caveat']}
- **Install:** `clawhub install {skill['clawhub_id']}`

"""

        guide += f"""## Setup Steps

"""
        for i, step in enumerate(profile['setup_steps'], 1):
            guide += f"{i}. {step}\n"

        guide += f"""
## Cost Expectations

{profile['estimated_monthly_cost']}

## Important Safety Reminders

1. **Always scan before installing** — Use Vetter Plus on every new skill
2. **Read SKILL.md files** — Every skill has limitations. Read them.
3. **Test before trusting** — What worked for us may not work for you
4. **Keep credentials private** — Never share API keys or tokens
5. **Start simple** — Don't install 10 skills on day one

## Honest Limitations

- These recommendations are based on our testing, not universal truth
- Skills change — what works today may break tomorrow
- We can't predict your exact costs
- Security is always your responsibility

## Next Steps

1. Install the recommended skills one at a time
2. Test each skill before moving to the next
3. Join the OpenClaw community for help
4. Check back at Skill Oracle for new curated skills

## Pro Templates Available

"""
        for name, info in PRO_TEMPLATES.items():
            guide += f"- **{name.replace('-', ' ').title()}** ({info['available_in']}): {info['description']}\n"

        guide += f"""
---

*Built by CertainLogic. We recommend skills we've tested. You verify before trusting.*
*This guide was generated automatically. Review all recommendations before acting.*
"""
        return guide

    def save_guide(self, guide: str, filename: Optional[str] = None) -> Path:
        """Save guide to workspace."""
        if filename is None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
            filename = f"onboarding-guide-{timestamp}.md"

        path = self.output_dir / filename
        path.write_text(guide, encoding="utf-8")
        return path

    def run(self, goal_input: Optional[str] = None) -> Path:
        """Run the full onboarding flow."""
        print("=" * 60)
        print("CertainLogic Onboarding Wizard v1.0.0")
        print("=" * 60)
        print()
        print("This wizard asks questions, then generates a personalized starter guide.")
        print("Nothing auto-installs. You follow the guide manually.")
        print()

        # Detect or ask for goal
        if goal_input:
            goal = self.detect_goal(goal_input)
            if goal:
                print(f"Detected goal: {GOAL_PROFILES[goal]['title']}")
            else:
                print(f"Could not match '{goal_input}' to a known goal.")
                goal = self._interactive_goal_select()
        else:
            goal = self._interactive_goal_select()

        if not goal:
            print("No goal selected. Exiting.")
            sys.exit(1)

        profile = GOAL_PROFILES[goal]
        print(f"\nGoal: {profile['title']}")
        print(f"I'll ask {len(profile['follow_up_questions'])} quick questions...")
        print()

        # Ask follow-up questions
        answers = []
        for q in profile['follow_up_questions']:
            answer = self.ask_question(q)
            answers.append(answer)

        # Generate guide
        print("\nGenerating your personalized starter guide...")
        guide = self.generate_guide(goal, answers)

        # Save
        path = self.save_guide(guide)
        print(f"\n✅ Guide saved to: {path}")
        print(f"\nNext step: Read the guide, then install skills one at a time.")
        print("Remember: Scan with Vetter Plus before installing anything.")

        return path

    def _interactive_goal_select(self) -> Optional[str]:
        """Show goals and let user pick."""
        print("Available goals:")
        for i, (key, profile) in enumerate(GOAL_PROFILES.items(), 1):
            print(f"  {i}. {profile['title']} ({key})")
        print()

        try:
            choice = input("Enter number or goal name: ").strip().lower()
        except EOFError:
            return None

        # Number selection
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(GOAL_PROFILES):
                return list(GOAL_PROFILES.keys())[idx]

        # Name matching
        return self.detect_goal(choice)

    def list_stacks(self):
        """Print all available starter stacks."""
        print("CertainLogic Onboarding Wizard — Available Starter Stacks")
        print("=" * 60)
        print()

        for goal, profile in GOAL_PROFILES.items():
            print(f"\n{profile['title']} ({goal})")
            print("-" * 40)
            for skill in profile['recommended_skills']:
                print(f"  • {skill['name']} — {skill['reason']}")
            print(f"  Skills: {len(profile['recommended_skills'])}")

        print(f"\n\nPro Templates:")
        for name, info in PRO_TEMPLATES.items():
            print(f"  • {name.replace('-', ' ').title()} — {info['description']} ({info['available_in']})")


def main():
    parser = argparse.ArgumentParser(
        description="CertainLogic Onboarding Wizard — Generates personalized starter guides"
    )
    parser.add_argument(
        "goal",
        nargs="?",
        help="Your goal (developer, business, research, productivity, beginner)"
    )
    parser.add_argument(
        "--list-stacks",
        action="store_true",
        help="List all available starter stacks"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Directory to save generated guides (default: ~/.openclaw/workspace/onboarding-guides)"
    )

    args = parser.parse_args()
    wizard = OnboardingWizard(output_dir=args.output_dir)

    if args.list_stacks:
        wizard.list_stacks()
        return

    wizard.run(goal_input=args.goal)


if __name__ == "__main__":
    main()
