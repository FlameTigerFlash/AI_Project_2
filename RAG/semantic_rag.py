from langchain_community.vectorstores import Chroma
from langchain_experimental.text_splitter import SemanticChunker
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader
import os

os.environ["GROQ_API_KEY"] = "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"

path = "dataset/sugar.txt"
loader = TextLoader(path, encoding='utf-8')
document = loader.load()

model_name = "cointegrated/LaBSE-en-ru"
embed_model = HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
)

semantic_chunker = SemanticChunker(embed_model, breakpoint_threshold_type="percentile", min_chunk_size=500)
semantic_chunks = semantic_chunker.create_documents([d.page_content for d in document])

semantic_chunk_vectorstore = FAISS.from_documents(semantic_chunks, embedding=embed_model)

semantic_chunk_retriever = semantic_chunk_vectorstore.as_retriever(search_kwargs={"k" : 3})
ans = semantic_chunk_retriever.invoke("Какие виды диабета существуют?")

for el in ans:
        print(el.page_content)
        print("\n-----" * 4)