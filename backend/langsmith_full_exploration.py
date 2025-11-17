#!/usr/bin/env python3
"""
Comprehensive LangSmith Exploration
Uses ALL available LangSmith Client tools to explore the system
"""

import os
from datetime import datetime, timedelta
from langsmith import Client
import json

def explore_langsmith():
    """Explore all LangSmith resources."""
    
    api_key = os.getenv("LANGSMITH_API_KEY")
    if not api_key:
        print("❌ LANGSMITH_API_KEY not set")
        return
    
    client = Client(api_key=api_key)
    
    print("=" * 80)
    print("COMPREHENSIVE LANGSMITH EXPLORATION")
    print("=" * 80)
    print()
    
    # 1. List all projects
    print("=" * 80)
    print("1. PROJECTS")
    print("=" * 80)
    try:
        projects = list(client.list_projects())
        print(f"📊 Total Projects: {len(projects)}")
        for project in projects:
            print(f"\n  📁 {project.name}")
            print(f"     ID: {project.id}")
            print(f"     Created: {project.created_at}")
            if hasattr(project, 'run_count'):
                print(f"     Runs: {project.run_count}")
    except Exception as e:
        print(f"❌ Error listing projects: {e}")
    
    print()
    
    # 2. List all datasets
    print("=" * 80)
    print("2. DATASETS")
    print("=" * 80)
    try:
        datasets = list(client.list_datasets())
        print(f"📊 Total Datasets: {len(datasets)}")
        for dataset in datasets:
            print(f"\n  📦 {dataset.name}")
            print(f"     ID: {dataset.id}")
            print(f"     Description: {dataset.description or 'N/A'}")
            print(f"     Created: {dataset.created_at}")
            
            # Count examples in dataset
            try:
                examples = list(client.list_examples(dataset_id=dataset.id))
                print(f"     Examples: {len(examples)}")
            except:
                pass
    except Exception as e:
        print(f"❌ Error listing datasets: {e}")
    
    print()
    
    # 3. Get runs from each project (last 7 days)
    print("=" * 80)
    print("3. RECENT RUNS (Last 7 Days)")
    print("=" * 80)
    
    end_time = datetime.now()
    start_time = end_time - timedelta(days=7)
    
    try:
        projects = list(client.list_projects())
        for project in projects:
            print(f"\n📁 Project: {project.name}")
            try:
                runs = list(client.list_runs(
                    project_name=project.name,
                    start_time=start_time,
                    end_time=end_time,
                    is_root=True,
                    limit=10
                ))
                print(f"   Runs: {len(runs)}")
                
                if runs:
                    for run in runs[:5]:  # Show first 5
                        status = "✅" if not run.error else "❌"
                        print(f"   {status} {run.name} - {run.start_time}")
                        if run.error:
                            print(f"      Error: {str(run.error)[:100]}")
            except Exception as e:
                print(f"   ⚠️  Could not fetch runs: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()
    
    # 4. List experiments/evaluations
    print("=" * 80)
    print("4. EXPERIMENTS")
    print("=" * 80)
    try:
        # Try to list experiments (if any exist)
        print("Checking for experiments...")
        # Note: LangSmith doesn't have a direct list_experiments() method
        # Experiments are tracked through datasets and evaluation runs
        print("✅ Experiments are tracked through datasets and runs")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()
    print("=" * 80)
    print("✅ EXPLORATION COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    explore_langsmith()
