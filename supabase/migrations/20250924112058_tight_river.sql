/*
  # Create user activities table

  1. New Tables
    - `user_activities`
      - `id` (bigserial, primary key)
      - `user_id` (uuid, references profiles)
      - `activity_type` (text, required)
      - `target_id` (bigint, optional)
      - `target_type` (text, optional)
      - `activity_data` (text, optional for JSON data)
      - `created_at` (timestamp)

  2. Security
    - Enable RLS
    - Add policies for user self-access
*/

-- Create user_activities table
CREATE TABLE IF NOT EXISTS user_activities (
  id bigserial PRIMARY KEY,
  user_id uuid NOT NULL REFERENCES profiles(id),
  activity_type text NOT NULL CHECK (activity_type IN ('view', 'search', 'purchase', 'message', 'wishlist_add', 'wishlist_remove')),
  target_id bigint,
  target_type text CHECK (target_type IN ('listing', 'marketplace', 'user')),
  activity_data text, -- JSON string for additional data
  created_at timestamptz DEFAULT now()
);

-- Enable RLS
ALTER TABLE user_activities ENABLE ROW LEVEL SECURITY;

-- Create policies
CREATE POLICY "Allow users to create their own activities"
  ON user_activities
  FOR INSERT
  TO public
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Allow users to view their own activities"
  ON user_activities
  FOR SELECT
  TO public
  USING (auth.uid() = user_id);

-- Create index for performance
CREATE INDEX IF NOT EXISTS idx_user_activities_user_id_created_at 
  ON user_activities(user_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_user_activities_activity_type 
  ON user_activities(activity_type);