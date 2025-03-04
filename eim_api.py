import streamlit as st
import datetime
import time
import pytz
import xml.etree.ElementTree as ET
import google.generativeai as genai
# get current date and time
 
timezone = pytz.timezone('America/Vancouver')
#today = datetime.date.today()
now = datetime.datetime.now(timezone)
#curr_date = today.strftime("%Y-%m-%d")
curr_date = now.strftime("%Y-%m-%d")
curr_time = now.strftime("%H%M")
curr_time = int(curr_time)

api_key = st.secrets["gsc_connections"]["api_key"]
genai.configure(api_key=api_key)

# this is the main instruction
with open("/mount/src/eim_api/instructions.txt", "r") as file:
    instructions = file.read()

# this is the xml instruction
with open("/mount/src/eim_api/instructions_xml.txt", "r") as file:
    instructions_xml = file.read()

# Create the model
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}

# FUNCTIONS
def preprocess_instruction_text(sys_instructions):
    processed_text = sys_instructions.replace("@year",str(occ_year))
    processed_text = processed_text.replace("@occ_num",str(occ_num))
    processed_text = processed_text.replace("@9999/99/99", str(curr_date))
    processed_text = processed_text.replace("@9999", str(curr_time))
    return processed_text

def generate_xml():
    if not file_num:
     st.warning("A file number is required to generate the proper xml file.")

    sys_instructions = preprocess_instruction_text(instructions_xml)
    xml_text = generate(sys_instructions, file_num + new_data)
 
    # replace some variables. this applies to the xml text
    xml_text = xml_text.replace("```xml","")
    xml_text = xml_text.replace("```", "")
    xml_start_index = xml_text.find("<?xml")
    if xml_start_index != -1:
     xml_text = xml_text[xml_start_index:]
    else:
     xml_text = "Unable to generate xml."
    
    return xml_text
 
def generate(inst_text, prompt_text):
 model = genai.GenerativeModel(
  model_name="gemini-1.5-pro",
  generation_config=generation_config,
  system_instruction=inst_text)
  
 responses = model.generate_content(prompt_text, stream=True)
 resp_text = ""
  
 for response in responses:
   resp_text = resp_text + response.text
 return resp_text

def is_xml_compliant(xml_string):
    try:
        ET.fromstring(xml_string)
        return "Completed. You may download the report and import to MRE for further processing."
    except ET.ParseError:
        return "Sorry, I made a mistake in the XML. Please try again."

def wait(sec=35):
 placeholdertime = st.empty()
 while True:
  time.sleep(1)
  sec = sec - 1
  placeholdertime.write("Next request: " + str(sec))
  if sec <= 0:
   placeholdertime.empty()
   break
# PROGRAM BEGIN

st.write(curr_date)
st.image("/mount/src/eim_api/abstract representation of AI assisting police department.png", width=200)
#st.title("eIM + Offence Classifier + Summarizer")
st.markdown("<h3><span style='color: blue;'>eIM + Offence Classifier + Summarizer + MORE</h3></span>", unsafe_allow_html=True)
st.write('')
st.write('**Responses are generated using the Google Gemini AI API. This is the free version of the service, which comes with limitations in features, performance, or access compared to the paid version**')

occ_year = st.number_input("GO Year (mandatory)", value=None,  min_value=2000, max_value=2050)
occ_num = st.number_input("GO Number (mandatory)", value=None, min_value=1, max_value=500000)
file_num = "File number: " + str(occ_year) + "-" + str(occ_num) + " "
if occ_num is None or occ_year is None:
 file_num = "" 
 
spaces = "&nbsp;&nbsp;&nbsp;"
new_data = st.text_area("""Enter a narrative or ask me any question about eIM and I will guide you through the naming process. 
Although my training is limited, I am the proof of concept that AI can assist with multiple tasks at once.
You can ask me specific questions. \nYou don't need to erase the text if I ask you follow up questions. Just keep adding the details required. 
Example questions:\n
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;***What naming conventions were you trained on?*** \n
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;***What else can you do beside naming conventions?*** \n
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;***What is the naming convention for use of force?***"""
                        , height=200, value="The author is VA9000 Mary SIM. Victim Jane DOE (1991/02/03) was walking and suspect Bart SIMPSON (1990/01/01) assaulted victim. Witness John BROWN (1989/02/03) called police. PC VA9000 Mary SIM arrived and arrested Bart. Witness provided a statement to police. Suspect was released with conditions of no contact Jane DOE. PC VA9100 Bart BARROW assisted with canvassing in the Collingwood area and found no CCTV.")

st.write("***Tips: if you want to generate only specific text page, please indicate what you would like to generate. For example, generate a witness statement and a police note with the following details. On Feb 28, 2024, PC 9999 received the following statement from witness Jane DOE. I was walking and I saw.........***")

#if button is clicked
if st.button("Generate Response", help="Generate eIM based on the input text."):
    placeholder = st.empty()
    placeholder.write("Please be patient as it may take me a minute or two to generate a response with this free version........")
    result = generate(instructions, file_num + new_data)
    placeholder.empty()
    #placeholder.write("With this proof of concept, it is possible to use AI to reduce the repetive tasks and put officers back on the road. I can help add entities and text pages using details extracted from the officer's narrative. The possibilities are endless.")
    st.text_area("Response", result, height=800)
    wait()

if st.button("Generate  XML File", help="I will generate everything including entities and text pages ready to be sent to CPIC Transcription."):
 placeholder = st.empty()
 placeholder.write("Please be patient as it may take me a minute or two to generate the xml report with this free version........")
 xml_text = generate_xml()
 placeholder.empty()
 result_msg = is_xml_compliant(xml_text)
 placeholder.write(result_msg)
 #placeholder.write("Completed. You may download the report and import to MRE for further processing.")
 
 st.download_button(
  label="Download XML File",
  help="Download and edit or send the report to CPIC Transcription.",
  data = xml_text,
  file_name="ai_report.xml",
  mime="text/plain")



