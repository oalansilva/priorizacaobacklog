"""Serviço principal de priorização."""

from __future__ import annotations

import json
from typing import Any, List, Optional, Tuple

import pandas as pd
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

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
        self.logger.debug(
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
        self.logger.debug(
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
                estimado_qp=row.get("estimado_qp"),
                categoria=row.get("categoria"),
                area=row.get("area"),
                outros_dados={"score": float(row.get("score", 0.0))},
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
        
        # Remover linhas e colunas totalmente vazias
        df.dropna(axis=1, how="all", inplace=True)
        df.dropna(axis=0, how="all", inplace=True)
        
        df.columns = df.columns.str.strip().str.lower()
        df = df.loc[:, ~df.columns.duplicated()]
        
        # Normalizar colunas
        mapeamento = {
            # Esforço
            "esforco estimado": "horas",
            "esforco": "horas",
            "effort": "horas",
            "hours": "horas",
            "estimativa": "horas",
            # Item
            "titulo": "item",
            "title": "item",
            "nome": "item",
            "name": "item",
            "descricao": "item",
            # Impactos
            "impacto em negócios": "negocio",
            "impacto_negocios": "negocio",
            "impacto negocio": "negocio",
            "valor de negocio": "negocio",
            "impacto cliente": "cliente",
            "impacto_cliente": "cliente",
            "impacto financeiro": "financeiro",
            "impacto_financeiro": "financeiro",
            "okr": "okr",
            "estimado_qp": "estimado_qp",
            "categoria": "categoria",
            "area": "area"
        }
        df.rename(columns=mapeamento, inplace=True)
        df = df.loc[:, ~df.columns.duplicated()]
        
        # Garantir que temos a coluna item e remover linhas sem item
        if "item" in df.columns:
            df = df[df["item"].notna() & (df["item"] != "")]
            
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
        from app.core.database import get_repository
        
        # Obter configurações atualizadas do banco de dados
        repo = get_repository()
        db_settings = repo.get_settings()
        weights = db_settings.model_dump()
        
        # Fallback para self.settings se valores forem None (embora o DB deva ter defaults)
        if not weights.get('peso_financeiro'):
             weights.update(self.settings.model_dump())

        system_message = SystemMessage(build_system_prompt(capacidade_iniciativas, weights))
        human_message = HumanMessage(build_human_prompt(lista, capacidade_iniciativas))

        messages = [system_message, human_message]
        
        MAX_RETRIES = 3
        last_error = None
        
        for attempt in range(MAX_RETRIES):
            try:
                resposta = self.llm.invoke(messages)
                dados = self._parse_llm_response(resposta.content)

                if not isinstance(dados, list):
                    raise ValueError(
                        f"A IA retornou um formato inválido. Esperado list, recebido {type(dados)}"
                    )
                
                # Validar se todos os itens têm o campo 'status'
                # Convertemos para DataFrame temporariamente para facilitar a validação
                df_temp = pd.DataFrame(dados)
                if "status" not in df_temp.columns:
                     raise KeyError("O campo 'status' ('Priorizado' ou 'Despriorizado') é obrigatório para TODOS os itens, mas não foi encontrado na resposta.")

                resultado = pd.DataFrame(dados)
                resultado.columns = resultado.columns.str.strip().str.lower()
                # Remover colunas duplicadas (caso o LLM retorne 'Negocio' e 'negocio')
                resultado = resultado.loc[:, ~resultado.columns.duplicated()]
                return resultado
                
            except (ValueError, KeyError, json.JSONDecodeError) as e:
                last_error = e
                self.logger.warning(
                    "llm_retry",
                    attempt=attempt + 1,
                    error=str(e),
                    message="Solicitando correção para a LLM"
                )
                
                # Adicionar erro ao histórico da conversa para a LLM corrigir
                messages.append(AIMessage(content=str(resposta.content)))
                messages.append(HumanMessage(
                    content=f"Erro ao processar seu JSON: {str(e)}. "
                    "Por favor, corrija o formato e certifique-se de incluir o campo 'status' ('Priorizado' ou 'Despriorizado') para TODOS os itens. "
                    "Retorne APENAS o JSON corrigido."
                ))
        
        raise ValueError(f"Falha na priorização após {MAX_RETRIES} tentativas. A LLM não retornou o formato correto. Último erro: {last_error}")

    def _parse_llm_response(self, content: str) -> Any:
        """Parse LLM response, extracting JSON from markdown code blocks if present."""
        texto = content.strip()
        
        # Try to extract JSON from markdown code block
        if "```" in texto:
            # Find content between ``` markers
            import re
            # Match ```json or ``` followed by content and closing ```
            pattern = r'```(?:json)?\s*\n(.*?)\n```'
            match = re.search(pattern, texto, re.DOTALL)
            if match:
                texto = match.group(1).strip()
            else:
                # Fallback: remove first and last lines if they contain ```
                linhas = texto.split("\n")
                if linhas[0].strip().startswith("```"):
                    linhas = linhas[1:]
                if linhas and linhas[-1].strip() == "```":
                    linhas = linhas[:-1]
                texto = "\n".join(linhas).strip()
        
        # Try to find JSON array or object if there's extra text
        if not texto.startswith(("[", "{")):
            import re
            # Try to find a JSON array or object
            json_match = re.search(r'(\[.*\]|\{.*\})', texto, re.DOTALL)
            if json_match:
                texto = json_match.group(1)
        
        try:
            return json.loads(texto)
        except json.JSONDecodeError as e:
            self.logger.error(
                "json_parse_error",
                error=str(e),
                content_preview=texto[:500] if len(texto) > 500 else texto
            )
            raise ValueError(
                f"Não foi possível fazer parse da resposta do LLM. "
                f"Erro: {e}. Preview: {texto[:200]}..."
            )

    def _aplicar_status_e_prioridade(
        self, df: pd.DataFrame, capacidade_iniciativas: float
    ) -> pd.DataFrame:
        """
        Valida e organiza a resposta da LLM.
        A LLM já decidiu o status de cada item baseado na capacidade.
        """
        if "horas" not in df.columns:
            raise KeyError(
                "Coluna 'horas' não encontrada na resposta da IA. "
                f"Colunas disponíveis: {df.columns.tolist()}"
            )
        
        df = df.copy()
        df["horas"] = pd.to_numeric(df["horas"], errors="coerce").fillna(0)
        
        
        # Fallback: Se LLM não retornou status, calcular baseado na capacidade
        if "status" not in df.columns:
            raise KeyError(
                "Coluna 'status' não encontrada na resposta da IA. "
                "A LLM deve retornar o campo 'status' para cada item. "
                f"Colunas disponíveis: {df.columns.tolist()}"
            )
        
        # Normalizar status (Title Case) e tratar nulos
        if "status" in df.columns:
            df["status"] = df["status"].fillna("Despriorizado").astype(str).str.title()
            # Garantir que apenas valores válidos existam
            df.loc[~df["status"].isin(["Priorizado", "Despriorizado"]), "status"] = "Despriorizado"

        # Validação: avisar se Must Have foi despriorizado (não forçar mudança)
        if "must_have" in df.columns:
            mask_must_have_desp = (df["must_have"].str.lower() == "sim") & (df["status"] == "Despriorizado")
            if mask_must_have_desp.any():
                items_desp = df.loc[mask_must_have_desp, "item"].tolist()
                self.logger.warning(
                    "must_have_deprioritized",
                    count=mask_must_have_desp.sum(),
                    items=items_desp,
                    message="LLM despriorizou itens Must Have - revisar justificativas"
                )
        
        # Validação: avisar se total de horas priorizadas excede capacidade
        mask_priorizado = df["status"] == "Priorizado"
        total_horas_priorizadas = df.loc[mask_priorizado, "horas"].sum()
        if total_horas_priorizadas > capacidade_iniciativas:
            self.logger.warning(
                "capacity_exceeded",
                total_horas=total_horas_priorizadas,
                capacidade=capacidade_iniciativas,
                excesso=total_horas_priorizadas - capacidade_iniciativas,
                message=f"Total de horas priorizadas ({total_horas_priorizadas}h) excede capacidade ({capacidade_iniciativas}h)"
            )
        
        # Ordenar: Priorizado primeiro, depois Must Have primeiro, depois ordem original
        df["_status_order"] = df["status"].map({"Priorizado": 0, "Despriorizado": 1})
        if "must_have" in df.columns:
            df["_must_have_order"] = df["must_have"].str.lower().map({"sim": 0, "não": 1}).fillna(1)
        else:
            df["_must_have_order"] = 1
        
        df = df.sort_values(
            by=["_status_order", "_must_have_order"], 
            ascending=[True, True]
        )
        df.drop(columns=["_status_order", "_must_have_order"], inplace=True)
        df.reset_index(drop=True, inplace=True)
        
        # Atribuir prioridades numéricas
        df.loc[mask_priorizado, "prioridade"] = range(1, mask_priorizado.sum() + 1)
        df.loc[~mask_priorizado, "prioridade"] = 999
        
        self.logger.debug(
            "priority_assignment",
            num_priorizados=mask_priorizado.sum(),
            num_despriorizados=(~mask_priorizado).sum(),
            prioridades_priorizados=df.loc[mask_priorizado, "prioridade"].tolist() if mask_priorizado.sum() > 0 else [],
            prioridades_despriorizados=df.loc[~mask_priorizado, "prioridade"].tolist() if (~mask_priorizado).sum() > 0 else []
        )
        
        # Calcular Score
        # Obter pesos atuais (já carregados em 'weights' no método anterior, mas precisamos aqui também)
        # Como _aplicar_status_e_prioridade é chamado após _obter_priorizacao_da_ia, podemos recalcular ou passar os pesos.
        # Para simplificar, vamos buscar novamente do banco ou usar defaults
        from app.core.database import get_repository
        repo = get_repository()
        db_settings = repo.get_settings()
        
        peso_fin = db_settings.peso_financeiro
        peso_neg = db_settings.peso_negocios
        peso_cli = db_settings.peso_cliente
        peso_okr = db_settings.peso_okr
        total_pesos = peso_fin + peso_neg + peso_cli + peso_okr
        
        def calcular_score(row):
            # 1. Must Have = 100%
            if "must_have" in row and str(row["must_have"]).lower() == "sim":
                return 100.0
            
            # 2. Calcular com base nos pesos
            score = 0.0
            
            # Helper para converter Sim/Não em 1/0
            def val(col):
                v = str(row.get(col, "não")).lower()
                return 1.0 if v == "sim" else 0.0
            
            if total_pesos > 0:
                score += val("financeiro") * peso_fin
                score += val("negocio") * peso_neg
                score += val("cliente") * peso_cli
                score += val("okr") * peso_okr
                score = (score / total_pesos) * 100.0
            
            return round(score, 1)

        df["score"] = df.apply(calcular_score, axis=1)

        return df


