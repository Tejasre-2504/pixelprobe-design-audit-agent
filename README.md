# 🔍 PixelProbe — AI-Powered Design Audit Agent

**"Your designs deserve a second pair of eyes — one that never sleeps."**

PixelProbe is an intelligent design audit agent that automatically reviews UI screenshots, catches design problems before your users ever see them, and autonomously navigates live websites to detect regressions. It thinks like a senior designer, reports like an engineer, and works at the speed of AI.

---

## 🤔 Why PixelProbe?

Every frontend team faces the same problem. Developers ship code. Designers can't review every pull request. Code reviewers focus on logic, not pixels. And slowly, silently — spacing breaks, contrast fails, visual hierarchy collapses.

By the time someone notices, the damage is already in production.

PixelProbe was built to close that gap. It sits in your workflow, reviews every change, and tells you exactly what broke, where it broke, and how to fix it — in seconds, not days. And with Level 3, it does all of this autonomously — no human needed.

---

## ✨ What Can It Do?

### 🎯 Level 1 — Single Page Design Analysis
Drop in any UI screenshot and PixelProbe will analyze it across 5 core design principles. It tells you what's wrong, where it is on the page, how it affects users, and exactly what to do about it. The design score is calculated mathematically from actual findings — not guessed by the AI.

### 🔄 Level 2 — Before/After Regression Analysis
Give it two screenshots — a baseline and a current version — and it will find every visual difference, classify each one as an improvement, regression, or neutral change, and flag any accessibility risks immediately. Confidence and verdict are calculated mathematically, not blindly trusted from the AI.

### 🤖 Level 3 — Autonomous UI/UX Regression Testing
PixelProbe takes full control. It launches a headless browser, logs into a target website autonomously, navigates configured pages, masks dynamic content like timestamps and ads, captures clean screenshots at a fixed viewport, and compares them against stored baselines. First run creates baselines. Every subsequent run detects regressions automatically — completing a full scan of 3 pages in under 60 seconds.

---

## 🎨 The 5 Design Principles

PixelProbe doesn't just guess. Every finding is grounded in one of five established design principles:

| Principle | What PixelProbe Checks |
|---|---|
| 👁️ **Visual Hierarchy** | Are your primary actions more prominent than secondary ones? Can users instantly tell what to do next? |
| 🎨 **Contrast (WCAG AA)** | Do your text and background combinations meet accessibility standards? Can everyone actually read your UI? |
| 📐 **Spacing** | Is your whitespace consistent? Are elements cramped or breathing properly? |
| ⚖️ **Alignment** | Are your elements aligned to a consistent grid, or visually drifting? |
| 🔗 **Consistency** | Are your colors, fonts, buttons, and icons uniform across the page? |

---

## 🧠 How It Works

PixelProbe is not just an API wrapper. It's a proper agent with a full decision pipeline.

**Level 1 Pipeline:**
📸 Input Image
↓
🛡️ Input Validator (format, size, integrity)
↓
🤖 Groq Vision LLM (analyzes 5 design principles)
↓
🔍 Output Validator (strips hallucinations)
↓
📊 Mathematical Score Calculator
↓
✅ Dark Mode HTML Report + JSON

**Level 2 Pipeline:**
📸 Baseline Image + Current Image
↓
🤖 Groq Vision LLM (finds all visual differences)
↓
🔍 Validator (checks classifications + confidence)
↓
📊 Mathematical Confidence + Verdict Calculator
↓
✅ Tabbed Comparison Report + JSON

**Level 3 Pipeline:**
⚙️ Config (URL, credentials, pages list)
↓
🌐 Playwright headless browser launches
↓
🔐 Autonomous login (form fill + submit)
↓
🗺️ Navigate each configured page
↓
🎭 Mask dynamic content (timestamps, ads, spinners)
↓
📸 Screenshot at fixed viewport
↓
First run  → Save as baseline
Next runs  → Compare with baseline
↓
✅ Master Report + Per-page Regression Reports

Every step is logged. Every decision is traceable. If something goes wrong, PixelProbe tells you exactly what failed and why — it never silently skips anything.

---

## 🛡️ Production-Grade Guard Rails

PixelProbe was built with the same standards you'd expect from a production system:

- **Anti-hallucination validation** — every finding is checked against strict rules before it reaches you. Vague or unsupported findings are automatically rejected.
- **Mathematical scoring** — design scores and confidence values are calculated from actual findings, not trusted from AI output which tends to default to round numbers.
- **Confidence scoring** — every finding comes with a confidence score (0–100%). Critical findings require ≥75% confidence to pass validation.
- **Retry logic** — if the API call fails, PixelProbe retries up to 3 times with exponential backoff before reporting a failure.
- **Graceful error handling** — 403s, 429s, timeouts, and malformed responses are all caught, logged, and surfaced clearly.
- **Dynamic content masking** — Level 3 hides timestamps, ads, and session tokens before capturing screenshots to prevent false positives.
- **Full execution log** — every action the agent takes is logged with a timestamp and severity level, visible right in the HTML report.

---

## 📊 Sample Output

**Level 1 Terminal Output:**
============================================================
🔍 PixelProbe — AI-Powered Design Intelligence
✨ Catching design issues before your users do.
📸 Analyzing: sample_images/test.png
[2026-06-07T10:00:33] [INFO] Starting design audit...
[2026-06-07T10:00:33] [INFO] Input validation passed.
[2026-06-07T10:00:36] [INFO] Groq Vision API call successful.
[2026-06-07T10:00:36] [INFO] 7 findings returned. Validating...
[2026-06-07T10:00:36] [INFO] Design score calculated: 74/100
✅ AUDIT COMPLETE
📊 Overall Score   : 74/100
🔍 Total Findings  : 7
🔴 Critical        : 1
🟠 High            : 2
🟡 Medium          : 3
🟢 Low             : 1

**Level 2 Terminal Output:**
============================================================
🔍 PixelProbe — Before/After Regression Analysis
✨ Detecting regressions before they reach your users.
📸 Baseline : sample_images/before.png
📸 Current  : sample_images/after.png
✅ Overall Verdict       : NEUTRAL
📊 Overall Confidence   : 78%
🔍 Total Differences    : 7
✅ Improvements         : 2
❌ Regressions          : 3
♿ A11y Regressions     : 0

**Level 3 Terminal Output:**
============================================================
🤖 PixelProbe — Level 3: Autonomous Regression Testing
✨ Navigating, capturing, comparing — fully autonomous
✅ [INFO] Launching browser...
✅ [INFO] Browser launched successfully.
✅ [INFO] Navigating to login page...
✅ [INFO] Login successful!
✅ [INFO] Navigating to home: https://www.automationexercise.com/
✅ [INFO] Screenshot captured: baselines/home_current.png
✅ [INFO] Comparing home with baseline...
⚠️ [WARNING] cart — Verdict: regressed | Regressions: 2
✅ AUTONOMOUS SCAN COMPLETE
🌐 Site          : https://www.automationexercise.com
📄 Pages Scanned : 3
⏱️  Duration      : 36.6s
❌ Regressions   : 2
🗂️  Mode          : regression_scan

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- A free Groq API key from [console.groq.com](https://console.groq.com)

### Installation

**Step 1 — Clone the repository:**
```bash
git clone https://github.com/Tejasre-2504/pixelprobe-design-audit-agent.git
cd pixelprobe-design-audit-agent
```

**Step 2 — Install dependencies:**
```bash
pip install -r requirements.txt
```

**Step 3 — Install Playwright (for Level 3):**
```bash
playwright install chromium
```

**Step 4 — Set up your API key:**

Create a `.env` file in the root folder:
GROQ_API_KEY=your_groq_api_key_here

### Running PixelProbe

**Level 1 — Analyze a single screenshot:**
```bash
python main.py sample_images/your_screenshot.png
```

**Level 2 — Compare before and after:**
```bash
python main.py sample_images/before.png sample_images/after.png
```

**Level 3 — First run (creates baselines):**
```bash
python level3_agent.py
```

**Level 3 — Second run (detects regressions):**
```bash
python level3_agent.py
```

PixelProbe generates reports in the `outputs/` folder and baselines in the `baselines/` folder.

---

## 📁 Project Structure
pixelprobe-design-audit-agent/
├── agent.py            # Level 1 core — Groq Vision API integration
├── compare.py          # Level 2 comparison engine — mathematical confidence
├── validator.py        # Input/output guard rails + anti-hallucination
├── report.py           # Level 1 dark mode HTML report generator
├── report_compare.py   # Level 2 dark mode comparison report generator
├── level3_agent.py     # Level 3 autonomous browser agent — Playwright
├── main.py             # Entry point — auto-detects Level 1 vs Level 2
├── requirements.txt    # Python dependencies
├── sample_images/      # Put your test screenshots here
├── baselines/          # Level 3 baseline screenshots stored here
└── outputs/            # All generated reports appear here

---

## 🔧 Tech Stack

| Component | Technology |
|---|---|
| AI Vision Model | Groq LLaMA 4 Scout Vision |
| Language | Python 3.10+ |
| Browser Automation | Playwright (Level 3) |
| Image Processing | Pillow |
| Environment Config | python-dotenv |
| Report Generation | Pure HTML/CSS (no frameworks) |
| Output Formats | JSON + HTML |

---

## 📋 Output Report Features

The generated HTML reports include:
- 🌙 **Dark mode design** with neon accents and glassmorphism cards
- 📊 **Animated score circle** showing mathematically calculated design quality
- 🏷️ **Glowing severity badges** — critical findings glow red
- 📈 **Confidence bars** for every finding
- 🎨 **Principle breakdown** showing which areas need most work
- 📋 **Full agent execution log** at the bottom
- ✅ **Tabbed interface** (Level 2) — filter by improvements/regressions
- 🤖 **Master scan report** (Level 3) — per-page results with View Report links

---

## ⚠️ Known Limitations

- Image size must be under 20MB
- Supported formats: PNG, JPG, JPEG, WebP
- Groq free tier has rate limits — wait 60 seconds between runs if you hit a 429 error
- Level 2 works best when comparing the same page across versions
- Level 3 may need selector updates for sites with non-standard login forms
- Level 3 baseline refresh: delete the `baselines/` folder and run again

---

## 🙏 Acknowledgements

Built as part of the **Aivar Innovations AI/ML Engineering Hiring Challenge — June 2026.**

Designed and developed to demonstrate production-grade agentic AI system design — with real guard rails, real observability, autonomous browser control, and real output across all three levels.

---

