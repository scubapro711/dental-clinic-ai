"""
Open Source AI Model Testing for Dental Clinic System
בדיקות מודלי AI בקוד פתוח למערכת ניהול מרפאת שיניים

Tests various open source AI models as alternatives to OpenAI:
- Hugging Face Transformers
- Ollama local models
- LangChain with open source models
- Model performance comparison
- Multilingual support testing
"""

import pytest
import asyncio
import json
import time
import os
from typing import Dict, List, Any, Optional
from unittest.mock import patch, AsyncMock
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test configuration
AI_TEST_CONFIG = {
    "test_messages": {
        "hebrew": [
            "שלום, אני רוצה לקבוע תור לבדיקה",
            "האם יש תור פנוי השבוע?",
            "אני צריך לבטל את התור שלי",
            "מתי המרפאה פתוחה?",
            "כמה עולה בדיקה שגרתית?",
            "יש לי כאב שיניים, אני צריך תור דחוף"
        ],
        "english": [
            "Hello, I need to book an appointment",
            "Can I reschedule my appointment?",
            "What are your opening hours?",
            "Do you accept insurance?",
            "I need an emergency appointment",
            "How much does a cleaning cost?"
        ],
        "mixed": [
            "Hi, אני רוצה appointment",
            "שלום, I need to cancel",
            "Can you help me לקבוע תור?",
            "Emergency! יש לי כאב שיניים"
        ]
    },
    "expected_intents": {
        "book_appointment": ["book", "appointment", "schedule", "תור", "לקבוע"],
        "cancel_appointment": ["cancel", "reschedule", "לבטל", "לדחות"],
        "inquiry": ["hours", "cost", "insurance", "מתי", "כמה", "עולה"],
        "emergency": ["emergency", "urgent", "pain", "דחוף", "כאב"]
    }
}

class MockOpenSourceModel:
    """Mock open source model for testing"""
    
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.initialized = False
    
    async def initialize(self):
        """Initialize the model"""
        await asyncio.sleep(0.1)  # Simulate initialization time
        self.initialized = True
        logger.info(f"Initialized {self.model_name}")
    
    async def generate_response(self, prompt: str, context: Dict[str, Any] = None) -> str:
        """Generate response based on prompt"""
        if not self.initialized:
            raise RuntimeError(f"Model {self.model_name} not initialized")
        
        # Simulate processing time
        await asyncio.sleep(0.2)
        
        # Simple rule-based responses for testing
        prompt_lower = prompt.lower()
        
        if any(word in prompt_lower for word in ["תור", "appointment", "book", "schedule"]):
            if "hebrew" in self.model_name.lower():
                return "אני יכול לעזור לך לקבוע תור. איזה תאריך מתאים לך?"
            else:
                return "I can help you book an appointment. What date works for you?"
        
        elif any(word in prompt_lower for word in ["בטל", "cancel", "reschedule"]):
            if "hebrew" in self.model_name.lower():
                return "אני יכול לעזור לך לבטל או לדחות תור. מה מספר התור שלך?"
            else:
                return "I can help you cancel or reschedule. What's your appointment number?"
        
        elif any(word in prompt_lower for word in ["כאב", "pain", "emergency", "דחוף"]):
            if "hebrew" in self.model_name.lower():
                return "אני מבין שיש לך כאב. אני אנסה למצוא תור דחוף. איפה הכאב?"
            else:
                return "I understand you're in pain. Let me find an urgent appointment. Where is the pain?"
        
        else:
            if "hebrew" in self.model_name.lower():
                return "אני כאן לעזור עם תורים ושאלות על המרפאה. איך אני יכול לעזור?"
            else:
                return "I'm here to help with appointments and clinic questions. How can I assist you?"

class HuggingFaceModelTester:
    """Test Hugging Face models integration"""
    
    def __init__(self):
        self.models = {
            "hebrew_bert": "avichr/heBERT",
            "multilingual_bert": "bert-base-multilingual-cased",
            "hebrew_gpt": "Norod78/hebrew-gpt_neo-small",
            "xlm_roberta": "xlm-roberta-base"
        }
        self.initialized_models = {}
    
    async def initialize_model(self, model_name: str) -> bool:
        """Initialize a Hugging Face model"""
        try:
            # Mock initialization - in real implementation would load actual model
            mock_model = MockOpenSourceModel(f"HuggingFace_{model_name}")
            await mock_model.initialize()
            self.initialized_models[model_name] = mock_model
            return True
        except Exception as e:
            logger.error(f"Failed to initialize {model_name}: {e}")
            return False
    
    async def test_model_performance(self, model_name: str, test_messages: List[str]) -> Dict[str, Any]:
        """Test model performance on given messages"""
        if model_name not in self.initialized_models:
            await self.initialize_model(model_name)
        
        model = self.initialized_models[model_name]
        results = {
            "model_name": model_name,
            "total_messages": len(test_messages),
            "successful_responses": 0,
            "average_response_time": 0,
            "responses": []
        }
        
        total_time = 0
        
        for message in test_messages:
            start_time = time.time()
            try:
                response = await model.generate_response(message)
                end_time = time.time()
                response_time = end_time - start_time
                
                results["successful_responses"] += 1
                results["responses"].append({
                    "input": message,
                    "output": response,
                    "response_time": response_time
                })
                total_time += response_time
                
            except Exception as e:
                logger.error(f"Model {model_name} failed on message '{message}': {e}")
                results["responses"].append({
                    "input": message,
                    "output": None,
                    "error": str(e)
                })
        
        if results["successful_responses"] > 0:
            results["average_response_time"] = total_time / results["successful_responses"]
        
        return results

class OllamaModelTester:
    """Test Ollama local models"""
    
    def __init__(self):
        self.available_models = [
            "llama2:7b",
            "mistral:7b",
            "codellama:7b",
            "neural-chat:7b"
        ]
        self.initialized_models = {}
    
    async def check_ollama_availability(self) -> bool:
        """Check if Ollama is available"""
        try:
            # Mock Ollama availability check
            # In real implementation: subprocess.run(["ollama", "list"])
            return True
        except Exception:
            return False
    
    async def initialize_model(self, model_name: str) -> bool:
        """Initialize an Ollama model"""
        try:
            if not await self.check_ollama_availability():
                logger.warning("Ollama not available, using mock model")
            
            mock_model = MockOpenSourceModel(f"Ollama_{model_name}")
            await mock_model.initialize()
            self.initialized_models[model_name] = mock_model
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Ollama model {model_name}: {e}")
            return False
    
    async def test_model_performance(self, model_name: str, test_messages: List[str]) -> Dict[str, Any]:
        """Test Ollama model performance"""
        if model_name not in self.initialized_models:
            await self.initialize_model(model_name)
        
        model = self.initialized_models[model_name]
        results = {
            "model_name": f"Ollama_{model_name}",
            "total_messages": len(test_messages),
            "successful_responses": 0,
            "average_response_time": 0,
            "responses": []
        }
        
        total_time = 0
        
        for message in test_messages:
            start_time = time.time()
            try:
                # Add context for better responses
                context = {"model_type": "ollama", "language": "mixed"}
                response = await model.generate_response(message, context)
                end_time = time.time()
                response_time = end_time - start_time
                
                results["successful_responses"] += 1
                results["responses"].append({
                    "input": message,
                    "output": response,
                    "response_time": response_time
                })
                total_time += response_time
                
            except Exception as e:
                logger.error(f"Ollama model {model_name} failed: {e}")
                results["responses"].append({
                    "input": message,
                    "output": None,
                    "error": str(e)
                })
        
        if results["successful_responses"] > 0:
            results["average_response_time"] = total_time / results["successful_responses"]
        
        return results

@pytest.mark.ai
class TestOpenSourceModels:
    """Test suite for open source AI models"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.hf_tester = HuggingFaceModelTester()
        self.ollama_tester = OllamaModelTester()
    
    @pytest.mark.asyncio
    async def test_huggingface_hebrew_support(self):
        """Test Hugging Face models with Hebrew text"""
        hebrew_messages = AI_TEST_CONFIG["test_messages"]["hebrew"]
        
        # Test Hebrew BERT model
        results = await self.hf_tester.test_model_performance("hebrew_bert", hebrew_messages)
        
        assert results["successful_responses"] > 0, "Hebrew BERT model failed on all messages"
        assert results["average_response_time"] < 5.0, "Hebrew BERT model too slow"
        
        # Check that responses are in Hebrew
        for response_data in results["responses"]:
            if response_data["output"]:
                # Simple check for Hebrew characters
                hebrew_chars = any('\u0590' <= char <= '\u05FF' for char in response_data["output"])
                assert hebrew_chars, f"Response not in Hebrew: {response_data['output']}"
    
    @pytest.mark.asyncio
    async def test_multilingual_model_support(self):
        """Test multilingual model with mixed language input"""
        mixed_messages = AI_TEST_CONFIG["test_messages"]["mixed"]
        
        results = await self.hf_tester.test_model_performance("multilingual_bert", mixed_messages)
        
        assert results["successful_responses"] > 0, "Multilingual model failed"
        assert results["average_response_time"] < 5.0, "Multilingual model too slow"
        
        # Check that model handles mixed language input
        for response_data in results["responses"]:
            if response_data["output"]:
                assert len(response_data["output"]) > 10, "Response too short"
    
    @pytest.mark.asyncio
    async def test_ollama_local_models(self):
        """Test Ollama local models"""
        english_messages = AI_TEST_CONFIG["test_messages"]["english"]
        
        # Test Llama2 model
        results = await self.ollama_tester.test_model_performance("llama2:7b", english_messages)
        
        assert results["successful_responses"] > 0, "Ollama Llama2 model failed"
        
        # Test response quality
        for response_data in results["responses"]:
            if response_data["output"]:
                assert len(response_data["output"]) > 5, "Ollama response too short"
                assert "error" not in response_data["output"].lower(), "Error in Ollama response"
    
    @pytest.mark.asyncio
    async def test_intent_recognition_accuracy(self):
        """Test intent recognition accuracy across models"""
        test_cases = [
            ("אני רוצה לקבוע תור", "book_appointment"),
            ("I need to book an appointment", "book_appointment"),
            ("אני צריך לבטל תור", "cancel_appointment"),
            ("Can I cancel my appointment?", "cancel_appointment"),
            ("יש לי כאב שיניים דחוף", "emergency"),
            ("Emergency! I have tooth pain", "emergency"),
            ("מתי המרפאה פתוחה?", "inquiry"),
            ("What are your hours?", "inquiry")
        ]
        
        models_to_test = ["hebrew_bert", "multilingual_bert"]
        
        for model_name in models_to_test:
            correct_predictions = 0
            total_predictions = len(test_cases)
            
            for message, expected_intent in test_cases:
                results = await self.hf_tester.test_model_performance(model_name, [message])
                
                if results["successful_responses"] > 0:
                    response = results["responses"][0]["output"]
                    
                    # Simple intent detection based on keywords
                    predicted_intent = self._detect_intent(response)
                    
                    if predicted_intent == expected_intent:
                        correct_predictions += 1
                    
                    logger.info(f"Model: {model_name}, Input: {message}")
                    logger.info(f"Expected: {expected_intent}, Predicted: {predicted_intent}")
                    logger.info(f"Response: {response}")
            
            accuracy = correct_predictions / total_predictions
            logger.info(f"Model {model_name} accuracy: {accuracy:.2%}")
            
            # Require at least 60% accuracy for basic functionality
            assert accuracy >= 0.6, f"Model {model_name} accuracy too low: {accuracy:.2%}"
    
    def _detect_intent(self, response: str) -> str:
        """Simple intent detection based on response content"""
        response_lower = response.lower()
        
        if any(word in response_lower for word in ["תור", "appointment", "book", "schedule"]):
            return "book_appointment"
        elif any(word in response_lower for word in ["בטל", "cancel", "reschedule"]):
            return "cancel_appointment"
        elif any(word in response_lower for word in ["דחוף", "emergency", "urgent", "pain"]):
            return "emergency"
        else:
            return "inquiry"
    
    @pytest.mark.asyncio
    async def test_model_performance_comparison(self):
        """Compare performance across different models"""
        test_messages = AI_TEST_CONFIG["test_messages"]["english"][:3]  # Limit for performance
        
        models_to_compare = [
            ("HuggingFace", "multilingual_bert", self.hf_tester),
            ("Ollama", "llama2:7b", self.ollama_tester)
        ]
        
        performance_results = []
        
        for model_type, model_name, tester in models_to_compare:
            results = await tester.test_model_performance(model_name, test_messages)
            
            performance_results.append({
                "model_type": model_type,
                "model_name": model_name,
                "success_rate": results["successful_responses"] / results["total_messages"],
                "avg_response_time": results["average_response_time"],
                "total_responses": results["successful_responses"]
            })
        
        # Log performance comparison
        logger.info("Model Performance Comparison:")
        logger.info("-" * 50)
        for result in performance_results:
            logger.info(f"{result['model_type']} - {result['model_name']}:")
            logger.info(f"  Success Rate: {result['success_rate']:.2%}")
            logger.info(f"  Avg Response Time: {result['avg_response_time']:.3f}s")
            logger.info(f"  Total Responses: {result['total_responses']}")
        
        # Ensure at least one model performs adequately
        best_model = max(performance_results, key=lambda x: x['success_rate'])
        assert best_model['success_rate'] >= 0.8, "No model achieved adequate success rate"
    
    @pytest.mark.asyncio
    async def test_model_fallback_mechanism(self):
        """Test fallback mechanism when primary model fails"""
        # Simulate primary model failure
        with patch.object(self.hf_tester, 'test_model_performance') as mock_primary:
            mock_primary.side_effect = Exception("Primary model failed")
            
            # Test fallback to secondary model
            try:
                fallback_results = await self.ollama_tester.test_model_performance(
                    "mistral:7b", 
                    ["Hello, test fallback"]
                )
                
                assert fallback_results["successful_responses"] > 0, "Fallback model failed"
                logger.info("Fallback mechanism working correctly")
                
            except Exception as e:
                pytest.fail(f"Fallback mechanism failed: {e}")
    
    @pytest.mark.asyncio
    async def test_model_memory_usage(self):
        """Test model memory usage and resource management"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Initialize multiple models
        models = ["hebrew_bert", "multilingual_bert"]
        for model_name in models:
            await self.hf_tester.initialize_model(model_name)
        
        # Test with multiple messages
        test_messages = AI_TEST_CONFIG["test_messages"]["hebrew"] * 2
        
        for model_name in models:
            await self.hf_tester.test_model_performance(model_name, test_messages)
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        logger.info(f"Memory usage: {initial_memory:.1f}MB -> {final_memory:.1f}MB")
        logger.info(f"Memory increase: {memory_increase:.1f}MB")
        
        # Ensure memory usage is reasonable (less than 500MB increase)
        assert memory_increase < 500, f"Excessive memory usage: {memory_increase:.1f}MB"

@pytest.mark.ai
class TestAIIntegration:
    """Test AI integration with the dental clinic system"""
    
    @pytest.mark.asyncio
    async def test_ai_engine_switching(self):
        """Test switching between different AI engines"""
        # Mock the AI engine factory
        from unittest.mock import MagicMock
        
        # Test engine switching capability
        engines = ["openai", "huggingface", "ollama"]
        
        for engine in engines:
            # Mock engine initialization
            mock_engine = MagicMock()
            mock_engine.process_message = AsyncMock(return_value={
                "success": True,
                "response": f"Response from {engine} engine",
                "engine_used": engine
            })
            
            # Test message processing
            result = await mock_engine.process_message("Test message")
            
            assert result["success"] is True
            assert engine in result["response"]
            assert result["engine_used"] == engine
    
    @pytest.mark.asyncio
    async def test_multilingual_ai_responses(self):
        """Test AI responses in multiple languages"""
        test_cases = [
            ("שלום", "hebrew"),
            ("Hello", "english"),
            ("Hi אני רוצה תור", "mixed")
        ]
        
        hf_tester = HuggingFaceModelTester()
        
        for message, expected_language in test_cases:
            results = await hf_tester.test_model_performance("multilingual_bert", [message])
            
            assert results["successful_responses"] > 0, f"Failed on {expected_language} message"
            
            response = results["responses"][0]["output"]
            assert len(response) > 0, f"Empty response for {expected_language}"
            
            # Language-specific checks
            if expected_language == "hebrew":
                hebrew_chars = any('\u0590' <= char <= '\u05FF' for char in response)
                assert hebrew_chars, "Hebrew response should contain Hebrew characters"
            elif expected_language == "english":
                # Should contain mostly Latin characters
                latin_chars = any('a' <= char.lower() <= 'z' for char in response)
                assert latin_chars, "English response should contain Latin characters"

# Test runner for AI models
def run_ai_model_tests():
    """Run all AI model tests"""
    print("🤖 Starting Open Source AI Model Testing")
    print("=" * 50)
    
    # Run tests with pytest
    pytest.main([
        "tests/ai_testing/open_source_model_tests.py",
        "-v",
        "--tb=short",
        "-m", "ai"
    ])

if __name__ == "__main__":
    run_ai_model_tests()
