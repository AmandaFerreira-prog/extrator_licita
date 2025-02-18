#!/bin/bash

set -x  # Ativa o modo debug para exibir os comandos sendo executados
set -e  # Faz o script parar em caso de erro

ROOT_DIR=${PWD}  # Define o diretório raiz como o diretório atual
DATA_DIR=${ROOT_DIR}/area_test  # Define o diretório onde estão os arquivos

cd ${DATA_DIR}  # Navega para a pasta onde estão os diários

# Loop para processar cada arquivo JSON
for resultado in *-resumo-extracao.json
do
    # Gera o nome do arquivo de texto correspondente
    nome_base=$(basename "${resultado}" "-resumo-extracao.json")  # Remove o sufixo do JSON
    arquivo_txt="${nome_base}-extraido.txt"  # Constrói o nome do arquivo de texto

    python3 ${ROOT_DIR}/extrair_atos_test.py "${resultado}" "${arquivo_txt}" "${DATA_DIR}/${arquivo_txt}"
done
