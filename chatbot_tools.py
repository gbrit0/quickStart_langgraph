# Para lidar com perguntas que o chatbot não consegue responder a partir dos dados de treinamento, 
# é possível integrar uma toole (ferramenta) de busca na web.

# Pré-requisito:
#   Chave API de acesso a Tavily Search Engine. https://python.langchain.com/docs/integrations/tools/tavily_search/?_gl=1*1abzeov*_gcl_au*ODEzMDk2NjA0LjE3NjAzNjIwODU.*_ga*MTQ0NDIzMTEyOC4xNzYwMzYxMDU4*_ga_47WX3HKKY2*czE3NjAzNzgyMzkkbzMkZzAkdDE3NjAzNzgzODgkajYwJGwwJGgw

import os
from dotenv import load_dotenv

load_dotenv()

os.environ.get("TAVILY_API_KEY")

# Definir a tool de pesquisa na web:
from langchain_tavily import TavilySearch

tool = TavilySearch(max_results=2)
tools = [tool]

# Selecionar o LLM
os.environ.get("GOOGLE_API_KEY")

from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash"
)

from typing import Annotated

from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

class State(TypedDict):
    messages: Annotated[list, add_messages]

graph_builder = StateGraph(State)

# bind_tools permite o LLM saber o formato correto do JSON caso ele queira usar o motor de busca Tavily

llm_with_tools = llm.bind_tools(tools)

def chatbot(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

graph_builder.add_node("chatbot", chatbot)

# Criar uma função que roda as tools
# Adicionar as tools a um novo nó chamado BasicToolNode que checa a mensagem mais recente no state
# e chama as tools se a mensagem contém tool_calls.

import json

from langchain_core.messages import ToolMessage

class BasicToolNode:
    """Um nó que executa as tools requisitadas na última AIMessage."""

    def __init__(self, tools: list) -> None:
        self.tools_by_name = {tool.name: tool for tool in tools}

    def __call__(self, inputs: dict):
        if messages := inputs.get("messages", []):# := é o operador morsa. nesse caso realiza a tribuição de inputs.get(... a messages e depois verifica se messages existe
            message = messages[-1]
        else:
            raise ValueError("Mensagens não encontradas no input")
        outputs = []
        for tool_call in message.tool_calls:
            tool_result = self.tools_by_name[tool_call["name"]].invoke(
                tool_call["args"]
            )
            outputs.append(
                ToolMessage(
                    content=json.dumps(tool_result),
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"]
                )
            )
        return {"messages": outputs}
    
tool_node = BasicToolNode(tools=[tool])
graph_builder.add_node("tools", tool_node)

# Arestas condicionais:
# arestas controlam o fluxo de um nó para o próximo. Arestas condicionais iniciam de um nó único
# e geralmente contém sentenças 'if' para navegar para diferentes nós a depender do estado atual do grafo.

# Definir uma função que checa se há tool_calls no output do chatbot.

def route_tools(
        state: State
):
    """Use na aresta condicional para navegar até o ToolNode se a última mensagem possuir chamadas a funções. Caso contrário, navege para o fim"""
    if isinstance(state, list):
        ai_message = state[-1]
    elif messages := state.get("messages", []):
        ai_message = messages[-1]
    else:
        raise ValueError(f"Não foram encontradas mensagens no input state da ferramenta de arestas: {state}")
    
    if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
        return "tools"
    
    return END

graph_builder.add_conditional_edges(
    "chatbot",
    route_tools,
    # O dicionário a seguir permite dizer ao grafo para interpretar as saídas condicionas como um nó específico.
    {"tools": "tools", END: END}
)

graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge(START, "chatbot")
graph = graph_builder.compile()

def stream_graph_updates(user_input: str):
    for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}):
        for value in event.values():
            print("Assistant:", value["messages"][-1].content)

while True:
    try:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break

        stream_graph_updates(user_input)
    except:
        # fallback if input() is not available
        user_input = "What do you know about LangGraph?"
        print("User: " + user_input)
        stream_graph_updates(user_input)
        break