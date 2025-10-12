#!/bin/bash
set -e

export APP_ENV=test
export PYTHONPATH=/home/ubuntu/dental-clinic-ai/backend:$PYTHONPATH

echo "================================"
echo "RUNNING ALL DENTAFLOW TESTS"
echo "================================"
echo ""

echo "1. Initialization Tests (5 tests)..."
python3.11 app/tests/test_agent_initialization.py > /tmp/test1.log 2>&1
if [ $? -eq 0 ]; then
  echo "✅ Initialization: PASSED"
else
  echo "❌ Initialization: FAILED"
  cat /tmp/test1.log | tail -20
  exit 1
fi

echo "2. Alex Functional Tests (20 tests)..."
python3.11 app/tests/test_alex_tools_functional.py > /tmp/test2.log 2>&1
if [ $? -eq 0 ]; then
  echo "✅ Alex: PASSED"
else
  echo "❌ Alex: FAILED"
  cat /tmp/test2.log | tail -20
  exit 1
fi

echo "3. Sarah Functional Tests (10 tests)..."
python3.11 app/tests/test_sarah_tools_functional.py > /tmp/test3.log 2>&1
if [ $? -eq 0 ]; then
  echo "✅ Sarah: PASSED"
else
  echo "❌ Sarah: FAILED"
  cat /tmp/test3.log | tail -20
  exit 1
fi

echo "4. Marcus Functional Tests (8 tests)..."
python3.11 app/tests/test_marcus_tools_functional.py > /tmp/test4.log 2>&1
if [ $? -eq 0 ]; then
  echo "✅ Marcus: PASSED"
else
  echo "❌ Marcus: FAILED"
  cat /tmp/test4.log | tail -20
  exit 1
fi

echo "5. Marcus Complete Tests (15 tests)..."
python3.11 app/tests/test_marcus_tools_complete.py > /tmp/test5.log 2>&1
if [ $? -eq 0 ]; then
  echo "✅ Marcus Complete: PASSED"
else
  echo "❌ Marcus Complete: FAILED"
  cat /tmp/test5.log | tail -20
  exit 1
fi

echo "6. Sophia Functional Tests (15 tests)..."
python3.11 app/tests/test_sophia_tools_functional.py > /tmp/test6.log 2>&1
if [ $? -eq 0 ]; then
  echo "✅ Sophia: PASSED"
else
  echo "❌ Sophia: FAILED"
  cat /tmp/test6.log | tail -20
  exit 1
fi

echo "7. Sophia Complete Tests (28 tests)..."
python3.11 app/tests/test_sophia_tools_complete.py > /tmp/test7.log 2>&1
if [ $? -eq 0 ]; then
  echo "✅ Sophia Complete: PASSED"
else
  echo "❌ Sophia Complete: FAILED"
  cat /tmp/test7.log | tail -20
  exit 1
fi

echo ""
echo "================================"
echo "🎉 ALL TESTS PASSED! 🎉"
echo "================================"
echo ""
echo "Summary:"
echo "- Initialization: 5/5 ✅"
echo "- Alex: 20/20 ✅"
echo "- Sarah: 10/10 ✅"
echo "- Marcus: 23/23 ✅ (8+15)"
echo "- Sophia: 43/43 ✅ (15+28)"
echo ""
echo "Total: 101/101 tests (100%)"
