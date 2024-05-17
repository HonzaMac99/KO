#include <iostream>     
#include <sstream>
#include <fstream>
#include <string>
#include <chrono>
#include <vector>
#include <algorithm>

#define PRINT false


typedef std::vector<int> Vec1D;
typedef std::vector<std::vector<int>> Vec2D;

/*//{ data loading */

// convert file line into arr of 3 ints
int* get_int_arr(std::string file_line) {
  std::stringstream ss;
  int *number_array = new int[3]; 

  ss << file_line;

  // Check all words in the line for any ints 
  int i = 0;
  int number;
  while(!ss.eof() and i < 3) {
    ss >> number;
    number_array[i] = number;  
    i++;
  }

  // convert the input into python indexing
  number_array[0] -= 1;
  number_array[1] -= 1;

  return number_array;
}


// extract the edges from the file into a 2D array
int** get_file_data(std::string fname, int &n_verts, int &n_edges) {

  std::ifstream F(fname);
  std::string f_line;
   
  std::getline(F, f_line);
  n_edges = std::stoi(f_line); 

  if (PRINT) 
    std::cout << "n_edges: " << n_edges << std::endl;

  int **data = new int *[n_edges];
  int *num_array;

  int i = 0;
  while (getline(F, f_line) and i < n_edges) {
    num_array = get_int_arr(f_line);

    if (num_array[0] > n_verts) 
      n_verts = num_array[0];
    if (num_array[1] > n_verts) 
      n_verts = num_array[1];

    data[i++] = num_array;
  }
  n_verts += 1; // convert from max idx to max id

  F.close();
  return data;
}

/*//}*/

/*//{ rand permutations gen */

int getRandNum(int n) {
    auto t_now = std::chrono::high_resolution_clock::now().time_since_epoch();
    auto t_now_ms = std::chrono::duration_cast<std::chrono::nanoseconds>(t_now);
    int t_now_ms_count = t_now_ms.count();
    std::srand(t_now_ms_count);

    int index = std::rand() % n;
    return index;
}

// Function to return the next random number
int getNum(std::vector<int>& v)
{
    int index = getRandNum(v.size());
    int num = v[index];
    v[index] = v.back();
    v.pop_back();

    return num;
}
 
// Function to generate n non-repeating random numbers
std::vector<int> generatePrmt(int n)
{
    Vec1D v(n);
    Vec1D rand_arr(n);
 
    // v = [0, 1, 2, ..., n-1]
    for (int i = 0; i < n; i++)
        v[i] = i;
 
    // get a random number from the vector
    for (int i = 0; i < n; i++) 
        rand_arr[i] = getNum(v);

    if(v.size()) 
      std::cout << "Something got wrong\n";
    return rand_arr;
}
/*//}*/

/*//{ graph functions */
Vec2D create_adj(int **data, int n_v, int n_e) {
  Vec2D adj(n_v);
  for (int i = 0; i < n_e; i++) {
    int v_s = data[i][0];
    int v_t = data[i][1];
    adj[v_s].push_back(v_t);
  }

  if (PRINT) {
    std::cout << "n_vertices: " << n_v << std::endl;
    for(int i = 0; i < n_v; i++) {
      std::cout << i << ": [";
      for (size_t j = 0; j < adj[i].size()-1; j++) 
        std::cout << adj[i][j] << ", ";
      std::cout << adj[i][adj[i].size()-1] << "]" << std::endl;
    }
  }
  return adj;
}


void expand_vertex(const int v, Vec1D &top_ord, Vec1D &visited, const Vec2D adj) {

  visited[v] = 1;

  // go through the v's children in random order
  int n_v_next = adj[v].size();
  Vec1D v_next_prmt = generatePrmt(n_v_next);

  for (int i = 0; i < n_v_next; i++) {
    int idx = v_next_prmt[i];
    int v_next = adj[v][idx]; 
    if (!visited[v_next])
      expand_vertex(v_next, top_ord, visited, adj);
  }

  top_ord.push_back(v);
}


std::vector<int> create_top_ord(const Vec2D adj, const Vec1D v_prmt, const int n_v) {
  Vec1D top_ord;
  Vec1D visited(n_v, 0);

  for (int i = 0; i < n_v; i++) {
    int v_s = v_prmt[i];
    if (!visited[v_s])
      expand_vertex(v_s, top_ord, visited, adj);
  }

  std::reverse(top_ord.begin(), top_ord.end());
  // return top_ord;

  // convert to array of indexes, which is faster for getting the positions in top_ord
  Vec1D top_ord_idxs(n_v, 0);
  for (int i = 0; i < n_v; i++) { 
    top_ord_idxs[top_ord[i]] = i;
  }
  return top_ord_idxs;
}


// todo: use top_ord dict instead of Vec1D?
int rm_cycles(Vec2D &rm_edges, const Vec1D top_ord, int **data, int n_e) {
  int total_cost = 0;
  for(int i = 0; i < n_e; i++) {
    Vec1D edge = {data[i][0], data[i][1]};
    if (top_ord[edge[0]] > top_ord[edge[1]]) {
      rm_edges.push_back(edge);
      total_cost += data[i][2];
    }
  }
  return total_cost;
}
/*//}*/


int main(int argc, char* argv[]) {
  auto t_start = std::chrono::high_resolution_clock::now();

  std::string file_in  = "/home/honzamac/cvut/m2/KO/cc-rt/files/in.txt";
  std::string file_out = "/home/honzamac/cvut/m2/KO/cc-rt/files/out.txt";
  double time_limit    = 1.0;  // [s]

  if (argc > 1) file_in    = argv[1];
  if (argc > 2) file_out   = argv[2];
  if (argc > 3) time_limit = std::stod(argv[3]);

  std::cout << "TIME LIMIT: " << time_limit << "s" << std::endl;
  double time_limit_ms = time_limit*1000.0;

  int **data, n_edges = 0, n_verts = 0;
  data = get_file_data(file_in, n_verts, n_edges);
  Vec2D adj = create_adj(data, n_verts, n_edges);

  // double print_limit_ms = 13.0 * (n_edges / 10000.0); 

  int best_total_cost = std::numeric_limits<int>::max();
  Vec2D best_rm_edges;
  // Vec1D best_top_ord;

  auto t_now = std::chrono::high_resolution_clock::now();
  auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(t_now - t_start);
  do {  
    int total_cost;
    Vec2D rm_edges;

    Vec1D v_prmt = generatePrmt(n_verts);
    Vec1D top_ord = create_top_ord(adj, v_prmt, n_verts);
    total_cost = rm_cycles(rm_edges, top_ord, data, n_edges);

    if (total_cost < best_total_cost) {
      std::cout << "new_best_cost: " << total_cost << std::endl;
      best_total_cost = total_cost;
      best_rm_edges = rm_edges;
      // best_top_ord = top_ord;
    }

    t_now = std::chrono::high_resolution_clock::now();
    duration = std::chrono::duration_cast<std::chrono::milliseconds>(t_now - t_start);
    // std::cout << "Time taken: " << duration.count() << " milliseconds" << std::endl; 
  } 
  while(duration.count() < time_limit_ms*0.95);

  if (PRINT) {
    std::cout << best_total_cost << std::endl;
    for(int i = 0; i < (int)best_rm_edges.size(); i++) 
      std::cout << best_rm_edges[i][0]+1 << " " << best_rm_edges[i][1]+1 << std::endl;
  }

  std::ofstream F_out(file_out);
  F_out << best_total_cost << std::endl;
  for(int i = 0; i < (int)best_rm_edges.size(); i++) {
    F_out << best_rm_edges[i][0]+1 << " " << best_rm_edges[i][1]+1 << std::endl;
  }
  F_out.close();

  // clear the memory
  for (int i = 0; i < n_edges; i++)
    delete [] data[i];
  delete [] data;

  return 0;
}




