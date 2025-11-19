# -*- coding: utf-8 -*-

# Passo 1: Instale as bibliotecas necessárias
# pip install langchain-openai python-dotenv pandas openpyxl

import os
import sys
import pandas as pd
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
import json

# Configurar encoding UTF-8 para Windows
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except (AttributeError, ValueError):
        # Fallback para versões antigas do Python ou casos onde reconfigure não está disponível
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Carrega as variáveis de ambiente do ficheiro .env
load_dotenv()
LOG_PREFIX = "[DIAGNÓSTICO]"

def obter_priorizacao_da_ia(dados_df, capacidade_total):
    """
    Usa o LLM para a tarefa estratégica: ordenar a lista de itens por prioridade e
    adicionar a justificativa para essa ordem, considerando a capacidade total.
    """
    print("🤖 A chamar a IA para realizar a priorização estratégica das iniciativas...")
    
    lista_de_itens = dados_df.to_dict(orient='records')
    print(f"{LOG_PREFIX} A enviar {len(lista_de_itens)} itens para análise da IA.")
    
    llm = ChatOpenAI(model="gpt-4o", temperature=0.3)

    system_message = SystemMessage(
        content=f"""Você é um experiente Product Manager (PM). A sua tarefa é receber uma lista de itens de backlog e propor uma ordem de prioridade para um trimestre com uma capacidade total de {capacidade_total} horas para estas iniciativas.

1. Reordene a lista inteira, colocando os itens de maior prioridade estratégica no topo. A sua ordenação deve refletir a melhor estratégia para maximizar o valor dentro da capacidade disponível.
2. Para CADA item, adicione um novo campo chamado 'Justificativa', explicando o raciocínio para a sua posição na lista.
3. Retorne a lista JSON completa, reordenada e com o novo campo 'Justificativa'. A sua resposta deve conter APENAS o JSON e usar chaves em minúsculas (ex: 'item', 'horas').

Use os seguintes princípios para a sua análise:
- **Amplitude de Valor:** Itens que impactam Cliente, Negócio e Financeiro são mais valiosos.
- **Alinhamento com OKR:** A contribuição para um OKR tem um peso muito alto.
- **Custo-Benefício:** Pondere o esforço em 'Horas' versus o impacto gerado. Itens de alto custo que impediriam a entrega de vários outros itens de alto valor devem ser cuidadosamente avaliados."""
    )

    human_message = HumanMessage(
        content=f"Priorize estrategicamente a seguinte lista de itens, considerando o limite de {capacidade_total} horas, e adicione o campo 'Justificativa' para cada um: {json.dumps(lista_de_itens, indent=2)}"
    )

    try:
        resposta = llm.invoke([system_message, human_message])
        print(f"{LOG_PREFIX} Resposta bruta da IA recebida (primeiros 200 caracteres): {resposta.content[:200]}...")
        
        # Extrair JSON da resposta, removendo markdown code blocks se presentes
        json_string = resposta.content.strip()
        # Remover code blocks markdown (```json ... ``` ou ``` ... ```)
        if json_string.startswith("```"):
            lines = json_string.split("\n")
            # Remover primeira linha (```json ou ```)
            if lines[0].startswith("```"):
                lines = lines[1:]
            # Remover última linha (```)
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            json_string = "\n".join(lines)
        
        dados_priorizados = json.loads(json_string)
        
        # Validação: verificar se a resposta é uma lista
        if not isinstance(dados_priorizados, list):
            print(f"❌ ERRO CRÍTICO: A IA retornou um formato inválido. Esperava uma lista, recebeu: {type(dados_priorizados)}")
            return None
        
        if len(dados_priorizados) == 0:
            print(f"❌ ERRO CRÍTICO: A IA retornou uma lista vazia.")
            return None
        
        print(f"✅ Análise estratégica da IA concluída com sucesso! {len(dados_priorizados)} itens retornados.")
        return pd.DataFrame(dados_priorizados)
    except json.JSONDecodeError as e:
        print(f"❌ ERRO CRÍTICO: A IA não retornou um JSON válido. Ocorreu um erro de descodificação: {e}")
        if 'resposta' in locals() and hasattr(resposta, 'content'):
            print(f"{LOG_PREFIX} Resposta completa que causou o erro:\n{resposta.content}")
        return None
    except Exception as e:
        print(f"❌ Erro ao obter a priorização da IA: {e}")
        import traceback
        print(f"{LOG_PREFIX} Detalhes do erro:\n{traceback.format_exc()}")
        return None

def processar_roadmap(caminho_arquivo_csv, capacidade_iniciativas):
    """
    Orquestra o processo: ler os dados, obter a priorização da IA e, de forma fiável,
    processar e guardar o ficheiro final.
    """
    if "OPENAI_API_KEY" not in os.environ:
        print("Erro: A chave da API da OpenAI não foi encontrada.")
        return

    try:
        # --- 1. Carregar e Limpar os Dados ---
        print(f"\n--- Passo 1: Carregar e Limpar Dados ---")
        print(f"A ler o ficheiro de entrada: {caminho_arquivo_csv}...")
        df_iniciativas = pd.read_csv(caminho_arquivo_csv, sep=';')
        print(f"{LOG_PREFIX} Ficheiro lido. Shape inicial: {df_iniciativas.shape}")

        df_iniciativas.dropna(axis=1, how='all', inplace=True)
        print(f"{LOG_PREFIX} Colunas vazias removidas. Shape após limpeza: {df_iniciativas.shape}")

        df_iniciativas.columns = df_iniciativas.columns.str.strip().str.lower()
        print(f"{LOG_PREFIX} Nomes das colunas normalizados.")
        print(f"{LOG_PREFIX} Colunas detetadas: {df_iniciativas.columns.tolist()}")
        
        # Validação: verificar se o DataFrame não está vazio
        if df_iniciativas.empty:
            print(f"❌ ERRO CRÍTICO: O ficheiro '{caminho_arquivo_csv}' está vazio ou não contém dados válidos.")
            return None

        # --- 2. Obter a Ordem de Prioridade e Justificativas da IA ---
        print(f"\n--- Passo 2: Análise Estratégica da IA ---")
        df_iniciativas_priorizadas = obter_priorizacao_da_ia(df_iniciativas, capacidade_iniciativas)
        
        if df_iniciativas_priorizadas is None:
            print("❌ Processo interrompido devido a um erro na análise da IA.")
            return None
        
        if df_iniciativas_priorizadas.empty:
            print("❌ ERRO CRÍTICO: A IA retornou um DataFrame vazio.")
            return None

        df_iniciativas_priorizadas.columns = df_iniciativas_priorizadas.columns.str.strip().str.lower()
        print(f"{LOG_PREFIX} Colunas da resposta da IA normalizadas.")
        print(f"{LOG_PREFIX} Primeiras 3 linhas da lista priorizada pela IA:\n{df_iniciativas_priorizadas.head(3).to_string()}")

        # --- 3. Alocação de Capacidade e Atualização da Justificativa ---
        print(f"\n--- Passo 3: Alocação de Capacidade ---")
        
        # Validação: verificar se a coluna 'horas' existe
        if 'horas' not in df_iniciativas_priorizadas.columns:
            print(f"❌ ERRO CRÍTICO: A coluna 'horas' não foi encontrada no DataFrame retornado pela IA.")
            print(f"{LOG_PREFIX} Colunas disponíveis: {df_iniciativas_priorizadas.columns.tolist()}")
            return None
        
        # Converter coluna 'horas' para numérico de forma vetorizada
        df_iniciativas_priorizadas['horas'] = pd.to_numeric(df_iniciativas_priorizadas['horas'], errors='coerce').fillna(0)
        
        # Calcular status de forma vetorizada
        horas_cumulativas = df_iniciativas_priorizadas['horas'].cumsum()
        df_iniciativas_priorizadas['status'] = (horas_cumulativas <= capacidade_iniciativas).map({True: 'Priorizado', False: 'Despriorizado'})
        
        # Atualizar justificativas para itens despriorizados
        mask_despriorizado = df_iniciativas_priorizadas['status'] == 'Despriorizado'
        if mask_despriorizado.any():
            df_iniciativas_priorizadas.loc[mask_despriorizado, 'justificativa'] = (
                df_iniciativas_priorizadas.loc[mask_despriorizado, 'justificativa'].fillna("Item de valor estratégico.") +
                " No entanto, foi despriorizado por falta de capacidade neste trimestre."
            )
        
        horas_alocadas = df_iniciativas_priorizadas[df_iniciativas_priorizadas['status'] == 'Priorizado']['horas'].sum()
        print("✅ Status definido e justificativas de capacidade atualizadas.")
        print(f"{LOG_PREFIX} Total de horas alocadas para iniciativas: {horas_alocadas} / {capacidade_iniciativas}")

        # --- 4. Adicionar Coluna de Prioridade Numérica ---
        print(f"\n--- Passo 4: Adicionar Prioridade Numérica ---")
        df_iniciativas_priorizadas.insert(0, 'prioridade', range(1, 1 + len(df_iniciativas_priorizadas)))
        print("✅ Coluna 'Prioridade' adicionada.")

        # --- 4.5. Ordenar o Relatório Final ---
        print(f"\n--- Passo 4.5: Ordenar Relatório Final ---")
        # Ordena primeiro pelo Status (Priorizado primeiro) e depois pela Prioridade original.
        df_iniciativas_priorizadas = df_iniciativas_priorizadas.sort_values(
            by=['status', 'prioridade'],
            ascending=[False, True]
        )
        print("✅ Relatório final ordenado por Status.")
        
        # Resetar índice após ordenação
        df_iniciativas_priorizadas.reset_index(drop=True, inplace=True)

        # --- 5. Gerar o Ficheiro Excel Final ---
        print(f"\n--- Passo 5: Gerar Ficheiro Excel ---")
        caminho_output = 'roadmap_proposto.xlsx'
        df_iniciativas_priorizadas.to_excel(caminho_output, index=False, sheet_name='Roadmap Q3 2025')
        print(f"✅ Ficheiro '{caminho_output}' gerado com sucesso.")
        
        return horas_alocadas

    except FileNotFoundError:
        print(f"ERRO CRÍTICO: O ficheiro '{caminho_arquivo_csv}' não foi encontrado.")
        return None
    except KeyError as e:
        print(f"❌ ERRO CRÍTICO: Não foi possível encontrar a coluna esperada: {e}")
        print(f"{LOG_PREFIX} Verifique se o nome da coluna existe no ficheiro de entrada e corresponde ao esperado pelo script (após normalização).")
        return None
    except Exception as e:
        print(f"❌ Ocorreu um erro inesperado durante o processamento: {e}")
        return None

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

