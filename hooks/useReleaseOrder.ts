// import * as anchor from '@coral-xyz/anchor';
// import React from 'react';
// import { useSmartContract } from './useSmartContract';
// import useMarketPlace from './useMarketPlace';

// const useReleaseOrder = async () => {

//         const { program, wallet } = useSmartContract();
//         const { marketplacePda } = useMarketPlace();
    
//  await program.methods
//    .releaseServiceOrder()
//    .accounts({
//      escrow: escrowPda,
//      marketplace: marketplacePda,
//      listing: listingPda,
//      buyer: wallet.publicKey, // must match escrow.buyer OR marketplace authority
//      sellerAta, // seller’s ATA for mint
//      treasuryAta, // treasury ATA owned by marketplace authority
//      vault: vaultAta,
//      tokenProgram: anchor.utils.token.TOKEN_PROGRAM_ID,
//      systemProgram: anchor.web3.SystemProgram.programId,
//    })
//    .rpc();

// }

// export default useReleaseOrder