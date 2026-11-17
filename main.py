import re
import sys
import itertools
import pandas as pd

ARQUIVO_ENTRADA = sys.argv[1] if len(sys.argv) > 1 else 'TRABALHO.xlsx'
ARQUIVO_SAIDA = sys.argv[2] if len(sys.argv) > 2 else 'TRABALHO_TRATADO.xlsx'

DURACAO_MAX_VALIDA = 45
PENALIDADE_CORRECAO = 40
JANELA_VIZINHOS = 8
LIMITE_REVISAO = 365
DISTANCIA_CRONOLOGICA_MAX = 30

df = pd.read_excel(ARQUIVO_ENTRADA)
df.columns = df.columns.str.strip()


def parse_data(v):
    if pd.isna(v):
        return pd.NaT, False

    if hasattr(v, 'year'):
        ts = pd.Timestamp(v)
        return ts, (ts.day <= 12 and ts.day != ts.month)

    if isinstance(v, (int, float)):
        return pd.to_datetime(v, unit='D', origin='1899-12-30', errors='coerce'), False

    s = str(v).strip().replace(';', ':')
    if not s:
        return pd.NaT, False

    if re.match(r'^\d{4}-\d{2}-\d{2}', s):
        return pd.to_datetime(s, errors='coerce'), False

    s = re.sub(
        r'^(\d{1,2}/\d{1,2}/)(\d{3})(?=\s|$)',
        lambda m: m.group(1) + m.group(2)[:2] + '2' + m.group(2)[2:],
        s
    )

    if re.match(r'^\d+(\.\d+)?$', s):
        return pd.to_datetime(float(s), unit='D', origin='1899-12-30', errors='coerce'), False

    return pd.to_datetime(s, dayfirst=True, errors='coerce'), False


def parse_com_nota(v):
    if isinstance(v, str):
        t = v.strip()
        t = re.sub(
            r'^(\d{1,2}/\d{1,2}/)(\d{3})(?=\s|$)',
            lambda m: m.group(1) + m.group(2)[:2] + '2' + m.group(2)[2:],
            t
        )
        m = re.match(r'^(\d{1,2})/(\d{1,2})/(\d{4})(?=\s|$)', t)
        if m:
            a, b, ano = int(m.group(1)), int(m.group(2)), int(m.group(3))
            if a <= 12 < b:
                try:
                    return pd.Timestamp(ano, a, b), False, 'texto em formato americano (mês > 12)'
                except ValueError:
                    pass
    ts, amb = parse_data(v)
    return ts, amb, ''


ini_p = df['Data Inicial'].apply(parse_com_nota)
fim_p = df['Data Final'].apply(parse_com_nota)

df['Data Inicial DT'] = pd.to_datetime(ini_p.str[0], errors='coerce').dt.normalize()
df['Data Final DT'] = pd.to_datetime(fim_p.str[0], errors='coerce').dt.normalize()
df['_ini_amb'] = ini_p.str[1].astype(bool)
df['_fim_amb'] = fim_p.str[1].astype(bool)


def troca_dia_mes(ts):
    try:
        return ts.replace(month=ts.day, day=ts.month)
    except ValueError:
        return None


def muda_ano(ts, delta):
    try:
        return ts.replace(year=ts.year + delta)
    except ValueError:
        return None


def opcoes(ts, ambigua):
    ops = [(ts, '', 0)]
    if ambigua:
        t = troca_dia_mes(ts)
        if t is not None:
            ops.append((t, 'dia/mês trocados', 1))
    for d in (-1, 1):
        t = muda_ano(ts, d)
        if t is not None:
            ops.append((t, f'ano {d:+d}', 1))
    return ops


def referencia_local(serie_dias, usar_mascara, i, minimo=5):
    janela = JANELA_VIZINHOS
    while janela <= JANELA_VIZINHOS * 6:
        ini = max(0, i - janela)
        fim = min(len(serie_dias), i + janela + 1)
        viz = [
            serie_dias[j] for j in range(ini, fim)
            if j != i and usar_mascara[j] and serie_dias[j] is not None
        ]
        if len(viz) >= minimo:
            return float(pd.Series(viz).median())
        janela += JANELA_VIZINHOS
    return None


EPOCA = pd.Timestamp('2000-01-01')


def corrige_linha(i, ini, fim, ini_amb, fim_amb, ref):
    if pd.isna(ini) or pd.isna(fim):
        return None
    asis_valido = 0 <= (fim - ini).days <= DURACAO_MAX_VALIDA
    melhor, melhor_custo = None, None
    for (ni, di, ci), (nf, df_, cf) in itertools.product(opcoes(ini, ini_amb), opcoes(fim, fim_amb)):
        ordens = [(ni, nf, 0)]
        if not asis_valido:
            ordens.append((nf, ni, 1))
        for a, b, inv in ordens:
            dur = (b - a).days
            if not (0 <= dur <= DURACAO_MAX_VALIDA):
                continue
            dist = dist_fim = None
            if ref is not None:
                dist = abs((a - EPOCA).days - ref)
                dist_fim = abs((b - EPOCA).days - ref)
            n_corr = ci + cf + inv
            if asis_valido and n_corr > 0 and (dist is None or dist > DISTANCIA_CRONOLOGICA_MAX):
                continue
            custo = n_corr * PENALIDADE_CORRECAO + (2 * dist + dist_fim if dist is not None else 0)
            if melhor_custo is None or custo < melhor_custo:
                partes = []
                if inv:
                    partes.append('Início e fim invertidos')
                if di:
                    partes.append(f'Inicial: {di}')
                if df_:
                    partes.append(f'Final: {df_}')
                evid = 'duração original inválida' if not asis_valido else 'fora da ordem cronológica dos vizinhos'
                melhor, melhor_custo = (a, b, '; '.join(partes), evid), custo
    return melhor


n = len(df)
ini_orig = [pd.Timestamp(x[0]).normalize() if not pd.isna(x[0]) else pd.NaT for x in ini_p]
fim_orig = [pd.Timestamp(x[0]).normalize() if not pd.isna(x[0]) else pd.NaT for x in fim_p]
ini_amb = df['_ini_amb'].tolist()
fim_amb = df['_fim_amb'].tolist()


def consistente(a, b):
    return (not pd.isna(a)) and (not pd.isna(b)) and 0 <= (b - a).days <= DURACAO_MAX_VALIDA


ini_atual, fim_atual = list(ini_orig), list(fim_orig)
mascara = [consistente(ini_atual[i], fim_atual[i]) and not ini_amb[i] for i in range(n)]

for passada in range(3):
    ini_dias = [(x - EPOCA).days if not pd.isna(x) else None for x in ini_atual]
    novos_ini, novos_fim, motivos, evidencias = list(ini_atual), list(fim_atual), [''] * n, [''] * n
    for i in range(n):
        ref = referencia_local(ini_dias, mascara, i)
        r = corrige_linha(i, ini_orig[i], fim_orig[i], ini_amb[i], fim_amb[i], ref)
        if r is not None:
            novos_ini[i], novos_fim[i], motivos[i], evidencias[i] = r
    mudou = sum(1 for i in range(n) if novos_ini[i] != ini_atual[i] or novos_fim[i] != fim_atual[i])
    ini_atual, fim_atual = novos_ini, novos_fim
    mascara = [consistente(ini_atual[i], fim_atual[i]) for i in range(n)]
    if mudou == 0:
        break

df['Data Inicial DT'] = pd.to_datetime(pd.Series(ini_atual, index=df.index))
df['Data Final DT'] = pd.to_datetime(pd.Series(fim_atual, index=df.index))

notas_ini = ini_p.str[2].tolist()
notas_fim = fim_p.str[2].tolist()
for i in range(n):
    extra = [
        p for p in (
            f'Inicial: {notas_ini[i]}' if notas_ini[i] else '',
            f'Final: {notas_fim[i]}' if notas_fim[i] else ''
        ) if p
    ]
    if extra:
        motivos[i] = '; '.join(extra + ([motivos[i]] if motivos[i] else []))

serie_motivos = pd.Series(motivos, index=df.index)
print(f"Registros corrigidos automaticamente: {(serie_motivos != '').sum()}")
print(serie_motivos.value_counts().drop('', errors='ignore').to_string())

df['Duracao_Dias'] = (df['Data Final DT'] - df['Data Inicial DT']).dt.days
revisar_mask = (df['Duracao_Dias'] < 0) | (df['Duracao_Dias'] > LIMITE_REVISAO) | df['Duracao_Dias'].isna()
suspeitas = df[revisar_mask]
print(f"\nRegistros para revisar manualmente: {len(suspeitas)}")
if len(suspeitas):
    print(suspeitas[['Navio', 'Data Inicial', 'Data Final', 'Duracao_Dias']].to_string())

validas = df.loc[~revisar_mask, 'Duracao_Dias']
print(f"\nDuração Média: {validas.mean():.2f} dias")
print(f"Duração Mediana: {validas.median():.0f} dias")
print(f"Maior duração (válida): {validas.max():.0f} dias")

colunas_notas = [
    'Qualidade de serviço', 'Qualidade da Equipe', 'Cumprimento de Prazo',
    'Flexibilidade', 'Planejamento', 'Apresentação da Equipe',
    'Segurança', 'EPI', 'Liderança', 'Comunicação'
]
df['ISG'] = df[colunas_notas].mean(axis=1)
print(f"ISG Médio: {df['ISG'].mean():.2f}")

df['Peso_Cenario_Sem_Taxas'] = 1.20
demanda_simulada = int(len(df) * 1.20)
print(f"Demanda Atual: {len(df)} registros")
print(f"Demanda Simulada: {demanda_simulada} registros")

df = df.drop(columns=['_ini_amb', '_fim_amb'])

df['Data Inicial'] = df['Data Inicial DT'].dt.date
df['Data Final'] = df['Data Final DT'].dt.date
df = df.drop(columns=['Data Inicial DT', 'Data Final DT'])

with pd.ExcelWriter(ARQUIVO_SAIDA, engine='openpyxl') as writer:
    df.to_excel(writer, index=False)
    ws = writer.sheets['Sheet1']
    for nome in ('Data Inicial', 'Data Final'):
        col = list(df.columns).index(nome) + 1
        for linha in range(2, len(df) + 2):
            ws.cell(linha, col).number_format = 'DD/MM/YYYY'
        ws.column_dimensions[ws.cell(1, col).column_letter].width = 13
print("Planilha tratada exportada com sucesso!")