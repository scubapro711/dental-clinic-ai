"""
Performance Testing for Patient Portal

Tests response times and caching effectiveness.
"""

import requests
import time
from statistics import mean, median
from datetime import datetime
import sys

# Configuration
BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api/v1"

# Test configuration
NUM_REQUESTS = 10
CACHE_TEST_ITERATIONS = 5

# Colors
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'


def print_header(text):
    """Print header."""
    print(f"\n{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BLUE}{text:^70}{Colors.END}")
    print(f"{Colors.BLUE}{'='*70}{Colors.END}")


def print_success(text):
    """Print success."""
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")


def print_error(text):
    """Print error."""
    print(f"{Colors.RED}✗ {text}{Colors.END}")


def print_info(text):
    """Print info."""
    print(f"{Colors.YELLOW}ℹ {text}{Colors.END}")


class PerformanceTester:
    """Performance testing class."""
    
    def __init__(self, token=None):
        self.token = token
        self.results = {}
    
    def get_headers(self):
        """Get headers."""
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers
    
    def measure_endpoint(self, name, url, params=None):
        """Measure endpoint performance."""
        print(f"\n{Colors.YELLOW}Testing: {name}{Colors.END}")
        print(f"URL: {url}")
        
        times = []
        errors = 0
        
        for i in range(NUM_REQUESTS):
            try:
                start = time.time()
                response = requests.get(
                    url,
                    params=params,
                    headers=self.get_headers(),
                    timeout=30
                )
                end = time.time()
                
                elapsed = (end - start) * 1000  # Convert to ms
                times.append(elapsed)
                
                if response.status_code != 200:
                    errors += 1
                    print_error(f"Request {i+1}: {response.status_code}")
                else:
                    status = "✓" if elapsed < 100 else "⚠" if elapsed < 500 else "✗"
                    print(f"  Request {i+1}: {elapsed:.2f}ms {status}")
                    
            except Exception as e:
                errors += 1
                print_error(f"Request {i+1}: {e}")
        
        if times:
            avg = mean(times)
            med = median(times)
            min_time = min(times)
            max_time = max(times)
            
            self.results[name] = {
                'avg': avg,
                'median': med,
                'min': min_time,
                'max': max_time,
                'errors': errors,
                'total': NUM_REQUESTS
            }
            
            print(f"\n{Colors.BLUE}Results:{Colors.END}")
            print(f"  Average:  {avg:.2f}ms")
            print(f"  Median:   {med:.2f}ms")
            print(f"  Min:      {min_time:.2f}ms")
            print(f"  Max:      {max_time:.2f}ms")
            print(f"  Errors:   {errors}/{NUM_REQUESTS}")
            
            # Performance rating
            if avg < 100:
                print_success("Performance: EXCELLENT")
            elif avg < 500:
                print_info("Performance: GOOD")
            elif avg < 1000:
                print_error("Performance: ACCEPTABLE")
            else:
                print_error("Performance: POOR")
        else:
            print_error("All requests failed")
    
    def test_cache_effectiveness(self, name, url):
        """Test cache effectiveness."""
        print(f"\n{Colors.YELLOW}Cache Test: {name}{Colors.END}")
        print(f"URL: {url}")
        
        first_request_times = []
        cached_request_times = []
        
        for i in range(CACHE_TEST_ITERATIONS):
            print(f"\nIteration {i+1}/{CACHE_TEST_ITERATIONS}")
            
            # First request (cache miss)
            try:
                start = time.time()
                response = requests.get(
                    url,
                    headers=self.get_headers(),
                    timeout=30
                )
                end = time.time()
                
                first_time = (end - start) * 1000
                first_request_times.append(first_time)
                print(f"  First request:  {first_time:.2f}ms (cache miss)")
                
            except Exception as e:
                print_error(f"First request failed: {e}")
                continue
            
            # Second request (cache hit)
            try:
                time.sleep(0.1)  # Small delay
                start = time.time()
                response = requests.get(
                    url,
                    headers=self.get_headers(),
                    timeout=30
                )
                end = time.time()
                
                cached_time = (end - start) * 1000
                cached_request_times.append(cached_time)
                print(f"  Cached request: {cached_time:.2f}ms (cache hit)")
                
                improvement = ((first_time - cached_time) / first_time) * 100
                print(f"  Improvement:    {improvement:.1f}%")
                
            except Exception as e:
                print_error(f"Cached request failed: {e}")
            
            # Wait before next iteration
            time.sleep(1)
        
        if first_request_times and cached_request_times:
            avg_first = mean(first_request_times)
            avg_cached = mean(cached_request_times)
            avg_improvement = ((avg_first - avg_cached) / avg_first) * 100
            
            print(f"\n{Colors.BLUE}Cache Results:{Colors.END}")
            print(f"  Avg First Request:  {avg_first:.2f}ms")
            print(f"  Avg Cached Request: {avg_cached:.2f}ms")
            print(f"  Avg Improvement:    {avg_improvement:.1f}%")
            
            if avg_improvement > 70:
                print_success("Cache: EXCELLENT")
            elif avg_improvement > 40:
                print_success("Cache: GOOD")
            elif avg_improvement > 20:
                print_info("Cache: ACCEPTABLE")
            else:
                print_error("Cache: POOR")
    
    def run_all_tests(self):
        """Run all performance tests."""
        print_header("DENTAFLOW PERFORMANCE TESTS")
        print(f"Base URL: {BASE_URL}")
        print(f"Requests per endpoint: {NUM_REQUESTS}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Test 1: Health check
        print_header("Test 1: Health Check")
        self.measure_endpoint(
            "Health Check",
            f"{BASE_URL}/health"
        )
        
        # Test 2: API docs
        print_header("Test 2: API Documentation")
        self.measure_endpoint(
            "API Docs",
            f"{BASE_URL}/docs"
        )
        
        # If we have a token, test authenticated endpoints
        if self.token:
            print_header("Test 3: Patient Profile")
            self.measure_endpoint(
                "Patient Profile",
                f"{API_URL}/patient/profile"
            )
            
            print_header("Test 4: Health Score")
            self.measure_endpoint(
                "Health Score",
                f"{API_URL}/patient/health-score"
            )
            
            print_header("Test 5: Appointments")
            self.measure_endpoint(
                "Appointments",
                f"{API_URL}/appointments",
                params={"filter": "upcoming"}
            )
            
            print_header("Test 6: Doctors")
            self.measure_endpoint(
                "Doctors",
                f"{API_URL}/doctors"
            )
            
            print_header("Test 7: Available Slots")
            self.measure_endpoint(
                "Available Slots",
                f"{API_URL}/appointments/available-slots",
                params={
                    "start_date": "2025-10-10",
                    "end_date": "2025-10-17"
                }
            )
            
            # Cache tests
            print_header("CACHE EFFECTIVENESS TESTS")
            
            self.test_cache_effectiveness(
                "Patient Profile Cache",
                f"{API_URL}/patient/profile"
            )
            
            self.test_cache_effectiveness(
                "Doctors Cache",
                f"{API_URL}/doctors"
            )
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print summary."""
        print_header("PERFORMANCE SUMMARY")
        
        if not self.results:
            print_error("No results to display")
            return
        
        print(f"\n{'Endpoint':<30} {'Avg (ms)':<12} {'Median (ms)':<12} {'Rating':<12}")
        print("-" * 70)
        
        for name, data in self.results.items():
            avg = data['avg']
            med = data['median']
            
            if avg < 100:
                rating = f"{Colors.GREEN}EXCELLENT{Colors.END}"
            elif avg < 500:
                rating = f"{Colors.YELLOW}GOOD{Colors.END}"
            elif avg < 1000:
                rating = f"{Colors.YELLOW}ACCEPTABLE{Colors.END}"
            else:
                rating = f"{Colors.RED}POOR{Colors.END}"
            
            print(f"{name:<30} {avg:>10.2f}  {med:>10.2f}  {rating}")
        
        # Overall rating
        avg_times = [data['avg'] for data in self.results.values()]
        overall_avg = mean(avg_times)
        
        print(f"\n{Colors.BLUE}Overall Average: {overall_avg:.2f}ms{Colors.END}")
        
        if overall_avg < 100:
            print_success("Overall Performance: EXCELLENT ✓")
        elif overall_avg < 500:
            print_info("Overall Performance: GOOD ✓")
        elif overall_avg < 1000:
            print_info("Overall Performance: ACCEPTABLE ⚠")
        else:
            print_error("Overall Performance: POOR ✗")


def main():
    """Main function."""
    # Check if token is provided
    token = None
    if len(sys.argv) > 1:
        token = sys.argv[1]
        print(f"Using provided token: {token[:20]}...")
    else:
        print("No token provided - testing public endpoints only")
        print("Usage: python test_performance.py <token>")
    
    tester = PerformanceTester(token=token)
    tester.run_all_tests()


if __name__ == "__main__":
    main()

