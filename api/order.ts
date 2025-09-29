import { OrderDto } from "@/interface/orders";
import { axiosBaseInstance } from "@/lib/axiosBase"


export const orderProduct = async (data: OrderDto) => {
  try {
    const res = await axiosBaseInstance.post('/orders', data);
    console.log('API Response:', res);
    return res.data;
  } catch (error: any) {
    console.error('API Error:', error);
    console.error('❌ Error response data:', error?.response?.data);
    throw error;
  }
};