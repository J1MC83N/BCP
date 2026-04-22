//
// Created by Charles Du on 11/13/22.
//
//#include <CLI/CLI.hpp>
#include <Eigen/Core>
#include <Isometric_Injective_Energies/src/IO.h>
//#include <ghc/filesystem.hpp>
#include <Isometric_Injective_Energies/src/geo_util.h>
#include <Isometric_Injective_Energies/src/NewtonSolver.h>
#include <Isometric_Injective_Energies/src/QuasiNewtonSolver.h>
#include <Isometric_Injective_Energies/src/IsoTLC_2D_Formulation.h>
#include <iostream>
#include "Utils/MatlabInterface.h"
#include "Utils/MatlabGMMDataExchange.h"

using namespace Eigen;
using namespace std;

bool runIsoTLC2D(GMMDenseColMatrix& inputV, GMMDenseColMatrix& inputF, GMMDenseColMatrix& inputInitV, GMMDenseColMatrix& res, std::vector<size_t>& boundary_vertices, int maxIters = 100)
{
    // This function use the boundary as the handles
    res.clear();
    res.resize(inputV.nrows(), 2);
    MatrixXd restV;
    Matrix2Xd initV;
    Matrix3Xi F;
    VectorXi handles;

    //restV.resize(3, inputV.nrows());
    F.resize(3, inputF.nrows());
    initV.resize(2, inputV.nrows());
    restV.resize(3, inputV.nrows());
    for (int i = 0; i < inputV.nrows(); i++)
        for (int j = 0; j < 3; j++)
            restV(j, i) = inputV(i, j);
    for (int i = 0; i < inputF.nrows(); i++)
        for (int j = 0; j < 3; j++)
            F(j, i) = inputF(i, j);
    for (int i = 0; i < inputInitV.nrows(); i++)
        for (int j = 0; j < 2; j++)
            initV(j, i) = inputInitV(i, j);

    boundary_vertices.clear();
    boundary_vertices.reserve(inputV.nrows());
    extract_mesh_boundary_vertices(F, boundary_vertices);
    handles.resize(boundary_vertices.size());
    for (int i = 0; i < boundary_vertices.size(); i++)
        handles(i) = boundary_vertices[i];

    SolverOptions opts;

    opts.form = "harmonic";
    opts.alpha = 1e-8;
    opts.maxIter = maxIters;

    // normalize meshes to have unit area
    double init_total_area = abs(compute_total_signed_mesh_area(initV, F));
    initV *= sqrt(1. / init_total_area);
    double rest_total_area = compute_total_unsigned_area(restV, F);
    //restV *= sqrt(1. / rest_total_area);


    // initialize energy
    IsoTLC_2D_Formulation energy(restV, initV, F, handles, opts.form, opts.alpha);
    VectorXd x0 = energy.get_x();

    // minimize energy
    QuasiNewtonSolver QN_Solver;
    NewtonSolver PN_Solver;
    QN_Solver.maxIter = opts.maxIter;
    PN_Solver.maxIter = opts.maxIter;
    // stage 1: find injectivity
    //std::cout << "------ stage 1: find injectivity ------" << std::endl;
    bool injective_found = true;
    QN_Solver.check_custom_stop_criterion = true;
    QN_Solver.use_custom_stop_criterion = true;
    //cout << "Criteria already met: " << energy.met_custom_criterion() << endl;
    QN_Solver.optimize(&energy, x0);
    if (QN_Solver.get_stop_type() == StopType::Custom_Criterion_Reached) {
        // due to QN implementation (NLopt), the mesh with current vertices may not be injective,
        // even though QN_Solver stops at Custom_Criterion_Reached
        energy.set_V(energy.get_latest_injective_V());
    }
    //std::cout << "Quasi-Newton (" << get_stop_type_string(QN_Solver.get_stop_type()) << "), ";
    //std::cout << QN_Solver.get_num_iter() << " iterations, " << "E = " << QN_Solver.get_energy() << std::endl;
    if (!energy.met_custom_criterion()) {
        PN_Solver.check_custom_stop_criterion = true;
        PN_Solver.use_custom_stop_criterion = true;
        PN_Solver.optimize(&energy, x0);
        //std::cout << "Projected-Newton (" << get_stop_type_string(PN_Solver.get_stop_type()) << "), ";
        //std::cout << PN_Solver.get_num_iter() << " iterations, " << "E = " << PN_Solver.get_energy() << std::endl;
        if (!energy.met_custom_criterion()) {
            //std::cout << "Failed to find injective map!" << std::endl;
            injective_found = false;
        }
    }
    // stage 2: lower distortion
    if (injective_found) {
        //std::cout << "------ stage 2: lower distortion ------" << std::endl;
        // optimize until energy convergence, starting from the result of stage 1
        PN_Solver.check_custom_stop_criterion = true;
        PN_Solver.use_custom_stop_criterion = false;
        PN_Solver.gtol *= (opts.alpha / 1e-2);
        PN_Solver.optimize(&energy, energy.get_x());
        //std::cout << "Projected-Newton (" << get_stop_type_string(PN_Solver.get_stop_type()) << "), ";
        //std::cout << PN_Solver.get_num_iter() << " iterations, " << "E = " << PN_Solver.get_energy() << std::endl;
    }

    Eigen::Matrix2Xd resV = energy.get_latest_injective_V();

    if (!injective_found)
        return injective_found;
    for (int i = 0; i < inputInitV.nrows(); i++)
        for (int j = 0; j < 2; j++)
            res(i, j) = resV(j, i) * sqrt(init_total_area);

    return injective_found;
    // save result
    /*if (injective_found) {
        export_mesh(result_file, energy.get_latest_injective_V(), F);
    } else {
        export_mesh(result_file, energy.get_V(), F);
    }*/
}