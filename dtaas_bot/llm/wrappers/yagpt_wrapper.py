from .llm_wrapper_interface import LLMWrapperInterface, Message

class YaGPTWrapper(LLMWrapperInterface):
    def __init__(self, base_prompt="") -> None:
        super().__init__(base_prompt)

    def call(self, msg: str) -> str:
        raise NotImplementedError()
        return super().call(msg)
    
    def call_chat(self, messages: list[Message]) -> str:
        raise NotImplementedError()
        return super().call_chat(messages)