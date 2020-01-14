# Full Stack Casting Agency API 

## Getting Started

### Installing Dependencies

#### Python 3.7

Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

#### Virtual Enviornment

We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organaized. Instructions for setting up a virual enviornment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

#### PIP Dependencies

Once you have your virtual environment setup and running, install dependencies by naviging to the `/backend` directory and running:

```bash
pip install -r requirements.txt
```

This will install all of the required packages we selected within the `requirements.txt` file.

##### Key Dependencies

- [Flask](http://flask.pocoo.org/)  is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM we'll use handle the lightweight sqlite database. You'll primarily work in app.py and can reference models.py. 

## Running the server

Ensure you are working using your created virtual environment.

**Create DB**
```
createdb capstone
```

To run the server, execute:

```bash
export FLASK_APP=app.py
export FLASK_ENV=development
flask run
```

Setting the `FLASK_ENV` variable to `development` will detect file changes and restart the server automatically.

## Casting Agency Specifications

The Casting Agency models a company that is responsible for creating movies and managing and assigning actors to those movies. You are an Executive Producer within the company and are creating a system to simplify and streamline your process. 

**Roles**

1. `Casting Assistant` Can view actors and movies
2. `Casting Director` All permissions a Casting Assistance has, Can add or delete an actor from the database, Can modify actors or movies
3. `Executive Producer` All permissions a Casting Director has, Can Add pr delete a movie from the database, Can Create a cast record, Can assign a cast to a movie and Can assign actors to a cast 

**DB Model**
1. `Movies` table holds movie information, and have a one to one relationship with `Casts` table
2. `Actor` table holds actor information, and have a one to many relationship with `Starring` table
3. `Casts` table allows the user to assign a cast to a movie, and have a one to many relationship with `Starring` table
4. `Starring` table allows the user to assign an actor to a cast

## REST Resource

**Getting Started**
- Base URL: This app is hosted locally and the default url is http://127.0.0.1:5000/
- Authentication: This version of the application requires authentication via Auth0. Bearer Token jwt is required to make requests to this API endpoints, see the roles above

**Error Handling**
```
{
  "error": 404,
  "message": "Resource not Found",
  "success": false
}
```
The API will return one of 6 error types when request fails.
- 400: Bad Request
- 404: Resource Not Found
- 422: Unprocessable Entity
- 500: Internal Server Error
- 403: "Permission Denied"
- 401: "Authorization Failed"

**Endpoints**


GET '/actors'
- Fetches a list of actors 
- Request Arguments: None
- Authorization: Bearer Token
- Returns: a list of actors 
- Sample: curl http://127.0.0.1:5000/actors
```
{
    "actors": [
        {
            "age": 38,
            "gender": "male",
            "id": 2,
            "name": "Brian J. Smith",
            "nationality": "United States"
        },
        {
            "age": 34,
            "gender": "female",
            "id": 3,
            "name": "Tracy Ifeachor",
            "nationality": "Nigeria"
        },
        {
            "age": 32,
            "gender": "female",
            "id": 4,
            "name": "Han Hyo-joo",
            "nationality": "South Korea"
        },
        {
            "age": 29,
            "gender": "male",
            "id": 5,
            "name": "Jeremy Irvine",
            "nationality": "United Kingdom"
        }
    ],
    "success": true
}
```

GET '/actors/{actor_id}'
- Fetches an actor by ID
- Request Arguments: None
- Authorization: Bearer Token
- Returns: an actor by id 
- Sample: curl http://127.0.0.1:5000/actors/2
```
{
    "actor": {
        "age": 38,
        "gender": "male",
        "id": 2,
        "name": "Brian J. Smith",
        "nationality": "United States"
    },
    "success": true
}
```

GET '/actors/nationality/{nationality}'
- Fetches filters actor by nationality
- Request Arguments: None
- Authorization: Bearer Token
- Returns: a list of actors of given nationality
- Sample: curl http://127.0.0.1:5000/actors/nationality/Nigeria
```
{
    "actors": [
        {
            "age": 34,
            "gender": "female",
            "id": 3,
            "name": "Tracy Ifeachor",
            "nationality": "Nigeria"
        }
    ],
    "success": true
}
```

GET 'actors/{actor_id}/movies'
- Fetches all the movies actor is starred in
- Request Arguments: None
- Authorization: Bearer Token
- Returns: a list of movie titles
- Sample: curl http://127.0.0.1:5000/actors/2/movies
```
{
    "movies": [
        "Treadstone"
    ],
    "success": true
}
```

GET '/movies'
- Fetches All movies in DB
- Request Arguments: None
- Authorization: Bearer Token
- Returns: a list of movies with descriptions
- Sample: curl http://127.0.0.1:5000/movies
```
{
    "movies": [
        {
            "description": "This is a sample desc",
            "id": 2,
            "release_date": "Tue Mar 02 2021",
            "title": "Rise of Skywalker"
        },
        {
            "description": "From the world of Jason Bourne, agents across the globe are awakening to resume deadly missions.",
            "id": 4,
            "release_date": "Sat Jan 04 2020",
            "title": "Treadstone"
        }
    ],
    "success": true
}
```

GET '/movies/{movie_id}'
- Fetches movie by ID
- Request Arguments: None
- Authorization: Bearer Token
- Returns: a movie by id
- Sample: curl http://127.0.0.1:5000/movies/4
```
{
    "movie": {
        "description": "From the world of Jason Bourne, agents across the globe are awakening to resume deadly missions.",
        "id": 4,
        "release_date": "Sat Jan 04 2020",
        "title": "Treadstone"
    },
    "success": true
}
```

GET '/movies/{movie_id}/cast'
- Fetches cast list of actors in the specified movie
- Request Arguments: None
- Authorization: Bearer Token
- Returns: cast list for a movie
- Sample: curl http://127.0.0.1:5000/movies/4/cast
```
{
    "casts": [
        "Brian J. Smith",
        "Tracy Ifeachor"
    ],
    "movie": "Treadstone",
    "success": true
}
```

GET '/casts'
- Fetches All casts in DB
- Request Arguments: None
- Authorization: Bearer Token
- Returns: a list of all casts
- Sample: curl http://127.0.0.1:5000/casts
```
{
    "casts": [
        {
            "id": 1,
            "movie_id": 2
        },
        {
            "id": 4,
            "movie_id": 4
        }
    ],
    "success": true
}
```

GET '/casts/{cast_id}'
- Fetches cast by id
- Request Arguments: None
- Authorization: Bearer Token
- Returns: cast by id
- Sample: curl http://127.0.0.1:5000/casts/4
```
{
    "cast": {
        "id": 4,
        "movie_id": 4
    },
    "success": true
}
```

GET '/stars'
- Fetches all stars in DB
- Request Arguments: None
- Authorization: Bearer Token
- Returns: a list of all stars
- Sample: curl http://127.0.0.1:5000/stars
```
{
    "stars": [
        {
            "actor_id": 2,
            "cast_id": 4,
            "id": 6
        },
        {
            "actor_id": 3,
            "cast_id": 4,
            "id": 7
        }
    ],
    "success": true
}
```

GET '/stars/{star_id}'
- Fetches star by id
- Request Arguments: None
- Authorization: Bearer Token
- Returns: star by id
- Sample: curl http://127.0.0.1:5000/stars/7
```
{
    "star": {
        "actor_id": 3,
        "cast_id": 4,
        "id": 7
    },
    "success": true
}
```




POST '/questions'
- Creates a question
- Request Arguments: None
- Returns: 201 response
- Sample: curl -data '{"question":"What is my name", "answer": "John", "category": "2", "difficulty": "3"}' -H "Content-Type: application/json" -X ttp://http://127.0.0.1:5000/questions
```
{
  "success": true
}
```

POST '/questions'
- Get questions based on a search term, search is case insensitive
- Request Arguments: None
- Sample: curl -d '{"searchTerm":"vinci"}' -H "Content-Type: application/json" -X POST http://127.0.0.1:5000/questions
```
{
  "currentCategory": {
    "id": 1,
    "type": "Art"
  },
  "questions": [
    {
      "answer": "Vinci",
      "category": "1",
      "difficulty": 3,
      "id": 1,
      "question": "In which town was Leonardo da Vinci born?"
    }
  ],
  "success": true,
  "total_questions": 1
}
```

GET '/categories/{categoryId}/questions'
- Fetches questions based on category
- Request Arguments: None
- Returns: An object with keys (questions, current_category, success, total_questions)
- Sample: http://127.0.0.1:5000/categories/4/questions
```
{
  "current_category": {
    "id": 4,
    "type": "History"
  },
  "questions": [
    {
      "answer": "Muhammad Ali",
      "category": 4,
      "difficulty": 1,
      "id": 9,
      "question": "What boxer's original name is Cassius Clay?"
    },
    {
      "answer": "George Washington Carver",
      "category": 4,
      "difficulty": 2,
      "id": 12,
      "question": "Who invented Peanut Butter?"
    },
    {
      "answer": "Scarab",
      "category": 4,
      "difficulty": 4,
      "id": 23,
      "question": "Which dung beetle was worshipped by the ancient Egyptians?"
    }
  ],
  "success": true,
  "total_questions": 3
}
```

POST '/quizzes'
- Fetches questions to play the quiz
- Request Body: json with two keys(quiz_category, previous_questions), category id and a list of previous question ids
- Return: A random question within the given category, if provided, and that is not one of the previous questions
- Sample: http://127.0.0.1:5000/quizzes
```
{
  "question": {
    "answer": "Vulture",
    "category": "5",
    "difficulty": 4,
    "id": 6,
    "question": "In Disney’s The Jungle Book what kind of animal is Ringo? Monkey, snake, vulture, elephant"
  }
}
```

DELETE '/questions/{questionId}'
- Deletes a question
- Sample: http://127.0.0.1:5000/questions/5
```
{
  "success": true
}
```


## Testing
To run the tests, run
```
dropdb capstone_test
createdb capstone_test
python3 -m unittest test_app.py
```