# PC 上でインタプリタを試す:  make && ./basic
#   テスト:                   make test
CXXFLAGS = -std=c++17 -Wall -Wextra -O1 -g -fsanitize=address,undefined

basic: host_console.cpp ../PicoIntegerBasic/basic.cpp ../PicoIntegerBasic/basic.h ../PicoIntegerBasic/console.h
	$(CXX) $(CXXFLAGS) -o $@ host_console.cpp ../PicoIntegerBasic/basic.cpp

test: basic
	./run_tests.sh

clean:
	rm -f basic *.BAS
.PHONY: test clean
