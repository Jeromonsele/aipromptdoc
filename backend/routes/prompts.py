from fastapi import APIRouter, Depends, Header
from fastapi import HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
import os
import json
import logging
from .deps import get_db
from ..schemas import ExplainIn, ExplainOut, GenerateIn, GenerateOut, RunOut, CompareIn, CompareOut, StatsOut, StatsWeek, StatsAllTime
from ..services.explain import explain
from ..services.generate import generate
from ..services.scoring import compare_prompts
from ..services.logger import record_run, get_or_create_scratchpad_version, track_event, get_run_stats
from ..models import Run, PromptScore, PromptTransformation

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/explain", response_model=ExplainOut)
def explain_endpoint(
    body: ExplainIn, 
    db: Session = Depends(get_db),
    x_use_llm: Optional[str] = Header(None)
):
    """
    Explain a prompt goal with hybrid heuristic + optional LLM refinement.
    Pass 'x-use-llm: true' header to enable LLM refinement (requires OPENAI_API_KEY).
    """
    use_llm = x_use_llm is not None and x_use_llm.lower() in ["true", "1", "yes"]
    data = explain(
        body.goal, 
        body.constraints or "", 
        body.desired_format or "",
        use_llm=use_llm
    )
    return data

@router.post("/generate", response_model=GenerateOut)
@track_event("generate_call")
def generate_endpoint(body: GenerateIn, db: Session = Depends(get_db)):
    """
    Generate a prompt in the specified style.
    Supports: directive, schema_json, few_shot, planner_executor, rubric_scored
    
    Automatically logs each generation run to the database for telemetry.
    """
    started_at = datetime.utcnow()
    
    # Generate the prompt
    out = generate(
        body.goal, 
        style=body.style,
        model=body.model or "gpt-4o-mini",
        params=body.params or {}
    )
    
    finished_at = datetime.utcnow()
    
    # Get or create a scratchpad version for this run
    version_id = get_or_create_scratchpad_version(
        db, 
        style=body.style, 
        model=body.model or "gpt-4o-mini"
    )
    
    # Log the run
    record_run(
        db=db,
        prompt_version_id=version_id,
        style=body.style,
        model=body.model or "gpt-4o-mini",
        params=body.params or {},
        started_at=started_at,
        finished_at=finished_at,
        output=out.get("prompt_body", ""),
        tokens_in=0,  # Placeholder - actual token counting would require API integration
        tokens_out=0,
        cost=0.0,
        source="web"
    )
    
    return out

@router.get("/runs", response_model=List[RunOut])
def get_runs_endpoint(db: Session = Depends(get_db), limit: int = 20):
    """
    Get recent runs with basic telemetry data.
    Returns the last N runs ordered by most recent first.
    
    Args:
        limit: Maximum number of runs to return (default: 20)
    """
    runs = db.query(Run).order_by(Run.started_at.desc()).limit(limit).all()
    return runs

@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint for monitoring, CI probes, and Docker health checks.
    
    Returns:
        - status: overall health status
        - db: database connectivity status
        - openai_key: whether OpenAI API key is configured
        - metrics: aggregate run statistics
    """
    db_ok = True
    try:
        # Test database connection
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_ok = False
    
    # Get run statistics
    stats = get_run_stats(db) if db_ok else {
        "total_runs": 0,
        "avg_latency_ms": 0,
        "total_cost": 0.0,
        "success_rate": 0.0
    }
    
    return {
        "status": "ok" if db_ok else "degraded",
        "db": db_ok,
        "openai_key": bool(os.getenv("OPENAI_API_KEY")),
        "metrics": stats
    }

@router.post("/compare", response_model=CompareOut)
def compare_endpoint(body: CompareIn, db: Session = Depends(get_db)):
    """
    Compare original prompt with optimized version.
    Shows before/after scores, problems, and improvement percentage.
    
    This is the "money shot" for viral LinkedIn sharing.
    """
    # Run comparison
    result = compare_prompts(body.prompt, body.context or "")
    
    # Store in database
    try:
        # Store before score
        before_score = PromptScore(
            prompt_text=body.prompt,
            score=result["before"]["score"],
            problems_json=json.dumps(result["before"]["problems"])
        )
        db.add(before_score)
        db.commit()
        db.refresh(before_score)
        
        # Store transformation
        transformation = PromptTransformation(
            before_id=before_score.id,
            after_prompt_text=result["after"]["prompt"],
            after_score=result["after"]["score"],
            fixes_json=json.dumps(result["after"]["fixes"]),
            improvement_pct=result["improvement_pct"]
        )
        db.add(transformation)
        db.commit()
        
    except Exception as e:
        logger.warning(f"Failed to store comparison: {e}")
        # Don't fail the request if DB write fails
    
    return result

@router.get("/stats/me", response_model=StatsOut)
def get_stats_endpoint(db: Session = Depends(get_db)):
    """
    Get user's personal impact statistics.
    Shows time saved, cost avoided, and success metrics.
    """
    from sqlalchemy import func
    from datetime import timedelta
    
    # Calculate week boundary
    now = datetime.utcnow()
    week_ago = now - timedelta(days=7)
    
    # Week stats
    week_runs = db.query(func.count(Run.id)).filter(
        Run.created_at >= week_ago
    ).scalar() or 0
    
    week_transforms = db.query(func.count(PromptTransformation.id)).filter(
        PromptTransformation.created_at >= week_ago
    ).scalar() or 0
    
    # All time stats
    total_runs = db.query(func.count(Run.id)).scalar() or 0
    total_transforms = db.query(func.count(PromptTransformation.id)).scalar() or 0
    
    # Calculate derived metrics
    # Formula: 15 min saved per optimized prompt
    week_time_saved = week_transforms * 15
    all_time_saved = total_transforms * 15
    
    # Formula: $0.02 per failed attempt avoided (avg 3 retries saved)
    week_cost_avoided = week_transforms * 0.02 * 3
    all_cost_avoided = total_transforms * 0.02 * 3
    
    # Success rate (runs that completed successfully)
    total_completed = db.query(func.count(Run.id)).filter(
        Run.finished_at.isnot(None)
    ).scalar() or 0
    success_rate = int((total_completed / total_runs * 100)) if total_runs > 0 else 95
    
    return StatsOut(
        week=StatsWeek(
            time_saved_min=week_time_saved,
            cost_avoided_usd=round(week_cost_avoided, 2),
            success_rate_pct=success_rate,
            prompts_created=week_runs
        ),
        all_time=StatsAllTime(
            time_saved_hr=round(all_time_saved / 60, 1),
            cost_avoided_usd=round(all_cost_avoided, 2),
            prompts_created=total_runs,
            in_prod=total_transforms  # Simplified: transformations = prod-quality
        )
    )
