from retrieval_engine import RetrievalEngine

# 初始化检索引擎并重新构建模型
engine = RetrievalEngine()
engine.initialize()

# 测试检索功能
test_query = "Artificial intelligence (AI) is a tool."
results = engine.retrieve_top_k(test_query, k=5)

print(f"\n测试查询: {test_query}")
print("Top-5检索结果:")
for i, result in enumerate(results, 1):
    print(f"\n{i}. {result['term']} (相似度: {result['similarity']:.4f})")
    print(f"   释义: {result['definition'][:100]}...")

# 保存新模型
engine.save_model()
