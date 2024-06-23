import tkinter as tk
from tkinter import messagebox
import cv2
import os
import smtplib
from PIL import Image, ImageTk
import settings_variables as sv
import importlib

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
    return email.split('@')[0]+".jpg"

def create_image_frame_folder(My_Frame):
                       # Extract the image path from the My_Frame object
                       image_path = My_Frame
    
                       # Extract the image name without the extension
                       image_name = os.path.splitext(os.path.basename(image_path))[0]

                       # Define the new folder name
                       new_folder_name = f"Photos_with_Frame_{image_name}"

                        # Define the directory path to the new folder
                       new_folder_path = os.path.join(os.path.dirname(image_path), new_folder_name)

                    # Check if the folder already exists
                       if not os.path.exists(new_folder_path):
                         # Create the new folder
                        os.makedirs(new_folder_path)

                       # Set the directory path to a variable
                       curr_die = new_folder_path

                       # Output the directory path
                       print(f"Directory path: {curr_die}")
                       return curr_die

# Function to capture image and send email
def capture_and_send_email(receiver_email, root, app):
    try:
        # Reload settings before capturing the image
        reload_settings()

        # Open a connection to the webcam
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            messagebox.showerror("Error", "Failed to open webcam!")
            return

        # Set webcam resolution using the reloaded settings
        set_resolution(cap, sv.WEBCAM_WIDTH, sv.WEBCAM_HEIGHT)

        # Load the frame image
        frame_image_path = sv.MY_Frame
        frame_img = cv2.imread(frame_image_path, cv2.IMREAD_UNCHANGED)

        # Ensure the frame image has an alpha channel (transparency)
        if frame_img is None or frame_img.shape[2] != 4:
            messagebox.showerror("Error", "The frame image does not have an alpha channel or could not be loaded.")
            cap.release()
            return

        # Capture a frame to get dimensions
        ret, frame = cap.read()
        if not ret:
            messagebox.showerror("Error", "Failed to grab frame.")
            cap.release()
            return

        # Get webcam frame dimensions
        webcam_height, webcam_width = frame.shape[:2]

        # Resize frame image to match webcam dimensions
        frame_img_resized = resize_frame_image(frame_img, webcam_width, webcam_height)

        # Create a new window for the webcam feed
        camera_window = tk.Toplevel(root)
        camera_window.title("Webcam with Frame")
        camera_window.geometry(f"{webcam_width}x{webcam_height}")
        camera_window.attributes("-topmost", True)

        # Function to handle window close event
        def on_close():
            cap.release()
            cv2.destroyAllWindows()
            camera_window.destroy()
            app.refresh()

        camera_window.protocol("WM_DELETE_WINDOW", on_close)

        # Capture image
        while True:
            ret, frame = cap.read()
            if ret:
                # Create an alpha mask from the resized frame image
                alpha_frame = frame_img_resized[:, :, 3] / 255.0
                alpha_background = 1.0 - alpha_frame

                # Blend the images
                for c in range(0, 3):
                    frame[:, :, c] = (alpha_frame * frame_img_resized[:, :, c] +
                                      alpha_background * frame[:, :, c])

                # Display the resulting frame
                cv2.imshow('Webcam with Frame', frame)

                # Check for key presses
                key = cv2.waitKey(1) & 0xFF
                if key == 27:
                    # Release the webcam capture
                    cap.release()
                    cv2.destroyAllWindows()

                    # Close the camera window
                    camera_window.destroy()

                    # Break the loop on 'q' key press
                    break
                elif key == 32:
                    phot_name = extract_local_part(receiver_email)
                    
                    
                    
                    # Capture and save the image on 'c' key press
                    captured_image_dir=create_image_frame_folder(sv.MY_Frame)
                      


                    captured_image_path = os.path.join(captured_image_dir, phot_name)
                    cv2.imwrite(captured_image_path, frame)
                    print(f"Captured image saved as '{captured_image_path}'")

                    # Send email with captured image
                    send_email(receiver_email, captured_image_path)

                    # Release the webcam capture
                    cap.release()
                    cv2.destroyAllWindows()

                    # Close the camera window
                    camera_window.destroy()

                    # Display success message
                    messagebox.showinfo("Success", "Email sent successfully!")
                    break
                elif key == ord('q') or cv2.getWindowProperty('Camera Window', cv2.WND_PROP_VISIBLE) > 1:
                    
                    # Release the webcam capture
                    cap.release()
                    cv2.destroyAllWindows()

                    # Close the camera window
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

        # Email account details
        sender_email = sv.SENDER_EMAIL
        sender_password = sv.SENDER_PASSWORD

        # Create the email content
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = sv.MESSAGE_SUBJECT

        body = sv.MESSAGE_BODY
        msg.attach(MIMEText(body, 'plain'))

        # Attach the image
        filename = os.path.basename(image_path)
        attachment = open(image_path, 'rb')
        part = MIMEBase('application', 'octet-stream')
        part.set_payload((attachment).read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', "attachment; filename= %s" % filename)
        msg.attach(part)

        # Connect to Gmail's SMTP server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()

        # Login to Gmail
        server.login(sender_email, sender_password)

        # Send the email
        text = msg.as_string()
        server.sendmail(sender_email, receiver_email, text)
        server.quit()

        print(f"Email sent successfully to {receiver_email}")

    except Exception as e:
        print(f"Error sending email: {str(e)}")