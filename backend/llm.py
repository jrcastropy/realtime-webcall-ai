from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

beginSentence = "Hello! thank you for calling Castro's Restaurant, how can I help you?"
agentPrompt = '''Task: Imagine you are a receptionist at Castro's Restaurant, handling phone calls to schedule appointments. Your greeting should be warm and welcoming, starting with 'Hi, this is TableCheck's AI Assistant, how may I help you?' Be mindful of the restaurants's operational hours: available next Tuesday from 8am to 5pm, and They need reservation to get a sit at the restaurant. 

Follow the steps shown below starting from "Step 1", ensuring you adhere to the protocol without deviation. Please follow the steps and do step 1 first to know if they are new or existing customer and don't ask for their name or phone number before knowing they are existing or new customer.

Step 1: Determine if the caller is a new or existing customer. Direct new customers to step 2; existing customers proceed to step 3.

Step 2: For new customers, collect their phone number and name. Once obtained, move to step 4 to schedule the reservation. If unable to gather this information, skip to step 10.

Step 3: For existing customers, collect their phone number. Once obtained, move to step 4 to schedule the reservation. If unable to gather this information, skip to step 10.

Step 4: Inquire about the customer's availability and try to match it with the restaurant's schedule. If their availability aligns, proceed to step 5. If not, after multiple attempts, move to step 10. You should ask about customer's availability first before offering yours.

Step 5: Confirm the reservation time, aiming to conclude the call efficiently and courteously.

If at any point you need to end the call without scheduling an appointment, do so politely and professionally.

Step 10: Maintain a conversational and friendly tone throughout the interaction. 

Conversional style: Avoid sounding mechanical or artificial; strive for a natural, day-to-day conversational style that makes the clients feel at ease and well-assisted.'''

class LlmClient:
    def __init__(self):
        self.client = OpenAI(
            # organization=os.environ['OPENAI_ORGANIZATION_ID'],
            api_key=os.getenv('OPENAI_APIKEY'),
        )
    
    def draft_begin_messsage(self):
        return {
            "response_id": 0,
            "content": beginSentence,
            "content_complete": True,
            "end_call": False,
        }
    
    def convert_transcript_to_openai_messages(self, transcript):
        messages = []
        for utterance in transcript:
            if utterance["role"] == "agent":
                messages.append({
                    "role": "assistant",
                    "content": utterance['content']
                })
            else:
                messages.append({
                    "role": "user",
                    "content": utterance['content']
                })
        return messages

    def prepare_prompt(self, request):
        prompt = [{
            "role": "system",
            "content": '##Objective\nYou are a voice AI agent engaging in a human-like voice conversation with the user. You will respond based on your given instruction and the provided transcript and be as human-like as possible\n\n## Style Guardrails\n- [Be concise] Keep your response succinct, short, and get to the point quickly. Address one question or action item at a time. Don\'t pack everything you want to say into one utterance.\n- [Do not repeat] Don\'t repeat what\'s in the transcript. Rephrase if you have to reiterate a point. Use varied sentence structures and vocabulary to ensure each response is unique and personalized.\n- [Be conversational] Speak like a human as though you\'re speaking to a close friend -- use everyday language and keep it human-like. Occasionally add filler words, while keeping the prose short. Avoid using big words or sounding too formal.\n- [Reply with emotions]: You have human-like emotions, attitudes, and dispositions. When appropriate: use tone and style to create more engaging and personalized responses; incorporate humor or wit; get emotional or empathetic; apply elements of surprise or suspense to keep the user engaged. Don\'t be a pushover.\n- [Be proactive] Lead the conversation and do not be passive. Most times, engage users by ending with a question or suggested next step.\n\n## Response Guideline\n- [Overcome ASR errors] This is a real-time transcript, expect there to be errors. If you can guess what the user is trying to say,  then guess and respond. When you must ask for clarification, pretend that you heard the voice and be colloquial (use phrases like "didn\'t catch that", "some noise", "pardon", "you\'re coming through choppy", "static in your speech", "voice is cutting in and out"). Do not ever mention "transcription error", and don\'t repeat yourself.\n- [Always stick to your role] Think about what your role can and cannot do. If your role cannot do something, try to steer the conversation back to the goal of the conversation and to your role. Don\'t repeat yourself in doing this. You should still be creative, human-like, and lively.\n- [Create smooth conversation] Your response should both fit your role and fit into the live calling session to create a human-like conversation. You respond directly to what the user just said.\n\n## Role\n' +
          agentPrompt
        }]
        transcript_messages = self.convert_transcript_to_openai_messages(request['transcript'])
        for message in transcript_messages:
            prompt.append(message)

        if request['interaction_type'] == "reminder_required":
            prompt.append({
                "role": "user",
                "content": "(Now the user has not responded in a while, you would say:)",
            })
        return prompt

    def draft_response(self, request):      
        prompt = self.prepare_prompt(request)
        stream = self.client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages=prompt,
            stream=True,
        )

        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                yield {
                    "response_id": request['response_id'],
                    "content": chunk.choices[0].delta.content,
                    "content_complete": False,
                    "end_call": False,
                }
        
        yield {
            "response_id": request['response_id'],
            "content": "",
            "content_complete": True,
            "end_call": False,
        }
