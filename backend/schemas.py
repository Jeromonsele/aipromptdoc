from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from enum import Enum
from datetime import datetime

class PromptStyle(str, Enum):
    """Supported prompt generation styles"""
    directive = "directive"
    schema_json = "schema_json"
    few_shot = "few_shot"
    planner_executor = "planner_executor"
    rubric_scored = "rubric_scored"

class ExplainIn(BaseModel):
    goal: str
    constraints: Optional[str] = ""
    example_input: Optional[str] = ""
    desired_format: Optional[str] = ""

class ExplainOut(BaseModel):
    intent: str
    inputs: List[str]
    outputs: List[str]
    constraints: List[str]
    format: str
    risks: List[str]
    readiness_score: int
    missing: List[str]

class GenerateIn(BaseModel):
    goal: str
    style: str = Field(default="directive", description="directive, schema_json, few_shot, planner_executor, or rubric_scored")
    model: Optional[str] = "gpt-4o-mini"
    params: Optional[Dict[str, Any]] = {}

class GenerateOut(BaseModel):
    style: str
    is_dual_prompt: bool = False
    prompt_body: str
    planner_prompt: Optional[str] = None
    executor_prompt: Optional[str] = None
    language_variants: Union[Dict[str, str], Dict[str, Dict[str, str]]]
    notes: List[str] = []
    
    class Config:
        json_schema_extra = {
            "example": {
                "style": "directive",
                "is_dual_prompt": False,
                "prompt_body": "You are a precise assistant...",
                "language_variants": {
                    "python": "from openai import OpenAI...",
                    "javascript": "import OpenAI from 'openai'...",
                    "curl": "curl https://api.openai.com..."
                },
                "notes": ["Generated directive style prompt"]
            }
        }

class RunOut(BaseModel):
    """Output schema for run records"""
    id: int
    prompt_version_id: int
    style: str
    model: str
    source: str
    started_at: datetime
    finished_at: Optional[datetime]
    latency_ms: int
    tokens_in: int
    tokens_out: int
    cost: float
    
    class Config:
        from_attributes = True

class CompareIn(BaseModel):
    """Input for prompt comparison"""
    prompt: str
    context: Optional[str] = ""

class PromptScoreData(BaseModel):
    """Prompt score data"""
    prompt: str
    score: int
    problems: List[str]
    expected_quality_pct: int
    fixes: Optional[List[str]] = None

class CompareOut(BaseModel):
    """Output for prompt comparison"""
    before: PromptScoreData
    after: PromptScoreData
    improvement_pct: int

class StatsWeek(BaseModel):
    """Weekly stats"""
    time_saved_min: int
    cost_avoided_usd: float
    success_rate_pct: int
    prompts_created: int

class StatsAllTime(BaseModel):
    """All-time stats"""
    time_saved_hr: float
    cost_avoided_usd: float
    prompts_created: int
    in_prod: int

class StatsOut(BaseModel):
    """User stats output"""
    week: StatsWeek
    all_time: StatsAllTime
