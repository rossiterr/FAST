import os
import numpy as np

projects = ['chart_v0', 'closure_v0', 'flex_v3', 'grep_v3', 'gzip_v1', 
            'lang_v0', 'make_v1', 'math_v0', 'sed_v6', 'time_v0']

print('='*80)
print('ANÁLISE DE CORRELAÇÃO: Branch Coverage vs Signature Coverage')
print('='*80)
print()

results = []

for project in projects:
    tsv_file = f'correlation_sig/{project}/{project}_branch_analysis.tsv'
    
    if os.path.exists(tsv_file):
        with open(tsv_file, 'r') as f:
            lines = f.readlines()
        
        branches_covered = []
        signature_coverage = []
        
        for line in lines[1:]:
            parts = line.strip().split('\t')
            if len(parts) >= 6:
                branches_covered.append(int(parts[2]))
                signature_coverage.append(int(parts[3]))
        
        total_tests = int(lines[-1].split('\t')[1])
        total_branches = branches_covered[-1]
        total_sigs = signature_coverage[-1]
        unique_sigs = int(lines[-1].split('\t')[4])
        
        correlation = np.corrcoef(branches_covered, signature_coverage)[0, 1]
        compression_ratio = total_branches / total_sigs if total_sigs > 0 else 0
        unique_ratio = (unique_sigs / total_tests) * 100
        
        results.append({
            'project': project,
            'tests': total_tests,
            'branches': total_branches,
            'sigs': total_sigs,
            'unique_sigs': unique_sigs,
            'correlation': correlation,
            'compression': compression_ratio,
            'unique_ratio': unique_ratio
        })
        
        print(f'{project:12} | Testes: {total_tests:4} | Branches: {total_branches:6} | '
              f'Sigs: {total_sigs:5} | Corr: {correlation:.4f} | '
              f'Comp: {compression_ratio:5.1f}x | Unique: {unique_ratio:5.1f}%')

print()
print('='*80)
print('ESTATÍSTICAS GERAIS')
print('='*80)

correlations = [r['correlation'] for r in results]
compressions = [r['compression'] for r in results]
unique_ratios = [r['unique_ratio'] for r in results]

print(f'\nCorrelação Média: {np.mean(correlations):.4f}')
print(f'Correlação Mínima: {np.min(correlations):.4f}')
print(f'Correlação Máxima: {np.max(correlations):.4f}')

print(f'\nCompressão Média: {np.mean(compressions):.1f}x')
print(f'Compressão Mínima: {np.min(compressions):.1f}x')
print(f'Compressão Máxima: {np.max(compressions):.1f}x')

print(f'\nUnique Signatures Médio: {np.mean(unique_ratios):.1f}%')
print(f'Unique Signatures Mínimo: {np.min(unique_ratios):.1f}%')
print(f'Unique Signatures Máximo: {np.max(unique_ratios):.1f}%')

print()
print('='*80)
print('CATEGORIZAÇÃO POR CORRELAÇÃO')
print('='*80)

high = [r for r in results if r['correlation'] > 0.9]
medium = [r for r in results if 0.7 <= r['correlation'] <= 0.9]
low = [r for r in results if r['correlation'] < 0.7]

print(f'\nAlta Correlação (>0.9): {len(high)} projetos')
for r in high:
    print(f'  • {r["project"]:12} - {r["correlation"]:.4f}')

print(f'\nCorrelação Moderada (0.7-0.9): {len(medium)} projetos')
for r in medium:
    print(f'  • {r["project"]:12} - {r["correlation"]:.4f}')

print(f'\nBaixa Correlação (<0.7): {len(low)} projetos')
for r in low:
    print(f'  • {r["project"]:12} - {r["correlation"]:.4f}')

print()
print('='*80)
