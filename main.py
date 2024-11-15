import persistence as p
import clientService as cs
import productService as ps

def main():
    p.populateDb()  # This function will populate the database with the data from the csv files   

    client = cs.getClient(1)
    print(client)
    client['name'] = "Saracatunger"
    print(f"Modifying client {client}")
    cs.modifyClient(client)
    print(f"New client {cs.getClient(1)}")

    product = ps.getProduct(1)
    print(product)
    product['name'] = "Esencia de Saracatunga"
    print(f"Modifying product {product}")
    ps.modifyProduct(product)
    print(f"New product {ps.getProduct(1)}")

    p.session.end_session()   #end session and abort all ongoing transactions

    

main()