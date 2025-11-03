from fpdf import FPDF
from pathlib import Path
out = Path("sample_docs")
out.mkdir(exist_ok=True)
pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=12)
pdf.cell(0, 10, "Sample PDF from Colab", ln=True)
pdf.output(str(out / "sample_001.pdf"))
print("sample_docs created")
