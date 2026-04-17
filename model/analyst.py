"""
FD Dropout Analyst — RAG-powered cohort report generator.
"""

import json
import os
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import PromptTemplate
from groq import Groq


# --- Configuration ---
KNOWLEDGE_BASE_DIR = "knowledge_base"
COHORT_STATS_PATH = "model/cohort_stats.json"
REPORTS_OUTPUT_PATH = "model/analyst_reports.json"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
TOP_K_CHUNKS = 5

# FIX: Clean API key
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()

if not GROQ_API_KEY:
    raise ValueError("❌ GROQ_API_KEY is missing or invalid. Check your .env file.")


# --- Prompt ---
ANALYST_PROMPT = PromptTemplate(
    input_variables=["cohort_name", "cohort_stats", "retrieved_context"],
    template="""
You are a senior data analyst at a fintech company called Blostem.

You have been given behavioral data about a cohort of users who are at
risk of dropping off before completing their Fixed Deposit booking.

COHORT NAME: {cohort_name}

COHORT BEHAVIORAL STATS:
{cohort_stats}

RELEVANT CONTEXT FROM KNOWLEDGE BASE:
{retrieved_context}

Write a report with exactly three sections:

1. FINDING (2 sentences)
2. ROOT CAUSE (2 sentences)
3. RECOMMENDED ACTION (2-3 sentences)

Rules:
- No bullet points
- No extra headings
- No fluff
- Be specific, practical, and action-driven
- Sound like a fintech analyst with real product experience in India
"""
)


# --- Vector Store ---
def build_vector_store():
    loader = DirectoryLoader(
        KNOWLEDGE_BASE_DIR,
        glob="**/*.md",
        loader_cls=TextLoader
    )

    documents = loader.load()

    if not documents:
        raise ValueError("❌ No documents found in knowledge_base")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )

    chunks = splitter.split_documents(documents)

    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

    vector_store = FAISS.from_documents(chunks, embeddings)

    return vector_store


# --- Retrieval ---
def retrieve_context(vector_store, cohort_name, cohort_stats, top_k=TOP_K_CHUNKS):

    query = f"""
    {cohort_name} dropout behavior in Indian fintech FD platform.
    Days since login: {cohort_stats.get('avg_days_since_login', 0)}.
    KYC drop rate: {cohort_stats.get('pct_dropped_kyc', 0)}%.
    First-time investors: {cohort_stats.get('pct_first_time', 0)}%.
    Average sessions: {cohort_stats.get('avg_sessions', 0)}.
    """

    docs = vector_store.similarity_search(query, k=top_k)

    if not docs:
        return "No relevant context found."

    return "\n\n".join([doc.page_content for doc in docs])


# --- LLM Call ---
def generate_report(cohort_name, cohort_stats, retrieved_context):

    client = Groq(api_key=GROQ_API_KEY)

    prompt = ANALYST_PROMPT.format(
        cohort_name=cohort_name,
        cohort_stats=json.dumps(cohort_stats, indent=2),
        retrieved_context=retrieved_context
    )

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            max_tokens=400
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"❌ ERROR generating report: {str(e)}"


# --- Main Pipeline ---
def run_analyst():

    print("Loading cohort stats...")

    if not os.path.exists(COHORT_STATS_PATH):
        raise FileNotFoundError(f"❌ Missing file: {COHORT_STATS_PATH}")

    with open(COHORT_STATS_PATH, "r") as f:
        cohort_stats = json.load(f)

    print("Building RAG vector store from knowledge base...")
    vector_store = build_vector_store()
    print(f"Vector store built from: {KNOWLEDGE_BASE_DIR}")

    reports = {}

    for cohort_name, stats in cohort_stats.items():

        print(f"\nGenerating report for: {cohort_name}...")

        context = retrieve_context(vector_store, cohort_name, stats)
        report = generate_report(cohort_name, stats, context)

        reports[cohort_name] = {
            "cohort_stats": stats,
            "analyst_report": report
        }

        print("------------------------------------------------------------")
        print(report)
        print("------------------------------------------------------------")

    with open(REPORTS_OUTPUT_PATH, "w") as f:
        json.dump(reports, f, indent=2)

    print(f"\n✅ All reports saved to {REPORTS_OUTPUT_PATH}")

    return reports


# --- Entry Point ---
if __name__ == "__main__":
    run_analyst()