"""
CRUD operations for job queue in Supabase
Handles background processing job management
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

# Initialize Supabase client
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)


def create_job(
    job_type: str,
    video_id: Optional[str] = None,
    payload: Optional[Dict[str, Any]] = None,
    priority: int = 0
) -> Optional[Dict[str, Any]]:
    """
    Create a new background job
    
    Args:
        job_type: Type of job (subtitle_extraction, chunk_processing, ai_enrichment)
        video_id: Optional YouTube video ID
        payload: Optional JSON payload
        priority: Priority (higher = more urgent)
        
    Returns:
        Created job record or None on error
    """
    try:
        job_data = {
            'job_type': job_type,
            'video_id': video_id,
            'payload': payload or {},
            'priority': priority,
            'status': 'pending'
        }
        
        print(f"[DB->] INSERT job_queue (type={job_type}, video={video_id})")
        response = supabase.table("job_queue").insert(job_data).execute()
        
        if response.data and len(response.data) > 0:
            print(f"[DB<-] Created job: {job_type} (ID: {response.data[0]['id']})")
            return response.data[0]
        else:
            print(f"[DB!!] Failed to create job: {job_type}")
            return None
            
    except Exception as e:
        print(f"[DB!!] {str(e)}")
        return None


def get_next_job() -> Optional[Dict[str, Any]]:
    """
    Get next pending job by priority
    
    Returns:
        Job record or None if no pending jobs
    """
    try:
        print(f"[DB->] SELECT job_queue WHERE status=pending (limit=1, priority DESC)")
        response = supabase.table("job_queue").select(
            "*"
        ).eq("status", "pending").order(
            "priority", desc=True
        ).order("created_at").limit(1).execute()
        
        if response.data and len(response.data) > 0:
            print(f"[DB<-] Found pending job: {response.data[0]['job_type']}")
            return response.data[0]
        else:
            print(f"[DB<-] No pending jobs")
            return None
            
    except Exception as e:
        print(f"[DB!!] {str(e)}")
        return None


def update_job_status(
    job_id: int,
    status: str,
    error_message: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Update job status
    
    Args:
        job_id: Job ID
        status: New status (pending, processing, completed, failed)
        error_message: Optional error message
        
    Returns:
        Updated job record or None on error
    """
    try:
        update_data = {'status': status}
        
        if status == 'processing':
            update_data['started_at'] = datetime.utcnow().isoformat()
        elif status in ['completed', 'failed']:
            update_data['completed_at'] = datetime.utcnow().isoformat()
        
        if error_message:
            update_data['error_message'] = error_message
        
        print(f"[DB->] UPDATE job_queue (id={job_id}, status={status})")
        response = supabase.table("job_queue").update(
            update_data
        ).eq("id", job_id).execute()
        
        if response.data and len(response.data) > 0:
            print(f"[DB<-] Updated job {job_id} status to: {status}")
            return response.data[0]
        else:
            print(f"[DB!!] Failed to update job {job_id}")
            return None
            
    except Exception as e:
        print(f"[DB!!] {str(e)}")
        return None


def increment_job_attempts(job_id: int) -> Optional[Dict[str, Any]]:
    """
    Increment job attempt count
    
    Args:
        job_id: Job ID
        
    Returns:
        Updated job record or None on error
    """
    try:
        # Get current attempts
        print(f"[DB->] SELECT job_queue WHERE id={job_id}")
        response = supabase.table("job_queue").select(
            "attempts, max_attempts"
        ).eq("id", job_id).execute()
        
        if not response.data or len(response.data) == 0:
            print(f"[DB<-] Job not found: {job_id}")
            return None
        
        current_attempts = response.data[0].get('attempts', 0)
        max_attempts = response.data[0].get('max_attempts', 3)
        new_attempts = current_attempts + 1
        
        # Update attempts
        update_data = {'attempts': new_attempts}
        
        # If max attempts reached, mark as failed
        if new_attempts >= max_attempts:
            update_data['status'] = 'failed'
            update_data['error_message'] = f'Max attempts ({max_attempts}) reached'
            update_data['completed_at'] = datetime.utcnow().isoformat()
        
        print(f"[DB->] UPDATE job_queue (id={job_id}, attempts={new_attempts})")
        response = supabase.table("job_queue").update(
            update_data
        ).eq("id", job_id).execute()
        
        if response.data and len(response.data) > 0:
            print(f"[DB<-] Incremented job attempts to {new_attempts}")
            return response.data[0]
        else:
            print(f"[DB!!] Failed to increment attempts")
            return None
            
    except Exception as e:
        print(f"[DB!!] {str(e)}")
        return None


def get_jobs_by_video(video_id: str) -> List[Dict[str, Any]]:
    """
    Get all jobs for a video
    
    Args:
        video_id: YouTube video ID
        
    Returns:
        List of job records
    """
    try:
        print(f"[DB->] SELECT job_queue WHERE video_id={video_id}")
        response = supabase.table("job_queue").select(
            "*"
        ).eq("video_id", video_id).order("created_at", desc=True).execute()
        
        print(f"[DB<-] Found {len(response.data) if response.data else 0} jobs")
        return response.data if response.data else []
        
    except Exception as e:
        print(f"[DB!!] {str(e)}")
        return []


def get_job_stats() -> Dict[str, int]:
    """
    Get job statistics
    
    Returns:
        Dictionary with counts by status
    """
    try:
        stats = {
            'pending': 0,
            'processing': 0,
            'completed': 0,
            'failed': 0,
            'total': 0
        }
        
        print(f"[DB->] SELECT job_queue stats (count by status)")
        for status in ['pending', 'processing', 'completed', 'failed']:
            response = supabase.table("job_queue").select(
                "id", count="exact"
            ).eq("status", status).execute()
            
            stats[status] = response.count if response.count else 0
        
        stats['total'] = sum([stats[s] for s in ['pending', 'processing', 'completed', 'failed']])
        
        print(f"[DB<-] Stats: {stats['total']} total jobs")
        return stats
        
    except Exception as e:
        print(f"[DB!!] {str(e)}")
        return {'pending': 0, 'processing': 0, 'completed': 0, 'failed': 0, 'total': 0}


def cleanup_old_jobs(days: int = 7) -> int:
    """
    Clean up completed/failed jobs older than specified days
    
    Args:
        days: Number of days to keep
        
    Returns:
        Number of deleted jobs
    """
    try:
        cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
        
        print(f"[DB->] DELETE job_queue WHERE status IN (completed,failed) AND completed_at < {cutoff_date}")
        response = supabase.table("job_queue").delete().in_(
            "status", ["completed", "failed"]
        ).lt("completed_at", cutoff_date).execute()
        
        deleted_count = len(response.data) if response.data else 0
        print(f"[DB<-] Cleaned up {deleted_count} old jobs")
        return deleted_count
        
    except Exception as e:
        print(f"[DB!!] {str(e)}")
        return 0
