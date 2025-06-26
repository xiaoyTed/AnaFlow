import { type AnaFlowConfig } from "../config/types";

import { resolveServiceURL } from "./resolve-service-url";

declare global {
  interface Window {
    __anaFlowConfig: AnaFlowConfig;
  }
}

export async function loadConfig(): Promise<AnaFlowConfig> {
  try {
    const res = await fetch(resolveServiceURL("./config"));
    if (!res.ok) {
      throw new Error(`Failed to fetch config: ${res.status}`);
    }
    const config = await res.json();
    return config;
  } catch (error) {
    // During build time or when API server is not available, return default config
    console.warn("Failed to load config from API, using default configuration:", error);
    return {
      rag: {
        provider: "default"
      },
      models: {
        basic: [],
        reasoning: []
      }
    };
  }
}

export function getConfig(): AnaFlowConfig {
  if (
    typeof window === "undefined" ||
    typeof window.__anaFlowConfig === "undefined"
  ) {
    throw new Error("Config not loaded");
  }
  return window.__anaFlowConfig;
}
