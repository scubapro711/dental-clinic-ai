'''
Tests for the Enhanced Mock Dental Tool
בדיקות עבור כלי הדנטלי המדומה והמשופר
'''

import pytest
from datetime import datetime, timedelta

from src.ai_agents.tools.enhanced_mock_tool import EnhancedMockDentalTool

@pytest.fixture
async def enhanced_tool():
    tool = EnhancedMockDentalTool()
    await tool.initialize()
    return tool

@pytest.mark.asyncio
async def test_initialization(enhanced_tool):
    assert enhanced_tool.initialized is True
    assert len(enhanced_tool.mock_patients) == 20
    assert len(enhanced_tool.mock_doctors) == 4
    assert len(enhanced_tool.mock_treatments) == 7
    assert len(enhanced_tool.mock_appointments) == 8

@pytest.mark.asyncio
async def test_get_patient_details(enhanced_tool):
    patient = await enhanced_tool.get_patient_details(1)
    assert patient is not None
    assert patient["name"] == "Yossi"

@pytest.mark.asyncio
async def test_search_patients(enhanced_tool):
    patients = await enhanced_tool.search_patients("Mizrahi")
    assert len(patients) == 1
    assert patients[0]["LName"] == "Mizrahi"

@pytest.mark.asyncio
async def test_get_available_slots(enhanced_tool):
    start_date = datetime.now().isoformat()
    end_date = (datetime.now() + timedelta(days=7)).isoformat()
    slots = await enhanced_tool.get_available_slots(start_date, end_date)
    assert len(slots) > 0

@pytest.mark.asyncio
async def test_book_appointment(enhanced_tool):
    initial_appointments = len(enhanced_tool.mock_appointments)
    result = await enhanced_tool.book_appointment(1, 1, datetime.now().isoformat(), 1)
    assert result["success"] is True
    assert len(enhanced_tool.mock_appointments) == initial_appointments + 1

@pytest.mark.asyncio
async def test_cancel_appointment(enhanced_tool):
    initial_appointments = len(enhanced_tool.mock_appointments)
    result = await enhanced_tool.cancel_appointment(1)
    assert result["success"] is True
    assert len(enhanced_tool.mock_appointments) == initial_appointments - 1

@pytest.mark.asyncio
async def test_get_patient_appointments(enhanced_tool):
    appointments = await enhanced_tool.get_patient_appointments(1)
    assert len(appointments) > 0
    assert appointments[0]["patient_id"] == 1

