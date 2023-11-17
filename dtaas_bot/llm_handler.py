from langchain.chat_models import GigaChat
from langchain.chains import RetrievalQA
from langchain.schema import SystemMessage, HumanMessage, AIMessage
from langchain.prompts import HumanMessagePromptTemplate, ChatPromptTemplate
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough


class Giga:
    def __init__(self, prompt, vector_store, sys_message):
        self._llm = GigaChat(temperature=1e-15, verify_ssl_certs=False, scope='GIGACHAT_API_CORP')
        self.prompt = prompt
        self.vs = vector_store
        self.sys_message = sys_message

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
                return input["question"]
        chat_history_from_db = db.get_context(chat_id)
        condense_q_system_prompt = """Тебе дана история чата и последний вопрос пользователя \
        который может отсылать к истории чата, сформулируй отдельный вопрос \
        который может быть понятен без истории чата. НЕ отвечай на вопрос, \
        просто переформулируй его, если нужно, а если не нужно, то не надо переформулировать."""
        chat_history = list()
        for index, element in enumerate(chat_history_from_db):
            chat_history.append(HumanMessage(content=element[0]))
            chat_history.append(AIMessage(content=element[1]))

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
                RunnablePassthrough.assign(context=condense_question | self.vs.as_retriever(search_kwargs={"k": relevant_docs_k}) | format_docs)
                | qa_prompt
                | self._llm
        )

        result = rag_chain.invoke({"question": message, "chat_history": chat_history})
        print(result)
        return dict(result)['content']
