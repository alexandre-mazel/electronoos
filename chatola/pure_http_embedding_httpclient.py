import http.client
import json

def get_embedding(text, model="nomic-embed-text", host="obo-world.com", port=11434):
    conn = http.client.HTTPConnection(host, port)

    payload = json.dumps({
        "model": model,
        "prompt": text
    })

    headers = {
        "Content-Type": "application/json"
    }

    conn.request("POST", "/api/embeddings", body=payload, headers=headers)

    response = conn.getresponse()
    data = response.read()

    if response.status != 200:
        raise Exception(f"HTTP error {response.status}: {data.decode()}")

    result = json.loads(data)
    return result["embedding"]


# Exemple
if __name__ == "__main__":
    emb = get_embedding("Hello world")
    print(len(emb))
    print(emb[:10])
    model = "qwen3-embedding"
    emb = get_embedding("Hello world", model)
    print(len(emb))
    print(emb[:10])
    emb2 = get_embedding("Bonjour le monde", model)
    print(emb2[:10])
    import numpy as np
    simi = np.dot( emb, emb2 )
    print( "simi: %.3f" % simi )
    
    emb = get_embedding("Qu'est ce que la RAM ?", model)
    emb2 = get_embedding("C'est quoi la RAM?", model)
    simi = np.dot( emb, emb2 )
    print( "simi RAM: %.3f" % simi )