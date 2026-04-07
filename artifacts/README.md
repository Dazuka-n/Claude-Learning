<!-- ████████████████████████████████  HEADER  ████████████████████████████████ -->

<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=3,11,19&height=220&section=header&text=Claude%20Artifacts%20Showcase&fontSize=52&fontColor=ffffff&fontAlignY=40&desc=Three%20Production%20Tools%20%C2%B7%20Powered%20by%20the%20Claude%20API%20%C2%B7%20BYOK&descAlignY=64&descSize=17&animation=fadeIn&stroke=818CF8&strokeWidth=1" width="100%"/>

</div>

<div align="center">

[![Claude](https://img.shields.io/badge/Claude-Sonnet_4.5-D97757?style=for-the-badge&logo=anthropic&logoColor=white)](https://www.anthropic.com)
[![BYOK](https://img.shields.io/badge/BYOK-Bring_Your_Own_Key-22C55E?style=for-the-badge)](.)
[![No Backend](https://img.shields.io/badge/No_Backend-100%25_Static_HTML-818CF8?style=for-the-badge)](.)
[![Artifacts](https://img.shields.io/badge/Artifacts-3_Tools-E11D48?style=for-the-badge)](.)

</div>

---

## 🎯 What This Is

Three single-file HTML artifacts that demonstrate **prompt engineering, system prompt design, and direct Claude API integration** — all running entirely in the browser. Each artifact has two sides:

- **Left — Skill Panel:** the system prompt, memory design, prompt strategy, and Claude features used. The "engineering" is visible.
- **Right — Live Tool:** the actual working interface that calls the Claude API with whatever the user types.

A "See what Claude is being told →" button on every tool lets visitors inspect the **exact** system prompt and user message being sent. This shows the *skill*, not just the *output*.

> **Built as a public showcase.** These artifacts ship with a **Bring Your Own Key (BYOK)** flow so anyone can try them with their own Anthropic credits — no proxy server, no exposed keys.

---

## 🧰 The Three Artifacts

### 1. README Generator — `readme-generator.html`

<div align="center">

[![Theme](https://img.shields.io/badge/Theme-Dark_Terminal-0c0e12?style=flat-square)](.)
[![Output](https://img.shields.io/badge/Output-Markdown-181717?style=flat-square)](.)
[![Live Chat](https://img.shields.io/badge/Live_Chat-claude.ai_project-D97757?style=flat-square)](https://claude.ai/project/019d66fd-fb9d-7040-8d77-678792e41574)

</div>

**What it does:** Takes a structured form (project name, type, description, tech stack, license) and produces a complete, GitHub-flavoured README with badges, sections, and emoji headers — written in the right tone for the project type.

**Inputs:**
- Project name
- Project type — Library / CLI Tool / REST API / Web App / AI Agent
- One-line description
- Tech stack (free text)
- License (MIT, Apache 2.0, GPL-3.0, ISC, Proprietary)

**Prompt engineering technique:** Conditional tone routing. The system prompt branches based on `project_type`:
> *library = formal/precise · tool = friendly/practical · api = concise/developer-focused · webapp = inviting · agent = innovative*

**System prompt highlights:**
- Role priming: *"senior open-source developer and technical writer"*
- Explicit section list (must include in order): title with emoji → badges → description → ✨ Features → 🚀 Installation → 💻 Usage → 🛠️ Tech Stack table → 🤝 Contributing → 📄 License
- Output discipline: *"Output ONLY raw markdown. No commentary, no code fences."*
- Realistic shields.io badges generated for the stack

**Output:** Plain markdown in a copy-to-clipboard panel.

---

### 2. ATS Resume Builder — `ats-resume-builder.html`

<div align="center">

[![Theme](https://img.shields.io/badge/Theme-Editorial_Light-f5f3ef?style=flat-square)](.)
[![Output](https://img.shields.io/badge/Output-ATS--safe_text-1F2A44?style=flat-square)](.)
[![Live Chat](https://img.shields.io/badge/Live_Chat-claude.ai_project-D97757?style=flat-square)](https://claude.ai/project/019d3f62-3133-718f-8a4e-b6c4f76f171e)

</div>

**What it does:** Takes a job description + the candidate's raw experience and rewrites a complete resume tuned to beat Applicant Tracking Systems — pulling exact keywords from the JD and mirroring them into quantified bullets.

**Inputs:**
- Job description (full paste)
- Candidate name + target role
- Raw experience (free text — bullets or prose)
- Skills (comma-separated)
- Seniority level (Entry / Mid / Senior / Lead / Director+)

**Prompt engineering technique:** Two-pass reasoning compressed into a single call. The system prompt instructs Claude to:
1. **Extract** the top 10–15 ATS keywords from the JD
2. **Rewrite** the candidate's bullets using those exact keywords
3. **Quantify** every achievement (invent plausible numbers if needed)
4. **Format** in ATS-safe plain text — no tables, columns, or special characters

**System prompt highlights:**
- Role priming: *"15 years of experience helping candidates land interviews"*
- Strict structure enforced: NAME → contact line → PROFESSIONAL SUMMARY → CORE SKILLS → PROFESSIONAL EXPERIENCE → EDUCATION
- Action verb whitelist: *Led, Architected, Delivered, Optimized, Reduced, Scaled, Drove, Built*
- Anti-pattern guard: *"No tables, columns, graphics, or special characters — ATS cannot parse them"*

**Output:** ATS-safe plain text resume in a single copyable block.

---

### 3. Social Post Scheduler — `social-post-scheduler.html`

<div align="center">

[![Theme](https://img.shields.io/badge/Theme-Modern_Cards-fdfcfa?style=flat-square)](.)
[![Output](https://img.shields.io/badge/Output-JSON_→_Cards-3E6AA7?style=flat-square)](.)
[![Live Chat](https://img.shields.io/badge/Live_Chat-claude.ai_project-D97757?style=flat-square)](https://claude.ai/project/019d5271-25a5-769a-82e9-3f44e9593741)

</div>

**What it does:** Takes one weekly content theme and generates a full week of platform-native posts across LinkedIn, Twitter/X, Instagram, and Threads — each one written in that platform's specific tone, never duplicated, scheduled across Mon–Fri.

**Inputs:**
- Platform multi-select toggles (LinkedIn / Twitter/X / Instagram / Threads)
- Topic / weekly theme (free text)
- Brand voice — Authoritative / Casual / Bold / Warm / Technical
- Target audience
- Posts per platform — 3 (Mon/Wed/Fri) or 5 (Mon–Fri)

**Prompt engineering technique:** Platform-conditional tone rules + structured JSON output. The system prompt encodes per-platform rules and demands valid JSON back so the UI can render each post into its own card.

**System prompt highlights:**
- Per-platform tone matrix:
  > LinkedIn → professional, 1st-person, story arc, 150–300 words
  > Twitter/X → punchy hook, < 280 chars, CTA close
  > Instagram → visual-first, 3–5 emoji, hashtag block
  > Threads → casual, no hard sell, "talking to a smart friend"
- Anti-duplication constraint: *"NEVER use the same copy across platforms"*
- Day-of-week scheduling logic baked in
- Strict JSON output schema (no markdown fences)

**Output:** A grid of post cards, one per platform/day, each with its own copy button.

---

## 🔑 Bring Your Own Key (BYOK)

These artifacts call the Anthropic API **directly from the browser** — there is no backend, no proxy, no server. To make them safe to host publicly, every artifact ships with a built-in BYOK flow:

### How visitors use it

1. Open any of the three HTML files in a browser
2. Click the **"API Key"** button in the top-right header
   - **Amber dot** = no key set
   - **Green dot** (with glow) = key set, ready to go
3. Paste an Anthropic API key starting with `sk-ant-...`
4. Click **Save Key** → modal closes, dot turns green
5. Generate away

### Where the key lives

| Storage | Where | Who sees it |
|:---|:---|:---|
| `localStorage['anthropic_api_key']` | The user's own browser only | Nobody but the user |
| HTTP requests | Sent **directly** to `api.anthropic.com` over HTTPS | Only Anthropic's API |
| Logs / proxies / your servers | **None** | — |

The "Clear" button in the modal wipes the key from localStorage instantly.

### Under the hood

```js
fetch('https://api.anthropic.com/v1/messages', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'x-api-key': <user's key from localStorage>,
    'anthropic-version': '2023-06-01',
    'anthropic-dangerous-direct-browser-access': 'true'
  },
  body: JSON.stringify({
    model: 'claude-sonnet-4-5',
    max_tokens: 2000,
    system: SYSTEM_PROMPT,
    messages: [{ role: 'user', content: buildUserPrompt() }]
  })
});
```

The `anthropic-dangerous-direct-browser-access: true` header is what tells the Anthropic API to allow direct browser CORS calls. This is fine for BYOK because the key is the user's own — there is nothing to leak from the host.

> **Don't have a key?** A "Get one at console.anthropic.com →" link is built into the modal.

---

## 🚀 Run It Locally

No build step. No `npm install`. No backend.

```bash
# 1. Clone the repo (or just download the files)
git clone https://github.com/Dazuka-n/Claude-Learning.git
cd Claude-Learning/artifacts

# 2. Open any artifact in your browser
start readme-generator.html        # Windows
open  readme-generator.html        # macOS
xdg-open readme-generator.html     # Linux
```

That's it. Click "API Key", paste your `sk-ant-...` key, generate.

> **Tip:** For a quick local server (some browsers handle `file://` differently), run `python -m http.server 8000` and visit `http://localhost:8000`.

---

## 🧠 The Model

All three artifacts use **`claude-sonnet-4-5`** — the current stable Sonnet checkpoint. To swap models, change the `MODEL` constant near the top of the `<script>` block in each file:

```js
const MODEL = 'claude-sonnet-4-5';   // ← change to e.g. 'claude-haiku-4-5' for faster/cheaper
```

`max_tokens` is set per artifact based on output length:
- README Generator → `2000`
- ATS Resume Builder → `2000`
- Social Post Scheduler → `3000` (5 posts × 4 platforms = larger payload)

---

## 🗂️ Files

```
artifacts/
├── README.md                      ← you are here
├── showcase-guide.md              ← private playbook (publishing, LinkedIn posts, etc.)
├── readme-generator.html          ← Tool 1 — dark terminal aesthetic
├── ats-resume-builder.html        ← Tool 2 — light editorial aesthetic
└── social-post-scheduler.html     ← Tool 3 — modern card aesthetic
```

Each `.html` file is **fully self-contained** — HTML, CSS, JS in one file, with Google Fonts loaded via CDN. Drag any file onto a browser tab and it works.

---

## 🎨 Design Decisions

| Decision | Why |
|:---|:---|
| **One file per tool** | Drop-in portable. No bundler, no framework, no build pipeline. Anyone can fork a single file. |
| **Skill panel on the left** | Makes the prompt engineering visible. The "skill" is the prompt, not the UI. |
| **"See what Claude is being told →" button** | Total transparency. Visitors see the literal system prompt + user message, not a marketing claim. |
| **BYOK over a proxy** | Zero ongoing cost to host. No abuse risk. Anyone can self-test with their own credits. |
| **Distinct visual themes per tool** | Each tool feels like its own product. Demonstrates breadth of design + Claude application styles. |
| **Direct Anthropic API (no SDK)** | Keeps the file zero-dependency. The fetch call is the entire integration — easy to read and learn from. |

---

## 📜 Prompt Engineering Patterns Demonstrated

| Pattern | Where |
|:---|:---|
| **Role priming** | All three (`"You are a senior X with N years..."`) |
| **Conditional tone routing** | README Generator (project type → tone) |
| **Constraint-first prompting** | ATS Builder (anti-pattern guard against tables/columns) |
| **Structured output enforcement** | Social Scheduler (strict JSON schema, no fences) |
| **Two-pass reasoning in one call** | ATS Builder (extract → rewrite) |
| **Output discipline** | All three (`"Output ONLY X. No commentary."`) |
| **Per-context rule sets** | Social Scheduler (platform tone matrix) |
| **Quantification injection** | ATS Builder (forces numbers into bullets) |

---

## ⚠️ Caveats

- **CORS / browser direct access:** This requires `anthropic-dangerous-direct-browser-access: true`. The "dangerous" naming is because in a non-BYOK context, exposing your own key in client code would be a leak. With BYOK, the user is using their own key — that risk doesn't apply.
- **No conversation history:** Each generate is a single stateless API call. Add a `messages: [...]` array if you want multi-turn iteration.
- **Rate limits = the user's responsibility:** Since visitors use their own keys, they hit their own rate limits. Errors from the API are surfaced in the output area.
- **Originating chat links** point to `claude.ai/project/...` URLs. Those projects are private to the author by default — make them public from inside Claude.ai if you want visitors to actually open them.

---

## 🔗 Related

- [`../README.md`](../README.md) — the parent **Claude Learning Lab** repo (MCP integrations, custom servers, workflows, skills)
- [`./showcase-guide.md`](./showcase-guide.md) — private playbook for publishing these artifacts on LinkedIn / claude.ai / Vercel

---

<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=3,11,19&height=110&section=footer" width="100%"/>

**Built with Claude · Teeny Tech Trek**

[![Anthropic](https://img.shields.io/badge/Anthropic-Claude_API-D97757?style=flat-square&logo=anthropic&logoColor=white)](https://www.anthropic.com)
[![GitHub](https://img.shields.io/badge/GitHub-Dazuka--n-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/Dazuka-n)

> *Build small. Launch fast. Scale smart.*

</div>
