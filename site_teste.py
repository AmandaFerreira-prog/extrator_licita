import json
import glob
import os
import pandas as pd
from collections import Counter

os.makedirs("./json/empresas", exist_ok=True)

inicial = {}
geral = {
    "detalhe": {},
    "ranking_num_contratos": {},
    "ranking_gastos_totais": {},
    "ranking_objetos": {},
    "ranking_empresas": {}
}

# Função para arredondar valores para 2 casas decimais
def arredondar_valor(valor):
    return round(valor, 2)

# Dentro do loop de cada diário, onde você já coleta as informações das empresas e objetos
for path in glob.glob("/workspace/extrator_licita/data/diarios/*-atos.json"):
    with open(path, encoding="utf-8") as json_file:
        diarios = json.load(json_file)
        for diario in diarios:
            diario = json.loads(diario)
            id_municipio = diario["id"]
            nome_municipio = diario["municipio"].title()
            data_quebrada = diario["data_publicacao"].split("-")
            ano = int(data_quebrada[0])
            mes = int(data_quebrada[1])

            # Atualizando seção de detalhes do municipio
            dado_municipio = inicial.get(id_municipio, {})
            detalhe = dado_municipio.get("detalhe", {})
            detalhe_ano = detalhe.get(ano, {})
            detalhe_ano_resumo = detalhe_ano.get("resumo", {})
            detalhe_ano_mes = detalhe_ano.get(mes, {})
            detalhe_ano_resumo["num_diarios"] = detalhe_ano_resumo.get("num_diarios", 0) + 1
            detalhe_ano_mes["num_diarios"] = detalhe_ano_mes.get("num_diarios", 0) + 1
            empresas_mensais = []  # Lista para armazenar empresas mensais
            objetos_mensais = []   # Lista para armazenar objetos mensais
            gastos_mensais = []    # Lista para armazenar os gastos totais mensais

            for ato in diario["atos"]:
                ato = json.loads(ato)
                valores = ato["valores"]

                # Arredondando o total gasto
                total_gasto_ato = arredondar_valor(sum(valores))

                detalhe_ano_resumo["num_contratos"] = detalhe_ano_resumo.get("num_contratos", 0) + len(valores)
                detalhe_ano_resumo["total_gasto"] = detalhe_ano_resumo.get("total_gasto", 0) + total_gasto_ato
                detalhe_ano_mes["num_contratos"] = detalhe_ano_mes.get("num_contratos", 0) + len(valores)
                detalhe_ano_mes["total_gasto"] = detalhe_ano_mes.get("total_gasto", 0) + total_gasto_ato

                # Coletando empresas, objetos e valores
                for empresa in ato["partes_contratadas"]:
                    for objeto in ato["objetos"]:
                        empresas_mensais.append({
                            "objeto": objeto,
                            "empresa": empresa,
                            "valor_total": f"R$ {total_gasto_ato:,.2f}"
                        })

            # Atualizando os dados mensais no município
            detalhe_ano_mes["empresas_mensais"] = empresas_mensais  # Armazenando todas as empresas
            detalhe_ano_mes["objetos_mensais"] = objetos_mensais    # Armazenando todos os objetos

            detalhe_ano[mes] = detalhe_ano_mes
            detalhe[ano] = detalhe_ano
            detalhe_ano["resumo"] = detalhe_ano_resumo
            nome_municipio = nome_municipio.title()
            nome_municipio = nome_municipio.replace(" De ", " de ")
            nome_municipio = nome_municipio.replace(" Da ", " da ")
            nome_municipio = nome_municipio.replace(" Do ", " do ")
            inicial[id_municipio] = {
                "id": id_municipio,
                "nome": nome_municipio,
                "detalhe": detalhe,
            }

# Salvando os dados para renderização, agora incluindo todas as empresas
for id_municipio, dado in inicial.items():
    with open(f"./json/empresas/{id_municipio}.json", "w", encoding="utf-8") as json_file:
        json.dump(dado, json_file, indent=2, default=str, ensure_ascii=False)
