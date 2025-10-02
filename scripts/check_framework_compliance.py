#!/usr/bin/env python3
"""
Framework Compliance Checker
Validates that the project follows the Improved Holistic Framework V2.0
"""

import os
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent

def check_file_exists(path, description):
    """Check if a file exists"""
    full_path = REPO_ROOT / path
    exists = full_path.exists()
    status = "✅" if exists else "❌"
    print(f"  {status} {description}")
    return exists

def check_directory_exists(path, description):
    """Check if a directory exists and has files"""
    full_path = REPO_ROOT / path
    exists = full_path.exists() and full_path.is_dir()
    if exists:
        file_count = len(list(full_path.glob("*")))
        print(f"  ✅ {description} ({file_count} files)")
    else:
        print(f"  ❌ {description}")
    return exists

def check_git_hooks():
    """Check if git hooks are installed"""
    hooks_dir = REPO_ROOT / ".git" / "hooks"
    pre_commit = hooks_dir / "pre-commit"
    commit_msg = hooks_dir / "commit-msg"
    
    pre_commit_ok = pre_commit.exists() and pre_commit.stat().st_size > 100
    commit_msg_ok = commit_msg.exists() and commit_msg.stat().st_size > 100
    
    if pre_commit_ok and commit_msg_ok:
        print("  ✅ Git hooks installed (pre-commit, commit-msg)")
        return True
    else:
        print("  ❌ Git hooks not installed")
        if not pre_commit_ok:
            print("     Missing: .git/hooks/pre-commit")
        if not commit_msg_ok:
            print("     Missing: .git/hooks/commit-msg")
        return False

def main():
    print("🔍 Framework Compliance Check")
    print("=" * 60)
    print()
    
    total_checks = 0
    passed_checks = 0
    
    # Section 1: ADR System
    print("📋 1. ADR System (Architecture Decision Records)")
    total_checks += 4
    passed_checks += check_directory_exists("docs/adr", "ADR directory")
    passed_checks += check_file_exists("docs/adr/TEMPLATE.md", "ADR template")
    passed_checks += check_file_exists("docs/adr/README.md", "ADR README")
    
    # Count ADRs
    adr_dir = REPO_ROOT / "docs" / "adr"
    if adr_dir.exists():
        adrs = list(adr_dir.glob("ADR-*.md"))
        if len(adrs) >= 1:
            print(f"  ✅ At least 1 ADR created ({len(adrs)} found)")
            passed_checks += 1
        else:
            print("  ❌ No ADRs created yet")
    else:
        print("  ❌ No ADRs created yet")
    
    print()
    
    # Section 2: Git Workflow
    print("🔧 2. Git Workflow & Validation")
    total_checks += 3
    passed_checks += check_git_hooks()
    passed_checks += check_file_exists("scripts/hooks/pre-commit", "Pre-commit hook script")
    passed_checks += check_file_exists("scripts/hooks/commit-msg", "Commit-msg hook script")
    print()
    
    # Section 3: Feature Tracking
    print("📊 3. Feature Tracking & Inventory")
    total_checks += 3
    passed_checks += check_file_exists("FEATURE_INVENTORY.md", "Feature inventory")
    passed_checks += check_file_exists("scripts/check_work_plan_sync.py", "Work plan sync checker")
    passed_checks += check_file_exists(".github/PULL_REQUEST_TEMPLATE.md", "PR template")
    print()
    
    # Section 4: Work Plans
    print("📝 4. Work Plans & Documentation")
    total_checks += 2
    
    # Find latest work plan
    work_plans = list(REPO_ROOT.glob("WORK_PLAN_V*.md"))
    if work_plans:
        latest = max(work_plans, key=lambda p: p.name)
        print(f"  ✅ Work plan exists ({latest.name})")
        passed_checks += 1
    else:
        print("  ❌ No work plan found")
    
    passed_checks += check_file_exists("IMPROVED_FRAMEWORK_V2.md", "Framework document")
    print()
    
    # Section 5: Testing
    print("🧪 5. Testing Infrastructure")
    total_checks += 2
    passed_checks += check_directory_exists("backend/tests", "Test directory")
    
    # Check if tests exist
    test_dir = REPO_ROOT / "backend" / "tests"
    if test_dir.exists():
        test_files = list(test_dir.glob("test_*.py"))
        if len(test_files) >= 3:
            print(f"  ✅ Multiple test files ({len(test_files)} found)")
            passed_checks += 1
        else:
            print(f"  ⚠️  Few test files ({len(test_files)} found, recommend 3+)")
    else:
        print("  ❌ No test files found")
    
    print()
    
    # Section 6: CI/CD
    print("🚀 6. CI/CD & Automation")
    total_checks += 2
    passed_checks += check_directory_exists(".github/workflows", "GitHub Actions")
    passed_checks += check_file_exists("docker-compose.yml", "Docker Compose")
    print()
    
    # Summary
    print("=" * 60)
    print(f"📊 Summary: {passed_checks}/{total_checks} checks passed")
    
    percentage = (passed_checks / total_checks) * 100
    print(f"🎯 Compliance: {percentage:.1f}%")
    
    if percentage >= 90:
        print("✅ Excellent! Framework is well implemented.")
        return 0
    elif percentage >= 70:
        print("⚠️  Good, but some improvements needed.")
        return 0
    elif percentage >= 50:
        print("⚠️  Fair, several items need attention.")
        return 1
    else:
        print("❌ Poor compliance, significant work needed.")
        return 1

if __name__ == "__main__":
    exit(main())
