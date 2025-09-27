import unittest
from src.agent.activity_processor import ActivityStreamProcessor
from datetime import datetime, timedelta

class TestActivityStreamProcessor(unittest.TestCase):

    def setUp(self):
        self.processor = ActivityStreamProcessor()

    def test_process_log_known_patterns(self):
        self.assertEqual(self.processor.process_log({"message": "user login successful"}), "User logged in successfully.")
        self.assertEqual(self.processor.process_log({"message": "appointment created"}), "A new appointment was scheduled.")
        self.assertEqual(self.processor.process_log({"message": "patient added"}), "A new patient record was created.")

    def test_process_log_unknown_pattern(self):
        self.assertEqual(self.processor.process_log({"message": "user clicked button"}), "New activity: user clicked button")

    def test_process_stream(self):
        logs = [
            {"message": "user login successful"},
            {"message": "user clicked button"}
        ]
        self.assertEqual(self.processor.process_stream(logs), ["User logged in successfully.", "New activity: user clicked button"])

    def test_detect_patterns_failed_logins(self):
        logs = [{"message": "login failed"}] * 4
        patterns = self.processor.detect_patterns(logs)
        self.assertIn("Multiple failed login attempts detected (4). Possible security concern.", patterns)

    def test_detect_patterns_high_frequency(self):
        logs = [{"message": "same message"}] * 11
        patterns = self.processor.detect_patterns(logs)
        self.assertIn("High frequency of message: 'same message' (11 times).", patterns)

    def test_detect_patterns_rapid_succession(self):
        base_time = datetime.now()
        logs = [{"timestamp": base_time + timedelta(milliseconds=i*100)} for i in range(25)]
        patterns = self.processor.detect_patterns(logs)
        self.assertIn("Rapid succession of events detected (24 events in under 1 second).", patterns)

    def test_create_summary(self):
        logs = [
            {"timestamp": "2025-09-27 18:00:00", "message": "user login successful"},
            {"timestamp": "2025-09-27 18:01:00", "message": "appointment created"},
            {"timestamp": "2025-09-27 18:02:00", "message": "user login successful"}
        ]
        summary = self.processor.create_summary(logs)
        self.assertIn("3 activities recorded", summary)
        self.assertIn("User logged in successfully.: 2", summary)
        self.assertIn("A new appointment was scheduled.: 1", summary)

    def test_create_summary_no_logs(self):
        self.assertEqual(self.processor.create_summary([]), "No activity recorded.")

    def test_performance_benchmark(self):
        benchmark_results = self.processor.performance_benchmark(num_logs=1000)
        self.assertGreater(benchmark_results["logs_per_second"], 1000) # Check if it can process at least 1000 logs/sec

if __name__ == '__main__':
    unittest.main()

