// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

import { motion } from "framer-motion";

import { cn } from "~/lib/utils";

export function Welcome({ className }: { className?: string }) {
  return (
    <motion.div
      className={cn("flex flex-col", className)}
      style={{ transition: "all 0.2s ease-out" }}
      initial={{ opacity: 0, scale: 0.85 }}
      animate={{ opacity: 1, scale: 1 }}
    >
      <h3 className="mb-2 text-center text-3xl font-medium">
        👋 你好!
      </h3>
      <div className="text-muted-foreground px-4 text-center text-lg">
        AnaFlow, 欢迎使用，我是你的汽车销量预测助手，你可以向我提问关于汽车销量的问题，我会根据你的要求进行预测。
      </div>
    </motion.div>
  );
}
