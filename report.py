"""
report.py
---------
Level 1 — Premium Dark Mode Report Generator
Black/Navy with Neon Accents
"""

import json
from pathlib import Path
from datetime import datetime


SEVERITY_CONFIG = {
    "critical": {"color": "#FF2D55", "glow": "rgba(255,45,85,0.4)",  "icon": "🔴", "label": "CRITICAL"},
    "high":     {"color": "#FF9F0A", "glow": "rgba(255,159,10,0.4)", "icon": "🟠", "label": "HIGH"},
    "medium":   {"color": "#FFD60A", "glow": "rgba(255,214,10,0.4)", "icon": "🟡", "label": "MEDIUM"},
    "low":      {"color": "#30D158", "glow": "rgba(48,209,88,0.4)",  "icon": "🟢", "label": "LOW"},
    "info":     {"color": "#0A84FF", "glow": "rgba(10,132,255,0.4)", "icon": "🔵", "label": "INFO"},
}

PRINCIPLE_CONFIG = {
    "visual_hierarchy": {"color": "#BF5AF2", "icon": "👁️",  "label": "Visual Hierarchy"},
    "contrast":         {"color": "#FF2D55", "icon": "🎨",  "label": "Contrast (WCAG AA)"},
    "spacing":          {"color": "#0A84FF", "icon": "📐",  "label": "Spacing"},
    "alignment":        {"color": "#30D158", "icon": "⚖️",  "label": "Alignment"},
    "consistency":      {"color": "#FF9F0A", "icon": "🔗",  "label": "Consistency"},
}


def _score_color(score):
    if score >= 80: return "#30D158"
    elif score >= 60: return "#FFD60A"
    elif score >= 40: return "#FF9F0A"
    else: return "#FF2D55"

def _score_label(score):
    if score >= 80: return "Excellent"
    elif score >= 60: return "Needs Work"
    elif score >= 40: return "Poor"
    else: return "Critical"

def _finding_card(finding, index):
    sev = finding.get("severity","info").lower()
    prin = finding.get("principle","consistency").lower()
    sc = SEVERITY_CONFIG.get(sev, SEVERITY_CONFIG["info"])
    pc = PRINCIPLE_CONFIG.get(prin, {"color":"#888","icon":"🔍","label":prin.title()})
    conf = float(finding.get("confidence", 0))
    conf_color = "#30D158" if conf >= 75 else "#FFD60A" if conf >= 50 else "#FF2D55"

    return f"""
    <div class="finding-card" style="
        background:linear-gradient(135deg,rgba(255,255,255,0.05),rgba(255,255,255,0.02));
        border:1px solid rgba(255,255,255,0.08);
        border-left:3px solid {sc['color']};
        border-radius:16px;padding:24px;margin-bottom:16px;
        backdrop-filter:blur(20px);
        box-shadow:0 4px 24px rgba(0,0,0,0.3), 0 0 0 1px rgba(255,255,255,0.05);
        animation:slideIn 0.5s ease {index*0.1}s both;
        transition:all 0.3s ease;
        position:relative;overflow:hidden;
    " onmouseover="this.style.transform='translateY(-3px)';this.style.boxShadow='0 8px 32px rgba(0,0,0,0.4), 0 0 20px {sc['glow']}'"
       onmouseout="this.style.transform='translateY(0)';this.style.boxShadow='0 4px 24px rgba(0,0,0,0.3), 0 0 0 1px rgba(255,255,255,0.05)'">

        <div style="position:absolute;top:0;right:0;width:120px;height:120px;
            background:radial-gradient(circle,{sc['glow']},transparent 70%);
            pointer-events:none;"></div>

        <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:16px;flex-wrap:wrap;gap:8px;">
            <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
                <span style="
                    background:{sc['color']};color:black;
                    padding:4px 12px;border-radius:20px;
                    font-size:11px;font-weight:800;letter-spacing:0.5px;
                    box-shadow:0 0 12px {sc['glow']};
                ">{sc['icon']} {sc['label']}</span>
                <span style="
                    background:rgba(255,255,255,0.08);
                    color:{pc['color']};
                    border:1px solid {pc['color']}40;
                    padding:4px 12px;border-radius:20px;
                    font-size:11px;font-weight:600;
                ">{pc['icon']} {pc['label']}</span>
            </div>
            <span style="color:rgba(255,255,255,0.3);font-size:12px;font-weight:600;
                background:rgba(255,255,255,0.05);padding:4px 10px;border-radius:8px;">
                {finding.get('id','F001')}
            </span>
        </div>

        <div style="background:rgba(255,255,255,0.04);border-radius:10px;padding:12px 16px;margin-bottom:12px;border:1px solid rgba(255,255,255,0.06);">
            <div style="font-size:11px;color:rgba(255,255,255,0.4);font-weight:600;margin-bottom:4px;text-transform:uppercase;letter-spacing:0.5px;">📍 Location</div>
            <div style="font-size:14px;color:rgba(255,255,255,0.85);font-weight:500;">{finding.get('location','Not specified')}</div>
        </div>

        <div style="margin-bottom:12px;">
            <div style="font-size:11px;color:rgba(255,255,255,0.4);font-weight:600;margin-bottom:6px;text-transform:uppercase;letter-spacing:0.5px;">⚠️ Issue</div>
            <div style="font-size:14px;color:rgba(255,255,255,0.8);line-height:1.7;">{finding.get('issue','No description')}</div>
        </div>

        <div style="background:rgba(10,132,255,0.08);border-radius:10px;padding:12px 16px;margin-bottom:12px;border:1px solid rgba(10,132,255,0.2);">
            <div style="font-size:11px;color:#0A84FF;font-weight:600;margin-bottom:4px;text-transform:uppercase;letter-spacing:0.5px;">👤 User Impact</div>
            <div style="font-size:14px;color:rgba(255,255,255,0.7);line-height:1.6;">{finding.get('user_impact','Not specified')}</div>
        </div>

        <div style="background:rgba(48,209,88,0.08);border-radius:10px;padding:12px 16px;margin-bottom:14px;border:1px solid rgba(48,209,88,0.2);">
            <div style="font-size:11px;color:#30D158;font-weight:600;margin-bottom:4px;text-transform:uppercase;letter-spacing:0.5px;">✅ Recommendation</div>
            <div style="font-size:14px;color:rgba(255,255,255,0.7);line-height:1.6;">{finding.get('recommendation','No recommendation')}</div>
        </div>

        <div>
            <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
                <span style="font-size:11px;color:rgba(255,255,255,0.4);font-weight:600;text-transform:uppercase;letter-spacing:0.5px;">Confidence</span>
                <span style="font-size:13px;color:{conf_color};font-weight:700;">{conf:.0f}%</span>
            </div>
            <div style="background:rgba(255,255,255,0.06);border-radius:10px;height:6px;overflow:hidden;">
                <div style="width:{conf}%;background:linear-gradient(90deg,{conf_color},{conf_color}88);
                    height:100%;border-radius:10px;
                    box-shadow:0 0 8px {conf_color}88;
                    transition:width 1s ease;"></div>
            </div>
        </div>
    </div>"""


def generate_html_report(result, image_path, output_path):
    findings = result.get("findings", [])
    sev = result.get("severity_breakdown", {})
    prin = result.get("principle_breakdown", {})
    score = result.get("overall_score", 0)
    sc = _score_color(score)
    sl = _score_label(score)
    now = datetime.now().strftime("%B %d, %Y at %H:%M")
    image_name = Path(image_path).name

    cards_html = "".join([_finding_card(f, i) for i, f in enumerate(findings)])

    sev_bars = ""
    for s, count in sev.items():
        if count > 0:
            cfg = SEVERITY_CONFIG.get(s, {})
            sev_bars += f"""
            <div style="display:flex;align-items:center;gap:12px;margin-bottom:12px;">
                <span style="width:72px;font-size:12px;color:rgba(255,255,255,0.6);font-weight:600;text-transform:capitalize;">{cfg.get('icon','')} {s}</span>
                <div style="flex:1;background:rgba(255,255,255,0.06);border-radius:10px;height:8px;overflow:hidden;">
                    <div style="width:{min(count*20,100)}%;background:{cfg.get('color','#888')};height:100%;border-radius:10px;box-shadow:0 0 8px {cfg.get('glow','rgba(0,0,0,0)')}"></div>
                </div>
                <span style="font-size:14px;font-weight:700;color:{cfg.get('color','#888')};min-width:20px;">{count}</span>
            </div>"""

    prin_chips = ""
    for p, count in prin.items():
        if count > 0:
            cfg = PRINCIPLE_CONFIG.get(p, {"color":"#888","icon":"🔍","label":p})
            prin_chips += f"""
            <div style="
                display:inline-flex;align-items:center;gap:6px;
                background:rgba(255,255,255,0.05);
                border:1px solid {cfg['color']}40;
                color:{cfg['color']};
                padding:8px 14px;border-radius:20px;
                font-size:12px;font-weight:600;margin:4px;
            ">{cfg['icon']} {cfg['label']}: <strong>{count}</strong></div>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Design Audit Report — {image_name}</title>
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

/* Animated background */
body::before{{
    content:'';
    position:fixed;top:0;left:0;right:0;bottom:0;
    background:
        radial-gradient(ellipse at 20% 20%,rgba(103,50,242,0.15) 0%,transparent 50%),
        radial-gradient(ellipse at 80% 80%,rgba(10,132,255,0.1) 0%,transparent 50%),
        radial-gradient(ellipse at 50% 50%,rgba(48,209,88,0.05) 0%,transparent 70%);
    pointer-events:none;z-index:0;
    animation:bgPulse 8s ease-in-out infinite alternate;
}}
@keyframes bgPulse{{
    from{{opacity:0.6;}}
    to{{opacity:1;}}
}}
@keyframes slideIn{{
    from{{opacity:0;transform:translateY(24px);}}
    to{{opacity:1;transform:translateY(0);}}
}}
@keyframes fadeIn{{
    from{{opacity:0;}}
    to{{opacity:1;}}
}}
@keyframes scoreGlow{{
    0%,100%{{filter:drop-shadow(0 0 8px {sc});}}
    50%{{filter:drop-shadow(0 0 20px {sc});}}
}}
@keyframes float{{
    0%,100%{{transform:translateY(0px);}}
    50%{{transform:translateY(-6px);}}
}}
.glass{{
    background:rgba(255,255,255,0.03);
    border:1px solid rgba(255,255,255,0.08);
    backdrop-filter:blur(20px);
    border-radius:24px;
}}
</style>
</head>
<body>
<div class="container">

<!-- Floating orbs decoration -->
<div style="position:fixed;width:300px;height:300px;
    background:radial-gradient(circle,rgba(103,50,242,0.08),transparent);
    border-radius:50%;top:-100px;right:-100px;pointer-events:none;
    animation:float 6s ease-in-out infinite;z-index:0;"></div>
<div style="position:fixed;width:200px;height:200px;
    background:radial-gradient(circle,rgba(10,132,255,0.06),transparent);
    border-radius:50%;bottom:100px;left:-60px;pointer-events:none;
    animation:float 8s ease-in-out infinite reverse;z-index:0;"></div>

<!-- Header Card -->
<div class="glass" style="padding:36px;margin-bottom:20px;animation:fadeIn 0.6s ease;">

    <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:20px;">
        <div style="flex:1;">
            <div style="
                display:inline-flex;align-items:center;gap:8px;
                background:linear-gradient(135deg,rgba(103,50,242,0.3),rgba(10,132,255,0.3));
                border:1px solid rgba(103,50,242,0.4);
                color:white;padding:6px 16px;border-radius:20px;
                font-size:11px;font-weight:700;letter-spacing:1px;
                text-transform:uppercase;margin-bottom:16px;
            ">🔍 PixelProbe — Design Audit</div>

            <h1 style="
                font-size:32px;font-weight:900;
                background:linear-gradient(135deg,#ffffff,rgba(255,255,255,0.6));
                -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                background-clip:text;margin-bottom:10px;
            ">UI/UX Analysis</h1>

            <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">
                <span style="color:rgba(255,255,255,0.4);font-size:13px;">📁</span>
                <span style="color:rgba(255,255,255,0.6);font-size:13px;">{image_name}</span>
            </div>
            <div style="display:flex;align-items:center;gap:8px;">
                <span style="color:rgba(255,255,255,0.4);font-size:13px;">🕐</span>
                <span style="color:rgba(255,255,255,0.4);font-size:13px;">{now}</span>
            </div>
        </div>

        <!-- Score -->
        <div style="text-align:center;animation:scoreGlow 3s ease-in-out infinite;">
            <svg width="130" height="130" style="transform:rotate(-90deg);">
                <circle cx="65" cy="65" r="55" fill="none" stroke="rgba(255,255,255,0.06)" stroke-width="10"/>
                <circle cx="65" cy="65" r="55" fill="none" stroke="{sc}" stroke-width="10"
                    stroke-dasharray="345" stroke-dashoffset="{345-(345*score/100):.0f}"
                    stroke-linecap="round"/>
            </svg>
            <div style="margin-top:-100px;margin-bottom:60px;">
                <div style="font-size:34px;font-weight:900;color:{sc};
                    text-shadow:0 0 20px {sc};">{score}</div>
                <div style="font-size:12px;color:rgba(255,255,255,0.4);font-weight:600;">{sl}</div>
            </div>
        </div>
    </div>

    <!-- Summary -->
    <div style="
        background:linear-gradient(135deg,rgba(103,50,242,0.1),rgba(10,132,255,0.1));
        border:1px solid rgba(103,50,242,0.2);
        border-radius:14px;padding:18px 20px;margin-top:20px;
    ">
        <div style="font-size:11px;color:rgba(103,50,242,0.9);font-weight:700;
            margin-bottom:8px;text-transform:uppercase;letter-spacing:0.5px;">📝 Summary</div>
        <div style="font-size:15px;color:rgba(255,255,255,0.75);line-height:1.7;">
            {result.get('summary','No summary.')}
        </div>
    </div>
</div>

<!-- Stats -->
<div style="display:flex;gap:14px;margin-bottom:20px;flex-wrap:wrap;animation:fadeIn 0.6s ease 0.2s both;">
    {"".join([f'''
    <div class="glass" style="flex:1;min-width:130px;padding:20px;text-align:center;
        border-top:2px solid {cfg["color"]};transition:all 0.3s;
        box-shadow:0 0 20px rgba(0,0,0,0.3);"
        onmouseover="this.style.boxShadow='0 0 30px {cfg["glow"]}'"
        onmouseout="this.style.boxShadow='0 0 20px rgba(0,0,0,0.3)'">
        <div style="font-size:26px;margin-bottom:8px;">{cfg["icon"]}</div>
        <div style="font-size:26px;font-weight:800;color:{cfg["color"]};
            text-shadow:0 0 12px {cfg["glow"]};margin-bottom:4px;">{val}</div>
        <div style="font-size:12px;color:rgba(255,255,255,0.4);">{lbl}</div>
    </div>'''
    for cfg, val, lbl in [
        ({"color":"#BF5AF2","glow":"rgba(191,90,242,0.4)","icon":"🔍"}, result.get('total_findings',0), "Total Findings"),
        (SEVERITY_CONFIG["critical"], sev.get('critical',0), "Critical"),
        (SEVERITY_CONFIG["high"], sev.get('high',0), "High"),
        ({"color":sc,"glow":f"rgba(0,0,0,0.3)","icon":"⭐"}, f"{score}/100", "Design Score"),
    ]])}
</div>

<!-- Breakdown -->
<div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:20px;animation:fadeIn 0.6s ease 0.3s both;">
    <div class="glass" style="padding:24px;">
        <h3 style="font-size:15px;font-weight:700;color:rgba(255,255,255,0.85);margin-bottom:18px;">
            📊 Severity Breakdown
        </h3>
        {sev_bars}
    </div>
    <div class="glass" style="padding:24px;">
        <h3 style="font-size:15px;font-weight:700;color:rgba(255,255,255,0.85);margin-bottom:18px;">
            🎨 Principles Affected
        </h3>
        {prin_chips}
    </div>
</div>

<!-- Findings -->
<div style="animation:fadeIn 0.6s ease 0.4s both;">
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;">
        <h2 style="font-size:22px;font-weight:800;
            background:linear-gradient(135deg,#ffffff,rgba(255,255,255,0.5));
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">
            🔍 Detailed Findings
        </h2>
        <div style="
            background:rgba(103,50,242,0.2);border:1px solid rgba(103,50,242,0.3);
            color:rgba(255,255,255,0.7);padding:6px 16px;
            border-radius:20px;font-size:13px;font-weight:600;
        ">{result.get('total_findings',0)} issues found</div>
    </div>
    {cards_html}
</div>

<!-- Execution Log -->
<div class="glass" style="padding:24px;margin-top:20px;animation:fadeIn 0.6s ease 0.6s both;">
    <h3 style="font-size:15px;font-weight:700;color:rgba(255,255,255,0.7);margin-bottom:14px;">
        📋 Agent Execution Log
    </h3>
    <div style="font-family:'Courier New',monospace;font-size:12px;">
    {"".join([
        f'<div style="color:{"#30D158" if l["level"]=="INFO" else "#FF9F0A" if l["level"]=="WARNING" else "#FF2D55"};margin-bottom:4px;opacity:0.8;">[{l["timestamp"]}] [{l["level"]}] {l["message"]}</div>'
        for l in result.get("logs",[])
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
        <span style="font-size:16px;">🎯</span>
        <span style="color:rgba(255,255,255,0.4);font-size:13px;">
            PixelProbe &nbsp;•&nbsp; AI-Powered Design Intelligence &nbsp;•&nbsp; {now}
        </span>
    </div>
</div>

</div>
</body>
</html>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    return output_path


def save_json_report(result, output_path):
    clean = {k: v for k, v in result.items() if k != "logs"}
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(clean, f, indent=2, ensure_ascii=False)
    return output_path