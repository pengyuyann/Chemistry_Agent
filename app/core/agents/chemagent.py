'''
!/usr/bin/env python
-*- coding: utf-8 -*-
@Time    : 2025/7/16 15:26
@Author  : JunYU
@File    : chemagent
'''

from typing import Optional

import langchain
from IPython.core.debugger import prompt
from dotenv import load_dotenv
from langchain import PromptTemplate, chains
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from osmnx.settings import requests_timeout
from pydantic import ValidationError
from langchain.agents import initialize_agent, AgentType
from langchain.agents import AgentExecutor
from sympy.physics.units import temperature

from .prompts import FORMAT_INSTRUCTIONS, QUESTION_PROMPT, REPHRASE_TEMPLATE, SUFFIX
from .tools import make_tools

def _make_llm(model, temp, api_key, streaming:bool = False):
    # 设置代理
    import os
    os.environ["http_proxy"] = "http://127.0.0.1:7897"
    os.environ["https_proxy"] = "http://127.0.0.1:7897"
    
    if model.startswith("gpt-3.5-turbo") or model.startswith("gpt-4"):
        llm = langchain.chat_models.ChatOpenAI(
            temperature=temp,
            model_name = model,
            request_timeout=1000,
            streaming=streaming,
            callbacks= [StreamingStdOutCallbackHandler()],
            openai_api_key=api_key,
        )
    elif model.startswith("text-"):
        llm = langchain.OpenAI(
            temperature=temp,
            model_name = model,
            streaming=streaming,
            callbacks= [StreamingStdOutCallbackHandler()],
            openai_api_key=api_key,
        )
    elif model.startswith("deepseek-chat"):
        llm = langchain.chat_models.ChatOpenAI(
            temperature=temp,
            model_name = model,
            request_timeout=1000,
            streaming=streaming,
            callbacks= [StreamingStdOutCallbackHandler()],
            openai_api_key=api_key,
            openai_api_base="https://api.deepseek.com/v1",
        )
    else:
        raise ValueError(f"Invalid model name: {model}")
    return llm

class ChemAgent:
    def __init__(
            self,
            tools=None,
            model="deepseek-chat",
            tools_model="deepseek-chat",
            temp = 0.1,
            max_iterations = 40,
            verbose = True,
            streaming: bool = True,
            openai_api_key: Optional[str] = None,
            api_keys: dict = {},
            local_rxn: bool = False,
    ):
        """Initialize ChemAgent"""

        load_dotenv()
        try:
            self.llm = _make_llm(model, temp, openai_api_key, streaming)
        except ValidationError:
            raise ValueError("Invalid OpenAI API keys")

        if tools is None:
            api_keys["OPENAI_API_KEY"] = openai_api_key
            tools_llm = _make_llm(tools_model, temp, openai_api_key, streaming)
            tools = make_tools(tools_llm, api_keys=api_keys, local_rxn=local_rxn, verbose=verbose)

        # Initialize agent using standard LangChain
        self.agent_executor = initialize_agent(
            tools=tools,
            llm=self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            max_iterations=max_iterations,
            handle_parsing_errors=True,
        )

        rephrase = PromptTemplate(
            input_variables=["question", "agent_ans"], template=REPHRASE_TEMPLATE
        )

        self.rephrase_chain = chains.LLMChain(prompt=rephrase, llm=self.llm)

    def run(self, prompt):
        outputs = self.agent_executor({"input": prompt})
        return outputs["output"]