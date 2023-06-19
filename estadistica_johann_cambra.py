import typing
from pathlib import Path
from typing import Union
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


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


class Estadistica:
    _validate_constraints = {
        'dir_personas': Union[Path, str],
        'dir_usuarios': Union[Path, str],
        'dir_trabajadores': Union[Path, str],
        'dir_peliculas': Union[Path, str],
        'dir_scores': Union[Path, str]
    }

    @validate_params(_validate_constraints)
    def __init__(self, dir_personas=None, dir_usuarios=None, dir_trabajadores=None,
                 dir_peliculas=None, dir_scores=None) -> None:
        self.dir_personas = dir_personas
        self.dir_usuarios = dir_usuarios
        self.dir_trabajadores = dir_trabajadores
        self.dir_peliculas = dir_peliculas
        self.dir_scores = dir_scores
        self.personas = None
        self.usuarios = None
        self.trabajadores = None
        self.peliculas = None
        self.scores = None
        self._load_data()

    def _load_data(self) -> None:
        """Carge las bases de datos desde el archivo indicado
        """
        try:
            self.personas = pd.read_csv(self.dir_personas)
            self.usuarios = pd.read_csv(self.dir_usuarios)
            self.usuarios['Active Since'] = pd.to_datetime(
                self.usuarios['Active Since'])
            self.trabajadores = pd.read_csv(self.dir_trabajadores)
            self.trabajadores['Start Date'] = pd.to_datetime(
                self.trabajadores['Start Date'])
            self.peliculas = pd.read_csv(self.dir_peliculas)
            self.peliculas['Release Date'] = pd.to_datetime(
                self.peliculas['Release Date'])

            self.scores = pd.read_csv(self.dir_scores)
            self.scores['Date'] = pd.to_datetime(self.scores['Date'])

            self._check_data()

        except FileNotFoundError as e:
            print(f"No se pudo encontrar el archivo de base de datos: {e}")
        except Exception as e:
            print(f"Ocurrió un error al leer la base de datos: {e}")
        return

    def _check_data(self) -> None:
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

        # reindex de las bases de datos
        self.personas.reset_index(drop=True, inplace=True)
        self.usuarios.reset_index(drop=True, inplace=True)
        self.trabajadores.reset_index(drop=True, inplace=True)
        self.peliculas.reset_index(drop=True, inplace=True)
        self.scores.reset_index(drop=True, inplace=True)

        return

    def _print_movie(self, movie: pd.DataFrame) -> None:
        """Imprime la información de una película
        """
        generos = movie[movie.columns[4:]].to_dict('records')[0]
        generos = [k for k, v in generos.items() if v == 1]
        print("Nombre: ", movie['Name'].values[0])
        print("Fecha de lanzamiento: ",
              movie['Release Date'].dt.strftime('%d/%m/%Y').values[0])
        print("Generos: ", ' - '.join(generos))
        print("IMDB URL: ", movie['IMDB URL'].values[0])
        return

    def pelicula_mas_vieja(self, genero: str = None) -> None:
        """Imprime la pelicula mas vieja de la base de datos. Se puede especificar el género.

        Args:
            genero (str, optional): genero de la pelicula. Defaults to None.
        """

        if genero is None:
            movie = self.peliculas[self.peliculas['Release Date']
                                   == self.peliculas['Release Date'].min()]
            print("La pelicula más vieja es:")
            self._print_movie(movie)
        else:
            if genero in self.peliculas.columns[4:]:
                movies = self.peliculas[self.peliculas[genero] == 1]
                movie = movies[movies['Release Date']
                               == movies['Release Date'].min()]
                print(f"La pelicula más vieja del genero {genero} es:")
                self._print_movie(movie)
            else:
                print(f"No se encontró el genero {genero}.")

        return

    def pelicula_mas_nueva(self, genero=None) -> None:
        """Imprime la pelicula mas nueva de la base de datos. Se puede especificar el género.

        Args:
            genero (str, optional): genero de la pelicula. Defaults to None.
        """

        if genero is None:
            movie = self.peliculas[self.peliculas['Release Date']
                                   == self.peliculas['Release Date'].max()]
            self._print_movie(movie)

        else:
            if genero in self.peliculas.columns[4:]:
                movies = self.peliculas[self.peliculas[genero] == 1]
                movie = movies[movies['Release Date']
                               == movies['Release Date'].max()]
                self._print_movie(movie)

            else:
                print(f"No se encontró el genero {genero}.")

        return

    def peliculas_totales(self, genero: str = None) -> None:
        """Imprime el numero total de peliculas de la base de datos. Se puede especificar el género.

        Args:
            genero (str, optional): genero de la pelicula. Defaults to None.
        """
        if genero is None:
            print(f"La cantidad de peliculas es {self.peliculas.shape[0]}.")

        else:

            if genero in self.peliculas.columns[4:]:

                print(f"La cantidad de peliculas del genero {genero} son \
{self.peliculas[self.peliculas[genero] == 1].shape[0]}.")
            else:
                print(f"No se encontró el genero {genero}.")
                return

    def peliculas_anuales(self, start_year: int = None, end_year: int = None, genero: Union[list, str] = None) -> None:
        """Imprime el numero de peliculas por año. Se puede especificar el género.

        Args:
            int_year (int, optional): año inicial. Defaults to None.
            end_year (int, optional): año final. Defaults to None.
            genero (Union[list, str], optional): genero de la pelicula. Defaults to None.
        """
        if end_year is None and start_year is None:
            end_year = self.peliculas['Release Date'].max().year

        if start_year is None:
            start_year = self.peliculas['Release Date'].min().year

        if start_year > self.peliculas['Release Date'].max().year:
            print("El año inicial es mayor al año final.")
            return

        if end_year is None:
            end_year = start_year

        if genero is None:
            genero = self.peliculas.columns[4:]
        if isinstance(genero, str):
            if genero in self.peliculas.columns[4:]:
                genero = [genero]
            else:
                print(f"No se encontró el genero {genero}.")
                return
        if isinstance(genero, list):
            for gen in genero:
                if gen not in self.peliculas.columns[4:]:
                    print(f"No se encontró el genero {gen}.")
                    return

        df = self.peliculas[self.peliculas['Release Date'].dt.year.between(
            start_year, end_year)]
        df = df[df[genero].sum(axis=1) > 0]
        df = df.groupby(df['Release Date'].dt.year)[genero].sum()
        df = df.T
        return df

    def usuariosby(self, ocupacion: Union[list, str] = None, year_nacimiento: Union[list, int] = None, genero: Union[list, str] = None) -> None:
        """Imprime el numero de usuarios año de nacimiento, ocupación y genero.

        Args:
            ocupacion (str, optional): ocupación del usuario. Defaults to None.
            year_nacimiento (int, optional): año de nacimiento del usuario. Defaults to None.
            genero (str, optional): genero del usuario. Defaults to None.
        """

        if isinstance(genero, str):
            if genero in ['M', 'F']:
                genero = [genero]
            else:
                print(f"Los generos permitidos son M para masculino y F para femenino.")
                return

        if isinstance(genero, list):
            for gen in genero:
                if gen not in ['M', 'F']:
                    print(
                        f"Los generos permitidos son M para masculino y F para femenino.")
                    return

        if genero is None:
            genero = self.personas['Gender'].unique().tolist()

        if ocupacion is None:
            ocupacion = self.usuarios['Occupation'].unique()

        if isinstance(ocupacion, str):
            if ocupacion in self.usuarios['Occupation'].unique():
                ocupacion = [ocupacion]
            else:
                print(f"No se encontró la ocupación {ocupacion}.")
                return

        if isinstance(ocupacion, list):
            for ocu in ocupacion:
                if ocu not in self.usuarios['Occupation'].unique():
                    print(f"No se encontró la ocupación {ocu}.")
                    return

        if isinstance(year_nacimiento, int):
            if year_nacimiento in self.personas['year of birth'].unique():
                year_nacimiento = [year_nacimiento]
            else:
                print(
                    f"No se encontró el año de nacimiento {year_nacimiento}.")
                return

        if isinstance(year_nacimiento, list):
            for year in year_nacimiento:
                if year not in self.personas['year of birth'].unique():
                    print(f"No se encontró el año de nacimiento {year}.")
                    return

        if year_nacimiento is None:
            year_nacimiento = self.personas['year of birth'].unique().tolist()

        df = self.usuarios[self.usuarios['Occupation'].isin(ocupacion)]
        df = df.merge(self.personas, on='id', how='left')
        df = df[df['year of birth'].isin(year_nacimiento)]
        df = df[df['Gender'].isin(genero)]

        return df.groupby(['year of birth', 'Occupation', 'Gender']).size().reset_index(name='counts')

    def usuarios_totales(self, ocupacion: Union[list, str] = None, year_nacimiento: Union[list, int] = None, genero: Union[list, str] = None) -> None:
        """Imprime el numero de usuarios con año de nacimiento, ocupación y genero especificados.

        Args:
            ocupacion (str, optional): ocupación del usuario. Defaults to None.
            year_nacimiento (int, optional): año de nacimiento del usuario. Defaults to None.
            genero (str, optional): genero del usuario. Defaults to None.
        """

        if isinstance(genero, str):
            if genero in ['M', 'F']:
                genero = [genero]
            else:
                print(f"Los generos permitidos son M para masculino y F para femenino.")
                return

        if isinstance(genero, list):
            for gen in genero:
                if gen not in ['M', 'F']:
                    print(
                        f"Los generos permitidos son M para masculino y F para femenino.")
                    return

        if genero is None:
            genero = self.personas['Gender'].unique().tolist()

        if ocupacion is None:
            ocupacion = self.usuarios['Occupation'].unique()

        if isinstance(ocupacion, str):
            if ocupacion in self.usuarios['Occupation'].unique():
                ocupacion = [ocupacion]
            else:
                print(f"No se encontró la ocupación {ocupacion}.")
                return

        if isinstance(ocupacion, list):
            for ocu in ocupacion:
                if ocu not in self.usuarios['Occupation'].unique():
                    print(f"No se encontró la ocupación {ocu}.")
                    return

        if isinstance(year_nacimiento, int):
            if year_nacimiento in self.personas['year of birth'].unique():
                year_nacimiento = [year_nacimiento]
            else:
                print(
                    f"No se encontró el año de nacimiento {year_nacimiento}.")
                return

        if isinstance(year_nacimiento, list):
            for year in year_nacimiento:
                if year not in self.personas['year of birth'].unique():
                    print(f"No se encontró el año de nacimiento {year}.")
                    return

        if year_nacimiento is None:
            year_nacimiento = self.personas['year of birth'].unique().tolist()

        df = self.usuarios[self.usuarios['Occupation'].isin(ocupacion)]
        df = df.merge(self.personas, on='id', how='left')
        df = df[df['year of birth'].isin(year_nacimiento)]
        df = df[df['Gender'].isin(genero)]

        print(f"El número de usuarios es {df.shape[0]}.")

        return

    def personas_by_date_of_birth(self, start_year: int = None, end_year: int = None, genero: Union[list, str] = None) -> None:
        """Resume la cantidad de personas por año de nacimiento y genero.

        Args:
            start_year (int, optional): inicio de año de nacimiento. Defaults to None.
            end_year (int, optional): fin de año de nacimiento. Defaults to None.
            genero (Union[list, str], optional): genero de la persona. Defaults to None.
        """

        if isinstance(genero, str):
            if genero in ['M', 'F']:
                genero = [genero]
            else:
                print(f"Los generos permitidos son M para masculino y F para femenino.")
                return

        if isinstance(genero, list):
            for gen in genero:
                if gen not in ['M', 'F']:
                    print(
                        f"Los generos permitidos son M para masculino y F para femenino.")
                    return

        assert isinstance(
            start_year, int) or start_year is None, "El año de inicio debe ser un entero."
        assert isinstance(
            end_year, int) or end_year is None, "El año de fin debe ser un entero."

        if isinstance(start_year, int):
            if start_year > self.personas['year of birth'].max():
                print(
                    f"El año de inicio debe ser menor o igual a {self.personas['year of birth'].max()}.")
                return

        if isinstance(end_year, int):
            if end_year < self.personas['year of birth'].min():
                print(
                    f"El año de fin debe ser mayor o igual a {self.personas['year of birth'].min()}.")
                return

        if start_year is None and end_year is None and genero is None:
            print(
                f"La cantidad total de personas es {self.personas.shape[0]}.")

        elif start_year is None and end_year is None:
            for gen in genero:
                print(
                    f"La cantidad total de personas del genero {gen} es {self.personas[self.personas['Gender'] == gen].shape[0]}.")

        elif start_year is None:
            df = self.personas[(self.personas['year of birth'] <= end_year) & (
                self.personas['Gender'].isin(genero))]
            return df.groupby(['year of birth', 'Gender']).size().reset_index(name='counts')

        elif end_year is None:
            df = self.personas[(self.personas['year of birth'] >= start_year) & (
                self.personas['Gender'].isin(genero))]
            return df.groupby(['year of birth', 'Gender']).size().reset_index(name='counts')

        else:
            df = self.personas[(self.personas['year of birth'] >= start_year) & (
                self.personas['Gender'].isin(genero)) & (self.personas['year of birth'] <= end_year)]
            return df.groupby(['year of birth', 'Gender']).size().reset_index(name='counts')

    def trabajadoresby(self, posicion: Union[list, str, bool] = None):
        """Resume la cantidad de trabajadores por posicion.
            _ si posicion es None o False: se imprime el total de trabajadores.
            _ si posicion es True: se imprime el total de trabajadores por posicion.
            _ si posicion es una lista o string: se imprime el total de trabajadores para las 
                posiciones especificadas.

        Args:
            posicion (Union[list, str, bool], optional): posicion de la persona. Defaults to None.
        """

        if isinstance(posicion, str):
            if posicion in self.trabajadores['Position'].unique():
                posicion = [posicion]
            else:
                print(f"No se encontró la posicion {posicion}.")
                return

        if isinstance(posicion, list):
            for pos in posicion:
                if pos not in self.trabajadores['Position'].unique():
                    print(f"No se encontró la posicion {pos}.")
                    return

        if isinstance(posicion, bool):
            if posicion == True:
                posicion = self.trabajadores['Position'].unique().tolist()

        if isinstance(posicion, list):
            df = self.trabajadores[self.trabajadores['Position'].isin(
                posicion)]
            return df.groupby(['Position']).size().reset_index(name='counts')

        else:
            print(
                f"La cantidad total de trabajadores es {self.trabajadores.shape[0]}.")
            return

    def scores_by_movies(self, id_usuario: Union[list, int] = None,
                         year_movie: Union[list, int] = None,
                         genero_movie: Union[list, str] = None):
        """Resume las puntuaciones de las peliculas por usuario, año de estreno y genero.

        Args:
            id_usuario (Union[list, int], optional): id del usuario. Defaults to None.
            year_movie (Union[list, int], optional): año de estreno de la pelicula. Defaults to None.
            genero_movie (Union[list, str], optional): genero de la pelicula. Defaults to None.
        """

        # datos iniciales
        df = self.scores[['user_id', 'movie_id', 'rating']].merge(
            self.peliculas, how='left', left_on='movie_id', right_on='id').sort_values(by='user_id')

        if isinstance(id_usuario, int):
            if id_usuario not in df['user_id'].unique():
                print(
                    f"El usuario con id {id_usuario} no puntuó ninguna pelicula.")
                return
            df = df[df['user_id'].isin([id_usuario])]

        if isinstance(id_usuario, list):
            for user in id_usuario:
                if user not in df['user_id'].unique():
                    print(
                        f"El usuario con id {id_usuario} no puntuó ninguna pelicula.")
                    return
            df = df[df['user_id'].isin(id_usuario)]

        if isinstance(year_movie, int):
            if year_movie not in self.peliculas['Release Date'].dt.year.unique():
                print(f"No hay peliculas lanzadas en el año {year_movie}.")
                return
            df = df[df['Release Date'].dt.year == year_movie]

            if df.shape[0] == 0:
                print(
                    f"No hay peliculas con puntuación lanzados en el año {year_movie} que cumplan las condiciones de busqueda.")
                return

        if isinstance(year_movie, list):
            for year in year_movie:
                if year not in self.peliculas['Release Date'].dt.year.unique():
                    print(f"No hay peliculas lanzadas en el año {year}.")
                    return
            df = df[df['Release Date'].dt.year.isin(year_movie)]

            if df.shape[0] == 0:
                print(
                    f"No hay peliculas con puntuación lanzadas en los años {' - '.join(year_movie)} que cumplan las condiciones de busqueda.")
                return

        if isinstance(genero_movie, str):
            if genero_movie not in self.peliculas.columns[4:]:
                print(f"No se encuentra registrado el genero {genero_movie}.")
                return
            df = df[df[genero_movie] == 1]

            if df.shape[0] == 0:
                print(
                    f"No hay peliculas con puntuación que tengan el genero {genero_movie} que cumplan las condiciones de busqueda.")
                return

        if isinstance(genero_movie, list):
            for gen in genero_movie:
                if gen not in self.peliculas.columns[4:]:
                    print(f"No se encuentra registrado el genero {gen}.")
                    return
            df = df[df[genero_movie].sum(axis=1) > 0]

            if df.shape[0] == 0:
                print(
                    f"No hay peliculas con puntuación de los generos {' - '.join(genero_movie)} que cumplan las condiciones de busqueda.")
                return

        # se realiza promedio de rating por año, genero y usuario
        df = df[['Release Date', 'rating'] + df.columns[7:].to_list()]
        df['Release Date'] = df['Release Date'].dt.year
        df = df[df.columns[df.sum().values > 0]]
        aux_ = pd.DataFrame(index=df['Release Date'].dropna().unique(
        ), columns=df.columns[df.sum().values > 0][2:]).sort_index()
        for genero in aux_.columns:
            x = df[df[genero] == 1][['Release Date', 'rating']
                                    ].groupby('Release Date').mean()
            aux_.loc[x.index, genero] = x['rating'].values

        # se grafica
        fig, ax = plt.subplots(figsize=(20, 10))
        sns.heatmap(aux_.fillna(0), annot=True, fmt='.1f', cmap='Blues', ax=ax)
        ax.set_title('Promedio de rating por año y genero')
        plt.show()

        return

    def scores_by_users(self, genero_usuario: Union[list, str] = None,
                        ocupacion: Union[list, str] = None,
                        start_edad: int = None,
                        end_edad: int = None) -> None:
        """funcion que imprime el promedio de rating por genero, ocupacion y edad

        Args:
            genero_usuario (Union[list, str], optional): Genero del usuario (F, M) . Defaults to None.
            ocupacion (Union[list, str], optional): Ocupación del usuario. Defaults to None.
            start_edad (int, optional): Edad mínima del usuario. Defaults to None.
            end_edad (int, optional): Edad máxima del usuario. Defaults to None.

        """

        # datos iniciales
        df = self.scores[['user_id', 'movie_id', 'rating']].merge(
            self.personas[['id', 'year of birth', 'Gender']], how='left', left_on='user_id', right_on='id').sort_values(by='user_id')

        if isinstance(genero_usuario, str):
            if genero_usuario not in ['M', 'F']:
                print(f"Los generos permitidos son M para masculino y F para femenino.")

            df = df[df['Gender'] == genero_usuario]
            if df.shape[0] == 0:
                print(
                    f"No hay peliculas con puntuación puntuadas por usuarios de genero {genero_usuario} que cumplan las condiciones de busqueda.")
                return

        if isinstance(genero_usuario, list):
            for gen in genero_usuario:
                if gen not in ['M', 'F']:
                    print(
                        f"Los generos permitidos son M para masculino y F para femenino.")
                    return

        if isinstance(ocupacion, str):
            if ocupacion not in self.usuarios['Occupation'].unique():
                print(f"No se encuentra registrada la ocupacion {ocupacion}.")
                return
            id_usuario = self.usuarios[self.usuarios['Occupation']
                                       == ocupacion]['id'].to_list()
            df = df[df['user_id'].isin(id_usuario)]

            if df.shape[0] == 0:
                print(
                    f"No hay puntuaciones de usuarios de ocupacion {ocupacion} que cumplan las condiciones de busqueda.")
                return

        if isinstance(ocupacion, list):
            for ocup in ocupacion:
                if ocup not in self.usuarios['Occupation'].unique():
                    print(f"No se encuentra registrada la ocupacion {ocup}.")
                    return
            id_usuario = self.usuarios[self.usuarios['Occupation'].isin(
                ocupacion)]['id'].to_list()
            df = df[df['user_id'].isin(id_usuario)]

            if df.shape[0] == 0:
                print(
                    f"No hay puntuaciones de usuarios de ocupaciones {' - '.join(ocupacion)} que cumplan las condiciones de busqueda.")
                return

        if isinstance(start_edad, int) and isinstance(end_edad, int):
            if start_edad > end_edad:
                print(f"La edad start_edad no puede ser mayor a end_edad.")
                return

        if isinstance(start_edad, int):
            if start_edad <= 0:
                print(f"La edad start_edad no puede ser negativa o cero.")
                return
            if self.personas[(pd.Timestamp.today().year - self.personas['year of birth']) >= start_edad].shape[0] == 0:
                print(
                    f"No hay personas con edad mayor o igual a {start_edad}.")
                return

            df = df[(pd.Timestamp.today().year -
                     df['year of birth']) >= start_edad]
            if df.shape[0] == 0:
                print(
                    f"No hay puntuaciones de usuarios con edad mayor o igual a {start_edad} que cumplan las condiciones de busqueda.")
                return

        if isinstance(end_edad, int):
            if end_edad <= 0:
                print(f"La edad end_edad no puede ser negativa o cero.")
                return
            if self.personas[(pd.Timestamp.today().year - self.personas['year of birth']) <= end_edad].shape[0] == 0:
                print(f"No hay personas con edad menor o igual a {end_edad}.")
                return

            df = df[(pd.Timestamp.today().year -
                     df['year of birth']) <= end_edad]
            if df.shape[0] == 0:
                print(
                    f"No hay puntuaciones de usuarios con edad menor o igual a {start_edad} que cumplan las condiciones de busqueda.")
                return

        # se imprimen resultados
        print(f"El promedio de puntuaciones es: {df['rating'].mean():.2f}.")
        print(f"Total de puntuaciones: {df.shape[0]}.")
        print(f"Total de usuarios: {df['user_id'].nunique()}.")
        print(f"Total de peliculas puntuadas: {df['movie_id'].nunique()}.")
        if isinstance(genero_usuario, str):
            print(f"Genero de usuarios: {genero_usuario}.")
        if isinstance(genero_usuario, list):
            print(f"Generos de usuarios: {' - '.join(genero_usuario)}.")
        if isinstance(ocupacion, str):
            print(f"Ocupacion de usuarios: {ocupacion}.")
        if isinstance(ocupacion, list):
            print(f"Ocupaciones de usuarios: {' - '.join(ocupacion)}.")
        if isinstance(start_edad, int) and isinstance(end_edad, int):
            print(f"Edad de usuarios: {start_edad} - {end_edad}.")
        elif isinstance(start_edad, int):
            print(f"Edad de usuarios  mayor o igual a {start_edad}.")
        elif isinstance(end_edad, int):
            print(f"Edad de usuarios menor o igual a {end_edad}.")

        return  # df[['user_id', 'rating']].reset_index(drop=True)
