-- Seed data for development and testing

-- Insert sample profiles (these will be created automatically when users sign up)
-- This is just for reference - actual profiles are created via the trigger

-- Insert sample marketplaces
INSERT INTO marketplaces (name, description, created_by) VALUES
  ('University Campus Store', 'Official campus marketplace for students', (SELECT id FROM profiles LIMIT 1)),
  ('Student Exchange', 'Peer-to-peer marketplace for students', (SELECT id FROM profiles LIMIT 1))
ON CONFLICT DO NOTHING;

-- Insert sample listings
INSERT INTO listings (title, description, price, category, marketplace_id, user_id) VALUES
  ('MacBook Pro 13-inch', 'Excellent condition laptop perfect for students', 899.99, 'Electronics', 1, (SELECT id FROM profiles LIMIT 1)),
  ('Calculus Textbook', 'Stewart Calculus 8th Edition, minimal highlighting', 120.00, 'Books', 1, (SELECT id FROM profiles LIMIT 1)),
  ('Study Desk', 'IKEA desk perfect for dorm room', 75.00, 'Furniture', 1, (SELECT id FROM profiles LIMIT 1)),
  ('iPhone 12', 'Unlocked iPhone 12 in good condition', 450.00, 'Electronics', 2, (SELECT id FROM profiles LIMIT 1)),
  ('Chemistry Lab Manual', 'Required lab manual for CHEM 101', 45.00, 'Books', 2, (SELECT id FROM profiles LIMIT 1))
ON CONFLICT DO NOTHING;