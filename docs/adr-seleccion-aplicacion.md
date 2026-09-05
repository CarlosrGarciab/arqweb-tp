# ADR-001: Seleccion de aplicacion, modo de red y servidor web

## Contexto
El TP Integrador de ARQWEB exige desplegar una aplicación web de código abierto
en una VM, publicarla vía HTTP/HTTPS y demostrar comprensión de su arquitectura.

## Decisión
Se selecciona BookStack (PHP 8.2+/Laravel, MySQL/MariaDB) publicado detrás de
Nginx como proxy inverso, sobre una VM Ubuntu en Proxmox con red en modo puente
(bridge), obteniendo IP por DHCP en el mismo segmento que el anfitrión.

## Alternativas consideradas
- Redmine (Ruby on Rails): descartado por mayor complejidad de despliegue inicial
  (gemas, Bundler, mayor superficie de dependencias).
- Wiki.js (Node.js): candidato viable, descartado por preferencia del equipo por
  una pila PHP/MySQL más familiar y con documentación de instalación más simple.

## Justificación
BookStack tiene arquitectura en capas bien definida, instalación reproducible
vía composer/git, mantenimiento activo y se adapta naturalmente a Nginx +
PHP-FPM + MySQL, cubriendo los objetivos de la Unidad I y II del TP.

## Consecuencias
- Se requiere PHP-FPM como intermediario entre Nginx y la aplicación (FastCGI).
- MySQL corre localmente en la VM, sin exponerse a la red (solo 127.0.0.1:3306).
- El modo de red puente permite acceso directo desde el anfitrión sin NAT
  adicional, simplificando las pruebas de conectividad del Hito 1.