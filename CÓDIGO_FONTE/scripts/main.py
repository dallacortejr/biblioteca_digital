
# ============================================================
# scripts/main.py
# Script principal para listar documentos via GitHub API e gerar relatório.
# ============================================================

import os
import pandas as pd
from pathlib import Path
from ghapi.core import GhApi
from docx import Document
from fpdf import FPDF
from urllib.error import HTTPError 

# --- Configurações ---
GH_API = GhApi(token=os.environ.get("GITHUB_TOKEN")) 
OWNER = "dallacortejr"
REPO_NAME = "biblioteca_digital"
REPORT_PATH = Path("/content/projeto_biblioteca_work_colab/reports")

# --- Funções de Geração de Relatórios Formatados ---

def generate_docx_report(df: pd.DataFrame, path: Path):
    """Gera um relatório DOCX com o DataFrame de resumo."""
    doc = Document()
    doc.add_heading('Relatório de Acervo Digital (GitHub)', 0)
    t = doc.add_table(df.shape[0]+1, df.shape[1])
    t.style = 'Table Grid'
    for j in range(df.shape[-1]):
        t.cell(0, j).text = df.columns[j]
    for i in range(df.shape[0]):
        for j in range(df.shape[-1]):
            t.cell(i+1, j).text = str(df.values[i, j])
    doc.save(str(path))
    print(f"Relatório DOCX salvo em: {path.name}")

def generate_pdf_report(df: pd.DataFrame, path: Path):
    """Gera um relatório PDF com o DataFrame de resumo."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=16)
    pdf.cell(200, 10, txt="Relatório de Acervo Digital", ln=1, align="C")
    pdf.set_font("Arial", size=10)
    pdf.ln(5)
    data = [df.columns.tolist()] + df.values.tolist()
    col_widths = [40, 40, 60] 
    for row in data:
        for i, item in enumerate(row):
            pdf.cell(col_widths[i], 7, str(item), border=1)
        pdf.ln()
    pdf.output(str(path))
    print(f"Relatório PDF salvo em: {path.name}")

# --- Função de Busca de Metadados ---

def get_repo_files_metadata(owner: str, repo: str) -> pd.DataFrame:
    """Usa a GitHub API para listar todos os arquivos do repositório."""

    try:
        # 1. Obtém as informações do repositório para descobrir a branch padrão
        repo_info = GH_API.repos.get(owner=owner, repo=repo)
        default_branch = repo_info.get('default_branch', 'main')
        print(f"Branch padrão do repositório: {default_branch}")

        # 2. Obtém o SHA da branch padrão
        ref_path = f'heads/{default_branch}'
        branch_ref = GH_API.git.get_ref(owner=owner, repo=repo, ref=ref_path)
        selected_sha = branch_ref['object']['sha']

    except HTTPError as e:
        if e.code == 404:
            print("ERRO CRÍTICO: Repositório não encontrado, token inválido, ou branch principal vazia.")
        else:
            print(f"ERRO de API: {e}")
        return pd.DataFrame()
    except Exception as e:
        print(f"ERRO geral ao obter referência da branch: {e}")
        return pd.DataFrame()

    try:
        # 3. Obtém a tree (estrutura de arquivos) recursivamente
        tree = GH_API.git.get_tree(owner=owner, repo=repo, tree_sha=selected_sha, recursive=1)['tree']
    except Exception as e:
        print(f"ERRO ao obter a árvore de arquivos: {e}")
        return pd.DataFrame()


    data = []
    supported_extensions = ['.pdf', '.epub', '.docx', '.txt', '.mobi', '.azw']

    for item in tree:
        if item['type'] == 'blob': 
            path = item['path']
            ext = Path(path).suffix.lower()
            if ext in supported_extensions:
                # 🛑 CORREÇÃO NO CÓDIGO FINAL: Dicionário interno deve usar chaves simples
                # Esta string não é uma f-string, então as chaves simples { } serão tratadas como texto
                # e salvas corretamente no arquivo main.py.
                data.append({
                    'path': path,
                    'size': item.get('size', 0),
                    'extension': ext
                })

    return pd.DataFrame(data)


# ... (O restante da função main() ) ...
def main():

    df_metadata = get_repo_files_metadata(OWNER, REPO_NAME)

    if df_metadata.empty:
        print("Nenhum arquivo suportado encontrado ou falha na API.")
        return

    df_report = df_metadata.groupby('extension').agg(
        total_files=('path', 'count'),
        total_size_kb=('size', lambda x: x.sum() / 1024)
    ).reset_index()

    df_report['total_size_kb'] = df_report['total_size_kb'].round(2)
    df_report.columns = ['Extensao', 'Total Arquivos', 'Tamanho Total (KB)']

    print("\n--- Relatório de Documentos ---")
    print(df_report.to_markdown(index=False))

    generate_docx_report(df_report, REPORT_PATH / 'relatorio_biblioteca.docx')
    generate_pdf_report(df_report, REPORT_PATH / 'relatorio_biblioteca.pdf')

    df_report.to_csv(REPORT_PATH / 'relatorio_biblioteca.csv', index=False)
    print("Relatório CSV salvo.")


if __name__ == '__main__':
    main()
