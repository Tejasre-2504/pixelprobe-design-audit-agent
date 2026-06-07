"""
main.py
-------
Entry point for the Design Audit Agent — Level 1 & Level 2.
Level 1: python main.py <image>
Level 2: python main.py <baseline_image> <current_image>
"""

import sys
import os
from pathlib import Path
from datetime import datetime
from agent import DesignAuditAgent
from report import generate_html_report, save_json_report
from compare import CompareAgent
from report_compare import generate_compare_html_report


def run_level1(image_path: str):
    print("\n" + "="*60)
    print("   🔍 PixelProbe — AI-Powered Design Intelligence")
    print("   ✨ Catching design issues before your users do.")
    print("="*60 + "\n")

    if not Path(image_path).exists():
        print(f"❌ Image not found: {image_path}")
        sys.exit(1)

    print(f"📸 Analyzing: {image_path}\n")
    agent = DesignAuditAgent()
    result = agent.analyze(image_path)

    if result["status"] == "error":
        print(f"\n❌ Audit failed: {result['error']}")
        sys.exit(1)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    image_stem = Path(image_path).stem
    os.makedirs("outputs", exist_ok=True)

    html_path = f"outputs/{image_stem}_{timestamp}_report.html"
    json_path = f"outputs/{image_stem}_{timestamp}_findings.json"

    generate_html_report(result, image_path, html_path)
    save_json_report(result, json_path)

    print("\n" + "="*60)
    print("   ✅ AUDIT COMPLETE")
    print("="*60)
    print(f"\n📊 Overall Score   : {result['overall_score']}/100")
    print(f"🔍 Total Findings  : {result['total_findings']}")
    print(f"🔴 Critical        : {result['severity_breakdown'].get('critical', 0)}")
    print(f"🟠 High            : {result['severity_breakdown'].get('high', 0)}")
    print(f"🟡 Medium          : {result['severity_breakdown'].get('medium', 0)}")
    print(f"🟢 Low             : {result['severity_breakdown'].get('low', 0)}")
    print(f"🔵 Info            : {result['severity_breakdown'].get('info', 0)}")
    print(f"\n📝 Summary: {result['summary']}")
    print(f"\n📄 HTML Report : {html_path}")
    print(f"📋 JSON Report : {json_path}")
    print("\n" + "="*60 + "\n")


def run_level2(baseline_path: str, current_path: str):
    print("\n" + "="*60)
    print("   🔍 PixelProbe — Before/After Regression Analysis")
    print("   ✨ Detecting regressions before they reach your users.")
    print("="*60 + "\n")

    print(f"📸 Baseline : {baseline_path}")
    print(f"📸 Current  : {current_path}\n")

    agent = CompareAgent()
    result = agent.compare(baseline_path, current_path)

    if result["status"] == "error":
        print(f"\n❌ Comparison failed: {result['error']}")
        sys.exit(1)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs("outputs", exist_ok=True)

    html_path = f"outputs/compare_{timestamp}_report.html"
    json_path = f"outputs/compare_{timestamp}_findings.json"

    generate_compare_html_report(result, html_path)
    save_json_report(result, json_path)

    verdict_icon = "✅" if result["overall_verdict"] == "improved" else "❌" if result["overall_verdict"] == "regressed" else "➡️"

    print("\n" + "="*60)
    print("   ✅ COMPARISON COMPLETE")
    print("="*60)
    print(f"\n{verdict_icon} Overall Verdict       : {result['overall_verdict'].upper()}")
    print(f"📊 Overall Confidence  : {result['overall_confidence']}%")
    print(f"🔍 Total Differences   : {result['total_differences']}")
    print(f"✅ Improvements        : {result['improvement_count']}")
    print(f"❌ Regressions         : {result['regression_count']}")
    print(f"➡️  Neutral             : {result['neutral_count']}")
    print(f"♿ A11y Regressions    : {result['accessibility_regressions']}")
    print(f"\n📝 Summary: {result['net_summary']}")
    print(f"\n📄 HTML Report : {html_path}")
    print(f"📋 JSON Report : {json_path}")
    print("\n" + "="*60 + "\n")


def main():
    if len(sys.argv) == 2:
        run_level1(sys.argv[1])
    elif len(sys.argv) == 3:
        run_level2(sys.argv[1], sys.argv[2])
    else:
        print("\n❌ Usage:")
        print("  Level 1: python main.py <image>")
        print("  Level 2: python main.py <baseline> <current>")
        sys.exit(1)


if __name__ == "__main__":
    main()