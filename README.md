## LeetCode Daily Digest

This project is an automated system for tackling the daily LeetCode challenge. It streamlines the entire process from fetching the problem to publishing the solution's explanation, all without human intervention.

---

### Key Features

* **Automated Scraping:** An API scraper fetches the daily LeetCode problem and its official solution.
* **AI-Powered Explanations:** The **Ollama** AI model is used to generate a clear, step-by-step explanation for the solution.
* **Content Publishing:** **Playwright** is used for browser automation to publish the generated content to social platforms like LinkedIn.
* **Built-in Resiliency:** The system includes custom solvers for various captchas and a fallback mechanism using a **VNC server** to handle unexpected obstacles.

---

### How It Works

The workflow is a simple, automated pipeline:

1. A scheduled job initiates the process.
2. The LeetCode API is scraped for the day's problem and solution.
3. The solution is sent to the Ollama model, which generates a detailed explanation.
4. Playwright takes over, using browser automation to log in and publish the content.
5. If a captcha or another issue is encountered, the custom solver and VNC server provide a reliable fallback to ensure the process completes successfully.

---

This project showcases a complete automation loop, from data acquisition and AI processing to content delivery, all built to run reliably on its own.
