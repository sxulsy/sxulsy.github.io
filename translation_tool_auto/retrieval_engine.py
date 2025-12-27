import sqlite3
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import re
from typing import List, Dict, Tuple

class RetrievalEngine:
    def __init__(self, db_path: str = "terms.db"):
        self.db_path = db_path
        self.vectorizer = None
        self.term_matrix = None
        self.terms = []
        self.term_definitions = {}
    
    def load_terms_from_db(self):
        """从数据库加载术语数据"""
        print("正在从数据库加载术语数据...")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT word, definition FROM terms")
        rows = cursor.fetchall()
        
        for word, definition in rows:
            self.terms.append(word)
            self.term_definitions[word] = definition
        
        conn.close()
        print(f"加载完成，共 {len(self.terms)} 个术语")
    
    def build_vectorizer(self):
        """构建TF-IDF向量器"""
        print("正在构建TF-IDF向量器...")
        # 使用TF-IDF模型，考虑英文单词和短语，使用单词级别的分析器
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 3),  # 考虑1-3个单词的短语
            analyzer='word',     # 单词级别的分析器
            lowercase=True,      # 转换为小写
            stop_words='english' # 移除英文停用词
        )
        self.term_matrix = self.vectorizer.fit_transform(self.terms)
        print(f"向量器构建完成，词汇表大小: {len(self.vectorizer.vocabulary_)}")
    
    def retrieve_top_k(self, query: str, k: int = 5) -> List[Dict[str, str]]:
        """基于余弦相似度检索Top-K相关术语"""
        if self.vectorizer is None or self.term_matrix is None:
            raise ValueError("检索引擎尚未初始化，请先调用load_terms_from_db和build_vectorizer方法")
        
        # 预处理查询文本
        processed_query = self.preprocess_query(query)
        
        # 对查询文本进行向量化
        query_vector = self.vectorizer.transform([processed_query])
        
        # 计算与所有术语的余弦相似度
        similarities = cosine_similarity(query_vector, self.term_matrix)[0]
        
        # 获取Top-K最相似的术语索引
        top_k_indices = np.argsort(similarities)[::-1][:k]
        
        # 构建检索结果，不进行相似度过滤，确保返回足够的结果
        results = []
        for idx in top_k_indices:
            term = self.terms[idx]
            similarity = similarities[idx]
            # 移除相似度过滤，返回所有Top-K结果
            results.append({
                "term": term,
                "definition": self.term_definitions[term],
                "similarity": float(similarity)
            })
        
        return results
    
    def preprocess_query(self, query: str) -> str:
        """预处理查询文本，提高术语匹配准确性"""
        # 移除括号内的内容（如AI）
        query = re.sub(r'\([^)]*\)', '', query)
        # 移除标点符号
        query = re.sub(r'[^a-zA-Z\s]', '', query)
        # 转换为小写
        query = query.lower()
        # 移除多余空格
        query = ' '.join(query.split())
        
        return query
    
    def initialize(self):
        """初始化检索引擎"""
        self.load_terms_from_db()
        self.build_vectorizer()
        print("检索引擎初始化完成！")
    
    def save_model(self, vectorizer_path: str = "vectorizer.pkl", matrix_path: str = "term_matrix.npz"):
        """保存向量器和向量矩阵到文件"""
        import pickle
        from scipy import sparse
        
        # 保存向量器
        with open(vectorizer_path, 'wb') as f:
            pickle.dump(self.vectorizer, f)
        
        # 保存稀疏矩阵
        sparse.save_npz(matrix_path, self.term_matrix)
        
        print(f"模型保存完成：\n- 向量器: {vectorizer_path}\n- 向量矩阵: {matrix_path}")
    
    def load_model(self, vectorizer_path: str = "vectorizer.pkl", matrix_path: str = "term_matrix.npz"):
        """从文件加载向量器和向量矩阵"""
        import pickle
        from scipy import sparse
        import os
        
        if not os.path.exists(vectorizer_path) or not os.path.exists(matrix_path):
            print("模型文件不存在，将重新构建...")
            self.initialize()
            self.save_model()
            return
        
        print("正在从文件加载模型...")
        
        # 加载向量器
        with open(vectorizer_path, 'rb') as f:
            self.vectorizer = pickle.load(f)
        
        # 加载向量矩阵
        self.term_matrix = sparse.load_npz(matrix_path)
        
        # 确保术语数据已加载
        if not self.terms:
            self.load_terms_from_db()
        
        print("模型加载完成！")

if __name__ == "__main__":
    # 测试检索引擎
    engine = RetrievalEngine()
    engine.initialize()
    
    # 测试检索功能
    test_query = "人工智能"
    results = engine.retrieve_top_k(test_query, k=3)
    
    print(f"\n测试查询: {test_query}")
    print("Top-3检索结果:")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['term']} (相似度: {result['similarity']:.4f})")
        print(f"   释义: {result['definition'][:100]}...")
    
    # 保存模型
    engine.save_model()