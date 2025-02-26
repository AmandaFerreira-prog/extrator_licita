import re

import diario_municipal

# No final do regex, existe uma estrutura condicional para pegar nomes de municipios compostos..
# Exceções Notáveis
re_nomes_municipios = (
    r"ESTADO DA PARAÍBA(?:| )\n{1,2}(?:PREFEITURA MUNICIPAL DE|MUNICÍPIO DE) (?!.*\s* – )(\S.*?)(?=\s*(?=\n*(?:COMISS[AÃ]O|GABINETE|SECRET[ÁA]RIA|INEXIGIBILIDADE|EXTRATO|C[ÂA]MARA|ATA|PREFEITURA|CONS[ÓO]RCIO|CMAS|CPL|ADITIVO|TERMO|PREG[ÃA]O|ADMINISTRAÇ[ÃA]O|DECRETO|CONSELHO|AVISO|LICITAÇ[ÃA]O|SETOR|FUNDO|IPAM|INSTITUTO|EDITAL|FUNPREVE|DEPARTAMENTO|CONS[ÓO]RCIO|IPSEP|PREG[ÃA]O|TERMO|PORTARIA|HOMOLOGAÇ[ÃA]O)))")


def extrair_diarios_municipais(texto_diario: str):
    texto_diario_slice = texto_diario.lstrip().splitlines()

    # Processamento
    linhas_apagar = []  # slice de linhas a ser apagadas ao final.
    pb_header = texto_diario_slice[0]
    pb_header_count = 0
    codigo_count = 0
    codigo_total = texto_diario.count("Código Identificador")

    for num_linha, linha in enumerate(texto_diario_slice):
        # Remoção do cabeçalho PB, porém temos que manter a primeira aparição.
        if linha.startswith(pb_header):
            pb_header_count += 1
            if pb_header_count > 1:
                linhas_apagar.append(num_linha)

        # Remoção das linhas finais
        if codigo_count == codigo_total:
            linhas_apagar.append(num_linha)
        elif linha.startswith("Código Identificador"):
            codigo_count += 1

    # Apagando linhas do slice
    texto_diario_slice = [l for n, l in enumerate(
        texto_diario_slice) if n not in linhas_apagar]

    # Inserindo o cabeçalho no diário de cada município.
    texto_diarios = {}
    nomes_municipios = re.findall(
        re_nomes_municipios, texto_diario, re.MULTILINE)
    for municipio in nomes_municipios:
        municipio = diario_municipal.Municipio(municipio)
        texto_diarios[municipio] = pb_header + '\n\n'

    num_linha = 0
    municipio_atual = None
    while num_linha < len(texto_diario_slice):
        linha = texto_diario_slice[num_linha].rstrip()

        if linha.startswith("ESTADO DA PARAÍBA"):
            nome = nome_municipio(texto_diario_slice, num_linha)
            if nome is not None:
                municipio_atual = diario_municipal.Municipio(nome)

        # Só começa, quando algum muncípio for encontrado.
        if municipio_atual is None:
            num_linha += 1
            continue

        # Conteúdo faz parte de um muncípio
        texto_diarios[municipio_atual] += linha + '\n'
        num_linha += 1

    diarios = []
    for municipio, diario in texto_diarios.items():
        diarios.append(diario_municipal.Diario(municipio, pb_header, diario))

    return diarios


def nome_municipio(texto_diario_slice: slice, num_linha: int):
    texto = '\n'.join(texto_diario_slice[num_linha:num_linha+10])
    match = re.findall(re_nomes_municipios, texto, re.MULTILINE)
    if len(match) > 0:
        return match[0].strip().replace('\n', '')
    return None
