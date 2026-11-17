import pandas as pd

df = pd.read_excel('TRABALHO.xlsx')
df.columns = df.columns.str.strip()
df['Data Inicial'] = df['Data Inicial'].astype(str).str.replace('/205 ', '/2025 ')
df['Data Inicial DT'] = pd.to_datetime(df['Data Inicial'], dayfirst=True, errors='coerce').astype('datetime64[s]')
df['Data Final DT'] = pd.to_datetime(df['Data Final'], dayfirst=True, errors='coerce').astype('datetime64[s]')

def corrige_americano(dt):
    if pd.isna(dt): return dt
    if dt.day <= 12:
        try:
            return dt.replace(month=dt.day, day=dt.month)
        except ValueError:
            return dt
    return dt

mask_negativa = df['Data Final DT'] < df['Data Inicial DT']
df.loc[mask_negativa, 'Data Final DT'] = df.loc[mask_negativa, 'Data Final DT'].apply(corrige_americano)

df['Duracao_Dias'] = (df['Data Final DT'] - df['Data Inicial DT']).dt.days

mask_ainda_negativa = df['Duracao_Dias'] < 0

temp = df.loc[mask_ainda_negativa, 'Data Inicial DT'].copy() 
df.loc[mask_ainda_negativa, 'Data Inicial DT'] = df.loc[mask_ainda_negativa, 'Data Final DT']
df.loc[mask_ainda_negativa, 'Data Final DT'] = temp
df['Duracao_Dias'] = (df['Data Final DT'] - df['Data Inicial DT']).dt.days

kpi_duracao = df['Duracao_Dias'].mean()
print(f"Duração Média: {kpi_duracao:.2f} dias")

colunas_notas = ['Qualidade de serviço', 'Qualidade da Equipe', 'Cumprimento de Prazo', 'Flexibilidade', 'Planejamento', 'Apresentação da Equipe', 'Segurança', 'EPI', 'Liderança', 'Comunicação']
df['ISG'] = df[colunas_notas].mean(axis=1)
print(f"ISG Médio: {df['ISG'].mean():.2f}")

df['Peso_Cenario_Sem_Taxas'] = 1.20
demanda_simulada = int(len(df) * 1.20)
print(f"Demanda Atual: {len(df)} registros")
print(f"Demanda Simulada: {demanda_simulada} registros")

df.to_excel('TRABALHO_TRATADO.xlsx', index=False)
print("Planilha tratada exportada com sucesso!")