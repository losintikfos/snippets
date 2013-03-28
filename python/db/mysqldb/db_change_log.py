'''
@author: bdadson

Insert dummy data to table to simulate stargate
'''
from db_access import DataAccess

class NetworkType:
    PRIVATE = 'PRIVATE'
    PUBLIC = 'PUBLIC'


def fill():
    dao = DataAccess()
    try:    
        # TRUNCATE TABLES
        dao.commit("TRUNCATE TABLE customer")
        dao.commit("TRUNCATE TABLE ip_allocation")
        dao.commit("TRUNCATE TABLE private_assigned_ip_addr")
        dao.commit("TRUNCATE TABLE private_vlan")
        dao.commit("TRUNCATE TABLE public_assigned_ip_addr")
        dao.commit("TRUNCATE TABLE switch")
        dao.commit("TRUNCATE TABLE switch_connected_ports")
    
        # RESET AUTO-INCREMENTAL NUMBER
        dao.commit("ALTER TABLE customer AUTO_INCREMENT = 1")
        dao.commit("ALTER TABLE ip_allocation AUTO_INCREMENT = 1")
        dao.commit("ALTER TABLE private_assigned_ip_addr AUTO_INCREMENT = 1")
        dao.commit("ALTER TABLE private_vlan AUTO_INCREMENT = 1")
        dao.commit("ALTER TABLE switch AUTO_INCREMENT = 1")
        dao.commit("ALTER TABLE switch_connected_ports AUTO_INCREMENT = 1")
        
        # POPULATE TABLE CUSTOMER
        command = {
            "INSERT INTO customer \
            (title, fname, mname, lname) \
            VALUES (%s, %s, %s, %s)" :
            [
             ("Mr", "Foo" , "DARR", "Barr"),
             ("Mrs", "Harriet" , "Lotty", "Brown"),
             ("Mr", "Joe" , "Harrison", "Blogg")
             ]}
        dao.commit(command, True)
        
        
        # POPULATE TABLE SWITCH
        command = {
            "INSERT INTO switch \
            (is_of, name, number_of_ports) \
            VALUES (%s, %s, %s)" :
            [
             (True, "s1", 5),
             (True, "s2", 5),
             (True, "s3", 5)
             ]}
        dao.commit(command, True)
        
        # POPULATE TABLE PRIVATE_VLAN
        command = {
            "INSERT INTO private_vlan \
            (vlan_id, customer_id, description) \
            VALUES (%s, %s, %s)":
            [
             (100, 1, "VLAN for Mr. Foo DARR Bar"),
             (101, 2, "VLAN for Mrs. Harriet Lotty Brown"),
             (102, 3, "VLAN for Mr. Joe Harrison Blogg")
             ]}
        dao.commit(command, True)

        # POPULATE TABLE SWITCH_CONNECTED_PORTS
        command = {
            "INSERT INTO switch_connected_ports \
            (port_no, label, switch_id, customer_id,\
             private_ip_assign_id, private_vlan_id) \
             VALUES (%s, %s, %s, %s, %s, %s)" :
            [
             # Physical connection customer-1
             (1, "s1-eth1", 1, 1, 0, 1),
             (2, "s1-eth2", 1, 1, 0, 1),
             (3, "s3-eth3", 3, 1, 0, 1),
             
             # Physical connection for customer-2
             (1, "s2-eth1", 2, 2, 0, 2),
             (2, "s2-eth2", 2, 2, 0, 2),
             (3, "s1-eth3", 1, 2, 0, 2),
             
             # Physical connection for customer-3
             (1, "s3-eth1", 3, 3, 0, 3),
             (2, "s3-eth2", 3, 3, 0, 3),
             (3, "s2-eth3", 2, 2, 0, 3)
             ]
            }                   
        dao.commit(command, True)
        
        # POPULATE TABLE TO IP_ALLOCATION
        command = {
            "INSERT INTO ip_allocation (start_range, end_range, \
            customer_id, type, netmask) VALUES (%s, %s, %s, %s, %s)" :
            [
             ("192.168.0.0", "192.168.0.255", 1 , NetworkType.PRIVATE, "255.255.255.0"),
             ("192.168.1.0", "192.168.1.255", 2 , NetworkType.PRIVATE, "255.255.255.0"),
             ("192.168.2.0", "192.168.2.255", 3 , NetworkType.PRIVATE, "255.255.255.0")
             ]}
        dao.commit(command, True)
        
        # POPULATE PRIVATE_ASSIGNED_IP_ADDR
        command = {
            "INSERT INTO private_assigned_ip_addr (ip_addr, netmask, \
            host_name, description, customer_id, ip_alloc_id, switch_connected_port_id) VALUES\
             (%s, %s, %s, %s, %s, %s, %s)" :
            [
             # IP Assigned for customer-1
             ("192.168.0.2", "255.255.255.0", "s1h1" , "IP Assigned to Port label s1-eth1", 1, 1, 1),
             ("192.168.0.3", "255.255.255.0", "s1h2" , "IP Assigned to Port label s1-eth2", 1, 1, 2),
             ("192.168.0.4", "255.255.255.0", "s3h3" , "IP Assigned to Port label s3-eth3", 1, 1, 3),
             
             # IP Assign for customer-2
             ("192.168.1.2", "255.255.255.0", "s2h1" , "IP Assigned to Port label s2-eth1", 2, 2, 4),
             ("192.168.1.3", "255.255.255.0", "s2h2" , "IP Assigned to Port label s2-eth2", 2, 2, 5),
             ("192.168.1.4", "255.255.255.0", "s1h3" , "IP Assigned to Port label s1-eth3", 2, 2, 6),
             
             # IP Assign for customer-3
             ("192.168.2.2", "255.255.255.0", "s3h1" , "IP Assigned to Port label s3-eth1", 3, 3, 7),
             ("192.168.2.3", "255.255.255.0", "s3h2" , "IP Assigned to Port label s3-eth2", 3, 3, 8),
             ("192.168.2.4", "255.255.255.0", "s2h3" , "IP Assigned to Port label s2-eth3", 3, 3, 9)
             ]
            }
        dao.commit(command, True)
        
    except RuntimeError as e:
        print "Error occured while making insert(s) to \
            to database ({0}): {1}".format(e.errno, e.strerror)
    
if __name__ == "__main__":
    fill()
