#!/usr/bin/env python3
# Comprehensive Testing Runner for Dental Clinic AI System
# Version: 1.0.0
# Date: 2025-12-29

import subprocess
import sys
import time
import json
import os
from datetime import datetime
from pathlib import Path

class TestRunner:
    """Comprehensive test runner for the dental clinic AI system."""
    
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "test_suites": {},
            "summary": {
                "total_tests": 0,
                "passed": 0,
                "failed": 0,
                "errors": 0,
                "skipped": 0
            }
        }
        
    def run_command(self, command, description):
        """Run a command and capture output."""
        print(f"\n{'='*60}")
        print(f"Running: {description}")
        print(f"Command: {command}")
        print(f"{'='*60}")
        
        start_time = time.time()
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            print(f"Exit code: {result.returncode}")
            print(f"Duration: {duration:.2f} seconds")
            
            if result.stdout:
                print(f"\nSTDOUT:\n{result.stdout}")
            
            if result.stderr:
                print(f"\nSTDERR:\n{result.stderr}")
            
            return {
                "success": result.returncode == 0,
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "duration": duration
            }
            
        except subprocess.TimeoutExpired:
            print("Command timed out!")
            return {
                "success": False,
                "exit_code": -1,
                "stdout": "",
                "stderr": "Command timed out",
                "duration": 300
            }
        except Exception as e:
            print(f"Error running command: {e}")
            return {
                "success": False,
                "exit_code": -1,
                "stdout": "",
                "stderr": str(e),
                "duration": 0
            }
    
    def parse_pytest_output(self, output):
        """Parse pytest output to extract test statistics."""
        stats = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "errors": 0,
            "skipped": 0
        }
        
        # Look for the summary line
        lines = output.split('\n')
        for line in lines:
            if 'failed' in line and 'passed' in line:
                # Parse line like "1 failed, 96 passed, 4 warnings in 73.62s"
                parts = line.split(',')
                for part in parts:
                    part = part.strip()
                    if 'failed' in part:
                        stats['failed'] = int(part.split()[0])
                    elif 'passed' in part:
                        stats['passed'] = int(part.split()[0])
                    elif 'error' in part:
                        stats['errors'] = int(part.split()[0])
                    elif 'skipped' in part:
                        stats['skipped'] = int(part.split()[0])
                
                stats['total'] = stats['passed'] + stats['failed'] + stats['errors'] + stats['skipped']
                break
        
        return stats
    
    def run_basic_tests(self):
        """Run basic test suite."""
        print("\n🧪 Running Basic Test Suite...")
        
        result = self.run_command(
            "python -m pytest tests/simple_test.py tests/test_enhanced_mock_tool.py -v --tb=short",
            "Basic functionality tests"
        )
        
        stats = self.parse_pytest_output(result['stdout'])
        self.results['test_suites']['basic'] = {
            "result": result,
            "stats": stats
        }
        
        return result['success']
    
    def run_integration_tests(self):
        """Run integration test suite."""
        print("\n🔗 Running Integration Test Suite...")
        
        result = self.run_command(
            "python -m pytest tests/test_openmanus_integration.py tests/test_synthesizer_openmanus_integration.py -v --tb=short",
            "AI agent integration tests"
        )
        
        stats = self.parse_pytest_output(result['stdout'])
        self.results['test_suites']['integration'] = {
            "result": result,
            "stats": stats
        }
        
        return result['success']
    
    def run_dashboard_tests(self):
        """Run dashboard integration tests."""
        print("\n📊 Running Dashboard Integration Tests...")
        
        result = self.run_command(
            "python -m pytest tests/test_dashboard_integration.py -v --tb=short",
            "Dashboard-database integration tests"
        )
        
        stats = self.parse_pytest_output(result['stdout'])
        self.results['test_suites']['dashboard'] = {
            "result": result,
            "stats": stats
        }
        
        return result['success']
    
    def run_aggressive_tests(self):
        """Run aggressive test suite."""
        print("\n⚡ Running Aggressive Test Suite...")
        
        result = self.run_command(
            "python -m pytest tests/test_aggressive_suite.py -v --tb=short",
            "Aggressive stress and performance tests"
        )
        
        stats = self.parse_pytest_output(result['stdout'])
        self.results['test_suites']['aggressive'] = {
            "result": result,
            "stats": stats
        }
        
        return result['success']
    
    def run_security_tests(self):
        """Run security test suite."""
        print("\n🔒 Running Security Test Suite...")
        
        result = self.run_command(
            "python -m pytest tests/test_security_enhancements.py tests/test_security_improvements.py -v --tb=short",
            "Security and validation tests"
        )
        
        stats = self.parse_pytest_output(result['stdout'])
        self.results['test_suites']['security'] = {
            "result": result,
            "stats": stats
        }
        
        return result['success']
    
    def run_load_tests(self):
        """Run load tests with locust."""
        print("\n🚀 Running Load Tests...")
        
        # Start the server in background for load testing
        print("Starting server for load testing...")
        server_process = subprocess.Popen(
            ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8001"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for server to start
        time.sleep(5)
        
        try:
            # Run locust headless for 30 seconds
            result = self.run_command(
                "locust -f tests/load_test_locust.py --host=http://localhost:8001 --users 10 --spawn-rate 2 --run-time 30s --headless",
                "Load testing with Locust"
            )
            
            self.results['test_suites']['load'] = {
                "result": result,
                "stats": {"note": "Load test completed - check output for metrics"}
            }
            
            return result['success']
            
        finally:
            # Stop the server
            server_process.terminate()
            server_process.wait()
    
    def run_all_tests(self):
        """Run all test suites."""
        print("🎯 Starting Comprehensive Test Suite for Dental Clinic AI System")
        print(f"Timestamp: {self.results['timestamp']}")
        
        test_suites = [
            ("Basic Tests", self.run_basic_tests),
            ("Integration Tests", self.run_integration_tests),
            ("Dashboard Tests", self.run_dashboard_tests),
            ("Aggressive Tests", self.run_aggressive_tests),
            ("Security Tests", self.run_security_tests),
            ("Load Tests", self.run_load_tests),
        ]
        
        overall_success = True
        
        for suite_name, test_function in test_suites:
            try:
                success = test_function()
                if not success:
                    overall_success = False
                    print(f"❌ {suite_name} FAILED")
                else:
                    print(f"✅ {suite_name} PASSED")
            except Exception as e:
                print(f"💥 {suite_name} ERROR: {e}")
                overall_success = False
        
        # Calculate summary statistics
        for suite_data in self.results['test_suites'].values():
            if 'stats' in suite_data:
                stats = suite_data['stats']
                self.results['summary']['total_tests'] += stats.get('total', 0)
                self.results['summary']['passed'] += stats.get('passed', 0)
                self.results['summary']['failed'] += stats.get('failed', 0)
                self.results['summary']['errors'] += stats.get('errors', 0)
                self.results['summary']['skipped'] += stats.get('skipped', 0)
        
        return overall_success
    
    def generate_report(self):
        """Generate comprehensive test report."""
        print("\n" + "="*80)
        print("📋 COMPREHENSIVE TEST REPORT")
        print("="*80)
        
        print(f"Timestamp: {self.results['timestamp']}")
        print(f"Total Tests: {self.results['summary']['total_tests']}")
        print(f"Passed: {self.results['summary']['passed']}")
        print(f"Failed: {self.results['summary']['failed']}")
        print(f"Errors: {self.results['summary']['errors']}")
        print(f"Skipped: {self.results['summary']['skipped']}")
        
        if self.results['summary']['total_tests'] > 0:
            success_rate = (self.results['summary']['passed'] / self.results['summary']['total_tests']) * 100
            print(f"Success Rate: {success_rate:.1f}%")
        
        print("\nTest Suite Details:")
        print("-" * 40)
        
        for suite_name, suite_data in self.results['test_suites'].items():
            print(f"\n{suite_name.upper()}:")
            if 'stats' in suite_data:
                stats = suite_data['stats']
                print(f"  Total: {stats.get('total', 0)}")
                print(f"  Passed: {stats.get('passed', 0)}")
                print(f"  Failed: {stats.get('failed', 0)}")
                if stats.get('errors', 0) > 0:
                    print(f"  Errors: {stats['errors']}")
                if stats.get('skipped', 0) > 0:
                    print(f"  Skipped: {stats['skipped']}")
            
            result = suite_data['result']
            print(f"  Duration: {result['duration']:.2f}s")
            print(f"  Status: {'✅ PASSED' if result['success'] else '❌ FAILED'}")
        
        # Save detailed report to file
        report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Detailed report saved to: {report_file}")
        
        return self.results

def main():
    """Main function to run comprehensive tests."""
    if len(sys.argv) > 1:
        test_type = sys.argv[1].lower()
        
        runner = TestRunner()
        
        if test_type == "basic":
            success = runner.run_basic_tests()
        elif test_type == "integration":
            success = runner.run_integration_tests()
        elif test_type == "dashboard":
            success = runner.run_dashboard_tests()
        elif test_type == "aggressive":
            success = runner.run_aggressive_tests()
        elif test_type == "security":
            success = runner.run_security_tests()
        elif test_type == "load":
            success = runner.run_load_tests()
        elif test_type == "all":
            success = runner.run_all_tests()
        else:
            print(f"Unknown test type: {test_type}")
            print("Available types: basic, integration, dashboard, aggressive, security, load, all")
            sys.exit(1)
        
        runner.generate_report()
        sys.exit(0 if success else 1)
    
    else:
        # Run all tests by default
        runner = TestRunner()
        success = runner.run_all_tests()
        runner.generate_report()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
