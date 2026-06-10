"""
Análise comparativa entre Branch/Function/Line Coverage e Java Tokens Coverage
Analisa a evolução da cobertura a cada 1% dos testes executados em ordem aleatória
Suporta análise para branch, function e line coverage
"""

import os
import random
import numpy as np
import matplotlib.pyplot as plt


def load_coverage(filepath):
    """Carrega a cobertura (branches, functions ou lines)"""
    test_cases = []
    with open(filepath, 'r') as f:
        for line in f:
            entities = set(line.strip().split())
            test_cases.append(entities)
    return test_cases


def load_java_tokens(filepath):
    """Carrega os Java tokens (tokens únicos por teste)"""
    tokens = []
    with open(filepath, 'r') as f:
        for line in f:
            token_set = set(line.strip().split())
            tokens.append(token_set)
    return tokens


def analyze_java_tokens_coverage(coverage_file, tokens_file, output_prefix, entity_name='branch'):
    """
    Analisa a evolução da cobertura a cada 1% dos testes
    """
    print("Carregando dados...")
    coverage_data = load_coverage(coverage_file)
    java_tokens = load_java_tokens(tokens_file)

    total_tests = len(coverage_data)
    print(f"Total de casos de teste: {total_tests}")

    # Criar ordem aleatória
    indices = list(range(total_tests))
    random.shuffle(indices)
    print("Ordem aleatória gerada")

    # Calcular cobertura a cada 1%
    percentages = []
    entity_coverage = []
    tokens_coverage = []
    unique_tokens_ratio = []

    print("\nAnalisando cobertura...")

    for pct in range(1, 101):
        num_tests = max(1, int(total_tests * pct / 100))
        current_indices = indices[:num_tests]

        # Entity Coverage: entidades únicas acumuladas
        accumulated_entities = set()
        for idx in current_indices:
            accumulated_entities.update(coverage_data[idx])

        # Tokens Coverage: tokens únicos acumulados
        accumulated_tokens = set()
        for idx in current_indices:
            accumulated_tokens.update(java_tokens[idx])

        percentages.append(pct)
        entity_coverage.append(len(accumulated_entities))
        tokens_coverage.append(len(accumulated_tokens))

        # Razão de tokens únicos por teste
        total_tokens_in_tests = sum(len(java_tokens[idx]) for idx in current_indices)
        unique_ratio = (len(accumulated_tokens) / total_tokens_in_tests * 100) if total_tokens_in_tests > 0 else 0
        unique_tokens_ratio.append(unique_ratio)

        if pct % 10 == 0:
            print(f"  {pct}% - {num_tests} testes - "
                  f"{len(accumulated_entities)} {entity_name}s - "
                  f"{len(accumulated_tokens)} tokens únicos")

    print("\nGerando gráfico de comparação...")

    # Calcular porcentagens de cobertura
    max_entity = max(entity_coverage)
    max_tokens = max(tokens_coverage)

    entity_coverage_pct = [(x / max_entity) * 100 for x in entity_coverage]
    tokens_coverage_pct = [(x / max_tokens) * 100 for x in tokens_coverage]

    # Criar gráfico de comparação
    plt.figure(figsize=(12, 7))

    # Label dinâmico baseado na entidade
    entity_label = f"{entity_name.capitalize()} Coverage"

    # Plotar as duas curvas
    plt.plot(percentages, entity_coverage_pct,
             'b-', linewidth=2.5, label=entity_label, marker='o', markersize=3, markevery=5)
    plt.plot(percentages, tokens_coverage_pct,
             'g--', linewidth=2.5, label='Java Tokens Coverage', marker='^', markersize=3, markevery=5)

    # Linha de referência diagonal
    plt.plot([0, 100], [0, 100], 'k:', linewidth=1, alpha=0.3, label='Referência (y=x)')

    # Configurações do gráfico
    plt.xlabel('Porcentagem de Casos de Teste Executados (%)', fontsize=12, fontweight='bold')
    plt.ylabel('Porcentagem de Cobertura (%)', fontsize=12, fontweight='bold')

    # Título dinâmico
    title_parts = output_prefix.split(os.sep)
    title_name = title_parts[-1] if title_parts else output_prefix
    plt.title(f'Comparação: {entity_label} vs Java Tokens Coverage\n({title_name})',
              fontsize=14, fontweight='bold', pad=20)

    plt.grid(True, alpha=0.3, linestyle='--')
    plt.legend(fontsize=11, loc='lower right')

    plt.xlim(0, 100)
    plt.ylim(0, 100)

    # Adicionar anotações em pontos chave
    key_points = [10, 20, 50, 100]
    for pct in key_points:
        idx = pct - 1

        # Anotação para Entity Coverage
        plt.annotate(f'{entity_coverage_pct[idx]:.1f}%',
                    xy=(pct, entity_coverage_pct[idx]),
                    xytext=(10, 10), textcoords='offset points',
                    fontsize=9, color='blue',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='lightblue', alpha=0.7),
                    arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0', color='blue', lw=1))

        # Anotação para Java Tokens Coverage
        plt.annotate(f'{tokens_coverage_pct[idx]:.1f}%',
                    xy=(pct, tokens_coverage_pct[idx]),
                    xytext=(10, -20), textcoords='offset points',
                    fontsize=9, color='green',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='lightgreen', alpha=0.7),
                    arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0', color='green', lw=1))

    # Calcular correlação
    correlation = np.corrcoef(entity_coverage_pct, tokens_coverage_pct)[0, 1]

    # Adicionar informações estatísticas
    text_info = f'Correlação: {correlation:.4f}\n'
    text_info += f'Total {entity_name.capitalize()}s: {max_entity:,}\n'
    text_info += f'Total Java Tokens: {max_tokens:,}'

    plt.text(0.02, 0.98, text_info,
             transform=plt.gca().transAxes,
             fontsize=10,
             verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

    plt.tight_layout()

    # Criar diretório de saída se não existir
    output_dir = os.path.dirname(output_prefix)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Salvar gráfico
    plot_file = f'{output_prefix}_java_tokens_comparison.png'
    plt.savefig(plot_file, dpi=300, bbox_inches='tight')
    print(f"Gráfico salvo: {plot_file}")
    plt.close()

    # Salvar dados em arquivo TSV
    output_file = f'{output_prefix}_java_tokens_analysis.tsv'
    with open(output_file, 'w') as f:
        entity_col_name = f"{entity_name.capitalize()}s_Covered"
        f.write(f'Percentage\tTests_Executed\t{entity_col_name}\tJava_Tokens_Coverage\t'
                'Unique_Tokens_Ratio\n')
        for i in range(len(percentages)):
            num_tests = max(1, int(total_tests * percentages[i] / 100))
            f.write(f'{percentages[i]}\t{num_tests}\t{entity_coverage[i]}\t'
                   f'{tokens_coverage[i]}\t{unique_tokens_ratio[i]:.2f}\n')

    print(f"Dados salvos: {output_file}")

    # Estatísticas finais
    print("\n" + "="*60)
    print("ESTATÍSTICAS FINAIS")
    print("="*60)
    print(f"Total de casos de teste: {total_tests}")
    print(f"Total de {entity_name}s únicos: {max_entity}")
    print(f"Total de Java tokens únicos: {max_tokens}")
    print(f"Taxa de compressão ({entity_name}/tokens): {max_entity/max_tokens:.2f}x")
    print(f"Média de tokens por teste: {np.mean([len(s) for s in java_tokens]):.1f}")

    # Correlação entre as métricas
    print(f"\nCorrelação ({entity_label} vs Java Tokens Coverage): {correlation:.4f}")

    if correlation > 0.9:
        print(f"[OK] Alta correlacao: Java tokens coverage e excelente proxy para {entity_name} coverage")
    elif correlation > 0.7:
        print(f"[OK] Correlacao boa: Java tokens coverage captura bem a cobertura")
    elif correlation > 0.5:
        print(f"[WARN] Correlacao moderada: Java tokens coverage captura parcialmente a cobertura")
    else:
        print(f"[LOW] Baixa correlacao: Java tokens coverage pode nao refletir bem a cobertura")

    print("="*60)

    return correlation


if __name__ == "__main__":
    # Configurar seed para reprodutibilidade
    random.seed(42)
    np.random.seed(42)

    # Lista de projetos e entidades
    projects = [
        'chart_v0', 'closure_v0', 'lang_v0', 'math_v0', 'time_v0'
    ]

    entities = ['branch', 'function', 'line']

    print("="*60)
    print("ANÁLISE DE COBERTURA: Coverage vs Java Tokens")
    print("Processando todos os projetos e entidades com dados bbox")
    print("="*60 + "\n")

    total_analyses = len(projects) * len(entities)
    current = 0
    results = {}

    for project in projects:
        project_base = project.split('_')[0]
        results[project] = {}

        for entity in entities:
            current += 1

            coverage_file = f'input/{project}/{project_base}-{entity}.txt'
            tokens_file = f'input/{project}/{project_base}-bbox.tokens'

            # Verificar se os arquivos existem
            if not os.path.exists(coverage_file):
                print(f"[{current}/{total_analyses}] [WARN] IGNORADO: {coverage_file} nao encontrado\n")
                continue

            if not os.path.exists(tokens_file):
                print(f"[{current}/{total_analyses}] [WARN] IGNORADO: {tokens_file} nao encontrado (execute extract_java_tokens.py primeiro)\n")
                continue

            print(f"[{current}/{total_analyses}] Processando {project} - {entity}")
            print("-" * 60)
            print(f"Coverage file: {coverage_file}")
            print(f"Tokens file: {tokens_file}")

            # Definir caminho de saída: correlation_java_tokens/{entity}_cov/{project}/{project}_{entity}
            output_prefix = os.path.join('correlation_java_tokens', f'{entity}_cov', project, f'{project}_{entity}')

            try:
                r = analyze_java_tokens_coverage(coverage_file, tokens_file, output_prefix, entity_name=entity)
                results[project][entity] = r
                print(f"[OK] Concluido: {project} - {entity}\n")
            except Exception as e:
                print(f"[ERROR] ERRO ao processar {project} - {entity}: {e}\n")
                results[project][entity] = None

    print("="*60)
    print("ANÁLISE COMPLETA!")
    print(f"Resultados salvos em: correlation_java_tokens/{{branch,function,line}}_cov/")
    print("="*60)
