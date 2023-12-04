CREATE DATABASE IF NOT EXISTS scm;
use scm;

CREATE TABLE IF NOT EXISTS scm.forecast (
    fecha VARCHAR(255),
    demanda INT
);

CREATE TABLE IF NOT EXISTS scm.shifts (
    name VARCHAR(50),
    Inicio_Turno TIME,
    Fin_Turno TIME,
    Tipo_Turno VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS scm.availability (

    collaborator VARCHAR(255),
    date DATE,
    availability INT,
    week INT,
    day INT
);

INSERT INTO scm.forecast (fecha,demanda) VALUES
	 ('2023-09-04',6),
	 ('2023-09-05',7),
	 ('2023-09-06',8),
	 ('2023-09-07',7),
	 ('2023-09-08',10),
	 ('2023-09-09',6),
	 ('2023-09-10',6),
	 ('2023-09-11',7),
	 ('2023-09-12',7),
	 ('2023-09-13',6);

INSERT INTO scm.forecast (fecha,demanda) VALUES
	 ('2023-09-14',8),
	 ('2023-09-15',9),
	 ('2023-09-16',6),
	 ('2023-09-17',7),
	 ('2023-09-18',8),
	 ('2023-09-19',9),
	 ('2023-09-20',8),
	 ('2023-09-21',9),
	 ('2023-09-22',9),
	 ('2023-09-23',6);

INSERT INTO scm.forecast (fecha,demanda) VALUES
	 ('2023-09-24',6),
	 ('2023-09-25',8),
	 ('2023-09-26',9),
	 ('2023-09-27',8),
	 ('2023-09-28',9),
	 ('2023-09-29',9),
	 ('2023-09-30',6),
	 ('2023-10-01',7);


INSERT INTO scm.shifts (name,Inicio_Turno,Fin_Turno,Tipo_Turno) VALUES
	 ('madrugada FT','00:00:00','08:00:00','mañana'),
	 ('morning FT','07:00:00','15:00:00','mañana'),
	 ('tarde FT','11:00:00','19:00:00','tarde'),
	 ('cierre FT','16:00:00','00:00:00','noche'),
	 ('noche FT','14:00:00','22:00:00','noche'),
	 ('mañana PT','08:00:00','12:00:00','mañana'),
	 ('tarde 1 PT','12:00:00','16:00:00','tarde'),
	 ('tarde 2 PT','14:00:00','18:00:00','tarde'),
	 ('noche PT','18:00:00','22:00:00','noche');

