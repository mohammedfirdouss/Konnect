import { STORAGE_KEYS } from '@/constants/storageKeys';
import { axiosBaseInstance } from '@/lib/axiosBase';
import { StorageService } from '@/services/StorageService';


export const createListing = async (values: {
  title: string;
  description: string;
  price: number;
  category: string;
  marketplace_id: number;
}) => {
  try {
    console.log('🔧 Creating listing with data:', values);
    const res = await axiosBaseInstance.post('/listings', values);
    console.log('✅ Listing created:', res.data);
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

export const getListings = async (values: {
  skip: number;
  limit: number;
  category: string;
}) => {
  try {

    const marketplaceId = await StorageService.getItem(STORAGE_KEYS.MARKETPLACE);
    
    console.log('🔧 Get listings:', values);
    const res = await axiosBaseInstance.get('/listings', {
      params: {
        skip: values.skip,
        limit: values.limit,
        marketplace_id: Number(marketplaceId),
        category: values.category,
      },
    });
    console.log('✅ Get listings:', res.data);
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

export const getSingleListing = async (
 listingId: string | number
) => {
  try {
    const res = await axiosBaseInstance.get(`/listings/${listingId}`); 
    console.log('✅ Single Listing:', res.data);
    return res.data;
  } catch (error: any) {
    console.error('❌ Single Listing Error:', error);
    if (error.response) {
      console.error('❌ Error response data:', error.response.data);
      console.error('❌ Error response status:', error.response.status);
    }
    throw error;
  }
};

export const getListingImages = async (
 listingId: string | number
) => {
  try {
    const res = await axiosBaseInstance.get(`/listings/${listingId}/images`); 
    console.log('✅ Listing Images:', res.data);
    return res.data;
  } catch (error: any) {
    console.error('❌ Listing Image Error:', error);
    if (error.response) {
      console.error('❌ Error response data:', error.response.data);
      console.error('❌ Error response status:', error.response.status);
    }
    throw error;
  }
};
