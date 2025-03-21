import os
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq
from langchain_community.tools import DuckDuckGoSearchRun
from langgraph.checkpoint.memory import MemorySaver
from langchain_gigachat.chat_models import GigaChat

memory = MemorySaver()


def generate_answer(name=None, gender=None, age=None, weight=None, height=None, allergies=None, personal_file=None, message=""):
  llm = GigaChat(credentials="OThhMGI0MDctYzA5ZS00N2Y3LWIxYTYtOTM4NmZkZGU5YmY4Ojk5NjgwYzNiLTY4NjUtNDdhMi1hYzY2LTBlYTZmYzlkMWVkMg==",
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

  Характеристика: {personal_file}

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

    answer = 'Сервис сейчас недоступен'
    return answer

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