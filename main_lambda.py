"""Handler para deploy em AWS Lambda + API Gateway."""

from __future__ import annotations

from mangum import Mangum

from app.main import app

handler = Mangum(app, api_gateway_base_path="/prod")


