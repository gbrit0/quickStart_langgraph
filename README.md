# Quickstart LangGraph

Seguindo o quickstart oficial da [documentação LangGraph](https://langchain-ai.github.io/langgraph/concepts/why-langgraph/) para aprendizado dos conceitos básicos da ferramenta.

Para funcionamento correto da aplicação, o arquivo [.env.example](/.env.example) deve ser renomeado para **.env** e o valor ser alterado para uma chave de api real que pode ser obtida em https://aistudio.google.com/app/api-keys.

* [basic_chatbot.py](/basic_chatbot.py) contém o básico da implementação de um chatbot com LangGraph e o modelo gemini 2.0.

* [chatbot_tools.py](/chatbot_tools.py) replica a implementação de [basic_chatbot.py](/basic_chatbot.py) porém adicionando o recurso de pesquisa web por meio da API Tavily. Para implementação desta etapa é necessário criar uma [chave API de acesso a Tavily Search Engine.](https://python.langchain.com/docs/integrations/tools/tavily_search/?_gl=1*1abzeov*_gcl_au*ODEzMDk2NjA0LjE3NjAzNjIwODU.*_ga*MTQ0NDIzMTEyOC4xNzYwMzYxMDU4*_ga_47WX3HKKY2*czE3NjAzNzgyMzkkbzMkZzAkdDE3NjAzNzgzODgkajYwJGwwJGgw)

