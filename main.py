import streamlit as st
from multiprocessing import context
from unittest import result
from unittest import result

from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

template="""
Answer the question based on the following context:
Here is the conversation history: {context}

Question: {question}
Answer:
"""
model = OllamaLLM(model="minimax-m2.5:cloud")
prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model

def handle_conversation():
    context = ""
    print("Start a conversation with the bot (type 'exit' or 'quit' to end):")
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit", "bye","goodbye","chup raho"]:
            print("Exiting the conversation.")
            break
        
        result = chain.invoke({"context": context, "question": user_input}) # type: ignore
        print(f"Bot: {result}")
        context += f"\nYou: {user_input}\nBot: {result}\n" # type: ignore

if __name__ == "__main__":
    handle_conversation()
    