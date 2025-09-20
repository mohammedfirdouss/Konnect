import * as anchor from "@coral-xyz/anchor";

import { Konnect } from "../target/types/konnect";
import {
  PublicKey,
  Keypair,
  SystemProgram,
  LAMPORTS_PER_SOL,
} from "@solana/web3.js";
import {
  TOKEN_PROGRAM_ID,
  ASSOCIATED_TOKEN_PROGRAM_ID,
  createMint,
  createAssociatedTokenAccount,
  mintTo,
  getAssociatedTokenAddress,
} from "@solana/spl-token";
import { expect } from "chai";

describe("konnect marketplace", () => {
  // Configure the client to use the local cluster
  const provider = anchor.AnchorProvider.env();
  anchor.setProvider(provider);

  const program = anchor.workspace.konnect as anchor.Program<Konnect>;

  // Test accounts
  let marketplaceAuthority: Keypair;
  let merchant: Keypair;
  let buyer: Keypair;
  let mint: PublicKey;
  let marketplacePda: PublicKey;
  let merchantPda: PublicKey;
  let listingPda: PublicKey;

  // Token accounts
  let marketplaceAuthorityAta: PublicKey;
  let merchantAta: PublicKey;
  let buyerAta: PublicKey;
  let treasuryAta: PublicKey;

  before(async () => {
    // Use your CLI wallet as the funding account
    const fundingWallet = provider.wallet as anchor.Wallet;

    // Initialize test accounts
    marketplaceAuthority = Keypair.generate();
    merchant = Keypair.generate();
    buyer = Keypair.generate();

    // Transfer SOL from your CLI wallet to test accounts
    const transferAmount = 0.5 * LAMPORTS_PER_SOL; // 0.5 SOL each

    const transferToAuthority = new anchor.web3.Transaction().add(
      anchor.web3.SystemProgram.transfer({
        fromPubkey: fundingWallet.publicKey,
        toPubkey: marketplaceAuthority.publicKey,
        lamports: transferAmount,
      })
    );

    const transferToMerchant = new anchor.web3.Transaction().add(
      anchor.web3.SystemProgram.transfer({
        fromPubkey: fundingWallet.publicKey,
        toPubkey: merchant.publicKey,
        lamports: transferAmount,
      })
    );

    const transferToBuyer = new anchor.web3.Transaction().add(
      anchor.web3.SystemProgram.transfer({
        fromPubkey: fundingWallet.publicKey,
        toPubkey: buyer.publicKey,
        lamports: transferAmount,
      })
    );

    // Send transfers
    await provider.sendAndConfirm(transferToAuthority);
    await provider.sendAndConfirm(transferToMerchant);
    await provider.sendAndConfirm(transferToBuyer);

    // Wait for transfers to confirm
    await new Promise((resolve) => setTimeout(resolve, 1000));

    // Create a test token mint
    mint = await createMint(
      provider.connection,
      marketplaceAuthority,
      marketplaceAuthority.publicKey,
      null,
      6 // USDC has 6 decimals
    );

    // Create Associated Token Accounts
    marketplaceAuthorityAta = await createAssociatedTokenAccount(
      provider.connection,
      marketplaceAuthority,
      mint,
      marketplaceAuthority.publicKey
    );

    merchantAta = await createAssociatedTokenAccount(
      provider.connection,
      merchant,
      mint,
      merchant.publicKey
    );

    buyerAta = await createAssociatedTokenAccount(
      provider.connection,
      buyer,
      mint,
      buyer.publicKey
    );

    // Mint tokens to buyer for testing purchases
    await mintTo(
      provider.connection,
      buyer,
      mint,
      buyerAta,
      marketplaceAuthority,
      1000 * 10 ** 6 // 1000 USDC (with 6 decimals)
    );

    // Calculate PDAs
    [marketplacePda] = PublicKey.findProgramAddressSync(
      [Buffer.from("marketplace"), marketplaceAuthority.publicKey.toBuffer()],
      program.programId
    );

    [merchantPda] = PublicKey.findProgramAddressSync(
      [
        Buffer.from("merchant"),
        marketplacePda.toBuffer(),
        merchant.publicKey.toBuffer(),
      ],
      program.programId
    );

    [listingPda] = PublicKey.findProgramAddressSync(
      [
        Buffer.from("listing"),
        marketplacePda.toBuffer(),
        merchantPda.toBuffer(),
        mint.toBuffer(),
      ],
      program.programId
    );

    // Treasury ATA (owned by marketplace authority)
    treasuryAta = await getAssociatedTokenAddress(
      mint,
      marketplaceAuthority.publicKey
    );
  });

  describe("Marketplace Management", () => {
    it("Initializes marketplace", async () => {
      const feeBps = 250; // 2.5%

      await program.methods
        .initMarketplace(feeBps)
        .accounts({
          marketplace: marketplacePda,
          authority: marketplaceAuthority.publicKey,
          systemProgram: SystemProgram.programId,
        }as any)
        .signers([marketplaceAuthority])
        .rpc();

      // Verify marketplace was created correctly
      const marketplaceAccount = await program.account.marketplace.fetch(
        marketplacePda
      );

      expect(marketplaceAccount.authority.toString()).to.equal(
        marketplaceAuthority.publicKey.toString()
      );
      expect(marketplaceAccount.feeBps).to.equal(feeBps);
    });

    it("Updates marketplace fee", async () => {
      const newFeeBps = 300; // 3%

      await program.methods
        .updateMarketplace(newFeeBps, null)
        .accounts({
          marketplace: marketplacePda,
          authority: marketplaceAuthority.publicKey,
        }as any)
        .signers([marketplaceAuthority])
        .rpc();

      const marketplaceAccount = await program.account.marketplace.fetch(
        marketplacePda
      );
      expect(marketplaceAccount.feeBps).to.equal(newFeeBps);
    });

    it("Fails to set fee above 10%", async () => {
      try {
        await program.methods
          .updateMarketplace(1001, null) // 10.01%
          .accounts({
            marketplace: marketplacePda,
            authority: marketplaceAuthority.publicKey,
          }as any)
          .signers([marketplaceAuthority])
          .rpc();

        expect.fail("Should have failed with fee too high error");
      } catch (err) {
        expect(err.toString()).to.include("FeeTooHigh");
      }
    });
  });

  describe("Merchant Management", () => {
    it("Registers merchant", async () => {
      await program.methods
        .registerMerchant()
        .accounts({
          marketplace: marketplacePda,
          merchant: merchantPda,
          owner: merchant.publicKey,
          systemProgram: SystemProgram.programId,
        }as any)
        .signers([merchant])
        .rpc();

      const merchantAccount = await program.account.merchant.fetch(merchantPda);
      expect(merchantAccount.marketplace.toString()).to.equal(
        marketplacePda.toString()
      );
      expect(merchantAccount.owner.toString()).to.equal(
        merchant.publicKey.toString()
      );
      expect(merchantAccount.verified).to.equal(false);
    });

    it("Sets merchant verification status", async () => {
      await program.methods
        .setMerchantStatus(true)
        .accounts({
          merchant: merchantPda,
          marketplace: marketplacePda,
          authority: marketplaceAuthority.publicKey,
        }as any)
        .signers([marketplaceAuthority])
        .rpc();

      const merchantAccount = await program.account.merchant.fetch(merchantPda);
      expect(merchantAccount.verified).to.equal(true);
    });
  });

  describe("Listing Management", () => {
    it("Creates a goods listing", async () => {
      const price = new anchor.BN(100 * 10 ** 6); // 100 USDC
      const quantity = 10;
      const isService = false;

      await program.methods
        .createListing(price, quantity, isService)
        .accounts({
          marketplace: marketplacePda,
          merchant: merchantPda,
          owner: merchant.publicKey,
          listing: listingPda,
          mint: mint,
          systemProgram: SystemProgram.programId,
        }as any)
        .signers([merchant])
        .rpc();

      const listingAccount = await program.account.listing.fetch(listingPda);
      expect(listingAccount.price.toString()).to.equal(price.toString());
      expect(listingAccount.quantity).to.equal(quantity);
      expect(listingAccount.isService).to.equal(isService);
      expect(listingAccount.active).to.equal(true);
    });

    it("Updates listing", async () => {
      const newPrice = new anchor.BN(150 * 10 ** 6); // 150 USDC
      const newQuantity = 15;

      await program.methods
        .updateListing(newPrice, newQuantity, null)
        .accounts({
          listing: listingPda,
          seller: merchant.publicKey,
        }as any)
        .signers([merchant])
        .rpc();

      const listingAccount = await program.account.listing.fetch(listingPda);
      expect(listingAccount.price.toString()).to.equal(newPrice.toString());
      expect(listingAccount.quantity).to.equal(newQuantity);
    });
  });

  describe("Goods Purchase Flow", () => {
    let referenceKey: Keypair;

    beforeEach(() => {
      referenceKey = Keypair.generate();
    });

    it("Buys goods successfully", async () => {
      const quantity = 2;
      const listingAccount = await program.account.listing.fetch(listingPda);
      const expectedTotal = listingAccount.price.toNumber() * quantity;
      const expectedFee = Math.floor((expectedTotal * 300) / 10000); // 3% fee
      const expectedSellerAmount = expectedTotal - expectedFee;

      // Get initial balances
      const initialBuyerBalance = (
        await provider.connection.getTokenAccountBalance(buyerAta)
      ).value.amount;
      const initialMerchantBalance = (
        await provider.connection.getTokenAccountBalance(merchantAta)
      ).value.amount;

      await program.methods
        .buyNow(quantity, referenceKey.publicKey)
        .accounts({
          listing: listingPda,
          marketplace: marketplacePda,
          buyer: buyer.publicKey,
          buyerAta: buyerAta,
          sellerAta: merchantAta,
          treasuryAta: treasuryAta,
          mint: mint,
          tokenProgram: TOKEN_PROGRAM_ID,
        }as any)
        .remainingAccounts([
          {
            pubkey: referenceKey.publicKey,
            isWritable: false,
            isSigner: false,
          },
        ])
        .signers([buyer])
        .rpc();

      // Verify balances changed correctly
      const finalBuyerBalance = (
        await provider.connection.getTokenAccountBalance(buyerAta)
      ).value.amount;
      const finalMerchantBalance = (
        await provider.connection.getTokenAccountBalance(merchantAta)
      ).value.amount;
      const finalTreasuryBalance = (
        await provider.connection.getTokenAccountBalance(treasuryAta)
      ).value.amount;

      expect(
        parseInt(initialBuyerBalance) - parseInt(finalBuyerBalance)
      ).to.equal(expectedTotal);
      expect(
        parseInt(finalMerchantBalance) - parseInt(initialMerchantBalance)
      ).to.equal(expectedSellerAmount);
      expect(parseInt(finalTreasuryBalance)).to.equal(expectedFee);

      // Verify listing quantity was decremented
      const updatedListing = await program.account.listing.fetch(listingPda);
      expect(updatedListing.quantity).to.equal(15 - quantity);
    });

    it("Fails to buy inactive listing", async () => {
      // First deactivate the listing
      await program.methods
        .updateListing(null, null, false)
        .accounts({
          listing: listingPda,
          seller: merchant.publicKey,
        }as any)
        .signers([merchant])
        .rpc();

      try {
        await program.methods
          .buyNow(1, referenceKey.publicKey)
          .accounts({
            listing: listingPda,
            marketplace: marketplacePda,
            buyer: buyer.publicKey,
            buyerAta: buyerAta,
            sellerAta: merchantAta,
            treasuryAta: treasuryAta,
            mint: mint,
            tokenProgram: TOKEN_PROGRAM_ID,
          }as any)
          .remainingAccounts([
            {
              pubkey: referenceKey.publicKey,
              isWritable: false,
              isSigner: false,
            },
          ])
          .signers([buyer])
          .rpc();

        expect.fail("Should have failed with listing inactive error");
      } catch (err) {
        expect(err.toString()).to.include("ListingInactive");
      }

      // Reactivate for other tests
      await program.methods
        .updateListing(null, null, true)
        .accounts({
          listing: listingPda,
          seller: merchant.publicKey,
        }as any)
        .signers([merchant])
        .rpc();
    });
  });

  describe("Service Escrow Flow", () => {
    let serviceListingPda: PublicKey;
    let escrowPda: PublicKey;
    let vaultAta: PublicKey;
    let referenceKey: Keypair;
    let serviceMint: PublicKey;
    let serviceBuyerAta: PublicKey;
    let serviceMerchantAta: PublicKey;
    let serviceTreasuryAta: PublicKey;

    before(async () => {
      // Since we already have a goods listing, we need to create a new one for services
      // For simplicity, let's create a new mint for service listings
      serviceMint = await createMint(
        provider.connection,
        marketplaceAuthority,
        marketplaceAuthority.publicKey,
        null,
        6
      );

      serviceBuyerAta = await createAssociatedTokenAccount(
        provider.connection,
        buyer,
        serviceMint,
        buyer.publicKey
      );

      serviceMerchantAta = await createAssociatedTokenAccount(
        provider.connection,
        merchant,
        serviceMint,
        merchant.publicKey
      );

      serviceTreasuryAta = await getAssociatedTokenAddress(
        serviceMint,
        marketplaceAuthority.publicKey
      );

      // Mint tokens to buyer
      await mintTo(
        provider.connection,
        buyer,
        serviceMint,
        serviceBuyerAta,
        marketplaceAuthority,
        1000 * 10 ** 6
      );

      [serviceListingPda] = PublicKey.findProgramAddressSync(
        [
          Buffer.from("listing"),
          marketplacePda.toBuffer(),
          merchantPda.toBuffer(),
          serviceMint.toBuffer(),
        ],
        program.programId
      );

      // Create service listing
      await program.methods
        .createListing(new anchor.BN(200 * 10 ** 6), 1, true) // 200 USDC service
        .accounts({
          marketplace: marketplacePda,
          merchant: merchantPda,
          owner: merchant.publicKey,
          listing: serviceListingPda,
          mint: serviceMint,
          systemProgram: SystemProgram.programId,
        } as any)
        .signers([merchant])
        .rpc();

      [escrowPda] = PublicKey.findProgramAddressSync(
        [
          Buffer.from("escrow"),
          serviceListingPda.toBuffer(),
          buyer.publicKey.toBuffer(),
        ],
        program.programId
      );

      vaultAta = await getAssociatedTokenAddress(serviceMint, escrowPda, true);

      referenceKey = Keypair.generate();
    });

    it("Creates service order with escrow", async () => {
      await program.methods
        .createServiceOrder(referenceKey.publicKey)
        .accounts({
          marketplace: marketplacePda,
          listing: serviceListingPda,
          buyer: buyer.publicKey,
          buyerAta: serviceBuyerAta,
          escrow: escrowPda,
          vault: vaultAta,
          mint: serviceMint,
          tokenProgram: TOKEN_PROGRAM_ID,
          associatedTokenProgram: ASSOCIATED_TOKEN_PROGRAM_ID,
          systemProgram: SystemProgram.programId,
        }as any)
        .remainingAccounts([
          {
            pubkey: referenceKey.publicKey,
            isWritable: false,
            isSigner: false,
          },
        ])
        .signers([buyer])
        .rpc();

      // Verify escrow was created
      const escrowAccount = await program.account.escrow.fetch(escrowPda);
      expect(escrowAccount.buyer.toString()).to.equal(
        buyer.publicKey.toString()
      );
      expect(escrowAccount.released).to.equal(false);

      // Verify funds are in vault
      const vaultBalance = (
        await provider.connection.getTokenAccountBalance(vaultAta)
      ).value.amount;
      expect(parseInt(vaultBalance)).to.equal(200 * 10 ** 6);
    });

    it("Releases service order", async () => {
      const initialMerchantBalance = (
        await provider.connection.getTokenAccountBalance(serviceMerchantAta)
      ).value.amount;

      await program.methods
        .releaseServiceOrder()
        .accounts({
          escrow: escrowPda,
          marketplace: marketplacePda,
          listing: serviceListingPda,
          buyer: buyer.publicKey,
          sellerAta: serviceMerchantAta,
          treasuryAta: serviceTreasuryAta,
          vault: vaultAta,
          tokenProgram: TOKEN_PROGRAM_ID,
          systemProgram: SystemProgram.programId,
        }as any)
        .signers([buyer])
        .rpc();

      // Verify escrow is marked as released
      const escrowAccount = await program.account.escrow.fetch(escrowPda);
      expect(escrowAccount.released).to.equal(true);

      // Verify funds were distributed correctly
      const finalMerchantBalance = (
        await provider.connection.getTokenAccountBalance(serviceMerchantAta)
      ).value.amount;
      const treasuryBalance = (
        await provider.connection.getTokenAccountBalance(serviceTreasuryAta)
      ).value.amount;

      const totalAmount = 200 * 10 ** 6;
      const expectedFee = Math.floor((totalAmount * 300) / 10000); // 3% fee
      const expectedMerchantAmount = totalAmount - expectedFee;

      expect(
        parseInt(finalMerchantBalance) - parseInt(initialMerchantBalance)
      ).to.equal(expectedMerchantAmount);
      expect(parseInt(treasuryBalance)).to.equal(expectedFee);

      // Verify vault is closed
      try {
        await provider.connection.getTokenAccountBalance(vaultAta);
        expect.fail("Vault should be closed");
      } catch (err) {
        expect(err.toString()).to.include("could not find account");
      }
    });
  });

  describe("Service Cancellation Flow", () => {
    let cancelServiceListingPda: PublicKey;
    let cancelEscrowPda: PublicKey;
    let cancelVaultAta: PublicKey;
    let cancelReferenceKey: Keypair;
    let cancelServiceMint: PublicKey;
    let cancelServiceBuyerAta: PublicKey;

    it("Creates and cancels service order", async () => {
      // Create a new service listing for cancellation test
      cancelServiceMint = await createMint(
        provider.connection,
        marketplaceAuthority,
        marketplaceAuthority.publicKey,
        null,
        6
      );

      cancelServiceBuyerAta = await createAssociatedTokenAccount(
        provider.connection,
        buyer,
        cancelServiceMint,
        buyer.publicKey
      );

      // Mint tokens to buyer
      await mintTo(
        provider.connection,
        buyer,
        cancelServiceMint,
        cancelServiceBuyerAta,
        marketplaceAuthority,
        1000 * 10 ** 6
      );

      [cancelServiceListingPda] = PublicKey.findProgramAddressSync(
        [
          Buffer.from("listing"),
          marketplacePda.toBuffer(),
          merchantPda.toBuffer(),
          cancelServiceMint.toBuffer(),
        ],
        program.programId
      );

      // Create service listing
      await program.methods
        .createListing(new anchor.BN(100 * 10 ** 6), 1, true) // 100 USDC service
        .accounts({
          marketplace: marketplacePda,
          merchant: merchantPda,
          owner: merchant.publicKey,
          listing: cancelServiceListingPda,
          mint: cancelServiceMint,
          systemProgram: SystemProgram.programId,
        }as any)
        .signers([merchant])
        .rpc();

      [cancelEscrowPda] = PublicKey.findProgramAddressSync(
        [
          Buffer.from("escrow"),
          cancelServiceListingPda.toBuffer(),
          buyer.publicKey.toBuffer(),
        ],
        program.programId
      );

      cancelVaultAta = await getAssociatedTokenAddress(
        cancelServiceMint,
        cancelEscrowPda,
        true
      );

      cancelReferenceKey = Keypair.generate();

      // Create service order
      await program.methods
        .createServiceOrder(cancelReferenceKey.publicKey)
        .accounts({
          marketplace: marketplacePda,
          listing: cancelServiceListingPda,
          buyer: buyer.publicKey,
          buyerAta: cancelServiceBuyerAta,
          escrow: cancelEscrowPda,
          vault: cancelVaultAta,
          mint: cancelServiceMint,
          tokenProgram: TOKEN_PROGRAM_ID,
          associatedTokenProgram: ASSOCIATED_TOKEN_PROGRAM_ID,
          systemProgram: SystemProgram.programId,
        }as any)
        .remainingAccounts([
          {
            pubkey: cancelReferenceKey.publicKey,
            isWritable: false,
            isSigner: false,
          },
        ])
        .signers([buyer])
        .rpc();

      // Get initial buyer balance
      const initialBuyerBalance = (
        await provider.connection.getTokenAccountBalance(cancelServiceBuyerAta)
      ).value.amount;

      // Cancel the service order
      await program.methods
        .cancelServiceOrder()
        .accounts({
          escrow: cancelEscrowPda,
          marketplace: marketplacePda,
          buyer: buyer.publicKey,
          buyerAta: cancelServiceBuyerAta,
          vault: cancelVaultAta,
          tokenProgram: TOKEN_PROGRAM_ID,
        }as any)
        .signers([buyer])
        .rpc();

      // Verify funds were returned to buyer
      const finalBuyerBalance = (
        await provider.connection.getTokenAccountBalance(cancelServiceBuyerAta)
      ).value.amount;

      expect(parseInt(finalBuyerBalance)).to.equal(
        parseInt(initialBuyerBalance) + 100 * 10 ** 6
      );

      // Verify escrow is marked as released
      const escrowAccount = await program.account.escrow.fetch(cancelEscrowPda);
      expect(escrowAccount.released).to.equal(true);
    });
  });
});