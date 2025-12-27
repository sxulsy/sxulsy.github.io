from retrieval_engine import RetrievalEngine

# 初始化检索引擎
engine = RetrievalEngine()
engine.load_model()

# 测试查询
test_query = "Artificial intelligence (AI) is a tool."
print(f"测试查询: {test_query}")

# 执行检索
results = engine.retrieve_top_k(test_query, k=5)

# 输出结果
print(f"Top-5检索结果 ({len(results)} 个匹配):")
for i, result in enumerate(results, 1):
    print(f"\n{i}. {result['term']} (相似度: {result['similarity']:.4f})")
    print(f"   释义: {result['definition'][:100]}...")
