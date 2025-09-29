import React, { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { useFormik } from 'formik';
import { 
  View, 
  Text, 
  StyleSheet, 
  SafeAreaView, 
  ScrollView,
  TouchableOpacity,
  Image,
  Alert 
} from 'react-native';
import { theme } from '@/constants/Colors';
import { categories } from '@/constants/MockData';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Camera, Image as ImageIcon, X } from 'lucide-react-native';
import { router } from 'expo-router';
import { createListing } from '@/api/listings';
import { listingSchema } from '@/lib/schema';
import Toast from 'react-native-toast-message';
import { StorageService } from '@/services/StorageService';
import { STORAGE_KEYS } from '@/constants/storageKeys';

export default function AddListingScreen() {
  const [images, setImages] = useState<string[]>([]);

  const { mutate: mutateCreateListing, isPending: isCreating } = useMutation({
    mutationFn: createListing,
    onSuccess: async (res) => {
      Toast.show({
        type: 'success',
        text1: 'Listing created successfully!',
        text2: 'Your item is now available in the marketplace.',
      });
      router.back();
    },
    onError: (err: any) => {
      Toast.show({
        type: 'error',
        text1:
          typeof err?.response?.data?.detail === 'string'
            ? err?.response?.data?.detail
            : 'Error creating listing',
        text2: 'Please try again later.',
      });
    },
  });

  const { handleChange, values, errors, handleBlur, handleSubmit, setFieldValue } =
    useFormik({
      initialValues: {
        title: 'Book 1',
        description: 'something like a book',
        price: '10',
        category: 'Books',
      },
      validationSchema: listingSchema,
      validateOnBlur: true,
      onSubmit: async (values) => {
        // Get marketplace_id from storage
        const marketplaceId = await StorageService.getItem(STORAGE_KEYS.MARKETPLACE);
        
        mutateCreateListing({
          title: values.title,
          description: values.description,
          price: Number(values.price),
          category: values.category,
          marketplace_id: marketplaceId ? Number(marketplaceId) : 1,
        });
      },
    });


  const handleAddImage = () => {
    // Mock image picker
    const mockImages = [
      'https://images.pexels.com/photos/256520/pexels-photo-256520.jpeg?auto=compress&cs=tinysrgb&w=400',
      'https://images.pexels.com/photos/18105/pexels-photo.jpg?auto=compress&cs=tinysrgb&w=400',
      'https://images.pexels.com/photos/230325/pexels-photo-230325.jpeg?auto=compress&cs=tinysrgb&w=400',
    ];
    
    if (images.length < 5) {
      const randomImage = mockImages[Math.floor(Math.random() * mockImages.length)];
      setImages(prev => [...prev, randomImage]);
    }
  };

  const removeImage = (index: number) => {
    setImages(prev => prev.filter((_, i) => i !== index));
  };


  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Add New Listing</Text>
      </View>

      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        <Card style={styles.formCard}>
          <Input
            label="Title"
            placeholder="What are you selling?"
            value={values.title}
            onChangeText={handleChange('title')}
            error={errors.title}
            onBlur={handleBlur('title')}
          />

          <Input
            label="Description"
            placeholder="Describe your item or service..."
            value={values.description}
            onChangeText={handleChange('description')}
            multiline
            numberOfLines={4}
            style={styles.textArea}
            error={errors.description}
            onBlur={handleBlur('description')}
          />

          <Input
            label="Price (USD)"
            placeholder="0.00"
            value={values.price}
            onChangeText={handleChange('price')}
            keyboardType="numeric"
            error={errors.price}
            onBlur={handleBlur('price')}
          />
        </Card>

        <Card style={styles.categoryCard}>
          <Text style={styles.sectionTitle}>Category</Text>
          {errors.category && <Text style={styles.errorText}>{errors.category}</Text>}
          <View style={styles.categoriesGrid}>
            {categories.map((category) => (
              <TouchableOpacity
                key={category.id}
                style={[
                  styles.categoryOption,
                  values.category === category.name && styles.categoryOptionSelected,
                ]}
                onPress={() => setFieldValue('category', category.name)}
              >
                <Text style={styles.categoryIcon}>{category.icon}</Text>
                <Text style={[
                  styles.categoryName,
                  values.category === category.name && styles.categoryNameSelected,
                ]}>
                  {category.name}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </Card>

        <Card style={styles.imagesCard}>
          <Text style={styles.sectionTitle}>Photos ({images.length}/5)</Text>
          <Text style={styles.sectionSubtitle}>Add photos to showcase your item</Text>
          
          <View style={styles.imagesGrid}>
            {images.map((image, index) => (
              <View key={index} style={styles.imageContainer}>
                <Image source={{ uri: image }} style={styles.uploadedImage} />
                <TouchableOpacity 
                  style={styles.removeImageButton}
                  onPress={() => removeImage(index)}
                >
                  <X color={theme.text} size={16} />
                </TouchableOpacity>
              </View>
            ))}
            
            {images.length < 5 && (
              <TouchableOpacity 
                style={styles.addImageButton}
                onPress={handleAddImage}
              >
                <Camera color={theme.textMuted} size={32} />
                <Text style={styles.addImageText}>Add Photo</Text>
              </TouchableOpacity>
            )}
          </View>
        </Card>

        <View style={styles.footer}>
          <Button
            title="Create Listing"
            onPress={handleSubmit}
            style={styles.submitButton}
            isLoading={isCreating}
          />
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.background,
    paddingTop: 50,
  },
  header: {
    padding: 20,
    paddingBottom: 10,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: theme.text,
  },
  content: {
    flex: 1,
    paddingHorizontal: 20,
  },
  formCard: {
    marginBottom: 20,
  },
  textArea: {
    height: 100,
    textAlignVertical: 'top',
  },
  categoryCard: {
    marginBottom: 20,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: theme.text,
    marginBottom: 8,
  },
  sectionSubtitle: {
    fontSize: 14,
    color: theme.textMuted,
    marginBottom: 16,
  },
  errorText: {
    fontSize: 12,
    color: theme.error,
    marginBottom: 8,
  },
  categoriesGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
  },
  categoryOption: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: theme.background,
    borderRadius: 20,
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderWidth: 1,
    borderColor: theme.border,
  },
  categoryOptionSelected: {
    backgroundColor: theme.primary,
    borderColor: theme.primary,
  },
  categoryIcon: {
    fontSize: 16,
    marginRight: 6,
  },
  categoryName: {
    fontSize: 14,
    color: theme.text,
  },
  categoryNameSelected: {
    color: theme.text,
    fontWeight: '600',
  },
  imagesCard: {
    marginBottom: 20,
  },
  imagesGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
  },
  imageContainer: {
    position: 'relative',
  },
  uploadedImage: {
    width: 80,
    height: 80,
    borderRadius: 8,
  },
  removeImageButton: {
    position: 'absolute',
    top: -8,
    right: -8,
    backgroundColor: theme.danger,
    borderRadius: 12,
    width: 24,
    height: 24,
    alignItems: 'center',
    justifyContent: 'center',
  },
  addImageButton: {
    width: 80,
    height: 80,
    borderRadius: 8,
    borderWidth: 2,
    borderColor: theme.border,
    borderStyle: 'dashed',
    alignItems: 'center',
    justifyContent: 'center',
  },
  addImageText: {
    fontSize: 10,
    color: theme.textMuted,
    marginTop: 4,
  },
  footer: {
    paddingBottom: 40,
  },
  submitButton: {
    width: '100%',
  },
});