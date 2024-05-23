#!/usr/bin/env python3
import sys
import numpy as np

np.set_printoptions(linewidth=500)

ld_ori_id = 3
u_id = 2
f_id = 1
l_id = 0
infinity = 1000000
counter = 0


class Graph:
    def __init__(self,num_nodes,C,P):
        # classical edge matrix, 4 stands for l,f,l,b
        self.C = C
        self.P = P
        self.counter = 0
        self.counter2 = 0
        self.body = np.ones((num_nodes,num_nodes,4)) * -1
        self.num_nodes = num_nodes

    def dfs(self, start, visited, path = None, capacity = None):
        visited.append(start)
        # if self.counter >= 277:
        #     print(self.counter2)
        if capacity is None:
            capacity = []
        if start != self.num_nodes-1:
            nodes_id = [x for x in range(self.num_nodes)]

            nodes_id_forward = np.where(self.body[start,:,u_id] > -1)[0]

            mask = np.isin(nodes_id_forward, visited, invert=True)

            nodes_id_forward = nodes_id_forward[mask]

            nodes_id_backward = np.where(self.body[:,start, u_id] > -1)[0]

            mask = np.isin(nodes_id_backward, visited, invert=True)
            nodes_id_backward = nodes_id_backward[mask]

            condition = self.body[start,nodes_id_forward,f_id] < self.body[start,nodes_id_forward,u_id]
            nodes_id_forward = nodes_id_forward[condition]

            condition = self.body[nodes_id_backward,start,f_id] > self.body[nodes_id_backward,start,l_id]
            nodes_id_backward = nodes_id_backward[condition]

            for next in nodes_id_forward:
                u_i = self.body[start,next,u_id]
                f_i = self.body[start,next,f_id]
                self.dfs(next, visited,path + [next], capacity + [u_i - f_i])
                if self.capacity:
                    break
            if self.capacity is None:
                for next in nodes_id_backward:
                    l_i = self.body[next, start, l_id]
                    f_i = self.body[next, start, f_id]
                    self.dfs(next,visited, path + [next], capacity + [f_i - l_i])
                    if self.capacity:
                        break
        else:
            self.capacity = capacity
            self.path = path
        self.counter2 += 1

    def init_flow(self, flow = None):
        if flow is not None:
            self.body[:, :, f_id] = flow
        else:
            condition = self.body[:, :, l_id] == 0
            self.body[:, :, f_id][condition] = 0

    def ford_fulkerson(self):
        a = self.body[:,:,l_id]
        b =  self.body[:,:,u_id]
        c = self.body[:,:,f_id]
        d =  self.body[:,:,ld_ori_id]

        while True:
            # print(self.counter)
            # self.counter += 1
            # if self.counter == 277:
            #     print(4)
            self.capacity = None
            self.path = None
            self.dfs(self.num_nodes-2,[],[self.num_nodes-2])

            print(self.path)

            if self.path and self.capacity and min(self.capacity) > 0:
                self.capacity = min(self.capacity)
                c = self.body[:, :, f_id]
                for i,from_id in enumerate(self.path[:-1]):
                    to_id = self.path[i+1]

                    #is backward
                    if self.body[from_id,to_id,l_id] < 0:
                        self.body[to_id,from_id,f_id] -= self.capacity

                    #is forward
                    else:
                        self.body[from_id, to_id, f_id] += self.capacity
            else:
                break

    def find_P(self):
        visited = np.full((self.num_nodes),False)
        s_id = -2
        t_id = -1
        visited[s_id] = True
        path = [-2]
        actual_node = s_id
        min_capacity = infinity
        while not visited[t_id]:
            find_next = False
            #forward
            for i,u in enumerate(self.body[actual_node,:,u_id]):
                if u < 0 or visited[i] == True:
                    continue
                f_i = self.body[actual_node,i,f_id]
                if f_i < u:
                    if u - f_i < min_capacity:
                        min_capacity = u - f_i
                    actual_node = i
                    find_next = True
                    break
            if not find_next:
                #backward
                for i, l in enumerate(self.body[:,actual_node, l_id]):
                    if l < 0 or visited[i] == True:
                        continue
                    f_i = self.body[i,actual_node, f_id]
                    if f_i > l:
                        if f_i  - l < min_capacity:
                            min_capacity = f_i - l
                        actual_node = i
                        find_next = True
                        break
                if not find_next and not visited[t_id]:
                    return None,None
            path.append(actual_node)
            visited[actual_node] = True
        return min_capacity,path

    def prepare_result(self):
        v_min = self.body[self.C:self.C + self.P,-1,f_id]
        products = self.body[0:self.C,self.C:self.C + self.P,f_id]
        products[products < 0] = 0
        v_computed = np.sum(self.body[0:self.C,self.C:self.C + self.P,f_id],axis=0)
        if np.all(v_computed >= v_min):
            res = self.body[0:self.C,self.C:self.C + self.P,f_id]
        else:
            res = None
        return res

    def transform(self):
        self.body[-1,-2,l_id] = 0
        self.body[-1,-2,u_id] = infinity
        mask = self.body > 0
        tmp_body = mask * self.body
        l_in = np.sum(tmp_body[:,:,l_id],axis=0)
        l_out = np.sum(tmp_body[:,:,l_id],axis=1)
        balances = l_in - l_out

        #create new s,t
        new_body = np.ones((self.body.shape[0]+2,self.body.shape[1]+2,4))*-1
        new_body[:-2,:-2,:] = self.body
        self.body = new_body

        #add new edges based on balances
        for i,b in enumerate(balances):
            if b > 0:
                s_id = -2
                c_id = i
                self.body[s_id, c_id, l_id] = 0
                self.body[s_id, c_id, u_id] = b
            elif b < 0:
                t_id = -1
                c_id = i
                self.body[c_id,t_id, l_id] = 0
                self.body[c_id,t_id, u_id] = -b

        #change the rest of l
        self.body[:,:,ld_ori_id] = self.body[:,:,l_id]
        self.body[:,:,u_id] = self.body[:,:,u_id] - self.body[:,:,l_id]
        self.body[:,:,l_id][self.body[:,:,l_id] > 0] = 0
        self.body[:, :, u_id][self.body[:, :, l_id] != 0] = -1
        self.body[self.body < 0] = - infinity
        self.num_nodes += 2
        print("finished transform")
        # ok



def load_data(path2file):
    with open(path2file,"r") as f:
        C, P = map(int, f.readline().split())  # n_cust, n_prod
        graph = Graph(C+P+2, C, P)   # add t and s
        s_id = C+P
        t_id = C+P + 1
        for i in range(C):
            c_id = i
            line = [int(x) for x in f.readline().split()]
            graph.body[s_id, c_id, l_id] = line[0]
            graph.body[s_id, c_id, u_id] = line[1]
            for p in line[2:]:
                p_id = C + p-1
                graph.body[c_id,p_id,l_id] = 0
                graph.body[c_id, p_id, u_id] = 1
        line = [int(x) for x in f.readline().split()]

        for i,v_i in enumerate(line):
            p_id = i + C
            graph.body[p_id,t_id, l_id] = v_i
            graph.body[p_id,t_id, u_id] = infinity
    return graph


def safe_result(path2file,res):
    with open(path2file, "w") as f:
        if res is None:
            f.write(str(-1))
        else:
            for r in res:
                indices = np.where(r == 1)[0] + 1
                if indices.size != 0:            # Get the indices where the value is equal to 1
                    f.write(' '.join(map(str, indices)) + '\n')
    f.close()


if __name__ == '__main__':

    if len(sys.argv) < 3:
        # Default file names
        path2input_file = "in.txt"
        path2output_file = "out.txt"
    else:
        path2input_file = sys.argv[1]
        path2output_file = sys.argv[2]

    g = load_data(path2input_file)
    g_original = load_data(path2input_file)


    g.transform()
    g.init_flow()
    g.ford_fulkerson()
    result =g.body[:,:,f_id] + g.body[:,:,ld_ori_id]

    g_original.init_flow(result[:-2,:-2])
    g_original.ford_fulkerson()
    r = g_original.prepare_result()
    safe_result(path2output_file,r)

    print("end")