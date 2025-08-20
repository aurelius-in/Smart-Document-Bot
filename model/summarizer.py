import os
import re
from typing import Dict, List, Optional, Any
from openai import OpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.summarize import load_summarize_chain
from langchain.chat_models import ChatOpenAI
from langchain.schema import Document

class AdvancedSummarizer:
    """Advanced AI-powered document summarization using OpenAI GPT models"""
    
    def __init__(self, model_name: str = "gpt-4", max_tokens: int = 1000):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=4000,
            chunk_overlap=200,
            length_function=len,
        )
    
    def summarize_text(self, text: str, summary_type: str = "extractive", 
                      max_length: int = 500) -> Dict[str, Any]:
        """
        Advanced text summarization with multiple strategies
        
        Args:
            text: Input text to summarize
            summary_type: Type of summarization (extractive, abstractive, bullet_points, executive)
            max_length: Maximum length of summary
            
        Returns:
            Dictionary containing summary and metadata
        """
        if not text or len(text.strip()) < 100:
            return {
                "summary": text,
                "type": summary_type,
                "confidence": 1.0,
                "metadata": {"original_length": len(text), "summary_length": len(text)}
            }
        
        try:
            if summary_type == "extractive":
                return self._extractive_summarization(text, max_length)
            elif summary_type == "abstractive":
                return self._abstractive_summarization(text, max_length)
            elif summary_type == "bullet_points":
                return self._bullet_point_summarization(text, max_length)
            elif summary_type == "executive":
                return self._executive_summarization(text, max_length)
            else:
                return self._abstractive_summarization(text, max_length)
                
        except Exception as e:
            # Fallback to basic summarization
            return self._fallback_summarization(text, max_length)
    
    def _extractive_summarization(self, text: str, max_length: int) -> Dict[str, Any]:
        """Extractive summarization using key sentence extraction"""
        try:
            # Split text into sentences
            sentences = re.split(r'(?<=[.!?])\s+', text.strip())
            
            # Use OpenAI to score and select key sentences
            prompt = f"""
            Analyze the following text and identify the {max_length//50} most important sentences that best summarize the content.
            Focus on sentences that contain key information, main points, and conclusions.
            
            Text:
            {text}
            
            Return only the selected sentences in order, separated by newlines.
            """
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=self.max_tokens,
                temperature=0.1
            )
            
            summary = response.choices[0].message.content.strip()
            
            return {
                "summary": summary,
                "type": "extractive",
                "confidence": 0.9,
                "metadata": {
                    "original_length": len(text),
                    "summary_length": len(summary),
                    "compression_ratio": len(summary) / len(text) if len(text) > 0 else 0
                }
            }
            
        except Exception as e:
            return self._fallback_summarization(text, max_length)
    
    def _abstractive_summarization(self, text: str, max_length: int) -> Dict[str, Any]:
        """Abstractive summarization using GPT models"""
        try:
            # For long texts, use chunking
            if len(text) > 8000:
                return self._chunked_summarization(text, max_length)
            
            prompt = f"""
            Create a comprehensive summary of the following text in approximately {max_length} characters.
            The summary should capture the main points, key insights, and conclusions.
            Write in a clear, professional tone.
            
            Text:
            {text}
            
            Summary:
            """
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=self.max_tokens,
                temperature=0.3
            )
            
            summary = response.choices[0].message.content.strip()
            
            return {
                "summary": summary,
                "type": "abstractive",
                "confidence": 0.95,
                "metadata": {
                    "original_length": len(text),
                    "summary_length": len(summary),
                    "compression_ratio": len(summary) / len(text) if len(text) > 0 else 0
                }
            }
            
        except Exception as e:
            return self._fallback_summarization(text, max_length)
    
    def _bullet_point_summarization(self, text: str, max_length: int) -> Dict[str, Any]:
        """Bullet point summarization"""
        try:
            prompt = f"""
            Create a bullet-point summary of the following text with key points and insights.
            Use clear, concise bullet points that capture the main information.
            Limit to approximately {max_length} characters total.
            
            Text:
            {text}
            
            Bullet Point Summary:
            """
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=self.max_tokens,
                temperature=0.2
            )
            
            summary = response.choices[0].message.content.strip()
            
            return {
                "summary": summary,
                "type": "bullet_points",
                "confidence": 0.9,
                "metadata": {
                    "original_length": len(text),
                    "summary_length": len(summary),
                    "compression_ratio": len(summary) / len(text) if len(text) > 0 else 0
                }
            }
            
        except Exception as e:
            return self._fallback_summarization(text, max_length)
    
    def _executive_summarization(self, text: str, max_length: int) -> Dict[str, Any]:
        """Executive summary for business documents"""
        try:
            prompt = f"""
            Create an executive summary of the following text suitable for business leaders.
            Focus on key decisions, risks, opportunities, and actionable insights.
            Write in a professional, executive-level tone.
            Limit to approximately {max_length} characters.
            
            Text:
            {text}
            
            Executive Summary:
            """
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=self.max_tokens,
                temperature=0.2
            )
            
            summary = response.choices[0].message.content.strip()
            
            return {
                "summary": summary,
                "type": "executive",
                "confidence": 0.95,
                "metadata": {
                    "original_length": len(text),
                    "summary_length": len(summary),
                    "compression_ratio": len(summary) / len(text) if len(text) > 0 else 0
                }
            }
            
        except Exception as e:
            return self._fallback_summarization(text, max_length)
    
    def _chunked_summarization(self, text: str, max_length: int) -> Dict[str, Any]:
        """Handle long texts by chunking and summarizing"""
        try:
            # Split text into chunks
            chunks = self.text_splitter.split_text(text)
            
            # Summarize each chunk
            chunk_summaries = []
            for chunk in chunks:
                chunk_summary = self._abstractive_summarization(chunk, max_length // len(chunks))
                chunk_summaries.append(chunk_summary["summary"])
            
            # Combine chunk summaries
            combined_summary = " ".join(chunk_summaries)
            
            # Create final summary
            final_summary = self._abstractive_summarization(combined_summary, max_length)
            
            return {
                "summary": final_summary["summary"],
                "type": "chunked_abstractive",
                "confidence": 0.85,
                "metadata": {
                    "original_length": len(text),
                    "summary_length": len(final_summary["summary"]),
                    "chunks_processed": len(chunks),
                    "compression_ratio": len(final_summary["summary"]) / len(text) if len(text) > 0 else 0
                }
            }
            
        except Exception as e:
            return self._fallback_summarization(text, max_length)
    
    def _fallback_summarization(self, text: str, max_length: int) -> Dict[str, Any]:
        """Fallback summarization when AI fails"""
        sentences = re.split(r'(?<=[.!?])\s+', text.strip())
        
        # Simple extractive summarization
        if len(sentences) <= 3:
            summary = text
        else:
            # Take first, middle, and last sentences
            summary_parts = []
            summary_parts.append(sentences[0])
            
            if len(sentences) > 2:
                middle_idx = len(sentences) // 2
                summary_parts.append(sentences[middle_idx])
            
            if len(sentences) > 1:
                summary_parts.append(sentences[-1])
            
            summary = " ".join(summary_parts)
        
        # Truncate if too long
        if len(summary) > max_length:
            summary = summary[:max_length-3] + "..."
        
        return {
            "summary": summary,
            "type": "fallback",
            "confidence": 0.6,
            "metadata": {
                "original_length": len(text),
                "summary_length": len(summary),
                "compression_ratio": len(summary) / len(text) if len(text) > 0 else 0,
                "error": "AI summarization failed, using fallback method"
            }
        }
    
    def analyze_summary_quality(self, original_text: str, summary: str) -> Dict[str, Any]:
        """Analyze the quality of a summary"""
        try:
            prompt = f"""
            Analyze the quality of this summary compared to the original text.
            Rate the following aspects on a scale of 1-10:
            1. Completeness: Does it capture all key points?
            2. Accuracy: Is the information correct?
            3. Clarity: Is it easy to understand?
            4. Conciseness: Is it appropriately brief?
            5. Relevance: Does it focus on important information?
            
            Original Text:
            {original_text[:2000]}...
            
            Summary:
            {summary}
            
            Provide your analysis as JSON:
            {{
                "completeness": 8,
                "accuracy": 9,
                "clarity": 8,
                "conciseness": 7,
                "relevance": 9,
                "overall_score": 8.2,
                "strengths": ["Captures key points", "Clear language"],
                "improvements": ["Could include more details"]
            }}
            """
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.1
            )
            
            import json
            analysis = json.loads(response.choices[0].message.content.strip())
            return analysis
            
        except Exception as e:
            return {
                "completeness": 5,
                "accuracy": 5,
                "clarity": 5,
                "conciseness": 5,
                "relevance": 5,
                "overall_score": 5.0,
                "strengths": ["Fallback analysis"],
                "improvements": ["AI analysis failed"]
            }


# Backward compatibility function
def summarize_text(text: str, summary_type: str = "abstractive", max_length: int = 500) -> str:
    """
    Backward compatibility function for simple text summarization
    
    Args:
        text: Input text to summarize
        summary_type: Type of summarization
        max_length: Maximum length of summary
        
    Returns:
        Summarized text
    """
    summarizer = AdvancedSummarizer()
    result = summarizer.summarize_text(text, summary_type, max_length)
    return result["summary"]
