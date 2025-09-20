-- Update RLS policies for better security

-- Drop old permissive policies
DROP POLICY IF EXISTS "Enable read access for all users" ON public.marketplaces;
DROP POLICY IF EXISTS "Enable read access for all users" ON public.listings;
DROP POLICY IF EXISTS "Users can manage their own profiles" ON public.profiles;
DROP POLICY IF EXISTS "Users can manage their own marketplaces" ON public.marketplaces;
DROP POLICY IF EXISTS "Users can manage their own listings" ON public.listings;
DROP POLICY IF EXISTS "Users can manage their own orders" ON public.orders;
DROP POLICY IF EXISTS "Users can manage their own reviews" ON public.user_reviews;
DROP POLICY IF EXISTS "Users can manage their own wishlist" ON public.user_wishlist;
DROP POLICY IF EXISTS "Users can manage their own listing images" ON public.listing_images;
DROP POLICY IF EXISTS "Users can manage their own messages" ON public.messages;
DROP POLICY IF EXISTS "Users can manage their own purchases" ON public.purchases;
DROP POLICY IF EXISTS "Users can manage their own activities" ON public.user_activities;
DROP POLICY IF EXISTS "Users can manage their own marketplace requests" ON public.marketplace_requests;

-- Profiles
CREATE POLICY "Allow public read access to profiles" ON public.profiles FOR SELECT USING (true);
CREATE POLICY "Allow users to update their own profile" ON public.profiles FOR UPDATE USING (auth.uid() = id);

-- Marketplaces
CREATE POLICY "Allow public read access to active marketplaces" ON public.marketplaces FOR SELECT USING (is_active = true);
CREATE POLICY "Allow authenticated users to create marketplaces" ON public.marketplaces FOR INSERT WITH CHECK (auth.role() = 'authenticated');
CREATE POLICY "Allow owners to update their marketplaces" ON public.marketplaces FOR UPDATE USING (auth.uid() = created_by);

-- Listings
CREATE POLICY "Allow public read access to active listings" ON public.listings FOR SELECT USING (is_active = true);
CREATE POLICY "Allow authenticated users to create listings" ON public.listings FOR INSERT WITH CHECK (auth.role() = 'authenticated');
CREATE POLICY "Allow owners to update their listings" ON public.listings FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Allow owners to delete their listings" ON public.listings FOR DELETE USING (auth.uid() = user_id);

-- Orders
CREATE POLICY "Allow buyer and seller to view their orders" ON public.orders FOR SELECT USING (auth.uid() = buyer_id OR auth.uid() = seller_id);
CREATE POLICY "Allow authenticated users to create orders" ON public.orders FOR INSERT WITH CHECK (auth.role() = 'authenticated');
CREATE POLICY "Allow buyer and seller to update their orders" ON public.orders FOR UPDATE USING (auth.uid() = buyer_id OR auth.uid() = seller_id);

-- User Reviews
CREATE POLICY "Allow public read access to user reviews" ON public.user_reviews FOR SELECT USING (true);
CREATE POLICY "Allow authenticated users to create reviews" ON public.user_reviews FOR INSERT WITH CHECK (auth.role() = 'authenticated');
CREATE POLICY "Allow owners to update their reviews" ON public.user_reviews FOR UPDATE USING (auth.uid() = reviewer_id);
CREATE POLICY "Allow owners to delete their reviews" ON public.user_reviews FOR DELETE USING (auth.uid() = reviewer_id);

-- User Wishlist
CREATE POLICY "Allow users to view their own wishlist" ON public.user_wishlist FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Allow users to add to their own wishlist" ON public.user_wishlist FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Allow users to remove from their own wishlist" ON public.user_wishlist FOR DELETE USING (auth.uid() = user_id);

-- Listing Images
CREATE POLICY "Allow public read access to listing images" ON public.listing_images FOR SELECT USING (true);
CREATE POLICY "Allow listing owners to add images" ON public.listing_images FOR INSERT WITH CHECK (auth.uid() IN (SELECT user_id FROM listings WHERE id = listing_id));
CREATE POLICY "Allow listing owners to delete images" ON public.listing_images FOR DELETE USING (auth.uid() IN (SELECT user_id FROM listings WHERE id = listing_id));

-- Messages
CREATE POLICY "Allow users to view their messages" ON public.messages FOR SELECT USING (auth.uid() = sender_id OR auth.uid() = recipient_id);
CREATE POLICY "Allow authenticated users to send messages" ON public.messages FOR INSERT WITH CHECK (auth.role() = 'authenticated');

-- Purchases
CREATE POLICY "Allow users to view their own purchases" ON public.purchases FOR SELECT USING (auth.uid() = user_id);

-- User Activities
CREATE POLICY "Allow users to view their own activities" ON public.user_activities FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Allow users to create their own activities" ON public.user_activities FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Marketplace Requests
CREATE POLICY "Allow users to view their own marketplace requests" ON public.marketplace_requests FOR SELECT USING (auth.uid() = requested_by);
CREATE POLICY "Allow authenticated users to create marketplace requests" ON public.marketplace_requests FOR INSERT WITH CHECK (auth.role() = 'authenticated');

-- Function to check for admin role (example)
CREATE OR REPLACE FUNCTION is_admin()
RETURNS BOOLEAN AS $$
BEGIN
  RETURN (SELECT 'admin' IN (SELECT role FROM public.profiles WHERE id = auth.uid()));
END;
$$ LANGUAGE plpgsql;

-- Add admin policies for marketplace requests
CREATE POLICY "Allow admins to view all marketplace requests" ON public.marketplace_requests FOR SELECT USING (is_admin());
CREATE POLICY "Allow admins to update marketplace requests" ON public.marketplace_requests FOR UPDATE USING (is_admin());
