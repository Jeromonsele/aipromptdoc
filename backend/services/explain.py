import re
import os
import logging
from typing import List, Tuple, Optional
from services.helpers import smart_split

logger = logging.getLogger(__name__)

def extract_entities(goal: str) -> Tuple[List[str], List[str], List[str], List[str]]:
    """Fast heuristic extraction of intent components"""
    inputs, outputs, constraints, risks = [], [], [], []
    
    goal_lower = goal.lower()
    
    # Input detection
    if "transcript" in goal_lower:
        inputs.append("transcript_text")
    if "document" in goal_lower or "text" in goal_lower:
        inputs.append("document_text")
    if "image" in goal_lower or "photo" in goal_lower:
        inputs.append("image_file")
    if "data" in goal_lower or "csv" in goal_lower:
        inputs.append("dataset")
    
    # Output detection
    if "summary" in goal_lower or "summarize" in goal_lower:
        outputs.append("summary_text")
    if "action" in goal_lower or "task" in goal_lower:
        outputs.append("action_items")
    if "classify" in goal_lower or "category" in goal_lower:
        outputs.append("classification")
    if "extract" in goal_lower:
        outputs.append("extracted_entities")
    
    # Constraint detection
    if "json" in goal_lower:
        constraints.append("output JSON format")
    if re.search(r"\b\d+\s*bullet", goal_lower):
        constraints.append("fixed bullet count")
    if re.search(r"\b\d+\s*word", goal_lower):
        constraints.append("word count limit")
    if "concise" in goal_lower or "brief" in goal_lower:
        constraints.append("brevity required")
    
    # Risk detection
    if not inputs:
        risks.append("input type unclear")
    if not outputs:
        risks.append("expected output format ambiguous")
    if "json" in goal_lower and "schema" not in goal_lower:
        risks.append("JSON structure not specified")
    if len(goal.split()) < 5:
        risks.append("goal too vague")
    
    return inputs or ["raw_text"], outputs or ["structured_output"], constraints, risks

def calculate_readiness_score(goal: str, inputs: List[str], outputs: List[str], 
                              constraints: List[str], risks: List[str], 
                              missing: List[str]) -> int:
    """Calculate readiness score from 1-10"""
    score = 10
    
    # Deduct for missing clarity
    if len(missing) > 0:
        score -= len(missing) * 2
    
    # Deduct for risks
    if "input type unclear" in risks:
        score -= 1
    if "expected output format ambiguous" in risks:
        score -= 1
    if "goal too vague" in risks:
        score -= 2
    
    # Bonus for clarity
    if len(constraints) >= 2:
        score += 1
    if "raw_text" not in inputs:
        score += 1
    
    return max(1, min(10, score))

def refine_with_llm(goal: str, heuristic_spec: dict, provider: str = "openai") -> dict:
    """Use LLM to refine the heuristic spec - with graceful fallback"""
    try:
        if provider == "openai":
            from openai import OpenAI
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            
            prompt = f"""You are a prompt engineering assistant. Analyze this goal and extract structured information.

Goal: {goal}

Return JSON with these fields:
- intent: clear 1-sentence statement of what user wants
- inputs: array of input types needed (e.g., ["transcript_text", "meeting_date"])
- outputs: array of expected outputs (e.g., ["action_items", "summary"])
- constraints: array of requirements (e.g., ["output JSON", "max 6 bullets"])
- format: output format (e.g., "JSON", "plain text", "markdown")
- risks: array of potential issues (e.g., ["ambiguous date format"])
- missing: array of actionable gaps to fill (e.g., ["specify JSON schema"])

Be precise and actionable."""

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            
            import json
            llm_result = json.loads(response.choices[0].message.content)
            
            # Merge with heuristic spec (LLM takes precedence)
            refined = {
                "intent": llm_result.get("intent", heuristic_spec["intent"]),
                "inputs": llm_result.get("inputs", heuristic_spec["inputs"]),
                "outputs": llm_result.get("outputs", heuristic_spec["outputs"]),
                "constraints": llm_result.get("constraints", heuristic_spec["constraints"]),
                "format": llm_result.get("format", heuristic_spec["format"]),
                "risks": llm_result.get("risks", heuristic_spec["risks"]),
                "missing": llm_result.get("missing", heuristic_spec["missing"]),
            }
            
            # Recalculate readiness score with refined data
            refined["readiness_score"] = calculate_readiness_score(
                goal, refined["inputs"], refined["outputs"], 
                refined["constraints"], refined["risks"], refined["missing"]
            )
            
            return refined
            
    except Exception as e:
        logger.warning(f"LLM refinement failed: {e}. Falling back to heuristics.")
    
    return heuristic_spec

def explain(goal: str, constraints_text: str = "", desired_format: str = "", 
            use_llm: bool = False) -> dict:
    """
    Explain a prompt goal with hybrid heuristic + optional LLM refinement
    
    Args:
        goal: User's natural language goal
        constraints_text: Additional constraints
        desired_format: Preferred output format
        use_llm: Whether to refine with LLM (requires OPENAI_API_KEY)
    """
    # Fast heuristic baseline
    inputs, outputs, constraints, risks = extract_entities(goal)
    
    if constraints_text:
        constraints += [c.strip() for c in smart_split(constraints_text) if c.strip()]
    
    fmt = desired_format or ("JSON" if any("json" in c.lower() for c in constraints) else "plain text")
    
    # Detect missing information
    missing = []
    if "JSON" in fmt.upper() and "schema" not in goal.lower():
        missing.append("provide JSON fields or a sample object")
    if not any(word in goal.lower() for word in ["summarize", "extract", "classify", "generate", "analyze"]):
        missing.append("clarify the specific action (summarize, extract, classify, etc.)")
    if len(goal.split()) < 8:
        missing.append("add more context about the task requirements")
    
    readiness = calculate_readiness_score(goal, inputs, outputs, constraints, risks, missing)
    
    heuristic_spec = {
        "intent": goal.strip(),
        "inputs": inputs,
        "outputs": outputs,
        "constraints": constraints,
        "format": fmt,
        "risks": risks,
        "readiness_score": readiness,
        "missing": missing,
    }
    
    # Optional LLM refinement
    if use_llm and os.getenv("OPENAI_API_KEY"):
        return refine_with_llm(goal, heuristic_spec)
    
    return heuristic_spec
