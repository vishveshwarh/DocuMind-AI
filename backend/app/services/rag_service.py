# Core RAG logic — builds and runs the chain
# Uses LCEL (LangChain Expression Language) — standard in LangChain v1.x

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from app.config import settings
from app.logger import get_logger

logger = get_logger(__name__)

class RAGService:
    def __init__(self):
        self.qa_chain = None
        logger.info(f"Initialising LLM: {settings.GROQ_MODEL}")
        self.llm = ChatGroq(
            model=settings.GROQ_MODEL,
            temperature=settings.GROQ_TEMPERATURE,
            api_key=settings.GROQ_API_KEY
        )
        logger.info("LLM initialised successfully")

    def build_chain(self, retriever, language_instruction_fn):
        """
        Build LCEL RAG chain.
        language_instruction_fn: callable that returns current language instruction string
        Called at query time so language preference changes take effect immediately.
        """
        logger.info("Building RAG chain")

        prompt = ChatPromptTemplate.from_template("""
You are a helpful assistant. Answer the question based only on the context below.
If the answer is not in the context, say "I don't have enough information to answer that."

{language_instruction}

Context: {context}

Question: {question}
""")
        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)

        # LCEL chain — each | passes output to next step
        self.qa_chain = (
            {
                "context": retriever | format_docs,
                "question": RunnablePassthrough(),
                "language_instruction": lambda _: language_instruction_fn()
            }
            | prompt
            | self.llm
            | StrOutputParser()
        )

        logger.info("RAG chain built successfully")

    def answer(self, question: str) -> str:
        """Run question through RAG chain and return answer"""
        if not self.qa_chain:
            logger.warning("Chat attempted before PDF upload")
            raise ValueError("No document loaded. Please upload a PDF first.")

        logger.info(f"Processing question: {question[:80]}...")  # log first 80 chars only

        try:
            result = self.qa_chain.invoke(question)
            logger.info("Answer generated successfully")
            return result
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            raise

# Single instance
rag_service = RAGService()