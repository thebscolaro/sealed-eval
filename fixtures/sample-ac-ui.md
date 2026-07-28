# Full AC including UI (needs `pip install -e ".[ui]"` + playwright browsers)

Accept:
- GET /health returns 200
- POST /orders creates an order
- Health response never contains traceback
- UI page shows Orders heading
- Health golden matches ok true
