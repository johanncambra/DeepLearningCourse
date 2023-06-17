import typing
from pathlib import Path
from typing import Union
import pandas as pd
from faker import Faker
fake = Faker()

PERSONAS = ['id', 'Full Name', 'year of birth', 'Gender', 'Zip Code']
USUARIOS = ['id', 'Occupation', 'Active Since']
TRABAJADORES = ['id', 'Position', 'Category', 'Working Hours', 'Start Date']


def generate_movie() -> dict:
    generos = ['Action', 'Adventure', 'Animation', "Children's",
               'Comedy', 'Crime', 'Documentary', 'Drama',
               'Fantasy', 'Film-Noir', 'Horror', 'Musical',
               'Mystery', 'Romance', 'Sci-Fi', 'Thriller',
               'War', 'Western', 'unknown']
    return {
        'Name': ' '.join(fake.words()),
        'Release Date': fake.date_time().strftime('%Y-%m-%d %H:%M:%S'),
        'IMDB URL': fake.url(),
        'Gender': [fake.random_element(elements=generos), fake.random_element(elements=generos)]
    }


def generate_score() -> dict:
    return {'user_id': fake.random_int(),
            'movie_id': fake.random_int(),
            'score': fake.random_int(min=1, max=5),
            'Date': fake.date_time().strftime('%Y-%m-%d %H:%M:%S')
            }


def generate_person() -> dict:

    return {
        'id': fake.random_int(),
        'full_name': fake.name(),
        'year_of_birth': int(fake.year()),
        'gender': fake.random_element(elements=('M', 'F')),
        'zip_code': fake.zipcode()
    }


def generate_user() -> dict:
    return {'id': fake.random_int(),
            'occupation': fake.job(),
            'active_since': fake.date_time().strftime('%Y-%m-%d %H:%M:%S')
            }


def generate_worker() -> dict:
    return {'id': fake.random_int(),
            'Position': fake.job(),
            'Category': fake.random_element(elements=('A', 'B', 'C')),
            'Working Hours': fake.random_element(elements=('Full Time', 'Part Time')),
            'Start Date': fake.date()
            }


def validate_params(constraints):
    def decorator_init(init_method):
        def wrapper(self, *args, **kwargs):
            params = dict(
                zip(init_method.__code__.co_varnames[1:], args), **kwargs)
            for param, constrain in constraints.items():
                param_value = params.get(param)
                if typing.get_origin(constrain) is Union:
                    if not any(isinstance(param_value, t) for t in constrain.__args__):
                        types = ', '.join(
                            t.__name__ for t in constrain.__args__)
                        raise ValueError(
                            f"El parámetro '{param}' debe ser de tipo {types}")
                else:
                    if not isinstance(param_value, constrain):
                        raise ValueError(
                            f"El parámetro '{param}' debe ser de tipo {constrain.__name__}")
            init_method(self, **params)
        return wrapper
    return decorator_init


class DataBase:
    @classmethod
    def read(self) -> None:
        """Carge la base de datos desde el archivo indicado por dir_database.
        """
        if not isinstance(self.database, pd.DataFrame):
            try:
                self.database = pd.read_csv(self.dir_database)
                print(
                    f"La base de datos {self.__name__} fue cargada exitosamente.")
            except FileNotFoundError:
                print("No se pudo encontrar el archivo de base de datos.")
            except Exception as e:
                print(f"Ocurrió un error al leer la base de datos: {e}")
        return

    @classmethod
    def write(self) -> None:
        """Guarda la base de datos en el archivo indicado por dir_database.
        """
        try:
            self.database.to_csv(self.dir_database, index=False)
            print("Base de datos guardada exitosamente.")
        except Exception as e:
            print(f"Ocurrió un error al escribir la base de datos: {e}")
        return

    @classmethod
    def update(self, index: int, element: dict) -> None:
        """Actualiza el elemento indicado por index de la base de datos.
        Args:
            index (int): indice del elemento a actualizar. Debe estar presente en la base de datos.
            element (dict): diccionario con los campos a actualizar.
        """
        if index not in self.database.index:
            print("El elemento no está presente en la base de datos.")
            return

        # se lleva el elemento al formato de la base de datos
        element = self.to_class(element=element)

        # se valida que los campos estén presentes en la base de datos
        for col in element:
            if col not in self.database.columns:
                print(
                    f"El campo '{col}' no está presente en la base de datos.")
                return

        # se valida que los datos del nuevo elemento no estén repetidos
        if self._element_exist(element, index):
            return

        self.database.loc[index] = element
        print("Elemento actualizado exitosamente.")
        return

    @classmethod
    def new(self, element: dict) -> None:
        """Crear un nuevo elemento en la base de datos.
        Args:
            element (dict): Diccionario con los campos del nuevo elemento.
        """
        element = self.to_class(element=element)
        index = self.database.index[-1] + 1
        for col in element:
            if col not in self.database.columns:
                print(
                    f"El campo '{col}' no está presente en la base de datos.")
                return

        # existe elemento en base de datos
        if self._element_exist(element):
            return

        self.database.loc[index] = element
        print("Elemento creado exitosamente.")
        return

    @classmethod
    def get(self, index=None):
        """Obtiene un elemento de la base de datos indicado por index.

        Args:
            index (int): indice del elemento a tomar. Debe estar presente en la base de datos.

        Returns: retorna un objeto de la clase.
        """
        if index is None:
            index = self.database.index[-1]

        if index not in self.database.index:
            print("El elemento no está presente en la base de datos.")
            return
        return self.from_dict(data=self.database.loc[index].to_dict())

    @classmethod
    def delete(self, index: int) -> None:
        """Elimina un elemento de la base de datos indicado por index.

        Args:
            index (int): indice del elemento a eliminar. Debe estar presente en la base de datos.
        """

        if index not in self.database.index:
            print("El elemento no está presente en la base de datos.")
            return
        self.database.drop(index, inplace=True)
        print("Elemento eliminado exitosamente.")
        return


class Personas(DataBase):
    _validate_constraints = {
        'id': Union[int, None],
        'full_name': Union[str, None],
        'year_of_birth': Union[int, None],
        'gender': Union[str, None],
        'zip_code': Union[str, None],
        'dir_database': Union[str, Path, None]
    }
    database = None

    @validate_params(_validate_constraints)
    def __init__(self, id=None, full_name=None, year_of_birth=None, gender=None, zip_code=None, dir_database=None):
        if dir_database != None:
            Personas.dir_database = dir_database
            self.read()
        self.id = id
        self.full_name = full_name
        self.year_of_birth = year_of_birth
        self.gender = gender
        self.zip_code = zip_code

    def __repr__(self):
        return f"Persona: {self.full_name}, {self.gender}, {self.year_of_birth}, {self.zip_code}"

    @classmethod
    def from_dict(cls, data, dir_database=None):
        return cls(
            id=data['id'],
            full_name=data['Full Name'],
            year_of_birth=data['year of birth'],
            gender=data['Gender'],
            zip_code=data['Zip Code'],
            dir_database=dir_database
        )

    @classmethod
    def to_class(self, element: dict) -> dict:
        return {
            'id': element['id'],
            'Full Name': element['full_name'],
            'year of birth': element['year_of_birth'],
            'Gender': element['gender'],
            'Zip Code': element['zip_code']
        }

    @classmethod
    def _element_exist(self, element: dict, index: int = None) -> bool:
        """Valida si el elemento ya existe en la base de datos.
            Además, revisa que no esté asignado el id."""

        # cuando indice es None, se usa la funcion para crear un nuevo elemento
        if index is None:
            if (self.database == element).all(axis=1).any():
                print("El elemento ya está presente en la base de datos.")
                return True

            if (self.database['id'] == element['id']).any():
                print("El id ya está asignado en la base de datos.")
                return True
            return False
        # cuando indice no es None, se usa la funcion para actualizar un elemento y que no quede repetido
        else:
            if (self.database[self.database.index != index] == element).all(axis=1).any():
                print("El elemento ya está presente en la base de datos.")
                return True
            if (self.database[self.database.index != index]['id'] == element['id']).any():
                print("El id ya está asignado en la base de datos.")
                return True
            return False


class Usuarios(Personas):
    _validate_constraints = {
        'id': Union[int, None],
        'occupation': Union[str, None],
        'active_since': Union[str, None],
        'dir_database': Union[str, Path, None]
    }
    database = None
    persona = Personas()

    @validate_params(_validate_constraints)
    def __init__(self, id=None, occupation=None, active_since=None, dir_database=None):
        if dir_database != None:
            Usuarios.dir_database = dir_database
        self.read()
        self.id = id
        self.occupation = occupation
        self.active_since = active_since

    def __repr__(self):
        return f"Usuario: {self.id}, {self.occupation}, {self.active_since}"

    @classmethod
    def from_dict(cls, data, dir_database=None):
        return cls(
            id=data['id'],
            occupation=data['Occupation'],
            active_since=data['Active Since'],
            dir_database=dir_database
        )

    @classmethod
    def to_class(self, element: dict) -> dict:
        return {
            'id': element['id'],
            'Occupation': element['occupation'],
            'Active Since': element['active_since']
        }

    @classmethod
    def _element_exist(self, element: dict, index: int = None) -> bool:
        """Valida si el elemento ya existe en la base de datos.
            Además, revisa que no esté asignado el id."""

        # cuando indice es None, se usa la funcion para crear un nuevo elemento
        # se chequea dentro de la base de datos de personas que el id esté asignado a una persona
        if index is None:
            if (self.database == element).all(axis=1).any():
                print("El elemento ya está presente en la base de datos.")
                return True

            if (self.database['id'] == element['id']).any():
                print("El id ya está asignado en la base de datos.")
                return True

            if not (self.persona.database['id'] == element['id']).any():
                print("El id no está asignado a ninguna persona.")
                return True

            return False
        # cuando indice no es None, se usa la funcion para actualizar un elemento y que no quede repetido
        # se chequea dentro de la base de datos de personas que el id esté asignado a una persona
        else:
            if (self.database[self.database.index != index] == element).all(axis=1).any():
                print("El elemento ya está presente en la base de datos.")
                return True
            if (self.database[self.database.index != index]['id'] == element['id']).any():
                print("El id ya está asignado en la base de datos.")
                return True
            if not (self.persona.database['id'] == element['id']).any():
                print("El id no está asignado a ninguna persona.")
                return True
            return False
