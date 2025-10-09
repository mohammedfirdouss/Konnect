/*
  # Create profiles table for user management

  1. New Tables
    - `profiles`
      - `id` (uuid, primary key, references auth.users)
      - `username` (text, unique)
      - `full_name` (text, optional)
      - `role` (text, default 'buyer')
      - `is_verified_seller` (boolean, default false)
      - `verification_nft_mint` (text, optional)
      - `created_at` (timestamp)
      - `updated_at` (timestamp)

  2. Security
    - Enable RLS on `profiles` table
    - Add policies for public read access and user self-update
    - Add trigger for automatic profile creation on user signup

  3. Functions
    - `handle_new_user()` trigger function for automatic profile creation
    - `trigger_set_timestamp()` function for updated_at timestamps
*/

-- Create trigger function for setting timestamps
CREATE OR REPLACE FUNCTION trigger_set_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create function to handle new user registration
CREATE OR REPLACE FUNCTION handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.profiles (id, username, full_name, role)
  VALUES (
    NEW.id,
    COALESCE(NEW.raw_user_meta_data->>'username', NEW.email),
    NEW.raw_user_meta_data->>'full_name',
    'buyer'
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create profiles table
CREATE TABLE IF NOT EXISTS profiles (
  id uuid PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  username text UNIQUE NOT NULL,
  full_name text,
  role text DEFAULT 'buyer' CHECK (role IN ('buyer', 'seller', 'admin')),
  is_verified_seller boolean DEFAULT false,
  verification_nft_mint text,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- Enable RLS
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

-- Create RLS policies
CREATE POLICY "Allow public read access to profiles"
  ON profiles
  FOR SELECT
  TO public
  USING (true);

CREATE POLICY "Allow users to update their own profile"
  ON profiles
  FOR UPDATE
  TO public
  USING (auth.uid() = id);

-- Create trigger for updated_at
CREATE TRIGGER set_profiles_timestamp
  BEFORE UPDATE ON profiles
  FOR EACH ROW
  EXECUTE FUNCTION trigger_set_timestamp();

-- Create trigger for new user signup
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW
  EXECUTE FUNCTION handle_new_user();