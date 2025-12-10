"""
Análise comparativa entre Branch Coverage e Shingles Coverage
Analisa a evolução da cobertura a cada 1% dos testes executados em ordem aleatória
"""

import os
import random
import numpy as np
import matplotlib.pyplot as plt


def load_branch_coverage(filepath):
    """Carrega a cobertura de branches original"""
    test_cases = []
    with open(filepath, 'r') as f:
        for line in f:
            branches = set(line.strip().split())
            test_cases.append(branches)
    return test_cases


def load_shingles(filepath):
    """Carrega os shingles (hashes das substrings k=5)"""
    shingles = []
    with open(filepath, 'r') as f:
        for line in f:
            shingle_set = set(line.strip().split())
            shingles.append(shingle_set)
    return shingles


def analyze_shingles_coverage(branch_file, shingles_file, output_prefix):
    """
    Analisa a evolução da cobertura a cada 1% dos testes
    """
    print("Carregando dados...")
    branches = load_branch_coverage(branch_file)
    shingles = load_shingles(shingles_file)
    
    total_tests = len(branches)
    print(f"Total de casos de teste: {total_tests}")
    
    # Criar ordem aleatória
    indices = list(range(total_tests))
    random.shuffle(indices)
    print("Ordem aleatória gerada")
    
    # Calcular cobertura a cada 1%
    percentages = []
    branch_coverage = []
    shingles_coverage = []
    unique_shingles_ratio = []
    
    print("\nAnalisando cobertura...")
    
    for pct in range(1, 101):
        num_tests = max(1, int(total_tests * pct / 100))
        current_indices = indices[:num_tests]
        
        # Branch Coverage: branches únicos acumulados
        accumulated_branches = set()
        for idx in current_indices:
            accumulated_branches.update(branches[idx])
        
        # Shingles Coverage: shingles únicos acumulados
        accumulated_shingles = set()
        for idx in current_indices:
            accumulated_shingles.update(shingles[idx])
        
        percentages.append(pct)
        branch_coverage.append(len(accumulated_branches))
        shingles_coverage.append(len(accumulated_shingles))
        
        # Razão de shingles únicos por teste
        total_shingles_in_tests = sum(len(shingles[idx]) for idx in current_indices)
        unique_ratio = (len(accumulated_shingles) / total_shingles_in_tests * 100) if total_shingles_in_tests > 0 else 0
        unique_shingles_ratio.append(unique_ratio)
        
        if pct % 10 == 0:
            print(f"  {pct}% - {num_tests} testes - "
                  f"{len(accumulated_branches)} branches - "
                  f"{len(accumulated_shingles)} shingles únicos")
    
    print("\nGerando gráfico de comparação...")
    
    # Calcular porcentagens de cobertura
    max_branch = max(branch_coverage)
    max_shingles = max(shingles_coverage)
    
    branch_coverage_pct = [(x / max_branch) * 100 for x in branch_coverage]
    shingles_coverage_pct = [(x / max_shingles) * 100 for x in shingles_coverage]
    
    # Criar gráfico de comparação
    plt.figure(figsize=(12, 7))
    
    # Plotar as duas curvas
    plt.plot(percentages, branch_coverage_pct, 
             'b-', linewidth=2.5, label='Branch Coverage', marker='o', markersize=3, markevery=5)
    plt.plot(percentages, shingles_coverage_pct, 
             'g--', linewidth=2.5, label='Shingles Coverage', marker='^', markersize=3, markevery=5)
    
    # Linha de referência diagonal
    plt.plot([0, 100], [0, 100], 'k:', linewidth=1, alpha=0.3, label='Referência (y=x)')
    
    # Configurações do gráfico
    plt.xlabel('Porcentagem de Casos de Teste Executados (%)', fontsize=12, fontweight='bold')
    plt.ylabel('Porcentagem de Cobertura (%)', fontsize=12, fontweight='bold')
    
    # Título dinâmico
    title_parts = output_prefix.split(os.sep)
    title_name = title_parts[-1] if title_parts else output_prefix
    plt.title(f'Comparação: Branch Coverage vs Shingles Coverage\n({title_name})', 
              fontsize=14, fontweight='bold', pad=20)
    
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.legend(fontsize=11, loc='lower right')
    
    plt.xlim(0, 100)
    plt.ylim(0, 100)
    
    # Adicionar anotações em pontos chave
    key_points = [10, 20, 50, 100]
    for pct in key_points:
        idx = pct - 1
        
        # Anotação para Branch Coverage
        plt.annotate(f'{branch_coverage_pct[idx]:.1f}%',
                    xy=(pct, branch_coverage_pct[idx]),
                    xytext=(10, 10), textcoords='offset points',
                    fontsize=9, color='blue',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='lightblue', alpha=0.7),
                    arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0', color='blue', lw=1))
        
        # Anotação para Shingles Coverage
        plt.annotate(f'{shingles_coverage_pct[idx]:.1f}%',
                    xy=(pct, shingles_coverage_pct[idx]),
                    xytext=(10, -20), textcoords='offset points',
                    fontsize=9, color='green',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='lightgreen', alpha=0.7),
                    arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0', color='green', lw=1))
    
    # Calcular correlação
    correlation = np.corrcoef(branch_coverage_pct, shingles_coverage_pct)[0, 1]
    
    # Adicionar informações estatísticas
    compression_ratio = max_branch / max_shingles if max_shingles > 0 else 0
    text_info = f'Correlação: {correlation:.4f}\n'
    text_info += f'Total Branches: {max_branch:,}\n'
    text_info += f'Total Shingles: {max_shingles:,}'
    
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
    plot_file = f'{output_prefix}_shingles_comparison.png'
    plt.savefig(plot_file, dpi=300, bbox_inches='tight')
    print(f"Gráfico salvo: {plot_file}")
    plt.close()
    
    # Salvar dados em arquivo TSV
    output_file = f'{output_prefix}_shingles_coverage.tsv'
    with open(output_file, 'w') as f:
        f.write('Percentage\tTests_Executed\tBranches_Covered\tShingles_Coverage\t'
                'Unique_Shingles_Ratio\n')
        for i in range(len(percentages)):
            num_tests = max(1, int(total_tests * percentages[i] / 100))
            f.write(f'{percentages[i]}\t{num_tests}\t{branch_coverage[i]}\t'
                   f'{shingles_coverage[i]}\t{unique_shingles_ratio[i]:.2f}\n')
    
    print(f"Dados salvos: {output_file}")
    
    # Estatísticas finais
    print("\n" + "="*60)
    print("ESTATÍSTICAS FINAIS")
    print("="*60)
    print(f"Total de casos de teste: {total_tests}")
    print(f"Total de branches únicos: {max_branch}")
    print(f"Total de shingles únicos: {max_shingles}")
    print(f"Taxa de compressão (branch/shingles): {compression_ratio:.2f}x")
    print(f"Média de shingles por teste: {np.mean([len(s) for s in shingles]):.1f}")
    
    # Correlação entre as métricas
    print(f"\nCorrelação (Branch Coverage vs Shingles Coverage): {correlation:.4f}")
    
    if correlation > 0.9:
        print("✓ Alta correlação: Shingles coverage é excelente proxy para branch coverage")
    elif correlation > 0.7:
        print("~ Correlação boa: Shingles coverage captura bem a cobertura")
    elif correlation > 0.5:
        print("⚠ Correlação moderada: Shingles coverage captura parcialmente a cobertura")
    else:
        print("✗ Baixa correlação: Shingles coverage pode não refletir bem a cobertura")
    
    print("="*60)


if __name__ == "__main__":
    # Configurar seed para reprodutibilidade
    random.seed(42)
    np.random.seed(42)
    
    # Lista de projetos
    projects = [
        'chart_v0', 'closure_v0', 'lang_v0', 'math_v0', 'time_v0',
        'flex_v3', 'grep_v3', 'gzip_v1', 'make_v1', 'sed_v6'
    ]
    
    print("="*60)
    print("ANÁLISE DE COBERTURA: Branch vs Shingles")
    print("Processando projetos com dados bbox")
    print("="*60 + "\n")
    
    total_analyses = len(projects)
    current = 0
    
    for project in projects:
        current += 1
        project_base = project.split('_')[0]
        
        branch_file = f'input/{project}/{project_base}-branch.txt'
        shingles_file = f'input/{project}/{project_base}-bbox.shingles'
        
        # Verificar se os arquivos existem
        if not os.path.exists(branch_file):
            print(f"[{current}/{total_analyses}] ⚠️  IGNORADO: {branch_file} não encontrado\n")
            continue
        
        if not os.path.exists(shingles_file):
            print(f"[{current}/{total_analyses}] ⚠️  IGNORADO: {shingles_file} não encontrado\n")
            continue
        
        print(f"[{current}/{total_analyses}] Processando {project}")
        print("-" * 60)
        print(f"Branch file: {branch_file}")
        print(f"Shingles file: {shingles_file}")
        
        # Definir caminho de saída
        output_prefix = os.path.join('correlation_hashed_shingles', project, f'{project}_bbox')
        
        try:
            analyze_shingles_coverage(branch_file, shingles_file, output_prefix)
            print(f"✓ Concluído: {project}\n")
        except Exception as e:
            print(f"✗ ERRO ao processar {project}: {e}\n")
    
    print("="*60)
    print("ANÁLISE COMPLETA!")
    print(f"Resultados salvos em: correlation_hashed_shingles/")
    print("="*60)
