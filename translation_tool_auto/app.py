import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from translation_service import TranslationService
import os
from dotenv import load_dotenv
import sqlite3
import numpy as np
import re

# 加载环境变量
load_dotenv()

# 设置页面配置
st.set_page_config(
    page_title="术语检索增强翻译工具",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "terms.db")

# 定义全局的术语数据和向量器
@st.cache_resource
def load_terms_data():
    """加载术语数据并缓存"""

    print("=== DB DEBUG START ===")
    print("DB_PATH =", DB_PATH)
    print("Exists:", os.path.exists(DB_PATH))
    print("Size:", os.path.getsize(DB_PATH))

      # 以只读方式打开数据库，确保路径错误时不自动创建空库
    conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    cursor = conn.cursor()

    # 检查表是否存在（防止空数据库）
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [t[0] for t in cursor.fetchall()]
    if "terms" not in tables:
        raise RuntimeError(f"'terms' table not found in database at {DB_PATH}")

    # 执行查询
    cursor.execute("SELECT word, definition FROM terms")
    rows = cursor.fetchall()
    conn.close()

    # 拆分成两个列表返回
    terms = [r[0] for r in rows]
    definitions = [r[1] for r in rows]
    return terms, definitions

@st.cache_resource
def build_vectorizer(terms):
    """构建向量器并缓存"""
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 3),
        analyzer='word',
        lowercase=True,
        stop_words='english'
    )
    term_matrix = vectorizer.fit_transform(terms)
    return vectorizer, term_matrix

# 预处理查询
@st.cache_data
def preprocess_query(query):
    """预处理查询文本"""
    query = re.sub(r'\([^)]*\)', '', query)
    query = re.sub(r'[^a-zA-Z\s]', '', query)
    query = query.lower()
    return ' '.join(query.split())

# 检索函数
def retrieve_top_k(query, k=5):
    """基于余弦相似度检索Top-K相关术语"""
    # 加载缓存的术语数据
    terms, definitions = load_terms_data()
    
    # 预处理查询
    processed_query = preprocess_query(query)
    
    # 构建并缓存向量器
    vectorizer, term_matrix = build_vectorizer(terms)
    
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

# 初始化应用状态
if "terms_loaded" not in st.session_state:
    st.session_state.terms_loaded = False

# 创建侧边栏
st.sidebar.header("设置")

# API密钥设置
api_key = st.sidebar.text_input(
    "DeepSeek API密钥",
    type="password",
    placeholder="请输入您的DeepSeek API密钥",
    value=os.getenv("DEEPSEEK_API_KEY", "")
)

# Top-K参数设置
k_value = st.sidebar.slider(
    "术语检索数量 (Top-K)",
    min_value=1,
    max_value=20,
    value=5,
    step=1
)

# 主标题
st.title("🔍 术语检索增强翻译工具")

# 创建两列布局
col1, col2 = st.columns(2)

with col1:
    st.header("输入")
    # 文本输入区
    input_text = st.text_area(
        "待翻译文本",
        placeholder="请输入要翻译的文本...",
        height=200
    )
    
    # 翻译按钮
    translate_button = st.button("翻译", use_container_width=True, type="primary")

with col2:
    st.header("翻译结果")
    # 翻译结果展示区
    translation_result = st.empty()

# 添加测试术语检索的功能
st.header("🔍 术语检索测试")
test_input = st.text_area(
    "输入文本进行术语检索测试",
    placeholder="例如：Artificial intelligence (AI) is a tool.",
    height=100
)
test_button = st.button("测试检索", use_container_width=True)

# 测试术语检索处理逻辑
if test_button and test_input:
    with st.spinner("正在检索术语..."):
        try:
            # 检索相关术语
            related_terms = retrieve_top_k(test_input, k=k_value)
            
            # 直接显示检索结果，不使用占位符
            if related_terms:
                st.success(f"找到 {len(related_terms)} 个相关术语")
                for i, term in enumerate(related_terms, 1):
                    with st.expander(f"{i}. {term['term']} (相似度: {term['similarity']:.4f})"):
                        st.write(term['definition'][:200] + "..." if len(term['definition']) > 200 else term['definition'])
            else:
                st.info("未找到相关术语")
        except Exception as e:
            st.error(f"检索过程中出现错误: {str(e)}")
            st.exception(e)

# 术语检索结果展示区
st.header("相关术语检索结果")

# 翻译处理逻辑
if translate_button and input_text:
    # 验证API密钥
    if not api_key:
        st.error("请在侧边栏输入DeepSeek API密钥")
    else:
        # 显示加载状态
        with st.spinner("正在翻译..."):
            try:
                # 1. 检索相关术语
                related_terms = retrieve_top_k(input_text, k=k_value)
                
                # 2. 执行增强翻译
                translator = TranslationService(api_key=api_key)
                translated_text = translator.translate(input_text, related_terms)
                
                # 3. 显示翻译结果
                with col2:
                    translation_result.markdown(f"**翻译结果：**\n\n{translated_text}")
                
                # 4. 直接显示术语检索结果，不使用占位符
                if related_terms:
                    st.success(f"找到 {len(related_terms)} 个相关术语")
                    for i, term in enumerate(related_terms, 1):
                        with st.expander(f"{i}. {term['term']} (相似度: {term['similarity']:.4f})"):
                            st.write(term['definition'][:200] + "..." if len(term['definition']) > 200 else term['definition'])
                else:
                    st.info("未找到相关术语")
            except Exception as e:
                st.error(f"翻译过程中出现错误: {str(e)}")
                st.exception(e)

# 应用说明
st.sidebar.markdown("---")
st.sidebar.header("关于")
st.sidebar.info(
    "这是一个基于术语检索增强的翻译工具，利用牛津词典术语库和DeepSeek大模型实现精准翻译。\n\n"+
    "功能特点：\n"+
    "- 基于词袋模型的术语检索\n"+
    "- 余弦相似度Top-K匹配\n"+
    "- 增强型翻译Prompt\n"+
    "- DeepSeek API集成\n"+
    "- 直观易用的Web界面\n"
)

# 页脚信息
st.markdown("---")
st.markdown("© 2025 术语检索增强翻译工具 | 基于DeepSeek API和Oxford词典")
