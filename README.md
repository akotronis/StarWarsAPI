# Star Wars API

<details>
<summary><h2 style="display: inline;">Setup/Run and Testing Workflow</h2></summary>

### uv installation
- Install uv (Linux/Git Bash): `$ curl -LsSf https://astral.sh/uv/install.sh | sh`
- Enable shell autocompletion for uv commands (sh) (Linux/Git Bash): `$ echo 'eval "$(uv generate-shell-completion bash)"' >> ~/.bashrc`
- Check uv availability: `$ uv`

### Clone project and sync dependencies
- Clone project: `git clone https://github.com/akotronis/StarWarsAPI.git` or `git clone git@github.com:akotronis/StarWarsAPI.git`
- Go to cloned project folder: `$ cd StarWarsAPI`
- Sync all dependencies: `..StarWarsAPI$ uv sync --all-extras`

### Database migrations and superuser
- Create database an tables:
    - `..StarWarsAPI$ uv run python manage.py makemigrations`
    - `..StarWarsAPI$ uv run python manage.py migrate`
- Create superuser (Only for django admin): `..StarWarsAPI$ uv run python manage.py createsuperuser`

### Django settings/launch app
- Create a _secret_key_ and put it as value on the _SECRET_KEY_ variable of a _../StarWarsAPI/.env_ file: `..StarWarsAPI$ uv run python -c "import os; print(os.urandom(40).hex())"`
- Run the server (accesible on _localhost:8000_): `$ uv run python manage.py runserver 8000`

### Urls
#### Interfaces
- Django admin: `http://localhost:8000/admin`
- Browser API: `http://localhost:8000/api`
- Swagger: `http://localhost:8000/schema/swagger`

#### Resources
- Films: `http://localhost:8000/api/films`
- Characters: `http://localhost:8000/api/characters`
- Starships: `http://localhost:8000/api/starships`

#### Fetch SWAPI data and populate database
- `http://localhost:8001/api/swapi-fetch-populate`

### Tests and coverage report
- Run tests and create coverage html report: `..StarWarsAPI$ uv run coverage run manage.py test && uv run coverage html`
- Inspect _../StartWarsAPI/htmlcov/index.html_ coverage report
</details>

<details>
<summary><h2 style="display: inline;">Design/Implementation details</h2></summary>

### Database schema
- The SWAPI resource payloads suggests the object relations depicted in the below diagram ([DrawSQL](https://drawsql.app/teams/akotronis-team/diagrams/starwarsapi)), where:
    - _Characters_ correspond to the _People_ SWAPI url resource and to the _"pilots"_ field in _Starships_ resource.
    - _Selected_ fields are used (indicatively) for the models represenations.
<p><img src="./resources/database-schema.png" alt="Database Schema" width="800"/></p>

### Implementation
- Views/Serializers:
    - Used Mixin Pattern to ensure DRY principle
- Services:
    - Used separate resource-specific creation functions to maintain clarity and avoid over-abstracting distinct domain logic.
    - Traded temporary memory usage for database performance using in-memory mappings and bulk operations to minimize queries.
</details>

<details>
<summary><h2 style="display: inline;">Coverage Report</h2></summary>

<p><img src="./resources/coverage-report.png" alt="Coverage Report" width="800"/></p>

</details>

<details>
<summary><h2 style="display: inline;">Sample API screenshots</h2></summary>

#### SWAPI Fetch Populate Success
<p><img src="./resources/swapi-fetch-populate-success.png" alt="SWAPI Fetch Populate Success" width="800"/></p>

#### SWAPI Fetch Populate (Threaded) Success
<p><img src="./resources/swapi-fetch-populate-threaded-success.png" alt="SWAPI Fetch Populate (Threaded) Success" width="800"/></p>

#### SWAPI Fetch Populate Validation Errors
<p><img src="./resources/swapi-fetch-populate-validation-errors.png" alt="SWAPI Fetch Populate Validation Errors" width="800"/></p>

#### Films Paginated Response
<p><img src="./resources/films-paginated-response.png" alt="Films Paginated Response" width="800"/></p>

#### Films Filter Param Search
<p><img src="./resources/films-filter-param-search.png" alt="Films Filter Param Search" width="800"/></p>

#### Swagger
<p><img src="./resources/swagger.png" alt="Swagger" width="800"/></p>

</details>