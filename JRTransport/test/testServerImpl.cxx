///
/// @file    TestHello.cxx
/// @author  jsam <contact@justsam.io>
///
#include "JRTransport/ServerImpl.h"
#include "JRTransport/World.h"

#define BOOST_TEST_MODULE hello test
#define BOOST_TEST_MAIN
#define BOOST_TEST_DYN_LINK
#include <assert.h>
#include <boost/test/unit_test.hpp>

using JollyRoger::JRTransport::World;
using JollyRoger::JRTransport::ServerImpl;

BOOST_AUTO_TEST_CASE(ServerImplCreation)
{
  ServerImpl server;
  BOOST_CHECK_EQUAL(server.RequestCount(), 0);
}

BOOST_AUTO_TEST_CASE(ServerImplRun) {
    ServerImpl server;
    server.Run();
}

BOOST_AUTO_TEST_CASE(hello_test)
{
  World world;
  const int ret = world.returnsN(3);
  BOOST_CHECK_EQUAL(ret, 3);
}
