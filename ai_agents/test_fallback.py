from langchain_groq import ChatGroq
import os

os.environ["GROQ_API_KEY"] = "dummy"

llm1 = ChatGroq(model="llama-3.3-70b-versatile")
llm2 = ChatGroq(model="llama3-8b-8192")
fallback_llm = llm1.with_fallbacks([llm2])

try:
    from pydantic import BaseModel
    class TestTool(BaseModel):
        param: str
    
    fallback_llm.bind_tools([TestTool])
    print("bind_tools works!")
    
    fallback_llm.with_structured_output(TestTool)
    print("with_structured_output works!")
except Exception as e:
    print(f"Error: {e}")
