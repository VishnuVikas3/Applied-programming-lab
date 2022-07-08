import numpy as np
from sys import argv, exit

CIRCUIT = '.circuit'
END = '.end'

class Home():
    
    def __init__(self,line):
        self.line = line
        self.words = self.line.split()
        self.Node1=self.words[1]
        self.Node2=self.words[2]
        self.initial=self.words[0]
        self.element_name=self.words[0][0]
        
        if len(self.words)== 6 :
            phase=float(self.words[5])
            Vpp =float(self.words[4])/2
            Vpp_real=(Vpp*np.cos(phase))
            Vpp_imag=(Vpp*np.sin(phase))
            self.value=complex(Vpp_real,Vpp_imag)
            self.type = 'ac'

        elif len(self.words)==5:
            self.type='dc'
            self.value=float(self.words[4])
        else:
            self.type='dc'
            self.value=float(self.words[3])
def Matrix_Build(PARAGRAPH,M,b,n,k,w):
    for i in PARAGRAPH:
        if Home(i).element_name=='R':
            M[Nodes_dict[Home(i).Node1]][Nodes_dict[Home(i).Node1]] += 1/float((Home(i).words[3]))
            M[Nodes_dict[Home(i).Node2]][Nodes_dict[Home(i).Node2]] += 1/float((Home(i).words[3]))
            M[Nodes_dict[Home(i).Node1]][Nodes_dict[Home(i).Node2]] -= 1/float((Home(i).words[3]))
            M[Nodes_dict[Home(i).Node2]][Nodes_dict[Home(i).Node1]] -= 1/float((Home(i).words[3]))
        if Home(i).element_name=='C':
            M[Nodes_dict[Home(i).Node1]][Nodes_dict[Home(i).Node1]] += complex(0, 2*np.pi*w*float(Home(i).words[3]))
            M[Nodes_dict[Home(i).Node2]][Nodes_dict[Home(i).Node2]] += complex(0, 2*np.pi*w*float(Home(i).words[3]))
            M[Nodes_dict[Home(i).Node1]][Nodes_dict[Home(i).Node2]] -= complex(0, 2*np.pi*w*float(Home(i).words[3]))
            M[Nodes_dict[Home(i).Node2]][Nodes_dict[Home(i).Node1]] -= complex(0, 2*np.pi*w*float(Home(i).words[3]))

        if Home(i).element_name=='V':
            M[Nodes_dict[Home(i).Node1]][n+Voltage_dict[Home(i).initial]] += 1
            M[n+Voltage_dict[Home(i).initial]][Nodes_dict[Home(i).Node1]] -= 1
            M[Nodes_dict[Home(i).Node2]][n+Voltage_dict[Home(i).initial]] -= 1
            M[n+Voltage_dict[Home(i).initial]][Nodes_dict[Home(i).Node2]] += 1
            b[n+Voltage_dict[Home(i).initial]] = (Home(i).value)

        if Home(i).element_name=='I':
            b[Home(i).Node1] -= (Home(i).value)
            b[Home(i).Node2] += (Home(i).value)

        if Home(i).element_name=='L':
            if w==0:
                M[Nodes_dict[Home(i).Node1]][n+k+Ind_dict[Home(i).initial]] += 1
                M[n+k+Ind_dict[Home(i).initial]][Nodes_dict[Home(i).Node1]] -= 1
                M[Nodes_dict[Home(i).Node2]][n+k+Ind_dict[Home(i).initial]] -= 1
                M[n+k+Ind_dict[Home(i).initial]][Nodes_dict[Home(i).Node2]] += 1

            else:
                M[Nodes_dict[Home(i).Node1]][Nodes_dict[Home(i).Node1]] -= complex(0, 1/(2*np.pi*w*float(Home(i).words[3])))
                M[Nodes_dict[Home(i).Node2]][Nodes_dict[Home(i).Node2]] -= complex(0, 1/(2*np.pi*w*float(Home(i).words[3])))
                M[Nodes_dict[Home(i).Node1]][Nodes_dict[Home(i).Node2]] += complex(0, 1/(2*np.pi*w*float(Home(i).words[3])))
                M[Nodes_dict[Home(i).Node2]][Nodes_dict[Home(i).Node1]] += complex(0, 1/(2*np.pi*w*float(Home(i).words[3])))

if len(argv) != 2:
    print('\nUsage: %s <inputfile>' % argv[0])
    print("Invalid number of arguments.Please provide correct '.netlist' file ")
    exit()

"""
The use might input a wrong file name by mistake.
In this case, the open function will throw an IOError.
Make sure you have taken care of it using try-catch
"""
try:
    with open(argv[1]) as f:
        lines = f.readlines()
        start = -1; end = -2
        for line in lines:              # extracting circuit definition start and end lines
            if CIRCUIT == line[:len(CIRCUIT)]:
                start = lines.index(line)
            elif END == line[:len(END)]:
                end = lines.index(line)
                break
        if start >= end:                   # validating circuit block
            print('Invalid circuit definition')
            exit(0)
        PARAGRAPH = lines[start+1:end]    # Here PARAGRAPH contains the required lines from input file
        w=0
        for line in lines:
            if line[:len('.ac')]=='.ac':
                w = float(line.split()[2])  # extracting w from the input file

        f=float(w/(2*(np.pi)))              # Finding Frequency for AC voltage sources
        Nodes_list=[]
        Nodes_dict={}
        Volt_name=[]
        Voltage_dict={}
        Ind_name=[]
        Ind_dict={}
        index=1
        
        for line in PARAGRAPH:
            Nodes_list.append(Home(line).Node1)  
            Nodes_list.append(Home(line).Node2) # Here Nodes_list contains the all the FROM & TO nodes.

            if (Home(line).element_name=='V'):
                Volt_name.append(Home(line).initial)

            elif (Home(line).element_name=='L'):
                Ind_name.append(Home(line).initial)

        Nodes_list=list(set(Nodes_list))     # Removes the repeated nodes in the list
        n=len(Nodes_list)
        for i in Nodes_list:
            if i=='GND':
                Nodes_dict[i]=0
            else:
                Nodes_dict[i]=index
                index=index+1

        for i,j in enumerate(Volt_name):
             Voltage_dict[j] = i
        for i,j in enumerate(Ind_name):
             Ind_dict[j] = i
            
        k=len(Volt_name)
        l=len(Ind_name)
        switch=0
        if w==0:
            switch=1
            M = np.zeros((n+k+l,n+k+l),dtype=complex) # Creating M & b matrix of resepective dimensions
            b = np.zeros(n+k+l,dtype=complex)
        else:
            M = np.zeros((n+k,n+k),dtype=complex)
            b = np.zeros(n+k,dtype=complex)
           
        Matrix_Build(PARAGRAPH,M,b,n,k,w)   # Calling Matric_Build function
        M[0] = 0
        M[0,0] =1
        print('The M matrix is :\n',M)  
        print('The b matrix is :\n',b)      # Printing Matrix M & b
        try:
          x = np.linalg.solve(M,b)         # Solves Matix X
        except Exception:
            print('The Matrix cannot be inverted as it is singular.Provide a valid matrix entries')
            exit()
        for i in Nodes_list:
            print("The voltage at node {} is {}".format(i,x[Nodes_dict[i]]))
        for j in Volt_name:
            print('The current through source {} is {}'.format(j,x[n+Voltage_dict[j]]))
        if switch:
            for i in Ind_name:
                print("The current through inductor {} is {}".format(i,x[n+k+Ind_dict[i]]))
                  
        
except IOError:
    print('Invalid file.Enter the correct netlist file')
    exit()


