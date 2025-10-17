from typing import Dict, Union
import json
from services.explain import explain
from services.helpers import smart_split

def make_directive(spec: dict) -> str:
    """Traditional directive-style prompt with clear instructions"""
    lines = []
    lines.append("You are a precise assistant. Follow instructions exactly.")
    lines.append(f"Task: {spec['intent']}")
    if spec['constraints']:
        lines.append("Constraints:")
        for c in spec['constraints']:
            lines.append(f"- {c}")
    lines.append("Quality checks:")
    lines.append("- Output must be consistent, concise, and correct.")
    lines.append("- If information is missing, ask a single clarifying question.")
    return "\n".join(lines)

def make_schema_json(spec: dict) -> str:
    """JSON schema-validated output prompt"""
    # minimal schema derived from outputs
    fields = ["value"]
    if "action_items" in spec["outputs"]:
        fields = ["bullet", "owner_initials", "due_date"]
    elif "summary" in spec["outputs"] or "summary_text" in spec["outputs"]:
        fields = ["summary", "key_points"]
    elif "classification" in spec["outputs"]:
        fields = ["category", "confidence"]
    
    schema = {
        "type": "object",
        "properties": {f: {"type": "string"} for f in fields},
        "required": fields,
        "additionalProperties": False
    }
    body = f"""You are a validator. Return only JSON that validates against this schema. 
Schema:
{json.dumps(schema, indent=2)}

Task: {spec['intent']}
Do not include any commentary outside JSON.
"""
    return body

def make_few_shot(spec: dict) -> str:
    """Few-shot prompt with 2-3 task-relevant examples"""
    lines = []
    lines.append("You are a precise assistant. Learn from these examples, then complete the task.")
    lines.append("")
    
    # Generate examples based on task type
    task_lower = spec['intent'].lower()
    
    if "summarize" in task_lower or "summary" in task_lower:
        lines.append("Example 1:")
        lines.append("Input: Long meeting transcript discussing Q4 budget...")
        lines.append("Output: Q4 budget approved at $2M. Marketing gets 40%, engineering 35%, ops 25%.")
        lines.append("")
        lines.append("Example 2:")
        lines.append("Input: Email thread about project timeline...")
        lines.append("Output: Project deadline moved to Dec 15. Team needs 2 more developers.")
        
    elif "action" in task_lower or "task" in task_lower:
        lines.append("Example 1:")
        lines.append("Input: Meeting notes about new feature launch...")
        lines.append("Output:")
        lines.append("- [ ] Draft product spec (Sarah, Nov 1)")
        lines.append("- [ ] Review with eng team (Mike, Nov 5)")
        lines.append("")
        lines.append("Example 2:")
        lines.append("Input: Discussion about bug fixes...")
        lines.append("Output:")
        lines.append("- [ ] Fix login issue (Dev team, urgent)")
        lines.append("- [ ] Update docs (Tech writer, Nov 10)")
        
    elif "extract" in task_lower:
        lines.append("Example 1:")
        lines.append("Input: Customer feedback mentioning pricing and support...")
        lines.append("Output: {\"topics\": [\"pricing\", \"support\"], \"sentiment\": \"mixed\"}")
        lines.append("")
        lines.append("Example 2:")
        lines.append("Input: Product review discussing quality and delivery...")
        lines.append("Output: {\"topics\": [\"quality\", \"delivery\"], \"sentiment\": \"positive\"}")
    
    else:
        # Generic examples
        lines.append("Example 1:")
        lines.append("Input: [sample input matching your task]")
        lines.append("Output: [desired output format]")
        lines.append("")
        lines.append("Example 2:")
        lines.append("Input: [another sample input]")
        lines.append("Output: [desired output format]")
    
    lines.append("")
    lines.append(f"Now complete this task: {spec['intent']}")
    lines.append("Input: {{your_input_here}}")
    
    if spec['constraints']:
        lines.append("")
        lines.append("Constraints:")
        for c in spec['constraints']:
            lines.append(f"- {c}")
    
    return "\n".join(lines)

def make_planner_executor(spec: dict) -> Dict[str, str]:
    """Returns TWO prompts: planner and executor for complex tasks"""
    
    planner = f"""You are a task planner. Break down this goal into concrete steps.

Goal: {spec['intent']}

Output a JSON plan with:
1. "steps": array of step descriptions
2. "variables": object with key data to extract
3. "dependencies": array showing step order

Example:
{{
  "steps": ["Extract key points", "Organize by theme", "Format output"],
  "variables": {{"main_theme": "", "key_points": []}},
  "dependencies": ["step1 → step2 → step3"]
}}

Return only the JSON plan."""

    executor = f"""You are a task executor. You receive a plan and execute one step at a time.

Original goal: {spec['intent']}

You will receive:
- plan: the full task plan from the planner
- current_step: which step to execute (e.g., "step1", "step2")
- context: any data from previous steps

Execute the current step precisely and return results in the format specified by the plan.

Constraints:
"""
    if spec['constraints']:
        for c in spec['constraints']:
            executor += f"\n- {c}"
    else:
        executor += "\n- Follow the plan exactly"
        executor += "\n- Be precise and thorough"
    
    return {
        "planner_prompt": planner,
        "executor_prompt": executor
    }

def make_rubric_scored(spec: dict) -> str:
    """Prompt with self-grading rubric for quality control"""
    lines = []
    lines.append("You are a quality-focused assistant. Complete the task, then grade your work.")
    lines.append("")
    lines.append(f"Task: {spec['intent']}")
    lines.append("")
    
    if spec['constraints']:
        lines.append("Constraints:")
        for c in spec['constraints']:
            lines.append(f"- {c}")
        lines.append("")
    
    lines.append("After completing the task, grade your output against this rubric:")
    lines.append("")
    lines.append("Rubric (score each 1-5):")
    
    # Generate rubric based on task type
    task_lower = spec['intent'].lower()
    
    if "json" in task_lower or any("json" in c.lower() for c in spec.get('constraints', [])):
        lines.append("1. Valid JSON syntax: Can be parsed without errors")
        lines.append("2. Complete fields: All required fields present")
        lines.append("3. Accurate data: Values match the input correctly")
        lines.append("4. Consistent format: Follows schema exactly")
    elif "summary" in task_lower:
        lines.append("1. Completeness: Covers all key points from input")
        lines.append("2. Conciseness: No unnecessary details")
        lines.append("3. Accuracy: Facts correctly represented")
        lines.append("4. Clarity: Easy to understand")
    elif "action" in task_lower or "task" in task_lower:
        lines.append("1. Completeness: All action items identified")
        lines.append("2. Specificity: Clear owners and deadlines")
        lines.append("3. Actionability: Tasks are concrete and doable")
        lines.append("4. Priority: Urgent items clearly marked")
    else:
        lines.append("1. Accuracy: Output matches task requirements")
        lines.append("2. Completeness: Nothing important missing")
        lines.append("3. Format: Follows specified structure")
        lines.append("4. Quality: Professional and polished")
    
    lines.append("")
    lines.append("Self-check process:")
    lines.append("1. Complete the task")
    lines.append("2. Score your output (1-5 on each criterion)")
    lines.append("3. If total score < 16/20, revise and rescore")
    lines.append("4. Return final output only (not the scores)")
    
    return "\n".join(lines)

def code_wrappers(prompt_body: str, model: str = "gpt-4o-mini", params: dict = None) -> Dict[str, str]:
    """Generate code wrappers in Python, JavaScript, and cURL"""
    params = params or {}
    temperature = params.get("temperature", 0.2)
    max_tokens = params.get("max_tokens", None)
    
    # Escape for JSON properly
    import json
    prompt_escaped = json.dumps(prompt_body)
    
    # Build params string
    param_lines_py = [f'    model="{model}"', f'    messages=[{{"role":"user","content":{prompt_escaped}}}]']
    param_lines_js = [f'  model: "{model}"', f'  messages: [{{ role: "user", content: {prompt_escaped} }}]']
    param_dict = {"model": model, "messages": [{"role": "user", "content": prompt_body}]}
    
    if temperature is not None:
        param_lines_py.append(f'    temperature={temperature}')
        param_lines_js.append(f'  temperature: {temperature}')
        param_dict["temperature"] = temperature
    
    if max_tokens:
        param_lines_py.append(f'    max_tokens={max_tokens}')
        param_lines_js.append(f'  max_tokens: {max_tokens}')
        param_dict["max_tokens"] = max_tokens
    
    py = f"""# Python example
from openai import OpenAI
client = OpenAI()
resp = client.chat.completions.create(
{',\\n'.join(param_lines_py)}
)
print(resp.choices[0].message.content)
"""
    
    js = f"""// JavaScript example
import OpenAI from "openai";
const client = new OpenAI();
const resp = await client.chat.completions.create({{
{',\\n'.join(param_lines_js)}
}});
console.log(resp.choices[0].message.content);
"""
    
    curl_data = json.dumps(param_dict, indent=2)
    curl = f"""# cURL example
curl https://api.openai.com/v1/chat/completions \\
  -H "Authorization: Bearer $OPENAI_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{curl_data}'
"""
    
    return {"python": py, "javascript": js, "curl": curl}

def generate(goal: str, style: str = "directive", model: str = "gpt-4o-mini", 
              params: dict = None) -> dict:
    """
    Generate a prompt in the specified style
    
    Args:
        goal: User's natural language goal
        style: One of: directive, schema_json, few_shot, planner_executor, rubric_scored
        model: LLM model to use (default: gpt-4o-mini)
        params: Additional parameters like temperature, max_tokens
    """
    spec = explain(goal)
    params = params or {}
    
    # Generate prompt based on style
    if style == "schema_json":
        body = make_schema_json(spec)
        is_dual = False
    elif style == "few_shot":
        body = make_few_shot(spec)
        is_dual = False
    elif style == "planner_executor":
        dual_prompts = make_planner_executor(spec)
        body = dual_prompts  # This is a dict with planner_prompt and executor_prompt
        is_dual = True
    elif style == "rubric_scored":
        body = make_rubric_scored(spec)
        is_dual = False
    else:  # directive (default)
        body = make_directive(spec)
        is_dual = False
    
    result = {
        "style": style,
        "is_dual_prompt": is_dual,
        "notes": [f"Generated {style} style prompt"]
    }
    
    # Handle dual-prompt case (planner-executor)
    if is_dual:
        result["planner_prompt"] = body["planner_prompt"]
        result["executor_prompt"] = body["executor_prompt"]
        result["language_variants"] = {
            "planner": code_wrappers(body["planner_prompt"], model, params),
            "executor": code_wrappers(body["executor_prompt"], model, params)
        }
        # For compatibility with existing schema, also set prompt_body to planner
        result["prompt_body"] = body["planner_prompt"]
    else:
        result["prompt_body"] = body
        result["language_variants"] = code_wrappers(body, model, params)
    
    return result
