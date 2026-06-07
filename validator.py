"""
validator.py
------------
Guard rails for the Design Audit Agent.
Validates image inputs and AI-generated outputs to prevent hallucinations.
"""
 
import os
from pathlib import Path
from typing import Tuple
 
 
SUPPORTED_FORMATS = {".png", ".jpg", ".jpeg", ".webp"}
MAX_FILE_SIZE_MB = 20
 
 
def validate_image_input(image_path: str) -> Tuple[bool, str]:
    """
    Validates the input image before sending to AI.
    Returns (is_valid, error_message).
    """
    path = Path(image_path)
 
    # Check file exists
    if not path.exists():
        return False, f"File not found: {image_path}"
 
    # Check file extension
    if path.suffix.lower() not in SUPPORTED_FORMATS:
        return False, (
            f"Unsupported format '{path.suffix}'. "
            f"Supported: {', '.join(SUPPORTED_FORMATS)}"
        )
 
    # Check file size
    size_mb = path.stat().st_size / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        return False, f"File too large ({size_mb:.1f}MB). Maximum is {MAX_FILE_SIZE_MB}MB."
 
    # Check file is not empty
    if path.stat().st_size == 0:
        return False, "File is empty."
 
    return True, "OK"
 
 
def validate_ai_output(findings: list) -> Tuple[list, list]:
    """
    Validates AI-generated findings to strip hallucinations.
    Returns (valid_findings, rejected_findings).
    """
    REQUIRED_FIELDS = {
        "id", "principle", "severity", "location",
        "issue", "user_impact", "recommendation", "confidence"
    }
 
    VALID_SEVERITIES = {"critical", "high", "medium", "low", "info"}
    VALID_PRINCIPLES = {
        "visual_hierarchy", "contrast", "spacing",
        "alignment", "consistency"
    }
 
    valid = []
    rejected = []
 
    for finding in findings:
        errors = []
 
        # Check all required fields exist
        missing = REQUIRED_FIELDS - set(finding.keys())
        if missing:
            errors.append(f"Missing fields: {missing}")
 
        # Check severity is valid
        if finding.get("severity", "").lower() not in VALID_SEVERITIES:
            errors.append(f"Invalid severity: {finding.get('severity')}")
 
        # Check principle is valid
        if finding.get("principle", "").lower() not in VALID_PRINCIPLES:
            errors.append(f"Invalid principle: {finding.get('principle')}")
 
        # Check confidence is a number between 0 and 100
        conf = finding.get("confidence", -1)
        try:
            conf = float(conf)
            if not (0 <= conf <= 100):
                errors.append(f"Confidence out of range: {conf}")
        except (TypeError, ValueError):
            errors.append(f"Confidence not a number: {conf}")
 
        # Check critical findings have strong confidence (anti-hallucination)
        if finding.get("severity", "").lower() == "critical" and float(finding.get("confidence", 0)) < 75:
            errors.append("Critical finding must have confidence >= 75%")
 
        # Check issue and recommendation are not empty or too short
        if len(str(finding.get("issue", ""))) < 10:
            errors.append("Issue description too short (possible hallucination)")
 
        if len(str(finding.get("recommendation", ""))) < 10:
            errors.append("Recommendation too short (not actionable)")
 
        if errors:
            finding["_rejection_reasons"] = errors
            rejected.append(finding)
        else:
            valid.append(finding)
 
    return valid, rejected
