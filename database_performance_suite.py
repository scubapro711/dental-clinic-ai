#!/usr/bin/env python3
"""
📊 DATABASE PERFORMANCE TESTING SUITE 📊
Advanced database performance and stress testing

This suite performs:
- Connection pool testing
- Query performance analysis
- Database lock testing
- Memory usage monitoring
- Concurrent transaction testing
- Index efficiency testing
"""

import asyncio
import pymysql
import time
import threading
import statistics
import psutil
import os
import sys
from datetime import datetime, timedelta
import json
import random

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from ai_agents.tools.demo_data_adapter import DemoDataAdapter

class DatabasePerformanceTestSuite:
    """Comprehensive database performance testing suite"""
    
    def __init__(self):
        self.db_config = {
            'host': 'localhost',
            'user': 'dental_user',
            'password': 'dental_pass_2025',
            'database': 'dental_clinic_demo',
            'port': 3306,
            'charset': 'utf8mb4',
        }
        self.results = {
            'connection_pool': {},
            'query_performance': {},
            'concurrent_transactions': {},
            'memory_usage': {},
            'index_efficiency': {},
            'stress_test': {}
        }
        self.start_time = time.time()
        
    def log(self, message: str, level: str = "INFO"):
        """Enhanced logging with timestamps"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"[{timestamp}] [{level}] {message}")
    
    def get_memory_usage(self):
        """Get current memory usage"""
        process = psutil.Process(os.getpid())
        return {
            'rss': process.memory_info().rss / 1024 / 1024,  # MB
            'vms': process.memory_info().vms / 1024 / 1024,  # MB
            'percent': process.memory_percent()
        }
    
    async def test_connection_pool_performance(self):
        """Test database connection pool performance"""
        self.log("🔗 Starting connection pool performance tests", "PERF")
        
        pool_results = {
            'single_connection_time': [],
            'multiple_connections_time': [],
            'connection_reuse_time': [],
            'max_connections_tested': 0,
            'connection_failures': 0
        }
        
        # Test single connection performance
        for i in range(10):
            start_time = time.time()
            try:
                connection = pymysql.connect(**self.db_config)
                connection.close()
                pool_results['single_connection_time'].append(time.time() - start_time)
            except Exception as e:
                pool_results['connection_failures'] += 1
                self.log(f"Connection failure: {e}", "ERROR")
        
        # Test multiple simultaneous connections
        async def create_connection(connection_id):
            start_time = time.time()
            try:
                connection = pymysql.connect(**self.db_config)
                # Perform a simple query
                cursor = connection.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()
                cursor.close()
                connection.close()
                return time.time() - start_time
            except Exception as e:
                self.log(f"Connection {connection_id} failed: {e}", "ERROR")
                return None
        
        # Test with increasing number of concurrent connections
        for num_connections in [5, 10, 20, 50]:
            start_time = time.time()
            tasks = [create_connection(i) for i in range(num_connections)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            successful_connections = [r for r in results if isinstance(r, float)]
            pool_results['multiple_connections_time'].extend(successful_connections)
            pool_results['max_connections_tested'] = max(pool_results['max_connections_tested'], len(successful_connections))
            
            total_time = time.time() - start_time
            self.log(f"   {len(successful_connections)}/{num_connections} connections in {total_time:.3f}s", "PERF")
        
        # Test connection reuse
        connection = pymysql.connect(**self.db_config)
        for i in range(20):
            start_time = time.time()
            cursor = connection.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            pool_results['connection_reuse_time'].append(time.time() - start_time)
        connection.close()
        
        self.results['connection_pool'] = pool_results
        
        avg_single = statistics.mean(pool_results['single_connection_time']) if pool_results['single_connection_time'] else 0
        avg_multiple = statistics.mean(pool_results['multiple_connections_time']) if pool_results['multiple_connections_time'] else 0
        avg_reuse = statistics.mean(pool_results['connection_reuse_time']) if pool_results['connection_reuse_time'] else 0
        
        self.log(f"✅ Connection pool test completed", "PERF")
        self.log(f"   Single connection: {avg_single:.3f}s avg", "PERF")
        self.log(f"   Multiple connections: {avg_multiple:.3f}s avg", "PERF")
        self.log(f"   Connection reuse: {avg_reuse:.3f}s avg", "PERF")
    
    async def test_query_performance(self):
        """Test query performance across different scenarios"""
        self.log("📊 Starting query performance tests", "PERF")
        
        query_results = {
            'simple_select': [],
            'complex_join': [],
            'aggregation': [],
            'insert_performance': [],
            'update_performance': [],
            'delete_performance': []
        }
        
        connection = pymysql.connect(**self.db_config)
        cursor = connection.cursor()
        
        try:
            # Simple SELECT queries
            for i in range(50):
                start_time = time.time()
                cursor.execute("SELECT * FROM patients LIMIT 10")
                cursor.fetchall()
                query_results['simple_select'].append(time.time() - start_time)
            
            # Complex JOIN queries
            for i in range(20):
                start_time = time.time()
                cursor.execute("""
                    SELECT p.patients_name, p.patients_surname, d.doctors_name, a.appointments_title
                    FROM patients p
                    JOIN appointments a ON p.patients_id = a.patients_id
                    JOIN doctors d ON a.doctors_id = d.doctors_id
                    LIMIT 20
                """)
                cursor.fetchall()
                query_results['complex_join'].append(time.time() - start_time)
            
            # Aggregation queries
            for i in range(30):
                start_time = time.time()
                cursor.execute("""
                    SELECT d.doctors_name, COUNT(a.appointments_id) as appointment_count
                    FROM doctors d
                    LEFT JOIN appointments a ON d.doctors_id = a.doctors_id
                    GROUP BY d.doctors_id, d.doctors_name
                """)
                cursor.fetchall()
                query_results['aggregation'].append(time.time() - start_time)
            
            # INSERT performance
            for i in range(20):
                start_time = time.time()
                cursor.execute("""
                    INSERT INTO patients (treatmentspriceslists_id, patients_name, patients_surname, 
                                        patients_sex, patients_birthdate, patients_birthcity, 
                                        patients_doctext, patients_username, patients_password)
                    VALUES (1, %s, %s, 'M', '1990-01-01', 'Test City', 'Test patient', %s, 'test123')
                """, (f'TestName{i}', f'TestSurname{i}', f'test{i}'))
                connection.commit()
                query_results['insert_performance'].append(time.time() - start_time)
            
            # UPDATE performance
            for i in range(20):
                start_time = time.time()
                cursor.execute("""
                    UPDATE patients SET patients_notes = %s 
                    WHERE patients_name LIKE 'TestName%' LIMIT 1
                """, (f'Updated note {i}',))
                connection.commit()
                query_results['update_performance'].append(time.time() - start_time)
            
            # DELETE performance (cleanup test data)
            for i in range(20):
                start_time = time.time()
                cursor.execute("DELETE FROM patients WHERE patients_name LIKE 'TestName%' LIMIT 1")
                connection.commit()
                query_results['delete_performance'].append(time.time() - start_time)
        
        except Exception as e:
            self.log(f"Query performance test error: {e}", "ERROR")
        
        finally:
            cursor.close()
            connection.close()
        
        self.results['query_performance'] = query_results
        
        self.log("✅ Query performance test completed", "PERF")
        for query_type, times in query_results.items():
            if times:
                avg_time = statistics.mean(times)
                max_time = max(times)
                self.log(f"   {query_type}: {avg_time:.4f}s avg, {max_time:.4f}s max", "PERF")
    
    async def test_concurrent_transactions(self):
        """Test concurrent transaction performance"""
        self.log("🔄 Starting concurrent transaction tests", "PERF")
        
        transaction_results = {
            'concurrent_reads': [],
            'concurrent_writes': [],
            'deadlock_count': 0,
            'transaction_conflicts': 0
        }
        
        async def concurrent_read_worker(worker_id, num_operations):
            """Worker for concurrent read operations"""
            connection = pymysql.connect(**self.db_config)
            cursor = connection.cursor()
            times = []
            
            try:
                for i in range(num_operations):
                    start_time = time.time()
                    cursor.execute("SELECT * FROM patients WHERE patients_id = %s", (random.randint(1, 20),))
                    cursor.fetchall()
                    times.append(time.time() - start_time)
                    await asyncio.sleep(0.001)  # Small delay
            except Exception as e:
                self.log(f"Read worker {worker_id} error: {e}", "ERROR")
            finally:
                cursor.close()
                connection.close()
            
            return times
        
        async def concurrent_write_worker(worker_id, num_operations):
            """Worker for concurrent write operations"""
            connection = pymysql.connect(**self.db_config)
            cursor = connection.cursor()
            times = []
            
            try:
                for i in range(num_operations):
                    start_time = time.time()
                    try:
                        # Insert a test record
                        cursor.execute("""
                            INSERT INTO patients (treatmentspriceslists_id, patients_name, patients_surname, 
                                                patients_sex, patients_birthdate, patients_birthcity, 
                                                patients_doctext, patients_username, patients_password)
                            VALUES (1, %s, %s, 'M', '1990-01-01', 'Test City', 'Concurrent test', %s, 'test123')
                        """, (f'ConcTest{worker_id}_{i}', f'Worker{worker_id}', f'conc{worker_id}{i}'))
                        connection.commit()
                        
                        # Delete the test record
                        cursor.execute("DELETE FROM patients WHERE patients_name = %s", (f'ConcTest{worker_id}_{i}',))
                        connection.commit()
                        
                        times.append(time.time() - start_time)
                    except pymysql.Error as e:
                        if "Deadlock" in str(e):
                            transaction_results['deadlock_count'] += 1
                        else:
                            transaction_results['transaction_conflicts'] += 1
                        connection.rollback()
                    
                    await asyncio.sleep(0.001)  # Small delay
            except Exception as e:
                self.log(f"Write worker {worker_id} error: {e}", "ERROR")
            finally:
                cursor.close()
                connection.close()
            
            return times
        
        # Test concurrent reads
        read_tasks = [concurrent_read_worker(i, 10) for i in range(10)]
        read_results = await asyncio.gather(*read_tasks, return_exceptions=True)
        
        for result in read_results:
            if isinstance(result, list):
                transaction_results['concurrent_reads'].extend(result)
        
        # Test concurrent writes
        write_tasks = [concurrent_write_worker(i, 5) for i in range(5)]
        write_results = await asyncio.gather(*write_tasks, return_exceptions=True)
        
        for result in write_results:
            if isinstance(result, list):
                transaction_results['concurrent_writes'].extend(result)
        
        self.results['concurrent_transactions'] = transaction_results
        
        avg_read = statistics.mean(transaction_results['concurrent_reads']) if transaction_results['concurrent_reads'] else 0
        avg_write = statistics.mean(transaction_results['concurrent_writes']) if transaction_results['concurrent_writes'] else 0
        
        self.log("✅ Concurrent transaction test completed", "PERF")
        self.log(f"   Concurrent reads: {avg_read:.4f}s avg", "PERF")
        self.log(f"   Concurrent writes: {avg_write:.4f}s avg", "PERF")
        self.log(f"   Deadlocks: {transaction_results['deadlock_count']}", "PERF")
        self.log(f"   Conflicts: {transaction_results['transaction_conflicts']}", "PERF")
    
    async def test_memory_usage(self):
        """Test memory usage during database operations"""
        self.log("💾 Starting memory usage tests", "PERF")
        
        memory_results = {
            'baseline_memory': self.get_memory_usage(),
            'peak_memory': self.get_memory_usage(),
            'memory_samples': []
        }
        
        # Create multiple adapters to simulate real usage
        adapters = []
        for i in range(20):
            adapter = DemoDataAdapter(self.db_config)
            adapter.connect()
            adapters.append(adapter)
            
            # Sample memory usage
            current_memory = self.get_memory_usage()
            memory_results['memory_samples'].append(current_memory)
            
            if current_memory['rss'] > memory_results['peak_memory']['rss']:
                memory_results['peak_memory'] = current_memory
        
        # Perform operations with all adapters
        for i, adapter in enumerate(adapters):
            try:
                # Perform various operations
                adapter.search_patients("test")
                adapter.get_providers()
                adapter.get_available_slots(1, "2025-10-01")
                
                # Sample memory after operations
                current_memory = self.get_memory_usage()
                memory_results['memory_samples'].append(current_memory)
                
                if current_memory['rss'] > memory_results['peak_memory']['rss']:
                    memory_results['peak_memory'] = current_memory
                    
            except Exception as e:
                self.log(f"Memory test adapter {i} error: {e}", "ERROR")
        
        # Cleanup
        for adapter in adapters:
            adapter.disconnect()
        
        # Final memory sample
        final_memory = self.get_memory_usage()
        memory_results['final_memory'] = final_memory
        
        self.results['memory_usage'] = memory_results
        
        baseline_mb = memory_results['baseline_memory']['rss']
        peak_mb = memory_results['peak_memory']['rss']
        final_mb = memory_results['final_memory']['rss']
        
        self.log("✅ Memory usage test completed", "PERF")
        self.log(f"   Baseline: {baseline_mb:.1f} MB", "PERF")
        self.log(f"   Peak: {peak_mb:.1f} MB (+{peak_mb - baseline_mb:.1f} MB)", "PERF")
        self.log(f"   Final: {final_mb:.1f} MB", "PERF")
    
    async def test_index_efficiency(self):
        """Test database index efficiency"""
        self.log("🔍 Starting index efficiency tests", "PERF")
        
        index_results = {
            'indexed_queries': [],
            'non_indexed_queries': [],
            'query_plans': []
        }
        
        connection = pymysql.connect(**self.db_config)
        cursor = connection.cursor()
        
        try:
            # Test indexed queries (assuming we have indexes on common fields)
            indexed_queries = [
                "SELECT * FROM patients WHERE patients_id = 1",
                "SELECT * FROM doctors WHERE doctors_id = 1",
                "SELECT * FROM appointments WHERE appointments_id = 1"
            ]
            
            for query in indexed_queries:
                start_time = time.time()
                cursor.execute(query)
                cursor.fetchall()
                index_results['indexed_queries'].append(time.time() - start_time)
            
            # Test non-indexed queries (full table scans)
            non_indexed_queries = [
                "SELECT * FROM patients WHERE patients_notes LIKE '%test%'",
                "SELECT * FROM doctors WHERE doctors_doctext LIKE '%specialist%'",
                "SELECT * FROM appointments WHERE appointments_notes LIKE '%urgent%'"
            ]
            
            for query in non_indexed_queries:
                start_time = time.time()
                cursor.execute(query)
                cursor.fetchall()
                index_results['non_indexed_queries'].append(time.time() - start_time)
            
            # Get query execution plans (if supported)
            try:
                cursor.execute("EXPLAIN SELECT * FROM patients WHERE patients_id = 1")
                plan = cursor.fetchall()
                index_results['query_plans'].append(('indexed_query', plan))
                
                cursor.execute("EXPLAIN SELECT * FROM patients WHERE patients_notes LIKE '%test%'")
                plan = cursor.fetchall()
                index_results['query_plans'].append(('non_indexed_query', plan))
            except Exception as e:
                self.log(f"Could not get query plans: {e}", "WARNING")
        
        except Exception as e:
            self.log(f"Index efficiency test error: {e}", "ERROR")
        
        finally:
            cursor.close()
            connection.close()
        
        self.results['index_efficiency'] = index_results
        
        avg_indexed = statistics.mean(index_results['indexed_queries']) if index_results['indexed_queries'] else 0
        avg_non_indexed = statistics.mean(index_results['non_indexed_queries']) if index_results['non_indexed_queries'] else 0
        
        self.log("✅ Index efficiency test completed", "PERF")
        self.log(f"   Indexed queries: {avg_indexed:.4f}s avg", "PERF")
        self.log(f"   Non-indexed queries: {avg_non_indexed:.4f}s avg", "PERF")
        if avg_indexed > 0 and avg_non_indexed > 0:
            speedup = avg_non_indexed / avg_indexed
            self.log(f"   Index speedup: {speedup:.1f}x", "PERF")
    
    def generate_performance_report(self):
        """Generate comprehensive performance report"""
        total_time = time.time() - self.start_time
        
        report = f"""
📊 DATABASE PERFORMANCE TESTING REPORT 📊
=========================================
Test Duration: {total_time:.2f} seconds
Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🔗 CONNECTION POOL PERFORMANCE:
- Single Connection Avg: {statistics.mean(self.results['connection_pool'].get('single_connection_time', [0])):.4f}s
- Multiple Connections Avg: {statistics.mean(self.results['connection_pool'].get('multiple_connections_time', [0])):.4f}s
- Connection Reuse Avg: {statistics.mean(self.results['connection_pool'].get('connection_reuse_time', [0])):.4f}s
- Max Concurrent Connections: {self.results['connection_pool'].get('max_connections_tested', 0)}
- Connection Failures: {self.results['connection_pool'].get('connection_failures', 0)}

📊 QUERY PERFORMANCE:
"""
        
        for query_type, times in self.results.get('query_performance', {}).items():
            if times:
                avg_time = statistics.mean(times)
                max_time = max(times)
                min_time = min(times)
                report += f"- {query_type}: {avg_time:.4f}s avg (min: {min_time:.4f}s, max: {max_time:.4f}s)\n"
        
        concurrent_reads = self.results.get('concurrent_transactions', {}).get('concurrent_reads', [])
        concurrent_writes = self.results.get('concurrent_transactions', {}).get('concurrent_writes', [])
        
        report += f"""
🔄 CONCURRENT TRANSACTIONS:
- Concurrent Reads Avg: {statistics.mean(concurrent_reads) if concurrent_reads else 0:.4f}s
- Concurrent Writes Avg: {statistics.mean(concurrent_writes) if concurrent_writes else 0:.4f}s
- Deadlocks: {self.results.get('concurrent_transactions', {}).get('deadlock_count', 0)}
- Transaction Conflicts: {self.results.get('concurrent_transactions', {}).get('transaction_conflicts', 0)}

💾 MEMORY USAGE:
- Baseline Memory: {self.results.get('memory_usage', {}).get('baseline_memory', {}).get('rss', 0):.1f} MB
- Peak Memory: {self.results.get('memory_usage', {}).get('peak_memory', {}).get('rss', 0):.1f} MB
- Final Memory: {self.results.get('memory_usage', {}).get('final_memory', {}).get('rss', 0):.1f} MB
- Memory Increase: {self.results.get('memory_usage', {}).get('peak_memory', {}).get('rss', 0) - self.results.get('memory_usage', {}).get('baseline_memory', {}).get('rss', 0):.1f} MB

🔍 INDEX EFFICIENCY:
- Indexed Queries Avg: {statistics.mean(self.results.get('index_efficiency', {}).get('indexed_queries', [0])):.4f}s
- Non-Indexed Queries Avg: {statistics.mean(self.results.get('index_efficiency', {}).get('non_indexed_queries', [0])):.4f}s
"""
        
        indexed_avg = statistics.mean(self.results.get('index_efficiency', {}).get('indexed_queries', [0]))
        non_indexed_avg = statistics.mean(self.results.get('index_efficiency', {}).get('non_indexed_queries', [0]))
        
        if indexed_avg > 0 and non_indexed_avg > 0:
            speedup = non_indexed_avg / indexed_avg
            report += f"- Index Speedup: {speedup:.1f}x\n"
        
        # Performance score calculation
        score = 0
        max_score = 100
        
        # Connection performance (20 points)
        avg_connection_time = statistics.mean(self.results['connection_pool'].get('single_connection_time', [1]))
        if avg_connection_time < 0.01:
            score += 20
        elif avg_connection_time < 0.05:
            score += 15
        elif avg_connection_time < 0.1:
            score += 10
        
        # Query performance (30 points)
        simple_select_avg = statistics.mean(self.results.get('query_performance', {}).get('simple_select', [1]))
        if simple_select_avg < 0.001:
            score += 30
        elif simple_select_avg < 0.01:
            score += 20
        elif simple_select_avg < 0.1:
            score += 10
        
        # Concurrent performance (25 points)
        if len(concurrent_reads) > 0:
            concurrent_read_avg = statistics.mean(concurrent_reads)
            if concurrent_read_avg < 0.01:
                score += 25
            elif concurrent_read_avg < 0.05:
                score += 15
            elif concurrent_read_avg < 0.1:
                score += 10
        
        # Memory efficiency (15 points)
        memory_increase = (self.results.get('memory_usage', {}).get('peak_memory', {}).get('rss', 100) - 
                          self.results.get('memory_usage', {}).get('baseline_memory', {}).get('rss', 0))
        if memory_increase < 50:  # Less than 50MB increase
            score += 15
        elif memory_increase < 100:
            score += 10
        elif memory_increase < 200:
            score += 5
        
        # Index efficiency (10 points)
        if indexed_avg > 0 and non_indexed_avg > 0:
            speedup = non_indexed_avg / indexed_avg
            if speedup > 10:
                score += 10
            elif speedup > 5:
                score += 7
            elif speedup > 2:
                score += 5
        
        percentage = (score / max_score * 100)
        
        if percentage >= 90:
            performance_grade = "🚀 EXCELLENT PERFORMANCE"
        elif percentage >= 80:
            performance_grade = "⚡ GOOD PERFORMANCE"
        elif percentage >= 70:
            performance_grade = "📊 ACCEPTABLE PERFORMANCE"
        elif percentage >= 60:
            performance_grade = "⚠️ MODERATE PERFORMANCE"
        else:
            performance_grade = "🐌 POOR PERFORMANCE"
        
        report += f"""
🏆 OVERALL PERFORMANCE ASSESSMENT:
Performance Score: {score}/{max_score} ({percentage:.1f}%)
Performance Grade: {performance_grade}
"""
        
        return report

async def main():
    """Run the complete database performance testing suite"""
    print("📊 STARTING DATABASE PERFORMANCE TESTING SUITE")
    print("=" * 60)
    
    suite = DatabasePerformanceTestSuite()
    
    # Run all performance tests
    await suite.test_connection_pool_performance()
    await suite.test_query_performance()
    await suite.test_concurrent_transactions()
    await suite.test_memory_usage()
    await suite.test_index_efficiency()
    
    # Generate and display report
    report = suite.generate_performance_report()
    print(report)
    
    # Save detailed results to file
    with open('database_performance_results.json', 'w') as f:
        json.dump(suite.results, f, indent=2, default=str)
    
    print("\n📁 Detailed performance results saved to: database_performance_results.json")
    print("🏁 DATABASE PERFORMANCE TESTING COMPLETED!")

if __name__ == "__main__":
    asyncio.run(main())
