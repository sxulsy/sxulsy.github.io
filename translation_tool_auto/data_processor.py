import os
import sqlite3
from readmdict import MDX
import random
from typing import List, Tuple, Optional

class DataProcessor:
    def __init__(self, mdx_file_path: str = "oxford.mdx", db_path: str = "terms.db"):
        self.mdx_file_path = mdx_file_path
        self.db_path = db_path
        self.conn = None
        self.cursor = None
    
    def connect_db(self):
        """连接到SQLite数据库"""
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
    
    def create_table(self):
        """创建术语表"""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS terms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word TEXT UNIQUE NOT NULL,
                definition TEXT NOT NULL
            )
        ''')
        self.conn.commit()
    
    def parse_mdx_file(self) -> List[Tuple[str, str]]:
        """解析MDX文件，提取词条和释义"""
        if not os.path.exists(self.mdx_file_path):
            print(f"MDX文件 {self.mdx_file_path} 不存在，生成模拟数据...")
            return self.generate_sample_data()
        
        print(f"正在解析MDX文件: {self.mdx_file_path}...")
        mdx = MDX(self.mdx_file_path)
        items = []
        
        for word, definition in mdx.items():
            # 解码数据
            word_str = word.decode('utf-8', errors='ignore')
            def_str = definition.decode('utf-8', errors='ignore')
            # 简单清理HTML标签
            def_str = self.clean_html(def_str)
            items.append((word_str, def_str))
        
        print(f"解析完成，共提取 {len(items)} 个词条")
        return items
    
    def clean_html(self, html_str: str) -> str:
        """简单清理HTML标签"""
        import re
        return re.sub(r'<[^>]+>', '', html_str)
    
    def generate_sample_data(self) -> List[Tuple[str, str]]:
        """生成模拟术语数据"""
        sample_terms = [
            ("人工智能", "Artificial Intelligence, 缩写为AI, 是指由人制造出来的机器所表现出来的智能"),
            ("机器学习", "Machine Learning, 是人工智能的一个分支, 指通过经验自动改进的计算机算法"),
            ("深度学习", "Deep Learning, 是机器学习的一个分支, 基于人工神经网络, 具有多层结构"),
            ("自然语言处理", "Natural Language Processing, 缩写为NLP, 是人工智能领域的一个分支, 研究人与计算机之间用自然语言进行有效通信的各种理论和方法"),
            ("计算机视觉", "Computer Vision, 是人工智能领域的一个分支, 使计算机能够理解和解释图像或视频数据"),
            ("大数据", "Big Data, 指规模巨大到无法用传统数据库工具处理的数据集合"),
            ("云计算", "Cloud Computing, 是一种基于互联网的计算方式, 通过这种方式, 共享的软硬件资源和信息可以按需提供给计算机和其他设备"),
            ("区块链", "Blockchain, 是一种分布式账本技术, 通过密码学方法确保数据的不可篡改和不可伪造"),
            ("物联网", "Internet of Things, 缩写为IoT, 指通过各种信息传感器、射频识别技术、全球定位系统、红外感应器、激光扫描器等各种装置与技术, 实时采集任何需要监控、连接、互动的物体或过程"),
            ("增强现实", "Augmented Reality, 缩写为AR, 是一种实时地计算摄影机影像的位置及角度并加上相应图像、视频、3D模型的技术"),
            ("虚拟现实", "Virtual Reality, 缩写为VR, 是一种可以创建和体验虚拟世界的计算机仿真系统, 它利用计算机生成一种模拟环境"),
            ("量子计算", "Quantum Computing, 是一种遵循量子力学规律调控量子信息单元进行计算的新型计算模式"),
            ("数据挖掘", "Data Mining, 是指从大量的数据中通过算法搜索隐藏于其中信息的过程"),
            ("算法", "Algorithm, 是解题方案的准确而完整的描述, 是一系列解决问题的清晰指令"),
            ("神经网络", "Neural Network, 是一种模仿动物神经网络行为特征, 进行分布式并行信息处理的算法数学模型"),
            ("模型", "Model, 在机器学习中, 是指通过训练数据学习到的参数和结构, 用于预测或分类新数据"),
            ("训练", "Training, 在机器学习中, 指通过提供输入数据和期望输出, 让模型学习如何进行预测或分类"),
            ("测试", "Testing, 在机器学习中, 指使用未用于训练的数据集评估模型的性能"),
            ("验证", "Validation, 在机器学习中, 指在训练过程中使用一部分数据评估模型的性能, 用于调整超参数"),
            ("准确率", "Accuracy, 是指模型预测正确的样本数占总样本数的比例")
        ]
        return sample_terms
    
    def insert_data(self, items: List[Tuple[str, str]]):
        """将数据插入到数据库中"""
        print(f"正在向数据库插入 {len(items)} 个词条...")
        
        # 批量插入，提高效率
        self.cursor.executemany(
            "INSERT OR IGNORE INTO terms (word, definition) VALUES (?, ?)",
            items
        )
        
        inserted = self.cursor.rowcount
        self.conn.commit()
        print(f"数据插入完成，成功插入 {inserted} 个词条")
    
    def close_db(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
    
    def process(self):
        """完整的数据处理流程"""
        self.connect_db()
        self.create_table()
        items = self.parse_mdx_file()
        self.insert_data(items)
        self.close_db()
        print("数据处理流程完成！")

if __name__ == "__main__":
    processor = DataProcessor()
    processor.process()