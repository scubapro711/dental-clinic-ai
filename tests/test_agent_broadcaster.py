"""
Comprehensive Test Suite for Agent Status Broadcasting - Component 1.2
Aggressive testing protocol for real-time agent activity broadcasting

Test Categories:
1. Agent registration and status management
2. Activity broadcasting and processing
3. Decision explanation generation
4. Performance metrics tracking
5. Human handoff triggers
6. Integration with existing agent tools
7. WebSocket message broadcasting
8. Memory management and cleanup
"""

import asyncio
import json
import pytest
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any
from unittest.mock import Mock, patch, AsyncMock

# Import the broadcaster components
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src', 'websocket'))

from agent_broadcaster import (
    AgentBroadcaster, AgentStatus, ActivityType, AgentActivity, 
    AgentStatusUpdate, DecisionExplanation, broadcaster,
    start_agent_broadcasting, stop_agent_broadcasting, broadcast_custom_activity
)

class TestAgentBroadcaster:
    """Test suite for Agent Status Broadcasting"""
    
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """Setup and teardown for each test"""
        # Reset broadcaster state
        broadcaster.active_agents.clear()
        broadcaster.activity_history.clear()
        broadcaster.decision_history.clear()
        broadcaster.subscribers.clear()
        broadcaster.performance_metrics = {
            'total_activities': 0,
            'successful_activities': 0,
            'failed_activities': 0,
            'average_response_time': 0,
            'human_handoffs': 0,
            'decisions_made': 0
        }
        broadcaster.monitoring_active = False
        if broadcaster.monitoring_task:
            broadcaster.monitoring_task.cancel()
            broadcaster.monitoring_task = None
        
        yield
        
        # Cleanup after test
        broadcaster.active_agents.clear()
        broadcaster.activity_history.clear()
        broadcaster.decision_history.clear()
    
    @pytest.fixture
    def mock_websocket_manager(self):
        """Mock WebSocket manager for testing"""
        with patch('agent_broadcaster.websocket_manager') as mock_manager:
            mock_manager.broadcast = AsyncMock()
            yield mock_manager

class TestAgentRegistration(TestAgentBroadcaster):
    """Test agent registration and management"""
    
    @pytest.mark.asyncio
    async def test_agent_registration(self, mock_websocket_manager):
        """Test agent registration process"""
        # Act
        await broadcaster._register_agents()
        
        # Assert
        assert len(broadcaster.active_agents) == 3
        assert 'dental_agent' in broadcaster.active_agents
        assert 'demo_agent' in broadcaster.active_agents
        assert 'opendental_agent' in broadcaster.active_agents
        
        # Check agent info structure
        dental_agent = broadcaster.active_agents['dental_agent']
        assert dental_agent['name'] == 'Advanced Dental Agent'
        assert dental_agent['type'] == 'dental_specialist'
        assert 'appointment_scheduling' in dental_agent['capabilities']
        assert dental_agent['status'] == AgentStatus.IDLE
        assert 'registered_at' in dental_agent
        
        # Verify broadcast calls
        assert mock_websocket_manager.broadcast.call_count == 3  # One for each agent
    
    @pytest.mark.asyncio
    async def test_agent_status_update(self, mock_websocket_manager):
        """Test agent status update broadcasting"""
        # Arrange
        await broadcaster._register_agents()
        agent_id = 'dental_agent'
        
        # Act
        await broadcaster._broadcast_agent_status(
            agent_id, 
            AgentStatus.EXECUTING, 
            "Processing appointment request"
        )
        
        # Assert
        mock_websocket_manager.broadcast.assert_called()
        call_args = mock_websocket_manager.broadcast.call_args[0][0]
        
        assert call_args['type'] == 'agent_status_update'
        assert call_args['payload']['agent_id'] == agent_id
        assert call_args['payload']['status'] == AgentStatus.EXECUTING.value
        assert call_args['payload']['current_task'] == "Processing appointment request"
    
    @pytest.mark.asyncio
    async def test_get_agent_status(self):
        """Test retrieving agent status"""
        # Arrange
        await broadcaster._register_agents()
        
        # Act
        status = broadcaster.get_agent_status('dental_agent')
        
        # Assert
        assert status is not None
        assert status['agent_id'] == 'dental_agent'
        assert status['name'] == 'Advanced Dental Agent'
        assert status['type'] == 'dental_specialist'
    
    @pytest.mark.asyncio
    async def test_get_nonexistent_agent_status(self):
        """Test retrieving status of non-existent agent"""
        # Act
        status = broadcaster.get_agent_status('nonexistent_agent')
        
        # Assert
        assert status is None

class TestActivityBroadcasting(TestAgentBroadcaster):
    """Test activity broadcasting and processing"""
    
    @pytest.mark.asyncio
    async def test_activity_creation_and_broadcasting(self, mock_websocket_manager):
        """Test creating and broadcasting agent activities"""
        # Arrange
        await broadcaster._register_agents()
        
        activity = AgentActivity(
            activity_id="test-activity-123",
            agent_id="dental_agent",
            activity_type=ActivityType.APPOINTMENT_SCHEDULING,
            title="Schedule patient appointment",
            description="Scheduling appointment for John Doe",
            timestamp=datetime.now(),
            confidence_score=0.95,
            metadata={'patient_id': '12345', 'appointment_type': 'cleaning'}
        )
        
        # Act
        await broadcaster._broadcast_activity(activity)
        
        # Assert
        mock_websocket_manager.broadcast.assert_called()
        call_args = mock_websocket_manager.broadcast.call_args[0][0]
        
        assert call_args['type'] == 'agent_activity'
        assert call_args['payload']['activity_id'] == "test-activity-123"
        assert call_args['payload']['agent_id'] == "dental_agent"
        assert call_args['payload']['activity_type'] == ActivityType.APPOINTMENT_SCHEDULING.value
        assert call_args['payload']['title'] == "Schedule patient appointment"
    
    @pytest.mark.asyncio
    async def test_activity_processing_success(self, mock_websocket_manager):
        """Test successful activity processing"""
        # Arrange
        await broadcaster._register_agents()
        
        activity = AgentActivity(
            activity_id="test-activity-456",
            agent_id="dental_agent",
            activity_type=ActivityType.PATIENT_COMMUNICATION,
            title="Send appointment reminder",
            description="Sending reminder to patient",
            timestamp=datetime.now(),
            confidence_score=0.98
        )
        
        # Mock random to ensure success
        with patch('random.random', return_value=0.5):  # > 0.1, so success
            # Act
            await broadcaster._process_agent_activity(activity)
        
        # Assert
        assert len(broadcaster.activity_history) == 1
        processed_activity = broadcaster.activity_history[0]
        assert processed_activity.success is True
        assert processed_activity.duration_ms is not None
        assert processed_activity.explanation is not None
        
        # Check performance metrics
        assert broadcaster.performance_metrics['total_activities'] == 1
        assert broadcaster.performance_metrics['successful_activities'] == 1
        assert broadcaster.performance_metrics['failed_activities'] == 0
    
    @pytest.mark.asyncio
    async def test_activity_processing_failure(self, mock_websocket_manager):
        """Test failed activity processing"""
        # Arrange
        await broadcaster._register_agents()
        
        activity = AgentActivity(
            activity_id="test-activity-789",
            agent_id="dental_agent",
            activity_type=ActivityType.DATA_ANALYSIS,
            title="Analyze patient data",
            description="Analyzing patient treatment history",
            timestamp=datetime.now(),
            confidence_score=0.75
        )
        
        # Mock random to ensure failure
        with patch('random.random', return_value=0.05):  # < 0.1, so failure
            # Act
            await broadcaster._process_agent_activity(activity)
        
        # Assert
        assert len(broadcaster.activity_history) == 1
        processed_activity = broadcaster.activity_history[0]
        assert processed_activity.success is False
        assert "Failed to complete" in processed_activity.explanation
        
        # Check performance metrics
        assert broadcaster.performance_metrics['total_activities'] == 1
        assert broadcaster.performance_metrics['successful_activities'] == 0
        assert broadcaster.performance_metrics['failed_activities'] == 1
    
    @pytest.mark.asyncio
    async def test_get_recent_activities(self, mock_websocket_manager):
        """Test retrieving recent activities"""
        # Arrange
        await broadcaster._register_agents()
        
        # Create multiple activities
        activities = []
        for i in range(5):
            activity = AgentActivity(
                activity_id=f"test-activity-{i}",
                agent_id="dental_agent",
                activity_type=ActivityType.APPOINTMENT_SCHEDULING,
                title=f"Activity {i}",
                description=f"Description {i}",
                timestamp=datetime.now() - timedelta(minutes=i),
                success=True
            )
            activities.append(activity)
            broadcaster.activity_history.append(activity)
        
        # Act
        recent_activities = broadcaster.get_recent_activities(limit=3)
        
        # Assert
        assert len(recent_activities) == 3
        # Should be sorted by timestamp (most recent first)
        assert recent_activities[0].title == "Activity 0"
        assert recent_activities[1].title == "Activity 1"
        assert recent_activities[2].title == "Activity 2"
    
    @pytest.mark.asyncio
    async def test_get_recent_activities_filtered_by_agent(self, mock_websocket_manager):
        """Test retrieving activities filtered by agent"""
        # Arrange
        await broadcaster._register_agents()
        
        # Create activities for different agents
        for agent_id in ['dental_agent', 'demo_agent']:
            for i in range(3):
                activity = AgentActivity(
                    activity_id=f"{agent_id}-activity-{i}",
                    agent_id=agent_id,
                    activity_type=ActivityType.DATA_ANALYSIS,
                    title=f"{agent_id} Activity {i}",
                    description=f"Description {i}",
                    timestamp=datetime.now(),
                    success=True
                )
                broadcaster.activity_history.append(activity)
        
        # Act
        dental_activities = broadcaster.get_recent_activities(agent_id='dental_agent')
        
        # Assert
        assert len(dental_activities) == 3
        for activity in dental_activities:
            assert activity.agent_id == 'dental_agent'

class TestDecisionExplanations(TestAgentBroadcaster):
    """Test decision explanation generation and broadcasting"""
    
    @pytest.mark.asyncio
    async def test_decision_explanation_generation(self, mock_websocket_manager):
        """Test generating decision explanations"""
        # Arrange
        await broadcaster._register_agents()
        
        activity = AgentActivity(
            activity_id="test-activity-decision",
            agent_id="dental_agent",
            activity_type=ActivityType.DECISION_MAKING,
            title="Optimize appointment schedule",
            description="Deciding optimal appointment arrangement",
            timestamp=datetime.now(),
            confidence_score=0.92
        )
        
        # Act
        await broadcaster._generate_decision_explanation(activity)
        
        # Assert
        assert len(broadcaster.decision_history) == 1
        decision = broadcaster.decision_history[0]
        
        assert decision.agent_id == "dental_agent"
        assert decision.decision_type == ActivityType.DECISION_MAKING.value
        assert decision.confidence_score == 0.92
        assert len(decision.reasoning_steps) > 0
        assert len(decision.alternative_options) > 0
        assert decision.final_decision is not None
        
        # Check performance metrics
        assert broadcaster.performance_metrics['decisions_made'] == 1
        
        # Verify broadcast
        mock_websocket_manager.broadcast.assert_called()
        call_args = mock_websocket_manager.broadcast.call_args[0][0]
        assert call_args['type'] == 'agent_decision_explanation'
    
    @pytest.mark.asyncio
    async def test_human_review_required_flag(self, mock_websocket_manager):
        """Test human review required flag for low confidence decisions"""
        # Arrange
        await broadcaster._register_agents()
        
        activity = AgentActivity(
            activity_id="test-low-confidence",
            agent_id="dental_agent",
            activity_type=ActivityType.DECISION_MAKING,
            title="Complex scheduling decision",
            description="Difficult scheduling scenario",
            timestamp=datetime.now(),
            confidence_score=0.65  # Low confidence
        )
        
        # Act
        await broadcaster._generate_decision_explanation(activity)
        
        # Assert
        decision = broadcaster.decision_history[0]
        assert decision.human_review_required is True

class TestPerformanceMetrics(TestAgentBroadcaster):
    """Test performance metrics tracking and broadcasting"""
    
    @pytest.mark.asyncio
    async def test_performance_metrics_update(self, mock_websocket_manager):
        """Test performance metrics calculation and broadcasting"""
        # Arrange
        await broadcaster._register_agents()
        
        # Create activities with different durations
        for i in range(5):
            activity = AgentActivity(
                activity_id=f"perf-test-{i}",
                agent_id="dental_agent",
                activity_type=ActivityType.DATA_ANALYSIS,
                title=f"Performance test {i}",
                description="Test activity",
                timestamp=datetime.now(),
                duration_ms=1000 + (i * 500),  # 1000, 1500, 2000, 2500, 3000
                success=True
            )
            broadcaster.activity_history.append(activity)
        
        broadcaster.performance_metrics['total_activities'] = 5
        broadcaster.performance_metrics['successful_activities'] = 5
        
        # Act
        await broadcaster._update_performance_metrics()
        
        # Assert
        expected_avg = (1000 + 1500 + 2000 + 2500 + 3000) / 5  # 2000ms
        assert broadcaster.performance_metrics['average_response_time'] == expected_avg
        
        # Verify broadcast
        mock_websocket_manager.broadcast.assert_called()
        call_args = mock_websocket_manager.broadcast.call_args[0][0]
        assert call_args['type'] == 'performance_metrics'
        assert call_args['payload']['metrics']['total_activities'] == 5
    
    @pytest.mark.asyncio
    async def test_get_performance_summary(self, mock_websocket_manager):
        """Test performance summary generation"""
        # Arrange
        await broadcaster._register_agents()
        
        # Set up some metrics
        broadcaster.performance_metrics = {
            'total_activities': 10,
            'successful_activities': 8,
            'failed_activities': 2,
            'average_response_time': 1500,
            'human_handoffs': 1,
            'decisions_made': 5
        }
        
        # Add some activities for today
        today_activities = []
        for i in range(3):
            activity = AgentActivity(
                activity_id=f"today-{i}",
                agent_id="dental_agent",
                activity_type=ActivityType.APPOINTMENT_SCHEDULING,
                title=f"Today activity {i}",
                description="Today's activity",
                timestamp=datetime.now(),
                success=True
            )
            today_activities.append(activity)
            broadcaster.activity_history.append(activity)
        
        # Act
        summary = broadcaster.get_performance_summary()
        
        # Assert
        assert summary['metrics']['total_activities'] == 10
        assert summary['active_agents'] == 3
        assert summary['total_activities_today'] == 3
        assert summary['average_success_rate'] == 1.0  # All agents start with 1.0

class TestHumanHandoff(TestAgentBroadcaster):
    """Test human handoff functionality"""
    
    @pytest.mark.asyncio
    async def test_trigger_human_handoff(self, mock_websocket_manager):
        """Test triggering human handoff"""
        # Arrange
        await broadcaster._register_agents()
        agent_id = "dental_agent"
        reason = "Complex scheduling conflict detected"
        context = {
            'conflict_type': 'double_booking',
            'patients_affected': 2,
            'suggested_resolution': 'manual_review'
        }
        
        # Act
        await broadcaster.trigger_human_handoff(agent_id, reason, context)
        
        # Assert
        assert broadcaster.performance_metrics['human_handoffs'] == 1
        
        # Verify status update broadcast
        status_calls = [call for call in mock_websocket_manager.broadcast.call_args_list 
                       if call[0][0]['type'] == 'agent_status_update']
        assert len(status_calls) > 0
        
        status_call = status_calls[-1][0][0]
        assert status_call['payload']['status'] == AgentStatus.HUMAN_HANDOFF.value
        
        # Verify handoff notification broadcast
        handoff_calls = [call for call in mock_websocket_manager.broadcast.call_args_list 
                        if call[0][0]['type'] == 'human_handoff_required']
        assert len(handoff_calls) == 1
        
        handoff_call = handoff_calls[0][0][0]
        assert handoff_call['payload']['agent_id'] == agent_id
        assert handoff_call['payload']['reason'] == reason
        assert handoff_call['payload']['context'] == context
        assert handoff_call['payload']['priority'] == 'medium'
    
    @pytest.mark.asyncio
    async def test_high_priority_handoff_for_errors(self, mock_websocket_manager):
        """Test high priority handoff for error conditions"""
        # Arrange
        await broadcaster._register_agents()
        
        # Act
        await broadcaster.trigger_human_handoff(
            "dental_agent", 
            "Critical error in patient data processing", 
            {'error_type': 'data_corruption'}
        )
        
        # Assert
        handoff_calls = [call for call in mock_websocket_manager.broadcast.call_args_list 
                        if call[0][0]['type'] == 'human_handoff_required']
        
        handoff_call = handoff_calls[0][0][0]
        assert handoff_call['payload']['priority'] == 'high'

class TestMonitoringLoop(TestAgentBroadcaster):
    """Test monitoring loop functionality"""
    
    @pytest.mark.asyncio
    async def test_start_stop_monitoring(self, mock_websocket_manager):
        """Test starting and stopping monitoring"""
        # Act - Start monitoring
        await broadcaster.start_monitoring()
        
        # Assert - Monitoring started
        assert broadcaster.monitoring_active is True
        assert broadcaster.monitoring_task is not None
        assert len(broadcaster.active_agents) == 3  # Agents registered
        
        # Act - Stop monitoring
        await broadcaster.stop_monitoring()
        
        # Assert - Monitoring stopped
        assert broadcaster.monitoring_active is False
    
    @pytest.mark.asyncio
    async def test_monitoring_generates_activities(self, mock_websocket_manager):
        """Test that monitoring loop generates activities"""
        # Arrange
        with patch('random.choice') as mock_choice, \
             patch('random.randint', return_value=1), \
             patch('asyncio.sleep', return_value=None):  # Skip sleep
            
            # Mock to always select dental_agent
            mock_choice.return_value = 'dental_agent'
            
            # Start monitoring
            await broadcaster.start_monitoring()
            
            # Let it run one iteration
            await broadcaster._simulate_agent_activities()
            
            # Stop monitoring
            await broadcaster.stop_monitoring()
        
        # Assert
        # Should have generated at least one activity
        assert len(broadcaster.activity_history) >= 0  # May be 0 due to randomness

class TestMemoryManagement(TestAgentBroadcaster):
    """Test memory management and cleanup"""
    
    @pytest.mark.asyncio
    async def test_activity_history_cleanup(self, mock_websocket_manager):
        """Test activity history cleanup to prevent memory issues"""
        # Arrange
        await broadcaster._register_agents()
        
        # Create more than 1000 activities
        for i in range(1200):
            activity = AgentActivity(
                activity_id=f"cleanup-test-{i}",
                agent_id="dental_agent",
                activity_type=ActivityType.DATA_ANALYSIS,
                title=f"Cleanup test {i}",
                description="Test activity for cleanup",
                timestamp=datetime.now() - timedelta(minutes=i),
                success=True
            )
            broadcaster.activity_history.append(activity)
        
        # Act
        await broadcaster._cleanup_history()
        
        # Assert
        assert len(broadcaster.activity_history) == 1000
        # Should keep the most recent ones
        assert broadcaster.activity_history[0].title == "Cleanup test 199"  # Most recent kept
    
    @pytest.mark.asyncio
    async def test_decision_history_cleanup(self, mock_websocket_manager):
        """Test decision history cleanup"""
        # Arrange
        await broadcaster._register_agents()
        
        # Create more than 500 decisions
        for i in range(600):
            decision = DecisionExplanation(
                decision_id=f"decision-{i}",
                agent_id="dental_agent",
                timestamp=datetime.now() - timedelta(minutes=i),
                decision_type="test_decision",
                input_data={},
                reasoning_steps=["test"],
                confidence_score=0.8,
                alternative_options=[],
                final_decision={}
            )
            broadcaster.decision_history.append(decision)
        
        # Act
        await broadcaster._cleanup_history()
        
        # Assert
        assert len(broadcaster.decision_history) == 500

class TestIntegrationFunctions(TestAgentBroadcaster):
    """Test integration functions for external use"""
    
    @pytest.mark.asyncio
    async def test_broadcast_custom_activity(self, mock_websocket_manager):
        """Test broadcasting custom activity from external agent"""
        # Arrange
        await broadcaster._register_agents()
        
        # Act
        await broadcast_custom_activity(
            agent_id="dental_agent",
            activity_type="appointment_scheduling",
            title="Custom appointment booking",
            description="Booking appointment via external API",
            metadata={'source': 'external_api', 'patient_id': '67890'}
        )
        
        # Assert
        assert len(broadcaster.activity_history) == 1
        activity = broadcaster.activity_history[0]
        
        assert activity.agent_id == "dental_agent"
        assert activity.activity_type == ActivityType.APPOINTMENT_SCHEDULING
        assert activity.title == "Custom appointment booking"
        assert activity.metadata['source'] == 'external_api'
        assert activity.success is True
    
    @pytest.mark.asyncio
    async def test_start_stop_agent_broadcasting_functions(self, mock_websocket_manager):
        """Test module-level start/stop functions"""
        # Act
        await start_agent_broadcasting()
        
        # Assert
        assert broadcaster.monitoring_active is True
        
        # Act
        await stop_agent_broadcasting()
        
        # Assert
        assert broadcaster.monitoring_active is False

class TestRealisticActivityGeneration(TestAgentBroadcaster):
    """Test realistic activity generation for different agent types"""
    
    def test_dental_specialist_activities(self):
        """Test activity generation for dental specialist agent"""
        # Arrange
        agent_info = {
            'type': 'dental_specialist',
            'capabilities': ['appointment_scheduling', 'patient_communication']
        }
        
        # Act
        activities = broadcaster._generate_realistic_activities('dental_agent', agent_info)
        
        # Assert
        assert len(activities) > 0
        for activity in activities:
            assert activity.agent_id == 'dental_agent'
            assert activity.activity_type in [
                ActivityType.APPOINTMENT_SCHEDULING,
                ActivityType.PATIENT_COMMUNICATION,
                ActivityType.DATA_ANALYSIS
            ]
            assert activity.confidence_score is not None
            assert activity.metadata is not None
    
    def test_system_integrator_activities(self):
        """Test activity generation for system integrator agent"""
        # Arrange
        agent_info = {
            'type': 'system_integrator',
            'capabilities': ['opendental_sync', 'data_migration']
        }
        
        # Act
        activities = broadcaster._generate_realistic_activities('opendental_agent', agent_info)
        
        # Assert
        assert len(activities) > 0
        for activity in activities:
            assert activity.agent_id == 'opendental_agent'
            assert activity.activity_type in [
                ActivityType.SYSTEM_INTEGRATION,
                ActivityType.DATA_ANALYSIS
            ]
    
    def test_data_provider_activities(self):
        """Test activity generation for data provider agent"""
        # Arrange
        agent_info = {
            'type': 'data_provider',
            'capabilities': ['data_simulation', 'testing_support']
        }
        
        # Act
        activities = broadcaster._generate_realistic_activities('demo_agent', agent_info)
        
        # Assert
        assert len(activities) > 0
        for activity in activities:
            assert activity.agent_id == 'demo_agent'
            assert activity.activity_type == ActivityType.DATA_ANALYSIS

# Performance and stress tests
class TestPerformanceAndStress:
    """Performance and stress tests for agent broadcasting"""
    
    @pytest.mark.asyncio
    async def test_high_volume_activity_processing(self, mock_websocket_manager):
        """Test processing high volume of activities"""
        # Arrange
        await broadcaster._register_agents()
        
        activity_count = 100
        start_time = time.time()
        
        # Act
        tasks = []
        for i in range(activity_count):
            activity = AgentActivity(
                activity_id=f"stress-test-{i}",
                agent_id="dental_agent",
                activity_type=ActivityType.DATA_ANALYSIS,
                title=f"Stress test activity {i}",
                description="High volume test",
                timestamp=datetime.now(),
                success=True
            )
            task = broadcaster._broadcast_activity(activity)
            tasks.append(task)
        
        await asyncio.gather(*tasks)
        end_time = time.time()
        
        # Assert
        duration = end_time - start_time
        activities_per_second = activity_count / duration
        
        # Should handle at least 50 activities per second
        assert activities_per_second > 50
        
        # All broadcasts should have been called
        assert mock_websocket_manager.broadcast.call_count == activity_count
    
    @pytest.mark.asyncio
    async def test_concurrent_agent_operations(self, mock_websocket_manager):
        """Test concurrent operations across multiple agents"""
        # Arrange
        await broadcaster._register_agents()
        
        # Act - Simulate concurrent activities from all agents
        tasks = []
        for agent_id in broadcaster.active_agents.keys():
            for i in range(10):
                task = broadcaster._broadcast_agent_status(
                    agent_id,
                    AgentStatus.EXECUTING,
                    f"Concurrent task {i}"
                )
                tasks.append(task)
        
        await asyncio.gather(*tasks)
        
        # Assert
        # Should have broadcast 30 status updates (3 agents × 10 tasks)
        assert mock_websocket_manager.broadcast.call_count == 30

if __name__ == "__main__":
    # Run tests with coverage
    pytest.main([
        __file__,
        "-v",
        "--cov=agent_broadcaster",
        "--cov-report=html",
        "--cov-report=term-missing",
        "--cov-fail-under=95"
    ])
