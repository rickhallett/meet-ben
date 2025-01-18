curl -v -X POST http://localhost:8001/api/ben/ \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer $API_TOKEN" \
     -d '{
           "query": "example query",
           "user_id": "user123",
           "request_id": "req456",
           "session_id": "sess789"
         }'