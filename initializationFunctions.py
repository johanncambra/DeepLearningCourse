
import pandas as pd
import numpy as np


def load_all(file_personas, file_trabajadores, file_usuarios, file_peliculas, file_scores):

    df_personas = pd.read_csv(file_personas)
    df_usuarios = pd.read_csv(file_usuarios)
    df_trabajadores = pd.read_csv(file_trabajadores)
    df_peliculas = pd.read_csv(file_peliculas)
    df_scores = pd.read_csv(file_scores)

    df_personas.drop_duplicates(inplace=True)
    df_usuarios.drop_duplicates(inplace=True)
    df_trabajadores.drop_duplicates(inplace=True)
    df_peliculas.drop_duplicates(inplace=True)
    #df_scores.drop_duplicates()

    make_consitent(df_personas,df_trabajadores,'id')
    make_consitent(df_personas,df_usuarios,'id')
    #primero limpio a los usuarios que no son personas
    #despues limpio a los scores sin usuario
    make_consitent(df_usuarios,df_scores,'user_id')
    make_consitent(df_peliculas,df_scores,'movie_id')




    


    return df_personas, df_trabajadores, df_usuarios, df_peliculas, df_scores


def  make_consitent(primary_df,secondary_df,column_name):
     #Las entradas en primary deben estar en secondary. no necesariamente al revés



   # print(np.count_nonzero(primary_df.id.isin(secondary_df.id).values) == len(secondary_df) )

    mismatch_indices = (np.arange(0,len(secondary_df),1)[~ secondary_df[column_name].isin(primary_df[column_name]).values])
    if len(mismatch_indices) > 0:
        print('Se detectaron incosistencias. Serán elliminadas')
        mismatch_indices = list(mismatch_indices)

    secondary_df.drop(mismatch_indices, inplace = True)

    

 
   







#def save_all(df_personas, df_trabajadores, df_usuarios, df_peliculas, df_scores, file_personas="personas.csv", file_trabajadores="trabajadores.csv", file_usuarios="usuarios.csv", file_peliculas="peliculas.csv", file_scores="scores.csv"):
#Código de Salvado
#return 0 # O -1 si hubo algún error 