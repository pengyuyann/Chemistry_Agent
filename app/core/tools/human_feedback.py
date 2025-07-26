'''
!/usr/bin/env python
-*- coding: utf-8 -*-
@Time    : 2025/7/19 15:30
@Author  : JunYU
@File    : human_feedback
'''
import json
import time
from typing import Dict, List, Optional
from datetime import datetime
from langchain.tools import BaseTool
from langchain.schema import HumanMessage, AIMessage
from sqlalchemy.orm import Session

from app.core.db.models import HumanFeedback
from app.core.db.database import SessionLocal

class HumanFeedbackTool(BaseTool):
    """人类专家反馈工具 - 用于高风险任务的人工确认"""
    
    name: str = "HumanFeedback"
    description: str = (
        "当LLM无法确定或遇到高风险任务时，调用此工具请求人工反馈。"
        "适用于：管制化学品合成、爆炸性物质处理、高风险实验等场景。"
        "输入格式：JSON字符串，包含任务描述、风险评估、需要确认的问题等。"
    )
    
    def __init__(self, feedback_timeout: int = 300):
        super().__init__()
        # 使用私有属性避免Pydantic冲突
        self._feedback_timeout = feedback_timeout  # 反馈超时时间（秒）
        self._pending_feedbacks = {}  # 存储待处理的反馈请求
    
    def _run(self, request_data: str) -> str:
        """执行人类反馈请求"""
        try:
            # 解析请求数据
            if isinstance(request_data, str):
                request = json.loads(request_data)
            else:
                request = request_data
            
            # 生成反馈ID
            feedback_id = f"feedback_{int(time.time())}"
            
            # 创建反馈记录
            self._create_feedback_record(feedback_id, request)
            
            # 等待人工反馈
            response = self._wait_for_human_feedback(feedback_id, request)
            
            # 更新反馈记录
            self._update_feedback_record(feedback_id, response)
            
            return response.get("decision", "人工反馈超时，建议停止操作")
            
        except Exception as e:
            return f"人类反馈工具执行失败: {str(e)}"
    
    async def _arun(self, request_data: str) -> str:
        """异步执行人类反馈请求"""
        return self._run(request_data)
    
    def _create_feedback_record(self, feedback_id: str, request: Dict) -> None:
        """创建反馈记录到数据库"""
        try:
            db = SessionLocal()
            feedback = HumanFeedback(
                feedback_id=feedback_id,
                request_type=request.get("type", "unknown"),
                task_description=request.get("task_description", ""),
                risk_assessment=request.get("risk_assessment", ""),
                questions=json.dumps(request.get("questions", [])),
                status="pending",
                created_at=datetime.utcnow()
            )
            db.add(feedback)
            db.commit()
            db.close()
        except Exception as e:
            print(f"Warning: Failed to create feedback record: {e}")
    
    def _wait_for_human_feedback(self, feedback_id: str, request: Dict) -> Dict:
        """等待人工反馈"""
        start_time = time.time()
        
        # 构建反馈消息
        feedback_message = self._build_feedback_message(request)
        print(f"\n{'='*60}")
        print("🤖 需要人工确认的任务:")
        print(feedback_message)
        print(f"{'='*60}")
        
        # 模拟等待人工反馈（实际应用中应该通过Web界面或API）
        while time.time() - start_time < self._feedback_timeout:
            # 检查数据库中是否有反馈
            response = self._check_feedback_response(feedback_id)
            if response:
                return response
            
            time.sleep(2)  # 每2秒检查一次
        
        # 超时返回默认响应
        return {
            "decision": "timeout",
            "message": "人工反馈超时，建议停止操作以确保安全",
            "approved": False
        }
    
    def _build_feedback_message(self, request: Dict) -> str:
        """构建反馈消息"""
        message = []
        message.append(f"📋 任务类型: {request.get('type', '未知')}")
        message.append(f"📝 任务描述: {request.get('task_description', '无')}")
        
        if request.get('risk_assessment'):
            message.append(f"⚠️  风险评估: {request['risk_assessment']}")
        
        if request.get('questions'):
            message.append("❓ 需要确认的问题:")
            for i, question in enumerate(request['questions'], 1):
                message.append(f"   {i}. {question}")
        
        message.append("\n请通过管理界面进行确认或拒绝此操作。")
        return "\n".join(message)
    
    def _check_feedback_response(self, feedback_id: str) -> Optional[Dict]:
        """检查反馈响应"""
        try:
            db = SessionLocal()
            feedback = db.query(HumanFeedback).filter(
                HumanFeedback.feedback_id == feedback_id
            ).first()
            
            if feedback and feedback.status != "pending":
                response = {
                    "decision": feedback.status,
                    "message": feedback.response_message or "",
                    "approved": feedback.status == "approved",
                    "expert_name": feedback.expert_name,
                    "response_time": feedback.updated_at.isoformat() if feedback.updated_at else None
                }
                db.close()
                return response
            
            db.close()
            return None
            
        except Exception as e:
            print(f"Warning: Failed to check feedback response: {e}")
            return None
    
    def _update_feedback_record(self, feedback_id: str, response: Dict) -> None:
        """更新反馈记录"""
        try:
            db = SessionLocal()
            feedback = db.query(HumanFeedback).filter(
                HumanFeedback.feedback_id == feedback_id
            ).first()
            
            if feedback:
                feedback.status = response.get("decision", "unknown")
                feedback.response_message = response.get("message", "")
                feedback.expert_name = response.get("expert_name", "")
                feedback.updated_at = datetime.utcnow()
                db.commit()
            
            db.close()
        except Exception as e:
            print(f"Warning: Failed to update feedback record: {e}")
    
    def get_pending_feedbacks(self) -> List[Dict]:
        """获取待处理的反馈请求"""
        try:
            db = SessionLocal()
            pending = db.query(HumanFeedback).filter(
                HumanFeedback.status == "pending"
            ).all()
            
            result = []
            for feedback in pending:
                result.append({
                    "feedback_id": feedback.feedback_id,
                    "type": feedback.request_type,
                    "task_description": feedback.task_description,
                    "risk_assessment": feedback.risk_assessment,
                    "questions": json.loads(feedback.questions) if feedback.questions else [],
                    "created_at": feedback.created_at.isoformat() if feedback.created_at else None
                })
            
            db.close()
            return result
            
        except Exception as e:
            print(f"Warning: Failed to get pending feedbacks: {e}")
            return []
    
    def approve_feedback(self, feedback_id: str, expert_name: str, message: str = "") -> bool:
        """批准反馈请求"""
        return self._update_feedback_status(feedback_id, "approved", expert_name, message)
    
    def reject_feedback(self, feedback_id: str, expert_name: str, message: str = "") -> bool:
        """拒绝反馈请求"""
        return self._update_feedback_status(feedback_id, "rejected", expert_name, message)
    
    def _update_feedback_status(self, feedback_id: str, status: str, expert_name: str, message: str) -> bool:
        """更新反馈状态"""
        try:
            db = SessionLocal()
            feedback = db.query(HumanFeedback).filter(
                HumanFeedback.feedback_id == feedback_id
            ).first()
            
            if feedback:
                feedback.status = status
                feedback.response_message = message
                feedback.expert_name = expert_name
                feedback.updated_at = datetime.utcnow()
                db.commit()
                db.close()
                return True
            
            db.close()
            return False
            
        except Exception as e:
            print(f"Warning: Failed to update feedback status: {e}")
            return False

# 全局人类反馈工具实例
human_feedback_tool = HumanFeedbackTool() 