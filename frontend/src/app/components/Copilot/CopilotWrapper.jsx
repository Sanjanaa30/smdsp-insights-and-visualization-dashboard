"use client";
import "@copilotkit/react-ui/styles.css";
import { CopilotKit } from "@copilotkit/react-core";
import { CopilotPopup } from "@copilotkit/react-ui";
export default function CopilotWrapper() {
  return (
    <CopilotKit
      runtimeUrl={process.env.NEXT_PUBLIC_COPILOT_RUNTIME_URL}
      agent={"sql_agent"}
    >
      <div className="flex justify-center items-center h-screen w-screen">
        <div className="w-8/10 h-8/10">
          <CopilotPopup
            className="h-full rounded-lg"
            labels={{ initial: "initialPrompt.humanInTheLoop" }}
          />
        </div>
      </div>
    </CopilotKit>
  );
}
