import urllib.request
from urllib.parse import quote

prompt = "A high quality portrait of a fantasy silver knight in a glowing crystal cave"
url = f"https://image.pollinations.ai/prompt/{quote(prompt)}?width=800&height=1200&nologo=true"

print("Baixando de:", url)
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req) as response, open("test_knight.jpg", 'wb') as out_file:
    out_file.write(response.read())
print("Sucesso!")
