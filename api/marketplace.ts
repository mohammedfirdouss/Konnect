import { STORAGE_KEYS } from '@/constants/storageKeys';
import { axiosBaseInstance, BASE_API_URL } from '@/lib/axiosBase';
import { getToken } from '@/lib/helpers';
import { StorageService } from '@/services/StorageService';
import axios from 'axios';

// API request mock
export const getAllMarketplaces = async () => {
  try {
    const res = await axios.get(`${BASE_API_URL}/marketplaces`);
    return res.data;
  } catch (error) {
    console.error('API Error:', error);
  }
};

export const getSingleMarketplace = async (marketplaceId?: string) => {
  try {
    const id =
      marketplaceId || (await StorageService.getItem(STORAGE_KEYS.MARKETPLACE));

    console.log('marketplace ID:', id);

    const res = await axios.get(`${BASE_API_URL}/marketplaces/${id}`);
    console.log('API Response:', res);
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
export const getMarketplaceProducts = async () => {
  try {
    const marketplaceId = await StorageService.getItem(
      STORAGE_KEYS.MARKETPLACE
    );
    const res = await axiosBaseInstance.get(
      `/marketplaces/${marketplaceId}/products`,
      {
        params: { limit: 100 },
      }
    );
    console.log('API Response:', res);

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

export const requestMarketplace = async (values: any) => {
  try {
    console.log('🔧 Sending marketplace request data:', values);
    const res = await axiosBaseInstance.post(`/marketplaces/request`, values);
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
