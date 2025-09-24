/*
  # Create marketplace and listing tables

  1. New Tables
    - `marketplaces`
      - `id` (bigserial, primary key)
      - `name` (text, required)
      - `description` (text, optional)
      - `created_by` (uuid, references profiles)
      - `is_active` (boolean, default true)
      - `created_at` (timestamp)
      - `updated_at` (timestamp)

    - `listings`
      - `id` (bigserial, primary key)
      - `title` (text, required)
      - `description` (text, optional)
      - `price` (real, required)
      - `category` (text, optional)
      - `marketplace_id` (bigint, references marketplaces)
      - `user_id` (uuid, references profiles)
      - `is_active` (boolean, default true)
      - `created_at` (timestamp)
      - `updated_at` (timestamp)

  2. Security
    - Enable RLS on both tables
    - Add appropriate policies for CRUD operations
    - Add timestamp triggers
*/

-- Create marketplaces table
CREATE TABLE IF NOT EXISTS marketplaces (
  id bigserial PRIMARY KEY,
  name text NOT NULL,
  description text,
  created_by uuid NOT NULL REFERENCES profiles(id),
  is_active boolean DEFAULT true,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- Create listings table
CREATE TABLE IF NOT EXISTS listings (
  id bigserial PRIMARY KEY,
  title text NOT NULL,
  description text,
  price real NOT NULL CHECK (price > 0),
  category text,
  marketplace_id bigint NOT NULL REFERENCES marketplaces(id),
  user_id uuid NOT NULL REFERENCES profiles(id),
  is_active boolean DEFAULT true,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- Enable RLS
ALTER TABLE marketplaces ENABLE ROW LEVEL SECURITY;
ALTER TABLE listings ENABLE ROW LEVEL SECURITY;

-- Marketplaces policies
CREATE POLICY "Allow public read access to active marketplaces"
  ON marketplaces
  FOR SELECT
  TO public
  USING (is_active = true);

CREATE POLICY "Allow authenticated users to create marketplaces"
  ON marketplaces
  FOR INSERT
  TO public
  WITH CHECK (auth.role() = 'authenticated');

CREATE POLICY "Allow owners to update their marketplaces"
  ON marketplaces
  FOR UPDATE
  TO public
  USING (auth.uid() = created_by);

-- Listings policies
CREATE POLICY "Allow public read access to active listings"
  ON listings
  FOR SELECT
  TO public
  USING (is_active = true);

CREATE POLICY "Allow authenticated users to create listings"
  ON listings
  FOR INSERT
  TO public
  WITH CHECK (auth.role() = 'authenticated');

CREATE POLICY "Allow owners to update their listings"
  ON listings
  FOR UPDATE
  TO public
  USING (auth.uid() = user_id);

CREATE POLICY "Allow owners to delete their listings"
  ON listings
  FOR DELETE
  TO public
  USING (auth.uid() = user_id);

-- Create timestamp triggers
CREATE TRIGGER set_marketplaces_timestamp
  BEFORE UPDATE ON marketplaces
  FOR EACH ROW
  EXECUTE FUNCTION trigger_set_timestamp();

CREATE TRIGGER set_listings_timestamp
  BEFORE UPDATE ON listings
  FOR EACH ROW
  EXECUTE FUNCTION trigger_set_timestamp();