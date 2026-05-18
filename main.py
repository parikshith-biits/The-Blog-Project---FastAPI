from fastapi import FastAPI,Depends,HTTPException
from sqlalchemy.orm import Session
from database import Base,engine,get_db
from models import User,Post
from schemas import UserRegister,UserLogin,PostCreate,PostResponse
from auth import hash_password,verify_password,create_access_token,get_current_user
from roles import require_admin
Base.metadata.create_all(bind=engine)

app = FastAPI(title="The Blog Project")

@app.get("/")
def root():
    return {"message":"Blog API is running"}

@app.post("/register")
def register(
    user:UserRegister,
    db:Session=Depends(get_db)
):
    existing_user = db.query(User).filter(
        User.email==user.email
    ).first() 
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="email already exists"
        )
    new_user=User(
        username=user.username,
        email=user.email,
        hashed_password=hash_password(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message":"User registered sucessfully"}

@app.post("/login")
def login(
    user:UserLogin,
    db:Session=Depends(get_db)
):
    db_user= db.query(User).filter(
        User.email==user.email
    ).first()

    if not db_user:
        raise HTTPException(
            status_code=401,
            detail="invalid credentials"
        )
    if not verify_password(
        user.password,
        db_user.hashed_password
    ):
        raise HTTPException(
            status_code=401,
            detail="invalid credentials"
        )
    token=create_access_token(
    {"sub": str(db_user.id)}
)
    return{
        "access_token":token,
        "token_type":"bearer"
    }

@app.get("/me")
def get_me(
    current_user=Depends(get_current_user)
):
    return{
        "id":current_user.id,
        "username":current_user.username,
        "email":current_user.email,
        "role":current_user.role
    }

@app.post("/posts")
def create_post(
    post: PostCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    new_post = Post(
        title=post.title,
        content=post.content,
        owner_id=current_user.id
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@app.get("/posts", response_model=list[PostResponse])
def get_posts(
    db: Session = Depends(get_db)
):
    posts = db.query(Post).all()
    return posts

@app.put("/posts/{id}")
def update_post(
    id: int,
    updated_post: PostCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    post = db.query(Post).filter(
        Post.id == id
    ).first()

    if post is None:
        raise HTTPException(
            status_code=404,
            detail="Post not found"
        )
    if (
        post.owner_id != current_user.id
        and current_user.role != "admin"
    ):
        raise HTTPException(
            status_code=403,
            detail="Not authorized"
        )
    post.title = updated_post.title
    post.content = updated_post.content
    db.commit()
    db.refresh(post)
    return post


@app.delete("/posts/{id}")
def delete_post(
    id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    post = db.query(Post).filter(
        Post.id == id
    ).first()

    if post is None:
        raise HTTPException(
            status_code=404,
            detail="Post not found"
        )
    if (
        post.owner_id != current_user.id
        and current_user.role != "admin"
    ):
        raise HTTPException(
            status_code=403,
            detail="Not authorized"
        )
    db.delete(post)
    db.commit()
    return {
        "message": "Post deleted"
    }

@app.get("/admin/users")
def get_all_users(
    db: Session = Depends(get_db),
    admin = Depends(require_admin)
):
    users = db.query(User).all()
    return users


@app.delete("/admin/users/{id}")
def delete_user(
    id: int,
    db: Session = Depends(get_db),
    admin = Depends(require_admin)
):
    user = db.query(User).filter(
        User.id == id
    ).first()
    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    db.delete(user)
    db.commit()
    return {
        "message": "User deleted"
    }


