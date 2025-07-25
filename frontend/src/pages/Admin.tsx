import React, { useEffect, useState } from 'react';
import { Card, Table, Button, Tag, Popconfirm, message, Layout, Typography } from 'antd';
import { getUsers, setAdmin, deleteUser } from '../api/admin';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';

const { Header, Content } = Layout;
const { Title } = Typography;

interface User {
  id: number;
  username: string;
  is_admin: boolean;
}

const Admin: React.FC = () => {
  const { user } = useAuth();
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const data = await getUsers();
      setUsers(data);
    } catch {
      message.error('获取用户列表失败');
    } finally {
      setLoading(false);
    }
  };

  const handleSetAdmin = async (id: number, isAdmin: boolean) => {
    try {
      await setAdmin(id, isAdmin);
      message.success('操作成功');
      fetchUsers();
    } catch {
      message.error('操作失败');
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await deleteUser(id);
      message.success('删除成功');
      fetchUsers();
    } catch {
      message.error('删除失败');
    }
  };

  const columns = [
    { title: 'ID', dataIndex: 'id', key: 'id', width: 60 },
    { title: '用户名', dataIndex: 'username', key: 'username' },
    { title: '权限', dataIndex: 'is_admin', key: 'is_admin', render: (v: boolean) => v ? <Tag color="blue">管理员</Tag> : <Tag>普通用户</Tag> },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: User) => (
        <>
          {record.id !== user?.id && (
            <>
              <Button size="small" type={record.is_admin ? 'default' : 'primary'} onClick={() => handleSetAdmin(record.id, !record.is_admin)} style={{ marginRight: 8 }}>
                {record.is_admin ? '取消管理员' : '设为管理员'}
              </Button>
              <Popconfirm title="确定删除该用户？" onConfirm={() => handleDelete(record.id)} okText="删除" cancelText="取消">
                <Button size="small" danger>删除</Button>
              </Popconfirm>
            </>
          )}
        </>
      )
    }
  ];

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ background: 'linear-gradient(90deg, #667eea 0%, #764ba2 100%)', color: 'white', fontSize: 24, fontWeight: 700, letterSpacing: 1, display: 'flex', alignItems: 'center', boxShadow: '0 2px 8px rgba(102,126,234,0.08)' }}>
        <span role="img" aria-label="admin" style={{ marginRight: 16, fontSize: 32 }}>🛡️</span>
        管理员后台
      </Header>
      <Content style={{ padding: '32px', background: '#f5f6fa' }}>
        <Card style={{ maxWidth: 900, margin: '0 auto', borderRadius: 18, boxShadow: '0 4px 24px rgba(102,126,234,0.08)' }}>
          <Title level={4}>用户管理</Title>
          <Table rowKey="id" columns={columns} dataSource={users} loading={loading} pagination={false} />
        </Card>
      </Content>
    </Layout>
  );
};

export default Admin; 