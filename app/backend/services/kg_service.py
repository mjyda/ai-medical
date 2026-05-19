"""知识图谱构建服务：使用 LLM 从文档中提取实体与关系（领域无关）。"""
from __future__ import annotations

import json
import re

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from app.backend.repositories.kb_document_repository import KBDocumentRepository
from app.backend.repositories.kg_repository import KGRepository
from app.config.config import API_CONFIG, SYSTEM_CONFIG

# 仅作为历史兼容保留，实际类型由 LLM 动态决定
ENTITY_TYPES: list[str] = []
RELATION_TYPES: list[str] = []
RELATION_LABELS: dict[str, str] = {}

SYSTEM_PROMPT = """你是一个知识图谱构建助手。你的任务是从文本中提取关键实体及其语义关系。

## 实体提取规则
1. 识别文本中的关键概念、术语、人名、地名、技术名词、产品名、机构名、时间、事件等
2. 为每个实体确定一个合适的类型（根据实体在文本中的实际含义，用中文简短命名，如：编程语言、框架、公司、人物、疾病、药物、概念、技术、模型等）
3. 实体名称要精炼准确，使用文本中出现的原始表述
4. 每个实体的 type 是描述其本质的简短分类词

## 关系提取规则
1. 识别实体之间有意义的语义关联
2. 关系类型用简洁的中文短语描述（如：开发者、提出者、属于、包含、用于、依赖、治疗、导致、发布等）
3. source 和 target 必须是 entities 中出现的实体名称
4. 关系的方向要有意义：source → target 的语义方向要合理

## 输出格式
严格只返回 JSON：
{"entities": [{"name": "实体名", "type": "类型"}], "relations": [{"source": "源实体名", "target": "目标实体名", "type": "关系"}]}"""


class KGService:
    def __init__(self):
        self.llm = ChatOpenAI(
            api_key=API_CONFIG["local_model"]["api_key"],
            model=API_CONFIG["local_model"]["model_name"],
            base_url=API_CONFIG["local_model"]["base_url"],
            temperature=0.3,
        )
        self.repo = KGRepository()
        self.doc_repo = KBDocumentRepository()
        self.repo.ensure_table()

    def _extract_from_text(self, text: str) -> tuple[list[dict], list[dict]]:
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=f"从以下文本中提取实体和关系，直接返回 JSON：\n\n{text}"),
        ]
        response = self.llm.invoke(messages)
        raw = response.content.strip()
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
        try:
            data = json.loads(raw)
            entities = data.get("entities", []) if isinstance(data, dict) else []
            relations = data.get("relations", []) if isinstance(data, dict) else []
        except (json.JSONDecodeError, TypeError):
            print(f"[KG] LLM 返回非 JSON，原始响应前300字符: {raw[:300]}")
            return [], []
        valid_entities = []
        for e in entities:
            if isinstance(e, dict) and "name" in e:
                etype = (e.get("type") or e.get("entity_type") or "").strip()
                ename = str(e.get("name", "")).strip()
                if ename and etype:
                    valid_entities.append({"name": ename, "type": etype})
        valid_relations = []
        entity_names = {e["name"] for e in valid_entities}
        for r in relations:
            if isinstance(r, dict) and "source" in r and "target" in r:
                src = str(r["source"]).strip()
                tgt = str(r["target"]).strip()
                rtype = (r.get("type") or r.get("relation_type") or "").strip()
                if rtype and src in entity_names and tgt in entity_names and src != tgt:
                    valid_relations.append({"source": src, "target": tgt, "type": rtype})
        if valid_entities:
            print(f"[KG] 提取到 {len(valid_entities)} 个实体, {len(valid_relations)} 条关系")
        else:
            print(f"[KG] 未提取到有效实体, LLM返回JSON: {json.dumps(data, ensure_ascii=False)[:300]}")
        return valid_entities, valid_relations

    def build_from_documents(self, doc_ids: list[str] | None = None,
                             progress_callback=None) -> dict:
        if doc_ids is None:
            docs = self.doc_repo.list_recent(500)
            doc_ids = [d["id"] for d in docs if d["status"] in ("vectorized", "parsed")]
        if not doc_ids:
            return {"entity_count": 0, "relation_count": 0, "doc_count": 0}

        self.repo.clear_all()
        entity_map: dict[tuple[str, str], str] = {}
        total_entities = 0
        total_relations = 0
        processed = 0

        for doc_id in doc_ids:
            row = self.doc_repo.get_by_id(doc_id)
            if not row:
                print(f"[KG] 文档 {doc_id} 未找到")
                continue
            text = (row.get("parsed_text") or "")[:12000]
            if not text.strip():
                print(f"[KG] 文档 {doc_id} ({row.get('filename')}) 无 parsed_text，状态={row.get('status')}")
                continue

            chunks = [text[i:i + 2000] for i in range(0, len(text), 2000)]
            for chunk in chunks:
                entities, relations = self._extract_from_text(chunk)
                for e in entities:
                    key = (e["name"], e["type"])
                    if key not in entity_map:
                        eid = self.repo.insert_entity(e["name"], e["type"], doc_id)
                        if eid:
                            entity_map[key] = eid
                            total_entities += 1
                for r in relations:
                    src_key = (r["source"], self._find_entity_type(r["source"], entities))
                    tgt_key = (r["target"], self._find_entity_type(r["target"], entities))
                    src_id = entity_map.get(src_key)
                    tgt_id = entity_map.get(tgt_key)
                    if src_id and tgt_id:
                        self.repo.insert_relation(src_id, tgt_id, r["type"], doc_id)
                        total_relations += 1

            processed += 1
            if progress_callback:
                progress_callback(processed, len(doc_ids))

        print(f"[KG] 构建完成: {total_entities} 实体, {total_relations} 关系, {processed} 文档")
        return {"entity_count": total_entities, "relation_count": total_relations, "doc_count": processed}

    @staticmethod
    def _find_entity_type(name: str, entities: list[dict]) -> str:
        for e in entities:
            if e["name"] == name:
                return e["type"]
        return "其他"

    def get_graph_data(self) -> dict:
        return {
            "entities": self.repo.get_all_entities(),
            "relations": self.repo.get_all_relations(),
            "entity_count": self.repo.get_entity_count(),
            "relation_count": self.repo.get_relation_count(),
        }

    def clear_graph(self) -> None:
        self.repo.clear_all()
