#!/usr/bin/env python3
"""
Autonomous Coding Controller
===========================
Core autonomous loop that dispatches tasks to sub-agents.

Author: GLM-4.7
Created: 2026-02-13
Version: 3.1
"""

import json
import subprocess
import sys
import os
from datetime import datetime
from pathlib import Path
import time
import uuid

# Configuration
WORKSPACE = Path("/home/ubuntu/.openclaw/workspace")
TASK_LIST = WORKSPACE / ".task_list.json"
LOGS_DIR = WORKSPACE / "logs" / "autonomous"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Task priority weights
PRIORITY_WEIGHTS = {
    "high": 100,
    "medium": 50,
    "low": 10
}

# Quadrant weights (Eisenhower Matrix)  
QUADRANT_WEIGHTS = {
    "urgent_important": 100,
    "not_urgent_important": 75,
    "urgent_not_important": 50,
    "not_urgent_not_important": 25
}


def log(message, level="INFO"):
    """Write log message with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [{level}] {message}\n"
    print(log_entry, end="")
    
    # Write to daily log file
    log_file = LOGS_DIR / f"autonomous_{datetime.now().strftime('%Y%m%d')}.log"
    with open(log_file, "a") as f:
        f.write(log_entry)


def load_tasks():
    """Load task list from JSON file"""
    try:
        with open(TASK_LIST, "r") as f:
            data = json.load(f)
        return data.get("tasks", [])
    except Exception as e:
        log(f"Failed to load tasks: {e}", "ERROR")
        return []


def save_tasks(tasks):
    """Save task list back to JSON file"""
    try:
        with open(TASK_LIST, "r") as f:
            data = json.load(f)
        data["tasks"] = tasks
        data["last_updated"] = datetime.now().isoformat()
        
        # Update statistics
        status_counts = {"pending": 0, "in_progress": 0, "done": 0, "failed": 0}
        for task in tasks:
            status = task.get("status", "pending")
            if status in status_counts:
                status_counts[status] += 1
        
        data["statistics"] = {
            "total": len(tasks),
            **status_counts
        }
        
        with open(TASK_LIST, "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        log(f"Failed to save tasks: {e}", "ERROR")
        return False


def calculate_score(task):
    """Calculate priority score for a task"""
    priority_score = PRIORITY_WEIGHTS.get(task.get("priority", "medium"), 50)
    quadrant_score = QUADRANT_WEIGHTS.get(task.get("quadrant", "not_urgent_not_important"), 25)
    return priority_score + quadrant_score


def select_next_task(target_task_id=None):
    """
    Select the highest priority pending task.
    If target_task_id is specified, select that specific task.
    """
    tasks = load_tasks()
    pending_tasks = [t for t in tasks if t.get("status") == "pending"]
    
    if not pending_tasks:
        log("No pending tasks found", "INFO")
        return None, tasks
    
    # If a specific task is targeted, find it
    if target_task_id:
        for task in pending_tasks:
            if task.get("id") == target_task_id:
                log(f"Targeted task: {task['id']} - {task.get('title', 'Untitled')}")
                return task, tasks
        log(f"Target task {target_task_id} not found", "WARN")
        return None, tasks
    
    # Otherwise sort by score (highest first)
    pending_tasks.sort(key=calculate_score, reverse=True)
    
    selected = pending_tasks[0]
    log(f"Selected task: {selected['id']} - {selected.get('title', 'Untitled')}")
    log(f"  Priority: {selected.get('priority')}, Quadrant: {selected.get('quadrant')}")
    if selected.get('description'):
        log(f"  Description: {selected['description'][:150]}")
    
    return selected, tasks


def identify_task_type(task):
    """
    Identify the type of task based on title and description.
    Returns a string identifier.
    """
    title = task.get('title', '').lower()
    desc = task.get('description', '').lower()
    combined = f"{title} {desc}"
    
    # Moltbook/ImageHub cleanup tasks
    if any(keyword in combined for keyword in ['moltbook', 'imagehub', '重复', 'duplicate', '清理', 'cleanup']):
        return 'moltbook_cleanup'
    
    # WebDAV tasks
    if any(keyword in combined for keyword in ['webdav', '123pan', '123盘']):
        return 'webdav'
    
    # Knowledge management
    if any(keyword in combined for keyword in ['知识', 'knowledge', 'obsidian', '笔记']):
        return 'knowledge_management'
    
    # System maintenance
    if any(keyword in combined for keyword in ['监控', 'monitor', '维护', 'maintenance']):
        return 'monitoring'
    
    # Default
    return 'generic'


def execute_task_directly(task):
    """
    Execute a task directly by invoking tools and logic.
    This is the autonomous execution engine.
    """
    task_id = task.get("id", "UNKNOWN")
    task_title = task.get("title", "Untitled")
    task_desc = task.get("description", "")
    
    log(f"Executing task {task_id} directly...", "INFO")
    
    # Identify task type
    task_type = identify_task_type(task)
    log(f"Task type identified: {task_type}", "INFO")
    
    try:
        # Route to appropriate handler
        if task_type == 'moltbook_cleanup':
            return execute_moltbook_cleanup(task)
        
        elif task_type == 'webdav':
            return execute_webdav_task(task)
        
        elif task_type == 'knowledge_management':
            return execute_knowledge_task(task)
        
        elif task_type == 'monitoring':
            return execute_monitoring_task(task)
        
        else:
            return execute_generic_task(task)
            
    except Exception as e:
        log(f"Error executing task {task_id}: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return False, str(e)


def execute_moltbook_cleanup(task):
    """
    Execute the Moltbook duplicate posts cleanup task.
    """
    log("→ Moltbook/ImageHub cleanup handler", "INFO")
    
    try:
        # Check for the duplicate check script
        check_script = WORKSPACE / "check_moltbook_duplicates.py"
        detailed_script = WORKSPACE / "check_moltbook_detailed.py"
        
        # Use the detailed script if available
        script_to_run = detailed_script if detailed_script.exists() else check_script
        
        if not script_to_run.exists():
            log(f"Check script not found at {script_to_run}", "ERROR")
            return False, "Check script not found"
        
        log(f"Running check script: {script_to_run.name}", "INFO")
        
        result = subprocess.run(
            ["python3", str(script_to_run)],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        log(f"Script output:\n{result.stdout}", "INFO")
        
        if result.stderr:
            log(f"Script stderr:\n{result.stderr}", "WARN")
        
        if result.returncode == 0:
            # Analyze results
            output = result.stdout.lower()
            
            # Check for success indicators
            if "没有发现重复" in output or "no duplicate" in output or "✅" in output:
                log("✓ No issues found - task complete", "INFO")
                return True, "No duplicates detected, system healthy"
            
            # Check for actual issues (not just mentions of "duplicate")
            elif "发现重复" in output or ("duplicate" in output and "found" in output) or "error" in output.lower():
                log("⚠ Issues detected - manual review needed", "WARN")
                return False, "Issues detected requiring manual review"
            else:
                log("✓ Script completed successfully", "INFO")
                return True, "Check completed, no issues"
        else:
            log(f"Script failed with code {result.returncode}", "ERROR")
            return False, f"Script failed: {result.stderr[:200]}"
            
    except subprocess.TimeoutExpired:
        log("Script execution timed out", "ERROR")
        return False, "Script timeout"
    except Exception as e:
        log(f"Error in Moltbook cleanup: {e}", "ERROR")
        return False, str(e)


def execute_webdav_task(task):
    """Execute WebDAV related tasks"""
    log("→ WebDAV task handler", "INFO")
    
    try:
        # Check WebDAV mount status
        result = subprocess.run(
            ["mountpoint", "-q", "/home/ubuntu/123pan"],
            capture_output=True
        )
        
        if result.returncode == 0:
            log("✓ WebDAV mounted correctly", "INFO")
            
            # Test write access
            test_file = Path("/home/ubuntu/123pan/.autonomous_test")
            try:
                test_file.write_text(f"Autonomous test {datetime.now().isoformat()}")
                test_file.unlink()
                log("✓ WebDAV write access confirmed", "INFO")
                return True, "WebDAV healthy"
            except Exception as e:
                log(f"✗ WebDAV write failed: {e}", "ERROR")
                return False, f"Write access denied: {e}"
        else:
            log("✗ WebDAV not mounted", "ERROR")
            return False, "WebDAV not mounted"
            
    except Exception as e:
        log(f"Error checking WebDAV: {e}", "ERROR")
        return False, str(e)


def execute_knowledge_task(task):
    """Execute knowledge management tasks"""
    log("→ Knowledge management handler", "INFO")
    return False, "Knowledge management tasks not yet automated"


def execute_monitoring_task(task):
    """Execute monitoring tasks"""
    log("→ Monitoring handler", "INFO")
    return False, "Monitoring tasks not yet automated"


def execute_generic_task(task):
    """
    For tasks we don't have specific handlers for.
    """
    task_id = task.get("id")
    log("→ Generic task handler", "INFO")
    log("This task type requires manual implementation", "INFO")
    
    return False, "Task type not yet automated - requires manual handling"


def update_task_status(task_id, status, log_entry=None):
    """Update the status of a specific task"""
    tasks = load_tasks()
    
    updated = False
    for task in tasks:
        if task.get("id") == task_id:
            task["status"] = status
            if log_entry:
                if "logs" not in task:
                    task["logs"] = []
                task["logs"].append({
                    "timestamp": datetime.now().isoformat(),
                    "message": log_entry
                })
            updated = True
            break
    
    if updated:
        save_tasks(tasks)
        log(f"Task {task_id} status → {status}")


def run_once(target_task_id=None):
    """Run a single iteration of the autonomous loop"""
    log("=" * 60)
    log("AUTONOMOUS CONTROLLER - SINGLE RUN MODE")
    log("=" * 60)
    
    # Select next task (or specific targeted task)
    task, all_tasks = select_next_task(target_task_id)
    
    if task is None:
        log("No tasks to process.", "INFO")
        return True
    
    # Mark as in_progress
    task_id = task.get("id")
    update_task_status(task_id, "in_progress", "Task picked up by autonomous controller")
    
    # Execute the task
    success, result = execute_task_directly(task)
    
    # Update final status
    if success:
        update_task_status(task_id, "done", f"Completed: {result}")
        log(f"✓ Task {task_id} completed successfully", "INFO")
        log(f"  Result: {result[:200]}", "INFO")
    else:
        update_task_status(task_id, "pending", f"Execution failed: {result[:200]}")
        log(f"✗ Task {task_id} execution failed", "WARN")
        log(f"  Error: {result[:200]}", "WARN")
    
    return success


def main_loop(target_task_id=None, max_iterations=10):
    """Main autonomous loop - runs continuously"""
    log("=" * 60)
    log("AUTONOMOUS CONTROLLER STARTED")
    log(f"Workspace: {WORKSPACE}")
    if target_task_id:
        log(f"Targeting specific task: {target_task_id}")
    log("=" * 60)
    
    iteration_count = 0
    
    while iteration_count < max_iterations:
        try:
            iteration_count += 1
            log(f"\n[Iteration {iteration_count}/{max_iterations}]", "INFO")
            
            # If targeting a specific task, only run once
            if target_task_id:
                success = run_once(target_task_id)
                break
            
            # Select and execute next task
            task, all_tasks = select_next_task()
            
            if task is None:
                log("No pending tasks. Sleeping 30s...", "INFO")
                time.sleep(30)
                continue
            
            # Mark as in_progress
            task_id = task.get("id")
            update_task_status(task_id, "in_progress", f"Iteration {iteration_count}: Task picked up")
            
            # Execute
            success, result = execute_task_directly(task)
            
            # Update final status
            if success:
                update_task_status(task_id, "done", f"Completed in iteration {iteration_count}")
                log(f"✓ Task {task_id} completed", "INFO")
            else:
                update_task_status(task_id, "pending", f"Failed: {result[:100]}")
                log(f"✗ Task {task_id} failed, will retry", "WARN")
            
            # Brief pause between tasks
            time.sleep(5)
                
        except KeyboardInterrupt:
            log("\n⚠ Received interrupt signal. Shutting down...", "WARN")
            break
        except Exception as e:
            log(f"Error in main loop: {e}", "ERROR")
            import traceback
            traceback.print_exc()
            time.sleep(10)
    
    log("=" * 60)
    log(f"AUTONOMOUS CONTROLLER STOPPED after {iteration_count} iterations")
    log("=" * 60)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Autonomous Coding Controller")
    parser.add_argument("--once", action="store_true", help="Run single iteration")
    parser.add_argument("--task", type=str, help="Target specific task ID")
    parser.add_argument("--max-iterations", type=int, default=10, help="Max iterations (default: 10)")
    
    args = parser.parse_args()
    
    if args.once:
        exit(0 if run_once(args.task) else 1)
    else:
        main_loop(args.task, args.max_iterations)
