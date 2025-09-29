import { axiosBaseInstance, BASE_API_URL } from '@/lib/axiosBase';
import axios from 'axios';

// Register user API call
export const registerRequest = async (values: any) => {
  try {
    console.log('🔧 Sending registration data:', values);
    const res = await axios.post(`${BASE_API_URL}/auth/register`, values);
    console.log('✅ API Response:', res.data);
    return res.data;
  } catch (error: any) {
    console.error('❌ API Error:', error);
    if (error.response) {
      console.error('❌ Error response data:', error.response.data);
      console.error('❌ Error response status:', error.response.status);
    }
    throw error;
  }
};

// Login user API call
export const loginRequest = async (values: any) => {
  try {
    console.log('🔧 Sending login data:', values);
    const res = await axios.post(`${BASE_API_URL}/auth/token`, values, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    console.log('✅ API Response:', res.data);
    return res.data;
  } catch (error: any) {
    // console.log('✅ API Response:', res.data);
   if (error.response) {
     console.error('❌ Error response data:', error.response.data);
     console.error('❌ Error response status:', error.response.status);
   }


    throw error;
  }
};

// Fetch user profile API call
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
