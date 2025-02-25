def formatar_valor(valor: str):
    #Formata manualmente para o padrão brasileiro (milhar com ".", decimal com ",")
    valor_formatado = f"{float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    return valor_formatado

# Testes
valores = ["3954335.05", "395433505.0", "39543.35", "3395433.5"]

for v in valores:
    try:
        print(f"{v} -> {formatar_valor(v)}")
        print(type(formatar_valor(v)))
    except ValueError as e:
        print(f"Erro ao processar '{v}': {e}")

# Função para arredondar valores para 2 casas decimais
def arredondar_valor(valor):
    return round(valor, 2)
