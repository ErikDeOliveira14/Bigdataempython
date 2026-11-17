
import pandas as pd

# 1 - Abrindo a planilha tratada
df = pd.read_excel("servicos_atlantic_tratado.xlsx")

print("Total de registros na planilha:")
print(len(df))


# 2 - Lendo as datas para fazer a contagem
# Isso nao altera as datas do arquivo Excel
datas = pd.to_datetime(
    df["Data Inicial"],
    dayfirst=True,
    format="mixed",
    errors="coerce"
)

# Verificando se alguma data nao foi reconhecida
print("Datas nao reconhecidas:")
print(datas.isna().sum())

if datas.isna().sum() > 0:
    print("Confira as datas antes de continuar.")
    quit()


# 3 - Selecionando os servicos de 2026
dados_2026 = df[
    (datas.dt.year == 2026) &
    (datas.dt.month <= 9)
]

print("Servicos de janeiro a setembro de 2026:")
print(len(dados_2026))


# 4 - Calculando a media mensal
total = len(dados_2026)

media = total / 9

print("Media mensal de servicos:")
print(round(media, 2))


# 5 - Criando os meses de 2027
meses = [
    "01/01/2027",
    "01/02/2027",
    "01/03/2027",
    "01/04/2027",
    "01/05/2027",
    "01/06/2027"
]

# Criando uma nova tabela
simulacao = pd.DataFrame()

simulacao["Mes"] = meses

# Usado para ordenar os meses no Power BI
simulacao["Ordem"] = [1, 2, 3, 4, 5, 6]


# 6 - Criando as listas dos cenarios
cenario10 = []
cenario25 = []
cenario50 = []


# 7 - Calculando o crescimento dos servicos
for i in range(6):

    # Crescimento de 10%
    valor10 = round(media * (1 + 0.10 * i / 5))

    # Crescimento de 25%
    valor25 = round(media * (1 + 0.25 * i / 5))

    # Crescimento de 50%
    valor50 = round(media * (1 + 0.50 * i / 5))

    # Guardando os resultados nas listas
    cenario10.append(valor10)
    cenario25.append(valor25)
    cenario50.append(valor50)


# 8 - Colocando os resultados na tabela
simulacao["Cenario 10%"] = cenario10

simulacao["Cenario 25%"] = cenario25

simulacao["Cenario 50%"] = cenario50


# 9 - Mostrando os resultados
print("Simulacao para 2027:")
print(simulacao)


# 10 - Salvando no Excel
simulacao.to_excel("simulacao_2027.xlsx", index=False)

print("Simulacao criada com sucesso!")
