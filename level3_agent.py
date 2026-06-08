"""
level3_agent.py
---------------
Level 3 — Autonomous UI/UX Regression Testing Agent.
Logs in, navigates pages, captures screenshots,
compares against baselines, and reports regressions.
"""

import os
import json
import time
import asyncio
import shutil
from pathlib import Path
from datetime import datetime
from playwright.async_api import async_playwright
from compare import CompareAgent
from report_compare import generate_compare_html_report
from report import save_json_report

# ── Configuration ─────────────────────────────────────────
CONFIG = {
    "site": "https://www.automationexercise.com",
    "login_url": "https://www.automationexercise.com/login",
    "email": "test@test.com",
    "password": "test123",
    "pages": [
        {"name": "home",     "url": "https://www.automationexercise.com/"},
        {"name": "products", "url": "https://www.automationexercise.com/products"},
        {"name": "cart",     "url": "https://www.automationexercise.com/view_cart"},
    ],
    "viewport": {"width": 1280, "height": 800},
    "baseline_dir": "baselines",
    "outputs_dir": "outputs",
    "timeout": 30000,
}

DYNAMIC_SELECTORS = [
    ".timer", ".countdown", "[class*='timer']",
    "[class*='session']", "[class*='token']",
    ".ad-banner", "#ad", "[class*='advertisement']",
]


class Level3Agent:

    def __init__(self):
        self.logs = []
        self.baseline_dir = Path(CONFIG["baseline_dir"])
        self.outputs_dir = Path(CONFIG["outputs_dir"])
        self.baseline_dir.mkdir(exist_ok=True)
        self.outputs_dir.mkdir(exist_ok=True)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    def _log(self, level: str, message: str):
        entry = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "level": level,
            "message": message
        }
        self.logs.append(entry)
        icon = {"INFO": "✅", "WARNING": "⚠️", "ERROR": "❌"}.get(level, "ℹ️")
        print(f"[{entry['timestamp']}] {icon} [{level}] {message}")

    async def _mask_dynamic_content(self, page):
        for selector in DYNAMIC_SELECTORS:
            try:
                await page.evaluate(f"""
                    document.querySelectorAll('{selector}').forEach(el => {{
                        el.style.visibility = 'hidden';
                    }});
                """)
            except:
                pass

    async def _capture_screenshot(self, page, name: str) -> str:
        await page.wait_for_load_state("networkidle", timeout=CONFIG["timeout"])
        await asyncio.sleep(2)
        await self._mask_dynamic_content(page)
        path = str(self.baseline_dir / f"{name}_current.png")
        await page.screenshot(path=path, full_page=False)
        self._log("INFO", f"Screenshot captured: {path}")
        return path

    async def _login(self, page) -> bool:
        try:
            self._log("INFO", f"Navigating to login page: {CONFIG['login_url']}")
            await page.goto(CONFIG["login_url"], timeout=CONFIG["timeout"])
            await page.wait_for_load_state("networkidle")
            await page.fill("input[data-qa='login-email']", CONFIG["email"])
            self._log("INFO", "Email filled.")
            await page.fill("input[data-qa='login-password']", CONFIG["password"])
            self._log("INFO", "Password filled.")
            await page.click("button[data-qa='login-button']")
            await page.wait_for_load_state("networkidle")
            self._log("INFO", "Login submitted.")
            current_url = page.url
            if "login" not in current_url:
                self._log("INFO", "Login successful!")
                return True
            else:
                self._log("WARNING", "Login may have failed — continuing anyway.")
                return True
        except Exception as e:
            self._log("WARNING", f"Login error: {str(e)} — continuing without login.")
            return False

    def _is_baseline_exists(self, name: str) -> bool:
        return (self.baseline_dir / f"{name}_baseline.png").exists()

    def _save_as_baseline(self, name: str):
        current = self.baseline_dir / f"{name}_current.png"
        baseline = self.baseline_dir / f"{name}_baseline.png"
        if current.exists():
            shutil.copy(current, baseline)
            self._log("INFO", f"Baseline saved for: {name}")

    def _compare_with_baseline(self, name: str) -> dict:
        baseline_path = str(self.baseline_dir / f"{name}_baseline.png")
        current_path = str(self.baseline_dir / f"{name}_current.png")
        if not Path(baseline_path).exists():
            self._log("WARNING", f"No baseline found for {name}")
            return None
        self._log("INFO", f"Comparing {name} with baseline...")
        agent = CompareAgent()
        result = agent.compare(baseline_path, current_path)
        return result

    async def run(self) -> dict:
        start_time = time.time()
        self._log("INFO", "=" * 50)
        self._log("INFO", "PixelProbe Level 3 — Autonomous Scan Starting")
        self._log("INFO", f"Target: {CONFIG['site']}")
        self._log("INFO", f"Pages to scan: {len(CONFIG['pages'])}")
        self._log("INFO", "=" * 50)

        scan_results = []
        is_first_run = not self._is_baseline_exists("home")

        if is_first_run:
            self._log("INFO", "First run detected — will create baselines.")
        else:
            self._log("INFO", "Baselines exist — will compare and report regressions.")

        async with async_playwright() as p:
            self._log("INFO", "Launching browser...")
            browser = await p.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-dev-shm-usage"]
            )
            context = await browser.new_context(
                viewport=CONFIG["viewport"],
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
            page = await context.new_page()
            self._log("INFO", "Browser launched successfully.")

            await self._login(page)

            for page_config in CONFIG["pages"]:
                name = page_config["name"]
                url = page_config["url"]

                try:
                    self._log("INFO", f"Navigating to {name}: {url}")
                    await page.goto(url, timeout=CONFIG["timeout"])
                    await page.wait_for_load_state("networkidle")

                    await self._capture_screenshot(page, name)

                    if is_first_run:
                        self._save_as_baseline(name)
                        scan_results.append({
                            "page": name,
                            "url": url,
                            "status": "baseline_created",
                            "message": f"Baseline created for {name}"
                        })
                        self._log("INFO", f"Baseline created for {name}")
                    else:
                        compare_result = self._compare_with_baseline(name)
                        if compare_result:
                            # ✅ FIXED: correct paths without double outputs/
                            html_path = f"outputs/level3_{name}_{self.timestamp}_report.html"
                            json_path = f"outputs/level3_{name}_{self.timestamp}_findings.json"

                            generate_compare_html_report(compare_result, html_path)
                            save_json_report(compare_result, json_path)

                            scan_results.append({
                                "page": name,
                                "url": url,
                                "status": "compared",
                                "verdict": compare_result.get("overall_verdict"),
                                "regressions": compare_result.get("regression_count", 0),
                                "improvements": compare_result.get("improvement_count", 0),
                                "html_report": html_path,
                                "json_report": json_path,
                            })

                            self._log(
                                "WARNING" if compare_result.get("regression_count", 0) > 0 else "INFO",
                                f"{name} — Verdict: {compare_result.get('overall_verdict')} | "
                                f"Regressions: {compare_result.get('regression_count', 0)} | "
                                f"Improvements: {compare_result.get('improvement_count', 0)}"
                            )

                except Exception as e:
                    self._log("ERROR", f"Failed to process {name}: {str(e)}")
                    scan_results.append({
                        "page": name,
                        "url": url,
                        "status": "error",
                        "error": str(e)
                    })

            await browser.close()
            self._log("INFO", "Browser closed.")

        elapsed = round(time.time() - start_time, 1)
        self._log("INFO", f"Scan complete in {elapsed}s")

        total_regressions = sum(
            r.get("regressions", 0) for r in scan_results
            if r.get("status") == "compared"
        )

        final_result = {
            "status": "success",
            "mode": "baseline_creation" if is_first_run else "regression_scan",
            "site": CONFIG["site"],
            "pages_scanned": len(CONFIG["pages"]),
            "scan_duration_seconds": elapsed,
            "timestamp": self.timestamp,
            "total_regressions": total_regressions,
            "scan_results": scan_results,
            "logs": self.logs
        }

        # ✅ FIXED: correct master report paths
        master_json = f"outputs/level3_master_{self.timestamp}.json"
        save_json_report(final_result, master_json)
        self._generate_master_html(final_result)

        return final_result

    def _generate_master_html(self, result: dict):
        now = datetime.now().strftime("%B %d, %Y at %H:%M")
        scan_results = result.get("scan_results", [])
        mode = result.get("mode", "")
        is_baseline = mode == "baseline_creation"

        page_cards = ""
        for r in scan_results:
            status = r.get("status", "")
            verdict = r.get("verdict", "—")
            regressions = r.get("regressions", 0)
            improvements = r.get("improvements", 0)
            error = r.get("error", "")

            if status == "baseline_created":
                color = "#30D158"
                icon = "📸"
                badge = "BASELINE CREATED"
                detail = "First run — baseline saved for future comparisons"
            elif status == "compared":
                if regressions > 0:
                    color = "#FF2D55"
                    icon = "❌"
                    badge = "REGRESSIONS FOUND"
                else:
                    color = "#30D158"
                    icon = "✅"
                    badge = "CLEAN"
                detail = f"Verdict: {verdict.upper()} | Regressions: {regressions} | Improvements: {improvements}"
            else:
                color = "#FF9F0A"
                icon = "⚠️"
                badge = "ERROR"
                detail = error

            # ✅ FIXED: report link uses correct relative path
            report_link = ""
            if r.get("html_report"):
                report_name = Path(r["html_report"]).name
                report_link = f'<a href="{report_name}" style="color:#0A84FF;font-size:12px;">View Report →</a>'

            page_cards += f"""
            <div style="
                background:rgba(255,255,255,0.04);
                border:1px solid rgba(255,255,255,0.08);
                border-left:3px solid {color};
                border-radius:14px;padding:20px;margin-bottom:12px;
                backdrop-filter:blur(10px);
            ">
                <div style="display:flex;justify-content:space-between;
                    align-items:center;flex-wrap:wrap;gap:8px;margin-bottom:10px;">
                    <div style="display:flex;align-items:center;gap:10px;">
                        <span style="font-size:20px;">{icon}</span>
                        <span style="font-size:16px;font-weight:700;
                            color:rgba(255,255,255,0.9);">{r.get('page','?').upper()}</span>
                        <span style="background:{color};color:black;
                            padding:3px 10px;border-radius:20px;
                            font-size:10px;font-weight:800;">{badge}</span>
                    </div>
                    {report_link}
                </div>
                <div style="font-size:13px;color:rgba(255,255,255,0.5);">{r.get('url','')}</div>
                <div style="font-size:13px;color:rgba(255,255,255,0.7);margin-top:6px;">{detail}</div>
            </div>"""

        log_html = "".join([
            f'<div style="color:{"#30D158" if l["level"]=="INFO" else "#FF9F0A" if l["level"]=="WARNING" else "#FF2D55"};margin-bottom:4px;font-size:12px;">[{l["timestamp"]}] [{l["level"]}] {l["message"]}</div>'
            for l in result.get("logs", [])
        ])

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>PixelProbe — Level 3 Autonomous Scan</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{
    font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;
    background:#0a0a0f;color:white;
    min-height:100vh;padding:30px 20px;
}}
.container{{max-width:900px;margin:0 auto;}}
body::before{{
    content:'';position:fixed;top:0;left:0;right:0;bottom:0;
    background:
        radial-gradient(ellipse at 20% 20%,rgba(103,80,242,0.12) 0%,transparent 50%),
        radial-gradient(ellipse at 80% 80%,rgba(10,132,255,0.08) 0%,transparent 50%);
    pointer-events:none;z-index:0;
}}
.glass{{
    background:rgba(255,255,255,0.03);
    border:1px solid rgba(255,255,255,0.08);
    backdrop-filter:blur(20px);border-radius:24px;
}}
@keyframes fadeIn{{from{{opacity:0;}}to{{opacity:1;}}}}
</style>
</head>
<body>
<div class="container">

    <div class="glass" style="padding:36px;margin-bottom:20px;animation:fadeIn 0.6s ease;">
        <div style="
            display:inline-flex;align-items:center;gap:8px;
            background:linear-gradient(135deg,rgba(103,80,242,0.3),rgba(10,132,255,0.3));
            border:1px solid rgba(103,80,242,0.4);
            color:white;padding:6px 16px;border-radius:20px;
            font-size:11px;font-weight:700;letter-spacing:1px;
            text-transform:uppercase;margin-bottom:16px;
        ">🤖 PixelProbe — Level 3 Autonomous Scan</div>

        <h1 style="
            font-size:32px;font-weight:900;margin-bottom:8px;
            background:linear-gradient(135deg,#ffffff,rgba(255,255,255,0.6));
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;
            background-clip:text;
        ">Autonomous Regression Report</h1>

        <div style="color:rgba(255,255,255,0.4);font-size:14px;margin-bottom:20px;">
            🌐 {result.get('site','')} &nbsp;•&nbsp;
            🕐 {now} &nbsp;•&nbsp;
            ⏱️ Completed in {result.get('scan_duration_seconds','?')}s
        </div>

        <div style="
            background:{'rgba(48,209,88,0.1)' if is_baseline else 'rgba(10,132,255,0.1)'};
            border:1px solid {'rgba(48,209,88,0.3)' if is_baseline else 'rgba(10,132,255,0.3)'};
            border-radius:12px;padding:14px 20px;
        ">
            <div style="font-size:13px;color:{'#30D158' if is_baseline else '#0A84FF'};
                font-weight:700;margin-bottom:4px;">
                {'📸 BASELINE CREATION MODE' if is_baseline else '🔍 REGRESSION SCAN MODE'}
            </div>
            <div style="font-size:14px;color:rgba(255,255,255,0.6);">
                {'First run complete. Baselines saved. Run again to detect regressions.'
                if is_baseline else
                f"Scan complete. {result.get('total_regressions',0)} regression(s) found across {result.get('pages_scanned',0)} pages."}
            </div>
        </div>
    </div>

    <div style="display:flex;gap:14px;margin-bottom:20px;flex-wrap:wrap;">
        {"".join([f'''
        <div class="glass" style="flex:1;min-width:120px;padding:20px;text-align:center;
            border-top:2px solid {color};">
            <div style="font-size:24px;margin-bottom:6px;">{icon}</div>
            <div style="font-size:26px;font-weight:800;color:{color};margin-bottom:4px;">{val}</div>
            <div style="font-size:12px;color:rgba(255,255,255,0.4);">{lbl}</div>
        </div>'''
        for color, icon, val, lbl in [
            ("#6750F2", "🌐", result.get('pages_scanned', 0), "Pages Scanned"),
            ("#FF2D55", "❌", result.get('total_regressions', 0), "Regressions"),
            ("#30D158", "⏱️", f"{result.get('scan_duration_seconds','?')}s", "Scan Time"),
            ("#0A84FF", "🤖", "AUTO", "Mode"),
        ]])}
    </div>

    <h2 style="font-size:20px;font-weight:800;margin-bottom:14px;
        background:linear-gradient(135deg,#ffffff,rgba(255,255,255,0.5));
        -webkit-background-clip:text;-webkit-text-fill-color:transparent;
        background-clip:text;">📄 Page Scan Results</h2>
    {page_cards}

    <div class="glass" style="padding:24px;margin-top:20px;">
        <h3 style="font-size:15px;font-weight:700;
            color:rgba(255,255,255,0.7);margin-bottom:14px;">📋 Agent Execution Log</h3>
        <div style="font-family:'Courier New',monospace;">{log_html}</div>
    </div>

    <div style="text-align:center;padding:30px;">
        <div style="
            display:inline-flex;align-items:center;gap:10px;
            background:rgba(255,255,255,0.04);
            border:1px solid rgba(255,255,255,0.08);
            padding:12px 24px;border-radius:30px;
        ">
            <span>🔍</span>
            <span style="color:rgba(255,255,255,0.4);font-size:13px;">
                PixelProbe Level 3 &nbsp;•&nbsp; Autonomous UI/UX Regression Testing &nbsp;•&nbsp; {now}
            </span>
        </div>
    </div>

</div>
</body>
</html>"""

        # ✅ FIXED: correct master html path
        html_path = f"outputs/level3_master_{self.timestamp}.html"
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html)
        self._log("INFO", f"Master report saved: {html_path}")
        print(f"\n📄 Master Report: {html_path}")


async def main():
    print("\n" + "="*60)
    print("  🤖 PixelProbe — Level 3: Autonomous Regression Testing")
    print("  ✨ Navigating, capturing, comparing — fully autonomous")
    print("="*60 + "\n")

    agent = Level3Agent()
    result = await agent.run()

    print("\n" + "="*60)
    print("  ✅ AUTONOMOUS SCAN COMPLETE")
    print("="*60)
    print(f"\n🌐 Site          : {result['site']}")
    print(f"📄 Pages Scanned : {result['pages_scanned']}")
    print(f"⏱️  Duration      : {result['scan_duration_seconds']}s")
    print(f"❌ Regressions   : {result['total_regressions']}")
    print(f"🗂️  Mode          : {result['mode']}")
    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())