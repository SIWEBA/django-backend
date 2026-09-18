CREATE OR REPLACE TABLE `Roles_Sistema` (
	`id` INTEGER NOT NULL AUTO_INCREMENT,
	`nombre` VARCHAR(50) NOT NULL,
	PRIMARY KEY(`id`)
);

CREATE OR REPLACE TABLE `Lecturas` (
	`id` BIGINT NOT NULL AUTO_INCREMENT,
	`estacion_id` INTEGER NOT NULL,
	`fecha_hora` DATETIME NOT NULL,
	`out_temp` DECIMAL(5,2),
	`hi_temp` DECIMAL(5,2),
	`low_temp` DECIMAL(5,2),
	`out_hum` DECIMAL(5,2),
	`wind_speed` DECIMAL(5,2),
	`wind_dir` SMALLINT,
	`wind_run` DECIMAL(5,2),
	`hi_speed` DECIMAL(5,2),
	`hi_dir` SMALLINT,
	`rain` DECIMAL(5,2),
	`rain_rate` DECIMAL(5,2),
	`solar_rad` DECIMAL(6,2),
	`solar_energy` DECIMAL(6,2),
	`hi_solar_rad` DECIMAL(6,2),
	`uv_index` DECIMAL(5,2),
	`uv_dose` DECIMAL(5,2),
	`hi_uv` DECIMAL(5,2),
	`bar` DECIMAL(6,2),
	`dew_pt` DECIMAL(5,2),
	`wind_chill` DECIMAL(5,2),
	`heat_index` DECIMAL(5,2),
	`thw_index` DECIMAL(5,2),
	`thsw_index` DECIMAL(5,2),
	`et` DECIMAL(5,2),
	`in_temp` DECIMAL(5,2),
	`in_hum` DECIMAL(5,2),
	`iss_recept` DECIMAL(5,2),
	`arc_int` INTEGER,
	PRIMARY KEY(`id`)
);

CREATE UNIQUE INDEX `idx_estacion_fecha`
ON `Lecturas` (`estacion_id`, `fecha_hora`);
CREATE OR REPLACE TABLE `Usuarios_Estaciones` (
	`id` INTEGER NOT NULL AUTO_INCREMENT,
	`usuario_id` INTEGER NOT NULL,
	`estacion_id` INTEGER NOT NULL,
	`rol_estacion_id` INTEGER NOT NULL,
	`estado` VARCHAR(20) NOT NULL DEFAULT 'activo',
	`fecha_asignacion` DATETIME NOT NULL,
	PRIMARY KEY(`id`)
);

CREATE OR REPLACE TABLE `Estaciones` (
	`id` INTEGER NOT NULL AUTO_INCREMENT,
	`nombre` VARCHAR(100) NOT NULL,
	`ubicacion` VARCHAR(255),
	`latitud` DECIMAL(10,8),
	`longitud` DECIMAL(11,8),
	`modelo` VARCHAR(100),
	`estado` VARCHAR(50) NOT NULL,
	`ultima_conexion` DATETIME,
	`fecha_creacion` DATETIME NOT NULL,
	PRIMARY KEY(`id`)
);

CREATE OR REPLACE TABLE `Usuarios` (
	`id` INTEGER NOT NULL AUTO_INCREMENT,
	`rol_sistema_id` INTEGER NOT NULL,
	`nombre` VARCHAR(100) NOT NULL,
	`correo` VARCHAR(100) NOT NULL UNIQUE,
	`contrasena` VARCHAR(255) NOT NULL,
	`fecha_registro` DATETIME NOT NULL,
	PRIMARY KEY(`id`)
);

CREATE OR REPLACE TABLE `Roles_Estacion` (
	`id` INTEGER NOT NULL AUTO_INCREMENT,
	`nombre` VARCHAR(50) NOT NULL,
	PRIMARY KEY(`id`)
);

CREATE OR REPLACE TABLE `Telemetria_Dispositivo` (
	`id` BIGINT NOT NULL AUTO_INCREMENT,
	`estacion_id` INTEGER NOT NULL,
	`fecha_hora` DATETIME NOT NULL,
	`bateria_porcentaje` DECIMAL(5,2),
	`bateria_voltaje` DECIMAL(4,2),
	`panel_solar_voltaje` DECIMAL(4,2),
	`senal_rssi` INTEGER,
	PRIMARY KEY(`id`)
);

CREATE OR REPLACE TABLE `Api_Keys` (
	`id` INTEGER NOT NULL AUTO_INCREMENT,
	`estacion_id` INTEGER NOT NULL UNIQUE,
	`creado_por_usuario_id` INTEGER NOT NULL,
	`llave_hash` VARCHAR(255) NOT NULL,
	`prefijo_visible` VARCHAR(12) NOT NULL,
	`activa` BOOLEAN NOT NULL DEFAULT true,
	`fecha_creacion` DATETIME NOT NULL,
	`fecha_ultimo_uso` DATETIME,
	`fecha_expiracion` DATETIME,
	PRIMARY KEY(`id`)
);

ALTER TABLE `Usuarios`
ADD FOREIGN KEY(`rol_sistema_id`) REFERENCES `Roles_Sistema`(`id`)
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE `Usuarios_Estaciones`
ADD FOREIGN KEY(`usuario_id`) REFERENCES `Usuarios`(`id`)
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE `Usuarios_Estaciones`
ADD FOREIGN KEY(`estacion_id`) REFERENCES `Estaciones`(`id`)
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE `Usuarios_Estaciones`
ADD FOREIGN KEY(`rol_estacion_id`) REFERENCES `Roles_Estacion`(`id`)
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE `Lecturas`
ADD FOREIGN KEY(`estacion_id`) REFERENCES `Estaciones`(`id`)
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE `Api_Keys`
ADD FOREIGN KEY(`estacion_id`) REFERENCES `Estaciones`(`id`)
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE `Api_Keys`
ADD FOREIGN KEY(`creado_por_usuario_id`) REFERENCES `Usuarios`(`id`)
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE `Telemetria_Dispositivo`
ADD FOREIGN KEY(`estacion_id`) REFERENCES `Estaciones`(`id`)
ON UPDATE NO ACTION ON DELETE NO ACTION;
