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
from langchain_huggingface import HuggingFaceEmbeddings
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


def preprocess_text(text:str):
    while "\n\n\n\n" in text:
        text = text.replace("\n\n\n\n", "\n\n")

    chunks = text.split("\n\n")
    arr = [0 for i in range(len(chunks))]
    for i in range(len(chunks) - 1):
        if chunks[i][0].isdigit() and chunks[i+1][0].isdigit():
            arr[i] = 1
            continue
        max_pref = 0
        for j in range(min(len(chunks[i]), len(chunks[i+1]))):
            if chunks[i][j] != chunks[i+1][j]:
                break
            max_pref += 1
        if max_pref >= 3:
            arr[i] = 1

    new_chunks = []
    s = ""
    for i in range(len(chunks)):
        if arr[i] == 1:
            s += "\n" * (len(s) > 0) + chunks[i]
        else:
            s += "\n" * (len(s) > 0) + chunks[i]
            new_chunks.append(s)
            s = ""
        if i == len(chunks) - 1 and arr[i] == 1:
            new_chunks.append(s)

    chunks = new_chunks.copy()
    new_chunks.clear()
    arr = [0 for i in range(len(chunks))]

    for i in range(len(chunks) - 1):
        if chunks[i][0].isdigit():
            continue
        if (len(chunks[i]) < 60 and len(chunks[i+1]) >= 2 * len(chunks[i])) or (len(chunks[i]) < 100 and len(chunks[i+1]) >= 4 * len(chunks[i])):
            arr[i] = 1

    s = ""
    for i in range(len(chunks)):
        if arr[i] == 1:
            s += "\n" * (len(s) > 0) + chunks[i]
        else:
            s += "\n" * (len(s) > 0) + chunks[i]
            new_chunks.append(s)
            s = ""
        if i == len(chunks) - 1 and arr[i] == 1:
            new_chunks.append(s)
    return "\n\n".join(new_chunks)


class RAG:
    def __init__(self, embeddings: HuggingFaceEmbeddings, path:str):
        self.embeddings = embeddings
        self.path = path
        self.location = dict()

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=1024,
            chunk_overlap=256,
            separators=["\n\n", "(?<=\\. )", "\n", " "],
            length_function=len,
            is_separator_regex=False,
        )

    def vectorize_one(self, addr="dataset", file="burns.txt", preprocess:bool = False):
        full_path = addr+"/"+file
        if not os.path.exists(full_path):
            print(f"Файла не существует: {full_path}")
        if not file.endswith('.txt') or file.endswith('.TXT'):
            print(f"Неподобающий формат файла: {file}")

        text_loader = TextLoader(full_path, encoding='utf-8')
        documents = text_loader.load()
        text_contents = [doc.page_content for doc in documents]

        if preprocess:
            for (i, el) in enumerate(text_contents):
                try:
                    text_contents[i] = preprocess_text(el)
                except Exception as ex:
                    print(ex.__context__)

        split_documents = self.splitter.create_documents(text_contents)
        vector_store = FAISS.from_documents(
            split_documents, self.embeddings
        )

        new_name = filter_name(file[:-4].lower())
        if not os.path.exists(f"{self.path}/{new_name}"):
            os.mkdir(f"{self.path}/{new_name}")

        vector_store.save_local(f"{self.path}/{new_name}")
        self.location[new_name] = f"/{self.path}/{new_name}"

    def vectorize_all(self, addr="dataset", preprocess:bool = False):
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

                    if preprocess:
                        for (i, el) in enumerate(text_contents):
                            try:
                                text_contents[i] = preprocess_text(el)
                            except Exception as ex:
                                print(ex.__context__)

                    split_documents = self.splitter.create_documents(text_contents)
                    vector_store = FAISS.from_documents(
                        split_documents, self.embeddings
                    )
                    if not os.path.exists(f"{self.path}/{new_name}"):
                        os.mkdir(f"{self.path}/{new_name}")

                    vector_store.save_local(f"{self.path}/{new_name}")
                    self.location[new_name] = f"/{self.path}/{new_name}"

    def retrieve(self, filename, question:str, k:int = 1, threshold:float = 0):
        if not os.path.exists(f"{self.path}/{filename}"):
            print(f"Необходимый файл отсутствует: {self.path}/{filename}")
            return

        vector_store = FAISS.load_local(
            folder_path=f"{self.path}/{filename}",
            embeddings=self.embeddings,
            allow_dangerous_deserialization=True
        )
        retriever = vector_store.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={"k": k, "score_threshold": threshold}
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
    #rag.vectorize_all(addr='dataset', preprocess=True)

    for el in rag.retrieve(filename='sugar', question='Что следует включить в рацион согласно DASH-диете?', k=3, threshold=0.2):
        print(el.page_content)
        print('-----\n-----')