from typing import Annotated

from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

# Início pela criação de um StateGraph
# Um objeto StateGraph define a estrutura do chatbot como uma "máquina de estados"

# Adicionaremos "nós" para representar a llm e as funções que o chatbot pode chamas
# e "arestas" para especificar como o bot deve transitar entre as funções

class State(TypedDict):
    # Mensagens são do tipo 'list'. a Função 'add_messages' na anotação
    # define como a chave de estado deve ser atualizada
    # (nesse caso, acrescenta mensagens à lista ao invés de sobrescrever)
    messages: Annotated[list, add_messages]

graph_builder = StateGraph(State)

# O grafo agora consegue lidar com duas tarefas principais:
# 1. Cada nó pode receber o State atual como uma entrada e emite um state atualizado
# 2. Atualizações nas mensagens serão adicionadas à lista existente ao invés de sobrescrever

# Adicionando um nó
# Nós representam unidades de trabalho e são tipicamente funções comuns de Python

# Primeiro selecionamos um modelo de linguagem
# `pip install -u "langchain[google-genai]"`

import os
from dotenv import load_dotenv

load_dotenv()

os.environ.get("GOOGLE_API_KEY")

from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.7
)

def chatbot(state: State) -> State:
    """Incorporando o modelo de chat como um nó simples."""
    return {"messages": [llm.invoke(state["messages"])]}

# Adicionar o nó ao grafo:
# O primeiro argumento é o nome único do nó
# O segundo argumento é a função ou objeto que será chamado sempre que o nó for usado
graph_builder.add_node("chatbot", chatbot)

# ponto de entrada
graph_builder.add_edge(START, "chatbot") # diz ao grafo onde iniciar a cada execução

# ponto de saída
graph_builder.add_edge("chatbot", END) # diz ao grafo para encerrar após executar o nó do chatbot

# Compilar o grafo
graph = graph_builder.compile()

# from Ipython.display import Image, display

# try:
#     display(Image(graph.get_graph().draw_mermaid_png()))
# except Exception as e:
#     print(e)

# Executar o chatbot
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
        # se o input() não estiver disponível
        user_input = "O que você sabe sobre o LangGraph?"
        print("User: " + user_input)
        stream_graph_updates(user_input)
        break