#!/usr/bin/env python3
"""
Aggressive Testing Suite Runner
מריץ בדיקות אגרסיביות למערכת ניהול מרפאת שיניים AI

This script runs comprehensive testing including:
- Unit tests with coverage
- Integration tests
- Load testing with Locust
- Security testing
- AI model testing
- Performance benchmarking
- Bug hunting scenarios
"""

import os
import sys
import subprocess
import time
import json
import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('aggressive_testing.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AggressiveTestRunner:
    """Main test runner for aggressive testing suite"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.results = {
            "start_time": datetime.now().isoformat(),
            "test_results": {},
            "summary": {},
            "errors": []
        }
        self.project_root = Path(__file__).parent
        
    def run_command(self, command: List[str], timeout: int = 300) -> Dict[str, Any]:
        """Run a command and capture results"""
        logger.info(f"Running: {' '.join(command)}")
        
        try:
            start_time = time.time()
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=self.project_root
            )
            end_time = time.time()
            
            return {
                "command": ' '.join(command),
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "duration": end_time - start_time,
                "success": result.returncode == 0
            }
            
        except subprocess.TimeoutExpired:
            logger.error(f"Command timed out: {' '.join(command)}")
            return {
                "command": ' '.join(command),
                "returncode": -1,
                "stdout": "",
                "stderr": "Command timed out",
                "duration": timeout,
                "success": False
            }
        except Exception as e:
            logger.error(f"Command failed: {e}")
            return {
                "command": ' '.join(command),
                "returncode": -1,
                "stdout": "",
                "stderr": str(e),
                "duration": 0,
                "success": False
            }
    
    def check_system_health(self) -> bool:
        """Check if the system is running and healthy"""
        logger.info("🏥 Checking system health...")
        
        try:
            import httpx
            
            async def check_health():
                async with httpx.AsyncClient() as client:
                    try:
                        # Check Gateway
                        response = await client.get("http://localhost:8000/health", timeout=5.0)
                        gateway_healthy = response.status_code == 200
                        
                        # Check AI Agents (optional)
                        try:
                            response = await client.get("http://localhost:8001/health", timeout=5.0)
                            ai_healthy = response.status_code == 200
                        except:
                            ai_healthy = False
                            logger.warning("AI Agents service not responding (this is OK for testing)")
                        
                        return gateway_healthy
                    except Exception as e:
                        logger.error(f"Health check failed: {e}")
                        return False
            
            return asyncio.run(check_health())
            
        except ImportError:
            logger.warning("httpx not available, skipping health check")
            return True
    
    def run_unit_tests(self) -> Dict[str, Any]:
        """Run unit tests with coverage"""
        logger.info("🧪 Running unit tests with coverage...")
        
        command = [
            "python", "-m", "pytest",
            "tests/",
            "-v",
            "--cov=src",
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov",
            "--cov-report=xml:coverage.xml",
            "--cov-fail-under=70",
            "--tb=short",
            "-x"  # Stop on first failure for aggressive testing
        ]
        
        result = self.run_command(command, timeout=600)
        self.results["test_results"]["unit_tests"] = result
        
        return result
    
    def run_integration_tests(self) -> Dict[str, Any]:
        """Run integration tests"""
        logger.info("🔗 Running integration tests...")
        
        command = [
            "python", "-m", "pytest",
            "tests/test_complete_system.py",
            "-v",
            "--tb=short",
            "-m", "integration"
        ]
        
        result = self.run_command(command, timeout=300)
        self.results["test_results"]["integration_tests"] = result
        
        return result
    
    def run_security_tests(self) -> Dict[str, Any]:
        """Run security tests"""
        logger.info("🛡️ Running security tests...")
        
        # First run Bandit security scan
        bandit_result = self.run_command([
            "bandit", "-r", "src/", "-f", "json", "-o", "bandit_report.json"
        ], timeout=120)
        
        # Then run custom security tests
        security_result = self.run_command([
            "python", "-m", "pytest",
            "tests/security_testing/security_tests.py",
            "-v",
            "--tb=short",
            "-m", "security"
        ], timeout=300)
        
        # Run Safety check for dependencies
        safety_result = self.run_command([
            "safety", "check", "--json", "--output", "safety_report.json"
        ], timeout=120)
        
        combined_result = {
            "bandit": bandit_result,
            "security_tests": security_result,
            "safety": safety_result,
            "success": all([
                bandit_result["success"],
                security_result["success"],
                safety_result["success"]
            ])
        }
        
        self.results["test_results"]["security_tests"] = combined_result
        return combined_result
    
    def run_load_tests(self, users: int = 50, spawn_rate: int = 5, duration: int = 60) -> Dict[str, Any]:
        """Run load tests with Locust"""
        logger.info(f"🚀 Running load tests: {users} users, {spawn_rate} spawn rate, {duration}s duration...")
        
        # Check if system is healthy before load testing
        if not self.check_system_health():
            logger.error("System not healthy, skipping load tests")
            return {"success": False, "error": "System not healthy"}
        
        command = [
            "locust",
            "-f", "tests/load_testing/locustfile.py",
            "--host", "http://localhost:8000",
            "--users", str(users),
            "--spawn-rate", str(spawn_rate),
            "--run-time", f"{duration}s",
            "--headless",
            "--html", "load_test_report.html",
            "--csv", "load_test_results"
        ]
        
        result = self.run_command(command, timeout=duration + 60)
        self.results["test_results"]["load_tests"] = result
        
        return result
    
    def run_ai_model_tests(self) -> Dict[str, Any]:
        """Run AI model tests"""
        logger.info("🤖 Running AI model tests...")
        
        command = [
            "python", "-m", "pytest",
            "tests/ai_testing/open_source_model_tests.py",
            "-v",
            "--tb=short",
            "-m", "ai"
        ]
        
        result = self.run_command(command, timeout=300)
        self.results["test_results"]["ai_model_tests"] = result
        
        return result
    
    def run_performance_benchmarks(self) -> Dict[str, Any]:
        """Run performance benchmarks"""
        logger.info("⚡ Running performance benchmarks...")
        
        command = [
            "python", "-m", "pytest",
            "tests/",
            "--benchmark-only",
            "--benchmark-json=benchmark_results.json",
            "-v"
        ]
        
        result = self.run_command(command, timeout=300)
        self.results["test_results"]["performance_benchmarks"] = result
        
        return result
    
    def run_stress_tests(self) -> Dict[str, Any]:
        """Run stress tests to find breaking points"""
        logger.info("💥 Running stress tests...")
        
        if not self.check_system_health():
            logger.error("System not healthy, skipping stress tests")
            return {"success": False, "error": "System not healthy"}
        
        # Aggressive stress test with high load
        command = [
            "locust",
            "-f", "tests/load_testing/locustfile.py",
            "--host", "http://localhost:8000",
            "--users", "200",
            "--spawn-rate", "20",
            "--run-time", "30s",
            "--headless",
            "--html", "stress_test_report.html"
        ]
        
        result = self.run_command(command, timeout=90)
        self.results["test_results"]["stress_tests"] = result
        
        return result
    
    def run_memory_leak_tests(self) -> Dict[str, Any]:
        """Run tests to detect memory leaks"""
        logger.info("🧠 Running memory leak detection...")
        
        # This would typically use tools like valgrind or memory_profiler
        # For now, we'll run a simple memory monitoring test
        
        command = [
            "python", "-c", """
import psutil
import time
import requests
import os

process = psutil.Process(os.getpid())
initial_memory = process.memory_info().rss / 1024 / 1024

print(f"Initial memory: {initial_memory:.1f}MB")

# Simulate memory-intensive operations
for i in range(100):
    try:
        response = requests.get('http://localhost:8000/health', timeout=1)
    except:
        pass
    
    if i % 20 == 0:
        current_memory = process.memory_info().rss / 1024 / 1024
        print(f"Memory after {i} requests: {current_memory:.1f}MB")

final_memory = process.memory_info().rss / 1024 / 1024
memory_increase = final_memory - initial_memory

print(f"Final memory: {final_memory:.1f}MB")
print(f"Memory increase: {memory_increase:.1f}MB")

if memory_increase > 100:
    print("WARNING: Potential memory leak detected!")
    exit(1)
else:
    print("Memory usage within acceptable limits")
    exit(0)
"""
        ]
        
        result = self.run_command(command, timeout=120)
        self.results["test_results"]["memory_leak_tests"] = result
        
        return result
    
    def generate_report(self) -> str:
        """Generate comprehensive test report"""
        logger.info("📊 Generating test report...")
        
        self.results["end_time"] = datetime.now().isoformat()
        
        # Calculate summary statistics
        total_tests = len(self.results["test_results"])
        successful_tests = sum(1 for result in self.results["test_results"].values() 
                             if isinstance(result, dict) and result.get("success", False))
        
        self.results["summary"] = {
            "total_test_suites": total_tests,
            "successful_test_suites": successful_tests,
            "success_rate": successful_tests / total_tests if total_tests > 0 else 0,
            "total_duration": sum(
                result.get("duration", 0) for result in self.results["test_results"].values()
                if isinstance(result, dict)
            )
        }
        
        # Generate report
        report = f"""
# 🧪 Aggressive Testing Report - AI Dental Clinic System

**Generated:** {self.results["end_time"]}  
**Duration:** {self.results["summary"]["total_duration"]:.1f} seconds

## 📊 Summary

- **Total Test Suites:** {self.results["summary"]["total_test_suites"]}
- **Successful Test Suites:** {self.results["summary"]["successful_test_suites"]}
- **Success Rate:** {self.results["summary"]["success_rate"]:.1%}

## 📋 Test Results

"""
        
        for test_name, result in self.results["test_results"].items():
            if isinstance(result, dict):
                status = "✅ PASSED" if result.get("success", False) else "❌ FAILED"
                duration = result.get("duration", 0)
                
                report += f"### {test_name.replace('_', ' ').title()}\n"
                report += f"**Status:** {status}  \n"
                report += f"**Duration:** {duration:.1f}s  \n"
                
                if not result.get("success", False) and result.get("stderr"):
                    report += f"**Error:** {result['stderr'][:200]}...  \n"
                
                report += "\n"
        
        # Save report
        report_file = f"aggressive_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        # Save JSON results
        json_file = f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Report saved to: {report_file}")
        logger.info(f"JSON results saved to: {json_file}")
        
        return report_file
    
    def run_all_tests(self, include_load: bool = True, include_stress: bool = True) -> bool:
        """Run all aggressive tests"""
        logger.info("🚀 Starting Aggressive Testing Suite")
        logger.info("=" * 60)
        
        try:
            # 1. Unit Tests
            unit_result = self.run_unit_tests()
            if not unit_result["success"]:
                logger.error("Unit tests failed - stopping aggressive testing")
                return False
            
            # 2. Integration Tests
            integration_result = self.run_integration_tests()
            
            # 3. Security Tests
            security_result = self.run_security_tests()
            
            # 4. AI Model Tests
            ai_result = self.run_ai_model_tests()
            
            # 5. Performance Benchmarks
            benchmark_result = self.run_performance_benchmarks()
            
            # 6. Memory Leak Tests
            memory_result = self.run_memory_leak_tests()
            
            # 7. Load Tests (optional)
            if include_load:
                load_result = self.run_load_tests()
            
            # 8. Stress Tests (optional)
            if include_stress:
                stress_result = self.run_stress_tests()
            
            # Generate report
            report_file = self.generate_report()
            
            # Final assessment
            critical_tests = ["unit_tests", "integration_tests", "security_tests"]
            critical_passed = all(
                self.results["test_results"].get(test, {}).get("success", False)
                for test in critical_tests
            )
            
            if critical_passed:
                logger.info("🎉 All critical tests passed! System ready for AWS deployment.")
                return True
            else:
                logger.error("❌ Critical tests failed. System NOT ready for deployment.")
                return False
                
        except Exception as e:
            logger.error(f"Aggressive testing failed: {e}")
            self.results["errors"].append(str(e))
            return False

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Run aggressive testing suite")
    parser.add_argument("--no-load", action="store_true", help="Skip load testing")
    parser.add_argument("--no-stress", action="store_true", help="Skip stress testing")
    parser.add_argument("--quick", action="store_true", help="Run only critical tests")
    
    args = parser.parse_args()
    
    runner = AggressiveTestRunner()
    
    if args.quick:
        # Run only critical tests
        logger.info("Running quick test suite (critical tests only)")
        runner.run_unit_tests()
        runner.run_integration_tests()
        runner.run_security_tests()
        success = runner.generate_report()
    else:
        # Run full aggressive test suite
        success = runner.run_all_tests(
            include_load=not args.no_load,
            include_stress=not args.no_stress
        )
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
