import { OrderDto } from "@/interface/orders";
import { axiosBaseInstance } from "@/lib/axiosBase"


export const orderProduct = async (data: OrderDto) => {
      // Replace with real API call
      
// console.log('API Request Values:', values);
      try {
          const res = axiosBaseInstance.post("/orders", data);
      console.log('API Response:', res);
   }catch (error) {
      console.error('API Error:', error);
   }
      // Simulate network delay
    // await new Promise((resolve) => setTimeout(resolve, 1000));
    //   return { success: true };
      

  };