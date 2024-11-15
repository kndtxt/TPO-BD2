import Persistence as p

def main():
    p.populateDb()  # This function will populate the database with the data from the csv files
    print(p.getClient("Jacob", "Cooper"))
    #print(p.getClient("Jacob", "Cooper"))
    #p.insertClient(nroCliente=nroCliente,
    #        nombre=nombre,
    #        apellido=apellido,
    #        direccion=direccion,
    #        activo=activo,
    #        telefono=Telefono(codigoArea=codigoArea, nroTel=nroTel, tipoTel=tipoTel))

main()