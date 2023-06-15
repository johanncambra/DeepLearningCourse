import pandas as pd
import individuos as ind



df_personas = pd.read_csv("personas.csv")
df_users = pd.read_csv('usuarios.csv')
df_trabajadores = pd.read_csv('trabajadores.csv')


person = ind.Persona('Federico Hojman',1023,1995,'M')

usuario = ind.Usuario('Ing',person)
trabajador = ind.Trabajador('Ing','A','9-18',person)

person.alta_persona(df_personas)




usuario.alta_usuario(df_personas,df_users)

usuario.baja_persona(df_personas,df_users,df_trabajadores)

#trabajador.alta_trabajador(df_personas,df_trabajadores)



#personas_df.loc[len(personas_df)] = {'id':1+personas_df['id'].max(),'Full Name':'Federico Hojman','Zip Code':1023,'year of birth':1995,'Gender':'M'}
print(df_personas .loc[len(df_personas )-1])
print(df_users.loc[len(df_users)-1])
print(df_trabajadores.loc[len(df_trabajadores)-1])
