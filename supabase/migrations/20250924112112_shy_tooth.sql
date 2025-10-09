/*
  # Create messages table for user communication

  1. New Tables
    - `messages`
      - `id` (bigserial, primary key)
      - `sender_id` (uuid, references profiles)
      - `recipient_id` (uuid, references profiles)
      - `listing_id` (bigint, optional, references listings)
      - `subject` (text, optional)
      - `content` (text, required)
      - `is_read` (boolean, default false)
      - `created_at` (timestamp)

  2. Security
    - Enable RLS
    - Add policies for sender/recipient access
*/

-- Create messages table
CREATE TABLE IF NOT EXISTS messages (
  id bigserial PRIMARY KEY,
  sender_id uuid NOT NULL REFERENCES profiles(id),
  recipient_id uuid NOT NULL REFERENCES profiles(id),
  listing_id bigint REFERENCES listings(id),
  subject text,
  content text NOT NULL,
  is_read boolean DEFAULT false,
  created_at timestamptz DEFAULT now()
);

-- Enable RLS
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;

-- Create policies
CREATE POLICY "Allow authenticated users to send messages"
  ON messages
  FOR INSERT
  TO public
  WITH CHECK (auth.role() = 'authenticated');

CREATE POLICY "Allow users to view their messages"
  ON messages
  FOR SELECT
  TO public
  USING (auth.uid() = sender_id OR auth.uid() = recipient_id);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_messages_sender_id ON messages(sender_id);
CREATE INDEX IF NOT EXISTS idx_messages_recipient_id ON messages(recipient_id);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at DESC);