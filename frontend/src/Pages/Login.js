// src/pages/Login.js
import { useState } from 'react';
import AuthForm from '../components/AuthForm';
import { useNavigate } from 'react-router-dom';
import { login } from '../api/auth';

const Login = () => {
  const [formData, setFormData] = useState({ email: '', password: '' });
  const navigate = useNavigate();

  const handleChange = (e) =>
    setFormData({ ...formData, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    const res = await login(formData);
    if (res.success) {
      localStorage.setItem('token', res.token);
      navigate('/dashboard');
    } else {
      alert(res.message);
    }
  };

  return (
    <AuthForm
      isLogin={true}
      formData={formData}
      handleChange={handleChange}
      handleSubmit={handleSubmit}
    />
  );
};

export default Login;
