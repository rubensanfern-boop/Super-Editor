import json
import os

def carregar_tema(nome):
    caminho = os.path.join("temas", f"{nome}.json")
    with open(caminho, "r", encoding="utf-8") as f:
        return json.load(f)
