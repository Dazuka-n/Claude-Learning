# How to Showcase Your Claude Artifacts
**Teeny Tech Trek — Anisha Singla**

---

## What you have

Three production-ready HTML artifacts:
- `readme-generator.html` — dark terminal aesthetic
- `ats-resume-builder.html` — clean editorial light
- `social-post-scheduler.html` — modern card-based

Each has a **Skill Panel** (left) showing your prompt engineering + Claude features used, and a **Live Tool** (right) powered by the Claude API.

---

## Step 1 — Bring Your Own Key (BYOK) is built in

Every artifact now ships with a **BYOK (Bring Your Own Key)** flow. You no longer hardcode your API key in the HTML.

**How it works for any user who opens the artifact:**

1. They click the **"API Key"** button in the top-right header (amber dot = no key set, green dot = key set)
2. A modal opens — they paste their own `sk-ant-...` key
3. The key is saved to their browser's `localStorage` only — it never touches your servers, never gets logged, and is sent **directly** to `api.anthropic.com`
4. A friendly "Clear" button lets them remove it at any time

This means you can host the artifacts **publicly** without ever exposing your own API key. Anyone testing the demo uses their own Anthropic credits.

**Under the hood**, each artifact sends:

```js
headers: {
  'Content-Type': 'application/json',
  'x-api-key': <user's key from localStorage>,
  'anthropic-version': '2023-06-01',
  'anthropic-dangerous-direct-browser-access': 'true'
}
```

**Want a hosted demo where YOU pay?** Set up a thin proxy (Cloudflare Worker / Vercel Edge Function) that injects your key server-side, and point the fetch URL at the proxy. BYOK is the right default though — it's the safest path for a public showcase.

---

## Step 2 — Update the original chat link

In each artifact, find this line in the Skill Panel HTML:

```html
<a class="chat-link" href="https://claude.ai" target="_blank">
  View original claude.ai chat →
</a>
```

Replace `https://claude.ai` with the actual URL of your Claude project/chat for each tool.

---

## Step 3 — Choose your publishing method

### Option A — Publish as Claude Artifacts (recommended for showcasing Claude skills)

This is the most authentic way to show Claude ecosystem skills.

1. Open Claude.ai
2. Start a new chat
3. Paste the entire HTML content of each artifact into the chat with this prompt:

```
Please render this as an artifact:
[paste the full HTML here]
```

4. Claude will create a live artifact
5. Click the **Share** icon → **Share artifact** → copy the public link
6. The URL will be `claude.ai/artifacts/...` — this proves it lives inside the Claude ecosystem

Do this for all three. You now have three live `claude.ai` URLs.

---

### Option B — Host on Vercel / Netlify (for your TTT portfolio)

For embedding in your teenytechtrek.com portfolio:

1. Create a GitHub repo called `ttt-claude-showcase`
2. Add all three HTML files
3. Deploy to Vercel (free): `vercel --prod`
4. Set up a Cloudflare Worker to proxy Anthropic API calls (keeps key secure)
5. Embed as iFrames in your portfolio site

---

## Step 4 — Build your showcase page

Create a simple index page that links all three:

```html
<!-- ttt-showcase/index.html -->
<h1>Claude Projects by Teeny Tech Trek</h1>
<p>Three tools built inside Claude.ai using prompt engineering, 
   memory design, and the Claude API.</p>

<a href="readme-generator.html">README Generator →</a>
<a href="ats-resume-builder.html">ATS Resume Builder →</a>
<a href="social-post-scheduler.html">Social Post Scheduler →</a>
```

Or use Notion/Linktree as a quick landing page with the three artifact links.

---

## Step 5 — Write the LinkedIn post (do this for each artifact)

Template:

```
I built [Tool Name] inside Claude.ai — not as a SaaS, 
but as a demonstration of what you can do with 
prompt engineering + the Claude API.

Here's what's under the hood:
→ System prompt: [1 line description]
→ Memory design: [1 line description]  
→ Claude features: Artifacts, memory, iterative prompting

The "See what Claude is being told" button shows the 
exact prompt being sent — so you can see the skill, 
not just the output.

Live link: [your artifact URL]

Built with Claude · Teeny Tech Trek
#Claude #PromptEngineering #AI #Anthropic
```

---

## Step 6 — Showcase framing (the messaging that matters)

When someone visits your artifact, they should understand in 5 seconds:
1. This is a Claude project, not a standalone app
2. You engineered the prompts
3. They can see exactly how it works

**On LinkedIn / social:** Lead with "I trained Claude to..." not "I built an app that..."

**In client conversations:** "Here's a live demo of how I would design a Claude-powered workflow for your use case."

**In your TTT bio/portfolio:** "3 public Claude artifacts showcasing prompt engineering, memory design, and API integration."

---

## Step 7 — Update the original chat URLs

Once you have your original claude.ai chat URLs, update all three artifacts:

| Artifact | Variable to update |
|----------|-------------------|
| readme-generator.html | `href="https://claude.ai"` in skill panel |
| ats-resume-builder.html | `href="https://claude.ai"` in skill panel |
| social-post-scheduler.html | `href="https://claude.ai"` in skill panel |

---

## Quick checklist

- [ ] BYOK works locally — open each HTML, click "API Key", paste a test key, generate
- [ ] Original chat URLs updated in all three artifacts (replace `https://claude.ai`)
- [ ] All three published as Claude artifacts (get the claude.ai/artifacts/ URLs)
- [ ] LinkedIn posts drafted for each
- [ ] Showcase index page / Notion page with all three links
- [ ] TTT website updated with "Claude Projects" section

---

## BYOK testing checklist (do this once before publishing)

Open each artifact in your browser (just double-click the `.html` file) and verify:

- [ ] Top-right "API Key" button shows an **amber** dot when no key is set
- [ ] Clicking Generate without a key opens the modal automatically
- [ ] Pasting a valid `sk-ant-...` key + Save closes the modal and turns the dot **green**
- [ ] Generating actually returns a response from Claude
- [ ] Pasting an invalid string (no `sk-ant-` prefix) shows the validation alert
- [ ] Clicking "Clear" empties the field and resets the dot to amber
- [ ] Reloading the page keeps the saved key (localStorage persistence)
- [ ] An invalid/expired key shows a clear API error message in the output area

---

*Teeny Tech Trek · Build small. Launch fast. Scale smart.*
