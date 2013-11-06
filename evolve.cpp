#include <stdio.h>
#include <sstream>
#include <es/eoRealInitBounded.h>
#include <es/eoRealOp.h>
#include "pyutils.h"
#include <unistd.h>
using namespace std;

template<class EOT>
class PyPopEval : public eoPopEvalFunc<EOT> {
public:
  /** Ctor: set value of embedded eoEvalFunc */
  PyPopEval() {}

  /** Do the job: simple loop over the offspring */
  void operator()(eoPop<EOT> & _parents, eoPop<EOT> & offspring)
  {
      (void)_parents;
      py_popeval(offspring);
  }
};

// main
int main (int argc, char *argv[])
{
    eoParser parser(argc, argv);  // for user-parameter reading
    eoState state;                // to keep all things allocated

    stringstream input;
    // parameters
    unsigned int POP_SIZE = parser.createParam((unsigned int)(100), "popSize", "Population size",'P',"Param").value();
    input << "popSize:" << POP_SIZE<<"\n";

    unsigned int MAX_GEN = parser.createParam((unsigned int)(100), "maxGen", "Maximum number of generations",'G',"Param").value();
    input << "maxGen:" << MAX_GEN <<"\n";

    double M_EPSILON = parser.createParam(0.01, "mutEpsilon", "epsilon for mutation",'e',"Param").value();
    input << "mutEpsilon:" <<M_EPSILON <<"\n";

    double C_PROB = parser.createParam(0.25, "crossProb", "param crossover probability",'q',"Param").value();
    input << "crossProb:" <<C_PROB <<"\n";
    double P_CROSS = parser.createParam(0.25, "pCross", "Crossover probability",'C',"Param").value();
    input << "pCross:" <<P_CROSS <<"\n";

    double P_MUT = parser.createParam(1.0, "pMut", "individual mutation probability",'M',"Param").value();
    input << "pMut:" <<P_MUT <<"\n";

    double M_PROB = parser.createParam(0.35, "mutProb", "param mutation probability",'w',"Param").value();
    input << "mutProb:" <<M_PROB <<"\n";


    string P_PATH = parser.createParam(string("./"),"pPath","Python path",'t').value(); 
    input << "pPath:" <<P_PATH<<"\n";

    string P_MODULE = parser.createParam(string("ObjectiveVectorTraits"),"pModule","Python module",'m').value(); 
    input << "pModule:" <<P_MODULE<<"\n";

    string P_ALGO = parser.createParam(string("nsgaII"),"pAlgo","Evolution algorithm",'a').value(); 
    if(P_ALGO!="nsgaII" || P_ALGO!="spea2" || P_ALGO != "ibeaEps" || P_ALGO!="ibeaHV"){
        cout << "Algorithm chosen is not among supported nsgaII,spea2, ibeaEps or ibeaHV\n.";
    }
    input << "pAlgo:" <<P_ALGO<<"\n";
    cout << P_PATH << P_MODULE; 
 
/*
*/
    py_init(P_PATH,P_MODULE,P_ALGO);  
    // generate initial population
    int noParams = py_noParams();
    cout << "Number of params: " << noParams <<"\n";
    std::vector<double> minBounds(noParams);
    std::vector<double> maxBounds(noParams);
    
    for(int i=0;i<noParams;i++){
      minBounds[i]=py_minimalBounds(i);
      maxBounds[i]=py_maximalBounds(i);
      cout << i<<".bound: " <<minBounds[i] <<"-"<<maxBounds[i] <<"\n";
    }
    eoRealVectorBounds bounds (minBounds, maxBounds);
    
    cout << "Bounds set\n";
    //
    // crossover and mutation
    eoRealUXover <Evolve> xover(C_PROB);
    eoUniformMutation < Evolve > mutation (bounds,M_EPSILON,M_PROB);

    eoRealInitBounded < Evolve> init (bounds);
    eoPop < Evolve > pop (POP_SIZE, init);

    cout << "Crossover and mutation set\n";
  
    eoGenContinue < Evolve > defaultGenContinuator(MAX_GEN);
    //SchedulingTest singleScheduler;
    //ScheduleablePopEval< Evolve > singlePopEval(singleScheduler);    
    PyPopEval< Evolve > popEval;
    eoSGAGenOp < Evolve > defaultSGAGenOp(xover, P_CROSS, mutation, P_MUT);
    cout << "Popeval initialized\n";
    if(P_ALGO=="spea2"){
        moeoSPEA2Archive<Evolve> arch_spea(POP_SIZE);
        moeoSPEA2 <Evolve> spea2 (defaultGenContinuator, popEval,  xover, P_CROSS, mutation, P_MUT,arch_spea);
        spea2 (pop);
    }else if(P_ALGO=="ibeaEps"){
	    moeoAdditiveEpsilonBinaryMetric<EvolveObjectiveVector> indicator;
		moeoIBEA<Evolve> ibea (defaultGenContinuator, popEval, defaultSGAGenOp, indicator);
		ibea (pop);
    }else if(P_ALGO=="ibeaHV"){
        moeoHypervolumeBinaryMetric<EvolveObjectiveVector> indicator;
        moeoIBEA<Evolve> ibea (defaultGenContinuator, popEval, defaultSGAGenOp, indicator);
        ibea (pop);            
    }else{
        moeoNSGAII < Evolve > nsgaII (defaultGenContinuator, popEval, defaultSGAGenOp);
        nsgaII (pop);
    }
    moeoUnboundedArchive < Evolve > arch;
    arch(pop);
    stringstream ss;
    arch.sortedPrintOn (ss);
    py_report(input.str(),ss.str());
    py_fin();
    return EXIT_SUCCESS;
}
