from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):     # la usi al posto delle costanti hardcodate
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "LogSpy"
    log_level: str = "INFO"
    database_url: str = "sqlite:///./logspy.db"
    secret_key: str
    access_token_expire_minutes: int = 60
    max_upload_mb: int = 20


settings = Settings() #"Pylance/Pyright fanno analisi statica: leggono i tipi, non eseguono il codice. Sono ottimi per catturare errori prima del run, ma ciechi rispetto a comportamenti dinamici come l'injection da variabili d'ambiente.
