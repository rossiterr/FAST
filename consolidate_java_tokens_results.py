"""
Consolida os resultados de correlação de Java tokens de todos os projetos
Gera uma tabela TSV resumida
"""

import os
import re
import numpy as np


def extract_correlation_from_file(output_prefix, entity_name='branch'):
    """
    Extrai o valor de correlação do arquivo TSV gerado pela análise
    """
    tsv_file = f'{output_prefix}_java_tokens_analysis.tsv'

    if not os.path.exists(tsv_file):
        return None

    correlations = []
    try:
        with open(tsv_file, 'r') as f:
            lines = f.readlines()
            # Pula header
            for line in lines[1:]:
                parts = line.strip().split('\t')
                if len(parts) >= 4:
                    try:
                        pct = int(parts[0])
                        entity_cov = int(parts[2])
                        tokens_cov = int(parts[3])
                        correlations.append((pct, entity_cov, tokens_cov))
                    except:
                        pass

        if len(correlations) >= 2:
            entity_covs = [c[1] for c in correlations]
            tokens_covs = [c[2] for c in correlations]

            # Normalizar para percentuais
            max_entity = max(entity_covs)
            max_tokens = max(tokens_covs)

            entity_pct = [(x / max_entity * 100) if max_entity > 0 else 0 for x in entity_covs]
            tokens_pct = [(x / max_tokens * 100) if max_tokens > 0 else 0 for x in tokens_covs]

            # Calcular correlação de Pearson
            r = np.corrcoef(entity_pct, tokens_pct)[0, 1]
            return r if not np.isnan(r) else None

    except Exception as e:
        print(f"⚠️  Erro ao extrair correlação de {tsv_file}: {e}")
        return None

    return None


def consolidate_results():
    """
    Consolida todos os resultados em uma tabela resumida
    """
    projects = [
        'chart_v0', 'closure_v0', 'lang_v0', 'math_v0', 'time_v0'
    ]

    entities = ['branch', 'function', 'line']

    print("=" * 80)
    print("CONSOLIDAÇÃO DE RESULTADOS - JAVA TOKENS")
    print("=" * 80)
    print()

    results = {}

    # Extrair correlações de cada arquivo
    print("Extraindo correlações...")
    for project in projects:
        results[project] = {}
        for entity in entities:
            output_prefix = os.path.join('correlation_java_tokens', f'{entity}_cov', project, f'{project}_{entity}')
            r = extract_correlation_from_file(output_prefix, entity_name=entity)
            results[project][entity] = r

            if r is not None:
                print(f"  [OK] {project:15} - {entity:10}: r = {r:.4f}")
            else:
                print(f"  [ERROR] {project:15} - {entity:10}: erro ao extrair")

    print()

    # Gerar tabela consolidada
    output_file = 'correlation_tables/java_tokens_correlations.tsv'
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, 'w') as f:
        f.write('Project\tBranch\tFunction\tLine\n')
        for project in projects:
            branch = results[project].get('branch')
            function = results[project].get('function')
            line = results[project].get('line')

            branch_str = f"{branch:.4f}" if branch is not None else "N/A"
            function_str = f"{function:.4f}" if function is not None else "N/A"
            line_str = f"{line:.4f}" if line is not None else "N/A"

            f.write(f'{project}\t{branch_str}\t{function_str}\t{line_str}\n')

    print(f"[OK] Tabela consolidada salva: {output_file}")
    print()

    # Imprimir resumo
    print("=" * 80)
    print("RESUMO DOS RESULTADOS")
    print("=" * 80)
    print()

    # Calcular médias
    for entity in entities:
        values = [results[proj][entity] for proj in projects if results[proj][entity] is not None]
        if values:
            mean_r = np.mean(values)
            std_r = np.std(values)
            print(f"{entity.upper():10} Coverage")
            print(f"  Média:     {mean_r:.4f}")
            print(f"  Desvio:    {std_r:.4f}")
            print(f"  Mín:       {min(values):.4f}")
            print(f"  Máx:       {max(values):.4f}")
            print()

    # Tabela formatada
    print("Tabela de Correlações (Java Tokens vs White-Box):")
    print()
    print(f"{'Project':<15} {'Branch':<10} {'Function':<10} {'Line':<10}")
    print("-" * 50)

    for project in projects:
        branch = results[project].get('branch')
        function = results[project].get('function')
        line = results[project].get('line')

        branch_str = f"{branch:.4f}" if branch is not None else "N/A"
        function_str = f"{function:.4f}" if function is not None else "N/A"
        line_str = f"{line:.4f}" if line is not None else "N/A"

        print(f"{project:<15} {branch_str:<10} {function_str:<10} {line_str:<10}")

    print()
    print("=" * 80)
    print("CONSOLIDAÇÃO CONCLUÍDA!")
    print("=" * 80)

    return results


if __name__ == "__main__":
    consolidate_results()
