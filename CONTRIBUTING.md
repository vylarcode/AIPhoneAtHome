# Contributing to PhoneAIAtHome

Thank you for your interest in contributing to PhoneAIAtHome! We welcome contributions from the community.

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/YOUR_USERNAME/PhoneAIAtHome/issues)
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - System information (OS, Python version, GPU, etc.)
   - Relevant logs or error messages

### Suggesting Features

1. Check existing [Issues](https://github.com/YOUR_USERNAME/PhoneAIAtHome/issues) for similar requests
2. Create a new issue with the `enhancement` label
3. Describe the feature and its use case
4. Explain why it would benefit the project

### Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests if applicable
5. Ensure all tests pass (`pytest tests/`)
6. Commit with clear messages (`git commit -m 'Add amazing feature'`)
7. Push to your branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

### Development Setup

```powershell
# Clone your fork
git clone https://github.com/YOUR_USERNAME/PhoneAIAtHome.git
cd PhoneAIAtHome

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install in development mode
pip install -r requirements.txt
pip install -e .

# Install dev dependencies
pip install pytest pytest-cov black isort flake8
```

### Code Style

- Follow PEP 8
- Use type hints where appropriate
- Add docstrings to functions and classes
- Keep functions focused and small
- Write tests for new features

### Testing

```powershell
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_audio.py -v
```

### Areas We Need Help

- 🌍 **Internationalization**: Support for multiple languages
- 🎯 **Model Optimization**: Improving latency and accuracy
- 📱 **UI/Dashboard**: Web interface for monitoring calls
- 🔊 **Audio Processing**: Enhanced echo cancellation and noise reduction
- 📚 **Documentation**: Tutorials, guides, and examples
- 🧪 **Testing**: More comprehensive test coverage
- 🐳 **Deployment**: Kubernetes configurations, cloud deployment guides

## Code of Conduct

### Our Standards

- Be respectful and inclusive
- Welcome newcomers and help them get started
- Accept constructive criticism gracefully
- Focus on what's best for the community
- Show empathy towards others

### Unacceptable Behavior

- Harassment, discrimination, or offensive comments
- Personal attacks or trolling
- Publishing others' private information
- Other conduct that could be considered inappropriate

## Questions?

Feel free to:
- Open an issue for questions
- Start a discussion in [Discussions](https://github.com/YOUR_USERNAME/PhoneAIAtHome/discussions)
- Reach out to maintainers

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for helping make PhoneAIAtHome better! 🚀
