
import { axiosBaseInstance, } from '@/lib/axiosBase';


export const fetchAIRecommendations = async () => {
  try {
    const res = await axiosBaseInstance.get('/ai/recommendations');
    console.log('API Response:', res.data);
    return res.data;
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
};



