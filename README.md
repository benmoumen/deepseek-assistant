# DS Assistant Setup Guide

## Overview

The DS Assistant is a voice-controlled application with features such as screen OCR, permanent memory storage, and Google Docs integration. This guide provides instructions to build and run the application using Docker.

---

## Building the Docker Image

1. Clone the repository:

   ```bash
   git clone https://github.com/benmoumen/deepseek-assistant
   cd deepseek-assistant
   ```

2. Build the Docker image:
   ```bash
   docker build -t ds-assistant .
   ```

---

## Running the DS Assistant

1. Export your DeepSeek API key as an environment variable:

   ```bash
   export DEEPSEEK_API_KEY="your_deepseek_api_key"
   ```

   Replace `your_deepseek_api_key` with your actual API key.

2. Run the container with the environment variable and mount for local files:
   ```bash
   docker run -it --rm -e DEEPSEEK_API_KEY=$DEEPSEEK_API_KEY -v $(pwd):/app ds-assistant
   ```

---

## Features and Commands

### 1. **Screen Analysis (OCR)**

- Say: "What’s on my screen?"
- The assistant captures the screen, extracts text, and analyzes it using the DeepSeek API.

### 2. **Save Information**

- Say: "Remember that my favorite color is blue."
- The assistant saves the information to its memory file (`ds_memory.json`).

### 3. **Recall Information**

- Say: "What do you remember?"
- The assistant recalls saved notes and reads them out loud.

### 4. **Export Manual**

- Say: "Export manual" or "Save manual to Google Docs."
- Creates a Google Doc containing a predefined manual and shares the link.

---

## Environment Variables

- **DEEPSEEK_API_KEY**: Your DeepSeek API key is required for the assistant to function.
  ```bash
  export DEEPSEEK_API_KEY="your_deepseek_api_key"
  ```

---

## Troubleshooting

1. **Docker Build Issues**:

   - Ensure Docker is installed and running properly.

2. **Missing API Key**:

   - Ensure the `DEEPSEEK_API_KEY` environment variable is set correctly.

3. **Tesseract Not Found**:

   - Verify Tesseract is installed inside the Docker container. If issues persist, rebuild the image.

4. **Google API Authentication Issues**:
   - Place your `credentials.json` file in the mounted directory for Google API access.

---

## License

This project is licensed under [MIT License](LICENSE).

---

## Contributions

Feel free to open issues or pull requests for improvements or bug fixes.
