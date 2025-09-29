import { STORAGE_KEYS } from '@/constants/storageKeys';
import { StorageService } from '@/services/StorageService';
import { router } from 'expo-router';

export const logOut = () => {
  StorageService.clear();
  router.replace('/auth');
};

export const getToken = async () => {
  const token = await StorageService.getItem(STORAGE_KEYS.ACCESS_TOKEN);
  return token;
};

export function ellipsify(str = '', len = 4) {
  if (str.length > 30) {
    return (
      str.substring(0, len) + '..' + str.substring(str.length - len, str.length)
    );
  }
  return str;
}
