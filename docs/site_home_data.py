import json
import glob
import os
import pandas as pd
from collections import Counter

os.makedirs("./docs/site/dados", exist_ok=True)

inicial = {}
geral = {
    "detalhe": {},
    "ranking_num_contratos": {},
    "ranking_gastos_totais": {},
    "ranking_objetos": {},
    "ranking_empresas": {}
}

def formatar_valor(valor) -> str:
    # Formata manualmente para o padrão brasileiro (milhar com ".", decimal com ",")
    valor_formatado = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    return valor_formatado

for path in glob.glob("../data/diarios/*-atos.json"):
    with open(path, encoding="utf-8") as json_file:
        diarios = json.load(json_file)
        for diario in diarios:
            diario = json.loads(diario)
            id_municipio = diario["id"]
            nome_municipio = diario["municipio"].title()
            data_quebrada = diario["data_publicacao"].split("-")
            ano, mes, dia = map(int, data_quebrada)
            
            detalhe = inicial.setdefault(id_municipio, {"id": id_municipio, "nome": nome_municipio, "detalhe": {}})["detalhe"].setdefault(ano, {"resumo": {}, mes: {}})
            detalhe["resumo"]["num_diarios"] = detalhe["resumo"].get("num_diarios", 0) + 1
            detalhe[mes]["num_diarios"] = detalhe[mes].get("num_diarios", 0) + 1
            
            empresas_mensais, objetos_mensais = [], []
            for ato in diario["atos"]:
                ato = json.loads(ato)
                total_gasto_ato = sum(ato["valores"])
                
                detalhe["resumo"]["num_contratos"] = detalhe["resumo"].get("num_contratos", 0) + len(ato["valores"])
                detalhe["resumo"]["total_gasto"] = detalhe["resumo"].get("total_gasto", 0) + total_gasto_ato
                detalhe[mes]["num_contratos"] = detalhe[mes].get("num_contratos", 0) + len(ato["valores"])
                detalhe[mes]["total_gasto"] = detalhe[mes].get("total_gasto", 0) + total_gasto_ato
                
                empresas_mensais.extend(ato["partes_contratadas"])
                objetos_mensais.extend(ato["objetos"])
            
            detalhe[mes]["top_3_empresas"] = [item[0] for item in Counter(empresas_mensais).most_common(3)]
            detalhe[mes]["top_3_objetos"] = [item[0] for item in Counter(objetos_mensais).most_common(3)]
            detalhe[ano] = detalhe

def calcular_top10(tipo):
    todos = []
    for dado in inicial.values():
        for detalhe in dado["detalhe"].values():
            for mes, dados_mes in detalhe.items():
                if mes == "resumo":
                    continue
                todos.extend(dados_mes.get(f"top_3_{tipo}", []))
    return dict(Counter(todos).most_common(10))

geral["ranking_objetos"] = calcular_top10("objetos")
geral["ranking_empresas"] = calcular_top10("empresas")

for id_municipio, dado in inicial.items():
    num_diarios, num_contratos, total_gasto = 0, 0, 0
    todas_empresas, todos_objetos = [], []
    
    for detalhe in dado["detalhe"].values():
        resumo = detalhe.get("resumo", {})
        num_diarios += resumo.get("num_diarios", 0)
        total_gasto += resumo.get("total_gasto", 0)
        num_contratos += resumo.get("num_contratos", 0)
        
        for mes, dados_mes in detalhe.items():
            if mes == "resumo":
                continue
            todas_empresas.extend(dados_mes.get("top_3_empresas", []))
            todos_objetos.extend(dados_mes.get("top_3_objetos", []))
    
    inicial[id_municipio]["resumo"] = {
        "num_diarios": num_diarios,
        "num_contratos": num_contratos,
        "total_gasto": formatar_valor(total_gasto),
        "top_5_empresas": dict(Counter(todas_empresas).most_common(5)),
        "top_5_objetos": dict(Counter(todos_objetos).most_common(5))
    }

def top5(arg):
    df = pd.DataFrame.from_dict(inicial, orient='index')
    df = df[df["id"] != 'geral'].sort_values(by=['resumo'], ascending=False, key=lambda x: x.str.get(arg))
    return {i+1: {"nome": row["nome"], "num": formatar_valor(row["resumo"][arg])} for i, (_, row) in enumerate(df.head(5).iterrows())}

inicial['geral']['ranking_contratos'] = top5("num_contratos")
inicial['geral']['ranking_gastos_totais'] = top5("total_gasto")
inicial['geral']['ranking_objetos'] = geral["ranking_objetos"]
inicial['geral']['ranking_empresas'] = geral["ranking_empresas"]

for id_municipio, dado in inicial.items():
    with open(f"./docs/site/dados/{id_municipio}.json", "w", encoding="utf-8") as json_file:
        json.dump(dado, json_file, indent=2, default=str, ensure_ascii=False)
