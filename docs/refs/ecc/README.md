# ECC skills — curated references

Curated copies of selected agent skills from
[affaan-m/ECC](https://github.com/affaan-m/ECC) (MIT license). Kept here as
reference material to borrow ideas and guidance during development/review.

Each folder contains the original `SKILL.md` from ECC's `.agents/skills/<name>/`.

## Index

| Skill | Purpose |
|-------|---------|
| `coding-standards/` | Baseline naming/readability/immutability review conventions |
| `security-review/` | Security review checklist for code & data handling |
| `tdd-workflow/` | Test-driven development workflow |
| `verification-loop/` | Verify changes with tests before finishing |
| `api-design/` | REST/API endpoint + validation design |
| `plan-canvas/` | Planning structure for multi-step work |

## License
These files originate from `affaan-m/ECC`, MIT licensed.
See `LICENSE` at the repo root of `agent-009.` for the MIT text / attribution.
Source: https://github.com/affaan-m/ECC

## How I (OpenHands) use these
ECC is built for Claude Code's `.agents/skills` harness. In OpenHands I already
have native skills (`code-review`, `code-simplifier`, etc.) that overlap. So I
treat these files as **reference guidance** — read a relevant one when doing
review/planning/security work — not as auto-loaded skills.