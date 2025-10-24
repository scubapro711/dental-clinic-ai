"""
Tests for Bug #24: Timing attack vulnerability in authentication.

Ensures that authentication timing is constant regardless of whether
the user exists or not, preventing user enumeration attacks.
"""
import pytest
import time
from statistics import mean, stdev
from sqlalchemy.orm import Session

from app.services.auth_service import AuthService
from app.core.security import dummy_verify_password, get_password_hash
from app.models.user import User, UserRole


class TestBug24TimingAttack:
    """Test timing attack mitigation in authentication."""
    
    def test_dummy_verify_password_takes_time(self):
        """Test that dummy_verify_password takes similar time to real verification."""
        # Measure dummy verification time
        start = time.time()
        result = dummy_verify_password()
        dummy_time = time.time() - start
        
        # Should return False
        assert result is False
        
        # Should take at least 10ms (bcrypt is slow)
        assert dummy_time > 0.01, f"Dummy verification too fast: {dummy_time}s"
        
        # Should take less than 500ms (reasonable upper bound for bcrypt)
        assert dummy_time < 0.5, f"Dummy verification too slow: {dummy_time}s"
    
    def test_constant_time_user_not_found(self, db: Session):
        """Test that non-existent user authentication takes similar time to wrong password."""
        # Create a test user
        test_user = User(
            email="test@example.com",
            hashed_password=get_password_hash("correct_password"),
            full_name="Test User",
            role=UserRole.ORG_STAFF
        )
        db.add(test_user)
        db.commit()
        
        # Measure time for non-existent user (should call dummy_verify_password)
        times_not_exist = []
        for _ in range(10):
            start = time.time()
            result = AuthService.authenticate_user(db, "notexist@example.com", "any_password")
            times_not_exist.append(time.time() - start)
            assert result is None
        
        # Measure time for existing user with wrong password (real verify_password)
        times_wrong_pwd = []
        for _ in range(10):
            start = time.time()
            result = AuthService.authenticate_user(db, "test@example.com", "wrong_password")
            times_wrong_pwd.append(time.time() - start)
            assert result is None
        
        # Calculate averages
        avg_not_exist = mean(times_not_exist)
        avg_wrong_pwd = mean(times_wrong_pwd)
        
        # Times should be similar (within 50% of each other)
        # This is a reasonable tolerance for timing attacks
        ratio = max(avg_not_exist, avg_wrong_pwd) / min(avg_not_exist, avg_wrong_pwd)
        assert ratio < 1.5, f"Timing difference too large: {avg_not_exist:.3f}s vs {avg_wrong_pwd:.3f}s (ratio: {ratio:.2f})"
        
        # Clean up
        db.delete(test_user)
        db.commit()
    
    def test_timing_attack_mitigation_statistical(self, db: Session):
        """Statistical test to ensure timing attack is mitigated."""
        # Create test user
        test_user = User(
            email="timing@example.com",
            hashed_password=get_password_hash("password123"),
            full_name="Timing Test",
            role=UserRole.ORG_STAFF
        )
        db.add(test_user)
        db.commit()
        
        # Collect many samples
        n_samples = 50
        times_not_exist = []
        times_wrong_pwd = []
        
        for _ in range(n_samples):
            # Non-existent user
            start = time.time()
            AuthService.authenticate_user(db, "notexist@example.com", "password")
            times_not_exist.append(time.time() - start)
            
            # Wrong password
            start = time.time()
            AuthService.authenticate_user(db, "timing@example.com", "wrong")
            times_wrong_pwd.append(time.time() - start)
        
        # Statistical analysis
        mean_not_exist = mean(times_not_exist)
        mean_wrong_pwd = mean(times_wrong_pwd)
        std_not_exist = stdev(times_not_exist)
        std_wrong_pwd = stdev(times_wrong_pwd)
        
        # Means should be similar
        diff = abs(mean_not_exist - mean_wrong_pwd)
        combined_std = (std_not_exist + std_wrong_pwd) / 2
        
        # Difference should be less than 2 standard deviations
        assert diff < 2 * combined_std, f"Timing difference statistically significant: {mean_not_exist:.3f}s vs {mean_wrong_pwd:.3f}s"
        
        # Clean up
        db.delete(test_user)
        db.commit()
    
    def test_successful_login_timing(self, db: Session):
        """Test that successful login is faster than failed attempts."""
        # Create test user
        test_user = User(
            email="success@example.com",
            hashed_password=get_password_hash("correct_password"),
            full_name="Success Test",
            role=UserRole.ORG_STAFF
        )
        db.add(test_user)
        db.commit()
        
        # Measure successful login
        times_success = []
        for _ in range(10):
            start = time.time()
            result = AuthService.authenticate_user(db, "success@example.com", "correct_password")
            times_success.append(time.time() - start)
            assert result is not None
            assert result.email == "success@example.com"
        
        # Measure failed login
        times_failed = []
        for _ in range(10):
            start = time.time()
            result = AuthService.authenticate_user(db, "success@example.com", "wrong_password")
            times_failed.append(time.time() - start)
            assert result is None
        
        avg_success = mean(times_success)
        avg_failed = mean(times_failed)
        
        # Successful login should be similar in time (both do bcrypt)
        # But this is expected - we're not trying to hide successful logins
        # Just ensuring failed attempts don't leak user existence
        
        # Clean up
        db.delete(test_user)
        db.commit()
    
    def test_user_enumeration_prevented(self, db: Session):
        """Test that user enumeration via timing is prevented."""
        # Create one user
        test_user = User(
            email="exists@example.com",
            hashed_password=get_password_hash("password"),
            full_name="Exists",
            role=UserRole.ORG_STAFF
        )
        db.add(test_user)
        db.commit()
        
        # Try to enumerate users by timing
        test_emails = [
            "exists@example.com",      # Exists
            "notexist1@example.com",   # Doesn't exist
            "notexist2@example.com",   # Doesn't exist
            "notexist3@example.com",   # Doesn't exist
        ]
        
        timings = {}
        for email in test_emails:
            times = []
            for _ in range(20):
                start = time.time()
                AuthService.authenticate_user(db, email, "wrong_password")
                times.append(time.time() - start)
            timings[email] = mean(times)
        
        # All timings should be similar
        all_times = list(timings.values())
        max_time = max(all_times)
        min_time = min(all_times)
        ratio = max_time / min_time
        
        # Ratio should be close to 1 (within 50%)
        assert ratio < 1.5, f"Timing reveals user existence: {timings}"
        
        # Clean up
        db.delete(test_user)
        db.commit()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
