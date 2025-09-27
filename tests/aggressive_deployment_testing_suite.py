#!/usr/bin/env python3
"""
🚀 Aggressive Deployment Testing Suite
מערכת בדיקות אגרסיבית מקיפה לפריסת AWS

בודק את כל האספקטים של הפריסה:
- תשתית AWS
- ביצועים ועומסים
- אבטחה
- זמינות ועמידות
- Chaos Engineering
- מוניטורינג ולוגים
"""

import asyncio
import aiohttp
import boto3
import json
import time
import random
import subprocess
import logging
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Any, Optional
import psutil
import requests
from dataclasses import dataclass
import yaml

# הגדרת לוגינג
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/aggressive_testing.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class TestResult:
    """תוצאת בדיקה"""
    test_name: str
    status: str  # PASS, FAIL, WARNING
    duration: float
    details: Dict[str, Any]
    timestamp: datetime
    severity: str = "INFO"  # INFO, WARNING, CRITICAL

class AWSInfrastructureTester:
    """בודק תשתית AWS"""
    
    def __init__(self, region='us-east-1'):
        self.region = region
        self.ec2 = boto3.client('ec2', region_name=region)
        self.ecs = boto3.client('ecs', region_name=region)
        self.rds = boto3.client('rds', region_name=region)
        self.elasticache = boto3.client('elasticache', region_name=region)
        self.elbv2 = boto3.client('elbv2', region_name=region)
        self.cloudwatch = boto3.client('cloudwatch', region_name=region)
        
    async def test_vpc_connectivity(self) -> TestResult:
        """בדיקת קישוריות VPC"""
        start_time = time.time()
        try:
            # בדיקת VPC
            vpcs = self.ec2.describe_vpcs(
                Filters=[{'Name': 'tag:Project', 'Values': ['dental-clinic-ai']}]
            )
            
            if not vpcs['Vpcs']:
                return TestResult(
                    "VPC Connectivity", "FAIL", time.time() - start_time,
                    {"error": "No VPC found"}, datetime.now(), "CRITICAL"
                )
            
            vpc_id = vpcs['Vpcs'][0]['VpcId']
            
            # בדיקת subnets
            subnets = self.ec2.describe_subnets(
                Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}]
            )
            
            # בדיקת internet gateway
            igws = self.ec2.describe_internet_gateways(
                Filters=[{'Name': 'attachment.vpc-id', 'Values': [vpc_id]}]
            )
            
            details = {
                "vpc_id": vpc_id,
                "subnets_count": len(subnets['Subnets']),
                "internet_gateway": len(igws['InternetGateways']) > 0,
                "availability_zones": list(set([s['AvailabilityZone'] for s in subnets['Subnets']]))
            }
            
            return TestResult(
                "VPC Connectivity", "PASS", time.time() - start_time,
                details, datetime.now()
            )
            
        except Exception as e:
            return TestResult(
                "VPC Connectivity", "FAIL", time.time() - start_time,
                {"error": str(e)}, datetime.now(), "CRITICAL"
            )
    
    async def test_ecs_services(self) -> TestResult:
        """בדיקת שירותי ECS"""
        start_time = time.time()
        try:
            # בדיקת cluster
            clusters = self.ecs.list_clusters()
            dental_clusters = [c for c in clusters['clusterArns'] if 'dental' in c]
            
            if not dental_clusters:
                return TestResult(
                    "ECS Services", "FAIL", time.time() - start_time,
                    {"error": "No dental cluster found"}, datetime.now(), "CRITICAL"
                )
            
            cluster_arn = dental_clusters[0]
            
            # בדיקת services
            services = self.ecs.list_services(cluster=cluster_arn)
            service_details = []
            
            for service_arn in services['serviceArns']:
                service_desc = self.ecs.describe_services(
                    cluster=cluster_arn,
                    services=[service_arn]
                )
                
                service = service_desc['services'][0]
                service_details.append({
                    "name": service['serviceName'],
                    "status": service['status'],
                    "running_count": service['runningCount'],
                    "desired_count": service['desiredCount'],
                    "pending_count": service['pendingCount']
                })
            
            # בדיקת tasks
            tasks = self.ecs.list_tasks(cluster=cluster_arn)
            
            details = {
                "cluster": cluster_arn.split('/')[-1],
                "services": service_details,
                "total_tasks": len(tasks['taskArns']),
                "healthy_services": len([s for s in service_details if s['status'] == 'ACTIVE'])
            }
            
            # קביעת סטטוס
            unhealthy_services = [s for s in service_details if s['running_count'] != s['desired_count']]
            status = "FAIL" if unhealthy_services else "PASS"
            severity = "CRITICAL" if unhealthy_services else "INFO"
            
            return TestResult(
                "ECS Services", status, time.time() - start_time,
                details, datetime.now(), severity
            )
            
        except Exception as e:
            return TestResult(
                "ECS Services", "FAIL", time.time() - start_time,
                {"error": str(e)}, datetime.now(), "CRITICAL"
            )
    
    async def test_database_connectivity(self) -> TestResult:
        """בדיקת קישוריות מסד נתונים"""
        start_time = time.time()
        try:
            # בדיקת RDS instances
            instances = self.rds.describe_db_instances()
            dental_instances = [i for i in instances['DBInstances'] if 'dental' in i['DBInstanceIdentifier']]
            
            if not dental_instances:
                return TestResult(
                    "Database Connectivity", "FAIL", time.time() - start_time,
                    {"error": "No dental database found"}, datetime.now(), "CRITICAL"
                )
            
            db_instance = dental_instances[0]
            
            # בדיקת ElastiCache
            cache_clusters = self.elasticache.describe_cache_clusters()
            dental_cache = [c for c in cache_clusters['CacheClusters'] if 'dental' in c['CacheClusterId']]
            
            details = {
                "rds_status": db_instance['DBInstanceStatus'],
                "rds_engine": db_instance['Engine'],
                "rds_version": db_instance['EngineVersion'],
                "rds_multi_az": db_instance['MultiAZ'],
                "redis_available": len(dental_cache) > 0,
                "redis_status": dental_cache[0]['CacheClusterStatus'] if dental_cache else None
            }
            
            # קביעת סטטוס
            rds_healthy = db_instance['DBInstanceStatus'] == 'available'
            redis_healthy = dental_cache and dental_cache[0]['CacheClusterStatus'] == 'available'
            
            if rds_healthy and redis_healthy:
                status = "PASS"
                severity = "INFO"
            elif rds_healthy or redis_healthy:
                status = "WARNING"
                severity = "WARNING"
            else:
                status = "FAIL"
                severity = "CRITICAL"
            
            return TestResult(
                "Database Connectivity", status, time.time() - start_time,
                details, datetime.now(), severity
            )
            
        except Exception as e:
            return TestResult(
                "Database Connectivity", "FAIL", time.time() - start_time,
                {"error": str(e)}, datetime.now(), "CRITICAL"
            )

class LoadTester:
    """בודק עומסים וביצועים"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        
    async def test_basic_endpoints(self) -> TestResult:
        """בדיקת endpoints בסיסיים"""
        start_time = time.time()
        endpoints = [
            "/health",
            "/ai/health",
            "/",
            "/docs"
        ]
        
        results = {}
        
        async with aiohttp.ClientSession() as session:
            for endpoint in endpoints:
                try:
                    url = f"{self.base_url}{endpoint}"
                    async with session.get(url, timeout=10) as response:
                        results[endpoint] = {
                            "status_code": response.status,
                            "response_time": response.headers.get('X-Response-Time', 'N/A'),
                            "content_length": len(await response.text())
                        }
                except Exception as e:
                    results[endpoint] = {"error": str(e)}
        
        # קביעת סטטוס
        successful_endpoints = [e for e, r in results.items() if 'error' not in r and r.get('status_code', 0) < 400]
        success_rate = len(successful_endpoints) / len(endpoints)
        
        if success_rate >= 0.8:
            status = "PASS"
            severity = "INFO"
        elif success_rate >= 0.5:
            status = "WARNING"
            severity = "WARNING"
        else:
            status = "FAIL"
            severity = "CRITICAL"
        
        return TestResult(
            "Basic Endpoints", status, time.time() - start_time,
            {"endpoints": results, "success_rate": success_rate}, datetime.now(), severity
        )
    
    async def stress_test_concurrent_requests(self, concurrent_users=100, duration=60) -> TestResult:
        """בדיקת עומס עם בקשות מקבילות"""
        start_time = time.time()
        
        async def make_request(session, url):
            try:
                start_req = time.time()
                async with session.get(url, timeout=30) as response:
                    return {
                        "status": response.status,
                        "response_time": time.time() - start_req,
                        "success": response.status < 400
                    }
            except Exception as e:
                return {
                    "status": 0,
                    "response_time": time.time() - start_req,
                    "success": False,
                    "error": str(e)
                }
        
        results = []
        end_time = time.time() + duration
        
        async with aiohttp.ClientSession() as session:
            while time.time() < end_time:
                tasks = []
                for _ in range(concurrent_users):
                    url = f"{self.base_url}/health"
                    tasks.append(make_request(session, url))
                
                batch_results = await asyncio.gather(*tasks)
                results.extend(batch_results)
                
                await asyncio.sleep(1)  # הפסקה קצרה בין batches
        
        # ניתוח תוצאות
        successful_requests = [r for r in results if r['success']]
        failed_requests = [r for r in results if not r['success']]
        
        if successful_requests:
            avg_response_time = sum(r['response_time'] for r in successful_requests) / len(successful_requests)
            max_response_time = max(r['response_time'] for r in successful_requests)
            min_response_time = min(r['response_time'] for r in successful_requests)
        else:
            avg_response_time = max_response_time = min_response_time = 0
        
        success_rate = len(successful_requests) / len(results) if results else 0
        
        details = {
            "total_requests": len(results),
            "successful_requests": len(successful_requests),
            "failed_requests": len(failed_requests),
            "success_rate": success_rate,
            "avg_response_time": avg_response_time,
            "max_response_time": max_response_time,
            "min_response_time": min_response_time,
            "concurrent_users": concurrent_users,
            "duration": duration
        }
        
        # קביעת סטטוס
        if success_rate >= 0.95 and avg_response_time < 2.0:
            status = "PASS"
            severity = "INFO"
        elif success_rate >= 0.8 and avg_response_time < 5.0:
            status = "WARNING"
            severity = "WARNING"
        else:
            status = "FAIL"
            severity = "CRITICAL"
        
        return TestResult(
            "Stress Test Concurrent", status, time.time() - start_time,
            details, datetime.now(), severity
        )

class SecurityTester:
    """בודק אבטחה"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
    
    async def test_security_headers(self) -> TestResult:
        """בדיקת headers אבטחה"""
        start_time = time.time()
        
        required_headers = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': ['DENY', 'SAMEORIGIN'],
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': None,  # כל ערך מקובל
            'Content-Security-Policy': None
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/health") as response:
                    headers = dict(response.headers)
            
            results = {}
            missing_headers = []
            
            for header, expected_value in required_headers.items():
                if header in headers:
                    actual_value = headers[header]
                    if expected_value is None:
                        results[header] = {"present": True, "value": actual_value}
                    elif isinstance(expected_value, list):
                        results[header] = {
                            "present": True,
                            "value": actual_value,
                            "valid": actual_value in expected_value
                        }
                    else:
                        results[header] = {
                            "present": True,
                            "value": actual_value,
                            "valid": actual_value == expected_value
                        }
                else:
                    results[header] = {"present": False}
                    missing_headers.append(header)
            
            # קביעת סטטוס
            critical_missing = [h for h in missing_headers if h in ['X-Content-Type-Options', 'X-Frame-Options']]
            
            if not missing_headers:
                status = "PASS"
                severity = "INFO"
            elif not critical_missing:
                status = "WARNING"
                severity = "WARNING"
            else:
                status = "FAIL"
                severity = "CRITICAL"
            
            return TestResult(
                "Security Headers", status, time.time() - start_time,
                {"headers": results, "missing_headers": missing_headers}, datetime.now(), severity
            )
            
        except Exception as e:
            return TestResult(
                "Security Headers", "FAIL", time.time() - start_time,
                {"error": str(e)}, datetime.now(), "CRITICAL"
            )
    
    async def test_sql_injection_protection(self) -> TestResult:
        """בדיקת הגנה מפני SQL Injection"""
        start_time = time.time()
        
        # payloads נפוצים לבדיקת SQL injection
        sql_payloads = [
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "' UNION SELECT * FROM users --",
            "admin'--",
            "' OR 1=1#"
        ]
        
        results = {}
        vulnerable_endpoints = []
        
        try:
            async with aiohttp.ClientSession() as session:
                for payload in sql_payloads:
                    # בדיקה על endpoints שונים
                    test_endpoints = [
                        f"/api/search?q={payload}",
                        f"/api/login?username={payload}&password=test"
                    ]
                    
                    for endpoint in test_endpoints:
                        try:
                            url = f"{self.base_url}{endpoint}"
                            async with session.get(url, timeout=10) as response:
                                response_text = await response.text()
                                
                                # חיפוש אחר סימנים של SQL injection
                                sql_errors = [
                                    "SQL syntax error",
                                    "mysql_fetch",
                                    "ORA-",
                                    "PostgreSQL",
                                    "Warning: mysql_"
                                ]
                                
                                has_sql_error = any(error.lower() in response_text.lower() for error in sql_errors)
                                
                                results[f"{endpoint}_{payload}"] = {
                                    "status_code": response.status,
                                    "has_sql_error": has_sql_error,
                                    "response_length": len(response_text)
                                }
                                
                                if has_sql_error:
                                    vulnerable_endpoints.append(endpoint)
                                    
                        except Exception as e:
                            results[f"{endpoint}_{payload}"] = {"error": str(e)}
            
            # קביעת סטטוס
            if vulnerable_endpoints:
                status = "FAIL"
                severity = "CRITICAL"
            else:
                status = "PASS"
                severity = "INFO"
            
            return TestResult(
                "SQL Injection Protection", status, time.time() - start_time,
                {"results": results, "vulnerable_endpoints": vulnerable_endpoints}, datetime.now(), severity
            )
            
        except Exception as e:
            return TestResult(
                "SQL Injection Protection", "FAIL", time.time() - start_time,
                {"error": str(e)}, datetime.now(), "CRITICAL"
            )

class ChaosEngineeringTester:
    """בודק עמידות באמצעות Chaos Engineering"""
    
    def __init__(self, region='us-east-1'):
        self.region = region
        self.ecs = boto3.client('ecs', region_name=region)
    
    async def test_service_resilience(self) -> TestResult:
        """בדיקת עמידות השירות - הפסקת task אקראי"""
        start_time = time.time()
        
        try:
            # מציאת cluster
            clusters = self.ecs.list_clusters()
            dental_clusters = [c for c in clusters['clusterArns'] if 'dental' in c]
            
            if not dental_clusters:
                return TestResult(
                    "Service Resilience", "FAIL", time.time() - start_time,
                    {"error": "No dental cluster found"}, datetime.now(), "CRITICAL"
                )
            
            cluster_arn = dental_clusters[0]
            
            # מציאת tasks פעילים
            tasks = self.ecs.list_tasks(cluster=cluster_arn, desiredStatus='RUNNING')
            
            if not tasks['taskArns']:
                return TestResult(
                    "Service Resilience", "FAIL", time.time() - start_time,
                    {"error": "No running tasks found"}, datetime.now(), "CRITICAL"
                )
            
            # בחירת task אקראי להפסקה
            random_task = random.choice(tasks['taskArns'])
            
            logger.info(f"🔥 Chaos Test: Stopping random task {random_task}")
            
            # הפסקת task
            self.ecs.stop_task(
                cluster=cluster_arn,
                task=random_task,
                reason="Chaos Engineering Test"
            )
            
            # המתנה לשחזור
            recovery_time = 0
            max_wait = 300  # 5 דקות
            
            while recovery_time < max_wait:
                await asyncio.sleep(10)
                recovery_time += 10
                
                # בדיקה אם השירות התאושש
                current_tasks = self.ecs.list_tasks(cluster=cluster_arn, desiredStatus='RUNNING')
                
                if len(current_tasks['taskArns']) >= len(tasks['taskArns']):
                    break
            
            # בדיקת סטטוס סופי
            final_tasks = self.ecs.list_tasks(cluster=cluster_arn, desiredStatus='RUNNING')
            recovered = len(final_tasks['taskArns']) >= len(tasks['taskArns'])
            
            details = {
                "initial_tasks": len(tasks['taskArns']),
                "final_tasks": len(final_tasks['taskArns']),
                "recovery_time": recovery_time,
                "recovered": recovered,
                "stopped_task": random_task.split('/')[-1]
            }
            
            if recovered and recovery_time < 120:  # התאושש תוך 2 דקות
                status = "PASS"
                severity = "INFO"
            elif recovered:
                status = "WARNING"
                severity = "WARNING"
            else:
                status = "FAIL"
                severity = "CRITICAL"
            
            return TestResult(
                "Service Resilience", status, time.time() - start_time,
                details, datetime.now(), severity
            )
            
        except Exception as e:
            return TestResult(
                "Service Resilience", "FAIL", time.time() - start_time,
                {"error": str(e)}, datetime.now(), "CRITICAL"
            )

class MonitoringTester:
    """בודק מוניטורינג ולוגים"""
    
    def __init__(self, region='us-east-1'):
        self.region = region
        self.cloudwatch = boto3.client('cloudwatch', region_name=region)
        self.logs = boto3.client('logs', region_name=region)
    
    async def test_cloudwatch_metrics(self) -> TestResult:
        """בדיקת CloudWatch metrics"""
        start_time = time.time()
        
        try:
            # בדיקת metrics קיימים
            end_time = datetime.utcnow()
            start_time_cw = end_time - timedelta(hours=1)
            
            # בדיקת ECS metrics
            ecs_metrics = self.cloudwatch.get_metric_statistics(
                Namespace='AWS/ECS',
                MetricName='CPUUtilization',
                Dimensions=[
                    {'Name': 'ServiceName', 'Value': 'dental-prod-gateway'}
                ],
                StartTime=start_time_cw,
                EndTime=end_time,
                Period=300,
                Statistics=['Average']
            )
            
            # בדיקת ALB metrics
            alb_metrics = self.cloudwatch.get_metric_statistics(
                Namespace='AWS/ApplicationELB',
                MetricName='RequestCount',
                StartTime=start_time_cw,
                EndTime=end_time,
                Period=300,
                Statistics=['Sum']
            )
            
            details = {
                "ecs_datapoints": len(ecs_metrics['Datapoints']),
                "alb_datapoints": len(alb_metrics['Datapoints']),
                "metrics_available": len(ecs_metrics['Datapoints']) > 0 or len(alb_metrics['Datapoints']) > 0
            }
            
            if details["metrics_available"]:
                status = "PASS"
                severity = "INFO"
            else:
                status = "WARNING"
                severity = "WARNING"
            
            return TestResult(
                "CloudWatch Metrics", status, time.time() - start_time,
                details, datetime.now(), severity
            )
            
        except Exception as e:
            return TestResult(
                "CloudWatch Metrics", "FAIL", time.time() - start_time,
                {"error": str(e)}, datetime.now(), "CRITICAL"
            )
    
    async def test_log_groups(self) -> TestResult:
        """בדיקת log groups"""
        start_time = time.time()
        
        try:
            # חיפוש log groups של הפרויקט
            log_groups = self.logs.describe_log_groups(
                logGroupNamePrefix='/ecs/dental'
            )
            
            log_group_details = []
            
            for log_group in log_groups['logGroups']:
                # בדיקת streams אחרונים
                streams = self.logs.describe_log_streams(
                    logGroupName=log_group['logGroupName'],
                    orderBy='LastEventTime',
                    descending=True,
                    limit=5
                )
                
                log_group_details.append({
                    "name": log_group['logGroupName'],
                    "creation_time": log_group['creationTime'],
                    "stored_bytes": log_group.get('storedBytes', 0),
                    "active_streams": len(streams['logStreams'])
                })
            
            details = {
                "log_groups": log_group_details,
                "total_log_groups": len(log_groups['logGroups'])
            }
            
            if len(log_groups['logGroups']) >= 2:  # gateway + ai-agents
                status = "PASS"
                severity = "INFO"
            elif len(log_groups['logGroups']) >= 1:
                status = "WARNING"
                severity = "WARNING"
            else:
                status = "FAIL"
                severity = "CRITICAL"
            
            return TestResult(
                "Log Groups", status, time.time() - start_time,
                details, datetime.now(), severity
            )
            
        except Exception as e:
            return TestResult(
                "Log Groups", "FAIL", time.time() - start_time,
                {"error": str(e)}, datetime.now(), "CRITICAL"
            )

class AggressiveTestingSuite:
    """מערכת בדיקות אגרסיבית מקיפה"""
    
    def __init__(self, base_url: str, region: str = 'us-east-1'):
        self.base_url = base_url
        self.region = region
        self.results: List[TestResult] = []
        
        # יצירת testers
        self.aws_tester = AWSInfrastructureTester(region)
        self.load_tester = LoadTester(base_url)
        self.security_tester = SecurityTester(base_url)
        self.chaos_tester = ChaosEngineeringTester(region)
        self.monitoring_tester = MonitoringTester(region)
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """הרצת כל הבדיקות"""
        logger.info("🚀 Starting Aggressive Testing Suite")
        start_time = time.time()
        
        # רשימת כל הבדיקות
        test_functions = [
            # בדיקות תשתית
            self.aws_tester.test_vpc_connectivity,
            self.aws_tester.test_ecs_services,
            self.aws_tester.test_database_connectivity,
            
            # בדיקות ביצועים
            self.load_tester.test_basic_endpoints,
            lambda: self.load_tester.stress_test_concurrent_requests(50, 30),  # 50 users, 30 seconds
            
            # בדיקות אבטחה
            self.security_tester.test_security_headers,
            self.security_tester.test_sql_injection_protection,
            
            # בדיקות מוניטורינג
            self.monitoring_tester.test_cloudwatch_metrics,
            self.monitoring_tester.test_log_groups,
            
            # Chaos Engineering (אופציונלי - רק אם מאושר)
            # self.chaos_tester.test_service_resilience,
        ]
        
        # הרצת בדיקות במקביל
        tasks = []
        for test_func in test_functions:
            tasks.append(test_func())
        
        # המתנה לכל הבדיקות
        self.results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # טיפול בחריגות
        processed_results = []
        for i, result in enumerate(self.results):
            if isinstance(result, Exception):
                processed_results.append(TestResult(
                    f"Test_{i}", "FAIL", 0,
                    {"error": str(result)}, datetime.now(), "CRITICAL"
                ))
            else:
                processed_results.append(result)
        
        self.results = processed_results
        
        # יצירת דוח סיכום
        summary = self.generate_summary()
        
        logger.info(f"✅ Testing completed in {time.time() - start_time:.2f} seconds")
        
        return summary
    
    def generate_summary(self) -> Dict[str, Any]:
        """יצירת דוח סיכום"""
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r.status == "PASS"])
        failed_tests = len([r for r in self.results if r.status == "FAIL"])
        warning_tests = len([r for r in self.results if r.status == "WARNING"])
        
        critical_failures = [r for r in self.results if r.severity == "CRITICAL" and r.status == "FAIL"]
        
        # חישוב ציון כללי
        score = (passed_tests * 100 + warning_tests * 50) / (total_tests * 100) if total_tests > 0 else 0
        
        # קביעת סטטוס כללי
        if score >= 0.9 and not critical_failures:
            overall_status = "EXCELLENT"
        elif score >= 0.7 and len(critical_failures) <= 1:
            overall_status = "GOOD"
        elif score >= 0.5:
            overall_status = "ACCEPTABLE"
        else:
            overall_status = "POOR"
        
        return {
            "timestamp": datetime.now().isoformat(),
            "overall_status": overall_status,
            "score": score,
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "warning_tests": warning_tests,
            "critical_failures": len(critical_failures),
            "test_results": [
                {
                    "test_name": r.test_name,
                    "status": r.status,
                    "duration": r.duration,
                    "severity": r.severity,
                    "details": r.details
                }
                for r in self.results
            ],
            "recommendations": self.generate_recommendations()
        }
    
    def generate_recommendations(self) -> List[str]:
        """יצירת המלצות לשיפור"""
        recommendations = []
        
        failed_tests = [r for r in self.results if r.status == "FAIL"]
        warning_tests = [r for r in self.results if r.status == "WARNING"]
        
        for test in failed_tests:
            if "VPC" in test.test_name:
                recommendations.append("🔧 בדוק הגדרות VPC ו-networking")
            elif "ECS" in test.test_name:
                recommendations.append("🔧 בדוק הגדרות ECS services ו-tasks")
            elif "Database" in test.test_name:
                recommendations.append("🔧 בדוק קישוריות למסד נתונים ו-Redis")
            elif "Security" in test.test_name:
                recommendations.append("🔒 שפר הגדרות אבטחה ו-headers")
            elif "Load" in test.test_name or "Stress" in test.test_name:
                recommendations.append("⚡ שפר ביצועים או הגדל משאבים")
        
        for test in warning_tests:
            if "Monitoring" in test.test_name:
                recommendations.append("📊 שפר הגדרות מוניטורינג ו-CloudWatch")
        
        if not recommendations:
            recommendations.append("✅ המערכת עובדת מצוין! המשך לנטר ביצועים")
        
        return recommendations
    
    def save_report(self, filename: str = None):
        """שמירת דוח לקובץ"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"/tmp/aggressive_testing_report_{timestamp}.json"
        
        summary = self.generate_summary()
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"📄 Report saved to {filename}")
        return filename

async def main():
    """פונקציה ראשית"""
    # הגדרות
    BASE_URL = "http://dental-prod-alb-230896070.us-east-1.elb.amazonaws.com"
    REGION = "us-east-1"
    
    # יצירת suite
    suite = AggressiveTestingSuite(BASE_URL, REGION)
    
    try:
        # הרצת בדיקות
        summary = await suite.run_all_tests()
        
        # הדפסת תוצאות
        print("\n" + "="*80)
        print("🚀 AGGRESSIVE TESTING SUITE RESULTS")
        print("="*80)
        print(f"Overall Status: {summary['overall_status']}")
        print(f"Score: {summary['score']:.1%}")
        print(f"Tests: {summary['passed_tests']} PASS, {summary['failed_tests']} FAIL, {summary['warning_tests']} WARNING")
        
        if summary['critical_failures'] > 0:
            print(f"⚠️  Critical Failures: {summary['critical_failures']}")
        
        print("\n📋 RECOMMENDATIONS:")
        for rec in summary['recommendations']:
            print(f"  {rec}")
        
        # שמירת דוח
        report_file = suite.save_report()
        print(f"\n📄 Full report saved to: {report_file}")
        
        return summary
        
    except Exception as e:
        logger.error(f"❌ Testing failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
