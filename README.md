# 💾 Trabajo Practico Obligatorio - Bases de Datos II

## Consigna

1. Obtener los datos de los clientes junto con sus teléfonos: `Show Client Data` en `Clients`.
2. Obtener el/los teléfono/s y el número de cliente del cliente con nombre “Jacob” y apellido “Cooper”: `Show telephone numbers by Name and Last Name` en `Clients`
3. Mostrar cada teléfono junto con los datos del cliente: `Show telephone <> client data` en `Clients`
4. Obtener todos los clientes que tengan registrada al menos una factura: `Show clients with at least one bill` en `Clients`
5. Identificar todos los clientes que no tengan registrada ninguna factura: `Show clients without bills` en `Clients`
6. Devolver todos los clientes, con la cantidad de facturas que tienen registradas (si no tienen considerar cantidad en 0): `Clients <> Number of bills` en `Clients`
7. Listar los datos de todas las facturas que hayan sido compradas por el cliente de nombre "Kai" y apellido "Bullock": `Bills by Name and Last Name` en `Bills`
8. Seleccionar los productos que han sido facturados al menos 1 vez: `Products billed at least once` en `Bills`
9. Listar los datos de todas las facturas que contengan productos de las marcas “Ipsum”: `Bills with products from a particular brand` en `Bills`
10. Mostrar nombre y apellido de cada cliente junto con lo que gastó en total, con IVA incluido: `Name and Last Name <> what was spent` en `Clients`
11. Se necesita una vista que devuelva los datos de las facturas ordenadas por fecha: `Bill data ordered by dates` en `Bills`
12. Se necesita una vista que devuelva todos los productos que aún no han sido facturados: `Products that were not billed` en `Bills`
13. Implementar la funcionalidad que permita crear nuevos clientes, eliminar y modificar los ya existentes: en `CRUD`
14. Implementar la funcionalidad que permita crear nuevos productos y modificar los ya existentes. Tener en cuenta que el precio de un producto es sin IVA: en `CRUD`

## Para ejecutarlo

Instalar librerias necesarias
```
python3 -m pip install -r requirements.txt
```

Para correr el proyecto (API + UI)
```
./run.sh
```

