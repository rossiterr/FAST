"""
Análise agregada dos resultados de Shingles Coverage
Compara os resultados com Signature Coverage
"""

import os
import numpy as np


def extract_stats_from_output(project, entity='bbox'):
    """Extrai estatísticas do arquivo de análise de shingles"""
    project_base = project.split('_')[0]
    shingles_file = f'input/{project}/{project_base}-{entity}.shingles'
    branch_file = f'input/{project}/{project_base}-branch.txt'
    
    if not os.path.exists(shingles_file) or not os.path.exists(branch_file):
        return None
    
    # Carregar dados de shingles
    with open(shingles_file, 'r') as f:
        shingles_lines = f.readlines()
    
    # Carregar dados de branches
    with open(branch_file, 'r') as f:
        branch_lines = f.readlines()
    
    # Contar totais únicos
    all_shingles = set()
    all_branches = set()
    
    for line in shingles_lines:
        all_shingles.update(line.strip().split())
    
    for line in branch_lines:
        all_branches.update(line.strip().split())
    
    # Carregar arquivo TSV para obter correlação
    analysis_file = f'correlation_hashed_shingles/{project}/{project}_{entity}_shingles_analysis.tsv'
    
    if not os.path.exists(analysis_file):
        return None
    
    # Ler TSV para calcular correlação
    with open(analysis_file, 'r') as f:
        lines = f.readlines()[1:]  # Pular cabeçalho
    
    branch_coverage_values = []
    shingles_coverage_values = []
    
    for line in lines:
        parts = line.strip().split('\t')
        if len(parts) >= 4:
            branch_coverage_values.append(int(parts[2]))
            shingles_coverage_values.append(int(parts[3]))
    
    # Calcular porcentagens
    max_branch = max(branch_coverage_values)
    max_shingles = max(shingles_coverage_values)
    
    branch_pct = [(x / max_branch) * 100 for x in branch_coverage_values]
    shingles_pct = [(x / max_shingles) * 100 for x in shingles_coverage_values]
    
    # Calcular correlação
    correlation = np.corrcoef(branch_pct, shingles_pct)[0, 1]
    
    # Calcular compressão
    compression = len(all_branches) / len(all_shingles) if len(all_shingles) > 0 else 0
    
    # Média de shingles por teste
    avg_shingles = np.mean([len(line.strip().split()) for line in shingles_lines])
    
    return {
        'project': project,
        'total_branches': len(all_branches),
        'total_shingles': len(all_shingles),
        'compression': compression,
        'correlation': correlation,
        'avg_shingles_per_test': avg_shingles,
        'num_tests': len(shingles_lines)
    }


def load_signature_stats():
    """Carrega estatísticas de signature coverage do arquivo agregado"""
    sig_stats = {}
    
    results_file = 'results/RQ1-RQ2-EffectivenessEfficiencyResults.tsv'
    if not os.path.exists(results_file):
        return sig_stats
    
    # Para cada projeto, carregar dados de correlação de signatures
    projects = [
        'chart_v0', 'closure_v0', 'lang_v0', 'math_v0', 'time_v0',
        'flex_v3', 'grep_v3', 'gzip_v1', 'make_v1', 'sed_v6'
    ]
    
    for project in projects:
        project_base = project.split('_')[0]
        
        # Ler arquivo de análise de signatures
        sig_analysis = f'cov_correlation/{project}/{project}_branch_analysis.tsv'
        if os.path.exists(sig_analysis):
            with open(sig_analysis, 'r') as f:
                lines = f.readlines()[1:]  # Pular cabeçalho
            
            branch_cov = []
            sig_cov = []
            
            for line in lines:
                parts = line.strip().split('\t')
                if len(parts) >= 4:
                    branch_cov.append(int(parts[2]))
                    sig_cov.append(int(parts[3]))
            
            if branch_cov and sig_cov:
                max_branch = max(branch_cov)
                max_sig = max(sig_cov)
                
                branch_pct = [(x / max_branch) * 100 for x in branch_cov]
                sig_pct = [(x / max_sig) * 100 for x in sig_cov]
                
                correlation = np.corrcoef(branch_pct, sig_pct)[0, 1]
                compression = max_branch / max_sig if max_sig > 0 else 0
                
                sig_stats[project] = {
                    'correlation': correlation,
                    'compression': compression,
                    'total_branches': max_branch,
                    'total_signatures': max_sig
                }
    
    return sig_stats


if __name__ == "__main__":
    projects = [
        'chart_v0', 'closure_v0', 'lang_v0', 'math_v0', 'time_v0',
        'flex_v3', 'grep_v3', 'gzip_v1', 'make_v1', 'sed_v6'
    ]
    
    print("="*80)
    print("ANÁLISE COMPARATIVA: Shingles Coverage vs Signature Coverage")
    print("="*80 + "\n")
    
    # Coletar estatísticas de shingles
    shingles_stats = []
    for project in projects:
        stats = extract_stats_from_output(project)
        if stats:
            shingles_stats.append(stats)
    
    # Coletar estatísticas de signatures
    sig_stats = load_signature_stats()
    
    # Exibir resultados comparativos
    print("\n" + "="*80)
    print("RESULTADOS POR PROJETO")
    print("="*80)
    print(f"{'Projeto':<15} {'Correlação':<12} {'Compressão':<12} {'Branches':<10} {'Shingles':<10}")
    print(f"{'':15} {'Shingles':<12} {'(B/S)':<12} {'Únicos':<10} {'Únicos':<10}")
    print("-"*80)
    
    for stats in shingles_stats:
        print(f"{stats['project']:<15} {stats['correlation']:>10.4f}  "
              f"{stats['compression']:>10.1f}x  "
              f"{stats['total_branches']:>9,}  "
              f"{stats['total_shingles']:>9,}")
    
    # Estatísticas agregadas - Shingles
    print("\n" + "="*80)
    print("ESTATÍSTICAS AGREGADAS - SHINGLES COVERAGE")
    print("="*80)
    
    correlations = [s['correlation'] for s in shingles_stats]
    compressions = [s['compression'] for s in shingles_stats]
    
    print(f"\nCorrelação (Branch vs Shingles):")
    print(f"  Média:   {np.mean(correlations):.4f}")
    print(f"  Mediana: {np.median(correlations):.4f}")
    print(f"  Mínima:  {np.min(correlations):.4f} ({shingles_stats[np.argmin(correlations)]['project']})")
    print(f"  Máxima:  {np.max(correlations):.4f} ({shingles_stats[np.argmax(correlations)]['project']})")
    print(f"  Desvio:  {np.std(correlations):.4f}")
    
    print(f"\nCompressão (Branches / Shingles):")
    print(f"  Média:   {np.mean(compressions):.2f}x")
    print(f"  Mediana: {np.median(compressions):.2f}x")
    print(f"  Mínima:  {np.min(compressions):.2f}x ({shingles_stats[np.argmin(compressions)]['project']})")
    print(f"  Máxima:  {np.max(compressions):.2f}x ({shingles_stats[np.argmax(compressions)]['project']})")
    
    avg_shingles = [s['avg_shingles_per_test'] for s in shingles_stats]
    print(f"\nMédia de shingles por teste:")
    print(f"  Média geral: {np.mean(avg_shingles):.1f} shingles/teste")
    print(f"  Range: {np.min(avg_shingles):.1f} - {np.max(avg_shingles):.1f}")
    
    # Comparação com Signatures
    if sig_stats:
        print("\n" + "="*80)
        print("COMPARAÇÃO: SHINGLES vs SIGNATURES")
        print("="*80)
        
        print(f"\n{'Projeto':<15} {'Corr Shingles':<15} {'Corr Signatures':<15} {'Comp Shingles':<15} {'Comp Signatures':<15}")
        print("-"*80)
        
        for stats in shingles_stats:
            proj = stats['project']
            if proj in sig_stats:
                print(f"{proj:<15} {stats['correlation']:>13.4f}  "
                      f"{sig_stats[proj]['correlation']:>14.4f}  "
                      f"{stats['compression']:>13.1f}x  "
                      f"{sig_stats[proj]['compression']:>14.1f}x")
        
        # Médias comparativas
        print("\n" + "-"*80)
        sig_correlations = [sig_stats[s['project']]['correlation'] for s in shingles_stats if s['project'] in sig_stats]
        sig_compressions = [sig_stats[s['project']]['compression'] for s in shingles_stats if s['project'] in sig_stats]
        
        print(f"{'MÉDIAS':<15} {np.mean(correlations):>13.4f}  "
              f"{np.mean(sig_correlations):>14.4f}  "
              f"{np.mean(compressions):>13.1f}x  "
              f"{np.mean(sig_compressions):>14.1f}x")
        
        print("\n" + "="*80)
        print("ANÁLISE COMPARATIVA")
        print("="*80)
        
        print("\n1. GRANULARIDADE:")
        print(f"   • Branches (baseline):     Mais granular")
        print(f"   • Shingles (intermediário): Compressão ~{np.mean(compressions):.1f}x")
        print(f"   • Signatures (MinHash):     Compressão ~{np.mean(sig_compressions):.1f}x")
        
        print("\n2. CORRELAÇÃO COM BRANCH COVERAGE:")
        print(f"   • Shingles:    {np.mean(correlations):.4f} (±{np.std(correlations):.4f})")
        print(f"   • Signatures:  {np.mean(sig_correlations):.4f} (±{np.std(sig_correlations):.4f})")
        
        diff = np.mean(sig_correlations) - np.mean(correlations)
        print(f"   • Diferença:   {diff:+.4f} ({abs(diff)*100:.2f}% {'maior' if diff > 0 else 'menor'} para signatures)")
        
        print("\n3. EFICIÊNCIA DE COMPRESSÃO:")
        ratio = np.mean(sig_compressions) / np.mean(compressions)
        print(f"   • Signatures são {ratio:.1f}x mais compactas que Shingles")
        print(f"   • Trade-off: {abs(diff)*100:.2f}% de diferença na correlação para {(ratio-1)*100:.0f}% mais compressão")
        
        print("\n4. INTERPRETABILIDADE:")
        print(f"   • Shingles: Cada elemento representa substring real do output (k=5)")
        print(f"   • Signatures: Hash values abstratos (MinHash)")
        print(f"   • Vantagem: Shingles permitem inspeção direta do conteúdo")
        
    print("\n" + "="*80)
    print("CONCLUSÕES")
    print("="*80)
    
    if np.mean(correlations) > 0.95:
        print("\n✓ ALTA CORRELAÇÃO: Shingles são excelente proxy para branch coverage")
    elif np.mean(correlations) > 0.85:
        print("\n✓ BOA CORRELAÇÃO: Shingles capturam bem o comportamento dos testes")
    else:
        print("\n⚠ CORRELAÇÃO MODERADA: Shingles podem não refletir totalmente a cobertura")
    
    if sig_stats and abs(diff) < 0.05:
        print("✓ EQUIVALÊNCIA: Shingles e Signatures têm correlação similar")
        print("  → Shingles podem ser usados diretamente sem perda significativa")
        print(f"  → Benefício: {np.mean(compressions)/np.mean(sig_compressions):.1f}x mais informação que signatures")
    
    if np.mean(compressions) > 5:
        print(f"✓ BOA COMPRESSÃO: Shingles reduzem dimensionalidade em ~{np.mean(compressions):.1f}x")
        print("  → Escalabilidade mantida com interpretabilidade preservada")
    
    print("\n" + "="*80)
