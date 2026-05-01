# CertainLogic Onboarding Wizard

**Guided setup for new OpenClaw users** — Not automation, just a structured starting point.

v1.0.0

---

## What It Actually Does

This is a **guided questionnaire and recommendation system.** It:

- Asks about your goals (not detects — you tell it)
- Recommends a curated starter stack based on your answers
- Links to safety checks you run yourself
- Provides a personalized markdown guide you follow manually

**This is NOT an installer.** Every step requires your action.

## What It Does NOT Do

| ❌ Not This | ✅ What It Actually Is |
|-------------|------------------------|
| Auto-installs skills | Gives you a list. You install manually. |
| Scans your environment | Asks you questions. You answer. |
| Guarantees safety | Recommends skills we've tested. You verify. |
| Sets up API keys | Tells you what's needed. You handle credentials. |
| Runs benchmarks | Links to our benchmark repos. You run them if you want. |

## How to Use

```bash
clawhub install certainlogic-onboarding-wizard
```

Then tell your agent your goal:
- "I'm a freelance developer"
- "I need a small business assistant"
- "I want to research markets"

Your agent will ask 3-5 questions, then generate a personalized starter guide.

## Goal-Based Starter Stacks (Curated, Not Automatic)

| Goal | Recommended Skills | Why |
|------|-------------------|-----|
| Coding / Development | Context TokenReducer + GitHub skill | Cost control + repo access |
| Personal Productivity | PA Pack + Skill Oracle + TokenReducer | Curated workflow tools |
| Small Business | Vetter Plus + PA Pack + TokenReducer | Security check + productivity |
| Research | Skill Oracle + TokenReducer + Search skills | Quality sources without bloat |
| Just Starting | Vetter Plus + Skill Oracle + TokenReducer | Safe foundation |

**Important:** "Recommended" means we've tested these and they worked for us. Your mileage may vary. Vetter Plus catches obvious issues but misses subtle ones.

## What "Safety Checks" Really Means

The wizard does NOT run security scans. It:

1. Suggests you install Vetter Plus
2. Suggests you run `python3 scripts/vetter.py` on any skill before installing
3. Reminds you to check SKILL.md files for limitations
4. Links to our [hallucination benchmark repo](https://github.com/CertainLogicAI/hallucination-benchmark) if you want to test your setup

**You do the checking. The wizard just reminds you to do it.**

## Free vs Pro

**Free (this skill)**
- Goal questionnaire + curated recommendations
- Markdown starter guide generation
- Links to safety tools
- Works forever, no limits

**Pro ($29 one-time)**
- Custom industry templates
- Advanced configuration guidance
- Middleware integration notes (Pathfinder, Hallucination Guard)
- Priority support

## Honest Example Output

After onboarding you'll get a markdown file like:

```markdown
# Your OpenClaw Starter Guide (Coding Focus)

## Recommended Skills
1. Context TokenReducer — helps manage session size
2. GitHub skill — repository access
3. Vetter Plus — security pre-check

## Setup Steps
1. Install Vetter Plus: `clawhub install skill-vetter-plus`
2. Scan skills before installing (see Vetter Plus docs)
3. Install TokenReducer: `clawhub install token-reduction-engine-v2`
4. Set up GitHub token in your environment

## Cost Expectations
- Vetter Plus: Free
- TokenReducer: Free
- GitHub skill: Free
- Your API costs: Variable (depends on usage)

## Important Caveats
- TokenReducer manages session size but doesn't reduce API costs directly
- Vetter Plus catches obvious issues, not all security problems
- You must verify every skill before trusting it
```

**This is what you get:** A personalized markdown guide. Nothing auto-installs.

## Transparent Limitations

| Limitation | What That Means |
|------------|----------------|
| Markdown-only | No scripts, no automation. Your agent reads the guide, you execute. |
| Recommendations are opinions | What worked for us may not work for you. Always test. |
| No environment detection | We ask, you answer. We can't scan your system. |
| No guaranteed savings | TokenReducer manages sessions. Actual cost depends on your usage. |
| Security is your job | We recommend Vetter Plus. You must run it and interpret results. |

## Prerequisites

- OpenClaw installed
- Basic familiarity with `clawhub install`
- Willingness to read SKILL.md files before installing anything

## Links

- [CertainLogic Skills on ClawHub](https://clawhub.ai/certainlogicai)
- [Hallucination Benchmark](https://github.com/CertainLogicAI/hallucination-benchmark) — our test cases, not a guarantee
- [Vetter Plus](https://clawhub.ai/certainlogicai/skill-vetter-plus) — free security scanner
- [Skill Oracle](https://clawhub.ai/certainlogicai/skill-oracle) — curated skill recommendations

---

*Built by CertainLogic. We recommend skills we've tested. You verify before trusting.*

### Version
latest v1.0.0

### Runtime Requirements
OpenClaw + ability to follow markdown instructions
