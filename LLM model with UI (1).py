import tkinter as tk
from tkinter import messagebox, scrolledtext, font
import openai
import pandas as pd

# Load the datasets
description_df = pd.read_csv('description.csv')
diets_df = pd.read_csv('diets.csv')
medications_df = pd.read_csv('medications.csv')
precautions_df = pd.read_csv('precautions_df.csv')
workout_df = pd.read_csv('workout_df.csv')
symptoms_df = pd.read_csv('symtoms_df.csv')

# Replace underscores with spaces in symptom columns
symptoms_df['Symptom_1'] = symptoms_df['Symptom_1'].str.replace('_', ' ')
symptoms_df['Symptom_2'] = symptoms_df['Symptom_2'].str.replace('_', ' ')
symptoms_df['Symptom_3'] = symptoms_df['Symptom_3'].str.replace('_', ' ')
symptoms_df['Symptom_4'] = symptoms_df['Symptom_4'].str.replace('_', ' ')

# Rename the 'disease' column in workout_df to 'Disease' for consistency
workout_df.rename(columns={'disease': 'Disease'}, inplace=True)

# Merge datasets
merged_df = symptoms_df.merge(description_df, on='Disease', how='left')
merged_df = merged_df.merge(diets_df, on='Disease', how='left')
merged_df = merged_df.merge(medications_df, on='Disease', how='left')
merged_df = merged_df.merge(precautions_df, on='Disease', how='left')
merged_df = merged_df.merge(workout_df[['Disease', 'workout']], on='Disease', how='left')

# OpenAI API Key
openai.api_key = 'your-openai-api-key'

# Function to query OpenAI LLM
def query_llm(prompt):
    response = openai.Completion.create(
        engine="text-davinci-003",  # Adjust based on the model you use
        prompt=prompt,
        max_tokens=500,
        temperature=0.7
    )
    return response.choices[0].text.strip()

# Function to get recommendations from the dataset (handles symptoms with spaces)
def get_recommendations_from_data(symptom_input):
    # Convert the user input into a list of symptoms (stripping extra spaces and making it lowercase)
    symptoms = [sym.strip().lower() for sym in symptom_input.split(",")]
    
    # Filter diseases that have any of the input symptoms
    relevant_diseases = merged_df[
        merged_df.apply(lambda row: any(symptom in [str(row['Symptom_1']).strip().lower(),
                                                    str(row['Symptom_2']).strip().lower(),
                                                    str(row['Symptom_3']).strip().lower(),
                                                    str(row['Symptom_4']).strip().lower()]
                        for symptom in symptoms), axis=1)
    ]
    
    if relevant_diseases.empty:
        return "No matching diseases found for the given symptoms."
    
    # Return the first matching disease (or expand for multiple diseases if needed)
    result = relevant_diseases.iloc[0]
    output = {
        "Disease": result['Disease'],
        "Description": result['Description'],
        "Diet": result['Diet'],
        "Medication": result['Medication'],
        "Precautions": [result['Precaution_1'], result['Precaution_2'], result['Precaution_3'], result['Precaution_4']],
        "Workout": result['workout'],
        "Symptoms": [result['Symptom_1'], result['Symptom_2'], result['Symptom_3'], result['Symptom_4']]
    }
    return output

# Function to generate recommendation from the LLM if no match is found in the dataset
def generate_llm_recommendation(symptom_input):
    structured_data = get_recommendations_from_data(symptom_input)

    if isinstance(structured_data, str):
        # If no match found in the dataset, query the LLM
        prompt = f"Based on the symptoms: {symptom_input}, what could be the potential disease, its description, diet, medication, precautions, and workout?"
        llm_response = query_llm(prompt)
        return {"LLM Response": llm_response}
    else:
        return structured_data

# Tkinter GUI setup
def on_submit():
    symptoms = entry.get()
    if symptoms.strip():
        # Get the recommendation
        recommendations = generate_llm_recommendation(symptoms)
        
        # Clear previous output
        disease_label.config(text="")
        description_box.config(state=tk.NORMAL)
        description_box.delete(1.0, tk.END)
        diet_box.config(state=tk.NORMAL)
        diet_box.delete(1.0, tk.END)
        medication_box.config(state=tk.NORMAL)
        medication_box.delete(1.0, tk.END)
        precautions_box.config(state=tk.NORMAL)
        precautions_box.delete(1.0, tk.END)
        workout_box.config(state=tk.NORMAL)
        workout_box.delete(1.0, tk.END)
        
        if isinstance(recommendations, dict):
            if 'LLM Response' in recommendations:
                description_box.insert(tk.END, recommendations['LLM Response'])
            else:
                disease_label.config(text=recommendations['Disease'])
                description_box.insert(tk.END, recommendations['Description'])
                diet_box.insert(tk.END, recommendations['Diet'])
                medication_box.insert(tk.END, recommendations['Medication'])
                precautions_box.insert(tk.END, ', '.join(recommendations['Precautions']))
                workout_box.insert(tk.END, recommendations['Workout'])
        else:
            messagebox.showinfo("Error", recommendations)
        
        # Disable text boxes after writing
        description_box.config(state=tk.DISABLED)
        diet_box.config(state=tk.DISABLED)
        medication_box.config(state=tk.DISABLED)
        precautions_box.config(state=tk.DISABLED)
        workout_box.config(state=tk.DISABLED)
    else:
        messagebox.showinfo("Input Error", "Please enter symptoms separated by commas.")

# Main window
root = tk.Tk()
root.title("Medicine Recommendation System")

# Enlarging the window size
root.geometry("1000x800")

# Font styles
header_font = font.Font(family="Helvetica", size=16, weight="bold")
body_font = font.Font(family="Helvetica", size=14)

# High contrast colors
section_bg = "#e0e0e0"  # Light gray background for sections
input_bg = "#ffcccc"    # Light red background for input section
button_bg = "#ff9999"   # Darker red for the submit button
output_bg = "#ffffff"   # White background for output areas
text_color = "#000000"  # Black text for high contrast

# Input label and entry box
label = tk.Label(root, text="Enter symptoms separated by commas:", font=header_font, bg=input_bg, fg=text_color)
label.pack(pady=10, padx=10, fill="x")

entry = tk.Entry(root, width=60, font=body_font, bg=section_bg, fg=text_color)
entry.pack(pady=10, padx=10)

# Submit button
submit_btn = tk.Button(root, text="Submit", command=on_submit, font=body_font, bg=button_bg, fg=text_color)
submit_btn.pack(pady=10)

# Frames for each section with background colors
disease_frame = tk.LabelFrame(root, text="Disease", font=header_font, bg=section_bg, fg=text_color, padx=10, pady=10)
disease_frame.pack(fill="both", expand="yes", padx=20, pady=10)
disease_label = tk.Label(disease_frame, text="", font=body_font, bg=section_bg, fg=text_color)
disease_label.pack()

description_frame = tk.LabelFrame(root, text="Description", font=header_font, bg=section_bg, fg=text_color, padx=10, pady=10)
description_frame.pack(fill="both", expand="yes", padx=20, pady=10)
description_box = scrolledtext.ScrolledText(description_frame, height=5, wrap=tk.WORD, font=body_font, bg=output_bg, fg=text_color)
description_box.pack()

diet_frame = tk.LabelFrame(root, text="Diet", font=header_font, bg=section_bg, fg=text_color, padx=10, pady=10)
diet_frame.pack(fill="both", expand="yes", padx=20, pady=10)
diet_box = scrolledtext.ScrolledText(diet_frame, height=3, wrap=tk.WORD, font=body_font, bg=output_bg, fg=text_color)
diet_box.pack()

medication_frame = tk.LabelFrame(root, text="Medication", font=header_font, bg=section_bg, fg=text_color, padx=10, pady=10)
medication_frame.pack(fill="both", expand="yes", padx=20, pady=10)
medication_box = scrolledtext.ScrolledText(medication_frame, height=3, wrap=tk.WORD, font=body_font, bg=output_bg, fg=text_color)
medication_box.pack()

precautions_frame = tk.LabelFrame(root, text="Precautions", font=header_font, bg=section_bg, fg=text_color, padx=10, pady=10)
precautions_frame.pack(fill="both", expand="yes", padx=20, pady=10)
precautions_box = scrolledtext.ScrolledText(precautions_frame, height=3, wrap=tk.WORD, font=body_font, bg=output_bg, fg=text_color)
precautions_box.pack()

workout_frame = tk.LabelFrame(root, text="Workout", font=header_font, bg=section_bg, fg=text_color, padx=10, pady=10)
workout_frame.pack(fill="both", expand="yes", padx=20, pady=10)
workout_box = scrolledtext.ScrolledText(workout_frame, height=3, wrap=tk.WORD, font=body_font, bg=output_bg, fg=text_color)
workout_box.pack()

# Start the Tkinter main loop
root.mainloop()
