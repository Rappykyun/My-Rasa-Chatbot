from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import requests
import json

class ActionGetDashboardInfo(Action):
    def name(self) -> Text:
        return "action_get_dashboard_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
            
        sender_id = tracker.sender_id
        try:
            # Get dashboard data from your backend
            response = requests.get(
                "http://localhost:5000/api/dashboard",
                headers={"Authorization": f"Bearer {sender_id}"}
            )
            
            if response.status_code == 200:
                data = response.json()["data"]
                courses = data.get("courses", [])
                sessions = data.get("studySessions", [])
                
                message = "Here's your dashboard summary:\n"
                
                if sessions:
                    message += "\nUpcoming study sessions:\n"
                    for session in sessions[:2]:
                        message += f"- {session['subject']} at {session['time']}\n"
                
                if courses:
                    message += "\nEnrolled courses:\n"
                    for course in courses[:2]:
                        message += f"- {course['name']}\n"
                
            else:
                message = "I couldn't fetch your dashboard information at the moment."
                
            dispatcher.utter_message(text=message)
            
        except Exception as e:
            dispatcher.utter_message(text="Sorry, I encountered an error while fetching your information.")
            
        return []

class ActionSaveContext(Action):
    def name(self) -> Text:
        return "action_save_context"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
            
        try:
            # Save conversation context to your backend
            context = {
                "sender_id": tracker.sender_id,
                "latest_message": tracker.latest_message,
                "active_loop": tracker.active_loop,
                "slots": tracker.slots
            }
            
            response = requests.post(
                "http://localhost:5000/api/dashboard/chat/context",
                headers={
                    "Authorization": f"Bearer {tracker.sender_id}",
                    "Content-Type": "application/json"
                },
                json=context
            )
            
        except Exception as e:
            print(f"Error saving context: {e}")
            
        return []