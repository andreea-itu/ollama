#!/usr/bin/env bash
# Test script for app_solved.py
# Tests: health, chat with selective memory, and the two-model email chain
# Usage: bash test_app_solved.sh

BASE_URL="http://127.0.0.1:5000"

echo "========================================="
echo "  1. Health check"
echo "========================================="
curl -s "$BASE_URL/health" | python3 -m json.tool
echo ""

echo "========================================="
echo "  2. Create a new session"
echo "========================================="
SID=$(curl -s -X POST "$BASE_URL/new_session" | python3 -c "import sys,json; print(json.load(sys.stdin)['session_id'])")
echo "Session ID: $SID"
echo ""

echo "========================================="
echo "  3. Chat — remember a fact"
echo "========================================="
curl -s -X POST "$BASE_URL/chat" \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"remember: my name is Andreea and I study AI\", \"session_id\": \"$SID\", \"use_memory\": true}" | python3 -m json.tool
echo ""

echo "========================================="
echo "  4. Chat — normal question (should NOT update memory)"
echo "========================================="
curl -s -X POST "$BASE_URL/chat" \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"What is 2+2?\", \"session_id\": \"$SID\", \"use_memory\": true}" | python3 -m json.tool
echo ""

echo "========================================="
echo "  5. Chat — recall the remembered fact"
echo "========================================="
curl -s -X POST "$BASE_URL/chat" \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"What is my name and what do I study?\", \"session_id\": \"$SID\", \"use_memory\": true}" | python3 -m json.tool
echo ""

echo "========================================="
echo "  6. Chat — without memory (should not remember anything)"
echo "========================================="
curl -s -X POST "$BASE_URL/chat" \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"What is my name?\", \"session_id\": \"$SID\", \"use_memory\": false}" | python3 -m json.tool
echo ""

echo "========================================="
echo "  7. Reset session"
echo "========================================="
curl -s -X POST "$BASE_URL/reset_session" \
  -H "Content-Type: application/json" \
  -d "{\"session_id\": \"$SID\"}" | python3 -m json.tool
echo ""

echo "========================================="
echo "  8. Chat — after reset (should NOT remember)"
echo "========================================="
curl -s -X POST "$BASE_URL/chat" \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"What is my name?\", \"session_id\": \"$SID\", \"use_memory\": true}" | python3 -m json.tool
echo ""

echo "========================================="
echo "  9. Email chain — family email"
echo "========================================="
curl -s -X POST "$BASE_URL/email_chain" \
  -H "Content-Type: application/json" \
  -d '{
    "email_text": "Hey sis! Are you coming to Mom'\''s birthday dinner this Saturday? We'\''re thinking of making her favorite lasagna. Let me know if you can bring dessert! Love, Maria"
  }' | python3 -m json.tool
echo ""

echo "========================================="
echo "  10. Email chain — boss email"
echo "========================================="
curl -s -X POST "$BASE_URL/email_chain" \
  -H "Content-Type: application/json" \
  -d '{
    "email_text": "Hi, I wanted to follow up on the Q3 report. The deadline is this Friday and I haven'\''t received your section yet. Please prioritize this and send it by end of day Thursday. Regards, David Chen, VP of Operations"
  }' | python3 -m json.tool
echo ""

echo "========================================="
echo "  11. Email chain — school email"
echo "========================================="
curl -s -X POST "$BASE_URL/email_chain" \
  -H "Content-Type: application/json" \
  -d '{
    "email_text": "Dear Student, This is a reminder that the assignment for Introduction to AI is due next Monday. Please submit your work via the online portal. If you have questions, attend office hours on Wednesday. Best, Prof. Mueller"
  }' | python3 -m json.tool
echo ""

echo "========================================="
echo "  Done! All tests completed."
echo "========================================="
