<div align="center">
  <img src="app/static/img/hemav_logo_full.svg" alt="HemaV Logo" width="300" />
</div>

<h1 align="center">HemaV MedAssist 🩸</h1>
<p align="center">
  <strong>An AI-Powered Medical Knowledge Assistant specialized in Hematology and Iron Deficiency Anemia</strong>
</p>

<p align="center">
  <a href="#-quick-start">🚀 Quick Start</a> •
  <a href="#️-architecture--system-flow">🏗️ Architecture</a> •
  <a href="#-why-endee-vector-database">🧠 Why Endee?</a> •
  <a href="#-tech-stack">⚙️ Tech Stack</a>
</p>

---

## 📖 Overview

HemaV MedAssist is a high-performance **Retrieval-Augmented Generation (RAG)** application. It is designed to ingest complex medical literature (PDFs, research papers, clinical guidelines) and provide instant, perfectly grounded, hallunication-free answers to medical queries.

Built as an extremely sophisticated demonstration of the **Endee Vector Database**, this project processes **250+ pages of medical literature (1,547 semantic chunks)** and semantically retrieves the exact paragraphs needed to answer questions, citing its sources natively in the real-time chat interface.

---

## 🚀 Quick Start (Interactive Setup)

<details>
<summary><strong>👉 Step 1: Clone the Repository & Setup Environment</strong></summary>

```bash
git clone https://github.com/Ayush2554work/endee.io_ayush-kumar.git
cd endee.io_ayush-kumar

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```
</details>

<details>
<summary><strong>👉 Step 2: Start the Endee Vector Database (via Docker)</strong></summary>

The core of this application relies on the high-performance **Endee Vector Database** to perform ultra-fast Cosine Similarity searches across the parsed medical data.

1. Ensure **Docker Desktop** is running on your machine.
2. Run the Endee Docker container:
```bash
docker run -p 8080:8080 endeespace/endee:latest
```
*Leave this terminal window open in the background.*
</details>

<details>
<summary><strong>👉 Step 3: Run the Application!</strong></summary>

Open a new terminal window inside the project directory (ensure your virtual environment is still activated) and run:

```bash
python main.py
```

*This command automatically does two things:*
1. **Intelligent Ingestion:** It checks if the `hemav_medical_docs` index exists in Endee. If not, it parses all 9 medical PDFs in `data/medical_docs/`, chunks them, generates embeddings, and upserts **1,547 vectors** into the database.
2. **Starts the Server:** Once ingestion is verified, it launches the FastAPI server.

**Open your browser to [http://localhost:5000](http://localhost:5000) to use the app!**
</details>

<details>
<summary><strong>👉 Step 4: Add your Groq API Key (Optional)</strong></summary>

To generate the human-readable answers, the app uses the lightning-fast Groq Llama 3 LLM.
- You can add your API key securely directly in the Web UI by clicking the **⚙️ API Settings** button in the bottom left corner.
- *Alternatively, you can create a `.env` file in the root directory and add `GROQ_API_KEY=your_key_here`.*
</details>

---

## 🏗️ Architecture & System Flow

HemaV MedAssist employs a robust **Modular Pipeline Architecture**, ensuring a clean separation of concerns between data processing, embeddings, storage, and the web tier.

<details open>
<summary><strong>🔄 The RAG Lifecycle (How it works under the hood)</strong></summary>

1. **Document Parsing (`app/data/pdf_parser.py`)**: 
   - Reads complex, multi-column medical PDFs (like the 132-page WHO guidelines).
   - Extracts raw text while preserving page numbers for accurate citations.
2. **Semantic Chunking (`app/data/chunker.py`)**: 
   - Splits text into manageable `500-character` chunks with `50-character` overlaps.
   - This sliding-window approach ensures crucial medical context (like a symptom list spanning two paragraphs) isn't accidentally severed.
3. **Dense Embedding (`app/embeddings/`)**: 
   - Converts the raw text chunks into dense, 384-dimensional mathematical arrays (vectors) using HuggingFace's `all-MiniLM-L6-v2` transformer model.
4. **Vector Storage (`app/endee_integration/indexer.py`)**: 
   - Ingests the embeddings into the **Endee Vector Database** alongside metadata (source file, page number).
   - Configured to use `FLOAT16` precision to drastically reduce memory overhead while maintaining extreme accuracy.
5. **Real-time Querying (`app/rag_pipeline.py`)**: 
   - A user asks: *"What are the symptoms of Iron Deficiency?"*
   - The query is embedded, and Endee performs a sub-millisecond **Cosine Similarity** search across the 1,547 vectors, returning the Top-5 most relevant medical paragraphs.
   - The paragraphs and metadata are formatted into a rigorous prompt and sent to the **Groq Llama 3 LLM** to synthesize a final, clinically-grounded answer.
</details>

---

## 🧠 Why Endee Vector Database? (Instead of SQL)

Traditional relational databases (PostgreSQL, MySQL) are physically incapable of understanding the *meaning* of text. 

If a user searched for: **"Exhaustion from low iron"**
- **SQL (Keyword Search)**: `SELECT * FROM docs WHERE text LIKE '%Exhaustion from low iron%'`. This would fail miserably because the medical paper actually uses the words *"Fatigue associated with severe anemia"*.
- **Endee (Semantic Search)**: Uses the **Approximate Nearest Neighbor (HNSW)** algorithm to find vectors that point in the same mathematical direction. It understands that "exhaustion" and "fatigue" inhabit the exact same semantic space. 

By measuring the **Cosine Similarity** angle between the user's string of text and the 1,547 medical chunks, Endee enables true cognitive retrieval, eliminating hallucinations and ensuring the AI only ever speaks from the provided literature.

---

## ⚙️ Tech Stack

### 🚀 Core Intelligence
* **Vector Database:** [Endee](https://github.com/endee-io/endee) (High-performance HNSW vector search)
* **LLM Engine:** Groq API (Running Llama-3.3-70b-versatile for ultra-low latency generation)
* **Embedding Model:** `sentence-transformers/all-MiniLM-L6-v2` (Local execution for speed and privacy)

### 🧰 Backend & Data Pipeline
* **Framework:** FastAPI (Asynchronous, high-throughput Python server)
* **Data Processing:** PyPDF2 (Robust extraction from immense clinical documents)
* **Template Engine:** Jinja2

### 🎨 Frontend UI
* **Design System:** Custom CSS Architecture (Glassmorphism, CSS Variables, Responsive Grids)
* **Interactivity:** Vanilla JavaScript (Zero-dependency, utilizing `localStorage` to securely store user-provided Groq API keys directly in the browser).

---

<div align="center">
  <i>Developed for the Endee.io Open Source AI Challenge</i><br>
  <b>Ayush Kumar</b> | <a href="mailto:ayushkumarwork2554@gmail.com">ayushkumarwork2554@gmail.com</a> | <a href="https://github.com/Ayush2554work/">GitHub Profile</a>
</div>
