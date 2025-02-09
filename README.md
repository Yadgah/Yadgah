<div align="center">

<p>
    <a href="#">
        <img width="150" src="https://github.com/BDadmehr0/Yadgah/blob/main/favicon.ico" alt="The Yadgah Q&A website">
    </a>
</p>

# Yadgah

Yadgah A Platform for Experience Sharing &amp; Q&amp;A

</div>

Similar to platforms like Quora or StackOverflow, users can share their experiences or ask questions from others.

## Features:

- **User Profiles:** Users can share their questions and experiences.
- **Ask Questions & Receive Answers:** Users can post questions and get answers from the community.
- **Likes, Comments, & Ratings:** Users can like, comment on, and rate the answers.
- **Categories for Questions & Experiences:** Examples include work experiences, education, technology, health, etc.
- **User Ranking System:** Based on their contributions, such as identifying top contributors or best answer providers.


## Installation

### Prerequisites
- Python 3.x
- pip (Python package manager)

### Setup Instructions

1. Clone the repository:
```bash
git clone https://github.com/Yadgah/Yadgah.git
cd Yadgah
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run migrations:
```bash
python manage.py migrate
```

4. Create a superuser:
```bash
python manage.py createsuperuser
```

5. Run the development server:
```bash
python manage.py runserver
```

## Development

The project uses several code quality tools:
- flake8 for Python code linting
- pre-commit hooks
- prettier for frontend formatting

GitHub Actions workflows are set up for:
- Django CI
- Linting
- Pre-commit checks
- Security checks

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Project Structure

Main components:
- Django-based web application
- User authentication and profiles
- Question and answer system
- News section
- Static files and media handling
- Template-based frontend


