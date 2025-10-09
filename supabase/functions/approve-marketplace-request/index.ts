// Follow this setup guide to integrate the Deno language server with your editor:
// https://deno.land/manual/getting_started/setup_your_environment
// This enables autocomplete, go to definition, etc.

import { createClient } from '@supabase/supabase-js'
import { corsHeaders } from '../_shared/cors.ts'

interface RequestBody {
  request_id: string | number
}

interface MarketplaceRequest {
  id: string | number
  university_name: string
  description: string
  requested_by: string
  status: string
}

Deno.serve(async (req) => {
  // This is needed if you're planning to invoke your function from a browser.
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    const body: RequestBody = await req.json()
    const { request_id } = body

    // Validate request_id
    if (!request_id) {
      return new Response(JSON.stringify({ error: 'request_id is required' }), {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        status: 400,
      })
    }

    // Create a Supabase client with the Auth context of the logged in user.
    const supabaseClient = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_ANON_KEY') ?? '',
      { global: { headers: { Authorization: req.headers.get('Authorization')! } } }
    )

    // First, check if the user is an admin.
    const { data: { user } } = await supabaseClient.auth.getUser()
    if (!user) {
      return new Response(JSON.stringify({ error: 'Unauthorized' }), {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        status: 401,
      })
    }

    const { data: profile, error: profileError } = await supabaseClient
      .from('profiles')
      .select('role')
      .eq('id', user.id)
      .single()

    if (profileError || profile.role !== 'admin') {
      return new Response(JSON.stringify({ error: 'Forbidden: Admins only' }), {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        status: 403,
      })
    }

    // Now, perform the marketplace approval in a transaction.
    const { data: request, error: requestError } = await supabaseClient
      .from('marketplace_requests')
      .select('*')
      .eq('id', request_id)
      .single()

    if (requestError) {
      console.error('Error fetching marketplace request:', requestError)
      return new Response(JSON.stringify({ error: 'Failed to fetch marketplace request' }), {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        status: 500,
      })
    }

    if (!request) {
      return new Response(JSON.stringify({ error: 'Marketplace request not found' }), {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        status: 404,
      })
    }

    if (request.status !== 'pending') {
      return new Response(JSON.stringify({ error: 'Request is not pending approval' }), {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        status: 400,
      })
    }

    // Validate required fields from the request
    if (!request.university_name || !request.description || !request.requested_by) {
      return new Response(JSON.stringify({ error: 'Invalid marketplace request data' }), {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        status: 400,
      })
    }

    // Use a transaction-like approach: create marketplace first, then update request
    // This is safer than updating first and then rolling back
    const { data: newMarketplace, error: marketplaceError } = await supabaseClient
      .from('marketplaces')
      .insert({
        name: request.university_name,
        description: request.description,
        created_by: request.requested_by,
      })
      .select()

    if (marketplaceError) {
      console.error('Error creating marketplace:', marketplaceError)
      return new Response(JSON.stringify({ error: 'Failed to create marketplace' }), {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        status: 500,
      })
    }

    // Now update the request status
    const { data: updatedRequest, error: updateError } = await supabaseClient
      .from('marketplace_requests')
      .update({ status: 'approved' })
      .eq('id', request_id)
      .select()

    if (updateError) {
      console.error('Error updating request status:', updateError)
      // If updating the request fails, we should clean up the marketplace
      // This is a critical error that requires manual intervention
      return new Response(JSON.stringify({ 
        error: 'Marketplace created but failed to update request status. Manual intervention required.',
        marketplace_id: newMarketplace?.[0]?.id 
      }), {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        status: 500,
      })
    }

    return new Response(JSON.stringify({ marketplace: newMarketplace }), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      status: 201,
    })
  } catch (error) {
    console.error('Unexpected error in approve-marketplace-request:', error)
    
    // Handle different types of errors
    let errorMessage = 'An unexpected error occurred'
    let statusCode = 500
    
    if (error instanceof Error) {
      errorMessage = error.message
    } else if (typeof error === 'string') {
      errorMessage = error
    }
    
    // Handle JSON parsing errors
    if (errorMessage.includes('JSON')) {
      errorMessage = 'Invalid JSON in request body'
      statusCode = 400
    }
    
    return new Response(JSON.stringify({ error: errorMessage }), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      status: statusCode,
    })
  }
})