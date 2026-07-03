# D2-Diagram-Skill

A Claude Code skill that generates clean, professional diagrams using [D2](https://d2lang.com).

Ask for a diagram in plain English. Claude picks the right diagram family, writes idiomatic D2 source, and renders it to SVG or PNG.

## What it does

- Handles **architecture, sequence, ERD/SQL, UML class, C4, flowchart, state machine, grid/matrix, and org chart** diagrams
- Produces both the `.d2` source and the rendered `.svg` / `.png`
- Applies professional defaults out of the box (theme, ELK layout, padding)
- Asks you which color palette fits before drawing — never silently defaults the look
- Pulls in brand colors and official logos for real-world subjects

## Requirements

- [Claude Code](https://claude.com/claude-code)
- [D2 CLI](https://d2lang.com/tour/install) 
- Python 3 (uses the bundled `render.py` helper)
- Playwright (only needed for PNG output)

## Installation

Clone into your project's `.claude/skills/` folder:

```bash
git clone https://github.com/RayanAhmed0/D2-Diagram-Skill.git .claude/skills/d2
```

Resulting structure:

```
your-project/
└── .claude/
    └── skills/
        └── d2/
            ├── SKILL.md
            ├── render.py
            └── templates/
```

## Usage

Once installed, the skill auto-triggers when you describe something to visualize. You can also invoke it explicitly with `/d2`.

Examples:

- "Draw an architecture diagram for a Node API with Postgres and Redis"
- "Make a sequence diagram for OAuth login"
- "Design an ERD for users, orgs, and memberships"
- "Visualize our checkout flow as a state machine"

The workflow:

1. **Claude asks which color palette you want** (skipped only if you already named one — "use dark mode", "match our brand blue", etc.). The four options:
   - **Cool classics** — blues/grays, modern corporate *(recommended default)*
   - **Mixed berry blue** — modern + vibrant
   - **Dark mauve** — clean modern dark UI
   - **Topic-matched** — Claude picks based on the subject, including brand colors and logos for real products
2. **Claude writes the `.d2` source file** to `diagrams/`
3. **Claude renders it** to SVG by default (or PNG if you asked)

## What you get

For every request, the skill writes:

- `diagrams/<name>.d2` — idiomatic, formatted D2 source
- `diagrams/<name>.svg` (or `.png`) — the rendered diagram

Edit the `.d2` file anytime and re-render with:

```bash
python .claude/skills/d2/render.py diagrams/<name>.d2
```
## License

MIT

