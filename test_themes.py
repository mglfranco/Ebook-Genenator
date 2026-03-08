"""
Teste de diagnóstico: verifica se CSS custom properties são corretamente
sobrescritas entre stylesheets no WeasyPrint.
"""
from weasyprint import HTML, CSS

# Test 1: CSS vars override across multiple stylesheets?
html = """<html><body>
<div id="box1" style="background:var(--color-accent);width:200px;height:200px;"></div>
<p style="color:var(--color-text);">Este texto deveria ser azul com Corporativo</p>
</body></html>"""

css_main = ":root { --color-accent: #ff0000; --color-text: #ff0000; }"
css_override = ":root { --color-accent: #003366; --color-text: #003366; }"

# Test with 2 stylesheets
doc = HTML(string=html)
doc.write_pdf("output/var_override_test.pdf", stylesheets=[
    CSS(string=css_main),
    CSS(string=css_override),
])
print("Test 1: Two `:root` in separate stylesheets - check PDF for BLUE (override) vs RED (no override)")

# Test 2: What if we combine into single stylesheet?
combined = css_main + "\n" + css_override
doc2 = HTML(string=html)
doc2.write_pdf("output/var_combined_test.pdf", stylesheets=[CSS(string=combined)])
print("Test 2: Two `:root` in same stylesheet - check PDF")

# Test 3: Use !important to force override
css_force = ":root { --color-accent: #003366 !important; --color-text: #003366 !important; }"
doc3 = HTML(string=html)
doc3.write_pdf("output/var_important_test.pdf", stylesheets=[
    CSS(string=css_main),
    CSS(string=css_force),
])
print("Test 3: With !important - check PDF")

# Test 4: Direct property override (no vars)
html_direct = """<html><body>
<div style="background:#003366;width:200px;height:200px;"></div>
<p style="color:#003366;">Texto azul direto</p>
</body></html>"""
HTML(string=html_direct).write_pdf("output/direct_test.pdf")
print("Test 4: Direct colors (no vars) - baseline")

print("\nVerifique os PDFs na pasta output/")
