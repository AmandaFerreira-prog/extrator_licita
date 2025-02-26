import sys
import json
import atos
import diario_municipal


class asobject(object):
    def __init__(self, d):
        self.__dict__.update(d)


if __name__ == "__main__":
    # Verificando argumentos passados para o programa.
    if len(sys.argv) < 4:
        print("Usage: python extrair_atos_test.py <caminho para arquivo com resultado de extração> <desc> <path>", file=sys.stderr)
        sys.exit(1)

    # Argumentos recebidos.
    path_resultado = sys.argv[1]
    desc = sys.argv[2]
    path = sys.argv[3]

    # Lendo o arquivo de entrada.
    with open(path_resultado, "r", encoding="utf8") as in_file:
        resultados = json.load(in_file)

    diarios_processados = []

    # Processando cada resultado.
    for res in resultados:
        # Transformando a string JSON em dicionário
        res = json.loads(res)  # Desserializando a string JSON em um dicionário
        res = asobject(res)  # Convertendo o dicionário para um objeto

        diario = diario_municipal.Diario(
            diario_municipal.Municipio(res.municipio),
            res.cabecalho,
            res.texto,
        )

        diario.atos = atos.extrair(res.texto)

        # Criando a estrutura de atos no formato correto.
        atos_processados = []
        for ato in diario.atos:
            ato_json = json.loads(str(ato))  # Transformando o ato em dicionário.
            atos_processados.append({
                "partes_contratadas": ato_json.get("partes_contratadas", []),
                "cod": ato_json.get("cod", ""),
                "valores": ato_json.get("valores", []),
                "objetos": ato_json.get("objetos", []),
                "possui_contratos": ato_json.get("possui_contratos", False),
            })

        diarios_processados.append({
            "municipio": res.municipio,
            "atos": atos_processados,
        })

    # Criando a saída final.
    
    # Ajustando para acessar o primeiro item de resultados corretamente
    cabecalho = resultados[0]["cabecalho"] if len(resultados) > 0 else "Cabeçalho não encontrado"

    saida = {
        "desc": desc,
        "path": path,
        "cabecalho": cabecalho,  # Usando o cabeçalho do primeiro diário.
        "diarios": diarios_processados,
    }

    # Salvando o arquivo de saída.
    nome_arquivo = path_resultado.replace("-resumo-extracao.json", "-atos-final.json")
    with open(nome_arquivo, "w", encoding="utf8") as out_file:
        json.dump(saida, out_file, indent=2, ensure_ascii=False)
