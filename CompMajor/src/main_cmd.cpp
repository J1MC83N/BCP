#include "Newton.h"
#include <igl\read_triangle_mesh.h>
#include <igl\writeOBJ.h>
#include <time.h>
#include <Utils/MatlabInterface.h>
#include "Utils/MatlabGMMDataExchange.h"



#define BUFFER_SIZE 4000
void setMatlabPath();

double normalizeMeshArea(MatX3& V, MatX3i& F);


int main(int argc, char** argv)
{
	setMatlabPath();
	unsigned int num_threads = max(atoi(getenv("OMP_NUM_THREADS")), 1);
	omp_set_num_threads(num_threads);

	if (argc < 3)
	{
		cout << "Syntax: Parameterization_cmd.exe <Input OBJ file name> <Output OBJ file name> <Output MAT file name> <Meta data .txt file name> <target energy> <target time> <Initialization file name>" << endl;
		return false;
	}
	// Tutte is performed anyway, even if target time is smaller
	MatX3 V;
	MatX3i F;
	cout << "Started loading mesh..." << endl;
	if (!igl::read_triangle_mesh(argv[1], V, F))
	{
		cerr << "Failed to load mesh: " << argv[1] << endl;
		return false;
	}

	MatX3 init_V;
	MatX3i init_F;

	if (argc == 8)
		igl::read_triangle_mesh(argv[7], init_V, init_F);

	float target_Esd = 2.0;
	if (argc >= 6)
		target_Esd = stof(argv[5]);

	//target_Esd = 3.1;

	float target_time = 500.0;
	if (argc >= 7)
		target_time = stof(argv[6]);

	cout << "Finished loading mesh..." << endl;

	float time_Tutte_init = 0.0;
	long start_init_time = clock();

	double normalizationFactor = normalizeMeshArea(V, F);
	V /= normalizationFactor;
	Newton solver;
	if (argc <= 7)
		solver.init(V, F, time_Tutte_init);
	else
	{
		init_V /= normalizationFactor;
		solver.init_from_input(V, F, init_V);
	}

	long end_init_time = clock();

	long cur_time = clock();

	float prevF, curF;
	curF = INFINITY;
	Vec prevX = solver.m_x;

	int fcounter = 0, xcounter = 0, num_conv_iters = 3;
	float ftol = 1e-2, xtol = 1e-10;
	int iter = 0;

	prevF = solver.f / solver.energy->symDirichlet->Area.sum();

	int MAX_ITERS = 1000;
	int iters_count = 0;
	bool runStepSizeCheck = true;

	for (iter = 0; iter < MAX_ITERS; iter++)
	{
		solver.step();

		curF = solver.linesearch();

		cur_time = clock();
		if ((cur_time - start_init_time) / 1000.0 >= target_time)
			break;

		iters_count++;

		if (std::isnan(prevF))
			break;

		if (abs(curF - prevF) < ftol * (solver.f + 1))
		{
			if (fcounter >= num_conv_iters)
			{
				cout << "Converged: Change in energy < tol" << endl;
				break;
			}
			else
				fcounter += 1;
		}
		else
			fcounter = 0;

		if ((solver.m_x - prevX).norm() < xtol * (solver.m_x.norm() + 1))
		{
			if (xcounter >= num_conv_iters)
			{
				cout << "Converged: Change in X < tol" << endl;
				break;
			}
			else
				xcounter += 1;
		}
		else
			xcounter = 0;

		if (curF <= target_Esd)
		{
			cout << "Converged: reached target Esd" << endl;
			break;
		}

		Vec tmp = solver.m_x;
		prevX = tmp;
		prevF = solver.f / solver.energy->symDirichlet->Area.sum();

	}
	Vec tmp = solver.m_x;
	prevX = tmp;
	cout << "Esd = " << curF << endl;
	cout << "k = " << solver.energy->symDirichlet->evaluate_small_k(prevX) / solver.energy->symDirichlet->Area.sum() << endl;

	long end_Newton_time = clock();

	cout << "Newton time consumption: " << (end_Newton_time - end_init_time) / 1000.0 << endl;
	cout << "Total time consumption: " << (end_Newton_time - start_init_time) / 1000.0 << endl;
	cout << iters_count << " iterations were performed" << endl;

	MatX3 CN;
	MatX3i FN;
	solver.uv = Eigen::Map<MatX2>(prevX.data(), prevX.size() / 2, 2);
	MatX3 UVs(V.rows(), 3);
	UVs.leftCols(2) = solver.uv;
	UVs *= normalizationFactor;
	UVs.rightCols(1).setZero();
	if (strcmp(argv[2], "") != 0)
		igl::writeOBJ(argv[2], UVs, F, CN, FN, CN, FN);

	
	std::string uv_mat_path = argv[3];
	if (uv_mat_path != "")
	{
		GMMDenseColMatrix uvs(V.rows(), 2);
		for (int i = 0; i < V.rows(); i++)
		{
			uvs(i, 0) = UVs(i, 0);
			uvs(i, 1) = UVs(i, 1);
		}
		MatlabGMMDataExchange::SetEngineDenseMatrix("uvs", uvs);
		std::string cmd_save_uv = "save('" + uv_mat_path + "', 'uvs');";
		MatlabInterface::GetEngine().Eval(cmd_save_uv.c_str());
	}
	

	std::string file_path = argv[4];

	// Create an ofstream object
	std::ofstream file(file_path);

	// Check if the file is open
	if (file.is_open()) {
		file << "Total time consumption: " << (end_Newton_time - start_init_time) / 1000.0 << endl;
		file << "Newton iteration count: " << iters_count << std::endl;
		file << "Final E_SD: " << curF << endl;
		file << "Tutte initialization time: " << time_Tutte_init << endl;
		file << "Tutte + Hessian initialization time: " << (end_init_time - start_init_time) / 1000.0 << endl;
		file << "Did Tutte was finished before target time: " << (time_Tutte_init <= target_time) << endl;


		// Close the file
		file.close();

		std::cout << "Text successfully saved to " << file_path << std::endl;
	}
	else {
		// Handle the error if the file couldn't be opened
		std::cerr << "Failed to open file " << file_path << std::endl;
	}
	return 0;
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


double normalizeMeshArea(MatX3& V, MatX3i& F) {
	Eigen::VectorXd M;
	// set uv coords scale
	igl::doublearea(V, F, M);
	M /= 2.0;

	double mesh_area = M.sum();
	return sqrt(mesh_area);
}