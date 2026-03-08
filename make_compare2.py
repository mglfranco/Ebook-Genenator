import os

html = '<html><body style="display:flex; flex-wrap:wrap; gap:10px;">\n'
for f in os.listdir('output'):
    if f.startswith('v3_') and f.endswith('.pdf'):
        html += f'<div><h3>{f}</h3><embed src="{f}" width="400" height="600" /></div>\n'
html += '</body></html>\n'

with open('output/compare2.html', 'w', encoding='utf-8') as f:
    f.write(html)
