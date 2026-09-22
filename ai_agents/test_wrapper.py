import os

os.environ["GROQ_API_KEY"] = "dummy"

from langchain_groq import ChatGroq

class FallbackChatGroq:
    def __init__(self, temperature=0.0):
        self.temperature = temperature
        self.key = "dummy"
        self.primary = ChatGroq(api_key=self.key, model="llama-3.3-70b-versatile", temperature=temperature)
        self.fallback = ChatGroq(api_key=self.key, model="llama3-8b-8192", temperature=temperature)

    def bind_tools(self, tools):
        return self.primary.bind_tools(tools).with_fallbacks([self.fallback.bind_tools(tools)])

    def with_structured_output(self, schema):
        return self.primary.with_structured_output(schema).with_fallbacks([self.fallback.with_structured_output(schema)])

    def invoke(self, messages, **kwargs):
        return self.primary.with_fallbacks([self.fallback]).invoke(messages, **kwargs)

try:
    from pydantic import BaseModel
    class TestTool(BaseModel):
        param: str
    
    llm = FallbackChatGroq()
    llm_with_tools = llm.bind_tools([TestTool])
    print("Wrapper bind_tools works!")
    
    llm_with_struct = llm.with_structured_output(TestTool)
    print("Wrapper with_structured_output works!")
except Exception as e:
    print(f"Error: {e}")
