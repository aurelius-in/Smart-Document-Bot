import json
from typing import Any, Dict, List, Optional

from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma

from .base import BaseAgent, Tool
from ..models.base import AgentResult, AgentType, QAResponse


class VectorSearchTool(Tool):
    """Vector search tool for document retrieval"""
    
    def __init__(self):
        super().__init__("vector_search", "Search documents using vector embeddings")
        self.embeddings = OpenAIEmbeddings()
        self.vectorstore = None
    
    async def execute(self, query: str, documents: List[str], **kwargs) -> List[Dict[str, Any]]:
        """Search for relevant document chunks"""
        try:
            # Create vector store from documents
            texts = []
            metadatas = []
            
            for i, doc in enumerate(documents):
                # Split document into chunks
                chunks = self._chunk_text(doc, chunk_size=1000, overlap=200)
                for j, chunk in enumerate(chunks):
                    texts.append(chunk)
                    metadatas.append({
                        "doc_id": i,
                        "chunk_id": j,
                        "start_char": j * 800,  # Approximate
                        "end_char": (j + 1) * 800
                    })
            
            if not texts:
                return []
            
            # Create vector store
            self.vectorstore = Chroma.from_texts(
                texts=texts,
                embedding=self.embeddings,
                metadatas=metadatas
            )
            
            # Search
            results = self.vectorstore.similarity_search_with_score(query, k=5)
            
            # Format results
            formatted_results = []
            for doc, score in results:
                formatted_results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "similarity_score": 1 - score,  # Convert distance to similarity
                    "start_char": doc.metadata.get("start_char", 0),
                    "end_char": doc.metadata.get("end_char", 0)
                })
            
            return formatted_results
            
        except Exception as e:
            return []
    
    def _chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks"""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            
            # Try to break at sentence boundary
            if end < len(text):
                last_period = chunk.rfind('.')
                last_newline = chunk.rfind('\n')
                break_point = max(last_period, last_newline)
                
                if break_point > start + chunk_size // 2:
                    chunk = text[start:start + break_point + 1]
                    end = start + break_point + 1
            
            chunks.append(chunk)
            start = end - overlap
        
        return chunks


class AnswerGenerationTool(Tool):
    """Generate answers with citations"""
    
    def __init__(self):
        super().__init__("generate_answer", "Generate answer with citations")
    
    async def execute(self, question: str, context_chunks: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]:
        """Generate answer based on context chunks"""
        try:
            from langchain.chat_models import ChatOpenAI
            from langchain.schema import HumanMessage
            
            llm = ChatOpenAI(model="gpt-4", temperature=0.1)
            
            # Prepare context
            context_text = "\n\n".join([
                f"Chunk {i+1} (Score: {chunk['similarity_score']:.2f}):\n{chunk['content']}"
                for i, chunk in enumerate(context_chunks[:3])  # Top 3 chunks
            ])
            
            prompt = f"""
Answer the question based on the provided context. Include specific citations to the source chunks.

QUESTION: {question}

CONTEXT:
{context_text}

TASK:
1. Provide a comprehensive answer based on the context
2. Include specific citations to relevant chunks
3. If information is not in the context, say so
4. Provide confidence score (0.0-1.0)

Respond with JSON:
{{
    "answer": "comprehensive answer with citations",
    "citations": [
        {{
            "chunk_id": 1,
            "content": "relevant text from chunk",
            "start_char": 123,
            "end_char": 456,
            "similarity_score": 0.85
        }}
    ],
    "confidence": 0.9,
    "sources": ["chunk_1", "chunk_2"]
}}
"""
            
            response = await llm.agenerate([[HumanMessage(content=prompt)]])
            result_text = response.generations[0][0].text.strip()
            
            # Extract JSON
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0]
            elif "```" in result_text:
                result_text = result_text.split("```")[1]
            
            return json.loads(result_text)
            
        except Exception as e:
            return {
                "answer": f"Unable to generate answer: {str(e)}",
                "citations": [],
                "confidence": 0.0,
                "sources": []
            }


class KnowledgeBaseSearchTool(Tool):
    """Search knowledge base for additional context"""
    
    def __init__(self):
        super().__init__("kb_search", "Search knowledge base for additional context")
    
    async def execute(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """Search knowledge base"""
        try:
            # In a real implementation, this would search a knowledge base
            # For demo purposes, return mock results
            
            mock_kb = {
                "hipaa": [
                    "HIPAA requires covered entities to protect patient health information",
                    "PHI must be secured and access controlled",
                    "Breach notification is required within 60 days"
                ],
                "sec": [
                    "SEC regulations require material information disclosure",
                    "Insider trading is prohibited",
                    "Financial statements must be accurate and complete"
                ],
                "contract": [
                    "Contracts must have clear terms and conditions",
                    "Liability clauses should be specific",
                    "Termination clauses are important for risk management"
                ]
            }
            
            results = []
            for topic, entries in mock_kb.items():
                if topic.lower() in query.lower():
                    for entry in entries:
                        results.append({
                            "content": entry,
                            "source": f"KB_{topic.upper()}",
                            "relevance": 0.8
                        })
            
            return results[:3]  # Top 3 results
            
        except Exception as e:
            return []


class QAAgent(BaseAgent):
    """Agent responsible for question answering with citations"""
    
    def __init__(self, llm_model: str = "gpt-4"):
        super().__init__("QAAgent", AgentType.QA)
        self.llm = ChatOpenAI(model=llm_model, temperature=0.1)
        
        # Add tools
        self.add_tool(VectorSearchTool())
        self.add_tool(AnswerGenerationTool())
        self.add_tool(KnowledgeBaseSearchTool())
    
    async def run(self, goal: str, context: Dict[str, Any]) -> AgentResult:
        """Main Q&A process"""
        question = context.get("question")
        if not question:
            return AgentResult(
                output=None,
                rationale="No question provided in context",
                confidence=0.0,
                next_suggested_action="Provide question in context"
            )
        
        try:
            # Get document content
            document = context.get("document")
            documents = []
            if document and hasattr(document, 'content'):
                documents.append(document.content)
            
            # Search for relevant chunks
            search_tool = self.get_tool("vector_search")
            context_chunks = await search_tool.execute(
                query=question,
                documents=documents
            )
            
            # Search knowledge base for additional context
            kb_tool = self.get_tool("kb_search")
            kb_results = await kb_tool.execute(query=question)
            
            # Combine context
            all_context = context_chunks + kb_results
            
            # Generate answer
            answer_tool = self.get_tool("generate_answer")
            answer_result = await answer_tool.execute(
                question=question,
                context_chunks=all_context
            )
            
            # Create QAResponse object
            qa_response = QAResponse(
                answer=answer_result.get("answer", "No answer generated"),
                citations=answer_result.get("citations", []),
                confidence=answer_result.get("confidence", 0.0),
                sources=answer_result.get("sources", [])
            )
            
            # Calculate overall confidence
            overall_confidence = answer_result.get("confidence", 0.0)
            
            # Adjust confidence based on context quality
            if context_chunks:
                avg_similarity = sum(chunk.get("similarity_score", 0) for chunk in context_chunks) / len(context_chunks)
                overall_confidence = (overall_confidence + avg_similarity) / 2
            
            # Generate rationale
            rationale = f"Generated answer with {len(answer_result.get('citations', []))} citations. Context chunks: {len(context_chunks)}, KB results: {len(kb_results)}"
            
            return AgentResult(
                output=qa_response,
                rationale=rationale,
                confidence=overall_confidence,
                next_suggested_action="Ask follow-up question" if overall_confidence > 0.7 else "Refine question for better results"
            )
            
        except Exception as e:
            return AgentResult(
                output=QAResponse(
                    answer=f"Error generating answer: {str(e)}",
                    citations=[],
                    confidence=0.0,
                    sources=[]
                ),
                rationale=f"Q&A failed: {str(e)}",
                confidence=0.0,
                next_suggested_action="Try rephrasing the question"
            )
    
    async def answer_question(self, question: str, document_content: str) -> QAResponse:
        """Convenience method for answering questions"""
        context = {
            "question": question,
            "document": type('Document', (), {'content': document_content})()
        }
        
        result = await self.run("Answer question", context)
        return result.output if result.output else QAResponse(
            answer="Unable to generate answer",
            citations=[],
            confidence=0.0,
            sources=[]
        )
    
    def get_answer_quality_metrics(self, response: QAResponse) -> Dict[str, Any]:
        """Get quality metrics for an answer"""
        return {
            "confidence": response.confidence,
            "citation_count": len(response.citations),
            "source_count": len(response.sources),
            "answer_length": len(response.answer),
            "has_citations": len(response.citations) > 0,
            "quality_score": min(1.0, response.confidence * (1 + len(response.citations) * 0.1))
        }
