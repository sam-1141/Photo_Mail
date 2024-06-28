
# Photo Mail Application

## Overview
The Photo Mail Application is a desktop software designed to capture photos through a webcam, apply custom frames, and send them via email. This application is built using Python and leverages libraries such as Tkinter for the GUI, OpenCV for image processing, and smtplib for sending emails.

## Features
- **Webcam Integration**: Capture photos directly from your webcam.
- **Custom Frames**: Apply predefined or custom frames to the captured photos.
- **Email Integration**: Send the captured and framed photos via email directly from the application.
- **Settings Customization**: Customize sender email, password, webcam settings, and more through a user-friendly interface.

## Installation

### Prerequisites
Ensure you have Python installed on your machine (Python 3.7 or higher is recommended). Additionally, the following Python libraries are required:
- `tkinter`
- `opencv-python`
- `Pillow`
- `requests`
- `smtplib`

You can install the necessary libraries using pip:
```bash
pip install opencv-python Pillow requests
```

Note: `tkinter` typically comes pre-installed with Python. If not, you may need to install it via your system's package manager.

### Setup
1. Download the ZIP file or clone the repo using Git.
2. Navigate to the application directory.
3. Run the application using Python:
   ```bash
   python main.py
   ```

## Usage
- **Start the Application**: Double-click on `main.py` or run it from the command line.
- **Configure Settings**: Navigate to the Settings tab to configure your email, password, and other preferences.
- **Capture Photos**: Go to the Main tab, adjust your webcam, and capture photos.
- **Send Emails**: After capturing a photo, enter the recipient's email and click on the send button.

## Security and Privacy
This application does not store any personal data permanently. However, it requires network access to send emails. Ensure your antivirus and firewall settings allow this application to operate if prompted.

## Troubleshooting
If you encounter issues with camera access or email functionality, verify your settings and ensure all dependencies are correctly installed. Check your antivirus settings if the application is blocked or flagged as a potential threat.

## Contact
For support or further information, please contact [your-email@example.com](mailto:your-email@example.com).

