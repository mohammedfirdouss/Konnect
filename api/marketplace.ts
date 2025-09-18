import { axiosBaseInstance } from "@/lib/axiosBase";
import axios from "axios";

  // API request mock
  export const getAllMarketplaces = async () => {
      // Replace with real API call
      
// console.log('API Request Values:', values);
      try {
          const res = axios.get('/marketplaces');
      console.log('API Response:', res);
   }catch (error) {
      console.error('API Error:', error);
   }
      // Simulate network delay
    // await new Promise((resolve) => setTimeout(resolve, 1000));
    //   return { success: true };
    
  };

export const getMarketplaceProducts = async (marketplaceId: string, limit:number) => {
      // Replace with real API call
      
// console.log('API Request Values:', values);
      try {
          const res = axiosBaseInstance.get(`/marketplaces/${marketplaceId}/products`, {
              params: { limit }
          });
      console.log('API Response:', res);
   }catch (error) {
      console.error('API Error:', error);
   }
      // Simulate network delay
    // await new Promise((resolve) => setTimeout(resolve, 1000));
    //   return { success: true };
      

  };



