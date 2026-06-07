from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import tempfile, os, shutil

from langchain_groq import ChatGroq
from langchain_community.document_loaders import PyPDFLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

app = FastAPI(
    title="RAG Chatbot API",
    description="Upload a PDF and ask questions — powered by pgvector + Groq",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    # allow_origins=[
    #     "http://localhost:3000",
    #     "https://*.vercel.app",
    # ],
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

VECTOR_DIR = "./chroma_db"
COLLECTION_NAME = "rag_documents"

COLLECTION_NAME = "rag_documents"
qa_chain = None


class ChatRequest(BaseModel):
    question: str


@app.get("/")
def health_check():
    return {"status": "running", "vector_db": "chroma local"}


@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    global qa_chain

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    loader = PyPDFLoader(tmp_path)
    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = splitter.split_documents(documents)

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    if os.path.exists(VECTOR_DIR):
        shutil.rmtree(VECTOR_DIR)

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
        persist_directory=VECTOR_DIR,
    )

    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0
    )

    prompt = ChatPromptTemplate.from_template("""
Answer the question based only on the context below.
If you don't know the answer, say "I don't have enough information to answer that."

Context: {context}

Question: {question}
""")

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    qa_chain = (
        {
            "context": retriever | format_docs,
            "question": RunnablePassthrough()
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    os.unlink(tmp_path)

    return {
        "message": f"PDF loaded. {len(chunks)} chunks stored in ChromaDB. Ready to chat!"
    }


@app.post("/chat")
async def chat(req: ChatRequest):
    if not qa_chain:
        return {"answer": "Please upload a PDF first."}

    result = qa_chain.invoke(req.question)
    return {"answer": result}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)