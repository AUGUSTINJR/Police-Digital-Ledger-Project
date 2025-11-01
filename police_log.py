import streamlit as st
from PIL import Image
import mysql.connector
import pandas as pd

#DATABASE CREATION
def create_connection():
     try:
         connection =mysql.connector.connect(
             host="localhost",
             user="root",
             password="augus",
             database='Police_log1',
             auth_plugin="mysql_native_password"
         )
         return connection
     except Exception as e:
          st.error(f"Database Connection Error:{e}")
          return None
     
#FETCH DATA FROM DATABASE
def fetch_data(query):
     connection = create_connection()
     if connection:
          try:
                cursor = connection.cursor(dictionary=True) 
                cursor.execute(query)
                result=cursor.fetchall()
                df = pd.DataFrame(result)
                return df
          except Exception as e:
               st.error(f"Query Error: {e}")
               return pd.DataFrame()
          finally:
               connection.close()
     else:
          return pd.DataFrame()
     
               
#STREAMLIT UI
st.set_page_config(page_title="POLICE DIGITAL LEDGER",layout="wide")
st.markdown(
    """
    <style>
    .stApp{
    background-color:#d4edda; /*Light green */
    color:Black
    }
    /*sidebar background */
    [data-testid="stSidebar"]{
       background-color:#a8d5ba; /* Medium green*/
       color:black;
    }
    /* Sidebar text */
    [data-testid="stSidebar"]*{
        color:black !important;
        font_weight:500;
    }
    /*Title style*/
    h1 {
        text-align:center;
        color:#004d26;/* Dark green title*/
    }
    </style>
    """,
    unsafe_allow_html=True
)
image=Image.open(r"C:\Users\ELCOT\Desktop\Augustin\police cover image.jpg")
image=image.resize((1100,110))
st.image(image)
st.sidebar.header("Navigation")
section=st.sidebar.radio("Go to",["Home","Introduction","Logsheet","Q/A","Contact Info"])

#HOMEPAGE
if section =="Home":
    st.markdown("<div class='login-box'>",unsafe_allow_html=True)
    st.title("POLICE POST LOG")
    st.subheader("Officer Login")
    username=st.text_input("Username")
    password=st.text_input("Password",type="password")
    if st.button("Login"):
        if username =="augus" and password == "12345":
            st.session_state.login_in = True
            st.success("Login sucessfull! Welcome Officer")
        else:
            st.error("Invalid Username or Password")
elif  section == "Introduction":
      st.write("# POLICE DIGITAL LEDGER") 
      st.write("## Problem Statement:") 
      st.write("Police check posts require a centralized system for logging, tracking, and analyzing vehicle movements. Currently, manual logging and inefficient databases slow down security processes. This project aims to build an SQL-based check post database with a Python-powered dashboard for real-time insights and alerts.")
      st.write("## Flow Chart:")
      st.graphviz_chart("""
               digraph{
                    Rawdata ->" Check Duplicates" ->"Check Nan values"-> "Check Distribution"->"Check Outlier" ->
                    "Data Cleaning"->"SQL Database Creation" ->"Insert values"->" Streamlit Dashboard Creation" 
               }
     """)
elif  section =="Logsheet":
      st.title("Police Log Report Generator")
      with st.form("log_form"):
           col1,col2=st.columns(2)
           with col1:
                age=st.text_input("Driver Age")
                gender=st.selectbox("Driver Gender",["Male","Female"])
                violation=st.text_input("Violation")
                time_of_stop=st.time_input("Time Of Stop")
           with col2:
                search=("Was Search Conducted?",["Yes","No"])
                citation=st.selectbox("Was Citation Given?",["Yes","No"])
                stop_duration=st.text_input("Duration Of Stop")                
                drug_related=st.selectbox("Drug Related?",["Yes","No"])
           submitted=st.form_submit_button("Generate Report")
      if submitted:
           report=f""" 
           <div class='report-box'>
           A <b>{age}-year-old {gender.lower()} driver</b> was stopped for <b> {violation}</b> at <b>{time_of_stop.strftime("%I:%M %p")}</b>.
           {"A search was conducted" if search =="Yes" else "No search was conducted"}, and
           {"he received a <b>citation</b>" if citation =="Yes" else "No citation was issued"}.
           The stop lasted <b>{stop_duration} minutes </b> and was {"<b>drug_related</b>" if drug_related == "Yes" else "<b>not drug_related</b>"}
           </div>
           """
           st.markdown(report,unsafe_allow_html=True) 
elif  section =="Q/A":
     
     medium_selected_query=st.selectbox("Meduium Level Question",[
          "Top 10 vehicle_Number involved in drug-related stops",
          "Most frequently searched Vehicles",
          "Driver Age group with highest arrest rate",
          "Gender distribution of drivers stopped in each country",
          "Race and gender with highest search rate",
          "Time of day with most stops",
          "Average stop duration by violation",
          "Violations with most searches or arrests",
          "Violations common among young drivers (<25)",
          "Violation rarely resulting in search or arrest",
          "Country with highest drug-related stops",
          "Arrest rate by country and violation",
          "Country with most searches"
     ])
     medium_query_map={
         "Top 10 vehicle_Number involved in drug-related stops": "SELECT vehicle_number, COUNT(*) AS total FROM police_Postlog WHERE drugs_related_stop = TRUE GROUP BY vehicle_number ORDER BY total DESC LIMIT 10",
          "Most frequently searched Vehicles": "SELECT vehicle_number, COUNT(*) AS total FROM police_Postlog WHERE search_conducted = TRUE GROUP BY vehicle_number ORDER BY total DESC LIMIT 10",
          "Driver Age group with highest arrest rate":"SELECT driver_age, COUNT(*) AS total_arrests FROM police_Postlog WHERE is_arrested = TRUE GROUP BY driver_age ORDER BY total_arrests DESC LIMIT 1",
          "Gender distribution of drivers stopped in each country":"SELECT country_name, driver_gender, COUNT(*) AS total FROM police_Postlog GROUP BY country_name, driver_gender ORDER BY country_name",
          "Race and gender with highest search rate":"SELECT driver_race, driver_gender, COUNT(*) AS total FROM police_Postlog WHERE search_conducted = TRUE GROUP BY driver_race, driver_gender ORDER BY total DESC LIMIT 1",
          "Time of day with most stops":"SELECT stop_time, COUNT(*) AS total FROM police_Postlog GROUP BY stop_time ORDER BY total DESC LIMIT 1 ",
          "Average stop duration by violation":"SELECT violation, AVG(CASE WHEN stop_duration = '0-15 Min' THEN 7.5 WHEN stop_duration = '16-30 Min' THEN 23 WHEN stop_duration = '30+ Min' THEN 45 END) AS avg_duration_minutes FROM police_Postlog GROUP BY violation ORDER BY avg_duration_minutes DESC",
          "Violations with most searches or arrests":"SELECT violation, COUNT(*) AS total FROM police_Postlog WHERE search_conducted = TRUE OR is_arrested = TRUE GROUP BY violation ORDER BY total DESC ",
          "Violations common among young drivers (<25)":"SELECT violation, COUNT(*) AS total FROM police_Postlog WHERE driver_age < 25 GROUP BY violation ORDER BY total DESC",
          "Violation rarely resulting in search or arrest":"SELECT violation, COUNT(*) AS total FROM police_Postlog WHERE search_conducted = FALSE AND is_arrested = FALSE GROUP BY violation ORDER BY total ASC LIMIT 1",
          "Country with highest drug-related stops":"SELECT country_name, COUNT(*) AS total FROM police_Postlog WHERE drugs_related_stop = TRUE GROUP BY country_name ORDER BY total DESC",
          "Arrest rate by country and violation":"SELECT country_name, violation, COUNT(*) AS total FROM police_Postlog WHERE is_arrested = TRUE GROUP BY country_name, violation ORDER BY total DESC",
          "Country with most searches":"SELECT country_name, COUNT(*) AS total FROM police_Postlog WHERE search_conducted = TRUE GROUP BY country_name ORDER BY total DESC LIMIT 1",
     }
     if st.button("Run Query",key="run_medium"):
          result= fetch_data(medium_query_map[medium_selected_query])
          if not result.empty:
               st.write(result)
          else:
               st.warning("No result found for selected query.")

     complex_selected_query=st.selectbox("Complex Level Question",[
          "Yearly stops and arrests by country",
          "Violations by age and race",
          "Stops by year, month, hour",
          "Violations with high search and arrest rates",
          "Driver demographics by country",
          "Top 5 violations with highest arrests"
     ])
     complex_query_map={
          "Yearly stops and arrests by country":"SELECT country_name, YEAR(stop_date) AS year, COUNT(*) AS total FROM police_Postlog GROUP BY country_name, year",
          "Violations by age and race":"SELECT driver_age, driver_race, violation, COUNT(*) AS total FROM police_Postlog GROUP BY driver_age, driver_race, violation",
          "Stops by year, month, hour":"SELECT YEAR(stop_date) AS year, MONTH(stop_date) AS month, stop_time, COUNT(*) AS total FROM police_Postlog GROUP BY year, month, stop_time",
          "Violations with high search and arrest rates":"SELECT violation, COUNT(*) AS total FROM police_Postlog WHERE search_conducted = TRUE AND is_arrested = TRUE GROUP BY violation ORDER BY total DESC LIMIT 5",
          "Driver demographics by country":"SELECT country_name, driver_gender, driver_race, COUNT(*) AS total FROM police_Postlog GROUP BY country_name, driver_gender, driver_race",
          "Top 5 violations with highest arrests":"SELECT violation, COUNT(*) AS total FROM police_Postlog WHERE is_arrested = TRUE GROUP BY violation ORDER BY total DESC LIMIT 5",
          
     }
     if st.button("Run Query",key="run_complex"):
          result= fetch_data(complex_query_map[complex_selected_query])
          if not result.empty:
               st.write(result)
          else:
               st.warning("No result found for selected query.")

elif  section =="Contact Info":
     st.write("---")
     st.title("Creator Details")
     st.markdown("### Name: Augustin.J.R")
     st.markdown("### Project Title: Police Digital Ledger")
     st.write("---")
     st.subheader("Thank You")
     st.write("Thank You for visiting my project")
     st.balloons()
     
              
    

