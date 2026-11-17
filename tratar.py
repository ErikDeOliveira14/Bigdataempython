
import pandas as pd

# 1 - Abrindo a planilha
df = pd.read_excel("servicos_atlantic.xlsx")

print("Primeiras linhas:")
print(df.head())

print("Quantidade de linhas e colunas:")
print(df.shape)

print("Nomes das colunas:")
print(df.columns)

# 2 - Verificando dados vazios
print("Dados vazios:")
print(df.isnull().sum())


# 3 - Removendo espaços dos nomes das colunas
df.columns = df.columns.str.strip()


# 4 - Tratando a coluna Serviços
df["Serviços"] = df["Serviços"].str.strip()

print(df["Serviços"].value_counts())


# 5 - Tratando a coluna Navio
df["Navio"] = df["Navio"].str.strip()

print(df["Navio"].head())


# 6 - Tratando a coluna Cliente
df["Cliente"] = df["Cliente"].str.strip()

print(df["Cliente"].unique())


# 7 - Tratando a coluna Estado
df["Estado"] = df["Estado"].str.strip()

df["Estado"] = df["Estado"].replace({
    "Paranagua": "Paranaguá",
    "ESPIRITO SANTO": "Espírito Santo",
    "SALVADOR": "Salvador"
})

print(df["Estado"].value_counts())


# 8 - Tratando a coluna Porto
df["Porto"] = df["Porto"].str.strip()

df["Porto"] = df["Porto"].replace(
    "SALVADOR", "CODEBA"
)

print(df["Porto"].value_counts())


# 9 - Tratando a coluna Colaborador
df["Colaborador"] = df["Colaborador"].str.strip()

df["Colaborador"] = df["Colaborador"].str.upper()

# Padronizando colaboradores que trabalharam juntos
df["Colaborador"] = df["Colaborador"].str.replace(
    " E ", " / ", regex=False
)

print(df["Colaborador"].unique())


# 10 - Tratando as avaliações
notas = {
    "Excelente": 5,
    "Bom": 4,
    "Médio": 3,
    "Ruim": 2,
    "Muito ruim": 1
}

# Colunas de avaliação
colunas_notas = [
    "Qualidade de serviço",
    "Qualidade da Equipe",
    "Cumprimento de Prazo",
    "Flexibilidade",
    "Planejamento",
    "Apresentação da Equipe",
    "Segurança",
    "EPI",
    "Liderança",
    "Comunicação"
]

# Convertendo as avaliações para números
for coluna in colunas_notas:

    df[coluna] = df[coluna].astype(str).str.strip()

    df[coluna] = df[coluna].replace(notas)

    df[coluna] = pd.to_numeric(
        df[coluna],
        errors="coerce"
    )

print("Avaliações convertidas:")
print(df[colunas_notas].head())


# 11 - Verificando avaliações inválidas
print("Avaliações inválidas:")
print(df[colunas_notas].isnull().sum())


# 12 - Criando a média de avaliação por serviço
df["Media Avaliacao"] = df[colunas_notas].mean(axis=1).round(2)

print("Média das avaliações:")
print(df[["Serviços", "Navio", "Media Avaliacao"]].head())


# 13 - Salvando a planilha tratada
df.to_excel(
    "servicos_atlantic_tratado.xlsx",
    index=False
)

print("Planilha tratada com sucesso!")
