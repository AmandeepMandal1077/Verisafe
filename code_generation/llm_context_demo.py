import os
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables from .env file (for API keys)
load_dotenv()

# Import the necessary provider classes
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI

@dataclass
class LLMContext:
    prompt: str
    response: str
    strategy: str
    provider: str
    model_name: str

def generate_response(
    prompt: str, 
    strategy: str = "basic_test", 
    provider: str = "ollama", 
    model_name: str = "llama3"
) -> LLMContext:
    """
    Takes a prompt, queries the specified provider's model, and returns an LLMContext object.
    Supported providers: 'ollama', 'openai' (or 'chatgpt'), 'anthropic', 'gemini'
    """
    provider = provider.lower()
    
    if provider == "ollama":
        llm = ChatOllama(model=model_name)
        response = llm.invoke(prompt).content
        
    elif provider == "openai":
        llm = ChatOpenAI(model=model_name)
        response = llm.invoke(prompt).content
        
    elif provider == "anthropic":
        llm = ChatAnthropic(model=model_name)
        response = llm.invoke(prompt).content
        
    elif provider == "google":
        llm = ChatGoogleGenerativeAI(model=model_name)
        response = llm.invoke(prompt).content
        
    else:
        raise ValueError(f"Unsupported provider: {provider}")
    
    return LLMContext(
        prompt=prompt,
        response=response.strip(),
        strategy=strategy,
        provider=provider,
        model_name=model_name
    )
