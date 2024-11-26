import os
import streamlit as st
import pandas as pd
import smtplib
import random
import sqlite3
import re
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from openpyxl import load_workbook
import time
import warnings
import requests
import logging

# Suppress specific warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

# Read secrets from .streamlit/secrets.toml
your_name = st.secrets["your_name"]
your_email = st.secrets["your_email"]
your_password = st.secrets["your_password"]
#
api_key = st.secrets["api_key"]

# SMTP configuration
server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
server.ehlo()
server.login(your_email, your_password)

# Connect to the SQLite database (it will create the database if it doesn't exist)
conn = sqlite3.connect('school_admin.db')
cursor = conn.cursor()

# Create tables
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    schooladmin TEXT,
    sender_number TEXT,
    email_schooladmin TEXT,
    password TEXT,
    role TEXT,
    unique_code TEXT,
    is_activated INTEGER DEFAULT 0
)
''')

conn.commit()
conn.close()

def send_email(to_email, code):
    msg = MIMEMultipart()
    msg['From'] = your_email
    msg['To'] = to_email
    msg['Subject'] = "Your Unique Sign-In Code"
    body = f"Your unique sign-in code is:{code}"
    msg.attach(MIMEText(body, 'plain'))
    
    server.sendmail(your_email, to_email, msg.as_string())

def generate_unique_code():
    return ''.join(random.choices('0123456789ABCDEF', k=6))

def sign_up():
    st.title("📝 Sign Up")
    schooladmin = st.text_input("📝 Full Name (Including Mr./Ms.)", placeholder="Full Name (Including Mr./Ms., Example: Mr. Tohari Putra)")
    sender_number = st.text_input("📱 Active Whatsapp number(Example: 08122xxx)", placeholder="08122xxxxxxx")
    email_schooladmin = st.text_input("📧 Active Email, prefer using shb email", placeholder="xxx@shb.sch.id")
    password = st.text_input("🔒 Password", type="password",placeholder="Enter your password")
    role = st.radio("👤 Role", ["School Admin", "Academics VP", "Students VP", "Principal", "Cambridge Exam Officer","PIC","Subject Teacher", "Super Admin"], key="sign_up_role")
    
    if st.button("Sign Up"):
        if not re.match(r"^[0-9]{10,15}$", sender_number):
            st.error("❌ Invalid phone number. Please enter a valid phone number (10-15 digits).")
            return
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email_schooladmin):
            st.error("❌ Invalid email address. Please enter a valid email address.")
            return
        
        unique_code = generate_unique_code()
        send_email(email_schooladmin, unique_code)
        
        conn = sqlite3.connect('school_admin.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (schooladmin, sender_number, email_schooladmin, password, role, unique_code) VALUES (?, ?, ?, ?, ?, ?)",
                       (schooladmin, sender_number, email_schooladmin, password, role, unique_code))
        conn.commit()
        conn.close()
        
        st.success("Sign up successful! Check your email for the unique code.")
        time.sleep(2)  # Wait for 1 second
        st.session_state['signed_up'] = True
        st.experimental_rerun()  # Rerun the script to redirect to the Sign In page

def sign_in():
    st.title("Communication Channels")
    st.subheader("Email and WhatsApp Messaging for SHB Parents and Students")
    st.write("Dear Colleagues, 👋 Welcome.")
    st.write("If you don't have an account, please click on the left sidebar to register your account.")
    st.title("🔑 Sign In")
    st.write("If you already have an account, you can sign in directly here.")
    email_schooladmin = st.text_input("📧 Email", placeholder="Enter your email")
    password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
    unique_code = st.text_input("🆔 Unique Code", placeholder="Mandatory for first-time login. Enter your unique code (6 Digits)")
    st.write("""<small>If you are logging in for the first time, enter the 6-digit code that has been sent to your email.
    However, for subsequent logins, you can ignore the Unique Code menu.</small>""", unsafe_allow_html=True)
    
    if st.button("Sign In"):
        conn = sqlite3.connect('school_admin.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email_schooladmin = ? AND password = ?", (email_schooladmin, password))
        user = cursor.fetchone()
        
        if user:
            if user[7] == 1:
                st.session_state['logged_in'] = True
                st.session_state['role'] = user[5]
                st.session_state['sender_number'] = user[2]
                st.session_state['schooladmin'] = user[1]
                st.success("✅ Sign in successfully, welcome back! Press Sign In button one more.")
            elif user[6] == unique_code:
                cursor.execute("UPDATE users SET is_activated = 1 WHERE email_schooladmin = ?", (email_schooladmin,))
                conn.commit()
                st.session_state['logged_in'] = True
                st.session_state['role'] = user[5]
                st.session_state['sender_number'] = user[2]
                st.session_state['schooladmin'] = user[1]
                st.success("✅ Sign in successfully, welcome! Press Sign In button one more.")
            else:
                st.error("❌ Invalid unique code.")
        else:
            st.error("❌ Invalid credentials.")
        conn.close()

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if 'signed_up' not in st.session_state:
    st.session_state['signed_up'] = False

if 'schooladmin' not in st.session_state:
    st.session_state['schooladmin'] = None

if 'sender_number' not in st.session_state:
    st.session_state['sender_number'] = None

def superadmin_page():
    st.title("Super Admin Page")
    st.sidebar.button("Log Out", on_click=lambda: st.session_state.update({'logged_in': False}))
    
    conn = sqlite3.connect('school_admin.db')
    cursor = conn.cursor()
    
    st.subheader("View All Users")
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    df_users = pd.DataFrame(users, columns=['ID', 'School Admin', 'Sender Number', 'Email', 'Password', 'Role', 'Unique Code', 'Activated'])
    st.dataframe(df_users)

    st.subheader("Add or Update User")
    user_id = st.text_input("User ID (leave blank to add new user)", value="")
    schooladmin = st.text_input("School Admin")
    sender_number = st.text_input("Sender Number")
    email_schooladmin = st.text_input("Email")
    password = st.text_input("Password", type="password")
    role = st.radio("Role", ["schooladmin", "Academics VP", "Students VP", "Principal", "Cambridge Exam Officer","PIC","Subject Teacher", "superadmin"], key="superadmin_add_role")
    unique_code = generate_unique_code()
    
    if st.button("Add/Update User"):
        if user_id:
            cursor.execute("UPDATE users SET schooladmin = ?, sender_number = ?, email_schooladmin = ?, password = ?, role = ?, unique_code = ? WHERE id = ?",
                           (schooladmin, sender_number, email_schooladmin, password, role, unique_code, user_id))
            st.success("User updated successfully!")
        else:
            cursor.execute("INSERT INTO users (schooladmin, sender_number, email_schooladmin, password, role, unique_code) VALUES (?, ?, ?, ?, ?, ?)",
                           (schooladmin, sender_number, email_schooladmin, password, role, unique_code))
            st.success("User added successfully!")
        conn.commit()
    
    st.subheader("Delete User")
    delete_user_id = st.text_input("User ID to delete")
    if st.button("Delete User"):
        cursor.execute("DELETE FROM users WHERE id = ?", (delete_user_id,))
        conn.commit()
        st.success("User deleted successfully!")
    
    conn.close()

def schooladmin_page():
    st.write("You are logged in successfully ✅")
    st.sidebar.button("🚪 Log Out", on_click=lambda: st.session_state.update({'logged_in': False}))
    
    schooladmin = st.session_state['schooladmin']
    sender_number = st.session_state['sender_number']
    Role = st.session_state['role']
    variable1 = "👋 Welcome, "
    variable2 = schooladmin
    variable3 = "!"
    variable4=Role
    st.subheader(f"{variable1} {variable2}{variable3}")
    st.write(f"You are as {variable4}.")
    # Utility function to check allowed file extensions
    ALLOWED_EXTENSIONS = {'xlsx'}

    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    def send_whatsapp_messages(data, announcement=False, invoice=False, proof_payment=False):
        for index, row in data.iterrows():
            phone_number = str(row['Phone Number'])
            if not phone_number.startswith('0'):
                #phone_number = f'0{phone_number.lstrip("0")}'
                phone_number = f'0{phone_number.lstrip("0")}'

            if announcement:
                message = f"""
                Kepada Yth. Orang Tua/Wali Murid *{row['Nama_Siswa']}*,
    Kami hendak menyampaikan info mengenai:
     • *Subject:* {row['Subject']}
     • *Description:* {row['Description']}
     • *Link:* {row['Link']}
        
    Jika ada pertanyaan atau hendak konfirmasi dapat menghubungi {schooladmin}: https://wa.me/62{sender_number}
    Terima kasih atas kerjasamanya.
    ttd
    *{Role}*
    """
            elif invoice:
                message = f"""
                Kepada Yth. Orang Tua/Wali Murid *{row['customer_name']}* (Kelas *{row['Grade']}*),
    Kami hendak menyampaikan info mengenai:
     • *Subject:* {row['Subject']}
     • *Batas Tanggal Pembayaran:* {row['expired_date']}
     • *Sebesar:* Rp. {row['trx_amount']:,.0f}
     • *Pembayaran via nomor virtual account (VA) BNI/Bank:* {row['virtual_account']}
    Untuk pertanyaan lebih lanjut atau hendak konfirmasi dapat menghubungi {schooladmin}: https://wa.me/62{sender_number}
    Terima kasih atas kerjasamanya.
    
    ttd
    *{Role}*
        
    *Catatan:*
    Jika Ibu/Bapak sudah melakukan pembayaran, mohon *abaikan* pesan ini.
     """
            elif proof_payment:
                message = f"""
                Kepada Yth. Orang Tua/Wali Murid *{row['Nama_Siswa']}* (Kelas *{row['Grade']}*),
    Kami hendak menyampaikan info mengenai SPP:
     • *SPP yang sedang berjalan:* Rp {row['bulan_berjalan']:,.0f} ({row['Ket_1']})
     • *Denda:* Rp {row['Denda']:,.0f} ({row['Ket_2']})
     • *SPP bulan-bulan sebelumnya:* Rp {row['SPP_30hari']:,.0f} ({row['Ket_3']})
     • *Virtual Account (VA)/No. Akun Bank:* {row['virtual_account']}
     • *Keterangan:* {row['Ket_4']}
     • Total tagihan: Rp *{row['Total']:,.0f}*
    Jika ada pertanyaan atau hendak konfirmasi dapat menghubungi {schooladmin}: https://wa.me/62{sender_number}
    Terima kasih atas kerjasamanya.
    
    ttd
    *{Role}*
    """
            else:
                continue


            url = f"https://wanotif.shb.sch.id/send-message?api_key={api_key}&sender={sender_number}&number={phone_number}&message={requests.utils.quote(message)}"

            max_retries = 3
            for attempt in range(max_retries):
                try:
                    logging.info(f"Attempting to send message to {phone_number}... (Attempt {attempt + 1}/{max_retries})")
                    response = requests.get(url, timeout=10)  # Set a timeout
                    response = requests.get(url)
                    if response.status_code == 200:
                        logging.info(f"Message sent successfully to {phone_number}")
                        st.success(f"✅ Message sent successfully to {phone_number}")
                    else:
                        logging.error(f"Failed to send message to {phone_number}: {response.status_code} - {response.text}")
                        st.error(f"❌Failed to send message to {phone_number}: {response.text}")
                except requests.exceptions.RequestException as e:
                    logging.error(f"Request failed for {phone_number} on attempt {attempt + 1}: {e}")
                    if attempt < max_retries - 1:
                        time.sleep(2)  # Wait before retrying
                    else:
                        st.error(f"❌ Failed to send message to {phone_number} after {max_retries} attempts.")

    # Ensure your DataFrame and main application logic

    def send_emails(email_list, announcement=False, invoice=False, proof_payment=False):
        for idx, entry in enumerate(email_list):
            if announcement:
                subject = entry['Subject']
                name = entry['Nama_Siswa']
                email = entry['Email']
                description = entry['Description']
                link = entry['Link']
                message = f"""
                Kepada Yth.<br>Orang Tua/Wali Murid <span style="color: #007bff;">{name}</span><br>
                <p>Salam Hormat,</p>
                <p>Kami hendak menyampaikan info mengenai:</p>
                <ul>
                 <li><strong>Subject:</strong> {subject}</li>
                 <li><strong>Description:</strong> {description}</li>
                 <li><strong>Link:</strong> {link}</li>
                </ul>
                <p>Terima kasih atas kerjasamanya.</p>
                <p>{Role}</p>

                Catatan:
                <ul>
                 <li>Jika ada pertanyaan atau hendak konfirmasi dapat menghubungi {schooladmin}:<a href="https://wa.me/62{sender_number}?text=Yth%20{schooladmin}%0ASaya%20mau%20bertanya%20atau%20konfirmasi%20perihal%3A%0A...%0ADemikian%20dan%20terima%20kasih.">Click No. WhatsApp ini.</a></li>
                </ul>
                """
            elif invoice:
                subject = entry['Subject']
                grade = entry['Grade']
                va = entry['virtual_account']
                name = entry['customer_name']
                email = entry['customer_email']
                nominal = "{:,.0f}".format(entry['trx_amount'])
                expired_date = entry['expired_date']
                expired_time = entry['expired_time']
                description = entry['description']
                link = entry['link']
                message = f"""
                Kepada Yth.<br>Orang Tua/Wali Murid <span style="color: #007bff;">{name}</span> (Kelas <span style="color: #007bff;">{grade}</span>)<br>
                <p>Salam Hormat,</p>
                <p>Kami hendak menyampaikan info mengenai:</p>
                <ul>
                    <li><strong>Subject:</strong> {subject}</li>
                    <li><strong>Batas Tanggal Pembayaran:</strong> {expired_date}</li>
                    <li><strong>Sebesar:</strong> Rp. {nominal}</li>
                    <li><strong>Pembayaran via nomor virtual account (VA) BNI/Bank:</strong> {va}</li>
                </ul>
                <p>Terima kasih atas kerjasamanya.</p>
                <p>{Role}</p>
                Catatan:
                <ul>
                 <li>Jika Ibu/Bapak sudah melakukan pembayaran, mohon <strong>abaikan</strong> pesan ini.</li>
                 <li>Untuk pertanyaan lebih lanjut atau hendak konfirmasi dapat menghubungi {schooladmin}:<a href="https://wa.me/62{sender_number}?text=Yth%20{schooladmin}%0ASaya%20mau%20bertanya%20atau%20konfirmasi%20perihal%3A%0A...%0ADemikian%20dan%20terima%20kasih.">Click Nomor Whatsapp ini.</a></li>
                </ul>
                """
            elif proof_payment:
                subject = entry['Subject']
                va = entry['virtual_account']
                name = entry['Nama_Siswa']
                email = entry['Email']
                grade = entry['Grade']
                sppbuljal = "{:,.0f}".format(entry['bulan_berjalan'])
                ket1 = entry['Ket_1']
                spplebih = "{:,.0f}".format(entry['SPP_30hari'])
                ket2 = entry['Ket_2']
                denda = "{:,.0f}".format(entry['Denda'])
                ket3 =  entry['Ket_3']
                ket4 = entry['Ket_4']
                total = "{:,.0f}".format(entry['Total'])
                message = f"""
                Kepada Yth.<br>Orang Tua/Wali Murid <span style="color: #007bff;">{name}</span> (Kelas <span style="color: #007bff;">{grade}</span>)<br>
                <p>Salam Hormat,</p>
                <p>Kami hendak menyampaikan info mengenai SPP:</p>
                <ul>
                 <li><strong>SPP yang sedang berjalan:</strong> Rp. {sppbuljal} ({ket1})</li>
                 <li><strong>Denda:</strong> Rp. {denda} ({ket2})</li>
                 <li><strong>SPP bulan-bulan sebelumnya:</strong> Rp. {spplebih} ({ket3})</li>
                 <li><strong>Virtual Account (VA)/No. Akun Bank:</strong>{va}</li>                 
                 <li><strong>Keterangan:</strong> {ket4}</li>
                 <li><strong>Total tagihan:</strong> Rp. {total}</li>
                </ul>
                <p>Terima kasih atas kerjasamanya.</p>
                <p>{Role}</p>
                
                Catatan:
                <ul>
                <li>JIka Ibu/Bapak sudah melakukan pembayaran, mohon <strong>abaikan</strong> pesan ini.</li>
                <li>Untuk pertanyaan lebih lanjut atau hendak konfirmasi dapat menghubungi {schooladmin}:<a href="https://wa.me/62{sender_number}?text=Yth%20{schooladmin}%0ASaya%20mau%20bertanya%20atau%20konfirmasi%20perihal%3A%0A...%0ADemikian%20dan%20terima%20kasih.">Click No. Whatsapp ini.</a><li>
                </ul>
                """
            else:
                continue

            msg = MIMEMultipart()
            msg['From'] = your_email
            msg['To'] = email
            msg['Subject'] = subject
            msg.attach(MIMEText(message, 'html'))

            try:
                server.sendmail(your_email, email, msg.as_string())
                st.success(f'✅ Email {idx + 1} to {email} sent successfully!')
            except Exception as e:
                st.error(f'❌ Failed to send email {idx + 1} to {email}: {e}')

    def handle_file_upload(announcement=False, invoice=False, proof_payment=False):
        uploaded_file = st.file_uploader("Upload Excel file", type="xlsx")
        if uploaded_file is not None:
            df = pd.read_excel(uploaded_file)
            email_list = df.to_dict(orient='records')
            st.dataframe(df)

            if st.button("Send Emails"):
                send_emails(email_list, announcement, invoice, proof_payment)
            
            if st.button("Send WhatsApp Messages"):
                send_whatsapp_messages(df, announcement, invoice, proof_payment)

    def main():
        st.write('Sending emails and WhatsApp messages to parents/students at SHB')
        st.markdown("[Download Template Excel file](https://drive.google.com/drive/folders/1Xx7lLQ2_Xgwcby4PrBGmwr2eKE-z8p4w)")

        role = st.session_state['role']
        menu = ["Home", "Tutorial"]

        if role in ["School Admin", "Super Admin","schooladmin","superadmin"]:
            menu.extend(["Invoice", "Send Reminder", "Announcement"])
        elif role in ["Academics VP", "Students VP", "Principal", "Cambridge Exam Officer","PIC","Subject Teacher"]:
            menu.append("Announcement")

        # Add icons to the sidebar menu
        menu_options = {
            "Home": "🏠 Home",
            "Tutorial": "📚 Tutorial",
            "Invoice": "💸 Invoice",
            "Send Reminder": "⏰ Send Reminder",
            "Announcement": "📢 Announcement"
        }

        choice = st.sidebar.radio("Menu", [menu_options[option] for option in menu], key="main_menu")

        if choice == menu_options["Home"]:
            st.subheader("🏠 Home")
            st.write("Welcome to the Communication Sender App!")

        elif choice == menu_options["Announcement"]:
            st.subheader("📢 Announcement")
            handle_file_upload(announcement=True)

        elif choice == menu_options["Invoice"]:
            st.subheader("💸 Invoice")
            handle_file_upload(invoice=True)

        elif choice == menu_options["Send Reminder"]:
            st.subheader("⏰ Send Reminder")
            handle_file_upload(proof_payment=True)

        elif choice == menu_options["Tutorial"]:
            st.title("📚 Tutorial")
            st.subheader("First step")
            st.write(f"""Visit this web then login to access whatapp API:""")
            st.markdown("🌐 [https://wanotif.shb.sch.id/](https://wanotif.shb.sch.id/)")
            st.write(f"""Connect your Whatsapp number by scanning QR. 
             Click triple dots on the right top corner your WA App, then select Linked devices.""")
            st.subheader("Second step")
            st.write("Sign Up or Log in this web:")
            st.markdown("🌐 [shbinformation streamlit](https://shbinformation.streamlit.app/)")
            st.subheader("Third step")
            st.write("Create database properly. Use this template:")
            st.markdown("[Download Template Excel file](https://drive.google.com/drive/folders/1Xx7lLQ2_Xgwcby4PrBGmwr2eKE-z8p4w)")
            st.subheader("Furthermore")
            st.write("(Optional). Watch these tutorial videos to understand how to use this app:")
            
            videos = [
            {"subheader": "Goal of this application", "url": "https://www.youtube.com/embed/X5FKgE2sJ3Q?si=xHLgbVSCbiPPQt3h"},
            {"subheader": "How to Sign Up and Sign In", "url": "https://www.youtube.com/embed/ek2fsJWwkRA?si=RT1IqNHpZuG7b3ID"},
                #{"subheader": "How to send Invoice", "url": "https://www.youtube.com/embed/5ct-PqcJKz8"},
                #{"subheader": "How to send Announcement", "url": "https://www.youtube.com/embed/Hmmzoexf9aU"}
            ]
            
            for i, video in enumerate(videos):
                col1, col2 = st.columns([1, 1])
                with col1:
                    st.markdown(f"### {video['subheader']}")
                    st.markdown(f'<iframe width="100%" height="315" src="{video["url"]}" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>', unsafe_allow_html=True)
                if i % 2 == 1:
                    st.write("")
            st.write("Here is the end of the tutorials.")

    if __name__ == '__main__':
        main()

if st.session_state['logged_in']:
    role = st.session_state['role']
    if role == "Super Admin":
        superadmin_page()
    else:
        schooladmin_page()
else:
    choice = st.sidebar.radio("Choose Action", ["🔑 Sign In", "📝 Sign Up", "📖 Tutorial"], key="auth_action")
    if choice == "🔑 Sign In":
        sign_in()
    elif choice == "📝 Sign Up":
        sign_up()
    else:
        st.title("📚 Tutorial")
        st.subheader("First step")
        st.write(f"""Visit this web then login to access whatapp API:""")
        st.markdown("🌐 [https://wanotif.shb.sch.id/](https://wanotif.shb.sch.id/)")
        st.write(f"""Connect your Whatsapp number by scanning QR. 
        Click triple dots on the right top corner your WA App, then select Linked devices.""")
        st.subheader("Second step")
        st.write("Sign Up or Log in this web:")
        st.markdown("[🌐 shbinformation streamlit](https://shbinformation.streamlit.app/)")
        st.subheader("Third step")
        st.write("Create database properly. Use this template:")
        st.markdown("[Download Template Excel file](https://drive.google.com/drive/folders/1Xx7lLQ2_Xgwcby4PrBGmwr2eKE-z8p4w)")
        st.subheader("Furthermore")
        st.write("(Optional). Watch these tutorial videos to understand how to use this app:")
        
        videos = [
            {"subheader": "Goal of this application", "url": "https://www.youtube.com/embed/X5FKgE2sJ3Q?si=xHLgbVSCbiPPQt3h"},
            {"subheader": "How to Sign Up and Sign In", "url": "https://www.youtube.com/embed/ek2fsJWwkRA?si=RT1IqNHpZuG7b3ID"},
            #{"subheader": "How to send Invoice", "url": "https://www.youtube.com/embed/5ct-PqcJKz8"},
            #{"subheader": "How to send Announcement", "url": "https://www.youtube.com/embed/Hmmzoexf9aU"}
        ]
        
        for i, video in enumerate(videos):
            col1, col2 = st.columns([1, 1])
            with col1:
                st.markdown(f"### {video['subheader']}")
                st.markdown(f'<iframe width="100%" height="315" src="{video["url"]}" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>', unsafe_allow_html=True)
            if i % 2 == 1:
                st.write("")
        st.write("Here is the end of the tutorials page. Thank you for visiting.")
