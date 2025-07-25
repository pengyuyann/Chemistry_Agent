from typing import Optional

import langchain
from dotenv import load_dotenv
from langchain import PromptTemplate, chains
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.chat_history import BaseChatMessageHistory
from pydantic import ValidationError
from rmrkl import ChatZeroShotAgent, RetryAgentExecutor

from .prompts import FORMAT_INSTRUCTIONS, QUESTION_PROMPT, REPHRASE_TEMPLATE, SUFFIX
from .tools import make_tools


def _make_llm(model, temp, api_key, streaming: bool = False):
    if model.startswith("gpt-3.5-turbo") or model.startswith("gpt-4"):
        llm = langchain.chat_models.ChatOpenAI(
            temperature=temp,
            model_name=model,
            request_timeout=1000,
            streaming=streaming,
            callbacks=[StreamingStdOutCallbackHandler()],
            openai_api_key=api_key,
        )
    elif model.startswith("text-"):
        llm = langchain.OpenAI(
            temperature=temp,
            model_name=model,
            streaming=streaming,
            callbacks=[StreamingStdOutCallbackHandler()],
            openai_api_key=api_key,
        )
    else:
        raise ValueError(f"Invalid model name: {model}")
    return llm


class ChemCrow:
    def __init__(
        self,
        tools=None,
        model="gpt-4-0613",
        tools_model="gpt-3.5-turbo-0613",
        temp=0.1,
        max_iterations=40,
        verbose=True,
        streaming: bool = True,
        openai_api_key: Optional[str] = None,
        api_keys: dict = {},
        local_rxn: bool = False,
        memory_window_size: int = 5,
        chat_history_backend: Optional[BaseChatMessageHistory] = None,
    ):
        """Initialize ChemCrow agent with memory support."""

        load_dotenv()
        try:
            self.llm = _make_llm(model, temp, openai_api_key, streaming)
        except ValidationError:
            raise ValueError("Invalid OpenAI API key")

        if tools is None:
            api_keys["OPENAI_API_KEY"] = openai_api_key
            tools_llm = _make_llm(tools_model, temp, openai_api_key, streaming)
            tools = make_tools(tools_llm, api_keys=api_keys, local_rxn=local_rxn, verbose=verbose)

        # Initialize memory
        self.memory = ConversationBufferWindowMemory(
            k=memory_window_size,
            memory_key="chat_history",
            chat_memory=chat_history_backend,
            return_messages=True,
        )

        # Initialize agent with memory
        self.agent_executor = RetryAgentExecutor.from_agent_and_tools(
            tools=tools,
            agent=ChatZeroShotAgent.from_llm_and_tools(
                self.llm,
                tools,
                suffix=SUFFIX,
                format_instructions=FORMAT_INSTRUCTIONS,
                question_prompt=QUESTION_PROMPT,
            ),
            verbose=True,
            max_iterations=max_iterations,
            memory=self.memory,  # 添加 memory 支持
        )

        rephrase = PromptTemplate(
            input_variables=["question", "agent_ans"], template=REPHRASE_TEMPLATE
        )

        self.rephrase_chain = chains.LLMChain(prompt=rephrase, llm=self.llm)

    def run(self, prompt):
        """Run ChemCrow with memory support."""
        outputs = self.agent_executor({"input": prompt})
        return outputs["output"]
    
    def get_chat_history(self):
        """Get current chat history."""
        return self.memory.chat_memory.messages if self.memory.chat_memory else []
    
    def clear_memory(self):
        """Clear the conversation memory."""
        if self.memory.chat_memory:
            self.memory.chat_memory.clear()
