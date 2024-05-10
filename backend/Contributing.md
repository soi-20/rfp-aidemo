## Getting Started

1. Fork the repository on GitHub.
2. Clone your forked repository to your local machine.
3. Install the required dependencies by running pip install -r requirements.txt.

## Making Changes

1. Create a new branch for your changes: git checkout -b feature/your-feature-name.
2. Update the template.py file with the new site name and run the code to download data from SharePoint, save site details in the database, and save embeddings on Pinecone.
3. Add a new prompt for the new site name in the prompts.py file by copying an existing prompt and changing the site name.
4. Head over to the app.py file and add a new route for the new site. Change the prompt and site name in the new route.
5. Test your changes locally to ensure they work as expected.
6. Commit your changes with a descriptive commit message: git commit -m "Add support for new site: [site name]".
7. Push your changes to your forked repository: git push origin feature/your-feature-name.
8. Create a new pull request from your forked repository to the original repository.

## Coding Guidelines

1. Follow the existing code style and conventions used in the project.
2. Write clear and concise comments to explain your code.
3. Test your changes thoroughly before submitting a pull request.
4. Keep your pull requests focused on a single feature or bug fix.
