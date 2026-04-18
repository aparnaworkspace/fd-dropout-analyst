"""
FD Dropout Analyst — RAG-powered cohort report generator.
Loads cohort stats, retrieves relevant knowledge, and generates
a professional analyst report for each dropout cohort.
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
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is missing. Run: export GROQ_API_KEY=your_key")


# --- Prompt ---
ANALYST_PROMPT = PromptTemplate(
    input_variables=["cohort_name", "cohort_stats", "retrieved_context"],
    template="""
You are a senior data analyst at Blostem, an Indian fintech infrastructure
company that powers Fixed Deposit bookings for 30+ platforms including
MobiKwik, Upstox, and Jupiter.

You have behavioral data about a cohort of users who dropped off before
completing their FD booking. Your job is to write the kind of concise,
actionable report a product manager reads on Monday morning to decide
what to do that week.

COHORT NAME: {cohort_name}

COHORT BEHAVIORAL STATS:
{cohort_stats}

RELEVANT CONTEXT FROM KNOWLEDGE BASE:
{retrieved_context}

Write a report with exactly three labeled sections:

FINDING
Two sentences. What is happening with this cohort? What does the data
specifically tell us — use the actual numbers from the stats above.

ROOT CAUSE
Two sentences. What is the underlying behavioral reason this cohort is
dropping off? Reference specific friction points relevant to Indian
fintech users — KYC complexity, choice overload, financial literacy gaps,
Tier 2 city trust deficit, or low intent as appropriate.

RECOMMENDED ACTION
Two to three sentences. What specific intervention should the product team
trigger this week? Include the channel (WhatsApp, push, in-app), timing
(within 2 hours, 48 hours, weekly batch), and the exact message angle.
IMPORTANT: Match intervention intensity to intent level. Silent Churners
have low intent — recommend only lightweight batch interventions like
weekly rate-change alerts, never individual WhatsApp messages or human
agent assignment. KYC Dropouts have high intent — recommend immediate,
personalised outreach. Do not give the same recommendation to every cohort.

Write in plain professional English. No bullet points. No markdown formatting.
No filler phrases. Sound like someone who has shipped fintech products in India.
"""
)


# --- Vector Store ---
def build_vector_store():
    """
    Load markdown files from knowledge base, split into chunks,
    and build a FAISS vector store using sentence-transformer embeddings.
    """
    loader = DirectoryLoader(
        KNOWLEDGE_BASE_DIR,
        glob="**/*.md",
        loader_cls=TextLoader
    )
    documents = loader.load()

    if not documents:
        raise ValueError(f"No documents found in {KNOWLEDGE_BASE_DIR}")

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
    """
    Retrieve the most semantically relevant knowledge base chunks
    for a given cohort using similarity search.
    """
    query = f"""
    {cohort_name} dropout behavior in Indian fintech FD platform.
    Days since login: {cohort_stats.get('avg_days_since_login', 0)}.
    KYC drop rate: {cohort_stats.get('pct_dropped_kyc', 0)}%.
    First-time investors: {cohort_stats.get('pct_first_time', 0)}%.
    Average sessions before drop-off: {cohort_stats.get('avg_sessions', 0)}.
    Average banks compared: {cohort_stats.get('avg_banks_compared', 0)}.
    """
    docs = vector_store.similarity_search(query, k=top_k)

    if not docs:
        return "No relevant context found."

    return "\n\n".join([doc.page_content for doc in docs])


# --- Report Generation ---
def generate_report(cohort_name, cohort_stats, retrieved_context):
    """
    Call Groq LLM with structured prompt to generate
    a three-section analyst report for the given cohort.
    """
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
            max_tokens=500
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"ERROR generating report for {cohort_name}: {str(e)}"


# --- Main Pipeline ---
def run_analyst():
    """
    Full pipeline: load cohort stats → build RAG vector store →
    retrieve context per cohort → generate reports → save JSON output.
    """
    print("Loading cohort stats...")

    if not os.path.exists(COHORT_STATS_PATH):
        raise FileNotFoundError(f"Missing: {COHORT_STATS_PATH}. Run model/segment.py first.")

    with open(COHORT_STATS_PATH, "r") as f:
        cohort_stats = json.load(f)

    print("Building RAG vector store from knowledge base...")
    vector_store = build_vector_store()
    print(f"Vector store built from: {KNOWLEDGE_BASE_DIR}")

    reports = {}

    for cohort_name, stats in cohort_stats.items():
        print(f"\nGenerating report: {cohort_name}...")

        context = retrieve_context(vector_store, cohort_name, stats)
        report = generate_report(cohort_name, stats, context)

        reports[cohort_name] = {
            "cohort_stats": stats,
            "analyst_report": report
        }

        print("-" * 60)
        print(report)
        print("-" * 60)

    with open(REPORTS_OUTPUT_PATH, "w") as f:
        json.dump(reports, f, indent=2)

    print(f"\nAll reports saved to {REPORTS_OUTPUT_PATH}")
    return reports


# --- Entry Point ---
if __name__ == "__main__":
    run_analyst()