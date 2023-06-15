import pandas as pd
from datetime import datetime
import numpy as np

class Persona:

    def __init__(self, nombre_completo, codigo_postal, 
    fecha_nacimiento, genero):

        self.numero_identificacion = [] #assign_ID()#numero_identificacion
        self.nombre_completo = nombre_completo
        self.codigo_postal = codigo_postal
        self.fecha_nacimiento = fecha_nacimiento
        self.genero = genero
        
 
    def alta_persona(self,df_personas):


        is_already = self.check_if_already_exists(df_personas)
        similarities = self.check_similar_entries(df_personas)

        if is_already:
            
            print('Persona ya existe en la base de datos. Operación cancelada')
            return True

        elif   similarities:


            print('\n Se encontraron las siguientes entradas similares en la base de datos de personas \n\n')

            print(df_personas.loc[df_personas['Full Name'] == self.nombre_completo])

            proceed = input('\n Desea dar de alta una nueva persona? (Y/N)\n ')

            if proceed.lower() == 'y':
                self.numero_identificacion = 1+df_personas['id'].max()

                df_personas.loc[len(df_personas)] = {'id':self.numero_identificacion,
                                                'Full Name':self.nombre_completo,
                                                'Zip Code':self.codigo_postal,
                                                'year of birth':self.fecha_nacimiento,
                                                'Gender':self.genero}
                return True
            else:
                nextStep = input('Desea asociar estos datos a un usuario existente?(Y/N)\n')
                if nextStep.lower() == 'y':

                    existing_id = int(input('Ingrese ID deseado  '))
                    self.numero_identificacion = existing_id
            
                    id_row = self.get_row_index_from_condition(df_personas,'id',existing_id)

                    df_personas.loc[id_row] = { 'id':self.numero_identificacion,
                                            'Full Name':self.nombre_completo,
                                            'Zip Code':self.codigo_postal,
                                            'year of birth':self.fecha_nacimiento,
                                            'Gender':self.genero}
                    return True                        
                else:
                    print('Error. Operación cancelada')
                    return False


        elif not is_already and not similarities:

            self.numero_identificacion = 1+df_personas['id'].max()

            df_personas.loc[len(df_personas)] = {'id':self.numero_identificacion,
                                                'Full Name':self.nombre_completo,
                                                'Zip Code':self.codigo_postal,
                                                'year of birth':self.fecha_nacimiento,
                                                'Gender':self.genero}
        else:
            print('Error. Operación cancelada')
            return False
 
    
    

    def check_if_already_exists(self,df):

        if self.numero_identificacion in df['id'].values:
            
            return True
        else:

            return False

    def check_similar_entries(self,df_personas):

        if self.nombre_completo in df_personas['Full Name'].values:

            return True
        else:

            return False


    def get_person_data(self):

        return {'id':self.numero_identificacion ,
                'Full Name':self.nombre_completo, 
                'Zip Code':self.codigo_postal,
                'year of birth': self.fecha_nacimiento,
                'Gender': self.genero}

    def get_row_index_from_condition(self,df,column_name,matching_value):
        
         row_ix = (np.arange(0,len(df),1)[df[column_name].values == matching_value])
         if len(row_ix) > 0:
            row_ix = int(row_ix)
         return row_ix

    def baja_persona(self,df_personas,df_usuarios,df_trabajadores):

        #Toma TODOS los DF para que no quede nada en usuarios o trabajadores sin una persona asignada. Si borro persona, purgo todo

        row_id_personas = self.get_row_index_from_condition(df_personas,'id',self.numero_identificacion)
        row_id_trabajadores = self.get_row_index_from_condition(df_trabajadores,'id',self.numero_identificacion)
        row_id_usuarios = self.get_row_index_from_condition(df_usuarios,'id',self.numero_identificacion)

        df_trabajadores.drop(row_id_trabajadores, inplace=True)
        df_usuarios.drop(row_id_usuarios, inplace=True)
        df_personas.drop(row_id_personas, inplace=True)
    
        


class Trabajador(Persona):

    
    def __init__(self, puesto, categoria, horario_laboral, datos_persona): 

        if type(datos_persona) == Persona:
          
            self.numero_identificacion = datos_persona.numero_identificacion
            self.nombre_completo = datos_persona.nombre_completo
            self.codigo_postal = datos_persona.codigo_postal
            self.fecha_nacimiento = datos_persona.fecha_nacimiento
            self.genero = datos_persona.genero
            self.fecha_alta = []

        elif type(datos_persona) == 'dict':

            #self.numero_identificacion = datos_persona['numero_identificacion']
            self.nombre_completo = datos_persona['nombre_completo']
            self.codigo_postal = datos_persona['codigo_postal']
            self.fecha_nacimiento = datos_persona['fecha_nacimiento'] 
            self.genero = datos_persona['genero']
            self.fecha_alta =  datos_persona['fecha_alta']
        
        #self.fecha_alta =  fecha_alta
        self.puesto = puesto
        self.horario_laboral = horario_laboral
        self.categoria = categoria




        
       
    def alta_trabajador(self,df_personas,df_trabajadores):

        succesful_update = self.alta_persona(df_personas)

        if succesful_update:

            already_exists = self.check_if_already_exists(df_trabajadores)

            if already_exists:
                print('El trabajador ya está dado de alta')
            
            else:

                self.fecha_alta = datetime.now() 

                df_trabajadores.loc[len(df_trabajadores)] = {'id': self.numero_identificacion, 
                                                            'Position' : self.puesto, 
                                                            'Start Date':self.fecha_alta, 
                                                            'Working Hours': self.horario_laboral,
                                                            'Category': self.categoria}
        else: 
            print('No puede darse de alta el trabajador')


    def baja_trabajador(self,df_trabajadores):

        #verifica que no estemos metiendo mano en cualquier lado

        if df_trabajadores.columns[1] == 'Position':

            row_id = self.get_row_index_from_condition(df_trabajadores,'id',self.numero_identificacion)
            #print(row_id)

            df_trabajadores.drop(row_id, inplace=True)
        else: 
            print('DataFrame no compatible')
    


        
   



class Usuario(Persona):
      
    def __init__(self, ocupacion,datos_persona):

        if type(datos_persona) == Persona:

             #self.numero_identificacion = assign_ID(numero_identificacion
            self.numero_identificacion = datos_persona.numero_identificacion
            self.nombre_completo = datos_persona.nombre_completo
            self.codigo_postal = datos_persona.codigo_postal
            self.fecha_nacimiento = datos_persona.fecha_nacimiento
            self.genero = datos_persona.genero
            self.fecha_alta = []# datos_persona.fecha_alta

        elif type(datos_persona) == 'dict':
            
            self.numero_identificacion = datos_persona['numero_identificacion']
            self.nombre_completo = datos_persona['nombre_completo']
            self.codigo_postal = datos_persona['codigo_postal']
            self.fecha_nacimiento = datos_persona['fecha_nacimiento'] 
            self.genero = datos_persona['genero']
            #self.fecha_alta =  datos_persona['fecha_alta']
        else:
            raise ValueError(''' Accepted types for datos_persona are 'dict' and 'Persona' ''')
        
        #self.fecha_alta = #  fecha_alta
        self.ocupacion = ocupacion
        


    def alta_usuario(self,df_personas,df_usuarios):

        succesful_update = self.alta_persona(df_personas)

        if succesful_update:

            already_exists = self.check_if_already_exists(df_usuarios)

            if already_exists:

                print('El usuario ya existe')
            else:

                self.fecha_alta = datetime.now()

                df_usuarios.loc[len(df_usuarios)] = {'id':self.numero_identificacion,
                                                    'Occupation':self.ocupacion,
                                                    'Active Since':self.fecha_alta}
        else: 
            self.baja_persona(df_personas)
            print('No puede darse de alta el trabajador')

    def baja_usuario(self,df_usuarios):

        if df_usuarios.columns[1] == 'Occupation':

            row_id = self.get_row_index_from_condition(df_usuarios,'id',self.numero_identificacion)
            #print(row_id)

            df_usuarios.drop(row_id, inplace=True)
        else: 
            print('DataFrame no compatible')





