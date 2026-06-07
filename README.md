# 🔍 PixelProbe — AI-Powered Design Audit Agent

**"Your designs deserve a second pair of eyes — one that never sleeps."**

PixelProbe is an intelligent design audit agent that automatically reviews UI screenshots and catches design problems before your users ever see them. It thinks like a senior designer, reports like an engineer, and works at the speed of AI.

---

## 🤔 Why PixelProbe?

Every frontend team faces the same problem. Developers ship code. Designers can't review every pull request. Code reviewers focus on logic, not pixels. And slowly, silently — spacing breaks, contrast fails, visual hierarchy collapses.

By the time someone notices, the damage is already in production.

PixelProbe was built to close that gap. It sits in your workflow, reviews every change, and tells you exactly what broke, where it broke, and how to fix it — in seconds, not days.

---

## ✨ What Can It Do?

### 🎯 Level 1 — Single Page Design Analysis
Drop in any UI screenshot and PixelProbe will analyze it across 5 core design principles. It tells you what's wrong, where it is on the page, how it affects users, and exactly what to do about it.

### 🔄 Level 2 — Before/After Regression Analysis  
Give it two screenshots — a baseline and a current version — and it will find every visual difference, classify each one as an improvement, regression, or neutral change, and flag any accessibility risks immediately.

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

PixelProbe is not just an API wrapper. It's a proper agent with a full decision pipeline:

:
📸 Input Image
↓
🛡️ Input Validator
(checks format, size, integrity)
↓
🤖 Groq Vision LLM
(analyzes against 5 design principles)
↓
🔍 Output Validator
(strips hallucinations, checks confidence)
↓
📊 Report Generator
(beautiful dark mode HTML + structured JSON)
↓
✅ Findings Delivered

Every step is logged. Every decision is traceable. If something goes wrong, PixelProbe tells you exactly what failed and why — it never silently skips anything.

---

## 🛡️ Production-Grade Guard Rails

PixelProbe was built with the same standards you'd expect from a production system:

- **Anti-hallucination validation** — every finding is checked against strict rules before it reaches you. Vague or unsupported findings are automatically rejected.
- **Confidence scoring** — every finding comes with a confidence score (0–100%). Critical findings require ≥75% confidence to pass validation.
- **Retry logic** — if the API call fails, PixelProbe retries up to 3 times with exponential backoff before reporting a failure.
- **Graceful error handling** — 403s, 429s, timeouts, and malformed responses are all caught, logged, and surfaced clearly.
- **Full execution log** — every action the agent takes is logged with a timestamp and severity level, visible right in the HTML report.

---

## 📊 Sample Output

**Level 1 Terminal Output:**

============================================================
🔍 PixelProbe — AI-Powered Design Intelligence
✨ Catching design issues before your users do.
📸 Analyzing: sample_images/test.png
[2026-06-07T10:00:33] [INFO] Starting design audit...
[2026-06-07T10:00:33] [INFO] Validating input image...
[2026-06-07T10:00:33] [INFO] Input validation passed.
[2026-06-07T10:00:36] [INFO] Groq Vision API call successful.
[2026-06-07T10:00:36] [INFO] 7 findings returned. Validating...
[2026-06-07T10:00:36] [INFO] Validation complete: 7 valid, 0 rejected.
============================================================
✅ AUDIT COMPLETE
📊 Overall Score   : 60/100
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
📊 Overall Confidence   : 90%
🔍 Total Differences    : 7
✅ Improvements         : 2
❌ Regressions          : 3
♿ A11y Regressions     : 0

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

**Step 3 — Set up your API key:**

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

That's it. PixelProbe will generate two files in the `outputs/` folder:
- A beautiful **dark mode HTML report** you can open in any browser
- A structured **JSON file** with all findings for downstream processing

---

## 📁 Project Structure
pixelprobe-design-audit-agent/
├── agent.py          # Core AI agent — Groq Vision API integration
├── compare.py        # Level 2 comparison engine
├── validator.py      # Input/output guard rails + anti-hallucination
├── report.py         # Level 1 dark mode HTML report generator
├── report_compare.py # Level 2 comparison HTML report generator
├── main.py           # Entry point — handles Level 1 and Level 2
├── requirements.txt  # Python dependencies
├── sample_images/    # Put your test screenshots here
└── outputs/          # Generated reports appear here

---

## 🔧 Tech Stack

| Component | Technology |
|---|---|
| AI Vision Model | Groq LLaMA 4 Scout Vision |
| Language | Python 3.10+ |
| Image Processing | Pillow |
| Environment Config | python-dotenv |
| Report Generation | Pure HTML/CSS (no frameworks) |
| Output Formats | JSON + HTML |

---

## 📋 Output Report Features

The generated HTML report includes:
- 🌙 **Dark mode design** with neon accents and glassmorphism cards
- 📊 **Animated score circle** showing overall design quality
- 🏷️ **Glowing severity badges** — critical findings glow red
- 📈 **Confidence bars** for every finding
- 🎨 **Principle breakdown** showing which areas need most work
- 📋 **Full agent execution log** at the bottom
- ✅ **Tabbed interface** (Level 2) — filter by improvements/regressions

---

## ⚠️ Known Limitations

- Image size must be under 20MB
- Supported formats: PNG, JPG, JPEG, WebP
- Groq free tier has rate limits — wait 60 seconds between runs if you hit a 429 error
- Level 2 works best when comparing the same page across versions, not two completely different sites

---

## 🙏 Acknowledgements

Built as part of the **Aivar Innovations AI/ML Engineering Hiring Challenge — June 2026.**

Designed and developed to demonstrate production-grade agentic AI system design — with real guard rails, real observability, and real output.

---

