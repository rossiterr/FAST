"""
Gera malhas (grids) de gráficos mostrando as correlações visuais
Uma malha para cada tipo de cobertura: Branch, Function, Line
Cada malha mostra 10 projetos x 3 métodos (Signature, Hashed Shingles, Raw Shingles)
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle


def load_correlation_data(entity):
    """Carrega dados de correlação de um tipo de cobertura"""
    
    projects = [
        'chart_v0', 'closure_v0', 'flex_v3', 'grep_v3', 'gzip_v1',
        'lang_v0', 'make_v1', 'math_v0', 'sed_v6', 'time_v0'
    ]
    
    methods = ['Signature', 'Hashed_Shingles', 'Raw_Shingles']
    method_labels = ['Signature', 'Hashed Shingles', 'Raw Shingles']
    
    # Matriz para armazenar correlações: projetos x métodos
    correlation_matrix = np.zeros((len(projects), len(methods)))
    has_data = np.zeros((len(projects), len(methods)), dtype=bool)
    is_const = np.zeros((len(projects), len(methods)), dtype=bool)
    
    for i, project in enumerate(projects):
        for j, method in enumerate(methods):
            # Determinar arquivo baseado no método
            if method == 'Signature':
                tsv_file = f'correlation_sig/{entity}_cov/{project}/{project}_{entity}_analysis.tsv'
            elif method == 'Hashed_Shingles':
                tsv_file = f'correlation_hashed_shingles/{entity}_cov/{project}/{project}_bbox_shingles_coverage.tsv'
            else:  # Raw_Shingles
                tsv_file = f'correlation_raw_shingles/{entity}_cov/{project}/{project}_bbox_raw_shingles_analysis.tsv'
            
            if os.path.exists(tsv_file):
                try:
                    df = pd.read_csv(tsv_file, sep='\t')
                    coverage_cols = [col for col in df.columns if 'Covered' in col or 'Coverage' in col]
                    
                    if len(coverage_cols) >= 2:
                        entity_coverage = df[coverage_cols[0]].values
                        metric_coverage = df[coverage_cols[1]].values
                        
                        # Verificar cobertura constante
                        if entity_coverage.std() == 0 or metric_coverage.std() == 0:
                            is_const[i, j] = True
                            has_data[i, j] = True
                            correlation_matrix[i, j] = 0  # Placeholder visual
                        else:
                            # Normalizar e calcular correlação
                            entity_pct = (entity_coverage / entity_coverage.max()) * 100
                            metric_pct = (metric_coverage / metric_coverage.max()) * 100
                            correlation = np.corrcoef(entity_pct, metric_pct)[0, 1]
                            
                            if not np.isnan(correlation):
                                correlation_matrix[i, j] = correlation
                                has_data[i, j] = True
                
                except Exception as e:
                    print(f"  Erro ao processar {tsv_file}: {e}")
    
    return correlation_matrix, has_data, is_const, projects, method_labels


def create_correlation_grid(entity):
    """Cria malha de gráficos para um tipo de cobertura"""
    
    print(f"\n{'='*80}")
    print(f"Gerando malha de gráficos para {entity.upper()} COVERAGE")
    print(f"{'='*80}")
    
    correlation_matrix, has_data, is_const, projects, methods = load_correlation_data(entity)
    
    # Criar figura com subplots
    fig, axes = plt.subplots(len(projects), len(methods), figsize=(15, 25))
    fig.suptitle(f'{entity.capitalize()} Coverage - Correlations Grid\n' + 
                 f'(Projects × Methods)', 
                 fontsize=16, fontweight='bold', y=0.995)
    
    # Configurar cada subplot
    for i, project in enumerate(projects):
        for j, method in enumerate(methods):
            ax = axes[i, j]
            
            # Título apenas na primeira linha
            if i == 0:
                ax.set_title(method, fontsize=10, fontweight='bold', pad=8)
            
            # Label do projeto apenas na primeira coluna
            if j == 0:
                ax.set_ylabel(project.replace('_', ' ').title(), 
                            fontsize=9, fontweight='bold', rotation=0, 
                            ha='right', va='center', labelpad=40)
            
            if has_data[i, j]:
                if is_const[i, j]:
                    # Cobertura constante - mostrar marcador especial
                    ax.text(0.5, 0.5, 'CONST\n(σ=0)', 
                           ha='center', va='center', 
                           fontsize=12, fontweight='bold',
                           color='orange',
                           bbox=dict(boxstyle='round,pad=0.5', 
                                   facecolor='lightyellow', 
                                   edgecolor='orange', linewidth=2))
                    ax.set_xlim(0, 1)
                    ax.set_ylim(0, 1)
                else:
                    corr_value = correlation_matrix[i, j]
                    
                    # Cor baseada na correlação
                    if corr_value >= 0.95:
                        color = '#2ecc71'  # Verde forte
                        quality = 'Excellent'
                    elif corr_value >= 0.90:
                        color = '#27ae60'  # Verde
                        quality = 'Very Good'
                    elif corr_value >= 0.85:
                        color = '#f39c12'  # Laranja
                        quality = 'Good'
                    elif corr_value >= 0.80:
                        color = '#e67e22'  # Laranja escuro
                        quality = 'Fair'
                    else:
                        color = '#e74c3c'  # Vermelho
                        quality = 'Poor'
                    
                    # Mostrar valor da correlação
                    ax.text(0.5, 0.6, f'r = {corr_value:.4f}', 
                           ha='center', va='center', 
                           fontsize=11, fontweight='bold')
                    
                    ax.text(0.5, 0.4, f'({quality})', 
                           ha='center', va='center', 
                           fontsize=8, style='italic',
                           color='gray')
                    
                    # Background colorido
                    ax.add_patch(Rectangle((0, 0), 1, 1, 
                                          facecolor=color, alpha=0.3))
                    
                    ax.set_xlim(0, 1)
                    ax.set_ylim(0, 1)
            else:
                # Sem dados
                ax.text(0.5, 0.5, 'N/A', 
                       ha='center', va='center', 
                       fontsize=12, color='gray')
                ax.set_xlim(0, 1)
                ax.set_ylim(0, 1)
            
            # Remover ticks e bordas
            ax.set_xticks([])
            ax.set_yticks([])
            ax.spines['top'].set_visible(True)
            ax.spines['right'].set_visible(True)
            ax.spines['bottom'].set_visible(True)
            ax.spines['left'].set_visible(True)
            
            # Borda mais grossa
            for spine in ax.spines.values():
                spine.set_linewidth(1.5)
                spine.set_color('black')
    
    # Ajustar layout
    plt.tight_layout(rect=[0, 0, 1, 0.99])
    
    # Adicionar legenda
    legend_elements = [
        plt.Line2D([0], [0], marker='s', color='w', 
                  markerfacecolor='#2ecc71', markersize=10, 
                  label='Excellent (r ≥ 0.95)', alpha=0.3),
        plt.Line2D([0], [0], marker='s', color='w', 
                  markerfacecolor='#27ae60', markersize=10, 
                  label='Very Good (r ≥ 0.90)', alpha=0.3),
        plt.Line2D([0], [0], marker='s', color='w', 
                  markerfacecolor='#f39c12', markersize=10, 
                  label='Good (r ≥ 0.85)', alpha=0.3),
        plt.Line2D([0], [0], marker='s', color='w', 
                  markerfacecolor='#e67e22', markersize=10, 
                  label='Fair (r ≥ 0.80)', alpha=0.3),
        plt.Line2D([0], [0], marker='s', color='w', 
                  markerfacecolor='#e74c3c', markersize=10, 
                  label='Poor (r < 0.80)', alpha=0.3),
        plt.Line2D([0], [0], marker='s', color='w', 
                  markerfacecolor='lightyellow', markersize=10, 
                  label='Constant Coverage', 
                  markeredgecolor='orange', markeredgewidth=2)
    ]
    
    fig.legend(handles=legend_elements, 
              loc='lower center', 
              ncol=6, 
              frameon=True,
              fontsize=9,
              bbox_to_anchor=(0.5, -0.01))
    
    # Salvar figura
    output_dir = 'correlation_tables'
    os.makedirs(output_dir, exist_ok=True)
    output_file = f'{output_dir}/{entity}_coverage_correlation_grid.png'
    
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"✓ Malha salva: {output_file}")
    
    plt.close()
    
    # Estatísticas
    print(f"\nEstatísticas da malha {entity.upper()}:")
    for j, method in enumerate(methods):
        valid_corrs = correlation_matrix[has_data[:, j] & ~is_const[:, j], j]
        const_count = is_const[:, j].sum()
        
        if len(valid_corrs) > 0:
            print(f"  {method:<20}: μ={valid_corrs.mean():.4f}, "
                  f"σ={valid_corrs.std():.4f}, "
                  f"min={valid_corrs.min():.4f}, "
                  f"max={valid_corrs.max():.4f}")
            if const_count > 0:
                print(f"  {'':20}  [!] {const_count} caso(s) com cobertura constante")
        else:
            print(f"  {method:<20}: Sem dados válidos")


def generate_all_grids():
    """Gera malhas para todos os tipos de cobertura"""
    
    print("="*80)
    print("GERAÇÃO DE MALHAS DE CORRELAÇÃO")
    print("Criando visualizações: Projects × Methods para cada Coverage Type")
    print("="*80)
    
    entities = ['branch', 'function', 'line']
    
    for entity in entities:
        create_correlation_grid(entity)
    
    print(f"\n{'='*80}")
    print("TODAS AS MALHAS GERADAS COM SUCESSO!")
    print(f"Diretório de saída: correlation_tables/")
    print("Arquivos gerados:")
    print("  - branch_coverage_correlation_grid.png")
    print("  - function_coverage_correlation_grid.png")
    print("  - line_coverage_correlation_grid.png")
    print(f"{'='*80}")


if __name__ == "__main__":
    generate_all_grids()
