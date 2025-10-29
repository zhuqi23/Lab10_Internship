from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain.schema import Document
from langchain.prompts import PromptTemplate
import json
import os
from typing import List, Dict, Any


class InternshipRAGSystem:
    __instance = None

    @classmethod
    def get_instance(cls):
        if cls.__instance is None:
            print("正在初始化实习岗位RAG系统...")
            cls.__instance = cls()
        return cls.__instance

    def __init__(self):
        self.document_path = "document/深圳技术大学招聘详情.json"
        self.vector_db_path = "chroma_db_sztu"
        self.embeddings_model = "nomic-embed-text"
        self.llm_model = "qwen2.5:7b"
        
        self.documents = []
        self.raw_data = []
        
        self._load_documents()
        self._initialize_components()
        
    def _load_documents(self):
        """加载和预处理文档数据"""
        try:
            with open(self.document_path, "r", encoding="utf-8") as f:
                self.raw_data = json.load(f)
            
            print(f"成功加载 {len(self.raw_data)} 条实习岗位记录")
            
            # 创建优化的文档格式用于检索
            for i, item in enumerate(self.raw_data):
                if isinstance(item, dict):
                    # 创建结构化的检索内容
                    content_parts = []
                    
                    # 关键字段重点强调
                    # key_fields = ['company', 'position', 'location', 'salary', 
                    #             'work_type', 'duration', 'industry']
                    key_fields = ['公司名称', '招聘岗位', '薪资', '招聘人数', '工作地点', '详情页链接']
                    
                    for field in key_fields:
                        if field in item and item[field]:
                            content_parts.append(f"{field}: {item[field]}")
                    
                    # 技能和要求字段
                    # if 'skills' in item and item['skills']:
                    #     skills_text = ", ".join(item['skills']) if isinstance(item['skills'], list) else str(item['skills'])
                    #     content_parts.append(f"skills: {skills_text}")
                    
                    # if 'requirements' in item and item['requirements']:
                    #     content_parts.append(f"requirements: {item['requirements']}")
                    
                    # if 'description' in item and item['description']:
                    #     content_parts.append(f"description: {item['description']}")

                    if '岗位要求' in item and item['岗位要求']:
                        content_parts.append(f"岗位要求: {item['岗位要求']}")
                    
                    content = " | ".join(content_parts)
                    
                    self.documents.append(Document(
                        page_content=content,
                        metadata={
                            "source": self.document_path,
                            "row": i,
                            "公司名称": item.get('公司名称', ''),
                            "招聘岗位": item.get('招聘岗位', ''),
                            "薪资": item.get('薪资', ''),
                            "招聘人数": item.get('招聘人数', ''),
                            "工作地点": item.get('工作地点', ''),
                        }
                    ))
            
            print(f"预处理完成，生成 {len(self.documents)} 个检索文档")
            
        except Exception as e:
            print(f"文档加载失败: {e}")
            raise

    def _initialize_components(self):
        """初始化向量数据库和LLM组件"""
        # 初始化嵌入模型
        self.embeddings = OllamaEmbeddings(model=self.embeddings_model)
        
        # 初始化向量数据库
        if os.path.exists(self.vector_db_path):
            print("加载已存在的向量数据库...")
            self.vector_db = Chroma(
                persist_directory=self.vector_db_path,
                embedding_function=self.embeddings
            )
        else:
            print("创建新的向量数据库...")
            self.vector_db = Chroma.from_documents(
                documents=self.documents,
                embedding=self.embeddings,
                persist_directory=self.vector_db_path
            )
        
        # 配置检索器
        self.retriever = self.vector_db.as_retriever(
            search_type="similarity",
            search_kwargs={
                "k": 15,  # 检索最相关的10个文档
                # "score_threshold": 0.4,  # 相似度阈值
            }
        )
        
        # 初始化LLM
        self.llm = OllamaLLM(model=self.llm_model)
        
        print("RAG系统初始化完成！")

    def search_positions(self, query: str) -> List[Document]:
        """搜索相关实习岗位"""
        print(f"搜索查询: {query}")
        
        relevant_docs = self.retriever.invoke(query)
        
        print(f"找到 {len(relevant_docs)} 个相关岗位")
        for i, doc in enumerate(relevant_docs):
            print(f"相关岗位 {i+1}: {doc.page_content[:100]}...")
        
        return relevant_docs

    def get_detailed_response(self, query: str) -> str:
        """获取详细的岗位信息回复"""
        relevant_positions = self.search_positions(query)
        
        if not relevant_positions:
            return "抱歉，没有找到符合您要求的实习岗位。请尝试调整搜索条件。"
        
        # 构建详细的提示词
        prompt_template = """
根据用户查询: "{user_query}"

我找到了以下相关的实习岗位信息：

{positions_info}

请根据以上信息：
1. 筛选出真正符合用户要求的岗位
2. 为每个合适的岗位提供完整详细信息
3. 确保信息准确，不编造不存在的内容
4. 如果某些岗位信息不完整，请忽略
5. 确保岗位多样性，避免重复

请用清晰的中文回答，并首先提供一个汇总表格，然后对重点岗位进行详细说明。

要求输出格式：
## 符合要求的实习岗位汇总

[这里放置表格]

## 岗位详情
[对重点岗位的详细描述]
"""
        # 准备岗位信息
        positions_info = "\n\n".join([
            f"岗位 {i+1}:\n{doc.page_content}" 
            for i, doc in enumerate(relevant_positions)
        ])
        
        prompt = prompt_template.format(
            user_query=query,
            positions_info=positions_info
        )
        
        print("生成详细回复...")
        response = self.llm.invoke(prompt)
        print(response)
        return response


rag = InternshipRAGSystem.get_instance()
