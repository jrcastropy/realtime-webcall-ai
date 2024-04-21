import { useEffect, useState } from "react";
import "./App.css";
import { RetellWebClient } from "retell-client-js-sdk";
import 'bootstrap/dist/css/bootstrap.min.css';
import { Container, Row, Col, Image, Button } from "react-bootstrap";
import { TelephoneFill, TelephoneX } from "react-bootstrap-icons";

interface RegisterCallResponse {
  call_id?: string;
  sample_rate: number;
}

type conversationEndedType =  {
  code: string,
  reason: string
}

interface WordData {
  word: string;
  start: number;
  end: number;
}

const webClient = new RetellWebClient();

const App = () => {
  const [isCalling, setIsCalling] = useState(false);
  const [buttonVariant, setButtonVariant] = useState("success");
  const [teleIcon, setTeleIcon] = useState(<TelephoneFill size={30} />);
  const [transcript, setTranscript] = useState("");

  // Initialize the SDK
  useEffect(() => {
    // Setup event listeners
    webClient.on("conversationStarted", () => {
      console.log("conversationStarted");
    });

    webClient.on("audio", (audio: Uint8Array) => {
      console.log("There is audio");
    });

    webClient.on("conversationEnded", ( convEnded: conversationEndedType ) => {
      console.log("Closed with code:", convEnded.code, ", reason:", convEnded.reason);
      setIsCalling(false); // Update button to "Start" when conversation ends
    });

    webClient.on("error", (error: any) => {
      console.error("An error occurred:", error);
      setIsCalling(false); // Update button to "Start" in case of error
    });

    webClient.on("update", (update: any) => {
      update = update.transcript[update.transcript.length - 1]
      console.log("update", update.content);
      setTranscript(update.role == 'user'? 'Customer: ' + update.content : 'Assistant: ' + update.content)
    });
  }, []);

  const toggleConversation = async () => {
    if (isCalling) {
      webClient.stopConversation();
      setButtonVariant('success')
      setTeleIcon(<TelephoneFill size={30} />)
      setIsCalling(false);
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
        setButtonVariant('danger')
        setTeleIcon(<TelephoneX size={30} />) 
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
    } catch (err : any) {
      console.log(err);
      throw new Error(err);
    }
  };

  return (
    <>
      <div className="App">
        <Container fluid>
              <Row className="aligh-items-center justify-content-center vh-100">
                <Col xs={12} md={5} xl={4} className="m-md-auto mt-3 p-4 padCustom rounded rounded-5 align-items-center justify-content-center">
                    <div className="bg-dark text-white rounded rounded-5 align-items-center justify-content-center d-flex flex-column">
                        <h3 className="my-5">Castro's Restaurant</h3>
                        <Image className={isCalling ? "glowing my-3" : "my-3" } src="https://placehold.jp/300x300.png" roundedCircle fluid />
                        <h4 className="mt-3 mb-0">Alloy</h4>
                        <p>AI Assistant</p>
                        <div className="my-5 d-flex">
                          <Button variant={buttonVariant} size="lg" className="btn-block btn-lg px-5" onClick={toggleConversation}>
                            {teleIcon}
                          </Button>
                        </div>
                    </div>
                </Col>
                <Col xs={12} md={5} xl={6} className="chatBox m-md-auto mt-3 padCustom rounded rounded-5 align-items-center justify-content-center text-center text-white">
                  <h3 className="my-3">Transcript</h3>
                  <div className="innerChatBox p-3 bg-dark rounded rounded-3 d-flex flex-column">
                    {transcript}
                  </div>
                </Col>
              </Row>
          </Container>
      </div>    
    </>
  );
};

export default App;
