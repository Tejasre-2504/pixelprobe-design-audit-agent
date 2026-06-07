"""
compare.py
----------
Level 2 — Before/After Regression Analysis Engine.
Compares two UI screenshots and classifies each visual difference
as improvement, regression, or neutral with confidence scoring.
"""

import json
import base64
import time
from pathlib import Path
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL_NAME = "meta-llama/llama-4-scout-17b-16e-instruct"

COMPARE_PROMPT = """
You are a senior UI/UX design auditor comparing two versions of a UI.
Image 1 = BASELINE (before). Image 2 = CURRENT (after).

Your job is to find ALL visible differences and classify each one.

CLASSIFICATION RULES:
- improvement: change makes UI clearer, more accessible, or more usable
- regression: change makes UI worse, harder to use, or breaks accessibility
- neutral: purely cosmetic with no clear UX impact

CRITICAL RULES:
1. NEVER hallucinate — only report differences actually visible between the two images
2. Include hex color values when colors changed (e.g. #FF0000 → #00FF00)
3. Include pixel estimates when sizes changed (e.g. font 14px → 16px)
4. Flag ANY contrast ratio drops, font size reductions, or spacing compression as regression
5. Confidence score = how certain you are this difference is real (0-100)

OUTPUT FORMAT — return ONLY valid JSON, nothing else:
{
  "overall_verdict": "improved|regressed|neutral",
  "net_summary": "One sentence summary of overall change direction.",
  "improvement_count": <integer>,
  "regression_count": <integer>,
  "neutral_count": <integer>,
  "overall_confidence": <integer 0-100>,
  "differences": [
    {
      "id": "D001",
      "location": "<precise location on page>",
      "what_changed": "<specific description of what changed>",
      "before": "<what it looked like before>",
      "after": "<what it looks like after>",
      "classification": "<improvement|regression|neutral>",
      "ux_impact": "<how this affects user experience>",
      "confidence": <integer 0-100>,
      "accessibility_flag": <true|false>,
      "hex_values": "<e.g. #FFFFFF → #F0F0F0 or null>",
      "pixel_measurements": "<e.g. 14px → 16px or null>"
    }
  ]
}

Find a minimum of 5 differences. Return ONLY the JSON.
"""


class CompareAgent:
    """
    Level 2 — Before/After UI Regression Analysis Agent.
    """

    def __init__(self):
        self.client = client
        self.logs = []

    def _log(self, level: str, message: str):
        entry = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "level": level,
            "message": message
        }
        self.logs.append(entry)
        print(f"[{entry['timestamp']}] [{level}] {message}")

    def _encode_image(self, image_path: str) -> dict:
        path = Path(image_path)
        ext = path.suffix.lower()
        mime_map = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".webp": "image/webp"
        }
        with open(image_path, "rb") as f:
            data = base64.b64encode(f.read()).decode("utf-8")
        return {"mime_type": mime_map[ext], "data": data}

    def _call_groq(self, baseline_path: str, current_path: str, retries: int = 3) -> str:
        baseline = self._encode_image(baseline_path)
        current = self._encode_image(current_path)

        for attempt in range(1, retries + 1):
            try:
                self._log("INFO", f"Calling Groq Vision API for comparison (attempt {attempt}/{retries})...")
                response = self.client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": COMPARE_PROMPT},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:{baseline['mime_type']};base64,{baseline['data']}"
                                    }
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:{current['mime_type']};base64,{current['data']}"
                                    }
                                }
                            ]
                        }
                    ],
                    temperature=0.2,
                    max_tokens=4096
                )
                self._log("INFO", "Groq Vision API comparison call successful.")
                return response.choices[0].message.content
            except Exception as e:
                self._log("WARNING", f"API call failed (attempt {attempt}): {str(e)}")
                if attempt < retries:
                    wait = 2 ** attempt
                    self._log("INFO", f"Retrying in {wait}s...")
                    time.sleep(wait)
                else:
                    raise RuntimeError(f"Groq API failed after {retries} attempts: {str(e)}")

    def _parse_response(self, raw_text: str) -> dict:
        text = raw_text.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:-1])
        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            self._log("ERROR", f"Failed to parse JSON: {e}")
            raise ValueError(f"AI returned invalid JSON: {e}")

    def _validate_differences(self, differences: list):
        valid = []
        rejected = []
        for d in differences:
            required = {"id","location","what_changed","before","after","classification","ux_impact","confidence"}
            missing = required - set(d.keys())
            errors = []
            if missing:
                errors.append(f"Missing fields: {missing}")
            if d.get("classification","") not in {"improvement","regression","neutral"}:
                errors.append(f"Invalid classification: {d.get('classification')}")
            conf = d.get("confidence", -1)
            try:
                conf = float(conf)
                if not (0 <= conf <= 100):
                    errors.append("Confidence out of range")
            except:
                errors.append("Confidence not a number")
            if errors:
                d["_rejection_reasons"] = errors
                rejected.append(d)
            else:
                valid.append(d)
        return valid, rejected

    def compare(self, baseline_path: str, current_path: str) -> dict:
        self._log("INFO", f"Starting comparison: {baseline_path} vs {current_path}")

        # Validate both images exist
        for path in [baseline_path, current_path]:
            if not Path(path).exists():
                return {"status": "error", "error": f"File not found: {path}", "logs": self.logs}

        try:
            raw = self._call_groq(baseline_path, current_path)
        except RuntimeError as e:
            return {"status": "error", "error": str(e), "logs": self.logs}

        try:
            parsed = self._parse_response(raw)
        except ValueError as e:
            return {"status": "error", "error": str(e), "logs": self.logs}

        differences = parsed.get("differences", [])
        self._log("INFO", f"AI returned {len(differences)} differences. Validating...")

        valid_diffs, rejected = self._validate_differences(differences)
        self._log("INFO", f"Validation: {len(valid_diffs)} valid, {len(rejected)} rejected.")

        # Count accessibility flags
        accessibility_regressions = [
            d for d in valid_diffs
            if d.get("accessibility_flag") and d.get("classification") == "regression"
        ]

        result = {
            "status": "success",
            "baseline_image": Path(baseline_path).name,
            "current_image": Path(current_path).name,
            "overall_verdict": parsed.get("overall_verdict", "neutral"),
            "net_summary": parsed.get("net_summary", "No summary."),
            "improvement_count": parsed.get("improvement_count", 0),
            "regression_count": parsed.get("regression_count", 0),
            "neutral_count": parsed.get("neutral_count", 0),
            "overall_confidence": parsed.get("overall_confidence", 0),
            "total_differences": len(valid_diffs),
            "accessibility_regressions": len(accessibility_regressions),
            "differences": valid_diffs,
            "rejected_count": len(rejected),
            "logs": self.logs
        }

        self._log("INFO", f"Comparison complete. Verdict: {result['overall_verdict']}")
        return result