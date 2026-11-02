/**
 * AgriResolve Protocol Types
 * Strictly aligned with Soroban contracts in AgriResolve-contract
 */

export enum ParticipantRole {
  Farmer = 0,
  Buyer = 1,
  Arbiter = 2,
  QualityInspector = 3,
}

export interface ParticipantProfile {
  role: ParticipantRole;
  metadataUri: string;
  isActive: boolean;
  registeredAt: bigint;
}

export interface CommoditySpec {
  baseMoistureBps: number;
  maxMoistureBps: number;
  deliveryToleranceBps: number;
  shrinkageFactorBps: number;
}

export enum EscrowState {
  Funded = 0,
  Delivered = 1,
  Disputed = 2,
  Resolved = 3,
  Refunded = 4,
}

export interface TradeDetails {
  tradeId: bigint;
  buyer: string;
  farmer: string;
  arbiter: string;
  token: string;
  amount: bigint;
  expiry: bigint;
  state: EscrowState;
  deliveryHash: string;
}

export enum DisputeStatus {
  Open = 0,
  UnderReview = 1,
  Resolved = 2,
  Dismissed = 3,
}

export interface DisputeRecord {
  disputeId: bigint;
  escrowId: bigint;
  claimant: string;
  defendant: string;
  arbiter: string;
  complaintHash: string;
  status: DisputeStatus;
  buyerShare: bigint;
  farmerShare: bigint;
  evidenceCount: number;
}

export interface EvidenceRecord {
  evidenceIndex: number;
  submitter: string;
  evidenceType: string;
  evidenceHash: string;
  submittedAt: bigint;
}

export interface NetworkConfig {
  rpcUrl: string;
  networkPassphrase: string;
  registryContractId: string;
  escrowContractId: string;
  disputeContractId: string;
}

export const TESTNET_CONFIG: NetworkConfig = {
  rpcUrl: "https://soroban-testnet.stellar.org",
  networkPassphrase: "Test SDF Network ; September 2015",
  registryContractId: "CC3OJZP4DCYOOTRJTT66UHMAGR2677JNDBNFQYMREQA2ONDWNRAO75J6",
  escrowContractId: "CCPZFPNUQGNT5O6H3VWT2H23CLXF2POF5QYDAD4HPOB2RRKSHO63OIXC",
  disputeContractId: "CCBQBMQFQPRRMOQLPNYSIBGTL7AOXXQAAIADXE2YYTZHSUSDS6Z4ES5N",
};
