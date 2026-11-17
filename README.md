# Pipeline ETL e Análise Operacional — Atlantic Ocean Services

Projeto desenvolvido para tratamento, padronização e análise de dados operacionais de serviços marítimos e portuários da **Atlantic Ocean Services**, preparando a base para visualização estratégica no Power BI.

## Objetivo do Projeto
Transformar a base bruta (`TRABALHO.xlsx`), que apresentava inconsistências críticas de formatação de datas, em uma base limpa, confiável e estruturada (`TRABALHO_TRATADO.xlsx`), permitindo mensurar indicadores de desempenho operacional e simular cenários de expansão de demanda.

## Metodologia ETL (`main.py`)
O pipeline em Python (`pandas` e `openpyxl`) executa quatro etapas principais:

1. **Padronização Multi-Formato de Datas:** Tratamento unificado de datas nativas do Excel, strings no padrão ISO (`AAAA-MM-DD`), strings no padrão brasileiro (`DD/MM/AAAA`), números seriais do Excel e correção de anos truncados (ex.: `/205` e `/206`).
2. **Correção Cronológica Heurística:** Identificação e correção automática de **76 registros** inconsistentes utilizando análise de vizinhança cronológica (mediana local) e função de custo:
   * **31 registros** com dia/mês invertidos simultaneamente nas datas inicial e final (padrão americano `MM/DD`).
   * **23 registros** com erro de digitação no ano da data inicial (`ano -1`).
   * **14 registros** com data inicial e final lançadas invertidas.
   * **8 registros** adicionais com inversões pontuais de dia/mês ou ano.
   * **0 registros** pendentes para revisão manual após o processamento.
3. **Engenharia de Indicadores (KPIs):**
   * `Duracao_Dias`: tempo de execução de cada operação portuária em dias.
   * `ISG` (Índice de Satisfação Geral): média aritmética das 10 métricas de avaliação operacional (escala de 1 a 5).
4. **Simulação de Cenário de Negócio:** Criação da coluna multiplicadora `Peso_Cenario_Sem_Taxas` (`1.20`) para projetar o impacto de **+20% na demanda** operacional diante da eliminação de tarifas comerciais pelos EUA.

## Principais Resultados Obtidos

| Indicador | Valor | Observação |
| :--- | :--- | :--- |
| **Demanda Atual** | `1.118 registros` | Total de operações analisadas na base |
| **Demanda Simulada (+20%)** | `1.341 registros` | Projeção para cenário sem tarifas dos EUA |
| **Duração Média** | `0,60 dias` | Mediana de `0 dias` e máxima válida de `31 dias` |
| **ISG Médio** | `4,42 / 5,00` | Alta consistência na qualidade operacional |

## Estrutura do Repositório
* `main.py` — Script completo do pipeline de extração, limpeza heurística, cálculo de KPIs e exportação.
* `TRABALHO.xlsx` — Base de dados bruta original.
* `TRABALHO_TRATADO.xlsx` — Base tratada e formatada (`DD/MM/YYYY`), pronta para consumo no Power BI.

## Como Executar
1. Instale as dependências necessárias:
   ```bash
   pip install pandas openpyxl
