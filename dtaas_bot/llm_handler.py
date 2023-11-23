from langchain.tools import WikipediaQueryRun
from langchain.utilities import WikipediaAPIWrapper
from langchain.chat_models import GigaChat
from langchain.chains import RetrievalQA, LLMChain
from langchain.schema import SystemMessage, HumanMessage, AIMessage, StrOutputParser
from langchain.prompts import HumanMessagePromptTemplate
from langchain.agents import AgentExecutor, initialize_agent, Tool, AgentType, LLMSingleActionAgent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema.runnable import RunnablePassthrough
from langchain.memory import ConversationBufferMemory


class Retrieve:
    def __init__(self, vs, prompt, sys_message):
        self.vs = vs
        self.prompt = prompt
        self.sys_message = sys_message

    def run(self, message):
        """Инструмент позволяет получить информацию о кейсах цифровой трансформации"""
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
        self._llm = GigaChat(temperature=1e-15, verify_ssl_certs=False, scope='GIGACHAT_API_CORP')
        self.prompt = prompt
        self.vs = vector_store
        self.sys_message = sys_message
        self.memory = ConversationBufferMemory(memory_key="chat_history")

    def call(self, message):
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

    def get_response(self, message, db, chat_id, relevant_docs_k=5):
        def condense_question(input: dict):
            if input.get("chat_history"):
                return condense_q_chain
            else:
                return input["input"]
        retrieval = Retrieve(self.vs, self.prompt, self.sys_message)
        wikipedia = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())
        tools = [
            Tool(
                name="Case data",
                func=retrieval.run,
                description="Полезно, когда необходимо узнать о кейсах цифровой трансформации. В качестве параметров передай, о каком кейсе ты хотел бы узнать, пиши кратко"
            ),
            Tool(
                name="Wiki search",
                func=wikipedia.run,
                description="Полезно, когда нужно что-то узнать в википелии. В качестве параметров передай то, что было бы понятно википедии"
            ),
            Tool(
                name="Default answer",
                func=self._llm,
                description="Полезно, когда пользователь просто хочет сказать привет или что-то малозначимое. В качестве параметров передай то, что хочет сказать пользователь"

            )
        ]
        from langchain.embeddings import HuggingFaceEmbeddings
        from langchain.schema import Document
        from langchain.vectorstores import FAISS

        chat_history_from_db = db.get_context(chat_id)
        chat_history = list()
        for index, element in enumerate(chat_history_from_db):
            chat_history.append(HumanMessage(content=element[0]))
            chat_history.append(AIMessage(content=element[1]))

        condense_q_system_prompt = """Тебе дана история чата и последний вопрос пользователя \
        который может отсылать к истории чата, сформулируй отдельный вопрос \
        который может быть понятен без истории чата. НЕ ОТВЕЧАЙ НА ВОПРОС, \
        ПРОСТО ПЕРЕФОРМУЛИРУЙ ЕГО"""

        condense_q_prompt = ChatPromptTemplate.from_messages(
            [
                ('system', condense_q_system_prompt),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{question}. ПЕРЕФОРМУЛИРУЙ ЭТОТ ВОПРОС ТАК, ЧТОБЫ ОН ЗВУЧАЛ КАК ПРОДОЛЖЕНИЕ ДИАЛОГА И БЫЛ ПОНЯТЕН БЕЗ КОНТЕКСТА. ОБЯЗАТЕЛЬНО СОХРАНИ СМЫСЛ ВОПРОСА")
            ]
        )
        condense_q_chain = condense_q_prompt | self._llm | StrOutputParser()

        docs = [
            Document(page_content=t.description, metadata={"index": i})
            for i, t in enumerate(tools)
        ]
        vector_store = FAISS.from_documents(docs, HuggingFaceEmbeddings())

        retriever = vector_store.as_retriever()

        def get_tools(query):
            docs = retriever.get_relevant_documents(query)
            return [tools[d.metadata["index"]] for d in docs]

        tools = get_tools(message)

        mrkl = initialize_agent(tools, self._llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True, handle_parsing_errors=True)
        mrkl_chain = (
            RunnablePassthrough.assign(input=condense_question)
            | mrkl
        )
        output = mrkl_chain.invoke({"question": message, "chat_history": chat_history})
        print(output)
        return output['output']
