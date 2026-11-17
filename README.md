# Análise e Monitoramento de Serviços Marítimos — Atlantic Ocean Services

Projeto de extensão da disciplina **Tópicos de Big Data em Python** (Universidade Estácio de Sá — Campus Campo Grande), focado no tratamento, auditoria e estruturação de dados operacionais de serviços marítimos e portuários para análise gerencial e visualização no Power BI.

## Arquitetura da Solução

1. **Ingestão (`TRABALHO.xlsx`):** Leitura de 1.118 registros históricos distribuídos em 18 colunas (serviço, navio, cliente, estado, porto, colaborador, datas de início/fim e 10 critérios de avaliação).
2. **Processamento e Auditoria (`main.py`):** Pipeline em Python (`pandas` e `openpyxl`) para limpeza de cabeçalhos, normalização de datas mistas, correção heurística e geração de indicadores.
3. **Armazenamento (`TRABALHO_TRATADO.xlsx`):** Exportação da aba `Dados` com datas padronizadas (`DD/MM/YYYY`), preservação das datas originais, colunas de auditoria e destaque visual em amarelo (`#FFF2CC`) nos registros sinalizados para revisão manual.
4. **Visualização (Power BI):** Dashboard interativo com KPIs operacionais, análise de satisfação e simulação de cenário sem tarifas dos EUA.

## Principais Tratamentos Implementados (`main.py`)

* **Normalização de Datas Mistas:** Unificação de datas nativas do Excel, padrão ISO (`AAAA-MM-DD`), formato brasileiro (`DD/MM/AAAA`), números seriais e correção de anos truncados (ex.: `/205` e `/206`) via expressões regulares.
* **Auditoria Heurística com Vizinhança Direta:** Detecção automática de conflitos de regionalidade (`MM/DD` vs. `DD/MM`), datas de início/término invertidas e erros de ano apoiada por mediana local, comparação com registros vizinhos (`DIST_VIZINHO`) e trava contra datas futuras (`HOJE`).
* **Rastreabilidade e Revisão Manual:** Classificação das correções por nível de confiança (`alta` ou `baixa`), preservação das datas originais (`Data Inicial Original` e `Data Final Original`) e sinalização automática na coluna `Revisar_Manual` com destaque em amarelo na planilha final.
* **Engenharia de Atributos (KPIs):**
  * `Duracao_Dias`: Tempo de execução de cada operação em dias.
  * `ISG`: Índice de Satisfação Geral (média dos 10 critérios de avaliação, escala de 1 a 5).
  * `Peso_Cenario_Sem_Taxas`: Multiplicador (`1.20`) para simulação acadêmica de crescimento de +20% na demanda sem tarifas comerciais dos EUA.

## Resultados Consolidados

* **Registros processados:** 1.118 operações
* **Registros corrigidos automaticamente:** 73 (inversões de dia/mês, erros de ano e datas invertidas)
* **Registros sinalizados para revisão manual:** 41 (destacados em amarelo para conferência humana)
* **Duração Média:** 0,60 dias (mediana de 0 dias; máxima válida de 31 dias)
* **ISG Médio:** 4,42
* **Demanda Simulada (Cenário sem Tarifas):** 1.341 atendimentos (+20%)

## Como Executar

```bash
# 1. Criar e ativar o ambiente virtual
python -m venv .venv
.venv\Scripts\activate

# 2. Instalar as dependências
pip install pandas openpyxl

# 3. Executar o pipeline ETL
python main.py
