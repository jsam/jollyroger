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
    BOOST_CHECK_EQUAL(server.IsRunning(), false);
    server.Run();
    BOOST_CHECK_EQUAL(server.RequestCount(), 0);
    BOOST_CHECK_EQUAL(server.IsRunning(), true);

    JollyRoger::JRTransport::Client client(grpc::CreateChannel(":50051", grpc::InsecureChannelCredentials()));
    auto _request = new jrtransport::PingRequest();

    auto _id = new jrtransport::ID();
    _id->set_infohash("infohash:ping");
    _request->set_allocated_source(_id);

    auto response = client.Ping(_request);
    BOOST_CHECK_EQUAL(response->destination().infohash(), "infohash:pongReply");

    server.Stop();

    BOOST_CHECK_EQUAL(server.IsRunning(), false);
    BOOST_CHECK_EQUAL(server.RequestCount(), 1);
}

BOOST_AUTO_TEST_CASE(ServerImplBench) {
    Server server;
    BOOST_CHECK_EQUAL(server.IsRunning(), false);

    server.Run();
    BOOST_CHECK_EQUAL(server.RequestCount(), 0);
    BOOST_CHECK_EQUAL(server.IsRunning(), true);

    const int request_count = 1024;
    auto _request = new jrtransport::PingRequest();

    auto _id = new jrtransport::ID();
    _id->set_infohash("infohash:ping");
    _request->set_allocated_source(_id);

    std::vector<std::future<void>> v;
    std::chrono::steady_clock::time_point begin = std::chrono::steady_clock::now();
    for (int i = 0; i < 50; i++) {
        v.emplace_back(async(std::launch::async, [&_request, &request_count] {
            JollyRoger::JRTransport::Client client(grpc::CreateChannel(":50051", grpc::InsecureChannelCredentials()));
            for (int j = 0; j < request_count; ++j) {
                client.Ping(_request);
            }
        }));
    }
    for (auto& f: v) {
        f.wait();
    }
    std::chrono::steady_clock::time_point end = std::chrono::steady_clock::now();
    auto t = std::chrono::duration_cast<std::chrono::milliseconds>(end - begin).count();
    std::cout << "Executing " << request_count*50 << " ping requests in " << t << "ms\n";


    server.Stop();
    BOOST_CHECK_EQUAL(server.IsRunning(), false);
    BOOST_CHECK_EQUAL(server.RequestCount(), request_count*50);
}