"""
report_compare.py
-----------------
Generates a beautiful HTML report for Level 2 Before/After comparison.
"""

import json
from pathlib import Path
from datetime import datetime


CLASSIFICATION_COLORS = {
    "improvement": {"bg": "#34C759", "light": "#F0FFF4", "border": "#C6F6D5", "icon": "✅", "label": "Improvement"},
    "regression":  {"bg": "#FF3B30", "light": "#FFF0EF", "border": "#FFD5D5", "icon": "❌", "label": "Regression"},
    "neutral":     {"bg": "#8E8E93", "light": "#F8F8F8", "border": "#E0E0E0", "icon": "➡️", "label": "Neutral"},
}

VERDICT_COLORS = {
    "improved":  {"color": "#34C759", "bg": "#F0FFF4", "icon": "🚀", "label": "IMPROVED"},
    "regressed": {"color": "#FF3B30", "bg": "#FFF0EF", "icon": "⚠️", "label": "REGRESSED"},
    "neutral":   {"color": "#8E8E93", "bg": "#F8F8F8", "icon": "➡️", "label": "NEUTRAL"},
}


def _diff_card(diff: dict, index: int) -> str:
    cls = diff.get("classification", "neutral").lower()
    colors = CLASSIFICATION_COLORS.get(cls, CLASSIFICATION_COLORS["neutral"])
    conf = float(diff.get("confidence", 0))
    conf_color = "#27AE60" if conf >= 75 else "#F39C12" if conf >= 50 else "#E74C3C"
    a11y = diff.get("accessibility_flag", False)
    hex_vals = diff.get("hex_values") or ""
    px_vals = diff.get("pixel_measurements") or ""

    a11y_badge = ""
    if a11y:
        a11y_badge = """<span style="
            background:#FF3B30;color:white;
            padding:3px 10px;border-radius:20px;
            font-size:11px;font-weight:700;margin-left:6px;
        ">♿ A11Y RISK</span>"""

    hex_section = ""
    if hex_vals and hex_vals != "null":
        hex_section = f"""
        <div style="
            background:#1a1a2e;color:#00FF88;
            border-radius:8px;padding:10px 14px;
            font-family:monospace;font-size:13px;
            margin-bottom:10px;
        ">🎨 Color change: {hex_vals}</div>"""

    px_section = ""
    if px_vals and px_vals != "null":
        px_section = f"""
        <div style="
            background:#1a1a2e;color:#FFB347;
            border-radius:8px;padding:10px 14px;
            font-family:monospace;font-size:13px;
            margin-bottom:10px;
        ">📐 Size change: {px_vals}</div>"""

    return f"""
    <div style="
        background:white;border-radius:16px;padding:24px;
        margin-bottom:16px;
        border-left:5px solid {colors['bg']};
        box-shadow:0 4px 20px rgba(0,0,0,0.08);
        animation:slideIn 0.4s ease {index*0.08}s both;
        transition:transform 0.2s,box-shadow 0.2s;
    " onmouseover="this.style.transform='translateY(-2px)';this.style.boxShadow='0 8px 30px rgba(0,0,0,0.12)'"
       onmouseout="this.style.transform='translateY(0)';this.style.boxShadow='0 4px 20px rgba(0,0,0,0.08)'">

        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;margin-bottom:16px;">
            <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
                <span style="
                    background:{colors['bg']};color:white;
                    padding:4px 14px;border-radius:20px;
                    font-size:12px;font-weight:700;text-transform:uppercase;
                ">{colors['icon']} {colors['label']}</span>
                {a11y_badge}
            </div>
            <span style="color:#999;font-size:12px;font-weight:600;
                background:#F8F8F8;padding:4px 10px;border-radius:8px;">
                {diff.get('id','?')}
            </span>
        </div>

        <div style="background:{colors['light']};border-radius:10px;padding:12px 16px;margin-bottom:12px;border:1px solid {colors['border']};">
            <div style="font-size:12px;color:#888;font-weight:600;margin-bottom:4px;">📍 Location</div>
            <div style="font-size:14px;color:#333;font-weight:500;">{diff.get('location','?')}</div>
        </div>

        <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:12px;">
            <div style="background:#FFF8F0;border-radius:10px;padding:12px;border:1px solid #FFE0C0;">
                <div style="font-size:11px;color:#E67E22;font-weight:700;margin-bottom:6px;">⬅️ BEFORE</div>
                <div style="font-size:13px;color:#333;line-height:1.5;">{diff.get('before','?')}</div>
            </div>
            <div style="background:#F0FFF8;border-radius:10px;padding:12px;border:1px solid #C0FFE0;">
                <div style="font-size:11px;color:#27AE60;font-weight:700;margin-bottom:6px;">➡️ AFTER</div>
                <div style="font-size:13px;color:#333;line-height:1.5;">{diff.get('after','?')}</div>
            </div>
        </div>

        {hex_section}
        {px_section}

        <div style="background:#F8F9FF;border-radius:10px;padding:12px 16px;margin-bottom:12px;border:1px solid #E8ECFF;">
            <div style="font-size:12px;color:#667eea;font-weight:600;margin-bottom:4px;">👤 UX Impact</div>
            <div style="font-size:14px;color:#444;line-height:1.5;">{diff.get('ux_impact','?')}</div>
        </div>

        <div>
            <div style="font-size:12px;color:#888;font-weight:600;margin-bottom:6px;">Confidence Score</div>
            <div style="display:flex;align-items:center;gap:8px;">
                <div style="flex:1;background:#F0F0F0;border-radius:10px;height:8px;overflow:hidden;">
                    <div style="width:{conf}%;background:{conf_color};height:100%;border-radius:10px;"></div>
                </div>
                <span style="font-size:12px;color:{conf_color};font-weight:700;min-width:36px;">{conf:.0f}%</span>
            </div>
        </div>
    </div>"""


def generate_compare_html_report(result: dict, output_path: str) -> str:
    verdict = result.get("overall_verdict", "neutral").lower()
    vc = VERDICT_COLORS.get(verdict, VERDICT_COLORS["neutral"])
    now = datetime.now().strftime("%B %d, %Y at %H:%M")
    differences = result.get("differences", [])
    conf = result.get("overall_confidence", 0)
    conf_color = "#27AE60" if conf >= 75 else "#F39C12" if conf >= 50 else "#E74C3C"

    # Filter by classification
    improvements = [d for d in differences if d.get("classification") == "improvement"]
    regressions = [d for d in differences if d.get("classification") == "regression"]
    neutrals = [d for d in differences if d.get("classification") == "neutral"]

    # Build tab sections
    def build_section(diffs, start_index=0):
        if not diffs:
            return '<div style="text-align:center;padding:40px;color:#888;">No findings in this category</div>'
        return "".join([_diff_card(d, i + start_index) for i, d in enumerate(diffs)])

    all_cards = build_section(differences)
    regression_cards = build_section(regressions)
    improvement_cards = build_section(improvements)

    # Accessibility regressions
    a11y_count = result.get("accessibility_regressions", 0)
    a11y_badge = ""
    if a11y_count > 0:
        a11y_badge = f"""
        <div style="
            background:#FF3B30;color:white;
            border-radius:14px;padding:16px 24px;
            margin-bottom:20px;
            display:flex;align-items:center;gap:12px;
            box-shadow:0 4px 20px rgba(255,59,48,0.3);
        ">
            <span style="font-size:28px;">♿</span>
            <div>
                <div style="font-size:16px;font-weight:700;">Accessibility Regressions Detected</div>
                <div style="font-size:14px;opacity:0.9;">{a11y_count} change(s) may cause accessibility issues — review immediately</div>
            </div>
        </div>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Design Regression Report</title>
<style>
    *{{margin:0;padding:0;box-sizing:border-box;}}
    body{{
        font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;
        background:linear-gradient(135deg,#1a1a2e 0%,#16213e 50%,#0f3460 100%);
        min-height:100vh;padding:30px 20px;
    }}
    .container{{max-width:900px;margin:0 auto;}}
    @keyframes slideIn{{from{{opacity:0;transform:translateY(20px)}}to{{opacity:1;transform:translateY(0)}}}}
    @keyframes fadeIn{{from{{opacity:0}}to{{opacity:1}}}}
    .tab-content{{display:none;}}
    .tab-content.active{{display:block;}}
    .tab-btn{{
        padding:10px 20px;border:none;border-radius:10px;
        background:rgba(255,255,255,0.1);color:rgba(255,255,255,0.7);
        font-size:13px;font-weight:600;cursor:pointer;
        transition:all 0.2s;
    }}
    .tab-btn.active{{background:white;color:#1a1a2e;}}
    .tab-btn:hover{{background:rgba(255,255,255,0.2);}}
</style>
</head>
<body>
<div class="container">

    <!-- Header -->
    <div style="
        background:white;border-radius:24px;padding:36px;
        margin-bottom:20px;box-shadow:0 20px 60px rgba(0,0,0,0.3);
        animation:fadeIn 0.6s ease;
    ">
        <div style="
            display:inline-block;
            background:linear-gradient(135deg,#1a1a2e,#0f3460);
            color:white;padding:6px 16px;border-radius:20px;
            font-size:12px;font-weight:700;letter-spacing:1px;
            text-transform:uppercase;margin-bottom:12px;
        ">🔍 Before / After Regression Analysis</div>

        <h1 style="font-size:28px;font-weight:800;color:#1a1a2e;margin-bottom:16px;">
            UI/UX Comparison Report
        </h1>

        <!-- Image names -->
        <div style="display:grid;grid-template-columns:1fr auto 1fr;gap:12px;align-items:center;margin-bottom:20px;">
            <div style="background:#FFF8F0;border-radius:12px;padding:12px 16px;border:2px solid #FFE0C0;">
                <div style="font-size:11px;color:#E67E22;font-weight:700;margin-bottom:4px;">⬅️ BASELINE</div>
                <div style="font-size:13px;color:#333;font-weight:600;">{result.get('baseline_image','?')}</div>
            </div>
            <div style="font-size:24px;text-align:center;">→</div>
            <div style="background:#F0FFF8;border-radius:12px;padding:12px 16px;border:2px solid #C0FFE0;">
                <div style="font-size:11px;color:#27AE60;font-weight:700;margin-bottom:4px;">➡️ CURRENT</div>
                <div style="font-size:13px;color:#333;font-weight:600;">{result.get('current_image','?')}</div>
            </div>
        </div>

        <!-- Verdict -->
        <div style="
            background:{vc['bg']};border-radius:16px;padding:20px 24px;
            border:2px solid {vc['color']}40;
            display:flex;justify-content:space-between;align-items:center;
            flex-wrap:wrap;gap:12px;
        ">
            <div style="display:flex;align-items:center;gap:12px;">
                <span style="font-size:36px;">{vc['icon']}</span>
                <div>
                    <div style="font-size:12px;color:#888;font-weight:600;">Overall Verdict</div>
                    <div style="font-size:28px;font-weight:900;color:{vc['color']};">{vc['label']}</div>
                </div>
            </div>
            <div style="text-align:right;">
                <div style="font-size:12px;color:#888;margin-bottom:4px;">Confidence</div>
                <div style="font-size:32px;font-weight:800;color:{conf_color};">{conf}%</div>
            </div>
        </div>

        <!-- Net Summary -->
        <div style="
            background:linear-gradient(135deg,#F8F9FF,#EEF2FF);
            border-radius:14px;padding:16px 20px;margin-top:16px;
            border-left:4px solid #667eea;
        ">
            <div style="font-size:12px;color:#667eea;font-weight:700;margin-bottom:4px;">📝 NET SUMMARY</div>
            <div style="font-size:15px;color:#333;line-height:1.7;">{result.get('net_summary','')}</div>
        </div>

        <div style="color:#aaa;font-size:13px;margin-top:12px;">🕐 {now}</div>
    </div>

    <!-- Stats -->
    <div style="display:flex;gap:12px;margin-bottom:20px;flex-wrap:wrap;animation:fadeIn 0.6s ease 0.2s both;">
        <div style="flex:1;min-width:120px;background:white;border-radius:16px;padding:20px;text-align:center;box-shadow:0 4px 20px rgba(0,0,0,0.1);border-top:4px solid #667eea;">
            <div style="font-size:28px;margin-bottom:6px;">🔍</div>
            <div style="font-size:28px;font-weight:800;color:#667eea;">{result.get('total_differences',0)}</div>
            <div style="font-size:12px;color:#888;">Total Changes</div>
        </div>
        <div style="flex:1;min-width:120px;background:white;border-radius:16px;padding:20px;text-align:center;box-shadow:0 4px 20px rgba(0,0,0,0.1);border-top:4px solid #34C759;">
            <div style="font-size:28px;margin-bottom:6px;">✅</div>
            <div style="font-size:28px;font-weight:800;color:#34C759;">{result.get('improvement_count',0)}</div>
            <div style="font-size:12px;color:#888;">Improvements</div>
        </div>
        <div style="flex:1;min-width:120px;background:white;border-radius:16px;padding:20px;text-align:center;box-shadow:0 4px 20px rgba(0,0,0,0.1);border-top:4px solid #FF3B30;">
            <div style="font-size:28px;margin-bottom:6px;">❌</div>
            <div style="font-size:28px;font-weight:800;color:#FF3B30;">{result.get('regression_count',0)}</div>
            <div style="font-size:12px;color:#888;">Regressions</div>
        </div>
        <div style="flex:1;min-width:120px;background:white;border-radius:16px;padding:20px;text-align:center;box-shadow:0 4px 20px rgba(0,0,0,0.1);border-top:4px solid #FF3B30;">
            <div style="font-size:28px;margin-bottom:6px;">♿</div>
            <div style="font-size:28px;font-weight:800;color:#FF3B30;">{a11y_count}</div>
            <div style="font-size:12px;color:#888;">A11y Risks</div>
        </div>
    </div>

    {a11y_badge}

    <!-- Tabs -->
    <div style="margin-bottom:16px;animation:fadeIn 0.6s ease 0.3s both;">
        <div style="display:flex;gap:8px;flex-wrap:wrap;">
            <button class="tab-btn active" onclick="showTab('all')">
                All Changes ({result.get('total_differences',0)})
            </button>
            <button class="tab-btn" onclick="showTab('regressions')" style="{'background:rgba(255,59,48,0.3);color:white;' if regressions else ''}">
                ❌ Regressions ({len(regressions)})
            </button>
            <button class="tab-btn" onclick="showTab('improvements')">
                ✅ Improvements ({len(improvements)})
            </button>
        </div>
    </div>

    <!-- Tab Contents -->
    <div id="tab-all" class="tab-content active">{all_cards}</div>
    <div id="tab-regressions" class="tab-content">{regression_cards}</div>
    <div id="tab-improvements" class="tab-content">{improvement_cards}</div>

    <!-- Execution Log -->
    <div style="
        background:rgba(0,0,0,0.4);border-radius:20px;padding:24px;
        margin-top:20px;animation:fadeIn 0.6s ease 0.6s both;
    ">
        <h3 style="color:white;font-size:16px;font-weight:700;margin-bottom:14px;">📋 Agent Execution Log</h3>
        <div style="font-family:monospace;font-size:12px;">
        {"".join([
            f'<div style="color:{"#00FF88" if l["level"]=="INFO" else "#FFB347" if l["level"]=="WARNING" else "#FF6B6B"};margin-bottom:4px;">[{l["timestamp"]}] [{l["level"]}] {l["message"]}</div>'
            for l in result.get("logs", [])
        ])}
        </div>
    </div>

    <div style="text-align:center;padding:24px;color:rgba(255,255,255,0.5);font-size:13px;">
        Generated by Design Audit Agent — Level 2 &nbsp;•&nbsp; {now}
    </div>

</div>

<script>
function showTab(name) {{
    document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.getElementById('tab-' + name).classList.add('active');
    event.target.classList.add('active');
}}
</script>
</body>
</html>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    return output_path