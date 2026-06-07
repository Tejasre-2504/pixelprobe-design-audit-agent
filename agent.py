"""
agent.py
--------
Core Design Audit Agent — powered by Groq Vision (LLaMA).
"""

import os
import json
import base64
import time
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq
from PIL import Image
from validator import validate_image_input, validate_ai_output

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise EnvironmentError("GROQ_API_KEY not found in .env file.")

client = Groq(api_key=GROQ_API_KEY)
MODEL_NAME = "meta-llama/llama-4-scout-17b-16e-instruct"

SYSTEM_PROMPT = """
You are a senior UI/UX design auditor with 15+ years of experience.
Your job is to analyze a UI screenshot and identify REAL, VISIBLE design issues.

CRITICAL RULES:
1. NEVER hallucinate — every finding MUST reference something visibly present in the image.
2. Be SPECIFIC, not vague.
3. Every finding must have a precise location.
4. Confidence score reflects how certain you are the issue is real (0-100).
5. Critical severity requires confidence >= 75.

EVALUATE THESE 5 PRINCIPLES:
1. visual_hierarchy  — Are primary actions clearly more prominent than secondary ones?
2. contrast          — Do text/background combinations meet WCAG AA?
3. spacing           — Is whitespace consistent?
4. alignment         — Are elements visually aligned?
5. consistency       — Are colors, fonts, button styles uniform?

OUTPUT FORMAT — return ONLY valid JSON, nothing else:
{
  "summary": "One sentence overall assessment.",
  "overall_score": <integer 0-100>,
  "findings": [
    {
      "id": "F001",
      "principle": "<visual_hierarchy|contrast|spacing|alignment|consistency>",
      "severity": "<critical|high|medium|low|info>",
      "location": "<precise location on the page>",
      "issue": "<specific description of what is wrong>",
      "user_impact": "<how this affects the user experience>",
      "recommendation": "<specific actionable fix>",
      "confidence": <integer 0-100>
    }
  ]
}

Return at minimum 5 findings. Return ONLY the JSON — no markdown, no explanation.
"""


class DesignAuditAgent:

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
            image_data = base64.b64encode(f.read()).decode("utf-8")
        return {"mime_type": mime_map[ext], "data": image_data}

    def _get_image_info(self, image_path: str) -> dict:
        img = Image.open(image_path)
        return {
            "filename": Path(image_path).name,
            "format": img.format,
            "size": f"{img.width}x{img.height}px",
            "mode": img.mode
        }

    def _call_groq(self, image_path: str, retries: int = 3) -> str:
        image_data = self._encode_image(image_path)
        for attempt in range(1, retries + 1):
            try:
                self._log("INFO", f"Calling Groq Vision API (attempt {attempt}/{retries})...")
                response = self.client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": SYSTEM_PROMPT
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:{image_data['mime_type']};base64,{image_data['data']}"
                                    }
                                }
                            ]
                        }
                    ],
                    temperature=0.2,
                    max_tokens=4096
                )
                self._log("INFO", "Groq Vision API call successful.")
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
            self._log("ERROR", f"Failed to parse JSON response: {e}")
            raise ValueError(f"AI returned invalid JSON: {e}")

    def _calculate_score(self, findings: list) -> int:
        """
        Calculate design score mathematically from findings.
        Starts at 100 and deducts points based on severity
        and confidence of each finding.
        More critical findings = lower score.
        All low/info findings = higher score.
        """
        if not findings:
            return 95

        # Points deducted per severity level
        deductions = {
            "critical": 20,
            "high":     12,
            "medium":    7,
            "low":       3,
            "info":      1
        }

        total_deduction = 0
        for f in findings:
            sev = f.get("severity", "info").lower()
            weight = deductions.get(sev, 1)
            # Weight deduction by confidence — low confidence = smaller deduction
            confidence = float(f.get("confidence", 50)) / 100
            total_deduction += weight * confidence

        score = max(0, min(100, round(100 - total_deduction)))
        self._log("INFO", f"Design score calculated: {score}/100 (deducted {total_deduction:.1f} points from {len(findings)} findings)")
        return score

    def analyze(self, image_path: str) -> dict:
        self._log("INFO", f"Starting design audit for: {image_path}")

        self._log("INFO", "Validating input image...")
        is_valid, error_msg = validate_image_input(image_path)
        if not is_valid:
            self._log("ERROR", f"Input validation failed: {error_msg}")
            return {"status": "error", "error": error_msg, "logs": self.logs}
        self._log("INFO", "Input validation passed.")

        image_info = self._get_image_info(image_path)
        self._log("INFO", f"Image info: {image_info}")

        try:
            raw_response = self._call_groq(image_path)
        except RuntimeError as e:
            return {"status": "error", "error": str(e), "logs": self.logs}

        try:
            parsed = self._parse_response(raw_response)
        except ValueError as e:
            return {"status": "error", "error": str(e), "logs": self.logs}

        raw_findings = parsed.get("findings", [])
        self._log("INFO", f"AI returned {len(raw_findings)} findings. Validating...")

        valid_findings, rejected_findings = validate_ai_output(raw_findings)
        self._log("INFO", f"Validation complete: {len(valid_findings)} valid, {len(rejected_findings)} rejected.")

        if rejected_findings:
            for r in rejected_findings:
                self._log("WARNING", f"Rejected finding {r.get('id','?')}: {r.get('_rejection_reasons')}")

        # Calculate score mathematically — never trust AI's own score
        calculated_score = self._calculate_score(valid_findings)

        result = {
            "status": "success",
            "image_info": image_info,
            "summary": parsed.get("summary", "No summary provided."),
            "overall_score": calculated_score,
            "total_findings": len(valid_findings),
            "findings": valid_findings,
            "rejected_findings_count": len(rejected_findings),
            "severity_breakdown": self._count_severities(valid_findings),
            "principle_breakdown": self._count_principles(valid_findings),
            "logs": self.logs
        }

        self._log("INFO", f"Audit complete. {len(valid_findings)} findings returned.")
        return result

    def _count_severities(self, findings: list) -> dict:
        counts = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
        for f in findings:
            sev = f.get("severity", "").lower()
            if sev in counts:
                counts[sev] += 1
        return counts

    def _count_principles(self, findings: list) -> dict:
        counts = {
            "visual_hierarchy": 0, "contrast": 0,
            "spacing": 0, "alignment": 0, "consistency": 0
        }
        for f in findings:
            p = f.get("principle", "").lower()
            if p in counts:
                counts[p] += 1
        return counts