#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/7/16 15:26
# @Author  : JunYU
# @File    : chemagent

from typing import Optional, List, Dict
import os
import json
import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor

from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain import chains
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

from langchain.agents import initialize_agent, AgentType
from langchain.agents import AgentExecutor
try:
    from pydantic import ValidationError
except ImportError:
    try:
        from pydantic.v1 import ValidationError
    except ImportError:
        ValidationError = ValueError

from .prompts import FORMAT_INSTRUCTIONS, QUESTION_PROMPT, REPHRASE_TEMPLATE, SUFFIX
from .tools import make_tools

class SimpleStreamingCallbackHandler(BaseCallbackHandler):
    """简化的流式回调处理器，避免事件循环问题"""
    
    def __init__(self):
        self.tokens = []
        
    def on_llm_start(self, serialized, prompts, **kwargs):
        """LLM 开始时的回调"""
        pass
    
    def on_llm_new_token(self, token, **kwargs):
        """LLM 生成新 token 时的回调"""
        self.tokens.append(token)
    
    def on_llm_end(self, response, **kwargs):
        """LLM 结束时的回调"""
        pass
    
    def on_tool_start(self, serialized, input_str, **kwargs):
        """工具开始执行时的回调"""
        pass
    
    def on_tool_end(self, output, **kwargs):
        """工具执行结束时的回调"""
        pass

def _make_llm(model, temp, api_key, streaming: bool = False, callbacks=None):
    """创建LLM实例"""
    try:
        if model.startswith("gpt-3.5-turbo") or model.startswith("gpt-4"):
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                temperature=temp,
                model_name=model,
                request_timeout=1000,
                streaming=streaming,
                callbacks=callbacks,
                openai_api_key=api_key,
            )
        elif model.startswith("text-"):
            from langchain_openai import OpenAI
            return OpenAI(
                temperature=temp,
                model_name=model,
                streaming=streaming,
                callbacks=callbacks,
                openai_api_key=api_key,
            )
        elif model.startswith("deepseek-chat") or model.startswith("deepseek-reasoner"):
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                temperature=temp,
                model_name=model,
                request_timeout=1000,
                streaming=streaming,
                callbacks=callbacks,
                openai_api_key=api_key,
                openai_api_base="https://api.deepseek.com/v1",
            )
        else:
            raise ValueError(f"Invalid model name: {model}")
    except Exception as e:
        # 捕获所有可能的异常，包括ValidationError和其他配置错误
        raise ValueError(f"Failed to create LLM instance for model {model}: {str(e)}")

class ChemAgent:
    def __init__(
        self,
        tools=None,
        model="deepseek-chat",
        tools_model="deepseek-chat",
        temp=0.1,
        max_iterations=40,
        verbose=True,
        streaming=True,
        openai_api_key: Optional[str] = None,
        api_keys: dict = {},
        local_rxn: bool = False,
        user_id: Optional[int] = None,
        conversation_id: Optional[str] = None,
    ):
        """初始化 ChemAgent"""

        load_dotenv()

        # 创建简化的流式回调处理器
        self.streaming_callback = SimpleStreamingCallbackHandler()
        
        # 添加控制台输出回调
        callbacks = [self.streaming_callback, StreamingStdOutCallbackHandler()]

        try:
            self.llm = _make_llm(model, temp, openai_api_key, streaming, callbacks)
        except Exception as e:
            raise ValueError(f"Failed to initialize LLM: {str(e)}")

        if tools is None:
            api_keys["OPENAI_API_KEY"] = openai_api_key
            tools_llm = _make_llm(tools_model, temp, openai_api_key, streaming, callbacks)
            tools = make_tools(tools_llm, api_keys=api_keys, local_rxn=local_rxn, verbose=verbose,
                              user_id=user_id, conversation_id=conversation_id)

        # 构造智能体执行器 - 用于推理过程
        self.agent_executor = initialize_agent(
            tools=tools,
            llm=self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=verbose,
            max_iterations=max_iterations,
            handle_parsing_errors=True,
            return_intermediate_steps=True,
        )

        # 构造最终答案生成的模板链
        final_answer_template = """
你是一位专业的化学助手。基于以下推理过程，为用户的问题提供一个完整、准确、有教育意义的答案。

用户问题: {question}

可用工具:
{tool_strings}

推理过程:
{intermediate_steps}

请基于上述推理过程，为用户提供一个完整的答案。要求：
1. 保持专业、友好的语调
2. 准确反映推理过程中获得的信息
3. 解释关键结论是如何得出的
4. 如果涉及安全性检查，要明确说明
5. 如果涉及分子分析，要详细解释结果
6. 如果涉及合成规划，要提供清晰的步骤说明

答案:
"""
        final_answer_prompt = PromptTemplate(
            input_variables=["question", "intermediate_steps", "tool_strings"], 
            template=final_answer_template
        )
        self.final_answer_chain = chains.LLMChain(prompt=final_answer_prompt, llm=self.llm)

    def run(self, prompt):
        """同步执行"""
        outputs = self.agent_executor({"input": prompt})
        return outputs["output"]

    async def run_stream(self, prompt, conversation_context: List[Dict[str, str]] = None):
        """异步流式推理输出：分离推理过程和最终答案生成"""
        # 发送开始思考的信号
        yield json.dumps({
            "type": "thinking",
            "content": "开始分析问题..."
        }, ensure_ascii=False)
        await asyncio.sleep(0.1)

        try:
            # 构建包含历史上下文的输入
            if conversation_context:
                # 将历史对话格式化为字符串
                context_str = "\n\n".join([
                    f"用户: {msg['content']}" if msg['role'] == 'user' else f"助手: {msg['content']}"
                    for msg in conversation_context
                ])
                full_prompt = f"历史对话:\n{context_str}\n\n当前问题: {prompt}"
            else:
                full_prompt = prompt
            
            # 执行 agent 并获取结果
            result = await asyncio.get_event_loop().run_in_executor(
                None, self.agent_executor, {"input": full_prompt}
            )

            # 获取中间步骤
            intermediate_steps = result.get("intermediate_steps", [])

            # 处理每个推理步骤
            for i, step in enumerate(intermediate_steps, 1):
                action, observation = step
                
                tool_name = getattr(action, "tool", "")
                tool_input = getattr(action, "tool_input", "")
                thought = getattr(action, "log", "")

                # 发送工具开始信号
                yield json.dumps({
                    "type": "tool_start",
                    "tool": tool_name,
                    "input": tool_input
                }, ensure_ascii=False)
                await asyncio.sleep(0.1)

                # 发送推理步骤
                yield json.dumps({
                    "type": "step",
                    "thought": thought,
                    "action": tool_name,
                    "action_input": tool_input,
                    "observation": str(observation)
                }, ensure_ascii=False)
                await asyncio.sleep(0.1)

                # 发送工具结束信号
                yield json.dumps({
                    "type": "tool_end",
                    "output": str(observation)
                }, ensure_ascii=False)
                await asyncio.sleep(0.1)

            # 发送思考结束的信号
            yield json.dumps({
                "type": "thinking_end",
                "content": ""
            }, ensure_ascii=False)
            await asyncio.sleep(0.1)

            # 生成最终答案 - 回顾完整上下文
            final_answer = await self._generate_final_answer(prompt, intermediate_steps, conversation_context)

            # 输出最终答案
            yield json.dumps({
                "type": "final",
                "output": final_answer
            }, ensure_ascii=False)

        except Exception as e:
            # 发送错误信息
            yield json.dumps({
                "type": "error",
                "message": str(e)
            }, ensure_ascii=False)

    async def _generate_final_answer(self, question: str, intermediate_steps: list, conversation_context: List[Dict[str, str]] = None) -> str:
        """生成最终答案，回顾完整的推理上下文"""
        try:
            # 构建工具字符串
            tool_strings = "\n".join([f"- {tool.name}: {tool.description}" for tool in self.agent_executor.tools])

            # 构建中间步骤的文本表示
            steps_text = ""
            for i, (action, observation) in enumerate(intermediate_steps, 1):
                thought = getattr(action, "log", "")
                tool_name = getattr(action, "tool", "")
                tool_input = getattr(action, "tool_input", "")

                steps_text += f"步骤 {i}:\n"
                steps_text += f"思考: {thought}\n"
                steps_text += f"工具: {tool_name}\n"
                steps_text += f"输入: {tool_input}\n"
                steps_text += f"观察: {observation}\n\n"

            # 如果有历史上下文，添加到问题中
            context_enhanced_question = question
            if conversation_context:
                context_summary = self._summarize_context(conversation_context)
                context_enhanced_question = f"基于历史对话：{context_summary}\n\n当前问题：{question}"

            # 使用最终答案生成链
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                self.final_answer_chain.run,
                {
                    "question": context_enhanced_question,
                    "intermediate_steps": steps_text,
                    "tool_strings": tool_strings
                }
            )

            return result
        except Exception as e:
            # 如果最终答案生成失败，返回原始输出
            print(f"Final answer generation failed: {e}")
            return "抱歉，在生成最终答案时出现了问题。"

    def _summarize_context(self, conversation_context: List[Dict[str, str]]) -> str:
        """总结对话上下文"""
        if not conversation_context:
            return ""
        
        # 提取最近的几轮对话
        recent_messages = conversation_context[-6:]  # 最近3轮对话
        
        summary_parts = []
        for msg in recent_messages:
            role = "用户" if msg['role'] == 'user' else "助手"
            content = msg['content'][:100] + "..." if len(msg['content']) > 100 else msg['content']
            summary_parts.append(f"{role}: {content}")
        
        return "；".join(summary_parts)

    def get_context_prompt(self, user_input: str, include_context: bool = False, conversation_context: List[Dict[str, str]] = None) -> str:
        """获取包含上下文的提示"""
        if not include_context or not conversation_context:
            return user_input
        
        # 构建上下文提示
        context_str = "\n\n".join([
            f"用户: {msg['content']}" if msg['role'] == 'user' else f"助手: {msg['content']}"
            for msg in conversation_context[-4:]  # 最近2轮对话
        ])
        
        return f"历史对话:\n{context_str}\n\n当前问题: {user_input}"

    def add_to_context(self, role: str, content: str):
        """添加消息到上下文（保持向后兼容）"""
        # 这个方法现在主要用于向后兼容，实际上下文管理在API层处理
        pass
    
    def get_enhanced_context_prompt(self, user_input: str, conversation_context: List[Dict[str, str]] = None, 
                                   relevant_history: List[Dict] = None) -> str:
        """获取增强的上下文提示，包含重排序的历史对话"""
        if not conversation_context and not relevant_history:
            return user_input
        
        context_parts = []
        
        # 添加重排序的相关历史对话
        if relevant_history:
            history_context = []
            for i, hist in enumerate(relevant_history[:2]):  # 最多2个相关历史
                relevance_score = hist.get('relevance_score', 0)
                topics = hist.get('topics', [])
                entities = hist.get('key_entities', [])
                
                history_context.append(f"相关历史对话 {i+1} (相关性: {relevance_score:.2f}):")
                if topics:
                    history_context.append(f"主题: {', '.join(topics)}")
                if entities:
                    history_context.append(f"关键实体: {', '.join(entities)}")
                history_context.append("")
            
            if history_context:
                context_parts.append("相关历史对话:\n" + "\n".join(history_context))
        
        # 添加当前对话上下文
        if conversation_context:
            current_context = "\n\n".join([
                f"用户: {msg['content']}" if msg['role'] == 'user' else f"助手: {msg['content']}"
                for msg in conversation_context[-4:]  # 最近2轮对话
            ])
            context_parts.append(f"当前对话:\n{current_context}")
        
        # 组合所有上下文
        full_context = "\n\n".join(context_parts)
        return f"{full_context}\n\n当前问题: {user_input}"
