import React, { useEffect, useState } from "react";
import "./App.css";
import { RetellWebClient } from "retell-client-js-sdk";

interface RegisterCallResponse {
  call_id?: string;
  sample_rate: number;
}

interface GetAgentIDResponse {
  agent_id?: string;
}

const webClient = new RetellWebClient();

const App = () => {
  const [isCalling, setIsCalling] = useState(false);

  // Initialize the SDK
  useEffect(() => {
    // Setup event listeners
    webClient.on("conversationStarted", () => {
      console.log("conversationStarted");
    });

    webClient.on("audio", (audio: Uint8Array) => {
      console.log("There is audio");
    });

    webClient.on("conversationEnded", ({ code, reason }) => {
      console.log("Closed with code:", code, ", reason:", reason);
      setIsCalling(false); // Update button to "Start" when conversation ends
    });

    webClient.on("error", (error) => {
      console.error("An error occurred:", error);
      setIsCalling(false); // Update button to "Start" in case of error
    });

    webClient.on("update", (update) => {
      // Print live transcript as needed
      console.log("update", update);
    });
  }, []);

  const toggleConversation = async () => {
    if (isCalling) {
      webClient.stopConversation();
    } else {
      const registerCallResponse = await registerCall();
      if (registerCallResponse.call_id) {
        webClient
          .startConversation({
            callId: registerCallResponse.call_id,
            sampleRate: registerCallResponse.sample_rate,
            enableUpdate: true,
          })
          .catch(console.error);
        setIsCalling(true); // Update button to "Stop" when conversation starts
      }
    }
  };

  async function registerCall(): Promise<RegisterCallResponse> {
    try {
      // Replace with your server url
      const response = await fetch(
        "http://localhost:8000/get_call_details",
        {
          method: "GET",
        },
      );

      let callDetails: RegisterCallResponse = await response.json();
      console.log(callDetails)
      return callDetails;
    } catch (err) {
      console.log(err);
      throw new Error(err);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <button onClick={toggleConversation}>
          {isCalling ? "Stop the call" : "Start Calling JC Retaurant"}
        </button>
      </header>
    </div>
  );
};

export default App;
