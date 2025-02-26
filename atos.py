import json
import re


def extrair(texto_diario: str):
    atos = []
    matches = re.findall(
        r"^[\s\S]*?Código Identificador:.*$(?:\n|)", texto_diario, re.MULTILINE)
    for match in matches:
        atos.append(AtoContratual(match.strip()))
    return atos


class AtoContratual:
    # Padrões para extrair informações de contratos
    #Todas as regex prontas para valores,partes contratadas e objeto do contrato
    #regexs criadas a partir da avaliação dos modelos de registro de contratos dentre todo o periodo(2014-2024)
    re_valor = r"(?i)(?:Valor:\s*|- |VALOR TOTAL:\s*|valor global de\s*|,?\s*Valor Global do presente Contrato é de\s*|VALOR DO CONTRATO:\s*|Remuneração:\s*|VALOR TOTAL ESTIMADO:\s*|valor de (?:R\$)?\s*|VALOR GLOBAL:?\s*)R\$\s*([0-9]{1,3}(?:\.[0-9]{3})*(?:,\d{2})?)(?!.+valor global)"
    re_partes = r"(?is)(?:(?<!A\s)CONTRATANTE\s(?!\:)|(?<!ao\s)CONTRATAD[oa]:?(?!\,| objeto:|\))\s?(?:\(A\):)?\s?|[–-] \d{2}\.\d{2}\.\d{2} [–-]|PB –(?:CONTRATANTE)?\s|PARTES:\s.*?(?:\d{4}-\d{2} |\d{3}.\d{3}.\d{3}-\d{2} )e\s(?:A EMPRESA\s[–-]\s[–-]?\s?)?|E A(?:S)? EMPRESA(?:S)?:\s|e Pessoa Física:\s|R\$\s\d{1,3}\.\d{1,3}\,\d{1,2}(?:\;\s|\se\s)|A EMPRESA\s[–-]\s[–-]?\s?)(.*?)(?:\d{11}|\,?\s+CNPJ|\,?\.?\s+CPF| - R\$|\.?\sCONTRATADA|- (?!.*?LTDA)|\.?\sFunção|– CONTRATO| –|Objeto|\s\.\s|\s- Contrato|CLÁUSULA|\-?\sEPP|\,?\s+?(?:inscrit[oa]|portador|pessoa))"
    re_objeto = r"(?is)(?:objeto:\s*)(.*?)(?:\.?\s*valor|\,?\s*celebrado|\.?\s*FUNDAMENTO LEGAL|PROCEDIMENTO DE CONTRATAÇÃO DIRETA:|\.\s)"
    re_contrato = r"(?i)(EXTRATO D[EO] CONTRATO|TERMO ADITIVO (?:AO|DE) CONTRATO|EXTRATO DE ADITIVO)[\s\S]*?"

    def __init__(self, texto: str):

        self.texto = texto
        self.partes_contratadas = []
        self.cod = self._extrai_cod(texto)
        self.valores = []
        self.objetos = []
        self.possui_contratos = self._possui_contratos()
        if self.possui_contratos:
            self._extrai_informacoes()



    def _extrai_cod(self, texto: str):
        matches = re.findall(r'Código Identificador:(.*)', texto)
        return matches[0].strip() if matches else None

    def _possui_contratos(self):
        return re.search(self.re_contrato, self.texto) is not None

    def _extrai_informacoes(self):
        # Extraindo valores
        valor_matches = re.findall(self.re_valor, self.texto)
        self.valores = [self.formatar_valor(valor) for valor in valor_matches]

        # Extraindo partes contratadas
        parte_matches = re.findall(self.re_partes, self.texto)
        for match in parte_matches:
            # match contém os nomes completos
            self.partes_contratadas.append(match.strip())

        # Extraindo objetos
        objeto_matches = re.findall(self.re_objeto, self.texto)
        self.objetos = [match.strip() for match in objeto_matches]

    def formatar_valor(self, valor: str) -> float:
        valor = valor.strip()
    
        # Ajusta os separadores de milhar e decimal corretamente
        if "," in valor and "." in valor:
            if valor.rfind(",") > valor.rfind("."):
                valor = valor.replace(".", "").replace(",", ".")  # Milhar: ponto, Decimal: vírgula
            else:
                valor = valor.replace(",", "")  # Remove separador de milhar
        else:
            valor = valor.replace(".", "").replace(",", ".")  # Converte para float-friendly

        # Converte para float
        return float(valor)

    def __str__(self):
        # Criar uma cópia do dicionário do objeto sem o campo 'texto'
        data = {k: v for k, v in self.__dict__.items() if k != "texto"}
        return json.dumps(data, indent=4, ensure_ascii=False)

