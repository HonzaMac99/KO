#include <iostream>     
#include <sstream>
#include <fstream>
#include <string>
#include <chrono>


// convert file line into arr of 3 ints
int* get_int_arr(std::string file_line) {
  std::stringstream ss;
  int *number_array = new int[3]; 

  ss << file_line;

  // Check all words in the line for any ints 
  int i = 0;
  while(!ss.eof() and i < 3) {
    ss >> number_array[i];
    i++;
  }
  return number_array;
}


// extract the edges from the file into a 2D array
int** get_file_data(std::string fname, int &n_edges, int &n_verts) {

  std::fstream F(fname);
  std::string f_line;
   
  getline(F, f_line);
  n_edges = get_int_arr(f_line)[0]; 

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

  F.close();
  return data;
}


int main(int argc, char* argv[]) {
  // Start measuring time
  auto t_start = std::chrono::high_resolution_clock::now();

  // Read the input from file or stdin
  std::string file_in  = "/home/honzamac/cvut/m2/KO/cc-rt/files/in.txt";
  std::string file_out = "/home/honzamac/cvut/m2/KO/cc-rt/files/out.txt";
  double time_limit    = 10.0;  // [s]

  if (argc > 1) file_in    = argv[1];
  if (argc > 2) file_out   = argv[2];
  if (argc > 3) time_limit = std::stod(argv[3]);

  double time_limit_ms = time_limit*1000.0;

  int **data, n_edges = 0, n_verts = 0;
  data = get_file_data(file_in, n_edges, n_verts);

  std::cout << "Data check: " << std::endl;
  for(int i = 0; i < n_edges; i++) 
    std::cout << data[i][0] <<" "<< data[i][1] <<" "<< data[i][2] << std::endl;
  std::cout << "n_verts: " << n_verts << std::endl;

  std::ofstream F_out(file_out);
  for(int i = 0; i < n_edges; i++) 
    F_out << data[i][0] <<" "<< data[i][1] <<" "<< data[i][2] << std::endl;
  F_out.close();

  auto t_now = std::chrono::high_resolution_clock::now();
  auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(t_now - t_start);
  while(duration.count() < time_limit_ms*0.95) {
    std::cout << "Time taken: " << duration.count() << " milliseconds" << std::endl; 






    t_now = std::chrono::high_resolution_clock::now();
    duration = std::chrono::duration_cast<std::chrono::milliseconds>(t_now - t_start);
  }

  // clear the memory
  for (int i = 0; i < n_edges; i++)
    delete [] data[i];
  delete [] data;

  return 0;
}









