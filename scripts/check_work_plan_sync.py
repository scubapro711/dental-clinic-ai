#!/usr/bin/env python3
"""
Work Plan Sync Checker
Validates that current work plan matches actual codebase
"""

import os
import re
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent

def extract_agents_from_work_plan():
    """Extract agent list from latest work plan"""
    work_plans = sorted(REPO_ROOT.glob("WORK_PLAN_V*.md"), reverse=True)
    if not work_plans:
        print("⚠️  No work plan found")
        return set()
    
    latest = work_plans[0]
    print(f"📋 Reading: {latest.name}")
    
    with open(latest, encoding='utf-8') as f:
        content = f.read()
    
    # Extract agent names from work plan
    agents = set()
    
    # Look for specific agent sections
    # Pattern: ### AgentName Agent or ## AgentName Agent
    # Pattern: **AgentName** (AI Receptionist)
    # Pattern: | AgentName | ... |
    patterns = [
        r'###?\s+([A-Z][a-z]+)\s+Agent',  # ### Alex Agent
        r'\*\*([A-Z][a-z]+)\*\*\s+\([^)]*Agent[^)]*\)',  # **Alex** (AI Receptionist)
        r'^\|\s+([A-Z][a-z]+)\s+\|.*Agent',  # | Alex | ... Agent ... |
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, content, re.MULTILINE | re.IGNORECASE)
        agents.update(matches)
    
    # Also look for agent file references
    # Pattern: backend/app/agents/alex.py
    file_pattern = r'backend/app/agents/([a-z_]+)\.py'
    file_matches = re.findall(file_pattern, content)
    for match in file_matches:
        if match not in ['__init__', 'agent_graph', 'agent_graph_v2', 'state', 
                         'graph_state', 'orchestrator', 'error_handler']:
            agents.add(match.capitalize())
    
    # Filter out common false positives
    false_positives = {'The', 'This', 'All', 'Each', 'Any', 'For', 'With', 
                       'Agent', 'Backend', 'Frontend', 'Status', 'Alerts',
                       'Preview', 'Standard', 'Glacier', 'Onboarding', 'Recruitment'}
    agents = agents - false_positives
    
    return agents

def extract_agents_from_code():
    """Extract agent files from backend/app/agents/"""
    agents_dir = REPO_ROOT / "backend" / "app" / "agents"
    if not agents_dir.exists():
        print("⚠️  Agents directory not found")
        return set()
    
    agents = set()
    excluded = ["__init__", "agent_graph", "agent_graph_v2", "graph_state", 
                "state", "tools", "orchestrator", "error_handler"]
    
    for file in agents_dir.glob("*.py"):
        if file.stem not in excluded:
            # Capitalize first letter (alex.py → Alex)
            agent_name = file.stem.capitalize()
            agents.add(agent_name)
    
    return agents

def main():
    print("🔍 Work Plan Sync Check")
    print("=" * 60)
    print()
    
    planned_agents = extract_agents_from_work_plan()
    actual_agents = extract_agents_from_code()
    
    print(f"\n📋 Planned Agents ({len(planned_agents)}):")
    if planned_agents:
        for agent in sorted(planned_agents):
            print(f"   - {agent}")
    else:
        print("   (none found)")
    
    print(f"\n💻 Actual Agents in Code ({len(actual_agents)}):")
    if actual_agents:
        for agent in sorted(actual_agents):
            print(f"   - {agent}")
    else:
        print("   (none found)")
    
    # Gap analysis
    missing = planned_agents - actual_agents
    extra = actual_agents - planned_agents
    
    if missing:
        print(f"\n❌ Missing Agents ({len(missing)}):")
        print("   These agents are planned but not built:")
        for agent in sorted(missing):
            print(f"   - {agent}")
    
    if extra:
        print(f"\n⚠️  Extra Agents ({len(extra)}):")
        print("   These agents are built but not in plan:")
        for agent in sorted(extra):
            print(f"   - {agent}")
    
    if not missing and not extra:
        print("\n✅ Work plan and code are in sync!")
        print("   All planned agents are built.")
        print("   No extra agents found.")
        return 0
    else:
        print("\n🚨 Work plan and code are OUT OF SYNC!")
        print("\n📝 Action required:")
        if missing:
            print("   1. Build missing agents, OR")
            print("   2. Remove them from work plan, OR")
            print("   3. Create ADR explaining why they're deferred")
        if extra:
            print("   1. Add extra agents to work plan, OR")
            print("   2. Remove them from code, OR")
            print("   3. Create ADR explaining the change")
        return 1

if __name__ == "__main__":
    exit(main())
