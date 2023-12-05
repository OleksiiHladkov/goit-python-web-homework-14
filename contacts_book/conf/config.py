from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    postgres_db: str = "app_name"
    postgres_user: str = "user_name"
    postgres_password: str = "password"
    postgres_port: int = 5432
    postgres_host: str = "localhost"
    sqlalchemy_database_url: str = "postgresql+psycopg2://user_name:password@localhost:5432/app_name"
    secret_key: str = "secret_key"
    algorithm: str = "algorithm"
    mail_username: str = "exemple@ex.ua"
    mail_password: str = "password"
    mail_from: str = "exemple@ex.ua"
    mail_port: int = 465
    mail_server: str = "smtp.ex.ua"
    redis_host: str = "localhost"
    redis_port: int = 6379
    origins: str = "http://localhost:8000"
    cloudinary_name: str = "fgfgfgfgfgf"
    cloudinary_api_key: str = "12121212121212"
    cloudinary_api_secret: str = "7gh7gh7gh7gh7gh7gh7gh7gh7gh7"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()