import tkinter as tk
from tkinter import messagebox
import cv2
import os
import smtplib
from PIL import Image, ImageTk
import settings_variables as sv
import importlib ,time, threading

# Function to resize frame image to match webcam dimensions
def resize_frame_image(frame_img, webcam_width, webcam_height):
    return cv2.resize(frame_img, (webcam_width, webcam_height), interpolation=cv2.INTER_AREA)

# Function to set resolution of the webcam
def set_resolution(cap, width, height):
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

# Function to reload settings
def reload_settings():
    import settings_variables as sv
    importlib.reload(sv)
    print("Settings reloaded:")
    print(f"SENDER_EMAIL: {sv.SENDER_EMAIL}")
    print(f"SENDER_PASSWORD: {sv.SENDER_PASSWORD}")
    print(f"MY_Frame: {sv.MY_Frame}")
    print(f"WEBCAM_WIDTH: {sv.WEBCAM_WIDTH}")
    print(f"WEBCAM_HEIGHT: {sv.WEBCAM_HEIGHT}")
    print(f"MESSAGE_SUBJECT: {sv.MESSAGE_SUBJECT}")
    print(f"MESSAGE_BODY: {sv.MESSAGE_BODY}")

def extract_local_part(email: str) -> str:
    return email.split('@')[0] + ".jpg"

def create_image_frame_folder(My_Frame):
    image_path = My_Frame
    image_name = os.path.splitext(os.path.basename(image_path))[0]
    new_folder_name = f"Photos_with_Frame_{image_name}"
    new_folder_path = os.path.join(os.path.dirname(image_path), new_folder_name)

    if not os.path.exists(new_folder_path):
        os.makedirs(new_folder_path)

    print(f"Directory path: {new_folder_path}")
    return new_folder_path

import cv2

def prev(img_path):
    # Load the image
    image = cv2.imread(img_path)
    
    # Display the image
    cv2.imshow('Preview', image)
    
    # Initialize flag
    flag = None
    
    while True:
        key = cv2.waitKey(0)
        
        if key == 27:  # Esc key
            flag = 0
            break
        elif key == 32:  # Space bar
            flag = 1
            break
    
    # Close the image window
    cv2.destroyAllWindows()
    
    return flag

                        
    


# Function to capture image and send email
def capture_and_send_email(receiver_email, root, app):
    try:
        reload_settings()
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            messagebox.showerror("Error", "Failed to open webcam!")
            return

        set_resolution(cap, sv.WEBCAM_WIDTH, sv.WEBCAM_HEIGHT)

        frame_image_path = sv.MY_Frame
        frame_img = cv2.imread(frame_image_path, cv2.IMREAD_UNCHANGED)

        if frame_img is None or frame_img.shape[2] != 4:
            messagebox.showerror("Error", "The frame image does not have an alpha channel or could not be loaded.")
            cap.release()
            return

        ret, frame = cap.read()
        if not ret:
            messagebox.showerror("Error", "Failed to grab frame.")
            cap.release()
            return

        webcam_height, webcam_width = frame.shape[:2]
        frame_img_resized = resize_frame_image(frame_img, webcam_width, webcam_height)

        camera_window = tk.Toplevel(root)
        camera_window.title("Webcam with Frame")
        camera_window.geometry(f"{webcam_width}x{webcam_height}")
        camera_window.attributes("-topmost", True)
        camera_window.attributes("-fullscreen", True)  # Make the window fullscreen

        def on_close():
            cap.release()
            cv2.destroyAllWindows()
            camera_window.destroy()
            app.refresh()
        def sm(receiver_email, captured_image_path):
            send_email(receiver_email, captured_image_path)
            messagebox.showinfo("Success", "Email sent successfully!")

        camera_window.protocol("WM_DELETE_WINDOW", on_close)

        while True:
            ret, frame = cap.read()
            if ret:
                alpha_frame = frame_img_resized[:, :, 3] / 255.0
                alpha_background = 1.0 - alpha_frame

                for c in range(0, 3):
                    frame[:, :, c] = (alpha_frame * frame_img_resized[:, :, c] +
                                      alpha_background * frame[:, :, c])

                cv2.imshow('Webcam with Frame', frame)

                key = cv2.waitKey(1) & 0xFF
                if key == 27:
                    cap.release()
                    cv2.destroyAllWindows()
                    camera_window.destroy()
                    break
                elif key == 32:
                    phot_name = extract_local_part(receiver_email)
                    captured_image_dir = create_image_frame_folder(sv.MY_Frame)
                    captured_image_path = os.path.join(captured_image_dir, phot_name)
                    cv2.imwrite(captured_image_path, frame)
                    time.sleep(3)
                    print(f"Captured image saved as '{captured_image_path}'")
                    if prev(captured_image_path):
                        background_thread = threading.Thread(target=sm, args=(receiver_email, captured_image_path))
                        background_thread.start()
                        cap.release()
                        cv2.destroyAllWindows()
                        camera_window.destroy()
                        
                        break
                    else:
                        pass
                elif key == ord('q') or cv2.getWindowProperty('Camera Window', cv2.WND_PROP_VISIBLE) > 1:
                    cap.release()
                    cv2.destroyAllWindows()
                    camera_window.destroy()
            else:
                messagebox.showerror("Error", "Failed to capture image.")
                break
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

# Function to send email with captured image attached
def send_email(receiver_email, image_path):
    try:
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText
        from email.mime.base import MIMEBase
        from email import encoders

        sender_email = sv.SENDER_EMAIL
        sender_password = sv.SENDER_PASSWORD

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = sv.MESSAGE_SUBJECT

        body = sv.MESSAGE_BODY
        msg.attach(MIMEText(body, 'plain'))

        filename = os.path.basename(image_path)
        attachment = open(image_path, 'rb')
        part = MIMEBase('application', 'octet-stream')
        part.set_payload((attachment).read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f"attachment; filename= {filename}")
        msg.attach(part)

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, receiver_email, text)
        server.quit()

        print(f"Email sent successfully to {receiver_email}")

    except Exception as e:
        print(f"Error sending email: {str(e)}")

