// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

import { env } from "~/env";

export function resolveServiceURL(path: string) {
  let BASE_URL = "http://192.168.31.194:8000/api/";
  if (!BASE_URL.endsWith("/")) {
    BASE_URL += "/";
  }
  return new URL(path, BASE_URL).toString();
}
