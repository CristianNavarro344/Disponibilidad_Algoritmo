Para trabajar de manera local inserté los csv directamente en una base de datos. Dado que hubo que dockenizar la aplicación, implemente un contenedor con la bb.dd y le inserté la información base (los .csv) con un .sql que generé. (esto se haará de manera automatica al ejecutar los contenedores)

Para ejecutar los contenedores usar:

docker-compose up --build

Una vez levantados los contenedores, se verá en la consola el siguiente mensaje: "disponibilidad_algoritmo-fastapi-app-1  | INFO: Application startup complete." Ahora podemos entrar en el navegador a: 

http://127.0.0.1:8000/docs

Serán visibles las siguientes rutas:
    get_data_from_db
    disponibility

Al ingresar a 'get_data_from_db' retornará la información contenida en las tablas de forecast y shifts.
Al ingresar a 'disponibility' retornará "Inserted" indicando que se agregó el dataframe generado por el algoritmo en la tabla 'availability' de nuestra BB.DD.

Para verificar que se insertó correctamente la información, basta con abrir otra CLI e ingresar al contenedor de la BB.DD con el siguiente comando:

docker exec -it disponibilidad_algoritmo-mysql-db-1 mysql -uroot -p

Estó pedira una contraseña para ingresar, la cual es:

root

Luego nos encontraremos en la CLI de mysql, para acceder a la base de datos y visualizar la información insertada, ejecutar los siguientes comandos:

use scm;
select * from availability;

Aquí podremos comprobar que la información se cargó correctamente en la BB.DD.