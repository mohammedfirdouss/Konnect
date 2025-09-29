export interface MarketPlaceInterface {
    "created_at":string, "created_by": string, "description": string, "id": number | string, "is_active": boolean, "name": string, "profiles": {"username": string}, "updated_at": string
}

export interface MarketPlaceProductInterface {
    "category": string, 
    "created_at": string, 
    "description": string, 
    "id": number | string, 
    "is_active": boolean, 
    "marketplace_id": number | string, 
    "price": number, 
    "profiles": {"username": string}, 
    "title": string, 
    "updated_at": string, 
    "user_id": string
}

export interface ProductInterface {
    "category": string, 
    "created_at": string, 
    "description": string, 
    "id": number | string, 
    "is_active": boolean, 
    "marketplace_id": number | string, 
    "marketplaces": {"name": string}, 
    "price": number, 
    "profiles": {"full_name": string, "username": string}, 
    "title": string, 
    "updated_at": string, 
    "user_id": string
}

