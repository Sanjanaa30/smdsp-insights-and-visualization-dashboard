"use client";
import { CopilotKit } from "@copilotkit/react-core";
import { CopilotPopup } from "@copilotkit/react-ui";

const ChatWrapper = () => {
  // useCopilotChatSuggestions(
  //   {
  //     available: "enabled",
  //     instructions: "SUGGESTIONS_PROMPT",
  //     maxSuggestions: 3,
  //   },
  //   []
  // );

  return (
    <CopilotPopup
      labels={{
        title: "Your Assistant",
        initial: "Hi! 👋 How can I assist you today?",
      }}
      // onSubmitMessage={handleSubmitMessage}
    />
  );
};

const CopilotWrapper = ({ children }) => {
  return (
    <CopilotKit
      runtimeUrl={process.env.NEXT_PUBLIC_COPILOT_RUNTIME_URL}
      showDevConsole={false}
      agent="sql_agent"
    >
      <ChatWrapper />
      {children}
    </CopilotKit>
  );
};

export default CopilotWrapper;
