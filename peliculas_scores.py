from datetime import datetime
import typing
from pathlib import Path
from typing import Union
import pandas as pd
from faker import Faker
fake = Faker()


def generate_movie() -> dict:
    generos = ['Action', 'Adventure', 'Animation', "Children's",
               'Comedy', 'Crime', 'Documentary', 'Drama',
               'Fantasy', 'Film-Noir', 'Horror', 'Musical',
               'Mystery', 'Romance', 'Sci-Fi', 'Thriller',
               'War', 'Western', 'unknown']
    return {
        'name': ' '.join(fake.words()),
        'release_date': fake.date_time().strftime('%Y-%m-%d'),
        'url': fake.url(),
        'genero': [fake.random_element(elements=generos), fake.random_element(elements=generos)]
    }


def generate_score() -> dict:
    return {'user_id': fake.random_int(min=1, max=1200),
            'movie_id': fake.random_int(min=1, max=2000),
            'rating': fake.random_int(min=1, max=5),
            'date': fake.date_time().strftime('%Y-%m-%d %H:%M:%S')
            }


def generate_person() -> dict:

    return {
        'id': fake.random_int(min=800, max=2000),
        'full_name': fake.name(),
        'year_of_birth': int(fake.year()),
        'gender': fake.random_element(elements=('M', 'F')),
        'zip_code': fake.zipcode()
    }


def generate_user() -> dict:
    return {'id': fake.random_int(min=800, max=2000),
            'occupation': fake.job(),
            'active_since': fake.date_time().strftime('%Y-%m-%d %H:%M:%S')
            }


def generate_worker() -> dict:
    return {'id': fake.random_int(min=800, max=2000),
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
    _validate_constraints = {
        'dir_personas': Union[Path, str, None],
        'dir_usuarios': Union[Path, str, None],
        'dir_trabajadores': Union[Path, str, None],
        'dir_peliculas': Union[Path, str, None],
        'dir_scores': Union[Path, str, None]
    }

    personas = None
    usuarios = None
    trabajadores = None
    peliculas = None
    scores = None

    @validate_params(_validate_constraints)
    def __init__(self, dir_personas=None, dir_usuarios=None, dir_trabajadores=None,
                 dir_peliculas=None, dir_scores=None) -> None:
        DataBase.dir_personas = dir_personas
        DataBase.dir_usuarios = dir_usuarios
        DataBase.dir_trabajadores = dir_trabajadores
        DataBase.dir_peliculas = dir_peliculas
        DataBase.dir_scores = dir_scores
        self.load_data()

    @classmethod
    def load_data(self) -> None:
        """Carge las bases de datos desde el archivo indicado
        """
        try:
            if self.personas is None and self.dir_personas is not None:
                self.personas = pd.read_csv(self.dir_personas)

            if self.usuarios is None and self.dir_usuarios is not None:
                self.usuarios = pd.read_csv(self.dir_usuarios)

            if self.trabajadores is None and self.dir_trabajadores is not None:
                self.trabajadores = pd.read_csv(self.dir_trabajadores)

            if self.peliculas is None and self.dir_peliculas is not None:
                self.peliculas = pd.read_csv(self.dir_peliculas)

            if self.scores is None and self.dir_scores is not None:
                self.scores = pd.read_csv(self.dir_scores)

            # se chequea la consistencia de los datos cargados
            if self.scores is not None and self.peliculas is not None and \
                    self.trabajadores is not None and self.usuarios is not None and \
                    self.personas is not None:
                self.check_data()

        except FileNotFoundError as e:
            print(f"No se pudo encontrar el archivo de base de datos: {e}")
        except Exception as e:
            print(f"Ocurrió un error al leer la base de datos: {e}")
        return

    @classmethod
    def check_data(self) -> None:
        """Verifique que las bases de datos no estén vacías.
            Verifica que no esté duplicada una fila en cada base de datos
        """
        if self.personas.empty:
            print("La base de datos de personas está vacía.")
        if self.usuarios.empty:
            print("La base de datos de usuarios está vacía.")
        if self.trabajadores.empty:
            print("La base de datos de trabajadores está vacía.")
        if self.peliculas.empty:
            print("La base de datos de peliculas está vacía.")
        if self.scores.empty:
            print("La base de datos de scores está vacía.")

        # se eliminan las filas duplicadas de las bases de datos
        self.personas.drop_duplicates(inplace=True)
        self.usuarios.drop_duplicates(inplace=True)
        self.trabajadores.drop_duplicates(inplace=True)
        self.peliculas.drop_duplicates(inplace=True)
        self.scores.drop_duplicates(inplace=True)

        # se eliminan los id que esten duplicados en las bases de datos
        self.personas.drop_duplicates(subset=['id'], inplace=True)
        self.usuarios.drop_duplicates(subset=['id'], inplace=True)
        self.trabajadores.drop_duplicates(subset=['id'], inplace=True)

        # se filtran los datos por id en la base de datos de personas
        self.usuarios = self.usuarios[self.usuarios['id'].isin(
            self.personas.id)]
        self.trabajadores = self.trabajadores[self.trabajadores['id'].isin(
            self.personas.id)]
        self.scores = self.scores[self.scores['user_id'].isin(
            self.usuarios.id)]
        self.scores = self.scores[self.scores['movie_id'].isin(
            self.peliculas.id)]

        # reindex de las bases de datos
        self.personas.reset_index(drop=True, inplace=True)
        self.usuarios.reset_index(drop=True, inplace=True)
        self.trabajadores.reset_index(drop=True, inplace=True)
        self.peliculas.reset_index(drop=True, inplace=True)
        self.scores.reset_index(drop=True, inplace=True)
        return

    @classmethod
    def save_data(self) -> None:
        "Guarda las bases de datos"

        try:
            if self.personas is not None:
                self.personas.to_csv(self.dir_personas)

            if self.usuarios is not None:
                self.usuarios.to_csv(self.dir_usuarios)

            if self.trabajadores is not None:
                self.trabajadores.to_csv(self.dir_trabajadores)

            if self.peliculas is not None:
                self.peliculas.to_csv(self.dir_peliculas)

            if self.scores is not None:
                self.scores.to_csv(self.dir_scores)

        except Exception as e:
            print(f"Ocurrió un error al guardar la base de datos: {e}")
        return

    @classmethod
    def _check_inicializacion_database(self) -> None:
        """ Verifica que las bases de datos necesarias esten inicializadas"""
        if self.personas is None or self.peliculas is None or self.scores is None or \
                self.usuarios is None or self.trabajadores is None:
            print(
                "Debe inicializar las bases: personas, peliculas, usurios, trabajadores y scores.")
            raise ValueError


class Peliculas(DataBase):
    _validate_constraints = {
        'name': Union[str, None],
        'release_date': Union[str, datetime, None],
        'url': Union[str, None],
        'genero': Union[str, list, None]
    }

    db = DataBase()

    @validate_params(_validate_constraints)
    def __init__(self, name=None, release_date=None, url=None, genero=None) -> None:
        self._check_inicializacion_database()
        self.name = name
        self.url = url
        self.genero = genero
        self.release_date = release_date
        self._check_parametros()

    def _check_parametros(self) -> None:
        """Verifica que los parametros ingresados sean correctos"""

        # control de calidad de fecha de lanzamiento
        if isinstance(self.release_date, str):
            try:
                datetime.strptime(self.release_date, '%Y-%m-%d')
            except ValueError:
                print("El formato de la fecha debe ser YYYY-MM-DD.")
                raise ValueError
        elif isinstance(self.release_date, datetime):
            try:
                self.release_date = datetime.strftime(
                    self.release_date, '%Y-%m-%d')
            except ValueError:
                print("El formato de la fecha debe ser YYYY-MM-DD.")
                raise ValueError

        # control de calidad de genero
        if isinstance(self.genero, str):
            if self.genero not in self.db.peliculas.columns[4:]:
                print(f"No se encuentra registrado el genero {self.genero}.")
                print(
                    'En caso de no conocer el genero de la pelicula debe indicarlo como "unknown".')
                raise ValueError
            self.genero = [self.genero]

        if isinstance(self.genero, list):
            for gen in self.genero:
                if gen not in self.db.peliculas.columns[4:]:
                    print(f"No se encuentra registrado el genero {gen}.")
                    print(
                        'En caso de no conocer el genero de la pelicula debe indicarlo como "unknown".')
                    raise ValueError

    def __repr__(self) -> str:
        """ Representación de la clase """
        if isinstance(self.genero, list):
            return f'Pelicula "{self.name}", del genero "{" - " .join(self.genero) }" lanzada el "{self.release_date}".'
        return f'Pelicula "{self.name}", del genero "{self.genero }" lanzada el "{self.release_date}".'

    def eliminar_pelicula(self, name_pelicula: str = None, id_pelicula: int = None) -> None:
        """ Elimina una pelicula de la base de datos.

        Parameters
        ----------
        name_pelicula : str, optional
            Nombre de la pelicula a eliminar, by default None
        id_pelicula : int, optional
            Id de la pelicula a eliminar, by default None

        Raises
        ------
        ValueError
            Si no se ingresa el id o el nombre de la pelicula a eliminar
        """

        if id_pelicula is None and name_pelicula is None:
            print("Debe ingresar el id o el nombre de la pelicula a eliminar.")
            raise ValueError

        if id_pelicula is not None and name_pelicula is not None:
            print(
                f"Se eliminará la pelicula {name_pelicula}. Se ignorará el id.")

        if name_pelicula is not None:
            if name_pelicula not in self.db.peliculas['Name'].values:
                print(
                    f"La pelicula {name_pelicula} no se encuentra registrada.")
            else:
                id_pelicula = self.db.peliculas[self.db.peliculas['Name']
                                                == name_pelicula].id.values[0]
                self.db.scores.drop(
                    self.db.scores[self.db.scores['movie_id'] == id_pelicula].index, inplace=True)
                self.db.scores.reset_index(drop=True, inplace=True)
                self.db.peliculas.drop(
                    self.db.peliculas[self.db.peliculas['Name'] == name_pelicula].index, inplace=True)
                self.db.peliculas.reset_index(drop=True, inplace=True)
                print(f"Se eliminó la pelicula {name_pelicula}.")

        elif id_pelicula is not None and name_pelicula is None:
            if id_pelicula not in self.db.peliculas.id.values:
                print(f"El id {id_pelicula} no se encuentra registrado.")
            else:
                self.db.scores.drop(
                    self.db.scores[self.db.scores['movie_id'] == id_pelicula].index, inplace=True)
                self.db.scores.reset_index(drop=True, inplace=True)
                self.db.peliculas.drop(
                    self.db.peliculas[self.db.peliculas.id == id_pelicula].index, inplace=True)
                self.db.peliculas.reset_index(drop=True, inplace=True)
                print(f"Se eliminó la pelicula con id {id_pelicula}.")

        return

    def _to_dict(self):
        """ Convierte la clase en un diccionario para ser ingresado a la base de datos"""

        dict_aux = {
            'Name': self.name,
            'Release Date': self.release_date,
            'IMDB URL': self.url
        }
        for genero in self.db.peliculas.columns[4:]:
            if genero in self.genero:
                dict_aux[genero] = 1
            else:
                dict_aux[genero] = 0

        return dict_aux

    @classmethod
    def _from_dict(cls, data: dict):
        """ Crea una instancia de la clase a partir de un diccionario"""
        return cls(
            name=data['Name'],
            release_date=data['Release Date'],
            url=data['IMDB URL'],
            genero=[genero for genero in data.keys() if genero not in [
                'Name', 'Release Date', 'IMDB URL', 'id'] and data[genero] == 1]
        )

    def to_database(self) -> None:
        """ Ingresa una pelicula a la base de datos"""

        # se chequea que se hayan ingresado todos los parametros
        if self.name is None or self.url is None or self.genero is None or self.release_date is None:
            print("Debe ingresar todos los parametros de una pelicula.")
            raise ValueError

        # se chequea que la pelicula no se encuentre ya en la base de datos
        if self.name in self.db.peliculas['Name'].values:
            print(f"La pelicula {self.name} ya se encuentra registrada.")
            return

        # se formatea la pelicula para ingresarla a la base de datos
        elemento = self._to_dict()
        elemento['id'] = self.db.peliculas.id.max() + 1

        # se ingresa la pelicula a la base de datos
        self.db.peliculas.loc[self.db.peliculas.shape[0]] = elemento
        return

    def nueva_pelicula_to_database(self, name: str, release_date: str, url: str, genero: Union[list, str]) -> None:
        """Funcion que crea una nueva instancia de la clase Pelicula y la ingresa a la base de datos.   

        Args:
            name (str): Nombre de la pelicula.
            release_date (str): Fecha de lanzamiento de la pelicula.
            url (str, optional): URL de IMDB de la pelicula. 
            genero (list, str): Lista de generos de la pelicula. 

        """

        self.__init__(name, release_date, url, genero)
        self.to_database()
        return

    def get_pelicula(self, name_pelicula: str = None, id_pelicula: int = None):
        """Funcion que retorna una instancia de la clase Pelicula de la base de datos.
            _Si se pasa name_pelicula, se retorna la pelicula con ese nombre.
            _Si se pasa id_pelicula, se retorna la pelicula con ese id.
            _Si se pasa name_pelicula e id_pelicula, se desetima el id_pelicula y se retorna 
            la pelicula buscando por el nombre.

        Args:
            name_pelicula (str, optional): Nombre de la pelicula buscada. Defaults to None.
            id_pelicula (int, optional): ID de la pelicula buscada . Defaults to None.

        Returns:
           Pelicula: Elemento de la clase Pelicula con los datos de la pelicula buscada.
        """

        assert (id_pelicula is None or type(id_pelicula)
                == int), "El id debe ser un entero o None."
        assert (name_pelicula is None or type(name_pelicula)
                == str), "El nombre debe ser un string o None."

        if id_pelicula is None and name_pelicula is None:
            return self._from_dict(self.db.peliculas.iloc[-1].to_dict())

        if name_pelicula is not None:
            if name_pelicula not in self.db.peliculas['Name'].values:
                print(
                    f"La pelicula {name_pelicula} no se encuentra registrada.")
                return
            return self._from_dict(self.db.peliculas[self.db.peliculas['Name'] == name_pelicula].iloc[0].to_dict())

        if id_pelicula is not None and name_pelicula is None:
            if id_pelicula not in self.db.peliculas['id'].values:
                print(
                    f"La pelicula con id {id_pelicula} no se encuentra registrada.")
                return
            return self._from_dict(self.db.peliculas[self.db.peliculas['id'] == id_pelicula].iloc[0].to_dict())


class Scores(DataBase):
    _validate_constraints = {
        'user_id': Union[int, None],
        'movie_id': Union[int, None],
        'rating': Union[int, None],
        'date': Union[str, datetime, None]
    }

    db = DataBase()

    @validate_params(_validate_constraints)
    def __init__(self, user_id=None, movie_id=None, rating=None, date=None) -> None:
        self._check_inicializacion_database()
        self.user_id = user_id
        self.movie_id = movie_id
        self.rating = rating
        self.date = date
        self._check_parametros()

    def _check_parametros(self) -> None:
        """Verifica que los parametros ingresados sean correctos"""

        # control de calidad de fecha de reseña
        if isinstance(self.date, str):
            try:
                datetime.strptime(self.date, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                print("El formato de la fecha debe ser YYYY-MM-DD HH:MM:SS.")
                raise ValueError
        elif isinstance(self.date, datetime):
            try:
                self.date = datetime.strftime(
                    self.date, '%Y-%m-%d')
            except ValueError:
                print("El formato de la fecha debe ser YYYY-MM-DD HH:MM:SS.")
                raise ValueError

        # control de calidad de rating
        if isinstance(self.rating, int):
            if self.rating < 0 or self.rating > 5:
                print("El rating debe ser un numero entre 0 y 5.")
                raise ValueError

        # control de calidad de user_id
        if isinstance(self.user_id, int):
            if self.user_id not in self.db.personas['id'].values:
                print(f"El usuario {self.user_id} no se encuentra registrado.")
                print(
                    "Para registrar un nuevo usuario debe completar la base de datos de Personas.")
                raise ValueError

        # control de calidad de movie_id
        if isinstance(self.movie_id, int):
            if self.movie_id not in self.db.peliculas['id'].values:
                print(
                    f"La pelicula {self.movie_id} no se encuentra registrada.")
                print(
                    "Para registrar una nueva pelicula debe completar la base de datos de Peliculas.")
                raise ValueError
        return

    def __repr__(self) -> str:
        """ Representación de la clase """
        return f'Reseña de la pelicula {self.movie_id} por el usuario {self.user_id} con un rating de {self.rating} y fecha {self.date}.'

    def eliminar_score(self, user_id: int = None, movie_id: int = None, index: int = None) -> None:
        """ Elimina un score de una pelicula de la base de datos.
            Se debe ingresar el index de la base de datos o el user_id y el movie_id.
            Si se ingresan los 3 se eliminará por index, desestimando el user_id y el movie_id.

        Args:
            user_id (int, optional): ID del usuario que realizó la reseña. Defaults to None.
            movie_id (int, optional): ID de la pelicula reseñada. Defaults to None.
            index (int, optional): Indice de la reseña en la base de datos. Defaults to None.

        Raises:
            ValueError: Se debe ingresar el user_id y el movie_id o el index del score a eliminar.
            ValueError: El user_id debe ser un entero mayor a cero o None.
            ValueError: El movie_id debe ser un entero mayor a cero o None.
            ValueError: El index debe ser un entero mayor a cero o None.

        """

        # control de los datos ingresados
        assert (user_id is None or type(user_id) ==
                int), "El user_id debe ser un entero mayor a cero o None."
        assert (movie_id is None or type(movie_id) ==
                int), "El movie_id debe ser un entero mayor a cero o None."
        assert (index is None or type(index) ==
                int), "El index debe ser un entero mayor a cero o None."

        if isinstance(user_id, int):
            if user_id < 0:
                print("El user_id debe ser un entero mayor a cero o None.")
                raise ValueError

        if isinstance(movie_id, int):
            if movie_id < 0:
                print("El movie_id debe ser un entero mayor a cero o None.")
                raise ValueError

        if isinstance(index, int):
            if index < 0:
                print("El index debe ser un entero mayor a cero o None.")
                raise ValueError

        # datos en calidad -> eliminar
        if index is None:
            if user_id is None and movie_id is None:
                print("Debe ingresar el user_id y el movie_id del score a eliminar.")
                raise ValueError

            # está la reseña en la base de datos
            if self.db.scores[(self.db.scores['user_id'] == user_id) & (self.db.scores['movie_id'] == movie_id)].empty:
                print(
                    f"El score de la pelicula {movie_id} por el usuario {user_id} no se encuentra en la base de datos.")
                return

            # elimino la reseña
            self.db.scores.drop(self.db.scores[(self.db.scores['user_id'] == user_id) &
                                               (self.db.scores['movie_id'] == movie_id)].index,
                                inplace=True)

        else:
            if index not in self.db.scores.index:
                print(
                    f"El score con index {index} no se encuentra en la base de datos.")
                return
            self.db.scores.drop(index, inplace=True)
        return

    def _to_dict(self):
        """ Convierte la clase en un diccionario para ser ingresado a la base de datos"""
        return {
            'user_id': self.user_id,
            'movie_id': self.movie_id,
            'rating': self.rating,
            'Date': self.date
        }

    @classmethod
    def _from_dict(cls, data: dict):
        """ Crea una instancia de la clase a partir de un diccionario"""
        return cls(
            user_id=data['user_id'],
            movie_id=data['movie_id'],
            rating=data['rating'],
            date=data['Date'])

    def to_database(self) -> None:
        """ Ingresa el scoring a la base de datos"""

        # se chequea que se hayan ingresado todos los parametros
        if self.user_id is None or self.movie_id is None or self.rating is None or self.date is None:
            print("Debe ingresar todos los parametros de un scoring.")
            raise ValueError

        # se chequea que

        # se formatea el scoring para ingresarla a la base de datos
        elemento = self._to_dict()

        # se ingresa el scoring a la base de datos
        self.db.scores.loc[self.db.scores.shape[0]] = elemento
        return

    def nueva_scoring_to_database(self, user_id: int, movie_id: int, rating: int, date: Union[str, datetime]) -> None:
        """Funcion que crea una nueva instancia de la clase Scoring y la ingresa a la base de datos.

        Args:
            user_id (int): ID del usuario que realizó la reseña.
            movie_id (int): ID de la pelicula reseñada.
            rating (int): Rating de la pelicula.
            date (Union[str, datetime]): Fecha de la reseña.


        Raises:
            ValueError: El user_id debe ser un entero mayor a cero.
            ValueError: El movie_id debe ser un entero mayor a cero.
            ValueError: El rating debe ser un entero entre 0 y 5.
            ValueError: La fecha debe ser un string o un datetime.

        """
        self.__init__(user_id, movie_id, rating, date)
        self.to_database()
        return

    def get_scoring(self, user_id: int = None, movie_id: int = None, index: int = None):
        """ Obtiene un score de una pelicula de la base de datos.
            Se debe ingresar el index de la base de datos o el user_id y el movie_id.
            Si se ingresan los 3 se obtendrá por index, desestimando el user_id y el movie_id.

        Args:
            user_id (int, optional): ID del usuario que realizó la reseña. Defaults to None.
            movie_id (int, optional): ID de la pelicula reseñada. Defaults to None.
            index (int, optional): Indice de la reseña en la base de datos. Defaults to None.

        Raises:
            ValueError: Se debe ingresar el user_id y el movie_id o el index del score a eliminar.
            ValueError: El user_id debe ser un entero mayor a cero o None.
            ValueError: El movie_id debe ser un entero mayor a cero o None.
            ValueError: El index debe ser un entero mayor a cero o None.

        """

        # control de los datos ingresados
        assert (user_id is None or type(user_id) ==
                int), "El user_id debe ser un entero mayor a cero o None."
        assert (movie_id is None or type(movie_id) ==
                int), "El movie_id debe ser un entero mayor a cero o None."
        assert (index is None or type(index) ==
                int), "El index debe ser un entero mayor a cero o None."

        if isinstance(user_id, int):
            if user_id < 0:
                print("El user_id debe ser un entero mayor a cero o None.")
                raise ValueError

        if isinstance(movie_id, int):
            if movie_id < 0:
                print("El movie_id debe ser un entero mayor a cero o None.")
                raise ValueError

        if isinstance(index, int):
            if index < 0:
                print("El index debe ser un entero mayor a cero o None.")
                raise ValueError

        # datos en calidad -> se obtiene el score
        if index is None:
            if user_id is None and movie_id is None:
                print("Debe ingresar el user_id y el movie_id del score a selecionar.")
                raise ValueError

            # está la reseña en la base de datos
            if self.db.scores[(self.db.scores['user_id'] == user_id) & (self.db.scores['movie_id'] == movie_id)].empty:
                print(
                    f"El score de la pelicula {movie_id} por el usuario {user_id} no se encuentra en la base de datos.")
                return

            # devuelvo el scoring
            return self._from_dict(self.db.scores[(self.db.scores['user_id'] == user_id) &
                                                  (self.db.scores['movie_id'] == movie_id)].iloc[0].to_dict())
        else:
            if index not in self.db.scores.index:
                print(
                    f"El score con index {index} no se encuentra en la base de datos.")
                return
            return self._from_dict(self.db.scores.loc[index].to_dict())
