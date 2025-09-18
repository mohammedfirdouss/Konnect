import { StorageService } from "@/services/StorageService";
import { router } from 'expo-router';

export const logOut = () => {
    StorageService.clear();
    router.replace('/auth');

}