#pragma once
#include "Utils/GMM_Macros.h"
using namespace std;

class PT
{

public:
	PT();
	~PT() {}
	bool run(std::string source_matrices_path, std::string res_path);
	bool compute_middle_angle(std::string source_matrices_path, std::string res_path);

};

