"""
report_compare.py
-----------------
Level 2 — Dark Mode Before/After Comparison Report.
Matches PixelProbe Level 1 dark theme exactly.
"""

from pathlib import Path
from datetime import datetime


CLASSIFICATION_COLORS = {
    "improvement": {"bg": "#30D158", "glow": "rgba(48,209,88,0.4)",   "light": "rgba(48,209,88,0.08)",   "border": "rgba(48,209,88,0.2)",   "icon": "✅", "label": "IMPROVEMENT"},
    "regression":  {"bg": "#FF2D55", "glow": "rgba(255,45,85,0.4)",   "light": "rgba(255,45,85,0.08)",    "border": "rgba(255,45,85,0.2)",    "icon": "❌", "label": "REGRESSION"},
    "neutral":     {"bg": "#8E8E93", "glow": "rgba(142,142,147,0.4)", "light": "rgba(142,142,147,0.08)", "border": "rgba(142,142,147,0.2)", "icon": "➡️", "label": "NEUTRAL"},
}

VERDICT_CONFIG = {
    "improved":  {"color": "#30D158", "glow": "rgba(48,209,88,0.3)",   "icon": "🚀", "label": "IMPROVED"},
    "regressed": {"color": "#FF2D55", "glow": "rgba(255,45,85,0.3)",   "icon": "⚠️", "label": "REGRESSED"},
    "neutral":   {"color": "#8E8E93", "glow": "rgba(142,142,147,0.3)", "icon": "➡️", "label": "NEUTRAL"},
}


def _diff_card(diff: dict, index: int) -> str:
    cls = diff.get("classification", "neutral").lower()
    colors = CLASSIFICATION_COLORS.get(cls, CLASSIFICATION_COLORS["neutral"])
    conf = float(diff.get("confidence", 0))
    conf_color = "#30D158" if conf >= 75 else "#FFD60A" if conf >= 50 else "#FF2D55"
    a11y = diff.get("accessibility_flag", False)
    hex_vals = diff.get("hex_values") or ""
    px_vals = diff.get("pixel_measurements") or ""

    a11y_badge = ""
    if a11y:
        a11y_badge = """<span style="
            background:#FF2D55;color:white;
            padding:3px 10px;border-radius:20px;
            font-size:11px;font-weight:700;margin-left:6px;
            box-shadow:0 0 10px rgba(255,45,85,0.5);
        ">♿ A11Y RISK</span>"""

    hex_section = ""
    if hex_vals and hex_vals != "null":
        hex_section = f"""
        <div style="
            background:rgba(0,0,0,0.4);color:#30D158;
            border-radius:8px;padding:10px 14px;
            font-family:'Courier New',monospace;font-size:13px;
            margin-bottom:10px;border:1px solid rgba(48,209,88,0.2);
        ">🎨 Color change: {hex_vals}</div>"""

    px_section = ""
    if px_vals and px_vals != "null":
        px_section = f"""
        <div style="
            background:rgba(0,0,0,0.4);color:#FF9F0A;
            border-radius:8px;padding:10px 14px;
            font-family:'Courier New',monospace;font-size:13px;
            margin-bottom:10px;border:1px solid rgba(255,159,10,0.2);
        ">📐 Size change: {px_vals}</div>"""

    return f"""
    <div style="
        background:linear-gradient(135deg,rgba(255,255,255,0.05),rgba(255,255,255,0.02));
        border:1px solid rgba(255,255,255,0.08);
        border-left:3px solid {colors['bg']};
        border-radius:16px;padding:24px;margin-bottom:16px;
        backdrop-filter:blur(20px);
        box-shadow:0 4px 24px rgba(0,0,0,0.3);
        animation:slideIn 0.5s ease {index*0.08}s both;
        transition:all 0.3s ease;
        position:relative;overflow:hidden;
    " onmouseover="this.style.transform='translateY(-3px)';this.style.boxShadow='0 8px 32px rgba(0,0,0,0.4),0 0 20px {colors['glow']}'"
       onmouseout="this.style.transform='translateY(0)';this.style.boxShadow='0 4px 24px rgba(0,0,0,0.3)'">

        <div style="position:absolute;top:0;right:0;width:120px;height:120px;
            background:radial-gradient(circle,{colors['glow']},transparent 70%);
            pointer-events:none;"></div>

        <div style="display:flex;justify-content:space-between;align-items:center;
            flex-wrap:wrap;gap:8px;margin-bottom:16px;">
            <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
                <span style="
                    background:{colors['bg']};
                    color:{'black' if cls == 'improvement' else 'white'};
                    padding:4px 14px;border-radius:20px;
                    font-size:11px;font-weight:800;
                    text-transform:uppercase;letter-spacing:0.5px;
                    box-shadow:0 0 12px {colors['glow']};
                ">{colors['icon']} {colors['label']}</span>
                {a11y_badge}
            </div>
            <span style="color:rgba(255,255,255,0.3);font-size:12px;font-weight:600;
                background:rgba(255,255,255,0.05);padding:4px 10px;border-radius:8px;">
                {diff.get('id', '?')}
            </span>
        </div>

        <div style="background:{colors['light']};border-radius:10px;
            padding:12px 16px;margin-bottom:12px;border:1px solid {colors['border']};">
            <div style="font-size:11px;color:rgba(255,255,255,0.4);font-weight:600;
                margin-bottom:4px;text-transform:uppercase;letter-spacing:0.5px;">📍 Location</div>
            <div style="font-size:14px;color:rgba(255,255,255,0.85);font-weight:500;">
                {diff.get('location', '?')}</div>
        </div>

        <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:12px;">
            <div style="background:rgba(255,159,10,0.08);border-radius:10px;padding:12px;
                border:1px solid rgba(255,159,10,0.2);">
                <div style="font-size:11px;color:#FF9F0A;font-weight:700;margin-bottom:6px;
                    text-transform:uppercase;letter-spacing:0.5px;">⬅️ BEFORE</div>
                <div style="font-size:13px;color:rgba(255,255,255,0.7);line-height:1.5;">
                    {diff.get('before', '?')}</div>
            </div>
            <div style="background:rgba(103,80,242,0.08);border-radius:10px;padding:12px;
                border:1px solid rgba(103,80,242,0.2);">
                <div style="font-size:11px;color:#6750F2;font-weight:700;margin-bottom:6px;
                    text-transform:uppercase;letter-spacing:0.5px;">➡️ AFTER</div>
                <div style="font-size:13px;color:rgba(255,255,255,0.7);line-height:1.5;">
                    {diff.get('after', '?')}</div>
            </div>
        </div>

        {hex_section}
        {px_section}

        <div style="background:rgba(10,132,255,0.08);border-radius:10px;
            padding:12px 16px;margin-bottom:12px;border:1px solid rgba(10,132,255,0.2);">
            <div style="font-size:11px;color:#0A84FF;font-weight:600;margin-bottom:4px;
                text-transform:uppercase;letter-spacing:0.5px;">👤 UX Impact</div>
            <div style="font-size:14px;color:rgba(255,255,255,0.7);line-height:1.5;">
                {diff.get('ux_impact', '?')}</div>
        </div>

        <div>
            <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
                <span style="font-size:11px;color:rgba(255,255,255,0.4);font-weight:600;
                    text-transform:uppercase;letter-spacing:0.5px;">Confidence</span>
                <span style="font-size:13px;color:{conf_color};font-weight:700;">{conf:.0f}%</span>
            </div>
            <div style="background:rgba(255,255,255,0.06);border-radius:10px;
                height:6px;overflow:hidden;">
                <div style="width:{conf}%;
                    background:linear-gradient(90deg,{conf_color},{conf_color}88);
                    height:100%;border-radius:10px;
                    box-shadow:0 0 8px {conf_color}88;"></div>
            </div>
        </div>
    </div>"""


def generate_compare_html_report(result: dict, output_path: str) -> str:
    verdict = result.get("overall_verdict", "neutral").lower()
    vc = VERDICT_CONFIG.get(verdict, VERDICT_CONFIG["neutral"])
    now = datetime.now().strftime("%B %d, %Y at %H:%M")
    differences = result.get("differences", [])
    conf = result.get("overall_confidence", 0)
    conf_color = "#30D158" if conf >= 75 else "#FFD60A" if conf >= 50 else "#FF2D55"

    improvements = [d for d in differences if d.get("classification") == "improvement"]
    regressions  = [d for d in differences if d.get("classification") == "regression"]
    a11y_count   = result.get("accessibility_regressions", 0)

    def build_section(diffs, start_index=0):
        if not diffs:
            return '<div style="text-align:center;padding:40px;color:rgba(255,255,255,0.3);">No findings in this category</div>'
        return "".join([_diff_card(d, i + start_index) for i, d in enumerate(diffs)])

    all_cards         = build_section(differences)
    regression_cards  = build_section(regressions)
    improvement_cards = build_section(improvements)

    a11y_banner = ""
    if a11y_count > 0:
        a11y_banner = f"""
        <div style="
            background:rgba(255,45,85,0.15);
            border:1px solid rgba(255,45,85,0.3);
            border-radius:14px;padding:16px 24px;margin-bottom:20px;
            display:flex;align-items:center;gap:12px;
            box-shadow:0 0 20px rgba(255,45,85,0.2);
        ">
            <span style="font-size:28px;">♿</span>
            <div>
                <div style="font-size:16px;font-weight:700;color:#FF2D55;">
                    Accessibility Regressions Detected</div>
                <div style="font-size:14px;color:rgba(255,255,255,0.6);margin-top:4px;">
                    {a11y_count} change(s) may cause accessibility issues — review immediately</div>
            </div>
        </div>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>PixelProbe — Regression Report</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{
    font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;
    background:#0a0a0f;
    color:white;
    min-height:100vh;
    padding:30px 20px;
    overflow-x:hidden;
}}
.container{{max-width:900px;margin:0 auto;position:relative;z-index:1;}}
body::before{{
    content:'';
    position:fixed;top:0;left:0;right:0;bottom:0;
    background:
        radial-gradient(ellipse at 20% 20%,rgba(103,80,242,0.12) 0%,transparent 50%),
        radial-gradient(ellipse at 80% 80%,rgba(10,132,255,0.08) 0%,transparent 50%),
        radial-gradient(ellipse at 50% 50%,rgba(48,209,88,0.04) 0%,transparent 70%);
    pointer-events:none;z-index:0;
    animation:bgPulse 8s ease-in-out infinite alternate;
}}
@keyframes bgPulse{{from{{opacity:0.6;}}to{{opacity:1;}}}}
@keyframes slideIn{{from{{opacity:0;transform:translateY(24px);}}to{{opacity:1;transform:translateY(0);}}}}
@keyframes fadeIn{{from{{opacity:0;}}to{{opacity:1;}}}}
@keyframes float{{0%,100%{{transform:translateY(0);}}50%{{transform:translateY(-6px);}}}}
.glass{{
    background:rgba(255,255,255,0.03);
    border:1px solid rgba(255,255,255,0.08);
    backdrop-filter:blur(20px);
    border-radius:24px;
}}
.tab-btn{{
    padding:10px 20px;border:none;border-radius:10px;
    background:rgba(255,255,255,0.06);
    color:rgba(255,255,255,0.5);
    font-size:13px;font-weight:600;cursor:pointer;
    transition:all 0.2s;
    border:1px solid rgba(255,255,255,0.08);
}}
.tab-btn.active{{
    background:linear-gradient(135deg,rgba(103,80,242,0.4),rgba(10,132,255,0.4));
    color:white;border-color:rgba(103,80,242,0.4);
}}
.tab-btn:hover{{background:rgba(255,255,255,0.1);color:white;}}
.tab-content{{display:none;}}
.tab-content.active{{display:block;}}
</style>
</head>
<body>
<div class="container">

<!-- Floating orbs -->
<div style="position:fixed;width:300px;height:300px;
    background:radial-gradient(circle,rgba(103,80,242,0.08),transparent);
    border-radius:50%;top:-100px;right:-100px;pointer-events:none;
    animation:float 6s ease-in-out infinite;z-index:0;"></div>
<div style="position:fixed;width:200px;height:200px;
    background:radial-gradient(circle,rgba(10,132,255,0.06),transparent);
    border-radius:50%;bottom:100px;left:-60px;pointer-events:none;
    animation:float 8s ease-in-out infinite reverse;z-index:0;"></div>

<!-- Header -->
<div class="glass" style="padding:36px;margin-bottom:20px;animation:fadeIn 0.6s ease;">

    <div style="
        display:inline-flex;align-items:center;gap:8px;
        background:linear-gradient(135deg,rgba(103,80,242,0.3),rgba(10,132,255,0.3));
        border:1px solid rgba(103,80,242,0.4);
        color:white;padding:6px 16px;border-radius:20px;
        font-size:11px;font-weight:700;letter-spacing:1px;
        text-transform:uppercase;margin-bottom:16px;
    ">🔍 PixelProbe — Regression Analysis</div>

    <h1 style="
        font-size:32px;font-weight:900;margin-bottom:20px;
        background:linear-gradient(135deg,#ffffff,rgba(255,255,255,0.6));
        -webkit-background-clip:text;-webkit-text-fill-color:transparent;
        background-clip:text;
    ">UI/UX Comparison Report</h1>

    <!-- Image names -->
    <div style="display:grid;grid-template-columns:1fr auto 1fr;
        gap:12px;align-items:center;margin-bottom:20px;">
        <div style="background:rgba(255,159,10,0.08);border-radius:12px;
            padding:12px 16px;border:1px solid rgba(255,159,10,0.2);">
            <div style="font-size:11px;color:#FF9F0A;font-weight:700;margin-bottom:4px;
                text-transform:uppercase;letter-spacing:0.5px;">⬅️ Baseline</div>
            <div style="font-size:13px;color:rgba(255,255,255,0.8);font-weight:600;">
                {result.get('baseline_image', '?')}</div>
        </div>
        <div style="font-size:24px;text-align:center;color:rgba(255,255,255,0.3);">→</div>
        <div style="background:rgba(103,80,242,0.08);border-radius:12px;
            padding:12px 16px;border:1px solid rgba(103,80,242,0.2);">
            <div style="font-size:11px;color:#6750F2;font-weight:700;margin-bottom:4px;
                text-transform:uppercase;letter-spacing:0.5px;">➡️ Current</div>
            <div style="font-size:13px;color:rgba(255,255,255,0.8);font-weight:600;">
                {result.get('current_image', '?')}</div>
        </div>
    </div>

    <!-- Verdict -->
    <div style="
        background:rgba(255,255,255,0.03);
        border:1px solid {vc['color']}30;
        border-radius:16px;padding:20px 24px;
        display:flex;justify-content:space-between;align-items:center;
        flex-wrap:wrap;gap:12px;
        box-shadow:0 0 30px {vc['glow']};
    ">
        <div style="display:flex;align-items:center;gap:12px;">
            <span style="font-size:36px;">{vc['icon']}</span>
            <div>
                <div style="font-size:12px;color:rgba(255,255,255,0.4);font-weight:600;
                    text-transform:uppercase;letter-spacing:0.5px;">Overall Verdict</div>
                <div style="font-size:28px;font-weight:900;color:{vc['color']};
                    text-shadow:0 0 20px {vc['color']};">{vc['label']}</div>
            </div>
        </div>
        <div style="text-align:right;">
            <div style="font-size:12px;color:rgba(255,255,255,0.4);margin-bottom:4px;">
                Confidence</div>
            <div style="font-size:32px;font-weight:800;color:{conf_color};
                text-shadow:0 0 15px {conf_color};">{conf}%</div>
        </div>
    </div>

    <!-- Summary -->
    <div style="
        background:linear-gradient(135deg,rgba(103,80,242,0.1),rgba(10,132,255,0.1));
        border:1px solid rgba(103,80,242,0.2);
        border-radius:14px;padding:16px 20px;margin-top:16px;
    ">
        <div style="font-size:11px;color:rgba(103,80,242,0.9);font-weight:700;
            margin-bottom:8px;text-transform:uppercase;letter-spacing:0.5px;">📝 Net Summary</div>
        <div style="font-size:15px;color:rgba(255,255,255,0.75);line-height:1.7;">
            {result.get('net_summary', '')}</div>
    </div>

    <div style="color:rgba(255,255,255,0.3);font-size:13px;margin-top:12px;">🕐 {now}</div>
</div>

<!-- Stats -->
<div style="display:flex;gap:14px;margin-bottom:20px;
    flex-wrap:wrap;animation:fadeIn 0.6s ease 0.2s both;">
    {"".join([f'''
    <div class="glass" style="flex:1;min-width:130px;padding:20px;text-align:center;
        border-top:2px solid {color};transition:all 0.3s;"
        onmouseover="this.style.boxShadow='0 0 30px {glow}'"
        onmouseout="this.style.boxShadow='none'">
        <div style="font-size:26px;margin-bottom:8px;">{icon}</div>
        <div style="font-size:26px;font-weight:800;color:{color};
            text-shadow:0 0 12px {glow};margin-bottom:4px;">{val}</div>
        <div style="font-size:12px;color:rgba(255,255,255,0.4);">{lbl}</div>
    </div>'''
    for color, glow, icon, val, lbl in [
        ("#6750F2", "rgba(103,80,242,0.4)", "🔍", result.get('total_differences', 0), "Total Changes"),
        ("#30D158", "rgba(48,209,88,0.4)",  "✅", result.get('improvement_count', 0), "Improvements"),
        ("#FF2D55", "rgba(255,45,85,0.4)",  "❌", result.get('regression_count', 0),  "Regressions"),
        ("#FF2D55", "rgba(255,45,85,0.4)",  "♿", a11y_count,                          "A11y Risks"),
    ]])}
</div>

{a11y_banner}

<!-- Tabs -->
<div style="display:flex;gap:8px;flex-wrap:wrap;
    margin-bottom:16px;animation:fadeIn 0.6s ease 0.3s both;">
    <button class="tab-btn active" onclick="showTab('all',this)">
        All Changes ({result.get('total_differences', 0)})
    </button>
    <button class="tab-btn" onclick="showTab('regressions',this)">
        ❌ Regressions ({len(regressions)})
    </button>
    <button class="tab-btn" onclick="showTab('improvements',this)">
        ✅ Improvements ({len(improvements)})
    </button>
</div>

<!-- Tab Contents -->
<div id="tab-all" class="tab-content active">{all_cards}</div>
<div id="tab-regressions" class="tab-content">{regression_cards}</div>
<div id="tab-improvements" class="tab-content">{improvement_cards}</div>

<!-- Execution Log -->
<div class="glass" style="padding:24px;margin-top:20px;
    animation:fadeIn 0.6s ease 0.6s both;">
    <h3 style="font-size:15px;font-weight:700;
        color:rgba(255,255,255,0.7);margin-bottom:14px;">📋 Agent Execution Log</h3>
    <div style="font-family:'Courier New',monospace;font-size:12px;">
    {"".join([
        f'<div style="color:{"#30D158" if l["level"]=="INFO" else "#FF9F0A" if l["level"]=="WARNING" else "#FF2D55"};margin-bottom:4px;opacity:0.8;">[{l["timestamp"]}] [{l["level"]}] {l["message"]}</div>'
        for l in result.get("logs", [])
    ])}
    </div>
</div>

<!-- Footer -->
<div style="text-align:center;padding:30px;animation:fadeIn 0.6s ease 0.8s both;">
    <div style="
        display:inline-flex;align-items:center;gap:10px;
        background:rgba(255,255,255,0.04);
        border:1px solid rgba(255,255,255,0.08);
        padding:12px 24px;border-radius:30px;
    ">
        <span style="font-size:16px;">🔍</span>
        <span style="color:rgba(255,255,255,0.4);font-size:13px;">
            PixelProbe &nbsp;•&nbsp; AI-Powered Regression Analysis &nbsp;•&nbsp; {now}
        </span>
    </div>
</div>

</div>

<script>
function showTab(name, btn) {{
    document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.getElementById('tab-' + name).classList.add('active');
    btn.classList.add('active');
}}
</script>
</body>
</html>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    return output_path