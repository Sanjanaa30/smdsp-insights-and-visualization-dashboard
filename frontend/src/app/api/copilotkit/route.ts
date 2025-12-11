import {
  CopilotRuntime,
  OpenAIAdapter,
  copilotRuntimeNextJSAppRouterEndpoint,
} from "@copilotkit/runtime";
import OpenAI from "openai";
import { NextRequest } from "next/server";

const openai = new OpenAI({
  apiKey: "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",
});
const serviceAdapter = new OpenAIAdapter({ openai, model: "gpt-4.1-mini" } as any);
const runtime = new CopilotRuntime({
  remoteEndpoints: [
    {
      url:
        process.env.NEXT_PUBLIC_COPILOT_ENDOINT ||
        "http://localhost:8000/copilotkit",
    },
  ],
});

export const POST = async (req: NextRequest) => {
  const { handleRequest } = copilotRuntimeNextJSAppRouterEndpoint({
    runtime,
    serviceAdapter,
    endpoint: process.env.NEXT_PUBLIC_COPILOT_RUNTIME_URL || "/api/copilotkit",
  });

  return handleRequest(req);
};
