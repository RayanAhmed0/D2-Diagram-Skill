---
name: d2
description: Generate clean, modern, professional diagrams using D2 (d2lang.com). Use for any diagram request — architecture, sequence, ERD/SQL, UML, C4, flowchart, state machine, grid/matrix, org chart, or general graphs. Produces both the .d2 source and renders it to SVG/PNG. Trigger when the user asks to draw, design, diagram, visualize, or sketch a system, flow, schema, or relationship.
---

# D2 — Modern Diagram Generation

D2 is a text-to-diagram language that produces clean, professional diagrams from declarative source. This skill generates idiomatic D2 source and renders it to SVG/PNG.

## When to use

Use this skill whenever the user wants to:
- Draw / design / diagram / visualize / sketch a system, flow, or relationship
- Produce an architecture, sequence, ERD, UML, C4, flowchart, state, or org diagram
- Render a graph of nodes and edges with labels
- "Make a diagram of..." / "draw..." / "show me how X works"

Do NOT use for: mind maps, Gantt charts, Sankey, Venn, or geographic maps (D2 deliberately doesn't support these — use a different tool). For mathematical charting (plots, bar charts), reach for matplotlib/Plotly instead.

## What this skill produces

For every request, produce BOTH:
1. A `.d2` source file (idiomatic, formatted, commented where helpful)
2. A rendered `.svg` (default) or `.png` (when the user wants a raster)

Use the `render.py` helper in this folder — it applies the professional defaults (theme, layout, padding) for you. See **Rendering** below.

---

## Core workflow

1. **Pick a diagram family** from the table below. Start from the matching template in `templates/`.
2. **Set `direction`** at the top: `right` for pipelines/process flows, `down` for org/hierarchy.
3. **Pick a theme.** Ask the user which palette they want (see *Theme selection* below) — this is the one creative choice that most defines the look, and the only place you'll set `vars.d2-config` (see *Professional defaults* for the canonical block). **Never set `dark-theme-id` unless the user explicitly asks for a dark variant** — it bakes a `prefers-color-scheme: dark` switch into the SVG that silently flips the colors under OS dark mode.
4. **Write the model** (shapes + connections). Keep labels short.
5. **Apply aesthetics via `classes:`** — never inline hex colors (breaks dark mode, fights the theme).
6. **Render** with `python render.py <file.d2>` (or `python render.py <file.d2> --png`).

---

## Theme (color palette) — ask the user first

Before writing the diagram, ask the user which palette they want. This is the one creative choice that most defines the look — don't silently default it. Use the `AskUserQuestion` tool:

- **Question:** "Which color palette for this `<family>`?"
- **Options** (the user can also pick **Other** to name a vibe — "dark", "playful", "warm" — or any ID from the catalog below):
  1. **Cool classics** — blues/grays, modern corporate (`theme-id: 4`) *(Recommended)*
  2. **Mixed berry blue** — modern + vibrant (`theme-id: 5`)
  3. **Dark mauve** — clean modern dark UI (`theme-id: 200`)
  4. **Topic-matched — you pick based on the subject** (see table below)

Skip the question only when the user has already named a palette, theme ID, or aesthetic ("use dark mode", "make it vibrant", "match our brand blue") in their request.

**Don't bundle dark mode into a palette option.** "Match brand + dark-mode aware" is two choices — the user expects the brand color, not an OS-triggered dark flip. If you want dark mode, ask it as a separate yes/no question *after* the palette choice.

**When the user picks "Topic-matched" for a diagram about a real product, company, or technology**, web-search *that subject's* brand color and apply it via `theme-overrides` on a stock light theme (usually `4`). Do not silently ship the unmodified theme — that ignores the choice the user just made. Build a `B1`–`B6` ramp from the primary color (primary → progressively lighter). Source brand hexes from the subject's own brand-guidelines page when available.

**Same subject — also search for its logo.** For any diagram about a real product, service, or technology, search for that subject's official transparent logo (PNG or SVG with alpha), save it under `diagrams/icons/`, and reference via relative path on the relevant shapes via the `icon:` property. Simple Icons (`https://cdn.jsdelivr.net/npm/simple-icons@v16/icons/<slug>.svg`, CC0 monochrome SVGs) is a reliable source; brand-guidelines pages often have colored versions. If no clean icon exists, fall back to a meaningful D2 shape (`person`, `package`, `document`) — don't ship a broken or ugly icon.

### Topic-matched palette picker

When the user picks **Topic-matched** (or says "surprise me" / "you choose"): default to `4`. Reach for `1` (neutral grey) for clinical, science, or government work; `5` for vibrant contexts (creative, data, marketing); `3` for slide decks and polished brand collateral; `303` for C4 architecture reviews. For subjects with strong brand colors (a specific company, holiday, sports team), web-search the hex values and apply them via `theme-overrides` rather than swapping themes. Dark themes (`200`, `201`) are **opt-in only** — never set `dark-theme-id` unless the user has explicitly approved a dark variant for this specific diagram.

### Full palette catalog

D2 ships 19 themes — run `d2 themes` for the live list with previews. The professional picks:

| ID | Name | Vibe |
|---|---|---|
| `1` | Neutral grey | Cleanest, most neutral. Healthcare/science/gov. |
| `3` | Flagship Terrastruct | D2's own modern branded look. |
| `4` | Cool classics | Blues/grays, modern corporate. **Default.** |
| `5` | Mixed berry blue | Berry + blue, modern vibrant. |
| `8` | Colorblind clear | Accessibility-first. Use when colorblind readers are likely. |
| `200` | Dark mauve | Clean dark. Pairs with OS dark mode. |
| `201` | Dark Flagship Terrastruct | Dark version of `3`. Modern dev tooling. |
| `303` | C4 | C4 architecture diagrams only. |

For distinctive topic-native looks (sustainability greens `104`, earth tones `103`, warm education `101`, aubergine `7`), check `d2 themes` and pick by vibe. Avoid `0` (barebones), `6`/`102` (over-saturated), and the novelty terminal/origami themes for professional work.

### Custom palette via `theme-overrides`

If the topic calls for specific colors the theme doesn't ship (brand colors, sustainability greens, seasonal palettes), override individual slots — this keeps dark-mode pairing intact instead of fighting it with inline `style.fill` hex:

```d2
vars: {
  d2-config: {
    theme-id: 4
    theme-overrides: {
      B1: "#2E7D32"   # base/sequential — greens
      B2: "#66BB6A"
      B3: "#A5D6A7"
      B4: "#C5E1A5"
      B5: "#E6EE9C"
    }
    dark-theme-overrides: {
      # same key shape — used when OS dark mode is active
    }
  }
}
```

**Slot names:** `B1`–`B6` = base/sequential colors (the main palette), `AA2`/`AA4`/`AA5` = accent A, `AB4`/`AB5` = accent B, `N1`–`N7` = neutrals (darkest → lightest). Not every slot is used by every theme. **Quote hex values** — `#` starts a comment in D2.

---

## Diagram families → templates

| Family | When to use | Template |
|---|---|---|
| Architecture / system design | Boxes-and-arrows service diagram, cloud arch, deployment | `templates/architecture.d2` |
| Sequence diagram | "Who talks to whom, in what order" — request/response, protocol exchange | `templates/sequence.d2` |
| ERD / database schema | Tables with PK/FK, columns, relationships | `templates/erd.d2` |
| UML class diagram | OOP design, inheritance, fields/methods, multiplicity | `templates/uml_class.d2` |
| C4 (Context/Container/Component) | Multi-level architecture abstraction | `templates/c4_context.d2` |
| Flowchart / decision tree | Branching logic, process steps | `templates/flowchart.d2` |
| State machine | States + transitions (initial, final, events) | `templates/state.d2` |
| Grid / matrix / table | 2D layout (comparison matrix, periodic table, map) | `templates/grid_matrix.d2` |
| Reusable styles | Shared `classes.d2` (the "CSS") imported by other diagrams | `templates/classes.d2` |

The `templates/classes.d2` file is special — it defines the visual language (service / database / external / queue classes). Spread-import it (`...@classes`) into any diagram for consistent styling across the project.

---

## Professional defaults — always apply these

These three choices turn a default-looking D2 render into a polished one:

```d2
vars: {
  d2-config: {
    theme-id: 4           # was: 0 (barebones). 4 = Cool classics — blues/grays, modern
    layout-engine: elk    # was: dagre. ELK = cleaner orthogonal lines + precise column connections
    pad: 60               # was: 100 default. 60 = tighter, more slide-friendly
  }
}
```

**Theme picker** — ask the user first (see *Theme selection* above for the full catalog and the AskUserQuestion flow). Safe quick-pick when you must default silently: `4` Cool classics (light).

---

## Design principles — what makes the output "professional"

Distilled from D2's own design philosophy. Apply these to every diagram.

### Hierarchy & scope
- **3–7 elements per board.** Past that, split with `layers` (zoom-in), `scenarios` (alt states), or `steps` (build-up).
- **Containers** express ownership/deployment boundaries — flatten when there's no real parent/child.
- Don't mix abstraction levels in one board (a pod next to a cloud region = visual noise).
- Don't nest more than 3 levels deep.

### Labels
- **Edges use verbs**: `calls`, `reads`, `publishes to`, `depends on`. Never full sentences.
- **Protocol/mechanism in brackets on its own line**: `"Makes API calls to\n[JSON/HTTPS]"` (C4 convention).
- **Markdown labels** (`shape: rectangle` + `|md ... |`) for shapes needing title + subtitle + description.
- Don't label an edge with the destination's name.

### Color discipline
- **Default theme colors first**. Reach for explicit colors only when they encode information.
- **Use `class:` for semantic categories** (e.g., `customer-facing`, `internal`, `external`). One class = one concept.
- **No high-saturation inline hex fills on shapes** (`style.fill: "#FF0000"`) — they bypass theme color-coding and fight the palette. **Pastel container tints are encouraged for grouping** (`#E6F2FF`, `#FFF4E6`, `#F5F0FF`, `#EEFBF6` — pick a hue matching the brand). Works because we ship light-only by default.
- **≤5 color categories** — readers can't hold more in working memory.
- **Add a legend only when a visual signal (fill color, icon, `3d`, `multiple`) encodes meaning that ISN'T already shown by an adjacent text label.** `d2-legend: "" { near: bottom-right }` auto-populates from those signals. Skip it when:
  - The colored shape already has a label saying the same thing (e.g., a container tinted cream with the label "Morning" — the legend would just repeat "cream = Morning").
  - The only styling is border-radius / stroke-width / shadow (no fills/icons — the legend renders as an empty box).
  - There's only one color category (a single entry isn't a legend, it's a footnote).
  A diagram with 3 tinted containers labeled "Morning"/"Workday"/"Evening" does not need a legend. A diagram with 12 service boxes colored by class (`customer-facing` / `internal` / `external`) with per-service labels does — the colors carry info the labels don't.

### Direction
- Pick ONE direction per board. `right` for pipelines and process flows. `down` for org charts and hierarchies.
- Mixing directions creates visual noise.

### Shape vocabulary — match the shape to the concept

Don't default everything to `rectangle`: `package` (product/boundary), `hexagon` (process/service), `document` (served doc/config), `page` (output/deliverable), `cylinder` (persistent store), `stored_data` (stateful cache), `cloud` (external SaaS), `diamond` (decision), `parallelogram` (I/O), `person` (human actor), `rectangle` (generic default). Full inventory in the syntax cheat-sheet below.

### Animation — only on actual data flow

`style.animated: true` on an edge draws a moving dash that conveys runtime traffic. Use it on edges where data really does flow at runtime (request paths, event streams, SSE). **Do not animate static dependency edges** — composition relationships, "contains", "depends on at compile time" — animation would lie about what's happening.

```d2
client -> gateway: "invoke API" {
  style.animated: true
}
```

### Connections
- `->` calls / depends, `<->` bidirectional (DB read/write), `--` undirected association.
- `style.animated: true` only in animated renders — never on static output.
- Route nuance through edge labels, not extra "explanation" nodes.

### What to avoid
- ❌ Inline hex colors (breaks dark mode)
- ❌ `--sketch` for compliance/enterprise/client work (whiteboard vibe only)
- ❌ `animated: true` on static diagrams
- ❌ >1000 nodes in one board (split or use a different tool — D2 is whiteboard-fit)
- ❌ Mixing directions in one board
- ❌ Sentence-long edge labels
- ❌ Bare default theme (`theme-id: 0`) for professional output

---

## Syntax cheat-sheet (most-used)

### Shapes
```d2
# Bare key = rectangle (default). Key = label unless aliased.
api              # rectangle labeled "api"
db: PostgreSQL   # rectangle labeled "PostgreSQL", key "db"
cache: Redis {shape: cylinder}    # cylinder shape
user: Customer {shape: person}    # stick figure
external: Stripe {shape: step}    # step / process
```

Full shape list: `rectangle` (default), `square`, `oval`, `circle`, `cylinder` (DB), `person`, `cloud`, `diamond` (decision), `hexagon`, `page`, `package`, `queue`, `step`, `callout`, `stored_data`, `parallelogram`, `document`, `c4-person`. Plus special: `text`, `image`, `sql_table`, `class`, `sequence_diagram`, `code`.

### Connections
```d2
a -> b              # directed
a <-> b             # bidirectional
a -- b              # undirected
a -> b: label       # labeled
a -> b: hi { style.stroke-width: 3 }   # styled
a -> b: { source-arrowhead: 1; target-arrowhead: * }
```

### Containers
```d2
cloud: {
  api -> db
}
client -> cloud.api: HTTPS
```

### Style (use sparingly — prefer classes)
```d2
classes: {
  service: {
    style: {
      fill: white
      stroke: blue
      stroke-width: 2
      border-radius: 8
      shadow: true
    }
  }
}
api.class: service
```

Style keys: `fill`, `stroke`, `stroke-width` (1-15), `stroke-dash` (0-10), `border-radius` (0-20, 999=pill), `shadow`, `opacity` (0-1), `font-color`, `font-size`, `bold`, `italic`, `underline`, `animated`, `fill-pattern` (`dots`/`lines`/`grain`/`none`), `3d`, `multiple`, `double-border`.

**Quote hex colors** (`#` starts a comment): `style.fill: "#f4a261"`.

### Markdown labels (C4-style hierarchy)
```d2
api: |md
  ## API Gateway
  [Service]

  Receives all external traffic, routes to backend services.
| { shape: rectangle }
```

Markdown always goes on the shape itself — putting `label: |md ... |` inside a container declaration silently fails and renders an empty box.

### Icons
```d2
db: { icon: https://icons.terrastruct.com/tech%2F019-cloud-database.svg }
logo: { shape: image; icon: https://example.com/logo.svg; width: 120; height: 120 }
```

Icon libraries at `https://icons.terrastruct.com/`: `aws/`, `azure/`, `gcp/`, `tech/`, `dev/`, `infra/`, `essentials/`. URL-encode `/` as `%2F` and spaces as `%20`.

### Local icon library — check first

`diagrams/icons/` holds ~44 generic icons (database, server, cloud, queue, pipeline, lock, gear, sync, etc.) in a consistent navy-on-light-blue style. **Glob it before reaching for external URLs**:

- List available icons: `ls diagrams/icons/` (or glob `diagrams/icons/*.svg`)
- Use: `db: PostgreSQL { icon: icons/database.svg }` (path is relative to the `.d2` file — keep diagrams inside `diagrams/` so paths resolve)

Fall back to the Terrastruct URL catalog above or brand logos via Simple Icons only when no local icon fits. If you do fetch a brand logo for a one-off subject, save it under `diagrams/icons/` so it's reusable next time (see brand-logo guidance earlier in this file).

### Title and legend
```d2
title: |md # System Architecture | { near: top-center }
d2-legend: "" { near: bottom-right }   # auto-populates from styles in use
```

---

## Specialized diagram syntax (quick reference)

### Sequence diagram
```d2
shape: sequence_diagram
client -> api: GET /order
api -> db: query
api <- db: rows { style.stroke-dash: 5 }   # dashed = response
api -> client: 200 OK
```
- Solid: `->`, `<-`. Dashed (responses): add `style.stroke-dash: 5`.
- Self-message: `api -> api: retry`.
- Groups: wrap messages in a plain container.
- **Order matters** — only place in D2 where source order is preserved.

### SQL table (ERD)
```d2
users: {
  shape: sql_table
  id: int { constraint: primary_key }
  email: text { constraint: unique }
  org_id: int { constraint: foreign_key }
}
orgs: {
  shape: sql_table
  id: int { constraint: primary_key }
}
users.org_id -> orgs.id        # connect FK column → PK column
```
Constraints: `primary_key` (PK), `foreign_key` (FK), `unique` (UNQ). Multiple: `constraint: [primary_key; unique]`.

### UML class
```d2
Animal: {
  shape: class
  +name: string
  +age: int
  +eat(): void
}
Dog -> Animal: {
  target-arrowhead.shape: triangle
  target-arrowhead.style.filled: false
}
```
- Visibility: `+` public, `-` private, `\#` protected (escape `#`!).
- Methods detected by `(` in key.
- Inheritance: `target-arrowhead.shape: triangle` + `style.filled: false`.
- Composition: `source-arrowhead.shape: diamond` + `style.filled: true`.
- Aggregation: same, `style.filled: false`.
- Multiplicity: `source-arrowhead: 1..*`, `target-arrowhead: 0..1`.

### Grid / matrix
```d2
grid-rows: 3
grid-columns: 3
grid-gap: 0
# Cells fill row-by-row (or column-by-column if you list grid-columns first)
```

---

## Multi-board composition (when one board isn't enough)

```d2
# Root board
client -> api -> db

layers: {
  Network: { ... }     # blank board — completely different objects
  Deployment: { ... }
}

scenarios: {
  Failover: {          # inherits root + modifies
    db.style.opacity: 0.3
    client -> replica: emergency fallback
  }
}

steps: {               # for build-up animation
  1: { client -> api }
  2: { api -> db }     # inherits step 1
}
```

| Keyword | Inherits | Use for |
|---|---|---|
| `layers` | Nothing (blank) | Different abstraction levels |
| `scenarios` | Root board | What-if variants (cache hit/miss) |
| `steps` | Previous step | Sequential build-up |

Animate with `--animate-interval=1400` (SVG/GIF only — see Rendering).

---

## Rendering

### Quick render (recommended)
From the skill folder:
```bash
python render.py diagram.d2                    # → diagram.svg
python render.py diagram.d2 --png              # → diagram.png
python render.py diagram.d2 --format pdf       # → diagram.pdf
python render.py diagram.d2 --animate 1400     # animate multi-board
```

`render.py` reads `vars.d2-config` from the source (theme, layout, pad) and passes them as CLI flags. It prefers SVG, falls back to PNG only when explicitly requested, and verifies exit status (not output-file existence — D2 may write a partial render on error).

### Direct d2 CLI (when you need full control)
```bash
d2 diagram.d2                                  # → diagram.svg with defaults
d2 -t 4 --layout=elk --pad=60 diagram.d2       # professional defaults
d2 --dark-theme=200 diagram.d2                 # OPT-IN dark variant only — see Theme section
d2 --sketch diagram.d2                         # hand-drawn (casual only!)
d2 --animate-interval=1400 multi.d2 anim.svg   # multi-board animation
d2 diagram.d2 out.pdf                          # multi-page PDF (one board/page)
d2 diagram.d2 out.pptx                         # PowerPoint deck (one board/slide)
d2 diagram.d2 out.txt                          # ASCII art (beta)
d2 -w diagram.d2                               # live preview in browser
d2 fmt diagram.d2                              # format source in place
d2 validate diagram.d2                         # validate without rendering
```

### Output format → renderer
| Extension | Use when |
|---|---|
| `.svg` (default) | Web, docs, Confluence, README — supports dark mode, links, tooltips |
| `.png` | Slides, chat, anywhere SVG won't render (needs Playwright) |
| `.pdf` | Multi-page print; clickable layer links (C4 drill-down) |
| `.gif` | Animated multi-board for chat contexts |
| `.pptx` | Architecture review decks |
| `.txt` | Source-code comments, terminal-only READMEs (alpha) |

---

## Common pitfalls (read these once)

1. **Inline hex colors break dark mode.** Use `class:` + a `classes.d2` file imported with `...@classes`.
2. **`width`/`height` can't go on containers** — they auto-fit children.
3. **Hex colors must be quoted** (`"#fff"`) — `#` starts a comment.
4. **SQL relationships connect columns, not tables**: `users.org_id -> orgs.id`, not `users -> orgs`.
5. **PNG/PDF need Playwright** — first render downloads ~100MB. Flag this for users without it.
6. **TALA layout is paid/proprietary** — default to dagre (simple) or ELK (cleaner). Never emit `--layout=tala` without flagging this to the user.
7. **Spread-import paths are relative to the source file's directory.** `...@classes` only resolves when the `.d2` file sits next to `classes.d2`. From the project root (especially on Windows) the import fails with "cannot find the file." Workarounds: move the diagram next to `classes.d2`, reference the path explicitly, or inline the few classes you need.
8. **Literal `|` inside `|md ... |` block strings terminates the block.** D2's pipe-delimited multi-line strings end at the next `|` — so a markdown table cell, a regex, or even "completed | failed" inside the body will silently close the block and produce parse errors several lines later. Use `/` (slash), escape as `\|`, or rephrase.

---

## Where to look for more

- **In this skill:**
  - `templates/` — idiomatic starting points for each diagram family
  - `render.py` — rendering helper with professional defaults
- **Official docs:** https://d2lang.com/tour/
- **Playground:** https://play.d2lang.com (paste source to live-preview)
- **Theme previews:** run `d2 themes` on the CLI
- **Layout engines:** run `d2 layout` on the CLI
