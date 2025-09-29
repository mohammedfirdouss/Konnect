// import { PublicKey } from '@solana/web3.js';
// import * as anchor from '@coral-xyz/anchor';


// // const [listingPda] = PublicKey.findProgramAddressSync(
// //   [Buffer.from("listing"), marketplacePda.toBuffer(), merchantPda.toBuffer(), mint.toBuffer()],
// //   program.programId
// // );

// // Assume we already have: program, wallet, marketplacePda, listingPda, mint, etc.
// const createServiceOrder = async (program: any,listingPda: any) => {
//   const [escrowPda] = PublicKey.findProgramAddressSync(
//     [Buffer.from('escrow'), listingPda.toBuffer(), wallet.publicKey.toBuffer()],
//     program.programId
//   );

//   const vaultAta = await anchor.utils.token.associatedAddress({
//     mint,
//     owner: escrowPda, // vault ATA authority is escrow PDA
//   });

//   const reference = anchor.web3.Keypair.generate().publicKey; // generate reference (or from backend)

//   await program.methods
//     .createServiceOrder(reference)
//     .accounts({
//       marketplace: marketplacePda,
//       listing: listingPda,
//       buyer: wallet.publicKey,
//       buyerAta: buyerAta, // must be buyer’s ATA for mint
//       escrow: escrowPda,
//       vault: vaultAta,
//       mint,
//       tokenProgram: anchor.utils.token.TOKEN_PROGRAM_ID,
//       associatedTokenProgram: anchor.utils.token.ASSOCIATED_PROGRAM_ID,
//       systemProgram: anchor.web3.SystemProgram.programId,
//     })
//     .remainingAccounts([
//       { pubkey: reference, isWritable: false, isSigner: false },
//     ])
//     .rpc();
// };
