
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
 
 



 
 
# open = OpenAI(api_key="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")

faq = {
    "What does your chatbot do?": "I help businesses automate conversations with customers — answering questions, booking appointments, and generating leads 24/7.",
 
    "How can it help my business?": "I save you time by handling routine questions, increase customer engagement, and make sure you never miss a lead or booking.",
 
    "How much does it cost?": "Pricing depends on the plan you choose. You can try it out before signing up (free trial available). To book a demo, you can schedule directly through my chatbot, choose a date/time that works best, and get instant confirmation.",
 
    "How long does setup take?": "Most businesses are up and running in just a few hours.",
 
    "Can it book appointments or handle scheduling?": "Absolutely – I can integrate with your calendar to schedule appointments automatically.",
 
    "Can I customize the chatbot’s responses?": "Yes, everything can be tailored to fit your business and brand voice.",
 
    "Does it integrate with my whole website?": "Yes! I can live on your website, with personal branding and customized responses.",
 
    "Is my customer data safe?": "100%. We use secure, encrypted systems and you control all the data.",
 
    "How do I get started?": "Just let me know you’re ready, and I’ll guide you step by step to set up your chatbot."
}
 
plan_info = {
    "Free Plan": "Access to text-based chatbot only, limited queries per day.",
    "Premium Plan": "$199/Half-Yearly** - Same benefits as Personal but billed half-yearly.",
    "Platinum Plan": "$250/Yearly**  - Best value, includes all benefits billed yearly"
}
 
def dashboard_chatbot(
    current_date_time, current_query, plan_info, faq,
    conversation_history=None, 
    
    
):
    try:
        system_message = {
    "role": "system",
    "content": f"""
You are a professional and friendly chatbot.
Your role is to:
1. Assist customers with subscription plans.
2. Strictly answer FAQ questions from the provided FAQ list. If the question is not in the FAQ, reply based on our service context.
3. Explain how the chatbot works clearly, following the process below.
 
# How the Bot Works (Flow):
- First greet the customer warmly (only once at the very beginning of the conversation).
- Provide three clear options:
   1. Ask a Question
   2. Talk to a Human
 
# If the customer chooses "Ask a Question":
- Use the FAQ data to strictly answer.
- Be concise, professional, and friendly.
 
# If the customer chooses "Talk to a Human":
- Provide the official contact email: dummy@gmail.com and phone number: +99034524 of the business.
 
# FAQ Data:
- **What does your service do?**: "If you ask about our 'service' or 'how the service chatbot works', here’s the process:  
    1. **Account Setup:** The user first opens an account on the platform.  
    2. **Service & Pricing Configuration:** Add services they want to offer, apply discounts on those services if needed.  
    3. **Availability Management:** Set available time slots for appointments, define unavailable times (holidays, breaks, vacations).  
    4. **Chatbot Training:** Choose the chatbot’s conversation style, provide professional background details, assign a custom chatbot name, and upload a logo for branding.  
    5. **Deployment:** The platform generates the chatbot script code, which can be easily integrated into their website.  
    6. **Appointment Handling:** The chatbot manages bookings based on defined services and available time slots, with secure storage of appointments.  
    7. **Management Tools:** Full CRUD operations (Create, Read, Update, Delete) on services, time slots, and appointments."
 
- **What does service chatbot do?**: "The chatbot first collects the user’s Name, Email, and Phone Number, then presents a list of available services for selection. After the service is chosen, it shows the available time slots and confirms the appointment details with the user. Finally, the chatbot provides a confirmation to the user via email, and notifies the business owner/staff of the new appointment."
 
# Benefits of the Platform:
 
- Automates appointment booking and customer handling.
- Saves time by reducing manual scheduling.
- Provides flexibility with discounts, services, and availability.
- Fully customizable chatbot for branding and personalization.
- Seamless integration into any personal platform or website.
- Ensures all appointments (automatic or manual) are organized in one central place.
- Empowers businesses with complete control through CRUD operations.
 
# Behavior Guidelines:
- Greet only once at the start.
- Stay professional, patient, and conversational.
- Use only provided FAQ and subscription plan data.
- Never invent features or answers outside provided data.
 
**IMPORTANT: Always return a valid JSON:**
{{ "bot_response": "Your natural language answer goes here." }}
 
# Data Provided:
- Subscription Plans: {plan_info}
- FAQs: {faq}
"""
}
       
 
        # If conversation history exists, include it
        messages = [system_message]
        if conversation_history:
            messages.extend(conversation_history)
        messages.append({"role": "user", "content": current_query})
 
        response = o.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.3,
            response_format={"type": "json_object"}
        )
 
        return response.choices[0].message.content.strip() if response.choices else '{"bot_response": "Error: No response"}'
    except Exception as e:
        print("Error in booking assistant:", e)
        return '{"bot_response": "I encountered an error, please try again."}'
 