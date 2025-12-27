import sqlite3
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import re

# 简化的检索函数
def simple_retrieve(query, k=5):
    # 连接数据库
    conn = sqlite3.connect('terms.db')
    cursor = conn.cursor()
    
    # 加载术语数据
    cursor.execute("SELECT word, definition FROM terms LIMIT 10000")  # 只加载前10000条数据，提高测试速度
    rows = cursor.fetchall()
    
    terms = [word for word, _ in rows]
    definitions = {word: defi for word, defi in rows}
    
    # 关闭数据库连接
    conn.close()
    
    print(f"加载了 {len(terms)} 个术语")
    
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
    print(f"词汇表大小: {len(vectorizer.vocabulary_)}")
    
    # 向量化查询
    query_vector = vectorizer.transform([processed_query])
    
    # 计算余弦相似度
    similarities = cosine_similarity(query_vector, term_matrix)[0]
    
    # 获取Top-K结果
    top_k_indices = np.argsort(similarities)[::-1][:k]
    
    # 打印结果
    results = []
    for idx in top_k_indices:
        term = terms[idx]
        sim = similarities[idx]
        results.append((term, sim, definitions[term]))
    
    return results

# 测试
test_query = "Artificial intelligence (AI) is a tool."
results = simple_retrieve(test_query, k=5)

print(f"\n测试查询: {test_query}")
print("Top-5检索结果:")
for i, (term, sim, defi) in enumerate(results, 1):
    print(f"\n{i}. {term} (相似度: {sim:.4f})")
    print(f"   释义: {defi[:100]}...")
