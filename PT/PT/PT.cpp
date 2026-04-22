#include "PT.h"
#include "Utils/MatlabInterface.h"
#include "Utils/MatlabGMMDataExchange.h"


PT::PT() {
	std::cout.rdbuf(std::cerr.rdbuf()); //added since cout does not print to output window
}

bool PT::run(std::string source_matrices_path, std::string res_path)
{
	return compute_middle_angle(source_matrices_path, res_path);
}

bool PT::compute_middle_angle(std::string source_matrices_path, std::string res_path)
{
	std::string cmd = "load('" + source_matrices_path + "')";
	MatlabInterface::GetEngine().EvalToCout(cmd.c_str());
	GMMDenseColMatrix f;
	GMMDenseColMatrix one_rings;
	GMMDenseColMatrix integrated_angles;
	GMMDenseColMatrix all_one_ring_angles;
	GMMDenseColMatrix all_one_ring_angles_sums;
	MatlabGMMDataExchange::GetEngineDenseMatrix("f", f);
	MatlabGMMDataExchange::GetEngineDenseMatrix("one_rings", one_rings);
	MatlabGMMDataExchange::GetEngineDenseMatrix("integrated_angles", integrated_angles);
	MatlabGMMDataExchange::GetEngineDenseMatrix("all_one_ring_angles", all_one_ring_angles);
	MatlabGMMDataExchange::GetEngineDenseMatrix("all_one_ring_angles_sums", all_one_ring_angles_sums);

	GMMDenseColMatrix angles_vertices_to_faces(f.nrows(), 3);
	
	for (int f_i = 0; f_i < f.nrows(); f_i++)
	{
		for (int i = 0; i < 3; i++)
		{
			int v_i = f(f_i, i);
			int v_1 = f(f_i, (i + 1) % 3);
			int v_2 = f(f_i, (i + 2) % 3);

			int v1_index_in_onering = 0;
			int v2_index_in_onering = 0;
			double v_i_onering_angle_to_v1;
			double v_i_onering_angle_to_v2;
			for (int j = 0; j < one_rings.ncols(); j++)
			{
				if (one_rings(v_i, j) == v_1)
				{
					v1_index_in_onering = j;
				}
				if (one_rings(v_i, j) == v_2)
				{
					v2_index_in_onering = j;
				}
			}

			if ((v1_index_in_onering == one_rings.ncols() - 1) && (v2_index_in_onering < v1_index_in_onering - 1))
			{
				v_i_onering_angle_to_v1 = integrated_angles(v_i, v1_index_in_onering);
				v_i_onering_angle_to_v2 = all_one_ring_angles_sums(v_i, 0);
			}
			else if ((v2_index_in_onering == one_rings.ncols() - 1) && (v1_index_in_onering < v2_index_in_onering - 1))
			{
				v_i_onering_angle_to_v1 = all_one_ring_angles_sums(v_i, 0);
				v_i_onering_angle_to_v2 = integrated_angles(v_i, v2_index_in_onering);
			}
			else
			{
				v_i_onering_angle_to_v1 = integrated_angles(v_i, v1_index_in_onering);
				v_i_onering_angle_to_v2 = integrated_angles(v_i, v2_index_in_onering);
			}

			angles_vertices_to_faces(f_i, i) = (v_i_onering_angle_to_v2 + v_i_onering_angle_to_v1) / 2;
		}
	}
	double t1 = 1;
	cout << "Total time: " << t1 << endl;

	GMMDenseComplexColMatrix total_time(1, 1);
	total_time(0, 0) = t1;

	MatlabGMMDataExchange::SetEngineDenseMatrix("angles_vertices_to_faces", angles_vertices_to_faces);
	MatlabGMMDataExchange::SetEngineDenseMatrix("total_time", total_time);
	cmd = "save('" + res_path + "', 'angles_vertices_to_faces', 'total_time')";
	MatlabInterface::GetEngine().EvalToCout(cmd.c_str());
	return true;
}