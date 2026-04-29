"""
Análise comparativa entre Coverage (Branch/Function/Line) e Signature Coverage (Black-Box)
Analisa a evolução da cobertura a cada 1% dos testes executados em ordem aleatória
Usa signatures geradas a partir de hashed shingles (black-box) ao invés de white-box
"""

import os
import random
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict


def load_coverage(filepath):
    """Carrega a cobertura (branches, functions ou lines)"""
    test_cases = []
    with open(filepath, 'r') as f:
        for line in f:
            entities = set(line.strip().split())
            test_cases.append(entities)
    return test_cases


def load_signatures(filepath):
    """Carrega as assinaturas MinHash"""
    signatures = []
    with open(filepath, 'r') as f:
        for line in f:
            sig = line.strip().split()
            signatures.append(sig)
    return signatures


def calculate_signature_coverage(signatures_subset):
    """
    Calcula a cobertura de assinaturas: conta valores únicos em cada posição hash
    Similar ao branch coverage, conta quantos "branches de assinatura" foram vistos
    """
    if not signatures_subset:
        return 0
    
    num_hashes = len(signatures_subset[0])
    unique_values_per_position = [set() for _ in range(num_hashes)]
    
    for sig in signatures_subset:
        for pos in range(num_hashes):
            unique_values_per_position[pos].add(sig[pos])
    
    # Total de valores únicos em todas as posições
    total_unique = sum(len(s) for s in unique_values_per_position)
    return total_unique


def calculate_signature_uniqueness(signatures_subset):
    """
    Calcula o número de assinaturas únicas (completamente diferentes)
    """
    unique_sigs = set()
    for sig in signatures_subset:
        unique_sigs.add(tuple(sig))
    return len(unique_sigs)


def analyze_coverage(coverage_file, signature_file, output_prefix='chart_v0_branch', entity_name='branch'):
    """
    Analisa a evolução da cobertura a cada 1% dos testes
    """
    print("Carregando dados...")
    coverage_data = load_coverage(coverage_file)
    signatures = load_signatures(signature_file)
    
    total_tests = len(coverage_data)
    print(f"Total de casos de teste: {total_tests}")
    
    # Criar ordem aleatória
    indices = list(range(total_tests))
    random.shuffle(indices)
    print("Ordem aleatória gerada")
    
    # Calcular cobertura a cada 1%
    percentages = []
    entity_coverage = []
    signature_coverage = []
    signature_uniqueness = []
    unique_signatures_ratio = []
    
    print("\nAnalisando cobertura...")
    
    for pct in range(1, 101):
        num_tests = max(1, int(total_tests * pct / 100))
        current_indices = indices[:num_tests]
        
        # Entity Coverage: entidades únicas acumuladas
        accumulated_entities = set()
        for idx in current_indices:
            accumulated_entities.update(coverage_data[idx])
        
        # Signature Metrics
        current_signatures = [signatures[idx] for idx in current_indices]
        sig_coverage = calculate_signature_coverage(current_signatures)
        uniqueness = calculate_signature_uniqueness(current_signatures)
        
        percentages.append(pct)
        entity_coverage.append(len(accumulated_entities))
        signature_coverage.append(sig_coverage)
        signature_uniqueness.append(uniqueness)
        unique_signatures_ratio.append(uniqueness / num_tests * 100)
        
        if pct % 10 == 0:
            print(f"  {pct}% - {num_tests} testes - "
                  f"{len(accumulated_entities)} {entity_name}s cobertos - "
                  f"{sig_coverage} sig values cobertos - "
                  f"{uniqueness} sigs únicas")
    
    print("\nGerando gráfico de comparação...")
    
    # Calcular porcentagens de cobertura
    max_entity = max(entity_coverage)
    max_sig = max(signature_coverage)
    
    entity_coverage_pct = [(x / max_entity) * 100 for x in entity_coverage]
    signature_coverage_pct = [(x / max_sig) * 100 for x in signature_coverage]
    
    # Criar gráfico de comparação
    plt.figure(figsize=(12, 7))
    
    # Label dinâmico baseado na entidade
    entity_label = f"{entity_name.capitalize()} Coverage"
    
    # Plotar as duas curvas
    plt.plot(percentages, entity_coverage_pct, 
             'b-', linewidth=2.5, label=entity_label, marker='o', markersize=3, markevery=5)
    plt.plot(percentages, signature_coverage_pct, 
             'r--', linewidth=2.5, label='Signature Coverage (Black-Box)', marker='s', markersize=3, markevery=5)
    
    # Linha de referência diagonal (cobertura ideal = % testes)
    plt.plot([0, 100], [0, 100], 'k:', linewidth=1, alpha=0.3, label='Referência (y=x)')
    
    # Configurações do gráfico
    plt.xlabel('Porcentagem de Casos de Teste Executados (%)', fontsize=12, fontweight='bold')
    plt.ylabel('Porcentagem de Cobertura (%)', fontsize=12, fontweight='bold')
    
    # Título dinâmico baseado no output_prefix
    title_parts = output_prefix.split(os.sep)
    title_name = title_parts[-1] if title_parts else output_prefix
    plt.title(f'Comparação: {entity_label} vs Signature Coverage (Black-Box)\n({title_name})', 
              fontsize=14, fontweight='bold', pad=20)
    
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.legend(fontsize=11, loc='lower right')
    
    # Definir limites dos eixos
    plt.xlim(0, 100)
    plt.ylim(0, 100)
    
    # Adicionar anotações em pontos chave
    key_points = [10, 20, 50, 100]
    for pct in key_points:
        idx = pct - 1  # índice da lista (0-indexed)
        
        # Anotação para Entity Coverage
        plt.annotate(f'{entity_coverage_pct[idx]:.1f}%',
                    xy=(pct, entity_coverage_pct[idx]),
                    xytext=(10, 10), textcoords='offset points',
                    fontsize=9, color='blue',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='lightblue', alpha=0.7),
                    arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0', color='blue', lw=1))
        
        # Anotação para Signature Coverage
        plt.annotate(f'{signature_coverage_pct[idx]:.1f}%',
                    xy=(pct, signature_coverage_pct[idx]),
                    xytext=(10, -20), textcoords='offset points',
                    fontsize=9, color='red',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='lightcoral', alpha=0.7),
                    arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0', color='red', lw=1))
    
    # Calcular correlação
    correlation = np.corrcoef(entity_coverage_pct, signature_coverage_pct)[0, 1]
    
    # Adicionar informações estatísticas
    text_info = f'Correlação: {correlation:.4f}\n'
    text_info += f'Total {entity_name.capitalize()}s: {max_entity:,}\n'
    text_info += f'Total Signatures: {max_sig:,}'
    
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
    plot_file = f'{output_prefix}_comparison.png'
    plt.savefig(plot_file, dpi=300, bbox_inches='tight')
    print(f"Gráfico salvo: {plot_file}")
    plt.close()
    
    # Salvar dados em arquivo TSV
    output_file = f'{output_prefix}_analysis.tsv'
    with open(output_file, 'w') as f:
        entity_col_name = f"{entity_name.capitalize()}s_Covered"
        f.write(f'Percentage\tTests_Executed\t{entity_col_name}\tSignature_Coverage\t'
                'Unique_Signatures\tUnique_Sig_Ratio\n')
        for i in range(len(percentages)):
            num_tests = max(1, int(total_tests * percentages[i] / 100))
            f.write(f'{percentages[i]}\t{num_tests}\t{entity_coverage[i]}\t'
                   f'{signature_coverage[i]}\t{signature_uniqueness[i]}\t'
                   f'{unique_signatures_ratio[i]:.2f}\n')
    
    print(f"Dados salvos: {output_file}")
    
    # Estatísticas finais
    print("\n" + "="*60)
    print("ESTATÍSTICAS FINAIS")
    print("="*60)
    print(f"Total de casos de teste: {total_tests}")
    print(f"Total de {entity_name}s únicos: {max(entity_coverage)}")
    print(f"Total de signature values únicos: {max(signature_coverage)}")
    print(f"Total de assinaturas únicas: {max(signature_uniqueness)}")
    print(f"Porcentagem de assinaturas únicas: {(max(signature_uniqueness)/total_tests)*100:.2f}%")
    
    # Correlação entre as métricas
    correlation = np.corrcoef(entity_coverage, signature_coverage)[0, 1]
    print(f"\nCorrelação ({entity_label} vs Signature Coverage): {correlation:.4f}")
    
    if correlation > 0.8:
        print(f"✓ Alta correlação: Assinaturas LSH são um bom proxy para {entity_name} coverage")
    elif correlation > 0.5:
        print(f"~ Correlação moderada: Assinaturas LSH capturam parcialmente a cobertura")
    else:
        print(f"✗ Baixa correlação: Assinaturas LSH podem não refletir bem a cobertura")
    
    print("="*60)


if __name__ == "__main__":
    # Configurar seed para reprodutibilidade
    random.seed(42)
    np.random.seed(42)
    
    # Lista de projetos e entidades
    projects = [
        'chart_v0', 'closure_v0', 'lang_v0', 'math_v0', 'time_v0',
        'flex_v3', 'grep_v3', 'gzip_v1', 'make_v1', 'sed_v6'
    ]
    
    entities = ['branch', 'function', 'line']
    
    print("="*60)
    print("ANÁLISE DE COBERTURA: Coverage vs Black-Box Signature")
    print("Usando signatures geradas de hashed shingles (bbox)")
    print("Processando todos os projetos e entidades")
    print("="*60 + "\n")
    
    total_analyses = len(projects) * len(entities)
    current = 0
    
    for project in projects:
        # Extrair o nome base do projeto (ex: 'chart' de 'chart_v0')
        project_base = project.split('_')[0]
        
        for entity in entities:
            current += 1
            
            entity_file = f'input/{project}/{project_base}-{entity}.txt'
            signature_file = f'input/{project}/{project_base}-bbox.sig'  # Black-box signatures de shingles
            
            # Verificar se os arquivos existem
            if not os.path.exists(entity_file):
                print(f"[{current}/{total_analyses}] ⚠️  IGNORADO: {entity_file} não encontrado\n")
                continue
            
            if not os.path.exists(signature_file):
                print(f"[{current}/{total_analyses}] ⚠️  IGNORADO: {signature_file} não encontrado (execute prioritize.py primeiro)\n")
                continue
            
            print(f"[{current}/{total_analyses}] Processando {project} - {entity}")
            print("-" * 60)
            print(f"Coverage file: {entity_file}")
            print(f"Signature file (black-box): {signature_file}")
            
            # Definir caminho de saída: correlation_sig/{entity}_cov/{project}/{project}_{entity}
            output_prefix = os.path.join('correlation_sig', f'{entity}_cov', project, f'{project}_{entity}')
            
            try:
                analyze_coverage(entity_file, signature_file, output_prefix, entity_name=entity)
                print(f"✓ Concluído: {project} - {entity}\n")
            except Exception as e:
                print(f"✗ ERRO ao processar {project} - {entity}: {e}\n")
    
    print("="*60)
    print("ANÁLISE COMPLETA!")
    print(f"Resultados salvos em: correlation_sig/{{branch,function,line}}_cov/")
    print("="*60)
