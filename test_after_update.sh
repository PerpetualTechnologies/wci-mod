#!/bin/bash
curl -X POST "https://wci-720262754398.us-central1.run.app/webhook-wci" \
-H "Content-Type: application/json" \
-d '{
  "message": {
    "from": "51987654321",
    "text": {
      "body": "[Chat id: OGBZys] buenas tardes Lead Data: Email=test@email.com, DNI=12345678"
    }
  }
}'
