# Contributing to IONOS Cloud Network Hub

Thank you for your interest in contributing! This document provides guidelines for reporting issues, suggesting features, and submitting code changes.

## Reporting Bugs

Found a bug? Please help us fix it by opening a GitHub issue with:

- A clear, descriptive title
- Steps to reproduce the issue
- Expected behavior vs. actual behavior
- Your environment (OS, browser, Python version)
- Screenshots if applicable

Visit [Issues](https://github.com/rijeshharidas/ionos-cloud-network-hub/issues) to create a new bug report.

## Suggesting Features

We welcome feature suggestions! Open a GitHub issue with:

- A descriptive title starting with "Feature Request:"
- Clear explanation of the problem it solves
- Proposed solution or examples
- Any alternative approaches you've considered

## Development Setup

Getting started is simple:

```bash
git clone https://github.com/rijeshharidas/ionos-cloud-network-hub.git
cd ionos-cloud-network-hub
python3 serve.py
```

Open your browser to `http://localhost:8080` and start developing.

## Code Style Guidelines

IONOS Cloud Network Hub follows these conventions:

- **Single-file architecture**: Keep the main application in a single HTML/JS file for simplicity
- **D3.js patterns**: Use D3 selections and data binding idiomatically
- **CSS variables**: Define colors and sizing as CSS custom properties for consistency
- **Comments**: Document complex logic, especially data transformations
- **Naming**: Use descriptive variable/function names; abbreviations only for common conventions (e.g., `d` for data)

## Pull Request Process

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Make your changes following code style guidelines
4. Test thoroughly in your browser
5. Commit with clear messages: `git commit -m "Add feature: description"`
6. Push to your fork and open a Pull Request
7. Reference any related issues (e.g., "Fixes #123")
8. Ensure your PR title clearly describes the change

## Questions?

Open a discussion in [GitHub Discussions](https://github.com/rijeshharidas/ionos-cloud-network-hub/discussions) or reach out to the maintainers.

Happy coding!
