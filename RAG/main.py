import csv
import os
import random
from pathlib import Path

from langchain_core.prompts import PromptTemplate
from typing_extensions import List, TypedDict
from langchain.chat_models import init_chat_model
from langchain_core.documents import Document
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

os.environ["GROQ_API_KEY"] = "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"

def filter_name(s:str):
  ans = ""
  repl = {'ё': 'е', 'й': 'и'}
  for el in s:
    if el.isalpha() or el == " ":
      if el in repl:
        el = repl[el]
      ans += el
  return ans

class RAG:
    def __init__(self, embeddings: HuggingFaceEmbeddings, path:str):
        self.embeddings = embeddings
        self.path = path
        self.location = dict()

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=1024,
            chunk_overlap=256,
            separators=["\n\n"],
            length_function=len,
            is_separator_regex=False,
        )


    def vectorize_all(self, addr="dataset"):
        for root, dirs, files in os.walk(addr):
            for file in files:
                if file.endswith('.txt') or file.endswith('.TXT'):
                    file_path = Path(root) / file
                    new_name = filter_name(file[:-4].lower())
                    if new_name in self.location:
                        continue

                    text_loader = TextLoader(file_path, encoding='utf-8')
                    documents = text_loader.load()
                    text_contents = [doc.page_content for doc in documents]
                    split_documents = self.splitter.create_documents(text_contents)
                    vector_store = FAISS.from_documents(
                        split_documents, self.embeddings
                    )
                    if not os.path.exists(f"{self.path}/{new_name}"):
                        os.mkdir(f"{self.path}/{new_name}")

                    vector_store.save_local(f"{self.path}/{new_name}")
                    self.location[new_name] = f"/{self.path}/{new_name}"

    def retrieve(self, filename, question:str, k:int = 1, threshold:int = 0):
        if not os.path.exists(f"{self.path}/{filename}"):
            print(f"Необходимый файл отсутствует: {self.path}/{filename}")
            return

        vector_store = FAISS.load_local(
            folder_path=f"{self.path}/{filename}",
            embeddings=self.embeddings,
            allow_dangerous_deserialization=True
        )
        retriever = vector_store.as_retriever(
            search_type="mmr",
            k=k,
            score_threshold=threshold,
            #lambda_mult=0.6
        )
        return retriever.invoke(
            question
        )


if __name__ == "__main__":
    model_name = "cointegrated/LaBSE-en-ru"
    embeddings = HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )
    rag = RAG(embeddings=embeddings, path='vector_store')
    #rag.vectorize_all(addr='dataset')

    print(rag.retrieve(filename='burns', question='Что делать при ожоге?', k=3))