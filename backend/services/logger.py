"""
Telemetry and run logging service.
Centralized logging that can later hook into Langfuse, Posthog, or other observability tools.
"""

import logging
import json
from datetime import datetime
from typing import Optional, Dict, Any
from functools import wraps
from sqlalchemy.orm import Session
from models import Run, PromptVersion

logger = logging.getLogger(__name__)

def track_event(event_name: str):
    """
    Decorator for tracking events (future-proof for analytics integration)
    
    Usage:
        @track_event("generate_call")
        def generate(...):
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger.info(f"[EVENT] {event_name} triggered")
            result = func(*args, **kwargs)
            logger.info(f"[EVENT] {event_name} completed")
            return result
        return wrapper
    return decorator


def record_run(
    db: Session,
    prompt_version_id: int,
    style: str,
    model: str,
    params: Dict[str, Any],
    started_at: datetime,
    finished_at: Optional[datetime] = None,
    output: Optional[str] = None,
    tokens_in: int = 0,
    tokens_out: int = 0,
    cost: float = 0.0,
    source: str = "web"
) -> int:
    """
    Record a prompt generation run to the database.
    
    Args:
        db: Database session
        prompt_version_id: ID of the prompt version used
        style: Prompt style (directive, schema_json, etc.)
        model: LLM model name
        params: Model parameters (temperature, max_tokens, etc.)
        started_at: When the run started
        finished_at: When the run finished
        output: Generated output (optional)
        tokens_in: Input token count
        tokens_out: Output token count
        cost: Estimated cost in USD
        source: Source of the run (web, api, cli, notebook)
    
    Returns:
        run_id: ID of the created run record
    """
    try:
        # Calculate latency
        if finished_at:
            latency_ms = int((finished_at - started_at).total_seconds() * 1000)
        else:
            latency_ms = 0
        
        # Create run record
        run = Run(
            prompt_version_id=prompt_version_id,
            style=style,
            model=model,
            params_json=json.dumps(params),
            source=source,
            started_at=started_at,
            finished_at=finished_at or datetime.utcnow(),
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            cost=cost,
            latency_ms=latency_ms
        )
        
        db.add(run)
        db.commit()
        db.refresh(run)
        
        logger.info(f"[TELEMETRY] Recorded run {run.id}: style={style}, latency={latency_ms}ms")
        return run.id
        
    except Exception as e:
        logger.error(f"[TELEMETRY] Failed to record run: {e}")
        db.rollback()
        # Don't crash the app if telemetry fails
        return -1


def get_or_create_scratchpad_version(db: Session, style: str, model: str) -> int:
    """
    Get or create a scratchpad version for ad-hoc runs.
    This ensures all runs have a version, even in sandbox mode.
    
    Args:
        db: Database session
        style: Prompt style
        model: Model name
    
    Returns:
        version_id: ID of the scratchpad version
    """
    try:
        # Look for existing scratchpad version with this style
        version = db.query(PromptVersion).filter(
            PromptVersion.version_label == f"scratchpad-{style}",
            PromptVersion.prompt_id == None
        ).first()
        
        if not version:
            # Create new scratchpad version
            version = PromptVersion(
                prompt_id=None,
                version_label=f"scratchpad-{style}",
                model=model,
                params_json="{}",
                changelog="Auto-created scratchpad version"
            )
            db.add(version)
            db.commit()
            db.refresh(version)
            logger.info(f"[TELEMETRY] Created scratchpad version {version.id} for style={style}")
        
        return version.id
        
    except Exception as e:
        logger.error(f"[TELEMETRY] Failed to create scratchpad version: {e}")
        db.rollback()
        # Return a sentinel value if creation fails
        return 1  # Assume version 1 exists as fallback


def get_run_stats(db: Session, limit: int = 100) -> Dict[str, Any]:
    """
    Get aggregate run statistics for health/metrics reporting.
    
    Args:
        db: Database session
        limit: How many recent runs to analyze
    
    Returns:
        stats: Dictionary with aggregate metrics
    """
    try:
        from sqlalchemy import func
        
        # Get aggregate stats
        result = db.query(
            func.count(Run.id).label('total_runs'),
            func.avg(Run.latency_ms).label('avg_latency'),
            func.sum(Run.tokens_in).label('total_tokens_in'),
            func.sum(Run.tokens_out).label('total_tokens_out'),
            func.sum(Run.cost).label('total_cost')
        ).first()
        
        total_runs = result.total_runs or 0
        avg_latency = result.avg_latency or 0
        total_cost = result.total_cost or 0
        
        # Calculate success rate (runs that completed)
        completed_runs = db.query(func.count(Run.id)).filter(
            Run.finished_at.isnot(None)
        ).scalar()
        
        success_rate = completed_runs / total_runs if total_runs > 0 else 0
        
        return {
            "total_runs": int(total_runs),
            "avg_latency_ms": int(avg_latency),
            "total_cost": float(total_cost),
            "success_rate": round(success_rate, 3)
        }
        
    except Exception as e:
        logger.error(f"[TELEMETRY] Failed to get run stats: {e}")
        return {
            "total_runs": 0,
            "avg_latency_ms": 0,
            "total_cost": 0.0,
            "success_rate": 0.0
        }

