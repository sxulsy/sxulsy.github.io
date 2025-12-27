import streamlit as st
import sqlite3
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import re

# 设置页面配置
st.set_page_config(
    page_title="简化版术语检索工具",
    page_icon="🔍",
    layout="wide"
)

# 简化的检索函数
def simple_retrieve(query, k=5):
    # 连接数据库
    conn = sqlite3.connect('terms.db')
    cursor = conn.cursor()
    
    # 加载术语数据
    cursor.execute("SELECT word, definition FROM terms")
    rows = cursor.fetchall()
    
    terms = [word for word, _ in rows]
    definitions = {word: defi for word, defi in rows}
    
    # 关闭数据库连接
    conn.close()
    
    # 预处理查询
    def preprocess(q):
        q = re.sub(r'\([^)]*\)', '', q)
        q = re.sub(r'[^a-zA-Z\s]', '', q)
        q = q.lower()
        return ' '.join(q.split())
    
    processed_query = preprocess(query)
    
    # 构建TF-IDF向量器
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 3),
        analyzer='word',
        lowercase=True,
        stop_words='english'
    )
    
    # 向量化术语
    term_matrix = vectorizer.fit_transform(terms)
    
    # 向量化查询
    query_vector = vectorizer.transform([processed_query])
    
    # 计算余弦相似度
    similarities = cosine_similarity(query_vector, term_matrix)[0]
    
    # 获取Top-K结果
    top_k_indices = np.argsort(similarities)[::-1][:k]
    
    # 构建结果
    results = []
    for idx in top_k_indices:
        term = terms[idx]
        sim = similarities[idx]
        results.append({
            "term": term,
            "similarity": float(sim),
            "definition": definitions[term]
        })
    
    return results

# 主应用
st.title("🔍 简化版术语检索工具")

# 输入区域
input_text = st.text_area(
    "输入文本进行术语检索",
    placeholder="例如：Artificial intelligence (AI) is a tool.",
    height=150
)

# 参数设置
k_value = st.slider("术语检索数量 (Top-K)", 1, 20, 5)

# 检索按钮
retrieve_button = st.button("检索术语", use_container_width=True, type="primary")

# 结果展示
if retrieve_button and input_text:
    with st.spinner("正在检索术语..."):
        try:
            # 执行检索
            results = simple_retrieve(input_text, k=k_value)
            
            # 显示结果
            st.success(f"找到 {len(results)} 个相关术语")
            for i, result in enumerate(results, 1):
                with st.expander(f"{i}. {result['term']} (相似度: {result['similarity']:.4f})"):
                    st.write(result['definition'][:200] + "..." if len(result['definition']) > 200 else result['definition'])
        except Exception as e:
            st.error(f"检索过程中出现错误: {str(e)}")
            st.exception(e)
