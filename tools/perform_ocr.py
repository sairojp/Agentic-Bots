
import os
from termcolor import colored
import json
from states.state import AgentGraphState
import easyocr



def perform_ocr(state: AgentGraphState, image_info):

    # image_path = image_info[-1].content

    try:
        # Initialize the EasyOCR reader
        reader = easyocr.Reader(['en'])  # 'en' is for English. Add more languages if needed.

        # Path to the image file
        image_path = 'uploaded_images/ocr.png'  # Replace with your image file path

        # Perform OCR
        results = reader.readtext(image_path)

        formatted_results = []
        for (bbox, text, confidence) in results:
            formatted_results.append({
                "DetectedText": text,
                "Confidence": round(confidence, 2)
            })
        # Convert to JSON format for easy transfer and readability
        output_json = json.dumps({"OCR_Results": formatted_results}, indent=4)
        print(colored(f"Planner: {output_json}", "cyan"))

        # Delete the image after processing OCR
        if os.path.exists(image_path):
            os.remove(image_path)
            print(colored(f"Image {image_path} deleted after OCR.", "green"))

        state = {**state, "ocr_response": output_json}
        return state
    except Exception as e:
        image_path = 'uploaded_images/ocr.png'
        print(f"An error occurred: {e}")
        if os.path.exists(image_path):
            os.remove(image_path)
            print(colored(f"Image {image_path} deleted after OCR.", "green"))
        return {**state, "ocr_response": f"Error occurred: {e}"}
