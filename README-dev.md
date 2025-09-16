# Star Wars API

<details>
<summary><h2 style="display: inline;">Develpment Workflow</h2></summary>

### Local uv installation
- Install uv (Linux/Git Bash): `$ curl -LsSf https://astral.sh/uv/install.sh | sh`
- Enable shell autocompletion for uv commands (sh) (Linux/Git Bash): `$ echo 'eval "$(uv generate-shell-completion bash)"' >> ~/.bashrc`
- Check uv availability: `$ uv`

### Git/Github setup
- Git initialization: `..StarWarsAPI$ git init`
- Check git initialization: `..StarWarsAPI$ git status`
- Add a _README_ file
- Add project content: `..StarWarsAPI$ git add .`
- Commit uv project content: `..StarWarsAPI$ git commit -m "project setup"`
- Rename master branch: `..StarWarsAPI$ git branch -M main`
- Create Github **"StarWarsAPI"**
- Add Github remote: `..StarWarsAPI$ git remote add origin https://github.com/akotronis/StarWarsAPI.git`
- Check remote: `..StarWarsAPI$ git remote -v`
- Checkout and work on dev branch: `..StarWarsAPI$ git checkout -b dev`
- Push uv project content to dev branch: `..StarWarsAPI$ git push origin dev`

### Backend project folder and uv required files
- Make the _backend_ project folder and cd into it: `..StarWarsAPI$ mkdir backend && cd backend`
- Create uv files required for the build: `..backend$ uv init --python 3.12 --vcs none --no-readme && uv lock && rm main.py`

### Dockerfile
Keep the below (for development) to include uv in the final image for ease.
- `COPY --from=build /root/.local /root/.local`
- `ENV PATH="/root/.local/bin/:$PATH"`

Keep the container idle for easier development inside the container: `CMD ["tail", "-f", "/dev/null"]`

### docker-compose file
-  Bind mount backend working folder for easier development inside the container: `./backend:/opt/backend`

### Inside the container

#### Dependencies
- Add dependencies: `..backend$ uv add django psycopg2-binary requests djangorestframework python-dotenv drf-spectacular`
- Add dev dependencies: `..backend$ uv add --dev coverage`

#### Django project/app/mirations/superuser
- Create the Django project: `..backend$ uv run django-admin startproject swapi .`
- Create the Django project: `..backend$ uv run python manage.py startapp app`
- After model implementation:
    - `..backend$ uv run python manage.py makemigrations`
    - `..backend$ uv run python manage.py migrate`
    - `..backend$ uv run python manage.py createsuperuser`

#### Django settings/launch app
- Create a _secret_key_ and put it as value on the _SECRET_KEY_ variable of a _../StarWarsAPI/.env_ file: `..backend$ uv run python -c "import os; print(os.urandom(40).hex())"`

### For production
#### Dockerfile
Comment out the below (image size is reduced)
- `COPY --from=build /root/.local /root/.local`
- `ENV PATH="/root/.local/bin/:$PATH"`

Install only the required dependencies: `RUN uv sync --locked` (not the extras)

Run the sh file with the correct commands `CMD ["./run.sh"]`

#### docker-compose file
-  Remove the bind mount: `./backend:/opt/backend`


### Tests and coverage report
- Run tests and create coverage html report:
    - In the container: `..backend$ uv run coverage run manage.py test && uv run coverage html` (if uv is in the final image) OR
    - In the container: `..StarWarsAPI$ python -m coverage run manage.py test && python -m coverage html` OR
    - Outside the container: `..backend$ docker exec -it ctr-sw-back bash -c "python -m coverage run manage.py test && python -m coverage html"`
- Inspect _../StartWarsAPI/coverage/backend/htmlcov/index.html_ coverage report (Make sure the folder bind mount is in the compose file)
</details>

<details>
<summary><h2 style="display: inline;">CI/CD</h2></summary>

<!-- ### Secrets
On **Gihub**:
- Click on _Settings_ tab on the project repo
- In the left sidebar, click _on Secrets and variables > Actions_
- Click the _New repository secret_ button
- Example:
    - Add _SECRET_KEY_ and its value
    - Reference the secret inside workflow file: `..gihub/workflows/my-workflow-file.yml` with `${{ secrets.SECRET_KEY }}`
</details> -->