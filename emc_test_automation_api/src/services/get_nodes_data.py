from PyLTSpice import SimCommander, LTspice
import os

class Node_data:
    def __init__(self):
        pass
    # def generate_netlist(asc_file):
    #     # sim = SimCommander(asc_file)
    #     # sim.add_instruction('.tran 100u 100m 0 100u')
    #     # sim.run()

    #     # sim = SimCommander(asc_file)
    #     # pulse = 'Pulse1_12V' # Different pulses can be changed here
    #     # # pulse = '4-6-4_12V_LoadDumpWithoutSuppressionTestA'
    #     # node = 'Vin'
    #     # Ri = 1
    #     # sim.add_instruction(f'XU1 node1 0 {pulse} Ri=1u')
    #     # sim.add_instruction(f'Ri node1 {node} {Ri}')
    #     # sim.add_instruction('.tran 100u 100m 0 100u')
    #     # # sim.add_instruction('.op')
    #     # sim.add_instruction('.lib ISO7637-2.lib')
    #     # sim.run()


    #     netlist = asc_file.replace(".asc", ".net")
    #     #create an empty netlist file
    #     with open(netlist, 'w') as f:
    #         pass

    #     LTspice.create_netlist(asc_file)

    #     search_path='.'
    #     for root, dirs, files in os.walk(search_path):
    #         if netlist in files:
    #             return os.path.join(root, netlist)

    #     print(f"Netlist file not found {netlist}") 
    #     return None
    @staticmethod
    def generate_netlist(asc_file):
        sim = SimCommander(asc_file)
        try:
            sim.add_instruction('.tran 100u 100m 0 100u')
            sim.run()
        except Exception as e:
            print(f"Error running simulation: {e}")
            return None
        
        netlist = asc_file.replace(".asc", ".net")
        print("\n\n\n\n",netlist,"\n\n\n\n")
        return str(netlist)
    
    @staticmethod
    def get_node_details(asc_file):
        netlist_path = Node_data.generate_netlist(asc_file)
        print(netlist_path)
 
        components = {}
        nodes = set()
        with open(netlist_path, 'r') as f:
            netlist_lines = f.readlines()

            for line in netlist_lines:
                tokens = line.split()
                if tokens:  # Avoid empty lines
                    comp_name = tokens[0]
                    # Check for R, L, or C components
                    if comp_name.startswith(('R', 'L', 'C')):
                        node1 = tokens[1]
                        node2 = tokens[2]
                        components[comp_name] = [node1, node2]
                        nodes.add(node1)
                        nodes.add(node2)
        results = {'complete_node_data':components, 'nodes' : list(nodes), 'netlist_path': netlist_path}
        print(results)
        return results