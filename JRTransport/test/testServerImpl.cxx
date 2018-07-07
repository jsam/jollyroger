///
/// @file    TestHello.cxx
/// @author  jsam <contact@justsam.io>
///

#include <thread>
#include <chrono>

#include "grpc++/grpc++.h"

#include "JRTransport/Server.h"
#include "JRTransport/Client.h"
#include "JRTransport/Node.h"

#define BOOST_TEST_MODULE hello test
#define BOOST_TEST_MAIN
#define BOOST_TEST_DYN_LINK
#include <assert.h>
#include <boost/test/unit_test.hpp>

using JollyRoger::JRTransport::Node;
using JollyRoger::JRTransport::Server;
using JollyRoger::JRTransport::Client;

BOOST_AUTO_TEST_CASE(ServerImplCreation)
{
  Server server;
  BOOST_CHECK_EQUAL(server.RequestCount(), 0);
}

BOOST_AUTO_TEST_CASE(ServerImplRun) {
    Server server;
    server.Run();
    JollyRoger::JRTransport::Client client(grpc::CreateChannel(":50051", grpc::InsecureChannelCredentials()));
    auto response = client.Ping();
    std::cout << "Received: " << response.destination().infohash() << "\n";
    BOOST_CHECK_EQUAL(response.destination().infohash(), "infohash:pongReply");
    server.Stop();
}
