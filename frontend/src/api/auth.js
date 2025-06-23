// src/api/auth.js
import axios from 'axios';

const API = 'http://localhost:5000'; // Flask backend

export const signup = async (data) => {
  try {
    const res = await axios.post(`${API}/signup`, data);
    return { success: true, data: res.data };
  } catch (err) {
    return { success: false, message: err.response?.data?.message || 'Signup failed' };
  }
};

export const login = async (data) => {
  try {
    const res = await axios.post(`${API}/login`, data);
    return { success: true, token: res.data.token };
  } catch (err) {
    return { success: false, message: err.response?.data?.message || 'Login failed' };
  }
};
