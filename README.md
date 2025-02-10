<div align="center">

<p>
    <a href="#">
        <img width="150" src="https://github.com/BDadmehr0/Yadgah/blob/main/favicon.ico" alt="Yadgah Logo">
    </a>
</p>

# Yadgah

**A Platform for Experience Sharing & Q&A**

</div>

Yadgah is a community-driven platform where users can share experiences, ask questions, and engage with others. Inspired by platforms like Quora and StackOverflow, Yadgah empowers users to connect, learn, and grow through knowledge sharing.

---

## ✨ Features

- **User Profiles:** Create and customize your profile to share your questions and experiences.
- **Ask Questions & Get Answers:** Post questions and receive answers from the community.
- **Engage with Content:** Like, comment on, and rate answers to contribute to the discussion.
- **Categorized Content:** Organize questions and experiences into categories such as:
  - Work Experiences
  - Education
  - Technology
  - Health
  - And more!
- **User Ranking System:** Earn recognition based on your contributions, such as being a top contributor or providing the best answers.

---

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

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

4. **Create a superuser (admin account):**
   ```bash
   python manage.py createsuperuser
   ```

5. **Start the development server:**
   ```bash
   python manage.py runserver
   ```

---

## 🛠 Development

Yadgah follows best practices for code quality and maintainability. Here's what we use:

- **Code Linting:** `flake8` for Python code linting.
- **Pre-commit Hooks:** Automatically check code quality before commits.
- **Frontend Formatting:** `prettier` for consistent frontend code formatting.

### GitHub Actions Workflows
We have automated workflows for:
- **Django CI:** Continuous integration for Django.
- **Linting:** Ensures code adheres to style guidelines.
- **Pre-commit Checks:** Automates pre-commit validations.
- **Security Checks:** Identifies potential security vulnerabilities.

---

## 📂 Project Structure

The project is organized as follows:

```
Yadgah/
├── app/                  # Django apps (e.g., users, questions, answers)
├── static/               # Static files (CSS, JS, images)
├── templates/            # HTML templates
├── manage.py             # Django management script
├── requirements.txt      # Python dependencies
├── LICENSE               # MIT License
└── README.md             # Project documentation
```

---

## 📜 License

This project is licensed under the **MIT License**. For more details, see the [LICENSE](LICENSE) file.

---

## 💬 Contributing

We welcome contributions! If you'd like to contribute, please follow these steps:
1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Submit a pull request with a detailed description of your changes.

---

## 🌐 Connect with Us

Have questions or feedback? Reach out to us via [GitHub Issues](https://github.com/Yadgah/Yadgah/issues) or join our community discussions.
