import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate, Link } from 'react-router-dom';
import { Card, Input, Button, Typography, message } from 'antd';

const { Title } = Typography;

const Register: React.FC = () => {
  const { register } = useAuth();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await register(username, password);
      message.success('注册成功，已自动登录');
      navigate('/');
    } catch (err) {
      message.error('注册失败，用户名可能已存在');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#f5f6fa' }}>
      <Card style={{ width: 350, borderRadius: 12, boxShadow: '0 4px 24px rgba(0,0,0,0.08)' }}>
        <Title level={3} style={{ textAlign: 'center' }}>注册 Chemistry Agent</Title>
        <form onSubmit={handleSubmit}>
          <Input
            placeholder="用户名"
            value={username}
            onChange={e => setUsername(e.target.value)}
            style={{ marginBottom: 16 }}
            size="large"
            autoFocus
          />
          <Input.Password
            placeholder="密码"
            value={password}
            onChange={e => setPassword(e.target.value)}
            style={{ marginBottom: 16 }}
            size="large"
          />
          <Button type="primary" htmlType="submit" block size="large" loading={loading}>
            注册
          </Button>
        </form>
        <div style={{ marginTop: 16, textAlign: 'center' }}>
          已有账号？<Link to="/login">登录</Link>
        </div>
      </Card>
    </div>
  );
};

export default Register; 