# -*- coding: utf-8 -*-
"""
模式向量化模块：将依存句法分析得到的模式加载并向量化存储
"""
import os
import csv
import json
from typing import List, Dict, Any

try:
    from langchain_openai import OpenAIEmbeddings
    from langchain_community.vectorstores import Chroma
    from langchain_core.documents import Document
except ImportError:
    print("⚠️  警告：LangChain相关包未安装，请先运行: pip install -r requirements.txt")
    raise


class PatternVectorizer:
    """将模式数据向量化并存储到向量数据库"""
    
    def __init__(
        self,
        csv_path: str,
        json_path: str,
        persist_directory: str = "./chroma_db",
        collection_name: str = "phm_patterns",
        embedding_model: str = "text-embedding-3-small"
    ):
        """
        初始化向量化器
        
        Args:
            csv_path: CSV模式文件路径
            json_path: JSON schema文件路径
            persist_directory: ChromaDB持久化目录
            collection_name: 集合名称
            embedding_model: OpenAI embedding模型名称
        """
        self.csv_path = csv_path
        self.json_path = json_path
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        
        # 初始化 embedding 模型
        self.embeddings = OpenAIEmbeddings(
            model=embedding_model,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        self.vectorstore = None
        
    def load_csv_patterns(self) -> List[Dict[str, Any]]:
        """从CSV文件加载模式数据"""
        patterns = []
        
        with open(self.csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # 解析句法路径字符串
                syntactic_paths = self._parse_syntactic_paths(
                    row['句法实现路径 (Syntactic Realizations)']
                )
                
                pattern = {
                    'semantic_pattern': row['语义模式 (Semantic Pattern)'],
                    'total_frequency': int(row['总频次 (Total Freq)']),
                    'syntactic_paths': syntactic_paths
                }
                patterns.append(pattern)
        
        print(f"✅ 从CSV加载了 {len(patterns)} 条模式")
        return patterns
    
    def _parse_syntactic_paths(self, path_str: str) -> List[Dict[str, Any]]:
        """解析句法路径字符串"""
        paths = []
        
        # 简单解析，按照 "- 句法路径:" 分割
        parts = path_str.split('- 句法路径:')
        
        for part in parts[1:]:  # 跳过第一个空元素
            if not part.strip():
                continue
                
            # 提取频次和样例
            lines = part.strip().split('\n')
            if not lines:
                continue
            
            path_line = lines[0].strip()
            
            # 提取频次 (频次: X, 样例: ...)
            frequency = 1
            example_head = ""
            example_tail = ""
            
            if '频次:' in path_line:
                try:
                    freq_part = path_line.split('频次:')[1].split(',')[0].strip()
                    frequency = int(freq_part)
                except:
                    pass
            
            if '样例:' in path_line:
                try:
                    example_part = path_line.split('样例:')[1].strip()
                    # 格式: [头实体] → [尾实体])
                    if '[' in example_part and ']' in example_part:
                        parts = example_part.split('→')
                        if len(parts) == 2:
                            example_head = parts[0].strip().strip('[]')
                            example_tail = parts[1].strip().strip('[]').rstrip(')')
                except:
                    pass
            
            paths.append({
                'path': path_line,
                'frequency': frequency,
                'example_head': example_head,
                'example_tail': example_tail
            })
        
        return paths
    
    def load_json_schema(self) -> Dict[str, Any]:
        """从JSON文件加载schema定义"""
        with open(self.json_path, 'r', encoding='utf-8') as f:
            schema = json.load(f)
        
        print(f"✅ 加载了JSON schema，包含 {len(schema.get('entity_types', {}))} 种实体类型")
        return schema
    
    def create_documents(
        self,
        csv_patterns: List[Dict[str, Any]],
        json_schema: Dict[str, Any]
    ) -> List[Document]:
        """创建LangChain Document对象"""
        documents = []
        
        # 1. 从CSV模式创建文档
        for pattern in csv_patterns:
            semantic_pattern = pattern['semantic_pattern']
            total_freq = pattern['total_frequency']
            
            # 为每个句法路径创建一个文档
            for syn_path in pattern['syntactic_paths']:
                # 构造文档内容（用于向量化的文本）
                content = f"""语义模式: {semantic_pattern}
示例: {syn_path['example_head']} → {syn_path['example_tail']}
频次: {syn_path['frequency']}
句法路径: {syn_path['path'][:200]}"""  # 截断过长路径
                
                # 元数据（不参与向量化，但检索时返回）
                metadata = {
                    'type': 'csv_pattern',
                    'semantic_pattern': semantic_pattern,
                    'total_frequency': total_freq,
                    'example_head': syn_path['example_head'],
                    'example_tail': syn_path['example_tail'],
                    'frequency': syn_path['frequency'],
                    'syntactic_path': syn_path['path'][:500]  # 限制长度
                }
                
                documents.append(Document(
                    page_content=content,
                    metadata=metadata
                ))
        
        print(f"✅ 从CSV创建了 {len(documents)} 个文档")
        
        # 2. 从JSON的high_confidence_patterns创建文档
        if 'high_confidence_patterns' in json_schema:
            for pattern in json_schema['high_confidence_patterns']:
                for example in pattern.get('examples', []):
                    content = f"""语义模式: {pattern['head_type']} → {pattern['relation']} → {pattern['tail_type']}
示例: {example['head']} → {example['tail']}
置信度: {pattern['confidence_score']}
说明: {pattern['description']}"""
                    
                    metadata = {
                        'type': 'json_pattern',
                        'pattern_id': pattern['id'],
                        'semantic_template': pattern['semantic_template'],
                        'head_type': pattern['head_type'],
                        'relation': pattern['relation'],
                        'tail_type': pattern['tail_type'],
                        'confidence_score': pattern['confidence_score'],
                        'example_head': example['head'],
                        'example_tail': example['tail'],
                        'description': pattern['description']
                    }
                    
                    documents.append(Document(
                        page_content=content,
                        metadata=metadata
                    ))
        
        print(f"✅ 从JSON创建了 {len(documents) - len(csv_patterns)} 个高置信度模式文档")
        print(f"📊 总计创建 {len(documents)} 个文档用于向量化")
        
        return documents
    
    def build_vectorstore(self, documents: List[Document]) -> Chroma:
        """构建向量数据库"""
        print("🔄 开始向量化和构建数据库...")
        
        # 创建ChromaDB向量存储
        vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            collection_name=self.collection_name,
            persist_directory=self.persist_directory
        )
        
        print(f"✅ 向量数据库构建完成，已持久化到: {self.persist_directory}")
        
        self.vectorstore = vectorstore
        return vectorstore
    
    def run(self) -> Chroma:
        """执行完整的向量化流程"""
        print("\n" + "="*60)
        print("🚀 开始构建PHM模式向量数据库")
        print("="*60 + "\n")
        
        # 1. 加载数据
        csv_patterns = self.load_csv_patterns()
        json_schema = self.load_json_schema()
        
        # 2. 创建文档
        documents = self.create_documents(csv_patterns, json_schema)
        
        # 3. 构建向量库
        vectorstore = self.build_vectorstore(documents)
        
        print("\n" + "="*60)
        print("✅ 向量数据库构建完成！")
        print("="*60 + "\n")
        
        return vectorstore


def main():
    """主函数：构建向量数据库"""
    # 路径配置
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    ROOT_DIR = os.path.dirname(os.path.dirname(SCRIPT_DIR))
    
    CSV_PATH = os.path.join(ROOT_DIR, "依存路径提取结果", 
                            "semantic_syntactic_patterns_report_2025-10-14_172830.csv")
    JSON_PATH = os.path.join(ROOT_DIR, "schema文件", "phm_semantic_patterns.json")
    PERSIST_DIR = os.path.join(ROOT_DIR, "chroma_db")
    
    # 检查文件存在
    if not os.path.exists(CSV_PATH):
        raise FileNotFoundError(f"CSV文件不存在: {CSV_PATH}")
    if not os.path.exists(JSON_PATH):
        raise FileNotFoundError(f"JSON文件不存在: {JSON_PATH}")
    
    # 检查API Key
    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("请设置环境变量 OPENAI_API_KEY")
    
    # 创建向量化器并运行
    vectorizer = PatternVectorizer(
        csv_path=CSV_PATH,
        json_path=JSON_PATH,
        persist_directory=PERSIST_DIR,
        collection_name="phm_patterns"
    )
    
    vectorstore = vectorizer.run()
    
    # 测试检索
    print("\n" + "="*60)
    print("🧪 测试检索功能")
    print("="*60 + "\n")
    
    test_query = "航空发动机剩余寿命预测方法"
    results = vectorstore.similarity_search(test_query, k=3)
    
    print(f"查询: {test_query}")
    print(f"\n检索到 {len(results)} 个相关模式:\n")
    
    for i, doc in enumerate(results, 1):
        print(f"【结果 {i}】")
        print(f"内容: {doc.page_content[:200]}...")
        print(f"元数据: {doc.metadata.get('semantic_pattern', 'N/A')}")
        print(f"示例: {doc.metadata.get('example_head', '')} → {doc.metadata.get('example_tail', '')}")
        print("-" * 60)


if __name__ == "__main__":
    main()
