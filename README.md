
# Communication Channels App

  

Welcome to the Communication Channels App! This Streamlit application facilitates communication between SHB school administrators and parents/students through email and WhatsApp messaging. Below you will find detailed functionalities and usage instructions for the app.

  

## Features

  

1.  **User Authentication**:

- Sign Up: Allows new users to register by providing their full name, WhatsApp number, email, password, and role.

- Sign In: Enables registered users to log in using their email, password, and a unique code sent to their email.

  

2.  **Role-Based Access**:

- Super Admin: Has access to view, add, update, and delete users.

- School Admin and other roles: Can send announcements, invoices, and reminders.

  

3.  **Communication Channels**:

-  **Email**: Send emails to parents/students based on uploaded Excel data.

-  **WhatsApp**: Send WhatsApp messages to parents/students based on uploaded Excel data.

  

4.  **Tutorials and Guides**:

- Step-by-step instructions and video tutorials on how to use the app effectively.

  

## Getting Started

  

### Prerequisites

# Whatsapps and Emails Blast using streamlit and nodejs(Laravel) 
### Register and scan your Whatsapp number active here: 
   [wanotif.aaviaya.cloud/login](https://wanotif.aaviaya.cloud/login)

### A step by step installing dependencies
#### Get the API WA from [wanotif.aaviaya.cloud/login](https://wanotif.aaviaya.cloud/login), then put it on the script
#### In your VS Code Terminal: install
    pip install -r requirements.txt
#### Run project
    streamlit run app.py
    
### Create repository for pushing your Project on your github

### Deploy the project on streamlit
  [streamlit.io](https://streamlit.io/)
#### Connect your Github and streamlit cloud
#### copy and paste the app.py link
#### Generate web link
#### Done!

### Good Luck!


Ensure you have the following secrets stored in `.streamlit/secrets.toml`:

  

```toml

your_name = "Your Name"

your_email = "your-email@gmail.com"

your_password = "your-email-password"

api_key = "your-whatsapp-api-key"


