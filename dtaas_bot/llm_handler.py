import logging
from langchain.chat_models import GigaChat
from langchain.chains import RetrievalQA
from langchain.schema import SystemMessage, HumanMessage
from langchain.prompts import HumanMessagePromptTemplate, ChatPromptTemplate


class Giga:
    def __init__(self, prompt, vector_store, sys_message):
        self._llm = GigaChat(temperature=1e-15, verify_ssl_certs=False)
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

    def get_response(self, message, relevant_docs_k=3):
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
            self._llm,
            chain_type='stuff',
            retriever=self.vs.as_retriever(search_kwargs={"k": relevant_docs_k}),
            chain_type_kwargs={"prompt": chat_template},
            return_source_documents=False
        )
        result = qa_chain({"query": message})
        response = result["result"]
        return response
