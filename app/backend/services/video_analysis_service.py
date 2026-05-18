"""视频 AI 分析：摘要生成、标签提取、相关文档检索。"""
from __future__ import annotations

import json
import re

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from app.config.config import API_CONFIG, SYSTEM_CONFIG
from app.rag.optimized_rag_service import OptimizedRAGService


class VideoAnalysisService:
    def __init__(self):
        self.llm = ChatOpenAI(
            api_key=API_CONFIG["local_model"]["api_key"],
            model=API_CONFIG["local_model"]["model_name"],
            base_url=API_CONFIG["local_model"]["base_url"],
            temperature=SYSTEM_CONFIG["chat"]["temperature"],
        )
        try:
            self.rag_service = OptimizedRAGService()
        except Exception:
            self.rag_service = None

    def generate_summary(self, video_title: str) -> str:
        messages = [
            SystemMessage(content=(
                "你是一个专业的医疗内容分析师。请根据视频标题，生成一段简洁的中文摘要（100-200字），"
                "概括该视频可能涵盖的医疗主题和关键知识点。直接返回摘要文本，不要前缀或后缀说明。"
            )),
            HumanMessage(content=f"视频标题：{video_title}"),
        ]
        response = self.llm.invoke(messages)
        return response.content.strip()

    def generate_tags(self, video_title: str) -> list[str]:
        messages = [
            SystemMessage(content=(
                "你是一个医疗内容标签专家。请根据视频标题，生成3-5个相关的分类标签。"
                "必须以JSON数组格式返回，例如：[\"标签1\",\"标签2\",\"标签3\"]。"
                "只返回JSON数组，不要包含任何其他文本、解释或markdown代码块标记。"
            )),
            HumanMessage(content=f"视频标题：{video_title}"),
        ]
        response = self.llm.invoke(messages)
        raw = response.content.strip()
        # 清理可能的 markdown 代码块包装
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
        try:
            tags = json.loads(raw)
            if isinstance(tags, list) and all(isinstance(t, str) for t in tags):
                return tags
        except (json.JSONDecodeError, TypeError):
            pass
        # 回退：按行或逗号拆分
        fallback = [t.strip().strip("，,。\"'") for t in re.split(r"[,，\n]+", raw) if t.strip()]
        return [t for t in fallback if len(t) <= 20][:5]

    def find_related_documents(self, video_title: str, k: int = 5) -> list[dict]:
        if self.rag_service is None or self.rag_service.vector_store is None:
            return []
        try:
            pairs = self.rag_service.vector_store.similarity_search_with_relevance_scores(
                video_title, k=k
            )
        except Exception:
            return []
        results = []
        for doc, score in pairs:
            results.append({
                "doc_id": doc.metadata.get("doc_id"),
                "snippet": (doc.page_content or "")[:400],
                "score": float(score),
            })
        return results

    def run_full_analysis(self, video_title: str) -> tuple[str, list[str], list[dict]]:
        summary = self.generate_summary(video_title)
        tags = self.generate_tags(video_title)
        related_docs = self.find_related_documents(video_title)
        return summary, tags, related_docs
