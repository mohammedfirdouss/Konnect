# 🧩 Konnect Marketplace Smart Contract

**Program ID:** `B5nTWLtcbWiMpG26vTMBdVMZw3DL2ewsXZid1SDGBZNa`
**Framework:** [Anchor](https://book.anchor-lang.com/) (Solana)
**Language:** Rust
**Current Deployment Environment:** 🧪 **Devnet**
➡️ **Before continuing development, switch your environment to Localnet** for testing and modification:
```bash
solana config set --url localhost
````

---

## 📘 Overview

The **Konnect** program implements a decentralized marketplace on Solana supporting two primary flows:

1. **Goods flow** – one-time item or token sales (“buy now”)
2. **Service flow** – escrow-based payments for off-chain services

The architecture separates concerns into three logical layers:

| Layer           | Description                                            |
| --------------- | ------------------------------------------------------ |
| **Marketplace** | Global marketplace configuration (authority + fee bps) |
| **Merchant**    | A registered seller tied to a marketplace              |
| **Listing**     | A posted item/service offered by a merchant            |
| **Escrow**      | Temporary account for service-type transactions        |

---

## ⚙️ Setup & Local Development

### 1. Prerequisites

* Rust nightly toolchain
* Solana CLI ≥ v1.18
* Anchor CLI ≥ v0.30.0
* Localnet running (`solana-test-validator`)

### 2. Switch to Localnet

```bash
solana config set --url localhost
```

### 3. Build & Deploy

```bash
anchor build
anchor deploy
```

### 4. Test

You can create TypeScript or Rust tests. The simplest structure is:

```
tests/
  konnect_goods_flow.ts
  konnect_service_flow.ts
```

Recommended test coverage:

* Marketplace init & update
* Merchant registration
* Listing creation / update
* Goods buy-now purchase
* Service escrow creation → release → cancel

---

## 🧱 Program Structure

| Module                                                                  | Path          | Purpose                                           |
| ----------------------------------------------------------------------- | ------------- | ------------------------------------------------- |
| `init_marketplace` / `update_marketplace`                               | Root          | Initialize or update marketplace metadata         |
| `register_merchant` / `set_merchant_status`                             | Merchant flow | Register or verify merchants                      |
| `create_listing` / `update_listing`                                     | Listing flow  | Create or modify listings                         |
| `buy_now`                                                               | Goods flow    | Execute instant purchase (payment + transfer)     |
| `create_service_order`, `release_service_order`, `cancel_service_order` | Service flow  | Handle escrow creation, release, and cancellation |

---

## 🧩 Accounts Overview

| Account       | Purpose                                   | Seed derivation                            |
| ------------- | ----------------------------------------- | ------------------------------------------ |
| `Marketplace` | Holds authority + fee basis points        | `["marketplace", authority]`               |
| `Merchant`    | Registered merchant linked to marketplace | `["merchant", marketplace, owner]`         |
| `Listing`     | Item or service listing                   | `["listing", marketplace, merchant, mint]` |
| `Escrow`      | Temporary state for service transactions  | `["escrow", listing, buyer]`               |

---

## 📦 Token Flows

### 1. **Goods flow (buy now)**

* Buyer pays seller in SPL tokens.
* Fee (basis points) goes to the marketplace treasury.
* Listing quantity decrements and auto-deactivates when zero.
* ❗ **Issue:** Currently, no asset transfer from seller → buyer.
  Buyers pay but never receive the listed item. (See Fix Guide below.)

### 2. **Service flow (escrow)**

* Buyer deposits tokens into escrow vault ATA.
* Seller completes service off-chain.
* Buyer or marketplace releases escrow → tokens flow to seller + treasury.
* Escrow account is then closed and rent refunded.

---

## ⚠️ Known Issues and Recommended Fixes

Below are all current issues identified in the code, grouped by severity and impact.

### 🟥 Critical Issues (must fix before production)

#### 1. Missing asset transfer in `buy_now`

**Problem:**
When a buyer purchases goods, payment tokens move to the seller, but **the actual goods (minted tokens/NFTs) are never transferred** from seller to buyer.

**Fix (Recommended Vault Pattern):**

* When creating a listing, require the seller to deposit listed tokens into a **vault ATA** owned by the `listing` PDA.
* On `buy_now`, transfer from vault → buyer’s ATA using `listing` PDA as signer.
* Close the vault when quantity reaches zero.

(See **Implementation Fix Guide** section below.)

---

### 🟧 Medium Issues

#### 2. Decimals and Quantity Handling

`Listing.quantity` is a `u32` and treated as “whole tokens”, but real SPL tokens may have decimals.
**Fix:**

* Use `transfer_checked` instead of `transfer`.
* Multiply `quantity` by `10^mint.decimals` or treat `price`/`quantity` as raw token units.

#### 3. Seller Signature Missing in `buy_now`

Without a vault or delegate, the program cannot legally transfer tokens from the seller’s ATA (no signer).
**Fix:** Vault pattern resolves this.

#### 4. `CancelServiceOrder` sets `released = true` before closing

Redundant mutation.
**Fix:** Remove mutation or skip closing if you want to persist the record.

#### 5. `ReleaseServiceOrder` access control

Currently only the `buyer` can call it.
**Fix:** Allow marketplace authority as well:

```rust
require!(
    ctx.accounts.buyer.is_signer ||
    (ctx.accounts.marketplace.authority == ctx.accounts.buyer.key() && ctx.accounts.buyer.is_signer),
    MarketplaceError::Unauthorized
);
```

---

### 🟨 Minor / Improvement Suggestions

| Area                | Suggestion                                                                     |
| ------------------- | ------------------------------------------------------------------------------ |
| **Events**          | Add `fee` and `seller_amount` fields to `OrderCompleted` for indexer tracking. |
| **Error Handling**  | Add `InsufficientInventory` error code.                                        |
| **Overflow Safety** | Use `u128` for intermediate multiplication before casting to `u64`.            |
| **Housekeeping**    | Add `close_listing` and `withdraw_treasury` instructions.                      |
| **Docs**            | Define units for `price` and `quantity`.                                       |
| **Testing**         | Add unit/integration tests for both flows and edge cases.                      |

---

## 🧪 Testing Checklist

| Test                                   | Expected Result                            |
| -------------------------------------- | ------------------------------------------ |
| Initialize marketplace                 | ✅ Creates PDA                              |
| Register merchant                      | ✅ Merchant account created                 |
| Create listing (service)               | ✅ Vault + listing created                  |
| Buy-now flow                           | ✅ Tokens moved buyer→seller, goods → buyer |
| Service escrow release                 | ✅ Funds moved vault→seller, fee→treasury   |
| Service escrow cancel                  | ✅ Funds refunded to buyer                  |
| Fee calculation accuracy               | ✅ Matches bps percentage                   |
| Zero-quantity listing auto-deactivates | ✅ Listing inactive after full sale         |

---

## 🔐 PDA Seeds Summary

| PDA             | Seed Formula                               | Notes                              |
| --------------- | ------------------------------------------ | ---------------------------------- |
| **Marketplace** | `["marketplace", authority]`               | One per marketplace authority      |
| **Merchant**    | `["merchant", marketplace, owner]`         | One per merchant                   |
| **Listing**     | `["listing", marketplace, merchant, mint]` | Vault authority for listed assets  |
| **Escrow**      | `["escrow", listing, buyer]`               | Vault authority for service orders |

---

## 🧠 Design Philosophy

* **Atomicity:** Every flow is atomic and verifiable on-chain.
* **Traceability:** Every order emits a structured event.
* **Extensibility:** Marketplace fees and authorities are dynamic.
* **Solana Pay Integration:** `reference` field ties on-chain orders to off-chain payments.

---

## 🧩 Implementation Fix Guide (Vault Approach)

Below is a practical patch for the **goods flow** using the **vault pattern**.

### 1️⃣ `create_listing` – Deposit seller tokens into vault

```rust
#[derive(Accounts)]
pub struct CreateListing<'info> {
    #[account(mut)]
    pub merchant: Account<'info, Merchant>,
    #[account(init, payer = owner, space = 8 + Listing::LEN, seeds = [b"listing", merchant.marketplace.as_ref(), merchant.key().as_ref(), mint.key().as_ref()], bump)]
    pub listing: Account<'info, Listing>,
    #[account(mut)]
    pub owner: Signer<'info>,
    pub mint: Account<'info, Mint>,
    #[account(
        init,
        payer = owner,
        associated_token::mint = mint,
        associated_token::authority = listing
    )]
    pub vault_ata: Account<'info, TokenAccount>,
    #[account(mut)]
    pub seller_ata: Account<'info, TokenAccount>,
    pub token_program: Program<'info, Token>,
    pub system_program: Program<'info, System>,
    pub rent: Sysvar<'info, Rent>,
    pub associated_token_program: Program<'info, AssociatedToken>,
}

pub fn create_listing(ctx: Context<CreateListing>, price: u64, quantity: u64, listing_type: ListingType) -> Result<()> {
    let listing = &mut ctx.accounts.listing;
    listing.price = price;
    listing.quantity = quantity;
    listing.listing_type = listing_type;
    listing.merchant = ctx.accounts.merchant.key();
    listing.mint = ctx.accounts.mint.key();

    // Transfer tokens from seller into vault
    let cpi_accounts = Transfer {
        from: ctx.accounts.seller_ata.to_account_info(),
        to: ctx.accounts.vault_ata.to_account_info(),
        authority: ctx.accounts.owner.to_account_info(),
    };
    token::transfer(CpiContext::new(ctx.accounts.token_program.to_account_info(), cpi_accounts), quantity)?;

    Ok(())
}
```

---

### 2️⃣ `buy_now` – Transfer from vault to buyer

```rust
#[derive(Accounts)]
pub struct BuyNow<'info> {
    #[account(mut)]
    pub buyer: Signer<'info>,
    #[account(mut)]
    pub listing: Account<'info, Listing>,
    #[account(mut)]
    pub vault_ata: Account<'info, TokenAccount>,
    #[account(mut)]
    pub buyer_ata: Account<'info, TokenAccount>,
    #[account(mut)]
    pub seller_treasury_ata: Account<'info, TokenAccount>,
    pub mint: Account<'info, Mint>,
    #[account(mut)]
    pub marketplace_treasury_ata: Account<'info, TokenAccount>,
    pub token_program: Program<'info, Token>,
}

pub fn buy_now(ctx: Context<BuyNow>, quantity: u64) -> Result<()> {
    let listing = &mut ctx.accounts.listing;

    require!(listing.is_active, MarketplaceError::ListingInactive);
    require!(listing.quantity >= quantity, MarketplaceError::InsufficientInventory);

    let total_price = listing.price.checked_mul(quantity).unwrap();
    let fee_amount = total_price
        .checked_mul(listing.fee_bps.into())
        .unwrap()
        .checked_div(10_000)
        .unwrap();
    let seller_amount = total_price.checked_sub(fee_amount).unwrap();

    // Transfer payment from buyer → seller and treasury
    let cpi_ctx = CpiContext::new(
        ctx.accounts.token_program.to_account_info(),
        Transfer {
            from: ctx.accounts.buyer_ata.to_account_info(),
            to: ctx.accounts.seller_treasury_ata.to_account_info(),
            authority: ctx.accounts.buyer.to_account_info(),
        },
    );
    token::transfer(cpi_ctx, seller_amount)?;

    let cpi_ctx_fee = CpiContext::new(
        ctx.accounts.token_program.to_account_info(),
        Transfer {
            from: ctx.accounts.buyer_ata.to_account_info(),
            to: ctx.accounts.marketplace_treasury_ata.to_account_info(),
            authority: ctx.accounts.buyer.to_account_info(),
        },
    );
    token::transfer(cpi_ctx_fee, fee_amount)?;

    // Transfer goods from vault → buyer
    let seeds = &[
        b"listing",
        listing.marketplace.as_ref(),
        listing.merchant.as_ref(),
        listing.mint.as_ref(),
        &[ctx.bumps.listing],
    ];
    let signer_seeds = &[&seeds[..]];
    let vault_to_buyer_ctx = CpiContext::new_with_signer(
        ctx.accounts.token_program.to_account_info(),
        Transfer {
            from: ctx.accounts.vault_ata.to_account_info(),
            to: ctx.accounts.buyer_ata.to_account_info(),
            authority: ctx.accounts.listing.to_account_info(),
        },
        signer_seeds,
    );
    token::transfer(vault_to_buyer_ctx, quantity)?;

    // Update quantity
    listing.quantity = listing.quantity.checked_sub(quantity).unwrap();
    if listing.quantity == 0 {
        listing.is_active = false;
    }

    Ok(())
}
```

---

## 📚 Future Enhancements

* [ ] Implement per-merchant fee override
* [ ] Multi-token support
* [ ] Royalties / affiliate splits
* [ ] Listing expiration dates
* [ ] Partial milestone releases for services

---

## 👋 Developer Notes (Handover)

Hey dev 👋 —
This program is **deployed on Devnet** for testing.
Before making any changes or redeployments, **switch to Localnet** and test there.

The **service escrow** flow is fully functional.
The **goods flow** needs the vault logic above integrated and tested.

**Next steps:**

1. Implement the vault patch in both `create_listing` and `buy_now`.
2. Run full integration tests locally.
3. Verify PDAs and CPI calls with real token accounts on devnet.
4. Refactor + redeploy with a new Program ID once stable.

---
📄 License

MIT

✅ **This version includes everything** — setup, structure, issues, environment note, and the complete vault-based code patch.

