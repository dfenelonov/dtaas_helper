from langchain.tools import WikipediaQueryRun
from langchain.utilities import WikipediaAPIWrapper
from langchain.chat_models import GigaChat

from langchain.chains import RetrievalQA, LLMChain
from langchain.schema import SystemMessage, HumanMessage, AIMessage, StrOutputParser
from langchain.prompts import HumanMessagePromptTemplate
from langchain.agents import AgentExecutor, initialize_agent, Tool, AgentType, LLMSingleActionAgent, tool
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema.runnable import RunnablePassthrough
from langchain.memory import ConversationBufferMemory


class Retrieve:
    def __init__(self, vs, prompt, sys_message):
        self.vs = vs
        self.prompt = prompt
        self.sys_message = sys_message

    @tool
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

        wiki = Tool(
                name="Wiki search",
                func=wikipedia.run,
                description="Полезно, когда нужно что-то узнать в википелии. В качестве параметров передай то, что было бы понятно википедии"
        )

        def_ans = Tool(
                name="Default answer",
                func=self._llm.call_as_llm,
                description="Полезно, когда пользователь просто хочет сказать привет или что-то малозначимое. В качестве параметров передай то, что хочет сказать пользователь"
        )

        from langchain.embeddings import HuggingFaceEmbeddings
        from langchain.schema import Document
        from langchain.vectorstores import FAISS

        tools = [retrieval.run, wiki, def_ans]

        from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """Ты помощник клиентского менеджера по цифровой трансформации.""",
                ),
                ("user", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )

        from langchain.tools.render import format_tool_to_openai_function

        llm_with_tools = self._llm.bind(functions=[format_tool_to_openai_function(t) for t in tools])

        from langchain.agents.format_scratchpad import format_to_openai_functions
        from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser

        agent = (
                {
                    "input": lambda x: x["question"],
                    "agent_scratchpad": lambda x: format_to_openai_functions(
                        x["intermediate_steps"]
                    ),
                }
                | prompt
                | llm_with_tools
                | OpenAIFunctionsAgentOutputParser()
        )
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

        chat_history_from_db = db.get_context(chat_id)
        chat_history = list()
        for index, element in enumerate(chat_history_from_db):
            chat_history.append(HumanMessage(content=element[0]))
            chat_history.append(AIMessage(content=element[1]))

        condense_q_system_prompt = """Тебе дана история чата и последний вопрос пользователя \
                который может отсылать к истории чата, сформулируй отдельный вопрос \
                который может быть понятен без истории чата. НЕ отвечай на вопрос, \
                просто переформулируй его, если нужно, а если не нужно, то не надо переформулировать"""
        condense_q_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", condense_q_system_prompt),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{question}"),
            ]
        )
        condense_q_chain = condense_q_prompt | self._llm | StrOutputParser()

        qa_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self.prompt),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{question}"),
            ]
        )

        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)

        rag_chain = (
                RunnablePassthrough.assign(
                    context=condense_question | self.vs.as_retriever(search_kwargs={"k": 3}) | format_docs)
                | agent_executor
                | qa_prompt
                | self._llm
        )

        result = rag_chain.invoke({"question": message, "chat_history": chat_history})
        print(result)
        return dict(result)['content']
