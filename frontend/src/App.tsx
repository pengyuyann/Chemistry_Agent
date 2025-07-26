import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Login from './pages/Login';
import Register from './pages/Register';
import Chat from './pages/Chat';
import Profile from './pages/Profile';
import Admin from './pages/Admin';
import VectorManagement from './pages/VectorManagement';
import FeedbackManagement from './pages/FeedbackManagement';
import ChemicalDemo from './pages/ChemicalDemo'; // 根据实际文件路径调整

import { Spin } from 'antd';

const PrivateRoute: React.FC<{ children: React.ReactNode, adminOnly?: boolean }> = ({ children, adminOnly }) => {
  const { user, loading, isAdmin } = useAuth();
  if (loading) return <div style={{textAlign:'center',marginTop:100}}><Spin size="large" /></div>;
  if (!user) return <Navigate to="/login" replace />;
  if (adminOnly && !isAdmin) return <Navigate to="/" replace />;
  return <>{children}</>;
};

const App: React.FC = () => (
  <AuthProvider>
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/profile" element={<PrivateRoute><Profile /></PrivateRoute>} />
        <Route path="/admin" element={<PrivateRoute adminOnly><Admin /></PrivateRoute>} />
        <Route path="/vector" element={<PrivateRoute adminOnly><VectorManagement /></PrivateRoute>} />
        <Route path="/feedback" element={<PrivateRoute adminOnly><FeedbackManagement /></PrivateRoute>} />
        <Route path="/" element={<PrivateRoute><Chat /></PrivateRoute>} />
        <Route path="*" element={<Navigate to="/" />} />
        <Route path="/demo" element={<ChemicalDemo />} />

      </Routes>
    </BrowserRouter>
  </AuthProvider>
);

export default App; 