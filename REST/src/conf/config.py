from pydantic import BaseSettings


class Settings(BaseSettings):
    sqlalchemy_database_url: str = 'postgresql+psycopg2://user:password@127.0.0.1:5432/db_name'
    secret_key_jwt: str = 'secret key'
    algorithm: str = 'HS256'
    mail_username: str = 'example@meta.ua'
    mail_password: str ='secretPassword'
    mail_from: str = 'mail@gmail.com'
    mail_port: int = 123
    mail_server: str ='smtp.gmail.com'
    redis_host: str = '127.0.0.1'
    redis_port: int = 6379
    cloudinary_name: str = 'name'
    cloudinary_api_key: str = 12343
    cloudinary_api_secret: str = 'secret_key'

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
