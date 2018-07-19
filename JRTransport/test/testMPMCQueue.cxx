
#define BOOST_TEST_MODULE hello test
#define BOOST_TEST_MAIN
#define BOOST_TEST_DYN_LINK
#include <assert.h>
#include <boost/test/unit_test.hpp>

#include "JRUtils/MPMCQueue.h"

BOOST_AUTO_TEST_CASE(MPMCQueueRun)
{
    JollyRoger::JRUtils::MPMCQueue<int> queue(1024);

    for (int i = 0; i < 1024; ++i) {
        queue.push(i);
    }

    for (int i = 0; i < 1024*2; ++i) {
        int k;
        queue.pop(k);
        std::cout << k << std::endl;
        queue.push(k);
    }

}