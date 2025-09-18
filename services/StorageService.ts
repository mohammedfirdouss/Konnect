import AsyncStorage from '@react-native-async-storage/async-storage';
import { STORAGE_KEYS } from '../constants/storageKeys';

export class StorageService {
  static async setItem(key: string, value: any): Promise<void> {
    try {
      const jsonValue = JSON.stringify(value);
      await AsyncStorage.setItem(key, jsonValue);
    } catch (e) {
      // Handle error
      console.error('AsyncStorage setItem error:', e);
      throw e;
    }
  }

  static async getItem<T = any>(key: string): Promise<T | null> {
    try {
      const jsonValue = await AsyncStorage.getItem(key);
      return jsonValue != null ? JSON.parse(jsonValue) as T : null;
    } catch (e) {
      // Handle error
      console.error('AsyncStorage getItem error:', e);
      return null;
    }
  }

  static async removeItem(key: string): Promise<void> {
    try {
      await AsyncStorage.removeItem(key);
    } catch (e) {
      // Handle error
      console.error('AsyncStorage removeItem error:', e);
      throw e;
    }
  }

  static async clear(): Promise<void> {
    try {
      await AsyncStorage.clear();
    } catch (e) {
      // Handle error
      console.error('AsyncStorage clear error:', e);
      throw e;
    }
  }
}


// export const storageService = new StorageService()

// Example usage:

// Set item
// await StorageService.setItem(STORAGE_KEYS.USER, userData);

// Get item
// const user = await StorageService.getItem(STORAGE_KEYS.USER);
