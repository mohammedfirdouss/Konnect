/*
  # Create marketplace requests table

  1. New Tables
    - `marketplace_requests`
      - `id` (bigserial, primary key)
      - `university_name` (text, required)
      - `university_domain` (text, required)
      - `contact_email` (text, required)
      - `description` (text, optional)
      - `status` (text, default 'pending')
      - `requested_by` (uuid, references profiles)
      - `smart_contract_tx_hash` (text, optional)
      - `created_at` (timestamp)
      - `updated_at` (timestamp)

  2. Security
    - Enable RLS
    - Add policies for user and admin access
    - Add admin function for checking admin role

  3. Functions
    - `is_admin()` function to check if current user is admin
*/

-- Create admin check function
CREATE OR REPLACE FUNCTION is_admin()
RETURNS boolean AS $$
BEGIN
  RETURN EXISTS (
    SELECT 1 FROM profiles 
    WHERE id = auth.uid() AND role = 'admin'
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create marketplace_requests table
CREATE TABLE IF NOT EXISTS marketplace_requests (
  id bigserial PRIMARY KEY,
  university_name text NOT NULL,
  university_domain text NOT NULL,
  contact_email text NOT NULL,
  description text,
  status text DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected')),
  requested_by uuid NOT NULL REFERENCES profiles(id),
  smart_contract_tx_hash text,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- Enable RLS
ALTER TABLE marketplace_requests ENABLE ROW LEVEL SECURITY;

-- Create policies
CREATE POLICY "Allow authenticated users to create marketplace requests"
  ON marketplace_requests
  FOR INSERT
  TO public
  WITH CHECK (auth.role() = 'authenticated');

CREATE POLICY "Allow users to view their own marketplace requests"
  ON marketplace_requests
  FOR SELECT
  TO public
  USING (auth.uid() = requested_by);

CREATE POLICY "Allow admins to view all marketplace requests"
  ON marketplace_requests
  FOR SELECT
  TO public
  USING (is_admin());

CREATE POLICY "Allow admins to update marketplace requests"
  ON marketplace_requests
  FOR UPDATE
  TO public
  USING (is_admin());

-- Create timestamp trigger
CREATE TRIGGER set_marketplace_requests_timestamp
  BEFORE UPDATE ON marketplace_requests
  FOR EACH ROW
  EXECUTE FUNCTION trigger_set_timestamp();