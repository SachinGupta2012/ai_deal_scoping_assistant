import type { IconName } from "../components/Icon";

export type SessionStatus = "In Progress" | "Completed" | "Needs Review" | "Not Started";

export type SessionSummary = {
  id: string;
  name: string;
  subtitle: string;
  customer: string;
  opportunity: string;
  engagementType: string;
  status: SessionStatus;
  progress: number;
  updated: string;
  owner: string;
  ownerInitials: string;
};

export const scenarios = [
  { name: "Retail Banking Modernization", tag: "RFP", text: "Core banking platform upgrade with digital channels, cloud migration and enhanced customer experience.", icon: "dashboard" as IconName },
  { name: "Insurance Claims Platform", tag: "Discovery Call", text: "End-to-end claims processing platform with AI-assisted fraud detection and legacy integrations.", icon: "shield" as IconName },
  { name: "E-commerce Platform", tag: "Internal Initiative", text: "Scalable e-commerce solution with personalization, recommendation engine and multi-region deployment.", icon: "sessions" as IconName },
  { name: "Healthcare Data Platform", tag: "RFP", text: "Patient data integration, analytics platform and regulatory compliance requirements.", icon: "data" as IconName },
];
