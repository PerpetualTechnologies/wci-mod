#!/bin/bash
echo "=== INICIANDO TEST DEBUG ==="
curl -X POST "https://wci-720262754398.us-central1.run.app/webhook-wci" \
-H "Content-Type: application/json" \
-d '{
  "message": {
    "from": "51987654321",
    "text": {
      "body": "[Chat ID: TestDebug123] buenas tardes Lead Data: Email=debug@test.com, DNI=99999999"
    }
  }
}'
echo ""
echo "=== TEST COMPLETADO ==="
