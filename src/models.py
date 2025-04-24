from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    username: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    first_name: Mapped[str] = mapped_column(String(80))
    last_name: Mapped[str] = mapped_column(String(80))
    is_active: Mapped[bool] = mapped_column(Boolean(), default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    favorite_planets: Mapped[list["Planet"]] = relationship(
        "Planet", 
        secondary="user_favorites",
        back_populates="favorited_by"
    )
    
    favorite_characters: Mapped[list["Character"]] = relationship(
        "Character", 
        secondary="user_favorites",
        back_populates="favorited_by"
    )

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat()
        }

class Planet(db.Model):
    __tablename__ = 'planets'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    climate: Mapped[str] = mapped_column(String(120))
    terrain: Mapped[str] = mapped_column(String(120))
    population: Mapped[str] = mapped_column(String(120))  # String porque algunos son "unknown"
    diameter: Mapped[int] = mapped_column()
    orbital_period: Mapped[int] = mapped_column()
    swapi_id: Mapped[int] = mapped_column(unique=True)  # ID de la API SWAPI
    
    # Relación
    favorited_by: Mapped[list["User"]] = relationship(
        "User", 
        secondary="user_favorites",
        back_populates="favorite_planets"
    )

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "climate": self.climate,
            "terrain": self.terrain,
            "population": self.population,
            "diameter": self.diameter,
            "orbital_period": self.orbital_period,
            "swapi_id": self.swapi_id
        }

class Character(db.Model):
    __tablename__ = 'characters'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    height: Mapped[int] = mapped_column()
    mass: Mapped[int] = mapped_column()
    hair_color: Mapped[str] = mapped_column(String(50))
    eye_color: Mapped[str] = mapped_column(String(50))
    birth_year: Mapped[str] = mapped_column(String(20))
    gender: Mapped[str] = mapped_column(String(20))
    homeworld_id: Mapped[int] = mapped_column(db.ForeignKey('planets.id'))
    swapi_id: Mapped[int] = mapped_column(unique=True)  # ID de la API SWAPI
    
    # Relaciones
    homeworld: Mapped["Planet"] = relationship("Planet")
    favorited_by: Mapped[list["User"]] = relationship(
        "User", 
        secondary="user_favorites",
        back_populates="favorite_characters"
    )

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "height": self.height,
            "mass": self.mass,
            "hair_color": self.hair_color,
            "eye_color": self.eye_color,
            "birth_year": self.birth_year,
            "gender": self.gender,
            "homeworld": self.homeworld.serialize() if self.homeworld else None,
            "swapi_id": self.swapi_id
        }

class UserFavorites(db.Model):
    __tablename__ = 'user_favorites'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(db.ForeignKey('users.id'))
    planet_id: Mapped[int] = mapped_column(db.ForeignKey('planets.id'), nullable=True)
    character_id: Mapped[int] = mapped_column(db.ForeignKey('characters.id'), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Restricción para asegurar que sea planeta o personaje, pero no ambos
    __table_args__ = (
        db.CheckConstraint(
            '(planet_id IS NOT NULL AND character_id IS NULL) OR (planet_id IS NULL AND character_id IS NOT NULL)',
            name='check_favorite_type'
        ),
    )