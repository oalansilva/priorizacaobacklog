"""Serviços de persistência (local e S3)."""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Optional

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from app.config import Settings, get_settings


class StorageService:
    """Responsável por salvar artefatos localmente e opcionalmente no S3."""

    def __init__(self, settings: Optional[Settings] = None) -> None:
        self.settings = settings or get_settings()
        self._s3 = (
            boto3.client("s3", region_name=self.settings.aws_region)
            if self.settings.storage_bucket
            else None
        )

    def save_dataframe_as_excel(
        self, df, filename: str = "roadmap_proposto.xlsx"
    ) -> Path:
        """Grava o DataFrame como Excel num diretório temporário."""

        temp_dir = Path(tempfile.mkdtemp(prefix="roadmap-"))
        output_path = temp_dir / filename
        df.to_excel(
            output_path,
            index=False,
            sheet_name=self.settings.resultado_sheet_name,
        )
        return output_path

    def upload_to_s3(self, file_path: Path) -> Optional[str]:
        """Carrega o ficheiro para S3, se configurado."""

        if not self._s3 or not self.settings.storage_bucket:
            return None

        key = f"{self.settings.storage_prefix.rstrip('/')}/{file_path.name}"
        try:
            self._s3.upload_file(str(file_path), self.settings.storage_bucket, key)
        except (BotoCoreError, ClientError) as exc:  # pragma: no cover
            raise RuntimeError(f"Falha ao enviar arquivo para S3: {exc}") from exc

        return key

    def generate_presigned_url(self, object_key: str, expires_in: int = 3600) -> str:
        """Gera URL temporária para download do artefato."""

        if not self._s3 or not self.settings.storage_bucket:
            raise RuntimeError("S3 não configurado para gerar URLs.")

        try:
            return self._s3.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.settings.storage_bucket, "Key": object_key},
                ExpiresIn=expires_in,
            )
        except (BotoCoreError, ClientError) as exc:  # pragma: no cover
            raise RuntimeError(f"Falha ao gerar URL assinada: {exc}") from exc


