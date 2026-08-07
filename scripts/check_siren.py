import requests

def verifier_siren(siren):
    url = f"https://recherche-entreprises.api.gouv.fr/search?q={siren}"

    r = requests.get(url)
    r.raise_for_status()

    data = r.json()

    for entreprise in data.get("results", []):
        if entreprise.get("siren") == siren:
            return True, entreprise

    return False, None

existe, entreprise = verifier_siren("552100554")
print(existe)