// import React from 'react'
// import { PublicKey } from '@solana/web3.js';
// import * as anchor from '@coral-xyz/anchor';
// import { useSmartContract } from './useSmartContract';

// const useMarketPlace =  () => {

//     const { program, wallet } = useSmartContract();

// const [marketplacePda] = PublicKey.findProgramAddressSync(
//   [Buffer.from('marketplace'), wallet.publicKey.toBuffer()],
//   program.programId
// );

// const initMarketplace = async () => {
//     await program.methods
//     .initMarketplace(500) 
//     .accounts({
//       marketplace: marketplacePda,
//       authority: wallet.publicKey,
//       systemProgram: anchor.web3.SystemProgram.programId,
//     })
//     .rpc();
// }

//   return { marketplacePda, initMarketplace };

// }

// export default useMarketPlace