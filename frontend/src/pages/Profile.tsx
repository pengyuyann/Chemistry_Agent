import React, { useState, useEffect } from 'react';
import {
  Card,
  Row,
  Col,
  Statistic,
  Progress,
  Descriptions,
  Button,
  Modal,
  Form,
  Input,
  Select,
  InputNumber,
  message,
  Avatar,
  Tag,
  Divider,
  Space,
  Typography,
  Spin,
  Alert,
} from 'antd';
import {
  UserOutlined,
  MailOutlined,
  SettingOutlined,
  BarChartOutlined,
  CalendarOutlined,
  ClockCircleOutlined,
  EditOutlined,
  SaveOutlined,
  ReloadOutlined,
} from '@ant-design/icons';
import { useAuth } from '../context/AuthContext';
import { getUserProfile, updateUserEmail, updateUserPreferences, UserProfile } from '../api/auth';
import { useNavigate } from 'react-router-dom';

const { Title, Text } = Typography;
const { Option } = Select;

const Profile: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(false);
  const [editEmailModal, setEditEmailModal] = useState(false);
  const [editPreferencesModal, setEditPreferencesModal] = useState(false);
  const [emailForm] = Form.useForm();
  const [preferencesForm] = Form.useForm();

  // 加载用户信息
  const loadProfile = async () => {
    try {
      setLoading(true);
      const data = await getUserProfile();
      setProfile(data);
    } catch (error) {
      message.error('加载用户信息失败');
      console.error('加载用户信息错误:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadProfile();
  }, []);

  // 更新邮箱
  const handleUpdateEmail = async (values: { email: string }) => {
    try {
      setUpdating(true);
      await updateUserEmail(values.email);
      message.success('邮箱更新成功');
      setEditEmailModal(false);
      loadProfile(); // 重新加载用户信息
    } catch (error) {
      message.error('邮箱更新失败');
      console.error('邮箱更新错误:', error);
    } finally {
      setUpdating(false);
    }
  };

  // 更新偏好设置
  const handleUpdatePreferences = async (values: any) => {
    try {
      setUpdating(true);
      await updateUserPreferences(values);
      message.success('偏好设置更新成功');
      setEditPreferencesModal(false);
      loadProfile(); // 重新加载用户信息
    } catch (error) {
      message.error('偏好设置更新失败');
      console.error('偏好设置更新错误:', error);
    } finally {
      setUpdating(false);
    }
  };

  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh' 
      }}>
        <Spin size="large" />
      </div>
    );
  }

  if (!profile) {
    return (
      <div style={{ padding: 24 }}>
        <Alert
          message="加载失败"
          description="无法加载用户信息，请刷新页面重试"
          type="error"
          showIcon
          action={
            <Button size="small" onClick={loadProfile}>
              重试
            </Button>
          }
        />
      </div>
    );
  }

  // 计算API使用百分比（假设每日限制为100次）
  const dailyLimit = 100;
  const usagePercentage = Math.min((profile.api_calls_today / dailyLimit) * 100, 100);

  return (
    <div style={{ padding: 24, maxWidth: 1200, margin: '0 auto' }}>
      {/* 页面标题 */}
      <div style={{ marginBottom: 24 }}>
        <Title level={2} style={{ margin: 0, color: '#333' }}>
          <UserOutlined style={{ marginRight: 12, color: '#667eea' }} />
          个人信息
        </Title>
        <Text type="secondary">管理您的账户信息和偏好设置</Text>
      </div>

      <Row gutter={[24, 24]}>
        {/* 基本信息卡片 */}
        <Col xs={24} lg={12}>
          <Card
            title={
              <Space>
                <UserOutlined style={{ color: '#667eea' }} />
                基本信息
              </Space>
            }
            extra={
              <Button 
                type="text" 
                icon={<EditOutlined />}
                onClick={() => setEditEmailModal(true)}
              >
                编辑邮箱
              </Button>
            }
            style={{ height: '100%' }}
          >
            <div style={{ textAlign: 'center', marginBottom: 24 }}>
              <Avatar 
                size={80} 
                icon={<UserOutlined />} 
                style={{ 
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  marginBottom: 16
                }} 
              />
              <Title level={3} style={{ margin: 0 }}>{profile.username}</Title>
              {profile.is_admin && (
                <Tag color="blue" style={{ marginTop: 8 }}>
                  管理员
                </Tag>
              )}
            </div>

            <Descriptions column={1} size="small">
              <Descriptions.Item label="用户ID">{profile.user_id}</Descriptions.Item>
              <Descriptions.Item label="邮箱">
                {profile.email || (
                  <Text type="secondary">未设置</Text>
                )}
              </Descriptions.Item>
              <Descriptions.Item label="账户状态">
                <Tag color={profile.is_active ? 'green' : 'red'}>
                  {profile.is_active ? '激活' : '禁用'}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="注册时间">
                {new Date(profile.created_at).toLocaleString('zh-CN')}
              </Descriptions.Item>
              <Descriptions.Item label="最后登录">
                {profile.last_login 
                  ? new Date(profile.last_login).toLocaleString('zh-CN')
                  : '从未登录'
                }
              </Descriptions.Item>
            </Descriptions>
          </Card>
        </Col>

        {/* API使用情况卡片 */}
        <Col xs={24} lg={12}>
          <Card
            title={
              <Space>
                <BarChartOutlined style={{ color: '#667eea' }} />
                API使用情况
              </Space>
            }
            extra={
              <Button 
                type="text" 
                icon={<ReloadOutlined />}
                onClick={loadProfile}
              >
                刷新
              </Button>
            }
            style={{ height: '100%' }}
          >
            <Row gutter={[16, 16]}>
              <Col span={12}>
                <Statistic
                  title="总调用次数"
                  value={profile.api_calls_count}
                  valueStyle={{ color: '#667eea' }}
                />
              </Col>
              <Col span={12}>
                <Statistic
                  title="今日调用"
                  value={profile.api_calls_today}
                  valueStyle={{ color: '#52c41a' }}
                />
              </Col>
            </Row>

            <Divider />

            <div style={{ marginBottom: 16 }}>
              <Text strong>今日使用进度</Text>
              <Progress
                percent={usagePercentage}
                status={usagePercentage > 80 ? 'exception' : 'active'}
                strokeColor={{
                  '0%': '#667eea',
                  '100%': '#764ba2',
                }}
              />
              <Text type="secondary">
                {profile.api_calls_today} / {dailyLimit} 次
              </Text>
            </div>

            {profile.last_api_call && (
              <div>
                <Text type="secondary">
                  <ClockCircleOutlined style={{ marginRight: 4 }} />
                  最后调用: {new Date(profile.last_api_call).toLocaleString('zh-CN')}
                </Text>
              </div>
            )}
          </Card>
        </Col>

        {/* 偏好设置卡片 */}
        <Col xs={24} lg={12}>
          <Card
            title={
              <Space>
                <SettingOutlined style={{ color: '#667eea' }} />
                偏好设置
              </Space>
            }
            extra={
              <Button 
                type="text" 
                icon={<EditOutlined />}
                onClick={() => {
                  preferencesForm.setFieldsValue({
                    preferred_model: profile.preferred_model,
                    max_conversations: profile.max_conversations,
                    max_messages_per_conversation: profile.max_messages_per_conversation,
                  });
                  setEditPreferencesModal(true);
                }}
              >
                编辑设置
              </Button>
            }
            style={{ height: '100%' }}
          >
            <Descriptions column={1} size="small">
              <Descriptions.Item label="默认模型">
                <Tag color="blue">{profile.preferred_model}</Tag>
              </Descriptions.Item>
              <Descriptions.Item label="最大对话数">
                {profile.max_conversations}
              </Descriptions.Item>
              <Descriptions.Item label="每对话最大消息数">
                {profile.max_messages_per_conversation}
              </Descriptions.Item>
            </Descriptions>
          </Card>
        </Col>

        {/* 使用统计卡片 */}
        <Col xs={24} lg={12}>
          <Card
            title={
              <Space>
                <CalendarOutlined style={{ color: '#667eea' }} />
                使用统计
              </Space>
            }
            style={{ height: '100%' }}
          >
            <Row gutter={[16, 16]}>
              <Col span={12}>
                <Statistic
                  title="对话总数"
                  value={profile.conversation_count}
                  valueStyle={{ color: '#1890ff' }}
                />
              </Col>
              <Col span={12}>
                <Statistic
                  title="消息总数"
                  value={profile.message_count}
                  valueStyle={{ color: '#52c41a' }}
                />
              </Col>
            </Row>

            <Divider />

            <div style={{ textAlign: 'center' }}>
              <Text type="secondary">
                账户创建于 {new Date(profile.created_at).toLocaleDateString('zh-CN')}
              </Text>
            </div>
          </Card>
        </Col>
      </Row>

      {/* 编辑邮箱模态框 */}
      <Modal
        title="编辑邮箱"
        open={editEmailModal}
        onCancel={() => setEditEmailModal(false)}
        footer={null}
      >
        <Form
          form={emailForm}
          onFinish={handleUpdateEmail}
          layout="vertical"
          initialValues={{ email: profile.email || '' }}
        >
          <Form.Item
            name="email"
            label="邮箱地址"
            rules={[
              { required: true, message: '请输入邮箱地址' },
              { type: 'email', message: '请输入有效的邮箱地址' }
            ]}
          >
            <Input prefix={<MailOutlined />} placeholder="请输入邮箱地址" />
          </Form.Item>
          <Form.Item>
            <Space>
              <Button 
                type="primary" 
                htmlType="submit" 
                loading={updating}
                icon={<SaveOutlined />}
              >
                保存
              </Button>
              <Button onClick={() => setEditEmailModal(false)}>
                取消
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* 编辑偏好设置模态框 */}
      <Modal
        title="编辑偏好设置"
        open={editPreferencesModal}
        onCancel={() => setEditPreferencesModal(false)}
        footer={null}
      >
        <Form
          form={preferencesForm}
          onFinish={handleUpdatePreferences}
          layout="vertical"
        >
          <Form.Item
            name="preferred_model"
            label="默认模型"
            rules={[{ required: true, message: '请选择默认模型' }]}
          >
            <Select placeholder="选择默认模型">
              <Option value="deepseek-chat">DeepSeek Chat</Option>
              <Option value="gpt-4">GPT-4</Option>
              <Option value="gpt-3.5-turbo">GPT-3.5 Turbo</Option>
            </Select>
          </Form.Item>
          <Form.Item
            name="max_conversations"
            label="最大对话数"
            rules={[{ required: true, message: '请输入最大对话数' }]}
          >
            <InputNumber
              min={1}
              max={1000}
              style={{ width: '100%' }}
              placeholder="最大对话数"
            />
          </Form.Item>
          <Form.Item
            name="max_messages_per_conversation"
            label="每对话最大消息数"
            rules={[{ required: true, message: '请输入每对话最大消息数' }]}
          >
            <InputNumber
              min={1}
              max={10000}
              style={{ width: '100%' }}
              placeholder="每对话最大消息数"
            />
          </Form.Item>
          <Form.Item>
            <Space>
              <Button 
                type="primary" 
                htmlType="submit" 
                loading={updating}
                icon={<SaveOutlined />}
              >
                保存
              </Button>
              <Button onClick={() => setEditPreferencesModal(false)}>
                取消
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default Profile; 