
#define BOOST_TEST_MODULE hello test
#define BOOST_TEST_MAIN
#define BOOST_TEST_DYN_LINK
#include <boost/test/unit_test.hpp>
#include <JRTransport/transport.pb.h>

#include "JRStore/Store.h"


BOOST_AUTO_TEST_CASE(SerializeExample)
{
    jrtransport::PingRequest _request;

    jrtransport::ID id;
    id.set_infohash("infohash");
    id.set_address("192.168.1.1");
    id.set_port("50051");

    auto serialized_value = id.SerializeAsString();
    BOOST_CHECK_EQUAL(serialized_value.size(), 30);
}

BOOST_AUTO_TEST_CASE(BitsetExample) {
    std::cout << false << std::endl;
}

BOOST_AUTO_TEST_CASE(StoreImpl)
{
    using JollyRoger::JRTransport::Store;
    auto store = new Store();
    BOOST_CHECK_EQUAL(store != nullptr, true);
}