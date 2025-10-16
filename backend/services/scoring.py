"""
Rule-based prompt scoring engine.
Fast, deterministic scoring for prompt quality assessment.
"""

import logging
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)


def score_prompt(prompt: str) -> Dict:
    """
    Score a prompt on a 1-10 scale using rule-based heuristics.
    
    Returns:
        {
            "score": int (1-10),
            "problems": List[str],
            "expected_quality_pct": int (20-100)
        }
    """
    problems = []
    
    def miss(condition: bool, message: str):
        """Helper to add problem if condition is true"""
        if condition:
            problems.append(message)
    
    lp = prompt.lower()
    
    # Check for common prompt quality issues
    miss("task:" not in lp and "you are" not in lp, "No explicit task or role")
    miss("json" not in lp and "format" not in lp, "No explicit output format")
    miss("example" not in lp and "few-shot" not in lp, "No examples provided")
    miss("constraints" not in lp and "exactly" not in lp, "No constraints or bounds")
    miss("acceptance" not in lp and "quality check" not in lp, "No acceptance checks")
    miss("schema" not in lp and "fields" not in lp, "No schema or fields listed")
    
    # Additional quality checks
    miss(len(prompt.strip()) < 20, "Prompt too short (< 20 chars)")
    miss("summarize" in lp and "bullet" not in lp and "point" not in lp, "No output structure for summary")
    miss("extract" in lp and "list" not in lp and "array" not in lp, "No collection format for extraction")
    
    # Calculate score (10 - number of problems, capped 1-10)
    base = 10 - len(problems)
    score = max(1, min(10, base))
    
    # Expected quality percentage (rough estimate)
    expected_quality = 20 + score * 8  # 20% at score=1, 100% at score=10
    
    return {
        "score": score,
        "problems": problems,
        "expected_quality_pct": expected_quality
    }


def optimize_prompt(original_prompt: str, context: str = "") -> Tuple[str, List[str]]:
    """
    Optimize a prompt by applying fixes for identified problems.
    
    Returns:
        (optimized_prompt, fixes_applied)
    """
    fixes = []
    lines = []
    lp = original_prompt.lower()
    
    # Build optimized prompt
    
    # Add role if missing
    if "task:" not in lp and "you are" not in lp:
        lines.append("You are a precise and helpful assistant.")
        fixes.append("Added explicit role definition")
    
    # Add clear task statement
    task_line = f"Task: {original_prompt.strip()}"
    if not original_prompt.strip().endswith("."):
        task_line += "."
    lines.append(task_line)
    
    # Add output format if missing
    if "json" not in lp and "format" not in lp:
        lines.append("")
        lines.append("Output format: Provide your response in a clear, structured format.")
        fixes.append("Added output format specification")
    
    # Add constraints if missing
    if "constraints" not in lp and "exactly" not in lp:
        lines.append("")
        lines.append("Constraints:")
        lines.append("- Be concise and accurate")
        lines.append("- Include only relevant information")
        fixes.append("Added constraints for quality control")
    
    # Add quality checks if missing
    if "acceptance" not in lp and "quality check" not in lp:
        lines.append("")
        lines.append("Quality checks:")
        lines.append("- Verify all required information is included")
        lines.append("- Ensure output is consistent and well-formatted")
        fixes.append("Added quality acceptance criteria")
    
    # Add schema guidance if JSON mentioned but no schema
    if ("json" in lp or "JSON" in original_prompt) and "schema" not in lp and "fields" not in lp:
        lines.append("")
        lines.append("Required fields: Specify the exact JSON structure needed")
        fixes.append("Added schema/fields specification")
    
    # Add examples if appropriate task type
    if ("summarize" in lp or "extract" in lp or "classify" in lp) and "example" not in lp:
        lines.append("")
        lines.append("Approach: Follow best practices for this task type")
        fixes.append("Added task-specific guidance")
    
    optimized = "\n".join(lines)
    
    return optimized, fixes


def compare_prompts(original: str, context: str = "") -> Dict:
    """
    Compare original prompt with optimized version.
    
    Returns comprehensive before/after analysis.
    """
    # Score original
    before = score_prompt(original)
    before["prompt"] = original
    
    # Generate optimized version
    optimized, fixes = optimize_prompt(original, context)
    after = score_prompt(optimized)
    after["prompt"] = optimized
    after["fixes"] = fixes
    
    # Calculate improvement
    if before["score"] > 0:
        improvement_pct = int(((after["expected_quality_pct"] - before["expected_quality_pct"]) 
                               / before["expected_quality_pct"]) * 100)
    else:
        improvement_pct = 400  # Max for very bad prompts
    
    return {
        "before": before,
        "after": after,
        "improvement_pct": improvement_pct
    }

