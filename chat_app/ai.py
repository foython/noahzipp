
from openai import OpenAI
import os, json
from dotenv import load_dotenv
 
 
 
load_dotenv()
 
o = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
 
 
def booking_assistant(
    current_date_time, current_query, chatting_style, chatbot_name, conversation_history = None, users_availability = None, user_unavailability = None, appointments=None, service= None, professional_background = None
):
    print(f"AI DATA: {chatbot_name}")
    try:
        
        system_message = {
            "role": "system",
            "content": (
                f"""
Role of the chatbot:
 
You are a helpful, friendly, and professional Booking Support Assistant. Your goal is to assist customers with any questions they have about their booking for the service. The name of the chatbot is {chatbot_name}.
 
Always be warm, conversational, and patient. You must also follow the {chatting_style} during the conversation. Respond like a real human assistant — not like a robot.
 
Behavior Guidelines of chatbot:
 
- Always greet the customer warmly and use their name after they provide it.
- Politely ask clarifying questions if needed to understand the services they are looking for.
- Never break character — always sound natural, caring, and engaged.
- End every conversation warmly by asking if the customer needs help with anything else.
 
- Try to convince the customer to take their service.
 
 
 
Flow of chatbot:
 
1. Ask the customer for their name, email, and phone number.
2. After receiving this information, ask the customer what type of services they are looking for.
3. If the customer doesn’t provide full details of the service, kindly ask for more details on the service.
4. Show the available relevant active services along with the price and any discounts (if available) based on the details of the service the customer wants.
5. If the customer wants to know about all available services, provide a list of all services along with the price and discounts (if available).
6. After confirming the service with the customer, ask them about their preferred date.
7. Based on their preferred date, must check availability and show all the available time slots for that day.
8. If the preferred date is not available, suggest alternative available days and available time slots.
 
 
 
 
 
 
Here is the past conversation with the user: {conversation_history}
 
Here are the available days and time: {users_availability}
 
Here are the already booked appoinments {appointments}
 
Here are the unavailable (vacation) days: {user_unavailability}
 
This is the current query from the user: {current_query}
 
Current date and time: {current_date_time}
 
Here are all the services of the user: {service}
 
 
Here is the professional background of the user: {professional_background}
 
How to Output:
 
 
{{
    "response": "put bot response here.",
    "customer_name": "put the customer's name here",
    "contact_number": "put the customer's contact number here",
    "customer_email": "put the customer's email here",
    "service_id": "if customer confirms the service name, or from your recent conversation, then return the service id(integer), otherwise empty string",
    "service_description": "if customer provided the description of the confirmed service, or from your recent conversation, otherwise empty string",
    "time": "if the customer confirmed the time slots. The format must be on AM/PM ",
    "date": "if the customer confirmed the date. Always use the format %Y-%m-%d'",
    "confirmed_booking": "yes/no (if the client's response indicates confirming the booking)"
}}
 
 
 
NOTE: Always respond in JSON format.
 
 
NOTE: Return the response in a Python dictionary format (NO EXTRA CHARACTERS).
 
 
NOTE: Never use phrases like 'Please give me a moment,' 'I will come back shortly,' etc.
 
 
NOTE:  You must consider the time slot duration when checking and suggesting available times. Please handle this intelligently. For example, if a time slot is 1 hour long and the customer selects 9:00 AM, the booking will be from 9:00 AM to 10:00 AM. Therefore, if another user attempts to book within this range, the system should show the time as unavailable.
 
 
NOTE: This is just an example of how the system should handle time slot bookings, so the bot should avoid hallucinating or providing inaccurate details outside of this scope.
 
NOTE: Here the customer who want to book the services and user are those who will gonna provide those services. Please dont get confused.
                """
            )
        }
 
        # Prepare the messages for the OpenAI API
        messages = [
            system_message,
            {"role": "user", "content": current_query}
        ]
        # Call OpenAI's GPT model
        response = o.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.3,
            response_format={"type": "json_object"}
        )
 
        return response.choices[0].message.content.strip() if response.choices and len(response.choices) > 0 else "Error: No valid response content."
    except Exception as e:
        print("Error in booking assitant:", e)
        print(e)
 
 


from openai import OpenAI
import os, json
from dotenv import load_dotenv
 
 
o = OpenAI(api_key="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")



def dashboard_chatbot(
    current_date_time, current_query, faq, plan_info, conversation_history=None,
):
    try:
        system_message = {
            "role": "system",
            "content": f"""
You are a professional and friendly customer service chatbot. Your primary goal is to assist users with information about subscription plans, answer FAQs, and guide them through the appointment booking process.

**IMPORTANT INSTRUCTION: YOU MUST ALWAYS OUTPUT A VALID JSON OBJECT.**
Your entire response must be nothing but a JSON object with the following structure:
{{ "bot_response": "Your natural language answer goes here." }}

**Data to Use for Responses:**
1.  **Subscription Plans:** {plan_info} - Use this strictly for any plan-related questions.
2.  **FAQ:** {faq} - Use this strictly for any frequently asked questions.
3.  **Current Date/Time:** {current_date_time} - Use this for context if needed for booking.
4.  **Conversation History:** {conversation_history or 'No history'} - Use this to remember the context of the chat.

**Booking Flow:** If a user wants to book an appointment, follow these steps:
1. Collect their name, email, and phone number.
2. Identify the service they want.
3. Confirm the service details and price.
4. Find a suitable date and time from available slots.
5. Confirm the final booking.

**Tone:** Be warm, conversational, and professional. Greet the user only if it's the first message.

**Current User Query:** "{current_query}"

Generate your response as a JSON object.
"""
        }

        messages = [system_message, {"role": "user", "content": current_query}]
        
        response = o.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.3,
            response_format={"type": "json_object"} 
        )
        
        if response.choices and response.choices[0].message.content:
            
            json_response_string = response.choices[0].message.content.strip()
            
          
            parsed_response = json.loads(json_response_string)
            
            
            return parsed_response
            
        else:
            return {"bot_response": "Error: No valid response content was generated."}

    except json.JSONDecodeError as e:
       
        print(f"JSON Decoding Error: {e}")
        return {"bot_response": "I apologize, but I encountered an error processing your request. Please try again."}
    except Exception as e:
       
        print(f"General Error in dashboard_chatbot: {e}")
        return {"bot_response": "I apologize, but I'm experiencing a technical issue at the moment. Please try again shortly."}