# -*- coding: utf-8 -*-

# Passo 1: Instale as bibliotecas necessárias
# pip install langchain-openai python-dotenv pandas openpyxl

import sys
from typing import Optional

from dotenv import load_dotenv

from app.config import get_settings
from app.core.prioritization import PrioritizationService

# Configurar encoding UTF-8 para Windows
if sys.platform == "win32":
    try:  # pragma: no cover
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):  # pragma: no cover
        import io

        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

# Carrega as variáveis de ambiente do ficheiro .env
load_dotenv()
SETTINGS = get_settings()


def _obter_capacidade_total(input_func=input) -> int:
    capacidade_total = 0
    while True:
        try:
            capacidade_input = input_func(
                "➡️ Por favor, insira o total de horas de capacidade da equipa para o trimestre "
                f"(padrão: {SETTINGS.default_capacidade_total}): "
            )
            if not capacidade_input:
                capacidade_total = SETTINGS.default_capacidade_total
                print(
                    f"Nenhum valor inserido. A usar o valor padrão de {capacidade_total} horas."
                )
                break
            capacidade_total = int(capacidade_input)
            if capacidade_total > 0:
                break
            print("❌ Erro: Por favor, insira um número positivo.")
        except ValueError:
            print("❌ Erro: Entrada inválida. Por favor, insira um número inteiro.")
    return capacidade_total


def _obter_percentual_sustentacao(input_func=input) -> int:
    percentual_sustentacao = 0
    while True:
        try:
            percentual_input = input_func(
                "➡️ Insira o percentual (%) de capacidade para Sustentação "
                f"(padrão: {SETTINGS.default_percentual_sustentacao}): "
            )
            if not percentual_input:
                percentual_sustentacao = SETTINGS.default_percentual_sustentacao
                print(
                    f"Nenhum valor inserido. A usar o valor padrão de {percentual_sustentacao}%."
                )
                break
            percentual_sustentacao = int(percentual_input)
            if 0 <= percentual_sustentacao <= 100:
                break
            print("❌ Erro: Por favor, insira um número entre 0 e 100.")
        except ValueError:
            print("❌ Erro: Entrada inválida. Por favor, insira um número inteiro.")
    return percentual_sustentacao


def executar_processamento(
    caminho_csv: str,
    capacidade_total: Optional[int] = None,
    percentual_sustentacao: Optional[int] = None,
) -> None:
    """Executa fluxo utilizando o PrioritizationService."""

    service = PrioritizationService(settings=SETTINGS)

    print(f"\n--- Iniciando processamento do ficheiro {caminho_csv} ---")
    resposta = service.process_from_csv(
        caminho_csv,
        capacidade_total=capacidade_total,
        percentual_sustentacao=percentual_sustentacao,
    )

    print("\n✅ RESUMO FINAL DO PROCESSAMENTO ✅")
    print(
        f"Capacidade para Iniciativas: {resposta.capacidade_iniciativas} horas | "
        f"Horas alocadas: {resposta.horas_alocadas} horas"
    )
    if resposta.roadmap_url:
        print(f"Roadmap disponível em: {resposta.roadmap_url}")
    else:
        print("Arquivo local gerado em diretório temporário.")


def main() -> None:
    print("=" * 60)
    print("🤖 Bem-vindo ao Gênio Priorizador de Backlog (PAM-Q-3-2025) 🤖")
    print("=" * 60)

    capacidade_total = _obter_capacidade_total()
    percentual_sustentacao = _obter_percentual_sustentacao()

    print("-" * 60)
    horas_sustentacao = (capacidade_total * percentual_sustentacao) / 100
    capacidade_iniciativas = capacidade_total - horas_sustentacao
    print("📊 Resumo da Capacidade para o Trimestre:")
    print(f"Capacidade Total: {capacidade_total} horas")
    print(f"Reserva para Sustentação ({percentual_sustentacao}%): {horas_sustentacao} horas")
    print(f"Capacidade para Iniciativas: {capacidade_iniciativas} horas")
    print("-" * 60)

    nome_do_arquivo_csv = "demandas.csv"
    executar_processamento(
        nome_do_arquivo_csv,
        capacidade_total=capacidade_total,
        percentual_sustentacao=percentual_sustentacao,
    )


# --- Ponto de Entrada do Script ---
if __name__ == "__main__":
    main()

# --- Ponto de Entrada do Script ---
if __name__ == "__main__":
    print("=" * 60)
    print("🤖 Bem-vindo ao Gênio Priorizador de Backlog (PAM-Q-3-2025) 🤖")
    print("=" * 60)
    
    # --- Input da Capacidade Total ---
    capacidade_total = 0
    while True:
        try:
            capacidade_input = input("➡️ Por favor, insira o total de horas de capacidade da equipa para o trimestre (padrão: 1000): ")
            if not capacidade_input:
                capacidade_total = 1000
                print(f"Nenhum valor inserido. A usar o valor padrão de {capacidade_total} horas.")
                break
            capacidade_total = int(capacidade_input)
            if capacidade_total > 0:
                break
            else:
                print("❌ Erro: Por favor, insira um número positivo.")
        except ValueError:
            print("❌ Erro: Entrada inválida. Por favor, insira um número inteiro.")

    # --- Input do Percentual de Sustentação ---
    percentual_sustentacao = 0
    while True:
        try:
            percentual_input = input("➡️ Insira o percentual (%) de capacidade para Sustentação (padrão: 20): ")
            if not percentual_input:
                percentual_sustentacao = 20
                print(f"Nenhum valor inserido. A usar o valor padrão de {percentual_sustentacao}%.")
                break
            percentual_sustentacao = int(percentual_input)
            if 0 <= percentual_sustentacao <= 100:
                break
            else:
                print("❌ Erro: Por favor, insira um número entre 0 e 100.")
        except ValueError:
            print("❌ Erro: Entrada inválida. Por favor, insira um número inteiro.")

    print("-" * 60)

    # --- Cálculos de Capacidade ---
    horas_sustentacao = (capacidade_total * percentual_sustentacao) / 100
    capacidade_iniciativas = capacidade_total - horas_sustentacao
    
    print(f"📊 Resumo da Capacidade para o Trimestre:")
    print(f"Capacidade Total: {capacidade_total} horas")
    print(f"Reserva para Sustentação ({percentual_sustentacao}%): {horas_sustentacao} horas")
    print(f"Capacidade para Iniciativas: {capacidade_iniciativas} horas")
    print("-" * 60)

    # --- Execução do Processamento ---
    nome_do_arquivo_csv = "demandas.csv"
    horas_alocadas_iniciativas = processar_roadmap(nome_do_arquivo_csv, capacidade_iniciativas)
    
    # --- Relatório Final ---
    if horas_alocadas_iniciativas is not None:
        print("\n" + "=" * 60)
        print(f"✅ RESUMO FINAL DO PROCESSAMENTO ✅")
        print(f"O ficheiro 'roadmap_proposto.xlsx' foi criado com as iniciativas priorizadas.")
        print(f"Total de horas alocadas para iniciativas: {horas_alocadas_iniciativas} de {capacidade_iniciativas} disponíveis.")
        print("=" * 60)

