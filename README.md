use this command in terminal to querry from docker database
docker exec -it odoo18 psql -h db  -U odoo -d odoo -c "SELECT....;"