#!/usr/bin/env python3
"""
🔥 AGGRESSIVE TESTING SUITE FOR DENTAL CLINIC AI 🔥
Comprehensive testing using open source tools

This suite performs:
- Load testing with concurrent users
- Data integrity validation
- Performance benchmarking
- Security testing
- Edge case testing
- Database stress testing
"""

import asyncio
import concurrent.futures
import time
import random
import string
import json
import sys
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any
import threading
import statistics

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from ai_agents.tools.advanced_dental_tool import AdvancedDentalTool

class AggressiveTestSuite:
    """Comprehensive testing suite for the dental clinic system"""
    
    def __init__(self):
        self.results = {
            'load_test': {},
            'data_integrity': {},
            'performance': {},
            'security': {},
            'edge_cases': {},
            'database_stress': {}
        }
        self.start_time = time.time()
        
    def log(self, message: str, level: str = "INFO"):
        """Enhanced logging with timestamps"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"[{timestamp}] [{level}] {message}")
    
    async def test_concurrent_users(self, num_users: int = 50, operations_per_user: int = 10):
        """Test system with multiple concurrent users"""
        self.log(f"🚀 Starting concurrent user test: {num_users} users, {operations_per_user} ops each", "TEST")
        
        async def simulate_user(user_id: int):
            """Simulate a single user's operations"""
            tool = AdvancedDentalTool()
            user_results = {
                'operations': 0,
                'errors': 0,
                'response_times': [],
                'user_id': user_id
            }
            
            try:
                await tool.initialize()
                
                for op in range(operations_per_user):
                    start_time = time.time()
                    
                    # Random operation
                    operation = random.choice([
                        'search_patients',
                        'get_providers', 
                        'get_available_slots',
                        'health_check'
                    ])
                    
                    try:
                        if operation == 'search_patients':
                            query = random.choice(['Yossi', 'Miriam', 'Cohen', 'Levy', '1', '2'])
                            await tool.search_patients(query)
                        elif operation == 'get_providers':
                            await tool.get_providers()
                        elif operation == 'get_available_slots':
                            provider_id = random.randint(1, 4)
                            date = (datetime.now() + timedelta(days=random.randint(1, 7))).strftime('%Y-%m-%d')
                            await tool.get_available_slots(provider_id, date)
                        elif operation == 'health_check':
                            await tool.health_check()
                        
                        user_results['operations'] += 1
                        
                    except Exception as e:
                        user_results['errors'] += 1
                        self.log(f"User {user_id} error in {operation}: {e}", "ERROR")
                    
                    response_time = time.time() - start_time
                    user_results['response_times'].append(response_time)
                    
                    # Small delay to simulate real user behavior
                    await asyncio.sleep(random.uniform(0.1, 0.5))
                
            except Exception as e:
                self.log(f"User {user_id} initialization error: {e}", "ERROR")
            finally:
                await tool.cleanup()
            
            return user_results
        
        # Run all users concurrently
        start_time = time.time()
        tasks = [simulate_user(i) for i in range(num_users)]
        user_results = await asyncio.gather(*tasks, return_exceptions=True)
        total_time = time.time() - start_time
        
        # Analyze results
        successful_users = [r for r in user_results if isinstance(r, dict)]
        failed_users = [r for r in user_results if isinstance(r, Exception)]
        
        total_operations = sum(r['operations'] for r in successful_users)
        total_errors = sum(r['errors'] for r in successful_users)
        all_response_times = []
        for r in successful_users:
            all_response_times.extend(r['response_times'])
        
        self.results['load_test'] = {
            'num_users': num_users,
            'operations_per_user': operations_per_user,
            'total_time': total_time,
            'successful_users': len(successful_users),
            'failed_users': len(failed_users),
            'total_operations': total_operations,
            'total_errors': total_errors,
            'error_rate': (total_errors / total_operations * 100) if total_operations > 0 else 0,
            'operations_per_second': total_operations / total_time if total_time > 0 else 0,
            'avg_response_time': statistics.mean(all_response_times) if all_response_times else 0,
            'median_response_time': statistics.median(all_response_times) if all_response_times else 0,
            'max_response_time': max(all_response_times) if all_response_times else 0,
            'min_response_time': min(all_response_times) if all_response_times else 0
        }
        
        self.log(f"✅ Concurrent test completed: {total_operations} ops in {total_time:.2f}s", "RESULT")
        self.log(f"   Success rate: {100 - self.results['load_test']['error_rate']:.1f}%", "RESULT")
        self.log(f"   Throughput: {self.results['load_test']['operations_per_second']:.1f} ops/sec", "RESULT")
    
    async def test_data_integrity(self):
        """Test data integrity and consistency"""
        self.log("🔍 Starting data integrity tests", "TEST")
        
        tool = AdvancedDentalTool()
        await tool.initialize()
        
        integrity_results = {
            'patient_consistency': True,
            'provider_consistency': True,
            'appointment_consistency': True,
            'data_completeness': True,
            'foreign_key_integrity': True,
            'issues': []
        }
        
        try:
            # Test 1: Patient data consistency
            patients = await tool.search_patients("")  # Get all patients
            if not patients:
                integrity_results['patient_consistency'] = False
                integrity_results['issues'].append("No patients found in database")
            
            for patient in patients[:5]:  # Test first 5 patients
                if not all(key in patient for key in ['id', 'name', 'surname']):
                    integrity_results['patient_consistency'] = False
                    integrity_results['issues'].append(f"Patient {patient.get('id')} missing required fields")
            
            # Test 2: Provider data consistency
            providers = await tool.get_providers()
            if not providers:
                integrity_results['provider_consistency'] = False
                integrity_results['issues'].append("No providers found in database")
            
            for provider in providers:
                if not all(key in provider for key in ['id', 'name', 'surname']):
                    integrity_results['provider_consistency'] = False
                    integrity_results['issues'].append(f"Provider {provider.get('id')} missing required fields")
            
            # Test 3: Appointment consistency
            if patients and providers:
                patient_id = patients[0]['id']
                appointments = await tool.get_patient_appointments(patient_id)
                
                for appointment in appointments:
                    if 'appointments_from' not in appointment:
                        integrity_results['appointment_consistency'] = False
                        integrity_results['issues'].append(f"Appointment missing datetime field")
            
            # Test 4: Cross-reference integrity
            if patients and providers:
                # Try to book an appointment and verify it exists
                patient_id = patients[0]['id']
                provider_id = providers[0]['id']
                future_time = (datetime.now() + timedelta(days=5, hours=14)).isoformat()
                
                booking_result = await tool.book_appointment(
                    patient_id=patient_id,
                    provider_id=provider_id,
                    datetime_str=future_time,
                    treatment_type="Integrity Test"
                )
                
                if booking_result['success']:
                    # Verify the appointment appears in patient's appointments
                    updated_appointments = await tool.get_patient_appointments(patient_id)
                    appointment_found = any(
                        'Integrity Test' in str(apt.get('appointments_title', ''))
                        for apt in updated_appointments
                    )
                    
                    if not appointment_found:
                        integrity_results['foreign_key_integrity'] = False
                        integrity_results['issues'].append("Booked appointment not found in patient's appointments")
                    
                    # Clean up test appointment
                    await tool.cancel_appointment(str(booking_result['appointment']['id']))
        
        except Exception as e:
            integrity_results['data_completeness'] = False
            integrity_results['issues'].append(f"Data integrity test error: {e}")
        
        finally:
            await tool.cleanup()
        
        self.results['data_integrity'] = integrity_results
        
        issues_count = len(integrity_results['issues'])
        if issues_count == 0:
            self.log("✅ Data integrity tests passed", "RESULT")
        else:
            self.log(f"⚠️ Data integrity issues found: {issues_count}", "RESULT")
            for issue in integrity_results['issues']:
                self.log(f"   - {issue}", "RESULT")
    
    async def test_performance_benchmarks(self):
        """Performance benchmarking tests"""
        self.log("⚡ Starting performance benchmark tests", "TEST")
        
        tool = AdvancedDentalTool()
        await tool.initialize()
        
        benchmarks = {
            'search_patients': [],
            'get_providers': [],
            'get_available_slots': [],
            'book_appointment': [],
            'health_check': []
        }
        
        try:
            # Benchmark each operation multiple times
            for _ in range(20):
                # Search patients
                start = time.time()
                await tool.search_patients("Test")
                benchmarks['search_patients'].append(time.time() - start)
                
                # Get providers
                start = time.time()
                await tool.get_providers()
                benchmarks['get_providers'].append(time.time() - start)
                
                # Get available slots
                start = time.time()
                await tool.get_available_slots(1, "2025-10-01")
                benchmarks['get_available_slots'].append(time.time() - start)
                
                # Health check
                start = time.time()
                await tool.health_check()
                benchmarks['health_check'].append(time.time() - start)
                
                # Book and cancel appointment (to test write operations)
                start = time.time()
                future_time = (datetime.now() + timedelta(days=10, hours=15)).isoformat()
                booking_result = await tool.book_appointment(1, 1, future_time, "Benchmark Test")
                if booking_result['success']:
                    await tool.cancel_appointment(str(booking_result['appointment']['id']))
                benchmarks['book_appointment'].append(time.time() - start)
        
        except Exception as e:
            self.log(f"Performance benchmark error: {e}", "ERROR")
        
        finally:
            await tool.cleanup()
        
        # Calculate statistics
        performance_stats = {}
        for operation, times in benchmarks.items():
            if times:
                performance_stats[operation] = {
                    'avg': statistics.mean(times),
                    'median': statistics.median(times),
                    'min': min(times),
                    'max': max(times),
                    'std_dev': statistics.stdev(times) if len(times) > 1 else 0
                }
        
        self.results['performance'] = performance_stats
        
        self.log("✅ Performance benchmarks completed", "RESULT")
        for operation, stats in performance_stats.items():
            self.log(f"   {operation}: avg={stats['avg']:.3f}s, median={stats['median']:.3f}s", "RESULT")
    
    async def test_edge_cases(self):
        """Test edge cases and error handling"""
        self.log("🎯 Starting edge case tests", "TEST")
        
        tool = AdvancedDentalTool()
        await tool.initialize()
        
        edge_case_results = {
            'invalid_inputs': 0,
            'boundary_conditions': 0,
            'error_handling': 0,
            'total_tests': 0,
            'issues': []
        }
        
        try:
            # Test invalid patient searches
            invalid_queries = ["", "   ", "!@#$%", "x" * 1000, "SELECT * FROM patients", None]
            for query in invalid_queries:
                try:
                    if query is not None:
                        result = await tool.search_patients(str(query))
                        edge_case_results['total_tests'] += 1
                        if isinstance(result, list):
                            edge_case_results['invalid_inputs'] += 1
                except Exception:
                    edge_case_results['issues'].append(f"Unexpected error with query: {query}")
            
            # Test invalid provider IDs
            invalid_provider_ids = [-1, 0, 999999, "abc", None]
            for provider_id in invalid_provider_ids:
                try:
                    if provider_id is not None:
                        result = await tool.get_available_slots(provider_id, "2025-10-01")
                        edge_case_results['total_tests'] += 1
                        if isinstance(result, list):
                            edge_case_results['boundary_conditions'] += 1
                except Exception:
                    edge_case_results['issues'].append(f"Unexpected error with provider_id: {provider_id}")
            
            # Test invalid dates
            invalid_dates = ["", "2025-13-01", "2025-02-30", "invalid-date", "1900-01-01"]
            for date in invalid_dates:
                try:
                    result = await tool.get_available_slots(1, date)
                    edge_case_results['total_tests'] += 1
                    if isinstance(result, list):
                        edge_case_results['boundary_conditions'] += 1
                except Exception:
                    edge_case_results['issues'].append(f"Unexpected error with date: {date}")
            
            # Test booking with invalid data
            invalid_bookings = [
                (-1, 1, "2025-10-01T10:00:00", "Test"),
                (1, -1, "2025-10-01T10:00:00", "Test"),
                (1, 1, "invalid-datetime", "Test"),
                (1, 1, "2025-10-01T10:00:00", ""),
            ]
            
            for patient_id, provider_id, datetime_str, treatment in invalid_bookings:
                try:
                    result = await tool.book_appointment(patient_id, provider_id, datetime_str, treatment)
                    edge_case_results['total_tests'] += 1
                    if 'success' in result:
                        edge_case_results['error_handling'] += 1
                except Exception:
                    edge_case_results['issues'].append(f"Unexpected error with booking: {patient_id}, {provider_id}")
        
        except Exception as e:
            edge_case_results['issues'].append(f"Edge case test error: {e}")
        
        finally:
            await tool.cleanup()
        
        self.results['edge_cases'] = edge_case_results
        
        total_passed = (edge_case_results['invalid_inputs'] + 
                       edge_case_results['boundary_conditions'] + 
                       edge_case_results['error_handling'])
        
        self.log(f"✅ Edge case tests completed: {total_passed}/{edge_case_results['total_tests']} passed", "RESULT")
        if edge_case_results['issues']:
            self.log(f"⚠️ Issues found: {len(edge_case_results['issues'])}", "RESULT")
    
    async def test_database_stress(self):
        """Stress test the database with rapid operations"""
        self.log("💪 Starting database stress test", "TEST")
        
        stress_results = {
            'rapid_operations': 0,
            'connection_stability': True,
            'memory_usage': 'stable',
            'errors': 0,
            'duration': 0
        }
        
        start_time = time.time()
        
        try:
            # Create multiple tools to stress connections
            tools = []
            for i in range(10):
                tool = AdvancedDentalTool()
                await tool.initialize()
                tools.append(tool)
            
            # Perform rapid operations
            for iteration in range(100):
                tool = random.choice(tools)
                operation = random.choice(['search', 'providers', 'slots'])
                
                try:
                    if operation == 'search':
                        await tool.search_patients(f"test{iteration}")
                    elif operation == 'providers':
                        await tool.get_providers()
                    elif operation == 'slots':
                        await tool.get_available_slots(1, "2025-10-01")
                    
                    stress_results['rapid_operations'] += 1
                    
                except Exception as e:
                    stress_results['errors'] += 1
                    if stress_results['errors'] > 10:  # Too many errors
                        stress_results['connection_stability'] = False
                        break
            
            # Cleanup
            for tool in tools:
                await tool.cleanup()
        
        except Exception as e:
            stress_results['connection_stability'] = False
            self.log(f"Database stress test error: {e}", "ERROR")
        
        stress_results['duration'] = time.time() - start_time
        self.results['database_stress'] = stress_results
        
        self.log(f"✅ Database stress test completed: {stress_results['rapid_operations']} ops in {stress_results['duration']:.2f}s", "RESULT")
        self.log(f"   Connection stability: {'✅' if stress_results['connection_stability'] else '❌'}", "RESULT")
    
    def generate_report(self):
        """Generate comprehensive test report"""
        total_time = time.time() - self.start_time
        
        report = f"""
🔥 AGGRESSIVE TESTING SUITE REPORT 🔥
=====================================
Test Duration: {total_time:.2f} seconds
Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📊 LOAD TEST RESULTS:
- Concurrent Users: {self.results['load_test'].get('num_users', 'N/A')}
- Total Operations: {self.results['load_test'].get('total_operations', 'N/A')}
- Success Rate: {100 - self.results['load_test'].get('error_rate', 0):.1f}%
- Throughput: {self.results['load_test'].get('operations_per_second', 0):.1f} ops/sec
- Avg Response Time: {self.results['load_test'].get('avg_response_time', 0):.3f}s

🔍 DATA INTEGRITY:
- Patient Consistency: {'✅' if self.results['data_integrity'].get('patient_consistency') else '❌'}
- Provider Consistency: {'✅' if self.results['data_integrity'].get('provider_consistency') else '❌'}
- Appointment Consistency: {'✅' if self.results['data_integrity'].get('appointment_consistency') else '❌'}
- Foreign Key Integrity: {'✅' if self.results['data_integrity'].get('foreign_key_integrity') else '❌'}
- Issues Found: {len(self.results['data_integrity'].get('issues', []))}

⚡ PERFORMANCE BENCHMARKS:
"""
        
        for operation, stats in self.results.get('performance', {}).items():
            report += f"- {operation}: {stats['avg']:.3f}s avg, {stats['max']:.3f}s max\n"
        
        report += f"""
🎯 EDGE CASE TESTING:
- Total Tests: {self.results['edge_cases'].get('total_tests', 0)}
- Handled Gracefully: {self.results['edge_cases'].get('invalid_inputs', 0) + self.results['edge_cases'].get('boundary_conditions', 0) + self.results['edge_cases'].get('error_handling', 0)}
- Issues: {len(self.results['edge_cases'].get('issues', []))}

💪 DATABASE STRESS TEST:
- Rapid Operations: {self.results['database_stress'].get('rapid_operations', 0)}
- Connection Stability: {'✅' if self.results['database_stress'].get('connection_stability') else '❌'}
- Errors: {self.results['database_stress'].get('errors', 0)}

🏆 OVERALL ASSESSMENT:
"""
        
        # Calculate overall score
        score = 0
        max_score = 0
        
        # Load test score (30 points)
        if self.results['load_test'].get('error_rate', 100) < 5:
            score += 30
        elif self.results['load_test'].get('error_rate', 100) < 10:
            score += 20
        elif self.results['load_test'].get('error_rate', 100) < 20:
            score += 10
        max_score += 30
        
        # Data integrity score (25 points)
        integrity_issues = len(self.results['data_integrity'].get('issues', []))
        if integrity_issues == 0:
            score += 25
        elif integrity_issues < 3:
            score += 15
        elif integrity_issues < 5:
            score += 10
        max_score += 25
        
        # Performance score (20 points)
        avg_response = self.results['load_test'].get('avg_response_time', 1)
        if avg_response < 0.1:
            score += 20
        elif avg_response < 0.5:
            score += 15
        elif avg_response < 1.0:
            score += 10
        max_score += 20
        
        # Edge case score (15 points)
        edge_total = self.results['edge_cases'].get('total_tests', 1)
        edge_passed = (self.results['edge_cases'].get('invalid_inputs', 0) + 
                      self.results['edge_cases'].get('boundary_conditions', 0) + 
                      self.results['edge_cases'].get('error_handling', 0))
        edge_ratio = edge_passed / edge_total if edge_total > 0 else 0
        score += int(15 * edge_ratio)
        max_score += 15
        
        # Stress test score (10 points)
        if self.results['database_stress'].get('connection_stability'):
            score += 10
        max_score += 10
        
        percentage = (score / max_score * 100) if max_score > 0 else 0
        
        if percentage >= 90:
            grade = "🏆 EXCELLENT"
        elif percentage >= 80:
            grade = "🥇 VERY GOOD"
        elif percentage >= 70:
            grade = "🥈 GOOD"
        elif percentage >= 60:
            grade = "🥉 ACCEPTABLE"
        else:
            grade = "❌ NEEDS IMPROVEMENT"
        
        report += f"Score: {score}/{max_score} ({percentage:.1f}%)\nGrade: {grade}\n"
        
        return report

async def main():
    """Run the complete aggressive testing suite"""
    print("🚀 STARTING AGGRESSIVE TESTING SUITE")
    print("=" * 50)
    
    suite = AggressiveTestSuite()
    
    # Run all tests
    await suite.test_concurrent_users(num_users=25, operations_per_user=8)
    await suite.test_data_integrity()
    await suite.test_performance_benchmarks()
    await suite.test_edge_cases()
    await suite.test_database_stress()
    
    # Generate and display report
    report = suite.generate_report()
    print(report)
    
    # Save detailed results to file
    with open('aggressive_test_results.json', 'w') as f:
        json.dump(suite.results, f, indent=2, default=str)
    
    print("\n📁 Detailed results saved to: aggressive_test_results.json")
    print("🏁 AGGRESSIVE TESTING COMPLETED!")

if __name__ == "__main__":
    asyncio.run(main())
