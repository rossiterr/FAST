"""
Gera tabelas de correlação consolidadas para cada tipo de cobertura
Compara Signature, Hashed Shingles e Raw Shingles vs Coverage (branch/function/line)
"""

import os
import pandas as pd
import numpy as np


def extract_correlation_from_tsv(tsv_file):
    """Extrai a correlação calculando a partir dos dados do TSV"""
    if not os.path.exists(tsv_file):
        return None
    
    try:
        df = pd.read_csv(tsv_file, sep='\t')
        
        # Identificar as colunas de cobertura
        # A primeira coluna numérica após Tests_Executed é a coverage, a segunda é a métrica comparada
        coverage_cols = [col for col in df.columns if 'Covered' in col or 'Coverage' in col]
        
        if len(coverage_cols) < 2:
            return None
        
        # Primeira coluna de coverage (entity coverage)
        entity_coverage = df[coverage_cols[0]].values
        # Segunda coluna (signature/shingles coverage)
        metric_coverage = df[coverage_cols[1]].values
        
        # Verificar se há variação nos dados
        if entity_coverage.std() == 0 or metric_coverage.std() == 0:
            # Cobertura constante - correlação não pode ser calculada
            # Retornar um valor especial para indicar isso
            return -999.0  # Código especial para "cobertura constante"
        
        # Normalizar para porcentagens
        entity_pct = (entity_coverage / entity_coverage.max()) * 100
        metric_pct = (metric_coverage / metric_coverage.max()) * 100
        
        # Calcular correlação de Pearson
        correlation = np.corrcoef(entity_pct, metric_pct)[0, 1]
        
        # Se ainda resultar em NaN (por algum outro motivo), retornar None
        if np.isnan(correlation):
            return None
        
        return correlation
    except Exception as e:
        print(f"  Erro ao processar {tsv_file}: {e}")
        return None


def generate_correlation_table(entity):
    """Gera tabela de correlação para um tipo de cobertura específico"""
    
    projects = [
        'chart_v0', 'closure_v0', 'flex_v3', 'grep_v3', 'gzip_v1',
        'lang_v0', 'make_v1', 'math_v0', 'sed_v6', 'time_v0'
    ]
    
    # Estrutura para armazenar correlações
    results = []
    
    print(f"\n{'='*80}")
    print(f"Processando {entity.upper()} COVERAGE")
    print(f"{'='*80}")
    
    for project in projects:
        project_base = project.split('_')[0]
        
        row = {'Project': project}
        
        # 1. Signature Coverage
        sig_file = f'correlation_sig/{entity}_cov/{project}/{project}_{entity}_analysis.tsv'
        sig_corr = extract_correlation_from_tsv(sig_file)
        if sig_corr == -999.0:
            row['Signature'] = 'CONST'  # Cobertura constante
        else:
            row['Signature'] = sig_corr if sig_corr is not None else np.nan
        
        # 2. Hashed Shingles Coverage
        hashed_file = f'correlation_hashed_shingles/{entity}_cov/{project}/{project}_bbox_shingles_coverage.tsv'
        hashed_corr = extract_correlation_from_tsv(hashed_file)
        if hashed_corr == -999.0:
            row['Hashed_Shingles'] = 'CONST'
        else:
            row['Hashed_Shingles'] = hashed_corr if hashed_corr is not None else np.nan
        
        # 3. Raw Shingles Coverage
        raw_file = f'correlation_raw_shingles/{entity}_cov/{project}/{project}_bbox_raw_shingles_analysis.tsv'
        raw_corr = extract_correlation_from_tsv(raw_file)
        if raw_corr == -999.0:
            row['Raw_Shingles'] = 'CONST'
        else:
            row['Raw_Shingles'] = raw_corr if raw_corr is not None else np.nan
        
        results.append(row)
        
        # Status
        status = []
        if sig_corr is not None:
            if sig_corr == -999.0:
                status.append(f"Sig: CONST")
            else:
                status.append(f"Sig: {sig_corr:.4f}")
        if hashed_corr is not None:
            if hashed_corr == -999.0:
                status.append(f"Hashed: CONST")
            else:
                status.append(f"Hashed: {hashed_corr:.4f}")
        if raw_corr is not None:
            if raw_corr == -999.0:
                status.append(f"Raw: CONST")
            else:
                status.append(f"Raw: {raw_corr:.4f}")
        
        print(f"  {project:<15} | {' | '.join(status) if status else 'Nenhum dado encontrado'}")
    
    # Criar DataFrame
    df = pd.DataFrame(results)
    
    # Calcular estatísticas
    print(f"\n{'='*80}")
    print(f"ESTATÍSTICAS - {entity.upper()} COVERAGE")
    print(f"{'='*80}")
    print(f"\n{'Métrica':<20} {'Média':<12} {'Mediana':<12} {'Mín':<12} {'Máx':<12} {'Desvio':<12}")
    print("-" * 80)
    
    for col in ['Signature', 'Hashed_Shingles', 'Raw_Shingles']:
        # Filtrar valores numéricos (excluir 'CONST' e NaN)
        numeric_values = pd.to_numeric(df[col], errors='coerce').dropna()
        const_count = (df[col] == 'CONST').sum()
        missing_count = df[col].isna().sum()
        
        if len(numeric_values) > 0:
            print(f"{col:<20} {numeric_values.mean():>10.4f}  {numeric_values.median():>10.4f}  "
                  f"{numeric_values.min():>10.4f}  {numeric_values.max():>10.4f}  {numeric_values.std():>10.4f}")
            if const_count > 0:
                print(f"{'':20} [!] {const_count} projeto(s) com cobertura constante")
        else:
            status_msg = []
            if const_count > 0:
                status_msg.append(f"{const_count} CONST")
            if missing_count > 0:
                status_msg.append(f"{missing_count} N/A")
            print(f"{col:<20} {', '.join(status_msg) if status_msg else 'N/A':<12}")
    
    return df


def save_tables():
    """Gera e salva tabelas para todos os tipos de cobertura"""
    
    entities = ['branch', 'function', 'line']
    
    print("="*80)
    print("GERAÇÃO DE TABELAS DE CORRELAÇÃO")
    print("Comparando Signature, Hashed Shingles e Raw Shingles vs Coverage")
    print("="*80)
    
    # Criar diretório de saída
    output_dir = 'correlation_tables'
    os.makedirs(output_dir, exist_ok=True)
    
    all_tables = {}
    
    for entity in entities:
        df = generate_correlation_table(entity)
        all_tables[entity] = df
        
        # Salvar tabela individual
        output_file = f'{output_dir}/{entity}_coverage_correlations.tsv'
        df.to_csv(output_file, sep='\t', index=False, float_format='%.4f')
        print(f"\n✓ Tabela salva: {output_file}")
        
        # Salvar versão formatada para leitura
        output_txt = f'{output_dir}/{entity}_coverage_correlations.txt'
        with open(output_txt, 'w') as f:
            f.write(f"{'='*80}\n")
            f.write(f"{entity.upper()} COVERAGE - CORRELAÇÕES\n")
            f.write(f"{'='*80}\n\n")
            f.write(df.to_string(index=False, float_format=lambda x: f'{x:.4f}' if pd.notna(x) else 'N/A'))
            f.write("\n\n")
            
            # Estatísticas
            f.write(f"{'='*80}\n")
            f.write("ESTATÍSTICAS\n")
            f.write(f"{'='*80}\n\n")
            f.write(f"{'Métrica':<20} {'Média':<12} {'Mediana':<12} {'Mín':<12} {'Máx':<12} {'Desvio':<12}\n")
            f.write("-" * 80 + "\n")
            
            for col in ['Signature', 'Hashed_Shingles', 'Raw_Shingles']:
                # Filtrar valores numéricos (excluir 'CONST' e NaN)
                numeric_values = pd.to_numeric(df[col], errors='coerce').dropna()
                const_count = (df[col] == 'CONST').sum()
                missing_count = df[col].isna().sum()
                
                if len(numeric_values) > 0:
                    f.write(f"{col:<20} {numeric_values.mean():>10.4f}  {numeric_values.median():>10.4f}  "
                           f"{numeric_values.min():>10.4f}  {numeric_values.max():>10.4f}  {numeric_values.std():>10.4f}\n")
                    if const_count > 0:
                        f.write(f"{'':20} [!] {const_count} projeto(s) com cobertura constante\n")
                else:
                    status_msg = []
                    if const_count > 0:
                        status_msg.append(f"{const_count} CONST")
                    if missing_count > 0:
                        status_msg.append(f"{missing_count} N/A")
                    f.write(f"{col:<20} {', '.join(status_msg) if status_msg else 'N/A':<12}\n")
        
        print(f"✓ Tabela formatada salva: {output_txt}")
    
    # Criar tabela consolidada comparando as três entidades
    print(f"\n{'='*80}")
    print("TABELA CONSOLIDADA - COMPARAÇÃO ENTRE ENTIDADES")
    print(f"{'='*80}\n")
    
    consolidada = []
    for entity in entities:
        df = all_tables[entity]
        
        # Converter colunas para numérico, tratando 'CONST' como NaN
        sig_numeric = pd.to_numeric(df['Signature'], errors='coerce')
        hashed_numeric = pd.to_numeric(df['Hashed_Shingles'], errors='coerce')
        raw_numeric = pd.to_numeric(df['Raw_Shingles'], errors='coerce')
        
        row = {
            'Coverage_Type': entity.capitalize(),
            'Sig_Mean': sig_numeric.mean(),
            'Sig_Std': sig_numeric.std(),
            'Hashed_Mean': hashed_numeric.mean(),
            'Hashed_Std': hashed_numeric.std(),
            'Raw_Mean': raw_numeric.mean(),
            'Raw_Std': raw_numeric.std()
        }
        consolidada.append(row)
    
    df_consolidada = pd.DataFrame(consolidada)
    
    # Salvar tabela consolidada
    output_consolidada = f'{output_dir}/consolidated_correlations.tsv'
    df_consolidada.to_csv(output_consolidada, sep='\t', index=False, float_format='%.4f')
    
    output_consolidada_txt = f'{output_dir}/consolidated_correlations.txt'
    with open(output_consolidada_txt, 'w') as f:
        f.write(f"{'='*80}\n")
        f.write("TABELA CONSOLIDADA - MÉDIAS DE CORRELAÇÃO POR TIPO DE COBERTURA\n")
        f.write(f"{'='*80}\n\n")
        f.write(df_consolidada.to_string(index=False, float_format=lambda x: f'{x:.4f}' if pd.notna(x) else 'N/A'))
        f.write("\n")
    
    print(df_consolidada.to_string(index=False, float_format=lambda x: f'{x:.4f}' if pd.notna(x) else 'N/A'))
    print(f"\n✓ Tabela consolidada salva: {output_consolidada}")
    print(f"✓ Tabela consolidada formatada salva: {output_consolidada_txt}")
    
    print(f"\n{'='*80}")
    print("TODAS AS TABELAS GERADAS COM SUCESSO!")
    print(f"Diretório de saída: {output_dir}/")
    print(f"{'='*80}")


if __name__ == "__main__":
    save_tables()
