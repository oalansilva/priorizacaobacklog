"""Serviço principal de priorização."""

from __future__ import annotations

import json
from typing import Any, List, Optional, Tuple

import pandas as pd
from langchain_core.messages import HumanMessage, SystemMessage

from app.config import Settings, get_settings
from app.core.prompts import build_human_prompt, build_system_prompt
from app.logging import get_logger
from app.models import PrioritizationResponse, PrioritizedItem
from app.services.llm import get_llm
from app.services.storage import StorageService


class PrioritizationService:
    """Encapsula o fluxo de priorização de backlog."""

    def __init__(
        self,
        settings: Optional[Settings] = None,
        storage_service: Optional[StorageService] = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.llm = get_llm(self.settings)
        self.storage = storage_service or StorageService(self.settings)
        self.logger = get_logger(__name__).bind(service="PrioritizationService")

    def process_from_csv(
        self,
        path_csv: str,
        capacidade_total: Optional[int] = None,
        percentual_sustentacao: Optional[int] = None,
    ) -> PrioritizationResponse:
        """Ponto de entrada para ficheiros CSV locais."""

        df = pd.read_csv(path_csv, sep=";")
        return self.process_dataframe(
            df,
            capacidade_total=capacidade_total,
            percentual_sustentacao=percentual_sustentacao,
        )

    def process_dataframe(
        self,
        dataframe: pd.DataFrame,
        capacidade_total: Optional[int] = None,
        percentual_sustentacao: Optional[int] = None,
    ) -> PrioritizationResponse:
        """Executa todo o fluxo para um DataFrame."""

        capacidade = capacidade_total or self.settings.default_capacidade_total
        percentual = (
            percentual_sustentacao or self.settings.default_percentual_sustentacao
        )

        cleaned = self._clean_dataframe(dataframe)
        if cleaned.empty:
            raise ValueError("DataFrame fornecido está vazio após limpeza.")

        capacidade_iniciativas = self._calcular_capacidade_iniciativas(
            capacidade, percentual
        )
        self.logger.info(
            "process_dataframe.start",
            capacidade_total=capacidade,
            percentual_sustentacao=percentual,
            capacidade_iniciativas=capacidade_iniciativas,
            itens=len(cleaned),
        )

        priorizado = self._obter_priorizacao_da_ia(cleaned, capacidade_iniciativas)
        priorizado = self._aplicar_status_e_prioridade(
            priorizado, capacidade_iniciativas
        )

        horas_alocadas = float(
            priorizado.loc[priorizado["status"] == "Priorizado", "horas"].sum()
        )
        excel_path = self.storage.save_dataframe_as_excel(priorizado)
        s3_key = self.storage.upload_to_s3(excel_path)
        roadmap_url = (
            self.storage.generate_presigned_url(s3_key) if s3_key is not None else None
        )
        self.logger.info(
            "process_dataframe.end",
            horas_alocadas=horas_alocadas,
            total_itens=len(priorizado),
            s3_key=s3_key,
        )

        itens = [
            PrioritizedItem(
                prioridade=int(row["prioridade"]),
                item=str(row.get("item", "")),
                horas=float(row.get("horas", 0)),
                justificativa=str(row.get("justificativa", "")),
                status=str(row.get("status", "")),
                cliente=row.get("cliente"),
                negocio=row.get("negocio"),
                financeiro=row.get("financeiro"),
                okr=row.get("okr"),
                outros_dados=None,
            )
            for _, row in priorizado.iterrows()
        ]

        return PrioritizationResponse(
            capacidade_iniciativas=capacidade_iniciativas,
            horas_alocadas=horas_alocadas,
            itens=itens,
            roadmap_url=roadmap_url,
        )

    # --- Métodos internos -------------------------------------------------

    def _clean_dataframe(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        df = dataframe.copy()
        df.dropna(axis=1, how="all", inplace=True)
        df.columns = df.columns.str.strip().str.lower()
        return df

    def _calcular_capacidade_iniciativas(
        self, capacidade_total: int, percentual_sustentacao: int
    ) -> float:
        sustentacao = (capacidade_total * percentual_sustentacao) / 100
        return float(capacidade_total - sustentacao)

    def _obter_priorizacao_da_ia(
        self, df: pd.DataFrame, capacidade_iniciativas: float
    ) -> pd.DataFrame:
        lista = df.to_dict(orient="records")
        system_message = SystemMessage(build_system_prompt(capacidade_iniciativas))
        human_message = HumanMessage(build_human_prompt(lista, capacidade_iniciativas))

        resposta = self.llm.invoke([system_message, human_message])
        dados = self._parse_llm_response(resposta.content)

        if not isinstance(dados, list):
            raise ValueError(
                f"A IA retornou um formato inválido. Esperado list, recebido {type(dados)}"
            )

        resultado = pd.DataFrame(dados)
        resultado.columns = resultado.columns.str.strip().str.lower()
        return resultado

    def _parse_llm_response(self, content: str) -> Any:
        texto = content.strip()
        if texto.startswith("```"):
            linhas = texto.split("\n")
            if linhas[0].startswith("```"):
                linhas = linhas[1:]
            if linhas and linhas[-1].strip() == "```":
                linhas = linhas[:-1]
            texto = "\n".join(linhas)

        return json.loads(texto)

    def _aplicar_status_e_prioridade(
        self, df: pd.DataFrame, capacidade_iniciativas: float
    ) -> pd.DataFrame:
        if "horas" not in df.columns:
            raise KeyError(
                "Coluna 'horas' não encontrada na resposta da IA. "
                f"Colunas disponíveis: {df.columns.tolist()}"
            )

        df = df.copy()
        df["horas"] = pd.to_numeric(df["horas"], errors="coerce").fillna(0)
        df.insert(0, "prioridade", range(1, len(df) + 1))

        horas_cumulativas = df["horas"].cumsum()
        df["status"] = horas_cumulativas.le(capacidade_iniciativas).map(
            {True: "Priorizado", False: "Despriorizado"}
        )

        mask = df["status"] == "Despriorizado"
        if mask.any():
            df.loc[mask, "justificativa"] = (
                df.loc[mask, "justificativa"].fillna("Item de valor estratégico.")
                + " No entanto, foi despriorizado por falta de capacidade neste trimestre."
            )

        df = df.sort_values(by=["status", "prioridade"], ascending=[False, True])
        df.reset_index(drop=True, inplace=True)
        return df


