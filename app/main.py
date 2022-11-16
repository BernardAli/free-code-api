from typing import Optional
import time

from fastapi import FastAPI, Body, Response, status, HTTPException, Depends
from pydantic import BaseModel

from random import randrange

import psycopg2
from psycopg2.extras import RealDictCursor
from sqlalchemy.orm import Session

from . import models
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None


class UpdatePost(Post):
    pass


while True:
    try:
        conn = psycopg2.connect(host='localhost', database='free_code_api', user='allgift', password='Matt6:33',
                                cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("Database Connection Was Successful")
        break
    except Exception as error:
        print("Connection to database failed")
        print(f"Error {error}")
        time.sleep(5)


my_posts = [
    {
        "id": 1,
        "title": "First Post",
        "content": "Content of first post",
    },
    {
        "id": 2,
        "title": "Second Post",
        "content": "Content of second post post",
    }
]


def find_post(id):
    for p in my_posts:
        if p["id"] == id:
            return p


def find_index_post(id):
    for i, p in enumerate(my_posts):
        if p['id'] == id:
            return i


@app.get("/")
def root():
    return {"message": "Hello Free Code APIs"}


@app.get("/posts")
def posts():
    cursor.execute("""SELECT * FROM posts""")
    posts = cursor.fetchall()
    print(posts)
    return {"data": posts}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
def posts(post: Post):
    # post_dict = post.dict()
    # post_dict['id'] = randrange(0, 1e10)
    # my_posts.append(post_dict)
    cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *""",
                   (post.title, post.content, post.published))
    new_post = cursor.fetchone()
    conn.commit()
    return {f"data": new_post}


@app.get("/posts/{id}")
def posts(id: int):
    # post = find_post(id)
    cursor.execute("""SELECT * FROM posts WHERE id=%s""", str(id))
    post = cursor.fetchone()
    if not post:
        # response.status_code = status.HTTP_404_NOT_FOUND
        # return {"message": f"Post with id {id} was not found"}
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} was not found")
    return {"data_detail": post}


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def posts(id: int):
    # deleting post
    # find the index
    # index = find_index_post(id)
    # if not index:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} was not found")
    # my_posts.pop(index)
    cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING *""", (str(id), ))
    deleted_post = cursor.fetchone()
    conn.commit()
    if not deleted_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} was not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id}", status_code=status.HTTP_202_ACCEPTED)
def posts(id: int, post: UpdatePost):
    # deleting post
    # find the index
    # index = find_index_post(id)
    # if not index:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} was not found")
    #
    # post_dict = post.dict()
    # post_dict['id'] = id
    # my_posts[index] = post_dict

    cursor.execute("""UPDATE posts SET title=%s, content=%s, published=%s WHERE id=%s RETURNING *""",
                   (post.title, post.content, post.published, str(id)))
    post = cursor.fetchone()
    conn.commit()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} was not found")
    return {"data": post}