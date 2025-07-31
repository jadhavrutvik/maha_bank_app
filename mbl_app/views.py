import os
import google.generativeai as genai
from rest_framework.decorators import api_view
from rest_framework.response import Response
from mbl_app.scraper import *
from mbl_app.embeddings import *
from dotenv import load_dotenv,find_dotenv
APP_DIR = os.path.dirname(os.path.abspath(__file__))

load_dotenv(find_dotenv(os.path.join(APP_DIR,".env")))


genai.configure(api_key=os.getenv("gemini_api_key"))

@api_view(["GET"])
def loan_scraper_api(request):
    """
    Triggers loan data scraping and saves the result to text files.

    Returns a success response with the scraped data or an error message if scraping fails.
    """
    try:
        data = run_full_scrape()
        save_to_text_files(data)  
        return Response({"status": "success", "message": "Scraping completed and saved.", "data": data})
    except Exception as e:
        return Response({"status": "error", "message": str(e)}, status=500)

    

@api_view(["GET"])
def generate_embeddings_api(request):
    """
    Creates and saves sentence embeddings and FAISS index from given texts.

    Embeddings are stored in FAISS format for fast similarity search; original texts saved separately.
    """
    try:
        texts = load_texts()
        if not texts:
            return Response({"status": "error", "message": "No .txt files found in data/ directory."}, status=404)

        msg = create_embeddings(texts)
        return Response({"status": "success", "message": msg})
    
    except Exception as e:
        return Response({"status": "error", "message": str(e)}, status=500)


@api_view(["POST"])
def answer_question_api(request):
    """
    POST API to answer user questions using semantic search and Gemini.

    Finds relevant context from embeddings and queries Gemini for a response.
    """
    try:
        question = request.data.get("question")

        if not question:
            return Response({"status": "error", "message": "Missing 'question' in request body."}, status=400)

        chunks = search_similar_chunks(question, top_k=3)
        context = "\n\n".join(chunks)

        prompt = f"""
            You are a specialized bank assistant. You must ONLY use the information provided in the context below to answer the user's question.

            Strict Rules:
            - Do not guess or invent details.
            - Do not mention external links, websites, or refer the user to other sources.
            - Do not summarize sections (e.g., "see Rate of Interest section") or mention the document structure.
            - Do not include unnecessary explanations, politeness, or greetings.
            - Respond like a bank manager giving a direct and informative reply.
            - Be concise, factual, and align exactly with the user's question.

            Context:
            {context}

            Question:
            {question}

            Answer:"""

        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)
        return Response({"status": "success", "question": question, "answer": response.text})

    except Exception as e:
        return Response({"status": "error", "message": str(e)}, status=500)
