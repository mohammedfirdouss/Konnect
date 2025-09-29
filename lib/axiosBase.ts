import { STORAGE_KEYS } from '@/constants/storageKeys';
import { StorageService } from '@/services/StorageService';
import axios from 'axios';
import { logOut } from './helpers';
import Constants from 'expo-constants';

// Get BASE_API_URL from environment variables
export const BASE_API_URL =
  process.env.BASE_API_URL ||
  Constants.expoConfig?.extra?.BASE_API_URL ||
  'https://konnect-h72p.onrender.com';

console.log('🔧 Axios Base URL:', BASE_API_URL);

const axiosBaseInstance = axios.create({
  baseURL: BASE_API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

axiosBaseInstance.interceptors.request.use(
  async (config) => {
    const token = await StorageService.getItem(STORAGE_KEYS.ACCESS_TOKEN);

    // const dispatch = useDispatch();
    // const token = getToken();
    // console.log(token);
    if (token) {
      // if (isTokenExpired(token)) {
      //   // Token is expired, clear it and redirect to login
      //   // const currentRoute = window.location.pathname;
      //   logOut();
      //   return Promise.reject(new Error("Token expired"));
      // }

      config.headers.Authorization = `Bearer ${token}`;
      config.headers['Content-Type'] = 'application/json';
    }
    return config;
  },
  (error) => {
    const currentRoute = window.location.pathname;

    if (currentRoute !== '/login') {
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

axiosBaseInstance.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response) {
      const currentRoute = window.location.pathname;
      if (error.response.status === 401) {
        // logOut();
        // window.location.reload()
      }
      // if (error.response.status === 401 || error.response.status === 403) {
      //   if (currentRoute !== "/login") {
      //     window.location.href = "/login";
      //   }
      // }
    }

    return Promise.reject(error);
  }
);

export { axiosBaseInstance };
