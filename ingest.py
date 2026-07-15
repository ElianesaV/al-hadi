import os
import time
from dotenv import load_dotenv
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()

KNOWLEDGE_BASE_PATH = os.getenv("KNOWLEDGE_BASE_PATH")
if not KNOWLEDGE_BASE_PATH:
    raise ValueError("KNOWLEDGE_BASE_PATH not set in .env file")


def load_documents():
    documents = []
    for category in os.listdir(KNOWLEDGE_BASE_PATH):
        category_path = os.path.join(KNOWLEDGE_BASE_PATH, category)
        if os.path.isdir(category_path):
            for filename in os.listdir(category_path):
                if filename.endswith(".pdf"):
                    filepath = os.path.join(category_path, filename)
                    print(f"Loading: {category}/{filename}")
                    loader = PyMuPDFLoader(filepath)
                    docs = loader.load()
                    filtered = []
                    for doc in docs:
                        if len(doc.page_content.strip()) < 200:
                            continue
                        doc.metadata["category"] = category
                        doc.metadata["filename"] = filename
                        filtered.append(doc)
                    documents.extend(filtered)
    return documents


def split_documents(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )
    return splitter.split_documents(documents)


def store_embeddings(chunks):
    embeddings = GoogleGenerativeAIEmbeddings(
        model="gemini-embedding-2-preview",
        google_api_key=os.getenv("GEMINI_API_KEY")
    )

    client = QdrantClient(
        url=os.getenv("QDRANT_URL"),
        api_key=os.getenv("QDRANT_API_KEY")
    )

    # Get existing chunk hashes to skip already ingested chunks
    existing_ids = set()
    if client.collection_exists("al_hadi"):
        count = client.count(collection_name="al_hadi").count
        if count == 0:
            print("Collection exists but is empty. Recreating...")
            client.delete_collection("al_hadi")
            client.create_collection(
                collection_name="al_hadi",
                vectors_config=VectorParams(size=3072, distance=Distance.COSINE)
            )
        else:
            print(f"Collection exists with {count} vectors. Checking for new chunks only...")
            offset = None
            while True:
                results, offset = client.scroll(
                    collection_name="al_hadi",
                    limit=1000,
                    offset=offset,
                    with_payload=True
                )
                for point in results:
                    content = point.payload.get("page_content", "")
                    if content:
                        existing_ids.add(hash(content))
                if offset is None:
                    break
    else:
        print("Creating new collection...")
        client.create_collection(
            collection_name="al_hadi",
            vectors_config=VectorParams(size=3072, distance=Distance.COSINE)
        )

    # Filter out chunks that already exist by content hash
    new_chunks = [c for c in chunks if hash(c.page_content) not in existing_ids]

    if not new_chunks:
        print("No new documents to add. Knowledge base is up to date.")
        return

    print(f"Adding {len(new_chunks)} new chunks...")

    vectorstore = QdrantVectorStore(
        client=client,
        collection_name="al_hadi",
        embedding=embeddings
    )

    batch_size = 10
    for i in range(0, len(new_chunks), batch_size):
        batch = new_chunks[i: i + batch_size]
        print(f"Processing batch {i//batch_size + 1} of {len(new_chunks)//batch_size + 1}...")
        try:
            vectorstore.add_documents(batch)
            time.sleep(6)
        except Exception as e:
            print(f"Error in batch {i//batch_size + 1}: {e}")
            continue

    print(f"Done. Added {len(new_chunks)} chunks to Qdrant Cloud.")


if __name__ == "__main__":
    print("Loading documents...")
    documents = load_documents()
    print(f"Loaded {len(documents)} pages")
    print("Splitting into chunks...")
    chunks = split_documents(documents)
    print(f"Created {len(chunks)} chunks")
    print("Generating embeddings and storing...")
    store_embeddings(chunks)
    print("Done. Knowledge base is ready.")
