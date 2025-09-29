import * as Yup from 'yup';

export const registerSchema = Yup.object({
  email: Yup.string()
    .email('Invalid email format')
    .required('Email is required'),
  password: Yup.string()
    .min(6, 'Password must be at least 6 characters')
    .required('Password is required'),
  fullName: Yup.string().required('Name is required'),
  username: Yup.string().required('Username is required'),
  confirmPassword: Yup.string()
    .required('Please confirm your password')
    .oneOf([Yup.ref('password')], 'Passwords do not match'),
});

export const loginSchema = Yup.object({
  username: Yup.string().required('Username is required'),
  password: Yup.string().required('Password is required'),
});

export const marketplaceRequestSchema = Yup.object({
  universityName: Yup.string()
    .min(2, 'University name must be at least 2 characters')
    .required('University name is required'),
  campusLocation: Yup.string()
    .min(2, 'Campus name must be at least 2 characters')
    .required('Campus name is required'),
  adminEmail: Yup.string()
    .email('Invalid email format')
    .required('Admin email is required'),
  contactEmail: Yup.string()
    .email('Invalid email format')
    .required('Contact email is required'),
  universityDomain: Yup.string()
    .url('Invalid URL format')
    .required('University domain is required'),
});

export const listingSchema = Yup.object({
  title: Yup.string()
    .min(3, 'Title must be at least 3 characters')
    .required('Title is required'),
  description: Yup.string()
    .min(10, 'Description must be at least 10 characters')
    .required('Description is required'),
  price: Yup.number()
    .positive('Price must be greater than 0')
    .required('Price is required'),
  category: Yup.string()
    .required('Category is required'),
});