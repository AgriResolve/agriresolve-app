import { Address, nativeToScVal, scValToNative, xdr } from "@stellar/stellar-sdk";
import { createHash } from "node:crypto";

/**
 * Convert a Stellar G... or C... address into a Soroban ScVal Address
 */
export function addressToScVal(address: string): xdr.ScVal {
  return new Address(address).toScVal();
}

/**
 * Convert a symbol string into a Soroban ScVal Symbol
 */
export function symbolToScVal(symbol: string): xdr.ScVal {
  return xdr.ScVal.scvSymbol(symbol);
}

/**
 * Convert a string into a Soroban ScVal String
 */
export function stringToScVal(str: string): xdr.ScVal {
  return xdr.ScVal.scvString(str);
}

/**
 * Convert a u32 number into a Soroban ScVal
 */
export function u32ToScVal(num: number): xdr.ScVal {
  return xdr.ScVal.scvU32(num);
}

/**
 * Convert a u64 integer into a Soroban ScVal
 */
export function u64ToScVal(num: bigint | number): xdr.ScVal {
  return nativeToScVal(BigInt(num), { type: "u64" });
}

/**
 * Convert an i128 integer into a Soroban ScVal
 */
export function i128ToScVal(num: bigint | number): xdr.ScVal {
  return nativeToScVal(BigInt(num), { type: "i128" });
}

/**
 * Convert a boolean into a Soroban ScVal
 */
export function boolToScVal(val: boolean): xdr.ScVal {
  return xdr.ScVal.scvBool(val);
}

/**
 * Convert a 32-byte hex string or Buffer into a BytesN<32> ScVal
 */
export function bytes32ToScVal(hexOrBuffer: string | Buffer): xdr.ScVal {
  const buf = typeof hexOrBuffer === "string" 
    ? Buffer.from(hexOrBuffer.replace(/^0x/, ""), "hex") 
    : hexOrBuffer;
  if (buf.length !== 32) {
    throw new Error(`bytes32 must be exactly 32 bytes, got ${buf.length}`);
  }
  return xdr.ScVal.scvBytes(buf);
}

/**
 * Compute SHA-256 digest of input and return 32-byte Buffer
 */
export function sha256Digest(data: string | Buffer): Buffer {
  return createHash("sha256").update(data).digest();
}

/**
 * Re-export nativeToScVal and scValToNative for convenience
 */
export { nativeToScVal, scValToNative };
