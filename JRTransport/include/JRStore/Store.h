#ifndef PROJECT_STORE_H
#define PROJECT_STORE_H

#include <string>
#include "rocksdb/db.h"

namespace JollyRoger {
namespace JRTransport {

using byte = unsigned char;

class Store final {

  public:
    Store();
    ~Store() = default;

    const std::string& GetID();



    // const RoutingTable& GetRoutingTable();
    //    bool StoreRoutingTable(const RoutingTable& table);
    //
    //    bool StoreObject(std::string key, std::shared_ptr<byte[]> value);
    //    std::shared_ptr<byte[]> GetObject(std::string key);

  private:
    std::string ID;

    rocksdb::DB* db;
    rocksdb::Options options;
};

} // namespace JRTransport
} // namespace JollyRoger

#endif // PROJECT_STORE_H
