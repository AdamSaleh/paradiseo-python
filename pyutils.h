#include <string>
#include <sstream>
#include <vector>
#include <moeo>

using namespace std;

bool py_minimizing (int );
bool py_maximizing (int );
int py_nObjectives ();

double py_minimalBounds(int );
double py_maximalBounds(int );
int py_noParams ();

int py_init(string ,string ,string );
void py_report(string,string);
int py_fin();

// the moeoObjectiveVectorTraits : minimizing 2 objectives
class OVT : public moeoObjectiveVectorTraits
{
public:
 static bool minimizing (int index){
        return true;
    }
    static bool maximizing (int index){
        return false;
       
    }
    static unsigned int nObjectives (){
	      int out = py_nObjectives();
        return out;
    }
};


// objective vector of real values
typedef moeoRealObjectiveVector < OVT > EvolveObjectiveVector;

// multi-objective evolving object for the Evolve problem
class Evolve : public moeoRealVector < EvolveObjectiveVector >
{
public:
    Evolve() : moeoRealVector < EvolveObjectiveVector > (1)
    {}
};

void py_popeval (eoPop<Evolve> & offspring);