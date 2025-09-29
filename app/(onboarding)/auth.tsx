import React, { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import {
  View,
  Text,
  StyleSheet,
  SafeAreaView,
  TouchableOpacity,
} from 'react-native';
import { theme } from '@/constants/Colors';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { router } from 'expo-router';
import KeyboardView from '@/components/ui/KeyboardView';
import { loginRequest, registerRequest } from '@/api/auth';
import { loginSchema, registerSchema } from '@/lib/schema';
import Toast from 'react-native-toast-message';
import { StorageService } from '@/services/StorageService';
import { STORAGE_KEYS } from '@/constants/storageKeys';

export default function AuthScreen() {
  const [isLogin, setIsLogin] = useState(true);

  // Validation schema

  const { mutate: mutateLogin, isPending: loginPending } = useMutation({
    mutationFn: loginRequest,
    onSuccess: async (res) => {
      // Toast.show({
      //   type: 'success',
      //   text1: 'Login successful',
      // });

      StorageService.setItem(STORAGE_KEYS.ACCESS_TOKEN, res?.access_token);

      const marketplaceId = await StorageService.getItem(
        STORAGE_KEYS.MARKETPLACE
      );

      const user = await StorageService.getItem(STORAGE_KEYS.ROLE);
      if (user === 'buyer') {
        router.replace('/(tabs)');
        return;
      }

      router.replace('/(tabs)/dashboard');

      // if (marketplaceId) {
      //   router.push('/(onboarding)/university-selection');
      // } else {
      //   router.replace('/(tabs)');
      // }
    },
    onError: (err: any) => {
      // console.log(err?.response?.data?.detail);
      Toast.show({
        type: 'error',
        text1:
          typeof err?.response?.data?.detail === 'string'
            ? err?.response?.data?.detail
            : 'Error logining user',
        text2: '',
      });
    },
  });

  const { mutate: mutateRegister, isPending: isRegistering } = useMutation({
    mutationFn: registerRequest,
    onSuccess: (res) => {
      console.log('Auth', res);

      Toast.show({
        type: 'success',
        text1: 'Registration successful',
      });

      setIsLogin(true);
      // router.replace('/(tabs)');
    },
    onError: (err: any) => {
      Toast.show({
        type: 'error',
        text1:
          typeof err?.response?.data?.detail === 'string'
            ? err?.response?.data?.detail
            : 'Error registering user',
      });
    },
  });

  const { handleChange, values, errors, handleBlur, handleSubmit, resetForm } =
    useFormik({
      initialValues: {
        email: '',
        password: '',
        username: '',
        fullName: '',
        confirmPassword: '',
      },
      validationSchema: isLogin ? loginSchema : registerSchema,
      validateOnBlur: true,
      onSubmit: (values) => {
        // const user = await StorageService.getItem(STORAGE_KEYS.ROLE);
        // if (user === 'buyer') {
        //   router.replace('/(tabs)');
        // } else {
        //   router.replace('/(tabs)/dashboard');
        // }
        // console.log('values', values);

        if (isLogin) {
          mutateLogin({ email: values.email, password: values.password });
          return;
        }

        mutateRegister({
          username: values.username,
          full_name: values.fullName,
          email: values.email,
          password: values.password,
        });
      },
    });

  return (
    <SafeAreaView style={styles.container}>
      <KeyboardView style={styles.content}>
        <View style={styles.header}>
          <Text style={styles.title}>
            {isLogin ? 'Welcome Back' : 'Create Account'}
          </Text>
          <Text style={styles.subtitle}>
            {isLogin
              ? 'Sign in to continue to Konnect'
              : 'Join your campus marketplace today'}
          </Text>
        </View>

        <View style={styles.form}>
          {!isLogin && (
            <>
              <Input
                label="Username"
                placeholder="Enter your username"
                value={values.username}
                onChangeText={handleChange('username')}
                error={errors.username}
                onBlur={handleBlur('username')}
              />
              <Input
                label="Full Name"
                placeholder="Enter your name"
                value={values.fullName}
                onChangeText={handleChange('fullName')}
                error={errors.fullName}
                onBlur={handleBlur('fullName')}
              />
            </>
          )}

          <Input
            label="Email"
            placeholder="Enter your email"
            value={values.email}
            onChangeText={handleChange('email')}
            keyboardType="email-address"
            autoCapitalize="none"
            error={errors.email}
            onBlur={handleBlur('email')}
          />

          <Input
            label="Password"
            placeholder="Enter your password"
            value={values.password}
            onChangeText={handleChange('password')}
            secureTextEntry
            error={errors.password}
            onBlur={handleBlur('password')}
          />

          {!isLogin && (
            <Input
              label="Confirm Password"
              placeholder="Confirm your password"
              value={values.confirmPassword}
              onChangeText={handleChange('confirmPassword')}
              secureTextEntry
              error={errors.confirmPassword}
              onBlur={handleBlur('confirmPassword')}
            />
          )}

          <Button
            title={isLogin ? 'Sign In' : 'Create Account'}
            onPress={handleSubmit}
            style={styles.submitButton}
            isLoading={isRegistering || loginPending}
          />

          <TouchableOpacity
            style={styles.switchButton}
            onPress={() => {
              setIsLogin(!isLogin);
              resetForm();
            }}
          >
            <Text style={styles.switchText}>
              {isLogin
                ? "Don't have an account? Sign up"
                : 'Already have an account? Sign in'}
            </Text>
          </TouchableOpacity>
        </View>
      </KeyboardView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.background,
    paddingTop: 50,
  },
  content: {
    flex: 1,
    paddingHorizontal: 20,
    paddingTop: 60,
  },
  header: {
    marginBottom: 40,
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: theme.text,
    textAlign: 'center',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: theme.textMuted,
    textAlign: 'center',
  },
  form: {
    flex: 1,
  },
  submitButton: {
    marginTop: 20,
    marginBottom: 20,
  },
  switchButton: {
    alignItems: 'center',
    paddingVertical: 16,
  },
  switchText: {
    fontSize: 14,
    color: theme.primary,
  },
});