"""Handler para deploy em AWS Lambda + API Gateway."""

from __future__ import annotations

from mangum import Mangum

from app.main import app

# Handler para API Gateway
handler = Mangum(app)

# Alias para compatibilidade
lambda_handler = handler


