/*
  # Create orders and purchases tables

  1. New Tables
    - `orders`
      - `id` (bigserial, primary key)
      - `buyer_id` (uuid, references profiles)
      - `seller_id` (uuid, references profiles)
      - `listing_id` (bigint, references listings)
      - `quantity` (integer, default 1)
      - `total_amount` (real, required)
      - `delivery_address` (text, optional)
      - `notes` (text, optional)
      - `escrow_tx_hash` (text, optional)
      - `status` (text, default 'pending')
      - `created_at` (timestamp)
      - `updated_at` (timestamp)

    - `purchases`
      - `id` (bigserial, primary key)
      - `user_id` (uuid, references profiles)
      - `listing_id` (bigint, references listings)
      - `amount` (real, required)
      - `status` (text, default 'pending')
      - `payment_method` (text, optional)
      - `transaction_hash` (text, optional)
      - `created_at` (timestamp)
      - `updated_at` (timestamp)

  2. Security
    - Enable RLS on both tables
    - Add policies for buyer/seller access
    - Add timestamp triggers
*/

-- Create orders table
CREATE TABLE IF NOT EXISTS orders (
  id bigserial PRIMARY KEY,
  buyer_id uuid NOT NULL REFERENCES profiles(id),
  seller_id uuid NOT NULL REFERENCES profiles(id),
  listing_id bigint NOT NULL REFERENCES listings(id),
  quantity integer DEFAULT 1 CHECK (quantity > 0),
  total_amount real NOT NULL CHECK (total_amount > 0),
  delivery_address text,
  notes text,
  escrow_tx_hash text,
  status text DEFAULT 'pending' CHECK (status IN ('pending', 'paid', 'shipped', 'delivered', 'disputed', 'cancelled', 'completed')),
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- Create purchases table
CREATE TABLE IF NOT EXISTS purchases (
  id bigserial PRIMARY KEY,
  user_id uuid NOT NULL REFERENCES profiles(id),
  listing_id bigint NOT NULL REFERENCES listings(id),
  amount real NOT NULL CHECK (amount > 0),
  status text DEFAULT 'pending' CHECK (status IN ('pending', 'completed', 'cancelled')),
  payment_method text,
  transaction_hash text,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- Enable RLS
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE purchases ENABLE ROW LEVEL SECURITY;

-- Orders policies
CREATE POLICY "Allow authenticated users to create orders"
  ON orders
  FOR INSERT
  TO public
  WITH CHECK (auth.role() = 'authenticated');

CREATE POLICY "Allow buyer and seller to view their orders"
  ON orders
  FOR SELECT
  TO public
  USING (auth.uid() = buyer_id OR auth.uid() = seller_id);

CREATE POLICY "Allow buyer and seller to update their orders"
  ON orders
  FOR UPDATE
  TO public
  USING (auth.uid() = buyer_id OR auth.uid() = seller_id);

-- Purchases policies
CREATE POLICY "Allow users to view their own purchases"
  ON purchases
  FOR SELECT
  TO public
  USING (auth.uid() = user_id);

-- Create timestamp triggers
CREATE TRIGGER set_orders_timestamp
  BEFORE UPDATE ON orders
  FOR EACH ROW
  EXECUTE FUNCTION trigger_set_timestamp();

CREATE TRIGGER set_purchases_timestamp
  BEFORE UPDATE ON purchases
  FOR EACH ROW
  EXECUTE FUNCTION trigger_set_timestamp();