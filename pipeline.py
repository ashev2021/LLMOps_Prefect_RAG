from prefect import flow, task
from openai import OpenAI
import faiss
import numpy as np
import os
from dotenv import load_dotenv


load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


@task
def load_data(file_path="data.txt"):
    """
    Loads documents from a text file. Each line is considered a separate document.
    """
    docs = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                docs.append(line)
    return docs

@task
def chunk_data(docs, chunk_size=50):
    chunks = []
    for doc in docs:
        for i in range(0, len(doc), chunk_size):
            chunks.append(doc[i:i+chunk_size])
    return chunks

@task
def embed_texts(texts):
    response = client.embeddings.create(
        model="text-embedding-3-large",
        input=texts
    )
    embeddings = [np.array(data.embedding, dtype=np.float32) for data in response.data]
    return np.array(embeddings)

@task
def build_index(embeddings):
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)
    return index

@task
def get_query_embedding(query):
    response = client.embeddings.create(
        model="text-embedding-3-large",
        input=[query]
    )
    embedding = np.array(response.data[0].embedding, dtype=np.float32).reshape(1, -1)
    return embedding

@task
def query_index(index, query_embedding, top_k=1):
    distances, indices = index.search(query_embedding, top_k)
    return indices[0][0], distances[0][0]

@task
def answer_question(context, question):
    prompt = f"Context:\n{context}\n\nQuestion: {question}\nAnswer:"
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=150,
        temperature=0.3,
    )
    return completion.choices[0].message.content.strip()

@flow(name="rag-pipeline")
def rag_pipeline(question: str, file_path: str = "data.txt"):
    docs = load_data(file_path)
    chunks = chunk_data(docs)
    embeddings = embed_texts(chunks)
    index = build_index(embeddings)

    query_emb = get_query_embedding(question)
    idx, dist = query_index(index, query_emb)

    context = chunks[idx]
    answer = answer_question(context, question)

    return answer, context, dist