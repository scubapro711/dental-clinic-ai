#!/usr/bin/env python3
"""
Comprehensive LangSmith Trace Analysis for DentaFlow Agent System

This script performs deep analysis of LangSmith traces to identify:
1. Error patterns across all agents
2. Performance metrics and bottlenecks
3. Tool usage patterns
4. Success/failure rates
5. Agent routing effectiveness
"""

import os
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from typing import Dict, List, Any
import json

# Check if langsmith is available
try:
    from langsmith import Client
    LANGSMITH_AVAILABLE = True
except ImportError:
    LANGSMITH_AVAILABLE = False
    print("⚠️  LangSmith not available. Install with: pip install langsmith")

def analyze_traces(hours_back: int = 24):
    """Analyze LangSmith traces from the last N hours."""
    
    if not LANGSMITH_AVAILABLE:
        print("Cannot proceed without LangSmith client.")
        return
    
    # Initialize LangSmith client
    client = Client()
    
    # Calculate time range
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=hours_back)
    
    print("=" * 80)
    print(f"COMPREHENSIVE LANGSMITH TRACE ANALYSIS")
    print("=" * 80)
    print(f"Time Range: {start_time.strftime('%Y-%m-%d %H:%M')} to {end_time.strftime('%Y-%m-%d %H:%M')}")
    print(f"Duration: {hours_back} hours")
    print("=" * 80)
    print()
    
    # Fetch runs from LangSmith
    try:
        # Get project name from environment or use default
        project_name = os.getenv('LANGSMITH_PROJECT', 'dentaflow-agent-eval')
        print(f"🔍 Fetching runs from project: {project_name}")
        print()
        
        # Get all runs in the time range
        runs = list(client.list_runs(
            project_name=project_name,
            start_time=start_time,
            end_time=end_time,
            is_root=True  # Only get root runs (top-level agent invocations)
        ))
        
        print(f"📊 Total Runs Found: {len(runs)}")
        print()
        
        if not runs:
            print("No runs found in the specified time range.")
            return
        
        # Initialize counters
        error_count = 0
        success_count = 0
        agent_counts = Counter()
        tool_counts = Counter()
        error_types = Counter()
        error_messages = []
        
        # Analyze each run
        for run in runs:
            # Count by status
            if run.error:
                error_count += 1
                error_types[type(run.error).__name__] += 1
                error_messages.append({
                    'run_id': str(run.id),
                    'error': str(run.error),
                    'name': run.name
                })
            else:
                success_count += 1
            
            # Count by agent/tool name
            agent_counts[run.name] += 1
            
            # Get child runs (tool calls)
            child_runs = list(client.list_runs(
                trace_id=run.trace_id,
                is_root=False
            ))
            
            for child in child_runs:
                if 'tool' in child.name.lower() or 'function' in child.name.lower():
                    tool_counts[child.name] += 1
        
        # Print summary
        print("=" * 80)
        print("SUMMARY STATISTICS")
        print("=" * 80)
        print(f"✅ Successful Runs: {success_count} ({success_count/len(runs)*100:.1f}%)")
        print(f"❌ Failed Runs: {error_count} ({error_count/len(runs)*100:.1f}%)")
        print()
        
        # Agent usage
        print("=" * 80)
        print("AGENT USAGE BREAKDOWN")
        print("=" * 80)
        for agent, count in agent_counts.most_common():
            percentage = count / len(runs) * 100
            print(f"  {agent}: {count} runs ({percentage:.1f}%)")
        print()
        
        # Tool usage
        if tool_counts:
            print("=" * 80)
            print("TOOL USAGE BREAKDOWN")
            print("=" * 80)
            for tool, count in tool_counts.most_common(20):
                print(f"  {tool}: {count} calls")
            print()
        
        # Error analysis
        if error_count > 0:
            print("=" * 80)
            print("ERROR ANALYSIS")
            print("=" * 80)
            print(f"Total Errors: {error_count}")
            print()
            print("Error Types:")
            for error_type, count in error_types.most_common():
                print(f"  {error_type}: {count} occurrences")
            print()
            
            print("Recent Error Messages (Last 10):")
            for i, error_info in enumerate(error_messages[-10:], 1):
                print(f"\n  {i}. Run: {error_info['name']}")
                print(f"     ID: {error_info['run_id']}")
                print(f"     Error: {error_info['error'][:200]}...")
        
        # Save detailed results to file
        results = {
            'analysis_time': datetime.now().isoformat(),
            'time_range': {
                'start': start_time.isoformat(),
                'end': end_time.isoformat(),
                'hours': hours_back
            },
            'summary': {
                'total_runs': len(runs),
                'successful_runs': success_count,
                'failed_runs': error_count,
                'success_rate': success_count / len(runs) if runs else 0
            },
            'agent_usage': dict(agent_counts),
            'tool_usage': dict(tool_counts),
            'error_types': dict(error_types),
            'errors': error_messages
        }
        
        output_file = '/home/ubuntu/langsmith_analysis_results.json'
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print()
        print("=" * 80)
        print(f"✅ Detailed results saved to: {output_file}")
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Analyze last 24 hours
    analyze_traces(hours_back=24)
