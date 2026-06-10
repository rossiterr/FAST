"""
Extrai tokens Java de cada arquivo bbox e gera arquivos .tokens
Cada linha do arquivo .tokens contém os tokens únicos de um teste
"""

import os
import sys
try:
    import javalang
except ImportError:
    print("❌ Erro: javalang não está instalado")
    print("Execute: pip install javalang")
    sys.exit(1)


def extract_tokens_from_code(code_string):
    """
    Extrai tokens Java únicos de uma string de código
    Retorna: conjunto de tokens como strings
    """
    if not code_string or len(code_string) < 5:
        return set()

    try:
        # javalang.tokenize retorna um generator
        token_generator = javalang.tokenize(code_string)
        token_values = []
        for token in token_generator:
            if hasattr(token, 'value') and token.value:
                token_values.append(str(token.value))
        return set(token_values)
    except Exception:
        # Se falhar, tenta extrair tokens manualmente (fallback)
        # Palavras-chave Java comuns
        import re
        words = re.findall(r'\b[a-zA-Z_$][a-zA-Z0-9_$]*\b', code_string)
        return set(words)


def generate_tokens_file(input_bbox_file, output_tokens_file):
    """
    Lê arquivo bbox.txt (um teste por linha) e gera bbox.tokens
    Cada linha do .tokens contém tokens separados por espaço
    """
    if not os.path.exists(input_bbox_file):
        print(f"❌ Arquivo não encontrado: {input_bbox_file}")
        return False

    total_tests = 0
    failed_parses = 0

    with open(input_bbox_file, 'r', encoding='utf-8', errors='ignore') as f_in, \
         open(output_tokens_file, 'w', encoding='utf-8') as f_out:

        for line_num, line in enumerate(f_in, 1):
            code = line.strip()
            if not code:
                f_out.write('\n')
                continue

            tokens = extract_tokens_from_code(code)

            if not tokens:
                failed_parses += 1

            # Escreve tokens separados por espaço (uma linha por teste)
            f_out.write(' '.join(sorted(tokens)) + '\n')
            total_tests += 1

    return total_tests, failed_parses


if __name__ == "__main__":
    projects = [
        'chart_v0', 'closure_v0', 'lang_v0', 'math_v0', 'time_v0'
    ]

    print("=" * 70)
    print("EXTRAÇÃO DE TOKENS JAVA")
    print("=" * 70)
    print()

    total_generated = 0

    for project in projects:
        project_base = project.split('_')[0]
        input_file = f'input/{project}/{project_base}-bbox.txt'
        output_file = f'input/{project}/{project_base}-bbox.tokens'

        print(f"Processando: {project}")
        print(f"  Input:  {input_file}")
        print(f"  Output: {output_file}")

        total_tests, failed = generate_tokens_file(input_file, output_file)

        if total_tests:
            print(f"  [OK] Sucesso: {total_tests} testes processados")
            if failed > 0:
                print(f"  [WARN] {failed} testes falharam no parsing (ignorados)")
            total_generated += 1
            print()
        else:
            print(f"  [ERROR] Erro ao processar arquivo\n")

    print("=" * 70)
    print(f"CONCLUÍDO: {total_generated}/{len(projects)} projetos processados")
    print("=" * 70)
