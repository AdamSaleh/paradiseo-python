all : evolve.cpp
	g++ -DDEPRECATED_MESSAGES \
       	-Wunknown-pragmas -O0 -g \
	-I/usr/local/include/paradiseo \
	-I/usr/local/include/paradiseo/eo \
	-I/usr/local/include/paradiseo/mo \
	-I/usr/local/include/paradiseo/moeo \
	-oevolve.o \
	-c evolve.cpp

	g++ -DDEPRECATED_MESSAGES \
       	-Wunknown-pragmas -O0 -g \
	-I/usr/include/python2.7 \
	-I/usr/local/include/paradiseo \
	-I/usr/local/include/paradiseo/eo \
	-I/usr/local/include/paradiseo/mo \
	-I/usr/local/include/paradiseo/moeo \
	-opyutils.o \
	-c pyutils.cpp

	g++ -Wunknown-pragmas  -g  evolve.o pyutils.o -o evolve -rdynamic \
		-L"/usr/gcc_4_7/lib" -L"/usr/gcc_4_7/lib64" \
		"/usr/local/lib64/libeo.a" \
		"/usr/local/lib64/libga.a" \
		"/usr/local/lib64/libeoutils.a" \
		"/usr/local/lib64/libmoeo.a" -lpython2.7

	rm evolve.o
	rm pyutils.o

clean :
	rm evolve
