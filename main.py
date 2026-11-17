import re
import sys
import itertools
import statistics
import pandas as pd
from openpyxl.styles import PatternFill

ARQUIVO_ENTRADA = sys.argv[1] if len(sys.argv) > 1 else 'TRABALHO.xlsx'
ARQUIVO_SAIDA = sys.argv[2] if len(sys.argv) > 2 else 'TRABALHO_TRATADO.xlsx'
HOJE = pd.Timestamp(sys.argv[3]) if len(sys.argv) > 3 else pd.Timestamp.today().normalize()

DURACAO_MAX = 45
PENALIDADE = 40
JANELA = 8
DIST_VIZINHO = 15
DIST_ISOLADA = 30
FATOR_DEMANDA = 1.20
EPOCA = pd.Timestamp('2000-01-01')
COLUNAS_NOTAS = [
    'Qualidade de serviço', 'Qualidade da Equipe', 'Cumprimento de Prazo',
    'Flexibilidade', 'Planejamento', 'Apresentação da Equipe',
    'Segurança', 'EPI', 'Liderança', 'Comunicação'
]


def limpa(ts):
    return ts if pd.isna(ts) else ts.normalize()


def serial(x):
    return limpa(pd.to_datetime(float(x), unit='D', origin='1899-12-30', errors='coerce'))


def ler_data(v):
    if pd.isna(v):
        return pd.NaT, False, ''
    if hasattr(v, 'year'):
        ts = pd.Timestamp(v).normalize()
        return ts, ts.day <= 12 and ts.day != ts.month, ''
    if isinstance(v, (int, float)):
        return serial(v), False, ''
    s = str(v).strip().replace(';', ':')
    if re.match(r'^\d{4}-\d{2}-\d{2}', s):
        return limpa(pd.to_datetime(s, errors='coerce')), False, ''
    s = re.sub(r'^(\d{1,2}/\d{1,2}/)(\d{3})(?=\s|$)',
               lambda m: m.group(1) + m.group(2)[:2] + '2' + m.group(2)[2:], s)
    m = re.match(r'^(\d{1,2})/(\d{1,2})/(\d{4})(?=\s|$)', s)
    if m:
        a, b, ano = map(int, m.groups())
        if a <= 12 < b:
            try:
                return pd.Timestamp(ano, a, b), False, 'texto em formato americano (mês > 12)'
            except ValueError:
                pass
    if re.match(r'^\d+(\.\d+)?$', s):
        return serial(s), False, ''
    return limpa(pd.to_datetime(s, dayfirst=True, errors='coerce')), False, ''


def opcoes(ts, amb):
    ops = [(ts, '', 0)]
    if amb:
        try:
            ops.append((ts.replace(month=ts.day, day=ts.month), 'dia/mês trocados', 1))
        except ValueError:
            pass
    for d in (-1, 1):
        try:
            ops.append((ts.replace(year=ts.year + d), f'ano {d:+d}', 1))
        except ValueError:
            pass
    return ops


def valida(a, b):
    return pd.notna(a) and pd.notna(b) and 0 <= (b - a).days <= DURACAO_MAX


def referencia(dias, ok, i):
    n = len(dias)
    for janela in range(JANELA, JANELA * 6 + 1, JANELA):
        viz = [dias[j] for j in range(max(0, i - janela), min(n, i + janela + 1)) if j != i and ok[j]]
        if len(viz) >= 5:
            ant = next((dias[j] for j in range(i - 1, max(-1, i - 49), -1) if ok[j]), None)
            post = next((dias[j] for j in range(i + 1, min(n, i + 49)) if ok[j]), None)
            return statistics.median(viz), ant, post
    return None


def dist_vizinho(ref, dia):
    return min([abs(dia - v) for v in ref[1:] if v is not None], default=float('inf'))


def corrige_linha(ini, fim, ini_amb, fim_amb, ref):
    if pd.isna(ini) or pd.isna(fim):
        return None
    original_ok = valida(ini, fim) and fim <= HOJE
    dia_ini = (ini - EPOCA).days
    melhor, melhor_custo = None, None
    for (ni, di, ci), (nf, df_, cf) in itertools.product(opcoes(ini, ini_amb), opcoes(fim, fim_amb)):
        ordens = [(ni, nf, 0)] if original_ok else [(ni, nf, 0), (nf, ni, 1)]
        for a, b, inv in ordens:
            if not valida(a, b) or b > HOJE:
                continue
            n_corr = ci + cf + inv
            dia_a = (a - EPOCA).days
            custo = n_corr * PENALIDADE
            if ref is not None:
                custo += 2 * abs(dia_a - ref[0]) + abs((b - EPOCA).days - ref[0])
            if original_ok and n_corr > 0 and (
                    ref is None
                    or dist_vizinho(ref, dia_ini) <= DIST_VIZINHO
                    or dist_vizinho(ref, dia_a) > DIST_VIZINHO):
                continue
            if melhor_custo is None or custo < melhor_custo:
                partes = (['Início e fim invertidos'] if inv else []) \
                    + ([f'Inicial: {di}'] if di else []) + ([f'Final: {df_}'] if df_ else [])
                melhor, melhor_custo = (a, b, '; '.join(partes)), custo
    if melhor is None or not melhor[2]:
        return None
    if not valida(ini, fim):
        return melhor + ('duração original inválida', 'alta')
    if fim > HOJE:
        return melhor + ('data posterior a hoje', 'baixa')
    return melhor + ('fora da ordem cronológica dos vizinhos', 'baixa')


df = pd.read_excel(ARQUIVO_ENTRADA)
df.columns = df.columns.str.strip()

lidas_ini = [ler_data(v) for v in df['Data Inicial']]
lidas_fim = [ler_data(v) for v in df['Data Final']]
ini_orig = [x[0] for x in lidas_ini]
fim_orig = [x[0] for x in lidas_fim]
ini_amb = [x[1] for x in lidas_ini]
fim_amb = [x[1] for x in lidas_fim]
n = len(df)

ini_atual, fim_atual = list(ini_orig), list(fim_orig)
ok = [valida(a, b) and not amb for a, b, amb in zip(ini_atual, fim_atual, ini_amb)]
for _ in range(5):
    dias = [None if pd.isna(x) else (x - EPOCA).days for x in ini_atual]
    correcoes = [corrige_linha(ini_orig[i], fim_orig[i], ini_amb[i], fim_amb[i],
                               referencia(dias, ok, i)) for i in range(n)]
    novo_ini = [c[0] if c else ini_orig[i] for i, c in enumerate(correcoes)]
    novo_fim = [c[1] if c else fim_orig[i] for i, c in enumerate(correcoes)]
    terminou = novo_ini == ini_atual and novo_fim == fim_atual
    ini_atual, fim_atual = novo_ini, novo_fim
    ok = [valida(a, b) and (not amb or (a, b) != (ini_orig[i], fim_orig[i]))
          for i, (a, b, amb) in enumerate(zip(ini_atual, fim_atual, ini_amb))]
    if terminou:
        break

motivos, evidencias, confiancas = [], [], []
for i, c in enumerate(correcoes):
    notas = [f'{nome}: {l[i][2]}' for nome, l in (('Inicial', lidas_ini), ('Final', lidas_fim)) if l[i][2]]
    motivo = '; '.join(notas + ([c[2]] if c else []))
    motivos.append(motivo)
    evidencias.append(c[3] if c else '')
    confiancas.append(c[4] if c else ('alta' if motivo else ''))

ini_s = pd.to_datetime(pd.Series(ini_atual, index=df.index))
fim_s = pd.to_datetime(pd.Series(fim_atual, index=df.index))

def texto_original(v):
    if pd.isna(v):
        return ''
    return v.strftime('%d/%m/%Y %H:%M') if hasattr(v, 'strftime') else str(v).strip()

saida = df.copy()
saida['Data Inicial Original'] = df['Data Inicial'].map(texto_original)
saida['Data Final Original'] = df['Data Final'].map(texto_original)
saida['Data Inicial'] = ini_s.dt.date
saida['Data Final'] = fim_s.dt.date
saida['Duracao_Dias'] = (fim_s - ini_s).dt.days
saida['ISG'] = df[COLUNAS_NOTAS].mean(axis=1)
saida['Peso_Cenario_Sem_Taxas'] = FATOR_DEMANDA
saida['Correcao_Motivo'] = motivos
saida['Correcao_Evidencia'] = evidencias
saida['Confianca_Correcao'] = confiancas

dur_ok = saida['Duracao_Dias'].between(0, DURACAO_MAX)
futura = (ini_s > HOJE) | (fim_s > HOJE)
dias_ini = (ini_s - EPOCA).dt.days
isolada = (dias_ini.diff().abs() > DIST_ISOLADA) & (dias_ini.diff(-1).abs() > DIST_ISOLADA)
saida['Revisar_Manual'] = ~dur_ok | futura | isolada | (saida['Confianca_Correcao'] == 'baixa')

print(f"Registros corrigidos automaticamente: {(saida['Correcao_Motivo'] != '').sum()}")
print(saida['Correcao_Motivo'].value_counts().drop('', errors='ignore').to_string())
revisar = saida[saida['Revisar_Manual']]
print(f"\nRegistros para revisar manualmente: {len(revisar)}")
if len(revisar):
    print(revisar[['Navio', 'Data Inicial Original', 'Data Final Original',
                   'Data Inicial', 'Data Final', 'Confianca_Correcao']].to_string())
validas = saida.loc[dur_ok, 'Duracao_Dias']
print(f"\nDuração Média: {validas.mean():.2f} dias")
print(f"Duração Mediana: {validas.median():.0f} dias")
print(f"Maior duração (válida): {validas.max():.0f} dias")
print(f"ISG Médio: {saida['ISG'].mean():.2f}")
print(f"Demanda Atual: {n} registros")
print(f"Demanda Simulada: {int(n * FATOR_DEMANDA)} registros")

amarelo = PatternFill('solid', start_color='FFF2CC')
with pd.ExcelWriter(ARQUIVO_SAIDA, engine='openpyxl') as writer:
    saida.to_excel(writer, sheet_name='Dados', index=False)
    ws = writer.sheets['Dados']
    colunas = list(saida.columns)
    cols_data = [colunas.index('Data Inicial') + 1, colunas.index('Data Final') + 1]
    col_revisar = colunas.index('Revisar_Manual') + 1
    for linha in range(2, n + 2):
        for col in cols_data:
            ws.cell(linha, col).number_format = 'DD/MM/YYYY'
            if ws.cell(linha, col_revisar).value:
                ws.cell(linha, col).fill = amarelo
    for col in cols_data:
        ws.column_dimensions[ws.cell(1, col).column_letter].width = 13
print('Planilha tratada exportada com sucesso!')