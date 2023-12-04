Para trabajar de manera local inserté los csv directamente en una base de datos. Dado que hubo que dockenizar la aplicación, implemente un contenedor con la bb.dd y le inserté la información base (los .csv) con un .sql que generé. (esto se hará de manera automatica al ejecutar los contenedores)

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


Preguntas conceptuales:

    1.-En el caso de 96 datos por día no habria problema ya que el algoritmo actualmente considera que hay 96 datos para cada día, especificamente cuando se realiza:
        periodos = 24
        tiempo = [(timedelta(hours=0, minutes=15*i * 96/periodos)) for i in range(int(periodos))]
        En algún caso diferente por ejemplo si tuvieramos un dato cada 20 minutos, habría que modificar el algoritmo para que sea 72 datos por día
    Habria que revisar el caso real que tenga demanda por dia segmentada por minutos, ya que se podria unificar la información del día y realizar el mismo proceso.

    2.- Si, se podría unificar el código en único microservicio, como ventajas puede traer que el código es más simple de entender, dado que es un único flujo de   lectura de linea tras linea, sin embargo, unir los microservicios puede generar que en una futura actualización, falle la aplicación por completo, por ejemplo:
        En caso que se actualice una libreria o realicen cambios en el algoritmo que genera la disponibilidad, puede provocar algún error en el proceso y que no se genere correctamente, sin embargo con la estructura actual, la ruta 'get_data_from_db' seguiria funcionando y nos permitiria saber que el problema no esta en la bb.dd ni en la comunicación con esta, sinó que en el algoritmo. Si la aplicación estuviera unificada, habria que entrar a debuggear o revisar el código para saber donde esta fallando. Además, una aplicación separaa en microservicios es más escalable para agregar nuevas funcionalidades.

    3.- Para realizar el cálculo con el algoritmo 1000 veces, se podria hacer un ETL que ejecute el proceso en horario no habil para no producir latencia en la bb.dd y que los usuarios de laaplicación no se vean afectados. Además, dependiende de la utilidad o flujo que se requiera, se podría optimizar el código para reutilizar los parámetros por ejemplo y no volver a realizar cálculos de forma innecesaria, optimizando así el tiempo de ejecición del algoritmo..