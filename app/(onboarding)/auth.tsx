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

export default function AuthScreen() {
  const [isLogin, setIsLogin] = useState(true);

  // Validation schema

  const { mutate: mutateLogin, isPending: loginPending } = useMutation({
    mutationFn: loginRequest,
    onSuccess: () => {
      router.replace('/(tabs)');
    },
  });

  const { mutate: mutateRegister, isPending: isRegistering } = useMutation({
    mutationFn: registerRequest,
    onSuccess: () => {
      router.replace('/(tabs)');
    },
  });

  const { handleChange, values, errors, handleBlur, handleSubmit, resetForm } =
    useFormik({
      initialValues: {
        email: '',
        password: '',
        name: '',
        confirmPassword: '',
      },
      validationSchema: isLogin ? loginSchema : registerSchema,
      validateOnChange: false,
      validateOnBlur: true,
      onSubmit: (values) => {
        if (isLogin) {
          mutateLogin({ email: values.email, password: values.password });
          return;
        }
        mutateRegister(values);
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
            <Input
              label="Full Name"
              placeholder="Enter your name"
              value={values.name}
              onChangeText={handleChange('name')}
              error={errors.name}
              onBlur={handleBlur('name')}
            />
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