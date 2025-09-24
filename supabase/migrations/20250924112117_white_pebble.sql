/*
  # Create listing images table for image management

  1. New Tables
    - `listing_images`
      - `id` (bigserial, primary key)
      - `listing_id` (bigint, references listings)
      - `filename` (text, required)
      - `original_filename` (text, required)
      - `file_path` (text, required)
      - `file_size` (integer, required)
      - `mime_type` (text, required)
      - `is_primary` (boolean, default false)
      - `created_at` (timestamp)

  2. Security
    - Enable RLS
    - Add policies for listing owners and public read access
*/

-- Create listing_images table
CREATE TABLE IF NOT EXISTS listing_images (
  id bigserial PRIMARY KEY,
  listing_id bigint NOT NULL REFERENCES listings(id),
  filename text NOT NULL,
  original_filename text NOT NULL,
  file_path text NOT NULL,
  file_size integer NOT NULL CHECK (file_size > 0),
  mime_type text NOT NULL,
  is_primary boolean DEFAULT false,
  created_at timestamptz DEFAULT now()
);

-- Enable RLS
ALTER TABLE listing_images ENABLE ROW LEVEL SECURITY;

-- Create policies
CREATE POLICY "Allow public read access to listing images"
  ON listing_images
  FOR SELECT
  TO public
  USING (true);

CREATE POLICY "Allow listing owners to add images"
  ON listing_images
  FOR INSERT
  TO public
  WITH CHECK (
    auth.uid() IN (
      SELECT user_id FROM listings WHERE id = listing_images.listing_id
    )
  );

CREATE POLICY "Allow listing owners to delete images"
  ON listing_images
  FOR DELETE
  TO public
  USING (
    auth.uid() IN (
      SELECT user_id FROM listings WHERE id = listing_images.listing_id
    )
  );

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_listing_images_listing_id ON listing_images(listing_id);
CREATE INDEX IF NOT EXISTS idx_listing_images_is_primary ON listing_images(is_primary) WHERE is_primary = true;