import os
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq
from langchain_community.tools import DuckDuckGoSearchRun
from langgraph.checkpoint.memory import MemorySaver
from langchain_gigachat.chat_models import GigaChat
from RAG.rag import *

memory = MemorySaver()

rag_executor = RAG(embeddings=
    HuggingFaceEmbeddings(
        model_name="cointegrated/LaBSE-en-ru",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    ), path=r'../RAG/vector_store')

def generate_answer(name=None, gender=None, age=None, weight=None, height=None, allergies=None, personal_file=None, message=""):
  llm = GigaChat(
    credentials="OThhMGI0MDctYzA5ZS00N2Y3LWIxYTYtOTM4NmZkZGU5YmY4Ojk5NjgwYzNiLTY4NjUtNDdhMi1hYzY2LTBlYTZmYzlkMWVkMg==",
    scope="GIGACHAT_API_PERS",
    model="GigaChat",
    verify_ssl_certs=False,
    streaming=True)

  prompt_template = f"""
  Ты - интеллектуальный помощник по здоровью. Твоя цель - помогать человеку разбираться со здоровьем, составлять планы диет, тренировок и давать различные рекоммендации.
  Профиль пользователя:
  Имя: {name}
  Возраст: {age}
  Пол: {gender}
  Вес: {weight}
  Рост: {height}
  Аллергии: {allergies}

  В характеристике должна содержаться информация по типу физической активности, болезней (в том числе хронических), качества сна, пищевых предпочтений и прочая полезная информация

  Характеристика: 

  Если ты считаешь информацию о пользователе недостаточной, не стесняйся задавать ему дополнительные вопросы для заполнения характеристики пользователя. Старайся не сильно менять характеристику за раз, а также сохранять актуальную информацию.

  Сообщение: {message}
  """

  @tool
  def search_tool(prompt: str) -> str:
    """Возвращает информацию с использованием DuckDuckGoSearchRun. Использовать для нахождения информации, которую не получилось достать другими методами"""
    search = DuckDuckGoSearchRun(prompt)

    return f"Результат поиска: {search}"

  @tool
  def rag_agent_tool(prompt: str) -> str:
    """Возвращает релевантные фрагменты информации по различным медицинским источникам. Для получения отрывка текста нужно ввести прямой запрос, на который нужен ответ"""
    print(f"Используем инструмент RAG. Промпт: {prompt}")
    list_of_files = ", ".join(os.listdir(r"../RAG/vector_store"))
    #print(list_of_files)
    llmprompt = f'''
    Твоя задача - выбрать ОДИН из файлов, указанных ниже и вывести текстом ТОЛЬКО ТОЧНОЕ НАЗВАНИЕ файла, наиболее подходящего по смыслу для вопроса, написанного ниже.
    Список файлов: {list_of_files}
    Текст запроса: {prompt}
    Выводом должно быть ТОЛЬКО НАЗВАНИЕ НАИБОЛЕЕ ПОДХОДЯЩЕГО ФАЙЛА ИЗ ВЫБОРКИ, ДАЖЕ ЕСЛИ ПОДХОДЯЩЕГО ФАЙЛА НЕТ
    '''

    llm = GigaChat(
    credentials="OThhMGI0MDctYzA5ZS00N2Y3LWIxYTYtOTM4NmZkZGU5YmY4Ojk5NjgwYzNiLTY4NjUtNDdhMi1hYzY2LTBlYTZmYzlkMWVkMg==",
    scope="GIGACHAT_API_PERS",
    model="GigaChat",
    verify_ssl_certs=False,
    streaming=True)

    filename = llm.invoke(llmprompt).content
    #print(filename)
    if filename not in os.listdir(r"../RAG/vector_store"):
      print(filename)
      print("Инфы нет")
      return "К сожалению, необходимая информация отсутствует."

    answer = "/n".join([el.page_content for el in rag_executor.retrieve(filename=filename, question=prompt, threshold=0.1)])
    print(answer)
    return answer or "Не удалось найти в тексте необходимую информацию"

  @tool
  def update_personal_file(updated_profile: str) -> str:
    """Обновляет характеристику пользователя. Важно: характеристика вводится с нуля, поэтому нужно вписывать ВСЮ актуальную информацию о пользователе которая имеется."""
    nonlocal personal_file
    personal_file = updated_profile
    return "Профиль обновлен!"

  tools  = [search_tool, rag_agent_tool, update_personal_file]
  agent = create_react_agent(
    llm,
    tools,
    checkpointer=memory
  )

  config = {"configurable": {"thread_id": "abc123"}}

  to_go = prompt_template.format(name=name, age=age, gender=gender, weight=weight, height=height, allergies=allergies, personal_file=personal_file, message=message)

  result = agent.invoke({
    "messages": [{"role": "user", "content": to_go}]
},
  config)
  #print(result)

  return name, gender, age, weight, height, allergies, personal_file, result['messages'][-1].content