import streamlit as st
import requests
import smtplib
from bs4 import BeautifulSoup
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from chains import Chain
from portfolio import Portfolio
from utils import clean_text


def scrape_job_urls():
    url = "https://arc.dev/remote-jobs"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    job_urls = []
    for a_tag in soup.find_all('a', href=True):
        link = a_tag['href']
        if 'remote-jobs/details' in link:
            job_urls.append('https://arc.dev' + link)
    
    return job_urls


def extract_job_data(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    job_title = soup.find('h1') or soup.find('title')
    job_title = job_title.text.strip() if job_title else "Unknown Job Title"
    
    job_description = soup.find('div', class_='job-description') or soup.find('div', id='job-description')
    if not job_description:
        job_description = soup.find('body')
    job_description = job_description.text.strip() if job_description else ""
    
    return f"Job Title: {job_title}\n\nJob Description: {job_description}"


def send_email(sender_email, sender_password, receiver_email, subject, body):
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))
    
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False


def create_streamlit_app(llm, portfolio):
    st.title("📧 Cold Mail & LinkedIn Message Generator")
    
    pdf_file = st.file_uploader("Upload your Resume (PDF)", type='pdf')
    
    if pdf_file:
        portfolio.load_portfolio_from_pdf(pdf_file)
        st.success("Resume processed and portfolio updated!")
    
    st.markdown("### Email Credentials")
    user_email = st.text_input("Enter your email address:")
    user_password = st.text_input("Enter your email password:", type="password")

    job_urls = scrape_job_urls()
    st.markdown("#### Select a job or enter a custom job URL:")
    url_input = st.selectbox("Select a job URL", job_urls)
    custom_url = st.text_input("Or enter a custom job URL:")
    final_url = custom_url if custom_url else url_input  
    
    recipient_email = st.text_input("Enter recipient's email address:")
    submit_button = st.button("Generate Communication")
    send_button = st.button("Send Email")

    if submit_button and final_url:
        try:
            raw_data = extract_job_data(final_url)
            data = clean_text(raw_data)
            jobs = llm.extract_jobs(data)
            
            for job in jobs:
                if 'role' not in job or not job['role']:
                    job['role'] = raw_data.split('\n')[0].replace('Job Title:', '').strip()
                
                portfolio_items = portfolio.get_portfolio_items()
                
               
                email = llm.write_mail(job, portfolio_items)
                st.markdown("### Generated Cold Email:")
                st.code(email, language='markdown')
                
               
                linkedin_message = llm.write_linkedin_message(job, portfolio_items)
                st.markdown("### Generated LinkedIn Message:")
                st.code(linkedin_message, language='markdown')
                
               
                st.session_state.generated_email = email
                st.session_state.email_subject = f"Application for {job['role']}"
                st.session_state.linkedin_message = linkedin_message
                
        except Exception as e:
            st.error(f"An Error Occurred: {str(e)}")
    
    if send_button and recipient_email and user_email and user_password:
        if 'generated_email' in st.session_state:
            email_sent = send_email(user_email, user_password, recipient_email, st.session_state.email_subject, st.session_state.generated_email)
            if email_sent:
                st.success("Email sent successfully!")
            else:
                st.error("Failed to send email. Please check your credentials or network connection.")
        else:
            st.error("Please generate an email first before sending.")
    elif send_button:
        st.error("Please fill in your email credentials.")


if __name__ == "__main__":
    chain = Chain()
    portfolio = Portfolio()
    st.set_page_config(layout="wide", page_title="Cold Email & LinkedIn Message Generator", page_icon="📧")
    create_streamlit_app(chain, portfolio)
