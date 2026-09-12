from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from vectorstore.chroma_store import Retriever
from llm.llm_client import get_llm_completion

router = APIRouter()


class ChatRequest(BaseModel):
    question: str
    company: str | None = None
    year: int | None = None


@router.post("/chat")
async def chat(request: ChatRequest):
    try:
        # Initialize retriever
        retriever = Retriever()

        # Retrieve relevant context
        if request.company and request.year:
            docs = retriever.invoke(
                query=request.question,
                company=request.company,
                year=request.year
            )
        else:
            docs = retriever.invoke(
                query=request.question
            )

        context = "\n\n".join(doc.page_content for doc in docs)

        # Build chat prompt
        prompt = (
            f"Context from corporate reports:\n{context}\n\n"
            f"User Question: {request.question}\n\n"
            "Provide a clear, detailed financial analysis based on the context above."
        )

        answer = get_llm_completion(
            prompt=prompt,
            system_prompt="You are an expert financial analyst. Use the following context from corporate reports to answer the user's question. If the context does not contain relevant information, politely indicate that you do not have enough data."
        )

        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
