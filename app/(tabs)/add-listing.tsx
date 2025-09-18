import React, { useState } from 'react';
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

export default function AddListingScreen() {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [price, setPrice] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [images, setImages] = useState<string[]>([]);
  const [errors, setErrors] = useState<{[key: string]: string}>({});

  const validateForm = () => {
    const newErrors: {[key: string]: string} = {};

    if (!title.trim()) newErrors.title = 'Title is required';
    if (!description.trim()) newErrors.description = 'Description is required';
    if (!price.trim()) newErrors.price = 'Price is required';
    else if (isNaN(Number(price)) || Number(price) <= 0) newErrors.price = 'Invalid price';
    if (!selectedCategory) newErrors.category = 'Category is required';

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

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

  const handleSubmit = () => {
    if (validateForm()) {
      Alert.alert(
        'Success',
        'Listing created successfully!',
        [{ text: 'OK', onPress: () => router.back() }]
      );
    }
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
            value={title}
            onChangeText={setTitle}
            error={errors.title}
          />

          <Input
            label="Description"
            placeholder="Describe your item or service..."
            value={description}
            onChangeText={setDescription}
            multiline
            numberOfLines={4}
            style={styles.textArea}
            error={errors.description}
          />

          <Input
            label="Price (USD)"
            placeholder="0.00"
            value={price}
            onChangeText={setPrice}
            keyboardType="numeric"
            error={errors.price}
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
                  selectedCategory === category.name && styles.categoryOptionSelected,
                ]}
                onPress={() => setSelectedCategory(category.name)}
              >
                <Text style={styles.categoryIcon}>{category.icon}</Text>
                <Text style={[
                  styles.categoryName,
                  selectedCategory === category.name && styles.categoryNameSelected,
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