-- Enable Realtime on messages and listings tables

-- Messages
ALTER TABLE public.messages REPLICA IDENTITY FULL;

-- Listings
ALTER TABLE public.listings REPLICA IDENTITY FULL;

-- Add tables to the existing publication
ALTER PUBLICATION supabase_realtime ADD TABLE public.messages, public.listings;
