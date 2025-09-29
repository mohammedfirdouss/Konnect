
import { axiosBaseInstance, BASE_API_URL } from '@/lib/axiosBase';
import axios from 'axios';

export const fetchUser = async () => {
  try {
    const res = await axiosBaseInstance.get('/users/me');
    console.log('API Response:', res.data);
    return res.data;
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
};

export const fetchRecommendations = async () => {
  try {
    const res = await axiosBaseInstance.get('/users/me/recommendations');
    console.log('API Response:', res.data);
    return res.data;
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
};
