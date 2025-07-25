import React, { useState, useEffect } from 'react';
import { feedbackApi, PendingFeedback, FeedbackHistory, FeedbackStats } from '../api/feedback';
import './FeedbackManagement.css';

const FeedbackManagement: React.FC = () => {
  const [pendingFeedbacks, setPendingFeedbacks] = useState<PendingFeedback[]>([]);
  const [feedbackHistory, setFeedbackHistory] = useState<FeedbackHistory[]>([]);
  const [stats, setStats] = useState<FeedbackStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [activeTab, setActiveTab] = useState<'pending' | 'history' | 'stats'>('pending');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [expertName, setExpertName] = useState('');
  const [responseMessage, setResponseMessage] = useState('');

  useEffect(() => {
    loadData();
  }, [activeTab, currentPage]);

  const loadData = async () => {
    try {
      setLoading(true);
      setMessage('');

      switch (activeTab) {
        case 'pending':
          const pending = await feedbackApi.getPendingFeedbacks();
          setPendingFeedbacks(pending);
          break;
        case 'history':
          const history = await feedbackApi.getFeedbackHistory(20, (currentPage - 1) * 20);
          setFeedbackHistory(history.feedbacks);
          setTotalPages(Math.ceil(history.total / 20));
          break;
        case 'stats':
          const statsData = await feedbackApi.getFeedbackStats();
          setStats(statsData);
          break;
      }
    } catch (error) {
      setMessage('加载数据失败');
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFeedbackAction = async (
    feedbackId: string, 
    action: 'approve' | 'reject'
  ) => {
    if (!expertName.trim()) {
      setMessage('请输入专家姓名');
      return;
    }

    try {
      setLoading(true);
      setMessage('');

      const request = {
        expert_name: expertName,
        message: responseMessage
      };

      const result = action === 'approve' 
        ? await feedbackApi.approveFeedback(feedbackId, request)
        : await feedbackApi.rejectFeedback(feedbackId, request);

      setMessage(result.message);
      if (result.success) {
        await loadData(); // 重新加载数据
        setResponseMessage('');
      }
    } catch (error) {
      setMessage('操作失败');
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteFeedback = async (feedbackId: string) => {
    if (!window.confirm('确定要删除这条反馈记录吗？')) return;

    try {
      setLoading(true);
      const result = await feedbackApi.deleteFeedback(feedbackId);
      setMessage(result.message);
      if (result.success) {
        await loadData();
      }
    } catch (error) {
      setMessage('删除失败');
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'approved': return 'green';
      case 'rejected': return 'red';
      case 'pending': return 'orange';
      case 'timeout': return 'gray';
      default: return 'black';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'approved': return '✅ 已批准';
      case 'rejected': return '❌ 已拒绝';
      case 'pending': return '⏳ 待处理';
      case 'timeout': return '⏰ 超时';
      default: return status;
    }
  };

  return (
    <div className="feedback-management">
      <h1>👥 人类反馈管理</h1>

      {/* 标签页 */}
      <div className="tabs">
        <button 
          className={`tab ${activeTab === 'pending' ? 'active' : ''}`}
          onClick={() => setActiveTab('pending')}
        >
          ⏳ 待处理反馈 ({pendingFeedbacks.length})
        </button>
        <button 
          className={`tab ${activeTab === 'history' ? 'active' : ''}`}
          onClick={() => setActiveTab('history')}
        >
          📋 反馈历史
        </button>
        <button 
          className={`tab ${activeTab === 'stats' ? 'active' : ''}`}
          onClick={() => setActiveTab('stats')}
        >
          📊 统计信息
        </button>
      </div>

      {/* 专家信息输入 */}
      <div className="expert-info">
        <input
          type="text"
          value={expertName}
          onChange={(e) => setExpertName(e.target.value)}
          placeholder="专家姓名"
          className="expert-name-input"
        />
      </div>

      {/* 内容区域 */}
      <div className="content-area">
        {loading ? (
          <div className="loading">加载中...</div>
        ) : (
          <>
            {/* 待处理反馈 */}
            {activeTab === 'pending' && (
              <div className="pending-feedbacks">
                {pendingFeedbacks.length > 0 ? (
                  pendingFeedbacks.map((feedback) => (
                    <div key={feedback.feedback_id} className="feedback-card">
                      <div className="feedback-header">
                        <h3>反馈 ID: {feedback.feedback_id}</h3>
                        <span className="feedback-type">{feedback.type}</span>
                      </div>
                      
                      <div className="feedback-content">
                        <div className="field">
                          <strong>任务描述:</strong>
                          <p>{feedback.task_description}</p>
                        </div>
                        
                        {feedback.risk_assessment && (
                          <div className="field">
                            <strong>风险评估:</strong>
                            <p className="risk-assessment">{feedback.risk_assessment}</p>
                          </div>
                        )}
                        
                        {feedback.questions.length > 0 && (
                          <div className="field">
                            <strong>需要确认的问题:</strong>
                            <ul>
                              {feedback.questions.map((question, index) => (
                                <li key={index}>{question}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                        
                        <div className="field">
                          <strong>创建时间:</strong>
                          <span>{new Date(feedback.created_at).toLocaleString()}</span>
                        </div>
                      </div>

                      <div className="feedback-actions">
                        <textarea
                          value={responseMessage}
                          onChange={(e) => setResponseMessage(e.target.value)}
                          placeholder="回复消息（可选）"
                          className="response-input"
                        />
                        <div className="action-buttons">
                          <button
                            onClick={() => handleFeedbackAction(feedback.feedback_id, 'approve')}
                            disabled={loading || !expertName.trim()}
                            className="btn btn-success"
                          >
                            ✅ 批准
                          </button>
                          <button
                            onClick={() => handleFeedbackAction(feedback.feedback_id, 'reject')}
                            disabled={loading || !expertName.trim()}
                            className="btn btn-danger"
                          >
                            ❌ 拒绝
                          </button>
                        </div>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="empty-state">
                    <p>暂无待处理的反馈请求</p>
                  </div>
                )}
              </div>
            )}

            {/* 反馈历史 */}
            {activeTab === 'history' && (
              <div className="feedback-history">
                {feedbackHistory.length > 0 ? (
                  <>
                    <div className="history-list">
                      {feedbackHistory.map((feedback) => (
                        <div key={feedback.feedback_id} className="history-card">
                          <div className="history-header">
                            <h3>反馈 ID: {feedback.feedback_id}</h3>
                            <span 
                              className="status"
                              style={{ color: getStatusColor(feedback.status) }}
                            >
                              {getStatusText(feedback.status)}
                            </span>
                          </div>
                          
                          <div className="history-content">
                            <div className="field">
                              <strong>类型:</strong> {feedback.type}
                            </div>
                            <div className="field">
                              <strong>任务描述:</strong>
                              <p>{feedback.task_description}</p>
                            </div>
                            {feedback.response_message && (
                              <div className="field">
                                <strong>专家回复:</strong>
                                <p>{feedback.response_message}</p>
                              </div>
                            )}
                            {feedback.expert_name && (
                              <div className="field">
                                <strong>处理专家:</strong> {feedback.expert_name}
                              </div>
                            )}
                            <div className="field">
                              <strong>创建时间:</strong> {new Date(feedback.created_at).toLocaleString()}
                            </div>
                            {feedback.updated_at && (
                              <div className="field">
                                <strong>处理时间:</strong> {new Date(feedback.updated_at).toLocaleString()}
                              </div>
                            )}
                          </div>

                          <div className="history-actions">
                            <button
                              onClick={() => handleDeleteFeedback(feedback.feedback_id)}
                              className="btn btn-danger btn-sm"
                            >
                              🗑️ 删除
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>

                    {/* 分页 */}
                    {totalPages > 1 && (
                      <div className="pagination">
                        <button
                          onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                          disabled={currentPage === 1}
                          className="btn btn-secondary"
                        >
                          上一页
                        </button>
                        <span className="page-info">
                          第 {currentPage} 页，共 {totalPages} 页
                        </span>
                        <button
                          onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                          disabled={currentPage === totalPages}
                          className="btn btn-secondary"
                        >
                          下一页
                        </button>
                      </div>
                    )}
                  </>
                ) : (
                  <div className="empty-state">
                    <p>暂无反馈历史记录</p>
                  </div>
                )}
              </div>
            )}

            {/* 统计信息 */}
            {activeTab === 'stats' && stats && (
              <div className="stats-section">
                <div className="stats-grid">
                  <div className="stat-card">
                    <h3>总反馈数</h3>
                    <p>{stats.total}</p>
                  </div>
                  <div className="stat-card">
                    <h3>最近7天</h3>
                    <p>{stats.recent_7_days}</p>
                  </div>
                </div>

                <div className="stats-details">
                  <div className="status-distribution">
                    <h3>状态分布</h3>
                    <div className="distribution-list">
                      {Object.entries(stats.status_distribution).map(([status, count]) => (
                        <div key={status} className="distribution-item">
                          <span className="status-label">{getStatusText(status)}</span>
                          <span className="status-count">{count}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="type-distribution">
                    <h3>类型分布</h3>
                    <div className="distribution-list">
                      {Object.entries(stats.type_distribution).map(([type, count]) => (
                        <div key={type} className="distribution-item">
                          <span className="type-label">{type}</span>
                          <span className="type-count">{count}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            )}
          </>
        )}
      </div>

      {/* 消息提示 */}
      {message && (
        <div className={`message ${message.includes('失败') ? 'error' : 'success'}`}>
          {message}
        </div>
      )}
    </div>
  );
};

export default FeedbackManagement; 