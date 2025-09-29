// hooks/useProgram.ts
import { useMemo } from "react";
import { Program, Idl } from "@coral-xyz/anchor";
import idl from "../idl.json";
import { PublicKey } from "@solana/web3.js";
import { useAnchorProvider } from "./useAnchorProvider";

const PROGRAM_ID = new PublicKey("B5nTWLtcbWiMpG26vTMBdVMZw3DL2ewsXZid1SDGBZNa");

export function useSmartContract() {
  const provider = useAnchorProvider();

  const program = useMemo(() => {
    if (!provider) return null;
    return new Program(idl as Idl, PROGRAM_ID, provider);
  }, [provider]);

  return program;
}
