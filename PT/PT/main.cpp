#include <direct.h>
#include "Utils/MatlabInterface.h"
#include "Utils/MatlabGMMDataExchange.h"
#include "PT.h"

#define BUFFER_SIZE 4000
void setMatlabPath();

void main(int argc, char* argv[])
{

	std::string source_matrices_path = argv[1];
	std::string res_path = argv[2];
	int util_ind = stoi(argv[3]);

	setMatlabPath();

	PT program;
	program.run(source_matrices_path, res_path);
	//cin.get();
}

void setMatlabPath()
{
	char path[BUFFER_SIZE];
	_fullpath(path, "..\\", BUFFER_SIZE);
	int index = strlen(path);
	//path[index - 4] = '\0';
	std::string matlabPath(path);
	matlabPath += "MatlabScripts\\";
	MatlabInterface::GetEngine().AddScriptPath(matlabPath.c_str());
}