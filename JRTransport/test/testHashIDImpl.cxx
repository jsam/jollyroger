///
/// @file    testHashIDImpl.cxx
/// @author  jsam <contact@justsam.io>
///


#define BOOST_TEST_MODULE hello test
#define BOOST_TEST_MAIN
#define BOOST_TEST_DYN_LINK

#include "JRStore/HashID.h"
#include <boost/test/unit_test.hpp>
#include <assert.h>
#include <iostream>

using JollyRoger::JRStore::HashID;


BOOST_AUTO_TEST_CASE(HashIDConstructor)
{
    HashID<160> _hash;
    std::cout << _hash.ToString() << std::endl;
    BOOST_CHECK_EQUAL(_hash.ToString().size(), 160);
}

BOOST_AUTO_TEST_CASE(HashIDFromString) {
    std::string h("0000000100101011000011111110111101100111101000000100110110110010101011110011010001000010110110111111100000000001010100110001010100111001000010000111111000101010");
    HashID<160> _hash(h);
    BOOST_CHECK_EQUAL(_hash.ToString(), h);
}

BOOST_AUTO_TEST_CASE(HashIDFromHash) {
    HashID<160> hash_one;
    auto raw_hash = new HashID<160>::Hash(hash_one.get_hash());
    HashID<160> hash_two(*raw_hash);

    BOOST_CHECK_EQUAL(hash_one.ToString(), hash_two.ToString());
}

BOOST_AUTO_TEST_CASE(HashIDFromHashID) {
    HashID<160> hash_one, hash_two;
    BOOST_CHECK_EQUAL(hash_one.ToString() == hash_two.ToString(), false);
}

BOOST_AUTO_TEST_CASE(HashIDEquality) {
    HashID<160> hash_one, hash_two;

    std::cout << hash_one.ToString() << std::endl;
    std::cout << hash_two.ToString() << std::endl;

    auto areEqual = hash_one.IsGreater(hash_two);
    auto areDifferent = hash_one.IsGreater(hash_two) == !hash_two.IsGreater(hash_one);
    BOOST_CHECK_EQUAL(areEqual || areDifferent, true);
}

BOOST_AUTO_TEST_CASE(HashIDHalfSub) {
    HashID<160> hash;

    bool D, Bout;
    std::tie(D, Bout) = hash.HalfSub(false, false);
    BOOST_CHECK_EQUAL(D, false);
    BOOST_CHECK_EQUAL(Bout, false);

    std::tie(D, Bout) = hash.HalfSub(false, true);
    BOOST_CHECK_EQUAL(D, true);
    BOOST_CHECK_EQUAL(Bout, true);

    std::tie(D, Bout) = hash.HalfSub(true, false);
    BOOST_CHECK_EQUAL(D, true);
    BOOST_CHECK_EQUAL(Bout, false);

    std::tie(D, Bout) = hash.HalfSub(true, true);
    BOOST_CHECK_EQUAL(D, false);
    BOOST_CHECK_EQUAL(Bout, false);
}

BOOST_AUTO_TEST_CASE(HashFullSub) {
    do {
        HashID<8> hash_one, hash_two;

        auto cmp = hash_one.IsGreater(hash_two);

        if (cmp == HashID<8>::CURRENT_GREATER) {
            auto distance = hash_one.Sub(hash_two);
            break;
        }
    } while (true);
}