import * as Yup from 'yup';

export const registerSchema = Yup.object({
    email: Yup.string()
      .email('Invalid email format')
      .required('Email is required'),
    password: Yup.string()
      .min(6, 'Password must be at least 6 characters')
      .required('Password is required'),
    name: Yup.string().required('Name is required'),
    confirmPassword: Yup.string()
          .required('Please confirm your password')
          .oneOf([Yup.ref('password')], 'Passwords do not match'),
});
  
export const loginSchema = Yup.object({
    email: Yup.string()
      .email('Invalid email format')
      .required('Email is required'),
    password: Yup.string()
      .required('Password is required'),
  });