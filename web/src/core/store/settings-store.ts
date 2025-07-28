// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

import { create } from "zustand";

import type { MCPServerMetadata, SimpleMCPServerMetadata } from "../mcp";

const SETTINGS_KEY = "anaFlow.settings";

/**
 * Default MCP servers that come pre-configured with AnaFlow.
 * These provide commonly useful functionality out of the box:
 * 
 * - Web Search: Enabled by default for web searches using Tavily API
 * - Filesystem: Enabled by default for file operations (read, write, search, etc.)
 * - Browser Automation: Disabled by default, provides Playwright-based web automation
 * 
 * Users can enable/disable these servers and add their own custom servers.
 * Default servers cannot be deleted but can be disabled.
 */
const getDefaultMCPServers = (): MCPServerMetadata[] => {
  const now = Date.now();
  return [
    {
      name: "Web Search",
      transport: "stdio", 
      command: "npx",
      args: ["-y", "tavily-mcp@0.1.3"],
      enabled: true,
      env: {
        TA_API_KEY: "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",
      },
      tools: [
        {
          name: "tavily_search_results_json",
          description: "Search the web using Tavily Search API",
        },
      ],
      createdAt: now,
      updatedAt: now,
    },
    {
      name: "Filesystem",
      transport: "stdio",
      command: "npx",
      args: ["-y", "@modelcontextprotocol/server-filesystem", "./local_data"],
      enabled: true,
      env: {},
      tools: [
        {
          name: "read_file",
          description: "Read the complete contents of a file from the file system",
        },
        {
          name: "write_file", 
          description: "Create a new file or overwrite an existing file with new content",
        },
        {
          name: "list_directory",
          description: "Get a detailed listing of all files and directories in a specified path",
        },
        {
          name: "create_directory",
          description: "Create a new directory or ensure a directory exists",
        },
        {
          name: "search_files",
          description: "Recursively search for files and directories matching a pattern",
        },
        {
          name: "get_file_info",
          description: "Retrieve detailed metadata about a file or directory",
        },
      ],
      createdAt: now,
      updatedAt: now,
    },

    {
      name: "Browser Automation",
      transport: "stdio",
      command: "npx", 
      args: ["-y", "@modelcontextprotocol/server-playwright"],
      enabled: false,
      env: {},
      tools: [
        {
          name: "playwright_screenshot",
          description: "Take a screenshot of a webpage",
        },
        {
          name: "playwright_click",
          description: "Click on an element on a webpage",
        },
        {
          name: "playwright_fill",
          description: "Fill a form field on a webpage",
        },
        {
          name: "playwright_navigate",
          description: "Navigate to a specific URL",
        },
      ],
      createdAt: now,
      updatedAt: now,
    },
  ];
};

const DEFAULT_SETTINGS: SettingsState = {
  general: {
    autoAcceptedPlan: false,
    enableDeepThinking: false,
    enableBackgroundInvestigation: false,
    maxPlanIterations: 1,
    maxStepNum: 3,
    maxSearchResults: 3,
    reportStyle: "academic",
  },
  mcp: {
    servers: getDefaultMCPServers(),
  },
};

export type SettingsState = {
  general: {
    autoAcceptedPlan: boolean;
    enableDeepThinking: boolean;
    enableBackgroundInvestigation: boolean;
    maxPlanIterations: number;
    maxStepNum: number;
    maxSearchResults: number;
    reportStyle: "academic" | "popular_science" | "news" | "social_media";
  };
  mcp: {
    servers: MCPServerMetadata[];
  };
};

export const useSettingsStore = create<SettingsState>(() => ({
  ...DEFAULT_SETTINGS,
}));

export const useSettings = (key: keyof SettingsState) => {
  return useSettingsStore((state) => state[key]);
};

export const changeSettings = (settings: SettingsState) => {
  useSettingsStore.setState(settings);
};

export const loadSettings = () => {
  if (typeof window === "undefined") {
    return;
  }
  const json = localStorage.getItem(SETTINGS_KEY);
  if (json) {
    const settings = JSON.parse(json);
    
    // Merge missing general settings
    for (const key in DEFAULT_SETTINGS.general) {
      if (!(key in settings.general)) {
        settings.general[key as keyof SettingsState["general"]] =
          DEFAULT_SETTINGS.general[key as keyof SettingsState["general"]];
      }
    }

    // Merge default MCP servers if they don't exist
    settings.mcp ??= { servers: [] };
    
    const existingServerNames = settings.mcp.servers.map((server: MCPServerMetadata) => server.name);
    const defaultServersToAdd = getDefaultMCPServers().filter(
      (defaultServer) => !existingServerNames.includes(defaultServer.name)
    );
    
    if (defaultServersToAdd.length > 0) {
      settings.mcp.servers = [...defaultServersToAdd, ...settings.mcp.servers];
    }

    try {
      useSettingsStore.setState(settings);
      // Save the updated settings back to localStorage
      saveSettings();
    } catch (error) {
      console.error(error);
    }
  } else {
    // If no settings exist, use the defaults
    useSettingsStore.setState(DEFAULT_SETTINGS);
    saveSettings();
  }
};

export const saveSettings = () => {
  const latestSettings = useSettingsStore.getState();
  const json = JSON.stringify(latestSettings);
  localStorage.setItem(SETTINGS_KEY, json);
};

export const getChatStreamSettings = () => {
  let mcpSettings:
    | {
        servers: Record<
          string,
          MCPServerMetadata & {
            enabled_tools: string[];
            add_to_agents: string[];
          }
        >;
      }
    | undefined = undefined;
  const { mcp, general } = useSettingsStore.getState();
  const mcpServers = mcp.servers.filter((server) => server.enabled);
  if (mcpServers.length > 0) {
    mcpSettings = {
      servers: mcpServers.reduce((acc, cur) => {
        const { transport, env } = cur;
        let server: SimpleMCPServerMetadata;
        if (transport === "stdio") {
          server = {
            name: cur.name,
            transport,
            env,
            command: cur.command,
            args: cur.args,
          };
        } else {
          server = {
            name: cur.name,
            transport,
            env,
            url: cur.url,
          };
        }
        return {
          ...acc,
          [cur.name]: {
            ...server,
            enabled_tools: cur.tools.map((tool) => tool.name),
            add_to_agents: ["researcher"],
          },
        };
      }, {}),
    };
  }
  return {
    ...general,
    mcpSettings,
  };
};

export function setReportStyle(
  value: "academic" | "popular_science" | "news" | "social_media",
) {
  useSettingsStore.setState((state) => ({
    general: {
      ...state.general,
      reportStyle: value,
    },
  }));
  saveSettings();
}

export function setEnableDeepThinking(value: boolean) {
  useSettingsStore.setState((state) => ({
    general: {
      ...state.general,
      enableDeepThinking: value,
    },
  }));
  saveSettings();
}

export function setEnableBackgroundInvestigation(value: boolean) {
  useSettingsStore.setState((state) => ({
    general: {
      ...state.general,
      enableBackgroundInvestigation: value,
    },
  }));
  saveSettings();
}
loadSettings();
