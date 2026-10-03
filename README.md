# Skip YT

A simple Python automation project that detects YouTube's "Skip Ads" button and automatically clicks it.

## Why I Made This

I made this because it's annoying when an ad appears while I'm eating and my hands are greasy. 😅

Instead of stopping what I'm doing to click the Skip Ads button, I wanted to make a program that could do it for me.

## Features

- Detects the active YouTube tab
- Uses OpenCV to detect the Skip Ads button
- Automatically moves the mouse over the button
- Waits for the hover effect
- Automatically clicks the button
- Simple ON/OFF GUI
- Customizable global keybind
- Chrome extension communicates with the Python program

## Technologies Used

- Python
- OpenCV
- PyAutoGUI
- Tkinter
- NumPy
- JavaScript
- Chrome Extension API

## Project Structure

```text
Skip YT
├── extension/
│   ├── manifest.json
│   └── background.js
├── main.py
├── skip_button.png
├── .gitignore
└── README.md