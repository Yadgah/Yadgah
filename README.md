<div align="center">

<p>
    <a href="#">
        <img width="150" src="https://github.com/BDadmehr0/Yadgah/blob/main/favicon.ico" alt="Yadgah Logo">
    </a>
</p>

# Yadgah

**A Platform for Experience Sharing & Q&A**

</div>

Yadgah is a community-driven platform designed for sharing experiences, asking questions, and engaging in discussions. Inspired by Quera and Stack Overflow, Yadgah fosters a collaborative environment where users can learn, contribute, and grow.

## ✨ Features

- **User Profiles:** Create and customize your profile to share insights and engage with the community.
- **Q&A System:** Ask questions and receive answers from knowledgeable users.
- **Interactive Engagement:** Like, comment on, and rate answers to enhance discussions.
- **Organized Content:** Browse topics in various categories:
  - Work & Career
  - Education
  - Technology
  - Health
  - And more!
- **User Ranking System:** Gain recognition based on contributions and community feedback.

## 🚀 Installation

### Prerequisites
- Python 3.x
- pip (Python package manager)

### Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Yadgah/Yadgah.git
   cd Yadgah
   ```

2. **Create and actiavte virtual envirnoment:**
- On linux/ macOS:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
- On Windows (Command Prompt):
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```
- On Windows (Powershell):
   ```bash
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Make migrations:**
   ```bash
   python manage.py makemigrations home
   python manage.py makemigrations blog

   ```

5. **Apply database migrations:**
   ```bash
   python manage.py migrate
   ```

6. **Create a superuser (admin account):**
   ```bash
   python manage.py createsuperuser
   ```

7. **Start the development server:**
   ```bash
   python manage.py runserver
   ```

## 🛠 Development

Yadgah follows best coding practices to ensure maintainability and quality.

- **Code Linting:** `flake8` for Python.
- **Pre-commit Hooks:** Automates code checks before commits.

### GitHub Actions Workflows
Automated workflows include:
- **Django CI:** Ensures smooth integration.
- **Code Linting:** Maintains style and quality.
- **Pre-commit Checks:** Verifies code before merging.
- **Security Scans:** Detects vulnerabilities early.

## 📜 License

Yadgah is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

## 💬 Contributing

We welcome contributions! To contribute:
1. Fork the repository.
2. Create a new branch for your feature or fix.
3. Submit a pull request with a clear description of changes.

## 🌐 Connect with Us

Have questions or feedback? Reach out via [GitHub Issues](https://github.com/Yadgah/Yadgah/issues) or join our discussions.
