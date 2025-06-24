import { type DeerFlowConfig } from "../config/types";

import { resolveServiceURL } from "./resolve-service-url";

declare global {
  interface Window {
    __deerflowConfig: DeerFlowConfig;
  }
}

export async function loadConfig(): Promise<DeerFlowConfig> {
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

export function getConfig(): DeerFlowConfig {
  if (
    typeof window === "undefined" ||
    typeof window.__deerflowConfig === "undefined"
  ) {
    throw new Error("Config not loaded");
  }
  return window.__deerflowConfig;
}
