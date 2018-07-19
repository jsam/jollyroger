
#include <cassert>
#include "JRStore/Store.h"

using JollyRoger::JRTransport::Store;

Store::Store() {
    options.create_if_missing = true;
    rocksdb::Status status = rocksdb::DB::Open(options, "/tmp/testdb", &db);
    assert(status.ok());

    std::string value;
    rocksdb::Status s = db->Get(rocksdb::ReadOptions(), "id", &value);
    if (s.IsNotFound()) {
        // TODO: generate pseudo-random ID out of 160 bit search space

    }
}



const std::string& Store::GetID() { return ID; }

