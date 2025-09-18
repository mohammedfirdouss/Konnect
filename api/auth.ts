import { axiosBaseInstance } from "@/lib/axiosBase";
import axios from "axios";

  // API request mock
  export const registerRequest = async (values: any) => {
      // Replace with real API call
      
// console.log('API Request Values:', values);
      try {
          const res = axios.post('/auth/register', values);
      console.log('API Response:', res);
   }catch (error) {
      console.error('API Error:', error);
   }
      // Simulate network delay
    // await new Promise((resolve) => setTimeout(resolve, 1000));
    //   return { success: true };
      


  };


    // API request mock
  export const loginRequest = async (values: any) => {
      // Replace with real API call
      
// console.log('API Request Values:', values);
      try {
          const res = axios.post('/auth/login', values);
      console.log('API Response:', res);
   }catch (error) {
      console.error('API Error:', error);
   }
      // Simulate network delay
    // await new Promise((resolve) => setTimeout(resolve, 1000));
    //   return { success: true };
      


  };

  export const fetchUser = async (values: any) => {
      // Replace with real API call
      
// console.log('API Request Values:', values);
      try {
          const res = axiosBaseInstance.post('/users/me', values);
      console.log('API Response:', res);
   }catch (error) {
      console.error('API Error:', error);
   }
      // Simulate network delay
    // await new Promise((resolve) => setTimeout(resolve, 1000));
    //   return { success: true };
      


  };


  