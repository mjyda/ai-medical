from pathlib import Path
import sys

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
_FRONTEND = _ROOT / "app" / "frontend"
if str(_FRONTEND) not in sys.path:
    sys.path.insert(0, str(_FRONTEND))

import base64

import graphviz as gv
import requests
import streamlit as st

from app.backend.repositories.kb_document_repository import KBDocumentRepository
from app.backend.services.kg_service import KGService, RELATION_LABELS
from app.config.config import KNOWLEDGE_BASE_CONFIG

API_BASE = KNOWLEDGE_BASE_CONFIG["api_base_url"].rstrip("/")

_PALETTE = [
    "#E57373", "#FFB74D", "#64B5F6", "#81C784", "#BA68C8", "#4DD0E1",
    "#FF8A65", "#AED581", "#7986CB", "#4FC3F7", "#FFF176", "#F06292",
    "#90A4AE", "#A1887F", "#9575CD", "#4DB6AC", "#FFD54F", "#E0E0E0",
]


def _get_type_color(entity_type: str) -> str:
    h = hash(entity_type) % len(_PALETTE)
    return _PALETTE[h]


def _get_rel_label(relation_type: str) -> str:
    return RELATION_LABELS.get(relation_type, relation_type)

STATUS_LABELS = {
    "uploaded": "待处理", "parsing": "解析中", "parsed": "已解析",
    "vectorizing": "向量化中", "vectorized": "已完成", "failed": "失败",
}


@st.cache_resource
def _get_kg_service() -> KGService:
    return KGService()


@st.cache_data(ttl=30, show_spinner=False)
def _get_graph_data():
    return _get_kg_service().get_graph_data()


@st.cache_data(ttl=10, show_spinner=False)
def _get_all_docs():
    repo = KBDocumentRepository()
    return repo.list_recent(500)


@st.cache_data(ttl=3600, show_spinner=False)
def _render_png(dot: str) -> bytes | None:
    try:
        return gv.Source(dot, format="png").pipe()
    except Exception:
        return None


def _escape_dot(s: str) -> str:
    return s.replace('"', '\\"').replace("\n", " ")


def _build_dot(entities: list[dict], relations: list[dict],
               selected_types: set[str] | None = None) -> str:
    entity_ids = {e["id"] for e in entities}
    if selected_types:
        entity_ids = {e["id"] for e in entities if e["entity_type"] in selected_types}
    filtered_entities = [e for e in entities if e["id"] in entity_ids]
    filtered_relations = [
        r for r in relations
        if r["source_id"] in entity_ids and r["target_id"] in entity_ids
    ]

    lines = [
        "digraph KG {",
        '  rankdir=LR;',
        '  graph [bgcolor=transparent, fontname="WenQuanYi Micro Hei", dpi=150];',
        '  node [shape=box, style="filled,rounded", fontname="WenQuanYi Micro Hei", fontsize=11, margin="0.15,0.1"];',
        '  edge [fontname="WenQuanYi Micro Hei", fontsize=9, color="#9e9e9e"];',
    ]
    for e in filtered_entities:
        color = _get_type_color(e["entity_type"])
        name = _escape_dot(e["name"])
        label = f"{name}\\n[{e['entity_type']}]"
        lines.append(f'  "{e["id"]}" [label="{label}", fillcolor="{color}", color="#555"];')
    for r in filtered_relations:
        rel_label = _get_rel_label(r["relation_type"])
        lines.append(f'  "{r["source_id"]}" -> "{r["target_id"]}" [label="{rel_label}"];')
    lines.append("}")
    return "\n".join(lines)


def _render_stats(entities: list[dict], relations: list[dict]):
    cols = st.columns(4)
    with cols[0]:
        st.metric("实体数", len(entities))
    with cols[1]:
        st.metric("关系数", len(relations))
    with cols[2]:
        type_counts = {}
        for e in entities:
            type_counts[e["entity_type"]] = type_counts.get(e["entity_type"], 0) + 1
        st.metric("实体类型", len(type_counts))
    with cols[3]:
        doc_ids = set()
        for e in entities:
            if e.get("doc_id"):
                doc_ids.add(e["doc_id"])
        st.metric("来源文档", len(doc_ids))


def _upload_documents(uploaded_files: list) -> int:
    if not uploaded_files:
        return 0
    files_payload = []
    for uf in uploaded_files:
        files_payload.append(
            ("files", (uf.name, uf.getvalue(), "application/octet-stream"))
        )
    try:
        r = requests.post(f"{API_BASE}/docs/upload", files=files_payload, timeout=120)
        if r.status_code == 413:
            st.error("文件过大（>100MB）")
            return 0
        elif r.status_code != 200:
            st.error(f"上传失败 {r.status_code}: {r.text}")
            return 0
        else:
            data = r.json()
            items = data.get("items", [])
            return len(items)
    except requests.RequestException as e:
        st.error(f"无法连接 API：{e}")
        return 0


# ── Main UI ──

st.title("知识图谱")

service = _get_kg_service()

# ── Section 1: 文档来源（可折叠） ──
with st.expander("文档来源 — 上传 & 选择文档构建图谱", expanded=False):
    st.subheader("上传新文档")
    uploaded = st.file_uploader(
        "上传 PDF / DOCX（可多选）",
        type=["pdf", "docx"],
        accept_multiple_files=True,
        key="kg_uploader",
    )
    if uploaded:
        if st.button("提交上传并解析", type="primary", key="kg_upload_btn"):
            count = _upload_documents(uploaded)
            if count > 0:
                st.success(f"已上传 {count} 个文件")
                st.info("上传后需等待解析和向量化完成，才可用于构建图谱。可在「任务中心」查看进度。")
                _get_all_docs.clear()

    st.divider()
    st.subheader("从文档库选择文档构建图谱")

    all_docs = _get_all_docs()
    if not all_docs:
        st.info("文档库为空，请先上传文档。")
    else:
        ready_docs = [d for d in all_docs if d["status"] in ("vectorized", "parsed")]
        other_docs = [d for d in all_docs if d["status"] not in ("vectorized", "parsed")]

        st.caption(f"共 {len(all_docs)} 个文档，其中 {len(ready_docs)} 个可用于构建图谱")

        if ready_docs:
            doc_options = {}
            for d in ready_docs:
                label = f"{d['filename']}  [{STATUS_LABELS.get(d['status'], d['status'])}]  ({str(d.get('created_at', ''))[:10]})"
                doc_options[label] = d["id"]

            selected_doc_labels = st.multiselect(
                "选择用于构建图谱的文档",
                options=list(doc_options.keys()),
                key="kg_doc_select",
            )
            selected_doc_ids = [doc_options[l] for l in selected_doc_labels]

            c1, c2, c3 = st.columns([1.5, 1.5, 2])
            with c1:
                if st.button("从选中文档构建图谱", type="primary", use_container_width=True,
                             disabled=len(selected_doc_ids) == 0):
                    with st.spinner(f"正在从 {len(selected_doc_ids)} 个文档中提取实体和关系…"):
                        result = service.build_from_documents(selected_doc_ids)
                        if result['entity_count'] == 0:
                            st.warning(
                                f"未提取到任何实体。请确认：\n"
                                f"1. 文档已成功解析（状态为「已解析」或「已完成」）\n"
                                f"2. 文档内容包含可识别的实体信息\n"
                                f"3. LLM 服务正常运行"
                            )
                        else:
                            st.success(
                                f"图谱构建完成：{result['entity_count']} 个实体，"
                                f"{result['relation_count']} 条关系，涉及 {result['doc_count']} 个文档"
                            )
                        _get_graph_data.clear()
                        st.rerun()
            with c2:
                if st.button("从全部可用文档构建", use_container_width=True):
                    all_ready_ids = [d["id"] for d in ready_docs]
                    with st.spinner(f"正在从 {len(all_ready_ids)} 个文档中提取实体和关系…"):
                        result = service.build_from_documents(all_ready_ids)
                        if result['entity_count'] == 0:
                            st.warning(
                                f"未提取到任何实体。请确认：\n"
                                f"1. 文档已成功解析（状态为「已解析」或「已完成」）\n"
                                f"2. 文档内容包含可识别的实体信息\n"
                                f"3. LLM 服务正常运行"
                            )
                        else:
                            st.success(
                                f"图谱构建完成：{result['entity_count']} 个实体，"
                                f"{result['relation_count']} 条关系，涉及 {result['doc_count']} 个文档"
                            )
                        _get_graph_data.clear()
                        st.rerun()

        if other_docs:
            with st.expander(f"不可用文档（{len(other_docs)} 个 — 需完成解析和向量化）", expanded=False):
                for d in other_docs:
                    s = STATUS_LABELS.get(d["status"], d["status"])
                    st.caption(f"{d['filename']} — {s}")

st.divider()

# ── Section 2: 图谱可视化（始终可见） ──

graph = _get_graph_data()
entities = graph.get("entities", [])
relations = graph.get("relations", [])

c1, c2, c3 = st.columns([1.5, 1, 4])
with c1:
    if st.button("清空图谱", use_container_width=True):
        service.clear_graph()
        _get_graph_data.clear()
        st.rerun()
with c2:
    if st.button("刷新显示", use_container_width=True):
        _get_graph_data.clear()
        st.rerun()

if not entities:
    st.info('图谱为空。请展开上方的「文档来源」，上传文档或从文档库选择文档，然后点击构建图谱。')
    st.stop()

_render_stats(entities, relations)
st.divider()

# ── Graph + sidebar filters ──
left, right = st.columns([1, 3])

with left:
    st.subheader("筛选", divider=False)
    entity_types_in_graph = sorted({e["entity_type"] for e in entities})
    selected_types = st.multiselect(
        "实体类型",
        options=entity_types_in_graph,
        default=entity_types_in_graph,
        format_func=lambda t: f"{t}",
        key="kg_type_filter",
    )
    if not selected_types:
        selected_types = entity_types_in_graph

    st.divider()
    st.caption(f"共 {len(entities)} 个实体，{len(relations)} 条关系")

    with st.expander("实体列表", expanded=False):
        search = st.text_input("搜索实体", key="entity_search")
        filtered = entities
        if search:
            filtered = [e for e in entities if search.lower() in e["name"].lower()]
        for e in filtered[:50]:
            color = _get_type_color(e["entity_type"])
            st.markdown(f":{color}[▪] {e['name']}  `{e['entity_type']}`")

with right:
    dot = _build_dot(entities, relations, set(selected_types))
    png_bytes = _render_png(dot)

    if png_bytes:
        b64 = base64.b64encode(png_bytes).decode()

        # 下载按钮
        st.download_button(
            "⬇ 下载图谱 (PNG)",
            data=png_bytes,
            file_name="knowledge_graph.png",
            mime="image/png",
            key="kg_download_png",
            use_container_width=True,
        )

        # 交互式查看器 — 鼠标滚轮缩放 / 拖拽平移 / 双击重置，完全客户端实时
        viewer_html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
  body{{margin:0;overflow:hidden;background:#fafafa;font-family:Helvetica,Arial,sans-serif;}}
  #container{{width:100vw;height:100vh;overflow:hidden;position:relative;}}
  #img{{position:absolute;top:0;left:0;transform-origin:0 0;cursor:grab;user-select:none;-webkit-user-drag:none;}}
  #img:active{{cursor:grabbing;}}
  #hint{{position:fixed;bottom:16px;left:50%;transform:translateX(-50%);background:rgba(0,0,0,0.65);color:#fff;padding:6px 14px;border-radius:14px;font-size:11px;pointer-events:none;transition:opacity .6s;}}
  #zoom-badge{{position:fixed;bottom:16px;right:16px;background:rgba(0,0,0,0.65);color:#fff;padding:4px 10px;border-radius:10px;font-size:11px;}}
</style></head><body>
<div id="container"><img id="img" src="data:image/png;base64,{b64}" draggable="false"></div>
<div id="hint">🖱 滚轮缩放 · 拖拽平移 · 双击重置</div>
<div id="zoom-badge">100%</div>
<script>
(function(){{
  var c=document.getElementById('container'),img=document.getElementById('img'),
      hint=document.getElementById('hint'),badge=document.getElementById('zoom-badge'),
      scale=1,tx=0,ty=0,panning=false,sx,sy;
  function apply(){{
    img.style.transform='translate('+tx+'px,'+ty+'px) scale('+scale+')';
    badge.textContent=Math.round(scale*100)+'%';
  }}
  function fit(){{
    var w=c.clientWidth,h=c.clientHeight,iw=img.naturalWidth,ih=img.naturalHeight;
    if(iw&&ih&&(iw>w||ih>h)){{scale=Math.min(w/iw,h/ih)*0.9;tx=(w-iw*scale)/2;ty=(h-ih*scale)/2;}}
  }}
  c.addEventListener('wheel',function(e){{
    e.preventDefault();
    var rect=c.getBoundingClientRect(),mx=e.clientX-rect.left,my=e.clientY-rect.top;
    var old=scale,ns=old*(e.deltaY<0?1.12:0.9);
    ns=Math.min(8,Math.max(0.15,ns));
    tx=mx-(mx-tx)*(ns/old);ty=my-(my-ty)*(ns/old);scale=ns;
    apply();hint.style.opacity='0';
  }},{{passive:false}});
  c.addEventListener('mousedown',function(e){{panning=true;sx=e.clientX-tx;sy=e.clientY-ty;e.preventDefault();}});
  document.addEventListener('mousemove',function(e){{if(!panning)return;tx=e.clientX-sx;ty=e.clientY-sy;apply();hint.style.opacity='0';}});
  document.addEventListener('mouseup',function(){{panning=false;}});
  c.addEventListener('dblclick',function(){{scale=1;tx=0;ty=0;fit();apply();hint.style.opacity='1';}});
  c.addEventListener('touchstart',function(e){{if(e.touches.length===1){{panning=true;sx=e.touches[0].clientX-tx;sy=e.touches[0].clientY-ty;}}}});
  c.addEventListener('touchmove',function(e){{if(!panning)return;tx=e.touches[0].clientX-sx;ty=e.touches[0].clientY-sy;apply();}});
  c.addEventListener('touchend',function(){{panning=false;}});
  fit();apply();
  setTimeout(function(){{hint.style.opacity='0';}},4000);
}})();
</script></body></html>"""
        st.components.v1.html(viewer_html, height=550, scrolling=False)

    else:
        try:
            st.graphviz_chart(dot, use_container_width=True)
        except Exception as exc:
            with st.expander("Graphviz 源码（渲染失败）", expanded=True):
                st.code(dot, language="dot")

    st.divider()
    st.subheader("实体与关系详情", divider=False)
    detail_tab1, detail_tab2 = st.tabs(["实体", "关系"])
    with detail_tab1:
        if entities:
            entity_options = {f"{e['name']} [{e['entity_type']}]": e for e in entities}
            selected = st.selectbox(
                "选择实体查看详情", list(entity_options.keys()), key="detail_entity"
            )
            if selected:
                e = entity_options[selected]
                st.markdown(f"**名称：** {e['name']}")
                st.markdown(f"**类型：** {e['entity_type']}")
                if e.get("doc_id"):
                    st.caption(f"来源文档：{e['doc_id']}")
                related_rels = [
                    r for r in relations
                    if r["source_id"] == e["id"] or r["target_id"] == e["id"]
                ]
                if related_rels:
                    st.markdown("**关联关系：**")
                    for r in related_rels:
                        direction = "→"
                        if r["target_id"] == e["id"]:
                            direction = "←"
                        rel_label = _get_rel_label(r["relation_type"])
                        st.caption(
                            f"{r['source_name']} {direction} {rel_label} {direction if direction == '←' else ''} {r['target_name']}"
                        )
    with detail_tab2:
        if relations:
            rel_options = {}
            for r in relations:
                rel_label = _get_rel_label(r["relation_type"])
                key = f"{r['source_name']} → {rel_label} → {r['target_name']}"
                rel_options[key] = r
            selected_rel = st.selectbox(
                "选择关系查看详情", list(rel_options.keys()), key="detail_rel"
            )
            if selected_rel:
                r = rel_options[selected_rel]
                st.markdown(f"**源实体：** {r['source_name']} ({r['source_type']})")
                st.markdown(f"**目标实体：** {r['target_name']} ({r['target_type']})")
                rel_label = _get_rel_label(r["relation_type"])
                st.markdown(f"**关系：** {rel_label} (`{r['relation_type']}`)")
                if r.get("doc_id"):
                    st.caption(f"来源文档：{r['doc_id']}")
