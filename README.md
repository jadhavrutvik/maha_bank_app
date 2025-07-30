## 🔍 **Loan Product Assistant - Bank of Maharashtra**

A lightweight Retrieval-Augmented Generation (RAG) application to answer user queries related to **Bank of Maharashtra's** loan schemes using **web scraping**, **semantic search**, and **LLMs (Gemini)**.

---

### 🔑 **Key Features**
- Focuses on **Personal Loan**, **Home Loan**, and **Flexi Home Loan** schemes
- Semantic similarity search using **FAISS + Sentence Transformers**
- Answers are generated **only from verified scraped content**
- Uses **Gemini Flash** model for low-latency, high-quality completions

---

### ⚙️ **Project Setup**

#### 1. Clone the Repository
```bash
git clone -b maha_bank_repo https://github.com/jadhavrutvik/maha_bank_app.git
cd maha_bank_app
```

#### 2. Set Up a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### 3. Install Requirements
```bash
pip install -r requirements.txt
```

#### 4. Set Environment Variables
Create a `.env` file in the project root:
```ini
GOOGLE_API_KEY=your_gemini_api_key
```
Alternatively, update the hardcoded key inside `views.py` (not recommended for production).

#### 5. Run the Django Server
```bash
python manage.py runserver
```

---

### 🔌 **API Endpoints**

| Method | Endpoint             | Description                                  |
|--------|----------------------|----------------------------------------------|
| GET    | /loan-scraper        | Scrapes bank loan content and saves as .txt |
| GET    | /generate-embeddings | Generates FAISS index and text embeddings    |
| POST   | /answer-question     | Accepts question and returns Gemini response |

---

### 🧱 **Architecture Overview**

- **Web Scraping**: `requests`, `BeautifulSoup`
- **Embeddings**: `sentence-transformers (all-MiniLM-L6-v2)`
- **Vector Search**: `FAISS`
- **LLM Integration**: `google.generativeai (Gemini Flash)`
- **Framework**: `Django + DRF`

---

### 📄 **Data Strategy**

- **Source**: Scraped from official loan pages on Bank of Maharashtra’s website
- **Cleaning**: Retains relevant tags only (`<ul class="normlist">`, `<div class="inner_post_content">`)
- **Storage**: Saves each page as individual `.txt` files
- **Chunking**: Used whole documents as semantic chunks (no splitting needed)

---

### 🧠 **Model Selection**

#### 🔹 Embedding Model
- **Model**: `all-MiniLM-L6-v2`
- **Why**: Lightweight, fast, accurate for sentence-level comparison

#### 🔹 LLM Model
- **Model**: `Gemini Flash 2.0`
- **Why**: Google-hosted, fast response for prompt + context tasks

---

### 🛠️ **AI Tools Used**

| Tool                  | Purpose                            |
|-----------------------|------------------------------------|
| Gemini (Google AI)    | Final answer generation            |
| FAISS                 | Context retrieval via vector search |
| Sentence Transformers | Embedding generation               |

---

### 🧗 **Challenges Faced**
- 🌀 Inconsistent HTML structures across pages (`.in-loan-box2`, `.normlist`, etc.)
- 🔁 Duplicate and noisy content in subpages
- 🧾 Gemini output needed prompt tuning for bank-style answers

---

### 🚀 **Potential Improvements**
- ✂️ Token-level chunking to boost retrieval accuracy
- 🌐 Async scraping to reduce scrape time
- 💬 Gemini streaming for better UX
- 🧾 Metadata tagging for improved filtering
- 🖥️ React or Next.js frontend for user interface

---

### 📬 **Example Usage**

#### 🔸 POST `/answer-question`
**Request:**
```json
{
  "question": "What is the interest rate for personal loan?"
}
```
**Response:**
```json
{
  "status": "success",
  "question": "What is the interest rate for personal loan?",
  "answer": "For salaried borrowers, the interest ranges from RLLR + 0.70% to RLLR + 5.00%, depending on CIBIL score and account type."
}
```

---

### 🧪 **Quick Commands**
```bash
# Step 1: Scrape loan data
curl http://127.0.0.1:8000/loan-scraper

# Step 2: Generate embeddings
curl http://127.0.0.1:8000/generate-embeddings

# Step 3: Ask a question
curl -X POST http://127.0.0.1:8000/answer-question      -H "Content-Type: application/json"      -d '{"question": "What is the maximum tenure for a home loan?"}'
```

---

### 🙌 **Contributors**
- [Rutvik Jadhav] - Generative AI Developer