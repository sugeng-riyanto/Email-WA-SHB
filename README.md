
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

  

Ensure you have the following secrets stored in `.streamlit/secrets.toml`:

  

```toml

your_name = "Your Name"

your_email = "your-email@gmail.com"

your_password = "your-email-password"

api_key = "your-whatsapp-api-key"


