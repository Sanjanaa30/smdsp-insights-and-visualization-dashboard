import {
  CopilotRuntime,
  OpenAIAdapter,
  copilotRuntimeNextJSAppRouterEndpoint,
} from "@copilotkit/runtime";
import OpenAI from "openai";
import { NextRequest } from "next/server";

const openai = new OpenAI({
  baseURL: process.env.NEXT_PUBLIC_CHATGPT_BASE_URL,
  apiKey: process.env.NEXT_PUBLIC_CHATGPT_API_KEY,
});
const serviceAdapter = new OpenAIAdapter({ openai, model: "o3" } as any);
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
