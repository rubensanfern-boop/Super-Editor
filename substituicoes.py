import json

def carregar_substituicoes():
    with open("substitute.json", "r", encoding="utf-8") as f:
        return json.load(f)
