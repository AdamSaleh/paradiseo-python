#include <Python.h>
#include <stdio.h>
#include "pyutils.h"
#include <iostream>

PyObject *pModule, *pFuncMin, *pFuncMax,*pFuncNo,
*pFuncMinBounds,*pFuncReport, *pFuncMaxBounds,*pFuncNoParams,*pFuncPopeval;

bool py_bool_function(PyObject *fn,int index){
    bool out = false;	
    PyObject *pArgs, *pValue;
    if (fn && PyCallable_Check(fn)) {
        pArgs = PyTuple_New(1);
	pValue = PyInt_FromLong(index);
	PyTuple_SetItem(pArgs, 0, pValue);
	pValue = PyObject_CallObject(fn, pArgs);
	Py_DECREF(pArgs);
	if (pValue != NULL) {
		out= (Py_True == pValue);
	}
	else {
		PyErr_Print();
	}
     }
     Py_DECREF(pValue);

     return out;
}

void py_void_string_function(PyObject *fn,std::string i,std::string s){
    bool out = false;	
    PyObject *pArgs, *pValue;
    if (fn && PyCallable_Check(fn)) {
        pArgs = Py_BuildValue("(s,s)",i.c_str(), s.c_str());  
	PyObject_CallObject(fn, pArgs);
	Py_DECREF(pArgs);
    }
}

int py_int_function(PyObject *fn)
{
    long out = 0;	
        PyObject *pArgs, *pValue;
	if (fn && PyCallable_Check(fn)) {
		pValue = PyObject_CallObject(fn, NULL);
		if (pValue != NULL) {
			out= PyInt_AsLong(pValue);
		}
		else {
			PyErr_Print();
		}
	}
	Py_DECREF(pValue);
    
    return out;
}

double py_double_function(PyObject *fn,int index){
    double out = 0;
    PyObject *pArgs, *pValue;
    if (fn && PyCallable_Check(fn)) {
        pArgs = PyTuple_New(1);
        pValue = PyInt_FromLong(index);
        PyTuple_SetItem(pArgs, 0, pValue);
        pValue = PyObject_CallObject(fn, pArgs);
        Py_DECREF(pArgs);
        if (pValue != NULL) {
            out= PyFloat_AsDouble(pValue);
        }else {
            PyErr_Print();
        }
    }
    Py_DECREF(pValue);
    return out;
}

void py_popeval_func (PyObject *fn, eoPop<Evolve> & offspring){
    PyObject *pArgs, *pList, *pValue,*pReturnList;
    
    if (fn && PyCallable_Check(fn)) {
        pList = PyList_New(0);
        for(int i=0;i<offspring.size();i++){
            PyObject *pIndividual;
            pIndividual = PyList_New(0);
            for(int j=0;j<offspring[i].size();j++){
              pValue = PyFloat_FromDouble(offspring[i][j]);
              PyList_Append(pIndividual, pValue);
            }
            PyList_Append(pList,pIndividual);
            Py_DECREF(pIndividual);
        }
        pArgs = PyTuple_New(1);
        PyTuple_SetItem(pArgs, 0, pList);

        pReturnList = PyObject_CallObject(fn, pArgs);
        Py_DECREF(pArgs);
        Py_DECREF(pList);

        if (pReturnList != NULL) {
            int outlen = PyList_Size(pReturnList);  
            for(int i=0;i<outlen;i++){
                PyObject *pReturnList2 =PyList_GetItem(pReturnList,i);
                int outlen2 = PyList_Size(pReturnList2);  
                EvolveObjectiveVector objVec;
                for(int j=0;j<outlen2;j++){
                    pValue = PyList_GetItem(pReturnList2,j);   
                    objVec[j] = PyFloat_AsDouble(pValue);
                }
                offspring[i].objectiveVector(objVec);
            }
        }else {
            PyErr_Print();
        }
    }
    Py_DECREF(pValue);
    Py_DECREF(pReturnList);
}

void py_popeval (eoPop<Evolve> & pop){
    py_popeval_func(pFuncPopeval,pop);
}

int py_nObjectives ()
{
    return py_int_function(pFuncNo); 
}

double py_minimalBounds(int index)
{
    return py_double_function(pFuncMinBounds,index); 
}

double py_maximalBounds(int index)
{
    return py_double_function(pFuncMaxBounds,index);
}

int py_noParams ()
{
    return py_int_function(pFuncNoParams); 
}

void py_report(std::string input,std::string report){
  py_void_string_function(pFuncReport,input,report);		
}

int py_init(string P_PATH,string P_MODULE,string P_ALGO){
    Py_Initialize();              // will use python for glue
    // Add PROJECT to PATH
    stringstream path; 
    path << P_PATH;
    stringstream pyrun;
    pyrun << "import os, sys, threading\nsys.path.append('" << path.str() <<  "')\nos.chdir('" << path.str() << "')\n";
    PyRun_SimpleString(pyrun.str().c_str() ); 
    cout << pyrun.str() << endl;
	  
   if (pModule == NULL) {        
		PyObject *pName;
        	pName = PyString_FromString(P_MODULE.c_str());
        	/* Error checking of pName left out */
        	pModule = PyImport_Import(pName);
    cout << "Python:" << endl;
		Py_DECREF(pName);
		if (pModule != NULL) {
			pFuncNo = PyObject_GetAttrString(pModule, "nObjectives");
            if(pFuncNo !=NULL && PyCallable_Check(pFuncNo)){
                cout << "Number of objectives loaded." << endl;
            }else{
                cout << "ERROR: nObjectives function not found." << endl;
            }
			pFuncMinBounds = PyObject_GetAttrString(pModule, "minimumBounds");
    	    if(pFuncMinBounds !=NULL && PyCallable_Check(pFuncMinBounds)){
                cout << "Min bounds loaded." << endl;
            }else{
                cout << "ERROR: minimumBounds function not found." << endl;
            }
            pFuncMaxBounds = PyObject_GetAttrString(pModule, "maximumBounds");
		    if(pFuncMaxBounds !=NULL && PyCallable_Check(pFuncMaxBounds)){
                cout << "Max bounds loaded." << endl;
            }else{
                cout << "ERROR: maximumBounds function not found." << endl;
            }
            pFuncNoParams = PyObject_GetAttrString(pModule, "nParams");
			if(pFuncNoParams !=NULL && PyCallable_Check(pFuncNoParams)){
                cout << "Number of params loaded." << endl;
            }else{
                cout << "ERROR: nParams function not found." << endl;
            }
            pFuncPopeval = PyObject_GetAttrString(pModule, "popeval");
			if(pFuncPopeval !=NULL && PyCallable_Check(pFuncPopeval)){
                cout << "Popeval loaded." << endl;
            }else{
                cout << "ERROR: popeval function not found." << endl;
            }
            pFuncReport = PyObject_GetAttrString(pModule, "report");
			if(pFuncReport !=NULL && PyCallable_Check(pFuncReport)){
                cout << "Report loaded." << endl;
            }else{
                cout << "ERROR: report function not found." << endl;
            }
            
		}else {
			PyErr_Print();
	    }
	}
}

int py_fin(){
  Py_XDECREF(pFuncNo);
  Py_DECREF(pModule);
 Py_Finalize(); // finish python
}
