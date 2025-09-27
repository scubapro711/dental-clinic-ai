#!/usr/bin/env python3
"""
🔧 Demo: Modular Upgrade Capabilities
הדגמה מעשית של יכולות שדרוג מודולריות

This script demonstrates how our modular architecture handles:
1. Module version checking
2. Graceful fallbacks
3. Hot-swapping providers
4. Dependency management
"""

import sys
import os
import importlib
import logging
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class I18nProvider(ABC):
    """Abstract base class for i18n providers"""
    
    @abstractmethod
    def get_message(self, key: str, lang: str, **kwargs) -> str:
        pass
    
    @abstractmethod
    def detect_language(self, text: str) -> str:
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        pass

class DictionaryI18nProvider(I18nProvider):
    """Built-in dictionary provider - always works!"""
    
    def __init__(self):
        self.translations = {
            'he': {
                'welcome': 'ברוכים הבאים למרפאת השיניים',
                'patient_found': 'נמצא מטופל: {name}, גיל {age}',
                'system_error': 'אירעה שגיאה במערכת: {error}'
            },
            'en': {
                'welcome': 'Welcome to the dental clinic',
                'patient_found': 'Patient found: {name}, age {age}',
                'system_error': 'System error occurred: {error}'
            }
        }
    
    def get_message(self, key: str, lang: str, **kwargs) -> str:
        try:
            message = self.translations.get(lang, self.translations['he']).get(key, key)
            return message.format(**kwargs) if kwargs else message
        except Exception as e:
            return f"{key} (error: {e})"
    
    def detect_language(self, text: str) -> str:
        if any('\u0590' <= char <= '\u05FF' for char in text):
            return 'he'
        elif any(char.isascii() and char.isalpha() for char in text):
            return 'en'
        return 'he'
    
    def test_connection(self) -> bool:
        return True

class ExternalI18nProvider(I18nProvider):
    """External library provider with fallback"""
    
    def __init__(self):
        self.fallback = DictionaryI18nProvider()
        self.external_available = self._check_external_lib()
    
    def _check_external_lib(self) -> bool:
        try:
            import langdetect
            return True
        except ImportError:
            logger.warning("langdetect not available, using fallback")
            return False
    
    def get_message(self, key: str, lang: str, **kwargs) -> str:
        # Always use our dictionary for messages
        return self.fallback.get_message(key, lang, **kwargs)
    
    def detect_language(self, text: str) -> str:
        if self.external_available:
            try:
                from langdetect import detect
                detected = detect(text)
                # Map langdetect codes to our codes
                mapping = {'he': 'he', 'en': 'en', 'iw': 'he'}
                return mapping.get(detected, 'he')
            except Exception as e:
                logger.warning(f"External detection failed: {e}, using fallback")
        
        return self.fallback.detect_language(text)
    
    def test_connection(self) -> bool:
        return True  # Always works due to fallback

class ModuleManager:
    """Manage module loading and fallbacks"""
    
    def __init__(self):
        self.providers = {}
        self.active_providers = {}
        self.health_status = {}
    
    def register_provider(self, service: str, provider_class, priority: int = 0):
        """Register a service provider with priority"""
        if service not in self.providers:
            self.providers[service] = []
        
        self.providers[service].append({
            'class': provider_class,
            'priority': priority,
            'name': provider_class.__name__
        })
        
        # Sort by priority (higher = better)
        self.providers[service].sort(key=lambda x: x['priority'], reverse=True)
        logger.info(f"Registered {provider_class.__name__} for {service} with priority {priority}")
    
    def get_provider(self, service: str):
        """Get the best available provider for a service"""
        if service in self.active_providers:
            # Check if current provider is still healthy
            if self._check_provider_health(service):
                return self.active_providers[service]
        
        # Find new provider
        if service not in self.providers:
            raise ValueError(f"No providers registered for {service}")
        
        for provider_info in self.providers[service]:
            try:
                provider = provider_info['class']()
                if provider.test_connection():
                    self.active_providers[service] = provider
                    self.health_status[service] = {
                        'provider': provider_info['name'],
                        'status': 'healthy',
                        'priority': provider_info['priority']
                    }
                    logger.info(f"Activated {provider_info['name']} for {service}")
                    return provider
            except Exception as e:
                logger.warning(f"Provider {provider_info['name']} failed: {e}")
                continue
        
        raise RuntimeError(f"No working providers available for {service}")
    
    def _check_provider_health(self, service: str) -> bool:
        """Check if current provider is healthy"""
        try:
            provider = self.active_providers[service]
            return provider.test_connection()
        except:
            return False
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of all services"""
        return self.health_status.copy()
    
    def force_provider_switch(self, service: str, provider_name: str):
        """Force switch to specific provider"""
        if service not in self.providers:
            raise ValueError(f"Service {service} not found")
        
        for provider_info in self.providers[service]:
            if provider_info['name'] == provider_name:
                try:
                    provider = provider_info['class']()
                    if provider.test_connection():
                        old_provider = self.health_status.get(service, {}).get('provider', 'none')
                        self.active_providers[service] = provider
                        self.health_status[service] = {
                            'provider': provider_name,
                            'status': 'healthy',
                            'priority': provider_info['priority']
                        }
                        logger.info(f"Switched {service} from {old_provider} to {provider_name}")
                        return True
                except Exception as e:
                    logger.error(f"Failed to switch to {provider_name}: {e}")
                    return False
        
        raise ValueError(f"Provider {provider_name} not found for service {service}")

def demo_dependency_checking():
    """Demonstrate dependency checking capabilities"""
    print("\n🔍 === Dependency Checking Demo ===")
    
    dependencies = {
        'langdetect': {'required': False, 'purpose': 'Advanced language detection'},
        'pymysql': {'required': True, 'purpose': 'Database connectivity'},
        'flask': {'required': True, 'purpose': 'Web framework'},
        'nonexistent_lib': {'required': False, 'purpose': 'Demo missing library'},
    }
    
    print("Checking dependencies...")
    for lib, config in dependencies.items():
        try:
            module = importlib.import_module(lib)
            version = getattr(module, '__version__', 'unknown')
            status = "✅ Available"
            print(f"  {lib}: {status} (v{version}) - {config['purpose']}")
        except ImportError:
            status = "❌ Missing" if config['required'] else "⚠️  Optional"
            print(f"  {lib}: {status} - {config['purpose']}")
    
    print("✅ Dependency check completed")

def demo_provider_management():
    """Demonstrate provider management and fallbacks"""
    print("\n🔄 === Provider Management Demo ===")
    
    # Create module manager
    manager = ModuleManager()
    
    # Register providers with different priorities
    print("Registering providers...")
    manager.register_provider('i18n', ExternalI18nProvider, priority=10)
    manager.register_provider('i18n', DictionaryI18nProvider, priority=5)
    
    # Get active provider
    print("\nGetting active provider...")
    i18n = manager.get_provider('i18n')
    print(f"Active provider: {i18n.__class__.__name__}")
    
    # Test functionality
    print("\nTesting functionality...")
    test_cases = [
        ('שלום רופא', None),
        ('Hello doctor', None),
        ('welcome', 'he'),
        ('patient_found', 'en', {'name': 'John Doe', 'age': 35})
    ]
    
    for case in test_cases:
        if len(case) == 2:
            text, lang = case
            if lang:
                result = i18n.get_message(text, lang)
                print(f"  get_message('{text}', '{lang}') → {result}")
            else:
                detected = i18n.detect_language(text)
                welcome = i18n.get_message('welcome', detected)
                print(f"  detect_language('{text}') → {detected} → {welcome}")
        else:
            key, lang, kwargs = case
            result = i18n.get_message(key, lang, **kwargs)
            print(f"  get_message('{key}', '{lang}', {kwargs}) → {result}")
    
    # Show health status
    print(f"\nHealth status: {manager.get_health_status()}")

def demo_hot_swapping():
    """Demonstrate hot-swapping between providers"""
    print("\n🔥 === Hot-Swapping Demo ===")
    
    manager = ModuleManager()
    manager.register_provider('i18n', ExternalI18nProvider, priority=10)
    manager.register_provider('i18n', DictionaryI18nProvider, priority=5)
    
    # Get initial provider
    i18n = manager.get_provider('i18n')
    print(f"Initial provider: {i18n.__class__.__name__}")
    
    # Test with initial provider
    result1 = i18n.detect_language('שלום רופא')
    print(f"Language detection result: {result1}")
    
    # Force switch to dictionary provider
    print("\nForcing switch to DictionaryI18nProvider...")
    success = manager.force_provider_switch('i18n', 'DictionaryI18nProvider')
    print(f"Switch successful: {success}")
    
    # Get new provider (should be different instance)
    i18n_new = manager.get_provider('i18n')
    print(f"New provider: {i18n_new.__class__.__name__}")
    
    # Test with new provider
    result2 = i18n_new.detect_language('שלום רופא')
    print(f"Language detection result: {result2}")
    
    print(f"Final health status: {manager.get_health_status()}")

def demo_upgrade_simulation():
    """Simulate upgrading a module"""
    print("\n⬆️  === Module Upgrade Simulation ===")
    
    print("Simulating upgrade scenario:")
    print("1. Current: langdetect v1.0 (working)")
    print("2. Upgrade: langdetect v2.0 (might fail)")
    print("3. Fallback: Built-in detection (always works)")
    
    class LangDetectV1Provider(I18nProvider):
        def get_message(self, key: str, lang: str, **kwargs) -> str:
            return f"[v1] {key}"
        
        def detect_language(self, text: str) -> str:
            print("  Using langdetect v1.0...")
            return 'he' if any('\u0590' <= c <= '\u05FF' for c in text) else 'en'
        
        def test_connection(self) -> bool:
            return True
    
    class LangDetectV2Provider(I18nProvider):
        def __init__(self):
            self.should_fail = True  # Simulate upgrade failure
        
        def get_message(self, key: str, lang: str, **kwargs) -> str:
            return f"[v2] {key}"
        
        def detect_language(self, text: str) -> str:
            if self.should_fail:
                raise Exception("langdetect v2.0 has a bug!")
            print("  Using langdetect v2.0...")
            return 'he' if any('\u0590' <= c <= '\u05FF' for c in text) else 'en'
        
        def test_connection(self) -> bool:
            return not self.should_fail
    
    manager = ModuleManager()
    
    # Register providers (v2 has higher priority)
    manager.register_provider('langdetect', LangDetectV2Provider, priority=20)
    manager.register_provider('langdetect', LangDetectV1Provider, priority=10)
    manager.register_provider('langdetect', DictionaryI18nProvider, priority=5)
    
    print("\nAttempting to get provider (v2 should fail, fallback to v1)...")
    detector = manager.get_provider('langdetect')
    
    print(f"Active provider: {detector.__class__.__name__}")
    
    # Test detection
    test_text = "שלום רופא"
    try:
        result = detector.detect_language(test_text)
        print(f"Detection result for '{test_text}': {result}")
    except Exception as e:
        print(f"Detection failed: {e}")
    
    print(f"Health status: {manager.get_health_status()}")
    
    # Simulate fixing v2
    print("\nSimulating v2 bug fix...")
    if hasattr(detector, 'should_fail'):
        detector.should_fail = False
    
    # Force retry v2
    print("Retrying v2 provider...")
    try:
        manager.force_provider_switch('langdetect', 'LangDetectV2Provider')
        detector_v2 = manager.get_provider('langdetect')
        result = detector_v2.detect_language(test_text)
        print(f"v2 detection result: {result}")
    except Exception as e:
        print(f"v2 still failing: {e}")

def main():
    """Run all demos"""
    print("🏗️  Modular Architecture Capabilities Demo")
    print("=" * 50)
    
    try:
        demo_dependency_checking()
        demo_provider_management()
        demo_hot_swapping()
        demo_upgrade_simulation()
        
        print("\n🎉 === Demo Completed Successfully ===")
        print("Key takeaways:")
        print("✅ Dependency checking works")
        print("✅ Provider fallbacks work")
        print("✅ Hot-swapping works")
        print("✅ Upgrade simulation works")
        print("✅ System remains stable throughout")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
