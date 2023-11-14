from langchain.chat_models.gigachat import GigaChat
from langchain.chains import RetrievalQA
from langchain.schema import SystemMessage, HumanMessage
from langchain.prompts import HumanMessagePromptTemplate, ChatPromptTemplate
from langchain.agents import Tool

from langchain_experimental.autonomous_agents import AutoGPT



class Retrieve:
    def __init__(self, vs, prompt, sys_message):
        self.vs = vs
        self.prompt = prompt
        self.sys_message = sys_message

    def run(self, message):
        chat_template = ChatPromptTemplate.from_messages(
            [
                SystemMessage(
                    content=(
                        self.sys_message
                    )
                ),
                HumanMessagePromptTemplate.from_template(self.prompt),
            ]
        )
        qa_chain = RetrievalQA.from_chain_type(
            llm=GigaChat(temperature=1e-15, verify_ssl_certs=False, scope='GIGACHAT_API_CORP'),
            chain_type='stuff',
            retriever=self.vs.as_retriever(search_kwargs={"k": 3}),
            chain_type_kwargs={"prompt": chat_template},
            return_source_documents=False
        )
        result = qa_chain({"query": message})
        response = result["result"]
        return response


class Giga:
    def __init__(self, prompt, vector_store, sys_message):
        self._llm = GigaChat(verbose=True, temperature=1e-15, verify_ssl_certs=False, scope='GIGACHAT_API_CORP', timeout=300)
        self.prompt = prompt
        self.vs = vector_store
        self.sys_message = sys_message

    def call(self, message):
        print(self.prompt)
        messages = [
            SystemMessage(
                content=self.prompt
            ),
            HumanMessage(
                content=message
            ),
        ]
        response = self._llm(messages).content
        return response

    def get_response(self, message):
        retrieval = Retrieve(self.vs, self.prompt, self.sys_message)
        from langchain.vectorstores import FAISS
        import faiss
        from langchain.docstore import InMemoryDocstore
        from langchain.embeddings import OpenAIEmbeddings
        embeddings_model = OpenAIEmbeddings()
        embedding_size = 1536
        index = faiss.IndexFlatL2(embedding_size)
        vectorstore = FAISS(embeddings_model.embed_query, index, InMemoryDocstore({}), {})
        tools = [
            Tool.from_function(
                func=retrieval.run,
                name="Retrive",
                description="""Команда поиска в базе данных: используется, когда тебе нужно узнать информацию про цифровую трансформацию. Передай текст поискового запроса в аргумент \"arg name\". 
Не ищи ответы на комплексные и сложные вопросы - ищи только простые вопросы."""
                # coroutine= ... <- you can specify an async method if desired as well
            ),
            Tool.from_function(
                func=self.call,
                name="answer",
                description="""Команда используется, когда пользователь не спрашивает ничего конкретного. Передай ТЕКСТ ЗАПРОСА в аргумент \"arg name\". 
Не ищи ответы на комплексные и сложные вопросы - ищи только простые вопросы."""
                # coroutine= ... <- you can specify an async method if desired as well
            )
        ]
        agent = AutoGPT.from_llm_and_tools(
            ai_name="Гигачат",
            ai_role="Ассистент",
            tools=tools,
            llm=self._llm,
            memory=vectorstore.as_retriever()
        )
        # Отладка модели
        agent.chain.verbose = True
        print(message)
        response = agent.run([message])
        return response
