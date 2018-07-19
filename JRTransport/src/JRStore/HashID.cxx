
#include <random>
#include <sstream>

#include "JRStore/HashID.h"

using JollyRoger::JRStore::Hash;
using JollyRoger::JRStore::HashID;

HashID::HashID() {
    Next();
}

HashID::HashID(const std::string& from_str) {
    if (from_str.size() != SEARCH_SPACE_SIZE)
        throw "sequence does not contain complete search space size";

    for (unsigned long i = 0; i < from_str.size(); ++i) {
        _hash[SEARCH_SPACE_SIZE-1-i] = from_str.at(i) == '1';
    }
}

HashID::HashID(const JollyRoger::JRStore::HashID &other_hash) {
    _hash = other_hash.get_hash();
}

HashID::HashID(const JollyRoger::JRStore::Hash &other_hash) {
    _hash = other_hash;
}

bool HashID::At(int index) const {
    return _hash[index];
}

int HashID::CmpAt(int index, const JollyRoger::JRStore::HashID &other_hash) {
    if (_hash[index] < other_hash.At(index)) { return OTHER_GREATER; }
    if (_hash[index] > other_hash.At(index)) { return CURRENT_GREATER; }
    return EQUAL;
}

int HashID::IsGreater(const JollyRoger::JRStore::HashID &other_hash) {
    for (int i = 0; i < SEARCH_SPACE_SIZE; ++i) {
        switch(this->CmpAt(SEARCH_SPACE_SIZE-1-i, other_hash)) {
            case CURRENT_GREATER:
                return CURRENT_GREATER;

            case OTHER_GREATER:
                return OTHER_GREATER;

            default:
                continue;
        }
    }
    return EQUAL;
}

void HashID::SetAt(int index, bool bit) {
    _hash[index] = bit;
}

std::tuple<bool, bool> HashID::HalfSub(bool a, bool b) const {
    return std::make_tuple(a ^ b, b & ~a);
}

const HashID& HashID::Sub(const HashID &other_hash) {
    bool Bin = false;
    bool D1, D2, Bout1, Bout2;
    auto hash = new HashID;

    // we are sub from this
    for (int i = 0; i < SEARCH_SPACE_SIZE; ++i) {
        std::tie(D1, Bout1) = HalfSub(_hash[i], other_hash.At(i));
        std::tie(D2, Bout2) = HalfSub(D1, Bin);

        Bin = Bout2 | Bout1;
        hash->SetAt(i, D2);
    }

    return *hash;
}

void HashID::Next() {
    std::random_device r;
    std::default_random_engine engine(r());
    std::uniform_int_distribution<unsigned long long> uniform_dist;

    for (int i = 0; i < SEARCH_SPACE_SIZE; ++i) {
        _hash[i] = uniform_dist(engine) % 2 == 0;
    }
}

std::string HashID::ToString() {
    return _hash.to_string();
}

const std::bitset<JollyRoger::JRStore::SEARCH_SPACE_SIZE> &JollyRoger::JRStore::HashID::get_hash() const {
    return _hash;
}

