import {
  isConnected as freighterIsConnected,
  requestAccess as freighterRequestAccess,
  getAddress as freighterGetAddress,
  signTransaction as freighterSignTransaction,
} from "@stellar/freighter-api";

export interface WalletState {
  isConnected: boolean;
  address: string | null;
  error: string | null;
}

/**
 * Check if Freighter browser extension is installed and responsive
 */
export async function checkFreighterInstalled(): Promise<boolean> {
  try {
    const result = await freighterIsConnected();
    return Boolean(result && !result.error);
  } catch (error) {
    return false;
  }
}

/**
 * Request user authorization and return connected Stellar address
 */
export async function connectFreighter(): Promise<string> {
  const isInstalled = await checkFreighterInstalled();
  if (!isInstalled) {
    throw new Error(
      "Freighter wallet extension not detected. Please install Freighter from https://www.freighter.app/"
    );
  }

  const access = await freighterRequestAccess();
  if (access.error) {
    throw new Error(`Freighter access denied: ${access.error}`);
  }

  const addressResult = await freighterGetAddress();
  if (addressResult.error || !addressResult.address) {
    throw new Error(
      `Could not retrieve account address: ${addressResult.error || "Unknown error"}`
    );
  }

  return addressResult.address;
}

/**
 * Sign a transaction XDR with Freighter
 */
export async function signWithFreighter(
  xdr: string,
  networkPassphrase?: string
): Promise<string> {
  const result = await freighterSignTransaction(xdr, {
    networkPassphrase:
      networkPassphrase ||
      process.env.NEXT_PUBLIC_NETWORK_PASSPHRASE ||
      "Test SDF Network ; September 2015",
  });

  if (result.error) {
    throw new Error(`Transaction signing rejected: ${result.error}`);
  }

  return result.signedTxXdr;
}
