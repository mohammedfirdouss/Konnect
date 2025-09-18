import { STORAGE_KEYS } from "@/constants/storageKeys";
import { StorageService } from "@/services/StorageService";
import axios from "axios";
import { logOut } from "./helpers";


export const baseURL = process.env.NEXT_PUBLIC_BASE_API_URL;

// Debug logging to check the base URL
console.log("🔧 Axios Base URL:", baseURL);

const axiosBaseInstance = axios.create({
  baseURL: baseURL,
  headers: {
    "Content-Type": "application/json",
  },
});

axiosBaseInstance.interceptors.request.use(
  async (config) => {
const token = await StorageService.getItem(STORAGE_KEYS.TOKEN);

    // const dispatch = useDispatch();
    // const token = getToken();

  if (token) {
    // if (isTokenExpired(token)) {
    //   // Token is expired, clear it and redirect to login
    //   // const currentRoute = window.location.pathname;
    //   logOut();
    //   return Promise.reject(new Error("Token expired"));
    // }

    config.headers.Authorization = `Bearer ${token}`;
  }
    return config;
  },
  (error) => {
    const currentRoute = window.location.pathname;

    if (currentRoute !== "/login") {
      window.location.href = "/login";
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
      if (error.response.status === 401 ) {
        logOut();
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
