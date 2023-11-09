from langchain.chat_models import GigaChat
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA, StuffDocumentsChain, LLMChain, ConversationalRetrievalChain
import joblib

class Giga:
    def __init__(self, prompt, vector_store):
        self._llm = GigaChat(temperature=1e-15, verify_ssl_certs=False)
        self.prompt = prompt
        self.vs = vector_store

    def get_response(self, message, relevant_docs_k=2):
        response = ""
        qa_chain = RetrievalQA.from_chain_type(
            self._llm,
            chain_type='stuff',
            retriever=self.vs.as_retriever(search_kwargs={"k": relevant_docs_k}),
            chain_type_kwargs={"prompt": PromptTemplate(
                                                        template=self.prompt,
                                                        input_variables=["query", "context"]
                                                        )},
            return_source_documents=False
        )
        result = qa_chain({"query": message})
        response = result["result"]
        return response
