# Análise e Monitoramento de Serviços Marítimos — Atlantic Ocean Services

**Projeto acadêmico de extensão | Ciência da Computação — Universidade Estácio de Sá, Campus Campo Grande | Tópicos de Big Data em Python | 2026**

## Sobre o projeto

O projeto foi desenvolvido em colaboração com a **Atlantic Ocean Services**, empresa que atua no setor marítimo e portuário. Seu objetivo é **organizar, tratar e analisar registros operacionais** que estavam distribuídos em planilhas Excel e relatórios PDF, transformando-os em informações mais acessíveis para acompanhamento de serviços.

A solução combina **Python e Pandas** para tratamento dos dados, **Excel** para armazenamento intermediário e **Microsoft Power BI** para a visualização de indicadores e gráficos. Também inclui uma **simulação acadêmica de cenários para o primeiro semestre de 2027**.

## Base de dados

A base histórica consolidada utilizada no projeto reúne aproximadamente **1.118 registros e 18 colunas**, incluindo:

- Tipo de serviço, navio, cliente, estado e porto;
- Colaborador responsável e datas de início e término;
- Dez critérios de avaliação dos serviços.

Parte da consolidação precisou ser realizada manualmente, pois alguns relatórios PDF continham imagens ou informações de difícil extração.

> **Privacidade:** os dados operacionais foram disponibilizados pela empresa para a atividade acadêmica. A publicação de planilhas, PDFs ou informações identificáveis neste repositório deve ocorrer somente mediante autorização da Atlantic Ocean Services. Quando necessário, utilize dados fictícios ou anonimizados.

## Tecnologias utilizadas

| Ferramenta | Aplicação |
| --- | --- |
| Python | Scripts de tratamento e simulação |
| Pandas | Leitura, exploração, padronização e cálculos |
| Microsoft Excel | Organização e armazenamento intermediário |
| Microsoft Power BI | KPIs, gráficos e segmentações interativas |
| Visual Studio Code | Desenvolvimento e execução dos scripts |
| Git / GitHub | Versionamento e organização do projeto |

## Arquitetura e fluxo de dados

**Planilhas Excel + relatórios PDF → consolidação → tratamento com Pandas → planilha tratada → Power BI**

Em paralelo, a planilha tratada alimenta o script de simulação, que gera um segundo arquivo Excel para o gráfico de cenários de 2027.

### 1. Ingestão e análise exploratória

Os dados foram reunidos em uma planilha Excel. A estrutura foi examinada com comandos como `read_excel()`, `head()`, `shape`, `columns`, `info()` e `isnull().sum()`.

### 2. Tratamento dos registros

O script `tratar.py`, conforme descrito no relatório do projeto, aplica operações como:

- Remoção de espaços desnecessários nos textos e nomes das colunas com `str.strip()`;
- Padronização de nomes, localidades, portos e colaboradores;
- Conversão das avaliações **Excelente, Bom, Médio, Ruim e Muito ruim** para notas **5, 4, 3, 2 e 1**;
- Criação da coluna `Media Avaliacao` com a média das avaliações de cada registro, usando `mean(axis=1)`.

**Importante:** a conversão automática das datas apresentou problemas devido à variedade de formatos. Por isso, as datas foram **conferidas e padronizadas manualmente no Excel após a exportação da planilha tratada**. O projeto não removeu automaticamente registros parecidos, pois eles poderiam corresponder a serviços distintos. A duração dos serviços não foi calculada no escopo final.

### 3. Armazenamento

- `servicos_atlantic.xlsx`: base utilizada como entrada no tratamento;
- `servicos_atlantic_tratado.xlsx`: saída do tratamento, posteriormente conferida quanto às datas;
- `simulacao_2027.xlsx`: resultado dos cenários hipotéticos.

Os nomes acima seguem a documentação acadêmica. A estrutura e os nomes efetivamente publicados no repositório devem ser conferidos antes da entrega.

### 4. Dashboard no Power BI

O painel contém **2 KPIs**:

1. **Total de serviços realizados:** contagem de registros de serviços;
2. **Média das avaliações:** média da coluna `Media Avaliacao`, em escala de 1 a 5.

Foram utilizados **4 tipos de gráficos**:

- **Barras:** quantidade de serviços por categoria;
- **Rosca:** distribuição de serviços por porto;
- **Colunas:** evolução mensal dos serviços históricos;
- **Linhas:** comparação dos cenários simulados de crescimento para 2027.

A versão atualizada do dashboard possui **4 segmentações**: **período, tipo de serviço, porto e cliente**. O filtro por cliente foi acrescentado após a redação inicial do relatório acadêmico.

> As segmentações do histórico não devem ser interpretadas como previsões específicas da simulação para cada porto, cliente ou categoria. Se alguma avaliação da base tiver sido simulada, ela não deve ser apresentada como satisfação real de clientes.

## Simulação acadêmica de 2027

O script `simulacao.py` utiliza a base tratada e calcula a **média mensal dos serviços registrados entre janeiro e setembro de 2026**:

`media_mensal = total_de_servicos_no_periodo / 9`

Com essa referência, são construídos três cenários **hipotéticos** para janeiro a junho de 2027:

| Cenário | Crescimento total atingido em junho |
| --- | ---: |
| Conservador | 10% |
| Moderado | 25% |
| Otimista | 50% |

O crescimento é distribuído gradualmente pelos seis meses. Considerando `indice_mes = 0` em janeiro e `indice_mes = 5` em junho, a lógica de cálculo é:

`servicos_estimados = round(media_mensal * (1 + taxa * indice_mes / 5))`

Os resultados são exportados para `simulacao_2027.xlsx` e exibidos em um gráfico de linhas no Power BI.

**Os percentuais não são previsões econômicas, metas da empresa nem resultados de um modelo causal.** Foram definidos como hipóteses de um exercício acadêmico, em um contexto possível de redução de tarifas comerciais e de custos de combustível marítimo.

## Como executar os scripts

Com Python e os arquivos de entrada disponíveis **de forma autorizada**, instale as dependências principais:

```bash
pip install pandas openpyxl
```

Execute o tratamento:

```bash
python tratar.py
```

**Antes da simulação**, confira e padronize as datas no arquivo tratado, conforme o procedimento adotado no projeto. Evite executar novamente `tratar.py` sobre a versão final sem preservar as correções manuais.

Depois, execute:

```bash
python simulacao.py
```

O arquivo `simulacao_2027.xlsx` poderá então ser importado para o Power BI. **Esses comandos pressupõem que os scripts e os arquivos estejam na pasta de trabalho esperada**; ajuste os caminhos, se necessário.

## Integrantes e responsabilidades

| Integrante | Responsabilidades no projeto |
| --- | --- |
| **Erik de Oliveira Novaes Moreira** | Contato com a empresa, levantamento e consolidação de dados, participação nos códigos Python/Pandas |
| **Lucas de Paula Chaves Lopes** | Análise exploratória, identificação de inconsistências e apoio ao tratamento |
| **Kauan dos Santos Melo** | Definição dos indicadores, participação no tratamento e apoio ao Power BI |
| **Douglas Meireles S Silva** | Gráficos, organização do dashboard, testes, estruturação do GitHub e documentação técnica |
| **Cristiane Almeida dos Santos** | Documentação acadêmica, evidências, apoio à análise e revisão do relatório |

**Orientação acadêmica:** Prof. Lucas Antunes Floriano.

## Resultados e possibilidades de evolução

O projeto resultou em uma base histórica organizada, um dashboard com indicadores e visualizações e uma simulação didática para 2027.

Entre as possibilidades futuras estão a atualização periódica da base, a automatização da ingestão, a adoção de um banco de dados e a inclusão de indicadores financeiros, **condicionada à disponibilidade e autorização dos dados pela empresa**.

---

**Finalidade:** atividade acadêmica de extensão da disciplina de Tópicos de Big Data em Python — Universidade Estácio de Sá, 2026.
