# Star Wars API

<details>
<summary><h2 style="display: inline;">Develpment Workflow</h2></summary>

### uv installation
- Install uv (Linux/Git Bash): `$ curl -LsSf https://astral.sh/uv/install.sh | sh`
- Enable shell autocompletion for uv commands (sh) (Linux/Git Bash): `$ echo 'eval "$(uv generate-shell-completion bash)"' >> ~/.bashrc`
- Check uv availability: `$ uv`

### uv projet setup
- Create local repo folder: `$ mkdir StarWarsAPI && cd StarWarsAPI`
- Create a project managed by uv: `..StarWarsAPI$ uv init --python 3.12 --description "Star Wars API" && rm main.py`

### Git/Github setup
- Check git initialization: `..StarWarsAPI$ git status`
- Add uv project content: `..StarWarsAPI$ git add .`
- Commit uv project content: `..StarWarsAPI$ git commit -m "uv project setup"`
- Rename master branch: `..StarWarsAPI$ git branch -M main`
- Create Github **"StarWarsAPI"**
- Add Github remote: `..StarWarsAPI$ git remote add origin https://github.com/akotronis/StarWarsAPI.git`
- Check remote: `..StarWarsAPI$ git remote -v`
- Checkout and work on dev branch: `..StarWarsAPI$ git checkout -b dev`
- Push uv project content to dev branch: `..StarWarsAPI$ git push origin dev`

### Dependencies
- Add dependencies: `..StarWarsAPI$ uv add django requests djangorestframework python-dotenv drf-spectacular`
- Add dev dependencies: `..StarWarsAPI$ uv add --dev coverage`

### Django project/app/mirations/superuser
- Create the Django project: `..StarWarsAPI$ uv run django-admin startproject swapi .`
- Create the Django project: `..StarWarsAPI$ uv run python manage.py startapp app`
- After model implementation:
    - `..StarWarsAPI$ uv run python manage.py makemigrations`
    - `..StarWarsAPI$ uv run python manage.py migrate`
    - `..StarWarsAPI$ uv run python manage.py createsuperuser`

### Django settings/launch app
- Create a _secret_key_ and put it as value on the _SECRET_KEY_ variable of a _../StarWarsAPI/.env_ file: `..StarWarsAPI$ uv run python -c "import os; print(os.urandom(40).hex())"`
- Run the server (accesible on _localhost:800_): `$ uv run python manage.py runserver 8000`


### Tests and coverage report
- Run tests and create coverage html report: `..StarWarsAPI$ uv run coverage run manage.py test && uv run coverage html`
- Inspect _../StartWarsAPI/htmlcov/index.html_ coverage report
</details>

<details>
<summary><h2 style="display: inline;">CI/CD</h2></summary>

### Secrets
On **Gihub**:
- Click on _Settings_ tab on the project repo
- In the left sidebar, click _on Secrets and variables > Actions_
- Click the _New repository secret_ button
- Example:
    - Add _SECRET_KEY_ and its value
    - Reference the secret inside workflow file: `..gihub/workflows/my-workflow-file.yml` with `${{ secrets.SECRET_KEY }}`
</details>