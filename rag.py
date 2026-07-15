import os
from dotenv import load_dotenv
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()

KNOWLEDGE_BASE_PATH = os.getenv("KNOWLEDGE_BASE_PATH")
VECTORSTORE_PATH = os.path.join(
    os.path.dirname(KNOWLEDGE_BASE_PATH), "vectorstore"
)



_vectorstore = None

def load_vectorstore():
    global _vectorstore
    if _vectorstore is None:
        embeddings = GoogleGenerativeAIEmbeddings(
            model="gemini-embedding-2-preview",
            google_api_key=os.getenv("GEMINI_API_KEY")
        )
        
        client = QdrantClient(
            url=os.getenv("QDRANT_URL"),
            api_key=os.getenv("QDRANT_API_KEY")
        )
        
        _vectorstore = QdrantVectorStore(
            client=client,
            collection_name="al_hadi",
            embedding=embeddings
        )
    return _vectorstore


# All categories treated as priority — nothing gets deprioritized.
# Historical figures, jurisprudence, and theology are equally important.
PRIORITY_CATEGORIES = {
    "theology",
    "gospels",
    "teachings",
    "jurisprudence",
    "introductory",
    "classical_refs",
    "historical_figures",  # Added: covers Abu Bakr, Umar, Uthman, Muawiya, Yazid, Paul etc.
    "history",             # Added: general historical content
    "aropl",               # Added: direct AROPL content
    "imams",               # Added: Ahlu Al Bayt content
}


def retrieve_context(question, k=7):
    vectorstore = load_vectorstore()

    seen = set()
    seen_files = set()
    priority = []
    secondary = []
    sources = set()

    results = vectorstore.similarity_search(question, k=k)

    for doc in results:
        if doc.page_content not in seen:
            seen.add(doc.page_content)
            
            category = doc.metadata.get("category", "unknown")
            
            filename = doc.metadata.get("filename", "Unknown")                  
            page = doc.metadata.get("page", "?")
            
            clean_name = (
                filename
                .replace(".pdf", "")
                .replace("English", "")
                .replace("ENG", "")
                .replace("EN", "")
                .replace("-", " ")
                .replace("_", " ")
                .title()
            )
            
            # 2. Store the clean name BACK into the doc object temporarily 
            # so the second loop can see it
            doc.metadata["computed_clean_name"] = clean_name
            
            if filename not in seen_files and len(seen_files) < 3:
                seen_files.add(filename)
                sources.add(f"{clean_name} — PDF p.{page}")

            if category.lower() in PRIORITY_CATEGORIES:
                priority.append(doc)
            else:
                secondary.append(doc)

    all_results = priority + secondary
    
    context_text = "\n\n".join([
        f"SOURCE: {doc.metadata.get('computed_clean_name', 'Unknown')} (Page {doc.metadata.get('page', '?')})\n"
        f"CONTENT: {doc.page_content}"
        for doc in all_results
    ])
    
    return context_text, list(sources)
